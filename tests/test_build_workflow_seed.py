from __future__ import annotations

import json
from pathlib import Path

from analysis.build_workflow_seed import (
    build_workflow_seed,
    cluster_workflow_records,
    select_workflow_records,
    validate_workflow_units,
)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def _workflow_rows() -> list[dict[str, object]]:
    return [
        {
            "classification": "workflow",
            "question": "Jak wysłać korektę JPK_V7 z oznaczeniem GTU?",
            "primary_intent": "vat_jpk_ksef",
            "source_category": "jpk",
            "source_subcategory": "oznaczenia i znaczniki JPK",
            "source_frequency": 18,
            "missing_clarification_fields": ["okres_lub_data", "rodzaj_dokumentu"],
        },
        {
            "classification": "workflow",
            "question": "Jak nadać uprawnienia w KSeF dla biura rachunkowego?",
            "primary_intent": "vat_jpk_ksef",
            "source_category": "ksef",
            "source_subcategory": "uprawnienia",
            "source_frequency": 16,
            "missing_clarification_fields": ["rola_lub_status_strony"],
        },
        {
            "classification": "workflow",
            "question": "Jak zgłosić pracownika do ZUS przez PUE?",
            "primary_intent": "zus",
            "source_category": "zus",
            "source_subcategory": "zgłoszenia",
            "source_frequency": 14,
            "missing_clarification_fields": ["tytuł_ubezpieczenia"],
        },
        {
            "classification": "mixed",
            "question": "Jak ująć koszt grudniowy w styczniu w KPiR?",
            "primary_intent": "accounting_operational",
            "source_category": "rachunkowosc",
            "source_subcategory": "konta i dekretacja",
            "source_frequency": 12,
            "missing_clarification_fields": ["okres_księgowy", "rodzaj_ksiąg_lub_ewidencji"],
        },
    ]


def _golden_rows() -> list[dict[str, object]]:
    return [
        {"question": "Jak wysłać korektę JPK_V7 z oznaczeniem GTU?"},
        {"question": "Jak nadać uprawnienia w KSeF dla biura rachunkowego?"},
    ]


def test_cluster_workflow_records_returns_expected_shape(tmp_path: Path) -> None:
    workflow_path = tmp_path / "workflow.jsonl"
    golden_path = tmp_path / "golden.jsonl"
    _write_jsonl(workflow_path, _workflow_rows())
    _write_jsonl(golden_path, _golden_rows())

    records = select_workflow_records(workflow_path, golden_path)
    clusters = cluster_workflow_records(records)

    assert clusters
    assert clusters[0].definition.name
    assert clusters[0].records
    assert sum(len(cluster.records) for cluster in clusters) == len(records)


def test_build_workflow_seed_writes_valid_schema(tmp_path: Path) -> None:
    workflow_path = tmp_path / "workflow.jsonl"
    golden_path = tmp_path / "golden.jsonl"
    seed_path = tmp_path / "workflow_seed.json"
    report_json_path = tmp_path / "workflow_seed_report.json"
    report_md_path = tmp_path / "workflow_seed_report.md"
    _write_jsonl(workflow_path, _workflow_rows())
    _write_jsonl(golden_path, _golden_rows())

    units, report = build_workflow_seed(
        workflow_split_path=workflow_path,
        golden_eval_path=golden_path,
        workflow_seed_path=seed_path,
        report_json_path=report_json_path,
        report_md_path=report_md_path,
        unit_limit=4,
    )

    validate_workflow_units(units)
    assert seed_path.exists()
    assert report_json_path.exists()
    assert report_md_path.exists()
    assert report["workflow_questions_analyzed"] == 4
    assert report["workflow_seed_units_created"] == len(units)
    assert all(unit["workflow_area"] for unit in units)
    assert all(unit["title"] for unit in units)
    assert all(unit["category"] for unit in units)
    assert all(unit["question_examples"] for unit in units)
    assert all(unit["steps"] for unit in units)


def test_build_workflow_seed_is_deterministic(tmp_path: Path) -> None:
    workflow_path = tmp_path / "workflow.jsonl"
    golden_path = tmp_path / "golden.jsonl"
    _write_jsonl(workflow_path, _workflow_rows())
    _write_jsonl(golden_path, _golden_rows())

    first_units, first_report = build_workflow_seed(
        workflow_split_path=workflow_path,
        golden_eval_path=golden_path,
        workflow_seed_path=tmp_path / "first_seed.json",
        report_json_path=tmp_path / "first_report.json",
        report_md_path=tmp_path / "first_report.md",
        unit_limit=4,
    )
    second_units, second_report = build_workflow_seed(
        workflow_split_path=workflow_path,
        golden_eval_path=golden_path,
        workflow_seed_path=tmp_path / "second_seed.json",
        report_json_path=tmp_path / "second_report.json",
        report_md_path=tmp_path / "second_report.md",
        unit_limit=4,
    )

    assert first_units == second_units
    assert first_report == second_report
