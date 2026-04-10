"""Gap analysis: compare all KB-pipeline questions against the retriever.

Loads all questions from kb-pipeline/questions_*.json (excluding
questions_patch.json), runs each through categorizer + BM25 retriever
(no API key needed), and classifies results as:

  COVERED — top chunk BM25 score ≥ 2.0
  WEAK    — top chunk score 0.5–2.0
  GAP     — top chunk score < 0.5 or no results

Outputs:
  - Console summary with per-category breakdown
  - tests/output/kb_gaps_report.json with top 100 gaps + full statistics

Run:
    python -m tests.gap_analysis
    python -m tests.gap_analysis --limit 50   # limit per category
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

QUESTIONS_DIR = PROJECT_ROOT / "kb-pipeline"
KNOWLEDGE_PATH = PROJECT_ROOT / "data" / "seeds" / "law_knowledge.json"
OUTPUT_PATH = PROJECT_ROOT / "tests" / "output" / "kb_gaps_report.json"

# BM25 thresholds (matching config/settings.py BM25_MIN_SCORE = 2.0)
COVERED_THRESHOLD = 2.0
WEAK_THRESHOLD = 0.5

SKIP_FILES = {"questions_patch.json"}


def load_all_questions(limit_per_category: int | None = None) -> list[dict]:
    """Load questions from all kb-pipeline/questions_*.json files."""
    all_questions: list[dict] = []
    files = sorted(QUESTIONS_DIR.glob("questions_*.json"))

    for filepath in files:
        if filepath.name in SKIP_FILES:
            continue
        raw = json.loads(filepath.read_text(encoding="utf-8"))
        # Sort by source_freq descending if available, then take top N
        has_freq = any(q.get("source_freq") for q in raw)
        if has_freq:
            raw.sort(key=lambda q: q.get("source_freq", 0), reverse=True)
        if limit_per_category:
            raw = raw[:limit_per_category]
        for q in raw:
            q["_source_file"] = filepath.name
        all_questions.extend(raw)

    return all_questions


def classify_question(question: str) -> dict:
    """Run a single question through categorizer + BM25 and classify."""
    from core.categorizer import categorize_query
    from core.retriever import retrieve_chunks

    category = categorize_query(question)
    chunks = retrieve_chunks(query=question, knowledge_path=str(KNOWLEDGE_PATH), limit=5)

    top_score = chunks[0].score if chunks else 0.0
    avg_score = sum(c.score for c in chunks) / len(chunks) if chunks else 0.0

    if top_score >= COVERED_THRESHOLD:
        grade = "COVERED"
    elif top_score >= WEAK_THRESHOLD:
        grade = "WEAK"
    else:
        grade = "GAP"

    top_chunk_info = None
    if chunks:
        c = chunks[0]
        top_chunk_info = {
            "law_name": c.law_name,
            "article_number": c.article_number,
            "category": c.category,
            "score": round(c.score, 3),
            "content_preview": c.content[:150],
        }

    return {
        "category": category,
        "grade": grade,
        "top_score": round(top_score, 3),
        "avg_score": round(avg_score, 3),
        "num_chunks": len(chunks),
        "top_chunk": top_chunk_info,
    }


def main() -> None:
    limit_per_cat = None
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        limit_per_cat = int(sys.argv[idx + 1])

    print("Loading questions...")
    questions = load_all_questions(limit_per_category=limit_per_cat)
    print(f"Loaded {len(questions)} questions from {QUESTIONS_DIR}")

    # Show source file distribution
    file_counter: Counter[str] = Counter(q["_source_file"] for q in questions)
    print("\n  Source files:")
    for fname, count in file_counter.most_common():
        print(f"    {fname}: {count}")

    print(f"\nRunning categorizer + BM25 retriever on {len(questions)} questions...")
    print("(no API key needed — this tests retrieval only)\n")

    results: list[dict] = []
    grade_counter: Counter[str] = Counter()
    category_grades: dict[str, Counter[str]] = defaultdict(Counter)
    start_time = time.time()

    for i, q in enumerate(questions):
        question_text = q.get("question", "")
        if not question_text.strip():
            continue

        result = classify_question(question_text)
        result["question"] = question_text
        result["source_category"] = q.get("category", "?")
        result["topic"] = q.get("topic", "")
        result["source_freq"] = q.get("source_freq", 0)
        result["source_file"] = q.get("_source_file", "")
        results.append(result)

        grade_counter[result["grade"]] += 1
        category_grades[result["source_category"]][result["grade"]] += 1

        if (i + 1) % 100 == 0:
            elapsed = time.time() - start_time
            print(f"  Processed {i+1}/{len(questions)} ({elapsed:.1f}s) — "
                  f"COVERED: {grade_counter['COVERED']}, "
                  f"WEAK: {grade_counter['WEAK']}, "
                  f"GAP: {grade_counter['GAP']}")

    total_time = time.time() - start_time

    # --- Summary ---
    total = len(results)
    print(f"\n{'=' * 72}")
    print("GAP ANALYSIS SUMMARY")
    print(f"{'=' * 72}")
    print(f"\n  Total questions analyzed: {total}")
    print(f"  Time: {total_time:.1f}s ({total_time/max(total,1)*1000:.0f}ms/question)")
    print(f"\n  COVERED (score ≥ {COVERED_THRESHOLD}): {grade_counter['COVERED']:>4} "
          f"({100*grade_counter['COVERED']/max(total,1):.1f}%)")
    print(f"  WEAK    (score {WEAK_THRESHOLD}–{COVERED_THRESHOLD}):  {grade_counter['WEAK']:>4} "
          f"({100*grade_counter['WEAK']/max(total,1):.1f}%)")
    print(f"  GAP     (score < {WEAK_THRESHOLD}):      {grade_counter['GAP']:>4} "
          f"({100*grade_counter['GAP']/max(total,1):.1f}%)")

    # Per-category breakdown
    print(f"\n{'=' * 72}")
    print("PER-CATEGORY BREAKDOWN")
    print(f"{'=' * 72}")
    print(f"\n  {'Category':<20} {'Total':>5} {'COVERED':>8} {'WEAK':>6} {'GAP':>5} {'Cover%':>7}")
    print(f"  {'-'*20} {'-'*5} {'-'*8} {'-'*6} {'-'*5} {'-'*7}")

    for cat in sorted(category_grades.keys()):
        cg = category_grades[cat]
        cat_total = sum(cg.values())
        cover_pct = 100 * cg["COVERED"] / max(cat_total, 1)
        print(f"  {cat:<20} {cat_total:>5} {cg['COVERED']:>8} {cg['WEAK']:>6} {cg['GAP']:>5} {cover_pct:>6.1f}%")

    # Top 100 gaps sorted by source_freq (most-asked questions that KB can't answer)
    gaps = [r for r in results if r["grade"] == "GAP"]
    gaps.sort(key=lambda r: r.get("source_freq", 0), reverse=True)
    top_gaps = gaps[:100]

    print(f"\n{'=' * 72}")
    print(f"TOP {len(top_gaps)} GAPS (most-asked questions with no KB coverage)")
    print(f"{'=' * 72}")
    for i, g in enumerate(top_gaps[:30]):
        freq = g.get("source_freq", 0)
        freq_str = f"freq={freq}" if freq else "no-freq"
        q_short = g["question"][:70]
        print(f"  {i+1:>3}. [{g['source_category']}] ({freq_str}) score={g['top_score']:.2f}: {q_short}")
    if len(top_gaps) > 30:
        print(f"  ... and {len(top_gaps) - 30} more (see JSON report)")

    # Weak questions (potential quick wins)
    weaks = [r for r in results if r["grade"] == "WEAK"]
    weaks.sort(key=lambda r: r.get("source_freq", 0), reverse=True)

    print(f"\n{'=' * 72}")
    print(f"TOP 20 WEAK (quick wins — partially covered, score {WEAK_THRESHOLD}–{COVERED_THRESHOLD})")
    print(f"{'=' * 72}")
    for i, w in enumerate(weaks[:20]):
        freq = w.get("source_freq", 0)
        freq_str = f"freq={freq}" if freq else "no-freq"
        q_short = w["question"][:65]
        print(f"  {i+1:>3}. [{w['source_category']}] ({freq_str}) score={w['top_score']:.2f}: {q_short}")

    # Topic clustering for gaps
    gap_topics: Counter[str] = Counter()
    for g in gaps:
        topic = g.get("topic", "").strip()
        if topic:
            gap_topics[topic] += 1

    print(f"\n{'=' * 72}")
    print("GAP TOPIC CLUSTERS (most common missing topics)")
    print(f"{'=' * 72}")
    for topic, count in gap_topics.most_common(30):
        print(f"  {topic}: {count}")

    # Save JSON report
    report = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_questions": total,
            "total_time_seconds": round(total_time, 1),
            "covered_threshold": COVERED_THRESHOLD,
            "weak_threshold": WEAK_THRESHOLD,
        },
        "summary": {
            "covered": grade_counter["COVERED"],
            "weak": grade_counter["WEAK"],
            "gap": grade_counter["GAP"],
            "covered_pct": round(100 * grade_counter["COVERED"] / max(total, 1), 1),
            "weak_pct": round(100 * grade_counter["WEAK"] / max(total, 1), 1),
            "gap_pct": round(100 * grade_counter["GAP"] / max(total, 1), 1),
        },
        "per_category": {
            cat: {
                "total": sum(cg.values()),
                "covered": cg["COVERED"],
                "weak": cg["WEAK"],
                "gap": cg["GAP"],
                "covered_pct": round(100 * cg["COVERED"] / max(sum(cg.values()), 1), 1),
            }
            for cat, cg in sorted(category_grades.items())
        },
        "top_100_gaps": [
            {
                "question": g["question"],
                "source_category": g["source_category"],
                "topic": g.get("topic", ""),
                "source_freq": g.get("source_freq", 0),
                "detected_category": g["category"],
                "top_score": g["top_score"],
                "top_chunk": g.get("top_chunk"),
            }
            for g in top_gaps
        ],
        "top_20_weak": [
            {
                "question": w["question"],
                "source_category": w["source_category"],
                "topic": w.get("topic", ""),
                "source_freq": w.get("source_freq", 0),
                "detected_category": w["category"],
                "top_score": w["top_score"],
                "top_chunk": w.get("top_chunk"),
            }
            for w in weaks[:20]
        ],
        "gap_topic_clusters": [
            {"topic": topic, "count": count}
            for topic, count in gap_topics.most_common(50)
        ],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nReport saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
