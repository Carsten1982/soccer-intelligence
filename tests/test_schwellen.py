"""Version 0.19: Schwellen je Liga, KPI und Richtung mit Prognosewert (Spezifikation und Freigabe Carsten 18.11.2026).

1. Die ausgelieferte schwellen.toml enthält genau die freigegebenen 23 Schwellen (unabhängig mit tomllib gelesen).
2. Einstufung an den Grenzen (P1–P3): genau auf der Schwelle nicht auffällig, ohne Schwelle nie, vorläufig nie.
3. Dashboard-Werte mit den gültigen Schwellen = unabhängige Gegenrechnung (tests/gegenrechnung.py, grade_signal).
4. Echte Daten (P21, P22): der Schwellenvorschlag der Sensitivitätsanalyse ergibt genau die ausgelieferte Datei.
5. Die bestätigten KPI-Testfälle (docs/tests) prüfen Werte und Texte weiter mit der Schwelle 20 % (test_kpis.LEGACY).
"""

from __future__ import annotations

import tomllib
from decimal import Decimal

import gegenrechnung as G
import pytest
from conftest import LEAGUE_TEAMS, REAL_DATABASE, REFERENCE_DATABASE_2018
from test_thresholds import CONFIG, LEAGUES

from core.config import League, load_leagues
from core.kpis import HIGH, KPI_KEYS, LOW, MEDIUM, NONE, Match, Signal, Thresholds, classify, compute_match, \
    prepare_league
from core.loader import load_database
from core.thresholds import load_thresholds

D = Decimal

# Freigegeben am 18.11.2026 (Spezifikation, Abschnitt 3.1): (Liga, KPI, Richtung) -> (Schwelle, Prognosewert)
APPROVED = {
    ("Bundesliga", "kpi04", "mehr"): (10, LOW), ("Bundesliga", "kpi06", "weniger"): (10, MEDIUM),
    ("Bundesliga", "kpi08", "weniger"): (35, HIGH), ("Bundesliga", "kpi09", "mehr"): (15, HIGH),
    ("Bundesliga", "kpi09", "weniger"): (10, HIGH),
    ("Premier League", "kpi02", "weniger"): (10, MEDIUM), ("Premier League", "kpi03", "mehr"): (35, HIGH),
    ("Premier League", "kpi04", "mehr"): (10, MEDIUM), ("Premier League", "kpi06", "weniger"): (25, HIGH),
    ("Premier League", "kpi08", "mehr"): (25, HIGH), ("Premier League", "kpi09", "mehr"): (10, MEDIUM),
    ("Serie A", "kpi02", "weniger"): (15, HIGH), ("Serie A", "kpi03", "mehr"): (30, HIGH),
    ("Serie A", "kpi04", "weniger"): (15, HIGH), ("Serie A", "kpi05", "mehr"): (10, MEDIUM),
    ("Serie A", "kpi05", "weniger"): (10, HIGH), ("Serie A", "kpi09", "weniger"): (10, HIGH),
    ("LaLiga", "kpi02", "mehr"): (20, HIGH), ("LaLiga", "kpi03", "mehr"): (25, HIGH),
    ("LaLiga", "kpi04", "mehr"): (25, HIGH), ("LaLiga", "kpi04", "weniger"): (10, MEDIUM),
    ("LaLiga", "kpi09", "mehr"): (10, HIGH), ("LaLiga", "kpi09", "weniger"): (10, HIGH),
}


# --- 1. Ausgelieferte Datei ------------------------------------------------------------------------------------------

def test_shipped_file_contains_the_approved_thresholds():
    raw = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    assert raw["grundlage"]["saisons"] == "2019/2020-2025/2026" and raw["grundlage"]["freigabe"] == "2026-11-18"
    found = {(e["liga"], e["kpi"], e["richtung"]): (e["schwelle"], e["prognosewert"]) for e in raw["schwelle"]}
    assert found == APPROVED and len(found) == 23
    cfg = load_thresholds(CONFIG, LEAGUES)
    assert {(lg, k, d): (int(s.schwelle), s.prognosewert) for lg, k, d, s in cfg.entries()} == APPROVED
    bl = cfg.get("Bundesliga", "kpi09").negativ                 # P21: Herleitung in der Datei
    assert (bl.spiele, bl.trefferquote, bl.vergleichsgruppe, bl.mehrwert, bl.spanne_links, bl.spanne_rechts,
            bl.saisons_positiv) == (227, D("63.44"), D("51.57"), D("11.87"), D("5.06"), D("18.25"), "7/7")
    assert sum(1 for v in APPROVED.values() if v[1] == HIGH) == 16 and sum(1 for v in APPROVED.values()
                                                                             if v[1] == LOW) == 1


# --- 2. Einstufung an den Grenzen -------------------------------------------------------------------------------------

def test_p1_threshold_boundary_and_other_direction():
    t = Thresholds(None, Signal(D(10), HIGH))                 # nur „weniger“ 10 %
    assert classify(D("-10.00"), t) == (NONE, "negativ")
    assert classify(D("-10.01"), t) == (HIGH, "negativ")
    assert classify(D("25.00"), t) == (NONE, "positiv")       # andere Richtung ohne Schwelle
    assert classify(D("0.00"), t) == (NONE, None) and classify(None, t) == (None, None)


def test_p2_no_threshold_never_flagged():
    assert classify(D("80.00"), Thresholds()) == (NONE, "positiv")


def test_p3_provisional_values_never_flagged():
    from types import SimpleNamespace

    from core.top import Candidate, select_top
    r = SimpleNamespace(abweichung_rund=D("-30"), anomalie=HIGH, vorlaeufig=True)
    k = SimpleNamespace(**{key: r for key in ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08", "kpi09")})
    from datetime import date
    assert select_top([Candidate("Liga", 0, "2026/2027", 1, date(2026, 8, 1), 0, "A", "B", "", k)]) == []


# --- 3. Dashboard mit den gültigen Schwellen = Gegenrechnung ----------------------------------------------------------

def _counter(cfg, league: str, kpi: str):
    t = cfg.get(league, kpi)
    pos = (t.positiv.schwelle, t.positiv.prognosewert) if t.positiv else None
    neg = (t.negativ.schwelle, t.negativ.prognosewert) if t.negativ else None
    return pos, neg


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
                want = G.grade_signal(mine[kpi]["abweichung"], *_counter(cfg, league, kpi))
                got = getattr(app, kpi)
                checked += 1
                levels.add(want)
                if (got.abweichung_rund, got.anomalie) != (mine[kpi]["abweichung"], want):
                    diffs.append((gd, g.home, kpi, got.abweichung_rund, got.anomalie, want))
    assert not diffs, diffs[:10]
    assert checked >= 5 * (teams // 2) * 8 and NONE in levels and levels & {HIGH, MEDIUM, LOW}


# --- 4. Echte Daten: Vorschlag = ausgelieferte Datei (P21, P22) --------------------------------------------------------

@pytest.mark.langsam
def test_p21_p22_proposal_reproduces_shipped_file():
    """Mit der echten Datenbank (nur auf dem Server bzw. mit SI_DATA_DIR): Schwellenvorschlag mit den Saisons
    2019/20–2025/26 = ausgelieferte schwellen.toml (Schwelle und Prognosewert aller 23 Kombinationen)."""
    if not REAL_DATABASE.exists():
        pytest.skip("echte Datenbank nicht vorhanden")
    from core.sensitivity import proposal
    from core.simulation import build_cases, closed_matchdays
    db = load_database(REAL_DATABASE)
    leagues: list[League] = [lg for lg in load_leagues() if lg.name in LEAGUES]
    seasons = [f"{y}/{y + 1}" for y in range(2019, 2026)]
    cases, days = [], []
    import pandas as pd
    for lg in leagues:
        p = prepare_league(db.leagues[lg.name])
        cases.append(build_cases(p, lg))
        days.append(closed_matchdays(p, lg))
    c, d = pd.concat(cases), pd.concat(days)
    df = proposal(c[c["season"].isin(seasons)], d[d["season"].isin(seasons)], LEAGUES, list(KPI_KEYS))
    got = {(r.liga, r.kpi, r.richtung): (int(r.schwelle), r.prognosewert) for r in df.itertuples()}
    assert got == APPROVED
    bl = df[(df.liga == "Bundesliga") & (df.kpi == "kpi09") & (df.richtung == "weniger")].iloc[0]
    assert (bl.spiele, bl.eingetroffen, bl.saisons_positiv, bl.saisons) == (227, 144, 7, 7)
