from __future__ import annotations

import json

from core.retriever import retrieve_chunks


def test_retrieve_chunks_prefers_matching_category(tmp_path) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Housing Act",
                    "article_number": "Art. 10",
                    "category": "housing",
                    "verified_date": "2026-04-01",
                    "content": "A landlord should explain security deposit deductions after move out.",
                },
                {
                    "law_name": "Labor Code",
                    "article_number": "Art. 3",
                    "category": "employment",
                    "verified_date": "2026-04-01",
                    "content": "An employer should explain wage deductions to an employee.",
                },
            ]
        ),
        encoding="utf-8",
    )

    chunks = retrieve_chunks("My landlord kept my deposit after the lease ended.", seed_file, limit=1)

    assert len(chunks) == 1
    assert chunks[0].law_name == "Housing Act"


def test_retrieve_chunks_returns_top_three_results(tmp_path) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Housing Act",
                    "article_number": "Art. 10",
                    "category": "housing",
                    "verified_date": "2026-04-01",
                    "content": "A landlord should explain deposit deductions after move out.",
                },
                {
                    "law_name": "Tenant Guidance",
                    "article_number": "Art. 11",
                    "category": "housing",
                    "verified_date": "2026-04-02",
                    "content": "A tenant can request deposit records and receipts.",
                },
                {
                    "law_name": "Lease Rules",
                    "article_number": "Art. 12",
                    "category": "housing",
                    "verified_date": "2026-04-03",
                    "content": "Lease disputes can involve withheld deposit funds.",
                },
                {
                    "law_name": "Labor Code",
                    "article_number": "Art. 3",
                    "category": "employment",
                    "verified_date": "2026-04-01",
                    "content": "Wage deductions should be explained to employees.",
                },
            ]
        ),
        encoding="utf-8",
    )

    chunks = retrieve_chunks("My landlord kept my deposit after the lease ended.", seed_file)

    assert len(chunks) == 3
