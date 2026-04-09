from __future__ import annotations

import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_PATH = PROJECT_ROOT / "data" / "logs" / "queries.jsonl"
LOCAL_TZ = ZoneInfo("Europe/Warsaw")


def _read_query_logs() -> list[dict[str, object]]:
    if not LOG_PATH.exists():
        return []

    entries: list[dict[str, object]] = []
    with LOG_PATH.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(LOCAL_TZ)
    except ValueError:
        return None


def _render_password_gate() -> bool:
    analytics_password = os.environ.get("AKTUO_ADMIN_PASSWORD", "")
    if not analytics_password:
        st.title("Analytics")
        st.caption("Panel administracyjny Aktuo")
        st.info("Analytics disabled. Set AKTUO_ADMIN_PASSWORD to enable.")
        return False

    if st.session_state.get("analytics_authenticated"):
        return True

    st.title("Analytics")
    st.caption("Panel administracyjny Aktuo")
    with st.form("analytics_login"):
        password = st.text_input("Hasło administratora", type="password")
        submitted = st.form_submit_button("Otwórz dashboard", use_container_width=True)

    if submitted:
        if password == analytics_password:
            st.session_state.analytics_authenticated = True
            st.rerun()
        st.error("Nieprawidłowe hasło.")
    return False


def main() -> None:
    if not _render_password_gate():
        return

    st.title("Analytics")
    st.caption("Podgląd zapytań z wersji beta")

    entries = _read_query_logs()
    now = datetime.now(LOCAL_TZ)
    start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    with_timestamps: list[dict[str, object]] = []
    for entry in entries:
        parsed_ts = _parse_timestamp(entry.get("timestamp"))
        row = dict(entry)
        row["_parsed_timestamp"] = parsed_ts
        with_timestamps.append(row)

    total_queries = len(with_timestamps)
    today_queries = sum(
        1 for entry in with_timestamps if entry["_parsed_timestamp"] and entry["_parsed_timestamp"] >= start_today
    )
    week_queries = sum(1 for entry in with_timestamps if entry["_parsed_timestamp"] and entry["_parsed_timestamp"] >= week_ago)
    unique_users = len(
        {
            str(entry.get("user_email", "")).strip().lower()
            for entry in with_timestamps
            if str(entry.get("user_email", "")).strip()
        }
    )
    grounded_false = sum(1 for entry in with_timestamps if entry.get("grounded") is False)
    grounded_false_pct = (grounded_false / total_queries * 100) if total_queries else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Łączna liczba zapytań", total_queries)
    col2.metric("Dziś", today_queries)
    col3.metric("Ostatnie 7 dni", week_queries)
    col4.metric("Unikalni użytkownicy", unique_users)

    st.divider()

    top_questions = Counter(
        str(entry.get("question", "")).strip()
        for entry in with_timestamps
        if str(entry.get("question", "")).strip()
    ).most_common(20)

    st.subheader("Top 20 pytań")
    if top_questions:
        st.dataframe(
            [{"Pytanie": question, "Liczba": count} for question, count in top_questions],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Brak danych pytań w logach.")

    st.subheader("Rozkład kategorii")
    category_counts = Counter(str(entry.get("category", "brak")).strip() or "brak" for entry in with_timestamps)
    if category_counts:
        chart_rows = [{"kategoria": category, "liczba": count} for category, count in category_counts.most_common()]
        st.bar_chart(chart_rows, x="kategoria", y="liczba", horizontal=True)
    else:
        st.info("Brak kategorii do wyświetlenia.")

    st.subheader("Pokrycie bazy")
    st.metric("% odpowiedzi z grounded=false", f"{grounded_false_pct:.1f}%")

    st.subheader("Ostatnie 50 zapytań")
    recent_entries = sorted(
        with_timestamps,
        key=lambda entry: entry["_parsed_timestamp"] or datetime.min.replace(tzinfo=LOCAL_TZ),
        reverse=True,
    )[:50]

    if recent_entries:
        rows = []
        for entry in recent_entries:
            parsed_ts = entry["_parsed_timestamp"]
            rows.append(
                {
                    "Data": parsed_ts.strftime("%Y-%m-%d %H:%M") if parsed_ts else "brak",
                    "Email": str(entry.get("user_email", "")),
                    "Kategoria": str(entry.get("category", "")),
                    "Grounded": bool(entry.get("grounded", False)),
                    "Pytanie": str(entry.get("question", "")),
                }
            )
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("Brak zapisanych zapytań w queries.jsonl.")


if __name__ == "__main__":
    main()
