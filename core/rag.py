from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from config.settings import MAX_CONTEXT_TOKENS
from core.anonymizer import anonymize_text
from core.auditor import audit_answer
from core.categorizer import categorize_query
from core.generator import (
    GenerationMetrics,
    generate_answer,
    get_last_generation_metrics,
    is_low_confidence_retrieval,
    reset_last_generation_metrics,
    summarize_context,
)
from core.retriever import LawChunk, retrieve


@dataclass(slots=True)
class RagResult:
    answer: str
    chunks: list[LawChunk]
    audit: dict[str, object]
    redacted_query: str
    category: str
    needs_clarification: bool = False
    missing_slots: list[str] | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    no_match_reason: str | None = None


def _estimate_text_tokens(text: str) -> int:
    """Estimate token count using a lightweight word-like token heuristic."""

    return len(re.findall(r"[A-Za-zÀ-ÿ0-9_]+", text))


def _count_context_tokens(chunks: Iterable[LawChunk]) -> int:
    """Estimate the total token footprint of retrieved legal chunks."""

    return sum(
        _estimate_text_tokens(" ".join([chunk.law_name, chunk.article_number, chunk.content]))
        for chunk in chunks
    )


def _truncate_to_token_limit(text: str, max_tokens: int) -> str:
    """Truncate text to a soft token limit while preserving word boundaries."""

    words = re.findall(r"\S+", text)
    if len(words) <= max_tokens:
        return text.strip()
    return " ".join(words[:max_tokens]).strip()


def _merge_metrics(*metrics: GenerationMetrics) -> GenerationMetrics:
    """Sum multiple generator metric snapshots into one aggregate result."""

    total = GenerationMetrics()
    for metric in metrics:
        total.input_tokens += metric.input_tokens
        total.output_tokens += metric.output_tokens
        total.estimated_cost_usd = round(total.estimated_cost_usd + metric.estimated_cost_usd, 6)
    return total


def _compress_chunks_if_needed(
    query: str,
    chunks: list[LawChunk],
    system_prompt: str,
    api_key: str,
) -> tuple[list[LawChunk], GenerationMetrics]:
    """Summarize chunk contents when the retrieved context is too long."""

    context_tokens = _count_context_tokens(chunks)
    if context_tokens <= MAX_CONTEXT_TOKENS or not chunks:
        return chunks, GenerationMetrics()

    target_tokens_per_chunk = max(20, min(150, MAX_CONTEXT_TOKENS // len(chunks)))
    compressed_chunks: list[LawChunk] = []
    summary_metrics = GenerationMetrics()

    for chunk in chunks:
        summary = summarize_context(
            query=query,
            chunks=[chunk],
            system_prompt=system_prompt,
            api_key=api_key,
            max_words=target_tokens_per_chunk,
        )
        summary_metrics = _merge_metrics(summary_metrics, get_last_generation_metrics())
        summarized_content = _truncate_to_token_limit(summary or chunk.content, target_tokens_per_chunk)
        compressed_chunks.append(
            LawChunk(
                content=summarized_content,
                law_name=chunk.law_name,
                article_number=chunk.article_number,
                category=chunk.category,
                verified_date=chunk.verified_date,
                question_intent=chunk.question_intent,
                score=chunk.score,
            )
        )

    total_tokens = _count_context_tokens(compressed_chunks)
    if total_tokens <= MAX_CONTEXT_TOKENS:
        return compressed_chunks, summary_metrics

    # Final defensive pass: trim each chunk further to ensure the full context fits.
    hard_limit_per_chunk = max(10, MAX_CONTEXT_TOKENS // len(compressed_chunks))
    trimmed_chunks = [
        LawChunk(
            content=_truncate_to_token_limit(chunk.content, hard_limit_per_chunk),
            law_name=chunk.law_name,
            article_number=chunk.article_number,
            category=chunk.category,
            verified_date=chunk.verified_date,
            question_intent=chunk.question_intent,
            score=chunk.score,
        )
        for chunk in compressed_chunks
    ]
    return trimmed_chunks, summary_metrics


def answer_query(query: str, knowledge_path: str | Path, system_prompt: str, api_key: str) -> RagResult:
    if not isinstance(query, str):
        raise ValueError("query must be a string")
    if not query.strip():
        raise ValueError("query must not be empty")

    redacted_query = anonymize_text(query)
    retrieval_result = retrieve(query=redacted_query, knowledge_path=knowledge_path, limit=5)
    category = categorize_query(redacted_query)
    if retrieval_result.needs_clarification:
        missing_slots = retrieval_result.missing_slots or []
        audit = {
            "grounded": False,
            "context_count": 0,
            "sources": [],
            "missing_slots": missing_slots,
        }
        missing_text = ", ".join(missing_slots)
        answer = (
            "Potrzebuję doprecyzowania, zanim odpowiem. "
            f"Brakuje mi informacji: {missing_text}."
        )
        return RagResult(
            answer=answer,
            chunks=[],
            audit=audit,
            redacted_query=redacted_query,
            category=category,
            needs_clarification=True,
            missing_slots=missing_slots,
            no_match_reason="clarification_required",
        )

    chunks = retrieval_result.chunks
    low_confidence = is_low_confidence_retrieval(chunks)
    compression_metrics = GenerationMetrics()
    if not low_confidence:
        chunks, compression_metrics = _compress_chunks_if_needed(
            query=redacted_query,
            chunks=chunks,
            system_prompt=system_prompt,
            api_key=api_key,
        )
    reset_last_generation_metrics()
    answer = generate_answer(query=redacted_query, chunks=chunks, system_prompt=system_prompt, api_key=api_key)
    generation_metrics = _merge_metrics(compression_metrics, get_last_generation_metrics())

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
        needs_clarification=False,
        missing_slots=[],
        input_tokens=generation_metrics.input_tokens,
        output_tokens=generation_metrics.output_tokens,
        estimated_cost_usd=generation_metrics.estimated_cost_usd,
        no_match_reason="low_bm25_score" if low_confidence else None,
    )
