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


def test_classify_intent_operational_bookkeeping_phrase_routes_to_accounting(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_accounting_zus(taxonomy_path)
    _extend_taxonomy_with_pit_cit(taxonomy_path)

    assert classify_intent(
        "A jaką datę przyjąć do zaksięgowania na koncie 300 - rozliczenie zakupu?",
        str(taxonomy_path),
    ) == "accounting_operational"


def test_classify_intent_system_name_with_jpk_tags_stays_vat_not_software(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_full(taxonomy_path)

    assert classify_intent(
        "Czy ktoś księguje w InFakt i może podpowiedzieć gdzie tu widać oznaczenia w JPK BFK itp?",
        str(taxonomy_path),
    ) == "vat_jpk_ksef"


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


def test_operational_accounting_query_bypasses_clarification_gate(tmp_path, monkeypatch) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    slots_path = tmp_path / "clarification_slots.json"
    knowledge_path = tmp_path / "law_knowledge.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_accounting_zus(taxonomy_path)
    _write_slots(slots_path)
    knowledge_path.write_text("[]", encoding="utf-8")

    monkeypatch.setattr("core.retriever._retrieve_ranked_chunks", lambda q, kp, limit=5: [])

    result = retrieve(
        query="A jaką datę przyjąć do zaksięgowania na koncie 300 - rozliczenie zakupu?",
        knowledge_path=knowledge_path,
        taxonomy_path=str(taxonomy_path),
        slots_path=str(slots_path),
    )

    assert result.intent == "accounting_operational"
    assert result.needs_clarification is False


def _write_slots_zus(path) -> None:
    """Write a slots fixture that includes zus and cit_wht required facts."""
    path.write_text(
        json.dumps(
            {
                "vat_jpk_ksef": {
                    "required_facts": ["rodzaj_dokumentu", "okres_lub_data", "rola_lub_status_strony"]
                },
                "pit_ryczalt": {
                    "required_facts": ["forma_opodatkowania", "źródło_przychodu", "okres_lub_data"]
                },
                "zus": {
                    "required_facts": ["tytuł_ubezpieczenia", "status_osoby", "rodzaj_składki_lub_świadczenia"]
                },
                "cit_wht": {
                    "required_facts": ["typ_podmiotu", "rodzaj_transakcji_lub_płatności", "okres_lub_data"]
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_zus_underspecified_query_triggers_clarification(tmp_path, monkeypatch) -> None:
    """ZUS queries with 3 missing slots must trigger clarification (threshold=15)."""
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    slots_path = tmp_path / "clarification_slots.json"
    knowledge_path = tmp_path / "law_knowledge.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_accounting_zus(taxonomy_path)
    _write_slots_zus(slots_path)
    knowledge_path.write_text("[]", encoding="utf-8")

    monkeypatch.setattr("core.retriever._retrieve_ranked_chunks", lambda q, kp, limit=5: [])

    result = retrieve(
        query="Czy działa Wam e płatnik na pue ZUS?",
        knowledge_path=knowledge_path,
        taxonomy_path=str(taxonomy_path),
        slots_path=str(slots_path),
    )
    assert result.needs_clarification is True
    assert result.intent == "zus"


def test_cit_underspecified_query_triggers_clarification(tmp_path, monkeypatch) -> None:
    """CIT queries with missing slots should trigger clarification (threshold=20)."""
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    slots_path = tmp_path / "clarification_slots.json"
    knowledge_path = tmp_path / "law_knowledge.json"
    _write_taxonomy(taxonomy_path)
    _extend_taxonomy_with_pit_cit(taxonomy_path)
    _write_slots_zus(slots_path)
    knowledge_path.write_text("[]", encoding="utf-8")

    monkeypatch.setattr("core.retriever._retrieve_ranked_chunks", lambda q, kp, limit=5: [])

    result = retrieve(
        query="Wynajem auta za granicą. Czy w tej sytuacji należy pobrać podatek u źródła WHT?",
        knowledge_path=knowledge_path,
        taxonomy_path=str(taxonomy_path),
        slots_path=str(slots_path),
    )
    assert result.needs_clarification is True
    assert result.intent == "cit_wht"


def test_vat_odliczenie_query_triggers_clarification(tmp_path, monkeypatch) -> None:
    """Queries with 'odliczałam' must not bypass clarification after removing 'odlicz'."""
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    slots_path = tmp_path / "clarification_slots.json"
    knowledge_path = tmp_path / "law_knowledge.json"
    _write_taxonomy(taxonomy_path)
    _write_slots(slots_path)
    knowledge_path.write_text("[]", encoding="utf-8")

    monkeypatch.setattr("core.retriever._retrieve_ranked_chunks", lambda q, kp, limit=5: [])

    result = retrieve(
        query="W trakcie użytkowania odliczałam 50% VAT. Czy ta darowizna powinna być opodatkowana VAT?",
        knowledge_path=knowledge_path,
        taxonomy_path=str(taxonomy_path),
        slots_path=str(slots_path),
    )
    assert result.needs_clarification is True


# ---------------------------------------------------------------------------
# Tests for intent confusion fixes (fix: reduce top intent confusion pairs)
# ---------------------------------------------------------------------------

def _extend_taxonomy_full(taxonomy_path) -> None:
    """Add all intents needed for confusion-pair tests."""
    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    taxonomy.setdefault("business_of_accounting_office", {
        "description": "Pytania o prowadzenie biura rachunkowego: cenniki, klienci, rentowność.",
        "examples": ["Ile bierzecie za obsługę klienta biura?", "Cennik za KSeF w biurze rachunkowym."],
        "routing_recommendation": "Traktuj jako business/community.",
    })
    taxonomy.setdefault("legal_substantive", {
        "description": "Pytania o skutki materialnoprawne: obowiązki, stawki, limity.",
        "examples": ["Jak to ogarnąć?", "Proszę o pomoc z podatkami."],
        "routing_recommendation": "Kieruj do prawnika.",
    })
    taxonomy.setdefault("legal_procedural", {
        "description": "Pytania o korekty, wnioski, pełnomocnictwa i tryb postępowania.",
        "examples": ["Jak rozliczyć korektę?", "Czy urząd skarbowy sam zwróci nadpłatę?"],
        "routing_recommendation": "Kieruj do Ordynacji podatkowej.",
    })
    taxonomy.setdefault("education_community", {
        "description": "Pytania o kursy, szkolenia, rozwój kariery i rekomendacje.",
        "examples": ["Polecacie kurs online kadry i płace?", "Certyfikat księgowy — jak zdobyć?"],
        "routing_recommendation": "Traktuj jako community-only.",
    })
    taxonomy.setdefault("software_tooling", {
        "description": "Pytania o programy księgowe, importy, integracje i konfiguracje.",
        "examples": ["Jaki program do księgowania polecacie?", "Jak zaimportować dane do Optimy?"],
        "routing_recommendation": "Traktuj jako workflow/product support.",
    })
    taxonomy.setdefault("hr", {
        "description": "Pytania o kadry, umowy o pracę, urlopy i stosunki pracy.",
        "examples": ["Jakie są okresy wypowiedzenia?", "Ile dni urlopu przysługuje?"],
        "routing_recommendation": "Kieruj do kadr.",
    })
    taxonomy.setdefault("pit_ryczalt", {
        "description": "Pytania o PIT, ryczałt, formę opodatkowania i rozliczenia roczne.",
        "examples": ["Czy PIT-37 trzeba skorygować?", "Koszty w KPiR memoriałowo czy bieżąco?"],
        "routing_recommendation": "Kieruj do PIT.",
    })
    taxonomy.setdefault("accounting_operational", {
        "description": "Pytania o księgowanie, środki trwałe, remanent i ewidencje.",
        "examples": ["Jak ująć koszt za poprzedni rok?", "Remanent na koniec roku."],
        "routing_recommendation": "Kieruj do rachunkowości operacyjnej.",
    })
    taxonomy.setdefault("out_of_scope", {
        "description": "Pytania urwane, zbyt ogólne lub niezwiązane z Aktuo.",
        "examples": ["Jakie miasto?"],
        "routing_recommendation": "Zwracaj out-of-scope.",
    })
    taxonomy_path.write_text(json.dumps(taxonomy, ensure_ascii=False), encoding="utf-8")


class TestConfusionFix1_BusinessOfAccountingOffice:
    """Fix 1: bare 'klient' removed from business_of_accounting_office hints."""

    def test_klient_query_not_pulled_to_biuro(self, tmp_path) -> None:
        """Queries mentioning 'klient' in legal/tax context must NOT route to business_of_accounting_office."""
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        # Legal-substantive query about a client's tax situation
        result = classify_intent(
            "Co robicie jeżeli klient jest na ryczalcie, ma kasę fiskalną?",
            str(taxonomy_path),
        )
        assert result != "business_of_accounting_office"

    def test_biuro_rachunkowe_still_routes_to_biuro(self, tmp_path) -> None:
        """Queries about 'biuro rachunkowe' must still route correctly via rachunkow prefix."""
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        result = classify_intent(
            "Jak ustalić cennik w biurze rachunkowym za obsługę KSeF?",
            str(taxonomy_path),
        )
        assert result == "business_of_accounting_office"

    def test_vat_query_with_klient_not_pulled_to_biuro(self, tmp_path) -> None:
        """VAT query mentioning 'klient' must not be captured by business_of_accounting_office."""
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        result = classify_intent(
            "Klient wystawił fakturę końcem grudnia — czy to idzie do JPK za grudzień?",
            str(taxonomy_path),
        )
        assert result != "business_of_accounting_office"
        assert result == "vat_jpk_ksef"


class TestConfusionFix2_StopWordsKtosMoze:
    """Fix 2: 'ktos', 'moze', 'kto' added to STOP_WORDS to reduce taxonomy noise."""

    def test_ktos_podpowie_not_routed_to_education(self, tmp_path) -> None:
        """Generic 'ktoś podpowie' queries must not route to education_community."""
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        result = classify_intent(
            "Czy ktoś rozlicza spółkę komandytową?",
            str(taxonomy_path),
        )
        assert result != "education_community"

    def test_moze_query_not_biased(self, tmp_path) -> None:
        """'Może' as modal verb should not bias scoring."""
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        # Should go to vat or legal, not education_community
        result = classify_intent(
            "Może ktoś podpowie jak wystawić fakturę korygującą?",
            str(taxonomy_path),
        )
        assert result != "education_community"
        # "faktura korygujaca" hint should pull this to vat
        assert result == "vat_jpk_ksef"


class TestConfusionFix3_SoftwareToolingAnchors:
    """Fix 3: added software program names (streamsoft, saldeo, etc.) to software_tooling."""

    def test_streamsoft_routes_to_software(self, tmp_path) -> None:
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        result = classify_intent(
            "Czy ktoś używa programu Streamsoft PRO do importu danych?",
            str(taxonomy_path),
        )
        assert result == "software_tooling"

    def test_saldeo_routes_to_software(self, tmp_path) -> None:
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        result = classify_intent(
            "Czy macie jakieś pulpity klienta, albo klienci wam wrzucają wszystko np. w saldeo?",
            str(taxonomy_path),
        )
        assert result == "software_tooling"

    def test_mala_ksiegowosc_routes_to_software(self, tmp_path) -> None:
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        # Genitive/locative form: "Małej Księgowości" matches inflected hint
        result = classify_intent(
            "Czy ktoś pracuje na Małej Księgowości Rzeczpospolita?",
            str(taxonomy_path),
        )
        assert result == "software_tooling"


class TestConfusionFix4_LegalProceduralAnchors:
    """Fix 4: added 'wezwanie', 'konsekwencje', 'kara', 'sankcja' to legal_procedural."""

    def test_wezwanie_routes_to_legal_procedural(self, tmp_path) -> None:
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        # "wezwania" matches "wezwani" prefix hint
        result = classify_intent(
            "Czy wysłaliście wezwania do zapłaty do kontrahenta?",
            str(taxonomy_path),
        )
        assert result == "legal_procedural"

    def test_konsekwencje_routes_to_legal_procedural(self, tmp_path) -> None:
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        result = classify_intent(
            "Jakie są konsekwencje nieterminowego złożenia deklaracji?",
            str(taxonomy_path),
        )
        assert result == "legal_procedural"

    def test_kara_sankcja_routes_to_legal_procedural(self, tmp_path) -> None:
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        result = classify_intent(
            "Jakie kary grożą za nieterminowe złożenie deklaracji?",
            str(taxonomy_path),
        )
        assert result == "legal_procedural"

    def test_sankcja_routes_to_legal_procedural(self, tmp_path) -> None:
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        result = classify_intent(
            "Czy grożą sankcje karnoskarbowe za niezłożenie korekty?",
            str(taxonomy_path),
        )
        assert result == "legal_procedural"


class TestConfusionFix5_PitRyczaltNarrowed:
    """Fix 5: bare 'pit' removed from pit_ryczalt to avoid matching 'pulpity', 'kapitał'."""

    def test_pulpity_not_routed_to_pit(self, tmp_path) -> None:
        """'pulpity klienta' must not match bare 'pit' and route to pit_ryczalt."""
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        result = classify_intent(
            "Czy macie jakieś pulpity do zarządzania dokumentami w programie?",
            str(taxonomy_path),
        )
        assert result != "pit_ryczalt"

    def test_pit_37_still_routes_to_pit(self, tmp_path) -> None:
        """Explicit PIT-37 reference must still route to pit_ryczalt."""
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        assert classify_intent(
            "Czy PIT 37 trzeba skorygować za 2025 rok?",
            str(taxonomy_path),
        ) == "pit_ryczalt"

    def test_rozliczenie_pit_routes_to_pit(self, tmp_path) -> None:
        """Multi-word 'rozliczenie PIT' hint must route to pit_ryczalt."""
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        assert classify_intent(
            "Jak wygląda rozliczenie PIT dla najmu prywatnego za 2025?",
            str(taxonomy_path),
        ) == "pit_ryczalt"

    def test_kpir_koszt_routes_to_pit_not_vat(self, tmp_path) -> None:
        """KPiR cost-booking queries should route to pit_ryczalt, not vat."""
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        result = classify_intent(
            "Koszty w KPiR memoriałowo zaliczać do 2025 czy bieżąco styczeń 2026?",
            str(taxonomy_path),
        )
        assert result == "pit_ryczalt"


class TestConfusionFix6_SlotlessPenalty:
    """Fix 6: slot-less intents (business, education, out_of_scope) receive a -1 scoring
    penalty so that slotted intents with comparable keyword scores win instead of
    acting as routing 'black holes' for ambiguous queries."""

    def test_tie_broken_in_favour_of_slotted_intent(self, tmp_path) -> None:
        """When a slotted and slot-less intent tie on keyword score, the slotted one wins."""
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        # "formularz A1" gives ZUS +4 via hint, but the query also contains tokens
        # matching business_of_accounting_office taxonomy. The penalty should
        # ensure ZUS wins over business.
        result = classify_intent(
            "Dotyczące formularza A1. Prowadzę jednoosobową działalność gospodarczą.",
            str(taxonomy_path),
        )
        assert result != "business_of_accounting_office"

    def test_strong_slotless_signal_still_wins(self, tmp_path) -> None:
        """A slot-less intent with a strong domain signal must still win despite the penalty."""
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        # "biuro rachunkowe" + "cennik" = strong business_of_accounting_office signal
        result = classify_intent(
            "Jak ustalić cennik w biurze rachunkowym za obsługę KSeF?",
            str(taxonomy_path),
        )
        assert result == "business_of_accounting_office"

    def test_vague_query_prefers_slotted_intent(self, tmp_path) -> None:
        """Context-free questions that match a slot-less intent only by 1 token
        should prefer a slotted intent if available."""
        taxonomy_path = tmp_path / "intent_taxonomy.json"
        _write_taxonomy(taxonomy_path)
        _extend_taxonomy_full(taxonomy_path)

        # "kontrola" (from 'kontroli') could match both legal_procedural and
        # business_of_accounting_office. With penalty, legal_procedural wins.
        result = classify_intent(
            "Jak sobie radzicie z kontrolą wszystkiego?",
            str(taxonomy_path),
        )
        assert result != "business_of_accounting_office"
