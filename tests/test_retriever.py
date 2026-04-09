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
                    "question_intent": "Jakie elementy powinna zawierać faktura?",
                    "content": "Faktura powinna zawierać podstawowe dane sprzedawcy i nabywcy.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 99",
                    "category": "terminy",
                    "verified_date": "2026-04-01",
                    "question_intent": "Jaki jest termin złożenia deklaracji JPK_V7?",
                    "content": "Deklarację JPK_V7 składa się w ustawowym terminie za dany okres.",
                },
            ]
        ),
        encoding="utf-8",
    )

    chunks = retrieve_chunks("Jaki jest termin złożenia deklaracji JPK_V7?", seed_file, limit=1)

    assert len(chunks) == 1
    assert chunks[0].article_number == "art. 99"


def test_retrieve_chunks_returns_top_five_results_for_bm25_query(tmp_path) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106e",
                    "category": "fakturowanie",
                    "verified_date": "2026-04-01",
                    "question_intent": "Co musi zawierać faktura?",
                    "content": "Faktura powinna zawierać numer oraz datę wystawienia.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106h",
                    "category": "faktury",
                    "verified_date": "2026-04-02",
                    "question_intent": "Kiedy można wystawić fakturę do paragonu?",
                    "content": "Fakturę można wystawić do paragonu fiskalnego w określonych przypadkach.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106i",
                    "category": "fakturowanie",
                    "verified_date": "2026-04-03",
                    "question_intent": "Jaki jest termin wystawienia faktury?",
                    "content": "Termin wystawienia faktury zależy od rodzaju transakcji.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 99",
                    "category": "terminy",
                    "verified_date": "2026-04-01",
                    "question_intent": "Kiedy składa się deklaracje VAT?",
                    "content": "Deklaracje podatkowe składa się miesięcznie albo kwartalnie.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 86",
                    "category": "podatek_naliczony",
                    "verified_date": "2026-04-04",
                    "question_intent": "Kiedy można odliczyć VAT naliczony?",
                    "content": "Podatek naliczony można odliczyć, jeśli zakup służy czynnościom opodatkowanym.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 19a",
                    "category": "podatek_należny",
                    "verified_date": "2026-04-05",
                    "question_intent": "Kiedy powstaje obowiązek podatkowy w VAT?",
                    "content": "Obowiązek podatkowy powstaje z chwilą dokonania dostawy towarów lub wykonania usługi.",
                },
            ]
        ),
        encoding="utf-8",
    )

    chunks = retrieve_chunks("Kiedy trzeba wystawić fakturę i co powinna zawierać?", seed_file)

    assert len(chunks) == 5
    top_three = {chunk.article_number for chunk in chunks[:3]}
    assert "art. 106h" in top_three
    assert {"art. 106e", "art. 106i"} & top_three
