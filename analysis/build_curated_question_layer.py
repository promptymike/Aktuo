from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RAW_QUESTIONS_PATH = ROOT / "fb_pipeline" / "all_questions_raw.json"
DEDUP_QUESTIONS_PATH = ROOT / "fb_pipeline" / "dedup_questions_output_v3.json"
CURATED_DIR = ROOT / "data" / "curated"
INTENT_TAXONOMY_PATH = CURATED_DIR / "intent_taxonomy.json"
CLARIFICATION_SLOTS_PATH = CURATED_DIR / "clarification_slots.json"
GOLDEN_EVAL_SET_PATH = CURATED_DIR / "golden_eval_set.jsonl"
WORKFLOW_SPLIT_PATH = CURATED_DIR / "workflow_vs_legal_vs_out_of_scope.jsonl"
REPORT_PATH = ROOT / "analysis" / "curated_question_layer_report.json"

TARGET_GOLDEN_RECORDS = 500
MIN_GOLDEN_RECORDS = 200
JSONDict = dict[str, Any]


INTENT_DEFINITIONS: dict[str, dict[str, str]] = {
    "legal_substantive": {
        "description": "Pytania o skutki materialnoprawne: obowiązki, stawki, limity i warunki zastosowania przepisu.",
        "routing_recommendation": "Kieruj do legal KB i odpowiedzi opartej na konkretnym przepisie.",
    },
    "legal_procedural": {
        "description": "Pytania o korekty, wnioski, pełnomocnictwa, terminy i tryb działania wobec organu.",
        "routing_recommendation": "Kieruj do Ordynacji podatkowej i polityki dopytań o dokument, organ i etap sprawy.",
    },
    "accounting_operational": {
        "description": "Pytania o księgowanie, KPiR, dekretację, okresy i operacyjną pracę księgowego.",
        "routing_recommendation": "Kieruj do workflow KB, a gdy trzeba, dołącz podstawę prawną.",
    },
    "payroll": {
        "description": "Pytania o listę płac, zaliczki, PIT płatnika i składniki wynagrodzenia.",
        "routing_recommendation": "Kieruj do warstwy kadrowo-płacowej z follow-upem o typ umowy i okres.",
    },
    "hr": {
        "description": "Pytania o stosunek pracy, urlopy, wypowiedzenia i obowiązki pracodawcy.",
        "routing_recommendation": "Kieruj do Kodeksu pracy, pytaj o typ umowy i daty.",
    },
    "zus": {
        "description": "Pytania o ZUS, składki, zbiegi tytułów, deklaracje i świadczenia.",
        "routing_recommendation": "Kieruj do źródeł ZUS i dopytuj o tytuł ubezpieczenia oraz status osoby.",
    },
    "vat_jpk_ksef": {
        "description": "Pytania o VAT, JPK_V7, KSeF, faktury, korekty, oznaczenia i rozliczenia VAT.",
        "routing_recommendation": "Kieruj do VAT/JPK/KSeF i pytaj o daty, dokument, rolę strony i kontekst transakcji.",
    },
    "pit_ryczalt": {
        "description": "Pytania o PIT, ryczałt, formę opodatkowania, źródła przychodu i rozliczenia roczne.",
        "routing_recommendation": "Kieruj do PIT/ryczałtu i pytaj o formę opodatkowania, źródło przychodu i rok.",
    },
    "cit_wht": {
        "description": "Pytania o CIT, WHT, CIT-8, rezydencję, IFT, TPR i opodatkowanie spółek.",
        "routing_recommendation": "Kieruj do CIT/WHT i pytaj o typ podmiotu, płatność i kontekst międzynarodowy.",
    },
    "software_tooling": {
        "description": "Pytania o programy księgowe, importy, integracje, błędy i konfiguracje narzędzi.",
        "routing_recommendation": "Traktuj jako workflow/product support, nie jako poradę prawną.",
    },
    "business_of_accounting_office": {
        "description": "Pytania o prowadzenie biura rachunkowego: cenniki, klienci, rentowność i organizacja pracy.",
        "routing_recommendation": "Traktuj jako business/community support poza rdzeniem legal RAG.",
    },
    "education_community": {
        "description": "Pytania o kursy, szkolenia, rozwój kariery i rekomendacje społeczności.",
        "routing_recommendation": "Traktuj jako community-only i nie udawaj autorytatywnej porady.",
    },
    "out_of_scope": {
        "description": "Pytania urwane, zbyt ogólne, towarzyskie albo niezwiązane z zakresem Aktuo.",
        "routing_recommendation": "Zwracaj out-of-scope albo prośbę o doprecyzowanie.",
    },
}


CLARIFICATION_SLOT_DEFINITIONS: dict[str, dict[str, list[str]]] = {
    "legal_substantive": {
        "required_facts": ["obszar_prawa", "stan_faktyczny", "okres_lub_data"],
        "optional_helpful_facts": ["status_podatnika", "rodzaj_dokumentu", "kontekst_krajowy_lub_zagraniczny"],
        "must_ask_follow_up_when": [
            "Brakuje kluczowego stanu faktycznego albo pytanie miesza kilka reżimów prawnych.",
            "Nie da się ustalić, którego podatku lub strony dotyczy pytanie.",
        ],
        "insufficient_data_when": ["Pytanie jest urwane i nie zawiera żadnego konkretu poza prośbą o pomoc."],
    },
    "legal_procedural": {
        "required_facts": ["rodzaj_pisma_lub_wniosku", "organ_lub_kanał_złożenia", "etap_sprawy_lub_termin"],
        "optional_helpful_facts": ["czy_jest_pełnomocnik", "czy_to_korekta", "forma_elektroniczna_lub_papierowa"],
        "must_ask_follow_up_when": [
            "Nie wiadomo, jaki dokument lub tryb proceduralny ma być zastosowany.",
            "Pytanie dotyczy pisma, ale nie wiadomo do jakiego organu i na jakim etapie sprawy.",
        ],
        "insufficient_data_when": ["Pytanie odwołuje się tylko do skrótu formularza bez opisu celu lub skutku."],
    },
    "accounting_operational": {
        "required_facts": ["rodzaj_ksiąg_lub_ewidencji", "rodzaj_dokumentu", "okres_księgowy"],
        "optional_helpful_facts": ["forma_opodatkowania", "status_vat", "typ_podmiotu"],
        "must_ask_follow_up_when": [
            "Nie wiadomo, czy chodzi o KPiR, pełne księgi czy ewidencję VAT.",
            "Brakuje dokumentu albo okresu, którego dotyczy zapis.",
        ],
        "insufficient_data_when": ["Pytanie nie zawiera operacyjnej decyzji do podjęcia."],
    },
    "payroll": {
        "required_facts": ["typ_umowy", "składnik_wynagrodzenia_lub_dokument", "okres_lub_data"],
        "optional_helpful_facts": ["status_pracownika", "wiek_lub_uprawnienie", "nieobecność_lub_urlop"],
        "must_ask_follow_up_when": [
            "Nie wiadomo, czy chodzi o etat, zlecenie, dzieło albo kontrakt menedżerski.",
            "Brakuje miesiąca rozliczenia albo rodzaju składnika płacowego.",
        ],
        "insufficient_data_when": ["Pytanie nie wskazuje żadnej czynności płacowej ani dokumentu."],
    },
    "hr": {
        "required_facts": ["typ_umowy", "etap_zatrudnienia", "okres_lub_data"],
        "optional_helpful_facts": ["rodzaj_nieobecności", "staż_pracy", "status_szczególny_pracownika"],
        "must_ask_follow_up_when": [
            "Nie wiadomo, czy chodzi o nawiązanie, trwanie czy rozwiązanie stosunku pracy.",
            "Brakuje typu umowy albo kluczowych dat.",
        ],
        "insufficient_data_when": ["Pytanie jest wyłącznie opiniotwórcze albo społecznościowe."],
    },
    "zus": {
        "required_facts": ["tytuł_ubezpieczenia", "status_osoby", "rodzaj_składki_lub_świadczenia"],
        "optional_helpful_facts": ["ciągłość_ubezpieczenia", "okres_lub_data", "rodzaj_dokumentu"],
        "must_ask_follow_up_when": [
            "Nie wiadomo, czy chodzi o JDG, etat, zlecenie, zbieg tytułów albo osobę współpracującą.",
            "Brakuje rodzaju świadczenia lub deklaracji ZUS.",
        ],
        "insufficient_data_when": ["Pytanie nie wskazuje żadnego tytułu do ubezpieczenia ani świadczenia."],
    },
    "vat_jpk_ksef": {
        "required_facts": ["rodzaj_dokumentu", "okres_lub_data", "rola_lub_status_strony"],
        "optional_helpful_facts": ["kontekst_krajowy_lub_zagraniczny", "czy_to_korekta", "kanał_ksef_lub_jpk"],
        "must_ask_follow_up_when": [
            "Brakuje daty/okresu albo typu dokumentu.",
            "Nie wiadomo, czy pytanie dotyczy sprzedawcy, nabywcy, pełnomocnika albo uprawnień w KSeF.",
        ],
        "insufficient_data_when": ["Pytanie jest tak skrótowe, że nie da się ustalić, czy chodzi o VAT, JPK czy KSeF."],
    },
    "pit_ryczalt": {
        "required_facts": ["forma_opodatkowania", "źródło_przychodu", "okres_lub_data"],
        "optional_helpful_facts": ["status_prywatny_lub_firmowy", "rodzaj_majątku", "czy_to_korekta"],
        "must_ask_follow_up_when": [
            "Nie wiadomo, czy chodzi o skalę, liniowy, ryczałt albo najem prywatny.",
            "Brakuje źródła przychodu albo roku podatkowego.",
        ],
        "insufficient_data_when": ["Pytanie nie wskazuje źródła przychodu ani formy opodatkowania."],
    },
    "cit_wht": {
        "required_facts": ["typ_podmiotu", "rodzaj_transakcji_lub_płatności", "okres_lub_data"],
        "optional_helpful_facts": ["kraj_kontrahenta", "rezydencja_podatkowa", "formularz_lub_obowiązek"],
        "must_ask_follow_up_when": [
            "Nie wiadomo, czy chodzi o klasyczny CIT, estoński CIT czy WHT.",
            "Brakuje informacji o płatności, podmiocie albo kontekście międzynarodowym.",
        ],
        "insufficient_data_when": ["Pytanie jest zbyt skrótowe, by ustalić obszar CIT/WHT."],
    },
    "software_tooling": {
        "required_facts": ["nazwa_systemu", "czynność_operacyjna", "kontekst_błędu_lub_integracji"],
        "optional_helpful_facts": ["wersja_systemu", "format_pliku", "obszar_merytoryczny"],
        "must_ask_follow_up_when": ["Nie wiadomo, jakiego programu dotyczy pytanie albo jaka akcja się nie udaje."],
        "insufficient_data_when": ["Pytanie ma wyłącznie formę rekomendacji narzędzia bez kryteriów."],
    },
}


SLOT_PROMPTS: dict[str, str] = {
    "obszar_prawa": "Jakiego obszaru dotyczy pytanie: VAT, PIT, CIT, ZUS, KSeF czy kadry?",
    "stan_faktyczny": "Opisz krótko stan faktyczny: jaka czynność lub sytuacja wystąpiła?",
    "okres_lub_data": "Podaj okres lub datę, której dotyczy pytanie.",
    "rodzaj_pisma_lub_wniosku": "Jakie pismo, wniosek albo formularz chcesz złożyć lub skorygować?",
    "organ_lub_kanał_złożenia": "Do jakiego organu lub przez jaki kanał ma trafić dokument?",
    "etap_sprawy_lub_termin": "Na jakim etapie jest sprawa i jaki termin ma znaczenie?",
    "rodzaj_ksiąg_lub_ewidencji": "Czy chodzi o KPiR, pełne księgi, ewidencję VAT czy inną ewidencję?",
    "rodzaj_dokumentu": "Jakiego dokumentu dotyczy pytanie: faktury, korekty, umowy, JPK, deklaracji?",
    "okres_księgowy": "Za jaki okres księgowy lub miesiąc chcesz to ująć?",
    "typ_umowy": "Jaki jest typ umowy: etat, zlecenie, dzieło, B2B czy inna forma?",
    "składnik_wynagrodzenia_lub_dokument": "Jakiego składnika wynagrodzenia lub dokumentu dotyczy pytanie?",
    "tytuł_ubezpieczenia": "Jaki jest tytuł do ubezpieczenia: JDG, etat, zlecenie czy inny?",
    "status_osoby": "Kogo dotyczy pytanie: pracownika, zleceniobiorcy, przedsiębiorcy, emeryta?",
    "rodzaj_składki_lub_świadczenia": "O jaką składkę lub świadczenie chodzi: zdrowotną, społeczną, chorobowe, zasiłek?",
    "forma_opodatkowania": "Jaka jest forma opodatkowania: skala, liniowy, ryczałt, estoński CIT?",
    "źródło_przychodu": "Jakie jest źródło przychodu: działalność, najem, etat, zlecenie, dywidenda?",
    "typ_podmiotu": "Jakiego podmiotu dotyczy pytanie: JDG, spółki, fundacji czy osoby fizycznej?",
    "rodzaj_transakcji_lub_płatności": "Jakiej transakcji lub płatności dotyczy pytanie?",
    "nazwa_systemu": "Jakiego programu lub systemu dotyczy problem?",
    "czynność_operacyjna": "Jaką czynność chcesz wykonać w systemie lub procesie?",
    "kontekst_błędu_lub_integracji": "Jaki błąd, komunikat albo problem z integracją się pojawia?",
    "rola_lub_status_strony": "Kim jest strona w tej sytuacji: sprzedawcą, nabywcą, podatnikiem, pełnomocnikiem?",
}


INTENT_SOURCE_HINTS: dict[str, list[str]] = {
    "legal_substantive": ["legal_kb"],
    "legal_procedural": ["Ordynacja podatkowa", "legal_kb"],
    "accounting_operational": ["workflow_kb", "Ustawa o rachunkowości"],
    "payroll": ["workflow_kb", "Kodeks pracy", "PIT"],
    "hr": ["Kodeks pracy", "legal_kb"],
    "zus": ["Ustawa o systemie ubezpieczeń społecznych", "legal_kb"],
    "vat_jpk_ksef": ["Ustawa o VAT", "Rozporządzenie JPK_V7", "Rozporządzenie KSeF"],
    "pit_ryczalt": ["Ustawa o PIT", "Ustawa o ryczałcie"],
    "cit_wht": ["Ustawa o CIT", "WHT"],
    "software_tooling": ["workflow_kb"],
    "business_of_accounting_office": ["community_knowledge"],
    "education_community": ["community_knowledge"],
    "out_of_scope": [],
}


EXPECTED_AREA_BY_INTENT: dict[str, str] = {
    "legal_substantive": "przepisy materialne",
    "legal_procedural": "Ordynacja podatkowa / procedury",
    "accounting_operational": "rachunkowość operacyjna",
    "payroll": "kadry i płace",
    "hr": "Kodeks pracy",
    "zus": "ZUS",
    "vat_jpk_ksef": "VAT / JPK / KSeF",
    "pit_ryczalt": "PIT / ryczałt",
    "cit_wht": "CIT / WHT",
    "software_tooling": "oprogramowanie księgowe",
    "business_of_accounting_office": "prowadzenie biura rachunkowego",
    "education_community": "edukacja i społeczność",
    "out_of_scope": "poza zakresem",
}


@dataclass(slots=True)
class AggregatedQuestion:
    question: str
    normalized_question: str
    dedupe_key: str
    source_frequency: int
    category: str
    subcategory: str
    source_post_count: int
    examples: list[str]


def normalize_text(value: str) -> str:
    """Return whitespace-normalized text with repaired Unicode form."""
    cleaned = unicodedata.normalize("NFKC", value or "")
    cleaned = cleaned.replace("\u00a0", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def strip_diacritics(value: str) -> str:
    """Return an ASCII-like form used for robust keyword matching."""
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def build_dedupe_key(question: str) -> str:
    """Create a conservative normalization key for near-identical questions."""
    normalized = strip_diacritics(normalize_text(question).lower())
    normalized = normalized.replace("jpk_v7", "jpkv7")
    normalized = normalized.replace("jpk v7", "jpkv7")
    normalized = normalized.replace("ksef", "ksef")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def load_json(path: Path) -> Any:
    """Load JSON content from disk."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_raw_questions(path: Path) -> list[JSONDict]:
    """Load the raw exported accountant questions."""
    raw_data = load_json(path)
    if not isinstance(raw_data, list):
        raise ValueError(f"Expected a JSON list in {path}")
    return [item for item in raw_data if isinstance(item, dict)]


def load_dedup_questions(path: Path) -> list[JSONDict]:
    """Load the deduplicated question export."""
    dedup_data = load_json(path)
    if not isinstance(dedup_data, dict) or not isinstance(dedup_data.get("questions"), list):
        raise ValueError(f"Expected a JSON object with 'questions' list in {path}")
    return [item for item in dedup_data["questions"] if isinstance(item, dict)]


def aggregate_questions(raw_questions: list[JSONDict], dedup_questions: list[JSONDict]) -> list[AggregatedQuestion]:
    """Build a conservatively deduplicated question set with preserved frequencies."""
    raw_counter: Counter[str] = Counter()
    raw_examples: defaultdict[str, list[str]] = defaultdict(list)
    for item in raw_questions:
        question = normalize_text(str(item.get("q", "")))
        if not question:
            continue
        dedupe_key = build_dedupe_key(question)
        raw_counter[dedupe_key] += 1
        if question not in raw_examples[dedupe_key] and len(raw_examples[dedupe_key]) < 5:
            raw_examples[dedupe_key].append(question)

    aggregated: dict[str, AggregatedQuestion] = {}
    for item in dedup_questions:
        question = normalize_text(str(item.get("q", "")))
        if not question:
            continue
        dedupe_key = build_dedupe_key(question)
        freq = int(item.get("freq", 1) or 1)
        category = normalize_text(str(item.get("cat", "inne"))) or "inne"
        subcategory = normalize_text(str(item.get("sub", "")))
        source_post_count = len(item.get("post_ids", [])) if isinstance(item.get("post_ids"), list) else 0
        source_frequency = max(freq, raw_counter.get(dedupe_key, 0), 1)

        if dedupe_key in aggregated:
            existing = aggregated[dedupe_key]
            existing.source_frequency += source_frequency
            existing.source_post_count += source_post_count
            for example in raw_examples.get(dedupe_key, [question]):
                if example not in existing.examples and len(existing.examples) < 5:
                    existing.examples.append(example)
            if len(question) > len(existing.question):
                existing.question = question
                existing.normalized_question = normalize_text(question.lower())
                existing.category = category
                existing.subcategory = subcategory
            continue

        aggregated[dedupe_key] = AggregatedQuestion(
            question=question,
            normalized_question=normalize_text(question.lower()),
            dedupe_key=dedupe_key,
            source_frequency=source_frequency,
            category=category,
            subcategory=subcategory,
            source_post_count=source_post_count,
            examples=raw_examples.get(dedupe_key, [question])[:5],
        )

    return sorted(
        aggregated.values(),
        key=lambda item: (-item.source_frequency, item.category, item.question.lower()),
    )


def contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    """Return True when any token appears in the ASCII-normalized text."""
    normalized = strip_diacritics(text.lower())
    return any(token in normalized for token in tokens)


def infer_primary_intent(question: AggregatedQuestion) -> str:
    """Infer the primary product intent for a question."""
    text = strip_diacritics(f"{question.question} {question.subcategory}".lower())
    category = strip_diacritics(question.category.lower())

    if contains_any(text, ("symfonia", "optima", "comarch", "insert", "enova", "wf mag", "api", "integrac", "import ", "eksport ", "program")):
        return "software_tooling"
    if contains_any(text, ("kurs", "szkolen", "studia", "egzamin", "certyfikat", "polecacie", "polecacie kogos", "gdzie sie uczyc")):
        return "education_community"
    if contains_any(text, ("biuro rachunkowe", "cennik", "ile bierzecie", "jak wyceniacie", "pozyskac klienta", "rentownosc", "zarabiacie")):
        return "business_of_accounting_office"
    if contains_any(text, ("urlop", "wypowiedzen", "umowa o prace", "okres probny", "swiadectwo pracy", "pracownik", "kodeks pracy", "nadgodzin", "praca zdalna")) or category == "kadry":
        return "hr"
    if contains_any(text, ("lista plac", "wynagrodzen", "pit 11", "pit-11", "pit 4r", "pit-4r", "zaliczka od wynagrodzen", "pracodawca jako platnik", "skladnik wynagrodzenia")):
        return "payroll"
    if contains_any(text, ("zus", "krus", "chorobow", "macierzyn", "zasilek", "rca", "dra", "zua", "zpa", "ubezpieczen")) or category == "zus":
        return "zus"
    if contains_any(text, ("cit", "wht", "ift", "certyfikat rezydencji", "ceny transferowe", "tpr", "esto", "spolka z oo", "spolka z o o", "cit-8")) or category == "cit":
        return "cit_wht"
    if contains_any(text, ("pit", "ryczalt", "najem", "liniowy", "skala podatkowa", "dzialalnosc gospodarcza", "ulga", "przychod", "kpir", "amortyzac")) or category == "pit":
        return "pit_ryczalt"
    if contains_any(text, ("vat", "jpk", "ksef", "faktur", "gtu", "mpp", "wnt", "wdt", "ulga na zle dlugi")) or category in {"vat", "jpk", "ksef"}:
        return "vat_jpk_ksef"
    if contains_any(text, ("korekta", "czynny zal", "czynny żal", "nadplata", "pelnomoc", "upel", "upl-1", "pps-1", "stwierdzenie nadplaty", "wezwanie", "urzad skarbowy", "ordynacja")) or category == "ordynacja":
        return "legal_procedural"
    if contains_any(text, ("zaksi", "dekret", "bilans", "rzis", "sprawozdanie finansowe", "inwentaryzac", "dowod ksiegowy", "konto", "pk", "rozliczenie miedzyokresowe")) or category == "rachunkowosc":
        return "accounting_operational"
    if contains_any(text, ("podatek", "stawka", "limit", "zwolnienie", "obowiazek", "podstawa opodatkowania", "termin zaplaty", "termin zlozenia")):
        return "legal_substantive"
    if len(question.dedupe_key.split()) < 3:
        return "out_of_scope"
    return "legal_substantive"


def infer_secondary_intent(question: AggregatedQuestion, primary_intent: str) -> str | None:
    """Infer a supporting secondary intent when the question spans two areas."""
    text = strip_diacritics(f"{question.question} {question.subcategory}".lower())
    if primary_intent == "vat_jpk_ksef" and contains_any(text, ("korekta", "czynny zal", "pełnomoc", "pelnomoc", "urzad")):
        return "legal_procedural"
    if primary_intent == "pit_ryczalt" and contains_any(text, ("zaksi", "kpir", "ewidencj", "bilans")):
        return "accounting_operational"
    if primary_intent == "cit_wht" and contains_any(text, ("vat", "samochod", "leasing")):
        return "legal_substantive"
    if primary_intent == "accounting_operational" and contains_any(text, ("pit", "vat", "cit", "ryczalt")):
        return "legal_substantive"
    if primary_intent == "hr" and contains_any(text, ("zus", "chorobow", "zasilek")):
        return "zus"
    if primary_intent == "payroll" and contains_any(text, ("urlop", "wypowiedzen", "kodeks pracy")):
        return "hr"
    return None


def determine_classification(primary_intent: str, question: AggregatedQuestion) -> str:
    """Map a question to legal/workflow/community scope classification."""
    text = strip_diacritics(question.question.lower())
    if primary_intent == "out_of_scope":
        return "outside_scope"
    if primary_intent in {"business_of_accounting_office", "education_community"}:
        return "community_only"
    if primary_intent in {"accounting_operational", "software_tooling"}:
        return "workflow"
    if primary_intent in {"legal_substantive", "legal_procedural", "payroll", "hr", "zus", "vat_jpk_ksef", "pit_ryczalt", "cit_wht"}:
        if contains_any(text, ("jak zaksi", "jak ujac", "gdzie wpisac", "jak oznaczyc", "jak ustawic", "jak technicznie")):
            return "mixed"
        return "legal"
    return "mixed"


def detect_clarification_need(primary_intent: str, question: AggregatedQuestion) -> tuple[bool, list[str], list[str]]:
    """Return whether a follow-up is needed together with missing and helpful fields."""
    slots = CLARIFICATION_SLOT_DEFINITIONS.get(primary_intent, {})
    required_facts = list(slots.get("required_facts", []))
    helpful_facts = list(slots.get("optional_helpful_facts", []))
    text = strip_diacritics(question.question.lower())

    conditions: dict[str, tuple[str, ...]] = {
        "obszar_prawa": ("vat", "pit", "cit", "zus", "ksef", "jpk", "urlop", "umowa", "podatek"),
        "stan_faktyczny": ("sprzedaz", "zakup", "najem", "pracownik", "spolka", "jdg", "usluga", "towar"),
        "okres_lub_data": ("202", "styczen", "luty", "marzec", "kwiecien", "maj", "czerwiec", "lipiec", "sierp", "wrzes", "pazdz", "listopad", "grudzien", "miesiac", "rok", "termin", "data"),
        "rodzaj_pisma_lub_wniosku": ("wniosek", "pismo", "korekta", "upl", "pps", "zaw", "czynny zal", "nadplata"),
        "organ_lub_kanał_złożenia": ("urzad", "us", "skarbow", "e-urzad", "bramka", "ksef", "jpk"),
        "etap_sprawy_lub_termin": ("po terminie", "przed kontrola", "w trakcie", "po wysylce", "termin", "ile czasu"),
        "rodzaj_ksiąg_lub_ewidencji": ("kpir", "ksiegi", "ewidencj", "bilans", "rejestr"),
        "rodzaj_dokumentu": ("fakt", "rach", "paragon", "jpk", "pit", "cit", "umow", "lista plac"),
        "okres_księgowy": ("miesiac", "rok", "okres", "zamkniecie", "grudzien", "styczen"),
        "typ_umowy": ("umowa", "etat", "zlecen", "dzielo", "b2b", "kontrakt"),
        "składnik_wynagrodzenia_lub_dokument": ("premia", "dodatek", "pit", "plac", "wynagrodzen", "ekwiwalent"),
        "tytuł_ubezpieczenia": ("jdg", "zlecen", "etat", "wspolprac", "spolka"),
        "status_osoby": ("pracownik", "zleceniobiorca", "przedsiebiorca", "emeryt", "student"),
        "rodzaj_składki_lub_świadczenia": ("zdrowot", "spolecz", "chorob", "macierzyn", "emerytaln", "rentow"),
        "forma_opodatkowania": ("ryczalt", "liniowy", "skala", "eston", "karta"),
        "źródło_przychodu": ("najem", "sprzedaz", "dzialalnosc", "etat", "zlecen", "dywidend", "leasing"),
        "typ_podmiotu": ("spolka", "fundacja", "jdg", "osoba fizyczna", "sp z oo", "sa"),
        "rodzaj_transakcji_lub_płatności": ("dywidend", "odsetki", "licencj", "usluga", "wyplata"),
        "nazwa_systemu": ("symfonia", "insert", "comarch", "enova", "optima", "wapro"),
        "czynność_operacyjna": ("import", "eksport", "ustawic", "zaksieg", "wyslac", "wygenerowac"),
    }

    missing_facts: list[str] = []
    for fact in required_facts:
        fact_tokens = conditions.get(fact, ())
        if fact_tokens and not any(token in text for token in fact_tokens):
            missing_facts.append(fact)

    needs_clarification = bool(missing_facts)
    return needs_clarification, missing_facts, helpful_facts


def build_taxonomy_records(questions: list[AggregatedQuestion]) -> dict[str, JSONDict]:
    """Build the intent taxonomy file with corpus-backed examples."""
    examples_by_intent: defaultdict[str, list[str]] = defaultdict(list)
    for question in questions:
        primary_intent = infer_primary_intent(question)
        if len(examples_by_intent[primary_intent]) >= 5:
            continue
        examples_by_intent[primary_intent].append(question.question)

    records: dict[str, JSONDict] = {}
    for intent, definition in INTENT_DEFINITIONS.items():
        records[intent] = {
            "description": definition["description"],
            "routing_recommendation": definition["routing_recommendation"],
            "examples": examples_by_intent.get(intent, []),
        }
    return records


def expected_behavior(classification: str, needs_clarification: bool, missing_facts: list[str], question: str) -> str:
    """Choose the expected product behavior for an eval record."""
    if classification == "outside_scope":
        return "out_of_scope"
    if needs_clarification and (len(missing_facts) >= 2 or len(build_dedupe_key(question).split()) < 4):
        return "insufficient_data"
    if needs_clarification:
        return "ask_follow_up"
    if classification == "community_only":
        return "out_of_scope"
    if classification == "workflow" and classification != "mixed":
        return "answer_directly"
    return "answer_directly"


def expected_source_type(classification: str) -> str:
    """Map classification to the expected answer source type."""
    if classification == "workflow":
        return "workflow_kb"
    if classification == "mixed":
        return "mixed"
    return "legal_kb"


def build_curated_record(question: AggregatedQuestion) -> JSONDict:
    """Build a normalized annotated record used by downstream artifacts."""
    primary_intent = infer_primary_intent(question)
    secondary_intent = infer_secondary_intent(question, primary_intent)
    classification = determine_classification(primary_intent, question)
    needs_clarification, missing_facts, helpful_facts = detect_clarification_need(primary_intent, question)
    expected_law_or_area = EXPECTED_AREA_BY_INTENT.get(primary_intent, "nieustalone")
    if secondary_intent:
        expected_law_or_area = f"{expected_law_or_area} + {EXPECTED_AREA_BY_INTENT.get(secondary_intent, secondary_intent)}"

    notes: list[str] = []
    if missing_facts:
        notes.append(f"Brakujące fakty: {', '.join(missing_facts)}")
    if classification == "mixed":
        notes.append("Pytanie łączy workflow operacyjny z warstwą prawną.")
    if primary_intent in {"software_tooling", "business_of_accounting_office", "education_community"}:
        notes.append("Nie jest to klasyczne pytanie do legal RAG.")

    return {
        "question": question.question,
        "normalized_question": question.normalized_question,
        "source_frequency": question.source_frequency,
        "source_category": question.category,
        "source_subcategory": question.subcategory,
        "primary_intent": primary_intent,
        "secondary_intent": secondary_intent,
        "classification": classification,
        "needs_clarification": needs_clarification,
        "missing_clarification_fields": missing_facts,
        "optional_helpful_facts": helpful_facts,
        "likely_required_sources": INTENT_SOURCE_HINTS.get(primary_intent, []),
        "expected_behavior": expected_behavior(classification, needs_clarification, missing_facts, question.question),
        "expected_source_type": expected_source_type(classification),
        "expected_law_or_area": expected_law_or_area,
        "notes": " ".join(notes).strip(),
    }


def build_workflow_split_records(questions: list[AggregatedQuestion]) -> list[JSONDict]:
    """Build the workflow/legal/out-of-scope classification layer."""
    records = [build_curated_record(question) for question in questions]
    return sorted(records, key=lambda item: (-int(item["source_frequency"]), item["question"].lower()))


def choose_golden_eval_records(records: list[JSONDict]) -> list[JSONDict]:
    """Select a deterministic, high-signal eval set from the curated records."""
    target = min(TARGET_GOLDEN_RECORDS, len(records))
    per_intent_buckets: defaultdict[str, list[JSONDict]] = defaultdict(list)
    for record in records:
        per_intent_buckets[str(record["primary_intent"])].append(record)

    selected: list[JSONDict] = []
    intents_in_order = sorted(per_intent_buckets)
    quota = max(8, target // max(len(intents_in_order), 1))
    for intent in intents_in_order:
        candidates = per_intent_buckets[intent]
        candidates.sort(key=lambda item: (-int(item["source_frequency"]), item["question"].lower()))
        selected.extend(candidates[:quota])

    if len(selected) < MIN_GOLDEN_RECORDS:
        raise ValueError("Golden eval selection produced fewer than the minimum required records.")

    seen_questions: set[str] = set()
    unique_selected: list[JSONDict] = []
    for record in sorted(selected, key=lambda item: (-int(item["source_frequency"]), item["question"].lower())):
        question = str(record["question"])
        if question in seen_questions:
            continue
        seen_questions.add(question)
        unique_selected.append(record)

    if len(unique_selected) < target:
        for record in records:
            question = str(record["question"])
            if question in seen_questions:
                continue
            seen_questions.add(question)
            unique_selected.append(record)
            if len(unique_selected) >= target:
                break

    return unique_selected[: max(MIN_GOLDEN_RECORDS, min(target, len(unique_selected)))]


def top_counter_items(counter: Counter[str], limit: int = 10) -> list[JSONDict]:
    """Render a counter as a deterministic JSON-friendly list."""
    return [
        {"label": label, "count": count}
        for label, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def build_report(
    raw_questions: list[JSONDict],
    deduplicated_questions: list[AggregatedQuestion],
    workflow_records: list[JSONDict],
) -> JSONDict:
    """Build the curated question layer report."""
    taxonomy_distribution = Counter(str(record["primary_intent"]) for record in workflow_records)
    classification_distribution = Counter(str(record["classification"]) for record in workflow_records)
    ambiguity_counter: Counter[str] = Counter()
    missing_fields_counter: Counter[str] = Counter()
    roadmap_counter: Counter[str] = Counter()

    for record in workflow_records:
        if record["needs_clarification"]:
            ambiguity_counter[str(record["primary_intent"])] += int(record["source_frequency"])
            for field in record["missing_clarification_fields"]:
                missing_fields_counter[str(field)] += int(record["source_frequency"])
        if record["classification"] in {"workflow", "mixed"}:
            roadmap_counter["workflow_kb"] += int(record["source_frequency"])
        elif record["classification"] == "legal":
            roadmap_counter["legal_kb_depth"] += int(record["source_frequency"])
        elif record["classification"] == "community_only":
            roadmap_counter["community_or_content"] += int(record["source_frequency"])
        else:
            roadmap_counter["scope_filtering"] += int(record["source_frequency"])

    return {
        "total_raw_questions": len(raw_questions),
        "deduplicated_questions": len(deduplicated_questions),
        "taxonomy_distribution": dict(sorted(taxonomy_distribution.items())),
        "workflow_vs_legal_split": dict(sorted(classification_distribution.items())),
        "top_ambiguity_areas": top_counter_items(ambiguity_counter),
        "top_missing_clarification_fields": top_counter_items(missing_fields_counter),
        "top_roadmap_implications": top_counter_items(roadmap_counter),
    }


def write_json(path: Path, payload: Any) -> None:
    """Write deterministic pretty JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def write_jsonl(path: Path, records: list[JSONDict]) -> None:
    """Write deterministic JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def build_outputs() -> JSONDict:
    """Build all curated question layer artifacts and return summary counts."""
    raw_questions = load_raw_questions(RAW_QUESTIONS_PATH)
    dedup_questions = load_dedup_questions(DEDUP_QUESTIONS_PATH)
    deduplicated_questions = aggregate_questions(raw_questions, dedup_questions)
    taxonomy = build_taxonomy_records(deduplicated_questions)
    workflow_records = build_workflow_split_records(deduplicated_questions)
    golden_eval_records = choose_golden_eval_records(workflow_records)
    report = build_report(raw_questions, deduplicated_questions, workflow_records)

    write_json(INTENT_TAXONOMY_PATH, taxonomy)
    clarification_payload = dict(CLARIFICATION_SLOT_DEFINITIONS)
    clarification_payload["slot_prompts"] = SLOT_PROMPTS
    write_json(CLARIFICATION_SLOTS_PATH, clarification_payload)
    write_jsonl(GOLDEN_EVAL_SET_PATH, golden_eval_records)
    write_jsonl(WORKFLOW_SPLIT_PATH, workflow_records)
    write_json(REPORT_PATH, report)

    return {
        "raw_questions": len(raw_questions),
        "deduplicated_questions": len(deduplicated_questions),
        "taxonomy_intents": len(taxonomy),
        "clarification_slot_intents": len(CLARIFICATION_SLOT_DEFINITIONS),
        "golden_eval_records": len(golden_eval_records),
        "workflow_split_records": len(workflow_records),
    }


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Build the curated question intelligence layer from the FB corpus.")
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    parse_args()
    summary = build_outputs()
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
