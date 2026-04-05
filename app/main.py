from __future__ import annotations

import sys
import uuid
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.chat import render_chat_history, render_user_message
from app.sidebar import render_sidebar
from config.settings import MissingEnvironmentError, get_settings
from core.generator import AnthropicAPIError
from core.logger import log_query
from core.rag import answer_query


def render_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --aktuo-navy: #1a2744;
                --aktuo-border: #d7dfeb;
                --aktuo-surface: #f7f9fc;
                --aktuo-text: #122033;
                --aktuo-muted: #5f6d84;
            }

            .stApp {
                background: #ffffff;
                color: var(--aktuo-text);
            }

            [data-testid="stHeader"] {
                background: rgba(255, 255, 255, 0.92);
            }

            [data-testid="stSidebar"] {
                background: #f8fafc;
                border-right: 1px solid var(--aktuo-border);
            }

            .aktuo-hero {
                display: flex;
                align-items: center;
                gap: 1rem;
                padding: 1.2rem 1.3rem;
                margin-bottom: 1.25rem;
                border: 1px solid var(--aktuo-border);
                border-radius: 18px;
                background: linear-gradient(180deg, #ffffff 0%, #f7f9fc 100%);
            }

            .aktuo-logo {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 3rem;
                height: 3rem;
                border-radius: 14px;
                background: var(--aktuo-navy);
                color: #ffffff;
                font-weight: 700;
                font-size: 1.15rem;
                letter-spacing: 0.04em;
            }

            .aktuo-title {
                margin: 0;
                color: var(--aktuo-navy);
                font-size: 1.9rem;
                font-weight: 700;
                line-height: 1.1;
            }

            .aktuo-subtitle {
                margin: 0.2rem 0 0;
                color: var(--aktuo-muted);
                font-size: 0.98rem;
            }

            .aktuo-footer {
                margin-top: 1.5rem;
                padding-top: 0.8rem;
                color: var(--aktuo-muted);
                font-size: 0.82rem;
                border-top: 1px solid var(--aktuo-border);
            }

            .stChatMessage {
                border: 1px solid var(--aktuo-border);
                border-radius: 16px;
                background: #ffffff;
            }

            .stChatMessage [data-testid="stMarkdownContainer"] p {
                color: var(--aktuo-text);
            }

            .stChatInputContainer {
                background: #ffffff;
            }

            .stExpander {
                border: 1px solid var(--aktuo-border);
                border-radius: 14px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <section class="aktuo-hero">
            <div class="aktuo-logo">A</div>
            <div>
                <h1 class="aktuo-title">Aktuo</h1>
                <p class="aktuo-subtitle">Asystent prawno-podatkowy dla księgowych</p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        """
        <div class="aktuo-footer">
            Aktuo nie zastępuje porady prawnej. Zawsze weryfikuj z doradcą podatkowym.
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Aktuo", layout="wide")
    render_styles()

    try:
        settings = get_settings()
    except MissingEnvironmentError as exc:
        render_header()
        st.error("Brakuje wymaganej konfiguracji aplikacji.")
        st.info(f"Szczegóły: {exc}")
        st.stop()

    render_sidebar(settings)
    render_header()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    render_chat_history(st.session_state.chat_history)

    question = st.chat_input("Zadaj pytanie o prawo podatkowe...")
    if not question:
        if not st.session_state.chat_history:
            st.write("Na przykład: Od kiedy KSeF będzie obowiązkowy dla mojej firmy?")
        render_footer()
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
        st.error(f"Nie udało się odnaleźć bazy wiedzy: {exc}")
        st.stop()
    except AnthropicAPIError as exc:
        render_user_message(question)
        st.error(f"Nie udało się pobrać odpowiedzi: {exc}")
        st.stop()

    log_query(
        session_id=st.session_state.session_id,
        question=question,
        redacted_query=result.redacted_query,
        category=result.category,
        chunks_returned=len(result.chunks),
        chunk_ids=[f"{chunk.law_name} {chunk.article_number}" for chunk in result.chunks],
        answer_length=len(result.answer),
        grounded=bool(result.audit.get("grounded", False)),
    )

    st.session_state.chat_history.extend(
        [
            {"role": "user", "content": question},
            {"role": "assistant", "result": result},
        ]
    )
    render_footer()
    st.rerun()


if __name__ == "__main__":
    main()
