from __future__ import annotations

import re
import unicodedata


_POLISH_TRANS = str.maketrans(
    {"ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o", "ś": "s", "ż": "z", "ź": "z"}
)


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower().translate(_POLISH_TRANS))
    without_accents = "".join(character for character in normalized if not unicodedata.combining(character))
    return re.sub(r"\s+", " ", without_accents).strip()


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", text))


def _matches_keyword(query: str, query_tokens: set[str], keyword: str) -> bool:
    normalized_keyword = _normalize(keyword)
    keyword_tokens = re.findall(r"[a-z0-9_]+", normalized_keyword)
    if not keyword_tokens:
        return False

    if len(keyword_tokens) == 1:
        return keyword_tokens[0] in query_tokens

    padded_query = f" {query} "
    padded_keyword = f" {' '.join(keyword_tokens)} "
    return padded_keyword in padded_query


def categorize_query(query: str) -> str:
    """Categorize a user query into the legacy retriever category set."""

    lowered = _normalize(query)
    lowered_tokens = _tokenize(lowered)

    cit_priority_markers = (
        "ift-2r",
        "ift2r",
        "ift 2r",
        "jpk cit",
        "wht",
        "certyfikat rezydencji",
    )
    vat_priority_markers = (
        "vat-26",
        "vat26",
        "100% vat",
        "100 vat",
        "odliczenie vat",
        "odliczac vat",
        "odliczac 100% vat",
        "samochod ciezarowy",
        "samochod osobowy",
        "leasing samochodu",
        "leasing auta",
        "leasing operacyjny",
        "proporcj",
        "kasa fiskalna",
        "kasy fiskalne",
        "oss",
        "clo",
        "cło",
    )
    pit_priority_markers = (
        "pit-37",
        "pit 37",
        "pit37",
        "pit-36",
        "pit 36",
        "pit36",
        "pit-11a",
        "pit 11a",
        "pit11a",
        "pit-40a",
        "pit 40a",
        "pit40a",
        "kup",
        "koszt podatkowy",
        "koszty podatkowe",
        "przychod podatkowy",
        "przychody podatkowe",
        "wykup samochodu",
        "wartosc netto",
        "memorialowo",
    )

    if "pit" in lowered_tokens and "vat" in lowered_tokens:
        # When strong VAT-specific markers are present, classify as vat
        # even if PIT is also mentioned (e.g. "leasing samochodu VAT/PIT")
        if any(marker in lowered for marker in vat_priority_markers):
            return "vat"
        return "ogólne"
    if any(marker in lowered for marker in cit_priority_markers):
        return "cit"
    if "vat" in lowered and any(marker in lowered for marker in vat_priority_markers):
        return "vat"
    if any(marker in lowered for marker in ("oss", "vat-26", "vat26")):
        return "vat"
    if any(marker in lowered for marker in pit_priority_markers):
        return "pit"

    ksef_permission_markers = (
        "uprawn",
        "administrator",
        "token",
        "podglad w pdf",
        "dostep do faktur",
        "pobrania takich faktur",
        "dalszego ich przekazywania",
        "nada mi uprawnienia",
        "nadania uprawnien",
    )
    if ("ksef" in lowered or "ksefie" in lowered) and any(marker in lowered for marker in ksef_permission_markers):
        return "ksef"
    if "uprawn" in lowered and any(
        marker in lowered
        for marker in ("dalszego ich przekazywania", "pobrania takich faktur", "podglad w pdf", "administrator")
    ):
        return "ksef"
    if "jpk" in lowered and any(marker in lowered for marker in ("czynny", "zal", "żal", "korekt", "fv", "fakt")):
        return "jpk"
    if any(
        marker in lowered
        for marker in (
            "pe?nomoc",
            "pelnomoc",
            "pełnomoc",
            "profil zaufany",
            "podpis kwalifikowany",
            "zaw fa",
            "zaw-fa",
            "upl-1",
            "upl1",
            "pps-1",
            "pps1",
        )
    ):
        return "ordynacja"

    operational_accounting_markers = (
        "zaksieg",
        "przeksieg",
        "kpir",
        "koszt posredni",
        "koszty bilansowe",
        "bilansowych i kup",
        "zakup towarow",
        "koszty uboczne zakupu",
        "pozostale wydatki",
    )
    if any(marker in lowered for marker in operational_accounting_markers):
        return "rachunkowosc"
    if "pz" in lowered_tokens and ("faktura" in lowered_tokens or "ksiegowanie" in lowered):
        return "rachunkowosc"
    if "fv" in lowered_tokens and ("zakup" in lowered_tokens or "zaksi" in lowered):
        return "rachunkowosc"
    if "amortyz" in lowered and ("samoch" in lowered or "leasing" in lowered):
        return "rachunkowosc"

    cash_register_keywords = (
        "kasa fiskalna",
        "kasy fiskalne",
        "kasa rejestrujaca",
        "kasy rejestrujace",
        "zwolnienie z kasy",
    )
    if any(_matches_keyword(lowered, lowered_tokens, keyword) for keyword in cash_register_keywords):
        return "vat"

    if "leasing" in lowered and any(marker in lowered for marker in ("samoch", "auto")):
        if (("firmow" in lowered and "cel" in lowered) or "dzialaln" in lowered or any(marker in lowered for marker in ("vat26", "vat-26", "ewidencj"))):
            return "vat"
        if any(marker in lowered for marker in ("wykup", "koszt", "przychod", "srodek trwaly", "amortyz")):
            return "pit"

    if "ulg" in lowered and ("senior" in lowered or "emeryt" in lowered):
        return "pit"

    keyword_map = (
        (
            "ksef",
            (
                "ksef",
                "ksefie",
                "krajowy system e-faktur",
                "e-faktur",
                "e-faktura",
                "faktura ustrukturyzowana",
                "faktury ustrukturyzowane",
                "numer ksef",
                "token ksef",
                "uprawnienia ksef",
            ),
        ),
        (
            "rachunkowosc",
            (
                "bilans",
                "sprawozdanie",
                "sf",
                "rzis",
                "rachunek zyskow",
                "inwentaryzacja",
                "amortyzacja bilansowa",
                "dowod ksiegowy",
                "kpir",
                "ksiega przychodow i rozchodow",
                "pelne ksiegi",
                "e-sprawozdanie",
                "e sprawozdanie",
                "krs",
                "ustawa o rachunkowosci",
                "wycena aktywow",
                "rezerwa",
                "rmk",
                "odpis aktualizujacy",
                "zaksięgowac",
                "ksiegowac",
                "zaksięgowanie",
                "ksiegowanie",
                "przeksiegowac",
                "przeksiegowane",
                "koszt posredni",
                "koszty bilansowe",
                "bilansowych i kup",
                "pz",
                "fv",
                "zakup towarow",
                "koszty uboczne zakupu",
                "pozostale wydatki",
            ),
        ),
        (
            "jpk",
            (
                "jpk",
                "jpk_v7",
                "jpk_v7m",
                "jpk_v7k",
                "gtu",
                "bfk",
                "di",
                "fp",
                "wew",
                "ro",
                "mpp",
                "tp",
                "sw",
                "ee",
                "znacznik",
                "plik kontrolny",
                "ewidencja vat",
                "korekta jpk",
            ),
        ),
        (
            "cit",
            (
                "cit",
                "podatek dochodowy od osob prawnych",
                "spolka z o.o.",
                "spolka akcyjna",
                "stawka cit",
                "estonski cit",
                "estonczyk",
                "ryczalt od dochodow spolek",
                "wht",
                "podatek u zrodla",
                "ceny transferowe",
                "tp",
                "tpr",
                "cit-8",
                "cit8",
                "ift2r",
                "ift 2r",
                "ryczalt od dochodow",
                "maly podatnik cit",
                "ift-2r",
                "formularz ift-2r",
                "formularz ift2r",
                "jpk cit",
            ),
        ),
        (
            "pit",
            (
                "pit",
                "podatek dochodowy",
                "zaliczka na podatek",
                "zeznanie roczne",
                "pit-36",
                "pit 36",
                "pit36",
                "pit-37",
                "pit 37",
                "pit37",
                "pit-11",
                "pit11",
                "pit-11a",
                "pit 11a",
                "pit11a",
                "pit-40a",
                "pit 40a",
                "pit40a",
                "pit-4r",
                "pit4r",
                "ulga na dzieci",
                "ulga dla seniora",
                "ulga seniora",
                "ulga dla pracujacego seniora",
                "art. 21 ust. 1 pkt 154",
                "zwolnienie emeryt",
                "senior",
                "wynagrodzenie w euro",
                "waluta obca",
                "kurs nbp",
                "przeliczenie waluty",
                "kwota wolna",
                "skala podatkowa",
                "podatek liniowy",
                "ryczałt",
                "ryczałt ewidencjonowany",
                "najem prywatny",
                "stawka ryczałtu",
                "kup",
                "koszt podatkowy",
                "koszty podatkowe",
                "przychod podatkowy",
                "przychody podatkowe",
                "wykup samochodu",
                "wartosc netto",
                "memorialowo",
            ),
        ),
        (
            "zus",
            (
                "zus",
                "skladka",
                "skladki",
                "ubezpieczenie spoleczne",
                "ubezpieczenie zdrowotne",
                "fp",
                "fgsp",
                "dra",
                "rca",
                "rsa",
                "pue",
                "e platnik",
                "zasilek",
                "chorobowe",
                "macierzynski",
                "preferencyjny zus",
                "maly zus",
                "ulga na start",
                "zbieg tytulow",
                "podstawa wymiaru",
            ),
        ),
        (
            "kadry",
            (
                "kodeks pracy",
                "umowa o prace",
                "wypowiedzenie",
                "wypowiedzenia",
                "okres wypowiedzenia",
                "urlop",
                "nadgodziny",
                "czas pracy",
                "swiadectwo pracy",
                "okres probny",
                "praca zdalna",
                "bhp",
                "badania lekarskie",
                "macierzynski",
                "rodzicielski",
                "ekwiwalent",
                "wynagrodzenie minimalne",
                "zasilek chorobowy",
                "l4",
            ),
        ),
        (
            "ordynacja",
            (
                "ordynacja podatkowa",
                "przedawnienie",
                "kontrola podatkowa",
                "interpretacja indywidualna",
                "nadplata",
                "zaleglosc podatkowa",
                "odsetki za zwloke",
                "pelnomocnictwo",
            ),
        ),
        (
            "faktury_korygujące",
            (
                "faktura korygujaca",
                "faktury korygujace",
                "korekta faktury",
                "korekta",
                "korekty",
                "korygujacej",
                "korygujaca",
                "nota korygujaca",
                "blad na fakturze",
                "bledny nip",
                "nip",
            ),
        ),
        (
            "korekty",
            (
                "korekta vat",
                "korekty vat",
                "korekta podatku",
                "korekta odliczenia",
                "ulga na zle dlugi",
                "zle dlugi",
            ),
        ),
        (
            "fakturowanie",
            (
                "faktura",
                "faktury",
                "wystawic fakture",
                "wystawienie faktury",
                "duplikat faktury",
                "paragon",
                "numer faktury",
            ),
        ),
        (
            "podatek_naliczony",
            (
                "podatek naliczony",
                "vat naliczony",
                "odliczenie vat",
                "odliczyc vat",
                "odliczenia",
                "zakup",
                "nabycie",
            ),
        ),
        (
            "podatek_nalezny",
            (
                "podatek nalezny",
                "vat nalezny",
                "obowiazek podatkowy",
                "sprzedaz",
                "dostawa towarow",
                "import uslug",
                "stawka vat",
            ),
        ),
        (
            "vat",
            (
                "vat",
                "zwolnienie z vat",
                "rejestracja vat",
                "vat ue",
                "zwrot vat",
                "vat-26",
                "vat26",
                "kasa fiskalna",
                "kasy fiskalne",
                "kasa rejestrujaca",
                "kasy rejestrujace",
                "zwolnienie z kasy",
                "paragon",
                "oss",
                "clo",
                "cło",
                "podatek od towarow i uslug",
            ),
        ),
        (
            "terminy",
            (
                "termin",
                "terminy",
                "do kiedy",
                "kiedy zlozyc",
                "termin zlozenia",
                "deklaracja",
                "deklaracje",
                "okres rozliczeniowy",
                "miesiecznie",
                "kwartalnie",
            ),
        ),
    )
    for category, keywords in keyword_map:
        if any(_matches_keyword(lowered, lowered_tokens, keyword) for keyword in keywords):
            return category
    return "ogólne"
