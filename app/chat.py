from __future__ import annotations

from collections.abc import Sequence

import streamlit as st

from core.rag import RagResult


def render_user_message(question: str) -> None:
    with st.chat_message("user"):
        st.markdown("**Ty**")
        st.write(question)


def render_assistant_message(result: RagResult) -> None:
    with st.chat_message("assistant"):
        st.markdown("**Aktuo**")
        st.write(result.answer)
        if result.chunks:
            with st.expander("Pokaż źródła prawne", expanded=False):
                for chunk in result.chunks:
                    verified = f" | weryfikacja: {chunk.verified_date}" if chunk.verified_date else ""
                    st.markdown(
                        f"**{chunk.law_name} {chunk.article_number}**\n\n"
                        f"{chunk.content}\n\n"
                        f"_Kategoria: {chunk.category}{verified}_"
                    )


def render_chat_history(history: Sequence[dict[str, object]]) -> None:
    for message in history:
        role = message.get("role")
        if role == "user":
            render_user_message(str(message.get("content", "")))
        elif role == "assistant":
            result = message.get("result")
            if isinstance(result, RagResult):
                render_assistant_message(result)
