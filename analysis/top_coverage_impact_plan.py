from __future__ import annotations

import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, NamedTuple


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.article_coverage_audit import canonicalize_law_name  # noqa: E402
from core.categorizer import categorize_query  # noqa: E402
from core.retriever import LawChunk, load_slang_map, retrieve_chunks  # noqa: E402


FB_PATH = ROOT / "fb_pipeline" / "dedup_questions_output_v3.json"
KB_PATH = ROOT / "data" / "seeds" / "law_knowledge.json"
REPORT_PATH = ROOT / "analysis" / "top_coverage_impact_report.json"
BATCHES_PATH = ROOT / "analysis" / "top_gap_batches.json"

COVERED_THRESHOLD = 0.030
WEAK_THRESHOLD = 0.025
TOP_LIMIT = 3


class BatchRule(NamedTuple):
    name: str
    keywords: tuple[str, ...]
    laws: tuple[str, ...]
    synonym_hints: tuple[str, ...]
    fix_type: str


CATEGORY_TO_LAWS: dict[str, tuple[str, ...]] = {
    "vat": (
        "Ustawa o VAT",
        "Rozporządzenie MF o kasach rejestrujących",
    ),
    "pit": (
        "Ustawa o podatku dochodowym od osób fizycznych",
        "Ustawa o zryczałtowanym podatku dochodowym",
    ),
    "cit": ("Ustawa o podatku dochodowym od osób prawnych",),
    "jpk": (
        "Rozporządzenie JPK_V7",
        "Ustawa o VAT",
    ),
    "ksef": (
        "Rozporządzenie KSeF",
        "Ustawa o VAT",
        "Ustawa o VAT - KSeF terminy wdrożenia",
        "Ustawa o VAT - KSeF zwolnienia",
        "Ustawa o VAT - KSeF uproszczenia 2026",
    ),
    "rachunkowosc": ("Ustawa o rachunkowości",),
    "kadry": ("Kodeks pracy",),
    "zus": ("Ustawa o systemie ubezpieczeń społecznych",),
    "ordynacja": ("Ordynacja podatkowa",),
}

BATCH_RULES: tuple[BatchRule, ...] = (
    BatchRule(
        "Poza zakresem / community workflow",
        (
            "szukam osoby",
            "szukam biura",
            "polecacie kurs",
            "polecić kurs",
            "polecic kurs",
            "szkoleni",
            "kurs online",
            "współpracy",
            "wspolpracy",
            "za opłatą",
            "za oplata",
            "cv",
            "symfonia",
            "subiekt",
            "optima",
            "rewizor",
            "program do księgowania",
            "program do ksiegowania",
            "jaki program",
            "wdrożyć",
            "wdrozyc",
            "kompatybilny",
            "video",
            "jakiej ceny",
            "jaka cena",
        ),
        (),
        (),
        "categorizer",
    ),
    BatchRule(
        "WHT / IFT / certyfikat rezydencji",
        (
            "wht",
            "ift",
            "ift2r",
            "ift-2r",
            "certyfikat rezydencji",
            "rezydencji podatkowej",
            "podatek u źródła",
            "podatek u zrodla",
        ),
        ("Ustawa o podatku dochodowym od osób prawnych",),
        ("IFT2R", "WHT", "certyfikat rezydencji"),
        "mixed",
    ),
    BatchRule(
        "Formularze PIT i obowiązki płatnika",
        (
            "pit-4r",
            "pit4r",
            "pit-11",
            "pit11",
            "pit-11a",
            "pit11a",
            "pit-40a",
            "pit40a",
            "pit-37",
            "pit37",
            "pit-36",
            "pit36",
            "pit-36l",
            "pit36l",
            "pit-8ar",
            "pit8ar",
            "zerowy pit",
        ),
        ("Ustawa o podatku dochodowym od osób fizycznych",),
        ("PIT4R", "PIT11", "PIT11A", "PIT40A"),
        "mixed",
    ),
    BatchRule(
        "Procedury podatkowe / pisma / pełnomocnictwa",
        (
            "czynny żal",
            "czynny zal",
            "stwierdzenie nadpłaty",
            "stwierdzenie nadplaty",
            "nadpłaty",
            "nadplaty",
            "zwrot",
            "pełnomocnictw",
            "pelnomocnictw",
            "profil zaufany",
            "podpis kwalifikowany",
            "pełnomocnictwa",
            "pelnomocnictwa",
        ),
        (
            "Ordynacja podatkowa",
            "Ustawa o podatku dochodowym od osób prawnych",
            "Ustawa o VAT",
        ),
        ("PPO-1", "UPL-1"),
        "mixed",
    ),
    BatchRule(
        "JPK oznaczenia i procedury",
        (
            "jpk",
            "jpk_v7",
            "jpk v7",
            "gtu",
            "bfk",
            "di",
            "wew",
            "ro",
            "fp",
            "mpp",
            "tp",
            "sw",
            "ee",
            "oznaczenia",
            "oznaczenie",
        ),
        (
            "Rozporządzenie JPK_V7",
            "Ustawa o VAT",
        ),
        ("BFK", "DI", "GTU"),
        "mixed",
    ),
    BatchRule(
        "KPiR / rachunkowość operacyjna",
        (
            "kpir",
            "zaksięg",
            "zaksieg",
            "księg",
            "ksieg",
            "koszt bilans",
            "koszt pośredni",
            "koszt posredni",
            "przeksięgow",
            "przeksiegow",
            "tamtego roku",
            "kolumn",
            "sprawozdanie finansowe",
            "bilans",
            "amortyzacj",
        ),
        (
            "Ustawa o rachunkowości",
            "Ustawa o podatku dochodowym od osób fizycznych",
        ),
        ("KPiR", "SF"),
        "kb_units",
    ),
    BatchRule(
        "KSeF uprawnienia i obieg faktur",
        (
            "ksef",
            "uprawnienia",
            "pdf",
            "profil zaufany",
            "podpis kwalifikowany",
            "pobrania faktur",
            "faktur przez nas",
        ),
        (
            "Rozporządzenie KSeF",
            "Ustawa o VAT",
        ),
        ("KSeF",),
        "mixed",
    ),
    BatchRule(
        "ZUS / KRUS / kadry proceduralne",
        (
            "zus",
            "krus",
            "pue",
            "dra",
            "rca",
            "rsa",
            "składk",
            "skladk",
            "preferencyjny",
            "zasiłek",
            "zasilek",
            "umowa o pracę",
            "umowa o prace",
            "zleceni",
        ),
        (
            "Ustawa o systemie ubezpieczeń społecznych",
            "Kodeks pracy",
        ),
        ("PUE", "DRA", "RCA", "RSA", "KRUS"),
        "mixed",
    ),
    BatchRule(
        "Leasing / samochody / amortyzacja",
        (
            "leasing",
            "samoch",
            "auto",
            "vat-26",
            "vat26",
            "amortyzacj",
            "wykup",
            "limit 150",
            "limit 225",
        ),
        (
            "Ustawa o podatku dochodowym od osób fizycznych",
            "Ustawa o VAT",
            "Ustawa o rachunkowości",
        ),
        ("VAT26",),
        "kb_units",
    ),
    BatchRule(
        "Estoński CIT",
        (
            "estoński cit",
            "estonski cit",
            "estończyk",
            "estonczyk",
            "ukryte zyski",
            "ryczałt od dochodów spółek",
            "ryczalt od dochodow spolek",
        ),
        ("Ustawa o podatku dochodowym od osób prawnych",),
        ("estończyk",),
        "mixed",
    ),
    BatchRule(
        "VAT stawki / zwolnienia / korekty",
        (
            "stawka vat",
            "zwolnienie z vat",
            "korekta",
            "paragon",
            "kasa fiskalna",
            "kasy fiskalne",
            "odsetki",
            "faktura zaliczkowa",
            "faktura końcowa",
            "faktura koncowa",
        ),
        (
            "Ustawa o VAT",
            "Rozporządzenie MF o kasach rejestrujących",
        ),
        ("VAT-R",),
        "kb_units",
    ),
    BatchRule(
        "KSeF i faktury ustrukturyzowane",
        (
            "ksef",
            "faktura ustrukturyzowana",
            "numer ksef",
            "korygująca",
            "korygujaca",
            "faktura w ksef",
        ),
        (
            "Ustawa o VAT",
            "Rozporządzenie KSeF",
        ),
        ("KSeF",),
        "kb_units",
    ),
    BatchRule(
        "Ryczałt i stawki działalności",
        (
            "ryczałt",
            "ryczalt",
            "najem",
            "5,5%",
            "8,5%",
            "12%",
            "budowlan",
            "stawka ryczałtu",
            "stawka ryczaltu",
        ),
        ("Ustawa o zryczałtowanym podatku dochodowym",),
        ("ryczałt",),
        "kb_units",
    ),
)

PLACEHOLDER_PATTERNS = (
    "nie reguluje",
    "nie zawiera",
    "brak bezpośredniego odniesienia",
    "brak bezposredniego odniesienia",
    "poza zakresem",
    "wymaga weryfikacji poza",
)

FORM_PATTERN = re.compile(
    r"\b(?:pit[- ]?\d+[a-z]?|cit[- ]?8|ift[- ]?2r|vat[- ]?[a-z0-9]+|jpk[_ -]?v?7[mk]?|dra|rca|rsa|pue|krs)\b",
    flags=re.IGNORECASE,
)

ABBREVIATION_PATTERN = re.compile(r"\b[a-z]{2,6}\d{0,3}[a-z]?\b", flags=re.IGNORECASE)


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.lower())
    without_accents = "".join(character for character in normalized if not unicodedata.combining(character))
    compact = re.sub(r"\s+", " ", without_accents).strip()
    return compact.replace("?", " ")


def preview(text: str, limit: int = 180) -> str:
    compact = " ".join(str(text).split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def contains_keyword(query: str, keyword: str) -> bool:
    normalized_query = normalize_text(query)
    normalized_keyword = normalize_text(keyword)
    if not normalized_keyword:
        return False
    if re.fullmatch(r"[a-z0-9_-]+", normalized_keyword):
        if normalized_keyword.isalpha() and len(normalized_keyword) >= 5:
            pattern = re.compile(rf"(?<![a-z0-9]){re.escape(normalized_keyword)}[a-z0-9]*(?![a-z0-9])")
        else:
            pattern = re.compile(rf"(?<![a-z0-9]){re.escape(normalized_keyword)}(?![a-z0-9])")
        return bool(pattern.search(normalized_query))
    return normalized_keyword in normalized_query


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def serialize_chunk(chunk: LawChunk) -> dict[str, Any]:
    return {
        "law_name": chunk.law_name,
        "canonical_law_name": canonicalize_law_name(chunk.law_name),
        "article_number": chunk.article_number,
        "category": chunk.category,
        "score": round(float(chunk.score), 4),
        "preview": preview(chunk.content),
    }


def load_existing_synonyms() -> set[str]:
    slang_path = ROOT / "fb_pipeline" / "slang_analysis.json"
    if not slang_path.exists():
        return set()
    data = load_json(slang_path)
    terms: set[str] = set()
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                slang = str(item.get("short") or item.get("slang") or "").strip()
                if slang:
                    terms.add(normalize_text(slang))
    return terms


def question_has_keywords(query: str, keywords: tuple[str, ...]) -> bool:
    return any(contains_keyword(query, keyword) for keyword in keywords)


def infer_expected_laws(source_category: str, query: str, aktuo_category: str) -> set[str]:
    expected = set(CATEGORY_TO_LAWS.get(source_category, ()))
    normalized_query = normalize_text(query)

    if aktuo_category != "ogólne":
        expected.update(CATEGORY_TO_LAWS.get(aktuo_category, ()))

    if question_has_keywords(normalized_query, ("jpk", "gtu", "bfk", "di", "wew", "ro", "mpp", "tp", "sw", "ee")):
        expected.update(CATEGORY_TO_LAWS["jpk"])
    if question_has_keywords(normalized_query, ("ksef", "faktura ustrukturyzowana", "numer ksef")):
        expected.update(CATEGORY_TO_LAWS["ksef"])
    if question_has_keywords(normalized_query, ("certyfikat rezydencji", "rezydencji podatkowej", "wht", "ift", "cit-8", "cit8")):
        expected.update(CATEGORY_TO_LAWS["cit"])
    if question_has_keywords(normalized_query, ("ryczałt", "ryczalt", "najem", "5,5%", "8,5%", "12%")):
        expected.add("Ustawa o zryczałtowanym podatku dochodowym")
    if question_has_keywords(normalized_query, ("kasa fiskalna", "kasy fiskalne", "zwolnienie z kasy")):
        expected.add("Rozporządzenie MF o kasach rejestrujących")
    if question_has_keywords(normalized_query, ("zus", "krus", "pue", "dra", "rca", "rsa", "składk", "skladk")):
        expected.update(CATEGORY_TO_LAWS["zus"])
    if question_has_keywords(normalized_query, ("umowa o pracę", "umowa o prace", "urlop", "wypowiedzenie", "świadectwo pracy", "swiadectwo pracy")):
        expected.update(CATEGORY_TO_LAWS["kadry"])
    if question_has_keywords(normalized_query, ("sprawozdanie finansowe", "bilans", "zaksięg", "zaksieg", "kpir", "księg", "ksieg", "amortyzacj")):
        expected.update(CATEGORY_TO_LAWS["rachunkowosc"])

    return {canonicalize_law_name(law_name) for law_name in expected if law_name}


def law_matches_expected(law_name: str, expected_laws: set[str]) -> bool:
    return canonicalize_law_name(law_name) in expected_laws


def classify_question(source_category: str, query: str, aktuo_category: str, chunks: list[LawChunk]) -> tuple[str, str, set[str]]:
    expected_laws = infer_expected_laws(source_category, query, aktuo_category)
    if not chunks:
        return "GAP", "Brak chunków.", expected_laws

    top_score = float(chunks[0].score)
    top_matches = law_matches_expected(chunks[0].law_name, expected_laws)
    any_top3_match = any(law_matches_expected(chunk.law_name, expected_laws) for chunk in chunks[:TOP_LIMIT])

    if expected_laws:
        if top_score > COVERED_THRESHOLD and top_matches:
            return "COVERED", "Top chunk trafia w spodziewany akt prawny z mocnym score.", expected_laws
        if top_score >= WEAK_THRESHOLD and any_top3_match:
            return "WEAK", "W top 3 jest sensowny akt prawny, ale trafienie nie jest jeszcze wystarczająco mocne.", expected_laws
        return "GAP", "Brak mocnego trafienia w spodziewany akt prawny.", expected_laws

    if top_score >= COVERED_THRESHOLD and aktuo_category != "ogólne":
        return "WEAK", "Retriever zwrócił sensowny wynik, ale pytanie nie mapuje się jednoznacznie do jednej ustawy.", expected_laws
    return "GAP", "Pytanie nie mapuje się dziś do jednoznacznego pokrycia w bazie.", expected_laws


def is_cross_law_query(source_category: str, aktuo_category: str, query: str, chunks: list[LawChunk]) -> bool:
    normalized_query = normalize_text(query)
    if source_category != aktuo_category and aktuo_category != "ogólne":
        return True
    cross_keywords = (" i ", " oraz ", "czy ", "czyli ", "vat i pit", "pit i vat", "bilansowych i kup")
    if any(keyword in normalized_query for keyword in cross_keywords):
        canonical_laws = {canonicalize_law_name(chunk.law_name) for chunk in chunks[:TOP_LIMIT]}
        return len(canonical_laws) > 1
    return False


def abbreviations_in_query(query: str) -> set[str]:
    normalized = normalize_text(query)
    return {
        token
        for token in ABBREVIATION_PATTERN.findall(normalized)
        if any(character.isdigit() for character in token) or token.isupper()
    }


def is_obvious_community_query(query: str, dataset_category: str) -> bool:
    normalized_query = normalize_text(query)
    if re.search(r"https?://", query, flags=re.IGNORECASE):
        return True

    community_markers = (
        "szukam",
        "polec",
        "kurs",
        "szkolen",
        "program",
        "wdroz",
        "wdroż",
        "cv",
        "wspolprac",
        "współprac",
        "ktoś pomoże",
        "ktos pomoze",
        "bardzo prosze o pomoc",
        "jak myslicie",
        "jak myślicie",
        "czy jest ktos",
        "czy jest ktoś",
        "czy sa na grupie",
        "czy są na grupie",
    )
    if dataset_category in {"praktyka", "erp"} and any(contains_keyword(normalized_query, marker) for marker in community_markers):
        return True
    return dataset_category in {"praktyka", "inne", "erp"} and len(normalized_query.split()) <= 4


def guess_root_cause(
    query: str,
    source_category: str,
    aktuo_category: str,
    verdict: str,
    chunks: list[LawChunk],
    expected_laws: set[str],
    known_synonyms: set[str],
) -> str:
    if is_cross_law_query(source_category, aktuo_category, query, chunks):
        return "cross_law_question"

    normalized_query = normalize_text(query)
    top_chunk = chunks[0] if chunks else None
    top_chunk_preview = normalize_text(top_chunk.content) if top_chunk else ""
    top_chunk_matches = bool(top_chunk and law_matches_expected(top_chunk.law_name, expected_laws))

    abbreviations = {
        token
        for token in abbreviations_in_query(query)
        if token not in known_synonyms and token not in {"pit", "cit", "vat", "zus", "jpk", "ksef"}
    }
    if abbreviations and (aktuo_category == "ogólne" or verdict == "GAP"):
        return "missing_synonym"

    if FORM_PATTERN.search(query):
        return "procedural_form_gap"

    if source_category != aktuo_category and aktuo_category != "ogólne" and not top_chunk_matches:
        return "wrong_category_match"

    if top_chunk and any(pattern in top_chunk_preview for pattern in PLACEHOLDER_PATTERNS):
        return "weak_existing_chunk"

    return "missing_kb_unit"


def assign_batch(query: str, root_cause: str, dataset_category: str) -> BatchRule:
    if is_obvious_community_query(query, dataset_category):
        return BatchRule(
            "Poza zakresem / community workflow",
            (),
            (),
            (),
            "categorizer",
        )
    for rule in BATCH_RULES:
        if any(contains_keyword(query, keyword) for keyword in rule.keywords):
            return rule
    if root_cause == "missing_synonym":
        return BatchRule(
            "Słowniki skrótów i synonimów",
            (),
            (),
            (),
            "synonyms",
        )
    if root_cause == "wrong_category_match":
        return BatchRule(
            "Doprecyzowanie kategorizera",
            (),
            (),
            (),
            "categorizer",
        )
    return BatchRule(
        "Pozostałe luki produktowe",
        (),
        (),
        (),
        "mixed",
    )


def analyze_questions(limit: int, known_synonyms: set[str]) -> dict[str, Any]:
    payload = load_json(FB_PATH)
    questions = sorted(
        payload["questions"],
        key=lambda item: (-int(item.get("freq", 0)), str(item.get("cat", "")), str(item.get("q", ""))),
    )[:limit]

    items: list[dict[str, Any]] = []
    summary = Counter()
    per_category: dict[str, Counter[str]] = defaultdict(Counter)

    for raw in questions:
        query = str(raw.get("q", "")).strip()
        source_category = str(raw.get("cat", "")).strip()
        freq = int(raw.get("freq", 0))
        aktuo_category = categorize_query(query)
        chunks = retrieve_chunks(query, KB_PATH, limit=TOP_LIMIT)
        verdict, reason, expected_laws = classify_question(source_category, query, aktuo_category, chunks)
        root_cause = guess_root_cause(
            query=query,
            source_category=source_category,
            aktuo_category=aktuo_category,
            verdict=verdict,
            chunks=chunks,
            expected_laws=expected_laws,
            known_synonyms=known_synonyms,
        )
        batch = assign_batch(query, root_cause, source_category)

        summary[verdict] += 1
        per_category[source_category][verdict] += 1
        items.append(
            {
                "question": query,
                "freq": freq,
                "dataset_category": source_category,
                "aktuo_category": aktuo_category,
                "verdict": verdict,
                "reason": reason,
                "root_cause_guess": root_cause,
                "expected_laws": sorted(expected_laws),
                "assigned_batch": batch.name,
                "top_3_chunks": [serialize_chunk(chunk) for chunk in chunks[:TOP_LIMIT]],
            }
        )

    gap_questions = sorted(
        (item for item in items if item["verdict"] == "GAP"),
        key=lambda item: (-int(item["freq"]), str(item["dataset_category"]), str(item["question"])),
    )
    weak_questions = sorted(
        (item for item in items if item["verdict"] == "WEAK"),
        key=lambda item: (-int(item["freq"]), str(item["dataset_category"]), str(item["question"])),
    )

    total = len(items) or 1
    return {
        "summary": {
            "covered_count": summary["COVERED"],
            "weak_count": summary["WEAK"],
            "gap_count": summary["GAP"],
            "coverage_percent": round((summary["COVERED"] / total) * 100, 2),
        },
        "per_category_breakdown": {
            category: {
                "covered_count": counts["COVERED"],
                "weak_count": counts["WEAK"],
                "gap_count": counts["GAP"],
            }
            for category, counts in sorted(per_category.items())
        },
        "gap_questions": gap_questions,
        "weak_questions": weak_questions,
        "all_questions": items,
    }


def extract_candidate_synonyms(questions: list[dict[str, Any]], known_synonyms: set[str]) -> list[str]:
    candidates = Counter()
    for item in questions:
        for token in abbreviations_in_query(str(item["question"])):
            if token not in known_synonyms and token not in {"pit", "cit", "vat", "zus", "jpk", "ksef"}:
                candidates[token] += int(item["freq"])
    return [token for token, _ in sorted(candidates.items(), key=lambda pair: (-pair[1], pair[0]))[:8]]


def choose_fix_type(root_causes: Counter[str], default_fix_type: str) -> str:
    if default_fix_type != "mixed":
        return default_fix_type
    if root_causes["missing_synonym"] and not (root_causes["missing_kb_unit"] or root_causes["weak_existing_chunk"]):
        return "synonyms"
    if root_causes["wrong_category_match"] and root_causes.total() == root_causes["wrong_category_match"]:
        return "categorizer"
    if root_causes["cross_law_question"] and root_causes.total() == root_causes["cross_law_question"]:
        return "audit_mapping"
    if root_causes["missing_kb_unit"] or root_causes["weak_existing_chunk"]:
        return "kb_units"
    return "mixed"


def estimate_work(batch: dict[str, Any]) -> tuple[int, int]:
    question_count = int(batch["number_of_questions"])
    gap_count = int(batch["gap_count"])
    weak_count = int(batch["weak_count"])
    fix_type = str(batch["recommended_fix_type"])
    missing_synonym_count = int(batch["root_causes"].get("missing_synonym", 0))

    if fix_type == "audit_mapping":
        return 0, 0
    if fix_type == "categorizer":
        return 0, max(0, min(3, math.ceil(question_count / 6)))
    if fix_type == "synonyms":
        return 0, max(1, min(8, math.ceil(max(question_count, missing_synonym_count) / 3)))
    if fix_type == "kb_units":
        return max(2, math.ceil((gap_count * 1.4 + weak_count * 0.6) / 2)), max(0, min(3, math.ceil(missing_synonym_count / 2)))
    return (
        max(2, math.ceil((gap_count * 1.2 + weak_count * 0.5) / 2)),
        max(1, min(4, math.ceil(missing_synonym_count / 2))) if missing_synonym_count else 0,
    )


def priority_multiplier(batch: dict[str, Any]) -> float:
    if batch["batch_name"] == "Poza zakresem / community workflow":
        return 0.05
    if batch["batch_name"] == "Pozostałe luki produktowe":
        return 0.35
    fix_type = str(batch["recommended_fix_type"])
    if fix_type == "audit_mapping":
        return 0.25
    if fix_type == "categorizer":
        return 0.75
    if fix_type == "synonyms":
        return 0.85
    return 1.0


def build_batches(top100: dict[str, Any], top200: dict[str, Any], known_synonyms: set[str]) -> dict[str, Any]:
    grouped: dict[str, dict[str, Any]] = {}

    top100_questions = {item["question"] for item in top100["all_questions"]}
    unresolved_top200 = [item for item in top200["all_questions"] if item["verdict"] in {"WEAK", "GAP"}]

    for item in unresolved_top200:
        rule = assign_batch(str(item["question"]), str(item["root_cause_guess"]), str(item["dataset_category"]))
        batch = grouped.setdefault(
            rule.name,
            {
                "batch_name": rule.name,
                "number_of_questions": 0,
                "gap_count": 0,
                "weak_count": 0,
                "total_freq_impact": 0,
                "questions_in_top100": 0,
                "questions_in_top200": 0,
                "total_freq_top100": 0,
                "total_freq_top200": 0,
                "likely_laws_or_regulations_needed": set(rule.laws),
                "likely_synonym_additions_needed": set(rule.synonym_hints),
                "root_causes": Counter(),
                "recommended_fix_type": rule.fix_type,
                "questions": [],
            },
        )
        batch["number_of_questions"] += 1
        batch["total_freq_impact"] += int(item["freq"])
        batch["questions_in_top200"] += 1
        batch["total_freq_top200"] += int(item["freq"])
        if item["verdict"] == "GAP":
            batch["gap_count"] += 1
        else:
            batch["weak_count"] += 1
        if item["question"] in top100_questions:
            batch["questions_in_top100"] += 1
            batch["total_freq_top100"] += int(item["freq"])
        batch["root_causes"][str(item["root_cause_guess"])] += 1
        batch["questions"].append(
            {
                "question": item["question"],
                "freq": item["freq"],
                "dataset_category": item["dataset_category"],
                "aktuo_category": item["aktuo_category"],
                "verdict": item["verdict"],
                "root_cause_guess": item["root_cause_guess"],
            }
        )

    for batch in grouped.values():
        batch["likely_synonym_additions_needed"].update(
            extract_candidate_synonyms(batch["questions"], known_synonyms)
        )
        batch["recommended_fix_type"] = choose_fix_type(batch["root_causes"], str(batch["recommended_fix_type"]))
        estimated_units, estimated_synonyms = estimate_work(batch)
        batch["estimated_kb_units_needed"] = estimated_units
        batch["estimated_synonym_additions_needed"] = estimated_synonyms
        batch["questions"].sort(
            key=lambda item: (-int(item["freq"]), str(item["dataset_category"]), str(item["question"]))
        )
        batch["likely_laws_or_regulations_needed"] = sorted(batch["likely_laws_or_regulations_needed"])
        batch["likely_synonym_additions_needed"] = sorted(batch["likely_synonym_additions_needed"])
        batch["root_causes"] = dict(sorted(batch["root_causes"].items()))
        batch["priority_score"] = round(float(batch["total_freq_impact"]) * priority_multiplier(batch), 2)

    ranked_batches = sorted(
        grouped.values(),
        key=lambda batch: (
            -float(batch["priority_score"]),
            -int(batch["total_freq_impact"]),
            -int(batch["questions_in_top100"]),
            str(batch["batch_name"]),
        ),
    )

    return {
        "meta": {
            "source_file": str(FB_PATH.relative_to(ROOT)),
            "knowledge_file": str(KB_PATH.relative_to(ROOT)),
            "based_on_unresolved_questions_from_top_200": len(unresolved_top200),
        },
        "batches": ranked_batches,
    }


def build_next_actions(batches_report: dict[str, Any]) -> list[dict[str, Any]]:
    next_actions: list[dict[str, Any]] = []
    for batch in batches_report["batches"][:10]:
        next_actions.append(
            {
                "batch_name": batch["batch_name"],
                "recommended_fix_type": batch["recommended_fix_type"],
                "estimated_kb_units_needed": batch["estimated_kb_units_needed"],
                "estimated_synonym_additions_needed": batch["estimated_synonym_additions_needed"],
                "expected_impact_on_top100_questions": batch["questions_in_top100"],
                "expected_impact_on_top100_pp": round(float(batch["questions_in_top100"]), 2),
                "expected_impact_on_top200_questions": batch["questions_in_top200"],
                "expected_impact_on_top200_pp": round(float(batch["questions_in_top200"]) / 2, 2),
                "likely_laws_or_regulations_needed": batch["likely_laws_or_regulations_needed"],
                "likely_synonym_additions_needed": batch["likely_synonym_additions_needed"],
                "priority_score": batch["priority_score"],
            }
        )
    return next_actions


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    known_synonyms = load_existing_synonyms()
    top100 = analyze_questions(limit=100, known_synonyms=known_synonyms)
    top200 = analyze_questions(limit=200, known_synonyms=known_synonyms)
    batches_report = build_batches(top100, top200, known_synonyms)
    next_actions = build_next_actions(batches_report)

    report = {
        "top_100": top100,
        "top_200": top200,
        "next_actions": next_actions,
    }

    write_json(REPORT_PATH, report)
    write_json(BATCHES_PATH, batches_report)

    print(
        json.dumps(
            {
                "top_100": top100["summary"],
                "top_200": top200["summary"],
                "top_batch": next_actions[0] if next_actions else None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
