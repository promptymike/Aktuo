from __future__ import annotations

import streamlit as st

from config.settings import Settings


def render_sidebar(settings: Settings) -> None:
    with st.sidebar:
        st.header("Configuration")
        st.write("Stateless backend")
        st.text_input("Knowledge path", value=settings.law_knowledge_path, disabled=True)
        st.text_input("System prompt", value=settings.system_prompt, disabled=True)
        st.caption("All configuration comes from environment variables.")
