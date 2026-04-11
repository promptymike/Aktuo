"""Prepare raw KB units for reprocessing through generate_units.py.

The raw-unit detector saves records straight from law_knowledge.json. This script:
1. Groups them by canonical law, not by raw law_name string, so mojibake variants
   like "os?b" and "osób" do not split PIT/CIT into separate partial runs.
2. Preserves distinct VAT/KSeF supplement entries as separate reprocess inputs.
3. Reuses full parsed article text from articles_*.json when available.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
RAW_UNITS_PATH = ROOT / "raw_units_to_process.json"
REPROCESS_DIR = OUTPUT / "reprocess"


@dataclass(frozen=True)
class LawConfig:
    canonical_law_name: str
    short_name: str
    source_filename: str


LAW_CONFIGS = (
    (
        "ustawa o vat - ksef terminy wdrozenia",
        LawConfig(
            canonical_law_name="Ustawa o VAT - KSeF terminy wdrożenia",
            short_name="Ustawa o VAT KSeF terminy",
            source_filename="articles_vat.json",
        ),
    ),
    (
        "ustawa o vat - ksef uproszczenia 2026",
        LawConfig(
            canonical_law_name="Ustawa o VAT - KSeF uproszczenia 2026",
            short_name="Ustawa o VAT KSeF uproszczenia",
            source_filename="articles_vat.json",
        ),
    ),
    (
        "ustawa o vat - ksef zwolnienia",
        LawConfig(
            canonical_law_name="Ustawa o VAT - KSeF zwolnienia",
            short_name="Ustawa o VAT KSeF zwolnienia",
            source_filename="articles_vat.json",
        ),
    ),
    (
        "ustawa o vat",
        LawConfig(
            canonical_law_name="Ustawa o VAT",
            short_name="Ustawa o VAT",
            source_filename="articles_vat.json",
        ),
    ),
    (
        "podatku dochodowym od osob fizycznych",
        LawConfig(
            canonical_law_name="Ustawa o podatku dochodowym od osób fizycznych",
            short_name="Ustawa o PIT",
            source_filename="articles_pit.json",
        ),
    ),
    (
        "podatku dochodowym od osob prawnych",
        LawConfig(
            canonical_law_name="Ustawa o podatku dochodowym od osób prawnych",
            short_name="Ustawa o CIT",
            source_filename="articles_cit.json",
        ),
    ),
    (
        "ordynacja podatkowa",
        LawConfig(
            canonical_law_name="Ordynacja podatkowa",
            short_name="Ordynacja podatkowa",
            source_filename="articles_ordynacja.json",
        ),
    ),
    (
        "kodeks pracy",
        LawConfig(
            canonical_law_name="Kodeks pracy",
            short_name="Kodeks pracy",
            source_filename="articles_kodeks_pracy.json",
        ),
    ),
    (
        "ubezpieczen spolecznych",
        LawConfig(
            canonical_law_name="Ustawa o systemie ubezpieczeń społecznych",
            short_name="Ustawa o ZUS",
            source_filename="articles_zus.json",
        ),
    ),
    (
        "rachunkowosci",
        LawConfig(
            canonical_law_name="Ustawa o rachunkowości",
            short_name="Ustawa o rachunkowości",
            source_filename="articles_rachunkowosc.json",
        ),
    ),
    (
        "zryczaltowanym podatku dochodowym",
        LawConfig(
            canonical_law_name="Ustawa o zryczałtowanym podatku dochodowym",
            short_name="Ustawa o ryczałcie",
            source_filename="articles_ryczalt.json",
        ),
    ),
    (
        "kasach rejestrujacych",
        LawConfig(
            canonical_law_name="Rozporządzenie MF o kasach rejestrujących",
            short_name="Rozporządzenie o kasach",
            source_filename="articles_kasy.json",
        ),
    ),
    (
        "jpk_v7",
        LawConfig(
            canonical_law_name="Rozporządzenie JPK_V7",
            short_name="Rozporządzenie JPK_V7",
            source_filename="articles_jpk.json",
        ),
    ),
    (
        "ksef",
        LawConfig(
            canonical_law_name="Rozporządzenie KSeF",
            short_name="Rozporządzenie KSeF",
            source_filename="articles_ksef.json",
        ),
    ),
)


def normalize(text: str) -> str:
    translation = str.maketrans(
        {
            "ą": "a",
            "ć": "c",
            "ę": "e",
            "ł": "l",
            "ń": "n",
            "ó": "o",
            "ś": "s",
            "ż": "z",
            "ź": "z",
        }
    )
    normalized = unicodedata.normalize("NFKD", text.lower().translate(translation))
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    without_mojibake_markers = without_accents.replace("?", " ").replace("Â", " ").replace("Ă", " ")
    collapsed = re.sub(r"\s+", " ", without_mojibake_markers).strip()
    return collapsed.replace("os b", "osob").replace("rozporz dzenie", "rozporzadzenie")


def classify_law(law_name: str) -> LawConfig:
    normalized = normalize(law_name)
    for pattern, config in LAW_CONFIGS:
        if pattern in normalized:
            return config
    return LawConfig(
        canonical_law_name=law_name,
        short_name=law_name,
        source_filename="",
    )


def slugify(text: str) -> str:
    normalized = normalize(text)
    slug = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    return slug or "unknown"


def load_articles_index(articles_path: Path) -> dict[str, dict]:
    data = json.loads(articles_path.read_text(encoding="utf-8"))
    index: dict[str, dict] = {}
    for article in data.get("articles", []):
        index[str(article["article_number"])] = article
    return index


def extract_article_num(article_number: str) -> str:
    """Extract bare article or section number: 'art. 11a ust. 1' -> '11a'."""
    match = re.match(r"(?:art\.\s*|[§Â§]\s*)(\d+[a-z]*)", article_number, re.IGNORECASE)
    return match.group(1) if match else article_number


def generate_question(law_name: str, article_number: str, content: str) -> str:
    preview = " ".join(content.split())[:220]
    return f"Co reguluje {article_number} w akcie {law_name}? Kontekst przepisu: {preview}"


def main() -> None:
    raw_units = json.loads(RAW_UNITS_PATH.read_text(encoding="utf-8"))
    print(f"Loaded {len(raw_units)} raw units")

    grouped_units: dict[str, dict] = defaultdict(lambda: {"config": None, "units": [], "source_law_names": set()})
    for unit in raw_units:
        config = classify_law(str(unit["law_name"]))
        group_key = slugify(config.short_name)
        grouped_units[group_key]["config"] = config
        grouped_units[group_key]["units"].append(unit)
        grouped_units[group_key]["source_law_names"].add(str(unit["law_name"]))

    REPROCESS_DIR.mkdir(exist_ok=True)
    total_articles = 0
    total_questions = 0

    for group_key, payload in sorted(grouped_units.items(), key=lambda item: (-len(item[1]["units"]), item[0])):
        config: LawConfig = payload["config"]
        units: list[dict] = payload["units"]
        source_law_names = sorted(payload["source_law_names"])

        articles_path = OUTPUT / config.source_filename if config.source_filename else None
        full_articles: dict[str, dict] = {}
        if articles_path and articles_path.exists():
            full_articles = load_articles_index(articles_path)

        articles_out: list[dict] = []
        matches_out: list[dict] = []
        seen_art_nums: set[str] = set()

        for unit in units:
            art_num = extract_article_num(str(unit["article_number"]))
            full_art = full_articles.get(art_num)

            if full_art and art_num not in seen_art_nums:
                articles_out.append(full_art)
                seen_art_nums.add(art_num)
            elif art_num not in seen_art_nums:
                synthetic_source = {
                    "article_number": art_num,
                    "full_id": str(unit["article_number"]),
                    "division": "",
                    "chapter": "",
                    "raw_text": str(unit["content"]),
                    "paragraphs": [],
                    "is_repealed": False,
                    "char_count": len(str(unit["content"])),
                }
                articles_out.append(synthetic_source)
                seen_art_nums.add(art_num)

            matches_out.append(
                {
                    "question": generate_question(config.canonical_law_name, str(unit["article_number"]), str(unit["content"])),
                    "matched_articles": [art_num],
                    "topic": unit.get("category", ""),
                    "primary_article": art_num,
                    "source_law_name": unit["law_name"],
                    "source_article_number": unit["article_number"],
                }
            )

        articles_file = REPROCESS_DIR / f"articles_{group_key}.json"
        matched_file = REPROCESS_DIR / f"matched_{group_key}.json"

        articles_data = {
            "metadata": {
                "law_name": config.canonical_law_name,
                "short_name": config.short_name,
                "source_law_names": source_law_names,
                "raw_unit_count": len(units),
                "group_key": group_key,
            },
            "articles": articles_out,
        }
        matched_data = {
            "metadata": {
                "law_name": config.canonical_law_name,
                "short_name": config.short_name,
                "source_law_names": source_law_names,
                "raw_unit_count": len(units),
                "group_key": group_key,
            },
            "matches": matches_out,
        }

        articles_file.write_text(json.dumps(articles_data, ensure_ascii=False, indent=2), encoding="utf-8")
        matched_file.write_text(json.dumps(matched_data, ensure_ascii=False, indent=2), encoding="utf-8")

        total_articles += len(articles_out)
        total_questions += len(matches_out)
        full_text_count = sum(1 for article in articles_out if int(article.get("char_count", 0) or 0) > 600)
        full_pct = (full_text_count / max(len(articles_out), 1)) * 100
        print(
            f"  {config.short_name:<34} {len(units):>4} units -> "
            f"{len(articles_out):>4} articles, {len(matches_out):>4} questions "
            f"(full text: {full_pct:.0f}%)"
        )

    print(f"\nTotal: {total_articles} articles, {total_questions} questions")
    print(f"Output: {REPROCESS_DIR}")


if __name__ == "__main__":
    main()
