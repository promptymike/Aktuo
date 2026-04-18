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
    WORKFLOW_DRAFTS_DIR,
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


_POLISH_SUFFIXES = tuple(
    sorted(
        {
            "iejsze", "iejszy", "iejsza", "iejszych",
            "owego", "owemu", "owych", "owymi", "owska", "owski",
            "ejsze", "ejszy", "ejsza",
            "owie", "owym", "owej",
            "ego", "emu", "ymi", "imi", "owi", "owa", "owe", "owy",
            "ami", "ach", "iem", "iam",
            "om", "ej", "ie", "ia", "iu", "ym", "im", "um", "mu", "em",
            "y", "i", "a", "e", "u", "o",
        },
        key=len,
        reverse=True,
    )
)


def _stem(token: str, min_stem_len: int = 4) -> str:
    """Strip one common Polish declension suffix, preserving a minimum stem length."""

    for suffix in _POLISH_SUFFIXES:
        if len(suffix) < len(token) and token.endswith(suffix):
            stem = token[: -len(suffix)]
            if len(stem) >= min_stem_len:
                return stem
    return token


def _tokenize(text: str) -> frozenset[str]:
    base = [
        token
        for token in _normalize(text).split()
        if token and token not in POLISH_STOP_WORDS
    ]
    stems = [_stem(token) for token in base]
    return frozenset(base) | frozenset(stems)


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


def _as_clean_tuple(values: object) -> tuple[str, ...]:
    """Normalize workflow seed list-like fields into stripped string tuples."""

    if not isinstance(values, list):
        return ()
    cleaned = [str(value).strip() for value in values if str(value).strip()]
    return tuple(cleaned)


def _render_answer_steps(answer_steps: object) -> tuple[str, ...]:
    """Flatten workflow_draft `answer_steps` dicts into legacy-compatible step strings."""

    if not isinstance(answer_steps, list):
        return ()
    rendered: list[str] = []
    for entry in answer_steps:
        if not isinstance(entry, dict):
            text = str(entry).strip()
            if text:
                rendered.append(text)
            continue
        action = str(entry.get("action", "")).strip()
        detail = str(entry.get("detail", "")).strip()
        condition = str(entry.get("condition") or "").strip()
        parts = [part for part in (action, detail) if part]
        if condition:
            parts.append(f"(warunek: {condition})")
        if parts:
            rendered.append(" — ".join(parts))
    return tuple(rendered)


def _render_legal_anchors(legal_anchors: object) -> tuple[str, ...]:
    """Flatten heterogeneous legal_anchors dicts (v1/v2 schema) into display strings."""

    if not isinstance(legal_anchors, list):
        return ()
    rendered: list[str] = []
    for entry in legal_anchors:
        if not isinstance(entry, dict):
            text = str(entry).strip()
            if text:
                rendered.append(text)
            continue
        law_name = str(entry.get("law_name") or entry.get("full_name") or entry.get("short_name") or "").strip()
        article = str(entry.get("article_number") or entry.get("short_name") or "").strip()
        reason = str(entry.get("reason") or entry.get("description") or "").strip()
        head = " ".join(part for part in (law_name, article) if part).strip()
        if head and reason:
            rendered.append(f"{head} — {reason}")
        elif head:
            rendered.append(head)
        elif reason:
            rendered.append(reason)
    return tuple(rendered)


def _build_draft_content(record: dict[str, object]) -> str:
    """Render a workflow_draft (new schema) into plain context text for the generator."""

    title = str(record.get("title", "")).strip()
    topic_area = str(record.get("topic_area", "")).strip()
    steps = _render_answer_steps(record.get("answer_steps"))
    legal = _render_legal_anchors(record.get("legal_anchors"))
    edge_cases = _as_clean_tuple(record.get("edge_cases", []))
    mistakes = _as_clean_tuple(record.get("common_mistakes", []))

    parts = []
    if topic_area:
        parts.append(f"Workflow area: {topic_area}")
    if title:
        parts.append(f"Title: {title}")
    if steps:
        parts.append("Steps: " + " ".join(f"{i}. {step}" for i, step in enumerate(steps, start=1)))
    if legal:
        parts.append("Legal anchors: " + "; ".join(legal))
    if edge_cases:
        parts.append("Edge cases: " + "; ".join(edge_cases))
    if mistakes:
        parts.append("Common pitfalls: " + "; ".join(mistakes))
    return "\n".join(part for part in parts if part.strip())


def _build_document_from_legacy_seed(record: dict[str, object]) -> WorkflowDocument:
    """Build WorkflowDocument from legacy workflow_seed.json record (v1 schema)."""

    return WorkflowDocument(
        chunk=LawChunk(
            content=_build_workflow_content(record),
            law_name="Workflow layer",
            article_number=str(record.get("title", "")).strip(),
            category=str(record.get("category", "")).strip(),
            verified_date="",
            effective_from="",
            effective_to="",
            source_url="",
            source_hash="",
            last_verified_at="",
            question_intent=" | ".join(str(item).strip() for item in record.get("question_examples", [])[:3]),
            source_type=str(record.get("source_type", "workflow_seed_v1")).strip() or "workflow_seed_v1",
            workflow_area=str(record.get("workflow_area", "")).strip(),
            title=str(record.get("title", "")).strip(),
            workflow_steps=_as_clean_tuple(record.get("steps", [])),
            workflow_required_inputs=_as_clean_tuple(record.get("required_inputs", [])),
            workflow_common_pitfalls=_as_clean_tuple(record.get("common_pitfalls", [])),
            workflow_related_forms=_as_clean_tuple(record.get("related_forms", [])),
            workflow_related_systems=_as_clean_tuple(record.get("related_systems", [])),
        ),
        title_tokens=_tokenize(str(record.get("title", ""))),
        area_tokens=_tokenize(str(record.get("workflow_area", ""))),
        example_tokens=_tokenize(" ".join(str(item) for item in record.get("question_examples", []))),
        form_tokens=_tokenize(" ".join(str(item) for item in record.get("related_forms", []))),
        system_tokens=_tokenize(" ".join(str(item) for item in record.get("related_systems", []))),
        category_tokens=_tokenize(str(record.get("category", ""))),
    )


def _build_document_from_draft(record: dict[str, object]) -> WorkflowDocument:
    """Build WorkflowDocument from workflow_drafts/*.json record (v2 schema)."""

    title = str(record.get("title", "")).strip()
    topic_area = str(record.get("topic_area", "")).strip()
    draft_id = str(record.get("id", "")).strip()
    steps = _render_answer_steps(record.get("answer_steps"))
    legal = _render_legal_anchors(record.get("legal_anchors"))
    edge_cases = _as_clean_tuple(record.get("edge_cases", []))
    mistakes = _as_clean_tuple(record.get("common_mistakes", []))
    question_examples = record.get("question_examples", [])
    # common_mistakes + edge_cases bundled as pitfalls for legacy UI hooks
    pitfalls = tuple(list(mistakes) + [f"Edge case: {ec}" for ec in edge_cases])

    # Rich body text (answer_steps details + edge_cases + common_mistakes) is folded
    # into example_tokens so queries that use morphologically different forms than
    # `title`/`question_examples` can still match via the draft's body text.
    body_tokenization_source = " ".join(
        [
            " ".join(str(item) for item in question_examples),
            " ".join(steps),
            " ".join(edge_cases),
            " ".join(mistakes),
        ]
    )

    return WorkflowDocument(
        chunk=LawChunk(
            content=_build_draft_content(record),
            law_name="Workflow draft",
            article_number=draft_id or title,
            category=topic_area,
            verified_date=str(record.get("last_verified_at", "")).strip(),
            effective_from="",
            effective_to="",
            source_url="",
            source_hash="",
            last_verified_at=str(record.get("last_verified_at", "")).strip(),
            question_intent=" | ".join(str(item).strip() for item in question_examples[:3]),
            source_type="workflow_draft_v2",
            workflow_area=topic_area,
            title=title,
            workflow_steps=steps,
            workflow_required_inputs=(),
            workflow_common_pitfalls=pitfalls,
            workflow_related_forms=(),
            workflow_related_systems=(),
        ),
        title_tokens=_tokenize(title),
        area_tokens=_tokenize(" ".join([topic_area, title])),
        example_tokens=_tokenize(body_tokenization_source),
        form_tokens=_tokenize(" ".join(legal)),
        system_tokens=frozenset(),
        category_tokens=_tokenize(topic_area),
    )


def _load_legacy_seed(path: Path) -> tuple[WorkflowDocument, ...]:
    if not path.exists():
        return ()
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ()
    if not isinstance(records, list):
        return ()
    return tuple(
        _build_document_from_legacy_seed(record)
        for record in records
        if isinstance(record, dict)
        and str(record.get("title", "")).strip()
        and record.get("draft") is not True
    )


def _load_drafts_dir(drafts_dir: Path) -> tuple[WorkflowDocument, ...]:
    if not drafts_dir.exists() or not drafts_dir.is_dir():
        return ()
    documents: list[WorkflowDocument] = []
    for entry in sorted(drafts_dir.glob("wf_*.json")):
        try:
            record = json.loads(entry.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(record, dict):
            continue
        if not str(record.get("title", "")).strip():
            continue
        if "answer_steps" not in record and "steps" not in record:
            continue
        documents.append(_build_document_from_draft(record))
    return tuple(documents)


def _drafts_dir_revision(drafts_dir: Path) -> int:
    """Max mtime across wf_*.json files in drafts_dir (0 if empty/missing)."""

    if not drafts_dir.exists() or not drafts_dir.is_dir():
        return 0
    latest = 0
    for entry in drafts_dir.glob("wf_*.json"):
        try:
            mtime = entry.stat().st_mtime_ns
        except OSError:
            continue
        if mtime > latest:
            latest = mtime
    return latest


def load_workflow_documents(workflow_path: str | Path = WORKFLOW_SEED_PATH) -> list[WorkflowDocument]:
    """Load and cache workflow units as searchable documents.

    Merges two sources when invoked with the default WORKFLOW_SEED_PATH:
      - Legacy seed records from `workflow_path` (v1 schema, 10 units).
      - New drafts from `WORKFLOW_DRAFTS_DIR` (v2 schema, `wf_*.json`).

    When called with an explicit non-default `workflow_path` (e.g. test fixtures),
    only the seed file is loaded; drafts dir is skipped so tests stay isolated.
    """

    path = Path(workflow_path).resolve()
    default_seed = Path(WORKFLOW_SEED_PATH).resolve()
    merge_drafts = path == default_seed

    if not path.exists() and not merge_drafts:
        return []

    seed_mtime = path.stat().st_mtime_ns if path.exists() else 0
    drafts_dir = Path(WORKFLOW_DRAFTS_DIR).resolve() if merge_drafts else None
    drafts_rev = _drafts_dir_revision(drafts_dir) if drafts_dir is not None else 0

    cache_key = f"{path}::{drafts_dir if drafts_dir else ''}"
    cache_revision = seed_mtime + drafts_rev

    with _CACHE_LOCK:
        cached = _WORKFLOW_CACHE.get(cache_key)
        if cached and cached[0] == cache_revision:
            return list(cached[1])

    seed_docs = _load_legacy_seed(path)
    draft_docs = _load_drafts_dir(drafts_dir) if drafts_dir is not None else ()
    documents = tuple(draft_docs) + tuple(seed_docs)

    with _CACHE_LOCK:
        _WORKFLOW_CACHE[cache_key] = (cache_revision, documents)
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
            effective_from=chunk.effective_from,
            effective_to=chunk.effective_to,
            source_url=chunk.source_url,
            source_hash=chunk.source_hash,
            last_verified_at=chunk.last_verified_at,
            question_intent=chunk.question_intent,
            score=score,
            source_type=chunk.source_type,
            workflow_area=chunk.workflow_area,
            title=chunk.title,
            workflow_steps=chunk.workflow_steps,
            workflow_required_inputs=chunk.workflow_required_inputs,
            workflow_common_pitfalls=chunk.workflow_common_pitfalls,
            workflow_related_forms=chunk.workflow_related_forms,
            workflow_related_systems=chunk.workflow_related_systems,
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
