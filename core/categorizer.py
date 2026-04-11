from __future__ import annotations

import re
import unicodedata


_POLISH_TRANS = str.maketrans(
    {"ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o", "ś": "s", "ż": "z", "ź": "z"}
)


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower().translate(_POLISH_TRANS))
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
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
    lowered = _normalize(query)
    lowered_tokens = _tokenize(lowered)
    if "pit" in lowered_tokens and "vat" in lowered_tokens:
        return "ogólne"
    cash_register_keywords = (
        "kasa fiskalna",
        "kasy fiskalne",
        "kasa rejestrująca",
        "kasy rejestrujące",
        "zwolnienie z kasy",
    )
    if any(_matches_keyword(lowered, lowered_tokens, keyword) for keyword in cash_register_keywords):
        return "vat"
    if "ulg" in lowered and ("senior" in lowered or "emeryt" in lowered):
        return "pit"
    keyword_map = (
        (
            "ksef",
            (
                "ksef",
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
                "ryczalt od dochodow",
                "maly podatnik cit",
                "ift-2r",
                "formularz ift-2r",
                "formularz ift2r",
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
                "pit-37",
                "pit-11",
                "pit11",
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
            "faktury_koryguj\u0105ce",
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
            "podatek_nale\u017cny",
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
                "kasa fiskalna",
                "kasy fiskalne",
                "kasa rejestrujaca",
                "kasy rejestrujace",
                "zwolnienie z kasy",
                "paragon",
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
    return "og\u00f3lne"
