"""Prepare raw KB units for reprocessing through generate_units.py pipeline.

Creates per-law articles.json and matched.json inputs from raw units,
using full article text from parsed articles files where available.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
RAW_UNITS_PATH = ROOT / "raw_units_to_process.json"

# Map law_name patterns → articles file and canonical law name
LAW_FILE_MAP = {
    "Ustawa o VAT": ("articles_vat.json", "Ustawa o VAT"),
    "Ordynacja podatkowa": ("articles_ordynacja.json", "Ordynacja podatkowa"),
    "podatku dochodowym od osób fizycznych": ("articles_pit.json", "Ustawa o PIT"),
    "podatku dochodowym od os?b fizycznych": ("articles_pit.json", "Ustawa o PIT"),
    "podatku dochodowym od osób prawnych": ("articles_cit.json", "Ustawa o CIT"),
    "podatku dochodowym od os?b prawnych": ("articles_cit.json", "Ustawa o CIT"),
    "Kodeks pracy": ("articles_kodeks_pracy.json", "Kodeks pracy"),
    "ubezpiecze": ("articles_zus.json", "Ustawa o ZUS"),
    "rachunkowo": ("articles_rachunkowosc.json", "Ustawa o rachunkowości"),
    "zryczałtowanym": ("articles_ryczalt.json", "Ustawa o ryczałcie"),
    "zrycza": ("articles_ryczalt.json", "Ustawa o ryczałcie"),
    "kasach rejestruj": ("articles_kasy.json", "Rozporządzenie o kasach"),
    "JPK_V7": ("articles_jpk.json", "Rozporządzenie JPK_V7"),
    "KSeF": ("articles_ksef.json", "Ustawa o KSeF"),
}


def find_articles_file(law_name: str) -> tuple[Path | None, str]:
    for pattern, (filename, short) in LAW_FILE_MAP.items():
        if pattern.lower() in law_name.lower():
            path = OUTPUT / filename
            if path.exists():
                return path, short
    return None, law_name


def load_articles_index(articles_path: Path) -> dict[str, dict]:
    data = json.loads(articles_path.read_text(encoding="utf-8"))
    index: dict[str, dict] = {}
    for art in data.get("articles", []):
        index[art["article_number"]] = art
    return index


def extract_article_num(article_number: str) -> str:
    """Extract bare article number: 'art. 11a ust. 1' → '11a'."""
    m = re.match(r"(?:art\.\s*|§\s*)(\d+[a-z]*)", article_number, re.IGNORECASE)
    return m.group(1) if m else article_number


def generate_question(law_name: str, article_number: str, content: str) -> str:
    """Generate a synthetic question from raw unit metadata."""
    preview = " ".join(content.split())[:200]
    return f"Co reguluje {article_number} {law_name}? Kontekst: {preview}"


def main() -> None:
    raw_units = json.loads(RAW_UNITS_PATH.read_text(encoding="utf-8"))
    print(f"Loaded {len(raw_units)} raw units")

    # Group by law
    by_law: dict[str, list[dict]] = defaultdict(list)
    for unit in raw_units:
        by_law[unit["law_name"]].append(unit)

    output_dir = OUTPUT / "reprocess"
    output_dir.mkdir(exist_ok=True)

    total_articles = 0
    total_questions = 0

    for law_name, units in sorted(by_law.items(), key=lambda x: -len(x[1])):
        articles_path, short_name = find_articles_file(law_name)

        # Load full article texts if available
        full_articles: dict[str, dict] = {}
        if articles_path:
            full_articles = load_articles_index(articles_path)

        # Build articles list and matches
        articles_out: list[dict] = []
        matches_out: list[dict] = []
        seen_art_nums: set[str] = set()

        for unit in units:
            art_num = extract_article_num(unit["article_number"])

            # Try to find full article text
            full_art = full_articles.get(art_num)
            if full_art and art_num not in seen_art_nums:
                articles_out.append(full_art)
                seen_art_nums.add(art_num)
            elif art_num not in seen_art_nums:
                # Fallback: create synthetic article from unit content
                articles_out.append({
                    "article_number": art_num,
                    "full_id": unit["article_number"],
                    "division": "",
                    "chapter": "",
                    "raw_text": unit["content"],
                    "paragraphs": [],
                    "is_repealed": False,
                    "char_count": len(unit["content"]),
                })
                seen_art_nums.add(art_num)

            question = generate_question(law_name, unit["article_number"], unit["content"])
            matches_out.append({
                "question": question,
                "matched_articles": [art_num],
                "topic": unit.get("category", ""),
                "primary_article": art_num,
            })

        # Save per-law files
        slug = re.sub(r"[^a-z0-9]+", "_", short_name.lower()).strip("_")

        articles_file = output_dir / f"articles_{slug}.json"
        articles_data = {
            "metadata": {
                "law_name": law_name,
                "short_name": short_name,
            },
            "articles": articles_out,
        }
        articles_file.write_text(json.dumps(articles_data, ensure_ascii=False, indent=2), encoding="utf-8")

        matched_file = output_dir / f"matched_{slug}.json"
        matched_data = {"matches": matches_out}
        matched_file.write_text(json.dumps(matched_data, ensure_ascii=False, indent=2), encoding="utf-8")

        total_articles += len(articles_out)
        total_questions += len(matches_out)
        full_pct = sum(1 for a in articles_out if a.get("char_count", 0) > 600) / max(len(articles_out), 1) * 100
        print(
            f"  {short_name:<30} {len(units):>4} units -> "
            f"{len(articles_out):>4} articles, {len(matches_out):>4} questions "
            f"(full text: {full_pct:.0f}%)"
        )

    print(f"\nTotal: {total_articles} articles, {total_questions} questions")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
