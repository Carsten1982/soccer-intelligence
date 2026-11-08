"""Etappe F/H: Gegenrechnung der KPIs mit einer zweiten, unabhängigen Umsetzung (tests/gegenrechnung.py).

1. Die Gegenrechnung trifft die von Carsten bestätigten Testfälle (docs/tests, Referenz-Datenbanken):
   KPI 01–04 und seit Etappe H auch KPI 05–09. Damit ist sie selbst geprüft.
2. App und Gegenrechnung liefern für die echte Datenbank in ALLEN aktiven Ligen dieselben Werte:
   alle Begegnungen des Spielplans und eine Stichprobe der letzten abgeschlossenen Saison
   (die letzten 5 Spieltage komplett, sonst je Spieltag eine Begegnung).

Ein vollständiger Vergleich aller rund 8'800 Spiele wurde am 07.11.2026 (KPI 01–04) und am 08.11.2026
(KPI 01–09, zwei Nachkommastellen) einmalig durchgeführt (0 Abweichungen, siehe docs/tests/pruefprotokoll_etappe_f.md
und pruefprotokoll_etappe_h.md).
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import gegenrechnung as G
import openpyxl
import pytest
from conftest import REAL_DATABASE, REAL_FIXTURES, REFERENCE_DATABASE, REFERENCE_DATABASE_H
from test_kpis import json_cases

from core.config import active_leagues, load_leagues
from core.kpis import Match, compute_match, prepare_league
from core.loader import load_database


def dec(text: str | None) -> Decimal | None:
    """„+34.08“ / „−8,90“ / „4.35“ aus den Testfällen -> Decimal."""
    if text in (None, "–", "-"):
        return None
    return Decimal(text.replace("−", "-").replace("+", "").replace(",", ".").replace(" %", ""))


# --- 1. Gegenrechnung gegen die bestätigten Testfälle --------------------------------

@pytest.fixture(scope="module")
def reference_leagues():
    if not REFERENCE_DATABASE.exists():
        pytest.skip("Referenz-Datenbank nicht vorhanden")
    return {name: G.League(G.read_league(REFERENCE_DATABASE, name), md)
            for name, md in (("Bundesliga", 34), ("Premier League", 38))}


def _analyse(leagues, case):
    return G.analyse(leagues[case["liga"]], case["saison"], case["spieltag"],
                     dt.date.fromisoformat(case["analysedatum"]), case["heim"]["team"], case["auswaerts"]["team"])


@pytest.mark.parametrize("case", json_cases("test_kpi01_formkurve.md"), ids=lambda c: c["testfall"])
def test_counter_kpi01(reference_leagues, case):
    r = _analyse(reference_leagues, case)
    assert r["form_heim"] == case["heim"]["form"] and r["form_gast"] == case["auswaerts"]["form"]


@pytest.mark.parametrize("kpi,file,main,team_key,ref_key", [
    ("kpi02", "test_kpi02_erwartete_tore.md", "torindikator", "tore", "tore"),
    ("kpi03", "test_kpi03_over25.md", "gemeinsam", "tore", None),
    ("kpi04", "test_kpi04_gelbe_karten.md", "erwartet", "karten", "karten"),
])
def test_counter_kpi02_to_04(reference_leagues, kpi, file, main, team_key, ref_key):
    cases = json_cases(file)
    assert cases
    for case in cases:
        r = _analyse(reference_leagues, case)
        for side, exp in (("heim", case["heim"]), ("gast", case["auswaerts"])):
            assert r[f"{team_key}_{side}"] == (exp["spiele"], exp[team_key]), (case["testfall"], side)
        if ref_key:
            ref = case["ligareferenz"]
            assert r[f"ref_{ref_key}"] == (ref["spiele"], ref[ref_key]), case["testfall"]
        assert r[kpi]["hauptwert"] == dec(case[main]), case["testfall"]
        assert r[kpi]["abweichung"] == dec(case["abweichung"]), case["testfall"]
        assert r[kpi]["anomalie"] == case["anomalie"], case["testfall"]
        assert r[kpi]["vorlaeufig"] == case["vorlaeufig"], case["testfall"]


# --- 1b. Gegenrechnung gegen die bestätigten Testfälle KPI 05–09 --------------------------

@pytest.fixture(scope="module")
def reference_leagues_h():
    if not REFERENCE_DATABASE_H.exists():
        pytest.skip("Referenz-Datenbank (Etappe H) nicht vorhanden")
    return {name: G.League(G.read_league(REFERENCE_DATABASE_H, name), md)
            for name, md in (("Bundesliga", 34), ("Premier League", 38), ("Serie A", 38), ("LaLiga", 38))}


@pytest.mark.parametrize("kpi,file", [
    ("kpi05", "test_kpi05_ecken.md"), ("kpi06", "test_kpi06_tore_hz1.md"), ("kpi07", "test_kpi07_tore_hz2.md"),
    ("kpi08", "test_kpi08_btts.md"), ("kpi09", "test_kpi09_schuesse_aufs_tor.md"),
])
def test_counter_kpi05_to_09(reference_leagues_h, kpi, file):
    cases = json_cases(file)
    assert cases
    for case in cases:
        r = _analyse(reference_leagues_h, case)[kpi]
        for side, exp in (("heim", case["heim"]), ("gast", case["auswaerts"])):
            assert r[f"team_{side}"] == (exp["spiele"], exp["summe"]), (case["testfall"], side)
            assert r[f"wert_{side}"] == dec(exp["teamwert"]), (case["testfall"], side)
        ref = case["ligareferenz"]
        assert r["ref"] == (ref["spiele"], ref["summe"]) and r["liga"] == dec(ref["wert"]), case["testfall"]
        assert r["hauptwert"] == dec(case["hauptwert"]), case["testfall"]
        assert r["abweichung"] == dec(case["abweichung"]), case["testfall"]
        assert r["anomalie"] == case["anomalie"] and r["vorlaeufig"] == case["vorlaeufig"], case["testfall"]


# --- 2. App gegen Gegenrechnung mit der echten Datenbank, alle aktiven Ligen ------------

REAL = REAL_DATABASE.exists() and REAL_FIXTURES.exists()


def _app_values(k) -> dict:
    out = {"form_heim": k.form_home.form, "form_gast": k.form_away.form,
           "tore_heim": (k.kpi02.heim.spiele, k.kpi02.heim.summe),
           "tore_gast": (k.kpi02.auswaerts.spiele, k.kpi02.auswaerts.summe),
           "karten_heim": (k.kpi04.heim.spiele, k.kpi04.heim.summe),
           "karten_gast": (k.kpi04.auswaerts.spiele, k.kpi04.auswaerts.summe),
           "ref_tore": (k.kpi02.referenz.spiele, k.kpi02.referenz.summe),
           "ref_karten": (k.kpi04.referenz.spiele, k.kpi04.referenz.summe)}
    for name in ("kpi02", "kpi03", "kpi04"):
        r = getattr(k, name)
        out[name] = {"hauptwert": r.hauptwert_rund, "abweichung": r.abweichung_rund,
                     "anomalie": r.anomalie, "vorlaeufig": r.vorlaeufig}
    for name in ("kpi05", "kpi06", "kpi07", "kpi08", "kpi09"):
        r = getattr(k, name)
        out[name] = {"hauptwert": r.hauptwert_rund, "abweichung": r.abweichung_rund,
                     "anomalie": r.anomalie, "vorlaeufig": r.vorlaeufig,
                     "team_heim": (r.heim.spiele, r.heim.summe), "team_gast": (r.auswaerts.spiele, r.auswaerts.summe),
                     "ref": (r.referenz.spiele, r.referenz.summe), "wert_heim": r.heim.wert_rund,
                     "wert_gast": r.auswaerts.wert_rund, "liga": r.referenz.wert_rund}
    return out


@pytest.fixture(scope="module")
def real_db():
    if not REAL:
        pytest.skip("echte Datenbank/Spielplan nicht vorhanden")
    db = load_database(REAL_DATABASE)
    assert not db.has_errors
    return db


def _cases(lg: G.League, sheet: str, teams: int) -> list[tuple]:
    """Spielplan komplett + Stichprobe der letzten abgeschlossenen Saison."""
    out = []
    wb = openpyxl.load_workbook(REAL_FIXTURES, read_only=True, data_only=True)
    for r in wb[sheet].iter_rows(min_row=2, values_only=True):
        if r[0]:
            out.append((r[0], int(r[1]), r[2].date() if isinstance(r[2], dt.datetime) else r[2], r[4], r[5]))
    wb.close()
    full = teams * (teams - 1)
    seasons = sorted({s for s, _ in lg.by_key if sum(len(v) for k, v in lg.by_key.items() if k[0] == s) == full})
    if seasons:
        last, md = seasons[-1], 2 * (teams - 1)
        for gd in range(1, md + 1):
            games = lg.by_key.get((last, gd), [])
            for g in (games if gd > md - 5 else games[:1]):
                out.append((g.season, g.gameday, g.date, g.home, g.away))
    return out


@pytest.mark.skipif(not REAL, reason="echte Datenbank/Spielplan nicht vorhanden")
@pytest.mark.parametrize("league", active_leagues(load_leagues()), ids=lambda lg: lg.name)
def test_app_matches_counter_calculation(real_db, league):
    md = 2 * (league.teams - 1)
    prepared = prepare_league(real_db.leagues[league.name])
    lg = G.League(G.read_league(REAL_DATABASE, league.name), md)
    cases = _cases(lg, league.name, league.teams)
    assert len(cases) >= 40, league.name
    diffs = []
    for season, gd, stichtag, home, away in cases:
        mine = G.analyse(lg, season, gd, stichtag, home, away)
        app = _app_values(compute_match(prepared, Match(league.name, season, gd, stichtag, home, away), md))
        diffs += [(season, gd, home, away, key, mine[key], app[key]) for key in mine if mine[key] != app[key]]
    assert not diffs, diffs[:10]
