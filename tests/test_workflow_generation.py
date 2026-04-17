"""Regression tests for the workflow-draft pipeline (Zadanie 3).

No live LLM / retriever calls — everything runs against synthetic data or
tiny in-memory fixtures. The Opus call path is exercised with a fake
client that hands back pre-cooked responses.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from fb_pipeline.workflow import generate_draft as gd
from fb_pipeline.workflow import prepare_material as pm
from fb_pipeline.workflow import schema


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

def _valid_draft() -> dict:
    return {
        "id": "wf_test_foo",
        "title": "Test workflow",
        "topic_area": "kadry",
        "question_examples": [
            "Pyt 1?", "Pyt 2?", "Pyt 3?", "Pyt 4?", "Pyt 5?",
        ],
        "answer_steps": [
            {"step": 1, "action": "Sprawdź X", "detail": "Szczegół 1", "condition": None},
            {"step": 2, "action": "Ustal Y", "detail": "Szczegół 2", "condition": "if A"},
            {"step": 3, "action": "Wystaw Z", "detail": "Szczegół 3", "condition": None},
        ],
        "legal_anchors": [
            {"law_name": "Kodeks pracy", "article_number": "art. 151", "reason": "Reguluje temat."},
        ],
        "edge_cases": ["Wariant 1", "Wariant 2"],
        "common_mistakes": ["Błąd 1", "Błąd 2"],
        "related_questions": ["Pyt pok 1?", "Pyt pok 2?"],
        "last_verified_at": "2026-04-17",
        "draft": True,
        "requires_manual_legal_anchor": False,
        "generation_metadata": {
            "model": "claude-opus-4-7",
            "cluster_id": "7",
            "cluster_label": "Test cluster label",
            "generated_at": "2026-04-17T10:00:00Z",
            "source_post_ids": ["a", "b"],
        },
    }


# -----------------------------------------------------------------------------
# 1. Schema — valid draft passes
# -----------------------------------------------------------------------------

def test_schema_validation_valid_draft_passes() -> None:
    ok, err = schema.validate_draft(_valid_draft())
    assert ok, f"expected valid but got error: {err}"
    assert err is None


# -----------------------------------------------------------------------------
# 2. Schema — missing field fails
# -----------------------------------------------------------------------------

def test_schema_missing_field_fails() -> None:
    draft = _valid_draft()
    del draft["question_examples"]
    ok, err = schema.validate_draft(draft)
    assert not ok
    assert err is not None
    assert "question_examples" in err


def test_schema_bad_steps_fails() -> None:
    draft = _valid_draft()
    # Too few steps.
    draft["answer_steps"] = [{"step": 1, "action": "x", "detail": "y", "condition": None}]
    ok, err = schema.validate_draft(draft)
    assert not ok
    assert "answer_steps" in (err or "")


def test_schema_manual_anchor_allows_empty_list() -> None:
    draft = _valid_draft()
    draft["legal_anchors"] = []
    draft["requires_manual_legal_anchor"] = True
    ok, err = schema.validate_draft(draft)
    assert ok, err


def test_schema_empty_anchors_without_manual_flag_fails() -> None:
    draft = _valid_draft()
    draft["legal_anchors"] = []
    draft["requires_manual_legal_anchor"] = False
    ok, err = schema.validate_draft(draft)
    assert not ok


# -----------------------------------------------------------------------------
# 3. Retrieval candidates format (no real retriever — monkeypatch)
# -----------------------------------------------------------------------------

def test_retrieval_candidates_format(monkeypatch) -> None:
    """Exercises the adapter's contract without invoking BM25/KB I/O."""

    class _Chunk:
        def __init__(self, **kw: object) -> None:
            self.law_name = kw.get("law_name", "Ustawa o VAT")
            self.article_number = kw.get("article_number", "art. 19a")
            self.category = kw.get("category", "vat")
            self.content = kw.get("content", "Treść artykułu\n z nową linią.")
            self.score = kw.get("score", 0.42)

    def fake_retrieve(query, kb_path, limit=5):  # noqa: ARG001
        return [
            _Chunk(article_number="art. 106na", score=0.5),
            _Chunk(article_number="art. 19a", score=0.3),
        ]

    monkeypatch.setattr(
        "core.retriever.retrieve_chunks", fake_retrieve, raising=True
    )

    cands = pm.retrieve_kb_candidates("dummy", Path("dummy.json"), limit=5)
    assert len(cands) == 2
    assert all(isinstance(c, pm.LegalAnchorCandidate) for c in cands)
    assert cands[0].article_number == "art. 106na"
    # Newlines stripped to keep prompt blocks clean.
    assert "\n" not in cands[0].content_preview
    assert cands[0].score == 0.5


# -----------------------------------------------------------------------------
# 4. Cluster material assembly — synthetic 8-post cluster
# -----------------------------------------------------------------------------

def _build_synthetic_world(tmp_path: Path):
    """Return (spec, clusters, p2c, corpus, id_to_row, embeddings)."""

    rng = np.random.default_rng(42)
    dim = 8
    # 6 in-cluster posts, 4 noise.
    ids = [f"p{i:02d}" for i in range(10)]
    base = rng.normal(size=dim).astype(np.float32)
    base /= np.linalg.norm(base)
    in_cluster = np.stack(
        [base + 0.02 * rng.normal(size=dim).astype(np.float32) for _ in range(6)]
    )
    noise = rng.normal(size=(4, dim)).astype(np.float32)
    matrix = np.vstack([in_cluster, noise])
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    matrix = matrix / np.where(norms == 0, 1, norms)
    matrix = matrix.astype(np.float32)

    post_to_cluster = {pid: 99 if i < 6 else 0 for i, pid in enumerate(ids)}
    clusters = {
        99: {
            "cluster_id": 99,
            "label": "Test kadrowy",
            "topic_area": "kadry",
            "top_keywords": ["urlop", "pracownik", "umowa"],
            "top_bigrams": ["urlop wypoczynkowy"],
        }
    }
    # Build corpus with varying comments_count so high-engagement picker has work.
    corpus = {}
    for i, pid in enumerate(ids):
        comments_count = 0
        comments: list[str] = []
        if i in (0, 1, 2):
            comments_count = 4
            comments = [f"komentarz {j} do {pid}" * (j + 1) for j in range(4)]
        corpus[pid] = {
            "id": pid,
            "text": f"Pytanie z postu {pid} o urlop i umowę " * (i + 1),
            "normalized_text": f"pytanie z postu {pid} o urlop i umowę " * (i + 1),
            "comments": comments,
            "comments_count": comments_count,
            "text_length": 40 * (i + 1),
        }

    id_to_row = {pid: i for i, pid in enumerate(ids)}

    spec = pm.ClusterSpec(
        target_key="99",
        source_cluster_ids=[99],
        label="Test kadrowy",
        topic_area="kadry",
    )
    return spec, clusters, post_to_cluster, corpus, id_to_row, matrix


def test_cluster_material_assembly(tmp_path: Path, monkeypatch) -> None:
    """Assembly picks only cluster members and builds centroid/HE lists."""

    # Stub retriever to avoid loading KB.
    monkeypatch.setattr(
        pm, "retrieve_kb_candidates", lambda q, p, limit=10: []
    )

    spec, clusters, p2c, corpus, id_to_row, embeddings = _build_synthetic_world(tmp_path)
    material = pm.assemble_material(
        spec=spec,
        clusters=clusters,
        post_to_cluster=p2c,
        corpus=corpus,
        id_to_row=id_to_row,
        embeddings=embeddings,
        kb_path=tmp_path / "dummy_kb.json",
        centroid_k=5,
        high_engagement_k=3,
        legal_candidates_k=0,
    )

    assert material.size == 6  # only cluster 99 members
    # All centroid post ids belong to the cluster (p00..p05).
    for p in material.centroid_posts:
        assert p.post_id in {f"p{i:02d}" for i in range(6)}
    assert len(material.centroid_posts) <= 5
    # High-engagement picks only posts with >=3 comments and excludes centroid ids.
    centroid_ids = {p.post_id for p in material.centroid_posts}
    for p in material.high_engagement_posts:
        assert p.post_id not in centroid_ids
        assert p.comments_count >= 3
    # Keywords/bigrams propagated.
    assert "urlop" in material.top_keywords
    assert "urlop wypoczynkowy" in material.top_bigrams


def test_cluster_material_merged_pools_ids(tmp_path: Path, monkeypatch) -> None:
    """Merge spec pools posts from every source cluster_id."""

    monkeypatch.setattr(
        pm, "retrieve_kb_candidates", lambda q, p, limit=10: []
    )
    spec, clusters, p2c, corpus, id_to_row, embeddings = _build_synthetic_world(tmp_path)
    # Move two posts to a second cluster 100.
    p2c["p00"] = 100
    p2c["p01"] = 100
    clusters[100] = {
        "cluster_id": 100,
        "label": "Inny label",
        "topic_area": "kadry",
        "top_keywords": ["zlecenie"],
        "top_bigrams": [],
    }
    merged = pm.ClusterSpec(
        target_key="merge_99_100",
        source_cluster_ids=[99, 100],
        label="Merged",
        topic_area="kadry",
    )
    material = pm.assemble_material(
        spec=merged,
        clusters=clusters,
        post_to_cluster=p2c,
        corpus=corpus,
        id_to_row=id_to_row,
        embeddings=embeddings,
        kb_path=tmp_path / "dummy.json",
        centroid_k=10,
        high_engagement_k=5,
        legal_candidates_k=0,
    )
    assert material.size == 6  # 4 in cluster 99 + 2 in cluster 100 == original 6
    assert "urlop" in material.top_keywords
    assert "zlecenie" in material.top_keywords


# -----------------------------------------------------------------------------
# 5. Prompt builder is deterministic and includes cluster material
# -----------------------------------------------------------------------------

def test_build_prompt_includes_material() -> None:
    spec = pm.ClusterSpec(
        target_key="42",
        source_cluster_ids=[42],
        label="Test label",
        topic_area="VAT",
    )
    material = pm.ClusterMaterial(
        spec=spec,
        size=100,
        avg_comments=1.5,
        top_keywords=["vat", "faktura"],
        top_bigrams=["faktura vat"],
        centroid_posts=[
            pm.CentroidPost(
                post_id="p1", text="Pytanie testowe", comments_count=2,
                longest_comments=["Komentarz X"], cosine_to_centroid=0.9,
            )
        ],
        high_engagement_posts=[
            pm.HighEngagementPost(
                post_id="p2", text="Długie pytanie", comments_count=5,
                all_comments=["A", "B"], text_length=100,
            )
        ],
        legal_candidates=[
            pm.LegalAnchorCandidate(
                law_name="Ustawa o VAT", article_number="art. 19a",
                category="vat", content_preview="preview", score=0.5,
            )
        ],
    )
    prompt = gd.build_prompt(material, today_iso="2026-04-17")
    assert "Test label" in prompt
    assert "VAT" in prompt
    assert "p1" in prompt and "p2" in prompt
    assert "art. 19a" in prompt
    assert "2026-04-17" in prompt


# -----------------------------------------------------------------------------
# 6. parse_json_response accepts fenced + raw JSON
# -----------------------------------------------------------------------------

def test_parse_json_response_accepts_fenced_and_raw() -> None:
    draft = _valid_draft()
    raw = json.dumps(draft, ensure_ascii=False)
    assert gd.parse_json_response(raw)["id"] == draft["id"]
    fenced = f"```json\n{raw}\n```"
    assert gd.parse_json_response(fenced)["id"] == draft["id"]
    with_prefix = f"Oto JSON:\n{raw}"
    assert gd.parse_json_response(with_prefix)["id"] == draft["id"]


def test_parse_json_response_rejects_non_json() -> None:
    import pytest

    with pytest.raises(ValueError):
        gd.parse_json_response("totally not json")
    with pytest.raises(ValueError):
        gd.parse_json_response("")


# -----------------------------------------------------------------------------
# 7. generate_draft_with_retry: retry path + final success
# -----------------------------------------------------------------------------

class _Block:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class _Usage:
    def __init__(self, inp: int, out: int) -> None:
        self.input_tokens = inp
        self.output_tokens = out


class _Resp:
    def __init__(self, text: str, inp: int = 100, out: int = 50) -> None:
        self.content = [_Block(text)]
        self.usage = _Usage(inp, out)


class _FakeMessages:
    def __init__(self, responses: list[_Resp]) -> None:
        self._responses = list(responses)
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self._responses.pop(0)


class _FakeClient:
    def __init__(self, responses: list[_Resp]) -> None:
        self.messages = _FakeMessages(responses)


def test_generate_draft_retry_recovers_from_bad_json() -> None:
    good_payload = json.dumps(_valid_draft(), ensure_ascii=False)
    client = _FakeClient([_Resp("not json", 10, 5), _Resp(good_payload, 50, 40)])
    draft, attempts = gd.generate_draft_with_retry(
        client, prompt="dummy", max_retries=1
    )
    assert draft is not None
    assert attempts[0]["status"] == "parse_fail"
    assert attempts[1]["status"] == "ok"
    # Second call gets retry-augmented prompt.
    second_prompt = client.messages.calls[1]["messages"][0]["content"]
    assert "Poprzednia próba" in second_prompt


def test_generate_draft_gives_up_after_retries() -> None:
    client = _FakeClient([_Resp("still bad", 1, 1), _Resp("also bad", 1, 1)])
    draft, attempts = gd.generate_draft_with_retry(
        client, prompt="dummy", max_retries=1
    )
    assert draft is None
    assert len(attempts) == 2
    assert all(a["status"] != "ok" for a in attempts)
