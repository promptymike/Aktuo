"""Generate an intent-confusion analysis from the latest eval_report.json.

Outputs:
  analysis/intent_confusion_report.json  — machine-readable confusion matrix
  analysis/intent_confusion_report.md    — human-readable markdown summary

Usage:
  python analysis/intent_confusion_report.py
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EVAL_REPORT = ROOT / "eval_report.json"
OUT_JSON = ROOT / "intent_confusion_report.json"
OUT_MD = ROOT / "intent_confusion_report.md"


def load_report() -> list[dict]:
    with EVAL_REPORT.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["records"]


def build_confusion(records: list[dict]) -> list[dict]:
    """Group wrong-intent failures by (expected, predicted) pair."""

    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)

    for rec in records:
        if rec["behavior_match"]:
            continue
        expected = rec["expected_intent"]
        predicted = rec["predicted_intent"]
        if expected == predicted:
            continue  # correct intent, failure is clarification/law issue
        groups[(expected, predicted)].append(rec)

    pairs: list[dict] = []
    for (expected, predicted), recs in groups.items():
        freq = sum(r.get("source_frequency", 1) for r in recs)
        examples = [r["question"][:150] for r in recs[:5]]
        pairs.append({
            "expected_intent": expected,
            "predicted_intent": predicted,
            "count": len(recs),
            "total_frequency": freq,
            "examples": examples,
        })

    pairs.sort(key=lambda p: (-p["total_frequency"], -p["count"]))
    return pairs


def infer_fix(pair: dict) -> str:
    """Heuristic: suggest a fix type for a confusion pair."""

    expected = pair["expected_intent"]
    predicted = pair["predicted_intent"]

    # Common patterns
    if predicted == "unknown":
        return f"Add keyword hints for {expected} to INTENT_KEYWORD_HINTS (missing anchor words)."
    if expected == "out_of_scope" or expected == "education_community":
        return f"Add out_of_scope / community anchors so queries stop matching {predicted}."
    if predicted == "pit_ryczalt" and expected != "pit_ryczalt":
        return (
            f"The hint 'pit' in pit_ryczalt is overly broad — it captures "
            f"{expected} queries that mention PIT forms. Add disambiguating "
            f"hints to {expected} or narrow pit_ryczalt."
        )
    if predicted == "vat_jpk_ksef" and expected != "vat_jpk_ksef":
        return (
            f"Broad VAT hints ('faktura', 'nip') pull {expected} queries "
            f"into vat_jpk_ksef. Add stronger anchors for {expected}."
        )
    if predicted == "accounting_operational" and expected != "accounting_operational":
        return (
            f"Broad accounting hints pull {expected} queries into "
            f"accounting_operational. Add domain-specific anchors for {expected}."
        )
    if predicted == "education_community" and expected != "education_community":
        return (
            f"Community hints ('polecacie', 'jak zaczac') capture {expected} "
            f"queries. Add more specific anchors for {expected}."
        )
    if predicted == "business_of_accounting_office":
        return (
            f"Hints 'klient', 'biuro rachunkowe' are too broad and capture "
            f"{expected} queries. Add disambiguating hints for {expected}."
        )
    return (
        f"Add disambiguating keyword hints to separate {expected} from "
        f"{predicted}. Review overlapping tokens."
    )


def write_json(pairs: list[dict]) -> None:
    for p in pairs:
        p["suggested_fix"] = infer_fix(p)
    payload = {
        "total_wrong_intent_failures": sum(p["count"] for p in pairs),
        "total_confusion_pairs": len(pairs),
        "pairs": pairs,
    }
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_md(pairs: list[dict]) -> None:
    lines: list[str] = [
        "# Intent Confusion Report",
        "",
        f"Total wrong-intent failures: **{sum(p['count'] for p in pairs)}**",
        "",
        "## Top confusion pairs (ranked by total frequency)",
        "",
        "| # | Expected | Predicted | Count | Freq | Suggested fix |",
        "|---|----------|-----------|-------|------|---------------|",
    ]
    for i, p in enumerate(pairs[:20], 1):
        fix_short = p.get("suggested_fix", "")[:80]
        lines.append(
            f"| {i} | {p['expected_intent']} | {p['predicted_intent']} "
            f"| {p['count']} | {p['total_frequency']} | {fix_short} |"
        )

    lines.append("")
    lines.append("## Detailed examples (top 10 pairs)")
    lines.append("")
    for p in pairs[:10]:
        lines.append(
            f"### {p['expected_intent']} → {p['predicted_intent']} "
            f"({p['count']} records, freq={p['total_frequency']})"
        )
        lines.append("")
        for ex in p["examples"]:
            lines.append(f"- {ex}")
        lines.append("")
        lines.append(f"**Fix**: {p.get('suggested_fix', 'N/A')}")
        lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    records = load_report()
    pairs = build_confusion(records)
    write_json(pairs)
    write_md(pairs)

    print(f"Wrong-intent failures: {sum(p['count'] for p in pairs)}")
    print(f"Confusion pairs: {len(pairs)}")
    print()
    print("Top 10 confusion pairs:")
    for i, p in enumerate(pairs[:10], 1):
        print(
            f"  {i:2d}. {p['expected_intent']:28s} -> {p['predicted_intent']:28s}  "
            f"count={p['count']:2d}  freq={p['total_frequency']:3d}"
        )


if __name__ == "__main__":
    main()
