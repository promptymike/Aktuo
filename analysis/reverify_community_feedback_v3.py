"""Verifier v3: re-verify community_feedback_needed flags with expanded 12-domain whitelist.

Targets 329 flags tagged `final_status == "community_feedback_needed"` after v2.
Whitelist adds: eureka.mf.gov.pl (tax interpretations), orzeczenia.nsa.gov.pl
(NSA/WSA court rulings), stat.gov.pl (GUS statistics). Mutates each flag in
place to add verdict_v3 + verifier_reasoning_v3 (+ source_url_v3 + source_quote_v3).
Updates final_status if v3 resolves (confirmed/false_positive). Stops at COST_HARD_CAP.
"""

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DRAFTS_DIR = ROOT / "data" / "workflow_drafts"
REPORT_PATH = ROOT / "analysis" / "batch_all_verifier_v3_report.md"
ENV_PATH = ROOT / ".env"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1000
TEMPERATURE = 0.1
MAX_RETRIES = 3
RATE_LIMIT_S = 1.0
PRICE_IN_PER_1K = 0.003
PRICE_OUT_PER_1K = 0.015
PRICE_PER_SEARCH = 0.01
COST_HARD_CAP = 12.00
COST_LOG_EVERY = 30

WHITELIST = [
    # Original 9
    "gofin.pl",
    "interpretacje.gofin.pl",
    "podatki.gov.pl",
    "zus.pl",
    "biznes.gov.pl",
    "sejm.gov.pl",
    "isap.sejm.gov.pl",
    "ksiegowosc.infor.pl",
    "podatki.biz",
    # New in v3
    "eureka.mf.gov.pl",
    "orzeczenia.nsa.gov.pl",
    "stat.gov.pl",
]
NEW_DOMAINS_V3 = {"eureka.mf.gov.pl", "orzeczenia.nsa.gov.pl", "stat.gov.pl"}

TODAY_ISO = "2026-04-18"
SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}

SYSTEM_PROMPT = """Jesteś ekspertem weryfikującym czy flaga wątpliwości w drafcie workflow jest uzasadniona.

Ta weryfikacja to TRZECIE przejście — flaga już była sprawdzana w v1 (KB) i v2 (9 domen web),
ale poprzednie przejścia nie rozstrzygnęły sprawy. Teraz masz rozszerzoną whitelist z 12 domen.

Dostajesz:
1. Flagę (type, severity, description) od self_critic
2. Oryginalny fragment drafta
3. Narzędzia web_search i web_fetch ograniczone do 12 zaufanych polskich źródeł:
   - gofin.pl, interpretacje.gofin.pl — komentarze/praktyka księgowa
   - podatki.gov.pl — Ministerstwo Finansów (komunikaty urzędowe)
   - zus.pl — Zakład Ubezpieczeń Społecznych
   - biznes.gov.pl — praktyczne info dla firm
   - sejm.gov.pl, isap.sejm.gov.pl — teksty ustaw i rozporządzeń
   - ksiegowosc.infor.pl, podatki.biz — praktyka księgowo-podatkowa
   - **eureka.mf.gov.pl** — OFICJALNA baza interpretacji indywidualnych Ministra Finansów (NAJWYŻSZY autorytet dla sporów podatkowych)
   - **orzeczenia.nsa.gov.pl** — OFICJALNA baza orzecznictwa NSA i WSA (autorytet dla step_contradiction, interpretacji przepisów)
   - **stat.gov.pl** — GUS (oficjalne wskaźniki: minimalne wynagrodzenie, przeciętne wynagrodzenie, dane statystyczne używane w kadrach — najbardziej aktualne źródło dla outdated_data_risk)

Twoja rola: zweryfikować czy flaga to prawdziwy problem czy false positive, używając TYLKO tych 12 zaufanych źródeł.

Strategia wyboru domen (sugerowana):
- type "legal_anchor_uncertainty" → preferuj eureka.mf.gov.pl, isap.sejm.gov.pl, orzeczenia.nsa.gov.pl
- type "step_contradiction" → preferuj orzeczenia.nsa.gov.pl, eureka.mf.gov.pl, podatki.gov.pl
- type "outdated_data_risk" → preferuj stat.gov.pl, podatki.gov.pl, gofin.pl
- type "missing_critical_info" / "hallucination_risk" → dowolne z whitelisty, zacznij od najbardziej autorytatywnego
- type "edge_case_coverage" → preferuj gofin.pl, ksiegowosc.infor.pl (praktyka), eureka (interpretacje)

Zasady pracy:
- Najpierw wykonaj 1 web_search z krótką, konkretną frazą (maks 6 słów).
- Jeśli trzeba pogłębić, możesz opcjonalnie wykonać 1 web_fetch na najbardziej obiecujący URL z whitelisty.
- Jeśli snippet z web_search wystarcza — NIE wykonuj web_fetch.

Na końcu zwracasz DOKŁADNIE JEDEN obiekt JSON (bez dodatkowego tekstu):
{
  "verdict_v3": "confirmed" | "false_positive" | "still_cannot_verify",
  "confidence": 0.0-1.0,
  "reasoning": "1-3 zdania z konkretnym odniesieniem do znalezionego źródła",
  "source_url": "URL tylko jeśli znaleziono potwierdzenie/obalenie (MUSI być z whitelist)",
  "source_quote": "BARDZO KRÓTKI dosłowny cytat max 10 słów ze źródła (copyright)"
}

Definicje:
- "confirmed" = źródło potwierdza że flaga jest słuszna (draft jest błędny)
- "false_positive" = źródło potwierdza że draft jest poprawny
- "still_cannot_verify" = źródła z whitelisty (nawet rozszerzonej) nie rozstrzygają sprawy

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
    topic = draft.get("topic_area") or ""
    arts = re.findall(r"art\.?\s*\d+[a-zA-Z]*", flag.get("description", "") or "", re.I)
    first_art = arts[0] if arts else ""
    caps = re.findall(r"[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{3,}", flag.get("description", "") or "")
    picks = [w for w in caps if w.lower() not in {"draft", "step"}][:2]
    parts = [first_art] + picks
    if topic and topic not in " ".join(parts):
        parts.append(topic)
    if not any(parts):
        words = re.findall(r"\w{4,}", flag.get("description", "") or "")
        parts = words[:3]
    q = " ".join(p for p in parts if p)
    return " ".join(q.split()[:6])


def build_user_prompt(flag: dict[str, Any], draft: dict[str, Any]) -> str:
    section = _relevant_draft_section(flag, draft)
    hint = _hint_query(flag, draft)
    # Mention prior verdicts so model knows this is 3rd pass
    prior_v1 = flag.get("verdict") or "(brak)"
    prior_v2 = flag.get("verdict_v2") or "(brak — nie weryfikowane w v2)"
    return (
        "FLAGA DO WERYFIKACJI (TRZECIE przejście, v3):\n"
        f"Type: {flag.get('type')}\n"
        f"Severity: {flag.get('severity')}\n"
        f"Description: {flag.get('description')}\n"
        f"Verdict v1 (KB): {prior_v1}\n"
        f"Verdict v2 (web 9 domen): {prior_v2}\n\n"
        "FRAGMENT DRAFTA:\n"
        f"{section}\n\n"
        f"Sugerowane zapytanie do web_search (możesz użyć lub zmienić): \"{hint}\"\n\n"
        "Zweryfikuj flagę z użyciem web_search (i opcjonalnie web_fetch), korzystając tylko z whitelisty 12 domen. "
        "Szczególnie rozważ eureka.mf.gov.pl / orzeczenia.nsa.gov.pl / stat.gov.pl które nie były dostępne w v2. "
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


def _normalize_verdict_v3(v: Any) -> str:
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
    return any(host == d or host.endswith("." + d) for d in WHITELIST) or any(
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


def verify_flag_v3(client: Any, flag: dict[str, Any], draft: dict[str, Any]) -> tuple[dict[str, Any], int, int, int, int]:
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
    raise RuntimeError(f"verifier v3 failed after {MAX_RETRIES} attempts: {last_err}")


def _collect_flags(drafts_paths: list[Path]) -> list[tuple[Path, dict[str, Any], dict[str, Any]]]:
    """Flags with final_status == 'community_feedback_needed' and no verdict_v3 yet."""
    out: list[tuple[Path, dict[str, Any], dict[str, Any]]] = []
    for p in drafts_paths:
        draft = json.loads(p.read_text(encoding="utf-8"))
        for flag in (draft.get("self_critique") or {}).get("issues") or []:
            if flag.get("final_status") != "community_feedback_needed":
                continue
            if flag.get("verdict_v3"):
                continue
            out.append((p, draft, flag))
    return out


def _write_report(
    drafts_paths: list[Path],
    processed: list[tuple[str, dict[str, Any]]],
    skipped_count: int,
    total_pool: int,
    total_in: int,
    total_out: int,
    total_searches: int,
    total_fetches: int,
    cost: float,
    err_count: int,
) -> None:
    n = len(processed)
    global_v3 = Counter(f.get("verdict_v3", "still_cannot_verify") for _, f in processed)

    # Resolved = confirmed OR false_positive via v3
    resolved_flags = [(did, f) for did, f in processed if f.get("verdict_v3") in {"confirmed", "false_positive"}]

    # Domain breakdown (resolved only)
    domain_hits: Counter[str] = Counter()
    for _, flag in resolved_flags:
        d = _domain_of(flag.get("source_url_v3"))
        if d:
            domain_hits[d] += 1

    # New-domain contribution (eureka / NSA / GUS)
    new_domain_contribution = {d: domain_hits.get(d, 0) for d in NEW_DOMAINS_V3}

    # By type
    type_resolved: dict[str, dict[str, int]] = defaultdict(lambda: {"confirmed": 0, "false_positive": 0, "still": 0, "total": 0})
    for _, f in processed:
        t = f.get("type", "unknown")
        type_resolved[t]["total"] += 1
        v3 = f.get("verdict_v3", "still_cannot_verify")
        if v3 == "confirmed":
            type_resolved[t]["confirmed"] += 1
        elif v3 == "false_positive":
            type_resolved[t]["false_positive"] += 1
        else:
            type_resolved[t]["still"] += 1

    # Per-draft final totals (reading fresh from disk)
    per_draft: dict[str, dict[str, Any]] = {}
    for p in drafts_paths:
        draft = json.loads(p.read_text(encoding="utf-8"))
        did = draft.get("id") or p.stem
        issues = (draft.get("self_critique") or {}).get("issues") or []
        total_flags = len(issues)
        confirmed = sum(
            1 for i in issues
            if i.get("verdict") == "confirmed"
            or i.get("verdict_v2") == "confirmed"
            or i.get("verdict_v3") == "confirmed"
        )
        fp = sum(
            1 for i in issues
            if i.get("verdict") == "false_positive"
            or i.get("verdict_v2") == "false_positive"
            or i.get("verdict_v3") == "false_positive"
        )
        community = sum(1 for i in issues if i.get("final_status") == "community_feedback_needed")
        pct_uncertain = (100.0 * community / total_flags) if total_flags else 0.0
        per_draft[did] = {
            "total": total_flags,
            "confirmed": confirmed,
            "false_positive": fp,
            "community": community,
            "pct_uncertain": pct_uncertain,
        }

    total_confirmed_all = sum(d["confirmed"] for d in per_draft.values())
    total_fp_all = sum(d["false_positive"] for d in per_draft.values())
    total_community_all = sum(d["community"] for d in per_draft.values())
    total_flags_all = sum(d["total"] for d in per_draft.values())

    lines: list[str] = []
    lines.append("# Verifier v3 Report — Re-weryfikacja community_feedback_needed (wszystkie 42 drafty)")
    lines.append("")
    lines.append(f"Data: {TODAY_ISO}")
    lines.append(f"Model: {MODEL}")
    lines.append(f"Whitelist: {len(WHITELIST)} domen (9 z v2 + {', '.join(sorted(NEW_DOMAINS_V3))})")
    lines.append(f"Hard cap: ${COST_HARD_CAP:.2f}")
    lines.append(f"Koszt: ${cost:.4f}")
    lines.append(f"Pool: {total_pool} flag (final_status == community_feedback_needed po v2)")
    lines.append(f"Przetworzone: {n}/{total_pool}")
    if skipped_count:
        lines.append(f"Pominięte (cap lub resume): {skipped_count}")
    lines.append(f"Error count: {err_count}")
    lines.append(f"Web searches: {total_searches}  |  Web fetches: {total_fetches}")
    lines.append("")

    def _pct(x: int, base: int) -> str:
        return f"{(100.0 * x / base):.1f}%" if base else "0%"

    lines.append("## Rozkład verdictów v3")
    for key in ("confirmed", "false_positive", "still_cannot_verify"):
        lines.append(f"- {key}: {global_v3.get(key, 0)}/{n} ({_pct(global_v3.get(key, 0), n)})")
    lines.append("")

    lines.append(f"**Resolved by v3:** {len(resolved_flags)}/{n} ({_pct(len(resolved_flags), n)})")
    lines.append("")

    lines.append("## Skuteczność per domena (flagi rozstrzygnięte przez v3)")
    if domain_hits:
        for d in WHITELIST:
            hits = domain_hits.get(d, 0)
            marker = " **(NOWA w v3)**" if d in NEW_DOMAINS_V3 else ""
            lines.append(f"- {d}: {hits}{marker}")
        other = sum(v for k, v in domain_hits.items() if k not in WHITELIST)
        if other:
            lines.append(f"- (inne, poza whitelist): {other}")
    else:
        lines.append("(żadna flaga nie rozstrzygnięta — wszystko still_cannot_verify)")
    lines.append("")

    lines.append("## Wkład nowych domen (eureka / NSA / GUS)")
    total_new = sum(new_domain_contribution.values())
    lines.append(f"Łącznie flag rozstrzygniętych przez nowe domeny: {total_new}")
    for d, c in new_domain_contribution.items():
        lines.append(f"- {d}: {c}")
    lines.append("")

    lines.append("## Resolucja per typ flagi")
    lines.append("| Type | Total | Confirmed | False_pos | Still | Resolved% |")
    lines.append("|---|---|---|---|---|---|")
    for t, d in sorted(type_resolved.items(), key=lambda x: -x[1]["total"]):
        resolved = d["confirmed"] + d["false_positive"]
        pct = _pct(resolved, d["total"])
        lines.append(f"| {t} | {d['total']} | {d['confirmed']} | {d['false_positive']} | {d['still']} | {pct} |")
    lines.append("")

    lines.append("## Finalne rozkłady po v1+v2+v3 — wszystkie 476 flag z 42 draftów")
    lines.append(f"- Łącznie flag: {total_flags_all}")
    lines.append(f"- Confirmed (v1+v2+v3): {total_confirmed_all}")
    lines.append(f"- False_positive (v1+v2+v3): {total_fp_all}")
    lines.append(f"- Community_feedback_needed (wciąż nierozstrzygnięte): {total_community_all}")
    lines.append("")

    lines.append("## Top 5 nowo confirmed flag w v3")
    hits_conf = [(did, f) for did, f in processed if f.get("verdict_v3") == "confirmed"]
    for did, f in hits_conf[:5]:
        lines.append(f"- **Draft:** {did}")
        lines.append(f"  - Type: {f.get('type')} | Severity: {f.get('severity')}")
        lines.append(f"  - Description: {f.get('description', '').strip()}")
        lines.append(f"  - Source: {f.get('source_url_v3', '') or '(brak)'}")
        lines.append(f"  - Reasoning: {f.get('verifier_reasoning_v3', '')}")
        if f.get("source_quote_v3"):
            lines.append(f"  - Cytat: \"{f['source_quote_v3']}\"")
    if not hits_conf:
        lines.append("(brak)")
    lines.append("")

    lines.append("## Top 3 nowo false_positive flag w v3 (sanity check)")
    hits_fp = [(did, f) for did, f in processed if f.get("verdict_v3") == "false_positive"]
    for did, f in hits_fp[:3]:
        lines.append(f"- **Draft:** {did}")
        lines.append(f"  - Type: {f.get('type')} | Severity: {f.get('severity')}")
        lines.append(f"  - Description: {f.get('description', '').strip()}")
        lines.append(f"  - Source: {f.get('source_url_v3', '') or '(brak)'}")
        lines.append(f"  - Reasoning: {f.get('verifier_reasoning_v3', '')}")
        if f.get("source_quote_v3"):
            lines.append(f"  - Cytat: \"{f['source_quote_v3']}\"")
    if not hits_fp:
        lines.append("(brak)")
    lines.append("")

    lines.append("## Per draft — finalny status po v3")
    lines.append("| Draft | Total | Confirmed | False_pos | Community | % uncertain |")
    lines.append("|---|---|---|---|---|---|")
    for did, d in sorted(per_draft.items(), key=lambda x: x[1]["pct_uncertain"]):
        lines.append(
            f"| {did} | {d['total']} | {d['confirmed']} | {d['false_positive']} | "
            f"{d['community']} | {d['pct_uncertain']:.0f}% |"
        )
    lines.append("")

    lines.append("## Rekomendacje")
    ready = [did for did, d in per_draft.items() if d["pct_uncertain"] < 30.0]
    heavy = [did for did, d in per_draft.items() if d["pct_uncertain"] > 60.0]
    lines.append(f"- **Ready for testers (<30% uncertainty):** {len(ready)} draftów")
    if ready:
        lines.append("  - " + ", ".join(ready))
    lines.append(f"- **Heavy review needed (>60% uncertainty):** {len(heavy)} draftów")
    if heavy:
        lines.append("  - " + ", ".join(heavy))
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def _rebuild_community_feedback_summary(drafts_paths: list[Path]) -> None:
    """Rewrite batch2_community_feedback_summary.md to reflect post-v3 state."""
    summary_path = ROOT / "analysis" / "batch2_community_feedback_summary.md"
    by_type: Counter[str] = Counter()
    by_severity: Counter[str] = Counter()
    per_draft_rows: list[tuple[str, int, int, int, int]] = []
    total_community = 0
    drafts_touched = 0

    for p in drafts_paths:
        draft = json.loads(p.read_text(encoding="utf-8"))
        did = draft.get("id") or p.stem
        issues = (draft.get("self_critique") or {}).get("issues") or []
        cnt_c = sum(
            1 for i in issues
            if i.get("verdict") == "confirmed"
            or i.get("verdict_v2") == "confirmed"
            or i.get("verdict_v3") == "confirmed"
        )
        cnt_fp = sum(
            1 for i in issues
            if i.get("verdict") == "false_positive"
            or i.get("verdict_v2") == "false_positive"
            or i.get("verdict_v3") == "false_positive"
        )
        community_issues = [i for i in issues if i.get("final_status") == "community_feedback_needed"]
        cnt_com = len(community_issues)
        if cnt_com:
            drafts_touched += 1
        total_community += cnt_com
        for f in community_issues:
            by_type[f.get("type", "unknown")] += 1
            by_severity[str(f.get("severity", "low")).lower()] += 1
        per_draft_rows.append((did, cnt_c, cnt_fp, cnt_com, len(issues)))

    per_draft_rows.sort(key=lambda r: -r[3])

    lines: list[str] = []
    lines.append("# Batch 2 Community Feedback Needed Summary (all drafts, post v3)")
    lines.append("")
    lines.append("Scope: wszystkie 42 drafty (10 batch 1 + 32 batch 2).")
    lines.append(f"Total community_feedback_needed flags (po v3): **{total_community}**")
    lines.append(f"Drafts touched: {drafts_touched}/42")
    lines.append("")
    lines.append("## By type")
    lines.append("| Type | Count |")
    lines.append("|---|---|")
    for t, c in by_type.most_common():
        lines.append(f"| {t} | {c} |")
    lines.append("")
    lines.append("## By severity")
    lines.append("| Severity | Count |")
    lines.append("|---|---|")
    for s in ("high", "medium", "low"):
        lines.append(f"| {s} | {by_severity.get(s, 0)} |")
    lines.append("")
    lines.append("## Per draft")
    lines.append("| Draft | Confirmed | False_pos | Community_feedback | Total flags |")
    lines.append("|---|---|---|---|---|")
    for did, c, fp, com, total in per_draft_rows:
        lines.append(f"| {did} | {c} | {fp} | {com} | {total} |")
    lines.append("")

    summary_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    _load_env()
    import anthropic

    client = anthropic.Anthropic(timeout=300.0)

    drafts_paths = sorted(DRAFTS_DIR.glob("wf_*.json"))
    flags_queue = _collect_flags(drafts_paths)
    total_pool = len(flags_queue)
    print(f"Community_feedback flags to process: {total_pool}")

    flags_queue.sort(key=lambda t: SEVERITY_RANK.get(str(t[2].get("severity", "low")).lower(), 9))

    processed: list[tuple[str, dict[str, Any]]] = []
    total_in = 0
    total_out = 0
    total_searches = 0
    total_fetches = 0
    err_count = 0
    stopped_early = False
    dirty_paths: set[Path] = set()

    for i, (p, draft, flag) in enumerate(flags_queue, start=1):
        cost_so_far = (
            total_in / 1000 * PRICE_IN_PER_1K
            + total_out / 1000 * PRICE_OUT_PER_1K
            + total_searches * PRICE_PER_SEARCH
        )
        if cost_so_far >= COST_HARD_CAP:
            print(f"\nCOST CAP approached at ${cost_so_far:.4f} >= ${COST_HARD_CAP}. Stopping.", flush=True)
            stopped_early = True
            break

        in_tok = 0
        out_tok = 0
        searches = 0
        fetches = 0
        try:
            raw, in_tok, out_tok, searches, fetches = verify_flag_v3(client, flag, draft)
            total_in += in_tok
            total_out += out_tok
            total_searches += searches
            total_fetches += fetches
            verdict_v3 = _normalize_verdict_v3(raw.get("verdict_v3"))
            flag["verdict_v3"] = verdict_v3
            flag["verifier_reasoning_v3"] = str(raw.get("reasoning") or "").strip()
            try:
                flag["verifier_confidence_v3"] = float(raw.get("confidence") or 0.0)
            except Exception:
                flag["verifier_confidence_v3"] = 0.0
            src = raw.get("source_url") or ""
            if src and _is_whitelisted(src):
                flag["source_url_v3"] = src
            elif src:
                flag["source_url_v3"] = ""
                flag["verifier_reasoning_v3"] = (
                    flag["verifier_reasoning_v3"]
                    + f" [UWAGA: oryginalny source_url {src} poza whitelistą — usunięty]"
                )
            else:
                flag["source_url_v3"] = ""
            flag["source_quote_v3"] = _truncate_quote(str(raw.get("source_quote") or "").strip())
            flag["verified_at_v3"] = now_iso_utc()
            flag["verified_by_v3"] = MODEL
            flag["web_searches_used_v3"] = searches
            flag["web_fetches_used_v3"] = fetches

            # Update final_status if v3 resolved the flag
            if verdict_v3 in {"confirmed", "false_positive"}:
                flag["final_status"] = verdict_v3
                # Clear the UI label since flag is now resolved, not community-feedback
                if "ui_label" in flag:
                    flag["ui_label"] = None
        except Exception as e:
            err_count += 1
            flag["verdict_v3"] = "still_cannot_verify"
            flag["verifier_reasoning_v3"] = f"ERROR: {e}"
            flag["verifier_confidence_v3"] = 0.0
            flag["source_url_v3"] = ""
            flag["source_quote_v3"] = ""
            flag["verified_at_v3"] = now_iso_utc()
            flag["verified_by_v3"] = MODEL

        did = draft.get("id") or p.stem
        processed.append((did, flag))
        dirty_paths.add(p)

        cost_now = (
            total_in / 1000 * PRICE_IN_PER_1K
            + total_out / 1000 * PRICE_OUT_PER_1K
            + total_searches * PRICE_PER_SEARCH
        )
        print(
            f"[{i}/{total_pool}] {did[:45]:45} sev={str(flag.get('severity')):6} "
            f"v3={flag['verdict_v3']:20} in={in_tok} out={out_tok} "
            f"s={searches} f={fetches} cost=${cost_now:.4f}",
            flush=True,
        )

        if i % COST_LOG_EVERY == 0:
            print(
                f"  --- checkpoint at flag {i}: cost=${cost_now:.4f}, "
                f"searches={total_searches}, fetches={total_fetches}",
                flush=True,
            )

        # Persist draft after each flag (crash safety)
        p.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")

        time.sleep(RATE_LIMIT_S)

    cost = (
        total_in / 1000 * PRICE_IN_PER_1K
        + total_out / 1000 * PRICE_OUT_PER_1K
        + total_searches * PRICE_PER_SEARCH
    )
    skipped = total_pool - len(processed)
    print(
        f"\nDone. verified={len(processed)}/{total_pool} skipped={skipped} "
        f"in={total_in} out={total_out} searches={total_searches} fetches={total_fetches} "
        f"cost=${cost:.4f} errors={err_count}",
        flush=True,
    )

    _write_report(drafts_paths, processed, skipped, total_pool, total_in, total_out, total_searches, total_fetches, cost, err_count)
    print(f"Report: {REPORT_PATH}", flush=True)

    _rebuild_community_feedback_summary(drafts_paths)
    print(f"Rewritten: analysis/batch2_community_feedback_summary.md", flush=True)

    return 2 if stopped_early else 0


if __name__ == "__main__":
    raise SystemExit(main())
