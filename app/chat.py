from __future__ import annotations

from collections.abc import Sequence

import streamlit as st

from core.rag import RagResult


def render_user_message(question: str) -> None:
    with st.chat_message("user"):
        st.markdown("**User**")
        st.write(question)


def render_assistant_message(result: RagResult) -> None:
    with st.chat_message("assistant"):
        st.markdown("**Assistant**")
        st.write(result.answer)
        if result.chunks:
            st.caption("Retrieved context")
            for chunk in result.chunks:
                st.markdown(
                    f"- **{chunk.law_name} {chunk.article_number}** "
                    f"({chunk.category}, verified {chunk.verified_date}): {chunk.content}"
                )
        st.caption(
            f"Audit: grounded={result.audit['grounded']} | context_count={result.audit['context_count']}"
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
