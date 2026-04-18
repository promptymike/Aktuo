"""Verifier v2: web_search + whitelist for cannot_verify flags (batch 1).

For each flag with verdict == 'cannot_verify' in data/workflow_drafts/wf_*.json
self_critique.issues, call Sonnet 4.6 with web_search + web_fetch server tools
restricted to a 9-domain Polish accounting/legal whitelist. Mutates each flag
in place to add verdict_v2 + verifier_reasoning_v2 (+ source_url + source_quote
when a whitelist source rules). Stops at COST_HARD_CAP.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DRAFTS_DIR = ROOT / "data" / "workflow_drafts"
REPORT_PATH = ROOT / "analysis" / "batch1_verifier_v2_report.md"
ENV_PATH = ROOT / ".env"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1000
TEMPERATURE = 0.1
MAX_RETRIES = 3
RATE_LIMIT_S = 1.0
PRICE_IN_PER_1K = 0.003
PRICE_OUT_PER_1K = 0.015
PRICE_PER_SEARCH = 0.01
COST_HARD_CAP = 3.00
COST_LOG_EVERY = 20

WHITELIST = [
    "gofin.pl",
    "interpretacje.gofin.pl",
    "podatki.gov.pl",
    "zus.pl",
    "biznes.gov.pl",
    "sejm.gov.pl",
    "isap.sejm.gov.pl",
    "ksiegowosc.infor.pl",
    "podatki.biz",
]

TODAY_ISO = "2026-04-18"
SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}

SYSTEM_PROMPT = """Jesteś ekspertem weryfikującym czy flaga wątpliwości w drafcie workflow rekord jest uzasadniona.

Dostajesz:
1. Flagę (type, severity, description) od self_critic
2. Oryginalny fragment drafta
3. Masz dostęp do narzędzia web_search (oraz opcjonalnie web_fetch) ograniczonego do zaufanych polskich źródeł księgowo-prawnych: gofin.pl, interpretacje.gofin.pl, podatki.gov.pl, zus.pl, biznes.gov.pl, sejm.gov.pl, isap.sejm.gov.pl, ksiegowosc.infor.pl, podatki.biz.

Twoja rola: zweryfikować czy flaga to prawdziwy problem czy false positive, używając TYLKO tych zaufanych źródeł.

Zasady pracy:
- Najpierw wykonaj 1 web_search z krótką, konkretną frazą (maks 6 słów).
- Jeśli trzeba pogłębić, możesz opcjonalnie wykonać 1 web_fetch na najbardziej obiecujący URL z whitelisty.
- Jeśli snippet z web_search wystarcza — NIE wykonuj web_fetch (oszczędzaj tokeny).

Na końcu zwracasz DOKŁADNIE JEDEN obiekt JSON (bez dodatkowego tekstu):
{
  "verdict_v2": "confirmed" | "false_positive" | "still_cannot_verify",
  "confidence": 0.0-1.0,
  "reasoning": "1-3 zdania z konkretnym odniesieniem do znalezionego źródła",
  "source_url": "URL tylko jeśli znaleziono potwierdzenie/obalenie (MUSI być z whitelist)",
  "source_quote": "BARDZO KRÓTKI dosłowny cytat max 10 słów ze źródła (copyright)"
}

Definicje:
- "confirmed" = źródło potwierdza że flaga jest słuszna (draft jest błędny)
- "false_positive" = źródło potwierdza że draft jest poprawny
- "still_cannot_verify" = źródła z whitelisty nie rozstrzygają sprawy

KLUCZOWE:
- NIE halucynuj. Jeśli nie znalazłeś jednoznacznej odpowiedzi → "still_cannot_verify".
- source_url MUSI pochodzić z faktycznego wyniku web_search lub web_fetch — nie zmyślaj.
- source_quote MAX 10 słów dosłownie z treści strony (copyright).
- source_url puste + source_quote puste jest OK dla still_cannot_verify."""


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


def _relevant_draft_section(flag: dict[str, Any], draft: dict[str, Any]) -> str:
    blocks: list[str] = []
    la = draft.get("legal_anchors", []) or []
    if la:
        blocks.append("LEGAL_ANCHORS:\n" + json.dumps(la, ensure_ascii=False, indent=2))
    steps = draft.get("answer_steps", []) or []
    if steps:
        rendered: list[str] = []
        for s in steps:
            detail = (s.get("detail") or "")
            if len(detail) > 220:
                detail = detail[:220].rstrip() + "…"
            cond = s.get("condition")
            cond_str = f"  (warunek: {cond})" if cond else ""
            rendered.append(
                f"- step {s.get('step')}: {s.get('action')} — {detail}{cond_str}"
            )
        blocks.append("ANSWER_STEPS:\n" + "\n".join(rendered))
    if flag.get("type") == "edge_case_coverage":
        ec = draft.get("edge_cases", []) or []
        if ec:
            blocks.append("EDGE_CASES:\n" + json.dumps(ec, ensure_ascii=False, indent=2))
    return "\n\n".join(blocks)


def _hint_query(flag: dict[str, Any], draft: dict[str, Any]) -> str:
    """Return a short query hint (<=6 words) to suggest to Claude."""
    topic = draft.get("topic_area") or ""
    title = draft.get("title") or ""
    # Articles mentioned
    arts = re.findall(r"art\.?\s*\d+[a-zA-Z]*", flag.get("description", "") or "", re.I)
    first_art = arts[0] if arts else ""
    # Extract 2 significant nouns from description (simple heuristic: capitalized words)
    caps = re.findall(r"[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{3,}", flag.get("description", "") or "")
    picks = [w for w in caps if w.lower() not in {"draft", "step"}][:2]
    parts = [first_art] + picks
    if topic and topic not in " ".join(parts):
        parts.append(topic)
    # Fallback — use first 3 content words
    if not any(parts):
        words = re.findall(r"\w{4,}", flag.get("description", "") or "")
        parts = words[:3]
    q = " ".join(p for p in parts if p)
    # Keep under ~6 words
    return " ".join(q.split()[:6])


def build_user_prompt(flag: dict[str, Any], draft: dict[str, Any]) -> str:
    section = _relevant_draft_section(flag, draft)
    hint = _hint_query(flag, draft)
    return (
        "FLAGA DO WERYFIKACJI:\n"
        f"Type: {flag.get('type')}\n"
        f"Severity: {flag.get('severity')}\n"
        f"Description: {flag.get('description')}\n\n"
        "FRAGMENT DRAFTA:\n"
        f"{section}\n\n"
        f"Sugerowane zapytanie do web_search (możesz użyć lub zmienić): \"{hint}\"\n\n"
        "Zweryfikuj flagę z użyciem web_search (i opcjonalnie web_fetch), korzystając tylko z whitelisty. "
        "Zwróć wyłącznie obiekt JSON."
    )


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
    raise ValueError("no JSON in response")


def _normalize_verdict_v2(v: Any) -> str:
    s = str(v or "").strip().lower()
    if s in {"confirmed", "false_positive", "still_cannot_verify"}:
        return s
    if s in {"false-positive", "false positive", "falsepositive"}:
        return "false_positive"
    if s in {"cannot_verify", "cannot verify", "still cannot verify", "still-cannot-verify"}:
        return "still_cannot_verify"
    return "still_cannot_verify"


def _is_whitelisted(url: str | None) -> bool:
    if not url:
        return False
    try:
        host = (urlparse(url).hostname or "").lower()
    except Exception:
        return False
    return any(host == d or host.endswith("." + d) or host == d for d in WHITELIST) or any(
        d in host for d in WHITELIST
    )


def _domain_of(url: str | None) -> str:
    if not url:
        return ""
    try:
        host = (urlparse(url).hostname or "").lower()
    except Exception:
        return ""
    for d in WHITELIST:
        if host == d or host.endswith("." + d) or d in host:
            return d
    return host


def _truncate_quote(quote: str) -> str:
    if not quote:
        return ""
    words = quote.split()
    if len(words) > 10:
        return " ".join(words[:10])
    return quote


def _count_server_tools(resp_content: list[Any]) -> tuple[int, int]:
    searches = 0
    fetches = 0
    for b in resp_content:
        if getattr(b, "type", "") == "server_tool_use":
            if getattr(b, "name", "") == "web_search":
                searches += 1
            elif getattr(b, "name", "") == "web_fetch":
                fetches += 1
    return searches, fetches


def verify_flag_v2(client: Any, flag: dict[str, Any], draft: dict[str, Any]) -> tuple[dict[str, Any], int, int, int, int]:
    user_msg = build_user_prompt(flag, draft)
    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.beta.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
                tools=[
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "max_uses": 2,
                        "allowed_domains": WHITELIST,
                    },
                    {
                        "type": "web_fetch_20250910",
                        "name": "web_fetch",
                        "max_uses": 1,
                        "allowed_domains": WHITELIST,
                        "max_content_tokens": 2000,
                    },
                ],
                betas=["web-fetch-2025-09-10"],
            )
            text = "".join(
                getattr(b, "text", "") for b in resp.content
                if getattr(b, "type", "") == "text"
            )
            try:
                obj = _extract_json(text)
            except Exception as e:
                last_err = e
                time.sleep(min(30, 2 * attempt))
                continue
            searches, fetches = _count_server_tools(resp.content)
            return obj, resp.usage.input_tokens, resp.usage.output_tokens, searches, fetches
        except Exception as e:
            last_err = e
            msg = str(e).lower()
            sleep_s = min(30, 2 * attempt)
            if "rate" in msg or "429" in msg:
                sleep_s = min(30, 5 * attempt)
            time.sleep(sleep_s)
    raise RuntimeError(f"verifier v2 failed after {MAX_RETRIES} attempts: {last_err}")


def _collect_flags(drafts_paths: list[Path]) -> list[tuple[Path, dict[str, Any], dict[str, Any]]]:
    """Return list of (path, draft, flag) for every cannot_verify flag that lacks verdict_v2."""
    out: list[tuple[Path, dict[str, Any], dict[str, Any]]] = []
    for p in drafts_paths:
        draft = json.loads(p.read_text(encoding="utf-8"))
        for flag in (draft.get("self_critique") or {}).get("issues") or []:
            if flag.get("verdict") != "cannot_verify":
                continue
            if flag.get("verdict_v2"):
                continue
            out.append((p, draft, flag))
    return out


def _write_report(
    drafts_paths: list[Path],
    processed: list[tuple[str, dict[str, Any]]],
    skipped_count: int,
    total_cannot_verify: int,
    total_in: int,
    total_out: int,
    total_searches: int,
    total_fetches: int,
    cost: float,
    err_count: int,
) -> None:
    n = len(processed)
    global_v2 = Counter(f.get("verdict_v2", "still_cannot_verify") for _, f in processed)
    domain_hits: Counter[str] = Counter()
    for _, flag in processed:
        if flag.get("verdict_v2") in {"confirmed", "false_positive"}:
            d = _domain_of(flag.get("source_url"))
            if d:
                domain_hits[d] += 1

    # Aggregate per-draft totals (from disk — reflects committed state)
    per_draft: dict[str, dict[str, int]] = {}
    for p in drafts_paths:
        draft = json.loads(p.read_text(encoding="utf-8"))
        did = draft.get("id") or p.stem
        issues = (draft.get("self_critique") or {}).get("issues") or []
        pre_v1 = len(issues)
        c_v1 = sum(1 for i in issues if i.get("verdict") == "confirmed")
        fp_v1 = sum(1 for i in issues if i.get("verdict") == "false_positive")
        cv_v1 = sum(1 for i in issues if i.get("verdict") == "cannot_verify")
        c_v2 = sum(1 for i in issues if i.get("verdict_v2") == "confirmed")
        fp_v2 = sum(1 for i in issues if i.get("verdict_v2") == "false_positive")
        scv_v2 = sum(1 for i in issues if i.get("verdict_v2") == "still_cannot_verify")
        cv_unprocessed = sum(
            1 for i in issues
            if i.get("verdict") == "cannot_verify" and not i.get("verdict_v2")
        )
        total_confirmed = c_v1 + c_v2
        total_fp = fp_v1 + fp_v2
        community = scv_v2 + cv_unprocessed
        per_draft[did] = {
            "pre_v1": pre_v1,
            "after_v1_cv": cv_v1,
            "after_v2_scv": scv_v2 + cv_unprocessed,
            "confirmed": total_confirmed,
            "false_positive": total_fp,
            "community_needed": community,
        }

    # Final totals across all 122 flags
    total_confirmed_all = sum(d["confirmed"] for d in per_draft.values())
    total_fp_all = sum(d["false_positive"] for d in per_draft.values())
    total_community_all = sum(d["community_needed"] for d in per_draft.values())

    lines: list[str] = []
    lines.append("# Batch 1 Verifier v2 Report (web_search + whitelist)")
    lines.append("")
    lines.append(f"Data: {TODAY_ISO}")
    lines.append(f"Model: {MODEL}")
    lines.append(f"Whitelist: {len(WHITELIST)} domen ({', '.join(WHITELIST)})")
    lines.append(f"Koszt: ${cost:.4f}")
    lines.append(f"Flag to verify: {total_cannot_verify} (from cannot_verify pool)")
    lines.append(f"Flag verified: {n}/{total_cannot_verify}")
    if skipped_count:
        lines.append(f"Flag pominiętych (hit cost cap): {skipped_count}")
    lines.append(f"Error count: {err_count}")
    lines.append(f"Web searches: {total_searches}  |  Web fetches: {total_fetches}")
    lines.append("")

    def _pct(x: int, base: int) -> str:
        return f"{(100.0 * x / base):.1f}%" if base else "0%"

    lines.append("## Rozkład verdictów v2")
    for key in ("confirmed", "false_positive", "still_cannot_verify"):
        lines.append(f"- {key}: {global_v2.get(key, 0)}/{n} ({_pct(global_v2.get(key, 0), n)})")
    lines.append("")

    lines.append("## Skuteczność whitelist per domain (flagi rozstrzygnięte)")
    if domain_hits:
        for d in WHITELIST:
            lines.append(f"- {d}: {domain_hits.get(d, 0)}")
        other = sum(v for k, v in domain_hits.items() if k not in WHITELIST)
        if other:
            lines.append(f"- (inne, poza whitelist): {other}")
    else:
        lines.append("(żadna flaga nie została rozstrzygnięta przez whitelist — wszystko still_cannot_verify)")
    lines.append("")

    lines.append("## Finalne rozkłady (po v1 + v2) — wszystkie 122 flag")
    lines.append(f"- confirmed (v1 lub v2): {total_confirmed_all}")
    lines.append(f"- false_positive (v1 lub v2): {total_fp_all}")
    lines.append(f"- community_feedback_needed (still_cannot_verify + niepuszczone przez v2): {total_community_all}")
    lines.append("")

    lines.append("## Per draft status (po v1 + v2)")
    lines.append("| Draft | Pre-v1 | After v1 cv | After v2 scv | Confirmed | False_pos | Community_needed |")
    lines.append("|---|---|---|---|---|---|---|")
    for did, d in per_draft.items():
        lines.append(
            f"| {did} | {d['pre_v1']} | {d['after_v1_cv']} | {d['after_v2_scv']} | "
            f"{d['confirmed']} | {d['false_positive']} | {d['community_needed']} |"
        )
    lines.append("")

    lines.append("## Nowo confirmed flag (v2) — pełna lista")
    hits_conf = [(did, f) for did, f in processed if f.get("verdict_v2") == "confirmed"]
    if not hits_conf:
        lines.append("(brak)")
    for did, f in hits_conf:
        lines.append(f"- **Draft:** {did}")
        lines.append(f"  - Description: {f.get('description', '').strip()}")
        lines.append(f"  - Source: {f.get('source_url', '') or '(brak)'}")
        lines.append(f"  - Reasoning: {f.get('verifier_reasoning_v2', '')}")
        if f.get("source_quote"):
            lines.append(f"  - Cytat: \"{f['source_quote']}\"")
    lines.append("")

    lines.append("## Nowo false_positive flag (v2) — do 5 przykładów (sanity check)")
    hits_fp = [(did, f) for did, f in processed if f.get("verdict_v2") == "false_positive"]
    for did, f in hits_fp[:5]:
        lines.append(f"- **Draft:** {did}")
        lines.append(f"  - Description: {f.get('description', '').strip()}")
        lines.append(f"  - Source: {f.get('source_url', '') or '(brak)'}")
        lines.append(f"  - Reasoning: {f.get('verifier_reasoning_v2', '')}")
        if f.get("source_quote"):
            lines.append(f"  - Cytat: \"{f['source_quote']}\"")
    if not hits_fp:
        lines.append("(brak)")
    lines.append("")

    lines.append("## Still_cannot_verify summary")
    scv = [f for _, f in processed if f.get("verdict_v2") == "still_cannot_verify"]
    lines.append(f"Flag z verdict_v2 == still_cannot_verify: {len(scv)}")
    if scv:
        cat = Counter(f.get("type", "unknown") for f in scv)
        lines.append("Top 3 kategorie problemów (po v2):")
        for c, k in cat.most_common(3):
            lines.append(f"- {c}: {k}")
    lines.append(f"Plus {skipped_count} flag nie przetworzonych (cap kosztu) — traktowane jako community_feedback_needed.")
    lines.append("Rekomendacja: flagi z verdict_v2 == still_cannot_verify oznaczyć tagiem `community_feedback_needed` w pipeline testerów.")
    lines.append("")

    lines.append("## Rekomendacje dalszych kroków")
    ready = [did for did, d in per_draft.items() if d["confirmed"] <= 1]
    lines.append(
        "- Drafty względnie gotowe do aplikacji corrections (≤1 confirmed łącznie): "
        + (", ".join(ready) if ready else "brak")
    )
    problem = [did for did, d in per_draft.items() if d["confirmed"] >= 3]
    lines.append(
        "- Drafty do manualnego review (≥3 confirmed): "
        + (", ".join(problem) if problem else "brak")
    )
    # Categories to reinforce in batch 2 prompt
    from collections import defaultdict
    cat_conf: dict[str, int] = defaultdict(int)
    for p in drafts_paths:
        draft = json.loads(p.read_text(encoding="utf-8"))
        for f in (draft.get("self_critique") or {}).get("issues") or []:
            if f.get("verdict") == "confirmed" or f.get("verdict_v2") == "confirmed":
                cat_conf[f.get("type", "unknown")] += 1
    hot = [c for c, n in cat_conf.items() if n >= 3]
    lines.append(
        "- Kategorie do wzmocnienia w prompt Opusa dla batch 2 (≥3 confirmed łącznie): "
        + (", ".join(hot) if hot else "brak")
    )
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    _load_env()
    import anthropic

    client = anthropic.Anthropic()

    drafts_paths = sorted(DRAFTS_DIR.glob("wf_*.json"))
    flags_queue = _collect_flags(drafts_paths)
    total_cannot_verify = len(flags_queue)
    print(f"Cannot_verify flags to process: {total_cannot_verify}")

    # Sort by severity high > medium > low (stable)
    flags_queue.sort(key=lambda t: SEVERITY_RANK.get(str(t[2].get("severity", "low")).lower(), 9))

    processed: list[tuple[str, dict[str, Any]]] = []
    total_in = 0
    total_out = 0
    total_searches = 0
    total_fetches = 0
    err_count = 0
    stopped_early = False

    # Group by path so we write each file once after processing all its flags.
    # We also write after every N flags to avoid losing work on crash.
    dirty_paths: set[Path] = set()

    for i, (p, draft, flag) in enumerate(flags_queue, start=1):
        cost_so_far = (
            total_in / 1000 * PRICE_IN_PER_1K
            + total_out / 1000 * PRICE_OUT_PER_1K
            + total_searches * PRICE_PER_SEARCH
        )
        if cost_so_far >= COST_HARD_CAP:
            print(f"\nCOST CAP approached at ${cost_so_far:.4f} >= ${COST_HARD_CAP}. Stopping.")
            stopped_early = True
            break
        try:
            raw, in_tok, out_tok, searches, fetches = verify_flag_v2(client, flag, draft)
            total_in += in_tok
            total_out += out_tok
            total_searches += searches
            total_fetches += fetches
            verdict_v2 = _normalize_verdict_v2(raw.get("verdict_v2"))
            flag["verdict_v2"] = verdict_v2
            flag["verifier_reasoning_v2"] = str(raw.get("reasoning") or "").strip()
            try:
                flag["verifier_confidence_v2"] = float(raw.get("confidence") or 0.0)
            except Exception:
                flag["verifier_confidence_v2"] = 0.0
            # Source URL: only keep if whitelisted
            src = raw.get("source_url") or ""
            if src and _is_whitelisted(src):
                flag["source_url"] = src
            elif src:
                flag["source_url"] = ""
                flag["verifier_reasoning_v2"] = (
                    flag["verifier_reasoning_v2"]
                    + f" [UWAGA: oryginalny source_url {src} poza whitelistą — usunięty]"
                )
            flag["source_quote"] = _truncate_quote(str(raw.get("source_quote") or "").strip())
            flag["verified_at_v2"] = now_iso_utc()
            flag["verified_by_v2"] = MODEL
            flag["web_searches_used"] = searches
            flag["web_fetches_used"] = fetches
        except Exception as e:
            err_count += 1
            flag["verdict_v2"] = "still_cannot_verify"
            flag["verifier_reasoning_v2"] = f"ERROR: {e}"
            flag["verifier_confidence_v2"] = 0.0
            flag["source_url"] = ""
            flag["source_quote"] = ""
            flag["verified_at_v2"] = now_iso_utc()
            flag["verified_by_v2"] = MODEL

        did = draft.get("id") or p.stem
        processed.append((did, flag))
        dirty_paths.add(p)

        cost_now = (
            total_in / 1000 * PRICE_IN_PER_1K
            + total_out / 1000 * PRICE_OUT_PER_1K
            + total_searches * PRICE_PER_SEARCH
        )
        print(
            f"[{i}/{total_cannot_verify}] {did[:45]} sev={flag.get('severity'):6} "
            f"verdict={flag['verdict_v2']:20} in={in_tok if 'in_tok' in dir() else 0} "
            f"out={out_tok if 'out_tok' in dir() else 0} "
            f"s={searches if 'searches' in dir() else 0} f={fetches if 'fetches' in dir() else 0} "
            f"cost=${cost_now:.4f}"
        )

        if i % COST_LOG_EVERY == 0:
            print(f"  --- checkpoint at flag {i}: cost=${cost_now:.4f}, searches={total_searches}, fetches={total_fetches}")
            # Flush all modified drafts to disk.
            for path in list(dirty_paths):
                d = json.loads(path.read_text(encoding="utf-8"))
                # Identify by inspection — load fresh, overwrite just the matching flag's verdict_v2 fields
                # Easier: since we mutated the in-memory draft object, persist it.
                # But dirty_paths tracks paths for many drafts; we need the current draft obj per path.
            # Simpler: we persist after each flag for safety
        # Persist draft after each flag (cheap JSON write) for crash safety
        p.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")

        time.sleep(RATE_LIMIT_S)

    # Final flush
    for p in dirty_paths:
        pass  # already persisted per-flag

    cost = (
        total_in / 1000 * PRICE_IN_PER_1K
        + total_out / 1000 * PRICE_OUT_PER_1K
        + total_searches * PRICE_PER_SEARCH
    )
    skipped = total_cannot_verify - len(processed)
    print(
        f"\nDone. verified={len(processed)}/{total_cannot_verify} skipped={skipped} "
        f"in={total_in} out={total_out} searches={total_searches} fetches={total_fetches} "
        f"cost=${cost:.4f} errors={err_count}"
    )

    _write_report(drafts_paths, processed, skipped, total_cannot_verify, total_in, total_out, total_searches, total_fetches, cost, err_count)
    print(f"Report: {REPORT_PATH}")
    return 2 if stopped_early else 0


if __name__ == "__main__":
    raise SystemExit(main())
