from __future__ import annotations

import importlib
import json
from pathlib import Path


def _reload_retriever_stack():
    """Reload settings, retriever and rag after environment changes."""

    import config.settings as settings
    import core.rag as rag
    import core.retriever as retriever

    settings = importlib.reload(settings)
    retriever = importlib.reload(retriever)
    rag = importlib.reload(rag)
    return settings, retriever, rag


def test_load_slang_map_missing_file(monkeypatch) -> None:
    """Missing slang files should disable expansion instead of failing."""

    monkeypatch.setenv("AKTUO_SLANG_FILE_PATH", str(Path("does-not-exist.json")))

    _, retriever, _ = _reload_retriever_stack()

    assert retriever.load_slang_map() == {}


def test_load_slang_map_malformed_json(tmp_path, monkeypatch) -> None:
    """Malformed slang JSON should be ignored with an empty fallback map."""

    slang_file = tmp_path / "slang_analysis.json"
    slang_file.write_text("{not valid}", encoding="utf-8")
    monkeypatch.setenv("AKTUO_SLANG_FILE_PATH", str(slang_file))

    _, retriever, _ = _reload_retriever_stack()

    assert retriever.load_slang_map() == {}


def test_query_expansion_with_slang(tmp_path, monkeypatch) -> None:
    """Slang expansion should influence retrieval when built-in shortcuts are disabled."""

    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o podatku dochodowym od osób prawnych",
                    "article_number": "art. 28j",
                    "category": "cit",
                    "verified_date": "2026-04-01",
                    "question_intent": "Kto może wybrać estoński CIT?",
                    "content": "Estoński CIT jest systemem opodatkowania przewidzianym dla podatników spełniających warunki ustawowe.",
                },
                {
                    "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
                    "article_number": "art. 26",
                    "category": "pit",
                    "verified_date": "2026-04-01",
                    "question_intent": "Jak rozliczyć dochód z jednoosobowej działalności gospodarczej?",
                    "content": "Dochód z jednoosobowej działalności gospodarczej podlega rozliczeniu według zasad właściwych dla podatnika.",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    slang_file = tmp_path / "slang_analysis.json"
    slang_file.write_text(
        json.dumps(
            [
                {
                    "slang": "jdg",
                    "expanded": "jednoosobowa działalność gospodarcza",
                    "freq": 10,
                },
                {
                    "slang": "estończyk",
                    "expanded": "estoński CIT",
                    "freq": 5,
                },
                {
                    "slang": "pit11",
                    "expanded": "PIT-11",
                    "freq": 3,
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("AKTUO_SLANG_FILE_PATH", str(slang_file))

    _, retriever, rag = _reload_retriever_stack()
    monkeypatch.setattr(retriever, "CATEGORY_SYNONYM_MAP", {})
    monkeypatch.setattr(
        rag,
        "generate_answer",
        lambda query, chunks, system_prompt, api_key: "Mocked answer",
    )
    monkeypatch.setattr(rag, "is_low_confidence_retrieval", lambda chunks: False)
    monkeypatch.setattr(
        rag,
        "audit_answer",
        lambda answer, chunks: {"grounded": True, "context_count": len(chunks)},
    )

    result = rag.answer_query(
        query="Estończyk i jdg w pit11",
        knowledge_path=seed_file,
        system_prompt="Jesteś Aktuo.",
        api_key="test-key",
    )

    assert result.category in {"cit", "pit"}
    assert result.chunks
    assert any(
        chunk.law_name
        in {
            "Ustawa o podatku dochodowym od osób prawnych",
            "Ustawa o podatku dochodowym od osób fizycznych",
        }
        for chunk in result.chunks
    )


def test_query_expansion_deduplication(tmp_path, monkeypatch) -> None:
    """Expanded queries should still return unique chunks when duplicates exist."""

    seed_file = tmp_path / "law_knowledge.json"
    duplicate_unit = {
        "law_name": "Ustawa o podatku dochodowym od osób prawnych",
        "article_number": "art. 28j",
        "category": "cit",
        "verified_date": "2026-04-01",
        "question_intent": "Kto może wybrać estoński CIT?",
        "content": "Estoński CIT jest systemem opodatkowania przewidzianym dla podatników spełniających warunki ustawowe.",
    }
    seed_file.write_text(
        json.dumps([duplicate_unit, duplicate_unit], ensure_ascii=False),
        encoding="utf-8",
    )

    slang_file = tmp_path / "slang_analysis.json"
    slang_file.write_text(
        json.dumps(
            [
                {
                    "slang": "estończyk",
                    "expanded": "estoński CIT",
                    "freq": 5,
                },
                {
                    "slang": "estończyk",
                    "expanded": "estoński CIT",
                    "freq": 4,
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("AKTUO_SLANG_FILE_PATH", str(slang_file))

    _, retriever, rag = _reload_retriever_stack()
    monkeypatch.setattr(retriever, "CATEGORY_SYNONYM_MAP", {})
    monkeypatch.setattr(
        rag,
        "generate_answer",
        lambda query, chunks, system_prompt, api_key: "Mocked answer",
    )
    monkeypatch.setattr(rag, "is_low_confidence_retrieval", lambda chunks: False)
    monkeypatch.setattr(
        rag,
        "audit_answer",
        lambda answer, chunks: {"grounded": True, "context_count": len(chunks)},
    )

    result = rag.answer_query(
        query="estończyk",
        knowledge_path=seed_file,
        system_prompt="Jesteś Aktuo.",
        api_key="test-key",
    )

    assert len(result.chunks) == 1
