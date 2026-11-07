"""Tests für Spielplan, aktuellen Spieltag und Konfiguration (Etappe B).

Grundlage: docs/04_Spielplan.md (Abschnitte 2–5) und docs/05_Dashboard.md (Kapitel 4.4).
"""

from datetime import date, datetime

import openpyxl
import pandas as pd
import pytest
from conftest import KNOWN_FIXTURES_SHA, REAL_DATABASE, REAL_FIXTURES

from core.config import ConfigError, League, Team, active_leagues, load_leagues, load_teams
from core.fixtures import load_fixtures
from core.issues import FEHLER, HINWEIS, WARNUNG
from core.loader import load_database
from core.matchday import (
    CURRENT, ENDED, UPCOMING, current_matchday, date_range, matchday_games, matchday_overview, season_short,
)

BL = League("Bundesliga", "bundesliga", 4, True)          # Mini-Liga: 4 Teams -> 2 Spiele je Spieltag
PL = League("Premier League", "premier-league", 4, True)
LEAGUES = [BL, PL]
HEADER = ["Saison", "Spieltag", "Datum von", "Datum bis", "Heimmannschaft", "Gastmannschaft"]
D = datetime


def write_plan(path, sheets: dict[str, list[list]], header=HEADER):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for name, rows in sheets.items():
        ws = wb.create_sheet(name)
        if rows is not None:
            ws.append(header)
            for r in rows:
                ws.append(r)
    wb.save(path)
    return path


def plan_rows():
    """Zwei vollständige Spieltage je Liga."""
    return [
        ["2026/2027", 1, D(2026, 8, 28), D(2026, 8, 30), "A", "B"],
        ["2026/2027", 1, D(2026, 8, 28), D(2026, 8, 30), "C", "D"],
        ["2026/2027", 2, D(2026, 9, 4), D(2026, 9, 6), "B", "C"],
        ["2026/2027", 2, D(2026, 9, 4), D(2026, 9, 6), "D", "A"],
    ]


def db_frame(teams=("A", "B", "C", "D"), season="2025/2026"):
    rows = []
    for i, h in enumerate(teams):
        for a in teams:
            if h != a:
                rows.append({"Season": season, "homeTeam": h, "awayTeam": a})
    return pd.DataFrame(rows)


def load(path, db=None, teams=None, leagues=LEAGUES):
    db = db if db is not None else {"Bundesliga": db_frame(), "Premier League": db_frame()}
    return load_fixtures(path, leagues, db, teams or [])


def checks(fx, level):
    return [i.check for i in fx.issues if i.level == level]


# --- Gültiger Spielplan --------------------------------------------------------

def test_valid_plan(tmp_path):
    fx = load(write_plan(tmp_path / "s.xlsx", {"Bundesliga": plan_rows(), "Premier League": plan_rows()}))
    assert not fx.has_errors, fx.issues
    assert checks(fx, WARNUNG) == []
    df = fx.leagues["Bundesliga"]
    assert len(df) == 4
    assert set(df["status"]) == {"geplant"}            # Status fehlt -> geplant
    assert df.iloc[0]["datum_von"] == date(2026, 8, 28)
    assert df.iloc[0]["excel_row"] == 2


def test_empty_rows_and_extra_columns_are_ignored(tmp_path):
    rows = [r + ["Notiz"] for r in plan_rows()] + [[None] * 7] * 5
    path = write_plan(tmp_path / "s.xlsx", {"Bundesliga": rows, "Premier League": plan_rows()},
                      header=HEADER + ["Bemerkung"])
    fx = load(path)
    assert not fx.has_errors and checks(fx, WARNUNG) == []
    assert len(fx.leagues["Bundesliga"]) == 4


# --- Fehler: Spielplan wird nicht verwendet --------------------------------------

def test_missing_file(tmp_path):
    fx = load(tmp_path / "fehlt.xlsx")
    assert "Datei fehlt" in checks(fx, FEHLER)


def test_unreadable_file(tmp_path):
    path = tmp_path / "s.xlsx"
    path.write_bytes(b"PK\x03\x04 halb hochgeladen")
    assert "Datei nicht lesbar" in checks(load(path), FEHLER)


def test_missing_sheet_of_active_league(tmp_path):
    fx = load(write_plan(tmp_path / "s.xlsx", {"Bundesliga": plan_rows()}))
    assert "Blatt fehlt" in checks(fx, FEHLER)


def test_missing_required_column(tmp_path):
    header = HEADER[:3] + ["Datum"] + HEADER[4:]          # „Datum bis“ falsch geschrieben
    fx = load(write_plan(tmp_path / "s.xlsx", {"Bundesliga": plan_rows(), "Premier League": plan_rows()},
                         header=header))
    assert "Pflichtspalte fehlt" in checks(fx, FEHLER)


@pytest.mark.parametrize("col, value, check", [
    (2, "28.08-30.08", "Datum ungültig"),                  # Zeitraum als Text
    (3, None, "Pflichtfeld leer"),
    (1, 1.5, "Spieltag ungültig"),
    (1, 0, "Spieltag ungültig"),
    (1, "1", "Spieltag ungültig"),
    (0, "2026-27", "Saison ungültig"),
    (4, None, "Pflichtfeld leer"),
])
def test_row_errors(tmp_path, col, value, check):
    rows = plan_rows()
    rows[1][col] = value
    fx = load(write_plan(tmp_path / "s.xlsx", {"Bundesliga": rows, "Premier League": plan_rows()}))
    assert check in checks(fx, FEHLER)
    err = [i for i in fx.issues if i.check == check][0]
    assert err.excel_row == 3


def test_date_to_before_date_from(tmp_path):
    rows = plan_rows()
    rows[0][3] = D(2026, 8, 27)
    fx = load(write_plan(tmp_path / "s.xlsx", {"Bundesliga": rows, "Premier League": plan_rows()}))
    assert "Datum bis vor Datum von" in checks(fx, FEHLER)


def test_status_values(tmp_path):
    rows = [r + [s] for r, s in zip(plan_rows(), ["", "Verschoben", "abgesagt", "geplant"])]
    path = write_plan(tmp_path / "s.xlsx", {"Bundesliga": rows, "Premier League": plan_rows()},
                      header=HEADER + ["Status"])
    fx = load(path)
    assert not fx.has_errors
    assert list(fx.leagues["Bundesliga"]["status"]) == ["geplant", "verschoben", "abgesagt", "geplant"]

    rows[0][6] = "ausgefallen"
    path = write_plan(tmp_path / "s2.xlsx", {"Bundesliga": rows, "Premier League": plan_rows()},
                      header=HEADER + ["Status"])
    assert "Status ungültig" in checks(load(path), FEHLER)


# --- Warnungen ----------------------------------------------------------------

def test_warnings(tmp_path):
    rows = plan_rows()
    rows[1][4] = "A"                                       # A zweimal an Spieltag 1
    rows[3][4], rows[3][5] = "D", "D"                       # Heim = Gast
    rows.append(["2026/2027", 3, D(2026, 9, 11), D(2026, 9, 13), "A", "B"])   # Paarung A–B doppelt, 1 statt 2 Spiele
    fx = load(write_plan(tmp_path / "s.xlsx", {"Bundesliga": rows, "Premier League": plan_rows()}))
    w = checks(fx, WARNUNG)
    assert not fx.has_errors
    assert {"Team mehrfach im Spieltag", "Heim = Gast", "Paarung doppelt", "Spieltag unvollständig"} <= set(w)


def test_unknown_team_is_warning_known_promoted_is_hint(tmp_path):
    rows = plan_rows()
    rows[0][4] = "Neuling"
    path = write_plan(tmp_path / "s.xlsx", {"Bundesliga": rows, "Premier League": plan_rows()})
    fx = load(path)
    assert "Teamname unbekannt" in checks(fx, WARNUNG)
    fx = load(path, teams=[Team("neuling", "Neuling")])
    assert "Teamname unbekannt" not in checks(fx, WARNUNG)
    assert "Aufsteiger ohne Daten" in checks(fx, HINWEIS)
    assert fx.team_notes[("Bundesliga", "2026/2027", "Neuling")].startswith("Aufsteiger")


def test_team_outside_season_window_is_hint(tmp_path):
    db = {"Bundesliga": pd.concat([db_frame(("A", "B", "C")), db_frame(("D", "A"), season="2022/2023")]),
          "Premier League": db_frame()}
    fx = load(write_plan(tmp_path / "s.xlsx", {"Bundesliga": plan_rows(), "Premier League": plan_rows()}), db=db)
    assert "Teamname unbekannt" not in checks(fx, WARNUNG)
    assert "Keine Ligadaten im Zeitfenster" in checks(fx, HINWEIS)


def test_already_played_is_hint(tmp_path):
    db = {"Bundesliga": db_frame(season="2026/2027"), "Premier League": db_frame()}
    fx = load(write_plan(tmp_path / "s.xlsx", {"Bundesliga": plan_rows(), "Premier League": plan_rows()}), db=db)
    assert "Begegnung bereits gespielt" in checks(fx, HINWEIS)


def test_inactive_league_sheet(tmp_path):
    leagues = LEAGUES + [League("LaLiga", "laliga", 20, False)]
    path = write_plan(tmp_path / "s.xlsx", {"Bundesliga": plan_rows(), "Premier League": plan_rows(), "LaLiga": None})
    fx = load(path, leagues=leagues)
    assert not fx.has_errors
    assert "Blatt leer" in checks(fx, HINWEIS)
    assert "LaLiga" not in fx.leagues


# --- Aktueller Spieltag (Kapitel 4.4) --------------------------------------------

def plan_df(tmp_path, rows):
    fx = load(write_plan(tmp_path / "s.xlsx", {"Bundesliga": rows, "Premier League": plan_rows()},
                         header=HEADER + ["Status"]))
    assert not fx.has_errors, fx.issues
    return fx.leagues["Bundesliga"]


def with_status(rows, statuses):
    return [r + [s] for r, s in zip(rows, statuses)]


@pytest.mark.parametrize("today, expected", [
    (date(2026, 8, 1), 1),     # vor der Saison: erster nicht beendeter Spieltag
    (date(2026, 8, 30), 1),    # letzter Spieltag-Tag: noch nicht beendet
    (date(2026, 8, 31), 2),    # Tag danach: Wechsel (Regel 1)
    (date(2026, 9, 7), 2),     # alle beendet: letzter Spieltag der Datei (Regel 3)
    (date(2026, 12, 24), 2),
])
def test_current_matchday(tmp_path, today, expected):
    df = plan_df(tmp_path, with_status(plan_rows(), [""] * 4))
    md = current_matchday(df, today)
    assert (md.saison, md.spieltag) == ("2026/2027", expected)


def test_overview_status_labels(tmp_path):
    df = plan_df(tmp_path, with_status(plan_rows(), [""] * 4))
    ov = matchday_overview(df, date(2026, 9, 1))
    assert [(m.spieltag, m.status) for m in ov] == [(1, ENDED), (2, CURRENT)]
    ov = matchday_overview(df, date(2026, 8, 1))
    assert [(m.spieltag, m.status) for m in ov] == [(1, CURRENT), (2, UPCOMING)]
    assert (ov[0].erstes_datum, ov[0].letztes_datum, ov[0].anzahl) == (date(2026, 8, 28), date(2026, 8, 30), 2)


def test_postponed_game_does_not_keep_matchday_open(tmp_path):
    rows = plan_rows()
    rows[1][3] = D(2026, 10, 30)                             # verschobenes Spiel mit spätem Datum
    df = plan_df(tmp_path, with_status(rows, ["", "verschoben", "", ""]))
    assert current_matchday(df, date(2026, 8, 31)).spieltag == 2      # Regel 4
    df = plan_df(tmp_path, with_status(rows, ["", "", "", ""]))
    assert current_matchday(df, date(2026, 8, 31)).spieltag == 1      # ohne Status zählt das Spiel


def test_unknown_exact_date_uses_period(tmp_path):
    rows = plan_rows()
    rows[0][2] = rows[0][3] = D(2026, 8, 28)                 # genauer Termin bekannt
    df = plan_df(tmp_path, with_status(rows, [""] * 4))
    assert current_matchday(df, date(2026, 8, 30)).spieltag == 1      # anderes Spiel läuft bis 30.08.


def test_matchday_games_sorted_by_date_then_file_order(tmp_path):
    rows = [
        ["2026/2027", 1, D(2026, 8, 29), D(2026, 8, 29), "A", "B"],
        ["2026/2027", 1, D(2026, 8, 28), D(2026, 8, 28), "C", "D"],
        ["2026/2027", 1, D(2026, 8, 29), D(2026, 8, 29), "E", "F"],
    ]
    df = plan_df(tmp_path, with_status(rows, [""] * 3))
    games = matchday_games(df, "2026/2027", 1)
    assert list(games["heim"]) == ["C", "A", "E"]


def test_seasons_are_ordered(tmp_path):
    rows = [
        ["2027/2028", 1, D(2027, 8, 20), D(2027, 8, 22), "A", "B"],
        ["2026/2027", 34, D(2027, 5, 15), D(2027, 5, 15), "A", "B"],
    ]
    df = plan_df(tmp_path, with_status(rows, [""] * 2))
    assert current_matchday(df, date(2027, 6, 1)).saison == "2027/2028"
    assert current_matchday(df, date(2027, 5, 1)).spieltag == 34


def test_labels():
    assert season_short("2026/2027") == "2026/27"
    assert date_range(date(2026, 8, 28), date(2026, 8, 30)) == "28.08. – 30.08.2026"
    assert date_range(date(2026, 8, 28), date(2026, 8, 28)) == "28.08.2026"
    assert date_range(date(2026, 12, 30), date(2027, 1, 2)) == "30.12.2026 – 02.01.2027"


# --- Konfiguration ---------------------------------------------------------------

def test_real_config():
    leagues = load_leagues()
    assert [lg.name for lg in active_leagues(leagues)] == ["Bundesliga", "Premier League", "Serie A", "LaLiga"]
    assert [lg.url for lg in active_leagues(leagues)] == ["bundesliga", "premier-league", "serie-a", "laliga"]
    assert {lg.name: lg.games_per_matchday for lg in leagues} == {
        "Bundesliga": 9, "Premier League": 10, "Serie A": 10, "LaLiga": 10}
    assert {t.team_name for t in load_teams()} >= {"Elversberg", "Paderborn"}


@pytest.mark.parametrize("content", [
    '[[liga]]\nname = "X"\nurl = "x"\nteams = 17\naktiv = true\n',            # ungerade
    '[[liga]]\nname = "X"\nurl = "X Y"\nteams = 18\naktiv = true\n',          # ungültige url
    '[[liga]]\nname = "X"\nurl = "x"\nteams = 18\naktiv = false\n',           # keine aktive Liga
    '[[liga]]\nname = "X"\nteams = 18\n',                                      # url fehlt
    '[[liga]\nname = "X"',                                                     # kaputtes TOML
])
def test_invalid_league_config(tmp_path, content):
    path = tmp_path / "ligen.toml"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ConfigError):
        load_leagues(path)


def test_missing_teams_file_is_empty(tmp_path):
    assert load_teams(tmp_path / "gibt-es-nicht.toml") == []


# --- Echte Dateien ------------------------------------------------------------

@pytest.mark.skipif(not (REAL_FIXTURES.exists() and REAL_DATABASE.exists()), reason="echte Dateien nicht vorhanden")
def test_real_fixtures():
    db = load_database(REAL_DATABASE)
    fx = load_fixtures(REAL_FIXTURES, load_leagues(), db.leagues, load_teams())
    assert not fx.has_errors, [i for i in fx.issues if i.level == FEHLER]
    if fx.sha256 != KNOWN_FIXTURES_SHA:
        pytest.skip("neuerer Spielplan: genaue Erwartungswerte gelten nur für den bekannten Stand")
    assert checks(fx, WARNUNG) == [], [i for i in fx.issues if i.level == WARNUNG]
    assert len(fx.leagues["Bundesliga"]) == 9 and len(fx.leagues["Premier League"]) == 10
    for name in ("Bundesliga", "Premier League"):
        md = current_matchday(fx.leagues[name], date(2026, 10, 31))
        assert (md.saison, md.spieltag) == ("2026/2027", 1)
    notes = {k[2]: v for k, v in fx.team_notes.items()}
    assert set(notes) == {"Elversberg", "Paderborn", "Schalke"}


# --- Spieltag-Auswahl mit Pfeilen -------------------------------------------------

def _overview(tmp_path, today):
    from core.matchday import matchday_overview
    rows = plan_rows() + [
        ["2026/2027", 3, D(2026, 9, 11), D(2026, 9, 13), "A", "C"],
        ["2026/2027", 3, D(2026, 9, 11), D(2026, 9, 13), "B", "D"],
    ]
    return matchday_overview(plan_df(tmp_path, with_status(rows, [""] * 6)), today)


def test_selection_default_and_no_future(tmp_path):
    from core.matchday import select_matchday
    ov = _overview(tmp_path, date(2026, 9, 1))          # aktuell: Spieltag 2, Spieltag 3 liegt in der Zukunft
    sel = select_matchday(ov, {})
    assert sel.selected.spieltag == 2 and sel.is_current
    assert [m.spieltag for m in sel.choices] == [1, 2]   # nicht in die Zukunft
    assert sel.next is None and sel.previous.spieltag == 1
    future = select_matchday(ov, {"spieltag": "3"})
    assert future.selected.spieltag == 2 and future.requested_invalid


def test_selection_from_address(tmp_path):
    from core.matchday import params_for, select_matchday
    ov = _overview(tmp_path, date(2026, 9, 1))
    sel = select_matchday(ov, {"spieltag": "1"})
    assert sel.selected.spieltag == 1 and not sel.is_current and sel.next.spieltag == 2
    assert params_for(sel.selected, sel.current) == {"spieltag": "1"}
    assert params_for(sel.current, sel.current) == {}
    for bad in ({"spieltag": "x"}, {"spieltag": "0"}, {"spieltag": "1", "saison": "1999-00"}):
        s = select_matchday(ov, bad)
        assert s.is_current and s.requested_invalid


def test_selection_across_seasons(tmp_path):
    from core.matchday import matchday_overview, params_for, select_matchday
    rows = [
        ["2025/2026", 34, D(2026, 5, 16), D(2026, 5, 16), "A", "B"],
        ["2026/2027", 1, D(2026, 8, 28), D(2026, 8, 30), "A", "C"],
    ]
    ov = matchday_overview(plan_df(tmp_path, with_status(rows, ["", ""])), date(2026, 8, 1))
    sel = select_matchday(ov, {})
    assert (sel.selected.saison, sel.selected.spieltag) == ("2026/2027", 1)
    prev = sel.previous
    assert params_for(prev, sel.current) == {"spieltag": "34", "saison": "2025-26"}
    again = select_matchday(ov, {"spieltag": "34", "saison": "2025-26"})
    assert again.selected == prev
