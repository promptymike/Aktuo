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
    "cos",        # coś = something — pronoun, no topic signal
    "czy",
    "dla",
    "do",
    "i",
    "jak",
    "jest",
    "kto",        # who — interrogative pronoun, noisy across many taxonomy examples
    "ktos",       # ktoś = someone — pronoun appearing in many taxonomy examples
    "moze",       # może = maybe/can — modal verb, no topic signal
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

# Intents with no clarification slots defined.  Queries routed here never
# trigger follow-up questions, so ambiguous matches are penalised to let
# slotted intents with comparable scores win instead.
_SLOTLESS_INTENTS = frozenset({
    "business_of_accounting_office",
    "education_community",
    "out_of_scope",
})

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
        "vat-26",
        "vat26",
        "oss",
        "clo",
        "cło",
        "leasing samochodu",
        "samochod ciezarowy",
        "samochod osobowy",
        "leasing operacyjny",
        "kasa fiskalna",
        "kasy fiskalne",
        "odliczenie vat",
        "odliczac vat",
        "100 vat",
        "darowizna",         # donation subject to VAT
        "stawka vat",        # VAT rate query
        "proporcja vat",     # proportional VAT deduction
        "odwrotne obciazenie",  # reverse charge
        "import uslug",      # import usług — import of services, art. 28b
        "kase fiskaln",      # prefix: kasę fiskalną / kasy fiskalne (inflected forms)
    ),
    "zus": (
        "zus",
        "krus",
        "skladka",
        "skladki",
        "chorobowe",
        "macierzynski",
        "zasilek",
        "dra",
        "rca",
        # Additional anchors for PUE/e-Płatnik and reduced-contribution queries (top unknown group)
        "pue",               # Platforma Usług Elektronicznych ZUS
        "e-platnik",         # electronic payer system
        "e platnik",
        "zwua",              # ZUS ZWUA deregistration report
        "maly zus",          # "Mały ZUS Plus" reduced contributions
        "preferencyjny",     # preferential/reduced ZUS rates
        "pfron",             # PFRON disabled-persons fund levy
        "ubezpiecz",         # prefix: ubezpieczenie/ubezpieczenia/ubezpieczeniowe — insurance
        "formularz a1",      # ZUS A1 form for cross-border social security
    ),
    "payroll": (
        "lista plac",
        "wynagrodzenie",
        "pit11",
        "pit-11",
        "pit 11",
        "pit11a",
        "pit-11a",
        "pit 11a",
        "pit40a",
        "pit-40a",
        "pit 40a",
        "pit4r",
        "pit-4r",
        "pit 4r",
        "pit-4",
        "pit 4",
        "platnik",
        "wyplata",
    ),
    "hr": (
        "umowa o prace",
        "wypowiedzenie",
        "urlop",
        "pracownik",
        "swiadectwo pracy",
        "nadgodziny",
        "dziecko",       # "Odnośnie ulgi na dziecko?" – child-relief employee declaration
        "zmieni",        # "Co się zmieniło?", "Co się zmienił?" – HR law updates (prefix avoids ł normalization issue)
        "umowa zleceni",   # prefix: umowa zlecenie/zlecenia — civil law contract
        "etat",            # full-time employment
        "wspolprac",       # prefix: współpraca/współpracy — cooperation/employment
    ),
    "legal_substantive": (
        "ogarnac",           # "Jak to ogarnąć?"
        "prosze o pomoc",    # "Bardzo proszę o pomoc?"
        "w czym problem",    # "A w czym problem?"
        "co robie zle",      # "Co robię źle?"
        "nie rozumiem",      # general confusion about a legal rule
    ),
    "pit_ryczalt": (
        # Bare "pit" removed — it matched inside unrelated words (pulpity, kapitał).
        # Specific PIT form hints and multi-word anchors provide targeted matching.
        "pit-37",
        "pit 37",
        "pit37",
        "pit-36",
        "pit 36",
        "pit36",
        "rozliczenie pit",   # "jak rozliczyć PIT"
        "deklaracja pit",    # "deklaracja PIT-37"
        "zeznanie pit",      # "zeznanie roczne PIT"
        "pit roczny",        # "PIT roczny za 2025"
        "pit liniowy",       # "PIT liniowy"
        "ryczalt",
        "ryczałt",
        "najem",
        "najmu",
        "liniowy",
        "skala podatkowa",
        "kpir",
        "kup",
        "ulga",
        "amortyzacja",
        "koszt podatkowy",
        "przychod podatkowy",
        "wykup samochodu",
    ),
    "cit_wht": (
        "cit",
        "wht",
        "ift",
        "ift2r",
        "ift-2r",
        "ift 2r",
        "cit-8",
        "cit8",
        "certyfikat rezydencji",
        "tpr",
        "jpk cit",
        "estonski cit",
        "estoński cit",
        "estonczyk",
        "ukryte zyski",
        "ryczalt od dochodow",
        "dywidend",
    ),
    "accounting_operational": (
        "ksiegowanie",
        "zaksi",
        "bilans",
        "rzis",
        "sprawozdanie",
        "konto",
        "dekret",
        "kpir",
        # Additional anchors for cost-booking and asset queries (top unknown group)
        "remanent",          # inventory count at year-end
        "srodek trwaly",     # fixed asset
        "wartosci niematerialne",  # intangible assets
        "zamkniecie roku",   # year-end close
        "bilans otwarcia",   # opening balance
        "wynik finansowy",   # financial result
        "nota ksiegowa",     # accounting note
        "przeksiegowanie",   # reclassification entry
        "ujac koszt",        # "jak ująć koszt" generic cost booking
        "na kontach",
        "konto 300",
        "rozliczenie zakupu",
        "pod jaka data",
        "data zapisania",
        "koszty uboczne zakupu",
        "kolumna",
        "kolumny",
        "kst",
        "zakup towarow",
    ),
    "legal_procedural": (
        "korekta", "nadplata", "nadpłata", "pelnomocnictwo", "pełnomocnictwo",
        "upl-1", "pps-1", "czynny zal", "czynny żal",
        "wezwani",           # prefix: wezwanie/wezwania/wezwań
        "konsekwencj",       # prefix: konsekwencje/konsekwencji
        "kara",              # kara za nieterminowe złożenie
        "kary",              # plural: kary pieniężne
        "sankcj",            # prefix: sankcja/sankcji/sankcje
    ),
    "software_tooling": (
        "symfonia", "comarch", "insert", "enova", "optima", "subiekt",
        "program", "api", "integracja",
        "streamsoft",        # Streamsoft PRO — Polish ERP
        "saldeo",            # Saldeo — document scanning / automation
        "rewizor",           # Rewizor GT / nexo — accounting program
        "sage",              # Sage Symfonia / Sage 50
        "wapro",             # WAPRO ERP
        "fakturownia",       # Fakturownia.pl — invoicing SaaS
        "mala ksiegowosc",   # Mała Księgowość Rzeczpospolita (nominative)
        "malej ksiegowosci", # Mała Księgowość (genitive/locative)
        "program ksiegowy",  # generic "accounting program"
        "programu ksiegowego", # generic (genitive)
    ),
    "business_of_accounting_office": (
        "biuro rachunkowe",       # nominative (+4)
        "cennik",
        # Bare "klient" removed — it gave +3 to any query mentioning a client.
        # "klient biura" adds "klient" as +1 keyword (net positive for true queries).
        "klient biura",           # "klient biura rachunkowego"
        "klienta biura",          # genitive: "obsługa klienta biura"
        "rentownosc", "rentowność",
        "prowadzenie biura",      # "prowadzenie biura rachunkowego"
    ),
    "education_community": ("kurs", "szkolenie", "egzamin", "certyfikat", "polecacie", "jak zaczac"),
    "out_of_scope": ("co myslicie", "jak wrazenia", "czy warto"),
}

ACCOUNTING_ROUTING_MARKERS = (
    "jak zaksi",
    "ujac",
    "na kontach",
    "konto 300",
    "rozliczenie zakupu",
    "pod jaka data",
    "data zapisania",
    "kolumn",
    "pod jaki kst",
)

SOFTWARE_VENDOR_MARKERS = (
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
)

LEGAL_DOMAIN_MARKERS = (
    "vat",
    "jpk",
    "ksef",
    "pit",
    "cit",
    "zus",
    "bfk",
    "di",
    "ro",
    "gtu",
    "oznaczenie",
    "stawka",
    "zwolnienie",
    "obowiazek",
    "termin",
)

SLOT_HINTS: dict[str, tuple[str, ...]] = {
    "obszar_prawa": ("vat", "pit", "cit", "zus", "ksef", "jpk", "urlop", "umowa", "podatek"),
    "stan_faktyczny": (
        "sprzedaz", "zakup", "najem", "pracownik", "spolka", "spółka", "jdg", "usluga", "usługa", "towar",
        # Broader legal-context anchors so that specific legal questions are not over-blocked
        "umow",        # umowy, umowie, umową
        "faktur",      # faktury, fakturę, faktury
        "podatk",      # podatkowi, podatkiem, podatkowego
        "dzialalnosc", # działalność
        "dzielo",      # dzieło, dzieła
    ),
    "okres_lub_data": (
        "202",                    # any year 2020-2029
        # Month nominative forms (as typed) ↓
        "styczen", "styczeń",     # January nom.
        "luty",                   # February nom.
        "marzec",                 # March nom.
        "kwiecien", "kwiecień",   # April nom.
        "maj",                    # May (same in gen.)
        "czerwiec",               # June nom.
        "lipiec",                 # July nom.
        "sierp",                  # August prefix (sierpień / Sierpn-)
        "wrzes",                  # September prefix (wrzesień / Wrzesn-)
        "paz", "pazdz",           # October prefix (październik / Paźdz-)
        "listopad",               # November nom.
        "grudzien", "grudzień",   # December nom.
        # Genitive/oblique prefixes for ordinal dates ("1 Stycznia", "3 Marca" etc.) ↓
        "stycz",    # Stycz-nia  (January gen.)
        "lut",      # Lut-ego / Lut-ym  (February obl.)
        "marc",     # Marc-a / Marc-u  (March gen.)
        "kwiet",    # Kwiet-nia  (April gen.)
        "czerwc",   # Czerwc-a  (June gen.)
        "lipc",     # Lipc-a  (July gen.)
        "grudn",    # Grudn-ia  (December gen. — Grudnia)
        # Generic date/time anchors ↓
        "miesiac", "miesiąc", "rok", "termin", "data",
    ),
    "rodzaj_pisma_lub_wniosku": ("wniosek", "pismo", "korekta", "upl", "pps", "zaw", "czynny zal", "czynny żal", "nadplata", "nadpłata"),
    "organ_lub_kanał_złożenia": ("urzad", "urząd", "us", "skarbow", "e-urzad", "e-urząd", "bramka", "ksef", "jpk"),
    "etap_sprawy_lub_termin": ("po terminie", "przed kontrola", "przed kontrolą", "w trakcie", "po wysylce", "po wysyłce", "termin", "ile czasu"),
    "rodzaj_ksiąg_lub_ewidencji": ("kpir", "ksiegi", "księgi", "ewidencj", "bilans", "rejestr"),
    "rodzaj_dokumentu": ("faktur", "rach", "paragon", "jpk", "pit", "cit", "umow", "lista plac"),
    "okres_księgowy": ("miesiac", "miesiąc", "rok", "okres", "zamkniecie", "zamknięcie", "grudzien", "styczen"),
    "etap_zatrudnienia": (
        "zatrudni",      # nawiązanie zatrudnienia
        "wypowiedzeni",  # wypowiedzenie
        "zwolnieni",     # rozwiązanie/zwolnienie
        "probny",        # okres próbny
        "nawiaz",        # nawiązanie stosunku pracy
        "rozwiaz",       # rozwiązanie stosunku pracy
        "ustanie",       # ustanie zatrudnienia
        "trwanie",       # trwanie stosunku pracy
    ),
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


def _matches_marker(normalized_query: str, query_tokens: set[str], marker: str) -> bool:
    normalized_marker = _normalize(marker)
    if not normalized_marker:
        return False
    if " " in normalized_marker:
        return normalized_marker in normalized_query
    return any(token.startswith(normalized_marker) for token in query_tokens)


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

    if any(_matches_marker(normalized_query, query_tokens, marker) for marker in ACCOUNTING_ROUTING_MARKERS):
        return "accounting_operational"

    best_intent = "unknown"
    best_score = 0
    scored_intents: list[tuple[int, str]] = []
    for intent, record in taxonomy.items():
        keywords = _intent_keywords(intent, record)
        score = sum(1 for token in query_tokens if token in keywords)
        for hint in INTENT_KEYWORD_HINTS.get(intent, ()):
            normalized_hint = _normalize(hint)
            if normalized_hint in normalized_query:
                score += 5 if " " in normalized_hint else 4
        # Slot-less intents (no clarification fields) act as routing
        # "black holes": queries landing there never trigger follow-up
        # questions and always receive raw BM25 chunks.  A small penalty
        # ensures that a slotted intent with an equal or nearly-equal
        # keyword score wins instead, improving behavior accuracy for
        # ambiguous / context-free queries.
        if intent in _SLOTLESS_INTENTS:
            score -= 1
        scored_intents.append((score, intent))
        if score > best_score:
            best_intent = intent
            best_score = score

    if (
        best_intent == "software_tooling"
        and any(_matches_marker(normalized_query, query_tokens, marker) for marker in SOFTWARE_VENDOR_MARKERS)
        and any(_matches_marker(normalized_query, query_tokens, marker) for marker in LEGAL_DOMAIN_MARKERS)
    ):
        for score, intent in sorted(scored_intents, key=lambda item: (-item[0], item[1])):
            if intent != "software_tooling" and score > 0:
                return intent

    if (
        best_intent == "business_of_accounting_office"
        and any(_matches_marker(normalized_query, query_tokens, marker) for marker in SOFTWARE_VENDOR_MARKERS)
    ):
        return "software_tooling"

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
