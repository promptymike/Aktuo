from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from core.retriever import LawChunk


def audit_answer(answer: str, chunks: Sequence[LawChunk]) -> dict[str, object]:
    today = date.today().isoformat()
    return {
        "grounded": bool(chunks) and bool(answer.strip()),
        "context_count": len(chunks),
        "contains_expired_sources": any(
            bool(chunk.effective_to) and chunk.effective_to < today
            for chunk in chunks
        ),
        "sources": [f"{chunk.law_name} {chunk.article_number}" for chunk in chunks],
    }
