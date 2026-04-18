"""Apply 39 v3-confirmed corrections to batch 1+2 drafts.

For each flag in data/workflow_drafts/wf_*.json self_critique.issues where
verdict_v3 == 'confirmed' (but not yet logged in corrections_applied), call
Sonnet 4.6 with the stripped draft (self_critique elided) + the flag +
verifier_reasoning_v3 + source_url_v3 + source_quote_v3. Overwrite draft with
corrected JSON. Runs pytest and writes analysis/batch_all_v3_corrections_log.md.
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
REPORT_PATH = ROOT / "analysis" / "batch_all_v3_corrections_log.md"
ENV_PATH = ROOT / ".env"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 16000
TEMPERATURE = 0.1
MAX_RETRIES = 3
RATE_LIMIT_S = 1.0
PRICE_IN_PER_1K = 0.003
PRICE_OUT_PER_1K = 0.015
COST_HARD_CAP = 4.50

TODAY_ISO = "2026-04-19"
REQUIRED_FIELDS = ("id", "title", "topic_area", "answer_steps", "legal_anchors")

# 11 drafty <30% uncertainty z v3 report (ready for testers)
READY_FOR_TESTERS = {
    "wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece",
    "wf_45_wymiar_urlopu_wypoczynkowego_przy_niepelnym_etacie_i_zmianie",
    "wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p",
    "wf_110_kpir_2026_ksiegowanie_faktur_do_paragonu_i_sprzedazy_detalic",
    "wf_127_premie_w_podstawie_wynagrodzenia_chorobowego_i_urlopowego",
    "wf_134_zus_z_3_wynagrodzenie_i_zasilek_chorobowy_przy_firmach_20_pr",
    "wf_135_przejscie_roku_wynagrodzenie_chorobowe_vs_zasilek_i_okres_za",
    "wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze",
    "wf_19_delegowanie_i_podroze_sluzbowe_pracownikow_za_granice_zus_po",
    "wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan",
    "wf_35_ewidencja_i_rozliczanie_czasu_pracy_przy_roznych_systemach_i",
}

SYSTEM_PROMPT = """Jesteś redaktorem draftu workflow dla księgowych. Dostajesz aktualny draft + confirmed v3 flagę + rekomendowaną korektę z źródłem web. Zwróć ZMODYFIKOWANY draft z punktowo naprawionym problemem. NIE zmieniaj nic poza tym co wskazuje flaga. Zachowaj strukturę JSON, wszystkie istniejące pola, metadata, self_critique, corrections_applied. Zwróć CZYSTY JSON bez markdown bez komentarzy."""


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


def _build_user_prompt(draft_stripped: dict[str, Any], flag: dict[str, Any]) -> str:
    recommendation = (flag.get("verifier_reasoning_v3") or "").strip()
    source_url = flag.get("source_url_v3") or ""
    source_quote = flag.get("source_quote_v3") or ""
    return (
        "DRAFT (pełen JSON):\n"
        f"{json.dumps(draft_stripped, ensure_ascii=False, indent=2)}\n\n"
        "FLAGA V3 DO POPRAWY:\n"
        f"Type: {flag.get('type')}\n"
        f"Severity: {flag.get('severity')}\n"
        f"Description: {flag.get('description')}\n"
        f"REKOMENDACJA (z verifier_reasoning_v3): {recommendation}\n"
        f"SOURCE URL (v3): {source_url}\n"
        f"SOURCE QUOTE (v3): {source_quote}\n\n"
        "Zwróć naprawiony draft JSON."
    )


def apply_single_correction(
    client: Any,
    draft: dict[str, Any],
    flag: dict[str, Any],
) -> tuple[dict[str, Any], int, int]:
    """Return (new_draft_merged, input_tokens, output_tokens)."""
    self_crit = draft.get("self_critique")
    corrections_applied = draft.get("corrections_applied", [])
    stripped = {k: v for k, v in draft.items() if k != "self_critique"}

    user_msg = _build_user_prompt(stripped, flag)
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
            missing = [k for k in REQUIRED_FIELDS if k not in new_draft]
            if missing:
                last_err = ValueError(f"missing fields: {missing}")
                time.sleep(2 * attempt)
                continue
            if self_crit is not None:
                new_draft["self_critique"] = self_crit
            new_draft["corrections_applied"] = corrections_applied
            return new_draft, resp.usage.input_tokens, resp.usage.output_tokens
        except Exception as e:
            last_err = e
            time.sleep(2 * attempt)
    raise RuntimeError(f"correction failed after {MAX_RETRIES} attempts: {last_err}")


def run_pytest() -> tuple[int, int, str]:
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
    last = "\n".join(out.strip().splitlines()[-30:])
    return passed, failed, last


def _write_report(
    per_draft: dict[str, dict[str, int]],
    errors: list[dict[str, str]],
    applied: int,
    failed: int,
    total: int,
    cost: float,
    pytest_passed: int,
    pytest_failed: int,
    pytest_tail: str,
    stopped_early: bool,
    skipped_already: int,
    ready_touched: list[str],
) -> None:
    lines: list[str] = []
    lines.append("# V3 Corrections Log")
    lines.append("")
    lines.append(f"Data: {TODAY_ISO}")
    lines.append(f"Model: {MODEL}")
    lines.append(f"Applied: {applied} / {total}")
    lines.append(f"Failed: {failed}")
    if skipped_already:
        lines.append(f"Pominięte (już były w corrections_applied): {skipped_already}")
    lines.append(f"Koszt: ${cost:.4f} (cap ${COST_HARD_CAP:.2f})")
    lines.append(f"Pytest: {pytest_passed} passed, {pytest_failed} failed")
    if stopped_early:
        lines.append(f"STOPPED EARLY: hit ${COST_HARD_CAP} cost cap.")
    lines.append("")

    lines.append("## Ready-for-testers drafty które dostały v3 corrections")
    if ready_touched:
        for did in ready_touched:
            bucket = per_draft.get(did, {})
            lines.append(f"- {did} (applied: {bucket.get('applied', 0)}, failed: {bucket.get('failed', 0)})")
    else:
        lines.append("(żaden z 11 ready-for-testers draftów nie miał v3-confirmed flag)")
    lines.append("")

    lines.append("## Per draft")
    lines.append("| Draft | Flag applied | Flag failed |")
    lines.append("|---|---|---|")
    for did, d in sorted(per_draft.items()):
        lines.append(f"| {did} | {d.get('applied', 0)} | {d.get('failed', 0)} |")
    lines.append("")

    lines.append("## Failed items (do ewentualnego manual fix później)")
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

    # Build queue: flags where verdict_v3 == "confirmed" AND not yet in corrections_applied
    queue: list[tuple[Path, str, int, dict[str, Any]]] = []
    skipped_already = 0
    for p in draft_paths:
        draft = json.loads(p.read_text(encoding="utf-8"))
        did = draft.get("id") or p.stem
        issues = (draft.get("self_critique") or {}).get("issues") or []
        applied_descs = {
            (e.get("flag_description") or "")
            for e in (draft.get("corrections_applied") or [])
            if e.get("source") == "v3"
        }
        for idx, flag in enumerate(issues):
            if flag.get("verdict_v3") != "confirmed":
                continue
            if (flag.get("description") or "") in applied_descs:
                skipped_already += 1
                continue
            queue.append((p, did, idx, flag))
    total = len(queue)
    print(f"V3-confirmed flags to apply: {total} (skipped already-applied: {skipped_already})", flush=True)

    total_in = 0
    total_out = 0
    applied = 0
    failed = 0
    per_draft: dict[str, dict[str, int]] = {}
    errors: list[dict[str, str]] = []
    stopped_early = False
    ready_touched_set: set[str] = set()

    for step, (p, did, idx, flag) in enumerate(queue, start=1):
        cost_so_far = total_in / 1000 * PRICE_IN_PER_1K + total_out / 1000 * PRICE_OUT_PER_1K
        if cost_so_far >= COST_HARD_CAP:
            print(f"\nCOST CAP reached at ${cost_so_far:.4f} >= ${COST_HARD_CAP}. Stopping.", flush=True)
            stopped_early = True
            break

        # Re-read draft (may have been mutated by a prior correction on same file)
        draft = json.loads(p.read_text(encoding="utf-8"))
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

        try:
            new_draft, in_tok, out_tok = apply_single_correction(client, draft, current_flag)
            total_in += in_tok
            total_out += out_tok
            entry: dict[str, Any] = {
                "flag_type": current_flag.get("type"),
                "flag_description": current_flag.get("description"),
                "applied_at": now_iso_utc(),
                "source": "v3",
                "source_url": current_flag.get("source_url_v3") or "",
            }
            corrections_applied = new_draft.get("corrections_applied") or []
            corrections_applied.append(entry)
            new_draft["corrections_applied"] = corrections_applied

            p.write_text(json.dumps(new_draft, ensure_ascii=False, indent=2), encoding="utf-8")
            applied += 1
            bucket = per_draft.setdefault(did, {})
            bucket["applied"] = bucket.get("applied", 0) + 1
            if did in READY_FOR_TESTERS:
                ready_touched_set.add(did)

            print(
                f"[{step}/{total}] OK {did[:45]:45} flag#{idx} in={in_tok} out={out_tok} "
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
            print(f"[{step}/{total}] FAIL {did[:45]:45} flag#{idx}: {err_msg[:120]}", flush=True)

        time.sleep(RATE_LIMIT_S)

    cost = total_in / 1000 * PRICE_IN_PER_1K + total_out / 1000 * PRICE_OUT_PER_1K
    print(f"\nApply phase done. applied={applied} failed={failed} cost=${cost:.4f}", flush=True)

    print("\nRunning pytest...", flush=True)
    passed, pfailed, tail = run_pytest()
    print(f"pytest: {passed} passed, {pfailed} failed", flush=True)

    ready_touched = sorted(ready_touched_set)
    _write_report(
        per_draft,
        errors,
        applied,
        failed,
        total,
        cost,
        passed,
        pfailed,
        tail,
        stopped_early,
        skipped_already,
        ready_touched,
    )
    print(f"Report: {REPORT_PATH}", flush=True)
    return 2 if stopped_early else (1 if failed else 0)


if __name__ == "__main__":
    raise SystemExit(main())
