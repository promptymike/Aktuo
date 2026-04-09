from __future__ import annotations


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
    return text.lower().translate(translation)


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
                "skladki",
                "skladka zdrowotna",
                "skladka spoleczna",
                "maly zus",
                "preferencyjne skladki",
                "dra",
                "rca",
            ),
        ),
        (
            "kadry",
            (
                "kodeks pracy",
                "umowa o prace",
                "urlop",
                "wynagrodzenie minimalne",
                "nadgodziny",
                "wypowiedzenie",
                "swiadectwo pracy",
                "l4",
                "zasilek chorobowy",
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
                "korygujacej",
                "korygujaca",
                "nota korygujaca",
                "blad na fakturze",
                "bledny nip",
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
            "podatek_należny",
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
    return "ogólne"
