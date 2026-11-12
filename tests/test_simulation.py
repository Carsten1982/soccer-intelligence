"""Sensitivitätsanalyse, Teil Fälle (core/simulation.py): Ereignis, Fälle je Spiel, Saisonauswahl.

Der wichtigste Test vergleicht die Fälle der App mit der unabhängigen Gegenrechnung (tests/gegenrechnung.py) für alle
Spiele der Bundesliga 2025/26. Die Auswertung (Häufigkeit, Ergebnisqualität) prüft tests/test_sensitivity.py.
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
from core.kpis import Match, classify, compute_match, prepare_league
from core.seasons import analysed_seasons
from core.sensitivity import NEG, POS, Limits, evaluate
from core.simulation import _event, build_cases, default_choice, pct, running_seasons, season_choices
from core.top import TOP_KPIS

LEVEL = {"keine": 0, "leicht": 1, "stark": 2}


# --- Einstufung wie im Dashboard ----------------------------------------------------------------

def test_counting_matches_classify():
    """Bei symmetrischen Schwellen ±20/±35 zählt die Auswertung genau die Spiele, die das Dashboard als leichte bzw.
    starke Anomalie einstuft (classify, Regelwerk 2.2; leicht enthält stark)."""
    rng = np.random.default_rng(1)
    devs = [int(d) for d in rng.integers(-6000, 6000, 3000)] + [2000, -2000, 2001, -2001, 3500, 3501, -3501, 0]
    cases = pd.DataFrame({"league": "L", "season": "S", "gameday": 1, "complete": True, "game": range(len(devs)),
                          "kpi": "kpi02", "dev": devs, "up": 0.0, "down": 0.0})
    r = evaluate(cases, pd.DataFrame({"league": ["L"], "season": ["S"], "gameday": [1]}),
                 {"kpi02": Limits(Decimal(20), Decimal(-20), Decimal(35), Decimal(-35))})[0]
    stage = [LEVEL[classify(Decimal(d) / 100)[0]] for d in devs]
    assert r.light[POS].count == sum(1 for d, s in zip(devs, stage) if s >= 1 and d > 0)
    assert r.light[NEG].count == sum(1 for d, s in zip(devs, stage) if s >= 1 and d < 0)
    assert r.strong[POS].count == sum(1 for d, s in zip(devs, stage) if s == 2 and d > 0)
    assert r.strong[NEG].count == sum(1 for d, s in zip(devs, stage) if s == 2 and d < 0)


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


def test_season_choices():
    """Saisonauswahl Version 0.11 (Briefing „Neue Datenbank“, Abschnitt 4): Reihenfolge, Beschriftung, Inhalt."""
    cases = pd.DataFrame({"season": [f"{y}/{y + 1}" for y in range(2019, 2027)], "complete": [True] * 7 + [False]})
    choices = season_choices(cases)
    assert list(choices) == [
        "Aktuelle Saison (2026/27)", "Alle Saisons (2019/20–2025/26)",
        "Alle Saisons plus aktuelle (2019/20–2026/27)",
        "Letzte 2 Saisons (2024/25–2025/26)", "Letzte 3 Saisons (2023/24–2025/26)", "Letzte 4 Saisons (2022/23–2025/26)",
        "Letzte 5 Saisons (2021/22–2025/26)", "Letzte 6 Saisons (2020/21–2025/26)",
        "Saison 2025/26", "Saison 2024/25", "Saison 2023/24", "Saison 2022/23", "Saison 2021/22", "Saison 2020/21",
        "Saison 2019/20"]
    assert default_choice(choices) == "Alle Saisons (2019/20–2025/26)"
    assert choices["Aktuelle Saison (2026/27)"] == ["2026/2027"]
    assert len(choices["Alle Saisons (2019/20–2025/26)"]) == 7
    assert choices["Alle Saisons plus aktuelle (2019/20–2026/27)"][-1] == "2026/2027"
    assert choices["Letzte 2 Saisons (2024/25–2025/26)"] == ["2024/2025", "2025/2026"]     # ohne laufende Saison
    assert choices["Saison 2019/20"] == ["2019/2020"]
    assert running_seasons(cases) == ["2026/2027"]


def test_formats():
    assert pct(54.555) == "54,56" and pct(8.4, signed=True) == "+8,40" and pct(-6.1, signed=True) == "−6,10"
    assert pct(None) == "–" and pct(0.0, signed=True) == "0,00"
