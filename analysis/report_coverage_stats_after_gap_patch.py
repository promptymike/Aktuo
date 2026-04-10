from __future__ import annotations

import json
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.article_coverage_audit import build_report as build_article_report  # noqa: E402
from analysis.article_coverage_audit import canonicalize_law_name, load_json  # noqa: E402
from core.categorizer import categorize_query  # noqa: E402
from core.retriever import retrieve_chunks  # noqa: E402


KB_PATH = ROOT / "data" / "seeds" / "law_knowledge.json"
FB_PATH = ROOT / "fb_pipeline" / "dedup_questions_output_v3.json"

TOP100_JSON = ROOT / "analysis" / "top_100_fb_coverage_audit.json"
TOP100_MD = ROOT / "analysis" / "top_100_fb_coverage_audit.md"
TOP100_TESTS_JSON = ROOT / "tests" / "output" / "top100_coverage.json"

REPORT_JSON = ROOT / "tests" / "output" / "coverage_stats_after_gap_patch.json"
REPORT_MD = ROOT / "analysis" / "coverage_stats_after_gap_patch.md"


EXPECTED_LAW_BY_FB_CATEGORY = {
    "vat": ("ustawa o vat",),
    "pit": ("ustawa o podatku dochodowym od osób fizycznych",),
    "cit": ("ustawa o podatku dochodowym od osób prawnych",),
    "ksef": ("ksef", "ustawa o vat - ksef", "ustawa o vat"),
    "jpk": ("rozporządzenie jpk_v7", "ustawa o vat"),
    "rachunkowosc": ("ustawa o rachunkowości",),
    "kadry": ("kodeks pracy",),
    "zus": ("ustawa o systemie ubezpieczeń społecznych",),
    "ordynacja": ("ordynacja podatkowa",),
}


def normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(character for character in normalized if not unicodedata.combining(character))


def preview(text: str, limit: int = 160) -> str:
    compact = " ".join(str(text).split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def law_matches(source_category: str, law_name: str) -> bool:
    aliases = EXPECTED_LAW_BY_FB_CATEGORY.get(source_category)
    if not aliases:
        return False
    normalized_law_name = normalize(law_name)
    return any(normalize(alias) in normalized_law_name for alias in aliases)


def classify_top100_item(source_category: str, chunks: list[object]) -> tuple[str, str]:
    if not chunks:
        return "GAP", "Brak chunków."

    top_chunk = chunks[0]
    top_score = float(top_chunk.score)

    if source_category in EXPECTED_LAW_BY_FB_CATEGORY:
        if top_score > 5.0 and law_matches(source_category, top_chunk.law_name):
            return "COVERED", "Top chunk jest z właściwej ustawy i ma mocny score."
        if top_score >= 2.0 and any(law_matches(source_category, chunk.law_name) for chunk in chunks[:3]):
            return "WEAK", "W top 3 jest właściwa ustawa, ale match nie jest jeszcze dość mocny lub precyzyjny."
        return "GAP", "Brak mocnego trafienia we właściwą ustawę."

    if top_score >= 5.0:
        return "WEAK", "Kategoria źródłowa nie mapuje się jednoznacznie do ustawy, ale retriever zwrócił sensowny wynik."
    return "GAP", "Kategoria źródłowa nie ma dziś jednoznacznej podstawy w obecnej bazie."


def build_top100_report() -> dict[str, Any]:
    payload = load_json(FB_PATH)
    questions = sorted(payload["questions"], key=lambda item: int(item.get("freq", 0)), reverse=True)[:100]

    items: list[dict[str, Any]] = []
    summary = Counter()
    per_category: dict[str, Counter[str]] = defaultdict(Counter)

    for raw in questions:
        query = str(raw.get("q", "")).strip()
        source_category = str(raw.get("cat", "")).strip()
        freq = int(raw.get("freq", 0))
        aktuo_category = categorize_query(query)
        chunks = retrieve_chunks(query, KB_PATH, limit=3)
        verdict, reason = classify_top100_item(source_category, chunks)
        summary[verdict] += 1
        per_category[source_category][verdict] += 1
        items.append(
            {
                "freq": freq,
                "source_category": source_category,
                "aktuo_category": aktuo_category,
                "query": query,
                "verdict": verdict,
                "reason": reason,
                "top_score": round(float(chunks[0].score), 4) if chunks else 0.0,
                "chunks": [
                    {
                        "law_name": chunk.law_name,
                        "article_number": chunk.article_number,
                        "category": chunk.category,
                        "score": round(float(chunk.score), 4),
                        "preview": preview(chunk.content),
                    }
                    for chunk in chunks
                ],
            }
        )

    report = {
        "meta": {
            "source_file": str(FB_PATH.relative_to(ROOT)),
            "knowledge_file": str(KB_PATH.relative_to(ROOT)),
            "total_analyzed": len(items),
            "summary": {
                "COVERED": summary["COVERED"],
                "WEAK": summary["WEAK"],
                "GAP": summary["GAP"],
            },
            "summary_pct": {
                "COVERED": round((summary["COVERED"] / len(items)) * 100, 2) if items else 0.0,
                "WEAK": round((summary["WEAK"] / len(items)) * 100, 2) if items else 0.0,
                "GAP": round((summary["GAP"] / len(items)) * 100, 2) if items else 0.0,
            },
        },
        "per_category": {
            category: {
                "covered": counts["COVERED"],
                "weak": counts["WEAK"],
                "gap": counts["GAP"],
            }
            for category, counts in sorted(per_category.items())
        },
        "gap_questions": [item for item in items if item["verdict"] == "GAP"],
        "weak_questions": [item for item in items if item["verdict"] == "WEAK"],
        "all_items": items,
    }
    return report


def write_top100_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Audyt pokrycia top 100 pytań z Facebooka",
        "",
        "## Podsumowanie",
        "",
        f"- Łącznie przeanalizowanych pytań: `{report['meta']['total_analyzed']}`",
        f"- `COVERED`: `{report['meta']['summary']['COVERED']}` ({report['meta']['summary_pct']['COVERED']}%)",
        f"- `WEAK`: `{report['meta']['summary']['WEAK']}` ({report['meta']['summary_pct']['WEAK']}%)",
        f"- `GAP`: `{report['meta']['summary']['GAP']}` ({report['meta']['summary_pct']['GAP']}%)",
        "",
        "## Rozkład per kategoria",
        "",
        "| Kategoria | COVERED | WEAK | GAP |",
        "| --- | ---: | ---: | ---: |",
    ]

    for category, counts in report["per_category"].items():
        lines.append(f"| `{category}` | `{counts['covered']}` | `{counts['weak']}` | `{counts['gap']}` |")

    lines.extend(
        [
            "",
            "## Pytania GAP",
            "",
            "| Freq | Kategoria źródłowa | Kategoria Aktuo | Pytanie | Top score | Top chunk |",
            "| ---: | --- | --- | --- | ---: | --- |",
        ]
    )
    for item in report["gap_questions"]:
        top_chunk = item["chunks"][0] if item["chunks"] else {}
        top_label = f"{top_chunk.get('law_name', 'brak')} | {top_chunk.get('article_number', 'brak')}"
        lines.append(
            f"| `{item['freq']}` | `{item['source_category']}` | `{item['aktuo_category']}` | "
            f"{item['query']} | `{item['top_score']}` | {top_label} |"
        )

    lines.extend(
        [
            "",
            "## Pytania WEAK",
            "",
            "| Freq | Kategoria źródłowa | Kategoria Aktuo | Pytanie | Top chunk | Top score | Preview |",
            "| ---: | --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for item in report["weak_questions"]:
        top_chunk = item["chunks"][0] if item["chunks"] else {}
        top_label = f"{top_chunk.get('law_name', 'brak')} | {top_chunk.get('article_number', 'brak')}"
        lines.append(
            f"| `{item['freq']}` | `{item['source_category']}` | `{item['aktuo_category']}` | "
            f"{item['query']} | {top_label} | `{item['top_score']}` | {top_chunk.get('preview', '')} |"
        )

    TOP100_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_combined_report() -> dict[str, Any]:
    kb_records = load_json(KB_PATH)
    per_law_counter = Counter(canonicalize_law_name(str(record.get("law_name", ""))) for record in kb_records)
    article_report = build_article_report()
    top100_report = build_top100_report()
    return {
        "meta": {
            "knowledge_path": str(KB_PATH.relative_to(ROOT)),
            "total_kb_records": len(kb_records),
        },
        "kb_per_law": dict(sorted(per_law_counter.items())),
        "article_coverage": article_report,
        "top100_coverage": {
            "summary": top100_report["meta"]["summary"],
            "summary_pct": top100_report["meta"]["summary_pct"],
            "per_category": top100_report["per_category"],
        },
    }


def write_combined_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Coverage Stats After Systematic Gap Patching",
        "",
        f"- Łączna liczba unitów w KB: `{report['meta']['total_kb_records']}`",
        "",
        "## KB per ustawa",
        "",
        "| Ustawa | Unity |",
        "| --- | ---: |",
    ]
    for law_name, count in report["kb_per_law"].items():
        lines.append(f"| `{law_name}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Pokrycie artykułów",
            "",
            "| Ustawa | Aktywne artykuły sparsowane | Pokryte w KB | Brakujące | Pokrycie |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for law_name, details in sorted(report["article_coverage"]["laws"].items()):
        if details["source_active_articles"] is None:
            lines.append(f"| `{law_name}` | `n/a` | `n/a` | `n/a` | `n/a` |")
            continue
        lines.append(
            f"| `{law_name}` | `{details['source_active_articles']}` | `{details['covered_article_roots']}` | "
            f"`{details['missing_article_roots']}` | `{details['coverage_pct']}%` |"
        )

    top100 = report["top100_coverage"]
    lines.extend(
        [
            "",
            "## Top 100 pytań FB",
            "",
            f"- `COVERED`: `{top100['summary']['COVERED']}` ({top100['summary_pct']['COVERED']}%)",
            f"- `WEAK`: `{top100['summary']['WEAK']}` ({top100['summary_pct']['WEAK']}%)",
            f"- `GAP`: `{top100['summary']['GAP']}` ({top100['summary_pct']['GAP']}%)",
            "",
        ]
    )

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    top100_report = build_top100_report()
    TOP100_JSON.write_text(json.dumps(top100_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    TOP100_TESTS_JSON.write_text(json.dumps(top100_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_top100_markdown(top100_report)

    combined_report = build_combined_report()
    REPORT_JSON.write_text(json.dumps(combined_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_combined_markdown(combined_report)

    print(json.dumps(combined_report["meta"], ensure_ascii=False, indent=2))
    print(json.dumps(top100_report["meta"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
