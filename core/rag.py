from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.anonymizer import anonymize_text
from core.auditor import audit_answer
from core.categorizer import categorize_query
from core.generator import generate_answer, is_low_confidence_retrieval
from core.retriever import LawChunk, retrieve_chunks


@dataclass(slots=True)
class RagResult:
    answer: str
    chunks: list[LawChunk]
    audit: dict[str, object]
    redacted_query: str
    category: str
    no_match_reason: str | None = None


def answer_query(query: str, knowledge_path: str | Path, system_prompt: str, api_key: str) -> RagResult:
    redacted_query = anonymize_text(query)
    category = categorize_query(redacted_query)
    chunks = retrieve_chunks(query=redacted_query, knowledge_path=knowledge_path, limit=5)
    low_confidence = is_low_confidence_retrieval(chunks)
    answer = generate_answer(query=redacted_query, chunks=chunks, system_prompt=system_prompt, api_key=api_key)

    if low_confidence:
        audit = {
            "grounded": False,
            "context_count": len(chunks),
            "sources": [f"{chunk.law_name} {chunk.article_number}" for chunk in chunks],
        }
    else:
        audit = audit_answer(answer=answer, chunks=chunks)

    return RagResult(
        answer=answer,
        chunks=chunks,
        audit=audit,
        redacted_query=redacted_query,
        category=category,
        no_match_reason="low_bm25_score" if low_confidence else None,
    )
