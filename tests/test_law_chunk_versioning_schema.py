from __future__ import annotations

from pathlib import Path

from core.retriever import LawChunk, load_chunks


def test_law_chunk_accepts_versioning_fields() -> None:
    chunk = LawChunk(
        content="Treść przepisu.",
        law_name="Ustawa o VAT",
        article_number="art. 86",
        category="vat",
        verified_date="2026-04-01",
        effective_from="2025-01-01",
        effective_to="2025-12-31",
        source_url="https://isap.sejm.gov.pl/example",
        source_hash="abc123",
        last_verified_at="2026-04-15",
        question_intent="Czy można odliczyć VAT?",
    )

    assert chunk.effective_from == "2025-01-01"
    assert chunk.effective_to == "2025-12-31"
    assert chunk.source_url == "https://isap.sejm.gov.pl/example"
    assert chunk.source_hash == "abc123"
    assert chunk.last_verified_at == "2026-04-15"
    assert chunk.verified_date == "2026-04-01"


def test_law_chunk_versioning_fields_default_to_empty_strings() -> None:
    chunk = LawChunk(
        content="Treść przepisu.",
        law_name="Kodeks pracy",
        article_number="art. 221",
        category="kadry",
        verified_date="2026-04-01",
    )

    assert chunk.effective_from == ""
    assert chunk.effective_to == ""
    assert chunk.source_url == ""
    assert chunk.source_hash == ""
    assert chunk.last_verified_at == ""
    assert chunk.verified_date == "2026-04-01"


def test_load_chunks_exposes_optional_versioning_fields_for_existing_kb() -> None:
    knowledge_path = Path(__file__).resolve().parents[1] / "data" / "seeds" / "law_knowledge.json"

    chunks = load_chunks(knowledge_path)

    assert chunks
    for chunk in chunks:
        assert hasattr(chunk, "effective_from")
        assert hasattr(chunk, "effective_to")
        assert hasattr(chunk, "source_url")
        assert hasattr(chunk, "source_hash")
        assert hasattr(chunk, "last_verified_at")
        assert hasattr(chunk, "verified_date")
        assert isinstance(chunk.effective_from, str)
        assert isinstance(chunk.effective_to, str)
        assert isinstance(chunk.source_url, str)
        assert isinstance(chunk.source_hash, str)
        assert isinstance(chunk.last_verified_at, str)
        assert isinstance(chunk.verified_date, str)
