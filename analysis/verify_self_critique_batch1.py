"""Verifier layer for self_critique flags in batch 1 workflow drafts.

For each flag in data/workflow_drafts/wf_*.json self_critique.issues, call Sonnet 4.6
with the flag + relevant draft section + retrieved KB records from
data/seeds/law_knowledge.json, producing a verdict
(confirmed / false_positive / cannot_verify) with reasoning.

Mutates each wf_*.json in place to append verdict + verifier_reasoning + verifier_confidence
(+ optional corrective_suggestion) per issue. Writes analysis/batch1_verifier_report.md.
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

ROOT = Path(__file__).resolve().parents[1]
KB_PATH = ROOT / "data" / "seeds" / "law_knowledge.json"
DRAFTS_DIR = ROOT / "data" / "workflow_drafts"
REPORT_PATH = ROOT / "analysis" / "batch1_verifier_report.md"
ENV_PATH = ROOT / ".env"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 800
TEMPERATURE = 0.1
MAX_RETRIES = 3
RATE_LIMIT_S = 0.5
PRICE_IN_PER_1K = 0.003
PRICE_OUT_PER_1K = 0.015
COST_HARD_CAP = 1.50

TODAY_ISO = "2026-04-18"

SYSTEM_PROMPT = """Jesteś ekspertem weryfikującym czy flaga wątpliwości w draft workflow rekord jest uzasadniona.

Dostajesz:
1. Flagę (type, severity, description) od self_critic
2. Oryginalny fragment drafta którego dotyczy flaga
3. Relevantne rekordy z KB (ustawy polskie, 4472 rekordów)

Twoja rola: zweryfikować czy flaga to prawdziwy problem czy false positive.

Zwracasz JSON:
{
  "verdict": "confirmed" | "false_positive" | "cannot_verify",
  "confidence": 0.0-1.0,
  "reasoning": "1-3 zdania konkretne, cytowanie artykułów jeśli relevantne",
  "corrective_suggestion": "opcjonalnie - jak poprawić draft jeśli confirmed"
}

Zasady:
- "confirmed" = znalazłeś w KB dowód że flaga jest słuszna (np. artykuł faktycznie inaczej brzmi, dane są nieaktualne)
- "false_positive" = znalazłeś w KB dowód że draft jest poprawny (np. art. 87¹ KP istnieje i tak się go cytuje)
- "cannot_verify" = KB nie pokrywa tematu albo nie możesz jednoznacznie ocenić

BĄDŹ OSTROŻNY z "confirmed" - wymagaj twardego dowodu. Jeśli masz wątpliwości → "cannot_verify".
BĄDŹ OSTROŻNY z "false_positive" - nie odfiltrowuj flagi tylko dlatego że "prawdopodobnie OK".

ODPOWIEDŹ TYLKO JAKO JSON (bez dodatkowego tekstu)."""

# Polish-law-name detection in free text (flag description + draft legal_anchors).
LAW_HINTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(?:ustaw[ay]|ustawy)?\s*(?:o\s+)?VAT\b|\bKSeF\b", re.I), "Ustawa o VAT"),
    (re.compile(r"\bKodeks(?:u|em)?\s+pracy\b|\bKP\b", re.I), "Kodeks pracy"),
    (re.compile(r"\bPIT\b|\bpodatku\s+dochodowego\s+od\s+os(?:ó|o)b\s+fizycznych\b", re.I), "Ustawa o podatku dochodowym od osób fizycznych"),
    (re.compile(r"\bCIT\b|\bpodatku\s+dochodowego\s+od\s+os(?:ó|o)b\s+prawnych\b", re.I), "Ustawa o podatku dochodowym od osób prawnych"),
    (re.compile(r"\bOrdynacj[aei]\s+podatkowa?\b", re.I), "Ordynacja podatkowa"),
    (re.compile(r"\bubezpiecze(?:ń|n)\s+spo(?:ł|l)ecznych\b|\bZUS\b", re.I), "Ustawa o systemie ubezpieczeń społecznych"),
    (re.compile(r"\brachunkowo(?:ś|s)ci\b|\bUoR\b", re.I), "Ustawa o rachunkowości"),
    (re.compile(r"\brycza(?:ł|l)t(?:owy|owego|owego\s+podatku)?\b", re.I), "Ustawa o zryczałtowanym podatku dochodowym"),
    (re.compile(r"\bkas(?:ach|y|ami)\s+rejestruj(?:ą|a)cych\b", re.I), "Rozporządzenie MF o kasach rejestrujących"),
    (re.compile(r"\bJPK[_ ]?V7\b|\bJPK\b", re.I), "Rozporządzenie JPK_V7"),
]

ARTICLE_RE = re.compile(
    r"(?:art\.?\s*|§\s*)(\d+[a-zA-Z]*)",
    re.I,
)


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


def _derive_laws(flag: dict[str, Any], draft: dict[str, Any]) -> set[str]:
    text = flag.get("description", "") or ""
    laws: set[str] = set()
    for rx, canonical in LAW_HINTS:
        if rx.search(text):
            laws.add(canonical)
    for la in draft.get("legal_anchors", []) or []:
        ln = la.get("law_name") or ""
        for rx, canonical in LAW_HINTS:
            if rx.search(ln):
                laws.add(canonical)
    return laws


def _derive_articles(flag: dict[str, Any], draft: dict[str, Any]) -> list[str]:
    arts: list[str] = []
    for m in ARTICLE_RE.finditer(flag.get("description", "") or ""):
        a = m.group(1)
        if a and a not in arts:
            arts.append(a)
    if flag.get("type") == "legal_anchor_uncertainty":
        for la in draft.get("legal_anchors", []) or []:
            an = la.get("article_number") or ""
            for m in ARTICLE_RE.finditer(an):
                a = m.group(1)
                if a and a not in arts:
                    arts.append(a)
    return arts


def retrieve_kb(flag: dict[str, Any], draft: dict[str, Any], kb: list[dict[str, Any]]) -> list[dict[str, Any]]:
    laws = _derive_laws(flag, draft)
    arts = _derive_articles(flag, draft)
    desc = flag.get("description", "") or ""
    tokens = [w.lower() for w in re.findall(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]{5,}", desc)]
    # dedupe, keep top 10 distinct
    seen = set()
    tokens_unique: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            tokens_unique.append(t)
        if len(tokens_unique) >= 10:
            break

    scored: list[tuple[int, dict[str, Any]]] = []
    for rec in kb:
        score = 0
        ln = rec.get("law_name") or ""
        if laws and ln in laws:
            score += 3
        an = rec.get("article_number") or ""
        for a in arts:
            if re.search(r"(?<![0-9a-zA-Z])" + re.escape(a) + r"(?![0-9a-zA-Z])", an, re.I):
                score += 5
        content_lc = ((rec.get("content") or "") + " " + (rec.get("question_intent") or "")).lower()
        if tokens_unique:
            hits = sum(1 for t in tokens_unique if t in content_lc)
            score += hits
        if score > 0:
            scored.append((score, rec))
    scored.sort(key=lambda x: (-x[0], -len(x[1].get("content", "") or "")))
    return [r for _, r in scored[:3]]


def relevant_draft_section(flag: dict[str, Any], draft: dict[str, Any]) -> str:
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


def build_user_prompt(flag: dict[str, Any], draft: dict[str, Any], kb_hits: list[dict[str, Any]]) -> str:
    section = relevant_draft_section(flag, draft)
    if kb_hits:
        kb_block = "\n\n".join(
            f"[rec {i + 1}] {r.get('law_name', '')} {r.get('article_number', '')}\n"
            f"content: {r.get('content', '')}"
            for i, r in enumerate(kb_hits)
        )
    else:
        kb_block = "(brak trafień w KB — KB nie pokrywa tego tematu)"
    return (
        "FLAGA DO WERYFIKACJI:\n"
        f"Type: {flag.get('type')}\n"
        f"Severity: {flag.get('severity')}\n"
        f"Description: {flag.get('description')}\n\n"
        "FRAGMENT DRAFTA (ten do którego odnosi się flaga):\n"
        f"{section}\n\n"
        f"KONTEKST Z KB AKTUO ({len(kb_hits)} relevantnych rekordów):\n"
        f"{kb_block}\n\n"
        "Zweryfikuj flagę. Odpowiedz wyłącznie obiektem JSON."
    )


def _extract_json(text: str) -> dict[str, Any]:
    t = text.strip()
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


def _normalize_verdict(v: Any) -> str:
    s = str(v or "").strip().lower()
    if s in {"confirmed", "false_positive", "cannot_verify"}:
        return s
    if s in {"false-positive", "false positive", "falsepositive"}:
        return "false_positive"
    if s in {"cannot verify", "cannot-verify", "unknown", "unclear"}:
        return "cannot_verify"
    return "cannot_verify"


def verify_flag(client: Any, flag: dict[str, Any], draft: dict[str, Any], kb_hits: list[dict[str, Any]]) -> tuple[dict[str, Any], int, int]:
    import anthropic

    user_msg = build_user_prompt(flag, draft, kb_hits)
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
                getattr(b, "text", "") for b in resp.content if getattr(b, "type", "") == "text"
            )
            try:
                obj = _extract_json(text)
            except Exception as e:
                last_err = e
                time.sleep(2 * attempt)
                continue
            usage = resp.usage
            return obj, usage.input_tokens, usage.output_tokens
        except anthropic.APIStatusError as e:
            last_err = e
            time.sleep(2 * attempt)
        except Exception as e:
            last_err = e
            time.sleep(2 * attempt)
    raise RuntimeError(f"verifier failed after {MAX_RETRIES} attempts: {last_err}")


def _write_report(
    drafts_paths: list[Path],
    per_draft_counts: dict[str, Counter[str]],
    per_flag_outcomes: list[tuple[str, dict[str, Any]]],
    total_in: int,
    total_out: int,
    cost: float,
    retry_err_count: int,
) -> None:
    total_flags = len(per_flag_outcomes)
    global_verdicts: Counter[str] = Counter(f[1].get("verdict", "cannot_verify") for f in per_flag_outcomes)

    lines: list[str] = []
    lines.append("# Batch 1 Verifier Report")
    lines.append("")
    lines.append(f"Data: {TODAY_ISO}")
    lines.append(f"Model: {MODEL}")
    lines.append(f"Koszt: ${cost:.4f}")
    lines.append(f"Flag verified: {total_flags}")
    lines.append(f"Retry/error count: {retry_err_count}")
    lines.append("")
    lines.append("## Rozkład verdictów")

    def _pct(n: int) -> str:
        return f"{(100.0 * n / total_flags):.1f}%" if total_flags else "0%"

    for key in ("confirmed", "false_positive", "cannot_verify"):
        n = global_verdicts.get(key, 0)
        lines.append(f"- {key}: {n}/{total_flags} ({_pct(n)})")
    lines.append("")

    # Pre-verifier counts per draft
    pre_counts: dict[str, int] = {}
    for p in drafts_paths:
        draft = json.loads(p.read_text(encoding="utf-8"))
        pre_counts[draft.get("id") or p.stem] = len(
            (draft.get("self_critique") or {}).get("issues") or []
        )

    lines.append("## Rozkład confirmed flag per draft (po filtracji false positives)")
    lines.append("| Draft | Przed verifier | Confirmed | False_pos | Cannot_verify |")
    lines.append("|---|---|---|---|---|")
    confirmed_by_draft: list[tuple[str, int]] = []
    for draft_id, counts in per_draft_counts.items():
        pre = pre_counts.get(draft_id, sum(counts.values()))
        c = counts.get("confirmed", 0)
        fp = counts.get("false_positive", 0)
        cv = counts.get("cannot_verify", 0)
        confirmed_by_draft.append((draft_id, c))
        lines.append(f"| {draft_id} | {pre} | {c} | {fp} | {cv} |")
    lines.append("")

    confirmed_by_draft.sort(key=lambda x: -x[1])
    lines.append("## Top 5 najbardziej problematycznych draftów (po confirmed flag)")
    for did, n in confirmed_by_draft[:5]:
        lines.append(f"- {did} — {n} confirmed")
    lines.append("")

    lines.append("## Top 3 najlepsze drafty (najmniej confirmed flag)")
    for did, n in sorted(confirmed_by_draft, key=lambda x: x[1])[:3]:
        lines.append(f"- {did} — {n} confirmed")
    lines.append("")

    # Per-category breakdown
    cat_stats: dict[str, Counter[str]] = {}
    for _, flag in per_flag_outcomes:
        cat = flag.get("type") or "unknown"
        cat_stats.setdefault(cat, Counter())[flag.get("verdict", "cannot_verify")] += 1
    lines.append("## Kategorie problemów (rozkład verdictów)")
    for cat, c in sorted(cat_stats.items(), key=lambda x: -sum(x[1].values())):
        lines.append(
            f"- {cat}: {c.get('confirmed', 0)} confirmed, "
            f"{c.get('false_positive', 0)} false_positive, "
            f"{c.get('cannot_verify', 0)} cannot_verify"
        )
    lines.append("")

    # High severity confirmed issues full list
    lines.append("## High severity confirmed issues (lista pełna)")
    hi_count = 0
    for did, flag in per_flag_outcomes:
        if flag.get("verdict") == "confirmed" and str(flag.get("severity", "")).lower() == "high":
            hi_count += 1
            desc = flag.get("description", "").strip()
            corr = flag.get("corrective_suggestion") or "(brak sugestii)"
            lines.append(f"- **{did}** → {desc}")
            lines.append(f"  - *corrective:* {corr}")
    if hi_count == 0:
        lines.append("(brak)")
    lines.append("")

    # Cannot_verify summary by category
    cv_cat: Counter[str] = Counter()
    for _, flag in per_flag_outcomes:
        if flag.get("verdict") == "cannot_verify":
            cv_cat[flag.get("type") or "unknown"] += 1
    lines.append("## Cannot_verify summary")
    if cv_cat:
        lines.append("Flagi wymagające web_search / expert review (bo KB nie pokrywa):")
        for cat, n in cv_cat.most_common():
            lines.append(f"- {cat}: {n}")
    else:
        lines.append("(brak)")
    lines.append("")

    # Recommendations
    lines.append("## Rekomendacje dla następnego kroku")
    problem = [did for did, n in confirmed_by_draft if n >= 3]
    ready = [did for did, n in confirmed_by_draft if n <= 1]
    lines.append(
        "- Drafty do manualnego review przed pokazaniem testerom (≥3 confirmed): "
        + (", ".join(problem) if problem else "brak")
    )
    lines.append(
        "- Drafty względnie gotowe (≤1 confirmed): "
        + (", ".join(ready) if ready else "brak")
    )
    worst_cats = [c for c, stats in cat_stats.items() if stats.get("confirmed", 0) >= 3]
    lines.append(
        "- Kategorie wymagające ogólnej naprawy prompt Opusa dla batch 2 (≥3 confirmed): "
        + (", ".join(worst_cats) if worst_cats else "brak")
    )
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    _load_env()
    import anthropic

    client = anthropic.Anthropic()

    kb = json.loads(KB_PATH.read_text(encoding="utf-8"))
    drafts = sorted(DRAFTS_DIR.glob("wf_*.json"))
    print(f"KB: {len(kb)} records. Drafts: {len(drafts)}.")

    total_in = 0
    total_out = 0
    retry_err_count = 0
    per_flag_outcomes: list[tuple[str, dict[str, Any]]] = []
    per_draft_counts: dict[str, Counter[str]] = {}

    for p in drafts:
        draft = json.loads(p.read_text(encoding="utf-8"))
        draft_id = draft.get("id") or p.stem
        issues = (draft.get("self_critique") or {}).get("issues") or []
        per_draft_counts.setdefault(draft_id, Counter())
        print(f"[{draft_id}] {len(issues)} flagi")
        for idx, flag in enumerate(issues):
            if flag.get("verdict") in {"confirmed", "false_positive", "cannot_verify"}:
                per_draft_counts[draft_id][flag["verdict"]] += 1
                per_flag_outcomes.append((draft_id, flag))
                continue
            kb_hits = retrieve_kb(flag, draft, kb)
            in_tok = 0
            out_tok = 0
            try:
                raw, in_tok, out_tok = verify_flag(client, flag, draft, kb_hits)
                total_in += in_tok
                total_out += out_tok
                verdict = _normalize_verdict(raw.get("verdict"))
                flag["verdict"] = verdict
                flag["verifier_reasoning"] = str(raw.get("reasoning") or "").strip()
                try:
                    flag["verifier_confidence"] = float(raw.get("confidence") or 0.0)
                except Exception:
                    flag["verifier_confidence"] = 0.0
                cs = raw.get("corrective_suggestion")
                if cs:
                    flag["corrective_suggestion"] = str(cs).strip()
                flag["verified_at"] = now_iso_utc()
                flag["verified_by"] = MODEL
                flag["kb_records_used"] = len(kb_hits)
            except Exception as e:
                retry_err_count += 1
                flag["verdict"] = "cannot_verify"
                flag["verifier_reasoning"] = f"ERROR: {e}"
                flag["verifier_confidence"] = 0.0
                flag["verified_at"] = now_iso_utc()
                flag["verified_by"] = MODEL
                flag["kb_records_used"] = len(kb_hits)

            per_draft_counts[draft_id][flag["verdict"]] += 1
            per_flag_outcomes.append((draft_id, flag))

            cost_now = total_in / 1000 * PRICE_IN_PER_1K + total_out / 1000 * PRICE_OUT_PER_1K
            print(
                f"  [{idx + 1}/{len(issues)}] verdict={flag['verdict']:15} "
                f"conf={flag.get('verifier_confidence', 0):.2f} "
                f"in={in_tok} out={out_tok} "
                f"cost_so_far=${cost_now:.4f}"
            )
            time.sleep(RATE_LIMIT_S)

            if cost_now > COST_HARD_CAP:
                p.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"\nCOST CAP EXCEEDED at ${cost_now:.4f} > ${COST_HARD_CAP}. Stopping.")
                cost = cost_now
                _write_report(drafts, per_draft_counts, per_flag_outcomes, total_in, total_out, cost, retry_err_count)
                return 2

        p.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")

    cost = total_in / 1000 * PRICE_IN_PER_1K + total_out / 1000 * PRICE_OUT_PER_1K
    print(
        f"\nDone. total_in={total_in} total_out={total_out} cost=${cost:.4f} "
        f"retries/errors={retry_err_count}"
    )
    _write_report(drafts, per_draft_counts, per_flag_outcomes, total_in, total_out, cost, retry_err_count)
    print(f"Report: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
