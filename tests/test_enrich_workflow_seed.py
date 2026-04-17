from __future__ import annotations

import json
from pathlib import Path

from analysis.enrich_workflow_seed import enrich_workflow_seed


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def _seed_rows() -> list[dict[str, object]]:
    return [
        {
            "workflow_area": "JPK filing / correction / tags",
            "title": "Obsługa wysyłki, korekty i oznaczeń JPK",
            "category": "jpk",
            "question_examples": ["Jak wysłać korektę JPK?"],
            "steps": ["Sprawdź, czego dotyczy korekta."],
            "required_inputs": ["okres_lub_data"],
            "common_pitfalls": ["Brak UPO."],
            "related_forms": ["JPK_V7M"],
            "related_systems": ["JPK"],
            "source_type": "workflow_seed_v1",
            "user_intent": "checklist",
            "cluster_impact": {"question_count": 1, "total_frequency": 8, "weighted_impact": 8.0},
        }
    ]


def _workflow_rows() -> list[dict[str, object]]:
    return [
        {
            "classification": "workflow",
            "question": "Jak wysłać korektę JPK_V7 z oznaczeniem GTU?",
            "primary_intent": "vat_jpk_ksef",
            "source_category": "jpk",
            "source_frequency": 8,
            "missing_clarification_fields": ["okres_lub_data", "rodzaj_korekty_lub_oznaczenia"],
        },
        {
            "classification": "workflow",
            "question": "Jak oznaczyć korektę JPK po zmianie danych w ewidencji?",
            "primary_intent": "vat_jpk_ksef",
            "source_category": "jpk",
            "source_frequency": 6,
            "missing_clarification_fields": ["okres_lub_data", "rodzaj_korekty_lub_oznaczenia"],
        },
        {
            "classification": "workflow",
            "question": "Czy korektę JPK wysyłam przez tę samą bramkę i jak zapisać UPO?",
            "primary_intent": "vat_jpk_ksef",
            "source_category": "jpk",
            "source_frequency": 5,
            "missing_clarification_fields": ["nazwa_systemu", "okres_lub_data"],
        },
        {
            "classification": "workflow",
            "question": "Leasing samochodu osobowego – czy po wykupie mogę księgować koszty 20% i jak ująć VAT-26?",
            "primary_intent": "accounting_operational",
            "source_category": "rachunkowosc",
            "source_frequency": 7,
            "missing_clarification_fields": ["status_pojazdu_w_firmie", "sposób_użytkowania_pojazdu"],
        },
    ]


def _golden_rows() -> list[dict[str, object]]:
    return [
        {
            "question": "Jak wysłać korektę JPK_V7 z oznaczeniem GTU?",
            "source_frequency": 8,
        },
        {
            "question": "Jak oznaczyć korektę JPK po zmianie danych w ewidencji?",
            "source_frequency": 6,
        },
        {
            "question": "Czy korektę JPK wysyłam przez tę samą bramkę i jak zapisać UPO?",
            "source_frequency": 5,
        },
        {
            "question": "Leasing samochodu osobowego – czy po wykupie mogę księgować koszty 20% i jak ująć VAT-26?",
            "source_frequency": 7,
        },
    ]


def _answer_eval_report() -> dict[str, object]:
    return {
        "records": [
            {
                "subset": "workflow_answer_expected",
                "question": "Jak wysłać korektę JPK_V7 z oznaczeniem GTU?",
                "source_category": "jpk",
                "source_frequency": 8,
                "needs_clarification": True,
                "expected_law_or_area": "workflow",
            },
            {
                "subset": "workflow_answer_expected",
                "question": "Jak oznaczyć korektę JPK po zmianie danych w ewidencji?",
                "source_category": "jpk",
                "source_frequency": 6,
                "needs_clarification": True,
                "expected_law_or_area": "workflow",
            },
            {
                "subset": "workflow_answer_expected",
                "question": "Czy korektę JPK wysyłam przez tę samą bramkę i jak zapisać UPO?",
                "source_category": "jpk",
                "source_frequency": 5,
                "needs_clarification": True,
                "expected_law_or_area": "workflow",
            },
            {
                "subset": "workflow_answer_expected",
                "question": "Leasing samochodu osobowego – czy po wykupie mogę księgować koszty 20% i jak ująć VAT-26?",
                "source_category": "rachunkowosc",
                "source_frequency": 7,
                "needs_clarification": True,
                "expected_law_or_area": "workflow",
            },
        ]
    }


def _routing_eval_report() -> dict[str, object]:
    return {
        "error_analysis": {
            "top_workflow_questions_incorrectly_went_to_legal": [
                {
                    "question": "Leasing samochodu osobowego – czy po wykupie mogę księgować koszty 20% i jak ująć VAT-26?",
                    "source_category": "rachunkowosc",
                    "source_frequency": 7,
                    "expected_law_or_area": "workflow",
                }
            ]
        }
    }


def test_enrich_workflow_seed_preserves_schema_and_existing_data(tmp_path: Path) -> None:
    workflow_seed_path = tmp_path / "workflow_seed.json"
    workflow_split_path = tmp_path / "workflow_split.jsonl"
    golden_eval_path = tmp_path / "golden_eval.jsonl"
    workflow_answer_eval_path = tmp_path / "workflow_answer_eval.json"
    workflow_routing_eval_path = tmp_path / "workflow_routing_eval.json"
    report_json_path = tmp_path / "workflow_seed_enrichment_report.json"
    report_md_path = tmp_path / "workflow_seed_enrichment_report.md"

    _write_json(workflow_seed_path, _seed_rows())
    _write_jsonl(workflow_split_path, _workflow_rows())
    _write_jsonl(golden_eval_path, _golden_rows())
    _write_json(workflow_answer_eval_path, _answer_eval_report())
    _write_json(workflow_routing_eval_path, _routing_eval_report())

    report = enrich_workflow_seed(
        workflow_seed_path=workflow_seed_path,
        workflow_split_path=workflow_split_path,
        golden_eval_path=golden_eval_path,
        workflow_answer_eval_path=workflow_answer_eval_path,
        workflow_routing_eval_path=workflow_routing_eval_path,
        report_json_path=report_json_path,
        report_md_path=report_md_path,
    )

    enriched_seed = json.loads(workflow_seed_path.read_text(encoding="utf-8"))

    assert report_json_path.exists()
    assert report_md_path.exists()
    assert report["after_seed_unit_count"] == len(enriched_seed)
    assert report["units_safely_enriched_count"] >= 1
    assert report["selected_units"]
    assert report["next_recommended_units"]

    jpk_unit = next(row for row in enriched_seed if row["title"] == "Obsługa wysyłki, korekty i oznaczeń JPK")
    assert "Jak wysłać korektę JPK?" in jpk_unit["question_examples"]
    assert len(jpk_unit["question_examples"]) > 1
    assert len(jpk_unit["steps"]) >= 2
    assert len(jpk_unit["required_inputs"]) >= 2

    leasing_unit = next(row for row in enriched_seed if row["title"] == "Leasing, wykup samochodu i ewidencja kosztów pojazdu")
    for key in (
        "workflow_area",
        "title",
        "category",
        "question_examples",
        "steps",
        "required_inputs",
        "common_pitfalls",
        "related_forms",
        "related_systems",
        "source_type",
        "user_intent",
    ):
        assert key in leasing_unit
    assert leasing_unit["question_examples"]
    assert leasing_unit["steps"]


def test_enrich_workflow_seed_is_deterministic(tmp_path: Path) -> None:
    workflow_split_path = tmp_path / "workflow_split.jsonl"
    golden_eval_path = tmp_path / "golden_eval.jsonl"
    workflow_answer_eval_path = tmp_path / "workflow_answer_eval.json"
    workflow_routing_eval_path = tmp_path / "workflow_routing_eval.json"

    _write_jsonl(workflow_split_path, _workflow_rows())
    _write_jsonl(golden_eval_path, _golden_rows())
    _write_json(workflow_answer_eval_path, _answer_eval_report())
    _write_json(workflow_routing_eval_path, _routing_eval_report())

    first_seed_path = tmp_path / "first_seed.json"
    second_seed_path = tmp_path / "second_seed.json"
    _write_json(first_seed_path, _seed_rows())
    _write_json(second_seed_path, _seed_rows())

    first_report = enrich_workflow_seed(
        workflow_seed_path=first_seed_path,
        workflow_split_path=workflow_split_path,
        golden_eval_path=golden_eval_path,
        workflow_answer_eval_path=workflow_answer_eval_path,
        workflow_routing_eval_path=workflow_routing_eval_path,
        report_json_path=tmp_path / "first_report.json",
        report_md_path=tmp_path / "first_report.md",
    )
    second_report = enrich_workflow_seed(
        workflow_seed_path=second_seed_path,
        workflow_split_path=workflow_split_path,
        golden_eval_path=golden_eval_path,
        workflow_answer_eval_path=workflow_answer_eval_path,
        workflow_routing_eval_path=workflow_routing_eval_path,
        report_json_path=tmp_path / "second_report.json",
        report_md_path=tmp_path / "second_report.md",
    )

    assert json.loads(first_seed_path.read_text(encoding="utf-8")) == json.loads(second_seed_path.read_text(encoding="utf-8"))
    assert first_report == second_report
