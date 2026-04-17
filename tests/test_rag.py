from __future__ import annotations

import json
import pytest

from core.generator import GenerationMetrics
from core.rag import _count_context_tokens, answer_query
from core.retriever import LawChunk, QueryAnalysis, RetrievalResult


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
        query="Jan Kowalski pyta, czy błędny NIP na fakturze sprzedawcy z marca 2026 wymaga korekty.",
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
        query="Jak rozliczyć cło importowe na fakturze podatnika za marzec 2026?",
        knowledge_path=seed_file,
        system_prompt="Jesteś Aktuo.",
        api_key="test-key",
    )

    assert result.audit["grounded"] is False
    assert result.no_match_reason == "low_bm25_score"


@pytest.mark.parametrize("query", [None, "   "])
def test_answer_query_rejects_none_or_empty_query(query, tmp_path) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError):
        answer_query(
            query=query,  # type: ignore[arg-type]
            knowledge_path=seed_file,
            system_prompt="Jestes Aktuo.",
            api_key="test-key",
        )


def test_answer_query_handles_very_long_query(tmp_path, monkeypatch) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 86 ust. 1",
                    "category": "vat",
                    "verified_date": "2026-04-01",
                    "content": "Podatnik ma prawo do odliczenia podatku naliczonego w zakresie wykorzystania do czynnosci opodatkowanych.",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr("core.rag.generate_answer", lambda query, chunks, system_prompt, api_key: "Mocked answer")
    monkeypatch.setattr("core.rag.is_low_confidence_retrieval", lambda chunks: False)
    monkeypatch.setattr(
        "core.rag.analyze_query_requirements",
        lambda query: QueryAnalysis(intent="vat_jpk_ksef", missing_slots=[], needs_clarification=False),
    )
    monkeypatch.setattr(
        "core.rag.retrieve",
        lambda query, knowledge_path, limit=5: RetrievalResult(
            chunks=[
                LawChunk(
                    content="Podatnik ma prawo do odliczenia podatku naliczonego w zakresie wykorzystania do czynnosci opodatkowanych.",
                    law_name="Ustawa o VAT",
                    article_number="art. 86 ust. 1",
                    category="vat",
                    verified_date="2026-04-01",
                )
            ],
            intent="vat_jpk_ksef",
        ),
    )

    result = answer_query(
        query=("Jak rozliczyc VAT? " * 700).strip(),
        knowledge_path=seed_file,
        system_prompt="Jestes Aktuo.",
        api_key="test-key",
    )

    assert result.answer == "Mocked answer"
    assert result.category == "vat"


@pytest.mark.parametrize(
    "query",
    [
        "😀 Czy faktura korygujaca sprzedawcy za marzec 2026 wymaga nowego numeru?",
        "Can a Polish taxpayer deduct VAT from a March 2026 invoice?",
    ],
)
def test_answer_query_handles_emoji_and_foreign_language_queries(query, tmp_path, monkeypatch) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106j",
                    "category": "faktury_korygujace",
                    "verified_date": "2026-04-01",
                    "content": "Fakture korygujaca wystawia sie w razie pomylki w jakiejkolwiek pozycji faktury.",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr("core.rag.generate_answer", lambda query, chunks, system_prompt, api_key: "Mocked answer")
    monkeypatch.setattr("core.rag.is_low_confidence_retrieval", lambda chunks: False)

    result = answer_query(
        query=query,
        knowledge_path=seed_file,
        system_prompt="Jestes Aktuo.",
        api_key="test-key",
    )

    assert result.answer == "Mocked answer"


def test_answer_query_triggers_context_summarization_when_context_is_too_long(tmp_path, monkeypatch) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    long_content = " ".join(["przepis"] * 120)
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 86",
                    "category": "vat",
                    "verified_date": "2026-04-01",
                    "content": long_content,
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 87",
                    "category": "vat",
                    "verified_date": "2026-04-01",
                    "content": long_content,
                },
            ]
        ),
        encoding="utf-8",
    )

    summarize_calls: list[str] = []

    monkeypatch.setattr("core.rag.MAX_CONTEXT_TOKENS", 40)
    monkeypatch.setattr(
        "core.rag.summarize_context",
        lambda query, chunks, system_prompt, api_key, max_words=150: summarize_calls.append(chunks[0].article_number) or f"Krotkie streszczenie {chunks[0].article_number}",
    )
    monkeypatch.setattr("core.rag.get_last_generation_metrics", lambda: GenerationMetrics())
    monkeypatch.setattr("core.rag.generate_answer", lambda query, chunks, system_prompt, api_key: "Mocked answer")
    monkeypatch.setattr("core.rag.is_low_confidence_retrieval", lambda chunks: False)
    monkeypatch.setattr("core.rag.audit_answer", lambda answer, chunks: {"grounded": True})
    monkeypatch.setattr(
        "core.rag.analyze_query_requirements",
        lambda query: QueryAnalysis(intent="vat_jpk_ksef", missing_slots=[], needs_clarification=False),
    )
    monkeypatch.setattr(
        "core.rag.retrieve",
        lambda query, knowledge_path, limit=5: RetrievalResult(
            chunks=[
                LawChunk(
                    content=long_content,
                    law_name="Ustawa o VAT",
                    article_number="art. 86",
                    category="vat",
                    verified_date="2026-04-01",
                ),
                LawChunk(
                    content=long_content,
                    law_name="Ustawa o VAT",
                    article_number="art. 87",
                    category="vat",
                    verified_date="2026-04-01",
                ),
            ],
            intent="vat_jpk_ksef",
        ),
    )

    result = answer_query(
        query="Jak rozliczyc VAT?",
        knowledge_path=seed_file,
        system_prompt="Jestes Aktuo.",
        api_key="test-key",
    )

    assert result.answer == "Mocked answer"
    assert set(summarize_calls) == {"art. 86", "art. 87"}
    assert all(chunk.content.startswith("Krotkie streszczenie") for chunk in result.chunks)


def test_answer_query_shortened_context_fits_under_limit(tmp_path, monkeypatch) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    long_content = " ".join(["obowiazek"] * 100)
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 19a",
                    "category": "vat",
                    "verified_date": "2026-04-01",
                    "content": long_content,
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 29a",
                    "category": "vat",
                    "verified_date": "2026-04-01",
                    "content": long_content,
                },
            ]
        ),
        encoding="utf-8",
    )

    captured_context_sizes: list[int] = []

    monkeypatch.setattr("core.rag.MAX_CONTEXT_TOKENS", 30)
    monkeypatch.setattr(
        "core.rag.summarize_context",
        lambda query, chunks, system_prompt, api_key, max_words=150: "zwięzłe streszczenie przepisu z artykułem",
    )
    monkeypatch.setattr("core.rag.get_last_generation_metrics", lambda: GenerationMetrics())

    def fake_generate_answer(query, chunks, system_prompt, api_key):
        captured_context_sizes.append(_count_context_tokens(chunks))
        return "Mocked answer"

    monkeypatch.setattr("core.rag.generate_answer", fake_generate_answer)
    monkeypatch.setattr("core.rag.is_low_confidence_retrieval", lambda chunks: False)
    monkeypatch.setattr("core.rag.audit_answer", lambda answer, chunks: {"grounded": True})

    result = answer_query(
        query="Kiedy powstaje obowiazek podatkowy VAT przy sprzedazy fakturami nabywcy za marzec 2026?",
        knowledge_path=seed_file,
        system_prompt="Jestes Aktuo.",
        api_key="test-key",
    )

    assert result.answer == "Mocked answer"
    assert captured_context_sizes
    assert captured_context_sizes[0] <= 30


def test_answer_query_keeps_legal_clarification_behavior_for_missing_legal_facts(tmp_path, monkeypatch) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(
        "core.rag.analyze_query_requirements",
        lambda query: QueryAnalysis(
            intent="legal_substantive",
            missing_slots=["stan_faktyczny"],
            needs_clarification=True,
        ),
    )

    result = answer_query(
        query="Czy mogę tak zrobić w VAT?",
        knowledge_path=seed_file,
        system_prompt="Jesteś Aktuo.",
        api_key="test-key",
    )

    assert result.needs_clarification is True
    assert result.retrieval_path == "clarification"
    assert result.partial_answer is False
    assert "Potrzebuj" in result.answer
