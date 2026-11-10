"""Simulation – Spielwiese (Etappe I.1, KPI-Regelwerk Abschnitt 11): Einstufung, Ergebniskontrolle, Urteil.

Der wichtigste Test vergleicht die Ergebniskontrolle der App mit der unabhängigen Gegenrechnung (tests/gegenrechnung.py)
für alle Spiele der Bundesliga 2025/26.
"""

import math
from datetime import date
from decimal import Decimal
from fractions import Fraction
from types import SimpleNamespace

import gegenrechnung as G
import numpy as np
import pandas as pd
import pytest
from conftest import REFERENCE_DATABASE_H

from core.config import League
from core.kpis import STANDARD_THRESHOLDS, Match, Thresholds, classify, compute_match, prepare_league
from core.seasons import analysed_seasons
from core.simulation import (
    BETTER, NO_DIFF, SAME, TOO_FEW, WORSE, Quality, Setting, _event, build_cases, default_choice, frequency_rows, judge,
    levels, pct, quality_rows, quantize_threshold, running_seasons, season_choices,
)
from core.top import TOP_KPIS

LEVEL = {"keine": 0, "leicht": 1, "stark": 2}


def standard(league, kpi):
    return STANDARD_THRESHOLDS


# --- Einstufung wie im Dashboard ----------------------------------------------------------------

def test_levels_match_classify():
    rng = np.random.default_rng(1)
    devs = np.concatenate([rng.integers(-6000, 6000, 3000), [2000, -2000, 2001, -2001, 3500, 3501, -3501, 0]])
    got = levels(devs.astype(float), 2000.0, 3500.0)
    expected = [LEVEL[classify(Decimal(int(d)) / 100)[0]] for d in devs]
    assert list(got) == expected


# --- Wann ist eine Anomalie eingetroffen? -----------------------------------------------------------

def _r(ref):
    return SimpleNamespace(referenz=None if ref is None else SimpleNamespace(wert=ref))


@pytest.mark.parametrize("key, value, scale, ref, expected", [
    ("kpi02", 4, 1, Fraction(307, 100), (1.0, 0.0)),      # 4 Tore > 3,07
    ("kpi02", 3, 1, Fraction(307, 100), (0.0, 1.0)),      # 3 Tore < 3,07 (ganze Zahlen!)
    ("kpi03", 3, 1, None, (1.0, 0.0)),                    # feste Marke 2,5
    ("kpi03", 2, 1, None, (0.0, 1.0)),
    ("kpi08", 1, 100, Fraction(55), (1.0, 0.0)),          # beide treffen
    ("kpi08", 0, 100, Fraction(55), (0.0, 1.0)),
    ("kpi05", 10, 1, Fraction(10), (0.0, 0.0)),           # Gleichstand: in keiner Richtung eingetroffen
])
def test_event(key, value, scale, ref, expected):
    assert _event(_r(ref), value, scale, key) == expected


def test_event_missing_value_is_not_counted():
    assert all(math.isnan(x) for x in _event(_r(Fraction(10)), None, 1, "kpi05"))


# --- Fälle aufbauen ------------------------------------------------------------------------------------

def _mini() -> pd.DataFrame:
    """Zwei Saisons mit je 12 Spielen; Team C kommt erst in der zweiten Saison dazu (Aufsteiger)."""
    rows = []
    for season, start, teams in (("2024/2025", "2024-08", ("A", "B")), ("2025/2026", "2025-08", ("A", "C"))):
        for i in range(1, 13):
            home, away = teams if i % 2 else teams[::-1]
            rows.append({"id": len(rows) + 1, "Date": pd.Timestamp(f"{start}-{i:02d}"), "matchDate": "01-08-24 15:30",
                         "Season": season, "Gameday": i, "homeTeam": home, "awayTeam": away,
                         "FT Home Goals": i % 4, "FT Away Goals :": 1, "Home Yellow Cards Full Time": 2,
                         "Away Yellow Cards Full Time": 1, "Home Corners Full Time": 5 if i != 7 else None,
                         "Away Corners Full Time": 4})
    return prepare_league(pd.DataFrame(rows))


def test_build_cases_skips_first_season_and_provisional_values():
    db = _mini()
    assert analysed_seasons(db["season"]) == ["2025/2026"]          # 2024/25 = Referenzsaison (0.11)
    cases = build_cases(db, League("Liga", "liga", 2, True))
    assert set(cases["season"]) == {"2025/2026"}
    # Team C hat vor Spieltag 11 weniger als 10 Spiele -> vorläufig -> nicht in der Simulation
    m = Match("Liga", "2025/2026", 5, date(2025, 8, 5), "C", "A")
    assert compute_match(db, m, 2).kpi02.vorlaeufig
    assert cases.empty or cases["game"].min() > 12
    assert set(cases["kpi"]) <= set(TOP_KPIS)


@pytest.fixture(scope="module")
def bl_cases(cases_h):
    """Bundesliga aus den gemeinsamen Fällen der Referenz-Datenbank H (conftest, einmal je Testlauf berechnet)."""
    return cases_h[cases_h["league"] == "Bundesliga"].reset_index(drop=True)


def test_counter_calculation_bundesliga_2025_26(bl_cases):
    """Unabhängige Gegenrechnung: Abweichung, vorläufig und „eingetroffen“ für jedes Spiel und jeden KPI."""
    lg = G.League(G.read_league(REFERENCE_DATABASE_H, "Bundesliga"), 34)
    app = {(r.game, r.kpi): r for r in bl_cases[bl_cases["season"] == "2025/2026"].itertuples()}
    games = [g for gs in lg.by_key.values() for g in gs if g.season == "2025/2026"]
    assert len(games) == 306
    checked, diffs = 0, []
    for g in games:
        mine = G.analyse(lg, g.season, g.gameday, g.date, g.home, g.away)
        refs = {"kpi02": mine["ref_tore"], "kpi04": mine["ref_karten"]}
        actual = {"kpi02": g.hg + g.ag, "kpi03": g.hg + g.ag,
                  "kpi04": None if g.hy is None or g.ay is None else g.hy + g.ay}
        for key, (value, scale) in G.STAT_VALUES.items():
            refs[key] = mine[key]["ref"]
            actual[key] = value(g)
        for kpi in TOP_KPIS:
            res = mine[kpi]
            if res["vorlaeufig"] or res["abweichung"] is None:
                assert (g.id, kpi) not in app, (g.id, kpi)
                continue
            scale = 100 if kpi == "kpi08" else 1
            if kpi == "kpi03":
                ref = G.OVER
            else:
                n, total = refs[kpi]
                ref = Fraction(total * scale, n)
            a = actual[kpi]
            up = math.nan if a is None else float(a * scale > ref)
            down = math.nan if a is None else float(a * scale < ref)
            r = app[(g.id, kpi)]
            same = (r.dev == int(res["abweichung"] * 100)
                    and (math.isnan(up) and math.isnan(r.up) or up == r.up)
                    and (math.isnan(down) and math.isnan(r.down) or down == r.down))
            checked += 1
            if not same:
                diffs.append((g.id, kpi, res["abweichung"], r.dev, up, r.up, down, r.down))
    assert checked > 1500 and not diffs, diffs[:5]


def test_frequency_with_standard_equals_before(bl_cases):
    setting = Setting(standard, {k: STANDARD_THRESHOLDS for k in TOP_KPIS})
    for row in frequency_rows(bl_cases, setting):
        assert row["unchanged"] and row["total_before"] == row["total_after"]
        assert row["light_before"] + row["strong_before"] == row["total_before"]


def test_lower_threshold_gives_more_anomalies(bl_cases):
    after = {k: STANDARD_THRESHOLDS for k in TOP_KPIS}
    after["kpi05"] = Thresholds(Decimal(12), Decimal(18))
    rows = {r["kpi"]: r for r in frequency_rows(bl_cases, Setting(standard, after))}
    assert rows["kpi05"]["total_after"] > rows["kpi05"]["total_before"] and not rows["kpi05"]["unchanged"]
    assert rows["kpi02"]["total_after"] == rows["kpi02"]["total_before"]
    q = {(r["kpi"], r["direction"]): r for r in quality_rows(bl_cases, Setting(standard, after))}
    assert q[("kpi02", "positiv")]["judge"] == SAME
    assert q[("kpi05", "positiv")]["after"].cases > q[("kpi05", "positiv")]["before"].cases


# --- Ergebnisqualität und Urteil -----------------------------------------------------------------------

def test_quality_on_hand_made_cases():
    """4 positive Anomalien (3 eingetroffen), 4 Spiele ohne Anomalie (1 Mal mehr als die Referenz)."""
    cases = pd.DataFrame({"league": "L", "season": "S", "complete": True, "game": range(8), "kpi": "kpi02",
                          "dev": [2500, 3000, 4000, 2200, 0, 500, -1000, 100],
                          "up": [1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0], "down": [0.0] * 8})
    after = {k: STANDARD_THRESHOLDS for k in TOP_KPIS}
    row = quality_rows(cases, Setting(standard, after))[0]
    assert row["kpi"] == "kpi02" and row["direction"] == "positiv"
    a = row["after"]
    assert (a.cases, a.hit, a.control, a.gain) == (4, 75.0, 25.0, 50.0)
    strong = quality_rows(cases, Setting(standard, after), "stark")[0]["after"]
    assert (strong.cases, strong.hit) == (1, 100.0)                       # nur 40 % ist stark


@pytest.mark.parametrize("before, after, same, expected", [
    (Quality(500, 55.0, 46.0, 4.3), Quality(500, 55.0, 46.0, 4.3), True, SAME),
    (Quality(80, 60.0, 47.6, 10.7), Quality(558, 58.2, 47.8, 4.1), False, TOO_FEW),
    (Quality(515, 54.6, 46.1, 4.3), Quality(255, 56.5, 46.2, 6.1), False, NO_DIFF),      # +1,8 Punkte < ±6,1
    (Quality(515, 54.6, 46.1, 4.3), Quality(400, 66.0, 46.0, 4.6), False, BETTER),       # +11,5 Punkte > ±4,6
    (Quality(515, 54.6, 46.1, 4.3), Quality(900, 46.5, 46.4, 3.3), False, WORSE),
])
def test_judge(before, after, same, expected):
    assert judge(before, after, same) == expected


def test_season_choices():
    """Saisonauswahl Version 0.11 (Briefing „Neue Datenbank“, Abschnitt 4): Reihenfolge, Beschriftung, Inhalt."""
    cases = pd.DataFrame({"season": [f"{y}/{y + 1}" for y in range(2019, 2027)], "complete": [True] * 7 + [False]})
    choices = season_choices(cases)
    assert list(choices) == [
        "Aktuelle Saison (2026/27, vorläufig)", "Alle Saisons (2019/20–2025/26)",
        "Alle Saisons plus aktuelle (2019/20–2026/27, inkl. vorläufig)",
        "Letzte 2 Saisons (2024/25–2025/26)", "Letzte 3 Saisons (2023/24–2025/26)", "Letzte 4 Saisons (2022/23–2025/26)",
        "Letzte 5 Saisons (2021/22–2025/26)", "Letzte 6 Saisons (2020/21–2025/26)",
        "Saison 2025/26", "Saison 2024/25", "Saison 2023/24", "Saison 2022/23", "Saison 2021/22", "Saison 2020/21",
        "Saison 2019/20"]
    assert default_choice(choices) == "Alle Saisons (2019/20–2025/26)"
    assert choices["Aktuelle Saison (2026/27, vorläufig)"] == ["2026/2027"]
    assert len(choices["Alle Saisons (2019/20–2025/26)"]) == 7
    assert choices["Alle Saisons plus aktuelle (2019/20–2026/27, inkl. vorläufig)"][-1] == "2026/2027"
    assert choices["Letzte 2 Saisons (2024/25–2025/26)"] == ["2024/2025", "2025/2026"]     # ohne laufende Saison
    assert choices["Saison 2019/20"] == ["2019/2020"]
    assert running_seasons(cases) == ["2026/2027"]


def test_formats():
    assert pct(54.555) == "54,56" and pct(8.4, signed=True) == "+8,40" and pct(-6.1, signed=True) == "−6,10"
    assert pct(None) == "–" and pct(0.0, signed=True) == "0,00"
    assert quantize_threshold(12.5) == Decimal("12.50") and quantize_threshold(20) == Decimal("20.00")


# --- Unabhängige Gegenrechnung der Tabellenwerte (alle vier Ligen, Saison 2025/26, mehrere Schwellen) -------------

TEAMS = {"Bundesliga": 18, "Premier League": 20, "Serie A": 20, "LaLiga": 20}


@pytest.fixture(scope="module")
def all_cases(cases_h):
    return cases_h


@pytest.fixture(scope="module")
def counter_events():
    out = []
    for name, teams in TEAMS.items():
        lg = G.League(G.read_league(REFERENCE_DATABASE_H, name), 2 * (teams - 1))
        out += [G.sim_events(lg, g) for gs in lg.by_key.values() for g in gs if g.season == "2025/2026"]
    return out


@pytest.mark.parametrize("light, strong", [(20, 35), (12, 18), (15, 25), (30, 45)])
def test_tables_match_counter_calculation(all_cases, counter_events, light, strong):
    """Häufigkeit und Ergebnisqualität der App = unabhängig gezählte Werte der Gegenrechnung."""
    cases = all_cases[all_cases["season"] == "2025/2026"]
    t = Thresholds(Decimal(light), Decimal(strong))
    setting = Setting(standard, {k: t for k in TOP_KPIS})
    mine = G.sim_summary(counter_events, Decimal(light), Decimal(strong))
    for row in frequency_rows(cases, setting):
        c = mine[row["kpi"]]
        assert (row["light_after"], row["strong_after"]) == (c["leicht"], c["stark"]), row["kpi"]
    for row in quality_rows(cases, setting):
        c, a = mine[row["kpi"]], row["after"]
        n, hits = c[row["direction"]]
        n0, hits0 = c["ohne_" + row["direction"]]
        assert a.cases == n, (row["kpi"], row["direction"])
        if n:
            assert pct(a.hit) == pct(hits / n * 100) and pct(a.control) == pct(hits0 / n0 * 100)
            assert pct(a.gain, True) == pct(hits / n * 100 - hits0 / n0 * 100, True)
