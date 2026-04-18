"""Retag unresolved self_critique flags as community_feedback_needed.

After verifier v1 + verifier v2 (web), a portion of flags remain unresolved
(cannot_verify for v1 and not processed in v2 due to cost cap, or still
cannot_verify after v2). Those flags aren't evidence the draft is wrong —
only that our automatic tooling couldn't verify. We surface them in the
UI as "fragment needs human review" and collect community feedback there.

Criteria for tagging a flag as community_feedback_needed:
  - verdict == "cannot_verify" AND verdict_v2 is None (not processed in v2)
  - verdict_v2 in {"cannot_verify", "still_cannot_verify"} (v2 also uncertain)

We do NOT touch:
  - verdict == "confirmed" / "false_positive" (v1 resolved)
  - verdict_v2 == "confirmed" / "false_positive" (v2 resolved)

Idempotent — running twice produces the same output.
No LLM calls. Cost: $0.
"""
from __future__ import annotations

import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = ROOT / "data" / "workflow_drafts"
REPORT_PATH = ROOT / "analysis" / "batch1_community_feedback_summary.md"

UI_LABELS: dict[str, str] = {
    "legal_anchor_uncertainty": "Weryfikuję artykuł ustawy",
    "outdated_data_risk": "Sprawdź aktualność danych",
    "step_contradiction": "Niepewność w kolejności kroków",
    "missing_critical_info": "Możliwe brakujące informacje",
    "hallucination_risk": "Wymaga weryfikacji źródła",
    "edge_case_coverage": "Nietypowy przypadek - sprawdź",
}
DEFAULT_UI_LABEL = "Fragment wymaga weryfikacji"

UNRESOLVED_V2 = {"cannot_verify", "still_cannot_verify"}


def _needs_community_feedback(flag: dict) -> bool:
    v1 = flag.get("verdict")
    v2 = flag.get("verdict_v2")
    if v2 in UNRESOLVED_V2:
        return True
    if v1 == "cannot_verify" and v2 is None:
        return True
    return False


def _ui_label(flag_type: str) -> str:
    return UI_LABELS.get(flag_type, DEFAULT_UI_LABEL)


def process_draft(path: Path) -> dict:
    """Mutate draft in place. Returns per-draft stats dict."""
    draft = json.loads(path.read_text(encoding="utf-8"))
    issues = (draft.get("self_critique") or {}).get("issues") or []

    confirmed = 0
    false_pos = 0
    community = 0
    by_type: collections.Counter[str] = collections.Counter()
    by_severity: collections.Counter[str] = collections.Counter()

    for flag in issues:
        v1 = flag.get("verdict")
        v2 = flag.get("verdict_v2")

        # Resolved states — don't tag, count for report.
        if v2 == "confirmed" or (v1 == "confirmed" and v2 is None):
            confirmed += 1
            # Scrub stale final_status from earlier runs if criteria changed.
            flag.pop("final_status", None)
            flag.pop("ui_label", None)
            continue
        if v2 == "false_positive" or (v1 == "false_positive" and v2 is None):
            false_pos += 1
            flag.pop("final_status", None)
            flag.pop("ui_label", None)
            continue

        if _needs_community_feedback(flag):
            flag["final_status"] = "community_feedback_needed"
            flag["ui_label"] = _ui_label(flag.get("type", ""))
            community += 1
            by_type[flag.get("type", "unknown")] += 1
            by_severity[flag.get("severity", "unknown")] += 1
        else:
            # Unknown state — don't tag, but don't carry stale label.
            flag.pop("final_status", None)
            flag.pop("ui_label", None)

    # Draft-level summary
    if community:
        draft["community_feedback_summary"] = {
            "total_flags": community,
            "by_type": dict(by_type),
            "severity_breakdown": dict(by_severity),
        }
    else:
        draft.pop("community_feedback_summary", None)

    path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "draft_id": draft.get("id") or path.stem,
        "confirmed": confirmed,
        "false_positive": false_pos,
        "community_feedback": community,
        "total_flags": len(issues),
        "by_type": dict(by_type),
        "by_severity": dict(by_severity),
    }


def _write_report(per_draft: list[dict]) -> None:
    total_cf = sum(d["community_feedback"] for d in per_draft)
    agg_type: collections.Counter[str] = collections.Counter()
    agg_sev: collections.Counter[str] = collections.Counter()
    for d in per_draft:
        for k, v in d["by_type"].items():
            agg_type[k] += v
        for k, v in d["by_severity"].items():
            agg_sev[k] += v

    lines: list[str] = []
    lines.append("# Batch 1 Community Feedback Needed Summary")
    lines.append("")
    lines.append(f"Total community_feedback_needed flags: **{total_cf}** (oczekiwane ~64)")
    lines.append(f"Drafts touched: {sum(1 for d in per_draft if d['community_feedback'])}/{len(per_draft)}")
    lines.append("")
    lines.append("## By type")
    lines.append("| Type | Count |")
    lines.append("|---|---|")
    for t, n in sorted(agg_type.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {t} | {n} |")
    lines.append("")
    lines.append("## By severity")
    lines.append("| Severity | Count |")
    lines.append("|---|---|")
    for s, n in sorted(agg_sev.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {s} | {n} |")
    lines.append("")
    lines.append("## Per draft")
    lines.append("| Draft | Confirmed | False_pos | Community_feedback | Total flags |")
    lines.append("|---|---|---|---|---|")
    for d in sorted(per_draft, key=lambda x: -x["community_feedback"]):
        lines.append(
            f"| {d['draft_id']} | {d['confirmed']} | {d['false_positive']} "
            f"| {d['community_feedback']} | {d['total_flags']} |"
        )
    lines.append("")
    lines.append("## UI implications")
    lines.append("")
    top3_uncertain = sorted(per_draft, key=lambda x: -x["community_feedback"])[:3]
    lines.append("**Najwięcej uncertainty (intensity disclaimera w UI):**")
    for d in top3_uncertain:
        if d["community_feedback"] == 0:
            continue
        pct = d["community_feedback"] / max(1, d["total_flags"]) * 100
        lines.append(
            f"- `{d['draft_id']}` — {d['community_feedback']} flag "
            f"({pct:.0f}% wszystkich flag tego draftu)"
        )
    lines.append("")
    clean = [d for d in per_draft if d["community_feedback"] == 0]
    if clean:
        lines.append("**Drafty bez community_feedback_needed (pełna automatyczna weryfikacja):**")
        for d in clean:
            lines.append(f"- `{d['draft_id']}`")
        lines.append("")
    lines.append("**Dominujące typy flag (feedback UX categories):**")
    for t, n in sorted(agg_type.items(), key=lambda kv: -kv[1])[:3]:
        label = UI_LABELS.get(t, DEFAULT_UI_LABEL)
        lines.append(f"- `{t}` — {n} flag → label: \"{label}\"")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    paths = sorted(DRAFTS_DIR.glob("wf_*.json"))
    per_draft = [process_draft(p) for p in paths]
    _write_report(per_draft)
    total_cf = sum(d["community_feedback"] for d in per_draft)
    print(f"Tagged: {total_cf} flag across {len(per_draft)} drafts")
    print(f"Report: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
