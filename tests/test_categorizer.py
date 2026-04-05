from __future__ import annotations

from core.categorizer import categorize_query


def test_categorize_query_returns_polish_ksef_category() -> None:
    assert categorize_query("Od kiedy KSeF będzie obowiązkowy?") == "ksef"


def test_categorize_query_returns_polish_deadlines_category() -> None:
    assert categorize_query("Jaki jest termin złożenia deklaracji JPK_V7?") == "terminy"


def test_categorize_query_falls_back_to_ogolne() -> None:
    assert categorize_query("Potrzebuję ogólnej informacji podatkowej.") == "ogólne"
