from __future__ import annotations

import json

from streamlit.testing.v1 import AppTest

import app.main as app_main
from core.rag import RagResult


def test_clarification_chips_render_and_submit_followup(monkeypatch, tmp_path) -> None:
    """Chip buttons should render from JSON and submit only the selected slot value."""

    prompts_path = tmp_path / "clarification_slots.json"
    prompts_path.write_text(
        json.dumps(
            {
                "slot_prompts": {
                    "okres_lub_data": "Podaj okres lub datę.",
                    "forma_opodatkowania": "Jaka jest forma opodatkowania?",
                },
                "slot_chip_options": {
                    "forma_opodatkowania": ["ryczałt", "liniowy", "zasady ogólne"]
                },
                "slot_display_labels": {
                    "forma_opodatkowania": "Forma opodatkowania"
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    answer_calls: list[str] = []

    def fake_answer_query(query: str, knowledge_path: str, system_prompt: str, api_key: str) -> RagResult:  # noqa: ARG001
        answer_calls.append(query)
        if "ryczałt" in query:
            return RagResult(
                answer="Dziękuję, brakuje już tylko okresu.",
                chunks=[],
                audit={"grounded": False},
                redacted_query=query,
                category="pit",
                needs_clarification=True,
                missing_slots=["okres_lub_data"],
                no_match_reason="clarification_required",
            )
        return RagResult(
            answer="Potrzebuję doprecyzowania, zanim odpowiem.",
            chunks=[],
            audit={"grounded": False},
            redacted_query=query,
            category="pit",
            needs_clarification=True,
            missing_slots=["okres_lub_data", "forma_opodatkowania"],
            no_match_reason="clarification_required",
        )

    monkeypatch.setattr(app_main, "answer_query", fake_answer_query)
    monkeypatch.setattr(app_main, "CLARIFICATION_PROMPTS_PATH", str(prompts_path))
    monkeypatch.setattr(app_main, "CLARIFICATION_CHIPS_ENABLED", True)
    app_main.load_clarification_prompts.cache_clear()
    app_main.load_clarification_chip_options.cache_clear()
    app_main.load_clarification_display_labels.cache_clear()

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
clarification_chip_options = app_main.load_clarification_chip_options(app_main.CLARIFICATION_PROMPTS_PATH)
clarification_display_labels = app_main.load_clarification_display_labels(app_main.CLARIFICATION_PROMPTS_PATH)
chip_followup = st.session_state.pop("pending_clarification_followup", None)

render_chat_history(
    st.session_state.messages,
    session_id=st.session_state.session_id,
    user_email=st.session_state.user_email,
    clarification_prompts=clarification_prompts,
    clarification_chip_options=clarification_chip_options,
    clarification_display_labels=clarification_display_labels,
    clarification_chips_enabled=app_main.CLARIFICATION_CHIPS_ENABLED,
)

typed_question = st.chat_input("Zadaj pytanie")
payload = chip_followup or typed_question
if payload:
    if isinstance(payload, dict):
        display_question = payload["display_text"]
        submitted_question = payload["submitted_text"]
    else:
        display_question = payload
        submitted_question = payload

    result = app_main.answer_query(
        query=submitted_question,
        knowledge_path="unused.json",
        system_prompt="unused",
        api_key="unused",
    )
    st.session_state.messages.extend(
        [
            {"role": "user", "content": display_question, "timestamp": "2026-04-12T09:00:00+02:00"},
            {
                "role": "assistant",
                "result": result,
                "query": submitted_question,
                "timestamp": "2026-04-12T09:00:00+02:00",
            },
        ]
    )
    st.rerun()
"""
    )
    at.session_state["messages"] = []

    at.run()
    at.chat_input[0].set_value("Jak rozliczyć PIT z najmu?").run()

    button_labels = [button.proto.label for button in at.button]
    assert "ryczałt" in button_labels
    assert "liniowy" in button_labels
    assert "zasady ogólne" in button_labels

    chip_button = next(button for button in at.button if button.proto.label == "ryczałt")
    chip_button.click().run()

    markdown_values = [element.value for element in at.markdown]

    assert len(answer_calls) == 2
    assert answer_calls[1] == "ryczałt"
    assert any("Forma opodatkowania: ryczałt" == value for value in markdown_values)
    assert any("Podaj okres lub datę." in value for value in markdown_values)
    assert markdown_values[-1] == "1. Podaj okres lub datę."
    assert not any("Jaka jest forma opodatkowania?" in value for value in markdown_values[-6:])
