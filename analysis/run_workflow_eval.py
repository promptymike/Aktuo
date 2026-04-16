from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.retriever import LawChunk, analyze_query_requirements, retrieve_chunks
from core.workflow_retriever import is_workflow_eligible, retrieve_workflow

WORKFLOW_SPLIT_PATH = ROOT / "data" / "curated" / "workflow_vs_legal_vs_out_of_scope.jsonl"
GOLDEN_EVAL_PATH = ROOT / "data" / "curated" / "golden_eval_set.jsonl"
WORKFLOW_SEED_PATH = ROOT / "data" / "workflow" / "workflow_seed.json"
LEGAL_KNOWLEDGE_PATH = ROOT / "data" / "seeds" / "law_knowledge.json"
REPORT_JSON_PATH = ROOT / "analysis" / "workflow_eval_report.json"
REPORT_MD_PATH = ROOT / "analysis" / "workflow_eval_report.md"

JSONDict = dict[str, Any]
SUBSET_NAMES = ("workflow_expected", "legal_expected", "mixed_expected")
DEFAULT_LIMIT_PER_SUBSET = 150


@dataclass(slots=True)
class EvalRecord:
    """One deduplicated evaluation record prepared for routing evaluation."""

    question: str
    normalized_question: str
    subset: str
    classification: str
    primary_intent: str
    source_category: str
    source_frequency: int
    expected_behavior: str
    expected_law_or_area: str
    golden_overlap: bool


def normalize_text(value: str) -> str:
    """Normalize text for deterministic deduplication and sorting."""

    normalized = unicodedata.normalize("NFKD", value.lower())
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_value.split())


def read_jsonl(path: Path) -> list[JSONDict]:
    """Load a JSONL file into a list of dictionaries."""

    rows: list[JSONDict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def classify_eval_subset(record: JSONDict) -> str | None:
    """Map a curated record into one of the workflow evaluation subsets."""

    classification = str(record.get("classification", "")).strip()
    if classification == "workflow":
        return "workflow_expected"
    if classification == "legal":
        return "legal_expected"
    if classification == "mixed":
        return "mixed_expected"
    return None


def load_eval_records(
    workflow_split_path: Path = WORKFLOW_SPLIT_PATH,
    golden_eval_path: Path = GOLDEN_EVAL_PATH,
    limit_per_subset: int = DEFAULT_LIMIT_PER_SUBSET,
) -> list[EvalRecord]:
    """Load deterministic top-N evaluation subsets from curated workflow/legal data.

    Selection rules:
    - workflow_expected: records with ``classification == "workflow"``
    - legal_expected: records with ``classification == "legal"``
    - mixed_expected: records with ``classification == "mixed"``
    - community_only and outside_scope are excluded from this harness
    - within each subset, golden-eval overlap is prioritized, then source frequency,
      then question text for stable ordering
    """

    workflow_rows = read_jsonl(workflow_split_path)
    golden_rows = read_jsonl(golden_eval_path)
    golden_by_question = {
        normalize_text(str(row.get("question", ""))): row for row in golden_rows if row.get("question")
    }

    merged: dict[tuple[str, str], EvalRecord] = {}

    for source_rows in (workflow_rows, golden_rows):
        for row in source_rows:
            subset = classify_eval_subset(row)
            if subset is None:
                continue
            question = str(row.get("question", "")).strip()
            if not question:
                continue
            normalized_question = normalize_text(question)
            golden_match = golden_by_question.get(normalized_question)
            candidate = EvalRecord(
                question=question,
                normalized_question=normalized_question,
                subset=subset,
                classification=str(row.get("classification", "")).strip(),
                primary_intent=str(row.get("primary_intent", "")).strip(),
                source_category=str(row.get("source_category", "")).strip(),
                source_frequency=int(row.get("source_frequency", 1) or 1),
                expected_behavior=str(row.get("expected_behavior", "")).strip(),
                expected_law_or_area=str(row.get("expected_law_or_area", "")).strip(),
                golden_overlap=golden_match is not None,
            )
            key = (subset, normalized_question)
            previous = merged.get(key)
            if previous is None or (
                candidate.golden_overlap,
                candidate.source_frequency,
                candidate.question,
            ) > (
                previous.golden_overlap,
                previous.source_frequency,
                previous.question,
            ):
                merged[key] = candidate

    selected: list[EvalRecord] = []
    for subset in SUBSET_NAMES:
        subset_records = sorted(
            (record for record in merged.values() if record.subset == subset),
            key=lambda record: (
                not record.golden_overlap,
                -record.source_frequency,
                record.question,
            ),
        )
        selected.extend(subset_records[:limit_per_subset])

    return selected


def _top_chunk_metadata(chunk: LawChunk | None) -> JSONDict | None:
    """Serialize top chunk metadata for reports."""

    if chunk is None:
        return None
    return {
        "law_name": chunk.law_name,
        "article_number": chunk.article_number,
        "category": chunk.category,
        "source_type": chunk.source_type,
        "workflow_area": chunk.workflow_area,
        "title": chunk.title,
        "score": round(chunk.score, 4),
    }


def evaluate_record(
    record: EvalRecord,
    legal_knowledge_path: Path = LEGAL_KNOWLEDGE_PATH,
    workflow_seed_path: Path = WORKFLOW_SEED_PATH,
) -> JSONDict:
    """Run routing and retrieval for a single record without calling the generator."""

    analysis = analyze_query_requirements(record.question)
    workflow_eligible = is_workflow_eligible(record.question, analysis.intent)
    workflow_result = retrieve_workflow(record.question, workflow_path=workflow_seed_path, limit=5)

    if workflow_eligible and workflow_result.confident:
        selected_path = "workflow"
        selected_chunks = workflow_result.chunks
        selected_score = workflow_result.top_score
    elif workflow_eligible:
        selected_path = "legal_fallback_from_workflow"
        selected_chunks = retrieve_chunks(record.question, legal_knowledge_path, limit=5)
        selected_score = selected_chunks[0].score if selected_chunks else 0.0
    else:
        selected_path = "legal"
        selected_chunks = retrieve_chunks(record.question, legal_knowledge_path, limit=5)
        selected_score = selected_chunks[0].score if selected_chunks else 0.0

    top_chunk = selected_chunks[0] if selected_chunks else None

    if record.subset == "workflow_expected":
        path_correct = selected_path in {"workflow", "legal_fallback_from_workflow"}
    elif record.subset == "legal_expected":
        path_correct = selected_path == "legal"
    else:
        path_correct = selected_path in {"workflow", "legal_fallback_from_workflow"}

    return {
        "question": record.question,
        "subset": record.subset,
        "classification": record.classification,
        "source_category": record.source_category,
        "source_frequency": record.source_frequency,
        "expected_behavior": record.expected_behavior,
        "expected_law_or_area": record.expected_law_or_area,
        "golden_overlap": record.golden_overlap,
        "predicted_intent": analysis.intent,
        "clarification_flag": analysis.needs_clarification,
        "missing_slots": analysis.missing_slots,
        "workflow_eligible": workflow_eligible,
        "selected_path": selected_path,
        "path_correct": path_correct,
        "workflow_score": round(workflow_result.top_score, 4),
        "selected_score": round(float(selected_score), 4),
        "top_retrieved": _top_chunk_metadata(top_chunk),
        "workflow_top": _top_chunk_metadata(workflow_result.chunks[0] if workflow_result.chunks else None),
    }


def _safe_ratio(numerator: int, denominator: int) -> float:
    """Return a rounded ratio while avoiding division by zero."""

    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def build_workflow_eval_report(results: list[JSONDict]) -> JSONDict:
    """Aggregate routing and retrieval metrics for workflow evaluation."""

    subset_counts = Counter(result["subset"] for result in results)
    clarification_by_subset = {
        subset: _safe_ratio(
            sum(1 for result in results if result["subset"] == subset and result["clarification_flag"]),
            subset_counts[subset],
        )
        for subset in SUBSET_NAMES
    }

    workflow_path_total = sum(1 for result in results if result["selected_path"] == "workflow")
    legal_path_total = sum(1 for result in results if result["selected_path"] == "legal")
    workflow_expected_total = subset_counts["workflow_expected"]
    legal_expected_total = subset_counts["legal_expected"]

    workflow_correct_hits = sum(
        1
        for result in results
        if result["selected_path"] == "workflow" and result["subset"] in {"workflow_expected", "mixed_expected"}
    )
    legal_correct_hits = sum(
        1
        for result in results
        if result["selected_path"] == "legal" and result["subset"] == "legal_expected"
    )

    workflow_area_scores: dict[str, list[float]] = defaultdict(list)
    for result in results:
        workflow_top = result.get("workflow_top") or {}
        workflow_area = workflow_top.get("workflow_area")
        if workflow_area:
            workflow_area_scores[str(workflow_area)].append(float(result["workflow_score"]))

    strongest_workflow_areas = sorted(
        (
            {
                "workflow_area": area,
                "avg_score": round(sum(scores) / len(scores), 4),
                "count": len(scores),
            }
            for area, scores in workflow_area_scores.items()
        ),
        key=lambda item: (-item["avg_score"], -item["count"], item["workflow_area"]),
    )

    failures_workflow_to_legal = sorted(
        (
            result
            for result in results
            if result["subset"] == "workflow_expected" and result["selected_path"] == "legal"
        ),
        key=lambda item: (-item["source_frequency"], item["question"]),
    )
    failures_legal_to_workflow = sorted(
        (
            result
            for result in results
            if result["subset"] == "legal_expected" and result["selected_path"] == "workflow"
        ),
        key=lambda item: (-item["source_frequency"], item["question"]),
    )
    mixed_weak_routing = sorted(
        (
            result
            for result in results
            if result["subset"] == "mixed_expected" and result["selected_path"] not in {"workflow", "legal_fallback_from_workflow"}
        ),
        key=lambda item: (-item["source_frequency"], item["question"]),
    )

    recommendation = (
        "Wzmocnić workflow seed dla obszarów z najniższym workflow_score i najwyższym wolumenem workflow->legal, "
        "zwłaszcza tam, gdzie pytania są operacyjne, ale nie łapią się na confident workflow hit."
        if failures_workflow_to_legal
        else "Routing wygląda stabilnie; kolejny krok to poprawa coverage workflow seed dla mixed_expected."
    )

    return {
        "records_evaluated": len(results),
        "subset_counts": dict(subset_counts),
        "metrics": {
            "workflow_path_precision": _safe_ratio(workflow_correct_hits, workflow_path_total),
            "legal_path_precision": _safe_ratio(legal_correct_hits, legal_path_total),
            "workflow_recall_on_workflow_questions": _safe_ratio(
                sum(
                    1
                    for result in results
                    if result["subset"] == "workflow_expected" and result["selected_path"] == "workflow"
                ),
                workflow_expected_total,
            ),
            "legal_leakage_into_workflow": _safe_ratio(
                sum(
                    1
                    for result in results
                    if result["subset"] == "legal_expected" and result["selected_path"] == "workflow"
                ),
                legal_expected_total,
            ),
            "workflow_leakage_into_legal": _safe_ratio(
                sum(
                    1
                    for result in results
                    if result["subset"] == "workflow_expected" and result["selected_path"] == "legal"
                ),
                workflow_expected_total,
            ),
            "clarification_rate_per_subset": clarification_by_subset,
        },
        "error_analysis": {
            "top_workflow_questions_incorrectly_went_to_legal": failures_workflow_to_legal[:10],
            "top_legal_questions_incorrectly_went_to_workflow": failures_legal_to_workflow[:10],
            "top_mixed_questions_with_weak_routing": mixed_weak_routing[:10],
            "top_workflow_areas_with_strongest_retrieval_confidence": strongest_workflow_areas[:10],
            "top_workflow_areas_with_weakest_retrieval_confidence": list(reversed(strongest_workflow_areas[-10:])),
        },
        "recommendation": recommendation,
    }


def render_workflow_eval_markdown(report: JSONDict) -> str:
    """Render the workflow evaluation report as compact markdown."""

    metrics = report["metrics"]
    lines = [
        "# Workflow Evaluation Report",
        "",
        f"- Records evaluated: {report['records_evaluated']}",
        f"- workflow_expected: {report['subset_counts'].get('workflow_expected', 0)}",
        f"- legal_expected: {report['subset_counts'].get('legal_expected', 0)}",
        f"- mixed_expected: {report['subset_counts'].get('mixed_expected', 0)}",
        "",
        "## Core metrics",
        "",
        f"- workflow_path_precision: {metrics['workflow_path_precision']}",
        f"- legal_path_precision: {metrics['legal_path_precision']}",
        f"- workflow_recall_on_workflow_questions: {metrics['workflow_recall_on_workflow_questions']}",
        f"- legal_leakage_into_workflow: {metrics['legal_leakage_into_workflow']}",
        f"- workflow_leakage_into_legal: {metrics['workflow_leakage_into_legal']}",
        "",
        "## Clarification rate per subset",
        "",
        "| Subset | Clarification rate |",
        "|---|---:|",
    ]
    for subset in SUBSET_NAMES:
        lines.append(f"| {subset} | {metrics['clarification_rate_per_subset'].get(subset, 0.0)} |")

    lines.extend(["", "## Top routing failures", ""])
    failure_sections = [
        ("Workflow -> legal", report["error_analysis"]["top_workflow_questions_incorrectly_went_to_legal"]),
        ("Legal -> workflow", report["error_analysis"]["top_legal_questions_incorrectly_went_to_workflow"]),
        ("Mixed weak routing", report["error_analysis"]["top_mixed_questions_with_weak_routing"]),
    ]
    for title, items in failure_sections:
        lines.append(f"### {title}")
        if not items:
            lines.append("")
            lines.append("- none")
            lines.append("")
            continue
        lines.append("")
        for item in items[:10]:
            lines.append(
                f"- `{item['selected_path']}` | freq={item['source_frequency']} | {item['question']}"
            )
        lines.append("")

    lines.extend(["## Strongest workflow areas", ""])
    for item in report["error_analysis"]["top_workflow_areas_with_strongest_retrieval_confidence"][:5]:
        lines.append(f"- {item['workflow_area']} — avg_score={item['avg_score']} ({item['count']} queries)")

    lines.extend(["", "## Weakest workflow areas", ""])
    for item in report["error_analysis"]["top_workflow_areas_with_weakest_retrieval_confidence"][:5]:
        lines.append(f"- {item['workflow_area']} — avg_score={item['avg_score']} ({item['count']} queries)")

    lines.extend(["", "## Recommendation", "", report["recommendation"], ""])
    return "\n".join(lines)


def write_json(path: Path, payload: Any) -> None:
    """Write JSON with stable UTF-8 formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run_workflow_eval(
    workflow_split_path: Path = WORKFLOW_SPLIT_PATH,
    golden_eval_path: Path = GOLDEN_EVAL_PATH,
    workflow_seed_path: Path = WORKFLOW_SEED_PATH,
    legal_knowledge_path: Path = LEGAL_KNOWLEDGE_PATH,
    report_json_path: Path = REPORT_JSON_PATH,
    report_md_path: Path = REPORT_MD_PATH,
    limit_per_subset: int = DEFAULT_LIMIT_PER_SUBSET,
) -> JSONDict:
    """Execute the workflow evaluation harness and write both reports."""

    records = load_eval_records(workflow_split_path, golden_eval_path, limit_per_subset=limit_per_subset)
    results = [
        evaluate_record(record, legal_knowledge_path=legal_knowledge_path, workflow_seed_path=workflow_seed_path)
        for record in records
    ]
    report = build_workflow_eval_report(results)
    write_json(report_json_path, report)
    report_md_path.write_text(render_workflow_eval_markdown(report), encoding="utf-8")
    return report


def main() -> None:
    """CLI entrypoint for workflow routing evaluation."""

    parser = argparse.ArgumentParser(description="Run workflow retrieval and routing evaluation.")
    parser.add_argument("--limit-per-subset", type=int, default=DEFAULT_LIMIT_PER_SUBSET)
    args = parser.parse_args()
    report = run_workflow_eval(limit_per_subset=args.limit_per_subset)
    print(f"Records evaluated: {report['records_evaluated']}")
    print(f"Workflow precision: {report['metrics']['workflow_path_precision']}")
    print(f"Legal precision: {report['metrics']['legal_path_precision']}")


if __name__ == "__main__":
    main()
