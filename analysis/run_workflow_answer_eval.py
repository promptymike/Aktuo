from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import core.rag as rag_module
from core.rag import RagResult, answer_query
from core.retriever import LawChunk

WORKFLOW_SEED_PATH = ROOT / "data" / "workflow" / "workflow_seed.json"
WORKFLOW_SPLIT_PATH = ROOT / "data" / "curated" / "workflow_vs_legal_vs_out_of_scope.jsonl"
GOLDEN_EVAL_PATH = ROOT / "data" / "curated" / "golden_eval_set.jsonl"
LEGAL_KNOWLEDGE_PATH = ROOT / "data" / "seeds" / "law_knowledge.json"
REPORT_JSON_PATH = ROOT / "analysis" / "workflow_answer_eval_report.json"
REPORT_MD_PATH = ROOT / "analysis" / "workflow_answer_eval_report.md"

JSONDict = dict[str, Any]
WORKFLOW_HEADERS = (
    "Krótko",
    "Co zrób teraz",
    "Jakie dane / dokumenty będą potrzebne",
    "Na co uważać",
    "Powiązane formularze / systemy",
)
SUBSET_NAMES = (
    "workflow_answer_expected",
    "legal_answer_expected",
    "legal_fallback_expected",
)
DEFAULT_LIMIT_PER_SUBSET = 150


@dataclass(slots=True)
class WorkflowAnswerEvalCase:
    """One deterministic evaluation case for workflow answer quality checks."""

    question: str
    normalized_question: str
    subset: str
    classification: str
    primary_intent: str
    expected_behavior: str
    expected_law_or_area: str
    expected_source_type: str
    source_category: str
    source_frequency: int
    needs_clarification: bool
    golden_overlap: bool


def normalize_text(value: str) -> str:
    """Normalize text for deterministic matching and ordering."""

    normalized = unicodedata.normalize("NFKD", value.lower())
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_value.split())


def read_jsonl(path: Path) -> list[JSONDict]:
    """Load JSONL rows from a file."""

    rows: list[JSONDict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def classify_subset(record: JSONDict) -> str | None:
    """Map a curated record into one answer-quality subset.

    Rules:
    - workflow_answer_expected: curated workflow questions expected to draw from workflow KB
    - legal_answer_expected: curated legal questions expected to stay on legal KB
    - legal_fallback_expected: curated mixed questions where workflow-like phrasing may appear,
      but a legal answer or safe legal fallback is acceptable
    """

    classification = str(record.get("classification", "")).strip()
    expected_source_type = str(record.get("expected_source_type", "")).strip()

    if classification == "workflow" and expected_source_type == "workflow_kb":
        return "workflow_answer_expected"
    if classification == "legal" and expected_source_type == "legal_kb":
        return "legal_answer_expected"
    if classification == "mixed" or expected_source_type == "mixed":
        return "legal_fallback_expected"
    return None


def load_eval_cases(
    workflow_split_path: Path = WORKFLOW_SPLIT_PATH,
    golden_eval_path: Path = GOLDEN_EVAL_PATH,
    limit_per_subset: int = DEFAULT_LIMIT_PER_SUBSET,
) -> list[WorkflowAnswerEvalCase]:
    """Load deterministic answer-eval cases from curated datasets."""

    workflow_rows = read_jsonl(workflow_split_path)
    golden_rows = read_jsonl(golden_eval_path)
    golden_by_question = {
        normalize_text(str(row.get("question", ""))): row for row in golden_rows if row.get("question")
    }

    merged: dict[tuple[str, str], WorkflowAnswerEvalCase] = {}
    for source_rows in (workflow_rows, golden_rows):
        for row in source_rows:
            subset = classify_subset(row)
            if subset is None:
                continue

            question = str(row.get("question", "")).strip()
            if not question:
                continue

            normalized_question = normalize_text(question)
            golden_match = golden_by_question.get(normalized_question)
            candidate = WorkflowAnswerEvalCase(
                question=question,
                normalized_question=normalized_question,
                subset=subset,
                classification=str(row.get("classification", "")).strip(),
                primary_intent=str(row.get("primary_intent", "")).strip(),
                expected_behavior=str(row.get("expected_behavior", "")).strip(),
                expected_law_or_area=str(row.get("expected_law_or_area", "")).strip(),
                expected_source_type=str(row.get("expected_source_type", "")).strip(),
                source_category=str(row.get("source_category", "")).strip(),
                source_frequency=int(row.get("source_frequency", 1) or 1),
                needs_clarification=bool(row.get("needs_clarification", False)),
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

    selected: list[WorkflowAnswerEvalCase] = []
    for subset in SUBSET_NAMES:
        subset_cases = sorted(
            (case for case in merged.values() if case.subset == subset),
            key=lambda case: (
                not case.golden_overlap,
                -case.source_frequency,
                case.question,
            ),
        )
        selected.extend(subset_cases[:limit_per_subset])
    return selected


def _legal_answer_preview(
    query: str,
    chunks: list[LawChunk],
    system_prompt: str,
    api_key: str,
) -> str:
    """Build a deterministic legal-answer preview without external API calls."""

    del query, system_prompt, api_key
    if not chunks:
        return "insufficient data"

    top_chunk = chunks[0]
    snippet = " ".join(top_chunk.content.split())[:280].strip()
    return (
        f"Odpowiedź prawna oparta na dostępnym kontekście: {snippet}\n\n"
        f"Podstawa prawna:\n- {top_chunk.law_name}, {top_chunk.article_number}"
    )


@contextmanager
def legal_answer_preview_mode() -> Iterator[None]:
    """Temporarily disable external legal generation for deterministic evaluation."""

    original_generate_answer = rag_module.generate_answer
    original_max_context_tokens = rag_module.MAX_CONTEXT_TOKENS
    rag_module.generate_answer = _legal_answer_preview
    rag_module.MAX_CONTEXT_TOKENS = 1_000_000
    try:
        yield
    finally:
        rag_module.generate_answer = original_generate_answer
        rag_module.MAX_CONTEXT_TOKENS = original_max_context_tokens


def extract_answer_sections(answer: str) -> list[str]:
    """Return workflow section headers present in the answer text."""

    return [
        header
        for header in WORKFLOW_HEADERS
        if f"**{header}**" in answer or answer.startswith(f"{header}\n")
    ]


def _top_chunk_metadata(chunk: LawChunk | None) -> JSONDict | None:
    """Serialize top chunk metadata for reports."""

    if chunk is None:
        return None
    return {
        "law_name": chunk.law_name,
        "article_number": chunk.article_number,
        "category": chunk.category,
        "score": round(float(chunk.score), 4),
        "source_type": chunk.source_type,
        "workflow_area": chunk.workflow_area,
        "title": chunk.title,
    }


def _available_workflow_sections(chunk: LawChunk | None) -> list[str]:
    """List workflow sections that the top workflow chunk can legitimately support."""

    if chunk is None or not chunk.source_type.startswith("workflow"):
        return []

    available = ["Krótko"]
    if chunk.workflow_steps:
        available.append("Co zrób teraz")
    if chunk.workflow_required_inputs:
        available.append("Jakie dane / dokumenty będą potrzebne")
    if chunk.workflow_common_pitfalls:
        available.append("Na co uważać")
    if chunk.workflow_related_forms or chunk.workflow_related_systems:
        available.append("Powiązane formularze / systemy")
    return available


def evaluate_case(
    case: WorkflowAnswerEvalCase,
    *,
    knowledge_path: Path = LEGAL_KNOWLEDGE_PATH,
    system_prompt: str = "Eval preview only.",
    api_key: str = "eval-key",
) -> JSONDict:
    """Run one end-to-end answer-quality evaluation case without external APIs."""

    with legal_answer_preview_mode():
        result = answer_query(
            query=case.question,
            knowledge_path=knowledge_path,
            system_prompt=system_prompt,
            api_key=api_key,
        )

    top_chunk = result.chunks[0] if result.chunks else None
    sections_present = extract_answer_sections(result.answer)
    workflow_available_sections = _available_workflow_sections(top_chunk)
    invented_sections = [
        section for section in sections_present if section not in workflow_available_sections
    ]
    sparse_workflow_unit = bool(
        top_chunk
        and top_chunk.source_type.startswith("workflow")
        and len(workflow_available_sections) <= 2
    )
    workflow_formatted = bool(sections_present)

    return {
        "question": case.question,
        "subset": case.subset,
        "classification": case.classification,
        "source_category": case.source_category,
        "source_frequency": case.source_frequency,
        "expected_behavior": case.expected_behavior,
        "expected_law_or_area": case.expected_law_or_area,
        "expected_source_type": case.expected_source_type,
        "predicted_intent": result.category,
        "needs_clarification": result.needs_clarification,
        "missing_slots": list(result.missing_slots or []),
        "retrieval_path": result.retrieval_path,
        "top_chunk": _top_chunk_metadata(top_chunk),
        "answer": result.answer,
        "answer_sections": sections_present,
        "workflow_formatted": workflow_formatted,
        "available_workflow_sections": workflow_available_sections,
        "invented_sections": invented_sections,
        "sparse_workflow_unit": sparse_workflow_unit,
        "sparse_workflow_safe": sparse_workflow_unit and not invented_sections,
        "operational_answer": workflow_formatted and "Co zrób teraz" in sections_present,
        "legal_style_answer": "Podstawa prawna:" in result.answer and not workflow_formatted,
    }


def _safe_ratio(numerator: int, denominator: int) -> float:
    """Return a rounded ratio while avoiding division by zero."""

    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def build_workflow_answer_report(results: list[JSONDict]) -> JSONDict:
    """Aggregate workflow answer-quality and legal-safety metrics."""

    subset_counts = Counter(result["subset"] for result in results)
    workflow_results = [result for result in results if result["subset"] == "workflow_answer_expected"]
    legal_results = [result for result in results if result["subset"] == "legal_answer_expected"]
    fallback_results = [result for result in results if result["subset"] == "legal_fallback_expected"]

    workflow_hits = [result for result in workflow_results if result["retrieval_path"] == "workflow"]
    workflow_non_clarified_hits = [result for result in workflow_hits if not result["needs_clarification"]]
    sparse_workflow_results = [result for result in workflow_hits if result["sparse_workflow_unit"]]
    legal_safety_pool = legal_results + fallback_results

    section_completeness_scores = [
        _safe_ratio(len(result["answer_sections"]), len(result["available_workflow_sections"]))
        for result in workflow_non_clarified_hits
        if result["available_workflow_sections"]
    ]
    workflow_section_completeness = round(
        sum(section_completeness_scores) / len(section_completeness_scores),
        4,
    ) if section_completeness_scores else 0.0

    weak_workflow_answers = sorted(
        (
            result for result in workflow_results
            if result["retrieval_path"] != "workflow"
            or result["needs_clarification"]
            or not result["workflow_formatted"]
            or bool(result["invented_sections"])
            or not result["operational_answer"]
        ),
        key=lambda result: (-result["source_frequency"], result["question"]),
    )
    formatting_misses = sorted(
        (
            result for result in workflow_results
            if result["retrieval_path"] == "workflow" and not result["workflow_formatted"]
        ),
        key=lambda result: (-result["source_frequency"], result["question"]),
    )
    safe_fallbacks = sorted(
        (
            result for result in fallback_results
            if result["retrieval_path"] in {"legal", "legal_fallback"}
            and not result["workflow_formatted"]
        ),
        key=lambda result: (-result["source_frequency"], result["question"]),
    )
    sparse_workflow_answers = sorted(
        sparse_workflow_results,
        key=lambda result: (-result["source_frequency"], result["question"]),
    )

    sparse_titles = Counter(
        (result["top_chunk"] or {}).get("title", "")
        for result in sparse_workflow_answers
        if result.get("top_chunk")
    )
    top_sparse_titles = [
        {"title": title, "count": count}
        for title, count in sparse_titles.most_common(5)
        if title
    ]

    recommendation = (
        "enrich workflow seed"
        if weak_workflow_answers or sparse_workflow_answers
        else "move to UI rendering"
    )

    return {
        "records_evaluated": len(results),
        "subset_counts": dict(subset_counts),
        "subset_rules": {
            "workflow_answer_expected": (
                "classification=workflow and expected_source_type=workflow_kb"
            ),
            "legal_answer_expected": (
                "classification=legal and expected_source_type=legal_kb"
            ),
            "legal_fallback_expected": (
                "classification=mixed or expected_source_type=mixed"
            ),
        },
        "metrics": {
            "workflow_format_rate": _safe_ratio(
                sum(1 for result in workflow_non_clarified_hits if result["workflow_formatted"]),
                len(workflow_non_clarified_hits),
            ),
            "workflow_section_completeness": workflow_section_completeness,
            "sparse_unit_safety_rate": _safe_ratio(
                sum(1 for result in sparse_workflow_results if result["sparse_workflow_safe"]),
                len(sparse_workflow_results),
            ),
            "legal_path_contamination_rate": _safe_ratio(
                sum(1 for result in legal_safety_pool if result["workflow_formatted"]),
                len(legal_safety_pool),
            ),
            "workflow_fallback_safety_rate": _safe_ratio(
                sum(
                    1
                    for result in fallback_results
                    if result["retrieval_path"] in {"legal", "legal_fallback"} and not result["workflow_formatted"]
                ),
                len(fallback_results),
            ),
            "workflow_clarification_rate": _safe_ratio(
                sum(1 for result in workflow_results if result["needs_clarification"]),
                len(workflow_results),
            ),
            "legal_safety_rate": _safe_ratio(
                sum(1 for result in legal_results if not result["workflow_formatted"]),
                len(legal_results),
            ),
        },
        "error_analysis": {
            "top_weak_workflow_answers": weak_workflow_answers[:10],
            "top_missing_workflow_formatting": formatting_misses[:10],
            "top_safe_legal_fallbacks": safe_fallbacks[:10],
            "top_sparse_workflow_units": sparse_workflow_answers[:10],
            "workflow_units_to_enrich_first": top_sparse_titles,
        },
        "recommendation": recommendation,
        "records": results,
    }


def _render_markdown(report: JSONDict) -> str:
    """Build a human-readable markdown report."""

    metrics = report["metrics"]
    lines = [
        "# Workflow Answer Quality Evaluation",
        "",
        f"- Records evaluated: {report['records_evaluated']}",
        f"- Workflow answer expected: {report['subset_counts'].get('workflow_answer_expected', 0)}",
        f"- Legal answer expected: {report['subset_counts'].get('legal_answer_expected', 0)}",
        f"- Legal fallback expected: {report['subset_counts'].get('legal_fallback_expected', 0)}",
        "",
        "## Metrics",
        "",
        f"- workflow_format_rate: {metrics['workflow_format_rate']}",
        f"- workflow_section_completeness: {metrics['workflow_section_completeness']}",
        f"- sparse_unit_safety_rate: {metrics['sparse_unit_safety_rate']}",
        f"- legal_path_contamination_rate: {metrics['legal_path_contamination_rate']}",
        f"- workflow_fallback_safety_rate: {metrics['workflow_fallback_safety_rate']}",
        f"- workflow_clarification_rate: {metrics['workflow_clarification_rate']}",
        f"- legal_safety_rate: {metrics['legal_safety_rate']}",
        "",
        "## Top Weak Workflow Answers",
        "",
    ]

    weak_answers = report["error_analysis"]["top_weak_workflow_answers"]
    if not weak_answers:
        lines.append("- none")
    else:
        for result in weak_answers[:10]:
            lines.append(
                f"- {result['question']} | path={result['retrieval_path']} | "
                f"sections={', '.join(result['answer_sections']) or 'none'}"
            )

    lines.extend(
        [
            "",
            "## Top Cases Where Workflow Formatting Should Have Happened But Did Not",
            "",
        ]
    )
    formatting_misses = report["error_analysis"]["top_missing_workflow_formatting"]
    if not formatting_misses:
        lines.append("- none")
    else:
        for result in formatting_misses[:10]:
            lines.append(f"- {result['question']} | path={result['retrieval_path']}")

    lines.extend(
        [
            "",
            "## Top Safe Legal Fallback Cases",
            "",
        ]
    )
    safe_fallbacks = report["error_analysis"]["top_safe_legal_fallbacks"]
    if not safe_fallbacks:
        lines.append("- none")
    else:
        for result in safe_fallbacks[:10]:
            lines.append(f"- {result['question']} | path={result['retrieval_path']}")

    lines.extend(
        [
            "",
            "## Sparse Workflow Units To Enrich First",
            "",
        ]
    )
    enrich_first = report["error_analysis"]["workflow_units_to_enrich_first"]
    if not enrich_first:
        lines.append("- none")
    else:
        for item in enrich_first:
            lines.append(f"- {item['title']} ({item['count']})")

    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            f"- {report['recommendation']}",
        ]
    )
    return "\n".join(lines) + "\n"


def write_report_json(report: JSONDict, path: Path = REPORT_JSON_PATH) -> Path:
    """Write deterministic JSON report to disk."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_report_markdown(report: JSONDict, path: Path = REPORT_MD_PATH) -> Path:
    """Write markdown summary report to disk."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(report), encoding="utf-8")
    return path


def run_workflow_answer_eval(
    *,
    workflow_seed_path: Path = WORKFLOW_SEED_PATH,
    workflow_split_path: Path = WORKFLOW_SPLIT_PATH,
    golden_eval_path: Path = GOLDEN_EVAL_PATH,
    legal_knowledge_path: Path = LEGAL_KNOWLEDGE_PATH,
    report_json_path: Path = REPORT_JSON_PATH,
    report_md_path: Path = REPORT_MD_PATH,
    limit_per_subset: int = DEFAULT_LIMIT_PER_SUBSET,
) -> JSONDict:
    """Run the workflow answer quality harness and persist both reports."""

    del workflow_seed_path  # The current pipeline loads workflow seed via application settings.
    cases = load_eval_cases(
        workflow_split_path=workflow_split_path,
        golden_eval_path=golden_eval_path,
        limit_per_subset=limit_per_subset,
    )
    results = [
        evaluate_case(case, knowledge_path=legal_knowledge_path)
        for case in cases
    ]
    report = build_workflow_answer_report(results)
    write_report_json(report, report_json_path)
    write_report_markdown(report, report_md_path)
    return report


def main() -> None:
    """CLI entry point for workflow answer quality evaluation."""

    parser = argparse.ArgumentParser(description="Run workflow answer quality evaluation.")
    parser.add_argument("--limit-per-subset", type=int, default=DEFAULT_LIMIT_PER_SUBSET)
    args = parser.parse_args()

    report = run_workflow_answer_eval(limit_per_subset=args.limit_per_subset)
    print(json.dumps(report["metrics"], ensure_ascii=False))


if __name__ == "__main__":
    main()
