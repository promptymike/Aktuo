from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "analysis" / "workflow_eval_report.json"
OUTPUT_JSON_PATH = ROOT / "analysis" / "workflow_routing_priorities.json"
OUTPUT_MD_PATH = ROOT / "analysis" / "workflow_routing_priorities.md"

JSONDict = dict[str, Any]
GROUP_KEYS = (
    "workflow_should_have_hit_but_went_legal",
    "legal_should_have_stayed_legal_but_went_workflow",
    "weak_mixed_routing",
)


def _normalize(text: str) -> str:
    return " ".join((text or "").lower().split())


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    normalized = _normalize(text)
    return any(marker in normalized for marker in markers)


def _infer_topic(question: str, result: JSONDict) -> str:
    """Infer a compact routing-failure topic label from one failed record."""

    normalized_question = _normalize(question)
    workflow_top = result.get("workflow_top") or {}
    workflow_area = _normalize(str(workflow_top.get("workflow_area", "")))

    if _contains_any(
        normalized_question,
        ("zaksi", "ksieg", "kpir", "kśt", "kst", "konto", "kolumn", "data zapisania", "pod jaka data"),
    ) or _contains_any(
        workflow_area,
        ("kpir", "księgowanie", "magazyn", "klasyfikacja dokumentów", "okresy", "memoriał"),
    ):
        return "accounting_operational / księgowanie / KPiR / okresy"
    if _contains_any(
        normalized_question,
        ("ksef", "uprawn", "token", "dostep", "dostęp", "zaw-fa", "profil zaufany"),
    ) or _contains_any(workflow_area, ("ksef permissions", "authorization", "obieg faktur")):
        return "KSeF permissions / authorization / invoice circulation"
    if _contains_any(
        normalized_question,
        ("upl-1", "pps-1", "pełnomoc", "pelnomoc", "podpis", "e-urzad", "kanał", "kanal"),
    ) or _contains_any(workflow_area, ("pełnomocnictwa", "kanały złożenia", "podpis")):
        return "pełnomocnictwa / podpis / kanały złożenia"
    if _contains_any(
        normalized_question,
        ("infakt", "optima", "comarch", "symfonia", "enova", "pue", "e płatnik", "e-platnik"),
    ):
        return "system-name false positives"
    if _contains_any(normalized_question, ("jpk", "bfk", "di", "ro", "gtu", "oznaczen")):
        return "JPK tags / procedural-vs-legal ambiguity"
    return "other / mixed routing"


def _infer_fix_type(result: JSONDict) -> str:
    """Suggest the most likely fix type for one routing error."""

    question = _normalize(str(result.get("question", "")))
    predicted_intent = str(result.get("predicted_intent", ""))
    clarification_flag = bool(result.get("clarification_flag"))
    workflow_eligible = bool(result.get("workflow_eligible"))
    workflow_score = float(result.get("workflow_score") or 0.0)

    if clarification_flag and not workflow_eligible and workflow_score >= 6.0:
        return "clarification gate masking workflow hit"
    if not workflow_eligible and workflow_score >= 8.0:
        return "workflow eligibility issue"
    if workflow_eligible and workflow_score < 6.0:
        return "workflow confidence too low"
    if _contains_any(question, ("infakt", "optima", "comarch", "symfonia", "enova", "pue", "e-platnik", "e płatnik")):
        return "system-name false positive"
    if predicted_intent in {"pit_ryczalt", "cit_wht", "legal_substantive"} and _contains_any(
        question,
        ("zaksi", "ksieg", "kpir", "konto", "kolumn", "kśt", "kst", "data zapisania"),
    ):
        return "routing keyword issue"
    return "workflow confidence too low"


def _load_report(path: Path = REPORT_PATH) -> JSONDict:
    return json.loads(path.read_text(encoding="utf-8"))


def _group_records(records: list[JSONDict]) -> list[JSONDict]:
    """Group failed records by topic and fix type, ranked by impact."""

    grouped: dict[tuple[str, str], list[JSONDict]] = defaultdict(list)
    for record in records:
        topic = _infer_topic(str(record.get("question", "")), record)
        fix_type = _infer_fix_type(record)
        grouped[(topic, fix_type)].append(record)

    groups: list[JSONDict] = []
    for (topic, fix_type), items in grouped.items():
        total_frequency = sum(int(item.get("source_frequency", 1) or 1) for item in items)
        representative_examples = [
            {
                "question": item["question"],
                "source_frequency": item["source_frequency"],
                "predicted_intent": item["predicted_intent"],
                "selected_path": item["selected_path"],
                "workflow_score": item["workflow_score"],
            }
            for item in sorted(items, key=lambda item: (-int(item.get("source_frequency", 1) or 1), item["question"]))[:3]
        ]
        groups.append(
            {
                "topic": topic,
                "likely_fix_type": fix_type,
                "count": len(items),
                "total_frequency": total_frequency,
                "representative_examples": representative_examples,
            }
        )

    groups.sort(key=lambda item: (-item["total_frequency"], -item["count"], item["topic"], item["likely_fix_type"]))
    return groups


def build_priorities(report: JSONDict) -> JSONDict:
    """Build ranked workflow/legal routing priorities from the workflow eval report."""

    error_analysis = report.get("error_analysis", {})
    source_map = {
        "workflow_should_have_hit_but_went_legal": error_analysis.get("top_workflow_questions_incorrectly_went_to_legal", []),
        "legal_should_have_stayed_legal_but_went_workflow": error_analysis.get("top_legal_questions_incorrectly_went_to_workflow", []),
        "weak_mixed_routing": error_analysis.get("top_mixed_questions_with_weak_routing", []),
    }

    grouped_failures = {group_name: _group_records(records) for group_name, records in source_map.items()}
    fix_histogram = Counter(group["likely_fix_type"] for groups in grouped_failures.values() for group in groups)

    top_recommendations = [
        {
            "rank": index,
            "topic": group["topic"],
            "failure_group": group_name,
            "likely_fix_type": group["likely_fix_type"],
            "count": group["count"],
            "total_frequency": group["total_frequency"],
            "suggested_fix": _suggest_fix(group["topic"], group["likely_fix_type"]),
        }
        for index, (group_name, group) in enumerate(
            sorted(
                (
                    (group_name, group)
                    for group_name, groups in grouped_failures.items()
                    for group in groups
                ),
                key=lambda item: (-item[1]["total_frequency"], -item[1]["count"], item[0], item[1]["topic"]),
            ),
            start=1,
        )
    ]

    return {
        "baseline_metrics": report.get("metrics", {}),
        "failure_groups": grouped_failures,
        "fix_type_histogram": dict(sorted(fix_histogram.items())),
        "top_recommended_fixes": top_recommendations[:10],
    }


def _suggest_fix(topic: str, fix_type: str) -> str:
    """Turn a topic/fix-type pair into a concrete next-step suggestion."""

    if topic == "accounting_operational / księgowanie / KPiR / okresy":
        return "Boost accounting-operational routing for księgowanie/KPiR/date-of-entry phrases and allow workflow-first on strong bookkeeping verbs."
    if topic == "KSeF permissions / authorization / invoice circulation":
        return "Require stronger operational verbs for KSeF workflow-first, but explicitly allow uprawnienia/token flows when the query asks how to perform the action."
    if topic == "pełnomocnictwa / podpis / kanały złożenia":
        return "Route form/submission/signature questions to workflow only when they ask how to submit/sign, not when they ask whether something is legally allowed."
    if topic == "system-name false positives":
        return "Demote workflow-first when a system name appears without clear operational verbs and the query contains substantive legal markers."
    if topic == "JPK tags / procedural-vs-legal ambiguity":
        return "Keep legal-first for JPK tag/RO/BFK/DI obligation questions unless the query explicitly asks how to configure or submit them in a system."
    if fix_type == "clarification gate masking workflow hit":
        return "Reduce clarification gating for strongly operational queries so workflow retrieval can run before legal fallback."
    if fix_type == "workflow confidence too low":
        return "Increase confidence weighting for title/example overlaps on operational queries and penalize shallow collisions."
    return "Tighten routing keywords and workflow eligibility around this topic."


def render_markdown(priorities: JSONDict) -> str:
    """Render a concise markdown summary of routing priorities."""

    metrics = priorities.get("baseline_metrics", {})
    lines = [
        "# Workflow Routing Priorities",
        "",
        "## Baseline metrics",
        "",
        f"- workflow_path_precision: {metrics.get('workflow_path_precision', 0.0)}",
        f"- legal_path_precision: {metrics.get('legal_path_precision', 0.0)}",
        f"- workflow_recall_on_workflow_questions: {metrics.get('workflow_recall_on_workflow_questions', 0.0)}",
        f"- legal_leakage_into_workflow: {metrics.get('legal_leakage_into_workflow', 0.0)}",
        f"- workflow_leakage_into_legal: {metrics.get('workflow_leakage_into_legal', 0.0)}",
        "",
        "## Top recommended fixes",
        "",
        "| Rank | Failure group | Topic | Fix type | Count | Total freq | Suggested fix |",
        "|---|---|---|---|---:|---:|---|",
    ]

    for item in priorities.get("top_recommended_fixes", [])[:10]:
        lines.append(
            f"| {item['rank']} | {item['failure_group']} | {item['topic']} | {item['likely_fix_type']} | "
            f"{item['count']} | {item['total_frequency']} | {item['suggested_fix']} |"
        )

    lines.extend(["", "## Representative failure clusters", ""])
    for group_name in GROUP_KEYS:
        lines.append(f"### {group_name}")
        groups = priorities.get("failure_groups", {}).get(group_name, [])
        if not groups:
            lines.extend(["", "- none", ""])
            continue
        lines.append("")
        for group in groups[:5]:
            lines.append(
                f"- {group['topic']} ({group['likely_fix_type']}) — count={group['count']}, total_freq={group['total_frequency']}"
            )
        lines.append("")
    return "\n".join(lines)


def write_outputs(priorities: JSONDict) -> None:
    OUTPUT_JSON_PATH.write_text(json.dumps(priorities, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_MD_PATH.write_text(render_markdown(priorities), encoding="utf-8")


def main() -> None:
    report = _load_report()
    priorities = build_priorities(report)
    write_outputs(priorities)
    print(json.dumps(priorities.get("top_recommended_fixes", [])[:5], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
