"""
AKTUO — Merge & Stats from ChatGPT batch outputs
==================================================
Krok 3: Łączy outputy z ChatGPT, generuje statystyki.
Deduplikacja odbywa się w ChatGPT (prompt końcowy) — tu łączymy surowe outputy.

Input:  batch_outputs/batch_001_output.json, batch_002_output.json, ...
Output:
  - all_questions_raw.json    — wszystkie pytania ze wszystkich batchy
  - merge_stats.txt           — statystyki

Uruchomienie:
  python 03_merge_outputs.py
"""

import json
import os
from pathlib import Path
from collections import Counter

BATCH_OUTPUT_DIR = "batch_outputs"
MERGED_FILE = "all_questions_raw.json"
STATS_FILE = "merge_stats.txt"


def load_batch_outputs(directory: str) -> list:
    """Load all batch JSON outputs."""
    all_questions = []
    files = sorted(Path(directory).glob("batch_*_output.json"))

    if not files:
        print(f"No files found in {directory}/")
        print(f"Expected: batch_001_output.json, batch_002_output.json, ...")
        print(f"Save ChatGPT outputs there first.")
        return []

    for f in files:
        print(f"  Loading {f.name}...")
        try:
            with open(f, "r", encoding="utf-8-sig") as fp:
                data = json.load(fp)

            # Handle different output formats
            if isinstance(data, dict) and "questions" in data:
                questions = data["questions"]
            elif isinstance(data, list):
                questions = data
            else:
                print(f"    WARNING: unexpected format in {f.name}, skipping")
                continue

            for q in questions:
                q["source_batch"] = f.name
            all_questions.extend(questions)
            print(f"    → {len(questions)} pytań")

        except json.JSONDecodeError as e:
            print(f"    ERROR: Invalid JSON in {f.name}: {e}")
            print(f"    Tip: ChatGPT may have truncated. Check the file.")

    return all_questions


def generate_stats(questions: list) -> str:
    """Generate merge statistics."""
    total = len(questions)
    cats = Counter(q.get("cat", "unknown") for q in questions)

    lines = [
        "=" * 50,
        "AKTUO — Merged Questions Stats",
        "=" * 50,
        f"Total questions (before dedup): {total}",
        f"",
        "--- By category ---",
    ]

    for cat, count in cats.most_common():
        pct = count / total * 100 if total > 0 else 0
        lines.append(f"  {cat:15s}: {count:5d} ({pct:.1f}%)")

    # Sub-category stats
    subs = Counter(q.get("sub", "unknown") for q in questions)
    lines += [
        f"",
        "--- Top 20 sub-categories ---",
    ]
    for sub, count in subs.most_common(20):
        lines.append(f"  {sub:30s}: {count:4d}")

    lines += [
        f"",
        "=" * 50,
        f"Next step: Wklej {MERGED_FILE} do ChatGPT z PROMPT KOŃCOWY",
        f"(z pliku 02_chatgpt_prompts.md, sekcja 3)",
        "=" * 50,
    ]
    return "\n".join(lines)


def main():
    print("Merging batch outputs...")
    questions = load_batch_outputs(BATCH_OUTPUT_DIR)

    if not questions:
        return

    print(f"\nTotal: {len(questions)} questions from all batches.")

    # Save merged
    with open(MERGED_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"Saved → {MERGED_FILE}")

    # Stats
    stats = generate_stats(questions)
    print(stats)
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        f.write(stats)


if __name__ == "__main__":
    main()
