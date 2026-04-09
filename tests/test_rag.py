from __future__ import annotations

import json

from core.rag import answer_query


def test_answer_query_returns_grounded_result_for_polish_question(tmp_path, monkeypatch) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106j ust. 1 pkt 5",
                    "category": "faktury_korygujące",
                    "verified_date": "2026-04-01",
                    "content": "Pomyłka w NIP-ie na fakturze wymaga wystawienia faktury korygującej.",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr("core.rag.generate_answer", lambda query, chunks, system_prompt, api_key: "Mocked answer")
    monkeypatch.setattr("core.rag.is_low_confidence_retrieval", lambda chunks: False)

    result = answer_query(
        query="Jan Kowalski pyta, czy błędny NIP na fakturze wymaga korekty.",
        knowledge_path=seed_file,
        system_prompt="Jesteś Aktuo.",
        api_key="test-key",
    )

    assert result.audit["grounded"] is True
    assert result.category == "faktury_korygujące"
    assert result.chunks[0].law_name == "Ustawa o VAT"
    assert "[PERSON]" in result.redacted_query


def test_answer_query_marks_low_confidence_retrieval(tmp_path, monkeypatch) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 1",
                    "category": "vat",
                    "verified_date": "2026-04-01",
                    "content": "Przepis ogólny o podatku od towarów i usług.",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "core.rag.generate_answer",
        lambda query, chunks, system_prompt, api_key: "Nie znalazłem odpowiedzi w dostępnej bazie przepisów.",
    )
    monkeypatch.setattr("core.rag.is_low_confidence_retrieval", lambda chunks: True)

    result = answer_query(
        query="Jak rozliczyć cło importowe?",
        knowledge_path=seed_file,
        system_prompt="Jesteś Aktuo.",
        api_key="test-key",
    )

    assert result.audit["grounded"] is False
    assert result.no_match_reason == "low_bm25_score"
