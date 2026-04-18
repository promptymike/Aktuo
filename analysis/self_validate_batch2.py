"""Self-validation layer for batch 2 workflow drafts (Haiku 4.5).

Same critique logic as batch 1 but:
  - Only processes drafts that do NOT yet have ``self_critique`` (i.e.
    batch 2 newly generated) to avoid re-validating batch 1.
  - Writes to ``analysis/batch2_self_validation_report.md``.
  - Hard cost cap $3.00.

Run:
    .venv/Scripts/python -u -X utf8 analysis/self_validate_batch2.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.self_validate_batch1 import (  # noqa: E402
    MODEL,
    PRICE_INPUT_PER_1K,
    PRICE_OUTPUT_PER_1K,
    RATE_LIMIT_DELAY_S,
    SYSTEM_PROMPT,
    TODAY_ISO,
    _load_env,
    _normalize_status,
    critique_draft,
)

DRAFTS_DIR = ROOT / "data" / "workflow_drafts"
REPORT_PATH = ROOT / "analysis" / "batch2_self_validation_report.md"
COST_CAP = 3.00


def _build_report(results: list[dict], total_cost: float) -> str:
    n = len(results)
    clean = sum(1 for r in results if r["status"] == "clean")
    flagged = sum(1 for r in results if r["status"] == "flagged_for_review")
    major = sum(1 for r in results if r["status"] == "needs_major_revision")
    sev = {"high": 0, "medium": 0, "low": 0}
    types: dict[str, int] = {}
    for r in results:
        for iss in r["issues"]:
            s = (iss.get("severity") or "").lower()
            if s in sev:
                sev[s] += 1
            t = (iss.get("type") or "").strip()
            if t:
                types[t] = types.get(t, 0) + 1
    ranked = sorted(
        results,
        key=lambda r: (
            {"needs_major_revision": 0, "flagged_for_review": 1, "clean": 2}[r["status"]],
            -len(r["issues"]),
            r["confidence_score"],
        ),
    )
    top3 = ranked[:3]
    lines: list[str] = []
    lines.append("# Batch 2 Self-Validation Report")
    lines.append("")
    lines.append(f"Data: {TODAY_ISO}")
    lines.append(f"Model: {MODEL}")
    lines.append(f"Drafts processed: {n}")
    lines.append(f"Koszt: ${total_cost:.4f} (cap ${COST_CAP:.2f})")
    lines.append("")
    lines.append("## Statusy")
    lines.append(f"- clean: {clean}/{n}")
    lines.append(f"- flagged_for_review: {flagged}/{n}")
    lines.append(f"- needs_major_revision: {major}/{n}")
    lines.append("")
    lines.append("## Severity")
    lines.append(f"- high: {sev['high']}  medium: {sev['medium']}  low: {sev['low']}")
    lines.append("")
    lines.append("## Top 3 najsłabsze")
    for r in top3:
        lines.append(f"- {r['draft_id']} — {len(r['issues'])} issues — conf {r['confidence_score']:.2f} — `{r['status']}`")
    lines.append("")
    lines.append("## Kategorie flag")
    if types:
        for t, c in sorted(types.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"- {t}: {c}")
    else:
        lines.append("- (brak flag)")
    lines.append("")
    lines.append("## Per draft")
    for r in results:
        lines.append(f"### {r['draft_id']}")
        lines.append(f"- Topic: {r['topic_area']}  |  cluster: {r['cluster_id']}")
        lines.append(f"- Status: `{r['status']}`  conf: {r['confidence_score']:.2f}")
        lines.append(f"- Assessment: {r['general_assessment']}")
        if r["issues"]:
            lines.append("- Issues:")
            for iss in r["issues"]:
                lines.append(f"  - [{(iss.get('severity') or '').upper()}] {iss.get('type', '?')}: {iss.get('description', '')}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    _load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERR: ANTHROPIC_API_KEY not set", flush=True)
        return 2

    import anthropic

    client = anthropic.Anthropic(timeout=120.0)
    draft_files = sorted(DRAFTS_DIR.glob("wf_*.json"))
    to_process: list[tuple[Path, dict]] = []
    for p in draft_files:
        d = json.loads(p.read_text(encoding="utf-8"))
        if "self_critique" in d and d["self_critique"]:
            continue
        to_process.append((p, d))
    print(f"Batch 2 candidates (no self_critique): {len(to_process)}/{len(draft_files)}", flush=True)
    if not to_process:
        print("nothing to do", flush=True)
        return 0

    results: list[dict] = []
    total_in = 0
    total_out = 0

    for i, (path, draft) in enumerate(to_process, 1):
        did = draft.get("id", path.stem)
        print(f"[{i}/{len(to_process)}] {did}", flush=True)

        t0 = time.time()
        try:
            critique, in_tok, out_tok = critique_draft(client, draft)
        except Exception as exc:
            print(f"  FAILED: {exc}", flush=True)
            continue
        dt = time.time() - t0
        total_in += in_tok
        total_out += out_tok

        status = _normalize_status(critique.get("status", ""))
        issues = critique.get("issues") or []
        if not isinstance(issues, list):
            issues = []
        confidence = float(critique.get("confidence_score") or 0.0)
        assessment = (critique.get("general_assessment") or "").strip()

        draft["self_critique"] = {
            "validated_by": MODEL,
            "validated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": status,
            "confidence_score": confidence,
            "general_assessment": assessment,
            "issues": issues,
        }
        path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")

        results.append({
            "draft_id": did,
            "title": draft.get("title", ""),
            "topic_area": draft.get("topic_area", ""),
            "cluster_id": draft.get("generation_metadata", {}).get("cluster_id", ""),
            "status": status,
            "confidence_score": confidence,
            "general_assessment": assessment,
            "issues": issues,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "elapsed_s": round(dt, 2),
        })
        cost_so_far = total_in / 1000 * PRICE_INPUT_PER_1K + total_out / 1000 * PRICE_OUTPUT_PER_1K
        print(f"  status={status}  issues={len(issues)}  conf={confidence:.2f}  cost=${cost_so_far:.4f}", flush=True)
        if cost_so_far >= COST_CAP:
            print(f"  COST CAP hit (${cost_so_far:.4f} ≥ ${COST_CAP:.2f}) — stopping", flush=True)
            break
        time.sleep(RATE_LIMIT_DELAY_S)

    total_cost = total_in / 1000 * PRICE_INPUT_PER_1K + total_out / 1000 * PRICE_OUTPUT_PER_1K
    REPORT_PATH.write_text(_build_report(results, total_cost), encoding="utf-8")
    print(f"\nDone. in={total_in} out={total_out} cost=${total_cost:.4f}", flush=True)
    print(f"Report: {REPORT_PATH}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
