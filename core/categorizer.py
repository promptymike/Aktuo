from __future__ import annotations

import re
import unicodedata


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return re.sub(r"\s+", " ", without_accents).strip()


def categorize_query(query: str) -> str:
    lowered = _normalize(query)
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
                "rzis",
                "rachunek zyskow",
                "inwentaryzacja",
                "amortyzacja bilansowa",
                "dowod ksiegowy",
                "kpir",
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
                "ryczalt od dochodow spolek",
                "wht",
                "podatek u zrodla",
                "ceny transferowe",
                "tp",
                "tpr",
                "cit-8",
                "ryczalt od dochodow",
                "maly podatnik cit",
                "ift-2r",
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
                "ulga na dzieci",
                "kwota wolna",
                "skala podatkowa",
                "podatek liniowy",
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
        if any(keyword in lowered for keyword in keywords):
            return category
    return "og\u00f3lne"
