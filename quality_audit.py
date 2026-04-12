from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path

from analysis.run_eval import build_eval_report, write_eval_report
from core.categorizer import categorize_query
from core.retriever import retrieve_chunks


KB_PATH = Path("data/seeds/law_knowledge.json")
OUTPUT_PATH = Path("analysis/quality_audit_report.json")
EVAL_MIN_ACCURACY = float(os.getenv("AKTUO_EVAL_MIN_ACCURACY", "0.80"))

QUESTIONS = [
    {"query": "Termin złożenia JPK_V7?", "expected_laws": ["Ustawa o VAT", "Rozporządzenie JPK_V7"]},
    {"query": "Estoński CIT — kto może?", "expected_laws": ["Ustawa o podatku dochodowym od osób prawnych"]},
    {"query": "Okres wypowiedzenia umowy", "expected_laws": ["Kodeks pracy"]},
    {"query": "Kiedy składa się CIT-8?", "expected_laws": ["Ustawa o podatku dochodowym od osób prawnych"]},
    {"query": "Kiedy przedawnia się zobowiązanie podatkowe?", "expected_laws": ["Ordynacja podatkowa"]},
    {"query": "Kiedy składa się PIT-11?", "expected_laws": ["Ustawa o podatku dochodowym od osób fizycznych"]},
    {"query": "Jak działa ulga rehabilitacyjna na leki?", "expected_laws": ["Ustawa o podatku dochodowym od osób fizycznych"]},
    {"query": "Jak działa ulga na dziecko?", "expected_laws": ["Ustawa o podatku dochodowym od osób fizycznych"]},
    {"query": "Jakie są warunki 100% odliczenia VAT od samochodu?", "expected_laws": ["Ustawa o VAT"]},
    {"query": "Kiedy wystawia się fakturę korygującą?", "expected_laws": ["Ustawa o VAT"]},
    {"query": "Jakie są terminy wpłaty zaliczek CIT?", "expected_laws": ["Ustawa o podatku dochodowym od osób prawnych"]},
    {"query": "Co daje certyfikat rezydencji przy WHT?", "expected_laws": ["Ustawa o podatku dochodowym od osób prawnych"]},
    {"query": "Kiedy składa się sprawozdanie finansowe do KRS?", "expected_laws": ["Ustawa o rachunkowości"]},
    {"query": "Na czym polega inwentaryzacja?", "expected_laws": ["Ustawa o rachunkowości"]},
    {"query": "Kto podlega obowiązkowym ubezpieczeniom społecznym?", "expected_laws": ["Ustawa o systemie ubezpieczeń społecznych"]},
    {"query": "Na czym polega zbieg tytułów ZUS?", "expected_laws": ["Ustawa o systemie ubezpieczeń społecznych"]},
    {"query": "Kiedy trzeba pobrać WHT od usług reklamowych?", "expected_laws": ["Ustawa o podatku dochodowym od osób prawnych"]},
    {"query": "Jakie są warunki rozłożenia zaległości podatkowej na raty?", "expected_laws": ["Ordynacja podatkowa"]},
    {"query": "Czym jest JPK_V7K?", "expected_laws": ["Rozporządzenie JPK_V7", "Ustawa o VAT"]},
    {"query": "Kiedy składa się roczną deklarację PIT-4R?", "expected_laws": ["Ustawa o podatku dochodowym od osób fizycznych"]},
]

ARTICLE_FILES = {
    "Ustawa o VAT": Path("kb-pipeline/output/articles.json"),
    "Ustawa o podatku dochodowym od osób fizycznych": Path("kb-pipeline/output/articles_pit.json"),
    "Ustawa o podatku dochodowym od osób prawnych": Path("kb-pipeline/output/articles_cit.json"),
    "Ordynacja podatkowa": Path("kb-pipeline/output/articles_ordynacja.json"),
    "Ustawa o rachunkowości": Path("kb-pipeline/output/articles_rachunkowosc.json"),
    "Ustawa o systemie ubezpieczeń społecznych": Path("kb-pipeline/output/articles_zus.json"),
    "Kodeks pracy": Path("kb-pipeline/output/articles_kodeks_pracy.json"),
    "Rozporządzenie JPK_V7": Path("kb-pipeline/output/articles_jpk.json"),
}


def normalize_law_name(name: str) -> str:
    if "fizycznych" in name:
        return "Ustawa o podatku dochodowym od osób fizycznych"
    if "prawnych" in name:
        return "Ustawa o podatku dochodowym od osób prawnych"
    if "Ustawa o VAT" in name:
        return "Ustawa o VAT"
    if "Kodeks pracy" in name:
        return "Kodeks pracy"
    if "Ordynacja podatkowa" in name:
        return "Ordynacja podatkowa"
    if "rachunkowości" in name:
        return "Ustawa o rachunkowości"
    if "ubezpieczeń społecznych" in name:
        return "Ustawa o systemie ubezpieczeń społecznych"
    if "JPK_V7" in name:
        return "Rozporządzenie JPK_V7"
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


def main() -> None:
    article_texts = load_article_texts()
    summary: Counter[str] = Counter()
    results = []

    for item in QUESTIONS:
        query = item["query"]
        expected_laws = set(item["expected_laws"])
        category = categorize_query(query)
        chunks = retrieve_chunks(query, knowledge_path=KB_PATH, limit=5)
        reviews = []
        for chunk in chunks[:3]:
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

        if reviews and reviews[0]["normalized_law_name"] in expected_laws and reviews[0]["source_hits"]:
            status = "PASS"
        elif any(review["normalized_law_name"] in expected_laws and review["source_hits"] for review in reviews):
            status = "PARTIAL"
        else:
            status = "FAIL"

        summary[status] += 1
        results.append(
            {
                "query": query,
                "expected_laws": item["expected_laws"],
                "category": category,
                "status": status,
                "top_3": reviews,
            }
        )

    report = {"summary": dict(summary), "questions": results}
    OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))

    eval_report = build_eval_report(knowledge_path=KB_PATH)
    write_eval_report(eval_report)
    behavior_accuracy = float(eval_report["overall"]["behavior_accuracy"])
    if behavior_accuracy < EVAL_MIN_ACCURACY:
        raise SystemExit(
            f"Golden eval accuracy {behavior_accuracy:.2%} is below required threshold {EVAL_MIN_ACCURACY:.0%}."
        )


if __name__ == "__main__":
    main()
