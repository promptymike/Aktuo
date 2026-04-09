from __future__ import annotations

import sys
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

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

LOCAL_TZ = ZoneInfo("Europe/Warsaw")


def normalize_email(value: str) -> str:
    return value.strip().lower()


def current_timestamp() -> str:
    return datetime.now(LOCAL_TZ).isoformat()


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
                position: sticky;
                bottom: 0;
                z-index: 30;
                padding: 0.75rem 0 calc(0.75rem + env(safe-area-inset-bottom));
                background: rgba(255, 255, 255, 0.97);
                border-top: 1px solid var(--aktuo-border);
            }

            .stExpander {
                border: 1px solid var(--aktuo-border);
                border-radius: 14px;
            }

            [data-testid="stForm"] {
                max-width: 500px;
                margin: 1rem auto 0;
                padding: 1rem;
                border: 1px solid var(--aktuo-border);
                border-radius: 16px;
                background: #ffffff;
            }

            [data-testid="stForm"] [data-baseweb="input"] > div {
                border: 1px solid var(--aktuo-border);
                border-radius: 8px;
                background: #ffffff;
            }

            [data-testid="stForm"] input {
                color: var(--aktuo-text);
            }

            [data-testid="stForm"] [data-testid="stFormSubmitButton"] > button {
                background: var(--aktuo-navy);
                color: #ffffff;
                border: 1px solid var(--aktuo-navy);
                border-radius: 10px;
                padding: 0.6rem 1.5rem;
                font-weight: 600;
                transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
            }

            [data-testid="stForm"] [data-testid="stFormSubmitButton"] > button:hover {
                background: #243558;
                border-color: #243558;
                box-shadow: 0 10px 24px rgba(26, 39, 68, 0.14);
                transform: translateY(-1px);
            }

            @media (max-width: 768px) {
                .aktuo-hero {
                    gap: 0.75rem;
                    padding: 0.95rem 1rem;
                    margin-bottom: 1rem;
                }

                .aktuo-title {
                    font-size: 1.4rem;
                }

                .stChatMessage {
                    padding: 0.75rem !important;
                }

                .stChatInputContainer {
                    padding: 0.6rem 0 calc(0.75rem + env(safe-area-inset-bottom));
                }

                [data-testid="stForm"] {
                    max-width: 100%;
                    margin: 1rem auto 0;
                    padding: 0.9rem;
                }

                [data-testid="stForm"] [data-baseweb="input"] > div {
                    width: 100%;
                }

                [data-testid="stForm"] [data-testid="stFormSubmitButton"] > button {
                    width: 100%;
                }
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


def render_login_gate() -> None:
    st.markdown("### Zaloguj się do wersji beta")
    st.write("Podaj adres e-mail, aby korzystać z Aktuo i zapisywać historię zapytań na potrzeby testów beta.")
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Adres e-mail", placeholder="jan@firma.pl")
        submitted = st.form_submit_button("Zaloguj", use_container_width=True)
    if submitted:
        normalized = normalize_email(email)
        if not normalized or "@" not in normalized:
            st.error("Podaj prawidłowy adres e-mail.")
            return
        st.session_state.user_email = normalized
        st.rerun()


def render_chat_page() -> None:
    render_styles()

    try:
        settings = get_settings()
    except MissingEnvironmentError as exc:
        render_header()
        st.error("Brakuje wymaganej konfiguracji aplikacji.")
        st.info(f"Szczegóły: {exc}")
        st.stop()

    if "messages" not in st.session_state:
        if "chat_history" in st.session_state:
            st.session_state.messages = list(st.session_state.chat_history)
        else:
            st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    user_email = st.session_state.get("user_email")

    logout_requested = render_sidebar(settings, user_email)
    if logout_requested:
        st.session_state.clear()
        st.rerun()

    render_header()

    if not user_email:
        render_login_gate()
        render_footer()
        return

    render_chat_history(
        st.session_state.messages,
        session_id=st.session_state.session_id,
        user_email=user_email,
    )

    question = st.chat_input("Zadaj pytanie o prawo podatkowe...")
    if not question:
        if not st.session_state.messages:
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
        user_email=user_email,
        question=question,
        redacted_query=result.redacted_query,
        category=result.category,
        chunks_returned=len(result.chunks),
        chunk_ids=[f"{chunk.law_name} {chunk.article_number}" for chunk in result.chunks],
        answer_length=len(result.answer),
        grounded=bool(result.audit.get("grounded", False)),
        no_match_reason=result.no_match_reason,
    )

    message_timestamp = current_timestamp()
    st.session_state.messages.extend(
        [
            {"role": "user", "content": question, "timestamp": message_timestamp},
            {
                "role": "assistant",
                "result": result,
                "query": question,
                "timestamp": message_timestamp,
            },
        ]
    )
    render_footer()
    st.rerun()


def main() -> None:
    st.set_page_config(page_title="Aktuo", layout="wide")
    chat_page = st.Page(render_chat_page, title="Aktuo", url_path="", default=True)
    analytics_page = st.Page(
        Path(__file__).with_name("analytics.py"),
        title="Analytics",
        url_path="analytics",
    )
    navigation = st.navigation([chat_page, analytics_page], position="hidden")
    navigation.run()


if __name__ == "__main__":
    main()
