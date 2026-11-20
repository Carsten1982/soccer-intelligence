"""Liga-Bereich: kommende Spiele nach Spieltag mit KPI 01–09 (Dashboard-Briefing, Kapitel 4 und 7–9;
seit 0.16 nach Spielplan v2.1, Abschnitt 4, und dem Designentwurf vom 16.11.2026).

Ohne Auswahl („Kommende Spiele“) zeigt die Seite Abschnitte, je Abschnitt genau einen offiziellen Spieltag:
den anstehenden Spieltag, weitere Spieltage, die heute bis heute + 5 beginnen, und Sonderspiele (Nachholspiel,
vorgezogen) unter ihrer ursprünglichen Nummer; dazu bei Bedarf eine Hinweis-Box (Winter-, Spiel-, Sommerpause,
veralteter Datenstand). Welche Spiele erscheinen, entscheidet core/anzeige.py; hier wird nur dargestellt.

Mit den Pfeilen lässt sich ein einzelner Spieltag wählen: zurück alle Spieltage der Saison und der Vorsaison,
vorwärts höchstens 2 über den anstehenden hinaus. Die Auswahl steht in der Adresse (?spieltag=14, bei einer anderen
Saison zusätzlich &saison=2025-26). Die KPIs werden immer so berechnet, als wäre das Spiel noch nicht gespielt
(Stichtag „Datum von“); berechnet in core/results.py, zwischengespeichert in state.get_matchday_kpis. Seit 0.20
zeigen angepfiffene Spiele die Werte ihres Schnappschusses (core/schnappschuss.py), wie die Website.
"""

from __future__ import annotations

from datetime import datetime
from html import escape

import streamlit as st

from core import anzeige as A
from core import schnappschuss as S
from core.config import League
from core.matchday import PARAM_MATCHDAY, PARAM_SEASON, season_param, season_short
from importer.einstellungen import IMPORT_DIR
from state import get_database, get_fixtures, get_results, get_round_kpis, last_import, now
from views import components as ui
from views import kpi_table
from views.registry import PAGES

Key = tuple[str, int]


# --- Auswahl über die Adresse ---------------------------------------------------------------------

def requested(params: dict, keys: list[Key], anchor: Key | None) -> tuple[Key | None, bool]:
    """(gewählter Spieltag oder None = kommende Spiele, Adresse ungültig?)."""
    raw_md, raw_season = params.get(PARAM_MATCHDAY), params.get(PARAM_SEASON)
    if raw_md is None and raw_season is None:
        return None, False
    season = anchor[0] if anchor else None
    if raw_season is not None:
        season = next((s for s, _ in keys if season_param(s) == str(raw_season)), None)
    try:
        wanted = int(str(raw_md))
    except (TypeError, ValueError):
        return None, True
    key = (season, wanted)
    return (key, False) if key in keys else (None, True)


def params_for(key: Key | None, anchor: Key | None) -> dict[str, str]:
    if key is None:
        return {}
    params = {PARAM_MATCHDAY: str(key[1])}
    if anchor is None or key[0] != anchor[0]:
        params[PARAM_SEASON] = season_param(key[0])
    return params


def arrows(selected: Key | None, keys: list[Key], view: A.Upcoming) -> tuple[Key | None, Key | None]:
    """Ziele der Pfeile ◀ und ▶. Ohne Auswahl gehen sie vom anstehenden Spieltag aus (in der Sommerpause vom
    letzten): ◀ zum Spieltag davor, ▶ zum nächsten, der nicht schon als Abschnitt auf der Seite steht."""
    if selected is None:
        if view.anchor is None or view.anchor not in keys:
            return None, None
        i = keys.index(view.anchor)
        before = keys[i - 1] if i > 0 else None
        if not view.anchor_shown:
            return before, view.anchor
        return before, keys[i + 1] if i + 1 < len(keys) else None
    i = keys.index(selected)
    return (keys[i - 1] if i > 0 else None), (keys[i + 1] if i + 1 < len(keys) else None)


def _go_to(key: Key | None, anchor: Key | None) -> None:
    st.query_params.clear()
    for k, v in params_for(key, anchor).items():
        st.query_params[k] = v


# --- Bausteine --------------------------------------------------------------------------------------

def notice_html(n: A.Notice) -> str:
    """Hinweis-Box: „Winterpause – nächster Spieltag am Fr 08.01.2027 (Spieltag 15)“ bzw. der Datenstand."""
    if n.kind == A.STALE:
        return (f'<div class="si-note si-note-stale">⚠ {escape(n.title)} <b>{escape(n.text)}</b> – '
                f'{escape(n.detail)} <small>(wenn der letzte erfolgreiche Importlauf älter als '
                f'{A.STALE_HOURS} Stunden ist)</small></div>')
    text = f" – {escape(n.text)}" if n.text else ""
    detail = f" {escape(n.detail)}" if n.detail else ""
    return f'<div class="si-note"><b>{escape(n.title)}</b>{text}{detail}</div>'


def section_head_html(sec: A.Section, single: bool) -> str:
    """„Spieltag 23 [vorgezogen] Mi 02.12. · 2 Spiele (übrige Spiele des Spieltags im Februar)“."""
    extra = []
    if sec.rest:
        extra.append(sec.rest)
    if sec.hidden and not single:
        counts = {s: sec.hidden.count(s) for s in dict.fromkeys(sec.hidden)}
        extra.append(", ".join(f"{A.games_text(n)} {s}" for s, n in counts.items()) + " – beim Blättern sichtbar")
    more = f" ({escape('; '.join(extra))})" if extra else ""
    meta = f"{A.days_text(sec.first, sec.last)} · {A.games_text(len(sec.games))}{more}"
    return (f'<div class="si-sec"><span class="si-sec-t">Spieltag {sec.spieltag}</span>'
            f'{kpi_table.tag_html(sec.hinweis)}<span class="si-sec-m">{meta}</span></div>')


def date_html(cell: A.DateCell) -> str:
    strong = f"<b>{escape(cell.strong)}</b>" if cell.strong else ""
    return f"{escape(cell.text)}{strong}"


def section_rows(league: League, sec: A.Section, fxp, at: datetime, results: dict,
                 single: bool) -> list[kpi_table.TableRow]:
    rows, kpis = [], {}
    for g in sec.games.itertuples():
        key = (g.saison, int(g.spieltag))
        if key not in kpis:
            kpis[key] = get_round_kpis(league, *key)
        cell = A.date_cell(g, at, results)
        # ab dem Anstoss die Werte des Schnappschusses (seit 0.20), vorher die aktuell berechneten
        shown = S.shown_values(IMPORT_DIR, league.url, g, kpis[key].get(int(g.reihenfolge)), at, results, fxp)
        k, gate = shown.kpis, None
        if shown.quelle == S.WAITING:
            gate = WAITING_TEXT
        elif cell.active and k is not None:
            gate = A.values_gate(fxp, g, at, results)               # nach dem Anstoss nie (seit 0.20)
        rows.append(kpi_table.TableRow(g.heim, g.gast, "", k if cell.active else None,      # Status steht im Datum
                                       date_html(cell), cell.grey, gate, g.hinweis if single else ""))
    return rows


WAITING_TEXT = "Werte folgen nachträglich, sobald das Ergebnis des vorherigen Spiels übernommen ist"


def render_section(league: League, sec: A.Section, fxp, at: datetime, results: dict, single: bool = False) -> None:
    st.markdown(section_head_html(sec, single), unsafe_allow_html=True)
    rows = section_rows(league, sec, fxp, at, results, single)
    st.markdown(kpi_table.compact_table_html(rows), unsafe_allow_html=True)


LEGEND_UPCOMING = ('<div class="si-legend">Gespielte Spiele ab Anpfiff + 2 Stunden grau mit „Gespielt“, nach der '
                   'Übernahme mit Ergebnis; ihre KPI-Werte bleiben stehen (Schnappschuss vor dem Spiel). Abschnitte '
                   'zeitlich sortiert, Spieltagsnummer immer die offizielle. „Werte ab …“: erst wenn beide Teams ihr '
                   'vorheriges Spiel gespielt haben.</div>')


# --- Seite --------------------------------------------------------------------------------------------

def _header(league: League, selected: Key | None, keys: list[Key], view: A.Upcoming, at: datetime) -> None:
    left, right = st.columns([3, 2], vertical_alignment="bottom")
    left.markdown(ui.title_html(ui.SUBTITLE if selected else ui.SUBTITLE_UPCOMING), unsafe_allow_html=True)
    before, after = arrows(selected, keys, view)
    with right:
        b_prev, box, b_next = st.columns([1, 5, 1], vertical_alignment="bottom")
        b_prev.button("◀", key=f"prev_{league.url}", help="Vorheriger Spieltag", disabled=before is None,
                      on_click=_go_to, args=(before, view.anchor))
        if selected is None:
            season = view.anchor[0] if view.anchor else keys[-1][0]
            label, value = "Kommende Spiele", f"Saison {season_short(season)} · ab {A.day_text(at.date())}"
        else:
            label, value = "Ausgewählter Spieltag", f"Saison {season_short(selected[0])} · Spieltag {selected[1]}"
        box.markdown(ui.matchday_box_html(label, value), unsafe_allow_html=True)
        b_next.button("▶", key=f"next_{league.url}",
                      help=f"Nächster Spieltag (höchstens {A.FORWARD} über den anstehenden hinaus)",
                      disabled=after is None, on_click=_go_to, args=(after, view.anchor))


def render(league: League) -> None:
    db = get_database()
    fx = get_fixtures()
    fixtures = fx.leagues.get(league.name)
    if fixtures is None or fixtures.empty:
        ui.header()
        if db.has_errors or fx.has_errors:
            ui.blocked_notice(db.has_errors, fx.has_errors, PAGES.get("datenqualitaet"))
        else:
            st.info(f"Für die {league.name} ist im Spielplan noch kein Spieltag eingetragen.", icon="📅")
        ui.footer()
        return

    at = now()
    view = A.upcoming(fixtures, at, last_import())
    keys = A.choices(fixtures, view.anchor)
    selected, invalid = requested(dict(st.query_params), keys, view.anchor)
    _header(league, selected, keys, view, at)
    if invalid:
        st.caption("Der Spieltag aus der Adresse ist nicht verfügbar. Angezeigt werden die kommenden Spiele.")

    if db.has_errors or fx.has_errors:                     # erst danach rechnen (H.1)
        ui.blocked_notice(db.has_errors, fx.has_errors, PAGES.get("datenqualitaet"))
        ui.footer()
        return

    fxp = A.prepare(fixtures)
    results = get_results(league)
    if selected is not None:
        st.button("Zu den kommenden Spielen", key=f"current_{league.url}", on_click=_go_to,
                  args=(None, view.anchor))
        sec = A.round_section(fxp, *selected, full=True)
        st.caption(f"{league.name} · Spieltag {selected[1]} · Berechnung so, als wären die Spiele noch nicht gespielt "
                   "(Stichtag = Spieltermin) · Zeile anklicken für Details")
        render_section(league, sec, fxp, at, results, single=True)
    else:
        n = len(view.sections)
        if n:
            st.caption(f"{league.name} · {'1 Abschnitt' if n == 1 else f'{n} Abschnitte'} · Berechnung so, als wären "
                       "die Spiele noch nicht gespielt (Stichtag = Spieltermin) · Zeile anklicken für Details")
        if view.notice is not None:
            st.markdown(notice_html(view.notice), unsafe_allow_html=True)
        for sec in view.sections:
            render_section(league, sec, fxp, at, results)
        if not view.sections and view.anchor is not None and not view.anchor_shown:
            st.caption("Mit dem Pfeil ◀ sind die bisherigen Spieltage mit Ergebnissen erreichbar.")
    st.markdown(kpi_table.LEGEND_HTML, unsafe_allow_html=True)
    st.markdown(LEGEND_UPCOMING, unsafe_allow_html=True)
    ui.footer()
