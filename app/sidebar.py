from __future__ import annotations

import streamlit as st

from config.settings import Settings


def render_sidebar(_settings: Settings) -> None:
    with st.sidebar:
        st.markdown("### Aktuo")
        st.caption("Wsparcie dla polskich księgowych i doradców podatkowych.")
        st.markdown("**Jak zadawać pytania**")
        st.write(
            "Pisz konkretnie: opisz stan faktyczny, rodzaj dokumentu, termin lub obowiązek, który chcesz zweryfikować."
        )
        st.markdown("**Przykładowe tematy**")
        st.write("KSeF, faktury, korekty, terminy podatkowe, obowiązki dokumentacyjne.")
        st.caption("Odpowiedzi mają charakter informacyjny i powinny być dalej weryfikowane.")
