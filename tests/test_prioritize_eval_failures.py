from __future__ import annotations

import json

from analysis.prioritize_eval_failures import (
    build_priority_report,
    load_eval_report,
    render_markdown,
    write_priority_outputs,
)


def test_prioritize_eval_failures_groups_synthetic_report(tmp_path) -> None:
    """The prioritization script should group failed records by inferred root cause."""

    eval_report_path = tmp_path / "eval_report.json"
    output_json = tmp_path / "eval_priorities.json"
    output_md = tmp_path / "eval_priorities.md"

    eval_report_path.write_text(
        json.dumps(
            {
                "overall": {"behavior_accuracy": 0.5},
                "records": [
                    {
                        "question": "Jak rozliczyć VAT?",
                        "source_frequency": 12,
                        "expected_intent": "vat_jpk_ksef",
                        "predicted_intent": "vat_jpk_ksef",
                        "expected_behavior": "ask_follow_up",
                        "predicted_behavior": "answer_directly",
                        "expected_law_or_area": "VAT / JPK / KSeF",
                        "law_match": False,
                        "behavior_match": False,
                        "top_chunks": [{"law_name": "Ustawa o VAT"}],
                    },
                    {
                        "question": "PIT-37 za 2025",
                        "source_frequency": 8,
                        "expected_intent": "pit_ryczalt",
                        "predicted_intent": "unknown",
                        "expected_behavior": "answer_directly",
                        "predicted_behavior": "insufficient_data",
                        "expected_law_or_area": "PIT / ryczałt",
                        "law_match": False,
                        "behavior_match": False,
                        "top_chunks": [],
                    },
                    {
                        "question": "WHT przy odsetkach",
                        "source_frequency": 5,
                        "expected_intent": "cit_wht",
                        "predicted_intent": "vat_jpk_ksef",
                        "expected_behavior": "answer_directly",
                        "predicted_behavior": "answer_directly",
                        "expected_law_or_area": "CIT / WHT",
                        "law_match": False,
                        "behavior_match": False,
                        "top_chunks": [{"law_name": "Ustawa o VAT"}],
                    },
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    report = load_eval_report(eval_report_path)
    priorities = build_priority_report(report)
    json_path, md_path = write_priority_outputs(priorities, json_path=output_json, markdown_path=output_md)
    markdown = render_markdown(priorities)

    assert json_path.exists()
    assert md_path.exists()
    assert priorities["failed_records"] == 3

    root_causes = {item["root_cause"]: item for item in priorities["root_cause_summary"]}
    assert root_causes["needs_clarification_but_answered"]["count"] == 1
    assert root_causes["missing_synonym"]["total_frequency"] == 8
    assert root_causes["wrong_category_match"]["example_questions"] == ["WHT przy odsetkach"]

    top_fix = priorities["suggested_fixes"][0]
    assert top_fix["root_cause"] == "needs_clarification_but_answered"
    assert "VAT / JPK / KSeF" in top_fix["expected_law_or_area"]
    assert "Jak rozliczyć VAT?" in markdown
    assert "Top 20 suggested fixes" in output_md.read_text(encoding="utf-8")

