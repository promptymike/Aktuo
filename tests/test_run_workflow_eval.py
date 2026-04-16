from __future__ import annotations

import json
from pathlib import Path

from analysis.run_workflow_eval import evaluate_record, run_workflow_eval
from core.retriever import LawChunk, QueryAnalysis
from core.workflow_retriever import WorkflowRetrievalResult


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


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
            "expected_behavior": "ask_follow_up",
            "expected_law_or_area": "workflow",
        },
        {
            "classification": "legal",
            "question": "Jaki jest termin złożenia JPK_V7?",
            "primary_intent": "vat_jpk_ksef",
            "source_category": "jpk",
            "source_frequency": 11,
            "expected_behavior": "answer_directly",
            "expected_law_or_area": "VAT / JPK / KSeF",
        },
        {
            "classification": "mixed",
            "question": "Jak skorygować JPK po błędzie w fakturze?",
            "primary_intent": "legal_procedural",
            "source_category": "jpk",
            "source_frequency": 10,
            "expected_behavior": "ask_follow_up",
            "expected_law_or_area": "VAT / JPK / KSeF",
        },
    ]


def _golden_rows() -> list[dict[str, object]]:
    return list(_workflow_rows())


def _workflow_seed_rows() -> list[dict[str, object]]:
    return [
        {
            "workflow_area": "Sprawozdanie finansowe / podpis / wysyłka",
            "title": "Przygotowanie, podpisanie i wysyłka sprawozdania finansowego",
            "category": "rachunkowosc",
            "question_examples": ["Jak wysłać sprawozdanie finansowe?"],
            "steps": ["Przygotuj plik.", "Wyślij przez właściwą bramkę."],
            "required_inputs": ["okres_księgowy"],
            "common_pitfalls": ["Brak podpisu."],
            "related_forms": ["e-Sprawozdanie finansowe"],
            "related_systems": ["KRS"],
            "source_type": "workflow_seed_v1",
        }
    ]


def _legal_seed_rows() -> list[dict[str, object]]:
    return [
        {
            "law_name": "Ustawa o VAT",
            "article_number": "art. 99",
            "category": "terminy",
            "verified_date": "2026-04-01",
            "question_intent": "Jaki jest termin złożenia JPK_V7?",
            "content": "JPK_V7 składa się do 25. dnia miesiąca po danym okresie rozliczeniowym.",
        }
    ]


def _patch_runtime(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def fake_analyze(query: str) -> QueryAnalysis:
        if "sprawozdanie" in query.lower():
            return QueryAnalysis("accounting_operational", [], False)
        if "termin" in query.lower():
            return QueryAnalysis("vat_jpk_ksef", [], False)
        return QueryAnalysis("legal_procedural", [], False)

    def fake_workflow_eligible(query: str, intent: str) -> bool:
        return intent in {"accounting_operational", "legal_procedural"}

    def fake_workflow(query: str, workflow_path: Path, limit: int = 5) -> WorkflowRetrievalResult:
        if "sprawozdanie" in query.lower():
            return WorkflowRetrievalResult(
                chunks=[
                    LawChunk(
                        content="Workflow content",
                        law_name="Workflow layer",
                        article_number="Przygotowanie, podpisanie i wysyłka sprawozdania finansowego",
                        category="rachunkowosc",
                        verified_date="",
                        score=12.0,
                        source_type="workflow_seed_v1",
                        workflow_area="Sprawozdanie finansowe / podpis / wysyłka",
                        title="Przygotowanie, podpisanie i wysyłka sprawozdania finansowego",
                    )
                ],
                confident=True,
                top_score=12.0,
            )
        if "skorygować jpk" in query.lower():
            return WorkflowRetrievalResult(
                chunks=[
                    LawChunk(
                        content="Weak workflow",
                        law_name="Workflow layer",
                        article_number="Obsługa wysyłki, korekty i oznaczeń JPK",
                        category="jpk",
                        verified_date="",
                        score=4.0,
                        source_type="workflow_seed_v1",
                        workflow_area="JPK filing / correction / tags",
                        title="Obsługa wysyłki, korekty i oznaczeń JPK",
                    )
                ],
                confident=False,
                top_score=4.0,
            )
        return WorkflowRetrievalResult(chunks=[], confident=False, top_score=0.0)

    def fake_legal(query: str, knowledge_path: Path, limit: int = 5) -> list[LawChunk]:
        return [
            LawChunk(
                content="Legal content",
                law_name="Ustawa o VAT",
                article_number="art. 99",
                category="terminy",
                verified_date="2026-04-01",
                score=0.9,
                source_type="legal_kb",
            )
        ]

    monkeypatch.setattr("analysis.run_workflow_eval.analyze_query_requirements", fake_analyze)
    monkeypatch.setattr("analysis.run_workflow_eval.is_workflow_eligible", fake_workflow_eligible)
    monkeypatch.setattr("analysis.run_workflow_eval.retrieve_workflow", fake_workflow)
    monkeypatch.setattr("analysis.run_workflow_eval.retrieve_chunks", fake_legal)


def test_run_workflow_eval_generates_expected_report_schema(tmp_path: Path, monkeypatch) -> None:
    workflow_split = tmp_path / "workflow.jsonl"
    golden = tmp_path / "golden.jsonl"
    workflow_seed = tmp_path / "workflow_seed.json"
    legal_seed = tmp_path / "law_knowledge.json"
    report_json = tmp_path / "workflow_eval_report.json"
    report_md = tmp_path / "workflow_eval_report.md"
    _write_jsonl(workflow_split, _workflow_rows())
    _write_jsonl(golden, _golden_rows())
    _write_json(workflow_seed, _workflow_seed_rows())
    _write_json(legal_seed, _legal_seed_rows())
    _patch_runtime(monkeypatch)

    report = run_workflow_eval(
        workflow_split_path=workflow_split,
        golden_eval_path=golden,
        workflow_seed_path=workflow_seed,
        legal_knowledge_path=legal_seed,
        report_json_path=report_json,
        report_md_path=report_md,
        limit_per_subset=10,
    )

    assert report_json.exists()
    assert report_md.exists()
    assert report["records_evaluated"] == 3
    assert "metrics" in report
    assert "error_analysis" in report
    assert "recommendation" in report


def test_evaluate_record_routes_workflow_sample_to_workflow(tmp_path: Path, monkeypatch) -> None:
    workflow_split = tmp_path / "workflow.jsonl"
    golden = tmp_path / "golden.jsonl"
    _write_jsonl(workflow_split, _workflow_rows())
    _write_jsonl(golden, _golden_rows())
    _patch_runtime(monkeypatch)

    from analysis.run_workflow_eval import load_eval_records

    record = next(item for item in load_eval_records(workflow_split, golden, 10) if item.subset == "workflow_expected")
    result = evaluate_record(record)

    assert result["selected_path"] == "workflow"


def test_evaluate_record_routes_legal_sample_to_legal(tmp_path: Path, monkeypatch) -> None:
    workflow_split = tmp_path / "workflow.jsonl"
    golden = tmp_path / "golden.jsonl"
    _write_jsonl(workflow_split, _workflow_rows())
    _write_jsonl(golden, _golden_rows())
    _patch_runtime(monkeypatch)

    from analysis.run_workflow_eval import load_eval_records

    record = next(item for item in load_eval_records(workflow_split, golden, 10) if item.subset == "legal_expected")
    result = evaluate_record(record)

    assert result["selected_path"] == "legal"


def test_evaluate_record_routes_mixed_sample_to_safe_fallback(tmp_path: Path, monkeypatch) -> None:
    workflow_split = tmp_path / "workflow.jsonl"
    golden = tmp_path / "golden.jsonl"
    _write_jsonl(workflow_split, _workflow_rows())
    _write_jsonl(golden, _golden_rows())
    _patch_runtime(monkeypatch)

    from analysis.run_workflow_eval import load_eval_records

    record = next(item for item in load_eval_records(workflow_split, golden, 10) if item.subset == "mixed_expected")
    result = evaluate_record(record)

    assert result["selected_path"] == "legal_fallback_from_workflow"
