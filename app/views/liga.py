"""Liga-Bereich: alle Begegnungen des aktuellen Spieltags mit KPI 01–04 (Dashboard-Briefing, Kapitel 4 und 7–9)."""

from __future__ import annotations

import streamlit as st

from core.config import League
from core.fixtures import INACTIVE_STATUS
from core.kpis import Match, compute_match
from core.matchday import current_matchday, date_range, matchday_games, season_short
from state import get_database, get_fixtures, get_prepared, today
from views import components as ui
from views import kpi_table
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
    results = matchday_kpis(league, md.saison, md.spieltag, games)
    rows = []
    for g, k in zip(games.itertuples(), results):
        cells = kpi_table.empty_cells() if k is None else kpi_table.match_cells(k)
        rows.append(ui.MatchRow(home=g.heim, away=g.gast, status=g.status, cells=cells))

    st.caption(f"{league.name} · Spieltag {md.spieltag} · {date_range(md.erstes_datum, md.letztes_datum)} "
               f"· {len(rows)} Begegnungen · Berechnung so, als wären die Spiele noch nicht gespielt "
               "(Stichtag „Datum von“)")
    ui.match_table(rows, kpi_table.GROUPS)
    st.markdown(kpi_table.LEGEND_HTML, unsafe_allow_html=True)
    ui.footer()


def matchday_kpis(league: League, season: str, matchday: int, games) -> list:
    """KPI-Ergebnisse je Begegnung; None für verschobene/abgesagte Spiele. Stichtag = „Datum von“."""
    prepared = get_prepared().get(league.name)
    results = []
    for g in games.itertuples():
        if g.status in INACTIVE_STATUS or prepared is None:
            results.append(None)
            continue
        match = Match(league.name, season, matchday, g.datum_von, g.heim, g.gast)
        results.append(compute_match(prepared, match, 2 * (league.teams - 1)))
    return results
