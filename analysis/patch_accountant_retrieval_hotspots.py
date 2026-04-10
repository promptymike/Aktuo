from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.add_missing_articles_from_sources import clean_article_text, clip_text  # noqa: E402
from analysis.article_coverage_audit import KB_PATH, load_json  # noqa: E402


OUTPUT_JSON = ROOT / "tests" / "output" / "accountant_retrieval_hotspot_patch.json"


def load_source_article(path: Path, target_prefix: str) -> dict[str, Any]:
    payload = load_json(path)
    for article in payload.get("articles", []):
        if str(article.get("full_id", "")).startswith(target_prefix):
            return article
    raise KeyError(f"Article {target_prefix} not found in {path}")


def extract_between(text: str, start_pattern: str, end_pattern: str | None = None) -> str:
    start_match = re.search(start_pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if not start_match:
        return text
    segment = text[start_match.start() :]
    if end_pattern:
        end_match = re.search(end_pattern, segment, flags=re.IGNORECASE | re.DOTALL)
        if end_match:
            segment = segment[: end_match.start()]
    return segment


def extract_between_markers(text: str, start_marker: str, end_marker: str, *, after: str | None = None) -> str:
    search_from = 0
    if after:
        anchor_index = text.find(after)
        if anchor_index != -1:
            search_from = anchor_index + len(after)

    start_index = text.find(start_marker, search_from)
    if start_index == -1:
        raise ValueError(f"Marker {start_marker!r} not found after {after!r}")

    end_index = text.find(end_marker, start_index + len(start_marker))
    if end_index == -1:
        end_index = len(text)

    return text[start_index:end_index]


def build_targeted_records() -> list[dict[str, Any]]:
    pit_path = ROOT / "kb-pipeline" / "output" / "articles_pit.json"
    vat_path = ROOT / "kb-pipeline" / "output" / "articles.json"

    pit_11a = load_source_article(pit_path, "art. 11a")
    pit_14 = load_source_article(pit_path, "art. 14")
    pit_21 = load_source_article(pit_path, "art. 21")
    vat_19a = load_source_article(vat_path, "art. 19a")
    vat_111 = load_source_article(vat_path, "art. 111")
    vat_106na = load_source_article(vat_path, "art. 106na")

    pit_14_text = extract_between(str(pit_14.get("raw_text", "")), r"1c\.", r"\n?1d\.|\n?1e\.")
    pit_21_text = extract_between_markers(
        str(pit_21.get("raw_text", "")),
        "154)",
        "155)",
        after="153)",
    )
    vat_19a_text = extract_between(str(vat_19a.get("raw_text", "")), r"1\.", r"\n?1a\.")
    vat_111_text = extract_between(str(vat_111.get("raw_text", "")), r"1\.", r"\n?2\.")
    vat_106na_text = extract_between(str(vat_106na.get("raw_text", "")), r"1\.", r"\n?5\.")

    return [
        {
            "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
            "article_number": "art. 21 ust. 1 pkt 154",
            "category": "pit",
            "verified_date": "",
            "question_intent": "Ulga dla seniora - czy przysługuje proporcjonalnie czy za cały rok",
            "content": clip_text(clean_article_text(pit_21_text, "art. 21 ust. 1 pkt 154"), 600),
            "source": "accountant_retrieval_hotspot_patch",
        },
        {
            "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
            "article_number": "art. 11a ust. 1",
            "category": "pit",
            "verified_date": "",
            "question_intent": "Przeliczenie wynagrodzenia w euro na PLN - jaki kurs NBP zastosować",
            "content": clip_text(clean_article_text(str(pit_11a.get("raw_text", "")), "art. 11a ust. 1"), 600),
            "source": "accountant_retrieval_hotspot_patch",
        },
        {
            "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
            "article_number": "art. 14 ust. 1c",
            "category": "pit",
            "verified_date": "",
            "question_intent": "Obowiązek podatkowy PIT i VAT - data wykonania vs data faktury (część PIT)",
            "content": clip_text(clean_article_text(pit_14_text, "art. 14 ust. 1c"), 600),
            "source": "accountant_retrieval_hotspot_patch",
        },
        {
            "law_name": "Ustawa o VAT",
            "article_number": "art. 19a ust. 1",
            "category": "vat",
            "verified_date": "",
            "question_intent": "Obowiązek podatkowy PIT i VAT - data wykonania vs data faktury (część VAT)",
            "content": clip_text(clean_article_text(vat_19a_text, "art. 19a ust. 1"), 600),
            "source": "accountant_retrieval_hotspot_patch",
        },
        {
            "law_name": "Ustawa o VAT",
            "article_number": "art. 111 ust. 1",
            "category": "vat",
            "verified_date": "",
            "question_intent": "Sprzedaż bezpośrednia rolnik - zwolnienie z kasy fiskalnej i obowiązek ewidencji",
            "content": clip_text(clean_article_text(vat_111_text, "art. 111 ust. 1"), 600),
            "source": "accountant_retrieval_hotspot_patch",
        },
        {
            "law_name": "Ustawa o VAT",
            "article_number": "art. 106na ust. 1 i 3",
            "category": "ksef",
            "verified_date": "",
            "question_intent": "Jak księgować faktury z Bioestry po zmianie w KSeF - kiedy faktura jest wystawiona i otrzymana",
            "content": clip_text(clean_article_text(vat_106na_text, "art. 106na ust. 1 i 3"), 600),
            "source": "accountant_retrieval_hotspot_patch",
        },
    ]


def should_remove(record: dict[str, Any]) -> bool:
    law_name = str(record.get("law_name", ""))
    article_number = str(record.get("article_number", ""))
    content = str(record.get("content", "")).lower()
    question_intent = str(record.get("question_intent", "")).lower()
    source = str(record.get("source", ""))

    if source == "accountant_retrieval_hotspot_patch":
        return True
    if law_name == "Rozporządzenie KSeF" and source == "legacy":
        return True
    if "ulga dla seniora" in content or "ulga dla seniora" in question_intent:
        return article_number != "art. 21 ust. 1 pkt 154"
    if article_number in {"art. 26hc", "art. 154 ust. 1"} and "senior" in (content + " " + question_intent):
        return True
    return False


def main() -> None:
    kb_records = load_json(KB_PATH)
    filtered_records = [record for record in kb_records if not should_remove(record)]
    targeted_records = build_targeted_records()

    existing_keys = {
        (
            rec.get("law_name", ""),
            rec.get("article_number", ""),
            rec.get("question_intent", ""),
            rec.get("content", ""),
        )
        for rec in filtered_records
    }

    added = 0
    for record in targeted_records:
        key = (
            record["law_name"],
            record["article_number"],
            record["question_intent"],
            record["content"],
        )
        if key not in existing_keys:
            filtered_records.append(record)
            existing_keys.add(key)
            added += 1

    filtered_records.sort(
        key=lambda rec: (
            rec.get("law_name", ""),
            rec.get("article_number", ""),
            rec.get("question_intent", ""),
            rec.get("content", ""),
        )
    )
    KB_PATH.write_text(json.dumps(filtered_records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "removed_count": len(kb_records) - len(filtered_records) + added,
        "added_count": added,
        "new_total_records": len(filtered_records),
        "added_records": targeted_records,
    }
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
