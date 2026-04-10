"""Quality audit of law_knowledge.json and the RAG pipeline.

Run:
    python -m tests.quality_audit              # stats + retriever test (no API key needed)
    python -m tests.quality_audit --rag        # also run full RAG pipeline test (needs ANTHROPIC_API_KEY)
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
import time
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

KNOWLEDGE_PATH = PROJECT_ROOT / "data" / "seeds" / "law_knowledge.json"

# ---------------------------------------------------------------------------
# Test questions with expected answers
# ---------------------------------------------------------------------------

TEST_QUESTIONS: list[dict[str, object]] = [
    {
        "id": 1,
        "question": "Jaki jest podstawowy termin odliczenia VAT?",
        "expected_laws": ["Ustawa o VAT"],
        "expected_articles": ["art. 86"],
        "expected_facts": ["okres rozliczeniowy", "powstani"],
    },
    {
        "id": 2,
        "question": "Ile wynosi okres wypowiedzenia umowy o pracę po 5 latach?",
        "expected_laws": ["Kodeks pracy"],
        "expected_articles": ["art. 36"],
        "expected_facts": ["3 miesi"],
    },
    {
        "id": 3,
        "question": "Kto może stosować stawkę CIT 9%?",
        "expected_laws": ["Ustawa o podatku dochodowym od osób prawnych"],
        "expected_articles": ["art. 19"],
        "expected_facts": ["mał", "2"],
    },
    {
        "id": 4,
        "question": "Kiedy przedawnia się zobowiązanie podatkowe?",
        "expected_laws": ["Ordynacja podatkowa"],
        "expected_articles": ["art. 70"],
        "expected_facts": ["5 lat"],
    },
    {
        "id": 5,
        "question": "Jaki jest termin złożenia sprawozdania finansowego do KRS?",
        "expected_laws": ["Ustawa o rachunkowości"],
        "expected_articles": ["art. 69"],
        "expected_facts": ["15 dni"],
    },
    {
        "id": 6,
        "question": "Czy JDG musi płacić składki ZUS w pierwszych 6 miesiącach?",
        "expected_laws": ["Prawo przedsiębiorców", "Ustawa o systemie ubezpieczeń społecznych"],
        "expected_articles": ["art. 18"],
        "expected_facts": ["ulg", "6 miesi", "zdrowotn"],
    },
    {
        "id": 7,
        "question": "Co to jest GTU_12 w JPK?",
        "expected_laws": ["Rozporządzenie JPK"],
        "expected_articles": [],
        "expected_facts": ["niematerialn", "doradcz"],
    },
    {
        "id": 8,
        "question": "Od kiedy KSeF jest obowiązkowy?",
        "expected_laws": ["KSeF", "Ustawa o VAT"],
        "expected_articles": [],
        "expected_facts": ["202"],
    },
    {
        "id": 9,
        "question": "Ile wynosi zasiłek chorobowy dla JDG?",
        "expected_laws": ["Ustawa o świadczeniach pieniężnych", "Ustawa o systemie ubezpieczeń"],
        "expected_articles": [],
        "expected_facts": ["80%", "90 dni"],
    },
    {
        "id": 10,
        "question": "Jakie są limity umów na czas określony?",
        "expected_laws": ["Kodeks pracy"],
        "expected_articles": ["art. 25"],
        "expected_facts": ["33 miesi", "3 umow"],
    },
    {
        "id": 11,
        "question": "Czy mogę odliczyć VAT od samochodu osobowego?",
        "expected_laws": ["Ustawa o VAT"],
        "expected_articles": ["art. 86a"],
        "expected_facts": ["50%", "ewidencj"],
    },
    {
        "id": 12,
        "question": "Kiedy stosować mechanizm podzielonej płatności (MPP)?",
        "expected_laws": ["Ustawa o VAT"],
        "expected_articles": ["art. 108a"],
        "expected_facts": ["15", "załącznik"],
    },
    {
        "id": 13,
        "question": "Jak rozliczyć stratę podatkową w CIT?",
        "expected_laws": ["Ustawa o podatku dochodowym od osób prawnych"],
        "expected_articles": ["art. 7"],
        "expected_facts": ["5 lat", "50%"],
    },
    {
        "id": 14,
        "question": "Jaki jest termin płatności składek ZUS dla JDG?",
        "expected_laws": ["Ustawa o systemie ubezpieczeń"],
        "expected_articles": [],
        "expected_facts": ["20"],
    },
    {
        "id": 15,
        "question": "Czym różni się amortyzacja bilansowa od podatkowej?",
        "expected_laws": ["Ustawa o rachunkowości", "Ustawa o podatku dochodowym"],
        "expected_articles": [],
        "expected_facts": ["bilansow", "podatkow"],
    },
    {
        "id": 16,
        "question": "Kiedy trzeba robić inwentaryzację?",
        "expected_laws": ["Ustawa o rachunkowości"],
        "expected_articles": ["art. 26"],
        "expected_facts": ["ostatni dzień roku"],
    },
    {
        "id": 17,
        "question": "Jakie są formy opodatkowania JDG?",
        "expected_laws": ["Ustawa o podatku dochodowym"],
        "expected_articles": [],
        "expected_facts": ["skal", "liniow", "ryczałt"],
    },
    {
        "id": 18,
        "question": "Kto musi prowadzić pełne księgi rachunkowe?",
        "expected_laws": ["Ustawa o rachunkowości"],
        "expected_articles": ["art. 2"],
        "expected_facts": ["2"],
    },
    {
        "id": 19,
        "question": "Ile wynosi preferencyjny ZUS?",
        "expected_laws": ["Ustawa o systemie ubezpieczeń"],
        "expected_articles": ["art. 18a"],
        "expected_facts": ["30%", "24 miesi"],
    },
    {
        "id": 20,
        "question": "Jak korygować JPK_V7?",
        "expected_laws": ["Rozporządzenie JPK", "Ordynacja podatkowa"],
        "expected_articles": [],
        "expected_facts": ["korekta", "deklaracj"],
    },
]


# ---------------------------------------------------------------------------
# Part A+B: Knowledge base statistics
# ---------------------------------------------------------------------------


def load_knowledge() -> list[dict[str, str]]:
    return json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8-sig"))


def run_stats(records: list[dict[str, str]]) -> None:
    print("=" * 72)
    print("PART A: KNOWLEDGE BASE STATISTICS")
    print("=" * 72)
    print(f"\nTotal units: {len(records)}")

    # Units per law_name
    law_counter: Counter[str] = Counter()
    for r in records:
        law_counter[r.get("law_name", "(brak)")] += 1

    print(f"\n--- Units per law_name ({len(law_counter)} laws) ---")
    for law, count in law_counter.most_common():
        print(f"  {law}: {count}")

    # Answer length stats per law_name
    print("\n--- Content length stats per law_name ---")
    print(f"  {'Law':<50} {'Count':>5}  {'Min':>5}  {'Avg':>7}  {'Max':>5}")
    print(f"  {'-'*50} {'-'*5}  {'-'*5}  {'-'*7}  {'-'*5}")

    by_law: dict[str, list[int]] = defaultdict(list)
    for r in records:
        length = len(r.get("content", ""))
        by_law[r.get("law_name", "(brak)")].append(length)

    for law in sorted(by_law.keys()):
        lengths = by_law[law]
        avg = sum(lengths) / len(lengths)
        print(f"  {law:<50} {len(lengths):>5}  {min(lengths):>5}  {avg:>7.0f}  {max(lengths):>5}")

    # Empty legal_basis — not applicable, field doesn't exist in schema
    # but check for article_number being empty or "Brak"
    empty_article = [
        r for r in records
        if not r.get("article_number", "").strip()
        or "brak" in r.get("article_number", "").lower()
    ]
    print(f"\n--- Units with empty/missing article_number ---")
    print(f"  Count: {len(empty_article)} / {len(records)} ({100*len(empty_article)/len(records):.1f}%)")

    # Short content (< 50 chars)
    short = [r for r in records if len(r.get("content", "")) < 50]
    print(f"\n--- Units with content < 50 chars (suspicious) ---")
    print(f"  Count: {len(short)}")
    for r in short[:10]:
        print(f"    [{r.get('law_name')}] {r.get('article_number')}: {r.get('content', '')!r}")
    if len(short) > 10:
        print(f"    ... and {len(short) - 10} more")

    # Empty verified_date
    empty_date = [r for r in records if not r.get("verified_date", "").strip()]
    print(f"\n--- Units with empty verified_date ---")
    print(f"  Count: {empty_date.__len__()} / {len(records)} ({100*len(empty_date)/len(records):.1f}%)")

    # Duplicate content
    content_counter: Counter[str] = Counter()
    for r in records:
        content_counter[r.get("content", "").strip()] += 1
    duplicates = {text: count for text, count in content_counter.items() if count > 1}
    total_dup_units = sum(count for count in duplicates.values())
    print(f"\n--- Duplicate content ---")
    print(f"  Unique duplicate texts: {len(duplicates)}")
    print(f"  Total units involved: {total_dup_units}")
    if duplicates:
        print(f"  Top 10 most duplicated:")
        for text, count in sorted(duplicates.items(), key=lambda x: -x[1])[:10]:
            preview = text[:100].replace("\n", " ")
            print(f"    [{count}x] {preview}...")

    # Category distribution
    cat_counter: Counter[str] = Counter()
    for r in records:
        cat_counter[r.get("category", "(brak)")] += 1
    print(f"\n--- Category distribution ({len(cat_counter)} categories) ---")
    for cat, count in cat_counter.most_common():
        print(f"  {cat}: {count}")

    # Units with "Nie mogę odpowiedzieć" or "Brak przepisów"
    negative = [
        r for r in records
        if "nie mogę odpowiedzieć" in r.get("content", "").lower()
        or "nie zawiera przepisów" in r.get("content", "").lower()
        or "brak przepisów" in r.get("article_number", "").lower()
        or "poza zakresem" in r.get("content", "").lower()
    ]
    print(f"\n--- Units with negative/out-of-scope answers ---")
    print(f"  Count: {len(negative)} / {len(records)} ({100*len(negative)/len(records):.1f}%)")
    # Breakdown by law_name
    neg_by_law: Counter[str] = Counter()
    for r in negative:
        neg_by_law[r.get("law_name", "(brak)")] += 1
    for law, count in neg_by_law.most_common():
        print(f"    {law}: {count}")

    print()


# ---------------------------------------------------------------------------
# Part C+D: RAG pipeline test
# ---------------------------------------------------------------------------


def _normalize_lower(text: str) -> str:
    import unicodedata

    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in normalized if not unicodedata.combining(c))


def _check_law_match(chunks_laws: list[str], expected_laws: list[str]) -> bool:
    """Check if any retrieved chunk comes from one of the expected laws."""
    for chunk_law in chunks_laws:
        chunk_norm = _normalize_lower(chunk_law)
        for expected in expected_laws:
            exp_norm = _normalize_lower(expected)
            if exp_norm in chunk_norm or chunk_norm in exp_norm:
                return True
            # Partial match: at least the key word
            key_words = exp_norm.split()
            if len(key_words) >= 2 and all(w in chunk_norm for w in key_words[-2:]):
                return True
    return False


def _check_article_match(answer: str, expected_articles: list[str]) -> bool:
    """Check if any expected article is mentioned in the answer."""
    if not expected_articles:
        return True  # No article requirement
    answer_norm = _normalize_lower(answer)
    for article in expected_articles:
        art_norm = _normalize_lower(article)
        if art_norm in answer_norm:
            return True
    return False


def _check_facts(answer: str, expected_facts: list[str]) -> tuple[int, int]:
    """Return (matched, total) fact count."""
    if not expected_facts:
        return (0, 0)
    answer_norm = _normalize_lower(answer)
    matched = sum(1 for fact in expected_facts if _normalize_lower(fact) in answer_norm)
    return matched, len(expected_facts)


def run_retriever_tests() -> None:
    """Test categorizer + retriever pipeline (no API key needed).

    Evaluates whether the correct chunks are retrieved for each test
    question by checking law names, article numbers, and key facts
    against the *chunk content* (not an LLM-generated answer).
    """
    from core.anonymizer import anonymize_text
    from core.categorizer import categorize_query
    from core.generator import is_low_confidence_retrieval
    from core.retriever import retrieve_chunks

    print("=" * 72)
    print("PART B: RETRIEVER PIPELINE TEST (20 questions)")
    print("=" * 72)

    knowledge_path = str(KNOWLEDGE_PATH)
    results: list[dict[str, object]] = []
    pass_count = 0
    partial_count = 0
    fail_count = 0

    for tq in TEST_QUESTIONS:
        qid = tq["id"]
        question = str(tq["question"])
        expected_laws = list(tq["expected_laws"])  # type: ignore[arg-type]
        expected_articles = list(tq["expected_articles"])  # type: ignore[arg-type]
        expected_facts = list(tq["expected_facts"])  # type: ignore[arg-type]

        print(f"\n--- Q{qid}: {question}")
        sys.stdout.flush()

        redacted = anonymize_text(question)
        category = categorize_query(redacted)
        start = time.time()
        chunks = retrieve_chunks(query=redacted, knowledge_path=knowledge_path, limit=5)
        elapsed = time.time() - start
        low_conf = is_low_confidence_retrieval(chunks)

        chunks_laws = [c.law_name for c in chunks]
        # Combine all chunk content + article numbers for evaluation
        combined_text = " ".join(
            f"{c.law_name} {c.article_number} {c.content}" for c in chunks
        )

        law_ok = _check_law_match(chunks_laws, expected_laws)
        article_ok = _check_article_match(combined_text, expected_articles)
        facts_matched, facts_total = _check_facts(combined_text, expected_facts)
        facts_ok = facts_total == 0 or facts_matched >= max(1, facts_total // 2)

        notes_parts: list[str] = []
        if low_conf:
            notes_parts.append("LOW CONFIDENCE (all BM25 scores < 2.0)")

        if law_ok and article_ok and facts_ok and facts_matched == facts_total:
            grade = "PASS"
            pass_count += 1
        elif law_ok and (article_ok or facts_ok):
            grade = "PARTIAL"
            partial_count += 1
        else:
            grade = "FAIL"
            fail_count += 1

        if not law_ok:
            notes_parts.append(f"wrong law (got: {chunks_laws[:3]})")
        if not article_ok:
            notes_parts.append(f"missing article {expected_articles}")
        if facts_total > 0 and facts_matched < facts_total:
            missing = [
                f for f in expected_facts
                if _normalize_lower(f) not in _normalize_lower(combined_text)
            ]
            notes_parts.append(f"facts {facts_matched}/{facts_total} missing={missing}")

        notes = "; ".join(notes_parts) if notes_parts else "OK"
        scores = [round(c.score, 2) for c in chunks]

        print(f"  Category: {category}")
        print(f"  Retrieved laws: {chunks_laws}")
        print(f"  Articles: {[c.article_number for c in chunks]}")
        print(f"  Scores: {scores}  Low-conf: {low_conf}")
        print(f"  Law: {'YES' if law_ok else 'NO'} | Article: {'YES' if article_ok else 'NO'} | Facts: {facts_matched}/{facts_total}")
        print(f"  Grade: {grade} ({elapsed:.2f}s)")
        print(f"  Notes: {notes}")
        for i, c in enumerate(chunks):
            preview = c.content[:120].replace("\n", " ")
            print(f"    chunk[{i}] [{c.law_name} {c.article_number}] (score={c.score:.2f}): {preview}...")
        sys.stdout.flush()

        results.append({
            "id": qid,
            "question": question,
            "category": category,
            "grade": grade,
            "notes": notes,
            "chunks_laws": chunks_laws,
            "scores": scores,
            "low_conf": low_conf,
            "elapsed": round(elapsed, 3),
            "chunk_details": [
                {"law": c.law_name, "article": c.article_number, "score": round(c.score, 2),
                 "content": c.content[:300]}
                for c in chunks
            ],
        })

    # Summary table
    total = len(TEST_QUESTIONS)
    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)

    print(f"\n{'#':>3} | {'Question':<50} | {'Cat':<15} | {'Grade':<7} | Notes")
    print(f"{'-'*3}-+-{'-'*50}-+-{'-'*15}-+-{'-'*7}-+-{'-'*40}")
    for r in results:
        q_short = str(r["question"])[:48]
        cat = str(r.get("category", "?"))[:15]
        print(f"{r['id']:>3} | {q_short:<50} | {cat:<15} | {r['grade']:<7} | {str(r['notes'])[:70]}")

    print(f"\n  PASS:    {pass_count}/{total} ({100*pass_count/total:.0f}%)")
    print(f"  PARTIAL: {partial_count}/{total} ({100*partial_count/total:.0f}%)")
    print(f"  FAIL:    {fail_count}/{total} ({100*fail_count/total:.0f}%)")

    # Detail for FAILs
    fails = [r for r in results if r["grade"] == "FAIL"]
    if fails:
        print(f"\n{'=' * 72}")
        print("FAILED QUESTIONS — CHUNK DETAILS FOR REVIEW")
        print("=" * 72)
        for r in fails:
            print(f"\n--- Q{r['id']}: {r['question']}")
            print(f"  Category: {r.get('category', '?')}")
            print(f"  Notes: {r['notes']}")
            for cd in r.get("chunk_details", []):  # type: ignore[union-attr]
                print(f"  [{cd['law']} {cd['article']}] score={cd['score']}")  # type: ignore[index]
                for line in textwrap.wrap(str(cd["content"]), width=72):  # type: ignore[index]
                    print(f"    {line}")

    # Detail for PARTIALs
    partials = [r for r in results if r["grade"] == "PARTIAL"]
    if partials:
        print(f"\n{'=' * 72}")
        print("PARTIAL QUESTIONS — CHUNK DETAILS FOR REVIEW")
        print("=" * 72)
        for r in partials:
            print(f"\n--- Q{r['id']}: {r['question']}")
            print(f"  Category: {r.get('category', '?')}")
            print(f"  Notes: {r['notes']}")
            for cd in r.get("chunk_details", []):  # type: ignore[union-attr]
                print(f"  [{cd['law']} {cd['article']}] score={cd['score']}")  # type: ignore[index]
                for line in textwrap.wrap(str(cd["content"]), width=72):  # type: ignore[index]
                    print(f"    {line}")


def run_rag_tests() -> None:
    """Full RAG pipeline test including LLM generation (requires ANTHROPIC_API_KEY)."""
    from config.settings import get_settings
    from core.rag import answer_query

    print("=" * 72)
    print("PART C: FULL RAG PIPELINE TEST (20 questions, requires API key)")
    print("=" * 72)

    try:
        settings = get_settings()
    except Exception as exc:
        print(f"\nERROR: Cannot load settings: {exc}")
        print("Make sure .env is configured with ANTHROPIC_API_KEY.")
        return

    results: list[dict[str, object]] = []
    pass_count = 0
    partial_count = 0
    fail_count = 0

    for tq in TEST_QUESTIONS:
        qid = tq["id"]
        question = str(tq["question"])
        expected_laws = list(tq["expected_laws"])  # type: ignore[arg-type]
        expected_articles = list(tq["expected_articles"])  # type: ignore[arg-type]
        expected_facts = list(tq["expected_facts"])  # type: ignore[arg-type]

        print(f"\n--- Q{qid}: {question}")
        sys.stdout.flush()

        try:
            start = time.time()
            rag_result = answer_query(
                query=question,
                knowledge_path=settings.law_knowledge_path,
                system_prompt=settings.system_prompt,
                api_key=settings.anthropic_api_key,
            )
            elapsed = time.time() - start
        except Exception as exc:
            print(f"  ERROR: {exc}")
            results.append({
                "id": qid,
                "question": question,
                "grade": "FAIL",
                "notes": f"Exception: {exc}",
                "answer": "",
            })
            fail_count += 1
            continue

        answer = rag_result.answer
        chunks_laws = [c.law_name for c in rag_result.chunks]
        category = rag_result.category

        law_ok = _check_law_match(chunks_laws, expected_laws)
        article_ok = _check_article_match(answer, expected_articles)
        facts_matched, facts_total = _check_facts(answer, expected_facts)
        facts_ok = facts_total == 0 or facts_matched >= max(1, facts_total // 2)

        notes_parts: list[str] = []
        if law_ok and article_ok and facts_ok and facts_matched == facts_total:
            grade = "PASS"
            pass_count += 1
        elif law_ok and (article_ok or facts_ok):
            grade = "PARTIAL"
            partial_count += 1
        else:
            grade = "FAIL"
            fail_count += 1

        if not law_ok:
            notes_parts.append(f"wrong law (got: {chunks_laws[:3]})")
        if not article_ok:
            notes_parts.append(f"missing article {expected_articles}")
        if facts_total > 0 and facts_matched < facts_total:
            notes_parts.append(f"facts {facts_matched}/{facts_total}")

        notes = "; ".join(notes_parts) if notes_parts else "OK"

        print(f"  Category: {category}")
        print(f"  Retrieved laws: {chunks_laws}")
        print(f"  Chunks: {len(rag_result.chunks)}, Grounded: {rag_result.audit.get('grounded')}")
        print(f"  Law: {'YES' if law_ok else 'NO'} | Article: {'YES' if article_ok else 'NO'} | Facts: {facts_matched}/{facts_total}")
        print(f"  Grade: {grade} | Time: {elapsed:.1f}s")
        print(f"  Notes: {notes}")
        answer_preview = answer[:200].replace("\n", " ")
        print(f"  Answer preview: {answer_preview}...")
        sys.stdout.flush()

        results.append({
            "id": qid,
            "question": question,
            "category": category,
            "grade": grade,
            "notes": notes,
            "answer": answer,
            "chunks_laws": chunks_laws,
            "elapsed": round(elapsed, 1),
        })

        time.sleep(0.5)

    total = len(TEST_QUESTIONS)
    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)

    print(f"\n{'#':>3} | {'Question':<50} | {'Cat':<12} | {'Grade':<7} | Notes")
    print(f"{'-'*3}-+-{'-'*50}-+-{'-'*12}-+-{'-'*7}-+-{'-'*30}")
    for r in results:
        q_short = str(r["question"])[:48]
        cat = str(r.get("category", "?"))[:12]
        print(f"{r['id']:>3} | {q_short:<50} | {cat:<12} | {r['grade']:<7} | {str(r['notes'])[:60]}")

    print(f"\n  PASS:    {pass_count}/{total} ({100*pass_count/total:.0f}%)")
    print(f"  PARTIAL: {partial_count}/{total} ({100*partial_count/total:.0f}%)")
    print(f"  FAIL:    {fail_count}/{total} ({100*fail_count/total:.0f}%)")

    fails = [r for r in results if r["grade"] == "FAIL"]
    if fails:
        print(f"\n{'=' * 72}")
        print("FAILED QUESTIONS — FULL ANSWERS FOR REVIEW")
        print("=" * 72)
        for r in fails:
            print(f"\n--- Q{r['id']}: {r['question']}")
            print(f"  Category: {r.get('category', '?')}")
            print(f"  Retrieved laws: {r.get('chunks_laws', [])}")
            print(f"  Notes: {r['notes']}")
            print(f"  Full answer:")
            for line in textwrap.wrap(str(r["answer"]), width=72):
                print(f"    {line}")

    partials = [r for r in results if r["grade"] == "PARTIAL"]
    if partials:
        print(f"\n{'=' * 72}")
        print("PARTIAL QUESTIONS — FULL ANSWERS FOR REVIEW")
        print("=" * 72)
        for r in partials:
            print(f"\n--- Q{r['id']}: {r['question']}")
            print(f"  Category: {r.get('category', '?')}")
            print(f"  Retrieved laws: {r.get('chunks_laws', [])}")
            print(f"  Notes: {r['notes']}")
            print(f"  Full answer:")
            for line in textwrap.wrap(str(r["answer"]), width=72):
                print(f"    {line}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    records = load_knowledge()
    run_stats(records)
    run_retriever_tests()

    if "--rag" in sys.argv:
        run_rag_tests()
    else:
        print("\nTip: Run with --rag to also run full RAG pipeline test (requires ANTHROPIC_API_KEY).")


if __name__ == "__main__":
    main()
