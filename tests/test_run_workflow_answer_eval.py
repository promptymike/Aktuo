from __future__ import annotations

import json
from pathlib import Path

from analysis.run_workflow_answer_eval import evaluate_case, run_workflow_answer_eval
from core.rag import RagResult
from core.retriever import LawChunk


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def _workflow_rows() -> list[dict[str, object]]:
    return [
        {
            "classification": "workflow",
            "question": "Jak wysłać sprawozdanie finansowe?",
            "primary_intent": "accounting_operational",
            "source_category": "rachunkowosc",
            "source_frequency": 12,
            "expected_behavior": "answer_directly",
            "expected_law_or_area": "workflow",
            "expected_source_type": "workflow_kb",
            "needs_clarification": False,
        },
        {
            "classification": "legal",
            "question": "Jaki jest termin złożenia JPK_V7?",
            "primary_intent": "vat_jpk_ksef",
            "source_category": "jpk",
            "source_frequency": 11,
            "expected_behavior": "answer_directly",
            "expected_law_or_area": "VAT / JPK / KSeF",
            "expected_source_type": "legal_kb",
            "needs_clarification": False,
        },
        {
            "classification": "mixed",
            "question": "Jak skorygować JPK po błędzie w fakturze?",
            "primary_intent": "legal_procedural",
            "source_category": "jpk",
            "source_frequency": 10,
            "expected_behavior": "answer_directly",
            "expected_law_or_area": "VAT / JPK / KSeF",
            "expected_source_type": "mixed",
            "needs_clarification": False,
        },
    ]


def _rag_result_for_query(query: str) -> RagResult:
    if "sprawozdanie" in query.lower():
        return RagResult(
            answer=(
                "**Krótko**\nPrzygotowanie, podpisanie i wysyłka sprawozdania finansowego.\n\n"
                "**Co zrób teraz**\n1. Przygotuj plik.\n2. Wyślij przez właściwą bramkę.\n\n"
                "**Jakie dane / dokumenty będą potrzebne**\n- okres_księgowy\n\n"
                "**Na co uważać**\n- Brak podpisu.\n\n"
                "**Powiązane formularze / systemy**\n- e-Sprawozdanie finansowe\n- KRS"
            ),
            chunks=[
                LawChunk(
                    content="Workflow content",
                    law_name="Workflow layer",
                    article_number="Przygotowanie, podpisanie i wysyłka sprawozdania finansowego",
                    category="rachunkowosc",
                    verified_date="",
                    score=9.0,
                    source_type="workflow_seed_v1",
                    workflow_area="Sprawozdanie finansowe / podpis / wysyłka",
                    title="Przygotowanie, podpisanie i wysyłka sprawozdania finansowego",
                    workflow_steps=("Przygotuj plik.", "Wyślij przez właściwą bramkę."),
                    workflow_required_inputs=("okres_księgowy",),
                    workflow_common_pitfalls=("Brak podpisu.",),
                    workflow_related_forms=("e-Sprawozdanie finansowe",),
                    workflow_related_systems=("KRS",),
                )
            ],
            audit={"grounded": True},
            redacted_query=query,
            category="rachunkowosc",
            retrieval_path="workflow",
        )

    if "termin" in query.lower():
        return RagResult(
            answer="Odpowiedź prawna oparta na dostępnym kontekście.\n\nPodstawa prawna:\n- Ustawa o VAT, art. 99",
            chunks=[
                LawChunk(
                    content="JPK_V7 składa się do 25. dnia miesiąca po danym okresie rozliczeniowym.",
                    law_name="Ustawa o VAT",
                    article_number="art. 99",
                    category="terminy",
                    verified_date="2026-04-01",
                    score=0.8,
                )
            ],
            audit={"grounded": True},
            redacted_query=query,
            category="vat_jpk_ksef",
            retrieval_path="legal",
        )

    return RagResult(
        answer="Odpowiedź prawna oparta na dostępnym kontekście.\n\nPodstawa prawna:\n- Ustawa o VAT, art. 99",
        chunks=[
            LawChunk(
                content="Korekta JPK wymaga analizy przepisu materialnego.",
                law_name="Ustawa o VAT",
                article_number="art. 99",
                category="jpk",
                verified_date="2026-04-01",
                score=0.7,
            )
        ],
        audit={"grounded": True},
        redacted_query=query,
        category="legal_procedural",
        retrieval_path="legal_fallback",
    )


def test_run_workflow_answer_eval_generates_expected_report_schema(tmp_path: Path, monkeypatch) -> None:
    workflow_split = tmp_path / "workflow.jsonl"
    golden = tmp_path / "golden.jsonl"
    report_json = tmp_path / "workflow_answer_eval_report.json"
    report_md = tmp_path / "workflow_answer_eval_report.md"
    rows = _workflow_rows()
    _write_jsonl(workflow_split, rows)
    _write_jsonl(golden, rows)

    monkeypatch.setattr(
        "analysis.run_workflow_answer_eval.answer_query",
        lambda query, knowledge_path, system_prompt, api_key: _rag_result_for_query(query),
    )

    report = run_workflow_answer_eval(
        workflow_split_path=workflow_split,
        golden_eval_path=golden,
        report_json_path=report_json,
        report_md_path=report_md,
        limit_per_subset=10,
    )

    assert report_json.exists()
    assert report_md.exists()
    assert report["records_evaluated"] == 3
    assert set(report["subset_counts"]) == {
        "workflow_answer_expected",
        "legal_answer_expected",
        "legal_fallback_expected",
    }
    assert "metrics" in report
    assert "error_analysis" in report


def test_evaluate_case_detects_workflow_formatting(monkeypatch) -> None:
    case = _workflow_rows()[0]
    monkeypatch.setattr(
        "analysis.run_workflow_answer_eval.answer_query",
        lambda query, knowledge_path, system_prompt, api_key: _rag_result_for_query(query),
    )

    from analysis.run_workflow_answer_eval import WorkflowAnswerEvalCase

    result = evaluate_case(
        WorkflowAnswerEvalCase(
            question=case["question"],
            normalized_question=case["question"].lower(),
            subset="workflow_answer_expected",
            classification=str(case["classification"]),
            primary_intent=str(case["primary_intent"]),
            expected_behavior=str(case["expected_behavior"]),
            expected_law_or_area=str(case["expected_law_or_area"]),
            expected_source_type=str(case["expected_source_type"]),
            source_category=str(case["source_category"]),
            source_frequency=int(case["source_frequency"]),
            needs_clarification=bool(case["needs_clarification"]),
            golden_overlap=True,
        )
    )

    assert result["retrieval_path"] == "workflow"
    assert result["workflow_formatted"] is True
    assert "Co zrób teraz" in result["answer_sections"]


def test_evaluate_case_keeps_legal_answer_unformatted(monkeypatch) -> None:
    case = _workflow_rows()[1]
    monkeypatch.setattr(
        "analysis.run_workflow_answer_eval.answer_query",
        lambda query, knowledge_path, system_prompt, api_key: _rag_result_for_query(query),
    )

    from analysis.run_workflow_answer_eval import WorkflowAnswerEvalCase

    result = evaluate_case(
        WorkflowAnswerEvalCase(
            question=case["question"],
            normalized_question=case["question"].lower(),
            subset="legal_answer_expected",
            classification=str(case["classification"]),
            primary_intent=str(case["primary_intent"]),
            expected_behavior=str(case["expected_behavior"]),
            expected_law_or_area=str(case["expected_law_or_area"]),
            expected_source_type=str(case["expected_source_type"]),
            source_category=str(case["source_category"]),
            source_frequency=int(case["source_frequency"]),
            needs_clarification=bool(case["needs_clarification"]),
            golden_overlap=True,
        )
    )

    assert result["retrieval_path"] == "legal"
    assert result["workflow_formatted"] is False
    assert result["legal_style_answer"] is True


def test_sparse_workflow_unit_does_not_create_invented_sections(monkeypatch) -> None:
    sparse_result = RagResult(
        answer="**Krótko**\nUjęcie dokumentów w odpowiednim okresie i ewidencji.",
        chunks=[
            LawChunk(
                content="Workflow content",
                law_name="Workflow layer",
                article_number="Ujęcie dokumentów w odpowiednim okresie i ewidencji",
                category="rachunkowosc",
                verified_date="",
                score=8.0,
                source_type="workflow_seed_v1",
                workflow_area="KPiR / księgowanie / okresy i memoriał",
                title="Ujęcie dokumentów w odpowiednim okresie i ewidencji",
            )
        ],
        audit={"grounded": True},
        redacted_query="Jak ująć koszt w okresie?",
        category="rachunkowosc",
        retrieval_path="workflow",
    )

    monkeypatch.setattr(
        "analysis.run_workflow_answer_eval.answer_query",
        lambda query, knowledge_path, system_prompt, api_key: sparse_result,
    )

    from analysis.run_workflow_answer_eval import WorkflowAnswerEvalCase

    result = evaluate_case(
        WorkflowAnswerEvalCase(
            question="Jak ująć koszt w okresie?",
            normalized_question="jak ująć koszt w okresie?",
            subset="workflow_answer_expected",
            classification="workflow",
            primary_intent="accounting_operational",
            expected_behavior="answer_directly",
            expected_law_or_area="workflow",
            expected_source_type="workflow_kb",
            source_category="rachunkowosc",
            source_frequency=7,
            needs_clarification=False,
            golden_overlap=True,
        )
    )

    assert result["workflow_formatted"] is True
    assert result["invented_sections"] == []
    assert result["sparse_workflow_safe"] is True
