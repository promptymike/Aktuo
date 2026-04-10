"""Accountant-style audit: real FB questions through the retriever pipeline.

Picks 50 random questions from kb-pipeline/questions_*.json that have
source_freq (= real FB posts from bookkeepers), runs them through
categorizer + BM25 retriever, and grades results:

  GOOD — top chunk score ≥ 2.0 AND category match between source & detected
  WEAK — top chunk score 0.5–2.0, OR category mismatch with decent score
  MISS — top chunk score < 0.5, or detected category clearly wrong

This tests the system with real bookkeeper language: abbreviations (JDG,
UoP, DRA, PUE, B2B), typos, colloquial Polish, and incomplete sentences.

Run:
    python -m tests.accountant_audit
    python -m tests.accountant_audit --seed 42    # reproducible sample
    python -m tests.accountant_audit --all        # all FB questions, not just 50
"""

from __future__ import annotations

import json
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

QUESTIONS_DIR = PROJECT_ROOT / "kb-pipeline"
KNOWLEDGE_PATH = PROJECT_ROOT / "data" / "seeds" / "law_knowledge.json"
OUTPUT_PATH = PROJECT_ROOT / "tests" / "output" / "accountant_audit_report.json"

COVERED_THRESHOLD = 2.0
WEAK_THRESHOLD = 0.5
DEFAULT_SAMPLE_SIZE = 50

SKIP_FILES = {"questions_patch.json"}

# Map source category labels (uppercase) to categorizer output (lowercase)
CATEGORY_NORMALIZATION = {
    "VAT": {"vat", "fakturowanie", "faktury_korygujące", "korekty",
             "podatek_naliczony", "podatek_należny", "terminy"},
    "CIT": {"cit"},
    "PIT": {"pit"},
    "ZUS": {"zus"},
    "KADRY": {"kadry"},
    "JPK": {"jpk"},
    "KSeF": {"ksef"},
    "RACHUNKOWOŚĆ": {"rachunkowosc"},
    "RACHUNKOWO??": {"rachunkowosc"},
    "Ordynacja podatkowa": {"ordynacja"},
}


def _categories_compatible(source_cat: str, detected_cat: str) -> bool:
    """Check if the detected category is compatible with the source."""
    expected = CATEGORY_NORMALIZATION.get(source_cat, set())
    if not expected:
        return True  # Unknown source category, don't penalize
    return detected_cat in expected or detected_cat == "ogólne"


def load_fb_questions() -> list[dict]:
    """Load questions that have source_freq (real FB posts)."""
    fb_questions: list[dict] = []
    files = sorted(QUESTIONS_DIR.glob("questions_*.json"))

    for filepath in files:
        if filepath.name in SKIP_FILES:
            continue
        raw = json.loads(filepath.read_text(encoding="utf-8"))
        for q in raw:
            if q.get("source_freq", 0) > 0:
                q["_source_file"] = filepath.name
                fb_questions.append(q)

    return fb_questions


def audit_question(question: str, source_cat: str) -> dict:
    """Run a single question through categorizer + BM25 and grade it."""
    from core.categorizer import categorize_query
    from core.retriever import retrieve_chunks

    category = categorize_query(question)
    chunks = retrieve_chunks(query=question, knowledge_path=str(KNOWLEDGE_PATH), limit=5)

    top_score = chunks[0].score if chunks else 0.0
    avg_score = sum(c.score for c in chunks) / len(chunks) if chunks else 0.0
    cat_ok = _categories_compatible(source_cat, category)

    if top_score >= COVERED_THRESHOLD and cat_ok:
        grade = "GOOD"
    elif top_score >= WEAK_THRESHOLD or (top_score >= COVERED_THRESHOLD and not cat_ok):
        grade = "WEAK"
    else:
        grade = "MISS"

    issues: list[str] = []
    if not cat_ok:
        issues.append(f"category mismatch: {source_cat}→{category}")
    if top_score < WEAK_THRESHOLD:
        issues.append(f"low score: {top_score:.2f}")
    if not chunks:
        issues.append("no chunks returned")

    top_chunks_info = []
    for c in chunks[:3]:
        top_chunks_info.append({
            "law_name": c.law_name,
            "article_number": c.article_number,
            "category": c.category,
            "score": round(c.score, 3),
            "content_preview": c.content[:120],
        })

    return {
        "detected_category": category,
        "category_match": cat_ok,
        "grade": grade,
        "top_score": round(top_score, 3),
        "avg_score": round(avg_score, 3),
        "issues": issues,
        "top_chunks": top_chunks_info,
    }


def main() -> None:
    seed = 2026
    sample_size = DEFAULT_SAMPLE_SIZE
    run_all = False

    if "--seed" in sys.argv:
        idx = sys.argv.index("--seed")
        seed = int(sys.argv[idx + 1])
    if "--all" in sys.argv:
        run_all = True

    print("Loading FB questions (with source_freq)...")
    fb_questions = load_fb_questions()
    print(f"Found {len(fb_questions)} questions from real FB posts\n")

    if not fb_questions:
        print("ERROR: No FB questions found with source_freq > 0")
        sys.exit(1)

    # Source category distribution
    src_counter: Counter[str] = Counter(q.get("category", "?") for q in fb_questions)
    print("  Source category distribution:")
    for cat, count in src_counter.most_common():
        print(f"    {cat}: {count}")

    # Sample
    if run_all:
        sample = fb_questions
        print(f"\n  Running ALL {len(sample)} FB questions")
    else:
        random.seed(seed)
        sample = random.sample(fb_questions, min(sample_size, len(fb_questions)))
        print(f"\n  Sampled {len(sample)} questions (seed={seed})")

    print(f"\nRunning accountant-style audit (categorizer + BM25)...")
    print("Testing with real bookkeeper language: skróty, potoczny język, literówki\n")

    results: list[dict] = []
    grade_counter: Counter[str] = Counter()
    cat_mismatch_counter: Counter[str] = Counter()
    start_time = time.time()

    for i, q in enumerate(sample):
        question_text = q.get("question", "")
        source_cat = q.get("category", "?")
        if not question_text.strip():
            continue

        result = audit_question(question_text, source_cat)
        result["question"] = question_text
        result["source_category"] = source_cat
        result["topic"] = q.get("topic", "")
        result["source_freq"] = q.get("source_freq", 0)
        result["source_file"] = q.get("_source_file", "")
        results.append(result)

        grade_counter[result["grade"]] += 1
        if not result["category_match"]:
            cat_mismatch_counter[f"{source_cat}→{result['detected_category']}"] += 1

        if (i + 1) % 25 == 0:
            elapsed = time.time() - start_time
            print(f"  Processed {i+1}/{len(sample)} ({elapsed:.1f}s)")

    total_time = time.time() - start_time
    total = len(results)

    # --- Results table ---
    print(f"\n{'=' * 80}")
    print("ACCOUNTANT AUDIT RESULTS")
    print(f"{'=' * 80}")

    print(f"\n{'#':>3} {'Grade':<5} {'Score':>6} {'SrcCat':<8} {'DetCat':<18} Question")
    print(f"{'-'*3} {'-'*5} {'-'*6} {'-'*8} {'-'*18} {'-'*40}")

    for i, r in enumerate(results):
        q_short = r["question"][:55]
        print(f"{i+1:>3} {r['grade']:<5} {r['top_score']:>6.2f} "
              f"{r['source_category']:<8} {r['detected_category']:<18} {q_short}")

    # --- Summary ---
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"\n  Total audited: {total}")
    print(f"  Time: {total_time:.1f}s")
    print(f"\n  GOOD (well covered): {grade_counter['GOOD']:>3} ({100*grade_counter['GOOD']/max(total,1):.1f}%)")
    print(f"  WEAK (partial):      {grade_counter['WEAK']:>3} ({100*grade_counter['WEAK']/max(total,1):.1f}%)")
    print(f"  MISS (no coverage):  {grade_counter['MISS']:>3} ({100*grade_counter['MISS']/max(total,1):.1f}%)")

    # Category mismatch analysis
    mismatches = [r for r in results if not r["category_match"]]
    if mismatches:
        print(f"\n  Category mismatches: {len(mismatches)}")
        for pattern, count in cat_mismatch_counter.most_common():
            print(f"    {pattern}: {count}")

    # MISS details
    misses = [r for r in results if r["grade"] == "MISS"]
    if misses:
        print(f"\n{'=' * 80}")
        print("MISS DETAILS (questions the system cannot answer)")
        print(f"{'=' * 80}")
        for r in misses:
            print(f"\n  Q: {r['question'][:100]}")
            print(f"    Source: {r['source_category']} | Detected: {r['detected_category']} | "
                  f"Score: {r['top_score']:.2f} | Freq: {r['source_freq']}")
            for issue in r["issues"]:
                print(f"    Issue: {issue}")

    # WEAK details
    weaks = [r for r in results if r["grade"] == "WEAK"]
    if weaks:
        print(f"\n{'=' * 80}")
        print("WEAK DETAILS (partially covered)")
        print(f"{'=' * 80}")
        for r in weaks[:15]:
            print(f"\n  Q: {r['question'][:100]}")
            print(f"    Source: {r['source_category']} | Detected: {r['detected_category']} | "
                  f"Score: {r['top_score']:.2f}")
            for issue in r["issues"]:
                print(f"    Issue: {issue}")

    # Quality by source category
    cat_grades: dict[str, Counter[str]] = defaultdict(Counter)
    for r in results:
        cat_grades[r["source_category"]][r["grade"]] += 1

    print(f"\n{'=' * 80}")
    print("QUALITY BY SOURCE CATEGORY")
    print(f"{'=' * 80}")
    print(f"\n  {'Category':<12} {'Total':>5} {'GOOD':>5} {'WEAK':>5} {'MISS':>5} {'Good%':>6}")
    print(f"  {'-'*12} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*6}")
    for cat in sorted(cat_grades.keys()):
        cg = cat_grades[cat]
        cat_total = sum(cg.values())
        good_pct = 100 * cg["GOOD"] / max(cat_total, 1)
        print(f"  {cat:<12} {cat_total:>5} {cg['GOOD']:>5} {cg['WEAK']:>5} {cg['MISS']:>5} {good_pct:>5.1f}%")

    # Save JSON report
    report = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_audited": total,
            "sample_size": sample_size if not run_all else total,
            "seed": seed,
            "total_fb_questions_available": len(fb_questions),
            "total_time_seconds": round(total_time, 1),
        },
        "summary": {
            "good": grade_counter["GOOD"],
            "weak": grade_counter["WEAK"],
            "miss": grade_counter["MISS"],
            "good_pct": round(100 * grade_counter["GOOD"] / max(total, 1), 1),
            "weak_pct": round(100 * grade_counter["WEAK"] / max(total, 1), 1),
            "miss_pct": round(100 * grade_counter["MISS"] / max(total, 1), 1),
            "category_mismatches": len(mismatches),
        },
        "per_category": {
            cat: {
                "total": sum(cg.values()),
                "good": cg["GOOD"],
                "weak": cg["WEAK"],
                "miss": cg["MISS"],
            }
            for cat, cg in sorted(cat_grades.items())
        },
        "misses": [
            {
                "question": r["question"],
                "source_category": r["source_category"],
                "detected_category": r["detected_category"],
                "topic": r["topic"],
                "source_freq": r["source_freq"],
                "top_score": r["top_score"],
                "issues": r["issues"],
            }
            for r in misses
        ],
        "weaks": [
            {
                "question": r["question"],
                "source_category": r["source_category"],
                "detected_category": r["detected_category"],
                "topic": r["topic"],
                "source_freq": r["source_freq"],
                "top_score": r["top_score"],
                "issues": r["issues"],
            }
            for r in weaks
        ],
        "category_mismatches": dict(cat_mismatch_counter.most_common()),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nReport saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
