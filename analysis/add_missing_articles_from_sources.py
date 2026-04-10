from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.article_coverage_audit import (  # noqa: E402
    KB_PATH,
    SOURCE_FILE_BY_LAW,
    article_root,
    canonicalize_law_name,
    load_json,
    _normalize,
)

OUTPUT_JSON = ROOT / "tests" / "output" / "missing_articles_added_from_sources.json"


def clean_article_text(raw_text: str, article_number: str) -> str:
    text = raw_text.replace("\r", "\n")
    text = re.sub(r"^Art\.\s*[^\s]+\.\s*", "", text.strip())
    text = re.sub(r"^§\s*\d+[a-z]*\.\s*", "", text.strip())
    noise_patterns = [
        r"Opracowano na podstawie:.*?(?=\n|$)",
        r"©Kancelaria Sejmu.*?(?=\n|$)",
        r"Dz\.\s*U\.\s*z\s*\d{4}\s*r\..*?(?=\n|$)",
        r"Dz\. Urz\..*?(?=\n|$)",
    ]
    for pattern in noise_patterns:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" .;")
    text = re.sub(r"^\((uchylony|utracił moc|utracil moc)\)\s*", "", text, flags=re.IGNORECASE)
    return text.strip()


def clip_text(text: str, limit: int = 600) -> str:
    if len(text) <= limit:
        return text
    sentence_cut = max(text.rfind(". ", 0, limit), text.rfind("; ", 0, limit))
    if sentence_cut >= int(limit * 0.6):
        return text[: sentence_cut + 1].strip()
    word_cut = text.rfind(" ", 0, limit - 3)
    if word_cut >= int(limit * 0.6):
        return text[:word_cut].strip() + "..."
    return text[: limit - 3].strip() + "..."


def infer_category(law_name: str, article_number: str, chapter: str, content: str) -> str:
    text = _normalize(f"{chapter} {content}")
    article = article_root(article_number)

    if law_name == "Ustawa o VAT":
        if "krajowego systemu e-faktur" in text or article.startswith("art. 106g"):
            return "ksef"
        if article.startswith(("art. 106", "art. 111")) or "faktur" in text or "paragon" in text:
            if "koryguj" in text:
                return "faktury_korygujące"
            return "fakturowanie"
        if article.startswith(("art. 86", "art. 87", "art. 88", "art. 90", "art. 91")) or "odlicz" in text:
            return "podatek_naliczony"
        if article.startswith(("art. 19a", "art. 20", "art. 21", "art. 29a", "art. 41", "art. 42", "art. 43")):
            return "podatek_należny"
        if article.startswith(("art. 99", "art. 100", "art. 103", "art. 109")) or "terminie do" in text:
            return "terminy"
        if "korekt" in text or article in {"art. 89a", "art. 89b"}:
            return "korekty"
        return "vat"

    if law_name == "Ustawa o podatku dochodowym od osób fizycznych":
        return "pit"
    if law_name == "Ustawa o podatku dochodowym od osób prawnych":
        return "cit"
    if law_name == "Ustawa o systemie ubezpieczeń społecznych":
        return "zus"
    if law_name == "Kodeks pracy":
        return "kadry"
    if law_name == "Ordynacja podatkowa":
        return "ordynacja"
    if law_name == "Ustawa o rachunkowości":
        return "rachunkowosc"
    if law_name == "Rozporządzenie JPK_V7":
        return "jpk"
    if law_name == "Rozporządzenie KSeF":
        return "ksef"
    return "ogólne"


def build_question_intent(law_name: str, article_number: str, chapter: str, content: str) -> str:
    chapter_clean = re.sub(r"\s+", " ", chapter).strip()
    parts = [law_name, article_number]
    if chapter_clean:
        parts.append(chapter_clean)
    if content:
        parts.append(content[:120])
    return " | ".join(parts)[:240]


def is_usable_source_article(law_name: str, raw_text: str, cleaned_text: str) -> bool:
    stripped_raw = raw_text.strip()
    if not stripped_raw.startswith(("Art.", "§", "?")):
        return False

    normalized_clean = _normalize(cleaned_text)
    if not normalized_clean:
        return False
    if normalized_clean in {"(uchylony)", "(utracil moc)", "(pominiety)"}:
        return False
    if normalized_clean.startswith("(pominiety)") or normalized_clean.startswith("(uchylony)"):
        return False
    if law_name == "Rozporządzenie KSeF" and re.match(r"^\d+\.\s+\w+", cleaned_text):
        return False
    return True


def pick_first_article_per_missing_root(
    source_articles: list[dict[str, Any]],
    missing_roots: set[str],
) -> dict[str, dict[str, Any]]:
    picked: dict[str, dict[str, Any]] = {}
    for article in source_articles:
        root = article_root(str(article.get("full_id") or article.get("article_number") or ""))
        if root in missing_roots and root not in picked:
            picked[root] = article
    return picked


def main() -> None:
    kb_records = load_json(KB_PATH)
    kb_records = [record for record in kb_records if record.get("source") != "parsed_article_gap_patch"]
    kb_by_law_roots: dict[str, set[str]] = defaultdict(set)
    for record in kb_records:
        law = canonicalize_law_name(str(record.get("law_name", "")))
        kb_by_law_roots[law].add(article_root(str(record.get("article_number", ""))))

    added_records: list[dict[str, Any]] = []
    added_counts: Counter[str] = Counter()

    for law_name, source_path in SOURCE_FILE_BY_LAW.items():
        source_data = load_json(source_path)
        active_articles = [
            article for article in source_data.get("articles", []) if not article.get("is_repealed", False)
        ]
        source_roots = {
            article_root(str(article.get("full_id") or article.get("article_number") or ""))
            for article in active_articles
        }
        missing_roots = source_roots - kb_by_law_roots[law_name]
        selected_articles = pick_first_article_per_missing_root(active_articles, missing_roots)

        for root, article in sorted(selected_articles.items()):
            raw_text = str(article.get("raw_text", "")).strip()
            cleaned = clean_article_text(raw_text, root)
            if not is_usable_source_article(law_name, raw_text, cleaned):
                continue
            content = clip_text(cleaned, limit=600)
            chapter = str(article.get("chapter", "")).strip()
            record = {
                "law_name": law_name,
                "article_number": root,
                "category": infer_category(law_name, root, chapter, content),
                "verified_date": "",
                "question_intent": build_question_intent(law_name, root, chapter, content),
                "content": content,
                "source": "parsed_article_gap_patch",
            }
            added_records.append(record)
            added_counts[law_name] += 1

    kb_records.extend(added_records)
    kb_records.sort(
        key=lambda record: (
            canonicalize_law_name(str(record.get("law_name", ""))),
            article_root(str(record.get("article_number", ""))),
            str(record.get("question_intent", "")),
            str(record.get("content", "")),
        )
    )
    KB_PATH.write_text(json.dumps(kb_records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "meta": {
            "knowledge_path": str(KB_PATH.relative_to(ROOT)),
            "added_total": len(added_records),
            "new_total_records": len(kb_records),
        },
        "per_law": dict(added_counts),
        "sample_records": added_records[:30],
    }
    OUTPUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"added_total={len(added_records)}")
    print(f"new_total_records={len(kb_records)}")
    for law_name, count in added_counts.most_common():
        print(f"{law_name}: {count}")


if __name__ == "__main__":
    main()
