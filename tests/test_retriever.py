from __future__ import annotations

import json

from core.retriever import retrieve_chunks


def test_retrieve_chunks_prefers_matching_polish_category(tmp_path) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106e",
                    "category": "fakturowanie",
                    "verified_date": "2026-04-01",
                    "content": "Faktura powinna zawierać podstawowe dane sprzedawcy i nabywcy.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 99",
                    "category": "terminy",
                    "verified_date": "2026-04-01",
                    "content": "Deklarację JPK_V7 składa się w ustawowym terminie za dany okres.",
                },
            ]
        ),
        encoding="utf-8",
    )

    chunks = retrieve_chunks("Jaki jest termin złożenia deklaracji JPK_V7?", seed_file, limit=1)

    assert len(chunks) == 1
    assert chunks[0].article_number == "art. 99"


def test_retrieve_chunks_returns_top_three_results_for_polish_query(tmp_path) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106e",
                    "category": "fakturowanie",
                    "verified_date": "2026-04-01",
                    "content": "Faktura powinna zawierać numer oraz datę wystawienia.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106h",
                    "category": "faktury",
                    "verified_date": "2026-04-02",
                    "content": "Fakturę można wystawić do paragonu fiskalnego w określonych przypadkach.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106i",
                    "category": "fakturowanie",
                    "verified_date": "2026-04-03",
                    "content": "Termin wystawienia faktury zależy od rodzaju transakcji.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 99",
                    "category": "terminy",
                    "verified_date": "2026-04-01",
                    "content": "Deklaracje podatkowe składa się miesięcznie albo kwartalnie.",
                },
            ]
        ),
        encoding="utf-8",
    )

    chunks = retrieve_chunks("Kiedy trzeba wystawić fakturę i co powinna zawierać?", seed_file)

    assert len(chunks) == 3
    assert all(chunk.category in {"fakturowanie", "faktury"} for chunk in chunks)
