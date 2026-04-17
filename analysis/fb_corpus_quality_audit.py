"""Quality audit for FB corpus ingest (Zadanie 1.5).

Produces three diagnostic artifacts under ``analysis/``:

* ``rejected_no_question_sample.md`` — 50 random posts (seed=42) rejected by the
  ``no_question_pattern`` filter, full text, pending manual annotation.
* ``top50_engaging_validation.md``  — top-50 posts by ``comments_count`` with a
  heuristic ``looks_like_post`` / ``looks_like_comment`` / ``ambiguous`` tag.
* ``cross_file_dedupe_pairs.json`` — per-pair overlap counts used to rewrite
  section 5 of ``fb_corpus_ingest_report.md``.

Also computes a "cut-off marker" count (``Wyświetl więcej``, ``Zobacz więcej``,
trailing ellipsis) so we know how many posts are truncated by the scraper.

Run from repo root::

    python analysis/fb_corpus_quality_audit.py
"""

from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from fb_pipeline.ingest import ingest_fb_corpus as ingest  # noqa: E402


RNG_SEED = 42
NO_Q_SAMPLE_SIZE = 50
ENGAGING_TOP_N = 50


CUT_OFF_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("wyswietl_wiecej", re.compile(r"wyświetl\s*więcej\s*$", re.IGNORECASE)),
    ("zobacz_wiecej", re.compile(r"zobacz\s*więcej\s*$", re.IGNORECASE)),
    ("trailing_ascii_ellipsis", re.compile(r"\.{3}\s*$")),
    ("trailing_unicode_ellipsis", re.compile(r"…\s*$")),
)


LOWERCASE_START_RE = re.compile(r"^[a-ząćęłńóśżź]")
COMMENT_LIKE_OPENERS = (
    "a ", "i ", "ale ", "no ", "u mnie", "dokładnie", "zgadzam się",
    "nie zgadzam", "tak, ", "tak ", "też ", "właśnie ", "to zależy",
    "moim zdaniem", "według mnie", "wydaje mi się",
)
POST_LIKE_OPENERS = (
    "witam", "dzień dobry", "cześć", "hej", "halo", "kochani", "szanowni",
    "drodzy", "mam pytanie", "mam problem", "potrzebuję", "potrzebuje",
    "proszę o", "prosze o",
)
QUESTION_OPENERS = (
    "jak ", "czy ", "co ", "kiedy ", "gdzie ", "ile ", "kto ", "dlaczego ",
    "jaki ", "jaka ", "jakie ", "jakim ", "który ", "która ", "które ",
)


def _annotate_engaging(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return "ambiguous"
    lower = stripped.lower()
    first_line = lower.splitlines()[0]
    first40 = first_line[:40]

    starts_lowercase = bool(LOWERCASE_START_RE.match(stripped))
    is_comment_opener = any(first40.startswith(p) for p in COMMENT_LIKE_OPENERS)
    is_post_opener = any(first40.startswith(p) for p in POST_LIKE_OPENERS)
    is_question_opener = any(first40.startswith(p) for p in QUESTION_OPENERS)
    has_question_mark = "?" in stripped

    if is_post_opener:
        return "looks_like_post"
    if is_question_opener and has_question_mark:
        return "looks_like_post"
    if starts_lowercase and not is_post_opener:
        return "looks_like_comment"
    if is_comment_opener:
        return "looks_like_comment"
    if not has_question_mark and not is_question_opener:
        return "ambiguous"
    return "looks_like_post"


def _count_cut_offs(records: list[ingest.CandidateRecord]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for record in records:
        # Check each marker independently — a single post can end with both
        # "Wyświetl więcej" and an ellipsis.
        matched_any = False
        for label, pattern in CUT_OFF_PATTERNS:
            if pattern.search(record.text.rstrip()):
                counter[label] += 1
                matched_any = True
        if matched_any:
            counter["_any_cut_off"] += 1
    return counter


def _format_full_text(text: str) -> str:
    """Blockquote escaping: preserve newlines but prefix each line with ``> ``."""
    lines = text.rstrip().splitlines() or [""]
    return "\n".join(f"> {line}" if line.strip() else ">" for line in lines)


def main() -> int:
    # 1. Load sources and build candidates (no --apply, no corpus write).
    per_source_candidates: dict[str, list[ingest.CandidateRecord]] = {}
    per_source_raw: dict[str, int] = {}
    source_meta: dict[str, dict] = {}
    for path_rel, group_id, group_name in ingest.DEFAULT_SOURCES:
        full_path = (REPO_ROOT / path_rel).resolve()
        source = ingest.load_source(full_path, group_id, group_name)
        source_meta[Path(path_rel).name] = {
            "group_id": group_id,
            "group_name": group_name,
            "scraped_at": source.scraped_at,
            "raw": len(source.posts),
        }
        per_source_raw[Path(path_rel).name] = len(source.posts)
        candidates, _ = ingest.build_candidates(source)
        per_source_candidates[Path(path_rel).name] = candidates

    # 2. Cross-file dedupe.
    winners, cross_file_dupes, _, ids_per_source = ingest.resolve_cross_file_duplicates(
        per_source_candidates
    )

    # 3. Per-pair overlap counts.
    names = list(ids_per_source.keys())
    pair_overlaps: list[dict] = []
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            overlap = ids_per_source[left] & ids_per_source[right]
            pair_overlaps.append(
                {
                    "left": left,
                    "left_total": len(ids_per_source[left]),
                    "right": right,
                    "right_total": len(ids_per_source[right]),
                    "overlap": len(overlap),
                }
            )

    # 4. Classify all winners; collect no_question rejects and final records.
    rejected_no_q: list[ingest.CandidateRecord] = []
    final_records: list[ingest.CandidateRecord] = []
    for record in winners:
        keep, reason, _flags = ingest.classify_record(record)
        if not keep:
            if reason == "no_question_pattern":
                rejected_no_q.append(record)
            continue
        final_records.append(record)

    # 5. Random 50 sample of no_question rejects.
    rng = random.Random(RNG_SEED)
    sample_size = min(NO_Q_SAMPLE_SIZE, len(rejected_no_q))
    sampled = rng.sample(rejected_no_q, sample_size)

    # 6. Top-50 engaging from final records.
    top_engaging = sorted(
        final_records,
        key=lambda r: (len(r.comments), r.text_length),
        reverse=True,
    )[:ENGAGING_TOP_N]

    # 7. Cut-off marker counts — over the full final corpus (pre-normalization).
    cut_off_counts = _count_cut_offs(final_records)

    # --- write rejected sample MD ---
    md_lines: list[str] = []
    md_lines.append("# Rejected `no_question_pattern` — 50 random posts (seed=42)")
    md_lines.append("")
    md_lines.append(
        f"Z {len(rejected_no_q)} postów odrzuconych filtrem `no_question_pattern` "
        f"wylosowano {sample_size} próbek (seed={RNG_SEED}). Każda pozycja zachowuje "
        f"pełen tekst bez ucinania. Kolumna **annotation** jest do uzupełnienia "
        f"manualnie: `legit_question` / `truly_not_question` / `ambiguous`."
    )
    md_lines.append("")
    md_lines.append("Kryteria pomocnicze:")
    md_lines.append("- `legit_question` — post opisuje problem księgowy/HR i prosi o radę")
    md_lines.append("  (nawet bez znaku `?` i bez słów kluczowych z obecnej listy).")
    md_lines.append("- `truly_not_question` — ogłoszenie, anegdota, relacja, spam, politykierka,")
    md_lines.append("  dyskusja hipotetyczna bez pytania.")
    md_lines.append("- `ambiguous` — krótki tekst, kontekst niejasny.")
    md_lines.append("")
    for idx, record in enumerate(sampled, start=1):
        md_lines.append(f"## {idx}. `{record.id}` · {record.group_name} · comments: {len(record.comments)}")
        md_lines.append("")
        md_lines.append(f"- **source_file**: {record.source_file}")
        md_lines.append(f"- **text_length**: {record.text_length}")
        md_lines.append(f"- **num_links**: {record.num_links}")
        md_lines.append("- **annotation**: _TBD_")
        md_lines.append("")
        md_lines.append(_format_full_text(record.text))
        md_lines.append("")
    rejected_md_path = REPO_ROOT / "analysis" / "rejected_no_question_sample.md"
    rejected_md_path.write_text("\n".join(md_lines), encoding="utf-8")

    # --- write top-50 engaging validation MD ---
    heuristic_counter: Counter[str] = Counter()
    eng_lines: list[str] = []
    eng_lines.append("# Top 50 engaging posts — manual post/comment validation")
    eng_lines.append("")
    eng_lines.append(
        f"Top {ENGAGING_TOP_N} rekordów finalnego korpusu posortowanych po "
        "`comments_count` (tie-break: `text_length`). Kolumna **heuristic** pochodzi "
        "z prostej reguły otwierającej (lowercase/greeting/question starter). Kolumna "
        "**decision** jest do uzupełnienia manualnie: `looks_like_post` / "
        "`looks_like_comment` / `ambiguous`."
    )
    eng_lines.append("")
    eng_lines.append("| Rank | id | group | comments | chars | heuristic | decision | first 200 chars |")
    eng_lines.append("|---:|---|---|---:|---:|---|---|---|")
    for rank, record in enumerate(top_engaging, start=1):
        heuristic = _annotate_engaging(record.text)
        heuristic_counter[heuristic] += 1
        excerpt = record.text.replace("\n", " ").replace("|", "/").strip()
        if len(excerpt) > 200:
            excerpt = excerpt[:200].rstrip() + "…"
        eng_lines.append(
            f"| {rank} | `{record.id}` | {record.group_name} | {len(record.comments)} | "
            f"{record.text_length} | {heuristic} | _TBD_ | {excerpt} |"
        )
    eng_lines.append("")
    eng_lines.append("## Heuristic tally")
    eng_lines.append("")
    for tag in ("looks_like_post", "looks_like_comment", "ambiguous"):
        eng_lines.append(f"- {tag}: {heuristic_counter.get(tag, 0)}")
    eng_lines.append("")
    eng_lines.append("## Full text for records tagged `looks_like_comment` lub `ambiguous`")
    eng_lines.append("")
    for rank, record in enumerate(top_engaging, start=1):
        heuristic = _annotate_engaging(record.text)
        if heuristic == "looks_like_post":
            continue
        eng_lines.append(f"### {rank}. `{record.id}` · {heuristic}")
        eng_lines.append("")
        eng_lines.append(_format_full_text(record.text))
        eng_lines.append("")
    engaging_md_path = REPO_ROOT / "analysis" / "top50_engaging_validation.md"
    engaging_md_path.write_text("\n".join(eng_lines), encoding="utf-8")

    # --- write cross-file dedupe pairs JSON ---
    pairs_payload = {
        "sources": source_meta,
        "pairs": pair_overlaps,
        "cross_file_duplicates_total": cross_file_dupes,
    }
    pairs_path = REPO_ROOT / "analysis" / "cross_file_dedupe_pairs.json"
    pairs_path.write_text(
        json.dumps(pairs_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # --- stdout summary ---
    summary = {
        "rejected_no_question_total": len(rejected_no_q),
        "sample_written": sample_size,
        "top_engaging_written": len(top_engaging),
        "heuristic_counter": dict(heuristic_counter),
        "cut_off_counts": dict(cut_off_counts),
        "cross_file_dupes_total": cross_file_dupes,
        "pairs": pair_overlaps,
        "sources": source_meta,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
