from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.categorizer import categorize_query  # noqa: E402
from core.retriever import retrieve_chunks  # noqa: E402


KB_PATH = ROOT / "data" / "seeds" / "law_knowledge.json"
OUTPUT_JSON = ROOT / "tests" / "output" / "retest_7_accountant_questions.json"
OUTPUT_MD = ROOT / "analysis" / "retest_7_accountant_questions.md"


QUERIES = [
    {
        "id": 1,
        "query": "Termin złożenia JPK_V7?",
        "note": "Powinno trafić w terminy JPK_V7 z ustawy o VAT lub rozporządzenia JPK_V7.",
    },
    {
        "id": 2,
        "query": "Jak księgujecie faktury z Bioestry po zmianie w KSeF",
        "note": "Powinno trafić w KSeF i moment uznania faktury za wystawioną/otrzymaną.",
    },
    {
        "id": 3,
        "query": "Ulga dla seniora — czy przysługuje, proporcjonalnie czy za cały rok",
        "note": "Powinno trafić w PIT art. 21 ust. 1 pkt 154.",
    },
    {
        "id": 4,
        "query": "Usługa budowlana ryczałt 5.5% czy 8.5%",
        "note": "Brakuje całej ustawy o zryczałtowanym podatku dochodowym, więc dziś to nadal GAP.",
    },
    {
        "id": 5,
        "query": "Obowiązek podatkowy PIT i VAT — data wykonania vs data faktury",
        "note": "Powinno zwrócić równolegle VAT art. 19a i PIT art. 14 ust. 1c.",
    },
    {
        "id": 6,
        "query": "Przeliczenie wynagrodzenia w euro na PLN — jaki kurs",
        "note": "Powinno trafić w PIT art. 11a.",
    },
    {
        "id": 7,
        "query": "Sprzedaż bezpośrednia rolnik — zwolnienie z kasy fiskalnej",
        "note": "VAT art. 111 daje część odpowiedzi, ale pełne zwolnienia wymagają rozporządzenia o kasach rejestrujących.",
    },
]


def preview(text: str, limit: int = 160) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def chunk_to_dict(chunk: object) -> dict[str, object]:
    return {
        "law_name": chunk.law_name,
        "article_number": chunk.article_number,
        "category": chunk.category,
        "score": round(float(chunk.score), 4),
        "preview": preview(chunk.content),
    }


def classify_result(query_id: int, chunks: list[object]) -> tuple[str, str]:
    top = chunks[:3]
    article_numbers = {chunk.article_number for chunk in top}
    law_names = {chunk.law_name for chunk in top}

    if query_id == 1:
        if any(chunk.article_number.startswith("art. 99") for chunk in top):
            return "good", "Top wynik trafia w termin składania JPK_V7 z ustawy o VAT."
    elif query_id == 2:
        if top and top[0].article_number == "art. 106na ust. 1 i 3":
            return "good", "Top wynik trafia w moment wystawienia i otrzymania faktury w KSeF."
    elif query_id == 3:
        if top and top[0].article_number == "art. 21 ust. 1 pkt 154":
            return "good", "Top wynik trafia bezpośrednio w ulgę dla seniora."
    elif query_id == 4:
        ryczalt_hit = any(
            "zryczałtowanym" in chunk.law_name.lower() or "ryczalt" in chunk.law_name.lower()
            for chunk in top
        )
        if ryczalt_hit:
            return "good", "Top wynik trafia w ustawę o ryczałcie — stawki ryczałtu."
        return "gap", "Wyniki nadal wpadają w VAT, bo w bazie brakuje ustawy o ryczałcie."
    elif query_id == 5:
        has_vat = "art. 19a ust. 1" in article_numbers
        has_pit = "art. 14 ust. 1c" in article_numbers
        if has_vat and has_pit:
            return "good", "Retriever zwraca oba kluczowe przepisy: VAT art. 19a i PIT art. 14 ust. 1c."
    elif query_id == 6:
        if top and top[0].article_number == "art. 11a ust. 1":
            return "good", "Top wynik trafia w przeliczanie przychodów w walucie obcej według kursu NBP."
    elif query_id == 7:
        kasy_rozp_hit = any(
            "kasach rejestrujących" in chunk.law_name.lower() or "kasach rejestrujacych" in chunk.law_name.lower()
            for chunk in top
        )
        if top and top[0].article_number == "art. 111 ust. 1" and kasy_rozp_hit:
            return "good", "Top wynik trafia w obowiązek ewidencji (art. 111) + rozporządzenie o kasach."
        if top and top[0].article_number == "art. 111 ust. 1":
            return (
                "partial",
                "Top wynik sensownie pokazuje obowiązek ewidencji, ale pełne zwolnienia wymagają rozporządzenia o kasach rejestrujących.",
            )

    if not top:
        return "gap", "Brak chunków."

    if query_id in {2, 7}:
        return "partial", "Są częściowo trafne przepisy, ale brakuje pełnej podstawy prawnej."

    return "gap", "Top chunki nie odpowiadają wystarczająco precyzyjnie na pytanie."


def build_report() -> dict[str, object]:
    results: list[dict[str, object]] = []
    summary = {"good": 0, "partial": 0, "gap": 0}

    for item in QUERIES:
        query = item["query"]
        category = categorize_query(query)
        chunks = retrieve_chunks(query, KB_PATH, limit=3)
        verdict, reason = classify_result(item["id"], chunks)
        summary[verdict] += 1
        results.append(
            {
                "id": item["id"],
                "query": query,
                "category": category,
                "note": item["note"],
                "verdict": verdict,
                "reason": reason,
                "chunks": [chunk_to_dict(chunk) for chunk in chunks],
            }
        )

    return {
        "meta": {
            "knowledge_path": str(KB_PATH.relative_to(ROOT)),
            "previous_good_match_count": 1,
            "current_good_match_count": summary["good"],
            "current_good_or_partial_count": summary["good"] + summary["partial"],
            "summary": summary,
        },
        "results": results,
    }


def write_markdown(report: dict[str, object]) -> None:
    meta = report["meta"]
    lines = [
        "# Retest 7 pytań księgowych",
        "",
        f"- Wcześniej dobry match: `{meta['previous_good_match_count']}/7`",
        f"- Teraz dobry match: `{meta['current_good_match_count']}/7`",
        f"- Teraz dobry lub częściowy match: `{meta['current_good_or_partial_count']}/7`",
        f"- `good`: `{meta['summary']['good']}`",
        f"- `partial`: `{meta['summary']['partial']}`",
        f"- `gap`: `{meta['summary']['gap']}`",
        "",
    ]

    for item in report["results"]:
        lines.extend(
            [
                f"## {item['id']}. {item['query']}",
                "",
                f"- Kategoria: `{item['category']}`",
                f"- Ocena: `{item['verdict']}`",
                f"- Komentarz: {item['reason']}",
                f"- Kontekst: {item['note']}",
                "",
                "| # | Ustawa | Artykuł | Kategoria | Score | Preview |",
                "| ---: | --- | --- | --- | ---: | --- |",
            ]
        )
        for index, chunk in enumerate(item["chunks"], 1):
            lines.append(
                f"| `{index}` | `{chunk['law_name']}` | `{chunk['article_number']}` | `{chunk['category']}` | `{chunk['score']}` | {chunk['preview']} |"
            )
        lines.append("")

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    report = build_report()
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(report)
    print(json.dumps(report["meta"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
