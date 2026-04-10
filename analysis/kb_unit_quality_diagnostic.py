"""KB unit quality diagnostic — classifies units as processed (A) vs raw (B)."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.categorizer import categorize_query  # noqa: E402
from core.retriever import retrieve_chunks  # noqa: E402

KB_PATH = ROOT / "data" / "seeds" / "law_knowledge.json"
OUTPUT_MD = ROOT / "analysis" / "kb_unit_quality_diagnostic.md"

PROCESSED_WORDS = re.compile(
    r"oznacza|wynosi|obowi[aą]zek|termin|nale[żz]y|przys[łl]uguje|podlega",
    re.IGNORECASE,
)
RAW_START = re.compile(r"^(\d+[\.\)]\s|Art\.\s|§\s)")
LEGAL_REF = re.compile(
    r"o kt[oó]rym mowa w art\.|z zastrze[żz]eniem ust\.|w rozumieniu art\.|na podstawie art\.",
    re.IGNORECASE,
)

TEST_QUERIES = [
    {
        "query": "Przeliczenie wynagrodzenia w euro na PLN jaki kurs",
        "expected_article": "art. 11a",
    },
    {
        "query": "Ulga dla seniora czy przysługuje",
        "expected_article": "art. 21 ust. 1 pkt 154",
    },
]


def classify(entry: dict) -> str:
    content = entry.get("content", "")
    if len(content) < 100:
        return "B"
    if RAW_START.match(content):
        return "B"
    if len(LEGAL_REF.findall(content)) >= 3:
        return "B"
    if PROCESSED_WORDS.search(content) and len(content) > 150:
        return "A"
    return "B"


def preview(text: str, limit: int = 200) -> str:
    compact = " ".join(text.split())
    return compact[:limit] + "..." if len(compact) > limit else compact


def main() -> None:
    with open(KB_PATH, encoding="utf-8") as f:
        kb = json.load(f)

    classified = [(classify(e), e) for e in kb]
    type_a = [e for t, e in classified if t == "A"]
    type_b = [e for t, e in classified if t == "B"]

    law_a = Counter(e["law_name"] for e in type_a)
    law_b = Counter(e["law_name"] for e in type_b)
    all_laws = sorted(set(list(law_a.keys()) + list(law_b.keys())))

    lines = [
        "# KB Unit Quality Diagnostic",
        "",
        f"- Total units: **{len(kb)}**",
        f"- TYP A (przetworzone): **{len(type_a)}** ({round(100*len(type_a)/len(kb))}%)",
        f"- TYP B (surowe): **{len(type_b)}** ({round(100*len(type_b)/len(kb))}%)",
        "",
        "## Breakdown per ustawa",
        "",
        "| Ustawa | TYP A | TYP B | Razem | % A |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for law in all_laws:
        a = law_a.get(law, 0)
        b = law_b.get(law, 0)
        total = a + b
        pct = round(100 * a / total) if total else 0
        lines.append(f"| {law} | {a} | {b} | {total} | {pct}% |")
    lines.append(f"| **SUMA** | **{len(type_a)}** | **{len(type_b)}** | **{len(kb)}** | **{round(100*len(type_a)/len(kb))}%** |")
    lines.append("")

    import random
    random.seed(42)

    lines.append("## 5 przykładów TYP A (dobre)")
    lines.append("")
    for i, e in enumerate(random.sample(type_a, min(5, len(type_a))), 1):
        lines.append(f"**A{i}.** `{e['law_name']}` | `{e['article_number']}` | cat=`{e['category']}` | {len(e['content'])} zn.")
        lines.append(f"> {preview(e['content'])}")
        lines.append("")

    lines.append("## 5 przykładów TYP B (surowe)")
    lines.append("")
    for i, e in enumerate(random.sample(type_b, min(5, len(type_b))), 1):
        lines.append(f"**B{i}.** `{e['law_name']}` | `{e['article_number']}` | cat=`{e['category']}` | {len(e['content'])} zn.")
        lines.append(f"> {preview(e['content'])}")
        lines.append("")

    lines.append("## Retriever tests")
    lines.append("")
    for tq in TEST_QUERIES:
        q = tq["query"]
        cat = categorize_query(q)
        chunks = retrieve_chunks(q, KB_PATH, limit=5)
        lines.append(f"### {q}")
        lines.append(f"- Kategoria: `{cat}`")
        lines.append(f"- Oczekiwany artykuł: `{tq['expected_article']}`")
        hit = any(tq["expected_article"] in c.article_number for c in chunks)
        lines.append(f"- Trafienie w top 5: **{'TAK' if hit else 'NIE'}**")
        lines.append("")
        lines.append("| # | Ustawa | Artykuł | Kategoria | Score | Preview |")
        lines.append("| ---: | --- | --- | --- | ---: | --- |")
        for i, c in enumerate(chunks, 1):
            p = preview(c.content, 140)
            lines.append(f"| {i} | `{c.law_name}` | `{c.article_number}` | `{c.category}` | {c.score:.4f} | {p} |")
        lines.append("")

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {OUTPUT_MD}")
    print()
    print(f"Total: {len(kb)} | A: {len(type_a)} ({round(100*len(type_a)/len(kb))}%) | B: {len(type_b)} ({round(100*len(type_b)/len(kb))}%)")


if __name__ == "__main__":
    main()
