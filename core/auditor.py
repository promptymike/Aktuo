from __future__ import annotations

from collections.abc import Sequence

from core.retriever import LawChunk


def audit_answer(answer: str, chunks: Sequence[LawChunk]) -> dict[str, object]:
    return {
        "grounded": bool(chunks) and bool(answer.strip()),
        "context_count": len(chunks),
        "sources": [f"{chunk.law_name} {chunk.article_number}" for chunk in chunks],
    }
