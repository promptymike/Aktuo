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


def _visible_missing_slots(message_index: int, missing_slots: Sequence[str] | None) -> list[str]:
    """Return only missing slots that have not already been resolved via chip click."""

    resolved = set(st.session_state.get(f"clarification_resolved_{message_index}", []))
    return [slot_name for slot_name in (missing_slots or []) if slot_name not in resolved]


def _queue_clarification_chip_followup(
    *,
    message_index: int,
    slot_name: str,
    chip_value: str,
    display_label_map: dict[str, str] | None,
) -> None:
    """Queue a chip selection as the next follow-up user message and rerun."""

    resolved_key = f"clarification_resolved_{message_index}"
    resolved_slots = list(st.session_state.get(resolved_key, []))
    if slot_name not in resolved_slots:
        resolved_slots.append(slot_name)
    st.session_state[resolved_key] = resolved_slots
    display_label = (display_label_map or {}).get(slot_name, "").strip()
    display_text = f"{display_label}: {chip_value}" if display_label else chip_value
    st.session_state["pending_clarification_followup"] = {
        "display_text": display_text,
        "submitted_text": chip_value,
    }
    st.rerun()


def _active_clarification_slot(history: Sequence[dict[str, object]]) -> str | None:
    """Return the single unresolved clarification slot for the latest clarification step."""

    for message_index in range(len(history) - 1, -1, -1):
        message = history[message_index]
        result = message.get("result")
        if not isinstance(result, RagResult) or not result.needs_clarification:
            continue
        visible_slots = _visible_missing_slots(message_index, result.missing_slots)
        if len(visible_slots) == 1:
            return visible_slots[0]
        return None
    return None


def resolve_clarification_followup_display(
    history: Sequence[dict[str, object]],
    submitted_text: str,
    *,
    clarification_display_labels: dict[str, str] | None = None,
) -> str:
    """Return a user-facing clarification message with a slot label when the slot is unambiguous."""

    slot_name = _active_clarification_slot(history)
    if not slot_name:
        return submitted_text

    display_label = (clarification_display_labels or {}).get(slot_name, "").strip()
    return f"{display_label}: {submitted_text}" if display_label else submitted_text


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
    clarification_chip_options: dict[str, list[str]] | None = None,
    clarification_display_labels: dict[str, str] | None = None,
    clarification_chips_enabled: bool = True,
    timestamp: str | None = None,
) -> None:
    with st.chat_message("assistant"):
        st.markdown("<div class='aktuo-message-label'>Aktuo</div>", unsafe_allow_html=True)
        _render_timestamp(timestamp)
        st.write(result.answer)

        if result.needs_clarification:
            visible_slots = _visible_missing_slots(message_index, result.missing_slots)
            prompts = _resolve_clarification_prompts(visible_slots, clarification_prompts)
            if prompts:
                st.warning("Żeby odpowiedzieć precyzyjnie, potrzebuję jeszcze kilku informacji:")
                for index, slot_name in enumerate(visible_slots, start=1):
                    prompt = (clarification_prompts or {}).get(slot_name, GENERIC_CLARIFICATION_PROMPT)
                    st.markdown(f"{index}. {prompt}")
                    chip_options = (clarification_chip_options or {}).get(slot_name, [])
                    if clarification_chips_enabled and chip_options:
                        chip_columns = st.columns(len(chip_options))
                        for column, chip_value in zip(chip_columns, chip_options, strict=False):
                            if column.button(
                                chip_value,
                                key=f"clarification_chip_{message_index}_{slot_name}_{chip_value}",
                                use_container_width=True,
                            ):
                                _queue_clarification_chip_followup(
                                    message_index=message_index,
                                    slot_name=slot_name,
                                    chip_value=chip_value,
                                    display_label_map=clarification_display_labels,
                                )
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
    clarification_chip_options: dict[str, list[str]] | None = None,
    clarification_display_labels: dict[str, str] | None = None,
    clarification_chips_enabled: bool = True,
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
                    clarification_chip_options=clarification_chip_options,
                    clarification_display_labels=clarification_display_labels,
                    clarification_chips_enabled=clarification_chips_enabled,
                    timestamp=str(message.get("timestamp", "")),
                )
