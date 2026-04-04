from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class IngestedChunk:
    content: str
    law_name: str
    article_number: str
    category: str
    verified_date: str


def load_seed_laws(seed_path: str | Path) -> list[dict[str, str]]:
    path = Path(seed_path)
    return json.loads(path.read_text(encoding="utf-8"))


def split_text_into_chunks(text: str, max_chunk_length: int = 220) -> list[str]:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        candidate = sentence if not current else f"{current} {sentence}"
        if len(candidate) <= max_chunk_length:
            current = candidate
            continue
        if current:
            chunks.append(current)
        current = sentence

    if current:
        chunks.append(current)

    return chunks or [text.strip()]


def ingest_seed_chunks(seed_path: str | Path) -> list[IngestedChunk]:
    chunks: list[IngestedChunk] = []
    for item in load_seed_laws(seed_path):
        split_chunks = split_text_into_chunks(item["content"])
        for chunk_content in split_chunks:
            chunks.append(
                IngestedChunk(
                    content=chunk_content,
                    law_name=item["law_name"],
                    article_number=item["article_number"],
                    category=item["category"],
                    verified_date=item["verified_date"],
                )
            )
    return chunks
