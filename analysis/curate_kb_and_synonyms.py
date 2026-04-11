"""Curate proposed KB units and synonym additions.

This script turns noisy proposal files into a small, merge-safe set of
high-quality additions for:

- ``data/seeds/law_knowledge.json``
- ``fb_pipeline/slang_analysis.json``

It supports:

- rule-based curation
- optional interactive review
- optional merge into the live files
- a compact JSON report describing impact and rejection reasons
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

KB_PATH = ROOT / "data" / "seeds" / "law_knowledge.json"
SLANG_PATH = ROOT / "fb_pipeline" / "slang_analysis.json"
PROPOSED_KB_PATH = ROOT / "analysis" / "proposed_kb_units.json"
PROPOSED_SYNONYMS_PATH = ROOT / "analysis" / "proposed_synonyms.json"

CURATED_KB_PATH = ROOT / "data" / "seeds" / "law_knowledge_curated_additions.json"
CURATED_SLANG_PATH = ROOT / "fb_pipeline" / "slang_curated_additions.json"
REPORT_PATH = ROOT / "analysis" / "curation_report.json"

MIN_CONTENT_LENGTH = 120

WEAK_CONTENT_PATTERNS: tuple[str, ...] = (
    "brak danych",
    "nie reguluje",
    "nie wynika z przepisu",
    "poza zakresem",
    "brak podstawy prawnej",
    "brak podstaw prawnych",
    "nie znalazlem odpowiedzi",
    "nie znalazłem odpowiedzi",
)

LEGAL_SIGNAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bobowi[aą]zek\b", re.IGNORECASE),
    re.compile(r"\bobowi[aą]zany\b", re.IGNORECASE),
    re.compile(r"\bpowinien\b", re.IGNORECASE),
    re.compile(r"\bpowinna\b", re.IGNORECASE),
    re.compile(r"\bprzysluguje\b|\bprzysługuje\b", re.IGNORECASE),
    re.compile(r"\bpodlega\b|\bpodlegaj[aą]\b", re.IGNORECASE),
    re.compile(r"\bzwolnion[ey]\b|\bzwalnia\b", re.IGNORECASE),
    re.compile(r"\btermin\b|\bdo dnia\b|\bdo konca\b|\bdo końca\b", re.IGNORECASE),
    re.compile(r"\bwarun(?:ek|ki)\b", re.IGNORECASE),
    re.compile(r"\bmusi\b|\bmozna\b|\bmożna\b", re.IGNORECASE),
    re.compile(r"\bstawk[aię]\b|\bkwot[ayę]\b|\blimit\b", re.IGNORECASE),
    re.compile(r"\bw przypadku\b", re.IGNORECASE),
    re.compile(r"\bjezel[iy]\b|\bjeżeli\b", re.IGNORECASE),
    re.compile(r"\bdni\b|\bmiesi[aą]c(?:a|e|y)?\b|\brok(?:u|iem)?\b", re.IGNORECASE),
)

NOISY_SYNONYMS: set[str] = {
    "apple",
    "symfonia",
    "insert",
    "comarch",
    "enova",
}

STRONG_SHORT_TOKENS: set[str] = {
    "pit",
    "cit",
    "vat",
    "zus",
    "krus",
    "pkd",
    "ift2r",
    "ift-2r",
    "ift1r",
    "ift-1r",
    "jpk",
    "ksef",
    "kpir",
    "wht",
    "wdt",
    "wnt",
    "sent",
    "kst",
    "dg1",
    "dg-1",
    "st",
    "nip",
    "regon",
    "pesel",
    "pcc",
    "pkwiu",
}

DOMAIN_HINT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bpodatek\b", re.IGNORECASE),
    re.compile(r"\bskladk", re.IGNORECASE),
    re.compile(r"\bskładk", re.IGNORECASE),
    re.compile(r"\bfakt", re.IGNORECASE),
    re.compile(r"\bdeklar", re.IGNORECASE),
    re.compile(r"\bustaw", re.IGNORECASE),
    re.compile(r"\bart\.", re.IGNORECASE),
    re.compile(r"\bksef\b", re.IGNORECASE),
    re.compile(r"\bjpk\b", re.IGNORECASE),
    re.compile(r"\bpit\b|\bcit\b|\bvat\b|\bzus\b", re.IGNORECASE),
)

CANONICAL_LAW_NAMES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("kodeks pracy",), "Kodeks pracy"),
    (("rachunkow",), "Ustawa o rachunkowości"),
    (("systemie ubezpieczen spolecznych",), "Ustawa o systemie ubezpieczeń społecznych"),
    (("ordynacja podatkowa",), "Ordynacja podatkowa"),
    (
        ("podatku dochodowym od osob prawnych", "ustawa o cit", " cit "),
        "Ustawa o podatku dochodowym od osób prawnych",
    ),
    (
        ("podatku dochodowym od osob fizycznych", "ustawa o pit", " pit "),
        "Ustawa o podatku dochodowym od osób fizycznych",
    ),
    (
        ("zryczaltowanym podatku dochodowym", "ryczalt", "ryczałt"),
        "Ustawa o zryczałtowanym podatku dochodowym",
    ),
    (
        ("kasy rejestruj", "kas rejestruj"),
        "Rozporządzenie MF o kasach rejestrujących",
    ),
    (
        ("podatku od towarow i uslug", "ustawa o vat", " vat "),
        "Ustawa o VAT",
    ),
)

CATEGORY_FALLBACK_LAW_NAMES: dict[str, str] = {
    "vat": "Ustawa o VAT",
    "pit": "Ustawa o podatku dochodowym od osób fizycznych",
    "cit": "Ustawa o podatku dochodowym od osób prawnych",
    "zus": "Ustawa o systemie ubezpieczeń społecznych",
    "kadry": "Kodeks pracy",
    "ordynacja": "Ordynacja podatkowa",
    "rachunkowosc": "Ustawa o rachunkowości",
    "jpk": "Rozporządzenie JPK_V7",
    "ksef": "Rozporządzenie KSeF",
}

InputFunc = Callable[[str], str]


def normalize_text(value: str) -> str:
    """Return lowercase ASCII-like text for duplicate checks and heuristics."""

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
    normalized = unicodedata.normalize("NFKD", value.lower().translate(translation))
    without_marks = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return re.sub(r"\s+", " ", without_marks).strip()


def normalize_content(value: str) -> str:
    """Normalize content for duplicate detection."""

    compact = normalize_text(value)
    compact = re.sub(r"[^\w\s]", " ", compact)
    return re.sub(r"\s+", " ", compact).strip()


def ensure_list(value: Any, path: Path, label: str) -> list[dict[str, Any]]:
    """Validate that *value* is a JSON list of dict objects."""

    if not isinstance(value, list):
        raise ValueError(f"Expected {label} to be a JSON array in {path}")
    output: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"Expected {label}[{index}] to be an object in {path}")
        output.append(item)
    return output


def load_json_file(path: Path, *, missing_ok: bool = False) -> Any:
    """Load a JSON file with clear validation errors."""

    if missing_ok and not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise ValueError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON in {path}: {exc.msg}") from exc


def kb_duplicate_key(record: dict[str, Any]) -> tuple[str, str, str]:
    """Return the KB duplicate key: law, article, normalized content."""

    return (
        normalize_text(str(record.get("law_name", ""))),
        normalize_text(str(record.get("article_number", ""))),
        normalize_content(str(record.get("content", ""))),
    )


def synonym_key(record: dict[str, Any]) -> str:
    """Return a normalized synonym key."""

    raw = record.get("short") or record.get("slang") or ""
    normalized = normalize_text(str(raw))
    return re.sub(r"[^a-z0-9]", "", normalized)


def canonicalize_law_name(value: str) -> str:
    """Map noisy source law names onto stable KB law names."""

    raw = value.strip()
    normalized = f" {normalize_text(raw)} "
    for aliases, canonical in CANONICAL_LAW_NAMES:
        if any(alias in normalized for alias in aliases):
            return canonical
    return raw


def has_legal_reference(article_number: str) -> bool:
    """True when the article reference looks like a concrete legal citation."""

    return "art." in article_number.lower() or "§" in article_number


def looks_like_placeholder(content: str) -> bool:
    """True when content is obviously weak or placeholder-like."""

    lowered = normalize_text(content)
    return any(pattern in lowered for pattern in WEAK_CONTENT_PATTERNS)


def has_legal_grounding(content: str) -> bool:
    """Heuristic check that content contains an actual rule, duty, or condition."""

    if any(pattern.search(content) for pattern in LEGAL_SIGNAL_PATTERNS):
        return True
    return bool(re.search(r"\b\d+\b", content))


def build_question_intent(unit: dict[str, Any]) -> str:
    """Derive a stable question_intent for merged KB rows."""

    source_questions = unit.get("source_questions")
    if isinstance(source_questions, list):
        for question in source_questions:
            if isinstance(question, str) and question.strip():
                return question.strip()
    reason = str(unit.get("reason", "")).strip()
    if reason:
        return reason
    return f"{unit.get('law_name', '')} | {unit.get('article_number', '')}".strip(" |")


def to_curated_kb_record(unit: dict[str, Any]) -> dict[str, Any]:
    """Convert a proposal into the canonical KB-addition schema."""

    raw_law_name = str(unit["law_name"]).strip()
    category = str(unit["category"]).strip()
    law_name = canonicalize_law_name(raw_law_name)
    if law_name == raw_law_name:
        fallback = CATEGORY_FALLBACK_LAW_NAMES.get(normalize_text(category))
        if fallback:
            law_name = fallback
    return {
        "law_name": law_name,
        "article_number": str(unit["article_number"]).strip(),
        "category": category,
        "verified_date": "",
        "question_intent": build_question_intent({**unit, "law_name": law_name}),
        "content": str(unit["content"]).strip(),
        "source": "curate_kb_and_synonyms",
    }


def kb_sort_key(record: dict[str, Any]) -> tuple[str, str, str]:
    """Deterministic sort key for KB rows."""

    return (
        normalize_text(str(record.get("law_name", ""))),
        normalize_text(str(record.get("article_number", ""))),
        normalize_content(str(record.get("content", ""))),
    )


def slang_sort_key(record: dict[str, Any]) -> tuple[str, str]:
    """Deterministic sort key for synonym rows."""

    return (
        normalize_text(str(record.get("short", ""))),
        normalize_text(str(record.get("full_phrase", ""))),
    )


def explain_kb_pass(unit: dict[str, Any]) -> str:
    """Explain why a KB unit passed heuristics."""

    reasons: list[str] = []
    content = str(unit.get("content", ""))
    if has_legal_reference(str(unit.get("article_number", ""))):
        reasons.append("ma konkretny odnośnik prawny")
    if len(content.strip()) >= MIN_CONTENT_LENGTH:
        reasons.append("treść jest wystarczająco długa")
    if has_legal_grounding(content):
        reasons.append("zawiera konkretną regułę lub warunek")
    return ", ".join(reasons) or "przeszedł reguły jakości"


def explain_synonym_pass(synonym: dict[str, Any]) -> str:
    """Explain why a synonym passed heuristics."""

    reasons: list[str] = []
    token = str(synonym.get("slang", "")).strip()
    expanded = str(synonym.get("expanded", "")).strip()
    if token:
        reasons.append("ma niepusty skrót")
    if expanded:
        reasons.append("ma rozwinięcie")
    if token.lower() in STRONG_SHORT_TOKENS:
        reasons.append("to mocny skrót domenowy")
    return ", ".join(reasons) or "przeszedł reguły jakości"


def curate_kb_units(
    proposed_units: list[dict[str, Any]],
    existing_kb: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Curate proposed KB units and return accepted rows plus rejections."""

    existing_keys = {kb_duplicate_key(record) for record in existing_kb}
    accepted: list[dict[str, Any]] = []
    rejections: list[dict[str, str]] = []

    for unit in proposed_units:
        missing = [
            field
            for field in ("law_name", "article_number", "category", "content")
            if not str(unit.get(field, "")).strip()
        ]
        label = f"{unit.get('law_name', '?')} | {unit.get('article_number', '?')}"

        if missing:
            rejections.append({"item": label, "reason": f"missing fields: {', '.join(missing)}"})
            continue

        article_number = str(unit["article_number"]).strip()
        content = str(unit["content"]).strip()

        if len(content) < MIN_CONTENT_LENGTH:
            rejections.append({"item": label, "reason": "content too short"})
            continue

        if looks_like_placeholder(content):
            rejections.append({"item": label, "reason": "weak placeholder content"})
            continue

        if not has_legal_reference(article_number):
            rejections.append({"item": label, "reason": "invalid article reference"})
            continue

        if not has_legal_grounding(content):
            rejections.append({"item": label, "reason": "missing concrete legal grounding"})
            continue

        curated = to_curated_kb_record(unit)
        key = kb_duplicate_key(curated)
        if key in existing_keys:
            rejections.append({"item": label, "reason": "duplicate kb unit"})
            continue

        existing_keys.add(key)
        accepted.append(curated)

    accepted.sort(key=kb_sort_key)
    return accepted, rejections


def extract_existing_synonyms(existing_slang: Any) -> list[dict[str, Any]]:
    """Normalize existing slang JSON into a list of dict records."""

    if existing_slang == []:
        return []
    if isinstance(existing_slang, list):
        return ensure_list(existing_slang, SLANG_PATH, "slang entries")
    if isinstance(existing_slang, dict):
        if "top_slang_terms" in existing_slang:
            return ensure_list(existing_slang["top_slang_terms"], SLANG_PATH, "top_slang_terms")
        if "synonyms" in existing_slang:
            return ensure_list(existing_slang["synonyms"], SLANG_PATH, "synonyms")
    raise ValueError("Unsupported slang file format")


def looks_like_domain_synonym(token: str, expanded: str, examples: list[str]) -> bool:
    """Heuristic validation for accounting/legal relevance."""

    lowered_token = token.lower()
    if lowered_token in STRONG_SHORT_TOKENS:
        return True
    corpus = " ".join([expanded, *examples])
    return any(pattern.search(corpus) for pattern in DOMAIN_HINT_PATTERNS)


def to_curated_synonym(record: dict[str, Any]) -> dict[str, Any]:
    """Convert a proposed synonym into the curated output schema."""

    examples_raw = record.get("source_questions") or record.get("examples") or []
    examples = [
        str(example).strip()
        for example in examples_raw
        if isinstance(example, str) and example.strip()
    ]
    freq_raw = record.get("total_freq", record.get("freq", 0))
    try:
        freq = int(freq_raw)
    except (TypeError, ValueError):
        freq = 0

    return {
        "short": str(record.get("slang", record.get("short", ""))).strip(),
        "full_phrase": str(record.get("expanded", record.get("full_phrase", ""))).strip(),
        "freq": freq,
        "examples": examples[:5],
        "source_questions_count": int(
            record.get("source_questions_count", len(examples))
            if record.get("source_questions_count") is not None
            else len(examples)
        ),
        "slang": str(record.get("slang", record.get("short", ""))).strip(),
        "expanded": str(record.get("expanded", record.get("full_phrase", ""))).strip(),
    }


def curate_synonyms(
    proposed_synonyms: list[dict[str, Any]],
    existing_slang: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Curate proposed synonyms and return accepted rows plus rejections."""

    existing_entries = extract_existing_synonyms(existing_slang)
    seen_keys = {synonym_key(record) for record in existing_entries}
    accepted_keys: set[str] = set()
    accepted: list[dict[str, Any]] = []
    rejections: list[dict[str, str]] = []

    for record in proposed_synonyms:
        curated = to_curated_synonym(record)
        key = synonym_key(curated)
        token = curated["short"].strip()
        label = token or "<empty>"

        if not key:
            rejections.append({"item": label, "reason": "empty synonym key"})
            continue

        if key in NOISY_SYNONYMS:
            rejections.append({"item": label, "reason": "noise or brand synonym"})
            continue

        alnum_key = re.sub(r"[^a-z0-9]", "", key)
        if len(alnum_key) <= 4 and key not in STRONG_SHORT_TOKENS:
            rejections.append({"item": label, "reason": "ambiguous short token"})
            continue

        if key in seen_keys:
            rejections.append({"item": label, "reason": "duplicate existing synonym"})
            continue

        if key in accepted_keys:
            rejections.append({"item": label, "reason": "duplicate proposed synonym"})
            continue

        if not looks_like_domain_synonym(
            token,
            curated["full_phrase"],
            curated["examples"],
        ):
            rejections.append({"item": label, "reason": "not clearly domain-law relevant"})
            continue

        accepted_keys.add(key)
        accepted.append(curated)

    accepted.sort(key=slang_sort_key)
    return accepted, rejections


def review_kb_units_interactively(
    candidates: list[dict[str, Any]],
    input_func: InputFunc = input,
) -> list[dict[str, Any]]:
    """Review curated KB units interactively."""

    accepted: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        item = dict(candidate)
        while True:
            print(f"\n[KB {index}/{len(candidates)}]")
            print(json.dumps(item, ensure_ascii=False, indent=2))
            print(f"reason_passed: {explain_kb_pass(item)}")
            choice = input_func("Choose: [a]ccept / [r]eject / [e]dit / [q]uit: ").strip().lower()

            if choice in {"a", ""}:
                accepted.append(item)
                break
            if choice == "r":
                break
            if choice == "q":
                return accepted
            if choice == "e":
                new_category = input_func(f"New category [{item['category']}]: ").strip()
                if new_category:
                    item["category"] = new_category
                new_content = input_func(f"New content [{item['content']}]: ").strip()
                if new_content:
                    item["content"] = new_content
                continue

    accepted.sort(key=kb_sort_key)
    return accepted


def review_synonyms_interactively(
    candidates: list[dict[str, Any]],
    input_func: InputFunc = input,
) -> list[dict[str, Any]]:
    """Review curated synonym candidates interactively."""

    accepted: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        item = dict(candidate)
        while True:
            print(f"\n[SYN {index}/{len(candidates)}]")
            print(json.dumps(item, ensure_ascii=False, indent=2))
            print(f"reason_passed: {explain_synonym_pass(item)}")
            choice = input_func("Choose: [a]ccept / [r]eject / [e]dit / [q]uit: ").strip().lower()

            if choice in {"a", ""}:
                accepted.append(item)
                break
            if choice == "r":
                break
            if choice == "q":
                return accepted
            if choice == "e":
                new_phrase = input_func(f"New full phrase [{item['full_phrase']}]: ").strip()
                if new_phrase:
                    item["full_phrase"] = new_phrase
                    item["expanded"] = new_phrase
                continue

    accepted.sort(key=slang_sort_key)
    return accepted


def merge_kb_additions(kb_path: Path, additions: list[dict[str, Any]]) -> int:
    """Merge curated KB additions into the live KB without duplicates."""

    existing_raw = load_json_file(kb_path)
    existing = ensure_list(existing_raw, kb_path, "law knowledge")
    seen = {kb_duplicate_key(record) for record in existing}
    added = 0

    for record in additions:
        key = kb_duplicate_key(record)
        if key in seen:
            continue
        seen.add(key)
        existing.append(record)
        added += 1

    existing.sort(key=kb_sort_key)
    kb_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return added


def merge_synonym_additions(slang_path: Path, additions: list[dict[str, Any]]) -> int:
    """Merge curated synonym additions into the live slang file without duplicates."""

    existing_raw = load_json_file(slang_path, missing_ok=True)
    if existing_raw == []:
        existing_entries: list[dict[str, Any]] = []
        wrapper_key: str | None = None
        wrapper: dict[str, Any] | None = None
    elif isinstance(existing_raw, list):
        existing_entries = ensure_list(existing_raw, slang_path, "slang entries")
        wrapper_key = None
        wrapper = None
    elif isinstance(existing_raw, dict) and "top_slang_terms" in existing_raw:
        existing_entries = ensure_list(existing_raw["top_slang_terms"], slang_path, "top_slang_terms")
        wrapper_key = "top_slang_terms"
        wrapper = dict(existing_raw)
    elif isinstance(existing_raw, dict) and "synonyms" in existing_raw:
        existing_entries = ensure_list(existing_raw["synonyms"], slang_path, "synonyms")
        wrapper_key = "synonyms"
        wrapper = dict(existing_raw)
    else:
        raise ValueError(f"Unsupported slang file format in {slang_path}")

    seen = {synonym_key(record) for record in existing_entries}
    added = 0
    for record in additions:
        key = synonym_key(record)
        if key in seen:
            continue
        seen.add(key)
        existing_entries.append(record)
        added += 1

    existing_entries.sort(key=slang_sort_key)
    if wrapper_key is None:
        output: Any = existing_entries
    else:
        assert wrapper is not None
        wrapper[wrapper_key] = existing_entries
        output = wrapper

    slang_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return added


def build_curation_report(
    proposed_kb_units: list[dict[str, Any]],
    accepted_kb_units: list[dict[str, Any]],
    rejected_kb_units: list[dict[str, str]],
    proposed_synonyms: list[dict[str, Any]],
    accepted_synonyms: list[dict[str, Any]],
    rejected_synonyms: list[dict[str, str]],
) -> dict[str, Any]:
    """Build the curation report payload."""

    rejection_histogram: Counter[str] = Counter()
    for row in rejected_kb_units + rejected_synonyms:
        rejection_histogram[row["reason"]] += 1

    top_laws = Counter(record["law_name"] for record in accepted_kb_units)
    top_synonyms = sorted(
        accepted_synonyms,
        key=lambda record: (-int(record.get("freq", 0)), normalize_text(str(record.get("short", "")))),
    )[:10]

    return {
        "proposed_kb_units_total": len(proposed_kb_units),
        "proposed_kb_units_accepted": len(accepted_kb_units),
        "proposed_kb_units_rejected": len(rejected_kb_units),
        "proposed_synonyms_total": len(proposed_synonyms),
        "proposed_synonyms_accepted": len(accepted_synonyms),
        "proposed_synonyms_rejected": len(rejected_synonyms),
        "top_accepted_laws_by_count": dict(top_laws.most_common()),
        "top_accepted_synonyms_by_freq": [
            {
                "short": record["short"],
                "full_phrase": record["full_phrase"],
                "freq": int(record.get("freq", 0)),
            }
            for record in top_synonyms
        ],
        "rejection_reasons_histogram": dict(rejection_histogram.most_common()),
    }


def write_json(path: Path, payload: Any) -> None:
    """Write JSON deterministically."""

    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_curation(
    *,
    kb_path: Path = KB_PATH,
    slang_path: Path = SLANG_PATH,
    proposed_kb_path: Path = PROPOSED_KB_PATH,
    proposed_synonyms_path: Path = PROPOSED_SYNONYMS_PATH,
    curated_kb_path: Path = CURATED_KB_PATH,
    curated_slang_path: Path = CURATED_SLANG_PATH,
    report_path: Path = REPORT_PATH,
    interactive: bool = False,
    merge: bool = False,
    input_func: InputFunc = input,
) -> dict[str, Any]:
    """Run curation end-to-end and optionally merge accepted additions."""

    kb_raw = load_json_file(kb_path)
    proposed_kb_raw = load_json_file(proposed_kb_path)
    proposed_synonyms_raw = load_json_file(proposed_synonyms_path)
    slang_raw = load_json_file(slang_path, missing_ok=True)

    existing_kb = ensure_list(kb_raw, kb_path, "law knowledge")
    proposed_kb_units = ensure_list(proposed_kb_raw, proposed_kb_path, "proposed kb units")
    proposed_synonyms = ensure_list(proposed_synonyms_raw, proposed_synonyms_path, "proposed synonyms")

    accepted_kb_units, rejected_kb_units = curate_kb_units(proposed_kb_units, existing_kb)
    accepted_synonyms, rejected_synonyms = curate_synonyms(proposed_synonyms, slang_raw)

    if interactive:
        accepted_kb_units = review_kb_units_interactively(accepted_kb_units, input_func=input_func)
        accepted_synonyms = review_synonyms_interactively(accepted_synonyms, input_func=input_func)

    write_json(curated_kb_path, accepted_kb_units)
    write_json(curated_slang_path, accepted_synonyms)

    report = build_curation_report(
        proposed_kb_units,
        accepted_kb_units,
        rejected_kb_units,
        proposed_synonyms,
        accepted_synonyms,
        rejected_synonyms,
    )

    if merge:
        report["merge"] = {
            "kb_added": merge_kb_additions(kb_path, accepted_kb_units),
            "synonyms_added": merge_synonym_additions(slang_path, accepted_synonyms),
        }

    write_json(report_path, report)
    return report


def parse_args() -> argparse.Namespace:
    """Build the CLI."""

    parser = argparse.ArgumentParser(description="Curate proposed KB units and synonym additions.")
    parser.add_argument("--interactive", action="store_true", help="Review accepted candidates interactively.")
    parser.add_argument("--merge", action="store_true", help="Merge curated additions into live files.")
    parser.add_argument("--kb", type=Path, default=KB_PATH)
    parser.add_argument("--slang", type=Path, default=SLANG_PATH)
    parser.add_argument("--proposed-kb", type=Path, default=PROPOSED_KB_PATH)
    parser.add_argument("--proposed-synonyms", type=Path, default=PROPOSED_SYNONYMS_PATH)
    parser.add_argument("--curated-kb", type=Path, default=CURATED_KB_PATH)
    parser.add_argument("--curated-slang", type=Path, default=CURATED_SLANG_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""

    args = parse_args()
    report = run_curation(
        kb_path=args.kb,
        slang_path=args.slang,
        proposed_kb_path=args.proposed_kb,
        proposed_synonyms_path=args.proposed_synonyms,
        curated_kb_path=args.curated_kb,
        curated_slang_path=args.curated_slang,
        report_path=args.report,
        interactive=args.interactive,
        merge=args.merge,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
