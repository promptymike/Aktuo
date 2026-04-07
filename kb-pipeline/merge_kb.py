from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "kb-pipeline" / "output"
SEED_PATH = PROJECT_ROOT / "data" / "seeds" / "law_knowledge.json"
BACKUP_PATH = PROJECT_ROOT / "data" / "seeds" / "law_knowledge_backup_pre_merge.json"


def iter_kb_files() -> list[Path]:
    candidates: list[Path] = []
    for path in sorted(OUTPUT_DIR.glob("*_kb.json")):
        name = path.name.lower()
        if "test" in name or "first10" in name:
            continue
        candidates.append(path)

    names = {path.name for path in candidates}
    selected: list[Path] = []
    for path in candidates:
        name = path.name
        if name.startswith("verified_") and name.removeprefix("verified_") in names:
            selected.append(path)
            continue
        if f"verified_{name}" in names:
            continue
        selected.append(path)
    return selected


def normalize_record(record: dict) -> dict[str, str] | None:
    if {"law_name", "article_number", "category", "verified_date", "content"} <= record.keys():
        normalized = {
            "law_name": str(record["law_name"]).strip(),
            "article_number": str(record["article_number"]).strip(),
            "category": str(record["category"]).strip(),
            "verified_date": str(record.get("verified_date", "")).strip(),
            "content": str(record["content"]).strip(),
        }
        if record.get("source"):
            normalized["source"] = str(record["source"]).strip()
        return normalized

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
        "category": str(record.get("topic", "ogolne")).strip(),
        "verified_date": str(record.get("verified_date", "")).strip(),
        "content": content,
    }


def normalize_article_number(article_number: str) -> str:
    normalized = " ".join(str(article_number).strip().split())
    if normalized.lower().startswith("art."):
        normalized = "art." + normalized[4:]
    return normalized


def record_key(record: dict[str, str]) -> tuple[str, str, str]:
    return (
        record["law_name"],
        normalize_article_number(record["article_number"]),
        record["content"],
    )


def backup_seed() -> None:
    if not SEED_PATH.exists():
        return
    BACKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SEED_PATH, BACKUP_PATH)


def format_row(source: str, input_count: int, deduped_count: int) -> str:
    return f"| {source} | {input_count} | {deduped_count} |"


def main() -> None:
    kb_files = iter_kb_files()
    if not kb_files:
        raise SystemExit("Brak plików *_kb.json w kb-pipeline/output/")

    backup_seed()

    existing_seed: list[dict[str, str]] = []
    if SEED_PATH.exists():
        existing_seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))

    merged_records: list[dict[str, str]] = []
    seen_keys: set[tuple[str, str, str]] = set()
    counts_per_file: dict[str, int] = {}
    deduped_per_file: dict[str, int] = {}
    counts_per_law: Counter[str] = Counter()
    removed_duplicates = 0

    for path in kb_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        input_count = 0
        kept_count = 0
        for record in data:
            normalized = normalize_record(record)
            if not normalized:
                continue
            input_count += 1
            key = record_key(normalized)
            if key in seen_keys:
                removed_duplicates += 1
                continue
            seen_keys.add(key)
            merged_records.append(normalized)
            kept_count += 1
        counts_per_file[path.name] = input_count
        deduped_per_file[path.name] = kept_count

    legacy_added = 0
    for record in existing_seed:
        normalized = normalize_record(record)
        if not normalized:
            continue
        key = record_key(normalized)
        if key in seen_keys:
            continue
        normalized["source"] = "legacy"
        seen_keys.add(key)
        merged_records.append(normalized)
        legacy_added += 1

    final_records = sorted(
        merged_records,
        key=lambda item: (
            item["law_name"],
            normalize_article_number(item["article_number"]),
            item["content"],
        ),
    )

    for record in final_records:
        counts_per_law[record["law_name"]] += 1

    SEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEED_PATH.write_text(json.dumps(final_records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("Tabela scalenia:")
    print("| Źródło | Rekordy wejściowe | Po deduplikacji |")
    print("| --- | ---: | ---: |")
    total_input = 0
    total_deduped = 0
    for path in kb_files:
        name = path.name
        input_count = counts_per_file.get(name, 0)
        deduped_count = deduped_per_file.get(name, 0)
        total_input += input_count
        total_deduped += deduped_count
        print(format_row(name, input_count, deduped_count))
    print(format_row("Legacy (zachowane ze starego pliku)", len(existing_seed), legacy_added))
    print(format_row("RAZEM", total_input + len(existing_seed), total_deduped + legacy_added))

    print(f"\nUsunięte duplikaty (identyczny law_name + article_number + content): {removed_duplicates}")
    print(f"Dodane rekordy legacy: {legacy_added}")

    print("\nUnity per ustawa:")
    for law_name, count in sorted(counts_per_law.items()):
        print(f"  - {law_name}: {count}")

    print(f"\nŁącznie unikalnych rekordów: {len(final_records)}")
    print(f"Backup starego pliku: {BACKUP_PATH}")
    print(f"Zapisano: {SEED_PATH}")


if __name__ == "__main__":
    main()
