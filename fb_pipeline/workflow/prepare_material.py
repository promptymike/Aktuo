"""Assemble per-cluster material for workflow-draft generation.

For each target cluster we gather:
1. **Centroid posts** — top-k closest to the centroid in the 1024D Voyage
   space (cosine). Proxy for "typical" questions in the cluster.
2. **High-engagement posts** — comments_count >= 3, sorted by text length,
   top-k (dedup with centroid). Proxy for rich community discussions.
3. **KB candidates** — BM25+vector RRF retrieval against
   ``data/seeds/law_knowledge.json`` for label+keywords. Opus picks 1-3.

Merged clusters (IDs like ``"merge[120+121]"``) pool post_ids from every
source cluster before building the centroid.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import numpy as np


@dataclass
class ClusterSpec:
    target_key: str          # identifier used in filenames / metadata
    source_cluster_ids: list[int]
    label: str
    topic_area: str


@dataclass
class CentroidPost:
    post_id: str
    text: str
    comments_count: int
    longest_comments: list[str] = field(default_factory=list)
    cosine_to_centroid: float = 0.0


@dataclass
class HighEngagementPost:
    post_id: str
    text: str
    comments_count: int
    all_comments: list[str]
    text_length: int


@dataclass
class LegalAnchorCandidate:
    law_name: str
    article_number: str
    category: str
    content_preview: str
    score: float


@dataclass
class ClusterMaterial:
    spec: ClusterSpec
    size: int
    avg_comments: float
    top_keywords: list[str]
    top_bigrams: list[str]
    centroid_posts: list[CentroidPost]
    high_engagement_posts: list[HighEngagementPost]
    legal_candidates: list[LegalAnchorCandidate]


# ------------------------- Loaders (all pure reads) -------------------------

def load_post_to_cluster(path: Path) -> dict[str, int]:
    mapping: dict[str, int] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            mapping[row["post_id"]] = int(row["cluster_id"])
    return mapping


def load_corpus(path: Path) -> dict[str, dict]:
    index: dict[str, dict] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            index[row["id"]] = row
    return index


def load_clusters(path: Path) -> dict[int, dict]:
    index: dict[int, dict] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row["cluster_id"] == -1:
                continue
            index[int(row["cluster_id"])] = row
    return index


def load_embeddings(
    emb_path: Path, meta_path: Path
) -> tuple[list[str], np.ndarray]:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    ids = list(meta["post_ids"])
    matrix = np.load(emb_path)
    if matrix.shape[0] != len(ids):
        raise RuntimeError(
            f"embeddings row count {matrix.shape[0]} != meta ids {len(ids)}"
        )
    return ids, matrix.astype(np.float32)


# ------------------------- Centroid / nearest -------------------------

def members_for_spec(
    spec: ClusterSpec, post_to_cluster: dict[str, int]
) -> list[str]:
    target = set(spec.source_cluster_ids)
    return [pid for pid, cid in post_to_cluster.items() if cid in target]


def compute_centroid(
    member_ids: Sequence[str], id_to_row: dict[str, int], embeddings: np.ndarray
) -> np.ndarray:
    rows = [id_to_row[pid] for pid in member_ids if pid in id_to_row]
    if not rows:
        raise RuntimeError("no member posts found in embedding index")
    submatrix = embeddings[rows]
    centroid = submatrix.mean(axis=0)
    norm = np.linalg.norm(centroid)
    if norm > 0:
        centroid = centroid / norm
    return centroid.astype(np.float32)


def top_k_nearest_to_centroid(
    centroid: np.ndarray,
    member_ids: Sequence[str],
    id_to_row: dict[str, int],
    embeddings: np.ndarray,
    k: int,
) -> list[tuple[str, float]]:
    present = [pid for pid in member_ids if pid in id_to_row]
    if not present:
        return []
    rows = np.array([id_to_row[pid] for pid in present], dtype=np.int64)
    vecs = embeddings[rows]
    # Assumes embeddings are already unit-normalized (they are, per pipeline).
    norms = np.linalg.norm(vecs, axis=1)
    safe_norms = np.where(norms > 0, norms, 1.0)
    vecs_n = vecs / safe_norms[:, None]
    sims = vecs_n @ centroid
    order = np.argsort(-sims)[:k]
    return [(present[i], float(sims[i])) for i in order]


# ------------------------- High-engagement -------------------------

def pick_high_engagement(
    corpus: dict[str, dict],
    member_ids: Sequence[str],
    exclude_ids: set[str],
    k: int,
    min_comments: int = 3,
) -> list[HighEngagementPost]:
    candidates: list[HighEngagementPost] = []
    for pid in member_ids:
        if pid in exclude_ids:
            continue
        row = corpus.get(pid)
        if not row:
            continue
        ccount = int(row.get("comments_count", 0))
        if ccount < min_comments:
            continue
        comments_raw = row.get("comments") or []
        comments = [str(c).strip() for c in comments_raw if str(c).strip()]
        candidates.append(
            HighEngagementPost(
                post_id=pid,
                text=row.get("normalized_text") or row.get("text") or "",
                comments_count=ccount,
                all_comments=comments,
                text_length=int(row.get("text_length") or len(row.get("text", ""))),
            )
        )
    candidates.sort(key=lambda x: x.text_length, reverse=True)
    return candidates[:k]


def pick_centroid_posts_with_comments(
    corpus: dict[str, dict],
    top_pairs: Sequence[tuple[str, float]],
    longest_n: int = 3,
) -> list[CentroidPost]:
    out: list[CentroidPost] = []
    for pid, cos in top_pairs:
        row = corpus.get(pid)
        if not row:
            continue
        comments_raw = row.get("comments") or []
        comments = [str(c).strip() for c in comments_raw if str(c).strip()]
        comments.sort(key=len, reverse=True)
        out.append(
            CentroidPost(
                post_id=pid,
                text=row.get("normalized_text") or row.get("text") or "",
                comments_count=int(row.get("comments_count", 0)),
                longest_comments=comments[:longest_n],
                cosine_to_centroid=cos,
            )
        )
    return out


# ------------------------- KB retrieval candidates -------------------------

_SLUG_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def slug_from_label(label: str, max_len: int = 60) -> str:
    # Strip diacritics naively for a filesystem-safe slug.
    replacements = str.maketrans(
        "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ"
    )
    lowered = label.translate(replacements).lower()
    slug = _SLUG_NON_ALNUM.sub("_", lowered).strip("_")
    return slug[:max_len]


def retrieve_kb_candidates(
    query: str, kb_path: Path, limit: int = 10
) -> list[LegalAnchorCandidate]:
    """Thin adapter over ``core.retriever.retrieve_chunks``.

    Kept local to the module so tests can monkeypatch it cleanly.
    """

    from core.retriever import retrieve_chunks  # lazy import — heavy deps

    chunks = retrieve_chunks(query, kb_path, limit=limit)
    return [
        LegalAnchorCandidate(
            law_name=c.law_name,
            article_number=c.article_number,
            category=c.category,
            content_preview=(c.content or "")[:300].replace("\n", " "),
            score=float(c.score),
        )
        for c in chunks
    ]


# ------------------------- Orchestration -------------------------

def assemble_material(
    spec: ClusterSpec,
    clusters: dict[int, dict],
    post_to_cluster: dict[str, int],
    corpus: dict[str, dict],
    id_to_row: dict[str, int],
    embeddings: np.ndarray,
    kb_path: Path,
    centroid_k: int = 10,
    high_engagement_k: int = 5,
    legal_candidates_k: int = 10,
) -> ClusterMaterial:
    members = members_for_spec(spec, post_to_cluster)
    if not members:
        raise RuntimeError(f"no member posts for cluster spec {spec.target_key}")

    centroid = compute_centroid(members, id_to_row, embeddings)
    top_pairs = top_k_nearest_to_centroid(
        centroid, members, id_to_row, embeddings, centroid_k
    )
    centroid_posts = pick_centroid_posts_with_comments(corpus, top_pairs)
    centroid_ids = {p.post_id for p in centroid_posts}
    high_engagement_posts = pick_high_engagement(
        corpus, members, exclude_ids=centroid_ids, k=high_engagement_k
    )

    # Aggregate keywords/bigrams across source clusters.
    keywords: list[str] = []
    bigrams: list[str] = []
    for cid in spec.source_cluster_ids:
        row = clusters.get(cid)
        if not row:
            continue
        for kw in row.get("top_keywords") or []:
            if kw not in keywords:
                keywords.append(kw)
        for bg in row.get("top_bigrams") or []:
            if bg not in bigrams:
                bigrams.append(bg)
    keywords = keywords[:10]
    bigrams = bigrams[:5]

    kb_query = f"{spec.label} {' '.join(keywords[:3])}"
    legal_candidates = retrieve_kb_candidates(
        kb_query, kb_path, limit=legal_candidates_k
    )

    total_comments = sum(
        int(corpus.get(pid, {}).get("comments_count", 0)) for pid in members
    )
    avg_comments = total_comments / max(len(members), 1)

    return ClusterMaterial(
        spec=spec,
        size=len(members),
        avg_comments=avg_comments,
        top_keywords=keywords,
        top_bigrams=bigrams,
        centroid_posts=centroid_posts,
        high_engagement_posts=high_engagement_posts,
        legal_candidates=legal_candidates,
    )


def truncate(text: str, limit: int) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "…"
