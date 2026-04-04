from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.chat import render_chat_history, render_user_message
from app.sidebar import render_sidebar
from config.settings import MissingEnvironmentError, get_settings
from core.generator import AnthropicAPIError
from core.rag import answer_query


def main() -> None:
    st.set_page_config(page_title="Aktuo MVP", layout="wide")

    try:
        settings = get_settings()
    except MissingEnvironmentError as exc:
        st.title("Aktuo MVP")
        st.error(str(exc))
        st.info("Set the required variables in your shell and rerun the app.")
        st.code(
            "$env:AKTUO_APP_NAME='Aktuo MVP'\n"
            "$env:AKTUO_SYSTEM_PROMPT='You are Aktuo, a cautious legal information assistant.'\n"
            "$env:AKTUO_LAW_KNOWLEDGE_PATH='data/seeds/law_knowledge.json'\n"
            "$env:ANTHROPIC_API_KEY='your_anthropic_api_key'"
        )
        st.stop()

    render_sidebar(settings)
    st.title(settings.app_name)
    st.caption("Minimal stateless MVP scaffold for legal retrieval and response generation.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    render_chat_history(st.session_state.chat_history)

    question = st.chat_input("Ask a legal workflow question")
    if not question:
        if not st.session_state.chat_history:
            st.write("Try: What rights does a tenant have when a deposit is withheld?")
        return

    try:
        result = answer_query(
            query=question,
            knowledge_path=settings.law_knowledge_path,
            system_prompt=settings.system_prompt,
            api_key=settings.anthropic_api_key,
        )
    except FileNotFoundError as exc:
        render_user_message(question)
        st.error(f"Knowledge file not found: {exc}")
        st.stop()
    except AnthropicAPIError as exc:
        render_user_message(question)
        st.error(str(exc))
        st.stop()

    st.session_state.chat_history.extend(
        [
            {"role": "user", "content": question},
            {"role": "assistant", "result": result},
        ]
    )
    st.rerun()


if __name__ == "__main__":
    main()
