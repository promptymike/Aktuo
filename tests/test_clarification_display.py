from __future__ import annotations

import json

from streamlit.testing.v1 import AppTest

import app.main as app_main
from app.chat import resolve_clarification_followup_display
from core.rag import RagResult


def test_load_clarification_display_labels(tmp_path) -> None:
    """Display labels should be loaded from the clarification slots JSON file."""

    prompts_path = tmp_path / "clarification_slots.json"
    prompts_path.write_text(
        json.dumps(
            {
                "slot_display_labels": {
                    "forma_opodatkowania": "Forma opodatkowania",
                    "okres_lub_data": "Okres lub data",
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    app_main.load_clarification_display_labels.cache_clear()
    labels = app_main.load_clarification_display_labels(str(prompts_path))

    assert labels == {
        "forma_opodatkowania": "Forma opodatkowania",
        "okres_lub_data": "Okres lub data",
    }


def test_resolve_clarification_followup_display_uses_slot_label() -> None:
    """A single unresolved slot should produce a labeled user-facing clarification message."""

    history = [
        {
            "role": "assistant",
            "result": RagResult(
                answer="Doprecyzuj proszę pytanie.",
                chunks=[],
                audit={"grounded": False},
                redacted_query="Jak rozliczyć najem?",
                category="pit",
                needs_clarification=True,
                missing_slots=["forma_opodatkowania"],
                no_match_reason="clarification_required",
            ),
        }
    ]

    labeled = resolve_clarification_followup_display(
        history,
        "ryczałt",
        clarification_display_labels={"forma_opodatkowania": "Forma opodatkowania"},
    )

    assert labeled == "Forma opodatkowania: ryczałt"


def test_clarification_chip_followup_displays_label_but_submits_raw_value(monkeypatch, tmp_path) -> None:
    """Clarification chips should show a labeled message in chat while sending only the raw value."""

    prompts_path = tmp_path / "clarification_slots.json"
    prompts_path.write_text(
        json.dumps(
            {
                "slot_prompts": {
                    "forma_opodatkowania": "Jaka jest forma opodatkowania?"
                },
                "slot_chip_options": {
                    "forma_opodatkowania": ["ryczałt", "liniowy"]
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
        return RagResult(
            answer="Dziękuję za doprecyzowanie.",
            chunks=[],
            audit={"grounded": False},
            redacted_query=query,
            category="pit",
            needs_clarification=False,
            missing_slots=[],
            no_match_reason=None,
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
from core.rag import RagResult

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "user", "content": "Jak rozliczyć najem?", "timestamp": "2026-04-12T09:00:00+02:00"},
        {
            "role": "assistant",
            "result": RagResult(
                answer="Potrzebuję doprecyzowania, zanim odpowiem.",
                chunks=[],
                audit={"grounded": False},
                redacted_query="Jak rozliczyć najem?",
                category="pit",
                needs_clarification=True,
                missing_slots=["forma_opodatkowania"],
                no_match_reason="clarification_required",
            ),
            "query": "Jak rozliczyć najem?",
            "timestamp": "2026-04-12T09:00:00+02:00",
        },
    ]
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

payload = chip_followup
if payload:
    display_question = payload["display_text"]
    submitted_question = payload["submitted_text"]
    result = app_main.answer_query(
        query=submitted_question,
        knowledge_path="unused.json",
        system_prompt="unused",
        api_key="unused",
    )
    st.session_state.messages.extend(
        [
            {"role": "user", "content": display_question, "timestamp": "2026-04-12T09:01:00+02:00"},
            {
                "role": "assistant",
                "result": result,
                "query": submitted_question,
                "timestamp": "2026-04-12T09:01:00+02:00",
            },
        ]
    )
    st.rerun()
"""
    )

    at.run()
    chip_button = next(button for button in at.button if button.proto.label == "ryczałt")
    chip_button.click().run()

    markdown_values = [element.value for element in at.markdown]

    assert answer_calls == ["ryczałt"]
    assert any(value == "Forma opodatkowania: ryczałt" for value in markdown_values)

