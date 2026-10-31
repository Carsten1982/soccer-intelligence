"""Liga-Bereich: alle Begegnungen des aktuellen Spieltags (Dashboard-Briefing, Kapitel 4).

Etappe B: Spielplan und aktueller Spieltag. Die KPI-Spalten folgen in Etappe C.
"""

from __future__ import annotations

import streamlit as st

from core.config import League
from core.matchday import current_matchday, date_range, matchday_games, season_short
from state import get_database, get_fixtures, today
from views import components as ui
from views.registry import PAGES


def render(league: League) -> None:
    db = get_database()
    fx = get_fixtures()
    fixtures = fx.leagues.get(league.name)
    md = current_matchday(fixtures, today()) if fixtures is not None else None

    if md is not None:
        ui.header("Aktueller Spieltag", f"Saison {season_short(md.saison)} · Spieltag {md.spieltag}")
    else:
        ui.header()

    if db.has_errors or fx.has_errors:
        ui.blocked_notice(db.has_errors, fx.has_errors, PAGES.get("datenqualitaet"))
        ui.footer()
        return

    if md is None:
        st.info(f"Für die {league.name} ist im Spielplan noch kein Spieltag eingetragen.", icon="📅")
        ui.footer()
        return

    games = matchday_games(fixtures, md.saison, md.spieltag)
    rows = [ui.MatchRow(home=g.heim, away=g.gast, status=g.status) for g in games.itertuples()]
    st.caption(f"{league.name} · Spieltag {md.spieltag} · {date_range(md.erstes_datum, md.letztes_datum)} "
               f"· {len(rows)} Begegnungen")
    ui.match_table(rows)
    st.info("Die KPI-Spalten (Formkurve, Erwartete Tore, Over 2.5 Goals, Gelbe Karten) folgen in Etappe C.",
            icon="🛠️")
    ui.footer()
