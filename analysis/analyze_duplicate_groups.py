"""
Analyze duplicate groups in law_knowledge seed files.

Classifies each group of records sharing (law_name, article_number) as:
  - true_duplicate:       min pairwise content Jaccard similarity >= 0.85
  - near_duplicate:       0.60 <= min similarity < 0.85
  - legitimate_variants:  min similarity < 0.60

Outputs:
  analysis/duplicate_groups_report.json   full per-group detail
  analysis/duplicate_groups_report.md     human-readable summary

This script is analytical only  it does NOT modify any KB file.
"""

from __future__ import annotations

import json
import re
import string
from collections import defaultdict
from datetime import date
from itertools import combinations
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
SEED_DIR = ROOT / "data" / "seeds"

SOURCE_FILES = [
    SEED_DIR / "law_knowledge.json",
    SEED_DIR / "law_knowledge_additions.json",
    SEED_DIR / "law_knowledge_curated_additions.json",
]

OUT_DIR = ROOT / "analysis"
REPORT_JSON = OUT_DIR / "duplicate_groups_report.json"
REPORT_MD = OUT_DIR / "duplicate_groups_report.md"


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
TRUE_DUP_THRESHOLD = 0.85
NEAR_DUP_THRESHOLD = 0.60
KEY_COLLISION_COUNT = 10  # groups > this are flagged as potential key collision


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_PUNCT_RE = re.compile(f"[{re.escape(string.punctuation)}]")
_SPACE_RE = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    text = text.lower()
    text = _PUNCT_RE.sub(" ", text)
    text = _SPACE_RE.sub(" ", text).strip()
    return text


def tokenize(text: str) -> set[str]:
    normalized = normalize(text)
    if not normalized:
        return set()
    return set(normalized.split())


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def classify(min_sim: float) -> str:
    if min_sim >= TRUE_DUP_THRESHOLD:
        return "true_duplicate"
    if min_sim >= NEAR_DUP_THRESHOLD:
        return "near_duplicate"
    return "legitimate_variants"


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
def load_all_records() -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for path in SOURCE_FILES:
        if not path.exists():
            print(f"  [WARN] File not found, skipping: {path.name}")
            continue
        with open(path, encoding="utf-8") as f:
            records = json.load(f)
        for idx, rec in enumerate(records):
            rec["_source_file"] = path.name
            rec["_record_index"] = idx
        merged.extend(records)
        print(f"  Loaded {len(records):>5} records from {path.name}")
    print(f"  Total merged: {len(merged)}")
    return merged


# ---------------------------------------------------------------------------
# Analyze
# ---------------------------------------------------------------------------
def analyze_groups(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for rec in records:
        key = (rec.get("law_name", ""), rec.get("article_number", ""))
        groups[key].append(rec)

    dup_groups = {k: v for k, v in groups.items() if len(v) >= 2}
    print(f"  Duplicate groups (count >= 2): {len(dup_groups)}")

    results: list[dict[str, Any]] = []
    for (law_name, article_number), recs in sorted(dup_groups.items()):
        count = len(recs)

        content_tokens = [tokenize(r.get("content", "")) for r in recs]
        intent_tokens = [tokenize(r.get("question_intent", "")) for r in recs]

        content_sims: list[float] = []
        intent_sims: list[float] = []
        for i, j in combinations(range(count), 2):
            content_sims.append(jaccard(content_tokens[i], content_tokens[j]))
            intent_sims.append(jaccard(intent_tokens[i], intent_tokens[j]))

        c_min = min(content_sims) if content_sims else 0.0
        c_max = max(content_sims) if content_sims else 0.0
        c_avg = sum(content_sims) / len(content_sims) if content_sims else 0.0
        i_min = min(intent_sims) if intent_sims else 0.0
        i_max = max(intent_sims) if intent_sims else 0.0
        i_avg = sum(intent_sims) / len(intent_sims) if intent_sims else 0.0

        categories = {r.get("category", "") for r in recs}
        sources = {r.get("source", "") for r in recs}
        any_verified = any(bool(r.get("verified_date", "")) for r in recs)

        classification = classify(c_min)
        potential_key_collision = count > KEY_COLLISION_COUNT

        group_key = f"{law_name} | {article_number}"

        results.append(
            {
                "group_key": group_key,
                "law_name": law_name,
                "article_number": article_number,
                "count": count,
                "classification": classification,
                "potential_key_collision": potential_key_collision,
                "min_content_similarity": round(c_min, 4),
                "max_content_similarity": round(c_max, 4),
                "avg_content_similarity": round(c_avg, 4),
                "min_intent_similarity": round(i_min, 4),
                "max_intent_similarity": round(i_max, 4),
                "avg_intent_similarity": round(i_avg, 4),
                "same_category": len(categories) == 1,
                "categories": sorted(categories),
                "same_source": len(sources) == 1,
                "any_verified": any_verified,
                "records": [
                    {
                        "source_file": r.get("_source_file", ""),
                        "record_index": r.get("_record_index", -1),
                        "content_preview": r.get("content", "")[:150],
                        "question_intent_preview": r.get("question_intent", "")[:150],
                        "source": r.get("source", ""),
                        "category": r.get("category", ""),
                        "verified_date": r.get("verified_date", ""),
                    }
                    for r in recs
                ],
            }
        )

    return results


# ---------------------------------------------------------------------------
# Summary / impact
# ---------------------------------------------------------------------------
def build_classification_summary(groups: list[dict[str, Any]]) -> dict[str, int]:
    summary = {"true_duplicate": 0, "near_duplicate": 0, "legitimate_variants": 0}
    for g in groups:
        summary[g["classification"]] += 1
    return summary


def build_records_impact(
    groups: list[dict[str, Any]], total_records: int
) -> dict[str, int]:
    excess_true = sum(
        g["count"] - 1 for g in groups if g["classification"] == "true_duplicate"
    )
    excess_near = sum(
        g["count"] - 1 for g in groups if g["classification"] == "near_duplicate"
    )
    return {
        "would_remove_if_dedupe_true_duplicates": excess_true,
        "would_remove_if_dedupe_true_and_near": excess_true + excess_near,
        "final_kb_size_after_true_dedupe": total_records - excess_true,
        "final_kb_size_after_true_and_near_dedupe": total_records - excess_true - excess_near,
    }


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------
def _preview(text: str, n: int = 180) -> str:
    t = text.replace("\n", " ").replace("|", "/")
    return t[:n] + ("" if len(t) <= n else "")


def build_markdown(
    groups: list[dict[str, Any]],
    total_records: int,
    classification_summary: dict[str, int],
    records_impact: dict[str, int],
    scan_date: str,
) -> str:
    lines: list[str] = []
    lines.append("# Duplicate Groups Report")
    lines.append("")
    lines.append(f"- **Scan date:** {scan_date}")
    lines.append(f"- **Total records scanned:** {total_records}")
    lines.append(f"- **Total duplicate groups (count  2):** {len(groups)}")
    lines.append(
        f"- **Thresholds:** true_duplicate  min Jaccard  {TRUE_DUP_THRESHOLD}; "
        f"near_duplicate  [{NEAR_DUP_THRESHOLD}, {TRUE_DUP_THRESHOLD}); "
        f"legitimate_variants  < {NEAR_DUP_THRESHOLD}"
    )
    lines.append("")

    lines.append("## Classification summary")
    lines.append("")
    lines.append("| classification | groups |")
    lines.append("|---|---:|")
    for cls in ("true_duplicate", "near_duplicate", "legitimate_variants"):
        lines.append(f"| {cls} | {classification_summary[cls]} |")
    lines.append("")

    lines.append("## Records impact")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---:|")
    lines.append(
        f"| would_remove_if_dedupe_true_duplicates | "
        f"{records_impact['would_remove_if_dedupe_true_duplicates']} |"
    )
    lines.append(
        f"| would_remove_if_dedupe_true_and_near | "
        f"{records_impact['would_remove_if_dedupe_true_and_near']} |"
    )
    lines.append(
        f"| final_kb_size_after_true_dedupe | "
        f"{records_impact['final_kb_size_after_true_dedupe']} |"
    )
    lines.append(
        f"| final_kb_size_after_true_and_near_dedupe | "
        f"{records_impact['final_kb_size_after_true_and_near_dedupe']} |"
    )
    lines.append("")

    # Potential key collisions
    collisions = [g for g in groups if g["potential_key_collision"]]
    lines.append(f"## Potential key collisions (count > {KEY_COLLISION_COUNT})")
    lines.append("")
    if not collisions:
        lines.append("_None._")
    else:
        lines.append("| group_key | count | classification |")
        lines.append("|---|---:|---|")
        for g in sorted(collisions, key=lambda x: x["count"], reverse=True):
            lines.append(
                f"| {g['group_key']} | {g['count']} | {g['classification']} |"
            )
    lines.append("")

    # Top 10 largest groups
    lines.append("## Top 10 largest groups (by count)")
    lines.append("")
    lines.append(
        "| group_key | count | classification | min_sim | avg_sim |"
    )
    lines.append("|---|---:|---|---:|---:|")
    for g in sorted(groups, key=lambda x: x["count"], reverse=True)[:10]:
        lines.append(
            f"| {g['group_key']} | {g['count']} | {g['classification']} | "
            f"{g['min_content_similarity']} | {g['avg_content_similarity']} |"
        )
    lines.append("")

    # Top 10 true_duplicate examples
    lines.append("## Top 10 true_duplicate groups (with content previews)")
    lines.append("")
    true_dups = [g for g in groups if g["classification"] == "true_duplicate"]
    true_dups_sorted = sorted(
        true_dups, key=lambda x: (-x["count"], -x["min_content_similarity"])
    )[:10]
    if not true_dups_sorted:
        lines.append("_None._")
    else:
        for g in true_dups_sorted:
            lines.append(
                f"### {g['group_key']}  count={g['count']}, "
                f"min_sim={g['min_content_similarity']}, "
                f"avg_sim={g['avg_content_similarity']}"
            )
            lines.append("")
            for i, r in enumerate(g["records"]):
                lines.append(
                    f"- **[{i}]** `{r['source_file']}` idx={r['record_index']}  "
                    f"source: `{r['source']}`  "
                    f"verified_date: `{r['verified_date'] or ''}`"
                )
                lines.append(f"  - content: {_preview(r['content_preview'])}")
            lines.append("")

    # Top 10 legitimate_variants examples
    lines.append("## Top 10 legitimate_variants groups (sanity check)")
    lines.append("")
    legit = [g for g in groups if g["classification"] == "legitimate_variants"]
    legit_sorted = sorted(
        legit, key=lambda x: (x["min_content_similarity"], -x["count"])
    )[:10]
    if not legit_sorted:
        lines.append("_None._")
    else:
        for g in legit_sorted:
            lines.append(
                f"### {g['group_key']}  count={g['count']}, "
                f"min_sim={g['min_content_similarity']}, "
                f"avg_sim={g['avg_content_similarity']}"
            )
            lines.append("")
            for i, r in enumerate(g["records"]):
                lines.append(
                    f"- **[{i}]** `{r['source_file']}` idx={r['record_index']}"
                )
                lines.append(f"  - content: {_preview(r['content_preview'])}")
            lines.append("")

    # Recommendation
    lines.append("## Recommendation")
    lines.append("")
    kb_true = records_impact["final_kb_size_after_true_dedupe"]
    kb_trueNear = records_impact["final_kb_size_after_true_and_near_dedupe"]
    rem_true = records_impact["would_remove_if_dedupe_true_duplicates"]
    rem_trueNear = records_impact["would_remove_if_dedupe_true_and_near"]
    td = classification_summary["true_duplicate"]
    nd = classification_summary["near_duplicate"]
    lv = classification_summary["legitimate_variants"]

    lines.append(
        f"KB po dedup `true_duplicate`: **{kb_true}** rekordw "
        f"(usunite: {rem_true} z {td} grup). "
        f"KB po dedup `true + near`: **{kb_trueNear}** rekordw "
        f"(usunite: {rem_trueNear} z {td + nd} grup). "
        f"`legitimate_variants`: **{lv}** grup  do zachowania jako rne ujcia "
        f"tego samego artykuu. "
        f"**Sugerowana strategia:** w pierwszej kolejnoci dedupe tylko "
        f"`true_duplicate` (bezpieczne, wysoka pewno  min Jaccard  "
        f"{TRUE_DUP_THRESHOLD}), zachowujc rekord z niepustym "
        f"`verified_date` lub  jeli brak  z `law_knowledge_curated_additions.json`, "
        f"potem `law_knowledge.json`. `near_duplicate` wymaga manualnego przegldu "
        f"(moliwe redakcyjne warianty tego samego przepisu vs. komplementarne "
        f"wyjanienia). Grupy oznaczone `potential_key_collision` (count > "
        f"{KEY_COLLISION_COUNT}) mog sygnalizowa kolizj klucza "
        f"`(law_name, article_number)`  rozway wzbogacenie klucza o `paragraph` "
        f"lub `ustep` przed dedup."
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("=== Duplicate Groups Analysis ===\n")

    print("Loading records...")
    records = load_all_records()
    total_records = len(records)

    print("\nAnalyzing duplicate groups...")
    groups = analyze_groups(records)

    classification_summary = build_classification_summary(groups)
    records_impact = build_records_impact(groups, total_records)
    scan_date = date.today().isoformat()

    report = {
        "scan_date": scan_date,
        "total_records": total_records,
        "total_duplicate_groups": len(groups),
        "classification_summary": classification_summary,
        "records_impact": records_impact,
        "thresholds": {
            "true_duplicate_min_jaccard": TRUE_DUP_THRESHOLD,
            "near_duplicate_min_jaccard": NEAR_DUP_THRESHOLD,
            "key_collision_count_threshold": KEY_COLLISION_COUNT,
        },
        "groups": groups,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n  JSON report: {REPORT_JSON.relative_to(ROOT)}")

    md = build_markdown(
        groups, total_records, classification_summary, records_impact, scan_date
    )
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"  MD report:   {REPORT_MD.relative_to(ROOT)}")

    print("\n--- Classification ---")
    for k, v in classification_summary.items():
        print(f"  {k:22s} {v:>4} groups")
    print("\n--- Records impact ---")
    for k, v in records_impact.items():
        print(f"  {k:45s} {v}")
    print("\nDone.")


if __name__ == "__main__":
    main()
