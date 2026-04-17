from __future__ import annotations

import json
import re
from pathlib import Path

KB_FILES = [
    Path("data/seeds/law_knowledge.json"),
    Path("data/seeds/law_knowledge_additions.json"),
    Path("data/seeds/law_knowledge_curated_additions.json"),
]
TEXT_FIELDS = ["law_name", "category", "content", "question_intent"]
CORRUPTION_RE = re.compile(r"\w+\?\w+")
FALSE_POSITIVES = {"APPLE?Czy"}


def _load_records(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload["records"] if isinstance(payload, dict) else payload


def test_kb_text_fields_have_no_regex_detectable_utf8_corruption() -> None:
    issues: list[str] = []
    for path in KB_FILES:
        for index, record in enumerate(_load_records(path)):
            for field in TEXT_FIELDS:
                value = record.get(field)
                if not isinstance(value, str):
                    continue
                matches = sorted(set(CORRUPTION_RE.findall(value)))
                matches = [match for match in matches if match not in FALSE_POSITIVES]
                if matches:
                    issues.append(f"{path} record {index} field {field}: {matches}")

    assert not issues, "Found UTF-8 corruption patterns:\n" + "\n".join(issues)


def test_kb_files_are_valid_utf8_json() -> None:
    for path in KB_FILES:
        raw = path.read_text(encoding="utf-8")
        parsed = json.loads(raw)
        serialized = json.dumps(parsed, ensure_ascii=False)
        assert serialized.encode("utf-8").decode("utf-8") == serialized
