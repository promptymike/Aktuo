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
    keyword_map = {
        "ksef": (
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
        "faktury_korygujące": (
            "faktura korygujaca",
            "faktury korygujace",
            "korekta faktury",
            "korygujacej",
            "korygujaca",
            "nota korygujaca",
            "blad na fakturze",
            "bledny nip",
        ),
        "korekty": (
            "korekta vat",
            "korekty vat",
            "korekta podatku",
            "korekta odliczenia",
            "ulga na zle dlugi",
            "zle dlugi",
        ),
        "terminy": (
            "termin",
            "terminy",
            "do kiedy",
            "kiedy zlozyc",
            "termin zlozenia",
            "deklaracja",
            "deklaracje",
            "jpk",
            "jpk_v7",
            "ewidencja",
            "okres rozliczeniowy",
            "miesiecznie",
            "kwartalnie",
        ),
        "podatek_naliczony": (
            "podatek naliczony",
            "vat naliczony",
            "odliczenie vat",
            "odliczyc vat",
            "odliczenia",
            "zakup",
            "nabycie",
        ),
        "podatek_należny": (
            "podatek nalezny",
            "vat nalezny",
            "obowiazek podatkowy",
            "sprzedaz",
            "dostawa towarow",
            "import uslug",
            "stawka vat",
        ),
        "fakturowanie": (
            "faktura",
            "faktury",
            "wystawic fakture",
            "wystawienie faktury",
            "duplikat faktury",
            "paragon",
            "numer faktury",
        ),
        "vat": (
            "vat",
            "zwolnienie z vat",
            "rejestracja vat",
            "vat ue",
            "zwrot vat",
            "podatek od towarow i uslug",
        ),
    }
    for category, keywords in keyword_map.items():
        if any(keyword in lowered for keyword in keywords):
            return category
    return "ogólne"
