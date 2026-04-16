from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from config.settings import (
    WORKFLOW_CONDITIONAL_INTENTS,
    WORKFLOW_CONFIDENCE_THRESHOLD,
    WORKFLOW_ELIGIBLE_INTENTS,
    WORKFLOW_SEED_PATH,
)
from core.retriever import LawChunk

POLISH_STOP_WORDS = {
    "i",
    "w",
    "na",
    "do",
    "z",
    "o",
    "od",
    "dla",
    "jest",
    "nie",
    "sie",
    "to",
    "ze",
    "jak",
    "po",
    "za",
    "co",
    "czy",
    "ale",
    "lub",
    "oraz",
    "przez",
    "przy",
    "bez",
    "pod",
    "nad",
    "przed",
    "miedzy",
    "jaki",
    "jakie",
    "jest",
}

WORKFLOW_OPERATIONAL_MARKERS = (
    "wysl",
    "zloz",
    "oznacz",
    "nada",
    "doda",
    "pobrac",
    "podpis",
    "zglos",
    "wyrejestrowac",
    "wyrejestrow",
    "skorygow",
    "ustaw",
    "bramka",
    "status",
    "uprawnienia",
    "uprawnien",
    "dostep",
    "token",
    "pue",
    "korekta",
)


@dataclass(frozen=True, slots=True)
class WorkflowDocument:
    """In-memory workflow unit prepared for deterministic retrieval."""

    chunk: LawChunk
    title_tokens: frozenset[str]
    area_tokens: frozenset[str]
    example_tokens: frozenset[str]
    form_tokens: frozenset[str]
    system_tokens: frozenset[str]
    category_tokens: frozenset[str]


@dataclass(slots=True)
class WorkflowRetrievalResult:
    """Workflow retrieval outcome with deterministic confidence metadata."""

    chunks: list[LawChunk]
    confident: bool
    top_score: float = 0.0


_CACHE_LOCK = Lock()
_WORKFLOW_CACHE: dict[str, tuple[int, tuple[WorkflowDocument, ...]]] = {}


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(re.findall(r"[a-z0-9_]+", ascii_value))


def _tokenize(text: str) -> frozenset[str]:
    return frozenset(
        token
        for token in _normalize(text).split()
        if token and token not in POLISH_STOP_WORDS
    )


def _build_workflow_content(record: dict[str, object]) -> str:
    """Render a workflow unit into plain context text for the generator."""

    steps = [str(step).strip() for step in record.get("steps", []) if str(step).strip()]
    required_inputs = [str(item).strip() for item in record.get("required_inputs", []) if str(item).strip()]
    pitfalls = [str(item).strip() for item in record.get("common_pitfalls", []) if str(item).strip()]
    related_forms = [str(item).strip() for item in record.get("related_forms", []) if str(item).strip()]
    related_systems = [str(item).strip() for item in record.get("related_systems", []) if str(item).strip()]

    parts = [
        f"Workflow area: {str(record.get('workflow_area', '')).strip()}",
        f"Title: {str(record.get('title', '')).strip()}",
    ]
    if steps:
        parts.append("Steps: " + " ".join(f"{index}. {step}" for index, step in enumerate(steps, start=1)))
    if required_inputs:
        parts.append("Required inputs: " + ", ".join(required_inputs))
    if pitfalls:
        parts.append("Common pitfalls: " + "; ".join(pitfalls))
    if related_forms:
        parts.append("Related forms: " + ", ".join(related_forms))
    if related_systems:
        parts.append("Related systems: " + ", ".join(related_systems))
    return "\n".join(part for part in parts if part.strip())


def load_workflow_documents(workflow_path: str | Path = WORKFLOW_SEED_PATH) -> list[WorkflowDocument]:
    """Load and cache workflow seed units as searchable documents."""

    path = Path(workflow_path).resolve()
    if not path.exists():
        return []
    mtime_ns = path.stat().st_mtime_ns
    cache_key = str(path)

    with _CACHE_LOCK:
        cached = _WORKFLOW_CACHE.get(cache_key)
        if cached and cached[0] == mtime_ns:
            return list(cached[1])

    records = json.loads(path.read_text(encoding="utf-8"))
    documents: tuple[WorkflowDocument, ...] = tuple(
        WorkflowDocument(
            chunk=LawChunk(
                content=_build_workflow_content(record),
                law_name="Workflow layer",
                article_number=str(record.get("title", "")).strip(),
                category=str(record.get("category", "")).strip(),
                verified_date="",
                question_intent=" | ".join(str(item).strip() for item in record.get("question_examples", [])[:3]),
                source_type=str(record.get("source_type", "workflow_seed_v1")).strip() or "workflow_seed_v1",
                workflow_area=str(record.get("workflow_area", "")).strip(),
                title=str(record.get("title", "")).strip(),
            ),
            title_tokens=_tokenize(str(record.get("title", ""))),
            area_tokens=_tokenize(str(record.get("workflow_area", ""))),
            example_tokens=_tokenize(" ".join(str(item) for item in record.get("question_examples", []))),
            form_tokens=_tokenize(" ".join(str(item) for item in record.get("related_forms", []))),
            system_tokens=_tokenize(" ".join(str(item) for item in record.get("related_systems", []))),
            category_tokens=_tokenize(str(record.get("category", ""))),
        )
        for record in records
        if str(record.get("title", "")).strip()
    )

    with _CACHE_LOCK:
        _WORKFLOW_CACHE[cache_key] = (mtime_ns, documents)
    return list(documents)


def is_workflow_eligible(query: str, intent: str) -> bool:
    """Return True when the query should try workflow retrieval before legal KB."""

    if intent in WORKFLOW_ELIGIBLE_INTENTS:
        return True
    if intent not in WORKFLOW_CONDITIONAL_INTENTS:
        return False

    normalized_query = _normalize(query)
    return any(marker in normalized_query for marker in WORKFLOW_OPERATIONAL_MARKERS)


def _score_document(query_tokens: frozenset[str], document: WorkflowDocument) -> float:
    """Score one workflow document using weighted token overlap."""

    title_overlap = len(query_tokens & document.title_tokens)
    area_overlap = len(query_tokens & document.area_tokens)
    example_overlap = len(query_tokens & document.example_tokens)
    form_overlap = len(query_tokens & document.form_tokens)
    system_overlap = len(query_tokens & document.system_tokens)
    category_overlap = len(query_tokens & document.category_tokens)

    score = (
        (title_overlap * 4.0)
        + (area_overlap * 3.0)
        + (example_overlap * 2.0)
        + (form_overlap * 3.0)
        + (system_overlap * 2.0)
        + (category_overlap * 2.0)
    )

    if title_overlap >= 2:
        score += 2.0
    if example_overlap >= 2:
        score += 1.5
    if form_overlap >= 1 or system_overlap >= 1:
        score += 1.0
    return score


def retrieve_workflow(
    query: str,
    workflow_path: str | Path = WORKFLOW_SEED_PATH,
    limit: int = 5,
    confidence_threshold: float = WORKFLOW_CONFIDENCE_THRESHOLD,
) -> WorkflowRetrievalResult:
    """Retrieve top workflow units for an operational accountant query."""

    documents = load_workflow_documents(workflow_path)
    query_tokens = _tokenize(query)
    if not query_tokens:
        return WorkflowRetrievalResult(chunks=[], confident=False, top_score=0.0)

    ranked = sorted(
        (
            (_score_document(query_tokens, document), document.chunk)
            for document in documents
        ),
        key=lambda item: (
            item[0],
            item[1].workflow_area,
            item[1].title or item[1].article_number,
        ),
        reverse=True,
    )
    selected = [
        LawChunk(
            content=chunk.content,
            law_name=chunk.law_name,
            article_number=chunk.article_number,
            category=chunk.category,
            verified_date=chunk.verified_date,
            question_intent=chunk.question_intent,
            score=score,
            source_type=chunk.source_type,
            workflow_area=chunk.workflow_area,
            title=chunk.title,
        )
        for score, chunk in ranked[:limit]
        if score > 0
    ]
    top_score = selected[0].score if selected else 0.0
    return WorkflowRetrievalResult(
        chunks=selected,
        confident=bool(selected) and top_score >= confidence_threshold,
        top_score=top_score,
    )
