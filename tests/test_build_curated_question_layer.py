from __future__ import annotations

from analysis.build_curated_question_layer import (
    AggregatedQuestion,
    build_curated_record,
    build_dedupe_key,
    choose_golden_eval_records,
    infer_primary_intent,
)


def make_question(
    question: str,
    *,
    category: str = "inne",
    subcategory: str = "",
    frequency: int = 5,
) -> AggregatedQuestion:
    return AggregatedQuestion(
        question=question,
        normalized_question=question.lower(),
        dedupe_key=build_dedupe_key(question),
        source_frequency=frequency,
        category=category,
        subcategory=subcategory,
        source_post_count=frequency,
        examples=[question],
    )


def test_build_dedupe_key_collapses_whitespace_and_case() -> None:
    assert build_dedupe_key("  JPK_V7   za marzec? ") == build_dedupe_key("jpk v7 za marzec")


def test_infer_primary_intent_detects_vat_ksef() -> None:
    question = make_question("Czy faktura w KSeF wymaga dodatkowego oznaczenia w JPK?", category="ksef")
    assert infer_primary_intent(question) == "vat_jpk_ksef"


def test_build_curated_record_flags_missing_clarification_for_short_vat_question() -> None:
    record = build_curated_record(make_question("VAT od usługi?", category="vat"))
    assert record["primary_intent"] == "vat_jpk_ksef"
    assert record["needs_clarification"] is True
    assert "rodzaj_dokumentu" in record["missing_clarification_fields"]


def test_choose_golden_eval_records_is_deterministic() -> None:
    records = []
    intents = [
        "legal_substantive",
        "legal_procedural",
        "accounting_operational",
        "payroll",
        "hr",
        "zus",
        "vat_jpk_ksef",
        "pit_ryczalt",
        "cit_wht",
        "software_tooling",
        "business_of_accounting_office",
        "education_community",
        "out_of_scope",
    ]
    for idx in range(260):
        intent = intents[idx % len(intents)]
        records.append(
            {
                "question": f"Pytanie {idx:03d}",
                "source_frequency": 300 - idx,
                "primary_intent": intent,
                "classification": "legal",
                "needs_clarification": False,
            }
        )

    first = choose_golden_eval_records(records)
    second = choose_golden_eval_records(records)

    assert first == second
    assert len(first) >= 200
