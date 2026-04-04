from __future__ import annotations

import json

from core.rag import answer_query


def test_answer_query_returns_grounded_result(tmp_path, monkeypatch) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Housing Act",
                    "article_number": "Art. 10",
                    "category": "housing",
                    "verified_date": "2026-04-01",
                    "content": "A tenant can request an explanation for a withheld security deposit.",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr("core.rag.generate_answer", lambda query, chunks, system_prompt, api_key: "Mocked answer")

    result = answer_query(
        query="Anna Nowak says the landlord kept my deposit.",
        knowledge_path=seed_file,
        system_prompt="You are Aktuo.",
        api_key="test-key",
    )

    assert result.audit["grounded"] is True
    assert result.chunks[0].law_name == "Housing Act"
    assert "[PERSON]" in result.redacted_query
