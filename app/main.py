from __future__ import annotations

import json
import re
import sys
import uuid
from datetime import datetime, timedelta
from functools import lru_cache
from math import ceil
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.chat import render_chat_history
from app.sidebar import render_sidebar
from config.settings import (
    CLARIFICATION_PROMPTS_PATH,
    MAX_QUESTION_LENGTH,
    MissingEnvironmentError,
    RATE_LIMIT_PER_HOUR,
    get_settings,
)
from core.generator import AnthropicAPIError
from core.logger import log_query
from core.rag import answer_query

LOCAL_TZ = ZoneInfo("Europe/Warsaw")
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
QUICK_QUESTIONS = (
    "Termin złożenia JPK_V7?",
    "Estoński CIT — kto może?",
    "Okres wypowiedzenia umowy",
)


def normalize_email(value: str) -> str:
    return value.strip().lower()


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(value))


def is_question_too_long(value: str) -> bool:
    return len(value) > MAX_QUESTION_LENGTH


def current_timestamp() -> str:
    return datetime.now(LOCAL_TZ).isoformat()


@lru_cache(maxsize=4)
def load_clarification_prompts(path: str) -> dict[str, str]:
    """Load user-facing clarification prompts from the curated JSON file."""

    file_path = Path(path)
    if not file_path.exists():
        raise ValueError(f"Nie znaleziono pliku promptów doprecyzowujących: {file_path}")

    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Plik promptów doprecyzowujących jest uszkodzony: {file_path}") from exc

    if not isinstance(payload, dict):
        raise ValueError(f"Plik promptów doprecyzowujących musi zawierać obiekt JSON: {file_path}")

    raw_prompts = payload.get("slot_prompts", payload)
    if not isinstance(raw_prompts, dict):
        raise ValueError(f"Nieprawidłowy format promptów doprecyzowujących w pliku: {file_path}")

    return {
        str(slot_name): str(prompt)
        for slot_name, prompt in raw_prompts.items()
        if isinstance(slot_name, str) and isinstance(prompt, str)
    }


def load_recent_query_timestamps(now: datetime) -> list[datetime]:
    window_start = now - timedelta(hours=1)
    recent: list[datetime] = []
    for raw_value in st.session_state.get("query_timestamps", []):
        try:
            parsed = datetime.fromisoformat(raw_value)
        except (TypeError, ValueError):
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=LOCAL_TZ)
        if parsed >= window_start:
            recent.append(parsed)
    st.session_state.query_timestamps = [value.isoformat() for value in recent]
    return recent


def minutes_until_rate_limit_reset(recent: list[datetime], now: datetime) -> int:
    if not recent:
        return 0
    reset_at = min(recent) + timedelta(hours=1)
    remaining_seconds = max(0, (reset_at - now).total_seconds())
    return max(1, ceil(remaining_seconds / 60))


def render_styles() -> None:
    st.markdown(
        """
        <style>
            @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");

            :root {
                --aktuo-primary: #1a2744;
                --aktuo-primary-hover: #2a3d5c;
                --aktuo-primary-deep: #1a2744;
                --aktuo-primary-mid: #2a3d5c;
                --aktuo-sidebar: #f0f2f5;
                --aktuo-surface: #f0f2f5;
                --aktuo-surface-soft: #e8ecf1;
                --aktuo-text: #1A1A2E;
                --aktuo-muted: #666666;
                --aktuo-border: rgba(26, 39, 68, 0.22);
                --aktuo-border-strong: rgba(26, 39, 68, 0.38);
            }

            html, body, [class*="css"] {
                font-family: "Inter", "Segoe UI", sans-serif;
            }

            .stApp {
                background: #FFFFFF;
                color: var(--aktuo-text);
            }

            [data-testid="stHeader"] {
                background: rgba(255, 255, 255, 0.94);
            }

            [data-testid="stSidebar"] {
                background: var(--aktuo-sidebar);
                border-right: 1px solid rgba(26, 39, 68, 0.08);
            }

            [data-testid="stSidebar"] .stMarkdown,
            [data-testid="stSidebar"] .stCaption,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] label {
                color: var(--aktuo-text);
            }

            .aktuo-header {
                display: flex;
                align-items: center;
                gap: 0.95rem;
                margin: 0 0 1.35rem;
                padding: 0.15rem 0 0.25rem;
            }

            .aktuo-logo-shell {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 3.45rem;
                height: 3.45rem;
                padding: 0.18rem;
                border-radius: 999px;
                background: linear-gradient(135deg, var(--aktuo-primary-deep), var(--aktuo-primary-mid));
                box-shadow: 0 14px 34px rgba(26, 39, 68, 0.18);
                flex-shrink: 0;
            }

            .aktuo-logo-circle {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 100%;
                height: 100%;
                border-radius: 999px;
                background: var(--aktuo-primary);
                color: #FFFFFF;
                font-size: 1.3rem;
                font-weight: 700;
                letter-spacing: 0.03em;
            }

            .aktuo-title {
                margin: 0;
                color: var(--aktuo-text);
                font-size: 1.85rem;
                line-height: 1.05;
                font-weight: 700;
            }

            .aktuo-subtitle {
                margin: 0.28rem 0 0;
                color: var(--aktuo-muted);
                font-size: 0.98rem;
                line-height: 1.3;
                font-weight: 500;
            }

            .aktuo-login-intro {
                max-width: 32rem;
                color: var(--aktuo-muted);
                margin-bottom: 0.35rem;
            }

            [data-testid="stForm"] {
                max-width: 500px;
                margin: 1rem auto 0;
                padding: 1.15rem;
                border: 1px solid var(--aktuo-border);
                border-radius: 18px;
                background: #FFFFFF;
                box-shadow: 0 16px 36px rgba(26, 39, 68, 0.08);
            }

            [data-testid="stForm"] [data-baseweb="input"] > div,
            .stTextInput [data-baseweb="input"] > div {
                border: 1px solid rgba(26, 39, 68, 0.2);
                border-radius: 12px;
                background: #FFFFFF;
            }

            [data-testid="stForm"] [data-baseweb="input"] > div:focus-within,
            .stTextInput [data-baseweb="input"] > div:focus-within,
            div[data-testid="stChatInput"] textarea:focus,
            textarea:focus {
                border-color: var(--aktuo-primary);
                box-shadow: 0 0 0 3px rgba(26, 39, 68, 0.12);
            }

            .stButton > button,
            [data-testid="stFormSubmitButton"] > button {
                background: var(--aktuo-primary);
                color: #FFFFFF;
                border: 1px solid var(--aktuo-primary);
                border-radius: 12px;
                padding: 0.62rem 1rem;
                font-weight: 600;
                transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
            }

            .stButton > button:hover,
            [data-testid="stFormSubmitButton"] > button:hover {
                background: var(--aktuo-primary-hover);
                border-color: var(--aktuo-primary-hover);
                box-shadow: 0 14px 28px rgba(26, 39, 68, 0.18);
                transform: translateY(-1px);
            }

            .stButton > button:focus,
            [data-testid="stFormSubmitButton"] > button:focus {
                box-shadow: 0 0 0 3px rgba(26, 39, 68, 0.15);
            }

            .aktuo-quick-label {
                margin: 0.25rem 0 0.7rem;
                color: var(--aktuo-muted);
                font-size: 0.9rem;
                font-weight: 600;
            }

            .stChatMessage {
                border-radius: 18px;
                border: 1px solid var(--aktuo-border);
                box-shadow: 0 12px 28px rgba(26, 39, 68, 0.05);
                color: var(--aktuo-text);
            }

            div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
                background: #FFFFFF;
                border-color: var(--aktuo-border-strong);
            }

            div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
                background: var(--aktuo-surface-soft);
                border-color: rgba(26, 39, 68, 0.16);
            }

            div[data-testid="stChatMessageContent"] {
                color: var(--aktuo-text);
            }

            .aktuo-message-label {
                color: var(--aktuo-primary-hover);
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.02em;
                margin-bottom: 0.22rem;
                text-transform: uppercase;
            }

            .stChatInputContainer {
                position: sticky;
                bottom: 0;
                z-index: 30;
                padding: 0.85rem 0 calc(0.8rem + env(safe-area-inset-bottom));
                background: rgba(255, 255, 255, 0.96);
                border-top: 1px solid rgba(26, 39, 68, 0.12);
                backdrop-filter: blur(14px);
            }

            div[data-testid="stChatInput"] {
                background: #FFFFFF;
                border-radius: 16px;
            }

            div[data-testid="stChatInput"] textarea {
                border: 1px solid rgba(26, 39, 68, 0.18) !important;
                border-radius: 14px !important;
                min-height: 54px;
            }

            .stExpander {
                border: 1px solid rgba(26, 39, 68, 0.14);
                border-radius: 16px;
                background: rgba(255, 255, 255, 0.65);
            }

            .aktuo-footer {
                margin: 1.8rem 0 0.3rem;
                color: #999999;
                text-align: center;
                font-size: 0.76rem;
                line-height: 1.5;
                font-weight: 400;
            }

            @media (max-width: 768px) {
                .stApp,
                .stMarkdown,
                .stButton > button,
                input,
                textarea {
                    font-size: 14px !important;
                }

                .aktuo-header {
                    gap: 0.75rem;
                    margin-bottom: 1rem;
                }

                .aktuo-logo-shell {
                    width: 3rem;
                    height: 3rem;
                }

                .aktuo-title {
                    font-size: 1.45rem;
                }

                .aktuo-subtitle {
                    font-size: 0.92rem;
                }

                .stChatMessage,
                .stChatMessage p,
                .stChatMessage li,
                div[data-testid="stChatMessageContent"],
                div[data-testid="stChatMessageContent"] p {
                    color: #1A1A2E !important;
                }

                .stChatMessage {
                    padding: 0.8rem !important;
                }

                .stChatInputContainer {
                    padding: 0.65rem 0 calc(0.8rem + env(safe-area-inset-bottom));
                }

                [data-testid="stForm"] {
                    max-width: 100%;
                    padding: 1rem;
                }

                .stButton > button,
                [data-testid="stFormSubmitButton"] > button {
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
        <section class="aktuo-header">
            <div class="aktuo-logo-shell">
                <div class="aktuo-logo-circle">A</div>
            </div>
            <div>
                <h1 class="aktuo-title">Aktuo</h1>
                <p class="aktuo-subtitle">Asystent prawno-podatkowy</p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        """
        <div class="aktuo-footer">
            Informacje mają charakter poglądowy.<br>
            Aktuo nie zastępuje porady prawnej.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_gate() -> None:
    st.markdown("### Zaloguj się do wersji beta")
    st.markdown(
        "<p class='aktuo-login-intro'>Podaj adres e-mail, aby korzystać z Aktuo i zapisywać historię pytań na potrzeby testów beta.</p>",
        unsafe_allow_html=True,
    )
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Adres e-mail", placeholder="jan@firma.pl")
        submitted = st.form_submit_button("Zaloguj", use_container_width=True)
    if submitted:
        normalized = normalize_email(email)
        if not normalized or not is_valid_email(normalized):
            st.error("Podaj prawidłowy adres e-mail.")
            return
        st.session_state.user_email = normalized
        st.rerun()


def render_quick_questions() -> str | None:
    st.markdown("<div class='aktuo-quick-label'>Wypróbuj jedno z przykładowych pytań:</div>", unsafe_allow_html=True)
    columns = st.columns(3)
    for index, label in enumerate(QUICK_QUESTIONS):
        if columns[index].button(label, key=f"quick_question_{index}", use_container_width=True):
            return label
    return None


def render_chat_page() -> None:
    render_styles()

    try:
        settings = get_settings()
    except MissingEnvironmentError as exc:
        render_header()
        st.error("Brakuje wymaganej konfiguracji aplikacji.")
        st.info(f"Szczegóły: {exc}")
        st.stop()

    try:
        clarification_prompts = load_clarification_prompts(CLARIFICATION_PROMPTS_PATH)
    except ValueError:
        clarification_prompts = {}

    if "messages" not in st.session_state:
        if "chat_history" in st.session_state:
            st.session_state.messages = list(st.session_state.chat_history)
        else:
            st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "query_timestamps" not in st.session_state:
        st.session_state.query_timestamps = []
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

    quick_question = render_quick_questions()

    render_chat_history(
        st.session_state.messages,
        session_id=st.session_state.session_id,
        user_email=user_email,
        clarification_prompts=clarification_prompts,
    )

    typed_question = st.chat_input("Zadaj pytanie o prawo podatkowe...")
    question = quick_question or typed_question
    if not question:
        render_footer()
        return

    if is_question_too_long(question):
        st.error(f"Pytanie jest za długie. Maksymalna długość to {MAX_QUESTION_LENGTH} znaków.")
        render_footer()
        return

    now = datetime.now(LOCAL_TZ)
    recent_queries = load_recent_query_timestamps(now)
    if len(recent_queries) >= RATE_LIMIT_PER_HOUR:
        minutes_left = minutes_until_rate_limit_reset(recent_queries, now)
        st.error(f"Przekroczono limit pytań. Spróbuj ponownie za {minutes_left} minut.")
        render_footer()
        return
    st.session_state.query_timestamps.append(now.isoformat())

    try:
        result = answer_query(
            query=question,
            knowledge_path=settings.law_knowledge_path,
            system_prompt=settings.system_prompt,
            api_key=settings.anthropic_api_key,
        )
    except FileNotFoundError as exc:
        st.error(f"Nie udało się odnaleźć bazy wiedzy: {exc}")
        st.stop()
    except AnthropicAPIError as exc:
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
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        estimated_cost_usd=result.estimated_cost_usd,
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
