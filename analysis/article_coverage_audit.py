from __future__ import annotations

import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
import re


ROOT = Path(__file__).resolve().parents[1]
KB_PATH = ROOT / "data" / "seeds" / "law_knowledge.json"
OUTPUT_JSON = ROOT / "tests" / "output" / "article_coverage_by_law.json"
OUTPUT_MD = ROOT / "analysis" / "article_coverage_by_law.md"


SOURCE_FILE_BY_LAW = {
    "Ustawa o VAT": ROOT / "kb-pipeline" / "output" / "articles.json",
    "Ustawa o podatku dochodowym od osób fizycznych": ROOT / "kb-pipeline" / "output" / "articles_pit.json",
    "Ustawa o podatku dochodowym od osób prawnych": ROOT / "kb-pipeline" / "output" / "articles_cit.json",
    "Ordynacja podatkowa": ROOT / "kb-pipeline" / "output" / "articles_ordynacja.json",
    "Ustawa o rachunkowości": ROOT / "kb-pipeline" / "output" / "articles_rachunkowosc.json",
    "Kodeks pracy": ROOT / "kb-pipeline" / "output" / "articles_kodeks_pracy.json",
    "Ustawa o systemie ubezpieczeń społecznych": ROOT / "kb-pipeline" / "output" / "articles_zus.json",
    "Rozporządzenie KSeF": ROOT / "kb-pipeline" / "output" / "articles_ksef.json",
    "Rozporządzenie JPK_V7": ROOT / "kb-pipeline" / "output" / "articles_jpk.json",
}


PRIORITY_ARTICLES = {
    "Ustawa o podatku dochodowym od osób fizycznych": [
        "art. 11a",
        "art. 14",
        "art. 19",
        "art. 21",
        "art. 22",
        "art. 26",
        "art. 27",
        "art. 30c",
    ],
    "Ustawa o VAT": [
        "art. 19a",
        "art. 29a",
        "art. 106b",
        "art. 106c",
        "art. 106d",
        "art. 106e",
        "art. 106f",
        "art. 111",
        "art. 113",
    ],
}


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    without_mojibake_markers = without_accents.replace("?", " ")
    collapsed = re.sub(r"\s+", " ", without_mojibake_markers).strip()
    return collapsed.replace("os b", "osob")


def canonicalize_law_name(law_name: str) -> str:
    normalized = _normalize(law_name)
    if "ustawa o vat - ksef terminy wdrozenia" in normalized:
        return "Ustawa o VAT - KSeF terminy wdrożenia"
    if "ustawa o vat - ksef uproszczenia 2026" in normalized:
        return "Ustawa o VAT - KSeF uproszczenia 2026"
    if "ustawa o vat - ksef zwolnienia" in normalized:
        return "Ustawa o VAT - KSeF zwolnienia"
    if "podatku od towarow i uslug" in normalized or normalized == "ustawa o vat":
        return "Ustawa o VAT"
    if "podatku dochodowym od osob fizycznych" in normalized:
        return "Ustawa o podatku dochodowym od osób fizycznych"
    if "podatku dochodowym od osob prawnych" in normalized:
        return "Ustawa o podatku dochodowym od osób prawnych"
    if "ordynacja podatkowa" in normalized:
        return "Ordynacja podatkowa"
    if "rachunkowosci" in normalized:
        return "Ustawa o rachunkowości"
    if "kodeks pracy" in normalized:
        return "Kodeks pracy"
    if "ubezpieczen spolecznych" in normalized:
        return "Ustawa o systemie ubezpieczeń społecznych"
    if "jpk_v7" in normalized or "zakresu danych zawartych w deklaracjach podatkowych" in normalized:
        return "Rozporządzenie JPK_V7"
    if "krajowego systemu e-faktur" in normalized or "rozporzadzenie ksef" in normalized:
        return "Rozporządzenie KSeF"
    return law_name


def article_root(identifier: str) -> str:
    section_match = re.search(r"[§?]\s*\d+[a-z]*", identifier)
    if section_match:
        section = re.sub(r"\s+", " ", section_match.group(0)).strip().replace("?", "§")
        return section.lower()
    normalized = _normalize(identifier)
    art_match = re.search(r"art\.\s*\d+[a-z]*", normalized)
    if art_match:
        return re.sub(r"\s+", " ", art_match.group(0)).strip()
    par_match = re.search(r"§\s*\d+[a-z]*", identifier)
    if par_match:
        return re.sub(r"\s+", " ", par_match.group(0)).strip().lower()
    par_match_normalized = re.search(r"\bpar\.\s*\d+[a-z]*", normalized)
    if par_match_normalized:
        return re.sub(r"\s+", " ", par_match_normalized.group(0)).strip()
    return normalized


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    kb_records = load_json(KB_PATH)
    kb_by_law: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in kb_records:
        kb_by_law[canonicalize_law_name(str(record.get("law_name", "")))].append(record)

    report: dict[str, Any] = {
        "meta": {
            "knowledge_path": str(KB_PATH.relative_to(ROOT)),
            "source_files": {law: str(path.relative_to(ROOT)) for law, path in SOURCE_FILE_BY_LAW.items()},
            "kb_total_records": len(kb_records),
        },
        "laws": {},
        "priority_article_checks": {},
        "kb_only_laws_without_parsed_source": [],
    }

    all_law_names = sorted(kb_by_law.keys())
    for law_name in all_law_names:
        source_path = SOURCE_FILE_BY_LAW.get(law_name)
        law_report: dict[str, Any] = {
            "kb_records": len(kb_by_law[law_name]),
            "kb_unique_article_roots": 0,
            "source_file": str(source_path.relative_to(ROOT)) if source_path else None,
        }
        kb_roots = sorted(
            {
                article_root(str(record.get("article_number", "")))
                for record in kb_by_law[law_name]
                if str(record.get("article_number", "")).strip()
            }
        )
        law_report["kb_unique_article_roots"] = len(kb_roots)

        if source_path and source_path.exists():
            source_data = load_json(source_path)
            active_articles = [
                article for article in source_data.get("articles", []) if not article.get("is_repealed", False)
            ]
            source_roots = sorted(
                {
                    article_root(str(article.get("full_id") or article.get("article_number") or ""))
                    for article in active_articles
                }
            )
            kb_root_set = set(kb_roots)
            source_root_set = set(source_roots)
            covered = sorted(source_root_set & kb_root_set)
            missing = sorted(source_root_set - kb_root_set)
            law_report.update(
                {
                    "source_active_articles": len(source_roots),
                    "covered_article_roots": len(covered),
                    "missing_article_roots": len(missing),
                    "coverage_pct": round((len(covered) / len(source_roots)) * 100, 2) if source_roots else 0.0,
                    "missing_sample": missing[:40],
                    "covered_sample": covered[:20],
                }
            )
        else:
            law_report.update(
                {
                    "source_active_articles": None,
                    "covered_article_roots": None,
                    "missing_article_roots": None,
                    "coverage_pct": None,
                    "missing_sample": [],
                    "covered_sample": [],
                    "note": "No parsed article source mapped for this law.",
                }
            )
            report["kb_only_laws_without_parsed_source"].append(law_name)

        report["laws"][law_name] = law_report

    for law_name, articles in PRIORITY_ARTICLES.items():
        kb_law_records = kb_by_law.get(law_name, [])
        kb_roots = {article_root(str(record.get("article_number", ""))) for record in kb_law_records}
        report["priority_article_checks"][law_name] = []
        for target in articles:
            report["priority_article_checks"][law_name].append(
                {
                    "article": target,
                    "has_kb_unit": article_root(target) in kb_roots,
                }
            )

    return report


def build_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Article Coverage Audit")
    lines.append("")
    lines.append("| Ustawa | Unikalne aktywne artykuły sparsowane | Artykuły z pokryciem w KB | Brakujące | Pokrycie |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")

    for law_name, details in sorted(report["laws"].items()):
        if details["source_active_articles"] is None:
            lines.append(
                f"| {law_name} | n/a | n/a | n/a | n/a |"
            )
            continue
        lines.append(
            f"| {law_name} | {details['source_active_articles']} | {details['covered_article_roots']} | "
            f"{details['missing_article_roots']} | {details['coverage_pct']}% |"
        )

    lines.append("")
    lines.append("## Priorytetowe artykuły do sprawdzenia")
    lines.append("")
    for law_name, checks in report["priority_article_checks"].items():
        lines.append(f"### {law_name}")
        lines.append("")
        for item in checks:
            status = "TAK" if item["has_kb_unit"] else "NIE"
            lines.append(f"- {item['article']}: {status}")
        lines.append("")

    if report["kb_only_laws_without_parsed_source"]:
        lines.append("## Ustawy w KB bez zmapowanego sparsowanego źródła")
        lines.append("")
        for law_name in report["kb_only_laws_without_parsed_source"]:
            lines.append(f"- {law_name}")
        lines.append("")

    lines.append("## Największe luki")
    lines.append("")
    sortable = [
        (law_name, details)
        for law_name, details in report["laws"].items()
        if details["source_active_articles"] is not None
    ]
    sortable.sort(key=lambda item: item[1]["missing_article_roots"], reverse=True)
    for law_name, details in sortable[:10]:
        lines.append(
            f"- {law_name}: brakuje {details['missing_article_roots']} z {details['source_active_articles']} aktywnych artykułów."
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    report = build_report()
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(build_markdown(report) + "\n", encoding="utf-8")
    print(f"saved {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"saved {OUTPUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
