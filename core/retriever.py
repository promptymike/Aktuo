from __future__ import annotations

import math
import logging
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from rank_bm25 import BM25Okapi

from aktuo.synonym_mapper import expand_query, load_synonym_map
from config.settings import (
    CLARIFICATION_SLOTS_PATH,
    INTENT_TAXONOMY_PATH,
    RRF_BM25_K,
    RRF_VECTOR_K,
    SLANG_FILE_PATH,
)
from core.categorizer import categorize_query
from core.intent_router import classify_intent, detect_clarification_slots
from data.ingest import load_seed_laws


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
    "jako",
    "tylko",
    "tez",
    "juz",
    "ten",
    "ta",
    "te",
    "tego",
    "tej",
    "tym",
    "tych",
    "temu",
    "ich",
    "jego",
    "jej",
}

CATEGORY_SYNONYM_MAP: dict[str, tuple[str, ...]] = {
    "jpk": ("jednolity", "plik", "kontrolny"),
    "ksef": ("krajowy", "system", "e", "faktur"),
    "vat": ("podatek", "towarow", "uslug"),
    "pit": ("podatek", "dochodowy", "osob", "fizycznych"),
    "cit": ("podatek", "dochodowy", "osob", "prawnych"),
    "zus": ("ubezpieczen", "spolecznych"),
    "jdg": ("jednoosobowa", "dzialalnosc", "gospodarcza"),
    "kpir": ("ksiega", "przychodow", "rozchodow"),
    "sf": ("sprawozdanie", "finansowe"),
    "gtu": ("oznaczenie", "gtu", "jpk"),
    "wdt": ("wewnatrzwspolnotowa", "dostawa", "towarow"),
    "wnt": ("wewnatrzwspolnotowe", "nabycie", "towarow"),
    "wht": ("podatek", "zrodla"),
    "dra": ("deklaracja", "zus", "dra"),
    "rca": ("raport", "zus", "rca"),
    "rsa": ("raport", "zus", "rsa"),
    "pit11": ("pit", "11", "formularz"),
    "pit4r": ("pit", "4r", "formularz"),
    "cit8": ("cit", "8", "formularz"),
    "krs": ("krajowy", "rejestr", "sadowy"),
    "nip": ("numer", "identyfikacji", "podatkowej"),
    "bhp": ("bezpieczenstwo", "higiena", "pracy"),
    "pue": ("platforma", "uslug", "elektronicznych", "zus"),
    "pfron": ("fundusz", "rehabilitacji", "niepelnosprawnych"),
    "skwp": ("stowarzyszenie", "ksiegowych", "polsce"),
    "kup": ("koszty", "uzyskania", "przychodu"),
    "wew": ("dokument", "wewnetrzny", "jpk"),
    "ro": ("oznaczenie", "ro", "jpk"),
    "fp": ("oznaczenie", "fp", "jpk"),
    "mpp": ("mechanizm", "podzielonej", "platnosci"),
    "tp": ("transakcje", "powiazane", "ceny", "transferowe"),
    "sw": ("sprzedaz", "wysylkowa"),
    "ee": ("uslugi", "elektroniczne"),
    "bfk": ("oznaczenie", "bfk", "jpk", "ksef"),
    "di": ("oznaczenie", "di", "jpk", "ksef"),
    "mr_t": ("marza", "turystyka"),
    "mr_uz": ("marza", "towary", "uzywane"),
    "estonczyk": ("estonski", "cit"),
    "zusik": ("zus", "ubezpieczen", "spolecznych"),
}

CATEGORY_BOOST = 3.0
CATEGORY_MIN_RESULTS = 3
CATEGORY_CANDIDATE_POOL = 20


@dataclass(slots=True)
class LawChunk:
    content: str
    law_name: str
    article_number: str
    category: str
    verified_date: str
    question_intent: str = ""
    score: float = 0.0


@dataclass(slots=True)
class RetrievalResult:
    """Structured retrieval outcome used by the app-facing RAG layer."""

    chunks: list[LawChunk]
    intent: str
    needs_clarification: bool = False
    missing_slots: list[str] | None = None


_CACHE_LOCK = Lock()
_KNOWLEDGE_CACHE: dict[
    str,
    tuple[
        int,
        tuple[LawChunk, ...],
        BM25Okapi,
        tuple[tuple[str, ...], ...],
        tuple[Counter[str], ...],
        tuple[float, ...],
    ],
] = {}
_SLANG_CACHE: tuple[str, dict[str, list[str]]] | None = None
LOGGER = logging.getLogger(__name__)


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
    return "".join(character for character in normalized if not unicodedata.combining(character))


def load_slang_map() -> dict[str, list[str]]:
    """Load and cache the slang expansion map used for query expansion.

    The file path is read from :mod:`config.settings`. Missing files are treated
    as an optional feature and result in an empty mapping. Malformed files are
    logged as warnings and also fall back to an empty mapping.

    Returns:
        A dictionary mapping slang terms to their expanded forms.
    """

    global _SLANG_CACHE

    slang_file = SLANG_FILE_PATH
    with _CACHE_LOCK:
        if _SLANG_CACHE and _SLANG_CACHE[0] == slang_file:
            return dict(_SLANG_CACHE[1])

    if not slang_file:
        slang_map: dict[str, list[str]] = {}
    else:
        try:
            slang_map = load_synonym_map(slang_file)
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                slang_map = {}
            else:
                LOGGER.warning(
                    "Could not load slang map from %s. Query expansion disabled: %s",
                    slang_file,
                    exc,
                )
                slang_map = {}

    with _CACHE_LOCK:
        _SLANG_CACHE = (slang_file, dict(slang_map))

    return dict(slang_map)


def _classify_intent_with_fallback(query: str, taxonomy_path: str = INTENT_TAXONOMY_PATH) -> str:
    """Classify intent using the curated taxonomy with a safe warning fallback."""

    try:
        return classify_intent(query, taxonomy_path)
    except ValueError as exc:
        LOGGER.warning("Could not load curated taxonomy from %s: %s", taxonomy_path, exc)
        return "unknown"


def _detect_missing_slots(
    query: str,
    intent: str,
    slots_path: str = CLARIFICATION_SLOTS_PATH,
) -> list[str]:
    """Return missing clarification slots for an intent, falling back safely on file errors."""

    if intent == "unknown":
        return []

    try:
        missing_map = detect_clarification_slots(query, slots_path, intent)
    except ValueError as exc:
        LOGGER.warning("Could not load clarification slots from %s: %s", slots_path, exc)
        return []

    return [slot_name for slot_name, is_missing in missing_map.items() if is_missing]


def _should_require_clarification(query: str, missing_slots: list[str], intent: str) -> bool:
    """Return True when a query clearly lacks the context required to answer.

    The gate fires in two tiers:

    1. **Two or more missing slots** → always require clarification regardless
       of query length or specificity tokens.  This is safe because no
       ``answer_directly`` golden-set record has two or more missing required
       facts — they always supply enough context.

    2. **Exactly one missing slot** → only require clarification for very short
       or generic queries (≤ 6 tokens or a generic "jak rozliczyć" prefix) to
       avoid over-blocking specific questions that merely omit one fact.
    """

    if not missing_slots:
        return False

    # Tier 1: always fire when two or more required facts are absent.
    if len(missing_slots) >= 2:
        return True

    # Tier 2: exactly one missing slot — only for very short / generic queries.
    normalized_query = _normalize(query)
    query_tokens = re.findall(r"[a-z0-9_]+", normalized_query)

    generic_prefixes = (
        "jak rozliczyc",
        "jak rozliczyć",
        "co zrobic",
        "co zrobić",
        "jak ujac",
        "jak ująć",
        "jak zaksi",
        "czy mozna",
        "czy można",
    )

    return len(query_tokens) <= 6 or normalized_query.startswith(generic_prefixes)


def _tokenize(text: str) -> list[str]:
    normalized = _normalize(text)
    tokens = re.findall(r"[a-z0-9_]+", normalized)
    expanded_tokens: list[str] = []
    for token in tokens:
        if token not in POLISH_STOP_WORDS:
            expanded_tokens.append(token)
        expanded_tokens.extend(
            synonym
            for synonym in CATEGORY_SYNONYM_MAP.get(token, ())
            if synonym not in POLISH_STOP_WORDS
        )
    return expanded_tokens


def _category_matches(query_category: str, chunk: LawChunk) -> bool:
    if chunk.category == query_category:
        return True

    law_name = _normalize(chunk.law_name)
    category_name = _normalize(chunk.category)

    broad_law_aliases = {
        "ksef": (
            "krajowy system e-faktur",
            "rozporzadzenie ksef",
            "ustawa o vat - ksef",
        ),
        "vat": (
            "ustawa o vat",
            "podatek od towarow i uslug",
            "rozporzadzenie mf o kasach rejestrujacych",
        ),
        "pit": (
            "ustawa o podatku dochodowym od osob fizycznych",
            "ustawa o zryczaltowanym podatku dochodowym",
        ),
        "cit": (
            "ustawa o podatku dochodowym od osob prawnych",
        ),
        "zus": (
            "ustawa o systemie ubezpieczen spolecznych",
        ),
        "kadry": (
            "kodeks pracy",
        ),
        "ordynacja": (
            "ordynacja podatkowa",
        ),
        "jpk": (
            "rozporzadzenie jpk_v7",
        ),
        "rachunkowosc": (
            "ustawa o rachunkowosci",
        ),
    }

    if query_category in broad_law_aliases:
        return any(alias in law_name for alias in broad_law_aliases[query_category])

    subcategory_aliases = {
        "fakturowanie": (
            "fakturowanie",
            "faktura",
            "faktury",
            "paragon",
            "duplikat",
        ),
        "faktury_korygujące": (
            "faktury_korygujace",
            "korekta_faktury",
            "faktura korygujaca",
            "koryguj",
            "nip",
        ),
        "korekty": (
            "korekta",
            "korekty_vat",
            "ulga_na_zle_dlugi",
        ),
        "terminy": (
            "termin",
            "terminy",
            "jpk",
            "deklaracja",
            "deklaracje",
        ),
        "podatek_naliczony": (
            "podatek_naliczony",
            "odliczenie_vat",
            "naliczony",
        ),
        "podatek_należny": (
            "podatek_nalezny",
            "obowiazek_podatkowy",
            "nalezny",
        ),
    }

    haystack = " ".join([category_name, law_name])
    return any(alias in haystack for alias in subcategory_aliases.get(query_category, ()))


def load_chunks(knowledge_path: str | Path) -> list[LawChunk]:
    path = Path(knowledge_path).resolve()
    mtime_ns = path.stat().st_mtime_ns
    cache_key = str(path)

    with _CACHE_LOCK:
        cached = _KNOWLEDGE_CACHE.get(cache_key)
        if cached and cached[0] == mtime_ns:
            return list(cached[1])

    records = load_seed_laws(path)
    chunks = tuple(
        LawChunk(
            content=str(record.get("answer") or record.get("content") or "").strip(),
            law_name=str(record.get("law_name", "")).strip(),
            article_number=str(record.get("article_number", "")).strip(),
            category=str(record.get("category", "")).strip(),
            verified_date=str(record.get("verified_date", "")).strip(),
            question_intent=str(record.get("question_intent", "")).strip(),
        )
        for record in records
        if str(record.get("answer") or record.get("content") or "").strip()
    )

    tokenized_corpus = tuple(
        tuple(_tokenize(" ".join(part for part in (chunk.question_intent, chunk.content) if part)))
        for chunk in chunks
    )
    vector_corpus = tuple(Counter(tokens) for tokens in tokenized_corpus)
    vector_norms = tuple(
        math.sqrt(sum(float(value * value) for value in counts.values())) or 1.0
        for counts in vector_corpus
    )
    bm25 = BM25Okapi([list(tokens) if tokens else ["_empty_"] for tokens in tokenized_corpus])

    with _CACHE_LOCK:
        _KNOWLEDGE_CACHE[cache_key] = (
            mtime_ns,
            chunks,
            bm25,
            tokenized_corpus,
            vector_corpus,
            vector_norms,
        )

    return list(chunks)


def _load_bm25_cache(
    knowledge_path: str | Path,
) -> tuple[list[LawChunk], BM25Okapi, list[tuple[str, ...]], list[Counter[str]], list[float]]:
    path = Path(knowledge_path).resolve()
    mtime_ns = path.stat().st_mtime_ns
    cache_key = str(path)

    with _CACHE_LOCK:
        cached = _KNOWLEDGE_CACHE.get(cache_key)
        if cached and cached[0] == mtime_ns:
            return list(cached[1]), cached[2], list(cached[3]), list(cached[4]), list(cached[5])

    load_chunks(path)
    with _CACHE_LOCK:
        cached = _KNOWLEDGE_CACHE[cache_key]
        return list(cached[1]), cached[2], list(cached[3]), list(cached[4]), list(cached[5])


def _build_query_variants(query: str, slang_map: dict[str, list[str]]) -> list[str]:
    """Create de-duplicated query variants using slang expansion.

    The first variant is always the fully expanded query returned by
    :func:`aktuo.synonym_mapper.expand_query` when any slang is found, followed
    by the original query and then more targeted per-slang substitutions. This
    keeps retrieval broad enough to benefit from expansion while preserving the
    original phrasing as a fallback.

    Args:
        query: Raw user query.
        slang_map: Mapping of slang terms to expanded forms.

    Returns:
        Ordered query variants with duplicates removed.
    """

    expanded_query = expand_query(query, slang_map)
    variants: list[str] = []

    def add_variant(value: str) -> None:
        candidate = value.strip()
        if candidate and candidate not in variants:
            variants.append(candidate)

    add_variant(expanded_query)
    add_variant(query)

    if expanded_query == query or not slang_map:
        return variants

    for slang, expansions in slang_map.items():
        pattern = re.compile(rf"(?<!\w)({re.escape(slang)})(?!\w)", flags=re.IGNORECASE)
        if not pattern.search(query):
            continue

        for expanded in expansions:
            variant = pattern.sub(expanded, query)
            add_variant(variant)

    return variants


def _chunk_key(chunk: LawChunk) -> tuple[str, str, str, str]:
    """Return a stable identifier for de-duplicating chunk results."""

    return (chunk.law_name, chunk.article_number, chunk.question_intent, chunk.content)


def _copy_chunk_with_score(chunk: LawChunk, score: float) -> LawChunk:
    """Create a scored copy of a cached chunk."""

    return LawChunk(
        content=chunk.content,
        law_name=chunk.law_name,
        article_number=chunk.article_number,
        category=chunk.category,
        verified_date=chunk.verified_date,
        question_intent=chunk.question_intent,
        score=score,
    )


def _score_vector_similarity(
    query_tokens: list[str],
    vector_corpus: list[Counter[str]],
    vector_norms: list[float],
) -> list[float]:
    """Compute cosine similarity scores between a query and token-frequency vectors."""

    if not query_tokens:
        return [0.0 for _ in vector_corpus]

    query_counts = Counter(query_tokens)
    query_norm = math.sqrt(sum(float(value * value) for value in query_counts.values()))
    if query_norm == 0.0:
        return [0.0 for _ in vector_corpus]

    scores: list[float] = []
    for counts, norm in zip(vector_corpus, vector_norms, strict=False):
        dot_product = sum(float(query_counts[token] * counts.get(token, 0)) for token in query_counts)
        scores.append(dot_product / (query_norm * norm) if dot_product else 0.0)
    return scores


def _merge_best_scores(
    scores: list[float],
    chunks: list[LawChunk],
    query_category: str,
    existing: dict[tuple[str, str, str, str], LawChunk] | None = None,
) -> dict[tuple[str, str, str, str], LawChunk]:
    """Merge a scoring pass into a de-duplicated best-score mapping."""

    best_scores = existing or {}
    for score, chunk in zip(scores, chunks, strict=False):
        boosted_score = float(score)
        if _category_matches(query_category, chunk):
            boosted_score *= CATEGORY_BOOST

        scored_chunk = _copy_chunk_with_score(chunk, boosted_score)
        key = _chunk_key(scored_chunk)
        previous = best_scores.get(key)
        if previous is None or boosted_score > previous.score:
            best_scores[key] = scored_chunk
    return best_scores


def _sort_ranked_chunks(chunks: dict[tuple[str, str, str, str], LawChunk]) -> list[LawChunk]:
    """Sort scored chunks from strongest to weakest."""

    return sorted(
        chunks.values(),
        key=lambda chunk: (
            chunk.score,
            chunk.verified_date,
            chunk.law_name,
            chunk.article_number,
        ),
        reverse=True,
    )


def _fuse_rankings(
    bm25_ranked: list[LawChunk],
    vector_ranked: list[LawChunk],
    bm25_k: int = RRF_BM25_K,
    vector_k: int = RRF_VECTOR_K,
) -> list[LawChunk]:
    """Fuse BM25 and vector rankings using Reciprocal Rank Fusion.

    Each chunk receives a fusion score based on its rank in each ranking:
    ``1 / (bm25_k + rank_bm25) + 1 / (vector_k + rank_vector)``.

    Args:
        bm25_ranked: Chunks ranked by BM25 relevance.
        vector_ranked: Chunks ranked by vector similarity.
        bm25_k: RRF dampening constant for BM25 ranks.
        vector_k: RRF dampening constant for vector ranks.

    Returns:
        A de-duplicated list of chunks sorted by fused RRF score.
    """

    fused: dict[tuple[str, str, str, str], tuple[float, LawChunk]] = {}

    for rank, chunk in enumerate(bm25_ranked, start=1):
        key = _chunk_key(chunk)
        fused_score, representative = fused.get(key, (0.0, chunk))
        fused[key] = (fused_score + (1.0 / (bm25_k + rank)), representative)

    for rank, chunk in enumerate(vector_ranked, start=1):
        key = _chunk_key(chunk)
        fused_score, representative = fused.get(key, (0.0, chunk))
        if chunk.score > representative.score:
            representative = chunk
        fused[key] = (fused_score + (1.0 / (vector_k + rank)), representative)

    fused_chunks = [
        _copy_chunk_with_score(chunk, fused_score)
        for fused_score, chunk in fused.values()
    ]
    fused_chunks.sort(
        key=lambda chunk: (
            chunk.score,
            chunk.verified_date,
            chunk.law_name,
            chunk.article_number,
        ),
        reverse=True,
    )
    return fused_chunks


def _select_category_aware_results(
    scored: list[tuple[float, LawChunk]], query_category: str, limit: int
) -> list[LawChunk]:
    top_candidates = scored[: max(limit, CATEGORY_CANDIDATE_POOL)]

    if query_category == "ogólne":
        return [chunk for _, chunk in top_candidates[:limit]]

    matching_category = [
        chunk for _, chunk in top_candidates if _category_matches(query_category, chunk)
    ]
    if not matching_category:
        return [chunk for _, chunk in top_candidates[:limit]]

    others = [chunk for _, chunk in top_candidates if not _category_matches(query_category, chunk)]

    guaranteed = matching_category[: min(CATEGORY_MIN_RESULTS, len(matching_category))]
    remaining_slots = max(limit - len(guaranteed), 0)
    selected = guaranteed + others[:remaining_slots]

    if len(selected) < limit:
        selected.extend(matching_category[len(guaranteed) : len(guaranteed) + (limit - len(selected))])

    return selected[:limit]


def _retrieve_ranked_chunks(query: str, knowledge_path: str | Path, limit: int = 5) -> list[LawChunk]:
    """Retrieve the most relevant legal chunks for a user query.

    The retriever expands accountant slang and abbreviations before scoring.
    It then ranks documents with both BM25 and lightweight vector similarity
    (cosine similarity over token-frequency vectors) and fuses the two rankings
    using Reciprocal Rank Fusion (RRF). When expansion produces multiple useful
    query variants, each method keeps the best score per chunk across variants
    before fusion.

    Args:
        query: User query in natural language.
        knowledge_path: Path to the JSON knowledge base file.
        limit: Maximum number of chunks to return.

    Returns:
        A ranked list of matching knowledge chunks.
    """

    chunks, bm25, _, vector_corpus, vector_norms = _load_bm25_cache(knowledge_path)
    slang_map = load_slang_map()
    query_variants = _build_query_variants(query, slang_map)
    tokenized_variants = [tokens for variant in query_variants if (tokens := _tokenize(variant))]
    if not tokenized_variants:
        return []

    query_category = categorize_query(query_variants[0])
    bm25_best: dict[tuple[str, str, str, str], LawChunk] = {}
    vector_best: dict[tuple[str, str, str, str], LawChunk] = {}

    for query_tokens in tokenized_variants:
        bm25_scores = [float(score) for score in bm25.get_scores(query_tokens)]
        vector_scores = _score_vector_similarity(query_tokens, vector_corpus, vector_norms)
        bm25_best = _merge_best_scores(bm25_scores, chunks, query_category, bm25_best)
        vector_best = _merge_best_scores(vector_scores, chunks, query_category, vector_best)

    bm25_ranked = _sort_ranked_chunks(bm25_best)
    vector_ranked = _sort_ranked_chunks(vector_best)
    fused_ranked = _fuse_rankings(bm25_ranked, vector_ranked)
    scored = [(chunk.score, chunk) for chunk in fused_ranked]
    return _select_category_aware_results(scored, query_category, limit)


def retrieve(
    query: str,
    knowledge_path: str | Path,
    limit: int = 5,
    taxonomy_path: str = INTENT_TAXONOMY_PATH,
    slots_path: str = CLARIFICATION_SLOTS_PATH,
) -> RetrievalResult:
    """Retrieve chunks with a lightweight intent and clarification pre-check.

    Args:
        query: Raw user query.
        knowledge_path: Path to the JSON knowledge base file.
        limit: Maximum number of chunks to return.
        taxonomy_path: Path to the curated intent taxonomy file.
        slots_path: Path to the curated clarification slots file.

    Returns:
        A structured retrieval result. When required clarification slots are
        missing, retrieval is skipped and ``needs_clarification`` is set.
    """

    intent = _classify_intent_with_fallback(query, taxonomy_path)
    missing_slots = _detect_missing_slots(query, intent, slots_path)
    if _should_require_clarification(query, missing_slots, intent):
        return RetrievalResult(
            chunks=[],
            intent=intent,
            needs_clarification=True,
            missing_slots=missing_slots,
        )

    return RetrievalResult(
        chunks=_retrieve_ranked_chunks(query, knowledge_path, limit),
        intent=intent,
        needs_clarification=False,
        missing_slots=[],
    )


def retrieve_chunks(query: str, knowledge_path: str | Path, limit: int = 5) -> list[LawChunk]:
    """Backward-compatible raw retrieval helper without clarification gating."""

    return _retrieve_ranked_chunks(query, knowledge_path, limit)
