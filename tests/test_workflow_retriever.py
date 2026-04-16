from __future__ import annotations

import json
from pathlib import Path

from core.rag import answer_query
from core.retriever import LawChunk, QueryAnalysis
from core.workflow_retriever import (
    WorkflowRetrievalResult,
    is_workflow_eligible,
    load_workflow_documents,
    retrieve_workflow,
)


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _workflow_seed_payload() -> list[dict[str, object]]:
    return [
        {
            "workflow_area": "Sprawozdanie finansowe / podpis / wysyłka",
            "title": "Przygotowanie, podpisanie i wysyłka sprawozdania finansowego",
            "category": "rachunkowosc",
            "question_examples": [
                "Jak wysłać sprawozdanie finansowe?",
                "Jak podpisać sprawozdanie finansowe do KRS?",
            ],
            "steps": [
                "Ustal okres sprawozdawczy.",
                "Przygotuj plik i podpisy.",
                "Wyślij przez właściwą bramkę.",
            ],
            "required_inputs": ["okres_księgowy", "rodzaj_dokumentu"],
            "common_pitfalls": ["Brak podpisu osoby sporządzającej."],
            "related_forms": ["e-Sprawozdanie finansowe"],
            "related_systems": ["KRS", "eKRS"],
            "source_type": "workflow_seed_v1",
        },
        {
            "workflow_area": "KSeF permissions / authorization flow",
            "title": "Nadawanie uprawnień i dostępów w KSeF",
            "category": "ksef",
            "question_examples": [
                "Jak nadać uprawnienia w KSeF?",
                "Jak dodać dostęp do faktur w KSeF?",
            ],
            "steps": ["Zweryfikuj rolę.", "Nadaj uprawnienie.", "Sprawdź status."],
            "required_inputs": ["rola_lub_status_strony"],
            "common_pitfalls": ["Wybranie złej roli dostępu."],
            "related_forms": ["ZAW-FA"],
            "related_systems": ["KSeF", "e-Urząd Skarbowy"],
            "source_type": "workflow_seed_v1",
        },
        {
            "workflow_area": "JPK filing / correction / tags",
            "title": "Obsługa wysyłki, korekty i oznaczeń JPK",
            "category": "jpk",
            "question_examples": [
                "Jak oznaczyć korektę w JPK?",
                "Jak wysłać korektę JPK_V7?",
            ],
            "steps": ["Ustal okres.", "Zweryfikuj oznaczenie.", "Wyślij plik."],
            "required_inputs": ["okres_lub_data"],
            "common_pitfalls": ["Brak weryfikacji oznaczeń przed wysyłką."],
            "related_forms": ["JPK_V7M"],
            "related_systems": ["JPK", "e-Urząd Skarbowy"],
            "source_type": "workflow_seed_v1",
        },
    ]


def _legal_seed_payload() -> list[dict[str, object]]:
    return [
        {
            "law_name": "Ustawa o VAT",
            "article_number": "art. 99",
            "category": "terminy",
            "verified_date": "2026-04-01",
            "question_intent": "Jaki jest termin złożenia JPK_V7?",
            "content": "JPK_V7 składa się do 25. dnia miesiąca po danym okresie rozliczeniowym.",
        },
        {
            "law_name": "Ustawa o CIT",
            "article_number": "art. 28j",
            "category": "cit",
            "verified_date": "2026-04-01",
            "question_intent": "Kto może wybrać estoński CIT?",
            "content": "Estoński CIT mogą wybrać podatnicy spełniający warunki ustawowe.",
        },
    ]


def test_load_workflow_documents_reads_seed_metadata(tmp_path: Path) -> None:
    workflow_path = tmp_path / "workflow_seed.json"
    _write_json(workflow_path, _workflow_seed_payload())

    documents = load_workflow_documents(workflow_path)

    assert len(documents) == 3
    assert documents[0].chunk.source_type == "workflow_seed_v1"
    assert documents[0].chunk.workflow_area
    assert documents[0].chunk.title


def test_retrieve_workflow_returns_expected_unit_for_operational_query(tmp_path: Path) -> None:
    workflow_path = tmp_path / "workflow_seed.json"
    _write_json(workflow_path, _workflow_seed_payload())

    result = retrieve_workflow("Jak wysłać sprawozdanie finansowe?", workflow_path=workflow_path, limit=3)

    assert result.confident is True
    assert result.chunks
    assert result.chunks[0].title == "Przygotowanie, podpisanie i wysyłka sprawozdania finansowego"
    assert result.chunks[0].source_type == "workflow_seed_v1"


def test_retrieve_workflow_returns_expected_unit_for_ksef_permissions_query(tmp_path: Path) -> None:
    workflow_path = tmp_path / "workflow_seed.json"
    _write_json(workflow_path, _workflow_seed_payload())

    result = retrieve_workflow("Jak nadać uprawnienia w KSeF?", workflow_path=workflow_path, limit=3)

    assert result.confident is True
    assert result.chunks[0].title == "Nadawanie uprawnień i dostępów w KSeF"


def test_retrieve_workflow_returns_expected_unit_for_jpk_operational_query(tmp_path: Path) -> None:
    workflow_path = tmp_path / "workflow_seed.json"
    _write_json(workflow_path, _workflow_seed_payload())

    result = retrieve_workflow("Jak oznaczyć korektę w JPK?", workflow_path=workflow_path, limit=3)

    assert result.confident is True
    assert result.chunks[0].title == "Obsługa wysyłki, korekty i oznaczeń JPK"


def test_is_workflow_eligible_distinguishes_operational_and_deadline_jpk_queries() -> None:
    assert is_workflow_eligible("Jak oznaczyć korektę w JPK?", "vat_jpk_ksef") is True
    assert is_workflow_eligible("Jaki jest termin złożenia JPK_V7?", "vat_jpk_ksef") is False


def test_answer_query_falls_back_to_legal_when_workflow_confidence_is_low(tmp_path: Path, monkeypatch) -> None:
    legal_path = tmp_path / "law_knowledge.json"
    _write_json(legal_path, _legal_seed_payload())

    workflow_chunk = LawChunk(
        content="Workflow hint",
        law_name="Workflow layer",
        article_number="Słaby workflow",
        category="workflow",
        verified_date="",
        score=2.0,
        source_type="workflow_seed_v1",
        workflow_area="Fallback",
        title="Słaby workflow",
    )
    legal_chunk = LawChunk(
        content="JPK_V7 składa się do 25. dnia miesiąca po danym okresie rozliczeniowym.",
        law_name="Ustawa o VAT",
        article_number="art. 99",
        category="terminy",
        verified_date="2026-04-01",
        score=0.9,
    )

    monkeypatch.setattr(
        "core.rag.analyze_query_requirements",
        lambda query: QueryAnalysis(intent="software_tooling", missing_slots=[], needs_clarification=False),
    )
    monkeypatch.setattr(
        "core.rag.retrieve_workflow",
        lambda query, workflow_path, limit=5: WorkflowRetrievalResult(
            chunks=[workflow_chunk],
            confident=False,
            top_score=2.0,
        ),
    )
    monkeypatch.setattr("core.rag.retrieve_chunks", lambda query, knowledge_path, limit=5: [legal_chunk])
    monkeypatch.setattr("core.rag.generate_answer", lambda query, chunks, system_prompt, api_key: "Legal fallback answer")
    monkeypatch.setattr("core.rag.is_low_confidence_retrieval", lambda chunks: False)
    monkeypatch.setattr("core.rag.audit_answer", lambda answer, chunks: {"grounded": True})

    result = answer_query(
        query="Jak wysłać deklarację JPK?",
        knowledge_path=legal_path,
        system_prompt="Jesteś Aktuo.",
        api_key="test-key",
    )

    assert result.retrieval_path == "legal_fallback"
    assert result.chunks[0].law_name == "Ustawa o VAT"
    assert result.answer == "Legal fallback answer"


def test_answer_query_keeps_legal_path_for_legal_only_query(tmp_path: Path, monkeypatch) -> None:
    legal_path = tmp_path / "law_knowledge.json"
    _write_json(legal_path, _legal_seed_payload())

    legal_chunk = LawChunk(
        content="Estoński CIT mogą wybrać podatnicy spełniający warunki ustawowe.",
        law_name="Ustawa o CIT",
        article_number="art. 28j",
        category="cit",
        verified_date="2026-04-01",
        score=0.9,
    )

    monkeypatch.setattr(
        "core.rag.analyze_query_requirements",
        lambda query: QueryAnalysis(intent="cit_wht", missing_slots=[], needs_clarification=False),
    )

    def _unexpected_workflow(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("Workflow retriever should not be used for legal-only CIT questions")

    monkeypatch.setattr("core.rag.retrieve_workflow", _unexpected_workflow)
    monkeypatch.setattr("core.rag.retrieve_chunks", lambda query, knowledge_path, limit=5: [legal_chunk])
    monkeypatch.setattr("core.rag.generate_answer", lambda query, chunks, system_prompt, api_key: "Legal answer")
    monkeypatch.setattr("core.rag.is_low_confidence_retrieval", lambda chunks: False)
    monkeypatch.setattr("core.rag.audit_answer", lambda answer, chunks: {"grounded": True})

    result = answer_query(
        query="Estoński CIT — kto może?",
        knowledge_path=legal_path,
        system_prompt="Jesteś Aktuo.",
        api_key="test-key",
    )

    assert result.retrieval_path == "legal"
    assert result.chunks[0].law_name == "Ustawa o CIT"
    assert result.answer == "Legal answer"
