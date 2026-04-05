from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Thread
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = PROJECT_ROOT / "data" / "logs" / "queries.jsonl"


def _write_log_entry(entry: dict[str, Any]) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        return


def log_query(
    *,
    session_id: str,
    question: str,
    redacted_query: str,
    category: str,
    chunks_returned: int,
    chunk_ids: list[str],
    answer_length: int,
    grounded: bool,
) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "question": question,
        "redacted_query": redacted_query,
        "category": category,
        "chunks_returned": chunks_returned,
        "chunk_ids": chunk_ids,
        "answer_length": answer_length,
        "grounded": grounded,
    }
    Thread(target=_write_log_entry, args=(entry,), daemon=True).start()
