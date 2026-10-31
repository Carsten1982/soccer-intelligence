"""Startseite: Datenstand und Bestand je Liga (reine Zählungen, noch keine Analysen)."""

import streamlit as st

from core.issues import FEHLER
from core.overview import games_per_season, league_summary
from state import fmt_dt, get_database, status_banner

st.title("⚽ Soccer Intelligence")
st.caption("Fussball-Analysen auf Basis historischer Spieldaten – Bundesliga & Premier League")

db = get_database()
status_banner(db)

if db.has_errors:
    st.subheader("Gefundene Fehler")
    errors = db.issues_frame()
    st.dataframe(errors[errors["Stufe"] == FEHLER], hide_index=True, width="stretch")
    st.info("Solange Fehler bestehen, werden keine Auswertungen angezeigt.")
    st.stop()

st.subheader("Datenbestand")
cols = st.columns(len(db.leagues) or 1)
for col, (name, df) in zip(cols, db.leagues.items()):
    s = league_summary(df)
    with col, st.container(border=True):
        st.markdown(f"#### {name}")
        a, b = st.columns(2)
        a.metric("Spiele", f"{s['Spiele']:,}".replace(",", "."))
        b.metric("Teams", s["Teams"])
        st.caption(
            f"{s['Saisons']} Saisons ({s['Erste Saison']} – {s['Letzte Saison']}) · "
            f"{s['Erstes Spiel']:%d.%m.%Y} bis {s['Letztes Spiel']:%d.%m.%Y}"
        )

st.subheader("Spiele je Saison")
st.dataframe(games_per_season(db.leagues), width="stretch")

with st.expander("Datenquelle"):
    st.markdown(
        f"- **Datei:** `{db.path.name}`\n"
        f"- **Zuletzt geändert:** {fmt_dt(db.file_modified)}\n"
        f"- **Eingelesen:** {fmt_dt(db.loaded_at)}\n"
        f"- **Grösse:** {db.file_size / 1024:,.0f} KB\n"
        f"- **SHA-256:** `{(db.sha256 or '-')[:16]}…`"
    )

st.info("Spieltagsvorschau und Analysen folgen in den nächsten Schritten.", icon="🛠️")
