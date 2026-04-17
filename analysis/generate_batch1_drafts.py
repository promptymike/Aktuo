"""Zadanie 3 — batch 1: generate 10 workflow drafts from top clusters.

Pulls centroid + high-engagement examples + KB retrieval for each of
the 10 clusters Paweł greenlit, asks Opus 4.7 for a JSON draft, validates
the schema, retries once on failure, and writes per-cluster JSON + a
combined JSONL + a run-log with cost/telemetry.

Run from repo root:
    .venv/Scripts/python -X utf8 analysis/generate_batch1_drafts.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fb_pipeline.workflow.generate_draft import (  # noqa: E402
    build_prompt,
    generate_draft_with_retry,
    now_iso_utc,
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

REPO = Path(__file__).resolve().parents[1]
CLUSTERS_PATH = REPO / "data" / "corpus" / "fb_groups" / "clusters.jsonl"
POST_TO_CLUSTER_PATH = REPO / "data" / "corpus" / "fb_groups" / "post_to_cluster.jsonl"
CORPUS_PATH = REPO / "data" / "corpus" / "fb_groups" / "fb_corpus.jsonl"
EMB_PATH = REPO / "data" / "corpus" / "fb_groups" / "embeddings.npy"
EMB_META_PATH = REPO / "data" / "corpus" / "fb_groups" / "embeddings_meta.json"
KB_PATH = REPO / "data" / "seeds" / "law_knowledge.json"
OUT_DIR = REPO / "data" / "workflow_drafts"
BATCH_JSONL = OUT_DIR / "batch1_drafts.jsonl"
LOG_PATH = OUT_DIR / "batch1_run_log.json"

TODAY_ISO = "2026-04-17"

# Opus 4.7 pricing (per 1K tokens) — Anthropic public pricing.
PRICE_INPUT_PER_1K = 0.015
PRICE_OUTPUT_PER_1K = 0.075

BATCH1: list[ClusterSpec] = [
    ClusterSpec(
        target_key="merge_120_121",
        source_cluster_ids=[120, 121],
        label="KSeF: moment podatkowy, data wystawienia, korekty",
        topic_area="KSeF",
    ),
    ClusterSpec(
        target_key="7",
        source_cluster_ids=[7],
        label="Zaliczanie umów zlecenie i DG do stażu pracy od 2026",
        topic_area="kadry",
    ),
    ClusterSpec(
        target_key="63",
        source_cluster_ids=[63],
        label="Leasing samochodu osobowego: limity KUP i odliczenie VAT",
        topic_area="PIT",
    ),
    ClusterSpec(
        target_key="79",
        source_cluster_ids=[79],
        label="Mały ZUS Plus: ponowne skorzystanie po przerwie 2026",
        topic_area="ZUS",
    ),
    ClusterSpec(
        target_key="49",
        source_cluster_ids=[49],
        label="Środki trwałe: jednorazowa amortyzacja vs koszty bezpośrednie",
        topic_area="KPiR",
    ),
    ClusterSpec(
        target_key="10",
        source_cluster_ids=[10],
        label="Potrącenia komornicze niealimentacyjne z wynagrodzeń i zleceń",
        topic_area="kadry",
    ),
    ClusterSpec(
        target_key="107",
        source_cluster_ids=[107],
        label="Nowe oznaczenia JPK_VAT: BFK vs DI dla faktur WNT, importu i poza KSeF",
        topic_area="JPK",
    ),
    ClusterSpec(
        target_key="62",
        source_cluster_ids=[62],
        label="VAT przy wykupie, sprzedaży i darowiźnie samochodu z firmy",
        topic_area="VAT",
    ),
    ClusterSpec(
        target_key="21",
        source_cluster_ids=[21],
        label="Sprawozdania finansowe do KRS/KAS: schematy i składanie",
        topic_area="rachunkowość",
    ),
    ClusterSpec(
        target_key="139",
        source_cluster_ids=[139],
        label="KSeF: obieg, archiwizacja i weryfikacja faktur w biurze",
        topic_area="KSeF",
    ),
]


def _load_env() -> None:
    """Merge .env into os.environ for vars that are missing or blank."""

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


def _serialize_material(material) -> dict:
    return {
        "spec": asdict(material.spec),
        "size": material.size,
        "avg_comments": material.avg_comments,
        "top_keywords": material.top_keywords,
        "top_bigrams": material.top_bigrams,
        "centroid_posts": [asdict(p) for p in material.centroid_posts],
        "high_engagement_posts": [asdict(p) for p in material.high_engagement_posts],
        "legal_candidates": [asdict(c) for c in material.legal_candidates],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=0, help="process only first N specs (for probe)")
    args = parser.parse_args(argv)

    _load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERR: ANTHROPIC_API_KEY not set (check .env)")
        return 2

    import anthropic  # lazy

    client = anthropic.Anthropic()

    print("Loading corpus + embeddings...")
    clusters = load_clusters(CLUSTERS_PATH)
    post_to_cluster = load_post_to_cluster(POST_TO_CLUSTER_PATH)
    corpus = load_corpus(CORPUS_PATH)
    ids, embeddings = load_embeddings(EMB_PATH, EMB_META_PATH)
    id_to_row = {pid: i for i, pid in enumerate(ids)}
    print(
        f"  clusters={len(clusters)}  post_to_cluster={len(post_to_cluster)}  "
        f"corpus={len(corpus)}  emb={embeddings.shape}"
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    resume = os.environ.get("BATCH1_RESUME", "") == "1"
    # Clear batch jsonl unless resuming — it gets rebuilt from per-file drafts.
    if BATCH_JSONL.exists():
        BATCH_JSONL.unlink()

    specs = BATCH1 if not args.limit else BATCH1[: args.limit]

    results: list[dict] = []
    start_ts = time.time()
    total_in = 0
    total_out = 0

    for idx, spec in enumerate(specs, start=1):
        print(f"\n[{idx}/{len(specs)}] {spec.target_key} — {spec.label}")
        slug = slug_from_label(spec.label)
        expected_id = f"wf_{spec.target_key}_{slug}"
        existing_path = OUT_DIR / f"{expected_id}.json"
        if resume and existing_path.exists():
            try:
                draft = json.loads(existing_path.read_text(encoding="utf-8"))
            except Exception:
                draft = None
            if draft is not None:
                with BATCH_JSONL.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(draft, ensure_ascii=False) + "\n")
                results.append(
                    {
                        "target_key": spec.target_key,
                        "label": spec.label,
                        "topic_area": spec.topic_area,
                        "status": "ok_resumed",
                        "attempts": [],
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "elapsed_s": 0.0,
                        "material_size": None,
                        "material_avg_comments": None,
                        "centroid_n": None,
                        "high_engagement_n": None,
                        "legal_candidates_n": None,
                        "requires_manual_legal_anchor": draft.get(
                            "requires_manual_legal_anchor"
                        ),
                        "n_answer_steps": len(draft.get("answer_steps", [])),
                        "n_legal_anchors": len(draft.get("legal_anchors", [])),
                    }
                )
                print(f"  → RESUMED from {existing_path.name}")
                continue
        t0 = time.time()
        material = assemble_material(
            spec=spec,
            clusters=clusters,
            post_to_cluster=post_to_cluster,
            corpus=corpus,
            id_to_row=id_to_row,
            embeddings=embeddings,
            kb_path=KB_PATH,
        )
        print(
            f"  size={material.size}  avg_comments={material.avg_comments:.2f}  "
            f"centroid={len(material.centroid_posts)}  "
            f"high_eng={len(material.high_engagement_posts)}  "
            f"legal_cands={len(material.legal_candidates)}"
        )

        prompt = build_prompt(material, today_iso=TODAY_ISO)
        draft, attempts = generate_draft_with_retry(client, prompt, max_retries=1)

        in_tok = sum(a["input_tokens"] for a in attempts)
        out_tok = sum(a["output_tokens"] for a in attempts)
        total_in += in_tok
        total_out += out_tok
        dt = time.time() - t0

        # Always inject generation_metadata we can trust regardless of LLM drift.
        if draft is not None:
            draft.setdefault("generation_metadata", {})
            draft["generation_metadata"]["cluster_id"] = spec.target_key
            draft["generation_metadata"]["cluster_label"] = spec.label
            draft["generation_metadata"]["model"] = "claude-opus-4-7"
            if not draft["generation_metadata"].get("generated_at"):
                draft["generation_metadata"]["generated_at"] = now_iso_utc()
            # Ensure consistent id/slug.
            slug = slug_from_label(spec.label)
            expected_id = f"wf_{spec.target_key}_{slug}"
            draft["id"] = expected_id

            path = OUT_DIR / f"{expected_id}.json"
            path.write_text(
                json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            with BATCH_JSONL.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(draft, ensure_ascii=False) + "\n")
            status = "ok"
            print(
                f"  → {path.name}  steps={len(draft.get('answer_steps', []))}  "
                f"anchors={len(draft.get('legal_anchors', []))}  "
                f"manual={draft.get('requires_manual_legal_anchor')}"
            )
        else:
            status = "failed"
            print(f"  FAILED after {len(attempts)} attempts: {attempts}")

        results.append(
            {
                "target_key": spec.target_key,
                "label": spec.label,
                "topic_area": spec.topic_area,
                "status": status,
                "attempts": attempts,
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "elapsed_s": round(dt, 2),
                "material_size": material.size,
                "material_avg_comments": round(material.avg_comments, 3),
                "centroid_n": len(material.centroid_posts),
                "high_engagement_n": len(material.high_engagement_posts),
                "legal_candidates_n": len(material.legal_candidates),
                "requires_manual_legal_anchor": (
                    draft.get("requires_manual_legal_anchor") if draft else None
                ),
                "n_answer_steps": len(draft.get("answer_steps", [])) if draft else 0,
                "n_legal_anchors": len(draft.get("legal_anchors", [])) if draft else 0,
            }
        )

    elapsed = time.time() - start_ts
    cost = (total_in / 1000 * PRICE_INPUT_PER_1K) + (
        total_out / 1000 * PRICE_OUTPUT_PER_1K
    )

    summary = {
        "batch": "batch1",
        "generated_at": now_iso_utc(),
        "n_specs": len(specs),
        "n_ok": sum(1 for r in results if r["status"] == "ok"),
        "n_failed": sum(1 for r in results if r["status"] != "ok"),
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "total_cost_usd": round(cost, 4),
        "elapsed_s": round(elapsed, 2),
        "results": results,
    }
    LOG_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("\n=== BATCH 1 SUMMARY ===")
    print(
        f"ok={summary['n_ok']}/{summary['n_specs']}  "
        f"in_tok={total_in}  out_tok={total_out}  "
        f"cost=${summary['total_cost_usd']:.4f}  "
        f"elapsed={elapsed:.1f}s"
    )
    return 0 if summary["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
