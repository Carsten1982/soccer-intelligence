"""Sensitivitätsanalyse, Auswertung (Regelwerk 11; seit Version 0.19 eine Schwelle je Richtung und Prognosewert).

T1–T13 wie seit Version 0.12 (Häufigkeit, Spieltage, Ergebnisqualität, Gegenrechnung), angepasst an eine Schwelle je
Richtung; dazu die Testfälle P4–P16 der Spezifikation vom 18.11.2026 (Empfehlung mit Rand > +2, Stabilität,
Prognosewert, Wahl der Schwelle, einzelne Saison).
"""

from __future__ import annotations

import math
from decimal import Decimal

import gegenrechnung as G
import pandas as pd
import pytest
from conftest import LEAGUE_TEAMS, REFERENCE_DATABASE_2018

from core.config import League
from core.kpis import HIGH, LOW, MEDIUM, Signal, Thresholds, prepare_league
from core.sensitivity import (
    MEHR, NEGATIVE, NOT_RELEVANT, ONE_SEASON, RULES, TOO_FEW, UNCLEAR, WENIGER, WORKS, WORKS_LIGHT, Limits, evaluate,
    limit, matchday_summary, newcombe, prognosis, proposal, proposal_toml, recommendation,
)
from core.simulation import closed_matchdays
from core.top import TOP_KPIS

D = Decimal
DONE = [f"{y}/{y + 1}" for y in range(2019, 2026)]


def lim(mehr, weniger) -> Limits:
    return Limits(None if mehr is None else D(str(mehr)), None if weniger is None else D(str(weniger)))


def cases(devs, up=None, down=None, matchdays=None, kpi="kpi02", seasons=None) -> pd.DataFrame:
    """Handgemachte Fälle: Abweichung in Hundertsteln, Ereignis, Spieltag (alle in Liga L, Saison S)."""
    n = len(devs)
    return pd.DataFrame({"league": "L", "season": seasons or ["S"] * n, "gameday": matchdays or [1] * n,
                         "complete": True, "game": range(n), "kpi": kpi, "dev": devs,
                         "up": up if up is not None else [0.0] * n, "down": down if down is not None else [0.0] * n})


def days(*gds, season="S") -> pd.DataFrame:
    return pd.DataFrame({"league": "L", "season": season, "gameday": list(gds)})


# --- T1–T4: Häufigkeit ---------------------------------------------------------------------------------------------

def test_t1_counting_over_the_threshold():
    """Genau auf der Schwelle zählt nicht; je Richtung eine Schwelle (Betrag)."""
    r = evaluate(cases([1499, 1500, 1501, 2501, -1001, -1000]), days(1), {"kpi02": lim(15, 10)})[0]
    assert (r.counts[MEHR].count, r.counts[WENIGER].count) == (2, 1)


def test_t1b_no_threshold_in_one_direction():
    r = evaluate(cases([3000, -3000]), days(1), {"kpi02": lim(None, 10)})[0]
    assert (r.counts[MEHR].count, r.counts[WENIGER].count) == (0, 1)


def test_t3_t4_per_matchday_and_coverage():
    """4 Spieltage, Auffälligkeiten nur an Spieltag 1 (mehr, zweimal) und 3 (weniger)."""
    c = cases([3000, 2500, -3000, 100], matchdays=[1, 1, 3, 4])
    r = evaluate(c, days(1, 2, 3, 4), {"kpi02": lim(20, 20)})[0]
    assert (r.counts[MEHR].count, r.counts[MEHR].per_matchday, r.counts[MEHR].coverage) == (2, 0.5, 25.0)
    assert (r.counts[WENIGER].count, r.counts[WENIGER].per_matchday, r.counts[WENIGER].coverage) == (1, 0.25, 25.0)


def test_cases_of_open_matchdays_do_not_count():
    r = evaluate(cases([3000, 3000], matchdays=[1, 2]), days(1), {"kpi02": lim(20, 20)})[0]
    assert r.counts[MEHR].count == 1 and r.counts[MEHR].per_matchday == 1.0


# --- T5: Eingaben ----------------------------------------------------------------------------------------------------

def test_t5_limits_and_rounding():
    assert limit(15.5) == D("15.5") and limit(15.55) == D("15.6") and limit(-10) == D("10.0") and limit(None) is None
    assert lim(15, 10).errors() == [] and lim(0, 10).errors() and lim(None, None).errors() == []
    t = Thresholds(Signal(D(15), HIGH), None)
    assert Limits.from_thresholds(t) == lim(15, None) and Limits.from_thresholds(Thresholds()) == lim(None, None)


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
    md = closed_matchdays(_prepared([(1, 2), (2, 1), (3, 2), (4, 1)]), League("Liga", "x", 4, True))
    assert list(md["gameday"]) == [1, 2, 3] and set(md["season"]) == {"2026/2027"}      # Referenzsaison nie


def test_t6_all_leagues_current_season(matchdays_2018):
    cur = matchdays_2018[matchdays_2018["season"] == "2026/2027"]
    assert matchday_summary(cur) == {"Bundesliga": 9, "Premier League": 10, "Serie A": 11, "LaLiga": 12}
    done = matchdays_2018[matchdays_2018["season"].isin(DONE)]
    assert matchday_summary(done) == {"Bundesliga": 238, "Premier League": 266, "Serie A": 266, "LaLiga": 266}


# --- T8–T11: Ergebnisqualität ---------------------------------------------------------------------------------------------

def test_t8_quality_by_hand():
    """10 Auffälligkeiten „mehr“ (7 eingetroffen), alle 100 Spiele: 45 Mal mehr als die Referenz."""
    up = [1.0] * 7 + [0.0] * 3 + [1.0] * 38 + [0.0] * 52
    q = evaluate(cases([3000] * 10 + [0] * 90, up=up), days(1), {"kpi02": lim(20, 20)})[0].quality[MEHR]
    assert (q.cases, q.hits, q.rate, q.base) == (10, 7, 70.0, 45.0)
    assert math.isclose(q.gain, 25.0) and q.recommendation == TOO_FEW and q.prognosewert is None


def test_newcombe_published_examples():
    g, lo, hi = newcombe(56, 70, 48, 80)
    assert (round(lo, 4), round(hi, 4)) == (0.2553, 0.3662) or (round(lo, 2), round(hi, 2)) == (5.24, 33.39)


def test_t9_base_rate_does_not_depend_on_thresholds():
    up = [1.0, 0.0, 1.0, 1.0, 0.0, 0.0]
    c = cases([3000, 2500, 500, -500, -2500, 100], up=up)
    assert {evaluate(c, days(1), {"kpi02": x})[0].quality[MEHR].base
            for x in (lim(20, 20), lim(1, 1), lim(40, 5))} == {50.0}


# --- P4–P10: Empfehlung (Rand > +2 seit Entscheidung O1) ---------------------------------------------------------------

@pytest.mark.parametrize("n, gain, low, high, expected", [
    (49, 20.0, 10.0, 30.0, TOO_FEW),                 # P4
    (50, -5.0, -9.0, -0.01, NEGATIVE),               # P5
    (50, 5.0, 2.01, 10.0, WORKS),                    # P6
    (50, 5.0, 2.0, 10.0, WORKS_LIGHT),               # P7: Grenze nicht erreicht
    (50, 4.99, 3.5, 10.0, WORKS_LIGHT),              # P8: Mehrwert zu klein
    (50, 1.0, -6.0, 4.99, NOT_RELEVANT),             # P9
    (50, 1.0, -8.0, 10.0, UNCLEAR),                  # P10
    (50, 2.0, -5.01, 9.0, UNCLEAR),                  # „leicht“ nur mit linkem Rand ≥ −5
    (50, 1.995, -1.0, 4.99, WORKS_LIGHT),            # gerundet 2,00
])
def test_p4_to_p10_recommendation(n, gain, low, high, expected):
    assert recommendation(n, gain, low, high) == expected


# --- P11, P12, P16: Stabilität und Prognosewert ------------------------------------------------------------------------

def test_p11_stability_two_thirds_of_seasons():
    assert RULES.stable_needed(7) == 5 and RULES.stable_needed(6) == 4 and RULES.stable_needed(3) == 2
    assert prognosis(WORKS, 65.0, 12.0, 5, 7) == (HIGH, "")
    assert prognosis(WORKS, 65.0, 12.0, 4, 7) == (None, "nicht stabil (4 von 7 Saisons)")


@pytest.mark.parametrize("rate, gain, expected", [
    (60.0, 8.0, HIGH), (60.0, 7.99, MEDIUM), (59.99, 9.0, MEDIUM), (55.0, 6.0, MEDIUM), (54.99, 6.0, LOW),
    (50.0, 6.0, LOW), (49.99, 6.0, None),
])
def test_p12_prognosis_levels(rate, gain, expected):
    level, reason = prognosis(WORKS, rate, gain, 7, 7)
    assert level == expected and (reason == "" if expected else "unter 50" in reason)


def test_p12b_only_works_gets_a_prognosis():
    assert prognosis(WORKS_LIGHT, 70.0, 20.0, 7, 7) == (None, "Empfehlung: Funktioniert leicht")


def test_p16_single_season_has_no_prognosis():
    assert prognosis(WORKS, 70.0, 20.0, 1, 1) == (None, ONE_SEASON)


def _synthetic(n_flag, hits_flag, n_rest, hits_rest, dev, seasons=("A", "B", "C")):
    """Je Saison gleich verteilt: n_flag Fälle mit Abweichung dev (eingetroffen hits_flag), n_rest ohne (hits_rest)."""
    devs, up, ss = [], [], []
    for s in seasons:
        devs += [dev] * n_flag + [0] * n_rest
        up += [1.0] * hits_flag + [0.0] * (n_flag - hits_flag) + [1.0] * hits_rest + [0.0] * (n_rest - hits_rest)
        ss += [s] * (n_flag + n_rest)
    return cases(devs, up=up, seasons=ss)


def test_quality_with_stability_and_prognosis_from_cases():
    c = _synthetic(40, 28, 200, 90, 3000)                    # 70 % gegen 45 % + 70 % … je Saison
    d = pd.concat([days(1, season=s) for s in ("A", "B", "C")])
    q = evaluate(c, d, {"kpi02": lim(20, 20)})[0].quality[MEHR]
    assert (q.cases, q.hits, q.seasons, q.seasons_positive) == (120, 84, 3, 3)
    assert q.recommendation == WORKS and q.prognosewert == HIGH


# --- P13–P15: Wahl der Schwelle (Schwellenvorschlag) -------------------------------------------------------------------

def _proposal_cases(spec):
    """spec: Liste (Abweichung in Hundertsteln, Anzahl je Saison, Treffer je Saison); dazu 400 neutrale Spiele je Saison
    mit 45 % Treffern. Drei Saisons, Liga L, KPI 02, Richtung mehr."""
    devs, up, ss = [], [], []
    for s in ("A", "B", "C"):
        for dev, n, h in spec:
            devs += [dev] * n
            up += [1.0] * h + [0.0] * (n - h)
            ss += [s] * n
        devs += [0] * 400
        up += [1.0] * 180 + [0.0] * 220
        ss += [s] * 400
    return cases(devs, up=up, seasons=ss), pd.concat([days(1, season=s) for s in ("A", "B", "C")])


def test_p13_better_level_beats_more_games():
    # bis 20 %: 200 Spiele je Saison mit 55,5 % (mittel); ab 25 % nur die 50 mit 70 % (hoch) -> 25 % gewinnt
    c, d = _proposal_cases([(2200, 150, 76), (2600, 50, 35)])
    df = proposal(c, d, ["L"], ["kpi02"])
    row = df[df["richtung"] == MEHR].iloc[0]
    assert (row.schwelle, row.prognosewert) == (25, HIGH)


def test_p14_same_level_more_games_wins():
    c, d = _proposal_cases([(3600, 120, 84)])                # alle Auffälligkeiten über 35 %: 10 % … 35 % gleich
    row = proposal(c, d, ["L"], ["kpi02"]).iloc[0]
    assert (row.schwelle, row.prognosewert) == (10, HIGH)


def test_p15_no_candidate_no_row_and_toml():
    c, d = _proposal_cases([(3000, 50, 24)])                 # 48 % gegen 45 %: kein Mehrwert
    df = proposal(c, d, ["L"], ["kpi02"])
    assert df.empty
    c, d = _proposal_cases([(3600, 120, 84)])
    text = proposal_toml(proposal(c, d, ["L"], ["kpi02"]), "A-C", "2026-11-18")
    assert '[[schwelle]]\nliga = "L"\nkpi = "kpi02"\nrichtung = "mehr"\nschwelle = 10\nprognosewert = "hoch"' in text
    assert 'freigabe = ""' in text


# --- T12: Ausgangswerte = bisherige Häufigkeit -----------------------------------------------------------------------------

def test_t12_twenty_percent_matches_previous_frequency(cases_2018, matchdays_2018):
    """Alle Ligen, alle abgeschlossenen Saisons, 20 % je Richtung: wie die bisherige Zählung „leicht“ (KPI 02:
    1'332 Spiele) und die Probewerte (Mehrwert KPI 02 mehr +8,12)."""
    c = cases_2018[cases_2018["season"].isin(DONE)]
    md = matchdays_2018[matchdays_2018["season"].isin(DONE)]
    r = {x.kpi: x for x in evaluate(c, md, {k: lim(20, 20) for k in TOP_KPIS})}
    assert r["kpi02"].counts[MEHR].count + r["kpi02"].counts[WENIGER].count == 1332
    q = r["kpi02"].quality[MEHR]
    assert (q.cases, q.hits, round(q.gain, 2)) == (684, 374, 8.12) and q.seasons == 7
    assert round(r["kpi02"].counts[MEHR].coverage, 2) == 48.94 and len(md) == 1036


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


PER_LEAGUE = {"Bundesliga": (35, 5), "Premier League": (30, 10), "Serie A": (30, 10), "LaLiga": (20, 15)}


@pytest.mark.parametrize("limits", [(20, 20), (15, 10), (12.5, 7.5), (0.1, 0.1), PER_LEAGUE],
                         ids=["zwanzig", "ungleich", "komma", "klein", "je_liga"])
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

    def ref_lim(v):                                   # Gegenrechnung: leicht = stark = Schwelle der Richtung
        m, w = (D(str(x)) for x in v)
        return {"lp": m, "sp": m, "ln": -w, "sn": -w}
    if isinstance(limits, dict):
        mine = G.sens_summary(events, closed, {lg: ref_lim(v) for lg, v in limits.items()})
        app_limits = {lg: lim(*v) for lg, v in limits.items()}
    else:
        mine = G.sens_summary(events, closed, ref_lim(limits))
        app_limits = lim(*limits)
    for r in evaluate(c, md, {k: app_limits for k in TOP_KPIS}):
        m = mine[r.kpi]
        for d, key in ((MEHR, "pos"), (WENIGER, "neg")):
            app, ref = r.counts[d], m[f"leicht_{key}"]
            assert app.count == ref[0], (r.kpi, d)
            assert math.isclose(app.per_matchday, ref[1]) and math.isclose(app.coverage, ref[2]), (r.kpi, d)
            q, ref = r.quality[d], m["q_" + key]
            assert (q.cases, q.hits) == ref[:2], (r.kpi, d)
            for got, exp in zip((q.rate, q.base, q.gain, q.low, q.high), ref[2:]):
                assert (got is None and exp is None) or math.isclose(got, exp, abs_tol=1e-9), (r.kpi, d, got, exp)


def test_t15_limits_per_league():
    """Je Liga gilt die eigene Schwelle; Ergebnis = Summe der Ligen einzeln. Liga ohne Schwelle: nicht auffällig."""
    a = cases([3000, 2500, -1200, 100])
    b = cases([3000, 2500, -1200, 100]).assign(league="M")
    both = pd.concat([a, b], ignore_index=True)
    md = pd.concat([days(1), days(1).assign(league="M")], ignore_index=True)
    per = {"L": lim(20, 10), "M": lim(28, 15)}
    r = evaluate(both, md, {"kpi02": per})[0]
    one = evaluate(a, days(1), {"kpi02": per["L"]})[0]
    two = evaluate(b, days(1).assign(league="M"), {"kpi02": per["M"]})[0]
    for d in (MEHR, WENIGER):
        assert r.counts[d].count == one.counts[d].count + two.counts[d].count
    assert (r.counts[MEHR].count, r.counts[WENIGER].count) == (3, 1)
    only_l = evaluate(both, md, {"kpi02": {"L": per["L"]}})[0]
    assert only_l.counts[MEHR].count == one.counts[MEHR].count
