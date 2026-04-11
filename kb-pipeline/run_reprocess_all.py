"""Run generate_units.py and audit_units.py on all reprocess inputs.

Safe to restart thanks to checkpoint/resume in both pipeline steps.
Defaults to the local kb-pipeline virtualenv when present.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPROCESS_DIR = ROOT / "output" / "reprocess"
DEFAULT_TIMEOUT_SECONDS = 21_600
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
if not PYTHON.exists():
    PYTHON = Path(sys.executable)


def find_law_pairs(selected_slugs: set[str] | None = None) -> list[tuple[str, Path, Path]]:
    pairs: list[tuple[str, Path, Path]] = []
    for articles_file in sorted(REPROCESS_DIR.glob("articles_*.json")):
        slug = articles_file.stem.replace("articles_", "")
        if selected_slugs and slug not in selected_slugs:
            continue
        matched_file = REPROCESS_DIR / f"matched_{slug}.json"
        if matched_file.exists():
            pairs.append((slug, articles_file, matched_file))
    return pairs


def count_questions(matched_path: Path) -> int:
    data = json.loads(matched_path.read_text(encoding="utf-8"))
    return len(data.get("matches", []))


def run_subprocess(command: list[str], *, timeout: int) -> int:
    result = subprocess.run(command, cwd=str(ROOT), timeout=timeout)
    return int(result.returncode)


def run_generate(slug: str, articles: Path, matched: Path, *, timeout: int) -> Path:
    output = REPROCESS_DIR / f"draft_{slug}.json"
    questions = count_questions(matched)
    print(f"\n{'=' * 60}")
    print(f"GENERATE: {slug} ({questions} questions)")
    print(f"{'=' * 60}")

    return_code = run_subprocess(
        [str(PYTHON), str(ROOT / "generate_units.py"), str(articles), str(matched), "--output", str(output)],
        timeout=timeout,
    )
    if return_code != 0:
        print(f"  WARNING: generate_units.py exited with code {return_code}")
    return output


def run_audit(slug: str, articles: Path, draft: Path, *, timeout: int) -> Path:
    output = REPROCESS_DIR / f"verified_{slug}.json"
    print(f"\n{'=' * 60}")
    print(f"AUDIT: {slug}")
    print(f"{'=' * 60}")

    return_code = run_subprocess(
        [str(PYTHON), str(ROOT / "audit_units.py"), str(articles), str(draft), "--output", str(output)],
        timeout=timeout,
    )
    if return_code != 0:
        print(f"  WARNING: audit_units.py exited with code {return_code}")
    return output


def parse_args(argv: list[str]) -> tuple[set[str] | None, bool, bool, int]:
    selected_slugs: set[str] | None = None
    run_generate_phase = True
    run_audit_phase = True
    timeout = DEFAULT_TIMEOUT_SECONDS

    if "--only" in argv:
        index = argv.index("--only")
        selected_slugs = set()
        for item in argv[index + 1 :]:
            if item.startswith("--"):
                break
            selected_slugs.add(item)

    if "--generate-only" in argv:
        run_audit_phase = False
    if "--audit-only" in argv:
        run_generate_phase = False
    if "--timeout" in argv:
        timeout = int(argv[argv.index("--timeout") + 1])

    return selected_slugs, run_generate_phase, run_audit_phase, timeout


def main() -> None:
    selected_slugs, run_generate_phase, run_audit_phase, timeout = parse_args(sys.argv[1:])
    pairs = find_law_pairs(selected_slugs)
    print(f"Python: {PYTHON}")
    print(f"Found {len(pairs)} law pairs to process")
    for slug, _, matched in pairs:
        print(f"  {slug}: {count_questions(matched)} questions")

    total_start = time.time()
    drafts: list[tuple[str, Path, Path]] = []

    if run_generate_phase:
        for slug, articles, matched in pairs:
            draft = run_generate(slug, articles, matched, timeout=timeout)
            drafts.append((slug, articles, draft))
    else:
        drafts = [(slug, articles, REPROCESS_DIR / f"draft_{slug}.json") for slug, articles, _ in pairs]

    if run_audit_phase:
        for slug, articles, draft in drafts:
            if not draft.exists():
                print(f"  SKIP audit for {slug}: no draft file")
                continue
            run_audit(slug, articles, draft, timeout=timeout)

    elapsed = int(time.time() - total_start)
    minutes, seconds = divmod(elapsed, 60)
    hours, minutes = divmod(minutes, 60)
    print(f"\n{'=' * 60}")
    print(f"DONE: {hours}h {minutes:02d}m {seconds:02d}s")

    total_verified = 0
    total_needs_fix = 0
    total_rejected = 0
    total_cost = 0.0

    for slug, _, _ in pairs:
        verified_file = REPROCESS_DIR / f"verified_{slug}.json"
        if verified_file.exists():
            data = json.loads(verified_file.read_text(encoding="utf-8"))
            meta = data.get("metadata", {})
            total_verified += int(meta.get("verified", 0) or 0)
            total_needs_fix += int(meta.get("needs_fix", 0) or 0)
            total_rejected += int(meta.get("rejected", 0) or 0)
            total_cost += float(meta.get("total_cost_usd", 0.0) or 0.0)

        draft_file = REPROCESS_DIR / f"draft_{slug}.json"
        if draft_file.exists():
            data = json.loads(draft_file.read_text(encoding="utf-8"))
            total_cost += float(data.get("metadata", {}).get("total_cost_usd", 0.0) or 0.0)

    print(f"Verified: {total_verified}")
    print(f"Needs fix: {total_needs_fix}")
    print(f"Rejected: {total_rejected}")
    print(f"Total cost: ${total_cost:.2f}")


if __name__ == "__main__":
    main()
