"""Tests zu H.1 (Aufräumen und Tempo, Version 0.9.1): gleiche Ergebnisse auf dem schnelleren Rechenweg,
Kommazahlen gelten als fehlend, Anteile kaufmännisch gerundet, KPI-Ergebnisse eines Spieltags aus core."""

from dataclasses import asdict
from datetime import date

import pandas as pd
import pytest
from conftest import KNOWN_DB_SHA_H, REFERENCE_DATABASE_H
from gegenrechnung import _num

from core.config import League
from core.frequency import _share
from core.kpis import Match, _int_or_none, compute_match, league_references, prepare_league, stat_kpi
from core.loader import load_database
from core.results import matchday_kpis


def _mini_league(corners_home=(6,) * 12) -> pd.DataFrame:
    """12 Spiele von A, B, C mit allen Werten, die KPI 01–09 brauchen."""
    rows = []
    for i in range(1, 13):
        home, away = ("A", "B") if i % 2 else ("B", "C")
        rows.append({"id": i, "Date": pd.Timestamp(f"2026-08-{i:02d}"), "matchDate": f"{i:02d}-08-26 15:30",
                     "Season": "2026/2027", "Gameday": i, "homeTeam": home, "awayTeam": away,
                     "FT Home Goals": 2, "FT Away Goals :": 1, "Home Yellow Cards Full Time": 2,
                     "Away Yellow Cards Full Time": 1, "First-Half Home Goals": 1, "First-Half Away Goals": 0,
                     "Second-Half Home Goals": 1, "Second-Half Away Goals": 1,
                     "Home Corners Full Time": corners_home[i - 1], "Away Corners Full Time": 4,
                     "Home Shots on Target Full Time": 5, "Away Shots on Target Full Time": 3})
    return prepare_league(pd.DataFrame(rows))


# --- Kommazahlen gelten als fehlend, nie abgeschnitten (Punkt R5) ---------------------------

@pytest.mark.parametrize("values, expected", [
    ((2, 3), [2, 3]), ((2.0, 0.0), [2, 0]), ((2.5, 3), None), ((float("nan"), 3), None), ((pd.NA,), None),
])
def test_int_or_none(values, expected):
    assert _int_or_none(*values) == expected


def test_decimal_corners_count_as_missing_in_kpi05():
    """Ein Spiel mit 4,5 Ecken fällt weg wie ein leerer Wert (früher wäre 4 daraus geworden)."""
    corners = [6] * 11 + [4.5]                      # Spiel 12 (B – C) hat einen Kommawert
    r = stat_kpi(_mini_league(corners), Match("Liga", "2026/2027", 13, date(2026, 9, 1), "A", "B"), 34, "kpi05")
    assert 12 not in r.auswaerts.ids and r.auswaerts.spiele == 9
    assert r.auswaerts.summe == 9 * 10


@pytest.mark.parametrize("value, expected", [(None, None), ("", None), (" ", None), (4, 4), (4.0, 4), (4.5, None)])
def test_counter_calculation_num(value, expected):
    assert _num(value) == expected


# --- Schnellerer Rechenweg: gleiche Ergebnisse (Punkte L1, L2) -------------------------------

def test_compute_match_with_shared_references_is_identical():
    db = _mini_league()
    m = Match("Liga", "2026/2027", 13, date(2026, 9, 1), "A", "B")
    refs = league_references(db, m, 34)
    assert set(refs) == {"kpi02", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08", "kpi09"}
    assert asdict(compute_match(db, m, 34, references=refs)) == asdict(compute_match(db, m, 34))


@pytest.mark.skipif(not REFERENCE_DATABASE_H.exists(), reason="Referenz-Datenbank H nicht vorhanden")
def test_shared_references_identical_on_real_matchdays():
    """Echte Daten: Referenzen je (Saison, Spieltag, Stichtag) geteilt -> exakt dieselben Ergebnisse."""
    db = load_database(REFERENCE_DATABASE_H)
    assert db.sha256 == KNOWN_DB_SHA_H
    prepared = prepare_league(db.leagues["Bundesliga"])
    games = prepared[(prepared["season"] == "2025/2026") & prepared["gameday"].isin([17, 18])]
    shared = {}
    for g in games.itertuples():
        m = Match("Bundesliga", g.season, int(g.gameday), g.date, g.home, g.away)
        key = (m.season, m.matchday, m.stichtag)
        shared.setdefault(key, league_references(prepared, m, 34))
        assert asdict(compute_match(prepared, m, 34, references=shared[key])) == asdict(compute_match(prepared, m, 34))


# --- Häufigkeit: Anteile kaufmännisch gerundet (Punkt R10) -------------------------------------

@pytest.mark.parametrize("n, rated, expected", [
    (1, 800, "0,13 %"),          # 0,125 -> 0,13 (Gleitkomma hätte 0,12 ergeben)
    (1, 3, "33,33 %"), (2, 3, "66,67 %"), (0, 5, "0,00 %"), (5, 5, "100,00 %"), (0, 0, "–"),
])
def test_share_rounds_half_up(n, rated, expected):
    assert _share(n, rated) == expected


# --- Konfiguration und KPI-Ergebnisse eines Spieltags (Punkte A5, A11) --------------------------

def test_league_matchdays():
    assert League("Bundesliga", "bundesliga", 18, True).matchdays == 34
    assert League("Serie A", "serie-a", 20, True).matchdays == 38


def test_matchday_kpis_in_order_none_for_postponed():
    league = League("Liga", "liga", 18, True)
    games = pd.DataFrame([
        {"heim": "A", "gast": "B", "status": "geplant", "datum_von": date(2026, 9, 1)},
        {"heim": "B", "gast": "C", "status": "verschoben", "datum_von": date(2026, 9, 1)},
        {"heim": "C", "gast": "A", "status": "", "datum_von": date(2026, 9, 2)},
    ])
    db = _mini_league()
    results = matchday_kpis(db, league, "2026/2027", 13, games)
    assert [r is None for r in results] == [False, True, False]
    assert (results[0].match.home, results[2].match.home) == ("A", "C")
    assert asdict(results[0]) == asdict(compute_match(db, Match("Liga", "2026/2027", 13, date(2026, 9, 1), "A", "B"),
                                                      34))
    assert matchday_kpis(None, league, "2026/2027", 13, games) == [None, None, None]   # Liga nicht in der Datenbank
