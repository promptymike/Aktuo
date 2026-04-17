"""Self-validation layer for batch 1 workflow drafts.

Loads each of 10 wf_*.json drafts from data/workflow_drafts/, asks Haiku 4.5
to critique (not fix) along 6 problem categories, adds a `self_critique`
field to the draft, and writes a per-batch report with status distribution
and top offenders.

Run from repo root:
    .venv/Scripts/python -X utf8 analysis/self_validate_batch1.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DRAFTS_DIR = ROOT / "data" / "workflow_drafts"
REPORT_PATH = ROOT / "analysis" / "batch1_self_validation_report.md"

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 2000
TEMPERATURE = 0.2
MAX_RETRIES = 3
RATE_LIMIT_DELAY_S = 1.0

# Haiku 4.5 public pricing (per 1M tokens): $1 input / $5 output.
PRICE_INPUT_PER_1K = 0.001
PRICE_OUTPUT_PER_1K = 0.005

TODAY_ISO = "2026-04-18"

SYSTEM_PROMPT = """Jesteś ekspertem księgowym/podatkowym analizującym draft procedury operacyjnej wygenerowany przez AI. Twoja rola: znaleźć potencjalne błędy i niepewności, NIE poprawiać drafta.

Sprawdzasz 6 kategorii problemów:
1. legal_anchor_uncertainty - czy numery artykułów wyglądają prawdopodobnie?
2. outdated_data_risk - czy dane (limity, kwoty, daty) mogą być nieaktualne dla 2026?
3. step_contradiction - czy są sprzeczności między krokami?
4. missing_critical_info - czy brakuje krytycznego kroku/warunku?
5. hallucination_risk - czy draft wspomina przepisy/kody/formularze które mogą nie istnieć?
6. edge_case_coverage - czy edge cases wyglądają realistycznie czy wymyślone?

Dla każdego problemu podaj: type, severity (low/medium/high), description (1-2 zdania konkretne, nie ogólne).

Zwróć valid JSON w formacie:
{
  "status": "clean" | "flagged_for_review" | "needs_major_revision",
  "issues": [
    {"type": "...", "severity": "...", "description": "..."}
  ],
  "confidence_score": 0.0-1.0,
  "general_assessment": "1-2 zdania ogólnej oceny"
}

NIE generuj poprawek. Tylko flaguj problemy. Jeśli nie ma problemów, zwróć pustą listę issues i status "clean"."""


def _load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and not os.environ.get(key):
            os.environ[key] = value


def _extract_json(text: str) -> dict:
    """Pull the first {...} block out of Haiku's response."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"no JSON object found in response: {text[:200]}")
    return json.loads(match.group(0))


def critique_draft(client, draft: dict) -> tuple[dict, int, int]:
    """Return (critique_dict, input_tokens, output_tokens)."""
    # Strip any prior self_critique so we don't feed it back in.
    draft_for_review = {k: v for k, v in draft.items() if k != "self_critique"}
    user_prompt = (
        "Przeanalizuj ten draft workflow rekord dla polskiego asystenta AI "
        "dla księgowych:\n\n"
        f"{json.dumps(draft_for_review, ensure_ascii=False, indent=2)}\n\n"
        "Zwróć JSON z analizą problemów."
    )

    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = "".join(
                block.text for block in resp.content if getattr(block, "type", None) == "text"
            )
            critique = _extract_json(text)
            return (
                critique,
                resp.usage.input_tokens,
                resp.usage.output_tokens,
            )
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            print(f"  attempt {attempt}/{MAX_RETRIES} failed: {exc}")
            time.sleep(2 * attempt)
    raise RuntimeError(f"critique failed after {MAX_RETRIES} attempts: {last_err}")


def _normalize_status(status: str) -> str:
    s = (status or "").strip().lower()
    if s in {"clean", "flagged_for_review", "needs_major_revision"}:
        return s
    return "flagged_for_review"


def _build_report(results: list[dict], total_cost: float) -> str:
    n = len(results)
    clean = sum(1 for r in results if r["status"] == "clean")
    flagged = sum(1 for r in results if r["status"] == "flagged_for_review")
    major = sum(1 for r in results if r["status"] == "needs_major_revision")

    sev_counts = {"high": 0, "medium": 0, "low": 0}
    type_counts: dict[str, int] = {}
    for r in results:
        for iss in r["issues"]:
            sev = (iss.get("severity") or "").strip().lower()
            if sev in sev_counts:
                sev_counts[sev] += 1
            t = (iss.get("type") or "").strip()
            if t:
                type_counts[t] = type_counts.get(t, 0) + 1

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
    lines.append("# Batch 1 Self-Validation Report")
    lines.append("")
    lines.append(f"Data: {TODAY_ISO}")
    lines.append(f"Model: {MODEL}")
    lines.append(f"Koszt: ${total_cost:.4f}")
    lines.append("")
    lines.append("## Podsumowanie statusów")
    lines.append(f"- Clean: {clean}/{n}")
    lines.append(f"- Flagged_for_review: {flagged}/{n}")
    lines.append(f"- Needs_major_revision: {major}/{n}")
    lines.append("")
    lines.append("## Statystyki problemów (według severity)")
    lines.append(f"- High: {sev_counts['high']}")
    lines.append(f"- Medium: {sev_counts['medium']}")
    lines.append(f"- Low: {sev_counts['low']}")
    lines.append("")
    lines.append("## Top 3 najsłabsze drafty")
    for r in top3:
        lines.append(
            f"- {r['draft_id']} — {len(r['issues'])} issues — confidence {r['confidence_score']:.2f} — status `{r['status']}`"
        )
    lines.append("")
    lines.append("## Najczęstsze kategorie problemów")
    if type_counts:
        for t, c in sorted(type_counts.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"- {t}: {c}")
    else:
        lines.append("- (brak flag — wszystkie drafty clean)")
    lines.append("")
    lines.append("## Szczegóły per draft")
    lines.append("")
    for r in results:
        lines.append(f"### {r['draft_id']}")
        lines.append(f"- Title: {r['title']}")
        lines.append(f"- Cluster: {r['cluster_id']}  |  Topic: {r['topic_area']}")
        lines.append(f"- Status: `{r['status']}`")
        lines.append(f"- Confidence: {r['confidence_score']:.2f}")
        lines.append(f"- Assessment: {r['general_assessment']}")
        if r["issues"]:
            lines.append("- Issues:")
            for iss in r["issues"]:
                sev = (iss.get("severity") or "").upper()
                t = iss.get("type", "?")
                desc = iss.get("description", "")
                lines.append(f"  - [{sev}] {t}: {desc}")
        else:
            lines.append("- Issues: (none)")
        lines.append("")

    lines.append("## Rekomendacje dalszych kroków")
    if major:
        lines.append(
            f"- {major} draft(y) oznaczony jako `needs_major_revision` — priorytet P0, wymagają regeneracji lub manualnej rewizji eksperta przed publikacją."
        )
    if flagged:
        lines.append(
            f"- {flagged} draft(y) `flagged_for_review` — Paweł w weekendowej walidacji powinien przejść kategorie problemów i zdecydować: akceptacja z poprawką, regeneracja, czy merge z ekspertem."
        )
    if clean:
        lines.append(
            f"- {clean} draft(y) `clean` — kandydaci do szybkiej walidacji (spot-check) i publikacji bez regeneracji."
        )
    if sev_counts["high"] >= 5:
        lines.append(
            "- Duża liczba flag `high` — rozważ czy system prompt generatora (Opus) wymaga zacieśnienia instrukcji o aktualne limity 2026 i cytowanie dokładnych numerów artykułów."
        )
    lines.append(
        "- Następny krok: przejść top 3 najsłabsze drafty i porównać flagowane problemy z rzeczywistym stanem prawnym — jeśli potwierdzą się, regenerować z poprawioną materialą lub zwiększonym KB retrieval."
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    _load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERR: ANTHROPIC_API_KEY not set (check .env)")
        return 2

    import anthropic

    client = anthropic.Anthropic()

    draft_files = sorted(DRAFTS_DIR.glob("wf_*.json"))
    if not draft_files:
        print(f"ERR: no wf_*.json files in {DRAFTS_DIR}")
        return 2

    print(f"Found {len(draft_files)} drafts. Critiquing with {MODEL}...")

    results: list[dict] = []
    total_in = 0
    total_out = 0

    for i, path in enumerate(draft_files, 1):
        draft = json.loads(path.read_text(encoding="utf-8"))
        did = draft.get("id", path.stem)
        print(f"[{i}/{len(draft_files)}] {did}")

        t0 = time.time()
        critique, in_tok, out_tok = critique_draft(client, draft)
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
        path.write_text(
            json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        results.append(
            {
                "draft_id": did,
                "title": draft.get("title", ""),
                "topic_area": draft.get("topic_area", ""),
                "cluster_id": (
                    draft.get("generation_metadata", {}).get("cluster_id", "")
                ),
                "status": status,
                "confidence_score": confidence,
                "general_assessment": assessment,
                "issues": issues,
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "elapsed_s": round(dt, 2),
            }
        )
        print(
            f"  status={status}  issues={len(issues)}  conf={confidence:.2f}  "
            f"in={in_tok} out={out_tok}  {dt:.1f}s"
        )

        if i < len(draft_files):
            time.sleep(RATE_LIMIT_DELAY_S)

    total_cost = (
        total_in / 1000 * PRICE_INPUT_PER_1K + total_out / 1000 * PRICE_OUTPUT_PER_1K
    )
    print(
        f"\nDone. total_in={total_in} total_out={total_out} cost=${total_cost:.4f}"
    )

    report = _build_report(results, total_cost)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Report: {REPORT_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
