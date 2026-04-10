"""Remove negative/out-of-scope units and duplicate content from law_knowledge.json.

Run:
    python -m kb-pipeline.cleanup_negatives
    python -m kb-pipeline.cleanup_negatives --dry-run   # preview only, don't write
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_PATH = PROJECT_ROOT / "data" / "seeds" / "law_knowledge.json"

NEGATIVE_PHRASES = (
    "nie mogę odpowiedzieć",
    "nie moge odpowiedziec",
    "nie jestem w stanie",
    "poza zakresem",
    "brak danych",
    "nie dotyczy",
    "brak wystarczających informacji",
    "brak wystarczajacych informacji",
    "nie mam wystarczających",
    "nie mam wystarczajacych",
    "brak informacji",
    "nie zawiera przepisów",
    "nie zawiera przepisow",
)


def load_knowledge() -> list[dict[str, str]]:
    return json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8-sig"))


def save_knowledge(records: list[dict[str, str]]) -> None:
    KNOWLEDGE_PATH.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def is_negative(record: dict[str, str]) -> bool:
    content = record.get("content", "").lower()
    article = record.get("article_number", "").lower()
    return (
        any(phrase in content for phrase in NEGATIVE_PHRASES)
        or "brak przepisów" in article
        or "brak przepisow" in article
    )


def find_negatives(records: list[dict[str, str]]) -> list[tuple[int, dict[str, str]]]:
    return [(i, r) for i, r in enumerate(records) if is_negative(r)]


def find_duplicates(records: list[dict[str, str]]) -> list[int]:
    """Return indices of duplicate records to remove (keep first occurrence)."""
    seen: dict[str, int] = {}
    to_remove: list[int] = []
    for i, r in enumerate(records):
        content = r.get("content", "").strip()
        if content in seen:
            to_remove.append(i)
        else:
            seen[content] = i
    return to_remove


def print_law_table(records: list[dict[str, str]], label: str) -> None:
    counter: Counter[str] = Counter()
    for r in records:
        counter[r.get("law_name", "(brak)")] += 1
    print(f"\n  {label} ({len(records)} total):")
    for law, count in counter.most_common():
        print(f"    {law}: {count}")


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    records = load_knowledge()
    original_count = len(records)

    # --- Step 1: Remove negatives ---
    negatives = find_negatives(records)
    print(f"{'=' * 60}")
    print(f"STEP 1: NEGATIVE/OUT-OF-SCOPE UNITS")
    print(f"{'=' * 60}")
    print(f"\nFound {len(negatives)} negative units out of {original_count}")

    neg_by_law: Counter[str] = Counter()
    for _, r in negatives:
        neg_by_law[r.get("law_name", "(brak)")] += 1
    print("\n  Breakdown by law:")
    for law, count in neg_by_law.most_common():
        print(f"    {law}: {count}")

    print("\n  Sample (first 15):")
    for idx, r in negatives[:15]:
        preview = r.get("content", "")[:100].replace("\n", " ")
        print(f"    [{idx}] [{r.get('law_name')}] {r.get('article_number')}: {preview}...")

    negative_indices = {i for i, _ in negatives}
    cleaned = [r for i, r in enumerate(records) if i not in negative_indices]
    print(f"\n  After removing negatives: {len(cleaned)} units (removed {original_count - len(cleaned)})")

    # --- Step 2: Remove duplicates ---
    dup_indices = find_duplicates(cleaned)
    print(f"\n{'=' * 60}")
    print(f"STEP 2: DUPLICATE CONTENT")
    print(f"{'=' * 60}")
    print(f"\nFound {len(dup_indices)} duplicate units to remove")

    if dup_indices:
        print("\n  Sample duplicates (first 10):")
        for idx in dup_indices[:10]:
            r = cleaned[idx]
            preview = r.get("content", "")[:80].replace("\n", " ")
            print(f"    [{idx}] [{r.get('law_name')}] {r.get('article_number')}: {preview}...")

    dup_set = set(dup_indices)
    final = [r for i, r in enumerate(cleaned) if i not in dup_set]

    # --- Summary ---
    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"\n  Original: {original_count}")
    print(f"  Negatives removed: {len(negatives)}")
    print(f"  Duplicates removed: {len(dup_indices)}")
    print(f"  Final: {len(final)}")

    print_law_table(final, "Final distribution")

    if dry_run:
        print("\n  [DRY RUN] No changes written.")
    else:
        save_knowledge(final)
        print(f"\n  Written {len(final)} units to {KNOWLEDGE_PATH}")


if __name__ == "__main__":
    main()
