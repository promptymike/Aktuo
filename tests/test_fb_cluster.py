"""Tests for ``fb_pipeline.clustering.cluster_fb_corpus``.

Uses synthetic embeddings (random vectors nudged to form two groups) so that
nothing touches the real Voyage or Anthropic APIs. The HDBSCAN call is real,
but on <=20 short vectors it runs in milliseconds.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from fb_pipeline.clustering import cluster_fb_corpus as clu


def _record(
    post_id: str,
    text: str,
    *,
    comments: list[str] | None = None,
    comments_count: int | None = None,
    group_name: str = "grupa_a",
) -> clu.PostRecord:
    comments = list(comments or [])
    return clu.PostRecord(
        id=post_id,
        group_name=group_name,
        text=text,
        normalized_text=text.lower(),
        comments=comments,
        comments_count=comments_count if comments_count is not None else len(comments),
        scraped_at="2026-04-11T10:00:00.000Z",
        source_file="file1.json",
        quality_flags=[],
    )


def _two_cluster_embeddings(n_per: int = 10, dim: int = 16, seed: int = 7) -> np.ndarray:
    """Return ``2*n_per`` unit-normalized vectors forming two cohesive groups."""

    rng = np.random.default_rng(seed)
    # Two distinct centers with small jitter.
    center_a = rng.normal(size=dim).astype(np.float32)
    center_a /= np.linalg.norm(center_a)
    center_b = rng.normal(size=dim).astype(np.float32)
    center_b /= np.linalg.norm(center_b)
    jitter = 0.05

    group_a = center_a + rng.normal(scale=jitter, size=(n_per, dim)).astype(np.float32)
    group_b = center_b + rng.normal(scale=jitter, size=(n_per, dim)).astype(np.float32)
    matrix = np.vstack([group_a, group_b]).astype(np.float32)
    return clu.normalize_vectors(matrix)


# -----------------------------------------------------------------------------
# 1. Embedding cache round-trip
# -----------------------------------------------------------------------------

def test_embedding_cache_round_trip(tmp_path: Path) -> None:
    ids = [f"p{i:03d}" for i in range(5)]
    embeddings = np.random.default_rng(0).normal(size=(5, 16)).astype(np.float32)
    emb_path = tmp_path / "emb.npy"
    meta_path = tmp_path / "emb.meta.json"

    clu.save_embeddings(embeddings, ids, emb_path, meta_path, clu.EMBED_MODEL)

    # Same ids + same model -> cache hit.
    loaded = clu.load_cached_embeddings(emb_path, meta_path, ids, clu.EMBED_MODEL)
    assert loaded is not None
    assert loaded.shape == embeddings.shape
    np.testing.assert_allclose(loaded, embeddings)

    # Reordered ids -> cache miss (ids comparison is order-sensitive).
    loaded2 = clu.load_cached_embeddings(
        emb_path, meta_path, list(reversed(ids)), clu.EMBED_MODEL
    )
    assert loaded2 is None

    # Different model -> cache miss.
    loaded3 = clu.load_cached_embeddings(emb_path, meta_path, ids, "voyage-3")
    assert loaded3 is None

    # Different count -> cache miss.
    loaded4 = clu.load_cached_embeddings(
        emb_path, meta_path, ids + ["p999"], clu.EMBED_MODEL
    )
    assert loaded4 is None


# -----------------------------------------------------------------------------
# 2. Cluster output schema
# -----------------------------------------------------------------------------

def test_cluster_output_schema(tmp_path: Path) -> None:
    embeddings = _two_cluster_embeddings(n_per=10, dim=16)
    records = [
        _record(f"p{i:03d}", f"post numer {i} VAT deklaracja", comments=["ok"])
        for i in range(embeddings.shape[0])
    ]

    labels = clu.cluster_embeddings(embeddings, min_cluster_size=3, min_samples=1)
    assert set(labels) - {-1}, "synthetic groups should form ≥1 cluster"

    global_stop: set[str] = set()

    def stub_label(posts, kws, bgs):  # noqa: ARG001
        return {"label": "stub", "description": "", "topic_area": "inne"}

    summaries = clu.build_cluster_summaries(
        records, labels, embeddings, global_stop, stub_label
    )
    assert summaries, "should have at least one non-noise cluster"

    summary = summaries[0]
    payload = summary.to_dict()
    required = {
        "cluster_id", "label", "description", "topic_area", "size",
        "top_keywords", "top_bigrams", "centroid_post_ids", "sample_post_ids",
        "avg_comments_count", "has_many_comments_ratio",
    }
    assert required.issubset(payload.keys())
    assert isinstance(payload["top_keywords"], list)
    assert isinstance(payload["top_bigrams"], list)
    assert isinstance(payload["centroid_post_ids"], list)
    assert len(payload["centroid_post_ids"]) <= 10
    assert len(payload["sample_post_ids"]) <= 20
    assert summary.size == sum(1 for x in labels if x == summary.cluster_id)


# -----------------------------------------------------------------------------
# 3. post_to_cluster mapping
# -----------------------------------------------------------------------------

def test_post_to_cluster_mapping(tmp_path: Path) -> None:
    embeddings = _two_cluster_embeddings(n_per=8, dim=16)
    records = [_record(f"p{i:03d}", "treść") for i in range(embeddings.shape[0])]
    labels = clu.cluster_embeddings(embeddings, min_cluster_size=3, min_samples=1)

    def stub_label(posts, kws, bgs):  # noqa: ARG001
        return {"label": "stub", "description": "", "topic_area": "inne"}

    summaries = clu.build_cluster_summaries(records, labels, embeddings, set(), stub_label)

    clusters_jsonl = tmp_path / "clusters.jsonl"
    mapping_jsonl = tmp_path / "post_to_cluster.jsonl"
    clu.write_outputs(summaries, records, labels, clusters_jsonl, mapping_jsonl)

    # Mapping has exactly one line per input record, and every post id shows up.
    lines = mapping_jsonl.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == len(records)
    seen_ids = set()
    for line in lines:
        row = json.loads(line)
        assert set(row.keys()) == {"post_id", "cluster_id"}
        assert isinstance(row["cluster_id"], int)
        seen_ids.add(row["post_id"])
    assert seen_ids == {r.id for r in records}

    # Every cluster in clusters.jsonl appears in the mapping with matching size.
    mapping_counts: dict[int, int] = {}
    for line in lines:
        row = json.loads(line)
        mapping_counts[row["cluster_id"]] = mapping_counts.get(row["cluster_id"], 0) + 1
    for summary in summaries:
        assert mapping_counts.get(summary.cluster_id) == summary.size


# -----------------------------------------------------------------------------
# 4. Label generation graceful failure
# -----------------------------------------------------------------------------

class _Block:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class _Resp:
    def __init__(self, text: str) -> None:
        self.content = [_Block(text)]


class _FakeMessages:
    def __init__(self, *, raise_exc: Exception | None = None, text: str = "") -> None:
        self._raise = raise_exc
        self._text = text

    def create(self, **kwargs):  # noqa: ARG002
        if self._raise is not None:
            raise self._raise
        return _Resp(self._text)


class _FakeClient:
    def __init__(self, *, raise_exc: Exception | None = None, text: str = "") -> None:
        self.messages = _FakeMessages(raise_exc=raise_exc, text=text)


def test_label_generation_graceful_failure() -> None:
    post = _record("p001", "jakiś tekst")

    # API raises -> fallback.
    fallback = clu.label_cluster_with_claude(
        _FakeClient(raise_exc=RuntimeError("network down")),
        [post], ["vat"], ["vat deklaracja"],
    )
    assert fallback == {"label": "(unlabeled)", "description": "", "topic_area": "inne"}

    # API returns unparseable text -> fallback.
    fallback2 = clu.label_cluster_with_claude(
        _FakeClient(text="totally not json"),
        [post], ["vat"], ["vat deklaracja"],
    )
    assert fallback2 == {"label": "(unlabeled)", "description": "", "topic_area": "inne"}

    # Topic area outside the whitelist is coerced to "inne".
    good_payload = '{"label": "KSeF offline", "description": "kod QR", "topic_area": "nonsense"}'
    out = clu.label_cluster_with_claude(
        _FakeClient(text=good_payload), [post], ["ksef"], ["kod qr"]
    )
    assert out["label"] == "KSeF offline"
    assert out["topic_area"] == "inne"  # coerced

    # Valid topic area is kept.
    valid_payload = '{"label": "JPK miesięczny", "description": "raport", "topic_area": "JPK"}'
    out2 = clu.label_cluster_with_claude(
        _FakeClient(text=valid_payload), [post], ["jpk"], ["jpk v7"]
    )
    assert out2["topic_area"] == "JPK"


# -----------------------------------------------------------------------------
# 5. Noise records marked correctly
# -----------------------------------------------------------------------------

def test_noise_records_marked_correctly() -> None:
    # 10 records in two tight clusters + 3 outliers drawn from pure noise.
    two = _two_cluster_embeddings(n_per=5, dim=16)
    rng = np.random.default_rng(123)
    outliers = rng.normal(size=(3, 16)).astype(np.float32)
    outliers = clu.normalize_vectors(outliers)
    embeddings = np.vstack([two, outliers]).astype(np.float32)

    labels = clu.cluster_embeddings(embeddings, min_cluster_size=3, min_samples=2)
    # -1 is the HDBSCAN noise label. We need AT LEAST one cluster and allow
    # some noise; this proves the -1 convention is surfaced.
    assert (labels != -1).any(), "expected some clustered points"
    # Outliers (last 3 rows) should often be noise but we don't depend on it —
    # just ensure the label dtype & shape invariants.
    assert labels.shape == (embeddings.shape[0],)
    assert labels.dtype.kind in ("i", "u")

    records = [_record(f"p{i:03d}", "x") for i in range(embeddings.shape[0])]
    noise_picks = clu._noise_sample(records, labels, n=5, seed=0)
    # Every returned record must actually be labelled -1.
    for record in noise_picks:
        idx = records.index(record)
        assert labels[idx] == -1


# -----------------------------------------------------------------------------
# 6. Clustering deterministic
# -----------------------------------------------------------------------------

def test_clustering_deterministic() -> None:
    embeddings = _two_cluster_embeddings(n_per=12, dim=16, seed=42)
    labels_a = clu.cluster_embeddings(embeddings, min_cluster_size=4, min_samples=2)
    labels_b = clu.cluster_embeddings(embeddings, min_cluster_size=4, min_samples=2)
    np.testing.assert_array_equal(labels_a, labels_b)
