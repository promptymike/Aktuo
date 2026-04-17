"""One-off retry for cluster 62 — the only batch-1 failure (max_tokens cap)."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.generate_batch1_drafts import (  # noqa: E402
    BATCH1,
    BATCH_JSONL,
    CLUSTERS_PATH,
    CORPUS_PATH,
    EMB_META_PATH,
    EMB_PATH,
    KB_PATH,
    LOG_PATH,
    OUT_DIR,
    POST_TO_CLUSTER_PATH,
    PRICE_INPUT_PER_1K,
    PRICE_OUTPUT_PER_1K,
    TODAY_ISO,
    _load_env,
)
from fb_pipeline.workflow.generate_draft import (  # noqa: E402
    build_prompt,
    generate_draft_with_retry,
    now_iso_utc,
)
from fb_pipeline.workflow.prepare_material import (  # noqa: E402
    assemble_material,
    load_clusters,
    load_corpus,
    load_embeddings,
    load_post_to_cluster,
    slug_from_label,
)


def main() -> int:
    _load_env()
    import anthropic

    client = anthropic.Anthropic()

    clusters = load_clusters(CLUSTERS_PATH)
    post_to_cluster = load_post_to_cluster(POST_TO_CLUSTER_PATH)
    corpus = load_corpus(CORPUS_PATH)
    ids, embeddings = load_embeddings(EMB_PATH, EMB_META_PATH)
    id_to_row = {pid: i for i, pid in enumerate(ids)}

    spec = next(s for s in BATCH1 if s.target_key == "62")
    material = assemble_material(
        spec=spec,
        clusters=clusters,
        post_to_cluster=post_to_cluster,
        corpus=corpus,
        id_to_row=id_to_row,
        embeddings=embeddings,
        kb_path=KB_PATH,
    )

    prompt = build_prompt(material, today_iso=TODAY_ISO)
    t0 = time.time()
    # Bumped max_tokens — first attempt hit 4096 cap.
    draft, attempts = generate_draft_with_retry(
        client, prompt, max_retries=1, max_tokens=6500
    )
    dt = time.time() - t0

    in_tok = sum(a["input_tokens"] for a in attempts)
    out_tok = sum(a["output_tokens"] for a in attempts)
    cost = in_tok / 1000 * PRICE_INPUT_PER_1K + out_tok / 1000 * PRICE_OUTPUT_PER_1K
    print(
        f"attempts={len(attempts)}  status={[a['status'] for a in attempts]}  "
        f"in={in_tok} out={out_tok} cost=${cost:.4f} elapsed={dt:.1f}s"
    )
    if draft is None:
        print("STILL FAILED")
        return 1

    draft.setdefault("generation_metadata", {})
    draft["generation_metadata"]["cluster_id"] = spec.target_key
    draft["generation_metadata"]["cluster_label"] = spec.label
    draft["generation_metadata"]["model"] = "claude-opus-4-7"
    if not draft["generation_metadata"].get("generated_at"):
        draft["generation_metadata"]["generated_at"] = now_iso_utc()
    slug = slug_from_label(spec.label)
    expected_id = f"wf_{spec.target_key}_{slug}"
    draft["id"] = expected_id

    path = OUT_DIR / f"{expected_id}.json"
    path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
    with BATCH_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(draft, ensure_ascii=False) + "\n")

    # Update run_log with new data for cluster 62.
    log = json.loads(LOG_PATH.read_text(encoding="utf-8"))
    for r in log["results"]:
        if r["target_key"] == "62":
            r["status"] = "ok_retry"
            r["attempts"] = attempts
            r["input_tokens"] = in_tok
            r["output_tokens"] = out_tok
            r["elapsed_s"] = round(dt, 2)
            r["material_size"] = material.size
            r["material_avg_comments"] = round(material.avg_comments, 3)
            r["centroid_n"] = len(material.centroid_posts)
            r["high_engagement_n"] = len(material.high_engagement_posts)
            r["legal_candidates_n"] = len(material.legal_candidates)
            r["requires_manual_legal_anchor"] = draft.get(
                "requires_manual_legal_anchor"
            )
            r["n_answer_steps"] = len(draft.get("answer_steps", []))
            r["n_legal_anchors"] = len(draft.get("legal_anchors", []))
            break
    log["total_input_tokens"] += in_tok
    log["total_output_tokens"] += out_tok
    log["total_cost_usd"] = round(
        log["total_input_tokens"] / 1000 * PRICE_INPUT_PER_1K
        + log["total_output_tokens"] / 1000 * PRICE_OUTPUT_PER_1K,
        4,
    )
    log["n_ok"] = sum(1 for r in log["results"] if r["status"].startswith("ok"))
    log["n_failed"] = sum(1 for r in log["results"] if not r["status"].startswith("ok"))
    LOG_PATH.write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(
        f"→ {path.name} steps={len(draft.get('answer_steps', []))} "
        f"anchors={len(draft.get('legal_anchors', []))} "
        f"manual={draft.get('requires_manual_legal_anchor')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
