"""Version 0.13: neue Schwellen, positiv und negativ getrennt, KPI 03 je Liga (Entscheidung Carsten 14.11.2026).

1. Die ausgelieferte schwellen.toml enthält genau die festgelegten Werte (unabhängig mit tomllib gelesen).
2. Einstufung mit getrennten Schwellen, Grenzfälle (genau auf der Schwelle = schwächere Stufe).
3. Dateiformat: leicht/stark (gleich für beide Richtungen) oder vier Felder; klare Fehlermeldungen.
4. Dashboard-Werte mit den gültigen Schwellen = unabhängige Gegenrechnung (tests/gegenrechnung.py, grade_split)
   für alle Spiele der letzten fünf Spieltage 2025/26 in allen vier Ligen.
5. Die bestätigten Testfälle (docs/tests) rechnen weiter mit den Standardschwellen ±20/±35 und bleiben gültig.
"""

from __future__ import annotations

import tomllib
from decimal import Decimal

import gegenrechnung as G
import pytest
from conftest import LEAGUE_TEAMS, REFERENCE_DATABASE_2018

from core.config import ConfigError
from core.kpis import KPI_KEYS, LIGHT, NONE, STANDARD_THRESHOLDS, STRONG, Match, Thresholds, classify, \
    compute_match, prepare_league
from core.loader import load_database
from core.thresholds import describe, load_thresholds
from test_thresholds import CONFIG, LEAGUES, write

D = Decimal

# Festlegung Carsten 14.11.2026: (leicht positiv, stark positiv, leicht negativ, stark negativ)
DECIDED = {
    "kpi02": (20, 30, -15, -25), "kpi04": (15, 35, -20, -30), "kpi05": (15, 20, -10, -15),
    "kpi06": (15, 25, -20, -30), "kpi07": (25, 30, -20, -25), "kpi08": (20, 25, -30, -35), "kpi09": (15, 20, -10, -15),
}
DECIDED_KPI03 = {"Bundesliga": (35, 40, -5, -10), "Premier League": (30, 40, -10, -15),
                 "Serie A": (30, 40, -10, -20), "LaLiga": (20, 30, -15, -25)}


def expected(league: str, kpi: str) -> tuple:
    return DECIDED_KPI03[league] if kpi == "kpi03" else DECIDED[kpi]


def as_tuple(t: Thresholds) -> tuple:
    return (t.leicht, t.stark, t.leicht_negativ, t.stark_negativ)


# --- 1. Ausgelieferte Datei ------------------------------------------------------------------------------------------

def test_shipped_file_contains_the_decided_thresholds():
    raw = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    assert raw["standard"] == {"leicht": 20, "stark": 35}
    found = {(e.get("liga"), e["kpi"]): (e["leicht_positiv"], e["stark_positiv"], e["leicht_negativ"],
                                          e["stark_negativ"]) for e in raw["abweichung"]}
    want = {(None, k): v for k, v in DECIDED.items()} | {(lg, "kpi03"): v for lg, v in DECIDED_KPI03.items()}
    assert found == want
    cfg = load_thresholds(CONFIG, LEAGUES)
    for league in LEAGUES:
        for kpi in KPI_KEYS:
            assert as_tuple(cfg.get(league, kpi)) == tuple(D(v) for v in expected(league, kpi)), (league, kpi)
    assert cfg.get("Ligue 1", "kpi03") == STANDARD_THRESHOLDS          # neue Liga ohne eigene KPI-03-Schwelle


def test_describe_lists_four_thresholds_per_scope():
    rows = describe(load_thresholds(CONFIG, LEAGUES))
    assert rows[0] == {"Gilt für": "Standard (alle übrigen)", "Leicht positiv": "+20,00 %", "Stark positiv": "+35,00 %",
                       "Leicht negativ": "−20,00 %", "Stark negativ": "−35,00 %"}
    assert [r["Gilt für"] for r in rows[1:]] == ["KPI 02", "KPI 03 · Bundesliga", "KPI 03 · Premier League",
                                                  "KPI 03 · Serie A", "KPI 03 · LaLiga", "KPI 04", "KPI 05", "KPI 06",
                                                  "KPI 07", "KPI 08", "KPI 09"]
    assert rows[2] == {"Gilt für": "KPI 03 · Bundesliga", "Leicht positiv": "+35,00 %", "Stark positiv": "+40,00 %",
                       "Leicht negativ": "−5,00 %", "Stark negativ": "−10,00 %"}


# --- 2. Einstufung -----------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("dev, level", [
    ("20.00", NONE), ("20.01", LIGHT), ("30.00", LIGHT), ("30.01", STRONG),
    ("-15.00", NONE), ("-15.01", LIGHT), ("-25.00", LIGHT), ("-25.01", STRONG),
    ("0.00", NONE), ("19.99", NONE), ("-14.99", NONE),
])
def test_classify_with_split_thresholds(dev, level):
    t = Thresholds(D(20), D(30), D(-15), D(-25))                        # KPI 02
    assert classify(D(dev), t)[0] == level


def test_symmetric_thresholds_behave_as_before():
    """Ohne negative Angaben gelten −leicht/−stark: dieselbe Einstufung wie bis Version 0.12."""
    assert Thresholds(D(20), D(35)) == Thresholds(D(20), D(35), D(-20), D(-35)) == STANDARD_THRESHOLDS
    for dev in ("-35.01", "-35.00", "-20.01", "-20.00", "0.00", "20.00", "20.01", "35.00", "35.01"):
        size = abs(D(dev))
        old = NONE if size <= 20 else LIGHT if size <= 35 else STRONG
        assert classify(D(dev))[0] == old


# --- 3. Dateiformat ----------------------------------------------------------------------------------------------------

def test_split_entry_is_read(tmp_path):
    cfg = load_thresholds(write(tmp_path, """
[standard]
leicht = 20
stark = 35
[[abweichung]]
liga = "Serie A"
kpi = "kpi03"
leicht_positiv = 30
stark_positiv = 40.5
leicht_negativ = -10
stark_negativ = -20
"""), LEAGUES)
    assert as_tuple(cfg.get("Serie A", "kpi03")) == (D(30), D("40.5"), D(-10), D(-20))
    assert cfg.get("LaLiga", "kpi03") == STANDARD_THRESHOLDS


SPLIT = "leicht_positiv = 20\nstark_positiv = 30\nleicht_negativ = -15\nstark_negativ = -25\n"


@pytest.mark.parametrize("entry, message", [
    ("leicht = 20\nstark = 30\nleicht_negativ = -15\n", "nicht beides"),
    ("leicht_positiv = 20\nstark_positiv = 30\nleicht_negativ = -15\n", "'stark_negativ' fehlt"),
    (SPLIT.replace("stark_positiv = 30", "stark_positiv = 20"), "0 < leicht_positiv < stark_positiv"),
    (SPLIT.replace("leicht_negativ = -15", "leicht_negativ = 15"), "stark_negativ < leicht_negativ < 0"),
    (SPLIT.replace("stark_negativ = -25", "stark_negativ = -10"), "stark_negativ < leicht_negativ < 0"),
])
def test_split_entry_errors(tmp_path, entry, message):
    text = "[standard]\nleicht = 20\nstark = 35\n[[abweichung]]\nkpi = \"kpi02\"\n" + entry
    with pytest.raises(ConfigError, match=message):
        load_thresholds(write(tmp_path, text), LEAGUES)


# --- 4. Dashboard mit den gültigen Schwellen = Gegenrechnung ----------------------------------------------------------

@pytest.mark.langsam
@pytest.mark.parametrize("league", list(LEAGUE_TEAMS))
def test_dashboard_levels_match_counter_calculation(league):
    if not REFERENCE_DATABASE_2018.exists():
        pytest.skip("Referenz-Datenbank 451348b6 nicht vorhanden")
    teams = LEAGUE_TEAMS[league]
    md = 2 * (teams - 1)
    cfg = load_thresholds(CONFIG, LEAGUES)
    prepared = prepare_league(load_database(REFERENCE_DATABASE_2018).leagues[league])
    lg = G.League(G.read_league(REFERENCE_DATABASE_2018, league), md)
    checked, diffs, levels = 0, [], set()
    for gd in range(md - 4, md + 1):
        for g in lg.by_key[("2025/2026", gd)]:
            mine = G.analyse(lg, g.season, gd, g.date, g.home, g.away)
            app = compute_match(prepared, Match(league, g.season, gd, g.date, g.home, g.away), md, cfg.get)
            for kpi in KPI_KEYS:
                lp, sp, ln, sn = (D(v) for v in expected(league, kpi))
                want = G.grade_split(mine[kpi]["abweichung"], lp, sp, ln, sn)
                got = getattr(app, kpi)
                checked += 1
                levels.add(want)
                if (got.abweichung_rund, got.anomalie) != (mine[kpi]["abweichung"], want):
                    diffs.append((gd, g.home, kpi, got.abweichung_rund, got.anomalie, want))
    assert not diffs, diffs[:10]
    assert checked >= 5 * (teams // 2) * 8 and {NONE, LIGHT, STRONG} <= levels
