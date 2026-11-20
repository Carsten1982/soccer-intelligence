"""Bereich Top Anomalien (Dashboard-Briefing, Kapitel 5): die auffälligsten anstehenden Begegnungen aller aktiven
Ligen. Seit 0.16 (Spielplan v2.1, 4.7, Designentwurf 16.11.2026) je Liga der zeitlich nächste Block, nur Spiele mit
Werten; die Blöcke bildet core/anzeige.py, die Auswahl core/top.py (Regelwerk, Abschnitt 2.6; seit 0.19 nach
Prognosewert, seit 0.20 Signalqualität, mit Liga-Mix). Seit 0.20 bleiben gespielte Spiele ausgegraut stehen, mit den
Werten ihres Schnappschusses; es rückt kein anderes Spiel nach.
Unabhängig von den Spieltag-Pfeilen in den Liga-Bereichen.
"""

from __future__ import annotations

from datetime import datetime
from html import escape

import streamlit as st

from core import anzeige as A
from core import schnappschuss as S
from core.config import League
from core.kpis import de_signed
from core.top import LOW_HINT, MAX_ENTRIES, MAX_PER_LEAGUE, NO_ANOMALIES_TEXT, Candidate, TopEntry, has_low, select_top
from importer.einstellungen import IMPORT_DIR
from state import (
    get_active_leagues, get_database, get_fixtures, get_results, get_round_kpis, last_import, now,
)
from views import components as ui
from views.kpi_table import ANOMALY_LABEL, anomaly_cell, derivation, value_text
from views.registry import PAGES


def card_html(e: TopEntry) -> str:
    c, r = e.candidate, e.result
    text = f"<br>{escape(r.text)}" if r.text else ""
    when = f" · <b>{escape(c.when)}</b>" if c.when else ""
    return (
        f'<div class="si-card{" si-card-played" if c.played else ""}">'
        f'<div class="si-card-top"><span class="si-rank">{e.rank}</span>'
        f'<span class="si-card-meta">{escape(c.league)} · Spieltag {c.matchday}{when}</span></div>'
        f'<div class="si-card-match">{escape(c.home)} – {escape(c.away)}</div>'
        f'<div class="si-card-kpi">{escape(e.kpi_name)}</div>'
        f'<div class="si-card-value">{anomaly_cell(r.anomalie)} <strong>{value_text(r, r.hauptwert_rund)}</strong> · '
        f'{de_signed(r.abweichung_rund)} % · {ANOMALY_LABEL[r.anomalie]}</div>'
        f'<div class="si-desc"><strong>{escape(r.ueberschrift or "")}</strong>{text}</div>'
        + derivation(r) +
        "</div>"
    )


def league_blocks(at: datetime) -> list[tuple[League, A.Block | None]]:
    """Der zeitlich nächste Block je aktiver Liga (None: kein Spiel im Spielplan)."""
    fx = get_fixtures()
    stand = last_import()
    out = []
    for league in get_active_leagues():
        fixtures = fx.leagues.get(league.name)
        out.append((league, A.top_block(fixtures, at, stand) if fixtures is not None else None))
    return out


def collect_candidates(blocks: list[tuple[League, A.Block | None]], at: datetime) -> list[Candidate]:
    """Spiele der teilnehmenden Blöcke mit Werten (Spielplan v2.1, 4.5). Seit 0.20 auch angepfiffene Spiele mit den
    Werten ihres Schnappschusses (4.7: kein Nachrücken)."""
    fx = get_fixtures()
    candidates = []
    for order, (league, block) in enumerate(blocks):
        if block is None or not block.takes_part:
            continue
        fxp = A.prepare(fx.leagues[league.name])
        results = get_results(league)
        kpis: dict = {}
        for g in block.games.itertuples():
            if A.values_gate(fxp, g, at, results) is not None:            # vor dem Anstoss noch ohne Werte
                continue
            key = (g.saison, int(g.spieltag))
            if key not in kpis:
                kpis[key] = get_round_kpis(league, *key)
            shown = S.shown_values(IMPORT_DIR, league.url, g, kpis[key].get(int(g.reihenfolge)), at, results, fxp)
            if shown.kpis is None:
                continue
            when = A.date_cell(g, at, results)
            candidates.append(Candidate(league.name, order, g.saison, int(g.spieltag), g.datum_von,
                                        int(g.reihenfolge), g.heim, g.gast, g.status, shown.kpis,
                                        when.text + when.strong, played=when.played))
    return candidates


def render() -> None:
    db = get_database()
    fx = get_fixtures()
    at = now()
    blocks = league_blocks(at)
    ui.header(subtitle="KPI-Übersicht pro Spiel – je Liga der anstehende Spieltag")
    st.markdown(ui.chips_html([(lg.name, b.header if b else "–") for lg, b in blocks]), unsafe_allow_html=True)

    if db.has_errors or fx.has_errors:                     # erst danach rechnen (H.1)
        ui.blocked_notice(db.has_errors, fx.has_errors, PAGES.get("datenqualitaet"))
        ui.footer()
        return

    st.markdown("### Top Anomalien")
    entries = select_top(collect_candidates(blocks, at))
    if not entries:
        st.info(NO_ANOMALIES_TEXT, icon="ℹ️")
    else:
        if len(entries) < MAX_ENTRIES:
            st.caption(f"Aktuell nur {len(entries)} auffällige{'s' if len(entries) == 1 else ''} "
                       f"Spiel{'' if len(entries) == 1 else 'e'}.")
        if has_low(entries):
            st.caption(LOW_HINT)
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
    st.caption(selection_text())
    ui.footer()


_WORDS = {1: "ein", 2: "zwei", 3: "drei", 4: "vier"}


def selection_text() -> str:
    """Text unter der Liste mit Zwischentiteln und Absätzen (Wortlaut Carsten 18.11.2026, Version 0.19.1)."""
    per_league = _WORDS.get(MAX_PER_LEAGUE, str(MAX_PER_LEAGUE))
    return (
        "**Berücksichtigte Spiele**\n\n"
        "Einbezogen werden die anstehenden Spieltage aller Ligen sowie Nachhol- und vorgezogene Spiele. Je Liga zählt "
        f"der nächste Spieltag, wenn er innerhalb der nächsten {A.PAUSE_DAYS} Tage beginnt. Sonderspiele vor dem "
        "regulären Spieltag werden separat aufgeführt.\n\n"
        "Es zählen nur Spiele, für die vollständige, nicht vorläufige Werte vorliegen. Die Liste steht vor dem ersten "
        "Anpfiff fest: Gespielte Spiele bleiben ausgegraut an ihrem Platz, es rückt kein anderes Spiel nach.\n\n"
        "**Auswahl der Auffälligkeiten**\n\n"
        "Eine Kennzahl gilt als auffällig, wenn ihre Abweichung über der jeweiligen Schwelle der Liga liegt.\n\n"
        "Die Auswahl erfolgt nach der Signalqualität: zuerst stark, dann mittel und zuletzt gering. Innerhalb jeder Stufe "
        "entscheidet die grösste Abweichung.\n\n"
        "**Verteilung der Spiele**\n\n"
        "Pro Begegnung wird nur eine Auffälligkeit angezeigt – jene mit der höchsten Signalqualität.\n\n"
        f"Pro Liga werden in der Regel höchstens {per_league} Spiele berücksichtigt. Gibt es in anderen Ligen nicht genügend "
        "Auffälligkeiten, können weitere Spiele aus derselben Liga hinzukommen.\n\n"
        f"Maximale Anzahl: {MAX_ENTRIES} Spiele"
    )
