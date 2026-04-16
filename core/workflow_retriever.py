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
    "jak oznaczyc",
    "jak wyslac",
    "jak zlozyc",
    "jak ustawic",
    "jak dodac",
    "jak nadac",
    "jak pobrac",
    "jak podpisac",
    "jak zaksi",
    "jak ujac",
    "jak zaimport",
    "jak zsynchroniz",
    "gdzie klik",
    "gdzie ustawic",
    "wyslij",
    "zloz",
    "ustaw",
    "dodaj",
    "nadac",
    "nadaj",
    "pobrac",
    "pobier",
    "podpisac",
    "zaksi",
    "ujac",
    "zaimport",
    "zsynchroniz",
    "zaciag",
    "importuj",
    "wyeksport",
    "oznaczyc",
)

ACCOUNTING_OPERATIONAL_MARKERS = (
    "ksieg",
    "zaksi",
    "ujac",
    "na kontach",
    "konto",
    "konto 300",
    "rozliczenie zakupu",
    "kpir",
    "rmk",
    "kolumn",
    "kst",
    "magazyn",
    "pod jaka data",
    "data zapisania",
    "koszty uboczne zakupu",
    "przeksieg",
)

PERMISSION_OPERATIONAL_MARKERS = (
    "uprawnien",
    "dostep",
    "token",
    "zaw-fa",
    "upl-1",
    "pps-1",
    "profil zaufany",
    "podpis kwalifikowany",
    "certyfikat",
)

SOFTWARE_SYSTEM_MARKERS = (
    "infakt",
    "optima",
    "comarch",
    "symfonia",
    "enova",
    "streamsoft",
    "insert",
    "saldeo",
    "rewizor",
    "pue",
    "e-platnik",
    "erp",
)

SOFTWARE_ISSUE_MARKERS = (
    "nie dziala",
    "nie pobiera",
    "nie widac",
    "nie pojaw",
    "nie zaciaga",
    "blad",
    "synchroniz",
    "integrac",
    "import",
    "eksport",
    "api",
)

SOFTWARE_RECOMMENDATION_MARKERS = (
    "program",
    "oprogr",
    "wdroz",
    "wdrozyc",
    "polec",
    "szukam",
    "system",
    "narzedzi",
)

ACCOUNTING_CONTEXT_MARKERS = (
    "sprawozdanie",
    "bilans",
    "rzis",
    "remanent",
    "magazyn",
    "ksiegi rachunkowe",
    "sf",
    "krs",
)

COMMUNITY_ONLY_MARKERS = (
    "czy sa na grupie",
    "szukam osoby",
    "polecacie",
    "jaka wasza opinia",
)

LEGAL_DECISION_MARKERS = (
    "czy musi",
    "czy trzeba",
    "czy moge",
    "czy mozna",
    "jaka data",
    "ostatecznie data",
    "pod jaka data",
)

LEGAL_GUARD_MARKERS = (
    "jaki termin",
    "kiedy",
    "termin",
    "czy moge",
    "czy mozna",
    "czy musi",
    "czy przysluguje",
    "obowiazek",
    "obowiazk",
    "zwoln",
    "stawka",
    "podlega",
    "bfk",
    " di ",
    " ro ",
    "gtu",
    "oznaczenie",
    "oznaczenia",
    "bez oznaczenia",
    "vat nalezny",
    "odliczenie vat",
)

WORKFLOW_PATH_STRONG_MATCH_BONUS = 2.0
WORKFLOW_LEGAL_GUARD_PENALTY = 4.0
WORKFLOW_HIGH_CONFIDENCE_DELTA = 3.0


@dataclass(frozen=True, slots=True)
class WorkflowQuerySignals:
    """Deterministic query-level signals used by workflow routing and scoring."""

    normalized_query: str
    tokens: frozenset[str]
    operational_hits: int
    accounting_hits: int
    permission_hits: int
    system_hits: int
    issue_hits: int
    recommendation_hits: int
    accounting_context_hits: int
    community_hits: int
    legal_decision_hits: int
    legal_guard_hits: int
    explicit_how_to: bool


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
    translation = str.maketrans(
        {
            "ą": "a",
            "ć": "c",
            "ę": "e",
            "ł": "l",
            "ń": "n",
            "ó": "o",
            "ś": "s",
            "ż": "z",
            "ź": "z",
        }
    )
    normalized = unicodedata.normalize("NFKD", text.lower().translate(translation))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(re.findall(r"[a-z0-9_]+", ascii_value))


def _tokenize(text: str) -> frozenset[str]:
    return frozenset(
        token
        for token in _normalize(text).split()
        if token and token not in POLISH_STOP_WORDS
    )


def _contains_marker(normalized_query: str, tokens: frozenset[str], marker: str) -> bool:
    """Match either a phrase marker or a token-prefix marker against a query."""

    normalized_marker = _normalize(marker)
    if not normalized_marker:
        return False
    if " " in normalized_marker:
        return normalized_marker in normalized_query
    return any(token.startswith(normalized_marker) for token in tokens)


def _count_marker_hits(normalized_query: str, tokens: frozenset[str], markers: tuple[str, ...]) -> int:
    """Count distinct marker hits in a normalized query."""

    return sum(1 for marker in markers if _contains_marker(normalized_query, tokens, marker))


def _collect_query_signals(query: str) -> WorkflowQuerySignals:
    """Extract deterministic workflow-routing signals from a raw query."""

    normalized_query = _normalize(query)
    tokens = _tokenize(query)
    return WorkflowQuerySignals(
        normalized_query=normalized_query,
        tokens=tokens,
        operational_hits=_count_marker_hits(normalized_query, tokens, WORKFLOW_OPERATIONAL_MARKERS),
        accounting_hits=_count_marker_hits(normalized_query, tokens, ACCOUNTING_OPERATIONAL_MARKERS),
        permission_hits=_count_marker_hits(normalized_query, tokens, PERMISSION_OPERATIONAL_MARKERS),
        system_hits=_count_marker_hits(normalized_query, tokens, SOFTWARE_SYSTEM_MARKERS),
        issue_hits=_count_marker_hits(normalized_query, tokens, SOFTWARE_ISSUE_MARKERS),
        recommendation_hits=_count_marker_hits(normalized_query, tokens, SOFTWARE_RECOMMENDATION_MARKERS),
        accounting_context_hits=_count_marker_hits(normalized_query, tokens, ACCOUNTING_CONTEXT_MARKERS),
        community_hits=_count_marker_hits(normalized_query, tokens, COMMUNITY_ONLY_MARKERS),
        legal_decision_hits=_count_marker_hits(normalized_query, tokens, LEGAL_DECISION_MARKERS),
        legal_guard_hits=_count_marker_hits(normalized_query, tokens, LEGAL_GUARD_MARKERS),
        explicit_how_to=normalized_query.startswith(("jak ", "gdzie ", "w jaki sposob")),
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

    signals = _collect_query_signals(query)

    if (
        signals.community_hits > 0
        and signals.recommendation_hits == 0
        and signals.system_hits == 0
        and not signals.explicit_how_to
        and signals.issue_hits == 0
    ):
        return False

    if intent in WORKFLOW_ELIGIBLE_INTENTS:
        if intent == "software_tooling":
            if signals.legal_guard_hits >= 2 and not signals.explicit_how_to and signals.issue_hits == 0:
                return False
            return True

        if intent == "accounting_operational":
            if (
                signals.community_hits > 0
                and signals.accounting_hits == 0
                and signals.accounting_context_hits == 0
                and signals.operational_hits == 0
                and not signals.explicit_how_to
            ):
                return False
            return True

        if intent == "legal_procedural":
            if (
                signals.legal_decision_hits > 0
                and signals.permission_hits == 0
                and signals.system_hits == 0
                and signals.operational_hits == 0
                and not signals.explicit_how_to
            ):
                return False
            return True

        return True
    if intent not in WORKFLOW_CONDITIONAL_INTENTS:
        return False

    if intent in {"pit_ryczalt", "cit_wht"}:
        if (
            signals.legal_decision_hits > 0
            and signals.accounting_hits == 0
            and signals.accounting_context_hits == 0
            and not signals.explicit_how_to
        ):
            return False
        return (
            signals.accounting_hits >= 1
            or signals.accounting_context_hits >= 1
            or signals.explicit_how_to
        )

    if intent in {"vat_jpk_ksef", "zus"}:
        if signals.legal_decision_hits > 0 and not signals.explicit_how_to and signals.permission_hits > 0:
            return False
        return (
            (
                signals.explicit_how_to
                and (
                    signals.operational_hits > 0
                    or signals.permission_hits > 0
                    or signals.accounting_hits > 0
                )
            )
            or (
                signals.operational_hits > 0
                and (
                    signals.accounting_hits >= 1
                    or signals.system_hits >= 1
                    or signals.permission_hits >= 1
                )
            )
            or (signals.system_hits >= 1 and signals.issue_hits >= 1)
            or (signals.accounting_hits >= 2 and signals.system_hits >= 1)
        )

    return signals.operational_hits > 0


def _score_document(query_tokens: frozenset[str], document: WorkflowDocument, signals: WorkflowQuerySignals) -> float:
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

    area_text = _normalize(document.chunk.workflow_area)
    if signals.accounting_hits > 0 and _contains_marker(area_text, frozenset(area_text.split()), "kpir"):
        score += WORKFLOW_PATH_STRONG_MATCH_BONUS
    if signals.accounting_hits > 0 and _contains_marker(area_text, frozenset(area_text.split()), "ksieg"):
        score += WORKFLOW_PATH_STRONG_MATCH_BONUS
    if signals.permission_hits > 0 and (
        "authorization" in area_text or "uprawnien" in area_text or "pelnomocnictwa" in area_text
    ):
        score += WORKFLOW_PATH_STRONG_MATCH_BONUS
    if signals.system_hits > 0 and system_overlap >= 1:
        score += 1.5
    if signals.legal_guard_hits >= 2 and signals.operational_hits == 0:
        score -= WORKFLOW_LEGAL_GUARD_PENALTY
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
    signals = _collect_query_signals(query)
    if not query_tokens:
        return WorkflowRetrievalResult(chunks=[], confident=False, top_score=0.0)

    ranked = sorted(
        (
            (_score_document(query_tokens, document, signals), document.chunk)
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
    required_threshold = confidence_threshold
    if signals.accounting_hits >= 1 or signals.permission_hits >= 1 or signals.operational_hits >= 2:
        required_threshold = max(4.5, confidence_threshold - 1.0)
    if signals.legal_guard_hits >= 2 and signals.issue_hits == 0 and signals.operational_hits <= 1:
        required_threshold = confidence_threshold + WORKFLOW_HIGH_CONFIDENCE_DELTA

    return WorkflowRetrievalResult(
        chunks=selected,
        confident=bool(selected) and top_score >= required_threshold,
        top_score=top_score,
    )
