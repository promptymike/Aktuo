from __future__ import annotations

import json

from streamlit.testing.v1 import AppTest

import app.main as app_main
from core.rag import RagResult

def test_chat_ui_renders_clarification_prompts(monkeypatch, tmp_path) -> None:
    """The chat UI should surface user-friendly clarification prompts."""

    prompts_path = tmp_path / "clarification_slots.json"
    prompts_path.write_text(
        json.dumps(
            {
                "slot_prompts": {
                    "okres_lub_data": "Podaj okres lub datę (od–do).",
                    "forma_opodatkowania": "Jaka jest forma opodatkowania?",
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    answer_calls: list[str] = []
    generator_calls = {"count": 0}

    def fake_answer_query(query: str, knowledge_path: str, system_prompt: str, api_key: str) -> RagResult:  # noqa: ARG001
        answer_calls.append(query)
        return RagResult(
            answer="Potrzebuję doprecyzowania, zanim odpowiem.",
            chunks=[],
            audit={"grounded": False},
            redacted_query=query,
            category="vat",
            needs_clarification=True,
            missing_slots=["okres_lub_data", "forma_opodatkowania"],
            no_match_reason="clarification_required",
        )

    def fail_generator(*args, **kwargs):  # noqa: ANN002, ANN003
        generator_calls["count"] += 1
        raise AssertionError("generator should not be called for clarification flow")

    monkeypatch.setattr(app_main, "answer_query", fake_answer_query)
    monkeypatch.setattr(app_main, "CLARIFICATION_PROMPTS_PATH", str(prompts_path))
    app_main.load_clarification_prompts.cache_clear()

    import core.generator as generator

    monkeypatch.setattr(generator, "generate_answer", fail_generator)

    at = AppTest.from_string(
        """
import streamlit as st
import app.main as app_main
from app.chat import render_chat_history

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = "test-session"
if "user_email" not in st.session_state:
    st.session_state.user_email = "tester@example.com"

clarification_prompts = app_main.load_clarification_prompts(app_main.CLARIFICATION_PROMPTS_PATH)
render_chat_history(
    st.session_state.messages,
    session_id=st.session_state.session_id,
    user_email=st.session_state.user_email,
    clarification_prompts=clarification_prompts,
)

question = st.chat_input("Zadaj pytanie")
if question:
    result = app_main.answer_query(
        query=question,
        knowledge_path="unused.json",
        system_prompt="unused",
        api_key="unused",
    )
    st.session_state.messages.extend(
        [
            {"role": "user", "content": question, "timestamp": "2026-04-12T09:00:00+02:00"},
            {
                "role": "assistant",
                "result": result,
                "query": question,
                "timestamp": "2026-04-12T09:00:00+02:00",
            },
        ]
    )
    st.rerun()
"""
    )
    at.session_state["messages"] = []

    at.run()
    at.chat_input[0].set_value("Jak rozliczyć VAT?").run()

    markdown_values = [element.value for element in at.markdown]
    warning_values = [element.value for element in at.warning]

    assert answer_calls == ["Jak rozliczyć VAT?"]
    assert generator_calls["count"] == 0
    assert any("Podaj okres lub datę (od–do)." in value for value in markdown_values)
    assert any("Jaka jest forma opodatkowania?" in value for value in markdown_values)
    assert any("potrzebuję jeszcze kilku informacji" in value.lower() for value in warning_values)
