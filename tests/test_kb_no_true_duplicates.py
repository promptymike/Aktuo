from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

KB_FILES = [
    Path("data/seeds/law_knowledge.json"),
    Path("data/seeds/law_knowledge_additions.json"),
    Path("data/seeds/law_knowledge_curated_additions.json"),
]

ARTICLE_PREFIX_RE = re.compile(
    r"^\s*art\.?\s*[0-9A-Za-z]+(?:\s*\.?\s*§\s*[0-9A-Za-z]+)?\.?\s*",
    re.IGNORECASE,
)
SPACE_RE = re.compile(r"\s+")


def _load_records(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload["records"] if isinstance(payload, dict) else payload


def _normalized_content_hash(content: str) -> str:
    normalized = ARTICLE_PREFIX_RE.sub("", content.lower(), count=1)
    normalized = SPACE_RE.sub(" ", normalized).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def test_no_kodeks_pracy_triple_ingest_duplicates_by_normalized_content_hash() -> None:
    groups: dict[tuple[str, str, str], list[tuple[str, int]]] = defaultdict(list)

    for path in KB_FILES:
        for index, record in enumerate(_load_records(path)):
            content = record.get("content", "")
            if not isinstance(content, str):
                continue
            key = (
                record.get("law_name", ""),
                record.get("article_number", ""),
                _normalized_content_hash(content),
            )
            groups[key].append((path.name, index))

    issues: list[str] = []
    for (law_name, article_number, _), locations in sorted(groups.items()):
        source_files = {file_name for file_name, _ in locations}
        if (
            law_name == "Kodeks pracy"
            and len(locations) >= 3
            and {"law_knowledge.json", "law_knowledge_curated_additions.json"}.issubset(source_files)
        ):
            issues.append(f"{law_name} | {article_number}: {locations}")

    assert not issues, "Found Kodeks pracy triple-ingest duplicates:\n" + "\n".join(issues)
