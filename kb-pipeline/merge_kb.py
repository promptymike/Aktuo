from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "kb-pipeline" / "output"
SEED_PATH = PROJECT_ROOT / "data" / "seeds" / "law_knowledge.json"


def iter_kb_files() -> list[Path]:
    files = []
    for path in sorted(OUTPUT_DIR.glob("*_kb.json")):
        name = path.name.lower()
        if "test" in name or "first10" in name:
            continue
        files.append(path)
    return files


def normalize_record(record: dict) -> dict[str, str] | None:
    if {"law_name", "article_number", "category", "verified_date", "content"} <= record.keys():
        return {
            "law_name": str(record["law_name"]),
            "article_number": str(record["article_number"]),
            "category": str(record["category"]),
            "verified_date": str(record.get("verified_date", "")),
            "content": str(record["content"]),
        }

    legal_basis = record.get("legal_basis") or [{}]
    primary_basis = legal_basis[0] if legal_basis else {}
    law_name = str(primary_basis.get("law", "")).strip()
    article_number = str(primary_basis.get("article", "")).strip()
    content = str(record.get("answer", "")).strip()
    if not law_name or not article_number or not content:
        return None

    return {
        "law_name": law_name,
        "article_number": article_number,
        "category": str(record.get("topic", "ogólne")),
        "verified_date": str(record.get("verified_date", "")),
        "content": content,
    }


def main() -> None:
    kb_files = iter_kb_files()
    if not kb_files:
        raise SystemExit("Brak plików *_kb.json w kb-pipeline/output/")

    merged: dict[tuple[str, str], dict[str, str]] = {}
    counts_per_file: dict[str, int] = {}
    counts_per_law: Counter[str] = Counter()

    for path in kb_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        file_count = 0
        for record in data:
            normalized = normalize_record(record)
            if not normalized:
                continue
            key = (normalized["law_name"], normalized["article_number"])
            existing = merged.get(key)
            if existing is None or len(normalized["content"]) > len(existing["content"]):
                merged[key] = normalized
            file_count += 1
        counts_per_file[path.name] = file_count

    final_records = sorted(
        merged.values(),
        key=lambda item: (item["law_name"], item["article_number"], item["category"]),
    )

    for record in final_records:
        counts_per_law[record["law_name"]] += 1

    SEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEED_PATH.write_text(json.dumps(final_records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("Pliki KB:")
    for name, count in counts_per_file.items():
        print(f"  - {name}: {count}")

    print("Unity per ustawa:")
    for law_name, count in sorted(counts_per_law.items()):
        print(f"  - {law_name}: {count}")

    print(f"Łącznie po deduplikacji: {len(final_records)}")
    print(f"Zapisano: {SEED_PATH}")


if __name__ == "__main__":
    main()
