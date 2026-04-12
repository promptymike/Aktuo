from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import CLARIFICATION_SLOTS_PATH, INTENT_TAXONOMY_PATH
from core.retriever import LawChunk, retrieve


DEFAULT_EVAL_SET_PATH = ROOT / "data" / "curated" / "golden_eval_set.jsonl"
DEFAULT_KNOWLEDGE_PATH = ROOT / "data" / "seeds" / "law_knowledge.json"
DEFAULT_REPORT_PATH = ROOT / "analysis" / "eval_report.json"
OUT_OF_SCOPE_INTENTS = {"unknown", "out_of_scope", "education_community", "business_of_accounting_office"}
JSONDict = dict[str, Any]


@dataclass(slots=True)
class EvalOutcome:
    """Structured result of evaluating one golden-set record."""

    question: str
    source_frequency: int
    expected_intent: str
    predicted_intent: str
    expected_behavior: str
    predicted_behavior: str
    expected_law_or_area: str
    law_match: bool
    intent_match: bool
    behavior_match: bool
    needs_clarification: bool
    missing_slots: list[str]
    expected_missing_slots: list[str]
    top_chunks: list[JSONDict]


def load_eval_set(path: str | Path = DEFAULT_EVAL_SET_PATH) -> list[JSONDict]:
    """Load the curated golden evaluation set from JSONL."""

    file_path = Path(path)
    records: list[JSONDict] = []
    with file_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError(f"Invalid eval record at line {line_number}: expected JSON object.")
            records.append(payload)
    return records


def _normalize(value: str) -> str:
    return " ".join((value or "").lower().replace("–", "-").replace("—", "-").split())


def _law_area_matches(chunk: LawChunk | None, expected_area: str) -> bool:
    """Return True when the retrieved chunk matches the expected law area."""

    if chunk is None:
        return False

    expected = _normalize(expected_area)
    haystack = _normalize(" ".join([chunk.law_name, chunk.category, chunk.article_number, chunk.content[:160]]))
    aliases = {
        "vat / jpk / ksef": ("vat", "jpk", "ksef", "fakt"),
        "pit / ryczałt": ("fizycznych", "pit", "ryczalt"),
        "pit / ryczaĹ‚t": ("fizycznych", "pit", "ryczalt"),
        "cit / wht": ("prawnych", "cit", "wht", "rezydencj"),
        "ordynacja podatkowa / procedury": ("ordynacja", "nadplata", "pelnomoc", "korekta"),
        "rachunkowość operacyjna": ("rachunkow", "kpir", "ksieg", "sprawozdanie"),
        "rachunkowoĹ›Ä‡ operacyjna": ("rachunkow", "kpir", "ksieg", "sprawozdanie"),
        "kadry i płace": ("pracy", "wynagrodz", "urlop", "etat", "zlecen"),
        "kadry i pĹ‚ace": ("pracy", "wynagrodz", "urlop", "etat", "zlecen"),
        "zus": ("zus", "ubezpieczen", "skladk", "chorob"),
        "przepisy materialne": ("art.", "ustawa", "podatek", "vat", "pit", "cit"),
        "edukacja i społeczność": ("kurs", "szkol", "certyfikat", "spoleczn"),
        "edukacja i spoĹ‚ecznoĹ›Ä‡": ("kurs", "szkol", "certyfikat", "spoleczn"),
        "oprogramowanie księgowe": ("symfonia", "comarch", "insert", "enova", "program"),
        "oprogramowanie ksiÄ™gowe": ("symfonia", "comarch", "insert", "enova", "program"),
    }

    if expected in aliases:
        return any(alias in haystack for alias in aliases[expected])

    expected_tokens = [token for token in expected.split() if len(token) > 2]
    return bool(expected_tokens) and any(token in haystack for token in expected_tokens)


def _predict_behavior(expected_behavior: str, predicted_intent: str, retrieval_needs_clarification: bool, chunks: list[LawChunk]) -> str:
    """Predict high-level system behavior for one eval record."""

    if retrieval_needs_clarification:
        return "ask_follow_up"
    if not chunks:
        if predicted_intent in OUT_OF_SCOPE_INTENTS:
            return "out_of_scope"
        return "insufficient_data"
    return "answer_directly"


def evaluate_record(
    record: JSONDict,
    *,
    knowledge_path: str | Path = DEFAULT_KNOWLEDGE_PATH,
    taxonomy_path: str = INTENT_TAXONOMY_PATH,
    slots_path: str = CLARIFICATION_SLOTS_PATH,
) -> EvalOutcome:
    """Evaluate one golden-set record against the current intent router and retriever."""

    question = str(record.get("question", "")).strip()
    expected_intent = str(record.get("primary_intent", "unknown"))
    expected_behavior = str(record.get("expected_behavior", record.get("expected_behaviour", "answer_directly")))
    expected_law_or_area = str(record.get("expected_law_or_area", ""))
    expected_missing_slots = [str(slot) for slot in record.get("missing_clarification_fields", []) if isinstance(slot, str)]
    source_frequency = int(record.get("source_frequency", 1) or 1)

    retrieval_result = retrieve(
        query=question,
        knowledge_path=knowledge_path,
        taxonomy_path=taxonomy_path,
        slots_path=slots_path,
        limit=5,
    )
    predicted_intent = retrieval_result.intent
    predicted_behavior = _predict_behavior(
        expected_behavior,
        predicted_intent,
        retrieval_result.needs_clarification,
        retrieval_result.chunks,
    )
    top_chunk = retrieval_result.chunks[0] if retrieval_result.chunks else None
    law_match = _law_area_matches(top_chunk, expected_law_or_area)

    if expected_behavior == "answer_directly":
        behavior_match = not retrieval_result.needs_clarification and law_match
    elif expected_behavior == "ask_follow_up":
        behavior_match = retrieval_result.needs_clarification and set(expected_missing_slots).issubset(
            set(retrieval_result.missing_slots or [])
        )
    elif expected_behavior == "insufficient_data":
        behavior_match = retrieval_result.needs_clarification or not retrieval_result.chunks
    elif expected_behavior == "out_of_scope":
        behavior_match = not retrieval_result.chunks or predicted_intent in OUT_OF_SCOPE_INTENTS
    else:
        behavior_match = predicted_behavior == expected_behavior

    return EvalOutcome(
        question=question,
        source_frequency=source_frequency,
        expected_intent=expected_intent,
        predicted_intent=predicted_intent,
        expected_behavior=expected_behavior,
        predicted_behavior=predicted_behavior,
        expected_law_or_area=expected_law_or_area,
        law_match=law_match,
        intent_match=predicted_intent == expected_intent,
        behavior_match=behavior_match,
        needs_clarification=retrieval_result.needs_clarification,
        missing_slots=list(retrieval_result.missing_slots or []),
        expected_missing_slots=expected_missing_slots,
        top_chunks=[
            {
                "law_name": chunk.law_name,
                "article_number": chunk.article_number,
                "category": chunk.category,
                "score": round(chunk.score, 6),
            }
            for chunk in retrieval_result.chunks[:3]
        ],
    )


def _safe_ratio(numerator: int, denominator: int) -> float:
    return round((numerator / denominator) if denominator else 0.0, 4)


def build_eval_report(
    *,
    eval_set_path: str | Path = DEFAULT_EVAL_SET_PATH,
    knowledge_path: str | Path = DEFAULT_KNOWLEDGE_PATH,
    taxonomy_path: str = INTENT_TAXONOMY_PATH,
    slots_path: str = CLARIFICATION_SLOTS_PATH,
) -> JSONDict:
    """Run the evaluation harness and return a structured report."""

    records = load_eval_set(eval_set_path)
    outcomes = [
        evaluate_record(
            record,
            knowledge_path=knowledge_path,
            taxonomy_path=taxonomy_path,
            slots_path=slots_path,
        )
        for record in records
    ]

    actual_intent_counts = Counter(outcome.expected_intent for outcome in outcomes)
    predicted_intent_counts = Counter(outcome.predicted_intent for outcome in outcomes)
    true_positive_intents = Counter(
        outcome.expected_intent for outcome in outcomes if outcome.expected_intent == outcome.predicted_intent
    )

    per_intent: dict[str, JSONDict] = {}
    for intent in sorted(set(actual_intent_counts) | set(predicted_intent_counts)):
        total = actual_intent_counts[intent]
        predicted = predicted_intent_counts[intent]
        true_positive = true_positive_intents[intent]
        behavior_correct = sum(1 for outcome in outcomes if outcome.expected_intent == intent and outcome.behavior_match)
        per_intent[intent] = {
            "total": total,
            "predicted": predicted,
            "true_positive": true_positive,
            "accuracy": _safe_ratio(behavior_correct, total),
            "precision": _safe_ratio(true_positive, predicted),
            "recall": _safe_ratio(true_positive, total),
            "behavior_correct": behavior_correct,
        }

    total_records = len(outcomes)
    correct_behaviors = sum(1 for outcome in outcomes if outcome.behavior_match)
    correct_intents = sum(1 for outcome in outcomes if outcome.intent_match)
    macro_precision = _safe_ratio(
        sum(metrics["precision"] for metrics in per_intent.values()),
        len(per_intent),
    )
    macro_recall = _safe_ratio(
        sum(metrics["recall"] for metrics in per_intent.values()),
        len(per_intent),
    )

    return {
        "overall": {
            "total_records": total_records,
            "behavior_accuracy": _safe_ratio(correct_behaviors, total_records),
            "intent_accuracy": _safe_ratio(correct_intents, total_records),
            "macro_precision": macro_precision,
            "macro_recall": macro_recall,
        },
        "per_intent": per_intent,
        "records": [
            {
                "question": outcome.question,
                "source_frequency": outcome.source_frequency,
                "expected_intent": outcome.expected_intent,
                "predicted_intent": outcome.predicted_intent,
                "expected_behavior": outcome.expected_behavior,
                "predicted_behavior": outcome.predicted_behavior,
                "expected_law_or_area": outcome.expected_law_or_area,
                "law_match": outcome.law_match,
                "intent_match": outcome.intent_match,
                "behavior_match": outcome.behavior_match,
                "needs_clarification": outcome.needs_clarification,
                "missing_slots": outcome.missing_slots,
                "expected_missing_slots": outcome.expected_missing_slots,
                "top_chunks": outcome.top_chunks,
            }
            for outcome in outcomes
        ],
    }


def write_eval_report(report: JSONDict, path: str | Path = DEFAULT_REPORT_PATH) -> Path:
    """Write the evaluation report as deterministic JSON."""

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return file_path


def main() -> None:
    """CLI entry point for the golden-set evaluation harness."""

    report = build_eval_report()
    write_eval_report(report)
    print(json.dumps(report["overall"], ensure_ascii=False))


if __name__ == "__main__":
    main()
