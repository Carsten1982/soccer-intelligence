"""Liga-Bereich: alle Begegnungen eines Spieltags mit KPI 01–04 (Dashboard-Briefing, Kapitel 4 und 7–9).

Angezeigt wird der aktuelle Spieltag. Mit den Pfeilen lassen sich frühere Spieltage wählen (nicht in die Zukunft);
die Auswahl steht in der Adresse (?spieltag=1). Die KPIs werden immer so berechnet, als wäre der gewählte
Spieltag noch nicht gespielt (Stichtag „Datum von“).
"""

from __future__ import annotations

import streamlit as st

from core.config import League
from core.fixtures import INACTIVE_STATUS
from core.kpis import Match, compute_match
from core.matchday import (
    Matchday, Selection, date_range, matchday_games, matchday_overview, params_for, season_short, select_matchday,
)
from state import get_database, get_fixtures, get_prepared, today
from views import components as ui
from views import kpi_table
from views.registry import PAGES


def _go_to(md: Matchday, current: Matchday) -> None:
    """Pfeil geklickt: Auswahl in die Adresse schreiben (aktueller Spieltag = ohne Parameter)."""
    st.query_params.clear()
    for key, value in params_for(md, current).items():
        st.query_params[key] = value


def _matchday_header(league: League, sel: Selection) -> None:
    left, right = st.columns([3, 2], vertical_alignment="bottom")
    left.markdown(ui.title_html(), unsafe_allow_html=True)
    md = sel.selected
    with right:
        b_prev, box, b_next = st.columns([1, 5, 1], vertical_alignment="bottom")
        b_prev.button("◀", key=f"prev_{league.url}", help="Vorheriger Spieltag", disabled=sel.previous is None,
                      on_click=_go_to, args=(sel.previous, sel.current) if sel.previous else None)
        label = "Aktueller Spieltag" if sel.is_current else "Ausgewählter Spieltag"
        box.markdown(ui.matchday_box_html(label, f"Saison {season_short(md.saison)} · Spieltag {md.spieltag}"),
                     unsafe_allow_html=True)
        b_next.button("▶", key=f"next_{league.url}", help="Nächster Spieltag (höchstens bis zum aktuellen)",
                      disabled=sel.next is None,
                      on_click=_go_to, args=(sel.next, sel.current) if sel.next else None)
    if sel.requested_invalid:
        st.caption("Der Spieltag aus der Adresse ist nicht verfügbar. Angezeigt wird der aktuelle Spieltag.")
    if not sel.is_current:
        st.button(f"Zum aktuellen Spieltag ({sel.current.spieltag})", key=f"current_{league.url}",
                  on_click=_go_to, args=(sel.current, sel.current))


def render(league: League) -> None:
    db = get_database()
    fx = get_fixtures()
    fixtures = fx.leagues.get(league.name)
    overview = matchday_overview(fixtures, today()) if fixtures is not None else []
    sel = select_matchday(overview, dict(st.query_params))

    if sel is not None:
        _matchday_header(league, sel)
    else:
        ui.header()

    if db.has_errors or fx.has_errors:
        ui.blocked_notice(db.has_errors, fx.has_errors, PAGES.get("datenqualitaet"))
        ui.footer()
        return

    if sel is None:
        st.info(f"Für die {league.name} ist im Spielplan noch kein Spieltag eingetragen.", icon="📅")
        ui.footer()
        return

    md = sel.selected
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
