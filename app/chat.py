from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

import streamlit as st

from core.logger import log_feedback
from core.rag import RagResult

GENERIC_CLARIFICATION_PROMPT = "Proszę doprecyzować brakujące informacje."


def _format_timestamp(value: str | None) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value).strftime("%H:%M")
    except ValueError:
        return value


def _render_timestamp(timestamp: str | None) -> None:
    label = _format_timestamp(timestamp)
    if label:
        st.markdown(
            f"<div style='color:#999999;font-size:0.76rem;margin-bottom:0.35rem;'>{label}</div>",
            unsafe_allow_html=True,
        )


def _resolve_clarification_prompts(
    missing_slots: Sequence[str] | None,
    prompt_map: dict[str, str] | None,
) -> list[str]:
    """Map missing slot names to user-facing clarification prompts."""

    if not missing_slots:
        return []
    return [(prompt_map or {}).get(slot_name, GENERIC_CLARIFICATION_PROMPT) for slot_name in missing_slots]


def render_user_message(question: str, *, timestamp: str | None = None) -> None:
    with st.chat_message("user"):
        st.markdown("<div class='aktuo-message-label'>Ty</div>", unsafe_allow_html=True)
        _render_timestamp(timestamp)
        st.write(question)


def render_assistant_message(
    result: RagResult,
    *,
    message_index: int,
    session_id: str,
    user_email: str,
    query: str,
    clarification_prompts: dict[str, str] | None = None,
    timestamp: str | None = None,
) -> None:
    with st.chat_message("assistant"):
        st.markdown("<div class='aktuo-message-label'>Aktuo</div>", unsafe_allow_html=True)
        _render_timestamp(timestamp)
        st.write(result.answer)

        if result.needs_clarification:
            prompts = _resolve_clarification_prompts(result.missing_slots, clarification_prompts)
            if prompts:
                st.warning("Żeby odpowiedzieć precyzyjnie, potrzebuję jeszcze kilku informacji:")
                for index, prompt in enumerate(prompts, start=1):
                    st.markdown(f"{index}. {prompt}")
            return

        if result.chunks:
            with st.expander("Pokaż źródła prawne", expanded=False):
                for chunk in result.chunks:
                    verified = f" | weryfikacja: {chunk.verified_date}" if chunk.verified_date else ""
                    st.markdown(
                        f"**{chunk.law_name} {chunk.article_number}**\n\n"
                        f"{chunk.content}\n\n"
                        f"_Kategoria: {chunk.category}{verified}_"
                    )

        feedback_status_key = f"feedback_status_{message_index}"
        feedback_down_key = f"feedback_down_open_{message_index}"
        feedback_comment_key = f"feedback_comment_{message_index}"

        if st.session_state.get(feedback_status_key):
            st.success("Dziękujemy za feedback!")
            return

        col_up, col_down = st.columns(2)
        if col_up.button("👍", key=f"feedback_up_{message_index}", use_container_width=True):
            log_feedback(
                session_id=session_id,
                user_email=user_email,
                query=query,
                rating="up",
            )
            st.session_state[feedback_status_key] = "up"
            st.rerun()

        if col_down.button("👎", key=f"feedback_down_{message_index}", use_container_width=True):
            st.session_state[feedback_down_key] = True

        if st.session_state.get(feedback_down_key):
            st.text_input("Co było nie tak? (opcjonalne)", key=feedback_comment_key)
            if st.button("Wyślij feedback", key=f"feedback_submit_{message_index}", use_container_width=True):
                log_feedback(
                    session_id=session_id,
                    user_email=user_email,
                    query=query,
                    rating="down",
                    comment=str(st.session_state.get(feedback_comment_key, "")).strip(),
                )
                st.session_state[feedback_status_key] = "down"
                st.session_state.pop(feedback_down_key, None)
                st.rerun()


def render_chat_history(
    history: Sequence[dict[str, object]],
    *,
    session_id: str,
    user_email: str,
    clarification_prompts: dict[str, str] | None = None,
) -> None:
    for index, message in enumerate(history):
        role = message.get("role")
        if role == "user":
            render_user_message(
                str(message.get("content", "")),
                timestamp=str(message.get("timestamp", "")),
            )
        elif role == "assistant":
            result = message.get("result")
            if isinstance(result, RagResult):
                render_assistant_message(
                    result,
                    message_index=index,
                    session_id=session_id,
                    user_email=user_email,
                    query=str(message.get("query", "")),
                    clarification_prompts=clarification_prompts,
                    timestamp=str(message.get("timestamp", "")),
                )
