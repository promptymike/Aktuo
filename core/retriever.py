from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from core.categorizer import categorize_query
from data.ingest import ingest_seed_chunks


@dataclass(slots=True)
class LawChunk:
    content: str
    law_name: str
    article_number: str
    category: str
    verified_date: str


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _category_matches(query_category: str, chunk: LawChunk) -> bool:
    if chunk.category == query_category:
        return True

    if query_category == "ksef":
        haystack = " ".join([chunk.category, chunk.law_name, chunk.content]).lower()
        return any(
            keyword in haystack
            for keyword in ("ksef", "krajowy system e-faktur", "e-faktur", "ustrukturyz")
        )

    return False


def load_chunks(knowledge_path: str | Path) -> list[LawChunk]:
    return [
        LawChunk(
            content=chunk.content,
            law_name=chunk.law_name,
            article_number=chunk.article_number,
            category=chunk.category,
            verified_date=chunk.verified_date,
        )
        for chunk in ingest_seed_chunks(knowledge_path)
    ]


def retrieve_chunks(query: str, knowledge_path: str | Path, limit: int = 3) -> list[LawChunk]:
    query_tokens = _tokenize(query)
    query_category = categorize_query(query)
    scored: list[tuple[int, LawChunk]] = []

    for chunk in load_chunks(knowledge_path):
        searchable_text = " ".join(
            [chunk.content, chunk.law_name, chunk.article_number, chunk.category]
        )
        chunk_tokens = _tokenize(searchable_text)
        score = len(query_tokens & chunk_tokens)
        if _category_matches(query_category, chunk):
            score += 2
        if score > 0:
            scored.append((score, chunk))

    scored.sort(
        key=lambda item: (
            item[0],
            item[1].verified_date,
            item[1].law_name,
            item[1].article_number,
        ),
        reverse=True,
    )
    return [chunk for _, chunk in scored[:limit]]
