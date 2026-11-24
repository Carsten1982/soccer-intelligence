"""Version 0.11: Referenzsaison, ausgewertete Saisons, Saisonauswahl und neue Datenbank 2018/19–2026/27.

Briefing „Neue Datenbank 2018/19–2026/27 einführen“ (Freigabe Carsten 10.11.2026), Tests T1–T6:
- T1 Referenzsaison / ausgewertete Saisons, Lücken zwischen Saisons (Warnung in der Datenqualität)
- T2 Saisonauswahl im Simulations-Tab (Sonderfälle; Grundfall in test_simulation.py)
- T4 neue Referenzkopie tests/referenz/Database-Soccer-Intelligence_451348b6.xlsx
- T5 Vollvergleich alte gegen neue Datenbank (Simulation) und unabhängige Gegenrechnung der neu ausgewerteten Saisons
- T6 Ligaseiten und Top Anomalien: dieselben Werte mit alter und neuer Datenbank
T3 (bestehende KPI-Testfälle an 6d68583c und f37e36d3) läuft unverändert in test_kpis.py und test_gegenrechnung.py.
Der einmalige Vollvergleich aller Spiele steht in docs/tests/pruefprotokoll_datenbank_2018-2027.md.
"""

from __future__ import annotations

import math

import gegenrechnung as G
import pandas as pd
import pytest
from conftest import (
    KNOWN_DB_SHA_2018, KNOWN_DB_SHA_H, LEAGUE_TEAMS, REFERENCE_DATABASE_2018, REFERENCE_DATABASE_H, make_match,
    write_workbook,
)
from test_gegenrechnung import _app_values, _flags
from test_kpis import legacy

from core import schema
from core.config import League
from core.frequency import last_complete_season
from core.issues import WARNUNG
from core.kpis import Match, compute_match, prepare_league
from core.loader import load_database
from core.overview import league_summary, seasons_text
from core.seasons import analysed_seasons, reference_season, season_gaps, season_list
from core.simulation import build_cases, default_choice, season_choices
from core.top import Candidate, select_top
from core.validation import check_season_gaps

SEASONS_9 = [f"{y}/{y + 1}" for y in range(2018, 2027)]          # 2018/19 … 2026/27


# --- T1: Referenzsaison und ausgewertete Saisons ------------------------------------------------------------

@pytest.mark.parametrize("seasons, ref, analysed", [
    ([], None, []),
    (["2025/2026"], "2025/2026", []),                                          # nur eine Saison: nichts auswertbar
    (["2025/2026", "2024/2025"], "2024/2025", ["2025/2026"]),
    (["2024/2025", "2026/2027", "2025/2026"], "2024/2025", ["2025/2026", "2026/2027"]),
    (SEASONS_9, "2018/2019", SEASONS_9[1:]),
])
def test_reference_and_analysed_seasons(seasons, ref, analysed):
    assert reference_season(seasons) == ref
    assert analysed_seasons(seasons) == analysed


def test_season_list_ignores_duplicates_and_empty_values():
    s = pd.Series(["2020/2021", None, "2019/2020", "2020/2021", float("nan")])
    assert season_list(s) == ["2019/2020", "2020/2021"]
    assert reference_season(s) == "2019/2020" and analysed_seasons(s) == ["2020/2021"]


@pytest.mark.parametrize("seasons, gaps", [
    (SEASONS_9, []),
    (["2020/2021"], []),
    (["2020/2021", "2022/2023"], [("2021/2022", "2022/2023")]),
    (["2018/2019", "2021/2022", "2022/2023"], [("2019/2020", "2021/2022"), ("2020/2021", "2021/2022")]),
])
def test_season_gaps(seasons, gaps):
    assert season_gaps(seasons) == gaps


def _sheet(seasons: list[str]) -> pd.DataFrame:
    """Ligablatt mit je zwei Spielen (Hin- und Rückspiel) pro Saison."""
    rows = []
    for i, season in enumerate(seasons):
        year = int(season[:4])
        for j, (home, away) in enumerate((("Alpha", "Beta"), ("Beta", "Alpha"))):
            r = make_match(100 * i + j + 1, home, away, f"{year}-{9 + j:02d}-1{j}", gameday=j + 1)
            r["Season"] = season
            rows.append(r)
    return pd.DataFrame(rows, columns=list(schema.EXPECTED_COLUMNS))


def test_gap_warning_in_data_quality(tmp_path):
    """C5: Fehlt eine Saison zwischen zwei vorhandenen, meldet die Datenqualität eine Warnung (kein Fehler)."""
    sheets = {name: _sheet(["2018/2019", "2019/2020"]) for name in LEAGUE_TEAMS}
    sheets["Serie A"] = _sheet(["2020/2021", "2022/2023", "2023/2024"])
    db = load_database(write_workbook(tmp_path / "luecke.xlsx", sheets))
    assert not db.has_errors
    gaps = [i for i in db.issues if i.check == "Saison fehlt"]
    assert [(i.level, i.sheet, i.message) for i in gaps] == [
        (WARNUNG, "Serie A", "Saison 2021/22 fehlt; 2022/23 wird ohne Vorsaison berechnet")]
    assert check_season_gaps("Bundesliga", sheets["Bundesliga"]) == []


def test_league_summary_shows_reference_season():
    s = league_summary(_sheet(["2018/2019", "2019/2020", "2020/2021"]))
    assert s["Referenzsaison"] == "2018/2019" and s["Ausgewertet"] == ["2019/2020", "2020/2021"]
    assert seasons_text(s) == ("Referenzsaison: 2018/19 (nur Vorsaison, nicht ausgewertet) · "
                               "Ausgewertet: 2019/20–2020/21")
    one = league_summary(_sheet(["2025/2026"]))
    assert seasons_text(one) == ("Referenzsaison: 2025/26 (nur Vorsaison, nicht ausgewertet) · "
                                 "Ausgewertet: keine (nur eine Saison in der Datenbank)")
    two = league_summary(_sheet(["2024/2025", "2025/2026"]))
    assert seasons_text(two).endswith("Ausgewertet: 2025/26")


def _prepared(seasons: list[str], teams=("A", "B")) -> pd.DataFrame:
    """Aufbereitete Liga: je Saison 12 Spiele (2 Teams, 12 Spieltage), Saison vollständig ab 2 Spielen."""
    rows = []
    for season in seasons:
        year = int(season[:4])
        for i in range(1, 13):
            home, away = teams if i % 2 else teams[::-1]
            rows.append({"id": len(rows) + 1, "Date": pd.Timestamp(year, 8, 1) + pd.Timedelta(days=7 * i),
                         "matchDate": "01-08-24 15:30", "Season": season, "Gameday": i, "homeTeam": home,
                         "awayTeam": away, "FT Home Goals": i % 4, "FT Away Goals :": 1,
                         "Home Yellow Cards Full Time": 2, "Away Yellow Cards Full Time": 1,
                         "Home Corners Full Time": 5, "Away Corners Full Time": 4})
    return prepare_league(pd.DataFrame(rows))


def test_build_cases_skips_only_reference_season():
    """Die älteste Saison wird nie ausgewertet, alle anderen schon – auch nach einer Lücke (dann mit Warnung C5)."""
    league = League("Liga", "liga", 2, True)
    cases = build_cases(_prepared(["2022/2023", "2023/2024", "2025/2026"]), league)
    assert set(cases["season"]) == {"2023/2024", "2025/2026"}


def test_frequency_never_uses_reference_season():
    """Häufigkeit: letzte abgeschlossene Saison, aber nie die Referenzsaison (Regel 2 des Briefings)."""
    league = League("Liga", "liga", 4, True)                       # 4 Teams: 12 Spiele = vollständig
    assert last_complete_season(_prepared(["2025/2026"]), league) is None
    assert last_complete_season(_prepared(["2024/2025", "2025/2026"]), league) == "2025/2026"


# --- T2: Saisonauswahl, Sonderfälle ------------------------------------------------------------------------

def _cases(complete: dict[str, bool]) -> pd.DataFrame:
    return pd.DataFrame({"season": list(complete), "complete": list(complete.values())})


def test_choices_without_running_season():
    choices = season_choices(_cases({"2023/2024": True, "2024/2025": True, "2025/2026": True}))
    assert list(choices) == ["Alle Saisons (2023/24–2025/26)", "Letzte 2 Saisons (2024/25–2025/26)",
                             "Saison 2025/26", "Saison 2024/25", "Saison 2023/24"]
    assert default_choice(choices) == "Alle Saisons (2023/24–2025/26)"


def test_choices_with_one_complete_season():
    choices = season_choices(_cases({"2025/2026": True, "2026/2027": False}))
    assert list(choices) == ["Aktuelle Saison (2026/27)", "Alle Saisons (2025/26)",
                             "Alle Saisons plus aktuelle (2025/26–2026/27)", "Saison 2025/26"]
    assert default_choice(choices) == "Alle Saisons (2025/26)"


def test_choices_with_running_season_only():
    choices = season_choices(_cases({"2026/2027": False}))
    assert list(choices) == ["Aktuelle Saison (2026/27)"]
    assert default_choice(choices) == "Aktuelle Saison (2026/27)"
    assert default_choice({}) is None


def test_choices_never_contain_reference_season():
    league = League("Liga", "liga", 4, True)                       # 4 Teams: 12 Spiele = vollständig
    cases = build_cases(_prepared(["2023/2024", "2024/2025", "2025/2026"]), league)
    labels = " ".join(season_choices(cases))
    assert "2023/24" not in labels and "Saison 2024/25" in labels


# --- T4: neue Referenz-Datenbank -------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def db_2018():
    if not REFERENCE_DATABASE_2018.exists():
        pytest.skip("Referenz-Datenbank 451348b6 nicht vorhanden")
    db = load_database(REFERENCE_DATABASE_2018)
    assert db.sha256 == KNOWN_DB_SHA_2018
    return db


def test_new_database_loads_without_errors(db_2018):
    """Prüfbericht vom 10.11.2026: 0 Fehler, 24 Warnungen, 64 Hinweise; keine fehlende Saison. Seit 0.19.1 ist
    „Schüsse < aufs Tor + daneben“ nur Hinweis (Carsten 18.11.2026): 23 dieser Warnungen sind jetzt Hinweise. Seit 0.23
    ist „Spieltag unvollständig“ in der neuesten Saison ein Hinweis (Carsten 24.11.2026): die letzte Warnung."""
    assert (db_2018.count("Fehler"), db_2018.count("Warnung"), db_2018.count("Hinweis")) == (0, 0, 88)
    assert sum(1 for i in db_2018.issues if i.check == "Schüsse < aufs Tor + daneben") == 23
    assert not [i for i in db_2018.issues if i.check == "Saison fehlt"]
    for name, df in db_2018.leagues.items():
        s = league_summary(df)
        assert s["Referenzsaison"] == "2018/2019", name
        assert s["Ausgewertet"] == SEASONS_9[1:], name
        assert seasons_text(s) == ("Referenzsaison: 2018/19 (nur Vorsaison, nicht ausgewertet) · "
                                   "Ausgewertet: 2019/20–2026/27")
        teams = LEAGUE_TEAMS[name]
        assert last_complete_season(prepare_league(df), League(name, "x", teams, True)) == "2025/2026"


@pytest.mark.langsam
def test_new_database_simulation_seasons(cases_2018):
    for name in LEAGUE_TEAMS:
        seasons = set(cases_2018.loc[cases_2018["league"] == name, "season"])
        assert seasons == set(SEASONS_9[1:]), name                     # 2018/19 nie ausgewertet
    choices = season_choices(cases_2018)
    assert default_choice(choices) == "Alle Saisons (2019/20–2025/26)"
    assert "Saison 2019/20" in choices and "Aktuelle Saison (2026/27)" in choices
    assert not any("2018/19" in label for label in choices)


# --- T5: Vollvergleich alte gegen neue Datenbank, Gegenrechnung der neu ausgewerteten Saisons -------------------

@pytest.mark.langsam
def test_simulation_cases_unchanged_from_2021_22(cases_h, cases_2018):
    """Für alle Spiele, die schon in der alten Datenbank ausgewertet wurden (2021/22 bis 1. Spieltag 2026/27), sind
    Abweichung und „eingetroffen“ in jeder Liga und jedem KPI identisch. Neu dazu kommen 2019/20 und 2020/21."""
    key = ["league", "game", "kpi"]
    old = cases_h.set_index(key).sort_index()
    new = cases_2018.set_index(key).sort_index()
    common = new.loc[new.index.isin(old.index)]
    assert len(common) == len(old)                                  # jeder alte Fall ist auch neu vorhanden
    for col in ("season", "dev", "up", "down"):
        a, b = old[col], common[col]
        same = (a == b) | (a.isna() & b.isna())
        assert same.all(), (col, old[~same].head())
    # „complete“ unterscheidet sich nur in 2026/27 nicht: dort ist die Saison in beiden Dateien noch nicht fertig
    assert (old["complete"] == common["complete"]).all()
    added = set(new.loc[~new.index.isin(old.index), "season"])
    assert added == {"2019/2020", "2020/2021", "2026/2027"}         # 2026/27: Spiele bis 10.11.2026


def _sample(lg: G.League, seasons=("2019/2020", "2020/2021")) -> list:
    """Stichprobe der neu ausgewerteten Saisons: Spieltage 1–3 vollständig (hängen an der Referenzsaison bzw. an
    2019/20), sonst das erste Spiel jedes Spieltags."""
    out = []
    for (season, gd), games in sorted(lg.by_key.items()):
        if season in seasons:
            out += games if gd <= 3 else games[:1]
    return out


@pytest.fixture(scope="module")
def counter_2018():
    if not REFERENCE_DATABASE_2018.exists():
        pytest.skip("Referenz-Datenbank 451348b6 nicht vorhanden")
    return {name: G.League(G.read_league(REFERENCE_DATABASE_2018, name), 2 * (teams - 1))
            for name, teams in LEAGUE_TEAMS.items()}


@pytest.mark.parametrize("name", list(LEAGUE_TEAMS))
def test_counter_calculation_new_seasons(db_2018, counter_2018, cases_2018, name):
    """App = unabhängige Gegenrechnung für 2019/20 und 2020/21: alle Werte der Ligaseite (KPI 01–09, Teamwerte,
    Ligareferenz) und die Fälle der Simulation (Abweichung, eingetroffen)."""
    lg, teams = counter_2018[name], LEAGUE_TEAMS[name]
    prepared = prepare_league(db_2018.leagues[name])
    app_cases = {(r.game, r.kpi): r for r in cases_2018[cases_2018["league"] == name].itertuples()}
    sample = _sample(lg)
    assert len(sample) > 100
    diffs, checked = [], 0
    for g in sample:
        mine = _flags(G.analyse(lg, g.season, g.gameday, g.date, g.home, g.away))
        app = _app_values(compute_match(prepared, Match(name, g.season, g.gameday, g.date, g.home, g.away),
                                        2 * (teams - 1), legacy))
        diffs += [(g.id, key, mine[key], app[key]) for key in mine if mine[key] != app[key]]
        for kpi, (dev, provisional, more, less) in G.sim_events(lg, g).items():
            r = app_cases.get((g.id, kpi))
            if dev is None or provisional:
                assert r is None, (g.id, kpi)
                continue
            checked += 1
            up = math.nan if more is None else float(more)
            down = math.nan if less is None else float(less)
            if not (r.dev == int(dev * 100) and (r.up == up or math.isnan(r.up) and math.isnan(up))
                    and (r.down == down or math.isnan(r.down) and math.isnan(down))):
                diffs.append((g.id, kpi, dev, r.dev, up, r.up, down, r.down))
    assert checked > 500 and not diffs, diffs[:5]


# --- T6: Ligaseiten und Top Anomalien mit alter und neuer Datenbank ---------------------------------------------

MATCHDAYS = [("2021/2022", 1), ("2021/2022", 2), ("2023/2024", 17), ("2025/2026", 30), ("2026/2027", 1)]


def _pages(path) -> dict:
    """Ligaseite je Liga und Spieltag (Stichtag = erstes Datum des Spieltags, wie „Datum von“) und die Top Anomalien
    über alle vier Ligen, mit der Schwelle 20 % in beiden Richtungen (test_kpis.LEGACY)."""
    db = load_database(path)
    out, candidates = {}, {}
    for order, (name, teams) in enumerate(LEAGUE_TEAMS.items()):
        prepared = prepare_league(db.leagues[name])
        for season, gd in MATCHDAYS:
            games = prepared[(prepared["season"] == season) & (prepared["gameday"] == gd)]
            von = min(games["date"])
            res = [compute_match(prepared, Match(name, season, gd, von, g.home, g.away), 2 * (teams - 1), legacy)
                   for g in games.itertuples()]
            out[(name, season, gd)] = [repr(r) for r in res]
            candidates.setdefault((season, gd), []).extend(
                Candidate(name, order, season, gd, von, i, g.home, g.away, "geplant", r)
                for i, (g, r) in enumerate(zip(games.itertuples(), res)))
    for key, cands in candidates.items():
        out[("top",) + key] = [(e.candidate.league, e.candidate.home, e.kpi_key, e.result.anomalie,
                                e.result.abweichung_rund) for e in select_top(cands)]
    return out


@pytest.mark.langsam
def test_league_pages_and_top_unchanged():
    if not (REFERENCE_DATABASE_H.exists() and REFERENCE_DATABASE_2018.exists()):
        pytest.skip("Referenz-Datenbanken nicht vorhanden")
    old, new = _pages(REFERENCE_DATABASE_H), _pages(REFERENCE_DATABASE_2018)
    assert load_database(REFERENCE_DATABASE_H).sha256 == KNOWN_DB_SHA_H
    assert old.keys() == new.keys()
    assert [k for k in old if old[k] != new[k]] == []
    assert any(old[k] for k in old if k[0] == "top")                 # es gibt überhaupt Top-Einträge
