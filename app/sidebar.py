from __future__ import annotations

import streamlit as st

from config.settings import Settings


def render_sidebar(_settings: Settings, user_email: str | None) -> bool:
    with st.sidebar:
        st.markdown("### Jak zadawać pytania")
        st.write(
            "Pisz konkretnie: opisz dokument, obowiązek, termin albo sytuację praktyczną, którą chcesz zweryfikować."
        )
        st.caption("Przykład: Jaki jest termin złożenia JPK_V7 za marzec?")

        with st.expander("Baza wiedzy", expanded=False):
            st.write("✓ VAT (1250 zapisów)")
            st.write("✓ PIT (511)")
            st.write("✓ CIT (46)")
            st.write("✓ Ordynacja podatkowa (39)")
            st.write("✓ Rachunkowość (93)")
            st.write("✓ Kodeks pracy (58)")
            st.write("✓ ZUS (43)")
            st.write("✓ KSeF (30)")
            st.write("✓ JPK (42)")

        with st.expander("O Aktuo", expanded=False):
            st.write("Aktuo przeszukuje polskie ustawy podatkowe i odpowiada z cytatem konkretnego przepisu.")
            st.write("Baza zbudowana na analizie tysięcy pytań od praktyków księgowości.")
            st.write("Dla księgowych, doradców podatkowych i biur rachunkowych.")

        st.divider()
        if user_email:
            st.caption(f"Zalogowano jako: {user_email}")
            return st.button("Wyloguj", use_container_width=True)

        st.caption("Zaloguj się adresem e-mail, aby korzystać z wersji beta.")
        return False
