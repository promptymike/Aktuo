from __future__ import annotations

from pathlib import Path

from core.generator import format_workflow_answer
from core.rag import answer_query
from core.retriever import LawChunk, QueryAnalysis


def _write_seed(path: Path) -> None:
    path.write_text("[]", encoding="utf-8")


def _workflow_chunk(**overrides: object) -> LawChunk:
    payload: dict[str, object] = {
        "content": "Workflow layer content",
        "law_name": "Workflow layer",
        "article_number": "Nadawanie uprawnień w KSeF",
        "category": "ksef",
        "verified_date": "",
        "score": 8.5,
        "source_type": "workflow_seed_v1",
        "workflow_area": "KSeF permissions / authorization flow",
        "title": "Nadawanie uprawnień i dostępów w KSeF",
        "workflow_steps": (
            "Zweryfikuj rolę użytkownika.",
            "Nadaj właściwe uprawnienie w KSeF.",
            "Potwierdź, że dostęp jest aktywny.",
        ),
        "workflow_required_inputs": ("NIP podatnika", "rola użytkownika"),
        "workflow_common_pitfalls": ("Wybranie niewłaściwego zakresu uprawnień."),
        "workflow_related_forms": ("ZAW-FA",),
        "workflow_related_systems": ("KSeF", "e-Urząd Skarbowy"),
    }
    payload.update(overrides)
    return LawChunk(**payload)


def _legal_chunk() -> LawChunk:
    return LawChunk(
        content="JPK_V7 składa się do 25. dnia miesiąca po danym okresie rozliczeniowym.",
        law_name="Ustawa o VAT",
        article_number="art. 99",
        category="terminy",
        verified_date="2026-04-01",
        score=0.8,
    )


def test_format_workflow_answer_renders_workflow_sections() -> None:
    answer = format_workflow_answer("Jak nadać uprawnienia w KSeF?", [_workflow_chunk()])

    assert "**Krótko**" in answer
    assert "**Co zrób teraz**" in answer
    assert "**Jakie dane / dokumenty będą potrzebne**" in answer
    assert "**Na co uważać**" in answer
    assert "**Powiązane formularze / systemy**" in answer
    assert "ZAW-FA" in answer


def test_format_workflow_answer_omits_missing_sections_for_sparse_units() -> None:
    sparse_chunk = _workflow_chunk(
        workflow_steps=(),
        workflow_required_inputs=(),
        workflow_common_pitfalls=(),
        workflow_related_forms=(),
        workflow_related_systems=(),
    )

    answer = format_workflow_answer("Jak wysłać sprawozdanie?", [sparse_chunk])

    assert "**Krótko**" in answer
    assert "**Co zrób teraz**" not in answer
    assert "**Jakie dane / dokumenty będą potrzebne**" not in answer
    assert "**Na co uważać**" not in answer
    assert "**Powiązane formularze / systemy**" not in answer


def test_answer_query_uses_workflow_format_when_workflow_path_wins(tmp_path: Path, monkeypatch) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    _write_seed(seed_file)

    def _unexpected_generate(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("Legal generator should not run for workflow-formatted answers")

    monkeypatch.setattr(
        "core.rag.analyze_query_requirements",
        lambda query: QueryAnalysis(intent="software_tooling", missing_slots=[], needs_clarification=False),
    )
    monkeypatch.setattr("core.rag._retrieve_context", lambda **kwargs: ([_workflow_chunk()], "workflow"))
    monkeypatch.setattr("core.rag.generate_answer", _unexpected_generate)
    monkeypatch.setattr("core.rag.is_low_confidence_retrieval", lambda chunks: False)
    monkeypatch.setattr("core.rag.audit_answer", lambda answer, chunks: {"grounded": True})

    result = answer_query(
        query="Jak nadać uprawnienia w KSeF?",
        knowledge_path=seed_file,
        system_prompt="Jesteś Aktuo.",
        api_key="test-key",
    )

    assert result.retrieval_path == "workflow"
    assert "**Co zrób teraz**" in result.answer
    assert "NIP podatnika" in result.answer


def test_answer_query_keeps_legal_answer_for_legal_path(tmp_path: Path, monkeypatch) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    _write_seed(seed_file)

    monkeypatch.setattr(
        "core.rag.analyze_query_requirements",
        lambda query: QueryAnalysis(intent="cit_wht", missing_slots=[], needs_clarification=False),
    )
    monkeypatch.setattr("core.rag._retrieve_context", lambda **kwargs: ([_legal_chunk()], "legal"))
    monkeypatch.setattr(
        "core.rag.generate_answer",
        lambda query, chunks, system_prompt, api_key: "Legal answer with Podstawa prawna",
    )
    monkeypatch.setattr("core.rag.is_low_confidence_retrieval", lambda chunks: False)
    monkeypatch.setattr("core.rag.audit_answer", lambda answer, chunks: {"grounded": True})

    result = answer_query(
        query="Estoński CIT — kto może?",
        knowledge_path=seed_file,
        system_prompt="Jesteś Aktuo.",
        api_key="test-key",
    )

    assert result.retrieval_path == "legal"
    assert result.answer == "Legal answer with Podstawa prawna"
    assert "**Co zrób teraz**" not in result.answer


def test_answer_query_keeps_legal_answer_for_legal_fallback(tmp_path: Path, monkeypatch) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    _write_seed(seed_file)

    monkeypatch.setattr(
        "core.rag.analyze_query_requirements",
        lambda query: QueryAnalysis(intent="vat_jpk_ksef", missing_slots=[], needs_clarification=False),
    )
    monkeypatch.setattr("core.rag._retrieve_context", lambda **kwargs: ([_legal_chunk()], "legal_fallback"))
    monkeypatch.setattr(
        "core.rag.generate_answer",
        lambda query, chunks, system_prompt, api_key: "Legal fallback answer",
    )
    monkeypatch.setattr("core.rag.is_low_confidence_retrieval", lambda chunks: False)
    monkeypatch.setattr("core.rag.audit_answer", lambda answer, chunks: {"grounded": True})

    result = answer_query(
        query="Jaki jest termin złożenia JPK_V7?",
        knowledge_path=seed_file,
        system_prompt="Jesteś Aktuo.",
        api_key="test-key",
    )

    assert result.retrieval_path == "legal_fallback"
    assert result.answer == "Legal fallback answer"
    assert "**Krótko**" not in result.answer
