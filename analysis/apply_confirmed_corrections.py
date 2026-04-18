"""Apply 22 confirmed corrections from verifier v1+v2 to batch 1 drafts.

For each flag in data/workflow_drafts/wf_*.json self_critique.issues where
verdict == 'confirmed' OR verdict_v2 == 'confirmed', call Sonnet 4.6 with the
stripped draft (self_critique elided to save tokens) + the flag + the
recommendation/source info, and overwrite the draft with the corrected JSON
(self_critique re-attached, corrections_applied log extended).

Then run pytest and write analysis/batch1_corrections_log.md.
"""

from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DRAFTS_DIR = ROOT / "data" / "workflow_drafts"
REPORT_PATH = ROOT / "analysis" / "batch1_corrections_log.md"
SNAPSHOT_DIR = ROOT / "analysis" / "_correction_snapshots"
ENV_PATH = ROOT / ".env"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 16000
TEMPERATURE = 0.1
MAX_RETRIES = 3
RATE_LIMIT_S = 1.0
PRICE_IN_PER_1K = 0.003
PRICE_OUT_PER_1K = 0.015
COST_HARD_CAP = 2.00

TODAY_ISO = "2026-04-19"
REQUIRED_FIELDS = ("id", "title", "topic_area", "answer_steps", "legal_anchors")

SYSTEM_PROMPT = """Jesteś redaktorem draftu workflow dla księgowych. Dostajesz aktualny draft + confirmed flagę + rekomendowaną korektę. Zwróć ZMODYFIKOWANY draft z punktowo naprawionym problemem. NIE zmieniaj nic poza tym co wskazuje flaga. Zachowaj strukturę JSON, wszystkie istniejące pola, metadata, self_critique. Zwróć CZYSTY JSON bez markdown bez komentarzy."""


def _load_env() -> None:
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and not os.environ.get(k):
            os.environ[k] = v


def now_iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _extract_json(text: str) -> dict[str, Any]:
    t = (text or "").strip()
    if t.startswith("```"):
        m = re.search(r"```(?:json)?\s*(.*?)```", t, re.S)
        if m:
            t = m.group(1).strip()
    try:
        return json.loads(t)
    except Exception:
        pass
    m = re.search(r"\{.*\}", t, re.S)
    if m:
        return json.loads(m.group(0))
    raise ValueError("no JSON object in response")


def _classify_flag(flag: dict[str, Any]) -> str | None:
    """Return 'v2' if verdict_v2 == 'confirmed', 'v1' if verdict == 'confirmed', else None."""
    if flag.get("verdict_v2") == "confirmed":
        return "v2"
    if flag.get("verdict") == "confirmed":
        return "v1"
    return None


def _build_user_prompt(draft_stripped: dict[str, Any], flag: dict[str, Any], source: str) -> str:
    if source == "v2":
        recommendation = (flag.get("verifier_reasoning_v2") or "").strip()
        source_url = flag.get("source_url") or ""
        source_quote = flag.get("source_quote") or ""
    else:
        recommendation = (
            flag.get("corrective_suggestion")
            or flag.get("verifier_reasoning")
            or ""
        ).strip()
        source_url = ""
        source_quote = ""
    return (
        "DRAFT (pełen JSON):\n"
        f"{json.dumps(draft_stripped, ensure_ascii=False, indent=2)}\n\n"
        "FLAGA DO POPRAWY:\n"
        f"Type: {flag.get('type')}\n"
        f"Severity: {flag.get('severity')}\n"
        f"Description: {flag.get('description')}\n"
        f"REKOMENDACJA: {recommendation}\n"
        f"SOURCE URL: {source_url}\n"
        f"SOURCE QUOTE: {source_quote}\n\n"
        "Zwróć naprawiony draft JSON."
    )


def apply_single_correction(
    client: Any,
    draft: dict[str, Any],
    flag: dict[str, Any],
    source: str,
) -> tuple[dict[str, Any], int, int]:
    """Return (new_draft_merged, input_tokens, output_tokens)."""
    self_crit = draft.get("self_critique")
    corrections_applied = draft.get("corrections_applied", [])
    stripped = {k: v for k, v in draft.items() if k != "self_critique"}

    user_msg = _build_user_prompt(stripped, flag, source)
    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            text = "".join(
                getattr(b, "text", "") for b in resp.content
                if getattr(b, "type", "") == "text"
            )
            try:
                new_draft = _extract_json(text)
            except Exception as e:
                stop_reason = getattr(resp, "stop_reason", "?")
                last_err = Exception(f"json_parse stop_reason={stop_reason}: {e}")
                time.sleep(2 * attempt)
                continue
            # Validate required fields
            missing = [k for k in REQUIRED_FIELDS if k not in new_draft]
            if missing:
                last_err = ValueError(f"missing fields: {missing}")
                time.sleep(2 * attempt)
                continue
            # Merge back self_critique (we stripped it; model had no reason to touch it, but enforce)
            if self_crit is not None:
                new_draft["self_critique"] = self_crit
            new_draft["corrections_applied"] = corrections_applied
            return new_draft, resp.usage.input_tokens, resp.usage.output_tokens
        except Exception as e:
            last_err = e
            time.sleep(2 * attempt)
    raise RuntimeError(f"correction failed after {MAX_RETRIES} attempts: {last_err}")


def _snapshot_before(draft: dict[str, Any], did: str, flag_idx: int) -> None:
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    target = SNAPSHOT_DIR / f"{did}__{flag_idx:02d}__before.json"
    # Only write if doesn't exist (first correction on this draft)
    if not target.exists():
        target.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")


def _snapshot_after(draft: dict[str, Any], did: str, flag_idx: int) -> None:
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    (SNAPSHOT_DIR / f"{did}__{flag_idx:02d}__after.json").write_text(
        json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _diff_brief(before: dict[str, Any], after: dict[str, Any]) -> str:
    """Return a brief textual diff focusing on legal_anchors + answer_steps."""
    parts: list[str] = []
    # Legal anchors
    b_la = before.get("legal_anchors") or []
    a_la = after.get("legal_anchors") or []
    if b_la != a_la:
        parts.append("legal_anchors changed:")
        for i in range(max(len(b_la), len(a_la))):
            b = b_la[i] if i < len(b_la) else None
            a = a_la[i] if i < len(a_la) else None
            if b != a:
                parts.append(f"  - anchor #{i}:")
                if b is not None:
                    parts.append(f"    BEFORE: {b.get('law_name','')} {b.get('article_number','')}")
                if a is not None:
                    parts.append(f"    AFTER:  {a.get('law_name','')} {a.get('article_number','')}")
    # Answer steps
    b_st = before.get("answer_steps") or []
    a_st = after.get("answer_steps") or []
    step_changes = 0
    for i in range(max(len(b_st), len(a_st))):
        b = b_st[i] if i < len(b_st) else None
        a = a_st[i] if i < len(a_st) else None
        if b != a:
            step_changes += 1
            if step_changes <= 3:
                parts.append(f"  - step #{i + 1} changed:")
                if b:
                    parts.append(f"    BEFORE: {b.get('action','')} — {(b.get('detail') or '')[:150]}")
                if a:
                    parts.append(f"    AFTER:  {a.get('action','')} — {(a.get('detail') or '')[:150]}")
    if step_changes > 3:
        parts.append(f"  - (and {step_changes - 3} more step changes)")
    # Edge cases
    if (before.get("edge_cases") or []) != (after.get("edge_cases") or []):
        parts.append("edge_cases: changed")
    # Common mistakes / related_questions / draft field
    for k in ("common_mistakes", "related_questions", "draft", "last_verified_at"):
        if before.get(k) != after.get(k):
            parts.append(f"{k}: changed")
    if not parts:
        return "(no visible diff in tracked fields)"
    return "\n".join(parts)


def run_pytest() -> tuple[int, int, str]:
    """Return (passed, failed, last_lines_of_output)."""
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--no-header"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        return (0, 0, "pytest TIMEOUT after 600s")
    except Exception as e:
        return (0, 0, f"pytest ERROR: {e}")
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    passed = 0
    failed = 0
    m = re.search(r"(\d+)\s+passed", out)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+)\s+failed", out)
    if m:
        failed = int(m.group(1))
    # Take last ~30 lines
    last = "\n".join(out.strip().splitlines()[-30:])
    return passed, failed, last


def _write_report(
    per_draft: dict[str, dict[str, int]],
    top3: list[dict[str, Any]],
    errors: list[dict[str, str]],
    applied: int,
    failed: int,
    total: int,
    cost: float,
    pytest_passed: int,
    pytest_failed: int,
    pytest_tail: str,
    stopped_early: bool,
) -> None:
    lines: list[str] = []
    lines.append("# Batch 1 Corrections Log")
    lines.append("")
    lines.append(f"Data: {TODAY_ISO}")
    lines.append(f"Applied: {applied} / {total}")
    lines.append(f"Failed: {failed}")
    lines.append(f"Koszt: ${cost:.4f}")
    lines.append(f"Pytest: {pytest_passed} passed, {pytest_failed} failed")
    if stopped_early:
        lines.append(f"STOPPED EARLY: hit ${COST_HARD_CAP} cost cap.")
    lines.append("")
    lines.append("## Per draft")
    lines.append("| Draft | Flag applied | Flag skipped (errors) |")
    lines.append("|---|---|---|")
    for did, d in per_draft.items():
        lines.append(f"| {did} | {d.get('applied', 0)} | {d.get('failed', 0)} |")
    lines.append("")
    lines.append("## Top 3 examples (przed/po)")
    if not top3:
        lines.append("(brak — żaden draft z listy priorytetowej nie został zmodyfikowany)")
    for idx, entry in enumerate(top3, start=1):
        lines.append(f"### {idx}. {entry['draft_id']} — flag [{entry['flag_type']}] {entry['flag_description'][:120]}")
        lines.append(f"**Źródło:** {entry.get('source_url') or '(v1 corrective_suggestion)'}")
        lines.append("")
        lines.append("```")
        lines.append(entry["diff_text"])
        lines.append("```")
        lines.append("")
    lines.append("## Błędy")
    if not errors:
        lines.append("(brak)")
    for e in errors:
        lines.append(f"- **{e['draft_id']}** flag [{e['flag_type']}]: {e['error']}")
    lines.append("")
    lines.append("## Pytest wynik (ogon outputu)")
    lines.append("```")
    lines.append(pytest_tail)
    lines.append("```")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    _load_env()
    import anthropic

    client = anthropic.Anthropic(timeout=300.0)
    draft_paths = sorted(DRAFTS_DIR.glob("wf_*.json"))

    # Build the list of (path, draft_id, flag_idx, flag, source)
    # Skip flags already logged in corrections_applied (resume support).
    queue: list[tuple[Path, str, int, dict[str, Any], str]] = []
    skipped_already = 0
    for p in draft_paths:
        draft = json.loads(p.read_text(encoding="utf-8"))
        did = draft.get("id") or p.stem
        issues = (draft.get("self_critique") or {}).get("issues") or []
        applied_descs = {
            (e.get("flag_description") or "")
            for e in (draft.get("corrections_applied") or [])
        }
        for idx, flag in enumerate(issues):
            src = _classify_flag(flag)
            if src:
                if (flag.get("description") or "") in applied_descs:
                    skipped_already += 1
                    continue
                queue.append((p, did, idx, flag, src))
    total = len(queue)
    print(f"Confirmed flags to apply: {total} (skipped already-applied: {skipped_already})", flush=True)

    total_in = 0
    total_out = 0
    applied = 0
    failed = 0
    per_draft: dict[str, dict[str, int]] = {}
    errors: list[dict[str, str]] = []
    stopped_early = False

    # Priority drafts for before/after snippets: wf_10, wf_107, wf_63
    priority = ["wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece",
                "wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p",
                "wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat"]
    top3_slots: dict[str, dict[str, Any]] = {}

    for step, (p, did, idx, flag, src) in enumerate(queue, start=1):
        cost_so_far = total_in / 1000 * PRICE_IN_PER_1K + total_out / 1000 * PRICE_OUT_PER_1K
        if cost_so_far >= COST_HARD_CAP:
            print(f"\nCOST CAP reached at ${cost_so_far:.4f} >= ${COST_HARD_CAP}. Stopping.")
            stopped_early = True
            break

        # Re-read draft (may have been modified by previous correction)
        draft = json.loads(p.read_text(encoding="utf-8"))
        # Re-locate the same flag by type+description (indices are stable, but be robust)
        issues = (draft.get("self_critique") or {}).get("issues") or []
        if idx >= len(issues):
            msg = "flag index out of range after draft edits"
            errors.append({"draft_id": did, "flag_type": flag.get("type", ""), "error": msg})
            failed += 1
            bucket = per_draft.setdefault(did, {})
            bucket["failed"] = bucket.get("failed", 0) + 1
            continue
        current_flag = issues[idx]
        if (
            current_flag.get("type") != flag.get("type")
            or current_flag.get("description") != flag.get("description")
        ):
            msg = "flag identity mismatch after reload"
            errors.append({"draft_id": did, "flag_type": flag.get("type", ""), "error": msg})
            failed += 1
            bucket = per_draft.setdefault(did, {})
            bucket["failed"] = bucket.get("failed", 0) + 1
            continue

        # Snapshot before (only first correction per draft writes)
        before_copy = copy.deepcopy(draft)

        try:
            new_draft, in_tok, out_tok = apply_single_correction(client, draft, current_flag, src)
            total_in += in_tok
            total_out += out_tok
            # Log correction in corrections_applied
            entry: dict[str, Any] = {
                "flag_type": current_flag.get("type"),
                "flag_description": current_flag.get("description"),
                "applied_at": now_iso_utc(),
                "source": src,
            }
            if src == "v2":
                entry["source_url"] = current_flag.get("source_url") or ""
            corrections_applied = new_draft.get("corrections_applied") or []
            corrections_applied.append(entry)
            new_draft["corrections_applied"] = corrections_applied

            # Persist
            p.write_text(json.dumps(new_draft, ensure_ascii=False, indent=2), encoding="utf-8")
            applied += 1
            bucket = per_draft.setdefault(did, {})
            bucket["applied"] = bucket.get("applied", 0) + 1

            # Capture priority before/after snippet (first confirmed per priority draft)
            if did in priority and did not in top3_slots:
                diff_text = _diff_brief(before_copy, new_draft)
                top3_slots[did] = {
                    "draft_id": did,
                    "flag_type": current_flag.get("type", ""),
                    "flag_description": current_flag.get("description", ""),
                    "source_url": current_flag.get("source_url", "") if src == "v2" else "",
                    "diff_text": diff_text,
                }

            print(
                f"[{step}/{total}] OK {did[:45]} flag#{idx} [{src}] in={in_tok} out={out_tok} "
                f"cost=${total_in/1000*PRICE_IN_PER_1K + total_out/1000*PRICE_OUT_PER_1K:.4f}",
                flush=True,
            )
        except Exception as e:
            err_msg = str(e)[:300]
            errors.append(
                {
                    "draft_id": did,
                    "flag_type": current_flag.get("type", ""),
                    "error": err_msg,
                }
            )
            failed += 1
            bucket = per_draft.setdefault(did, {})
            bucket["failed"] = bucket.get("failed", 0) + 1
            print(f"[{step}/{total}] FAIL {did[:45]} flag#{idx}: {err_msg[:120]}", flush=True)

        time.sleep(RATE_LIMIT_S)

    cost = total_in / 1000 * PRICE_IN_PER_1K + total_out / 1000 * PRICE_OUT_PER_1K
    print(f"\nApply phase done. applied={applied} failed={failed} cost=${cost:.4f}")

    print("\nRunning pytest...")
    passed, pfailed, tail = run_pytest()
    print(f"pytest: {passed} passed, {pfailed} failed")

    top3 = [top3_slots[did] for did in priority if did in top3_slots]
    _write_report(
        per_draft,
        top3,
        errors,
        applied,
        failed,
        total,
        cost,
        passed,
        pfailed,
        tail,
        stopped_early,
    )
    print(f"Report: {REPORT_PATH}")
    return 2 if stopped_early else (1 if failed else 0)


if __name__ == "__main__":
    raise SystemExit(main())
