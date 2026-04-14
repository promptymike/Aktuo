from __future__ import annotations

import json

from core.intent_router import classify_intent, detect_clarification_slots
from core.retriever import RetrievalResult, retrieve


def _write_taxonomy(path) -> None:
    path.write_text(
        json.dumps(
            {
                "vat_jpk_ksef": {
                    "description": "Pytania o VAT, JPK_V7, KSeF, faktury i rozliczenia VAT.",
                    "examples": ["Kiedy złożyć JPK_V7 za marzec?", "Faktura w KSeF dla nabywcy krajowego."],
                    "routing_recommendation": "Kieruj do VAT/JPK/KSeF.",
                },
                "zus": {
                    "description": "Pytania o ZUS, składki, zbiegi tytułów i świadczenia.",
                    "examples": ["Jakie składki ZUS płaci JDG?", "Zbieg tytułów przy zleceniu i działalności."],
                    "routing_recommendation": "Kieruj do źródeł ZUS.",
                },
                "payroll": {
                    "description": "Pytania o listę płac, PIT-11 i wynagrodzenia.",
                    "examples": ["Kiedy wysłać PIT-11 pracownikowi?", "Jak rozliczyć premię na liście płac?"],
                    "routing_recommendation": "Kieruj do warstwy płacowej.",
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _write_slots(path) -> None:
    path.write_text(
        json.dumps(
            {
                "vat_jpk_ksef": {
                    "required_facts": ["rodzaj_dokumentu", "okres_lub_data", "rola_lub_status_strony"]
                },
                "pit_ryczalt": {
                    "required_facts": ["forma_opodatkowania", "źródło_przychodu", "okres_lub_data"]
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_classify_intent_matches_vat_zus_and_unknown(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)

    assert classify_intent("Kiedy złożyć JPK_V7 za marzec 2026?", str(taxonomy_path)) == "vat_jpk_ksef"
    assert classify_intent("Jakie składki ZUS płaci JDG?", str(taxonomy_path)) == "zus"
    assert classify_intent("Jak wysłać PIT-11 pracownikowi?", str(taxonomy_path)) == "payroll"
    assert classify_intent("Polecacie dobrą kawę do biura?", str(taxonomy_path)) == "unknown"


def _extend_taxonomy_with_pit_cit(taxonomy_path) -> None:
    """Add pit_ryczalt and cit_wht intents to the taxonomy fixture."""
    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    taxonomy["pit_ryczalt"] = {
        "description": "Pytania o PIT, ryczałt i formularze roczne.",
        "examples": ["Czy PIT-37 trzeba skorygować?", "Koszty w KPiR memoriałowo czy bieżąco?"],
        "routing_recommendation": "Kieruj do PIT.",
    }
    taxonomy["cit_wht"] = {
        "description": "Pytania o CIT, WHT i formularz IFT-2R.",
        "examples": ["Czy IFT-2R trzeba złożyć?", "Jak działa JPK CIT?"],
        "routing_recommendation": "Kieruj do CIT/WHT.",
    }
    taxonomy_path.write_text(json.dumps(taxonomy, ensure_ascii=False), encoding="utf-8")


def test_classify_intent_prefers_vat_pit_and_cit_priority_markers(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_pit_cit(taxonomy_path)

    assert classify_intent("Samochód zgłoszony do VAT-26 - czy odliczam 100% VAT?", str(taxonomy_path)) == "vat_jpk_ksef"
    assert classify_intent("Czy PIT 37 trzeba skorygować za 2025 rok?", str(taxonomy_path)) == "pit_ryczalt"
    assert classify_intent("Czy deklaracja IFT-2R może być podpisana przez jedną osobę?", str(taxonomy_path)) == "cit_wht"


def test_classify_intent_pit40a_and_pit11a_route_to_payroll(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_pit_cit(taxonomy_path)

    assert classify_intent(
        "Osoba która otrzymuje PIT40A z KRUS i PIT11A z ZUS - jak rozliczyć?",
        str(taxonomy_path),
    ) == "payroll"


def test_classify_intent_pit_11_with_space_routes_to_payroll(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_pit_cit(taxonomy_path)

    assert classify_intent(
        "Jak jest u Was technicznie z PIT 11?",
        str(taxonomy_path),
    ) == "payroll"


def test_classify_intent_leasing_samochodu_vat_routes_to_vat(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_pit_cit(taxonomy_path)

    assert classify_intent(
        "Mam fakturę za leasing samochodu - jak rozliczyć VAT?",
        str(taxonomy_path),
    ) == "vat_jpk_ksef"


def test_classify_intent_kasa_fiskalna_routes_to_vat(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_pit_cit(taxonomy_path)

    assert classify_intent(
        "Czy kasa fiskalna musi być cały czas podłączona?",
        str(taxonomy_path),
    ) == "vat_jpk_ksef"


def test_classify_intent_estonczyk_routes_to_cit(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_pit_cit(taxonomy_path)

    assert classify_intent(
        "Estoński CIT czy zakupiony obiad dla pracowników to ukryte zyski?",
        str(taxonomy_path),
    ) == "cit_wht"


def _extend_taxonomy_with_hr_legal(taxonomy_path) -> None:
    """Add hr, legal_substantive, cit_wht intents to the taxonomy fixture."""
    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    taxonomy["hr"] = {
        "description": "Pytania o kadry, umowy o pracę, urlopy i stosunki pracy.",
        "examples": ["Jakie są okresy wypowiedzenia?", "Co się zmieniło w Kodeksie pracy?"],
        "routing_recommendation": "Kieruj do kadr.",
    }
    taxonomy["legal_substantive"] = {
        "description": "Pytania o ogólne zagadnienia prawne i podatkowe.",
        "examples": ["Jak to ogarnąć?", "Proszę o pomoc z podatkami."],
        "routing_recommendation": "Kieruj do prawnika.",
    }
    taxonomy["cit_wht"] = {
        "description": "Pytania o CIT, WHT i formularz IFT-2R.",
        "examples": ["Czy IFT-2R trzeba złożyć?", "Jak działa JPK CIT?"],
        "routing_recommendation": "Kieruj do CIT/WHT.",
    }
    taxonomy_path.write_text(json.dumps(taxonomy, ensure_ascii=False), encoding="utf-8")


def test_classify_intent_generic_help_routes_to_legal_substantive(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_hr_legal(taxonomy_path)

    assert classify_intent("Jak to ogarnąć?", str(taxonomy_path)) == "legal_substantive"
    assert classify_intent("A w czym problem?", str(taxonomy_path)) == "legal_substantive"
    assert classify_intent("Bardzo proszę o pomoc z tym tematem.", str(taxonomy_path)) == "legal_substantive"


def test_classify_intent_zmienilo_and_dziecko_route_to_hr(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_hr_legal(taxonomy_path)

    assert classify_intent("Co się zmieniło w Kodeksie pracy?", str(taxonomy_path)) == "hr"
    assert classify_intent("Odnośnie ulgi na dziecko?", str(taxonomy_path)) == "hr"


def test_classify_intent_dywidenda_routes_to_cit(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_pit_cit(taxonomy_path)

    assert classify_intent(
        "Czy dywidendę zwolnioną z podatku w oparciu o art. 22 ustawy CIT?",
        str(taxonomy_path),
    ) == "cit_wht"


def test_detect_clarification_slots_for_vat_and_pit(tmp_path) -> None:
    slots_path = tmp_path / "clarification_slots.json"
    _write_slots(slots_path)

    vat_missing = detect_clarification_slots("Jak rozliczyć VAT?", str(slots_path), "vat_jpk_ksef")
    assert vat_missing == {
        "rodzaj_dokumentu": True,
        "okres_lub_data": True,
        "rola_lub_status_strony": True,
    }

    vat_complete = detect_clarification_slots(
        "Czy sprzedawca ma wykazać fakturę za marzec 2026 w JPK?",
        str(slots_path),
        "vat_jpk_ksef",
    )
    assert all(flag is False for flag in vat_complete.values())

    pit_missing = detect_clarification_slots("Jak rozliczyć PIT z najmu?", str(slots_path), "pit_ryczalt")
    assert pit_missing["forma_opodatkowania"] is True
    assert pit_missing["źródło_przychodu"] is False


def test_retrieve_returns_clarification_without_running_ranking(tmp_path, monkeypatch) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    slots_path = tmp_path / "clarification_slots.json"
    knowledge_path = tmp_path / "law_knowledge.json"
    _write_taxonomy(taxonomy_path)
    _write_slots(slots_path)
    knowledge_path.write_text("[]", encoding="utf-8")

    def fail_if_called(query, knowledge_path, limit=5):  # noqa: ARG001
        raise AssertionError("ranking retrieval should not run when clarification is required")

    monkeypatch.setattr("core.retriever._retrieve_ranked_chunks", fail_if_called)

    result = retrieve(
        query="Jak rozliczyć VAT?",
        knowledge_path=knowledge_path,
        taxonomy_path=str(taxonomy_path),
        slots_path=str(slots_path),
    )

    assert isinstance(result, RetrievalResult)
    assert result.needs_clarification is True
    assert result.chunks == []
    assert set(result.missing_slots or []) == {"rodzaj_dokumentu", "okres_lub_data", "rola_lub_status_strony"}


# ---------------------------------------------------------------------------
# Tests for new routing hints added in feat: refine clarification and intent
# ---------------------------------------------------------------------------

def _extend_taxonomy_with_accounting_zus(taxonomy_path) -> None:
    """Add accounting_operational and zus intents to the taxonomy fixture."""
    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    taxonomy["accounting_operational"] = {
        "description": "Pytania o księgowanie, środki trwałe, remanent i ewidencje.",
        "examples": ["Jak ująć koszt za poprzedni rok?", "Remanent na koniec roku."],
        "routing_recommendation": "Kieruj do rachunkowości operacyjnej.",
    }
    taxonomy["zus"] = {
        "description": "Pytania o ZUS, PUE, e-Płatnik i składki.",
        "examples": ["Czy działa PUE ZUS?", "Mały ZUS Plus limity."],
        "routing_recommendation": "Kieruj do ZUS.",
    }
    taxonomy_path.write_text(json.dumps(taxonomy, ensure_ascii=False), encoding="utf-8")


def test_classify_intent_remanent_and_srodek_trwaly_route_to_accounting(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_accounting_zus(taxonomy_path)

    assert classify_intent(
        "Jak ująć koszt środka trwałego zakupionego w poprzednim roku?",
        str(taxonomy_path),
    ) == "accounting_operational"
    assert classify_intent(
        "Remanent na koniec roku — co wpisać do KPiR?",
        str(taxonomy_path),
    ) == "accounting_operational"
    assert classify_intent(
        "Wynik finansowy za 2025 — jak zamknąć rok?",
        str(taxonomy_path),
    ) == "accounting_operational"


def test_classify_intent_pue_and_maly_zus_route_to_zus(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_accounting_zus(taxonomy_path)

    assert classify_intent("Czy działa Wam PUE ZUS?", str(taxonomy_path)) == "zus"
    assert classify_intent(
        "Mały ZUS Plus — jaki jest limit przychodu?",
        str(taxonomy_path),
    ) == "zus"
    assert classify_intent(
        "Jak złożyć ZWUA przez e-Płatnik?",
        str(taxonomy_path),
    ) == "zus"


def test_classify_intent_darowizna_routes_to_vat(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)

    assert classify_intent(
        "Czy darowizna samochodu powinna być opodatkowana VAT?",
        str(taxonomy_path),
    ) == "vat_jpk_ksef"


def test_period_slot_detected_with_genitive_month_date(tmp_path) -> None:
    """Genitive date forms like '1 Stycznia' must satisfy the okres_lub_data slot."""
    slots_path = tmp_path / "clarification_slots.json"
    _write_slots(slots_path)

    # Nominative month — already tested; just re-confirm baseline
    missing_nom = detect_clarification_slots(
        "Czy sprzedawca ma wykazać fakturę za marzec 2026 w JPK?",
        str(slots_path),
        "vat_jpk_ksef",
    )
    assert missing_nom["okres_lub_data"] is False

    # Genitive form: "1 stycznia" — should also be detected via "stycz" prefix
    missing_gen = detect_clarification_slots(
        "Czy fakturę wystawioną 1 stycznia 2026 trzeba ująć w JPK sprzedawcy?",
        str(slots_path),
        "vat_jpk_ksef",
    )
    assert missing_gen["okres_lub_data"] is False


def test_vat_ksef_correction_query_still_requires_clarification(tmp_path, monkeypatch) -> None:
    """KSeF correction queries must NOT bypass clarification via the old 'korekt' token."""
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    slots_path = tmp_path / "clarification_slots.json"
    knowledge_path = tmp_path / "law_knowledge.json"
    _write_taxonomy(taxonomy_path)
    _write_slots(slots_path)
    knowledge_path.write_text("[]", encoding="utf-8")

    call_count = {"n": 0}

    def count_calls(query, kp, limit=5):  # noqa: ARG001
        call_count["n"] += 1
        return []

    monkeypatch.setattr("core.retriever._retrieve_ranked_chunks", count_calls)

    result = retrieve(
        query="KSeF — korekta: czy da się wysłać korektę zmieniającą tylko dane odbiorcy?",
        knowledge_path=knowledge_path,
        taxonomy_path=str(taxonomy_path),
        slots_path=str(slots_path),
    )

    # Clarification must fire; ranking must NOT have been called
    assert result.needs_clarification is True
    assert call_count["n"] == 0
