from __future__ import annotations

from core.categorizer import categorize_query


def test_categorize_query_returns_polish_ksef_category() -> None:
    assert categorize_query("Od kiedy KSeF będzie obowiązkowy?") == "ksef"


def test_categorize_query_returns_jpk_category_before_generic_deadlines() -> None:
    assert categorize_query("Jaki jest termin złożenia deklaracji JPK_V7?") == "jpk"


def test_categorize_query_returns_rachunkowosc_category() -> None:
    assert categorize_query("Kiedy składa się sprawozdanie finansowe do KRS?") == "rachunkowosc"


def test_categorize_query_returns_cit_category() -> None:
    assert categorize_query("Jaka jest stawka CIT dla spółki z o.o.?") == "cit"


def test_categorize_query_returns_pit_category() -> None:
    assert categorize_query("Jak obliczyć zaliczkę na podatek i kiedy złożyć PIT-37?") == "pit"


def test_categorize_query_returns_ordynacja_category_without_diacritics() -> None:
    assert categorize_query("Jakie sa odsetki za zwloke i kiedy jest przedawnienie?") == "ordynacja"


def test_categorize_query_falls_back_to_ogolne() -> None:
    assert categorize_query("Potrzebuję ogólnej informacji podatkowej.") == "ogólne"
