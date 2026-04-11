from __future__ import annotations

from core.retriever import LawChunk, _fuse_rankings


def test_fuse_rankings_promotes_chunks_present_in_both_lists() -> None:
    """RRF should promote chunks that rank in both BM25 and vector lists."""

    shared = LawChunk(
        content="Wspolny chunk z obu rankingow.",
        law_name="Ustawa o CIT",
        article_number="art. 28j",
        category="cit",
        verified_date="2026-04-01",
        question_intent="Kto moze wybrac estonski CIT?",
        score=4.0,
    )
    bm25_only = LawChunk(
        content="Chunk silny tylko w BM25.",
        law_name="Ustawa o VAT",
        article_number="art. 99",
        category="vat",
        verified_date="2026-04-01",
        question_intent="Termin zlozenia deklaracji VAT.",
        score=9.0,
    )
    vector_only = LawChunk(
        content="Chunk silny tylko w rankingu wektorowym.",
        law_name="Kodeks pracy",
        article_number="art. 36",
        category="kadry",
        verified_date="2026-04-01",
        question_intent="Jakie sa okresy wypowiedzenia umowy o prace?",
        score=8.0,
    )

    fused = _fuse_rankings(
        bm25_ranked=[bm25_only, shared],
        vector_ranked=[shared, vector_only],
        bm25_k=1,
        vector_k=1,
    )

    assert fused[0].law_name == "Ustawa o CIT"
    assert fused[0].article_number == "art. 28j"


def test_fuse_rankings_deduplicates_identical_chunks() -> None:
    """The fused ranking should contain one entry per unique chunk."""

    duplicate = LawChunk(
        content="Ten sam chunk pojawia sie w obu rankingach.",
        law_name="Ustawa o PIT",
        article_number="art. 26",
        category="pit",
        verified_date="2026-04-01",
        question_intent="Jakie odliczenia przysluguja podatnikowi PIT?",
        score=3.0,
    )

    fused = _fuse_rankings(
        bm25_ranked=[duplicate],
        vector_ranked=[duplicate],
        bm25_k=10,
        vector_k=10,
    )

    assert len(fused) == 1
    assert fused[0].law_name == "Ustawa o PIT"
    assert fused[0].article_number == "art. 26"
