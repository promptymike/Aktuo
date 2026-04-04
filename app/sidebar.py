from __future__ import annotations

import streamlit as st

from config.settings import Settings


def render_sidebar(_settings: Settings) -> None:
    with st.sidebar:
        st.markdown("### Aktuo")
        st.caption("Wsparcie dla polskich ksi\u0119gowych i doradc\u00f3w podatkowych.")
        st.markdown("**Jak zadawa\u0107 pytania**")
        st.write(
            "Pisz konkretnie: opisz stan faktyczny, rodzaj dokumentu, termin lub obowi\u0105zek, kt\u00f3ry chcesz zweryfikowa\u0107."
        )
        st.markdown("**Przyk\u0142adowe tematy**")
        st.write("KSeF, faktury, korekty, terminy podatkowe, obowi\u0105zki dokumentacyjne.")
        st.caption("Odpowiedzi maj\u0105 charakter informacyjny i powinny by\u0107 dalej weryfikowane.")
