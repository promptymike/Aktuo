from __future__ import annotations

import json
from pathlib import Path

from analysis.run_eval import build_eval_report, write_eval_report


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_run_eval_builds_report_with_expected_keys(tmp_path) -> None:
    """The evaluation harness should load JSONL and return the expected report structure."""

    taxonomy_path = tmp_path / "intent_taxonomy.json"
    slots_path = tmp_path / "clarification_slots.json"
    knowledge_path = tmp_path / "law_knowledge.json"
    eval_path = tmp_path / "golden_eval_set.jsonl"
    report_path = tmp_path / "eval_report.json"

    _write_json(
        taxonomy_path,
        {
            "vat_jpk_ksef": {
                "description": "Pytania o VAT, JPK i KSeF.",
                "routing_recommendation": "Kieruj do VAT.",
                "examples": ["Czy faktura VAT z marca 2026 jest poprawna?"],
            }
        },
    )
    _write_json(
        slots_path,
        {
            "vat_jpk_ksef": {
                "required_facts": ["rodzaj_dokumentu", "okres_lub_data", "rola_lub_status_strony"]
            }
        },
    )
    _write_json(
        knowledge_path,
        [
            {
                "law_name": "Ustawa o VAT",
                "article_number": "art. 106e",
                "category": "vat",
                "content": "Faktura VAT powinna zawierać wymagane dane sprzedawcy i nabywcy.",
                "verified_date": "2026-04-01",
                "question_intent": "Jakie elementy musi zawierać faktura VAT?",
            }
        ],
    )
    eval_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "question": "Czy faktura VAT sprzedawcy z marca 2026 musi zawierać dane nabywcy?",
                        "primary_intent": "vat_jpk_ksef",
                        "expected_behavior": "answer_directly",
                        "expected_law_or_area": "VAT / JPK / KSeF",
                        "missing_clarification_fields": [],
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "question": "Jak rozliczyć VAT?",
                        "primary_intent": "vat_jpk_ksef",
                        "expected_behavior": "ask_follow_up",
                        "expected_law_or_area": "VAT / JPK / KSeF",
                        "missing_clarification_fields": [
                            "rodzaj_dokumentu",
                            "okres_lub_data",
                            "rola_lub_status_strony",
                        ],
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_eval_report(
        eval_set_path=eval_path,
        knowledge_path=knowledge_path,
        taxonomy_path=str(taxonomy_path),
        slots_path=str(slots_path),
    )
    written_path = write_eval_report(report, report_path)

    assert written_path == report_path
    assert report_path.exists()
    assert set(report) == {"overall", "per_intent", "records"}
    assert set(report["overall"]) == {"total_records", "behavior_accuracy", "intent_accuracy", "macro_precision", "macro_recall"}
    assert "vat_jpk_ksef" in report["per_intent"]
    assert len(report["records"]) == 2


def test_run_eval_vat_case_matches_expected_behaviour(tmp_path) -> None:
    """A simple VAT record should be marked as a correct direct-answer case."""

    taxonomy_path = tmp_path / "intent_taxonomy.json"
    slots_path = tmp_path / "clarification_slots.json"
    knowledge_path = tmp_path / "law_knowledge.json"
    eval_path = tmp_path / "golden_eval_set.jsonl"

    _write_json(
        taxonomy_path,
        {
            "vat_jpk_ksef": {
                "description": "Pytania o VAT, JPK i KSeF.",
                "routing_recommendation": "Kieruj do VAT.",
                "examples": ["Faktura VAT sprzedawcy za marzec 2026"],
            }
        },
    )
    _write_json(
        slots_path,
        {
            "vat_jpk_ksef": {
                "required_facts": ["rodzaj_dokumentu", "okres_lub_data", "rola_lub_status_strony"]
            }
        },
    )
    _write_json(
        knowledge_path,
        [
            {
                "law_name": "Ustawa o VAT",
                "article_number": "art. 106e",
                "category": "vat",
                "content": "Faktura VAT musi zawierać dane pozwalające zidentyfikować sprzedawcę i nabywcę.",
                "verified_date": "2026-04-01",
                "question_intent": "Jakie elementy musi zawierać faktura VAT?",
            }
        ],
    )
    eval_path.write_text(
        json.dumps(
            {
                "question": "Czy faktura VAT sprzedawcy z marca 2026 musi zawierać dane nabywcy?",
                "primary_intent": "vat_jpk_ksef",
                "expected_behavior": "answer_directly",
                "expected_law_or_area": "VAT / JPK / KSeF",
                "missing_clarification_fields": [],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_eval_report(
        eval_set_path=eval_path,
        knowledge_path=knowledge_path,
        taxonomy_path=str(taxonomy_path),
        slots_path=str(slots_path),
    )

    record = report["records"][0]
    assert record["predicted_intent"] == "vat_jpk_ksef"
    assert record["expected_behavior"] == "answer_directly"
    assert record["behavior_match"] is True
    assert record["law_match"] is True
    assert report["overall"]["behavior_accuracy"] == 1.0

