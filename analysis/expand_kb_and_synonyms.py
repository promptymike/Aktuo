"""Scan Facebook questions to suggest KB and slang/synonym expansions.

Classifies each question using the existing retriever (no API calls) and
identifies GAP/WEAK entries.  For those, it:
- detects abbreviations not in the current slang file and suggests new mappings
- regex-matches candidate articles from parsed ``articles_*.json`` files

Usage::

    python analysis/expand_kb_and_synonyms.py --top 200
    python analysis/expand_kb_and_synonyms.py --top 50 --interactive --merge
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.categorizer import categorize_query  # noqa: E402
from core.retriever import (  # noqa: E402
    CATEGORY_SYNONYM_MAP,
    LawChunk,
    retrieve_chunks,
)

LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# RRF-calibrated thresholds (same as report_coverage_stats_after_gap_patch.py)
# ---------------------------------------------------------------------------

COVERED_THRESHOLD = 0.030
WEAK_THRESHOLD = 0.025

EXPECTED_LAW_BY_FB_CATEGORY: dict[str, tuple[str, ...]] = {
    "vat": ("ustawa o vat",),
    "pit": ("ustawa o podatku dochodowym od osób fizycznych",),
    "cit": ("ustawa o podatku dochodowym od osób prawnych",),
    "ksef": ("ksef", "ustawa o vat - ksef", "ustawa o vat"),
    "jpk": ("rozporządzenie jpk_v7", "ustawa o vat"),
    "rachunkowosc": ("ustawa o rachunkowości",),
    "kadry": ("kodeks pracy",),
    "zus": ("ustawa o systemie ubezpieczeń społecznych",),
    "ordynacja": ("ordynacja podatkowa",),
}

CATEGORY_TO_ARTICLES_STEMS: dict[str, tuple[str, ...]] = {
    "vat": ("articles_vat", "articles_kasy"),
    "pit": ("articles_pit", "articles_ryczalt"),
    "cit": ("articles_cit",),
    "ksef": ("articles_ksef", "articles_ksef_ustawa"),
    "jpk": ("articles_jpk",),
    "kadry": ("articles_kodeks_pracy",),
    "zus": ("articles_zus",),
    "ordynacja": ("articles_ordynacja",),
    "rachunkowosc": ("articles_rachunkowosc",),
}

# Tokens that look like abbreviations but are not accountant slang.
_NOISE_TOKENS: set[str] = {
    "vat", "pit", "cit", "zus", "jpk", "ksef", "nip", "bhp", "br",
    "sp", "nr", "ul", "pkt", "ust", "art", "str", "dz", "poz",
    "tj", "np", "etc", "ok", "wg", "tzn", "itp", "itd",
    "ii", "iii", "iv", "vi", "vii", "viii", "ix", "xi", "xii",
    "cv", "www", "pdf", "xls", "xlsx", "sas", "ltd", "gmbh",
    "usd", "eur", "pln", "chf", "gbp", "oo", "sa",
}

# Best-effort expansion hints for common accounting abbreviations.
_EXPANSION_HINTS: dict[str, str] = {
    "ift": "informacja o podatku u źródła",
    "ift-2r": "informacja o podatku u źródła IFT-2R",
    "ift-1r": "informacja o podatku u źródła IFT-1R",
    "pfron": "Państwowy Fundusz Rehabilitacji Osób Niepełnosprawnych",
    "krus": "Kasa Rolniczego Ubezpieczenia Społecznego",
    "pkd": "Polska Klasyfikacja Działalności",
    "pkwiu": "Polska Klasyfikacja Wyrobów i Usług",
    "cn": "nomenklatura scalona",
    "saas": "Software as a Service",
    "wdt": "wewnątrzwspólnotowa dostawa towarów",
    "wnt": "wewnątrzwspólnotowe nabycie towarów",
    "wht": "withholding tax / podatek u źródła",
    "pit40a": "formularz PIT-40A",
    "pit11": "formularz PIT-11",
    "pit4r": "formularz PIT-4R",
    "cit8": "formularz CIT-8",
    "pit36": "formularz PIT-36",
    "pit37": "formularz PIT-37",
    "pit36l": "formularz PIT-36L",
    "pit28": "formularz PIT-28",
    "druk": "formularz",
    "pcc": "podatek od czynności cywilnoprawnych",
    "vat-ek": "VAT",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Normalize Polish text: lowercase, strip diacritics."""
    translation = str.maketrans(
        {"ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n",
         "ó": "o", "ś": "s", "ż": "z", "ź": "z"}
    )
    normalized = unicodedata.normalize("NFKD", text.lower().translate(translation))
    return "".join(c for c in normalized if not unicodedata.combining(c))


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_questions(dataset_path: Path) -> list[dict[str, Any]]:
    """Load and validate questions from the FB dataset.

    Raises:
        ValueError: If the file is missing, malformed, or lacks a
            ``questions`` key.
    """
    try:
        raw = json.loads(dataset_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Dataset not found: {dataset_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Malformed dataset '{dataset_path}': invalid JSON ({exc.msg})."
        ) from exc

    if not isinstance(raw, dict) or "questions" not in raw:
        raise ValueError(
            f"Expected a JSON object with a 'questions' key in {dataset_path}."
        )
    questions = raw["questions"]
    if not isinstance(questions, list):
        raise ValueError(
            f"'questions' must be a JSON array in {dataset_path}."
        )
    return questions


def load_slang(slang_path: Path) -> list[dict[str, Any]]:
    """Load existing slang entries from either the synonym-mapper format
    (``[{slang, expanded, freq}]``) or the analysis format
    (``{top_slang_terms: [{short, full_phrase, ...}]}``).

    Returns an empty list when the file is missing.
    """
    if not slang_path.exists():
        return []
    try:
        raw = json.loads(slang_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Malformed slang file '{slang_path}': invalid JSON ({exc.msg})."
        ) from exc

    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and "top_slang_terms" in raw:
        return raw["top_slang_terms"]
    raise ValueError(f"Unrecognised slang file format in {slang_path}.")


def load_articles(articles_dir: Path) -> dict[str, dict[str, Any]]:
    """Load every ``articles_*.json`` file from *articles_dir*.

    Returns a mapping from file stem (e.g. ``articles_vat``) to the
    parsed JSON payload (which contains ``metadata`` and ``articles``).
    """
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(articles_dir.glob("articles_*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "articles" in data:
                result[path.stem] = data
        except (json.JSONDecodeError, OSError) as exc:
            LOGGER.warning("Skipping %s: %s", path, exc)
    return result


# ---------------------------------------------------------------------------
# Classification (matches report_coverage_stats_after_gap_patch.py logic)
# ---------------------------------------------------------------------------

def classify_question(
    source_category: str,
    chunks: list[LawChunk],
) -> tuple[str, str]:
    """Classify a question as ``COVERED`` / ``WEAK`` / ``GAP``.

    Uses the same RRF-calibrated thresholds and law-matching logic as
    :func:`analysis.report_coverage_stats_after_gap_patch.classify_top100_item`.
    """
    if not chunks:
        return "GAP", "Brak chunków."

    top_chunk = chunks[0]
    top_score = float(top_chunk.score)

    def _law_matches_category(law_name: str) -> bool:
        aliases = EXPECTED_LAW_BY_FB_CATEGORY.get(source_category)
        if not aliases:
            return False
        norm_law = _normalize(law_name)
        return any(_normalize(a) in norm_law for a in aliases)

    if source_category in EXPECTED_LAW_BY_FB_CATEGORY:
        if top_score > COVERED_THRESHOLD and _law_matches_category(top_chunk.law_name):
            return "COVERED", "Top chunk z właściwej ustawy, mocny score."
        if top_score >= WEAK_THRESHOLD and any(
            _law_matches_category(c.law_name) for c in chunks[:3]
        ):
            return "WEAK", "Właściwa ustawa w top 3, ale match nie dość mocny."
        return "GAP", "Brak trafienia we właściwą ustawę."

    if top_score >= COVERED_THRESHOLD:
        return "WEAK", "Kategoria źródłowa bez jednoznacznej ustawy, ale sensowny wynik."
    return "GAP", "Kategoria źródłowa bez jednoznacznej podstawy w KB."


# ---------------------------------------------------------------------------
# Slang detection
# ---------------------------------------------------------------------------

def build_known_abbreviations(
    slang_entries: list[dict[str, Any]],
) -> set[str]:
    """Combine known abbreviations from the retriever synonym map, the
    existing slang file, and a hardcoded noise list.
    """
    known: set[str] = set(_NOISE_TOKENS)

    for abbr in CATEGORY_SYNONYM_MAP:
        known.add(abbr.lower())

    for entry in slang_entries:
        if isinstance(entry, dict):
            short = entry.get("slang") or entry.get("short") or ""
            if short:
                known.add(short.strip().lower())

    return known


# Pattern: 2-8 uppercase letters, optionally followed by dash + digits + letters
_ABBREV_RE = re.compile(
    r"\b([A-ZĘÓĄŚŁŻŹĆŃ]{2,8}(?:-?\d+[A-Z]*)?)\b"
)


def detect_slang(
    query: str,
    known: set[str],
) -> list[str]:
    """Return abbreviation-like tokens in *query* not present in *known*."""
    tokens = _ABBREV_RE.findall(query)
    seen: set[str] = set()
    candidates: list[str] = []
    for token in tokens:
        lower = token.strip().lower()
        if lower in known or lower in seen or len(lower) < 2:
            continue
        seen.add(lower)
        candidates.append(token)
    return candidates


def suggest_expansion(token: str) -> str:
    """Return a best-effort expansion for *token*, or ``""``."""
    key = token.strip().lower().replace("-", "")
    # Check hints first (exact)
    hint = _EXPANSION_HINTS.get(key) or _EXPANSION_HINTS.get(token.strip().lower())
    if hint:
        return hint
    # Prefix match for form numbers (PIT36L -> formularz PIT-36L)
    form_match = re.match(r"^(pit|cit|vat|ift|pcc|sd)(\d.*)$", key, re.IGNORECASE)
    if form_match:
        prefix = form_match.group(1).upper()
        suffix = form_match.group(2).upper()
        return f"formularz {prefix}-{suffix}"
    return ""


# ---------------------------------------------------------------------------
# Candidate article search
# ---------------------------------------------------------------------------

_QUERY_STOP_WORDS: set[str] = {
    "jest", "czy", "jak", "kiedy", "gdzie", "moze", "trzeba", "musi",
    "powinien", "bedzie", "bylo", "byly", "ktora", "ktory", "ktore",
    "tego", "temu", "nich", "tylko", "jeszcze", "jaka", "jaki",
    "ktos", "dlaczego", "bardzo", "prosz", "pomoc", "szukam",
    "dzien", "dobry", "pozdrawiam", "dobrze", "teraz", "jesli",
    "jakies", "jakie", "takze", "jestem", "mamy", "bylo",
    "prawda", "zeby", "taki", "takie", "takiej", "jakas",
}

# Crude Polish pseudo-stemming: truncate tokens to this length to capture
# inflectional variants (e.g. "subskrypcja" ↔ "subskrypcje").
_STEM_LEN = 6


def find_candidate_articles(
    query: str,
    source_category: str,
    articles_db: dict[str, dict[str, Any]],
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Locate up to *limit* candidate articles matching the query.

    Scoring heuristic:
    - +10 for a direct article/section number reference match
    - +1 per content keyword shared between query and article text
    """
    stems = CATEGORY_TO_ARTICLES_STEMS.get(source_category)
    if not stems:
        stems = tuple(articles_db.keys())

    # Regex: extract article and section references from the query
    article_refs = re.findall(r"art\.\s*(\d+[a-z]*)", query, re.IGNORECASE)
    section_refs = re.findall(r"§\s*(\d+[a-z]*)", query)

    query_norm = _normalize(query)
    raw_words = set(re.findall(r"[a-z]{4,}", query_norm)) - _QUERY_STOP_WORDS
    query_words = {w[:_STEM_LEN] for w in raw_words}

    candidates: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()

    for stem in stems:
        file_data = articles_db.get(stem)
        if not file_data:
            continue

        law_name = file_data.get("metadata", {}).get("law_name", stem)
        articles = file_data.get("articles", [])

        for article in articles:
            if article.get("is_repealed"):
                continue

            art_num = str(article.get("article_number", ""))
            full_id = str(article.get("full_id", ""))
            raw_text = str(article.get("raw_text", ""))

            key = (_normalize(law_name), art_num)
            if key in seen_keys:
                continue

            score = 0
            reason_parts: list[str] = []

            for ref in article_refs:
                if art_num == ref or art_num.startswith(ref):
                    score += 10
                    reason_parts.append(f"article ref art. {ref}")
            for ref in section_refs:
                if art_num == ref:
                    score += 10
                    reason_parts.append(f"section ref § {ref}")

            text_norm = _normalize(raw_text)
            text_stems = {w[:_STEM_LEN] for w in re.findall(r"[a-z]{4,}", text_norm)}
            matching_words = query_words & text_stems
            if matching_words:
                score += len(matching_words)
                if len(matching_words) >= 2:
                    reason_parts.append(
                        f"keywords: {', '.join(sorted(matching_words)[:5])}"
                    )

            if score > 0:
                seen_keys.add(key)
                reason = "; ".join(reason_parts) if reason_parts else (
                    f"matched {len(matching_words)} keywords"
                )
                candidates.append({
                    "law_name": law_name,
                    "article_number": full_id,
                    "category": source_category,
                    "content": raw_text[:600],
                    "score": score,
                    "reason": reason,
                })

    if not candidates:
        LOGGER.debug(
            "No candidate articles for category=%s, query=%.60s",
            source_category,
            query,
        )

    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates[:limit]


# ---------------------------------------------------------------------------
# Main analysis loop
# ---------------------------------------------------------------------------

def run(
    dataset_path: Path,
    law_units_path: Path,
    slang_path: Path,
    articles_dir: Path,
    *,
    top_n: int = 200,
    min_freq: int = 1,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Analyse the top-*top_n* questions and return expansion proposals.

    Returns:
        ``(proposed_units, proposed_synonyms)`` – two JSON-serialisable
        lists sorted by relevance / frequency.
    """

    questions = load_questions(dataset_path)
    slang_entries = load_slang(slang_path)
    articles_db = load_articles(articles_dir)
    known_abbrs = build_known_abbreviations(slang_entries)

    questions.sort(key=lambda q: int(q.get("freq", 0)), reverse=True)
    questions = questions[:top_n]

    # Build set of (normalised law_name, normalised article_number) already
    # present in the KB so we can skip duplicates.
    try:
        kb_records: list[dict[str, Any]] = json.loads(
            law_units_path.read_text(encoding="utf-8")
        )
    except (FileNotFoundError, json.JSONDecodeError):
        kb_records = []
    existing_kb_keys: set[tuple[str, str]] = {
        (_normalize(str(r.get("law_name", ""))),
         _normalize(str(r.get("article_number", ""))))
        for r in kb_records
    }

    proposed_units_map: dict[tuple[str, str], dict[str, Any]] = {}
    slang_map: dict[str, dict[str, Any]] = {}
    gap_weak_count = 0

    for i, q_data in enumerate(questions, 1):
        query = str(q_data.get("q", "")).strip()
        source_cat = str(q_data.get("cat", "")).strip()
        freq = int(q_data.get("freq", 0))

        if not query or freq < min_freq:
            continue

        chunks = retrieve_chunks(query, str(law_units_path), limit=3)
        verdict, _reason = classify_question(source_cat, chunks)

        if verdict == "COVERED":
            continue

        gap_weak_count += 1

        # --- Slang detection ---
        for slang_token in detect_slang(query, known_abbrs):
            key = slang_token.lower()
            if key not in slang_map:
                slang_map[key] = {
                    "slang": slang_token,
                    "expanded": suggest_expansion(slang_token),
                    "source_questions": [],
                    "total_freq": 0,
                }
            entry = slang_map[key]
            if len(entry["source_questions"]) < 5:
                entry["source_questions"].append(query[:200])
            entry["total_freq"] += freq

        # --- Candidate articles ---
        for candidate in find_candidate_articles(
            query, source_cat, articles_db, limit=3
        ):
            art_key = (
                _normalize(candidate["law_name"]),
                _normalize(candidate["article_number"]),
            )
            if art_key in existing_kb_keys:
                continue
            if art_key not in proposed_units_map:
                proposed_units_map[art_key] = {
                    "law_name": candidate["law_name"],
                    "article_number": candidate["article_number"],
                    "category": candidate["category"],
                    "content": candidate["content"],
                    "source_questions": [],
                    "reason": candidate["reason"],
                }
            unit_entry = proposed_units_map[art_key]
            if len(unit_entry["source_questions"]) < 5:
                unit_entry["source_questions"].append(query[:200])

        if i % 50 == 0:
            LOGGER.info("  ... processed %d/%d questions", i, len(questions))

    proposed_units = sorted(
        proposed_units_map.values(),
        key=lambda u: len(u.get("source_questions", [])),
        reverse=True,
    )
    proposed_synonyms = sorted(
        slang_map.values(),
        key=lambda s: s.get("total_freq", 0),
        reverse=True,
    )

    LOGGER.info(
        "Done: %d questions, %d GAP/WEAK, %d proposed units, %d proposed synonyms",
        len(questions),
        gap_weak_count,
        len(proposed_units),
        len(proposed_synonyms),
    )
    return proposed_units, proposed_synonyms


# ---------------------------------------------------------------------------
# Interactive review
# ---------------------------------------------------------------------------

def _interactive_review(
    items: list[dict[str, Any]],
    label: str,
) -> list[dict[str, Any]]:
    """Prompt the user to approve or reject each item.

    Responses:
    - ``y`` – approve
    - ``n`` or Enter – skip
    - ``q`` – stop reviewing and return approved items so far
    """
    approved: list[dict[str, Any]] = []
    for i, item in enumerate(items, 1):
        print(f"\n{'=' * 60}")
        print(f"[{label} {i}/{len(items)}]")
        preview = json.dumps(item, ensure_ascii=False, indent=2)
        print(preview[:600])
        if len(preview) > 600:
            print("  ...")
        response = input("Approve? [y/N/q] ").strip().lower()
        if response == "q":
            break
        if response == "y":
            approved.append(item)
    return approved


# ---------------------------------------------------------------------------
# Merge helpers
# ---------------------------------------------------------------------------

def merge_kb_units(
    law_units_path: Path,
    new_units: list[dict[str, Any]],
) -> int:
    """Append *new_units* to the KB file and return the count added."""
    try:
        kb: list[dict[str, Any]] = json.loads(
            law_units_path.read_text(encoding="utf-8")
        )
    except (FileNotFoundError, json.JSONDecodeError):
        kb = []

    count = 0
    for unit in new_units:
        kb.append({
            "law_name": unit["law_name"],
            "article_number": unit["article_number"],
            "category": unit["category"],
            "verified_date": "",
            "question_intent": f"{unit['law_name']} | {unit['article_number']}",
            "content": unit["content"],
            "source": "expand_kb_and_synonyms",
        })
        count += 1

    law_units_path.write_text(
        json.dumps(kb, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return count


def merge_synonyms(
    slang_path: Path,
    new_synonyms: list[dict[str, Any]],
) -> int:
    """Append *new_synonyms* to the slang file (``load_synonym_map`` format)
    and return the count added.  Entries without an ``expanded`` value are
    silently skipped.
    """
    try:
        existing: list[dict[str, Any]] = json.loads(
            slang_path.read_text(encoding="utf-8")
        )
        if not isinstance(existing, list):
            existing = []
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []

    count = 0
    for syn in new_synonyms:
        if not syn.get("expanded"):
            continue
        existing.append({
            "slang": syn["slang"],
            "expanded": syn["expanded"],
            "freq": syn.get("total_freq", 1),
        })
        count += 1

    slang_path.write_text(
        json.dumps(existing, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return count


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Expand KB and synonym dictionary from FB questions."
    )
    parser.add_argument(
        "--dataset", type=Path,
        default=ROOT / "fb_pipeline" / "dedup_questions_output_v3.json",
        help="Path to the deduplicated FB questions JSON.",
    )
    parser.add_argument(
        "--kb", type=Path,
        default=ROOT / "data" / "seeds" / "law_knowledge.json",
        help="Path to the law_knowledge.json KB file.",
    )
    parser.add_argument(
        "--slang", type=Path,
        default=ROOT / "tests" / "output" / "slang_analysis.json",
        help="Path to the current slang/synonym file.",
    )
    parser.add_argument(
        "--articles-dir", type=Path,
        default=ROOT / "kb-pipeline" / "output",
        help="Directory containing articles_*.json files.",
    )
    parser.add_argument(
        "--top", type=int, default=200,
        help="Number of top-frequency questions to process (default: 200).",
    )
    parser.add_argument(
        "--min-freq", type=int, default=1,
        help="Minimum question frequency to include (default: 1).",
    )
    parser.add_argument(
        "--interactive", action="store_true",
        help="Review and approve each suggestion interactively.",
    )
    parser.add_argument(
        "--merge", action="store_true",
        help="Append approved items to the KB and slang files.",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "analysis",
        help="Directory for proposal output files.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    proposed_units, proposed_synonyms = run(
        dataset_path=args.dataset,
        law_units_path=args.kb,
        slang_path=args.slang,
        articles_dir=args.articles_dir,
        top_n=args.top,
        min_freq=args.min_freq,
    )

    if args.interactive:
        proposed_units = _interactive_review(proposed_units, "KB Unit")
        proposed_synonyms = _interactive_review(proposed_synonyms, "Synonym")

    units_path = args.output_dir / "proposed_kb_units.json"
    synonyms_path = args.output_dir / "proposed_synonyms.json"

    units_path.write_text(
        json.dumps(proposed_units, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    synonyms_path.write_text(
        json.dumps(proposed_synonyms, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"\nProposed KB units:  {len(proposed_units)} -> {units_path}")
    print(f"Proposed synonyms:  {len(proposed_synonyms)} -> {synonyms_path}")

    if args.merge:
        kb_merged = merge_kb_units(args.kb, proposed_units)
        syn_merged = merge_synonyms(args.slang, proposed_synonyms)
        print(f"\nMerged {kb_merged} KB units and {syn_merged} synonyms.")


if __name__ == "__main__":
    main()
