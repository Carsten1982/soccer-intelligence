"""Bereich Top Anomalien (Dashboard-Briefing, Kapitel 5): die auffälligsten Begegnungen des aktuellen
Spieltags aller aktiven Ligen. Die Auswahl erfolgt zentral in core/top.py (Regelwerk, Abschnitt 2.6).
Zeigt immer den aktuellen Spieltag, unabhängig von den Spieltag-Pfeilen in den Liga-Bereichen.
"""

from __future__ import annotations

from html import escape

import streamlit as st

from core.kpis import de_signed
from core.matchday import current_matchday, matchday_games
from core.top import NO_ANOMALIES_TEXT, TOP_KPIS, Candidate, TopEntry, select_top
from state import get_active_leagues, get_database, get_fixtures, today
from views import components as ui
from views.kpi_table import ANOMALY_LABEL, anomaly_cell, value_text
from views.liga import matchday_kpis
from views.registry import PAGES


def card_html(e: TopEntry) -> str:
    c, r = e.candidate, e.result
    text = f"<br>{escape(r.text)}" if r.text else ""
    return (
        '<div class="si-card">'
        f'<div class="si-card-top"><span class="si-rank">{e.rank}</span>'
        f'<span class="si-card-meta">{escape(c.league)} · Spieltag {c.matchday}</span></div>'
        f'<div class="si-card-match">{escape(c.home)} – {escape(c.away)}</div>'
        f'<div class="si-card-kpi">{escape(e.kpi_name)}</div>'
        f'<div class="si-card-value">{anomaly_cell(r.anomalie)} <strong>{value_text(r, r.hauptwert_rund)}</strong> · '
        f'{de_signed(r.abweichung_rund)} % · {ANOMALY_LABEL[r.anomalie]}</div>'
        f'<div class="si-desc"><strong>{escape(r.ueberschrift or "")}</strong>{text}</div>'
        "</div>"
    )


def collect_candidates() -> tuple[list[Candidate], list[str]]:
    """Begegnungen des aktuellen Spieltags je aktiver Liga, mit KPI-Ergebnissen."""
    fx = get_fixtures()
    heute = today()
    candidates, header_parts = [], []
    for order, league in enumerate(get_active_leagues()):
        fixtures = fx.leagues.get(league.name)
        md = current_matchday(fixtures, heute) if fixtures is not None else None
        header_parts.append(f"{league.name}: Spieltag {md.spieltag}" if md else f"{league.name}: –")
        if md is None:
            continue
        games = matchday_games(fixtures, md.saison, md.spieltag)
        for g, k in zip(games.itertuples(), matchday_kpis(league, md.saison, md.spieltag, games)):
            candidates.append(Candidate(league.name, order, md.saison, md.spieltag, g.datum_von, int(g.reihenfolge),
                                        g.heim, g.gast, g.status, k))
    return candidates, header_parts


def render() -> None:
    db = get_database()
    fx = get_fixtures()
    candidates, header_parts = collect_candidates()
    ui.header("Aktueller Spieltag", header_parts)          # eine Zeile je Liga, kompakt (Etappe F)

    if db.has_errors or fx.has_errors:
        ui.blocked_notice(db.has_errors, fx.has_errors, PAGES.get("datenqualitaet"))
        ui.footer()
        return

    st.markdown("### Top Anomalien")
    entries = select_top(candidates)
    if not entries:
        st.info(NO_ANOMALIES_TEXT, icon="ℹ️")
    else:
        leagues = {lg.name: lg for lg in get_active_leagues()}
        cols = st.columns(2)
        for i, e in enumerate(entries):
            with cols[i % 2]:
                st.markdown(card_html(e), unsafe_allow_html=True)
                page = PAGES.get(f"liga_{leagues[e.candidate.league].url}")
                if page is not None:
                    try:
                        st.page_link(page, label=f"Zur {e.candidate.league} →")
                    except Exception:  # noqa: BLE001 - ausserhalb der Navigation (Tests)
                        pass
    st.caption(f"Berücksichtigt: KPI 02–09 ({len(TOP_KPIS)} KPIs) mit leichter oder starker Anomalie, ohne vorläufige "
               "Werte und ohne verschobene oder abgesagte Spiele. Höchstens vier Einträge, pro Begegnung einer. "
               "Rangfolge: stark vor leicht, dann grösste Abweichung (Gewichtung wird mit der Schwellen-Analyse "
               "überarbeitet).")
    ui.footer()
