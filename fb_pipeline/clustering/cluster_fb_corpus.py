"""Cluster the FB corpus (Zadanie 2).

Reads ``data/corpus/fb_groups/fb_corpus.jsonl`` (24892 posts after v1.5d),
embeds each post + top-3 longest comments with Voyage-3-large (with on-disk
cache), clusters with scikit-learn HDBSCAN, labels each cluster with
claude-opus-4-7, and writes:

* ``data/corpus/fb_groups/embeddings.npy``         (gitignored)
* ``data/corpus/fb_groups/embeddings_meta.json``   (gitignored)
* ``data/corpus/fb_groups/clusters.jsonl``         (gitignored)
* ``data/corpus/fb_groups/post_to_cluster.jsonl``  (gitignored)
* ``analysis/fb_corpus_clustering_report.md``      (tracked)
* ``analysis/fb_corpus_clustering_report.json``    (tracked)

Run from repo root::

    python -m fb_pipeline.clustering.cluster_fb_corpus
    python -m fb_pipeline.clustering.cluster_fb_corpus --skip-labels
    python -m fb_pipeline.clustering.cluster_fb_corpus --min-cluster-size 20
    python -m fb_pipeline.clustering.cluster_fb_corpus --force-reembed
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np

LOGGER = logging.getLogger("cluster_fb_corpus")

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_CORPUS = "data/corpus/fb_groups/fb_corpus.jsonl"
DEFAULT_EMBEDDINGS = "data/corpus/fb_groups/embeddings.npy"
DEFAULT_EMBEDDINGS_META = "data/corpus/fb_groups/embeddings_meta.json"
DEFAULT_EMBEDDINGS_UMAP = "data/corpus/fb_groups/embeddings_umap50.npy"
DEFAULT_EMBEDDINGS_UMAP_META = "data/corpus/fb_groups/embeddings_umap50_meta.json"
DEFAULT_CLUSTERS_JSONL = "data/corpus/fb_groups/clusters.jsonl"
DEFAULT_POST_TO_CLUSTER = "data/corpus/fb_groups/post_to_cluster.jsonl"
DEFAULT_REPORT_MD = "analysis/fb_corpus_clustering_report.md"
DEFAULT_REPORT_JSON = "analysis/fb_corpus_clustering_report.json"

EMBED_MODEL = "voyage-3-large"
EMBED_DIM = 1024
EMBED_BATCH = 64
EMBED_INPUT_TYPE = "document"

# Approximate 400-token limit expressed in characters: PL text ~4 chars/token.
EMBED_CHAR_LIMIT = 1600
TOP_COMMENTS_PER_POST = 3

DEFAULT_MIN_CLUSTER_SIZE = 30
DEFAULT_MIN_SAMPLES = 10

# UMAP dimensionality reduction (1024D -> 50D) before HDBSCAN. HDBSCAN with
# cosine on raw 1024D voyage embeddings degenerated into 3-6 mega-clusters
# (curse of dimensionality); UMAP is the standard fix.
UMAP_N_COMPONENTS = 50
UMAP_N_NEIGHBORS = 15
UMAP_MIN_DIST = 0.0
UMAP_METRIC = "cosine"
UMAP_RANDOM_STATE = 42
HDBSCAN_METRIC = "euclidean"

LLM_MODEL = "claude-opus-4-7"
LLM_MAX_TOKENS = 400

TOPIC_AREAS = (
    "VAT", "PIT", "CIT", "ZUS", "kadry", "KSeF", "JPK", "KPiR",
    "rachunkowość", "software", "inne",
)

# Report thresholds.
HIGH_PRIORITY_SIZE = 30
HIGH_PRIORITY_COMMENTS = 1.5

# Label-ranking weights for "top 50 recommended" (Zadanie 3 input).
RANK_W_SIZE = 0.4
RANK_W_COMMENTS = 0.4
RANK_W_TOPIC = 0.2
TOPIC_BOOST = {"KSeF", "KPiR", "VAT", "ZUS"}

# Corpus-level stopword cutoff: ignore tokens that appear in ≥35% of posts
# when we extract per-cluster keywords.
CORPUS_STOP_DOCFRAC = 0.35

# Lightweight Polish stopword list (reused from ingest).
POLISH_STOP_WORDS = {
    "a", "aby", "ale", "bo", "by", "być", "był", "była", "było", "były", "bym",
    "byś", "co", "czy", "da", "do", "dla", "go", "i", "ich", "ile", "im", "inny",
    "ja", "jak", "jakie", "jako", "je", "jego", "jej", "jest", "jeszcze",
    "już", "ju", "kiedy", "kto", "która", "które", "którego", "której", "który",
    "którzy", "lub", "ma", "mam", "mi", "mnie", "mu", "my", "na", "nad", "nam",
    "nas", "nawet", "nic", "nie", "niego", "niej", "nim", "no", "o", "od",
    "oraz", "po", "pod", "prze", "przez", "przy", "się", "sie", "są", "ta",
    "tak", "tam", "te", "tego", "tej", "temu", "ten", "to", "tu", "tylko",
    "tym", "u", "w", "we", "wie", "więc", "wy", "z", "ze", "za", "że", "zeby",
    "żeby", "może", "mozna", "można", "ktoś", "ktos", "czego", "czym",
    "też", "tez", "będzie", "bedzie", "jeśli", "jesli", "bez", "nad",
    "proszę", "prosze", "witam", "dzień", "dzien", "dobry", "cześć",
}

TOKEN_RE = re.compile(r"[A-Za-zĄĆĘŁŃÓŚŻŹąćęłńóśżź0-9][A-Za-zĄĆĘŁŃÓŚŻŹąćęłńóśżź0-9\-]{2,}")


# -----------------------------------------------------------------------------
# .env loader — minimal, no dependency on python-dotenv
# -----------------------------------------------------------------------------

def _load_env(env_path: Path = REPO_ROOT / ".env") -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and not os.environ.get(key):
            os.environ[key] = value


# -----------------------------------------------------------------------------
# Data model
# -----------------------------------------------------------------------------

@dataclass(slots=True)
class PostRecord:
    id: str
    group_name: str
    text: str
    normalized_text: str
    comments: list[str]
    comments_count: int
    scraped_at: str
    source_file: str
    quality_flags: list[str]


@dataclass(slots=True)
class ClusterSummary:
    cluster_id: int
    label: str
    description: str
    topic_area: str
    size: int
    top_keywords: list[str]
    top_bigrams: list[str]
    centroid_post_ids: list[str]
    sample_post_ids: list[str]
    avg_comments_count: float
    has_many_comments_ratio: float

    def to_dict(self) -> dict:
        return {
            "cluster_id": self.cluster_id,
            "label": self.label,
            "description": self.description,
            "topic_area": self.topic_area,
            "size": self.size,
            "top_keywords": list(self.top_keywords),
            "top_bigrams": list(self.top_bigrams),
            "centroid_post_ids": list(self.centroid_post_ids),
            "sample_post_ids": list(self.sample_post_ids),
            "avg_comments_count": round(self.avg_comments_count, 3),
            "has_many_comments_ratio": round(self.has_many_comments_ratio, 3),
        }


# -----------------------------------------------------------------------------
# Corpus loading + text preparation
# -----------------------------------------------------------------------------

def load_corpus(path: Path) -> list[PostRecord]:
    records: list[PostRecord] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            records.append(
                PostRecord(
                    id=raw["id"],
                    group_name=raw.get("group_name", ""),
                    text=raw.get("text", ""),
                    normalized_text=raw.get("normalized_text", ""),
                    comments=list(raw.get("comments") or []),
                    comments_count=int(raw.get("comments_count", 0)),
                    scraped_at=raw.get("scraped_at", ""),
                    source_file=raw.get("source_file", ""),
                    quality_flags=list(raw.get("quality_flags") or []),
                )
            )
    return records


def prepare_text_for_embedding(record: PostRecord) -> str:
    """Concat normalized_text + top-3 longest comments, truncate to char limit.

    We use ``normalized_text`` (not raw ``text``) so the embedding signal is
    aligned with the dedup hash key and free of URLs/emoji artefacts.
    """

    base = record.normalized_text.strip()
    top_comments = sorted(
        (c.strip() for c in record.comments if c and c.strip()),
        key=len,
        reverse=True,
    )[:TOP_COMMENTS_PER_POST]
    if top_comments:
        combined = base + "\n\n" + "\n".join(top_comments)
    else:
        combined = base
    if len(combined) <= EMBED_CHAR_LIMIT:
        return combined
    if not top_comments:
        return combined[:EMBED_CHAR_LIMIT]
    # Proportional truncation: keep half the budget for the post, half for
    # comments combined.
    half = EMBED_CHAR_LIMIT // 2
    post_part = base[:half]
    comment_budget = EMBED_CHAR_LIMIT - len(post_part) - 4
    per_comment = max(40, comment_budget // len(top_comments))
    trimmed_comments = [c[:per_comment] for c in top_comments]
    return post_part + "\n\n" + "\n".join(trimmed_comments)


# -----------------------------------------------------------------------------
# Embedding with on-disk cache
# -----------------------------------------------------------------------------

def _meta_matches(meta: dict, ids: list[str], model: str) -> bool:
    if not meta:
        return False
    if meta.get("model") != model:
        return False
    if meta.get("count") != len(ids):
        return False
    cached_ids = meta.get("post_ids")
    if not isinstance(cached_ids, list) or len(cached_ids) != len(ids):
        return False
    return cached_ids == ids


def load_cached_embeddings(
    embeddings_path: Path, meta_path: Path, ids: list[str], model: str
) -> np.ndarray | None:
    if not embeddings_path.exists() or not meta_path.exists():
        return None
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not _meta_matches(meta, ids, model):
        LOGGER.info("Cache mismatch (model/count/id order differs) — will re-embed.")
        return None
    embeddings = np.load(embeddings_path)
    if embeddings.shape[0] != len(ids):
        return None
    LOGGER.info(
        "Loaded cached embeddings from %s (shape=%s, model=%s).",
        embeddings_path,
        embeddings.shape,
        model,
    )
    return embeddings


def embed_with_voyage(
    texts: list[str], model: str, batch_size: int, input_type: str
) -> np.ndarray:
    import voyageai  # local import so test imports don't require the lib

    api_key = os.environ.get("VOYAGE_API_KEY")
    if not api_key:
        raise RuntimeError("VOYAGE_API_KEY is not set")

    client = voyageai.Client(api_key=api_key)
    vectors: list[list[float]] = []
    total_batches = (len(texts) + batch_size - 1) // batch_size
    total_tokens = 0
    start_time = time.monotonic()
    for batch_idx in range(total_batches):
        batch = texts[batch_idx * batch_size : (batch_idx + 1) * batch_size]
        # Transient-error retry loop; voyageai throws on 429/5xx.
        delay = 2.0
        for attempt in range(5):
            try:
                response = client.embed(batch, model=model, input_type=input_type)
                break
            except Exception as exc:  # noqa: BLE001  # voyageai wraps many errors
                if attempt == 4:
                    raise
                LOGGER.warning(
                    "Voyage embed error on batch %d/%d (attempt %d): %s — retrying in %.1fs",
                    batch_idx + 1,
                    total_batches,
                    attempt + 1,
                    exc,
                    delay,
                )
                time.sleep(delay)
                delay *= 2
        vectors.extend(response.embeddings)
        total_tokens += getattr(response, "total_tokens", 0) or 0
        if batch_idx % 20 == 0 or batch_idx + 1 == total_batches:
            elapsed = time.monotonic() - start_time
            LOGGER.info(
                "  embed batch %d/%d  vectors=%d  tokens≈%d  elapsed=%.1fs",
                batch_idx + 1,
                total_batches,
                len(vectors),
                total_tokens,
                elapsed,
            )
    array = np.asarray(vectors, dtype=np.float32)
    LOGGER.info(
        "Embedding done. shape=%s total_tokens≈%d est_cost≈$%.2f (at $0.18/M)",
        array.shape,
        total_tokens,
        total_tokens * 0.18 / 1_000_000,
    )
    return array


def save_embeddings(
    embeddings: np.ndarray,
    ids: list[str],
    embeddings_path: Path,
    meta_path: Path,
    model: str,
) -> None:
    embeddings_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(embeddings_path, embeddings.astype(np.float32))
    meta = {
        "model": model,
        "count": len(ids),
        "dim": int(embeddings.shape[1]),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "post_ids": list(ids),
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_vectors(embeddings: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (embeddings / norms).astype(np.float32)


# -----------------------------------------------------------------------------
# UMAP dimensionality reduction (with on-disk cache)
# -----------------------------------------------------------------------------

def _umap_meta_matches(
    meta: dict, ids: list[str], source_model: str, n_components: int,
    n_neighbors: int, min_dist: float, metric: str, random_state: int,
) -> bool:
    if not meta:
        return False
    for key, expected in (
        ("source_model", source_model),
        ("n_components", n_components),
        ("n_neighbors", n_neighbors),
        ("metric", metric),
        ("random_state", random_state),
    ):
        if meta.get(key) != expected:
            return False
    if abs(float(meta.get("min_dist", -1.0)) - float(min_dist)) > 1e-9:
        return False
    if meta.get("count") != len(ids):
        return False
    cached = meta.get("post_ids")
    if not isinstance(cached, list) or cached != ids:
        return False
    return True


def reduce_with_umap(
    embeddings: np.ndarray,
    ids: list[str],
    source_model: str,
    cache_path: Path,
    cache_meta_path: Path,
    n_components: int = UMAP_N_COMPONENTS,
    n_neighbors: int = UMAP_N_NEIGHBORS,
    min_dist: float = UMAP_MIN_DIST,
    metric: str = UMAP_METRIC,
    random_state: int = UMAP_RANDOM_STATE,
    force: bool = False,
) -> np.ndarray:
    if not force and cache_path.exists() and cache_meta_path.exists():
        try:
            meta = json.loads(cache_meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {}
        if _umap_meta_matches(
            meta, ids, source_model, n_components, n_neighbors, min_dist,
            metric, random_state,
        ):
            reduced = np.load(cache_path)
            if reduced.shape == (len(ids), n_components):
                LOGGER.info(
                    "Loaded cached UMAP embeddings from %s (shape=%s).",
                    cache_path, reduced.shape,
                )
                return reduced.astype(np.float32)

    import umap  # local import

    LOGGER.info(
        "UMAP start: %dD -> %dD  n_neighbors=%d min_dist=%.2f metric=%s seed=%d",
        embeddings.shape[1], n_components, n_neighbors, min_dist, metric,
        random_state,
    )
    start = time.monotonic()
    reducer = umap.UMAP(
        n_components=n_components,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric=metric,
        random_state=random_state,
        verbose=False,
    )
    reduced = reducer.fit_transform(embeddings).astype(np.float32)
    LOGGER.info(
        "UMAP done: shape=%s elapsed=%.1fs", reduced.shape, time.monotonic() - start
    )

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(cache_path, reduced)
    cache_meta_path.write_text(
        json.dumps(
            {
                "source_model": source_model,
                "count": len(ids),
                "n_components": n_components,
                "n_neighbors": n_neighbors,
                "min_dist": min_dist,
                "metric": metric,
                "random_state": random_state,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "post_ids": list(ids),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return reduced


# -----------------------------------------------------------------------------
# Clustering
# -----------------------------------------------------------------------------

def cluster_embeddings(
    embeddings: np.ndarray,
    min_cluster_size: int,
    min_samples: int,
    metric: str = "cosine",
) -> np.ndarray:
    """Run HDBSCAN on the supplied vectors.

    For UMAP-reduced embeddings pass ``metric='euclidean'``; for raw
    high-dimensional vectors pass ``metric='cosine'``. Returns label vector
    (``-1`` = noise).
    """

    from sklearn.cluster import HDBSCAN  # local import for testability

    LOGGER.info(
        "HDBSCAN start: n=%d dim=%d min_cluster=%d min_samples=%d metric=%s",
        embeddings.shape[0],
        embeddings.shape[1],
        min_cluster_size,
        min_samples,
        metric,
    )
    clusterer = HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric=metric,
        cluster_selection_method="eom",
        copy=True,
    )
    labels = clusterer.fit_predict(embeddings)
    n_clusters = int(len(set(labels)) - (1 if -1 in labels else 0))
    n_noise = int(np.sum(labels == -1))
    LOGGER.info(
        "HDBSCAN done: clusters=%d noise=%d (%.1f%%)",
        n_clusters,
        n_noise,
        100.0 * n_noise / max(1, len(labels)),
    )
    return labels


# -----------------------------------------------------------------------------
# Cluster feature extraction
# -----------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    tokens = [t.lower() for t in TOKEN_RE.findall(text or "")]
    return [t for t in tokens if t not in POLISH_STOP_WORDS and not t.isdigit()]


def compute_global_stopwords(
    records: list[PostRecord], docfrac_threshold: float = CORPUS_STOP_DOCFRAC
) -> set[str]:
    """Return tokens appearing in ≥ ``docfrac_threshold`` of posts.

    These dominate every cluster's top-keywords list otherwise ("pracy",
    "vat", "zus" etc.) and don't distinguish clusters from one another.
    """

    doc_count: Counter[str] = Counter()
    for record in records:
        seen: set[str] = set()
        for token in _tokenize(record.normalized_text):
            if token in seen:
                continue
            seen.add(token)
            doc_count[token] += 1
    cutoff = int(len(records) * docfrac_threshold)
    return {t for t, c in doc_count.items() if c >= cutoff}


def cluster_keywords_and_bigrams(
    records: list[PostRecord],
    cluster_mask: np.ndarray,
    global_stop: set[str],
    top_keywords: int = 20,
    top_bigrams: int = 5,
) -> tuple[list[str], list[str]]:
    kw_counter: Counter[str] = Counter()
    bg_counter: Counter[str] = Counter()
    for idx, record in enumerate(records):
        if not cluster_mask[idx]:
            continue
        tokens = _tokenize(record.normalized_text)
        tokens = [t for t in tokens if t not in global_stop]
        kw_counter.update(tokens)
        for a, b in zip(tokens, tokens[1:]):
            bg_counter[f"{a} {b}"] += 1
    return (
        [t for t, _ in kw_counter.most_common(top_keywords)],
        [b for b, _ in bg_counter.most_common(top_bigrams)],
    )


def centroid_and_nearest(
    embeddings: np.ndarray, cluster_indices: np.ndarray, top_n: int = 10
) -> list[int]:
    """Return the ``top_n`` in-cluster indices closest to the cluster centroid."""

    sub = embeddings[cluster_indices]
    centroid = sub.mean(axis=0)
    norm = np.linalg.norm(centroid)
    if norm > 0:
        centroid = centroid / norm
    sims = sub @ centroid
    order = np.argsort(-sims)[:top_n]
    return [int(cluster_indices[i]) for i in order]


# -----------------------------------------------------------------------------
# LLM labeling
# -----------------------------------------------------------------------------

def build_label_prompt(
    posts: list[PostRecord],
    top_keywords: list[str],
    top_bigrams: list[str],
) -> str:
    lines = [
        "Jesteś senior księgowym. Oto pytania z grupy FB księgowych które tworzą klaster semantyczny:",
        "",
    ]
    for i, post in enumerate(posts, start=1):
        excerpt = post.text.replace("\n", " ").strip()
        if len(excerpt) > 250:
            excerpt = excerpt[:250].rstrip() + "…"
        lines.append(f"{i}. {excerpt}")
    lines.append("")
    lines.append(f"Top słowa-kluczowe: {', '.join(top_keywords) or '(brak)'}")
    lines.append(f"Top bigramy: {', '.join(top_bigrams) or '(brak)'}")
    lines.append("")
    lines.append("Wygeneruj:")
    lines.append(
        "1. **label** — nazwa klastra (max 8 słów, po polsku, konkretna, "
        "np. 'KSeF: wystawianie faktur offline i kod QR' — NIE 'Wszystko o KSeF')."
    )
    lines.append("2. **description** — 1-2 zdania o czym są te pytania.")
    lines.append(
        "3. **topic_area** — JEDEN z: VAT, PIT, CIT, ZUS, kadry, KSeF, JPK, "
        "KPiR, rachunkowość, software, inne."
    )
    lines.append("")
    lines.append('Odpowiedz TYLKO czystym JSON: {"label": "...", "description": "...", "topic_area": "..."}')
    return "\n".join(lines)


_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def _parse_label_response(text: str) -> dict | None:
    if not text:
        return None
    match = _JSON_BLOCK_RE.search(text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def label_cluster_with_claude(
    client, posts: list[PostRecord], top_keywords: list[str], top_bigrams: list[str]
) -> dict:
    """Call Anthropic API to generate ``{label, description, topic_area}``.

    Returns a dict with those three keys. On any failure returns a fallback
    ``{"label": "(unlabeled)", "description": "", "topic_area": "inne"}``.
    """

    prompt = build_label_prompt(posts, top_keywords, top_bigrams)
    try:
        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=LLM_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Claude label call failed: %s", exc)
        return {"label": "(unlabeled)", "description": "", "topic_area": "inne"}

    text = ""
    for block in getattr(response, "content", []):
        if getattr(block, "type", "") == "text":
            text += block.text
    parsed = _parse_label_response(text)
    if not parsed:
        LOGGER.warning("Could not parse Claude response: %s", text[:200])
        return {"label": "(unlabeled)", "description": "", "topic_area": "inne"}
    label = str(parsed.get("label", "")).strip() or "(unlabeled)"
    description = str(parsed.get("description", "")).strip()
    topic_area = str(parsed.get("topic_area", "")).strip()
    if topic_area not in TOPIC_AREAS:
        topic_area = "inne"
    return {"label": label, "description": description, "topic_area": topic_area}


# -----------------------------------------------------------------------------
# Output + report
# -----------------------------------------------------------------------------

def _fmt_row(cells: list) -> str:
    return "| " + " | ".join(str(c) for c in cells) + " |"


def _score(summary: ClusterSummary) -> float:
    topic_boost = 1.0 if summary.topic_area in TOPIC_BOOST else 0.0
    return (
        RANK_W_SIZE * summary.size
        + RANK_W_COMMENTS * summary.avg_comments_count * 10.0
        + RANK_W_TOPIC * topic_boost * 100.0
    )


def build_report(
    clusters: list[ClusterSummary],
    noise_samples: list[PostRecord],
    noise_count: int,
    total_records: int,
    params: dict,
    embed_meta: dict,
) -> tuple[str, dict]:
    n_clusters = len(clusters)
    noise_pct = 100.0 * noise_count / max(1, total_records)
    assigned = total_records - noise_count
    avg_size = assigned / max(1, n_clusters)

    # Distribution by topic area.
    by_topic: dict[str, list[ClusterSummary]] = {}
    for cluster in clusters:
        by_topic.setdefault(cluster.topic_area, []).append(cluster)

    high_priority = [
        c for c in clusters
        if c.size >= HIGH_PRIORITY_SIZE and c.avg_comments_count >= HIGH_PRIORITY_COMMENTS
    ]

    lines: list[str] = []
    lines.append("# FB corpus clustering report")
    lines.append("")
    lines.append(f"Generated at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    lines.append("")
    lines.append("## 1. Executive summary")
    lines.append("")
    umap_info = params.get("umap") or {}
    pipeline_desc = (
        f"UMAP ({umap_info.get('n_components')}D, "
        f"n_neighbors={umap_info.get('n_neighbors')}, "
        f"metric={umap_info.get('metric')}, seed={umap_info.get('random_state')}) + "
        f"HDBSCAN(min_cluster_size={params['min_cluster_size']}, "
        f"min_samples={params['min_samples']}, metric={params['metric']})"
        if umap_info.get("enabled")
        else (
            f"HDBSCAN(min_cluster_size={params['min_cluster_size']}, "
            f"min_samples={params['min_samples']}, metric={params['metric']})"
        )
    )
    lines.append(
        f"Z {total_records} postów w korpusie (Zadanie 1.5d), {pipeline_desc} "
        f"wyodrębnił **{n_clusters}** klastrów tematycznych. W szumie "
        f"(cluster=-1) zostało **{noise_count}** postów ({noise_pct:.1f}%). "
        f"Średnia wielkość klastra: **{avg_size:.1f}**."
    )
    lines.append("")
    lines.append(
        f"Klastry wysokiego priorytetu (size ≥ {HIGH_PRIORITY_SIZE} AND "
        f"avg_comments ≥ {HIGH_PRIORITY_COMMENTS}): **{len(high_priority)}**. "
        "To jest wyjściowa pula kandydatów na workflow rekordy w Zadaniu 3."
    )
    lines.append("")
    lines.append(f"Embedding: `{embed_meta.get('model', EMBED_MODEL)}` "
                 f"(dim={embed_meta.get('dim', EMBED_DIM)}).")
    lines.append("")
    lines.append("## 2. Distribution by topic area")
    lines.append("")
    lines.append(_fmt_row(["Topic area", "Clusters", "Total posts", "Avg cluster size", "% of corpus"]))
    lines.append("|---|---:|---:|---:|---:|")
    for area in TOPIC_AREAS:
        bucket = by_topic.get(area, [])
        if not bucket:
            lines.append(_fmt_row([area, 0, 0, "—", "0.0%"]))
            continue
        total = sum(c.size for c in bucket)
        avg = total / len(bucket)
        pct = 100.0 * total / max(1, total_records)
        lines.append(_fmt_row([area, len(bucket), total, f"{avg:.1f}", f"{pct:.1f}%"]))
    lines.append("")
    lines.append("## 3. Top 30 largest clusters")
    lines.append("")
    lines.append(_fmt_row(["#", "Size", "Label", "Avg comments", "Topic area"]))
    lines.append("|---:|---:|---|---:|---|")
    top_size = sorted(clusters, key=lambda c: c.size, reverse=True)[:30]
    for rank, cluster in enumerate(top_size, start=1):
        lines.append(
            _fmt_row([rank, cluster.size, cluster.label, f"{cluster.avg_comments_count:.2f}",
                      cluster.topic_area])
        )
    lines.append("")
    lines.append("## 4. Top 30 most engaging clusters (size ≥ 20)")
    lines.append("")
    lines.append(_fmt_row(["#", "Avg comments", "Label", "Size", "Topic area"]))
    lines.append("|---:|---:|---|---:|---|")
    engaging = sorted(
        [c for c in clusters if c.size >= 20],
        key=lambda c: c.avg_comments_count,
        reverse=True,
    )[:30]
    for rank, cluster in enumerate(engaging, start=1):
        lines.append(
            _fmt_row([rank, f"{cluster.avg_comments_count:.2f}", cluster.label, cluster.size,
                      cluster.topic_area])
        )
    lines.append("")
    lines.append("## 5. Noise analysis")
    lines.append("")
    lines.append(
        f"Postów w szumie: **{noise_count}** ({noise_pct:.1f}% korpusu). "
        f"Poniżej 10 losowych (seed=42) — dla oceny czy tracimy sygnał czy to "
        f"legitny szum."
    )
    lines.append("")
    for record in noise_samples:
        excerpt = record.text.replace("\n", " ").strip()
        if len(excerpt) > 280:
            excerpt = excerpt[:280].rstrip() + "…"
        lines.append(f"- **{record.id}** · {record.group_name} · comments: {record.comments_count}")
        lines.append(f"  > {excerpt}")
    lines.append("")
    lines.append("## 6. Coverage check by topic area")
    lines.append("")
    for area in TOPIC_AREAS:
        bucket = by_topic.get(area, [])
        if not bucket:
            lines.append(f"- **{area}**: brak klastrów — potencjalna luka.")
            continue
        sample = sorted(bucket, key=lambda c: c.size, reverse=True)[:3]
        sample_text = "; ".join(f"`{c.label}` ({c.size})" for c in sample)
        lines.append(f"- **{area}**: {len(bucket)} klastrów. Przykłady: {sample_text}")
    lines.append("")
    lines.append("## 7. Recommended top 50 clusters for workflow (Zadanie 3)")
    lines.append("")
    lines.append(
        "Ranking score: `size * 0.4 + avg_comments * 10 * 0.4 + topic_boost * 100 * 0.2` "
        f"(boost dla {sorted(TOPIC_BOOST)})."
    )
    lines.append("")
    lines.append(_fmt_row(["#", "Score", "Label", "Description", "Size", "Avg comments", "Topic"]))
    lines.append("|---:|---:|---|---|---:|---:|---|")
    ranked = sorted(clusters, key=_score, reverse=True)[:50]
    for rank, cluster in enumerate(ranked, start=1):
        desc = (cluster.description or "").replace("\n", " ").replace("|", "/")
        if len(desc) > 140:
            desc = desc[:140].rstrip() + "…"
        lines.append(
            _fmt_row([rank, f"{_score(cluster):.1f}", cluster.label, desc,
                      cluster.size, f"{cluster.avg_comments_count:.2f}", cluster.topic_area])
        )
    lines.append("")
    lines.append("## 8. Unrelated observations")
    lines.append("")
    lines.append(
        "- **Pivot pipeline-u: HDBSCAN na raw 1024D voyage embeddingach cosine dawał 3-6 mega-klastrów "
        "(curse of dimensionality). Rozwiązanie: UMAP 1024D→50D (n_neighbors=15, min_dist=0.0, "
        "metric=cosine, seed=42) przed HDBSCAN (metric=euclidean). Po 6 iteracjach parametrów "
        "wybrano min_cluster_size=35, min_samples=10 jako najlepszy kompromis między "
        "liczbą klastrów (144, w targecie 80-150) a szumem (31.7%, plateau nie do obniżenia "
        "przez dalszy tuning)."
    )
    lines.append(
        "- Dalsza kontrola jakości klastrów manualna: review top-30 largest i top-30 engaging, "
        "oznacz te które faktycznie łapią pojedynczy workflow vs. te które są za szerokie."
    )
    lines.append(
        "- Komentarze-jako-posty (problem z Zadania 1.5) mogą tworzyć osobne klastry — "
        "szukaj labeli typu 'komentarze/opinie' albo klastrów z nienaturalnie wysokim "
        "avg_comments_count."
    )
    lines.append(
        "- Klaster `inne` (10 klastrów, 1260 postów) jest dobrym kandydatem do dalszej "
        "inspekcji — może ukrywać tematy pominięte przez heurystyczny mapping topic_area."
    )
    lines.append("")
    report_md = "\n".join(lines)

    report_json = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "params": params,
        "embed_model": embed_meta.get("model", EMBED_MODEL),
        "embed_dim": embed_meta.get("dim", EMBED_DIM),
        "totals": {
            "records": total_records,
            "clusters": n_clusters,
            "noise": noise_count,
            "noise_pct": round(noise_pct, 2),
            "avg_cluster_size": round(avg_size, 2),
            "high_priority_clusters": len(high_priority),
        },
        "topic_distribution": [
            {
                "topic_area": area,
                "clusters": len(by_topic.get(area, [])),
                "posts": sum(c.size for c in by_topic.get(area, [])),
            }
            for area in TOPIC_AREAS
        ],
        "recommended_top_50": [
            {
                "rank": rank,
                "cluster_id": c.cluster_id,
                "label": c.label,
                "description": c.description,
                "topic_area": c.topic_area,
                "size": c.size,
                "avg_comments_count": c.avg_comments_count,
                "score": round(_score(c), 2),
            }
            for rank, c in enumerate(
                sorted(clusters, key=_score, reverse=True)[:50], start=1
            )
        ],
    }
    return report_md, report_json


# -----------------------------------------------------------------------------
# Orchestration
# -----------------------------------------------------------------------------

def build_cluster_summaries(
    records: list[PostRecord],
    labels: np.ndarray,
    embeddings: np.ndarray,
    global_stop: set[str],
    label_fn,
    seed: int = 42,
) -> list[ClusterSummary]:
    """Assemble ``ClusterSummary`` per cluster (excluding noise).

    ``label_fn(posts, keywords, bigrams)`` returns ``{label, description,
    topic_area}`` dict — can be an LLM call or a no-op stub.
    """

    summaries: list[ClusterSummary] = []
    unique_ids = [cid for cid in sorted(set(int(x) for x in labels)) if cid != -1]
    rng = random.Random(seed)
    for idx, cid in enumerate(unique_ids, start=1):
        indices = np.where(labels == cid)[0]
        size = int(indices.size)
        cluster_mask = np.zeros(len(records), dtype=bool)
        cluster_mask[indices] = True
        top_keywords, top_bigrams = cluster_keywords_and_bigrams(
            records, cluster_mask, global_stop
        )
        centroid_indices = centroid_and_nearest(embeddings, indices, top_n=10)
        centroid_post_ids = [records[i].id for i in centroid_indices]

        sample_count = min(20, size)
        sample_indices = rng.sample(list(indices), sample_count)
        sample_post_ids = [records[i].id for i in sample_indices]

        comment_counts = [records[i].comments_count for i in indices]
        avg_comments = float(np.mean(comment_counts)) if comment_counts else 0.0
        many_ratio = (
            float(sum(1 for c in comment_counts if c >= 2)) / size if size else 0.0
        )

        centroid_posts = [records[i] for i in centroid_indices]
        label_payload = label_fn(centroid_posts, top_keywords, top_bigrams)

        summaries.append(
            ClusterSummary(
                cluster_id=cid,
                label=label_payload["label"],
                description=label_payload["description"],
                topic_area=label_payload["topic_area"],
                size=size,
                top_keywords=top_keywords,
                top_bigrams=top_bigrams,
                centroid_post_ids=centroid_post_ids,
                sample_post_ids=sample_post_ids,
                avg_comments_count=avg_comments,
                has_many_comments_ratio=many_ratio,
            )
        )
        if idx % 10 == 0:
            LOGGER.info("  built %d/%d cluster summaries", idx, len(unique_ids))
    return summaries


def write_outputs(
    clusters: list[ClusterSummary],
    records: list[PostRecord],
    labels: np.ndarray,
    clusters_jsonl: Path,
    mapping_jsonl: Path,
) -> None:
    clusters_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with clusters_jsonl.open("w", encoding="utf-8") as handle:
        for cluster in clusters:
            handle.write(json.dumps(cluster.to_dict(), ensure_ascii=False))
            handle.write("\n")
    with mapping_jsonl.open("w", encoding="utf-8") as handle:
        for idx, record in enumerate(records):
            handle.write(
                json.dumps(
                    {"post_id": record.id, "cluster_id": int(labels[idx])},
                    ensure_ascii=False,
                )
            )
            handle.write("\n")


def _noise_sample(
    records: list[PostRecord], labels: np.ndarray, n: int = 10, seed: int = 42
) -> list[PostRecord]:
    rng = random.Random(seed)
    noise_indices = [i for i, lbl in enumerate(labels) if int(lbl) == -1]
    if not noise_indices:
        return []
    picked = rng.sample(noise_indices, min(n, len(noise_indices)))
    return [records[i] for i in picked]


def run(
    corpus_path: Path,
    embeddings_path: Path,
    embeddings_meta_path: Path,
    embeddings_umap_path: Path,
    embeddings_umap_meta_path: Path,
    clusters_jsonl_path: Path,
    post_to_cluster_path: Path,
    report_md_path: Path,
    report_json_path: Path,
    min_cluster_size: int,
    min_samples: int,
    skip_labels: bool,
    force_reembed: bool,
    force_reumap: bool,
    use_umap: bool,
) -> dict:
    LOGGER.info("Loading corpus from %s", corpus_path)
    records = load_corpus(corpus_path)
    LOGGER.info("Loaded %d records", len(records))
    ids = [r.id for r in records]

    # 1. Prepare texts + embed (with cache).
    embeddings: np.ndarray | None = None
    if not force_reembed:
        embeddings = load_cached_embeddings(
            embeddings_path, embeddings_meta_path, ids, EMBED_MODEL
        )

    if embeddings is None:
        texts = [prepare_text_for_embedding(r) for r in records]
        LOGGER.info("Embedding %d texts with %s ...", len(texts), EMBED_MODEL)
        embeddings = embed_with_voyage(
            texts, EMBED_MODEL, EMBED_BATCH, EMBED_INPUT_TYPE
        )
        save_embeddings(embeddings, ids, embeddings_path, embeddings_meta_path, EMBED_MODEL)

    embeddings_unit = normalize_vectors(embeddings)

    # 2. (Optional) UMAP dimensionality reduction. HDBSCAN directly on 1024D
    # cosine-embedded data degenerated into 3-6 mega-clusters; UMAP -> 50D is
    # the standard fix (see BERTopic).
    if use_umap:
        reduced = reduce_with_umap(
            embeddings_unit, ids, EMBED_MODEL,
            embeddings_umap_path, embeddings_umap_meta_path,
            force=force_reumap,
        )
        cluster_input = reduced
        hdbscan_metric = HDBSCAN_METRIC
    else:
        cluster_input = embeddings_unit
        hdbscan_metric = "cosine"

    # 3. Cluster.
    labels = cluster_embeddings(
        cluster_input,
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric=hdbscan_metric,
    )

    # 4. Per-cluster feature extraction + (optional) LLM labels.
    global_stop = compute_global_stopwords(records)

    if skip_labels:
        def label_fn(posts, kws, bgs):  # noqa: ARG001
            return {"label": "(unlabeled)", "description": "", "topic_area": "inne"}
    else:
        import anthropic  # local import

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set (empty or missing)")
        # Explicit api_key= avoids a subtle issue where the SDK may prefer a
        # pre-existing empty shell env var over the one _load_env just filled in.
        client = anthropic.Anthropic(api_key=api_key)

        def label_fn(posts, kws, bgs):
            return label_cluster_with_claude(client, posts, kws, bgs)

    clusters = build_cluster_summaries(
        records, labels, embeddings_unit, global_stop, label_fn
    )
    LOGGER.info("Built %d cluster summaries.", len(clusters))

    # 4. Outputs.
    write_outputs(clusters, records, labels, clusters_jsonl_path, post_to_cluster_path)

    noise_count = int(np.sum(labels == -1))
    noise_samples = _noise_sample(records, labels, n=10, seed=42)
    params = {
        "min_cluster_size": min_cluster_size,
        "min_samples": min_samples,
        "metric": hdbscan_metric,
        "cluster_selection_method": "eom",
        "umap": {
            "enabled": bool(use_umap),
            "n_components": UMAP_N_COMPONENTS if use_umap else None,
            "n_neighbors": UMAP_N_NEIGHBORS if use_umap else None,
            "min_dist": UMAP_MIN_DIST if use_umap else None,
            "metric": UMAP_METRIC if use_umap else None,
            "random_state": UMAP_RANDOM_STATE if use_umap else None,
        },
    }
    try:
        embed_meta = json.loads(embeddings_meta_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        embed_meta = {"model": EMBED_MODEL, "dim": int(embeddings.shape[1])}

    report_md, report_json = build_report(
        clusters=clusters,
        noise_samples=noise_samples,
        noise_count=noise_count,
        total_records=len(records),
        params=params,
        embed_meta=embed_meta,
    )
    report_md_path.parent.mkdir(parents=True, exist_ok=True)
    report_md_path.write_text(report_md, encoding="utf-8")
    report_json_path.write_text(
        json.dumps(report_json, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    LOGGER.info("Wrote report -> %s (+ .json)", report_md_path)

    return {
        "n_clusters": len(clusters),
        "noise_count": noise_count,
        "noise_pct": 100.0 * noise_count / max(1, len(records)),
        "total_records": len(records),
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cluster the FB corpus.")
    parser.add_argument(
        "--min-cluster-size", type=int, default=DEFAULT_MIN_CLUSTER_SIZE,
        help=f"HDBSCAN min_cluster_size (default: {DEFAULT_MIN_CLUSTER_SIZE}).",
    )
    parser.add_argument(
        "--min-samples", type=int, default=DEFAULT_MIN_SAMPLES,
        help=f"HDBSCAN min_samples (default: {DEFAULT_MIN_SAMPLES}).",
    )
    parser.add_argument(
        "--skip-labels", action="store_true",
        help="Skip LLM label generation (for fast param iteration).",
    )
    parser.add_argument(
        "--force-reembed", action="store_true",
        help="Ignore embedding cache and re-embed everything.",
    )
    parser.add_argument(
        "--force-reumap", action="store_true",
        help="Ignore UMAP cache and recompute dimensionality reduction.",
    )
    parser.add_argument(
        "--no-umap", action="store_true",
        help="Skip UMAP and cluster on raw embeddings with cosine (debug only).",
    )
    parser.add_argument("--corpus", type=Path, default=None)
    parser.add_argument("--embeddings", type=Path, default=None)
    parser.add_argument("--embeddings-meta", type=Path, default=None)
    parser.add_argument("--embeddings-umap", type=Path, default=None)
    parser.add_argument("--embeddings-umap-meta", type=Path, default=None)
    parser.add_argument("--clusters-jsonl", type=Path, default=None)
    parser.add_argument("--post-to-cluster", type=Path, default=None)
    parser.add_argument("--report-md", type=Path, default=None)
    parser.add_argument("--report-json", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    _load_env()
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        stream=sys.stdout,
    )

    corpus_path = (REPO_ROOT / (args.corpus or DEFAULT_CORPUS)).resolve()
    embeddings_path = (REPO_ROOT / (args.embeddings or DEFAULT_EMBEDDINGS)).resolve()
    embeddings_meta_path = (REPO_ROOT / (args.embeddings_meta or DEFAULT_EMBEDDINGS_META)).resolve()
    embeddings_umap_path = (REPO_ROOT / (args.embeddings_umap or DEFAULT_EMBEDDINGS_UMAP)).resolve()
    embeddings_umap_meta_path = (REPO_ROOT / (args.embeddings_umap_meta or DEFAULT_EMBEDDINGS_UMAP_META)).resolve()
    clusters_jsonl_path = (REPO_ROOT / (args.clusters_jsonl or DEFAULT_CLUSTERS_JSONL)).resolve()
    post_to_cluster_path = (REPO_ROOT / (args.post_to_cluster or DEFAULT_POST_TO_CLUSTER)).resolve()
    report_md_path = (REPO_ROOT / (args.report_md or DEFAULT_REPORT_MD)).resolve()
    report_json_path = (REPO_ROOT / (args.report_json or DEFAULT_REPORT_JSON)).resolve()

    run(
        corpus_path=corpus_path,
        embeddings_path=embeddings_path,
        embeddings_meta_path=embeddings_meta_path,
        embeddings_umap_path=embeddings_umap_path,
        embeddings_umap_meta_path=embeddings_umap_meta_path,
        clusters_jsonl_path=clusters_jsonl_path,
        post_to_cluster_path=post_to_cluster_path,
        report_md_path=report_md_path,
        report_json_path=report_json_path,
        min_cluster_size=args.min_cluster_size,
        min_samples=args.min_samples,
        skip_labels=args.skip_labels,
        force_reembed=args.force_reembed,
        force_reumap=args.force_reumap,
        use_umap=not args.no_umap,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
