from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from config.settings import (
    CLARIFICATION_SLOTS_PATH,
    MAX_CONTEXT_TOKENS,
    WORKFLOW_PARTIAL_ANSWER_ENABLED,
    WORKFLOW_PARTIAL_CONFIDENCE_THRESHOLD,
    WORKFLOW_PARTIAL_FATAL_SLOTS,
    WORKFLOW_PARTIAL_MIN_STEPS,
    WORKFLOW_SEED_PATH,
)
from core.anonymizer import anonymize_text
from core.auditor import audit_answer
from core.categorizer import categorize_query
from core.generator import (
    GenerationMetrics,
    format_partial_workflow_answer,
    format_workflow_answer,
    generate_answer,
    get_last_generation_metrics,
    is_low_confidence_retrieval,
    reset_last_generation_metrics,
    summarize_context,
)
from core.retriever import LawChunk, analyze_query_requirements, retrieve, retrieve_chunks
from core.workflow_retriever import is_workflow_eligible, retrieve_workflow


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
    retrieval_path: str = "legal"
    partial_answer: bool = False


_CLARIFICATION_METADATA_CACHE: dict[str, dict[str, object]] = {}


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


def _copy_chunk_with_content(chunk: LawChunk, content: str) -> LawChunk:
    """Return a shallow LawChunk copy with updated content."""

    return LawChunk(
        content=content,
        law_name=chunk.law_name,
        article_number=chunk.article_number,
        category=chunk.category,
        verified_date=chunk.verified_date,
        question_intent=chunk.question_intent,
        score=chunk.score,
        source_type=chunk.source_type,
        workflow_area=chunk.workflow_area,
        title=chunk.title,
        workflow_steps=chunk.workflow_steps,
        workflow_required_inputs=chunk.workflow_required_inputs,
        workflow_common_pitfalls=chunk.workflow_common_pitfalls,
        workflow_related_forms=chunk.workflow_related_forms,
        workflow_related_systems=chunk.workflow_related_systems,
    )


def _is_workflow_generation_context(retrieval_path: str, chunks: list[LawChunk]) -> bool:
    """Return True when the workflow retrieval result should use workflow formatting."""

    if retrieval_path != "workflow" or not chunks:
        return False
    return any(chunk.source_type.startswith("workflow") for chunk in chunks)


def _load_clarification_metadata(path: str | Path = CLARIFICATION_SLOTS_PATH) -> dict[str, object]:
    """Load clarification metadata used to render human-friendly missing fields."""

    cache_key = str(path)
    cached = _CLARIFICATION_METADATA_CACHE.get(cache_key)
    if cached is not None:
        return cached

    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        payload = {}

    _CLARIFICATION_METADATA_CACHE[cache_key] = payload
    return payload


def _slot_display_label(slot_name: str, metadata: dict[str, object]) -> str:
    """Return a user-facing label for a clarification slot."""

    labels = metadata.get("slot_display_labels", {})
    if isinstance(labels, dict):
        label = labels.get(slot_name)
        if isinstance(label, str) and label.strip():
            return label.strip()
    return slot_name.replace("_", " ")


def _workflow_unit_supports_partial(chunks: list[LawChunk]) -> bool:
    """Return True when workflow chunks contain enough structure for a partial answer."""

    if not chunks:
        return False

    primary_chunk = chunks[0]
    if len(primary_chunk.workflow_steps) < WORKFLOW_PARTIAL_MIN_STEPS:
        return False

    return bool(
        primary_chunk.workflow_required_inputs
        or primary_chunk.workflow_common_pitfalls
        or primary_chunk.workflow_related_forms
        or primary_chunk.workflow_related_systems
    )


def _missing_slots_are_nonfatal(missing_slots: list[str]) -> bool:
    """Return True when missing slots still allow a safe partial workflow answer."""

    fatal_slots = {slot.strip() for slot in WORKFLOW_PARTIAL_FATAL_SLOTS if slot.strip()}
    return bool(missing_slots) and not any(slot in fatal_slots for slot in missing_slots)


def _build_workflow_partial_result(
    query: str,
    category: str,
    chunks: list[LawChunk],
    missing_slots: list[str],
) -> RagResult:
    """Create a deterministic partial workflow answer instead of hard clarification."""

    metadata = _load_clarification_metadata()
    missing_labels = [_slot_display_label(slot, metadata) for slot in missing_slots]
    answer = format_partial_workflow_answer(
        query=query,
        chunks=chunks,
        missing_details=missing_labels,
    )
    audit = {
        "grounded": True,
        "context_count": len(chunks),
        "sources": [f"{chunk.law_name} {chunk.article_number}" for chunk in chunks],
        "missing_slots": missing_slots,
        "partial_answer": True,
    }
    return RagResult(
        answer=answer,
        chunks=chunks,
        audit=audit,
        redacted_query=query,
        category=category,
        needs_clarification=False,
        missing_slots=missing_slots,
        retrieval_path="workflow",
        partial_answer=True,
    )


def _try_workflow_partial_answer(
    *,
    query: str,
    category: str,
    missing_slots: list[str],
    intent: str,
) -> RagResult | None:
    """Attempt a safe partial workflow answer before returning clarification-only."""

    if not WORKFLOW_PARTIAL_ANSWER_ENABLED:
        return None
    if not missing_slots:
        return None
    if category in {"ogólne", "unknown"}:
        return None
    if len(missing_slots) > 3:
        return None
    if not _missing_slots_are_nonfatal(missing_slots):
        return None
    if not is_workflow_eligible(query, intent):
        return None

    workflow_result = retrieve_workflow(
        query=query,
        workflow_path=WORKFLOW_SEED_PATH,
        limit=5,
        confidence_threshold=WORKFLOW_PARTIAL_CONFIDENCE_THRESHOLD,
    )
    if not workflow_result.confident:
        return None
    if not _is_workflow_generation_context("workflow", workflow_result.chunks):
        return None
    if not _workflow_unit_supports_partial(workflow_result.chunks):
        return None

    return _build_workflow_partial_result(
        query=query,
        category=category,
        chunks=workflow_result.chunks,
        missing_slots=missing_slots,
    )


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
            _copy_chunk_with_content(chunk, summarized_content)
        )

    total_tokens = _count_context_tokens(compressed_chunks)
    if total_tokens <= MAX_CONTEXT_TOKENS:
        return compressed_chunks, summary_metrics

    # Final defensive pass: trim each chunk further to ensure the full context fits.
    hard_limit_per_chunk = max(10, MAX_CONTEXT_TOKENS // len(compressed_chunks))
    trimmed_chunks = [
        _copy_chunk_with_content(chunk, _truncate_to_token_limit(chunk.content, hard_limit_per_chunk))
        for chunk in compressed_chunks
    ]
    return trimmed_chunks, summary_metrics


def _retrieve_context(
    query: str,
    knowledge_path: str | Path,
    category: str,
    intent: str,
    limit: int = 5,
) -> tuple[list[LawChunk], str]:
    """Choose workflow or legal retrieval path with legal fallback."""

    if is_workflow_eligible(query, intent):
        workflow_result = retrieve_workflow(query=query, workflow_path=WORKFLOW_SEED_PATH, limit=limit)
        if workflow_result.confident:
            return workflow_result.chunks, "workflow"
        legal_path = "legal_fallback" if workflow_result.chunks else "legal"
        return retrieve_chunks(query, knowledge_path, limit), legal_path

    return retrieve_chunks(query, knowledge_path, limit), "legal"


def answer_query(query: str, knowledge_path: str | Path, system_prompt: str, api_key: str) -> RagResult:
    if not isinstance(query, str):
        raise ValueError("query must be a string")
    if not query.strip():
        raise ValueError("query must not be empty")

    redacted_query = anonymize_text(query)
    category = categorize_query(redacted_query)
    query_analysis = analyze_query_requirements(redacted_query)
    if query_analysis.needs_clarification:
        missing_slots = query_analysis.missing_slots or []
        partial_result = _try_workflow_partial_answer(
            query=redacted_query,
            category=category,
            missing_slots=missing_slots,
            intent=query_analysis.intent,
        )
        if partial_result is not None:
            return partial_result
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
            retrieval_path="clarification",
            partial_answer=False,
        )

    chunks, retrieval_path = _retrieve_context(
        query=redacted_query,
        knowledge_path=knowledge_path,
        category=category,
        intent=query_analysis.intent,
        limit=5,
    )
    workflow_mode = _is_workflow_generation_context(retrieval_path, chunks)
    low_confidence = is_low_confidence_retrieval(chunks)
    compression_metrics = GenerationMetrics()
    if not low_confidence and not workflow_mode:
        chunks, compression_metrics = _compress_chunks_if_needed(
            query=redacted_query,
            chunks=chunks,
            system_prompt=system_prompt,
            api_key=api_key,
        )
    reset_last_generation_metrics()
    if workflow_mode:
        answer = format_workflow_answer(query=redacted_query, chunks=chunks)
        generation_metrics = GenerationMetrics()
    else:
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
        retrieval_path=retrieval_path,
        partial_answer=False,
    )
