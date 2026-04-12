from __future__ import annotations

from core.categorizer import categorize_query


def test_categorize_query_returns_polish_ksef_category() -> None:
    assert categorize_query("Od kiedy KSeF będzie obowiązkowy?") == "ksef"


def test_categorize_query_returns_jpk_category_before_generic_deadlines() -> None:
    assert categorize_query("Jaki jest termin złożenia deklaracji JPK_V7?") == "jpk"


def test_categorize_query_returns_rachunkowosc_category() -> None:
    assert categorize_query("Kiedy składa się sprawozdanie finansowe do KRS?") == "rachunkowosc"


def test_categorize_query_recognizes_sf_shortcut() -> None:
    assert categorize_query("Kiedy złożyć SF do KRS?") == "rachunkowosc"


def test_categorize_query_returns_cit_category() -> None:
    assert categorize_query("Jaka jest stawka CIT dla spółki z o.o.?") == "cit"


def test_categorize_query_returns_extended_cit_keyword_category() -> None:
    assert categorize_query("Kiedy składa się CIT-8 i czy dotyczy mnie WHT?") == "cit"


def test_categorize_query_recognizes_estonczyk_and_cit8() -> None:
    assert categorize_query("Czy estończyk i CIT8 są dla mojej spółki?") == "cit"


def test_categorize_query_recognizes_ift2r_as_cit() -> None:
    assert (
        categorize_query(
            "Dzień dobry, czy składacie deklarację IFT2R do miesięcznej subskrypcji Google?"
        )
        == "cit"
    )


def test_categorize_query_recognizes_ift_2r_and_jpk_cit_as_cit() -> None:
    assert categorize_query("Czy deklaracja IFT-2R może być podpisana przez jedną osobę?") == "cit"
    assert categorize_query("Jak opisać faktury zakupowe w świetle JPK CIT?") == "cit"


def test_categorize_query_returns_pit_category() -> None:
    assert categorize_query("Jak obliczyć zaliczkę na podatek i kiedy złożyć PIT-37?") == "pit"


def test_categorize_query_recognizes_ulga_dla_seniora_as_pit() -> None:
    assert categorize_query("Ulga dla seniora - czy przysługuje za cały rok?") == "pit"


def test_categorize_query_recognizes_pit37_kup_and_tax_cost_phrases_as_pit() -> None:
    assert categorize_query("Czy PIT 37 trzeba skorygować za 2025 rok?") == "pit"
    assert categorize_query("Czy wartość netto i 50% VAT jest przychodem podatkowym?") == "pit"
    assert categorize_query("Koszty w KPiR memoriałowo zaliczać do 2025 czy bieżąco styczeń 2026?") == "pit"


def test_categorize_query_recognizes_cash_register_as_vat() -> None:
    assert categorize_query("Sprzedaż bezpośrednia rolnik - zwolnienie z kasy fiskalnej") == "vat"


def test_categorize_query_recognizes_vat26_oss_and_vehicle_vat_questions_as_vat() -> None:
    assert categorize_query("Samochód osobowy zgłoszony do VAT-26 - czy leasing odliczam proporcją?") == "vat"
    assert categorize_query("Czy od samochodu ciężarowego do 3,5 t można odliczać 100% VAT?") == "vat"
    assert categorize_query("OSS sprzedaż towaru do Niemiec - jaka stawka VAT?") == "vat"


def test_categorize_query_mixed_pit_and_vat_falls_back_to_ogolne() -> None:
    assert categorize_query("Obowiązek podatkowy PIT i VAT - data wykonania vs data faktury") == "ogólne"


def test_categorize_query_returns_zus_category() -> None:
    assert categorize_query("Jaki jest zbieg tytułów ZUS przy zleceniu i działalności?") == "zus"


def test_categorize_query_recognizes_dra_and_pue_shortcuts() -> None:
    assert categorize_query("Czy DRA trzeba wysłać przez PUE ZUS?") == "zus"


def test_categorize_query_returns_kadry_category() -> None:
    assert categorize_query("Jakie są okresy wypowiedzenia umowy o pracę i kiedy dać świadectwo pracy?") == "kadry"


def test_categorize_query_does_not_match_shortcuts_inside_unrelated_words() -> None:
    assert categorize_query("Jakie są okresy wypowiedzenia umowy o pracę?") == "kadry"


def test_categorize_query_returns_ordynacja_category_without_diacritics() -> None:
    assert categorize_query("Jakie sa odsetki za zwloke i kiedy jest przedawnienie?") == "ordynacja"


def test_categorize_query_falls_back_to_ogolne() -> None:
    assert categorize_query("Potrzebuję ogólnej informacji podatkowej.") == "ogólne"
