from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from threading import Lock
from typing import Any


JSONDict = dict[str, Any]
_CACHE_LOCK = Lock()
_TAXONOMY_CACHE: dict[str, dict[str, JSONDict]] = {}
_SLOTS_CACHE: dict[str, dict[str, JSONDict]] = {}

STOP_WORDS = {
    "a",
    "aby",
    "albo",
    "ale",
    "bo",
    "co",
    "czy",
    "dla",
    "do",
    "i",
    "jak",
    "jest",
    "na",
    "nie",
    "o",
    "od",
    "oraz",
    "po",
    "przy",
    "sie",
    "się",
    "to",
    "w",
    "z",
    "za",
}

INTENT_KEYWORD_HINTS: dict[str, tuple[str, ...]] = {
    "vat_jpk_ksef": (
        "vat",
        "jpk",
        "jpk_v7",
        "jpkv7",
        "ksef",
        "faktura",
        "faktury",
        "faktura korygujaca",
        "korekta faktury",
        "nip",
        "gtu",
        "mpp",
        "wnt",
        "wdt",
    ),
    "zus": ("zus", "krus", "skladka", "skladki", "chorobowe", "macierzynski", "zasilek", "dra", "rca"),
    "payroll": ("lista plac", "wynagrodzenie", "pit11", "pit-11", "pit4r", "pit-4r", "platnik", "wyplata"),
    "hr": ("umowa o prace", "wypowiedzenie", "urlop", "pracownik", "swiadectwo pracy", "nadgodziny"),
    "pit_ryczalt": ("pit", "ryczalt", "ryczałt", "najem", "najmu", "liniowy", "skala podatkowa", "kpir", "ulga", "amortyzacja"),
    "cit_wht": ("cit", "wht", "ift", "cit-8", "cit8", "certyfikat rezydencji", "tpr", "estonski cit", "estoński cit"),
    "accounting_operational": ("ksiegowanie", "zaksi", "bilans", "rzis", "sprawozdanie", "konto", "dekret", "kpir"),
    "legal_procedural": ("korekta", "nadplata", "nadpłata", "pelnomocnictwo", "pełnomocnictwo", "upl-1", "pps-1", "czynny zal", "czynny żal"),
    "software_tooling": ("symfonia", "comarch", "insert", "enova", "optima", "subiekt", "program", "api", "integracja"),
    "business_of_accounting_office": ("biuro rachunkowe", "cennik", "klient", "rentownosc", "rentowność"),
    "education_community": ("kurs", "szkolenie", "egzamin", "certyfikat", "polecacie", "jak zaczac"),
    "out_of_scope": ("co myslicie", "jak wrazenia", "czy warto"),
}

SLOT_HINTS: dict[str, tuple[str, ...]] = {
    "obszar_prawa": ("vat", "pit", "cit", "zus", "ksef", "jpk", "urlop", "umowa", "podatek"),
    "stan_faktyczny": ("sprzedaz", "zakup", "najem", "pracownik", "spolka", "spółka", "jdg", "usluga", "usługa", "towar"),
    "okres_lub_data": ("202", "styczen", "styczeń", "luty", "marzec", "kwiecien", "kwiecień", "maj", "czerwiec", "lipiec", "sierp", "wrzes", "paź", "pazdz", "listopad", "grudzien", "grudzień", "miesiac", "miesiąc", "rok", "termin", "data"),
    "rodzaj_pisma_lub_wniosku": ("wniosek", "pismo", "korekta", "upl", "pps", "zaw", "czynny zal", "czynny żal", "nadplata", "nadpłata"),
    "organ_lub_kanał_złożenia": ("urzad", "urząd", "us", "skarbow", "e-urzad", "e-urząd", "bramka", "ksef", "jpk"),
    "etap_sprawy_lub_termin": ("po terminie", "przed kontrola", "przed kontrolą", "w trakcie", "po wysylce", "po wysyłce", "termin", "ile czasu"),
    "rodzaj_ksiąg_lub_ewidencji": ("kpir", "ksiegi", "księgi", "ewidencj", "bilans", "rejestr"),
    "rodzaj_dokumentu": ("faktur", "rach", "paragon", "jpk", "pit", "cit", "umow", "lista plac"),
    "okres_księgowy": ("miesiac", "miesiąc", "rok", "okres", "zamkniecie", "zamknięcie", "grudzien", "styczen"),
    "typ_umowy": ("umowa", "etat", "zlecen", "dzieło", "dzielo", "b2b", "kontrakt"),
    "składnik_wynagrodzenia_lub_dokument": ("premia", "dodatek", "pit", "plac", "płac", "wynagrodzen", "ekwiwalent"),
    "tytuł_ubezpieczenia": ("jdg", "zlecen", "etat", "wspolprac", "współprac", "spolka", "spółka"),
    "status_osoby": ("pracownik", "zleceniobiorca", "przedsiebiorca", "przedsiębiorca", "emeryt", "student"),
    "rodzaj_składki_lub_świadczenia": ("zdrowot", "spolecz", "społecz", "chorob", "macierzyn", "emerytaln", "rentow", "zasilek", "zasiłek"),
    "forma_opodatkowania": ("ryczalt", "ryczałt", "liniowy", "skala", "eston", "karta"),
    "źródło_przychodu": ("najem", "najmu", "najm", "sprzedaz", "sprzedaż", "działalność", "dzialalnosc", "etat", "zlecen", "dywidend", "leasing"),
    "typ_podmiotu": ("spolka", "spółka", "fundacja", "jdg", "osoba fizyczna", "sp z oo", "sa"),
    "rodzaj_transakcji_lub_płatności": ("dywidend", "odsetki", "licencj", "usluga", "usługa", "wyplata", "wypłata"),
    "nazwa_systemu": ("symfonia", "insert", "comarch", "enova", "optima", "wapro"),
    "czynność_operacyjna": ("import", "eksport", "ustawic", "ustawić", "zaksieg", "zaksięg", "wyslac", "wysłać", "wygenerowac", "wygenerować"),
    "kontekst_błędu_lub_integracji": ("blad", "błąd", "nie dziala", "nie działa", "integrac", "api", "import", "eksport"),
    "rola_lub_status_strony": ("sprzedawca", "nabywca", "odbiorca", "pelnomocnik", "pełnomocnik", "biuro rachunkowe", "podatnik", "taxpayer"),
}


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", (text or "").lower())
    without_marks = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", without_marks).strip()


def _tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9_]+", _normalize(text)) if token not in STOP_WORDS]


def _read_json_dict(path: str) -> dict[str, JSONDict]:
    file_path = Path(path)
    if not file_path.exists():
        raise ValueError(f"Curated JSON file does not exist: {file_path}")

    try:
        with file_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Curated JSON file is malformed: {file_path}") from exc

    if not isinstance(payload, dict):
        raise ValueError(f"Curated JSON file must contain an object: {file_path}")
    return payload


def _load_taxonomy(taxonomy_path: str) -> dict[str, JSONDict]:
    with _CACHE_LOCK:
        cached = _TAXONOMY_CACHE.get(taxonomy_path)
        if cached is not None:
            return cached

    taxonomy = _read_json_dict(taxonomy_path)
    with _CACHE_LOCK:
        _TAXONOMY_CACHE[taxonomy_path] = taxonomy
    return taxonomy


def _load_slots(slots_path: str) -> dict[str, JSONDict]:
    with _CACHE_LOCK:
        cached = _SLOTS_CACHE.get(slots_path)
        if cached is not None:
            return cached

    slots = _read_json_dict(slots_path)
    with _CACHE_LOCK:
        _SLOTS_CACHE[slots_path] = slots
    return slots


def _intent_keywords(intent: str, record: JSONDict) -> set[str]:
    text_parts: list[str] = [intent.replace("_", " ")]
    for key in ("description", "routing_recommendation"):
        value = record.get(key)
        if isinstance(value, str):
            text_parts.append(value)
    examples = record.get("examples")
    if isinstance(examples, list):
        text_parts.extend(str(example) for example in examples if isinstance(example, str))

    keywords = set(_tokenize(" ".join(text_parts)))
    for hint in INTENT_KEYWORD_HINTS.get(intent, ()):
        keywords.update(_tokenize(hint))
    return keywords


def classify_intent(query: str, taxonomy_path: str) -> str:
    """Classify a query into one curated intent using taxonomy-backed keyword matching.

    Args:
        query: User query to classify.
        taxonomy_path: Path to ``intent_taxonomy.json``.

    Returns:
        A taxonomy intent label or ``"unknown"`` when no keyword match is found.

    Raises:
        ValueError: If the taxonomy file is missing or malformed.
    """

    taxonomy = _load_taxonomy(taxonomy_path)
    query_tokens = set(_tokenize(query))
    normalized_query = _normalize(query)
    if not query_tokens:
        return "unknown"

    best_intent = "unknown"
    best_score = 0
    for intent, record in taxonomy.items():
        keywords = _intent_keywords(intent, record)
        score = sum(1 for token in query_tokens if token in keywords)
        for hint in INTENT_KEYWORD_HINTS.get(intent, ()):
            normalized_hint = _normalize(hint)
            if normalized_hint in normalized_query:
                score += 4 if " " in normalized_hint else 3
        if score > best_score:
            best_intent = intent
            best_score = score

    return best_intent if best_score > 0 else "unknown"


def detect_clarification_slots(query: str, slots_path: str, intent: str) -> dict[str, bool]:
    """Detect which required clarification slots are missing for a given intent.

    Args:
        query: User query to inspect.
        slots_path: Path to ``clarification_slots.json``.
        intent: Curated intent label.

    Returns:
        A mapping of required slot name to ``True`` when missing.

    Raises:
        ValueError: If the slots file is missing or malformed.
    """

    slots_payload = _load_slots(slots_path)
    if intent not in slots_payload:
        return {}

    slot_record = slots_payload[intent]
    required_slots = slot_record.get("required_facts")
    if not isinstance(required_slots, list):
        raise ValueError(f"Clarification slots for intent '{intent}' must contain 'required_facts' list.")

    normalized_query = _normalize(query)
    missing: dict[str, bool] = {}
    for slot_name in required_slots:
        if not isinstance(slot_name, str):
            raise ValueError(f"Invalid slot name for intent '{intent}' in clarification slots file.")
        hints = SLOT_HINTS.get(slot_name, ())
        missing[slot_name] = not any(_normalize(hint) in normalized_query for hint in hints)
    return missing
