from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from threading import Thread
from typing import Any

from core.anonymizer import anonymize_text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = PROJECT_ROOT / "data" / "logs" / "queries.jsonl"
FEEDBACK_PATH = PROJECT_ROOT / "data" / "logs" / "feedback.jsonl"
LOGGER = logging.getLogger(__name__)


def _hash_email(value: str) -> str:
    normalized = value.strip().lower()
    if not normalized:
        return ""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:8]


def _sanitize_text(value: str) -> str:
    if not value:
        return ""
    return anonymize_text(value)


def _write_log_entry(entry: dict[str, Any]) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as exc:
        LOGGER.warning("Failed to write query log: %s", exc)
        return


def _write_feedback_entry(entry: dict[str, Any]) -> None:
    try:
        FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
        with FEEDBACK_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as exc:
        LOGGER.warning("Failed to write feedback log: %s", exc)
        return


def log_query(
    *,
    session_id: str,
    user_email: str,
    question: str,
    redacted_query: str,
    category: str,
    chunks_returned: int,
    chunk_ids: list[str],
    answer_length: int,
    grounded: bool,
    input_tokens: int = 0,
    output_tokens: int = 0,
    estimated_cost_usd: float = 0.0,
    no_match_reason: str | None = None,
) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "user_email": _hash_email(user_email),
        "question": _sanitize_text(question),
        "redacted_query": _sanitize_text(redacted_query),
        "category": category,
        "chunks_returned": chunks_returned,
        "chunk_ids": chunk_ids,
        "answer_length": answer_length,
        "grounded": grounded,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": estimated_cost_usd,
    }
    if no_match_reason:
        entry["no_match_reason"] = no_match_reason
    Thread(target=_write_log_entry, args=(entry,), daemon=True).start()


def log_feedback(
    *,
    session_id: str,
    user_email: str,
    query: str,
    rating: str,
    comment: str = "",
) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "user_email": _hash_email(user_email),
        "query": _sanitize_text(query),
        "rating": rating,
        "comment": _sanitize_text(comment),
    }
    Thread(target=_write_feedback_entry, args=(entry,), daemon=True).start()
