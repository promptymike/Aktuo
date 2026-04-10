from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FB_PATH = ROOT / "fb_pipeline" / "dedup_questions_output_v3.json"
OUTPUT_JSON = ROOT / "tests" / "output" / "missing_laws_impact.json"
OUTPUT_MD = ROOT / "analysis" / "missing_laws_impact.md"


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", without_accents).strip()


LAW_BUCKETS = {
    "ustawa_o_ryczalcie": {
        "label": "Ustawa o zryczałtowanym podatku dochodowym",
        "patterns": [
            r"\bryczalt\b",
            r"\bnajem\b",
        ],
    },
    "rozporzadzenie_o_kasach": {
        "label": "Rozporządzenie MF o kasach rejestrujących",
        "patterns": [
            r"\bkasa fiskalna\b",
            r"\bkasy fiskalne\b",
            r"\bzwolnienie z kasy\b",
            r"\bzwolnienie z kasy fiskalnej\b",
            r"\bkasa rejestrujaca\b",
            r"\bkasy rejestrujace\b",
        ],
    },
    "prawo_przedsiebiorcow": {
        "label": "Prawo przedsiębiorców",
        "patterns": [
            r"\bulga na start\b",
            r"\bzawieszenie dzialalnosci\b",
            r"\bzawiesic dzialalnosc\b",
            r"\bzawieszona dzialalnosc\b",
        ],
    },
}


def load_rows() -> list[dict[str, Any]]:
    payload = json.loads(FB_PATH.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return list(payload.get("questions", []))
    return list(payload)


def classify_question(question: str) -> list[str]:
    normalized = _normalize(question)
    matched: list[str] = []
    for bucket_key, bucket in LAW_BUCKETS.items():
        if any(re.search(pattern, normalized) for pattern in bucket["patterns"]):
            matched.append(bucket_key)
    return matched


def build_report() -> dict[str, Any]:
    rows = load_rows()
    bucket_rows: dict[str, list[dict[str, Any]]] = {key: [] for key in LAW_BUCKETS}
    all_missing_rows: list[dict[str, Any]] = []
    overlap_counter: Counter[str] = Counter()

    for row in rows:
        question = str(row.get("q", "")).strip()
        freq = int(row.get("freq", 1))
        cat = str(row.get("cat", "")).strip()
        matched_buckets = classify_question(question)
        if not matched_buckets:
            continue

        payload = {
            "question": question,
            "freq": freq,
            "cat": cat,
            "matched_buckets": matched_buckets,
        }
        all_missing_rows.append(payload)
        overlap_counter[" + ".join(sorted(matched_buckets))] += 1
        for bucket_key in matched_buckets:
            bucket_rows[bucket_key].append(payload)

    report: dict[str, Any] = {
        "meta": {
            "source_file": str(FB_PATH.relative_to(ROOT)),
            "total_rows": len(rows),
        },
        "per_missing_law": {},
        "union_missing_whole_law": {
            "unique_questions": len(all_missing_rows),
            "weighted_freq_sum": sum(row["freq"] for row in all_missing_rows),
        },
        "overlap_patterns": dict(overlap_counter),
    }

    for bucket_key, bucket in LAW_BUCKETS.items():
        matched_rows = bucket_rows[bucket_key]
        report["per_missing_law"][bucket_key] = {
            "label": bucket["label"],
            "unique_questions": len(matched_rows),
            "weighted_freq_sum": sum(row["freq"] for row in matched_rows),
            "top_source_categories": Counter(row["cat"] for row in matched_rows).most_common(8),
            "top_questions": sorted(matched_rows, key=lambda row: row["freq"], reverse=True)[:20],
        }

    return report


def build_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Missing Laws Impact Assessment")
    lines.append("")
    lines.append("| Brakujący akt | Unikalne pytania | Suma freq |")
    lines.append("| --- | ---: | ---: |")
    for details in report["per_missing_law"].values():
        lines.append(
            f"| {details['label']} | {details['unique_questions']} | {details['weighted_freq_sum']} |"
        )
    lines.append("")
    lines.append("## Łączny wpływ brakujących całych ustaw")
    lines.append("")
    lines.append(
        f"- Unikalne pytania trafiające w brak całej ustawy: "
        f"`{report['union_missing_whole_law']['unique_questions']}`"
    )
    lines.append(
        f"- Łączna suma wystąpień tych pytań (`freq`): "
        f"`{report['union_missing_whole_law']['weighted_freq_sum']}`"
    )
    lines.append("")
    lines.append("## Przykładowe pytania")
    lines.append("")
    for details in report["per_missing_law"].values():
        lines.append(f"### {details['label']}")
        lines.append("")
        for question in details["top_questions"][:10]:
            lines.append(f"- ({question['freq']}) {question['question']}")
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
