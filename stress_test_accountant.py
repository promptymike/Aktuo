from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from core.categorizer import categorize_query
from core.retriever import retrieve_chunks


FB_PATH = Path("fb_pipeline/dedup_questions_output_v3.json")
KB_PATH = Path("data/seeds/law_knowledge.json")
OUTPUT_PATH = Path("analysis/stress_test_accountant_report.json")

ARTICLE_FILES = {
    "Ustawa o VAT": Path("kb-pipeline/output/articles.json"),
    "Ustawa o podatku dochodowym od osób fizycznych": Path("kb-pipeline/output/articles_pit.json"),
    "Ustawa o podatku dochodowym od osób prawnych": Path("kb-pipeline/output/articles_cit.json"),
}

EXPECTED_LAWS = {
    "vat": {"Ustawa o VAT"},
    "pit": {"Ustawa o podatku dochodowym od osób fizycznych"},
    "cit": {"Ustawa o podatku dochodowym od osób prawnych"},
}


def normalize_law_name(name: str) -> str:
    if "fizycznych" in name:
        return "Ustawa o podatku dochodowym od osób fizycznych"
    if "prawnych" in name:
        return "Ustawa o podatku dochodowym od osób prawnych"
    if "Ustawa o VAT" in name:
        return "Ustawa o VAT"
    return name


def split_article_numbers(article_number: str) -> list[str]:
    normalized = (
        article_number.lower()
        .replace("art.", " ")
        .replace("§", " ")
        .replace("Â§", " ")
        .replace("ust.", " ")
        .replace("pkt", " ")
        .strip()
    )
    values = re.findall(r"\d+[a-z]?", normalized)
    return list(dict.fromkeys(values))


def load_article_texts() -> dict[str, dict[str, str]]:
    article_texts: dict[str, dict[str, str]] = {}
    for law_name, path in ARTICLE_FILES.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        article_texts[law_name] = {
            article["article_number"]: article.get("raw_text", "")
            for article in data.get("articles", [])
        }
    return article_texts


def load_questions() -> list[dict[str, object]]:
    fb_data = json.loads(FB_PATH.read_text(encoding="utf-8-sig"))["questions"]
    grouped: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for item in fb_data:
        grouped[str(item.get("cat", ""))].append(item)
    selected: list[dict[str, object]] = []
    for category in ("vat", "pit", "cit"):
        selected.extend(
            sorted(grouped[category], key=lambda entry: (-int(entry.get("freq", 0)), str(entry.get("q", ""))))[:10]
        )
    return selected


def main() -> None:
    article_texts = load_article_texts()
    questions = load_questions()
    summary: Counter[str] = Counter()
    results = []

    for item in questions:
        query = str(item["q"])
        source_cat = str(item["cat"])
        chunks = retrieve_chunks(query, knowledge_path=KB_PATH, limit=5)[:3]
        reviews = []
        for chunk in chunks:
            normalized_law = normalize_law_name(chunk.law_name)
            source_hits = []
            for article_id in split_article_numbers(chunk.article_number):
                source_text = article_texts.get(normalized_law, {}).get(article_id)
                if source_text:
                    source_hits.append(
                        {
                            "article": article_id,
                            "source_excerpt": source_text[:220].replace("\n", " "),
                        }
                    )
            reviews.append(
                {
                    "law_name": chunk.law_name,
                    "normalized_law_name": normalized_law,
                    "article_number": chunk.article_number,
                    "score": round(chunk.score, 4),
                    "content_excerpt": chunk.content[:220].replace("\n", " "),
                    "source_hits": source_hits,
                }
            )

        if reviews and reviews[0]["normalized_law_name"] in EXPECTED_LAWS[source_cat] and reviews[0]["source_hits"]:
            status = "PASS"
        elif any(review["normalized_law_name"] in EXPECTED_LAWS[source_cat] and review["source_hits"] for review in reviews):
            status = "PARTIAL"
        else:
            status = "FAIL"

        summary[status] += 1
        results.append(
            {
                "query": query,
                "source_cat": source_cat,
                "freq": int(item.get("freq", 0)),
                "aktuo_category": categorize_query(query),
                "status": status,
                "top_3": reviews,
            }
        )

    report = {"summary": dict(summary), "questions": results}
    OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
