"""Bereich Top Anomalien (Dashboard-Briefing, Kapitel 5).

Etappe B: Kopfbereich mit dem aktuellen Spieltag je Liga.
Die Auswahl der Top-Anomalien folgt in Etappe D, sobald die KPIs berechnet werden.
"""

from __future__ import annotations

import streamlit as st

from core.matchday import current_matchday
from state import get_active_leagues, get_database, get_fixtures, today
from views import components as ui
from views.registry import PAGES


def render() -> None:
    db = get_database()
    fx = get_fixtures()
    heute = today()
    parts = []
    for league in get_active_leagues():
        fixtures = fx.leagues.get(league.name)
        md = current_matchday(fixtures, heute) if fixtures is not None else None
        parts.append(f"{league.name}: Spieltag {md.spieltag}" if md else f"{league.name}: –")
    ui.header("Aktueller Spieltag", " · ".join(parts))

    if db.has_errors or fx.has_errors:
        ui.blocked_notice(db.has_errors, fx.has_errors, PAGES.get("datenqualitaet"))
        ui.footer()
        return

    st.info(
        "Hier erscheinen die auffälligsten Anomalien des aktuellen Spieltags aller Ligen (höchstens vier). "
        "Die Auswahl folgt in Etappe D, sobald die KPIs berechnet werden.",
        icon="🛠️",
    )
    ui.footer()
