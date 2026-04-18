"""Batch 2 — generate 32 workflow drafts (Opus 4.7 + web_search for 2026 topics).

Differences vs batch 1:
  * Uses an enhanced SYSTEM prompt with 7 hard rules distilled from
    batch 1 verifier findings (precise numbers, legal anchor discipline,
    korekty dziedziczenie, umowa type disambiguation, date transitions,
    uncertainty flagging, concrete thresholds).
  * For clusters flagged ``is_2026_topic=True`` in ``batch2_plan.json``
    (4 topics: KSeF uprawnienia/cert, Najem 2026, min. wynagr. 2026,
    KPiR 2026) invokes Anthropic web_search with a 9-domain whitelist
    so the draft is anchored on live 2026 guidance.
  * Hard caps: $20 cost, 30 min wall-clock, 2 s rate limit between Opus
    calls, 3x retry per cluster. On retry exhaustion — error-log and
    continue.
  * Tries ``claude-opus-4-7`` first, falls back to ``claude-opus-4-6``
    on 404 (older model alias still available).

Run from repo root:
    .venv/Scripts/python -u -X utf8 analysis/generate_batch2_drafts.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fb_pipeline.workflow.generate_draft import (  # noqa: E402
    build_prompt,
    now_iso_utc,
    parse_json_response,
)
from fb_pipeline.workflow.prepare_material import (  # noqa: E402
    ClusterSpec,
    assemble_material,
    load_clusters,
    load_corpus,
    load_embeddings,
    load_post_to_cluster,
    slug_from_label,
)
from fb_pipeline.workflow.schema import validate_draft  # noqa: E402

REPO = ROOT
PLAN_PATH = REPO / "analysis" / "batch2_plan.json"
CLUSTERS_PATH = REPO / "data" / "corpus" / "fb_groups" / "clusters.jsonl"
POST_TO_CLUSTER_PATH = REPO / "data" / "corpus" / "fb_groups" / "post_to_cluster.jsonl"
CORPUS_PATH = REPO / "data" / "corpus" / "fb_groups" / "fb_corpus.jsonl"
EMB_PATH = REPO / "data" / "corpus" / "fb_groups" / "embeddings.npy"
EMB_META_PATH = REPO / "data" / "corpus" / "fb_groups" / "embeddings_meta.json"
KB_PATH = REPO / "data" / "seeds" / "law_knowledge.json"
OUT_DIR = REPO / "data" / "workflow_drafts"
BATCH_JSONL = OUT_DIR / "batch2_drafts.jsonl"
LOG_PATH = OUT_DIR / "batch2_run_log.json"
GEN_LOG_MD = REPO / "analysis" / "batch2_generation_log.md"

TODAY_ISO = "2026-04-18"

# Opus 4.7 pricing (per 1K tokens).
PRICE_INPUT_PER_1K = 0.015
PRICE_OUTPUT_PER_1K = 0.075
# Web search is billed per request at ~$10/1000 = $0.01/req.
PRICE_WEB_SEARCH_REQ = 0.010

# Hard caps.
COST_CAP_USD = 25.0  # raised from 20 — 30/32 done at $20.26, need ~$1 more for last 2
TIME_CAP_SEC = 50 * 60
RATE_LIMIT_SEC = 2.0
MAX_RETRIES = 3
MAX_TOKENS = 8000

MODEL_PRIMARY = "claude-opus-4-7"
MODEL_FALLBACK = "claude-opus-4-6"

ALLOWED_DOMAINS = [
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

# Enhanced SYSTEM prompt — 7 hard rules from batch 1 verifier lessons.
SYSTEM_PROMPT = """Jesteś senior księgowym, doradcą podatkowym i kadrowym dla polskich biur \
rachunkowych. Tworzysz workflow rekord dla systemu Aktuo (2026).

TWARDE ZASADY (na podstawie weryfikacji batch 1 — nie łam ich):

1. KONKRETNE LICZBY Z ŹRÓDŁEM: każdy próg, limit, procent podawaj z obowiązującą
   wartością 2026 i nazwą aktu prawnego. Nie pisz "zazwyczaj", "często", "około".
   Zamiast "kwota wolna to minimalne wynagrodzenie" → "kwota wolna to 100% min.
   wynagrodzenia netto (4 666 zł brutto od 1.01.2026, po ZUS/PIT)".

2. KOTWICE PRAWNE Z DYSCYPLINĄ: cytuj tylko artykuł, który naprawdę zawiera
   daną normę. Jeśli nie jesteś pewien — ustaw requires_manual_legal_anchor=true
   i zostaw pustą listę legal_anchors. Nigdy nie zgaduj numeru ustępu/punktu.

3. KOREKTY DZIEDZICZĄ OZNACZENIA: w każdym workflow dotyczącym JPK_VAT/KSeF/
   oznaczeń wyraźnie napisz jak zachowują się faktury korygujące (co do zasady
   dziedziczą oznaczenie faktury pierwotnej, wyjątki jawnie wymień).

4. UMOWA O PRACĘ vs ZLECENIE vs B2B: w każdym workflow kadrowym/ZUS osobno
   opisz minimum 2 z tych form (jeśli temat dotyczy). Nie mieszaj limitów
   i progów — stosują się inaczej.

5. DATY PRZEJŚCIOWE: jeśli przepis zmienia się od 1.01.2026 lub w trakcie
   roku — jawnie oznacz "dla umów zawartych do DD.MM.RRRR" vs "od DD.MM.RRRR".
   Stan "prawo nabyte" wyjaśnij w edge_cases.

6. FLAGA NIEPEWNOŚCI: jeśli pewna norma opiera się o niepotwierdzone źródło
   (szkolenia, sprzeczne interpretacje KIS) — krok musi zaczynać się od
   "Zweryfikuj..." i odwoływać do pisemnego zapytania KIS.

7. KONKRETNY PROGRAM KSIĘGOWY: jeśli krok dotyczy oprogramowania, wymień
   1–2 popularne (Comarch Optima / Symfonia / Enova / WAPRO / WFirma) i
   nazwy modułów/akcji (np. "Kadry → Listy płac → Korekta").

Zwracaj TYLKO JSON (bez markdown fence, bez tekstu przed/po). Polskie
znaki diakrytyczne OK. Jeśli używasz web_search — cytuj tylko domeny
z whitelisty, które dostałeś w narzędziu."""


def _load_env() -> None:
    env_path = REPO / ".env"
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


def _parse_cluster_id(raw: str) -> tuple[str, list[int]]:
    """Return (target_key, source_cluster_ids) for a plan cluster_id string.

    Accepts plain ``"45"`` or merged ``"merge[33+86+95]"``.
    """
    s = str(raw).strip()
    if s.startswith("merge[") and s.endswith("]"):
        inside = s[len("merge["):-1]
        ids = [int(x) for x in inside.split("+") if x.strip()]
        key = "merge_" + "_".join(str(i) for i in ids)
        return key, ids
    return s, [int(s)]


def _load_specs() -> list[tuple[ClusterSpec, dict]]:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    out: list[tuple[ClusterSpec, dict]] = []
    for entry in plan:
        key, ids = _parse_cluster_id(entry["cluster_id"])
        spec = ClusterSpec(
            target_key=key,
            source_cluster_ids=ids,
            label=entry["cluster_label"],
            topic_area=entry["topic"],
        )
        out.append((spec, entry))
    return out


def _extract_text(resp: Any) -> str:
    parts: list[str] = []
    for block in resp.content:
        t = getattr(block, "type", None)
        if t == "text":
            parts.append(block.text)
    return "".join(parts)


def _usage(resp: Any) -> dict[str, int]:
    u = getattr(resp, "usage", None)
    if not u:
        return {"input_tokens": 0, "output_tokens": 0, "web_search_requests": 0}
    out = {
        "input_tokens": int(getattr(u, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(u, "output_tokens", 0) or 0),
    }
    # server_tool_use is nested — try a couple of shapes
    stu = getattr(u, "server_tool_use", None)
    if stu is not None:
        out["web_search_requests"] = int(getattr(stu, "web_search_requests", 0) or 0)
    else:
        out["web_search_requests"] = 0
    return out


def _call_opus_plain(client: Any, prompt: str, *, model: str) -> tuple[str, dict]:
    resp = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return _extract_text(resp), _usage(resp)


def _call_opus_web(client: Any, prompt: str, *, model: str) -> tuple[str, dict]:
    """Opus call with web_search_20250305 tool + domain whitelist."""
    # The model decides if/how many times to search; max_uses=3 caps it.
    resp = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "allowed_domains": ALLOWED_DOMAINS,
                "max_uses": 3,
            }
        ],
        messages=[{"role": "user", "content": prompt}],
    )
    return _extract_text(resp), _usage(resp)


def _generate_with_retry(
    client: Any,
    prompt: str,
    *,
    use_web: bool,
    errors: list[str],
    models_tried: dict[str, bool],
) -> tuple[dict | None, list[dict]]:
    attempts: list[dict] = []
    current_prompt = prompt
    last_err: str | None = None

    for attempt_idx in range(MAX_RETRIES):
        model = MODEL_PRIMARY if models_tried.get(MODEL_PRIMARY) is not False else MODEL_FALLBACK

        try:
            if use_web:
                text, usage = _call_opus_web(client, current_prompt, model=model)
            else:
                text, usage = _call_opus_plain(client, current_prompt, model=model)
            models_tried[model] = True
        except Exception as exc:
            err_str = f"{type(exc).__name__}: {exc}"
            # 404 on primary → mark unavailable, retry on fallback in next loop.
            if "404" in err_str and models_tried.get(MODEL_PRIMARY, True):
                models_tried[MODEL_PRIMARY] = False
                errors.append(f"  model 404 for {MODEL_PRIMARY}, falling back")
                last_err = err_str
                attempts.append({"attempt": attempt_idx + 1, "status": "api_404", "error": err_str})
                continue
            last_err = err_str
            attempts.append({"attempt": attempt_idx + 1, "status": "api_error", "error": err_str})
            # small backoff
            time.sleep(2.0)
            continue

        rec = {
            "attempt": attempt_idx + 1,
            "model": model,
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "web_search_requests": usage.get("web_search_requests", 0),
            "raw_text_len": len(text),
        }
        try:
            parsed = parse_json_response(text)
        except ValueError as exc:
            last_err = f"parse: {exc}"
            rec["status"] = "parse_fail"
            rec["error"] = last_err
            attempts.append(rec)
            current_prompt = (
                prompt
                + f"\n\nPoprzednia próba zwróciła niepoprawny JSON: {last_err}. "
                "Zwróć TYLKO poprawny JSON, bez markdown fence."
            )
            continue

        ok, err = validate_draft(parsed)
        if not ok:
            last_err = f"schema: {err}"
            rec["status"] = "schema_fail"
            rec["error"] = last_err
            attempts.append(rec)
            current_prompt = (
                prompt
                + f"\n\nPoprzednia próba miała niepoprawny schemat: {last_err}. "
                "Zwróć JSON zgodny ze schematem."
            )
            continue

        rec["status"] = "ok"
        attempts.append(rec)
        return parsed, attempts

    if last_err:
        errors.append(f"  final error: {last_err}")
    return None, attempts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=0, help="process only first N specs (for probe)")
    parser.add_argument("--resume", action="store_true", help="skip clusters whose draft already exists")
    args = parser.parse_args(argv)

    _load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERR: ANTHROPIC_API_KEY not set", flush=True)
        return 2

    import anthropic  # lazy

    client = anthropic.Anthropic(timeout=300.0)

    print("Loading corpus + embeddings...", flush=True)
    clusters = load_clusters(CLUSTERS_PATH)
    post_to_cluster = load_post_to_cluster(POST_TO_CLUSTER_PATH)
    corpus = load_corpus(CORPUS_PATH)
    ids, embeddings = load_embeddings(EMB_PATH, EMB_META_PATH)
    id_to_row = {pid: i for i, pid in enumerate(ids)}
    print(
        f"  clusters={len(clusters)}  post_to_cluster={len(post_to_cluster)}  "
        f"corpus={len(corpus)}  emb={embeddings.shape}",
        flush=True,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if BATCH_JSONL.exists() and not args.resume:
        BATCH_JSONL.unlink()

    specs = _load_specs()
    if args.limit:
        specs = specs[: args.limit]

    print(f"Processing {len(specs)} clusters (2026 web: {sum(1 for _, e in specs if e.get('is_2026_topic'))})", flush=True)

    results: list[dict] = []
    errors: list[str] = []
    models_tried: dict[str, bool] = {}
    start_ts = time.time()
    total_in = 0
    total_out = 0
    total_web = 0

    for idx, (spec, entry) in enumerate(specs, start=1):
        elapsed_total = time.time() - start_ts
        cost_so_far = (
            total_in / 1000 * PRICE_INPUT_PER_1K
            + total_out / 1000 * PRICE_OUTPUT_PER_1K
            + total_web * PRICE_WEB_SEARCH_REQ
        )
        if cost_so_far >= COST_CAP_USD:
            errors.append(f"COST CAP ${COST_CAP_USD:.2f} hit at ${cost_so_far:.2f} — stopping")
            print(errors[-1], flush=True)
            break
        if elapsed_total >= TIME_CAP_SEC:
            errors.append(f"TIME CAP {TIME_CAP_SEC}s hit at {elapsed_total:.0f}s — stopping")
            print(errors[-1], flush=True)
            break

        print(f"\n[{idx}/{len(specs)}] {spec.target_key} — {spec.label}", flush=True)
        print(
            f"  topic={spec.topic_area}  is_2026={entry.get('is_2026_topic')}  "
            f"cost_so_far=${cost_so_far:.3f}  elapsed={elapsed_total:.0f}s",
            flush=True,
        )

        slug = slug_from_label(spec.label)
        expected_id = f"wf_{spec.target_key}_{slug}"
        out_path = OUT_DIR / f"{expected_id}.json"

        if args.resume and out_path.exists():
            try:
                draft = json.loads(out_path.read_text(encoding="utf-8"))
                with BATCH_JSONL.open("a", encoding="utf-8") as h:
                    h.write(json.dumps(draft, ensure_ascii=False) + "\n")
                print(f"  → RESUMED {out_path.name}", flush=True)
                results.append({
                    "target_key": spec.target_key,
                    "label": spec.label,
                    "topic_area": spec.topic_area,
                    "is_2026_topic": entry.get("is_2026_topic"),
                    "status": "ok_resumed",
                    "attempts": [],
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "web_search_requests": 0,
                    "elapsed_s": 0.0,
                })
                continue
            except Exception:
                pass

        t0 = time.time()
        try:
            material = assemble_material(
                spec=spec,
                clusters=clusters,
                post_to_cluster=post_to_cluster,
                corpus=corpus,
                id_to_row=id_to_row,
                embeddings=embeddings,
                kb_path=KB_PATH,
            )
        except Exception as exc:
            errors.append(f"{spec.target_key}: material assembly failed: {exc}")
            print(f"  MATERIAL FAIL: {exc}", flush=True)
            results.append({
                "target_key": spec.target_key,
                "label": spec.label,
                "topic_area": spec.topic_area,
                "is_2026_topic": entry.get("is_2026_topic"),
                "status": "material_failed",
                "error": str(exc),
            })
            continue

        print(
            f"  size={material.size}  avg_comments={material.avg_comments:.2f}  "
            f"centroid={len(material.centroid_posts)}  "
            f"high_eng={len(material.high_engagement_posts)}  "
            f"legal_cands={len(material.legal_candidates)}",
            flush=True,
        )

        prompt = build_prompt(material, today_iso=TODAY_ISO)
        if entry.get("is_2026_topic"):
            prompt += (
                "\n\nUWAGA: Ten temat dotyczy zmian 2026 — KORZYSTAJ z web_search "
                "(whitelist: gofin.pl, podatki.gov.pl, zus.pl, biznes.gov.pl, "
                "sejm.gov.pl, isap.sejm.gov.pl, ksiegowosc.infor.pl, podatki.biz, "
                "interpretacje.gofin.pl). Zacytuj url źródła w detail kroku."
            )

        use_web = bool(entry.get("is_2026_topic"))
        draft, attempts = _generate_with_retry(
            client, prompt, use_web=use_web, errors=errors, models_tried=models_tried,
        )

        in_tok = sum(a.get("input_tokens", 0) for a in attempts)
        out_tok = sum(a.get("output_tokens", 0) for a in attempts)
        web_req = sum(a.get("web_search_requests", 0) for a in attempts)
        total_in += in_tok
        total_out += out_tok
        total_web += web_req
        dt = time.time() - t0

        if draft is not None:
            draft.setdefault("generation_metadata", {})
            draft["generation_metadata"]["cluster_id"] = spec.target_key
            draft["generation_metadata"]["cluster_label"] = spec.label
            draft["generation_metadata"]["model"] = (
                next((a.get("model") for a in attempts if a.get("status") == "ok"), MODEL_PRIMARY)
            )
            draft["generation_metadata"]["batch"] = "batch2"
            draft["generation_metadata"]["used_web_search"] = use_web
            if not draft["generation_metadata"].get("generated_at"):
                draft["generation_metadata"]["generated_at"] = now_iso_utc()
            draft["id"] = expected_id

            out_path.write_text(
                json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            with BATCH_JSONL.open("a", encoding="utf-8") as h:
                h.write(json.dumps(draft, ensure_ascii=False) + "\n")
            status = "ok"
            print(
                f"  → {out_path.name}  steps={len(draft.get('answer_steps', []))}  "
                f"anchors={len(draft.get('legal_anchors', []))}  "
                f"manual={draft.get('requires_manual_legal_anchor')}  "
                f"web={web_req}  in={in_tok} out={out_tok}",
                flush=True,
            )
        else:
            status = "failed"
            errors.append(f"{spec.target_key}: failed after {len(attempts)} attempts")
            print(f"  FAILED: {attempts}", flush=True)

        results.append({
            "target_key": spec.target_key,
            "label": spec.label,
            "topic_area": spec.topic_area,
            "is_2026_topic": entry.get("is_2026_topic"),
            "status": status,
            "attempts": attempts,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "web_search_requests": web_req,
            "elapsed_s": round(dt, 2),
        })

        time.sleep(RATE_LIMIT_SEC)

    elapsed = time.time() - start_ts
    cost = (
        total_in / 1000 * PRICE_INPUT_PER_1K
        + total_out / 1000 * PRICE_OUTPUT_PER_1K
        + total_web * PRICE_WEB_SEARCH_REQ
    )

    n_ok = sum(1 for r in results if r.get("status") in ("ok", "ok_resumed"))
    n_fail = sum(1 for r in results if r.get("status") not in ("ok", "ok_resumed"))

    summary = {
        "batch": "batch2",
        "generated_at": now_iso_utc(),
        "n_specs": len(specs),
        "n_ok": n_ok,
        "n_failed": n_fail,
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "total_web_search_requests": total_web,
        "total_cost_usd": round(cost, 4),
        "elapsed_s": round(elapsed, 2),
        "errors": errors,
        "results": results,
    }
    LOG_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_markdown_log(summary)

    print("\n=== BATCH 2 SUMMARY ===", flush=True)
    print(
        f"ok={n_ok}/{len(specs)}  in_tok={total_in}  out_tok={total_out}  "
        f"web_req={total_web}  cost=${cost:.4f}  elapsed={elapsed:.1f}s",
        flush=True,
    )
    if errors:
        print(f"ERRORS ({len(errors)}):", flush=True)
        for e in errors[:20]:
            print(f"  - {e}", flush=True)
    return 0 if n_fail == 0 else 1


def _write_markdown_log(summary: dict) -> None:
    r = summary["results"]
    lines = []
    lines.append("# Batch 2 Generation Log")
    lines.append("")
    lines.append(f"Data: {TODAY_ISO}")
    lines.append(f"Model: {MODEL_PRIMARY} (fallback {MODEL_FALLBACK})")
    lines.append(f"OK: {summary['n_ok']}/{summary['n_specs']}")
    lines.append(f"Failed: {summary['n_failed']}")
    lines.append(f"Input tokens: {summary['total_input_tokens']}")
    lines.append(f"Output tokens: {summary['total_output_tokens']}")
    lines.append(f"Web search requests: {summary['total_web_search_requests']}")
    lines.append(f"Cost: ${summary['total_cost_usd']:.4f} (cap ${COST_CAP_USD:.2f})")
    lines.append(f"Elapsed: {summary['elapsed_s']}s (cap {TIME_CAP_SEC}s)")
    lines.append("")
    lines.append("## Per cluster")
    lines.append("| # | target_key | topic | 2026? | status | in | out | web | s |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for i, row in enumerate(r, start=1):
        lines.append(
            f"| {i} | {row.get('target_key')} | {row.get('topic_area')} "
            f"| {'Y' if row.get('is_2026_topic') else ''} "
            f"| {row.get('status')} | {row.get('input_tokens', 0)} "
            f"| {row.get('output_tokens', 0)} | {row.get('web_search_requests', 0)} "
            f"| {row.get('elapsed_s', 0)} |"
        )
    if summary["errors"]:
        lines.append("")
        lines.append("## Errors")
        for e in summary["errors"]:
            lines.append(f"- {e}")
    GEN_LOG_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
