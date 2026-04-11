from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.add_missing_articles_from_sources import (  # noqa: E402
    build_question_intent,
    clean_article_text,
    clip_text,
    infer_category,
    is_usable_source_article,
)
from analysis.article_coverage_audit import (  # noqa: E402
    KB_PATH,
    SOURCE_FILE_BY_LAW,
    article_root,
    canonicalize_law_name,
    load_json,
)

COVERAGE_PATH = ROOT / "tests" / "output" / "top100_coverage.json"
ADDITIONS_PATH = ROOT / "data" / "seeds" / "law_knowledge_additions.json"
REPORT_PATH = ROOT / "analysis" / "add_missing_units_report.json"


@dataclass(frozen=True, slots=True)
class LawSource:
    law_name: str
    source_path: Path | None
    category_hint: str


LAW_PATTERN_SOURCES: tuple[tuple[re.Pattern[str], LawSource], ...] = (
    (
        re.compile(r"\brycza[łl]t|\bnajem\b|stawk[aeyi] rycza[łl]tu", re.IGNORECASE),
        LawSource(
            law_name="Ustawa o zryczałtowanym podatku dochodowym",
            source_path=ROOT / "kb-pipeline" / "output" / "articles_ryczalt.json",
            category_hint="pit",
        ),
    ),
    (
        re.compile(r"\bprawo przedsi[eę]biorc[óo]w|\bulga na start\b|\bzawieszenie dzia[łl]alno", re.IGNORECASE),
        LawSource(
            law_name="Prawo przedsiębiorców",
            source_path=None,
            category_hint="ogólne",
        ),
    ),
    (
        re.compile(r"\bksh\b|\bkodeks sp[oó][łl]ek handlowych\b|\bsp[oó][łl]k[ai]\b", re.IGNORECASE),
        LawSource(
            law_name="Kodeks spółek handlowych",
            source_path=None,
            category_hint="ogólne",
        ),
    ),
    (
        re.compile(r"\bzasi[łl]ek chorobow", re.IGNORECASE),
        LawSource(
            law_name="Ustawa o systemie ubezpieczeń społecznych",
            source_path=ROOT / "kb-pipeline" / "output" / "articles_zus.json",
            category_hint="zus",
        ),
    ),
    (
        re.compile(r"\bkasa fiskalna|\bkasy rejestruj[aą]c|\bzwolnienie z kasy", re.IGNORECASE),
        LawSource(
            law_name="Rozporządzenie MF o kasach rejestrujących",
            source_path=ROOT / "kb-pipeline" / "output" / "articles_kasy.json",
            category_hint="vat",
        ),
    ),
    (
        re.compile(r"\bksef\b|krajowy system e-faktur", re.IGNORECASE),
        LawSource(
            law_name="Rozporządzenie KSeF",
            source_path=ROOT / "kb-pipeline" / "output" / "articles_ksef.json",
            category_hint="ksef",
        ),
    ),
    (
        re.compile(r"\bjpk\b|\bgtu\b|jpk_v7", re.IGNORECASE),
        LawSource(
            law_name="Rozporządzenie JPK_V7",
            source_path=ROOT / "kb-pipeline" / "output" / "articles_jpk.json",
            category_hint="jpk",
        ),
    ),
    (
        re.compile(r"\besto[ńn]ski cit\b|\bcit-?8\b|\bcertyfikat rezydencji\b|\bwht\b", re.IGNORECASE),
        LawSource(
            law_name="Ustawa o podatku dochodowym od osób prawnych",
            source_path=ROOT / "kb-pipeline" / "output" / "articles_cit.json",
            category_hint="cit",
        ),
    ),
    (
        re.compile(r"\bpit\b|\bulga dla seniora\b|\bkurs\b|\bwalut", re.IGNORECASE),
        LawSource(
            law_name="Ustawa o podatku dochodowym od osób fizycznych",
            source_path=ROOT / "kb-pipeline" / "output" / "articles_pit.json",
            category_hint="pit",
        ),
    ),
    (
        re.compile(r"\bsprawozdanie\b|\bkpir\b|\bzaksi[eę]gowa[cć]\b|\binwentaryzac", re.IGNORECASE),
        LawSource(
            law_name="Ustawa o rachunkowości",
            source_path=ROOT / "kb-pipeline" / "output" / "articles_rachunkowosc.json",
            category_hint="rachunkowosc",
        ),
    ),
    (
        re.compile(r"\bordynacja\b|\bnadp[łl]at", re.IGNORECASE),
        LawSource(
            law_name="Ordynacja podatkowa",
            source_path=ROOT / "kb-pipeline" / "output" / "articles_ordynacja.json",
            category_hint="ordynacja",
        ),
    ),
    (
        re.compile(r"\bwypowiedzeni|\burlop\b|\bumowa o prac[eę]\b", re.IGNORECASE),
        LawSource(
            law_name="Kodeks pracy",
            source_path=ROOT / "kb-pipeline" / "output" / "articles_kodeks_pracy.json",
            category_hint="kadry",
        ),
    ),
    (
        re.compile(r"\bzus\b|\bsk[łl]adk|\bdra\b|\brca\b", re.IGNORECASE),
        LawSource(
            law_name="Ustawa o systemie ubezpieczeń społecznych",
            source_path=ROOT / "kb-pipeline" / "output" / "articles_zus.json",
            category_hint="zus",
        ),
    ),
    (
        re.compile(r"\bvat\b|\bfaktur|\bparagon\b", re.IGNORECASE),
        LawSource(
            law_name="Ustawa o VAT",
            source_path=ROOT / "kb-pipeline" / "output" / "articles.json",
            category_hint="vat",
        ),
    ),
)


CATEGORY_FALLBACK_SOURCES: dict[str, LawSource] = {
    "cit": LawSource(
        law_name="Ustawa o podatku dochodowym od osób prawnych",
        source_path=ROOT / "kb-pipeline" / "output" / "articles_cit.json",
        category_hint="cit",
    ),
    "pit": LawSource(
        law_name="Ustawa o podatku dochodowym od osób fizycznych",
        source_path=ROOT / "kb-pipeline" / "output" / "articles_pit.json",
        category_hint="pit",
    ),
    "vat": LawSource(
        law_name="Ustawa o VAT",
        source_path=ROOT / "kb-pipeline" / "output" / "articles.json",
        category_hint="vat",
    ),
    "rachunkowosc": LawSource(
        law_name="Ustawa o rachunkowości",
        source_path=ROOT / "kb-pipeline" / "output" / "articles_rachunkowosc.json",
        category_hint="rachunkowosc",
    ),
    "kadry": LawSource(
        law_name="Kodeks pracy",
        source_path=ROOT / "kb-pipeline" / "output" / "articles_kodeks_pracy.json",
        category_hint="kadry",
    ),
    "ordynacja": LawSource(
        law_name="Ordynacja podatkowa",
        source_path=ROOT / "kb-pipeline" / "output" / "articles_ordynacja.json",
        category_hint="ordynacja",
    ),
    "jpk": LawSource(
        law_name="Rozporządzenie JPK_V7",
        source_path=ROOT / "kb-pipeline" / "output" / "articles_jpk.json",
        category_hint="jpk",
    ),
    "ksef": LawSource(
        law_name="Rozporządzenie KSeF",
        source_path=ROOT / "kb-pipeline" / "output" / "articles_ksef.json",
        category_hint="ksef",
    ),
    "zus": LawSource(
        law_name="Ustawa o systemie ubezpieczeń społecznych",
        source_path=ROOT / "kb-pipeline" / "output" / "articles_zus.json",
        category_hint="zus",
    ),
}


def normalize_text(text: str) -> str:
    """Normalize text for fuzzy keyword comparisons."""

    normalized = unicodedata.normalize("NFKD", text.lower())
    normalized = "".join(character for character in normalized if not unicodedata.combining(character))
    normalized = normalized.replace("?", " ")
    return re.sub(r"\s+", " ", normalized).strip()


def tokenize(text: str) -> set[str]:
    """Tokenize a normalized string into simple lowercase words."""

    return set(re.findall(r"[a-z0-9_]{3,}", normalize_text(text)))


def load_gap_questions(path: Path) -> list[dict[str, Any]]:
    """Load GAP questions from the coverage audit output."""

    payload = load_json(path)
    gap_questions = payload.get("gap_questions", [])
    if not isinstance(gap_questions, list):
        raise ValueError(f"Expected 'gap_questions' list in {path}")
    return [question for question in gap_questions if isinstance(question, dict)]


def load_articles(path: Path | None) -> list[dict[str, Any]]:
    """Load parsed ISAP articles from an articles_*.json file."""

    if path is None or not path.exists():
        return []
    payload = load_json(path)
    if isinstance(payload, dict):
        articles = payload.get("articles", [])
        return articles if isinstance(articles, list) else []
    if isinstance(payload, list):
        return payload
    return []


def detect_sources(question: dict[str, Any]) -> list[LawSource]:
    """Detect candidate legal sources for a GAP question."""

    query = str(question.get("query", ""))
    source_category = str(question.get("source_category", "")).strip().lower()
    matched: list[LawSource] = []
    seen: set[str] = set()

    for pattern, source in LAW_PATTERN_SOURCES:
        if pattern.search(query) and source.law_name not in seen:
            matched.append(source)
            seen.add(source.law_name)

    fallback = CATEGORY_FALLBACK_SOURCES.get(source_category)
    if fallback and fallback.law_name not in seen:
        matched.append(fallback)

    chunk_laws = question.get("chunks", [])
    if isinstance(chunk_laws, list):
        for chunk in chunk_laws:
            if not isinstance(chunk, dict):
                continue
            chunk_law_name = canonicalize_law_name(str(chunk.get("law_name", "")).strip())
            source_path = SOURCE_FILE_BY_LAW.get(chunk_law_name)
            if chunk_law_name and chunk_law_name not in seen:
                matched.append(
                    LawSource(
                        law_name=chunk_law_name,
                        source_path=source_path,
                        category_hint=str(chunk.get("category", "ogólne")).strip() or "ogólne",
                    )
                )
                seen.add(chunk_law_name)

    return matched


def score_article(query: str, article: dict[str, Any]) -> tuple[float, str]:
    """Score a parsed article against a GAP question using keyword overlap."""

    raw_text = str(article.get("raw_text", "")).strip()
    chapter = str(article.get("chapter", "")).strip()
    division = str(article.get("division", "")).strip()
    full_id = str(article.get("full_id") or article.get("article_number") or "").strip()
    haystack = " ".join([full_id, chapter, division, raw_text])

    query_tokens = tokenize(query)
    article_tokens = tokenize(haystack)
    if not query_tokens or not article_tokens:
        return 0.0, ""

    overlap = query_tokens & article_tokens
    overlap_score = len(overlap)

    if full_id and full_id.lower() in normalize_text(query):
        overlap_score += 4
    if "certyfikat rezydencji" in normalize_text(query) and "certyfikat rezydencji" in normalize_text(haystack):
        overlap_score += 4
    if "zasilek" in normalize_text(query) and "chorobow" in normalize_text(haystack):
        overlap_score += 3

    return float(overlap_score), ", ".join(sorted(overlap)[:12])


def build_proposed_unit(
    question: dict[str, Any],
    source: LawSource,
    article: dict[str, Any],
    score: float,
    overlap_hint: str,
) -> dict[str, Any]:
    """Convert a parsed article into a proposed KB unit."""

    full_id = str(article.get("full_id") or article.get("article_number") or "").strip()
    chapter = str(article.get("chapter", "")).strip()
    raw_text = str(article.get("raw_text", "")).strip()
    cleaned = clean_article_text(raw_text, full_id)
    content = clip_text(cleaned, limit=600)
    law_name = canonicalize_law_name(source.law_name)
    category = infer_category(law_name, article_root(full_id), chapter, content)
    if category == "ogĂłlne":
        category = source.category_hint

    return {
        "law_name": law_name,
        "article_number": article_root(full_id),
        "category": category,
        "verified_date": "",
        "question_intent": build_question_intent(law_name, article_root(full_id), chapter, content),
        "content": content,
        "source": "gap_question_addition",
        "gap_query": str(question.get("query", "")).strip(),
        "gap_freq": int(question.get("freq", 0) or 0),
        "gap_source_category": str(question.get("source_category", "")).strip(),
        "proposal_meta": {
            "matched_law": law_name,
            "matched_source_file": str(source.source_path.relative_to(ROOT)) if source.source_path else None,
            "score": score,
            "overlap_hint": overlap_hint,
            "chapter": chapter,
        },
    }


def select_candidates(question: dict[str, Any], max_candidates_per_source: int) -> list[dict[str, Any]]:
    """Find the best candidate articles for a GAP question."""

    query = str(question.get("query", "")).strip()
    proposals: list[dict[str, Any]] = []

    for source in detect_sources(question):
        articles = load_articles(source.source_path)
        scored_articles: list[tuple[float, str, dict[str, Any]]] = []
        for article in articles:
            raw_text = str(article.get("raw_text", "")).strip()
            cleaned = clean_article_text(raw_text, str(article.get("full_id") or article.get("article_number") or ""))
            if not is_usable_source_article(source.law_name, raw_text, cleaned):
                continue
            score, overlap_hint = score_article(query, article)
            if score <= 0:
                continue
            scored_articles.append((score, overlap_hint, article))

        scored_articles.sort(
            key=lambda item: (
                item[0],
                str(item[2].get("chapter", "")),
                str(item[2].get("full_id") or item[2].get("article_number") or ""),
            ),
            reverse=True,
        )

        for score, overlap_hint, article in scored_articles[:max_candidates_per_source]:
            proposals.append(build_proposed_unit(question, source, article, score, overlap_hint))

    proposals.sort(
        key=lambda item: (
            float(item.get("proposal_meta", {}).get("score", 0.0)),
            int(item.get("gap_freq", 0)),
        ),
        reverse=True,
    )
    return proposals


def choose_proposals(
    gap_questions: list[dict[str, Any]],
    interactive: bool,
    max_candidates_per_source: int,
) -> list[dict[str, Any]]:
    """Build additions either automatically or with lightweight user prompts."""

    chosen: list[dict[str, Any]] = []
    existing_keys: set[tuple[str, str, str]] = set()

    for question in gap_questions:
        candidates = select_candidates(question, max_candidates_per_source=max_candidates_per_source)
        if not candidates:
            continue

        selected: dict[str, Any] | None
        if interactive:
            print()
            print(f"Q: {question.get('query', '')}")
            print(f"freq={question.get('freq', 0)} | source_category={question.get('source_category', '')}")
            for index, candidate in enumerate(candidates[:5], start=1):
                meta = candidate.get("proposal_meta", {})
                print(
                    f"[{index}] {candidate['law_name']} | {candidate['article_number']} | "
                    f"score={meta.get('score')} | overlap={meta.get('overlap_hint')}"
                )
                print(f"     {candidate['content'][:240]}")
            decision = input("Wybierz numer, Enter=1, s=skip: ").strip().lower()
            if decision == "s":
                selected = None
            elif decision.isdigit() and 1 <= int(decision) <= min(5, len(candidates)):
                selected = candidates[int(decision) - 1]
            else:
                selected = candidates[0]
        else:
            selected = candidates[0]

        if not selected:
            continue

        key = (
            selected["law_name"],
            selected["article_number"],
            selected["content"],
        )
        if key in existing_keys:
            continue
        existing_keys.add(key)
        chosen.append(selected)

    return chosen


def write_additions(additions: list[dict[str, Any]], output_path: Path) -> None:
    """Write proposed units to a standalone additions file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(additions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def integrate_additions(additions_path: Path, kb_path: Path) -> dict[str, Any]:
    """Merge additions into the main KB and return a post-update report."""

    additions = load_json(additions_path) if additions_path.exists() else []
    if not isinstance(additions, list):
        raise ValueError(f"Expected additions list in {additions_path}")

    kb_records = load_json(kb_path)
    if not isinstance(kb_records, list):
        raise ValueError(f"Expected KB list in {kb_path}")

    before_total = len(kb_records)
    before_counts = Counter(canonicalize_law_name(str(record.get("law_name", ""))) for record in kb_records)
    existing_keys = {
        (
            canonicalize_law_name(str(record.get("law_name", ""))),
            str(record.get("article_number", "")),
            str(record.get("content", "")),
        )
        for record in kb_records
    }

    added_counts: Counter[str] = Counter()
    for addition in additions:
        key = (
            canonicalize_law_name(str(addition.get("law_name", ""))),
            str(addition.get("article_number", "")),
            str(addition.get("content", "")),
        )
        if key in existing_keys:
            continue
        kb_records.append(addition)
        existing_keys.add(key)
        added_counts[key[0]] += 1

    kb_records.sort(
        key=lambda record: (
            canonicalize_law_name(str(record.get("law_name", ""))),
            article_root(str(record.get("article_number", ""))),
            str(record.get("question_intent", "")),
            str(record.get("content", "")),
        )
    )
    kb_path.write_text(json.dumps(kb_records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    after_counts = Counter(canonicalize_law_name(str(record.get("law_name", ""))) for record in kb_records)
    report = {
        "meta": {
            "kb_path": str(kb_path.relative_to(ROOT)),
            "additions_path": str(additions_path.relative_to(ROOT)),
            "before_total": before_total,
            "after_total": len(kb_records),
            "added_total": sum(added_counts.values()),
        },
        "added_per_law": dict(added_counts),
        "counts_per_law_after": dict(sorted(after_counts.items())),
        "counts_per_law_before": dict(sorted(before_counts.items())),
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line interface for the GAP-unit workflow."""

    parser = argparse.ArgumentParser(
        description=(
            "Generate proposed KB units from GAP questions and parsed ISAP articles, "
            "optionally integrate them into the main knowledge base."
        )
    )
    parser.add_argument(
        "--mode",
        choices=("propose", "integrate", "all"),
        default="all",
        help="Run only proposal generation, only integration, or the full workflow.",
    )
    parser.add_argument(
        "--coverage",
        type=Path,
        default=COVERAGE_PATH,
        help="Path to top100_coverage.json with GAP questions.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ADDITIONS_PATH,
        help="Path to save proposed additions JSON.",
    )
    parser.add_argument(
        "--knowledge-base",
        type=Path,
        default=KB_PATH,
        help="Main law_knowledge.json path.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for each GAP question instead of auto-selecting the top candidate.",
    )
    parser.add_argument(
        "--max-candidates-per-source",
        type=int,
        default=3,
        help="How many top article candidates to keep from each matched source file.",
    )
    return parser


def main() -> None:
    """Run the GAP-driven unit suggestion and integration workflow."""

    parser = build_parser()
    args = parser.parse_args()

    if args.mode in {"propose", "all"}:
        gap_questions = load_gap_questions(args.coverage)
        additions = choose_proposals(
            gap_questions=gap_questions,
            interactive=args.interactive,
            max_candidates_per_source=args.max_candidates_per_source,
        )
        write_additions(additions, args.output)
        per_law = Counter(canonicalize_law_name(str(item.get("law_name", ""))) for item in additions)
        print(f"Saved {len(additions)} proposed units to {args.output}")
        for law_name, count in per_law.most_common():
            print(f"  {law_name}: {count}")

    if args.mode in {"integrate", "all"}:
        report = integrate_additions(args.output, args.knowledge_base)
        print("Integrated additions into KB.")
        print(f"  before_total: {report['meta']['before_total']}")
        print(f"  added_total:  {report['meta']['added_total']}")
        print(f"  after_total:  {report['meta']['after_total']}")
        print("  added per law:")
        for law_name, count in sorted(report["added_per_law"].items()):
            print(f"    {law_name}: {count}")
        print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
