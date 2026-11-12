"""Version 0.12: Sensitivitätsanalyse (Spezifikation 11.11.2026, Testfälle T1–T13).

Rechenkern app/core/sensitivity.py (Auswertung) und core.simulation.closed_matchdays (Nenner). Der wichtigste Test (T13)
vergleicht alle Tabellenwerte mit der unabhängigen Gegenrechnung tests/gegenrechnung.py, für alle vier Ligen und
mehrere, auch ungleiche Schwellen.
"""

from __future__ import annotations

import math
from decimal import Decimal

import gegenrechnung as G
import pandas as pd
import pytest
from conftest import LEAGUE_TEAMS, REFERENCE_DATABASE_2018

from core.config import League
from core.kpis import STANDARD_THRESHOLDS, Thresholds, prepare_league
from core.sensitivity import (
    NEG, NEGATIVE, NOT_RELEVANT, POS, TOO_FEW, TOTAL, UNCLEAR, WORKS, WORKS_LIGHT, Limits, evaluate, limit,
    matchday_summary, newcombe, recommendation, wilson,
)
from core.simulation import closed_matchdays
from core.top import TOP_KPIS

D = Decimal
DONE = [f"{y}/{y + 1}" for y in range(2019, 2026)]


def lim(lp, ln, sp, sn) -> Limits:
    return Limits(D(str(lp)), D(str(ln)), D(str(sp)), D(str(sn)))


def cases(devs, up=None, down=None, matchdays=None, kpi="kpi02") -> pd.DataFrame:
    """Handgemachte Fälle: Abweichung in Hundertsteln, Ereignis, Spieltag (alle in Liga L, Saison S)."""
    n = len(devs)
    return pd.DataFrame({"league": "L", "season": "S", "gameday": matchdays or [1] * n, "complete": True,
                         "game": range(n), "kpi": kpi, "dev": devs,
                         "up": up if up is not None else [0.0] * n, "down": down if down is not None else [0.0] * n})


def days(*gds) -> pd.DataFrame:
    return pd.DataFrame({"league": "L", "season": "S", "gameday": list(gds)})


# --- T1–T4: Häufigkeit ---------------------------------------------------------------------------------------------

def test_t1_counting_over_the_threshold():
    """Genau auf der Schwelle zählt nicht; leicht enthält stark."""
    r = evaluate(cases([1499, 1500, 1501, 2501, -1001]), days(1), {"kpi02": lim(15, -10, 25, -15)})[0]
    assert (r.light[POS].count, r.strong[POS].count, r.light[NEG].count, r.strong[NEG].count) == (2, 1, 1, 0)
    assert r.light[TOTAL].count == 3 and r.strong[TOTAL].count == 1


def test_t3_totals_and_t4_coverage():
    """4 Spieltage, Anomalien nur an Spieltag 1 (positiv, zweimal) und 3 (negativ): Ø und Abdeckung je Spieltag."""
    c = cases([3000, 2500, -3000, 100], matchdays=[1, 1, 3, 4])
    r = evaluate(c, days(1, 2, 3, 4), {"kpi02": lim(20, -20, 35, -35)})[0]
    assert (r.light[POS].count, r.light[POS].per_matchday, r.light[POS].coverage) == (2, 0.5, 25.0)
    assert (r.light[NEG].count, r.light[NEG].per_matchday, r.light[NEG].coverage) == (1, 0.25, 25.0)
    t = r.light[TOTAL]
    assert t.count == 3 and t.per_matchday == r.light[POS].per_matchday + r.light[NEG].per_matchday
    assert t.coverage == 50.0 >= max(r.light[POS].coverage, r.light[NEG].coverage)


def test_cases_of_open_matchdays_do_not_count():
    """Fälle eines nicht abgeschlossenen Spieltags zählen nicht (Spezifikation R7)."""
    r = evaluate(cases([3000, 3000], matchdays=[1, 2]), days(1), {"kpi02": lim(20, -20, 35, -35)})[0]
    assert r.light[POS].count == 1 and r.light[POS].per_matchday == 1.0


def test_t2_strong_is_subset_of_light(cases_2018, matchdays_2018):
    for limits in (lim(20, -20, 35, -35), lim(15, -10, 25, -15), lim(5, 0, 5, -0.5), lim(0, 0, 0, 0)):
        for r in evaluate(cases_2018, matchdays_2018, {k: limits for k in TOP_KPIS}):
            for d in (POS, NEG, TOTAL):
                assert r.strong[d].count <= r.light[d].count and r.strong[d].coverage <= r.light[d].coverage


# --- T5: Eingaben ----------------------------------------------------------------------------------------------------

def test_t5_limits_and_rounding():
    assert limit(15.5) == D("15.5") and limit(15.55) == D("15.6") and limit(-10) == D("-10.0")
    assert lim(15, -10, 25, -15).errors() == []
    assert lim(15, -10, 15, -10).errors() == []                       # stark = leicht erlaubt
    assert lim(-1, -10, 25, -15).errors() and lim(15, 1, 25, 2).errors()
    assert lim(15, -10, 14, -15).errors() and lim(15, -10, 25, -9).errors()
    assert Limits.from_thresholds(Thresholds(D(20), D(35))) == lim(20, -20, 35, -35)


# --- T6, T7: Spieltage --------------------------------------------------------------------------------------------------

def _prepared(gamedays: list[tuple[int, int]], season="2026/2027") -> pd.DataFrame:
    """Liga mit 4 Teams (2 Spiele je Spieltag) und einer Vorsaison; gamedays = [(Spieltag, Anzahl Spiele)]."""
    rows, pairs = [], [("A", "B"), ("C", "D")]
    for s, gds in (("2025/2026", [(1, 2)]), (season, gamedays)):
        for gd, n in gds:
            for home, away in pairs[:n]:
                rows.append({"id": len(rows) + 1, "Date": pd.Timestamp(int(s[:4]), 9, gd), "matchDate": "01-09-25 15:30",
                             "Season": s, "Gameday": gd, "homeTeam": home, "awayTeam": away, "FT Home Goals": 1,
                             "FT Away Goals :": 0})
    return prepare_league(pd.DataFrame(rows))


def test_t7_closed_matchdays():
    """Spieltag 2 mit offenem Nachholspiel zählt (Spieltag 3 ist vollständig), der halb gespielte Spieltag 4 nicht."""
    md = closed_matchdays(_prepared([(1, 2), (2, 1), (3, 2), (4, 1)]), League("Liga", "x", 4, True))
    assert list(md["gameday"]) == [1, 2, 3] and set(md["season"]) == {"2026/2027"}      # Referenzsaison nie


def test_t6_all_leagues_current_season(matchdays_2018):
    """Laufende Saison: Ligen unterschiedlich weit (Bundesliga 9 … LaLiga 12), zusammen 42 abgeschlossene Spieltage;
    LaLiga Spieltag 8 mit offenem Nachholspiel zählt."""
    cur = matchdays_2018[matchdays_2018["season"] == "2026/2027"]
    assert matchday_summary(cur) == {"Bundesliga": 9, "Premier League": 10, "Serie A": 11, "LaLiga": 12}
    assert len(cur) == 42 and ((cur["league"] == "LaLiga") & (cur["gameday"] == 8)).any()
    done = matchdays_2018[matchdays_2018["season"].isin(DONE)]
    assert matchday_summary(done) == {"Bundesliga": 238, "Premier League": 266, "Serie A": 266, "LaLiga": 266}


# --- T8–T11: Ergebnisqualität ---------------------------------------------------------------------------------------------

def test_t8_quality_by_hand():
    """10 positive Anomalien (7 eingetroffen), alle 100 Spiele: 45 Mal mehr als die Referenz."""
    up = [1.0] * 7 + [0.0] * 3 + [1.0] * 38 + [0.0] * 52
    r = evaluate(cases([3000] * 10 + [0] * 90, up=up), days(1), {"kpi02": lim(20, -20, 35, -35)})[0]
    q = r.quality[POS]
    assert (q.cases, q.hits, q.hit, q.base) == (10, 7, 70.0, 45.0)
    assert math.isclose(q.gain, 25.0) and q.recommendation == TOO_FEW
    assert (r.total_cases, r.total_hits) == (10, 7)


def test_newcombe_published_examples():
    """Newcombe (1998), Methode 10, und Wilson-Intervall: veröffentlichte Beispiele."""
    g, lo, hi = newcombe(56, 70, 48, 80)
    assert (round(g, 2), round(lo, 2), round(hi, 2)) == (20.0, 5.24, 33.39)
    g, lo, hi = newcombe(9, 10, 3, 10)
    assert (round(lo, 2), round(hi, 2)) == (17.05, 80.9)
    lo, hi = wilson(81, 263)
    assert (round(lo, 4), round(hi, 4)) == (0.2553, 0.3662)


def test_t9_base_rate_does_not_depend_on_thresholds():
    up = [1.0, 0.0, 1.0, 1.0, 0.0, 0.0]
    c = cases([3000, 2500, 500, -500, -2500, 100], up=up)
    bases = {evaluate(c, days(1), {"kpi02": limits})[0].quality[POS].base
             for limits in (lim(20, -20, 35, -35), lim(1, -1, 1, -1), lim(40, -5, 50, -60))}
    assert bases == {50.0}


@pytest.mark.parametrize("n, gain, low, high, expected", [
    (49, 30.0, 10.0, 50.0, TOO_FEW),
    (50, 5.0, 0.01, 10.0, WORKS),
    (50, 5.0, 0.0, 10.0, WORKS_LIGHT),                 # unterer Rand nicht über 0
    (50, 3.0, -0.01, -0.01, NEGATIVE),                 # ganze Spanne unter 0 geht vor
    (50, 2.0, -5.0, 9.0, WORKS_LIGHT),
    (50, 2.0, -5.01, 9.0, UNCLEAR),                    # „leicht“ nur mit unterem Rand ≥ −5
    (50, 1.99, -1.0, 4.99, NOT_RELEVANT),
    (50, 1.99, -3.0, 5.01, UNCLEAR),
    (50, 1.994, -1.0, 4.99, NOT_RELEVANT),             # gerundet 1,99
    (50, 1.995, -1.0, 4.99, WORKS_LIGHT),              # gerundet 2,00
])
def test_t10_recommendation(n, gain, low, high, expected):
    assert recommendation(n, gain, low, high) == expected


def test_t11_quality_uses_light_threshold_only():
    up = [1.0] * 5 + [0.0] * 5
    c = cases([3000, 3000, 2600, 2100, 1000, 3000, 2600, 2100, 1000, 500], up=up)
    a = evaluate(c, days(1), {"kpi02": lim(20, -20, 35, -35)})[0].quality[POS]
    b = evaluate(c, days(1), {"kpi02": lim(20, -20, 28, -35)})[0].quality[POS]       # nur stark geändert
    d = evaluate(c, days(1), {"kpi02": lim(25, -20, 35, -35)})[0].quality[POS]       # leicht geändert
    assert a == b and (a.cases, d.cases) == (7, 5)


# --- T12: Ausgangswerte = bisherige Häufigkeit -----------------------------------------------------------------------------

def test_t12_standard_thresholds_match_previous_frequency(cases_2018, matchdays_2018):
    """Alle Ligen, alle abgeschlossenen Saisons, ±20/±35: wie bisher im Simulations-Tab (KPI 02: 1'229 leicht +
    103 stark = 1'332) und wie die Probewerte der Spezifikation (Mehrwert KPI 02 positiv +8,12, „Funktioniert“)."""
    c = cases_2018[cases_2018["season"].isin(DONE)]
    md = matchdays_2018[matchdays_2018["season"].isin(DONE)]
    r = {x.kpi: x for x in evaluate(c, md, {k: Limits.from_thresholds(STANDARD_THRESHOLDS) for k in TOP_KPIS})}
    assert (r["kpi02"].light[TOTAL].count, r["kpi02"].strong[TOTAL].count) == (1332, 103)
    assert (r["kpi03"].light[TOTAL].count, r["kpi03"].strong[TOTAL].count) == (3201, 1167)
    q = r["kpi02"].quality[POS]
    assert (q.cases, q.hits, round(q.gain, 2), q.recommendation) == (684, 374, 8.12, WORKS)
    assert round(r["kpi02"].light[POS].coverage, 2) == 48.94 and len(md) == 1036


# --- T13: unabhängige Gegenrechnung ------------------------------------------------------------------------------------

SEASONS = {"2025/2026", "2026/2027"}


@pytest.fixture(scope="module")
def counter():
    if not REFERENCE_DATABASE_2018.exists():
        pytest.skip("Referenz-Datenbank 451348b6 nicht vorhanden")
    events, closed = [], set()
    for name, teams in LEAGUE_TEAMS.items():
        lg = G.League(G.read_league(REFERENCE_DATABASE_2018, name), 2 * (teams - 1))
        closed |= {(name, md) for md in G.sens_closed_matchdays(lg, teams, SEASONS)}
        events += [(name, (g.season, g.gameday), G.sim_events(lg, g))
                   for (s, _), gs in lg.by_key.items() if s in SEASONS for g in gs]
    return events, closed


@pytest.mark.parametrize("limits", [(20, -20, 35, -35), (15, -10, 25, -15), (12.5, -7.5, 30, -40), (0, 0, 0, 0)])
@pytest.mark.parametrize("league", ["Alle Ligen", "Bundesliga", "LaLiga"])
def test_t13_counter_calculation(cases_2018, matchdays_2018, counter, limits, league):
    events, closed = counter
    c = cases_2018[cases_2018["season"].isin(SEASONS)]
    md = matchdays_2018[matchdays_2018["season"].isin(SEASONS)]
    if league != "Alle Ligen":
        c, md = c[c["league"] == league], md[md["league"] == league]
        events = [e for e in events if e[0] == league]
        closed = {x for x in closed if x[0] == league}
    assert len(md) == len(closed)
    mine = G.sens_summary(events, closed, dict(zip(("lp", "ln", "sp", "sn"), (D(str(v)) for v in limits))))
    for r in evaluate(c, md, {k: lim(*limits) for k in TOP_KPIS}):
        m = mine[r.kpi]
        for stage, attr in (("leicht", "light"), ("stark", "strong")):
            for d, key in ((POS, "pos"), (NEG, "neg"), (TOTAL, "tot")):
                app, ref = getattr(r, attr)[d], m[f"{stage}_{key}"]
                assert app.count == ref[0], (r.kpi, stage, d)
                assert math.isclose(app.per_matchday, ref[1]) and math.isclose(app.coverage, ref[2]), (r.kpi, stage, d)
        for d, key in ((POS, "pos"), (NEG, "neg")):
            q, ref = r.quality[d], m["q_" + key]
            assert (q.cases, q.hits) == ref[:2], (r.kpi, d)
            for got, exp in zip((q.hit, q.base, q.gain, q.low, q.high), ref[2:]):
                assert (got is None and exp is None) or math.isclose(got, exp, abs_tol=1e-9), (r.kpi, d, got, exp)
