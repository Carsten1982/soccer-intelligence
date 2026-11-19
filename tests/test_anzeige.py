"""Anzeige kommender Spieltage (Version 0.16): Testfälle A1–A27 aus docs/07_Spielplan_Anzeige.md, Abschnitt 7.2.

Ohne Netz und ohne Streamlit: kleine, feste Spielpläne (4 Teams, 2 Spiele je Spieltag) und die echten Saisonlisten
2026/27 aller vier Ligen (Stand 15.11.2026, tests/referenz/api). „Jetzt“ und der Beginn des letzten Importlaufs
werden übergeben (Europe/Zurich, ohne Zeitzonenangabe). Seit 0.20: Gespielt ab Anpfiff + 2 Stunden, Datenstand
48 Stunden, Top-Block ohne Nachrücken, „Werte ab“ nach dem Anstoss nie (Testfälle A28–A35).
"""

from __future__ import annotations

import gzip
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

from core import anzeige as A
from core.fixtures import FIXTURE_COLUMNS

S, PREV = "2026/2027", "2025/2026"
API = Path(__file__).resolve().parent / "referenz" / "api"


# --- Hilfen ------------------------------------------------------------------------------------------

def game(md, day, clock="15:30", home="A", away="B", status="geplant", hint="", termin="bestätigt", saison=S):
    return {"saison": saison, "spieltag": md, "datum_von": day, "datum_bis": day, "heim": home, "gast": away,
            "status": status, "anstoss": clock, "termin": termin, "hinweis": hint, "api_status": "NS"}


def rnd(md, first, last=None, saison=S, clock="15:30"):
    """Ein Spieltag mit 2 Spielen: A–B am ersten Tag, C–D am letzten Tag (Heimrecht wechselt)."""
    last = last or first
    pairs = (("A", "B"), ("C", "D")) if md % 2 else (("B", "A"), ("D", "C"))
    return [game(md, first, clock, *pairs[0], saison=saison), game(md, last, clock, *pairs[1], saison=saison)]


def plan(*groups) -> pd.DataFrame:
    rows = [g for grp in groups for g in (grp if isinstance(grp, list) else [grp])]
    for i, r in enumerate(rows):
        r.update(excel_row=i + 2, reihenfolge=i, api_id=None)
    return pd.DataFrame(rows, columns=FIXTURE_COLUMNS)


def d(text: str) -> date:
    return date.fromisoformat(text)


def at(text: str) -> datetime:
    return datetime.fromisoformat(text)


def view(fx, now: str, imported: int | None = 0):
    """imported = vor wie vielen Tagen der letzte erfolgreiche Lauf begann (gleiche Uhrzeit), None = nie."""
    now_dt = at(now)
    return A.upcoming(fx, now_dt, None if imported is None else now_dt - timedelta(days=imported))


def keys(v) -> list:
    return [(s.spieltag, s.hinweis) for s in v.sections]


def played(fx, before: str) -> dict:
    """Ergebnisse (1:0) für alle aktiven Spiele, die vor dem Zeitpunkt angepfiffen wurden."""
    p = A.prepare(fx)
    return {(r.saison, r.heim, r.gast): (1, 0) for r in p.itertuples() if r.aktiv and r.anstoss_zeit < at(before)}


def real_plan(league: str, today: date) -> pd.DataFrame:
    """Echte Spielliste 2026/27 (API-Football, Stand 15.11.2026) wie im Import (importer.spielplan.fixture_rows)."""
    from importer.spielplan import fixture_rows
    from importer.teams import TeamNames
    data = json.loads(gzip.decompress((API / f"{league}_2026_spielliste.json.gz").read_bytes()))["response"]
    rows = fixture_rows(data, TeamNames(by_id={}, renames={}), today)
    return plan([{"saison": r["Saison"], "spieltag": r["Spieltag"], "datum_von": r["Datum von"].date(),
                  "datum_bis": r["Datum bis"].date(), "heim": r["Heimmannschaft"], "gast": r["Gastmannschaft"],
                  "status": r["Status"] or "geplant", "anstoss": r["Anstoss"], "termin": r["Termin"],
                  "hinweis": r["Hinweis"], "api_status": r["API-Status"]} for r in rows])


# Grundplan: Spieltage Fr–So im Wochenrhythmus ab Fr 06.11.2026
WEEKS = plan(rnd(1, d("2026-11-06"), d("2026-11-08")), rnd(2, d("2026-11-13"), d("2026-11-15")),
             rnd(3, d("2026-11-20"), d("2026-11-22")), rnd(4, d("2026-11-27"), d("2026-11-29")))


# --- Texte und Grundlagen ------------------------------------------------------------------------------

def test_texts_weekday_and_weekend():
    assert A.day_text(d("2026-11-20")) == "Fr 20.11." and A.day_text_year(d("2027-01-08")) == "Fr 08.01.2027"
    assert A.days_text(d("2026-11-20"), d("2026-11-22")) == "Fr 20.11. – So 22.11."
    assert A._weekend(d("2027-02-06")) == "Wochenende 06./07.02."           # Sa
    assert A._weekend(d("2027-02-07")) == "Wochenende 06./07.02."           # So
    assert A._weekend(d("2027-01-31")) == "Wochenende 30./31.01."
    assert A._weekend(d("2027-05-01")) == "Wochenende 01./02.05."
    assert A._weekend(d("2026-10-31")) == "Wochenende 31.10./01.11."        # über das Monatsende
    assert A._weekend(d("2027-01-12")) == "Di 12.01."                       # kein Wochenende
    assert A.games_text(1) == "1 Spiel" and A.games_text(9) == "9 Spiele"


def test_kickoff_time_open_and_old_plan_count_until_day_end():
    fx = A.prepare(plan(game(1, d("2026-11-21"), "18:30"), game(1, d("2026-11-21"), "18:30", "C", "D",
                                                                 termin="Zeit offen"),
                        game(1, d("2026-11-21"), "", "B", "A")))
    assert list(fx["anstoss_zeit"].dt.strftime("%H:%M")) == ["18:30", "23:59", "23:59"]


def test_stale_boundary_and_christmas():
    """A28 (seit 0.20): veraltet erst nach mehr als 48 Stunden ab Beginn des letzten erfolgreichen Laufs."""
    assert not A.is_stale(at("2026-11-14T04:00"), at("2026-11-16T04:00"))      # genau 48 Stunden: in Ordnung
    assert A.is_stale(at("2026-11-14T04:00"), at("2026-11-16T04:01")) and A.is_stale(None, at("2026-11-16T10:00"))
    assert A.is_stale(at("2026-11-13T04:00"), at("2026-11-16T03:00"))         # bis 0.19.1 (3 Tage) noch aktuell
    assert A._has_christmas(d("2026-12-20"), d("2027-01-08"))
    assert not A._has_christmas(d("2026-12-26"), d("2027-01-08")) and not A._has_christmas(d("2026-09-06"),
                                                                                          d("2026-09-25"))


# --- A1–A11: Abschnitte ----------------------------------------------------------------------------------

@pytest.mark.parametrize("now, first", [("2026-11-06T10:00", 1), ("2026-11-07T10:00", 1), ("2026-11-08T22:00", 1),
                                        ("2026-11-09T00:01", 2)])
def test_a1_round_visible_friday_to_sunday(now, first):
    v = view(WEEKS, now)
    assert v.sections[0].spieltag == first and v.notice is None
    assert (1, "") not in keys(v) or first == 1


def test_a2_played_game_stays_with_result_until_sunday_evening():
    v = view(WEEKS, "2026-11-08T12:00")
    sec = v.sections[0]
    assert sec.spieltag == 1 and len(sec.games) == 2
    cell = A.date_cell(next(sec.games.itertuples()), at("2026-11-08T12:00"), {(S, "A", "B"): (2, 1)})
    assert (cell.text, cell.strong, cell.grey, cell.played) == ("Fr 06.11. · ", "2:1", True, True)
    waiting = A.date_cell(next(sec.games.itertuples()), at("2026-11-08T12:00"), {})
    assert waiting.strong == "Gespielt" and waiting.grey and waiting.played          # seit 0.20 statt „Ergebnis folgt“


def test_a3_laliga_friday_to_monday():
    fx = plan(rnd(1, d("2026-11-06"), d("2026-11-09")), rnd(2, d("2026-11-13"), d("2026-11-16")))
    assert view(fx, "2026-11-09T22:00").sections[0].spieltag == 1                 # Mo: noch sichtbar
    assert keys(view(fx, "2026-11-10T08:00")) == [(2, "")]                         # Di: der nächste


def test_a4_english_week_two_sections_then_values():
    fx = plan(rnd(11, d("2026-11-28"), d("2026-11-29")), rnd(12, d("2026-12-05"), d("2026-12-05")),
              rnd(13, d("2026-12-08"), d("2026-12-09")), rnd(14, d("2026-12-12"), d("2026-12-13")))
    v = view(fx, "2026-12-05T10:00")
    assert keys(v) == [(12, ""), (13, "")]                    # 14 beginnt erst heute + 7
    fxp, res = A.prepare(fx), played(fx, "2026-12-05T00:00")
    g13 = next(v.sections[1].games.itertuples())
    assert A.values_gate(fxp, g13, at("2026-12-05T10:00"), res) == \
        "Werte ab So 06.12. – beide Teams spielen vorher noch (Spieltag 12)"
    v = view(fx, "2026-12-07T10:00")
    assert keys(v) == [(13, ""), (14, "")]
    res = played(fx, "2026-12-06T00:00")
    assert all(A.values_gate(fxp, g, at("2026-12-07T10:00"), res) is None for g in v.sections[0].games.itertuples())
    assert view(fx, "2026-12-09T23:00").sections[0].spieltag == 13                # bis Mittwochabend
    assert keys(view(fx, "2026-12-10T08:00")) == [(14, "")]


def test_a5_three_rounds_within_six_days_real_bundesliga():
    fx = real_plan("bundesliga", d("2027-01-09"))
    assert keys(view(fx, "2027-01-09T10:00")) == [(15, ""), (16, ""), (17, "")]
    assert keys(view(fx, "2027-01-08T10:00")) == [(15, ""), (16, "")]             # 17 beginnt erst heute + 7


@pytest.mark.parametrize("offset, shown", [(6, True), (7, False)])
def test_a6_window_today_plus_six(offset, shown):
    today = d("2026-11-09")
    fx = plan(rnd(1, d("2026-11-06"), d("2026-11-09")), rnd(2, today + timedelta(days=offset)))
    v = view(fx, "2026-11-09T10:00")
    assert ((2, "") in keys(v)) is shown


@pytest.mark.parametrize("offset, shown", [(5, True), (6, True), (7, False), (10, False)])
def test_a7_catchup_game_under_original_matchday(offset, shown):
    today = d("2026-11-16")
    fx = plan(rnd(1, d("2026-11-06"), d("2026-11-08")), rnd(2, d("2026-11-13"), d("2026-11-15")),
              rnd(3, d("2026-11-20"), d("2026-11-22")),
              game(1, today + timedelta(days=offset), "20:30", "E", "F", hint="Nachholspiel"))
    v = view(fx, "2026-11-16T10:00")
    assert ((1, "Nachholspiel") in keys(v)) is shown
    if shown:
        sec = next(s for s in v.sections if s.hinweis)
        assert sec.rest == "übrige Spiele des Spieltags im November" and len(sec.games) == 1


def test_a8_early_games_real_laliga_order():
    fx = real_plan("laliga", d("2026-12-01"))
    v = view(fx, "2026-12-01T10:00")
    assert keys(v) == [(23, "vorgezogen"), (15, "")]
    assert v.sections[0].rest == "übrige Spiele des Spieltags im Februar" and len(v.sections[0].games) == 2
    assert len(v.sections[1].games) == 10


def test_a9_two_rounds_same_day_by_number():
    fx = plan(rnd(4, d("2026-11-20")), rnd(3, d("2026-11-20"), d("2026-11-21")))
    assert keys(view(fx, "2026-11-18T10:00")) == [(3, ""), (4, "")]


def test_a10_time_open_and_provisional_are_not_postponed():
    fx = plan(game(1, d("2026-12-05"), "15:30", termin="Zeit offen"),
              game(1, d("2027-02-06"), "15:30", "C", "D", termin="vorläufig"),
              game(1, d("2026-11-20"), "20:30", "E", "F"))
    rows = list(A.prepare(fx).itertuples())
    now = at("2026-11-16T10:00")
    assert A.date_cell(rows[0], now, {}) == A.DateCell("", "Sa 05.12. · Zeit offen")
    assert A.date_cell(rows[1], now, {}) == A.DateCell("Wochenende 06./07.02. · Termin offen")
    assert A.date_cell(rows[2], now, {}) == A.DateCell("", "Fr 20.11. · 20:30")
    assert all(A.date_cell(r, now, {}).active for r in rows)


def test_a11_inactive_games_not_upcoming_but_in_round_with_status():
    fx = plan(rnd(1, d("2026-11-20"), d("2026-11-22")),
              game(1, d("2026-11-21"), "15:30", "E", "F", status="verschoben"),
              game(1, d("2026-11-21"), "15:30", "G", "H", status="abgebrochen"),
              game(1, d("2026-11-21"), "15:30", "I", "J", status="ausgesetzt"),
              game(1, d("2026-11-21"), "15:30", "K", "L", status="gewertet"))
    sec = view(fx, "2026-11-16T10:00").sections[0]
    assert len(sec.games) == 2 and sorted(sec.hidden) == ["abgebrochen", "ausgesetzt", "gewertet", "verschoben"]
    full = A.round_section(A.prepare(fx), S, 1, full=True)
    cells = [A.date_cell(r, at("2026-11-16T10:00"), {}) for r in full.games.itertuples()]
    assert len(full.games) == 6
    assert sorted(c.text for c in cells if not c.active) == ["Sa 21.11. · abgebrochen", "Sa 21.11. · ausgesetzt",
                                                             "Sa 21.11. · gewertet", "Sa 21.11. · verschoben"]
    assert all(c.grey for c in cells if not c.active)


# --- A12–A19: Pausen, Saisonende, Datenstand ---------------------------------------------------------------

def test_a12_pause_of_twelve_days_no_notice():
    fx = plan(rnd(9, d("2026-11-06"), d("2026-11-08")), rnd(10, d("2026-11-20"), d("2026-11-22")))
    v = view(fx, "2026-11-09T10:00")
    assert v.notice is None and keys(v) == [(10, "")]


@pytest.mark.parametrize("day, sections", [("2026-12-21", []), ("2026-12-24", []), ("2026-12-25", [(15, "")]),
                                           ("2027-01-07", [(15, ""), (16, "")])])
def test_a13_bundesliga_winter_break_real(day, sections):
    fx = real_plan("bundesliga", d(day))
    v = view(fx, f"{day}T10:00")
    assert v.notice.kind == A.WINTER and v.notice.text == "nächster Spieltag am Fr 08.01.2027"
    assert v.notice.detail == ("" if sections else "(Spieltag 15)")
    assert keys(v) == sections


BREAK = plan(rnd(4, d("2026-09-04"), d("2026-09-06")), rnd(5, d("2026-09-25"), d("2026-09-27")))


def test_a14_long_break_in_september():
    v = view(BREAK, "2026-09-08T10:00")                       # 17 Tage bis Spieltag 5
    assert (v.notice.kind, v.notice.title) == (A.BREAK, "Spielpause") and v.sections == []
    assert v.notice.text == "nächster Spieltag am Fr 25.09.2026" and v.notice.detail == "(Spieltag 5)"
    v = view(BREAK, "2026-09-11T10:00")                       # 14 Tage: Hinweis und Spieltag
    assert v.notice.kind == A.BREAK and keys(v) == [(5, "")]


def test_a15_exactly_fourteen_days_shows_round():
    assert keys(view(BREAK, "2026-09-11T00:00")) == [(5, "")]
    assert keys(view(BREAK, "2026-09-10T23:59")) == []


def test_a16_open_catchup_game_after_last_round_no_summer_break():
    fx = plan(rnd(33, d("2027-05-14"), d("2027-05-16")), rnd(34, d("2027-05-22")),
              game(30, d("2027-06-10"), "20:30", "E", "F", hint="Nachholspiel"))
    v = view(fx, "2027-05-24T10:00")
    assert v.notice is None and keys(v) == [(30, "Nachholspiel")]          # offenes Spiel normal gezeigt
    fx = plan(rnd(34, d("2027-05-22")), game(34, d("2027-05-22"), "15:30", "E", "F", status="verschoben"))
    v = view(fx, "2027-05-24T10:00")
    assert v.notice is None and keys(v) == [(34, "")]                       # verschoben, noch offen


def test_a17_summer_break_all_played():
    fx = plan(rnd(33, d("2027-05-14"), d("2027-05-16")), rnd(34, d("2027-05-22")))
    v = view(fx, "2027-06-10T10:00")
    assert (v.notice.kind, v.notice.title, v.notice.text) == (A.SUMMER, "Sommerpause", "")
    assert keys(v) == [(34, "")] and v.anchor == (S, 34) and v.anchor_shown


@pytest.mark.parametrize("days, notice", [(30, True), (15, True), (14, False)])
def test_a18_new_season(days, notice):
    start = d("2027-08-20")
    fx = plan(rnd(34, d("2027-05-22"), saison=S), rnd(1, start, start + timedelta(days=2), saison="2027/2028"))
    now = datetime.combine(start - timedelta(days=days), datetime.min.time())
    v = A.upcoming(fx, now, now)
    if notice:
        assert (v.notice.kind, v.notice.text) == (A.SEASON_START, "Saisonstart am Fr 20.08.2027")
        assert [(s.saison, s.spieltag) for s in v.sections] == [(S, 34)]
    else:
        assert v.notice is None and [(s.saison, s.spieltag) for s in v.sections] == [("2027/2028", 1)]
    assert v.anchor == ("2027/2028", 1)                    # die neue Saison ist Standard für die Pfeile


def test_a19_stale_import_hides_pause_notice():
    fx = real_plan("bundesliga", d("2026-12-23"))
    v = view(fx, "2026-12-23T10:00", imported=4)
    assert v.stale and v.notice.kind == A.STALE and v.notice.text == "Sa 19.12.2026" and v.sections == []
    v = view(fx, "2026-11-16T10:00", imported=4)              # auch während der Saison
    assert v.notice.kind == A.STALE and keys(v) == [(10, "")]
    v = view(fx, "2026-11-16T10:00", imported=None)
    assert v.notice.text.startswith("unbekannt")
    assert view(fx, "2026-12-23T10:00", imported=2).notice.kind == A.WINTER       # 48 Stunden: noch aktuell (0.20)
    assert view(fx, "2026-12-23T10:00", imported=3).notice.kind == A.STALE        # bis 0.19.1 noch aktuell


# --- A20: Navigation ----------------------------------------------------------------------------------------

def test_a20_navigation_back_all_forward_two():
    fx = plan(rnd(1, d("2025-08-22"), saison=PREV), rnd(2, d("2025-08-29"), saison=PREV),
              *[rnd(n, d("2026-08-21") + timedelta(days=7 * (n - 1))) for n in range(1, 7)])
    v = view(fx, "2026-08-28T10:00")
    assert v.anchor == (S, 2)
    assert A.choices(fx, v.anchor) == [(PREV, 1), (PREV, 2), (S, 1), (S, 2), (S, 3), (S, 4)]
    assert A.choices(fx, None) == [(PREV, 1), (PREV, 2)] + [(S, n) for n in range(1, 7)]


# --- A21–A22: „Werte ab“ ------------------------------------------------------------------------------------

def test_a21_values_after_previous_game_of_both_teams():
    fx = plan(rnd(1, d("2026-11-06"), d("2026-11-08")), game(2, d("2026-11-13"), "20:30", "A", "C"),
              game(2, d("2026-11-15"), "15:30", "B", "D"), game(3, d("2026-11-17"), "20:30", "B", "A"),
              game(3, d("2026-11-17"), "20:30", "D", "C"))
    fxp, now = A.prepare(fx), at("2026-11-12T10:00")
    res = played(fx, "2026-11-12T00:00")
    a_b = next(r for r in fxp.itertuples() if r.spieltag == 3 and r.heim == "B")
    assert A.values_gate(fxp, a_b, now, res) == "Werte ab Mo 16.11. – beide Teams spielen vorher noch (Spieltag 2)"
    res[(S, "A", "C")] = (1, 1)
    assert A.values_gate(fxp, a_b, at("2026-11-14T10:00"), res) == "Werte ab Mo 16.11. – B spielt vorher noch (So 15.11.)"
    res[(S, "B", "D")] = (0, 0)
    assert A.values_gate(fxp, a_b, at("2026-11-16T10:00"), res) is None
    del res[(S, "B", "D")]                                    # gespielt, aber noch nicht übernommen
    assert A.values_gate(fxp, a_b, at("2026-11-16T10:00"), res) == \
        "Werte folgen, sobald das Ergebnis vom So 15.11. übernommen ist"


def test_a21_both_teams_in_different_rounds_named():
    fx = plan(rnd(1, d("2026-11-06"), d("2026-11-08")), game(2, d("2026-11-13"), "20:30", "A", "C"),
              game(1, d("2026-11-15"), "15:30", "B", "D", hint="Nachholspiel"), game(3, d("2026-11-17"), "20:30", "B", "A"))
    fxp = A.prepare(fx)
    b_a = next(r for r in fxp.itertuples() if r.spieltag == 3)
    assert A.values_gate(fxp, b_a, at("2026-11-12T10:00"), played(fx, "2026-11-12T00:00")) == \
        "Werte ab Mo 16.11. – B (So 15.11.) und A (Fr 13.11.) spielen vorher noch"


def test_a21_first_game_in_plan_has_values():
    fx = plan(rnd(1, d("2026-08-21"), d("2026-08-23")))
    fxp = A.prepare(fx)
    assert all(A.values_gate(fxp, r, at("2026-08-20T10:00"), {}) is None for r in fxp.itertuples())


def test_a22_previous_game_by_real_date_not_matchday_number():
    """A spielt sein Nachholspiel von Spieltag 1 nach Spieltag 3: massgebend für Spieltag 4 ist das Nachholspiel."""
    fx = plan(game(1, d("2026-11-06"), "15:30", "C", "D"),
              game(1, d("2026-11-25"), "20:30", "A", "E", hint="Nachholspiel"),
              rnd(2, d("2026-11-13"), d("2026-11-15")), rnd(3, d("2026-11-20"), d("2026-11-22")),
              game(4, d("2026-11-28"), "15:30", "A", "C"))
    fxp = A.prepare(fx)
    res = played(fx, "2026-11-23T00:00")
    a_c = next(r for r in fxp.itertuples() if r.spieltag == 4)
    assert A.values_gate(fxp, a_c, at("2026-11-23T10:00"), res) == \
        "Werte ab Do 26.11. – A spielt vorher noch (Mi 25.11.)"


def test_previous_game_ignores_postponed():
    fx = plan(rnd(1, d("2026-11-06"), d("2026-11-08")), game(2, d("2026-11-13"), "20:30", "A", "B", status="verschoben"),
              game(3, d("2026-11-20"), "20:30", "A", "C"))
    fxp = A.prepare(fx)
    res = played(fx, "2026-11-10T00:00")
    a_c = next(r for r in fxp.itertuples() if r.spieltag == 3)
    assert A.values_gate(fxp, a_c, at("2026-11-16T10:00"), res) is None


# --- A23–A26: Top Anomalien und Tagesgrenze ---------------------------------------------------------------------

def test_a23_top_block_keeps_kicked_off_games():
    """A23 (geändert in 0.20, Entscheidung Carsten 19.11.2026): angepfiffene Spiele bleiben im Block, kein Nachrücken."""
    fx = plan(game(10, d("2026-11-20"), "20:30", "A", "B"), game(10, d("2026-11-21"), "18:30", "C", "D"),
              game(10, d("2026-11-22"), "15:30", "E", "F"))
    b = A.top_block(fx, at("2026-11-21T16:00"), at("2026-11-21T04:00"))
    assert list(zip(b.games["heim"], b.games["gast"])) == [("A", "B"), ("C", "D"), ("E", "F")]
    assert b.remaining == 2 and b.header == "Spieltag 10 · noch 2 Spiele" and b.takes_part
    assert len(view(fx, "2026-11-21T16:00").sections[0].games) == 3           # Ligaseite: mit Freitagsspiel
    b = A.top_block(fx, at("2026-11-22T18:00"), at("2026-11-22T04:00"))
    assert len(b.games) == 3 and b.remaining == 0 and b.header == "Spieltag 10 · alle Spiele angepfiffen"
    assert A.top_block(fx, at("2026-11-23T00:00"), at("2026-11-23T00:00")) is None   # Ende des Spieltags


def test_a24_catchup_on_same_weekend_belongs_to_block():
    fx = plan(rnd(1, d("2026-08-21"), d("2026-08-23")), game(15, d("2026-12-11"), "20:30", "A", "B"),
              game(15, d("2026-12-13"), "15:30", "C", "D"),
              game(1, d("2026-12-13"), "18:30", "E", "F", hint="Nachholspiel"))
    b = A.top_block(fx, at("2026-12-10T10:00"), at("2026-12-10T04:00"))
    assert len(b.games) == 3 and b.label == "Spieltag 15" and b.header == "Spieltag 15 · noch 3 Spiele"
    assert keys(view(fx, "2026-12-10T10:00")) == [(15, ""), (1, "Nachholspiel")]   # Ligaseite: zwei Abschnitte


def test_a24_early_games_form_own_block_until_their_day_ends():
    fx = real_plan("laliga", d("2026-12-01"))
    b = A.top_block(fx, at("2026-12-01T10:00"), at("2026-12-01T04:00"))
    assert b.header == "Spieltag 23 · vorgezogen · noch 2 Spiele" and len(b.games) == 2
    b = A.top_block(fx, at("2026-12-02T22:00"), at("2026-12-02T04:00"))
    assert b.header == "Spieltag 23 · vorgezogen · alle Spiele angepfiffen"
    b = A.top_block(fx, at("2026-12-03T08:00"), at("2026-12-03T04:00"))
    assert b.label == "Spieltag 15" and len(b.games) == 10


@pytest.mark.parametrize("days, takes_part", [(18, False), (15, False), (14, True)])
def test_a25_top_block_within_fourteen_days(days, takes_part):
    b = A.top_block(BREAK, datetime(2026, 9, 25) - timedelta(days=days), datetime(2026, 9, 25) - timedelta(days=days))
    assert b.takes_part is takes_part
    assert b.header == ("Spieltag 5 · noch 2 Spiele" if takes_part else "Spielpause bis 24.09.")


def test_a25_top_header_winter_break_real():
    fx = real_plan("bundesliga", d("2026-12-23"))
    assert A.top_block(fx, at("2026-12-23T10:00"), at("2026-12-23T04:00")).header == "Winterpause bis 07.01."
    assert A.top_block(fx, at("2026-12-23T10:00"), at("2026-12-18T04:00")).header == "nächster Spieltag am Fr 08.01."


def test_a26_day_boundary_sunday_evening():
    fx = plan(game(1, d("2026-11-20"), "20:30", "A", "B"), game(1, d("2026-11-22"), "21:00", "C", "D"),
              rnd(2, d("2026-11-27"), d("2026-11-29")))
    assert view(fx, "2026-11-22T23:59").sections[0].spieltag == 1
    assert keys(view(fx, "2026-11-23T00:00")) == [(2, "")]


# --- A27: echte Saisonlisten 2026/27 aller vier Ligen -------------------------------------------------------------

EXPECTED_2026 = {
    ("bundesliga", "2026-11-16"): (None, [10]), ("bundesliga", "2026-12-21"): (A.WINTER, []),
    ("bundesliga", "2026-12-25"): (A.WINTER, [15]), ("bundesliga", "2027-01-09"): (None, [15, 16, 17]),
    ("premier_league", "2026-12-01"): (None, [13, 14]), ("premier_league", "2026-12-24"): (None, [17, 18]),
    ("premier_league", "2027-01-02"): (None, [19, 20]),
    ("serie_a", "2026-12-21"): (None, [17]), ("serie_a", "2026-12-28"): (None, [17]),
    ("laliga", "2026-12-01"): (None, [23, 15]), ("laliga", "2026-12-25"): (None, [18]),
}


@pytest.mark.parametrize("league, day", list(EXPECTED_2026))
def test_a27_real_season_lists(league, day):
    notice, sections = EXPECTED_2026[(league, day)]
    v = view(real_plan(league, d(day)), f"{day}T10:00")
    assert (v.notice.kind if v.notice else None) == notice
    assert [s.spieltag for s in v.sections] == sections


def test_a27_premier_league_and_serie_a_without_pause_notice():
    for league in ("premier_league", "serie_a", "laliga"):
        for offset in range(0, 40, 3):
            day = d("2026-12-10") + timedelta(days=offset)
            v = view(real_plan(league, day), f"{day}T10:00")
            assert v.notice is None and v.sections, (league, day)


def test_results_index_from_prepared_database():
    prepared = pd.DataFrame({"season": [S, S], "home": ["A", "C"], "away": ["B", "D"], "hg": [2.0, 0.0],
                             "ag": [1.0, 0.0]})
    assert A.results_index(prepared) == {(S, "A", "B"): (2, 1), (S, "C", "D"): (0, 0)}
    assert A.results_index(None) == {}


# --- Vorschau im Reiter Datenimport/API (Spezifikation, Abschnitt 5) --------------------------------------------

def test_preview_rows_for_import_tab():
    pv = A.preview(real_plan("laliga", d("2026-12-01")), at("2026-12-01T10:00"))
    assert pv == A.Preview("Spieltag 23 (vorgezogen) · Mi 02.12.; Spieltag 15 · So 06.12.", "2 + 10",
                           "Spieltag 23 · vorgezogen · noch 2 Spiele", "Mi 02.12., Tagesende bzw. So 06.12., Tagesende")
    pv = A.preview(real_plan("bundesliga", d("2026-12-23")), at("2026-12-23T10:00"))
    assert pv == A.Preview("Winterpause – nächster Spieltag am Fr 08.01.2027 (Spieltag 15)", "–",
                           "Winterpause bis 07.01.", "–")
    fx = plan(rnd(1, d("2026-11-20"), d("2026-11-22")), game(1, d("2026-11-21"), "15:30", "E", "F", status="verschoben"))
    assert A.preview(fx, at("2026-11-16T10:00")).shown == "Spieltag 1 · Fr 20.11. – So 22.11. (1 Spiel verschoben)"


# --- A29–A35: Statusmodell seit 0.20 (Entscheidungen Carsten 19.11.2026) -----------------------------------------

def test_a29_played_two_hours_after_kickoff():
    """Bis Anpfiff + 2 Stunden normal (auch während des Spiels nichts), danach „Gespielt“, mit Ergebnis der Endstand."""
    fxp = A.prepare(plan(game(1, d("2026-11-21"), "15:30")))
    g = next(fxp.itertuples())
    assert g.gespielt_ab == at("2026-11-21T17:30") == A.played_from(g)
    for now in ("2026-11-21T15:29", "2026-11-21T15:30", "2026-11-21T17:29"):
        assert A.date_cell(g, at(now), {}) == A.DateCell("", "Sa 21.11. · 15:30"), now
        assert not A.is_played(g, at(now), {})
    cell = A.date_cell(g, at("2026-11-21T17:30"), {})
    assert (cell.text, cell.strong, cell.grey, cell.played) == ("Sa 21.11. · ", "Gespielt", True, True)
    assert A.is_played(g, at("2026-11-21T17:30"), {})
    assert A.date_cell(g, at("2026-11-22T04:30"), {(S, "A", "B"): (2, 1)}).strong == "2:1"


def test_a30_without_kickoff_time_played_from_midnight():
    fxp = A.prepare(plan(game(1, d("2026-11-21"), "", termin="Zeit offen"),
                         game(1, d("2026-11-21"), "", "C", "D")))
    for g in fxp.itertuples():
        assert g.gespielt_ab == at("2026-11-22T00:00")
        assert not A.date_cell(g, at("2026-11-21T23:59"), {}).played
        assert A.date_cell(g, at("2026-11-22T00:00"), {}).strong == "Gespielt"


def test_a31_inactive_never_played_and_result_counts_at_once():
    fxp = A.prepare(plan(game(1, d("2026-11-21"), "15:30", status="verschoben"), game(1, d("2026-11-21"), "15:30", "C", "D")))
    post, normal = list(fxp.itertuples())
    assert not A.is_played(post, at("2026-11-23T10:00"), {(S, "A", "B"): (1, 0)})
    assert A.is_played(normal, at("2026-11-21T16:00"), {(S, "C", "D"): (1, 0)})     # Ergebnis vor + 2 h (Zeitreise)


def test_a32_values_from_structured_and_never_after_kickoff():
    fx = plan(rnd(1, d("2026-11-06"), d("2026-11-08")), game(2, d("2026-11-13"), "20:30", "A", "C"),
              game(2, d("2026-11-15"), "15:30", "B", "D"), game(3, d("2026-11-17"), "20:30", "B", "A"))
    fxp = A.prepare(fx)
    res = played(fx, "2026-11-12T00:00")
    b_a = next(r for r in fxp.itertuples() if r.spieltag == 3)
    gate = A.values_from(fxp, b_a, at("2026-11-12T10:00"), res)
    assert gate.ab == d("2026-11-16") and gate.ergebnis_vom is None
    assert gate.text == A.values_gate(fxp, b_a, at("2026-11-12T10:00"), res)
    gate = A.values_from(fxp, b_a, at("2026-11-16T10:00"), res)                       # gespielt, nicht übernommen
    assert gate.ab is None and gate.ergebnis_vom == d("2026-11-15")
    assert [team for team, _ in A.missing_previous(fxp, b_a, res)] == ["B", "A"]
    assert A.values_from(fxp, b_a, at("2026-11-17T20:30"), res) is None              # ab dem Anstoss nie (4a)
    assert A.missing_previous(fxp, b_a, played(fx, "2026-11-16T00:00")) == []


def test_a33_awarded_but_played_stays_played(tmp_path):
    """Absicherung gegen nachträgliches „gewertet“ (AWD): Ergebnis vom Platz in der Datenbank → gespielt."""
    from openpyxl import Workbook

    from core.config import League
    from core.fixtures import STATUS_AWARDED, STATUS_PLANNED, load_fixtures
    wb = Workbook()
    ws = wb.active
    ws.title = "Bundesliga"
    ws.append(["Saison", "Spieltag", "Datum von", "Datum bis", "Heimmannschaft", "Gastmannschaft", "Status"])
    ws.append([S, 1, datetime(2026, 8, 21), datetime(2026, 8, 21), "A", "B", STATUS_AWARDED])   # gespielt
    ws.append([S, 1, datetime(2026, 8, 22), datetime(2026, 8, 22), "C", "D", STATUS_AWARDED])   # nie gespielt
    wb.save(tmp_path / "plan.xlsx")
    db = {"Bundesliga": pd.DataFrame({"Season": [S, S], "homeTeam": ["A", "C"], "awayTeam": ["B", "E"]})}
    fx = load_fixtures(tmp_path / "plan.xlsx", [League("Bundesliga", "bundesliga", 18, True)], db)
    df = fx.leagues["Bundesliga"]
    assert list(df["status"]) == [STATUS_PLANNED, STATUS_AWARDED]
    hits = [i for i in fx.issues if i.check == "Gewertet, aber gespielt"]
    assert len(hits) == 1 and hits[0].match == "A – B (Spieltag 1)" and not fx.has_errors
