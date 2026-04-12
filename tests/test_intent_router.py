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


def test_classify_intent_prefers_vat_pit_and_cit_priority_markers(tmp_path) -> None:
    taxonomy_path = tmp_path / "intent_taxonomy.json"
    _write_taxonomy(taxonomy_path)
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

    assert classify_intent("Samochód zgłoszony do VAT-26 - czy odliczam 100% VAT?", str(taxonomy_path)) == "vat_jpk_ksef"
    assert classify_intent("Czy PIT 37 trzeba skorygować za 2025 rok?", str(taxonomy_path)) == "pit_ryczalt"
    assert classify_intent("Czy deklaracja IFT-2R może być podpisana przez jedną osobę?", str(taxonomy_path)) == "cit_wht"


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
