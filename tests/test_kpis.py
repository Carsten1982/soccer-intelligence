"""KPI 01–04 gegen die bestätigten Testfälle in docs/tests/*.md (JSON-Blöcke).

Die Testfälle gelten für die Datenbank mit der SHA-256 aus conftest.KNOWN_DB_SHA.
Zusätzlich: Grenzfälle der Rundung und Einstufung, fehlende Kartenwerte (Union Berlin, id 14421),
2-Tage-Regel mit einem ausgedachten Mini-Datensatz.
"""

import json
import re
from datetime import date
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pandas as pd
import pytest
from conftest import KNOWN_DB_SHA, REFERENCE_DATABASE

from core.kpis import (
    LIGHT, NONE, STRONG, Match, classify, compute_match, de, de_signed, fmt, fmt_signed, kpi01_team, kpi02, kpi04,
    prepare_league, reference_keys, reference_label, round1, team_cards, team_goals,
)
from core.loader import load_database

DOCS = Path(__file__).resolve().parents[1] / "docs" / "tests"
MATCHDAYS = {"Bundesliga": 34, "Premier League": 38}
TOL = 1e-9


def json_cases(filename: str) -> list[dict]:
    text = (DOCS / filename).read_text(encoding="utf-8")
    cases = []
    for block in re.findall(r"```json\n(.*?)```", text, re.S):
        cases += json.loads(block)
    return cases


def id_table(filename: str) -> dict[str, list[int]]:
    """Spiel-IDs je Team aus den Kontrolltabellen in test_kpi03_over25.md (Abschnitte 3.3 und 6.3)."""
    text = (DOCS / filename).read_text(encoding="utf-8")
    out: dict[str, list[list[int]]] = {}
    for team, ids in re.findall(r"^\| ([^|]+?) \| \d+ \| [\d–]+ \| [\d,–]+ \| ([\d, ]+) \|$", text, re.M):
        out.setdefault(team, []).append([int(i) for i in ids.split(",")])
    return out


@pytest.fixture(scope="module")
def prepared():
    if not REFERENCE_DATABASE.exists() or not DOCS.exists():
        pytest.skip("Referenz-Datenbank oder docs/tests nicht vorhanden")
    db = load_database(REFERENCE_DATABASE)
    assert db.sha256 == KNOWN_DB_SHA, "Referenz-Datenbank wurde verändert"
    return {name: prepare_league(df) for name, df in db.leagues.items()}


def match_of(case) -> Match:
    return Match(case["liga"], case["saison"], case["spieltag"], date.fromisoformat(case["analysedatum"]),
                 case["heim"]["team"], case["auswaerts"]["team"])


def close(actual, expected):
    if expected is None:
        return actual is None
    return actual is not None and abs(float(actual) - expected) < TOL


def check_team(tv, exp, key):
    assert tv.team == exp["team"]
    assert tv.spiele == exp["spiele"], (tv.team, tv.spiele)
    assert tv.summe == exp[key], (tv.team, tv.summe)
    assert close(tv.wert, exp["teamwert_roh"]), (tv.team, tv.wert)
    assert fmt(tv.wert_rund) == exp["teamwert"]


def check_result(r, case, main_key):
    assert close(r.hauptwert, case[f"{main_key}_roh"]), (case["testfall"], r.hauptwert)
    assert fmt(r.hauptwert_rund) == case[main_key]
    assert close(r.abweichung, case["abweichung_roh"]), (case["testfall"], r.abweichung)
    assert fmt_signed(r.abweichung_rund) == case["abweichung"]
    assert r.anomalie == case["anomalie"]
    assert r.richtung == case["richtung"]
    assert r.vorlaeufig == case["vorlaeufig"]
    assert r.ueberschrift == case["ueberschrift"]
    assert r.text == case["text"]


def check_reference(ref, exp, key):
    assert ref.label == exp["saison_spieltage"]
    assert ref.spiele == exp["spiele"]
    assert ref.summe == exp[key]
    assert close(ref.wert, exp["wert_roh"])
    assert fmt(ref.wert_rund) == exp["wert"]


# --- Testfälle aus docs/tests ------------------------------------------------------

@pytest.mark.parametrize("case", json_cases("test_kpi01_formkurve.md"), ids=lambda c: c["testfall"])
def test_kpi01(prepared, case):
    m = match_of(case)
    for side, team in (("heim", m.home), ("auswaerts", m.away)):
        exp = case[side]
        ft = kpi01_team(prepared[m.league], team, m.season, m.stichtag)
        assert ft.form == exp["form"], (team, ft.form)
        assert ft.anzahl == exp["anzahl"]
        assert ft.vorlaeufig == exp["vorlaeufig"]


@pytest.mark.parametrize("case", json_cases("test_kpi02_erwartete_tore.md"), ids=lambda c: c["testfall"])
def test_kpi02(prepared, case):
    m = match_of(case)
    r = kpi02(prepared[m.league], m, MATCHDAYS[m.league])
    check_team(r.heim, case["heim"], "tore")
    check_team(r.auswaerts, case["auswaerts"], "tore")
    check_reference(r.referenz, case["ligareferenz"], "tore")
    check_result(r, case, "torindikator")


@pytest.mark.parametrize("case", json_cases("test_kpi03_over25.md"), ids=lambda c: c["testfall"])
def test_kpi03(prepared, case):
    m = match_of(case)
    r = compute_match(prepared[m.league], m, MATCHDAYS[m.league]).kpi03
    assert case["referenzwert"] == "2.5"
    check_team(r.heim, case["heim"], "tore")
    check_team(r.auswaerts, case["auswaerts"], "tore")
    for dev, side in zip(r.teamabweichung, ("heim", "auswaerts")):
        assert close(dev, case[side]["teamabweichung_roh"])
        assert fmt_signed(round1(dev)) == case[side]["teamabweichung"]
    check_result(r, case, "gemeinsam")


@pytest.mark.parametrize("case", json_cases("test_kpi04_gelbe_karten.md"), ids=lambda c: c["testfall"])
def test_kpi04(prepared, case):
    m = match_of(case)
    r = kpi04(prepared[m.league], m, MATCHDAYS[m.league])
    check_team(r.heim, case["heim"], "karten")
    check_team(r.auswaerts, case["auswaerts"], "karten")
    check_reference(r.referenz, case["ligareferenz"], "karten")
    check_result(r, case, "erwartet")


def test_selected_game_ids(prepared):
    """Die verwendeten Spiel-IDs je Team entsprechen exakt den Kontrolltabellen (KPI 02/03)."""
    tables = id_table("test_kpi03_over25.md")
    checked = 0
    for case in json_cases("test_kpi03_over25.md"):
        m = match_of(case)
        for team in (m.home, m.away):
            expected = [ids for ids in tables.get(team, [])]
            if not expected:
                continue
            tv = team_goals(prepared[m.league], team, m.season, m.stichtag)
            assert sorted(tv.ids) in [sorted(e) for e in expected], (case["testfall"], team, tv.ids)
            checked += 1
    assert checked >= 12


# --- Kontrollpunkte aus den Testfällen ---------------------------------------------

def test_postponed_game_counts_to_original_matchday(prepared):
    """id 14680 (Spieltag 15, gespielt 12.02.2025) gehört nicht in die Referenz für Spieltag 3 2025/26."""
    m = Match("Premier League", "2025/2026", 3, date(2025, 8, 30), "Manchester Utd", "Burnley")
    r = kpi02(prepared[m.league], m, 38)
    assert r.referenz.spiele == 200


def test_missing_cards_are_not_replaced(prepared):
    """Union Berlin, Spieltag 15 2024/25: id 14421 ohne Karten -> KPI 04 9 Spiele und 179 Referenzspiele,
    KPI 02 dagegen 10 Spiele und 180 Referenzspiele (Tore sind vorhanden)."""
    m = Match("Bundesliga", "2024/2025", 15, date(2024, 12, 21), "Werder Bremen", "Union Berlin")
    pl = prepared[m.league]
    cards = team_cards(pl, "Union Berlin", m.season, m.stichtag)
    goals = team_goals(pl, "Union Berlin", m.season, m.stichtag)
    assert cards.spiele == 9 and 14421 not in cards.ids
    assert goals.spiele == 10 and 14421 in goals.ids
    assert set(cards.ids) < set(goals.ids)                 # kein älteres Spiel nachgezogen
    r4, r2 = kpi04(pl, m, 34), kpi02(pl, m, 34)
    assert r4.referenz.spiele == 179 and r2.referenz.spiele == 180
    assert r4.vorlaeufig and not r2.vorlaeufig


# --- Rundung, Einstufung, Formatierung (ohne Daten) ----------------------------------

@pytest.mark.parametrize("value, expected", [
    (Fraction(87, 20), "4.4"),       # 4,35 -> 4,4 (round() ergäbe 4,3)
    (Fraction(53, 20), "2.7"),       # 2,65 -> 2,7
    (Fraction(-53, 20), "-2.7"),     # kaufmännisch weg von null
    (Fraction(2004, 100), "20.0"),
    (Fraction(6), "6.0"),
])
def test_round1(value, expected):
    assert fmt(round1(value)) == expected


@pytest.mark.parametrize("dev, expected", [
    ("20.0", (NONE, "positiv")), ("-20.0", (NONE, "negativ")), ("20.1", (LIGHT, "positiv")),
    ("35.0", (LIGHT, "positiv")), ("-35.0", (LIGHT, "negativ")), ("35.1", (STRONG, "positiv")),
    ("0.0", (NONE, None)),
])
def test_classify_boundaries(dev, expected):
    assert classify(Decimal(dev)) == expected


def test_display_formats():
    assert de(Decimal("4.4")) == "4,4" and de(None) == "–"
    assert de_signed(Decimal("-8.9")) == "−8,9" and de_signed(Decimal("7.0")) == "+7,0"
    assert de_signed(Decimal("0.0")) == "0,0"


def test_reference_keys_wrap_season():
    assert reference_label(reference_keys("2026/2027", 1, 34)) == "2025/2026: 15-34"
    assert reference_label(reference_keys("2025/2026", 3, 38)) == "2024/2025: 21-38 + 2025/2026: 1-2"
    assert len(reference_keys("2025/2026", 25, 34)) == 20


# --- 2-Tage-Regel und Spezialfälle mit ausgedachten Daten ------------------------------

def mini_db(rows):
    """rows: (id, Datum, Saison, Spieltag, Heim, Gast, Tore H, Tore G, Gelb H, Gelb G)"""
    return prepare_league(pd.DataFrame([{
        "id": r[0], "Date": pd.Timestamp(r[1]), "matchDate": pd.Timestamp(r[1]).strftime("%d-%m-%y 15:30"),
        "Season": r[2], "Gameday": r[3], "homeTeam": r[4], "awayTeam": r[5],
        "FT Home Goals": r[6], "FT Away Goals :": r[7],
        "Home Yellow Cards Full Time": r[8], "Away Yellow Cards Full Time": r[9],
    } for r in rows]))


def test_two_day_rule():
    db = mini_db([
        (1, "2026-09-01", "2026/2027", 1, "A", "B", 1, 0, 1, 1),   # 4 Tage vorher: zählt
        (2, "2026-09-03", "2026/2027", 2, "B", "A", 2, 2, 1, 1),   # 2 Tage vorher: zählt
        (3, "2026-09-04", "2026/2027", 3, "A", "C", 3, 0, 1, 1),   # Vortag: zählt nicht
        (4, "2026-09-05", "2026/2027", 4, "C", "A", 0, 1, 1, 1),   # selber Tag: zählt nicht
    ])
    ft = kpi01_team(db, "A", "2026/2027", date(2026, 9, 5))
    assert ft.form == ["–", "–", "–", "S", "U"] and ft.anzahl == 2
    tv = team_goals(db, "A", "2026/2027", date(2026, 9, 5))
    assert (tv.spiele, tv.summe) == (2, 5)


def test_one_game_and_real_zero_cards():
    db = mini_db([(1, "2026-08-01", "2026/2027", 1, "A", "B", 0, 0, 0, 2)])
    a = team_cards(db, "A", "2026/2027", date(2026, 9, 1))
    assert (a.spiele, a.summe, a.wert) == (1, 0, Fraction(0))   # echte Null zählt mit
    m = Match("Liga", "2026/2027", 2, date(2026, 9, 1), "A", "B")
    r = kpi04(db, m, 34)
    assert r.vorlaeufig and r.hauptwert == Fraction(2)


def test_kpi03_zero_deviation_has_title_but_no_text():
    db = mini_db([(1, "2026-08-01", "2026/2027", 1, "A", "B", 2, 1, 0, 0),
                  (2, "2026-08-08", "2026/2027", 2, "B", "A", 1, 1, 0, 0)])
    m = Match("Liga", "2026/2027", 3, date(2026, 9, 1), "A", "B")
    r = compute_match(db, m, 34).kpi03
    assert fmt_signed(r.abweichung_rund) == "0.0"
    assert r.ueberschrift == "Keine statistische Besonderheit" and r.text is None


def test_later_games_do_not_change_earlier_matchday(prepared):
    """Spieltag-Auswahl: Spieltag 1 wird so berechnet, als hätte es ihn noch nicht gegeben –
    auch wenn seine Ergebnisse (und spätere) schon in der Datenbank stehen."""
    base = prepared["Bundesliga"]
    m1 = Match("Bundesliga", "2026/2027", 1, date(2026, 8, 28), "Bayern Munich", "Stuttgart")
    before = compute_match(base, m1, 34)
    extra = mini_db([
        (900001, "2026-08-28", "2026/2027", 1, "Bayern Munich", "Stuttgart", 9, 9, 9, 9),
        (900002, "2026-09-04", "2026/2027", 2, "Stuttgart", "Bayern Munich", 7, 7, 7, 7),
    ])
    extended = pd.concat([base, extra]).sort_values(["date", "time", "id"], kind="stable").reset_index(drop=True)
    after = compute_match(extended, m1, 34)
    for key in ("kpi02", "kpi03", "kpi04"):
        a, b = getattr(before, key), getattr(after, key)
        assert (a.hauptwert, a.abweichung, a.vorlaeufig) == (b.hauptwert, b.abweichung, b.vorlaeufig)
        if a.referenz:
            assert (a.referenz.spiele, a.referenz.summe) == (b.referenz.spiele, b.referenz.summe)
    assert before.form_home.form == after.form_home.form
    # Spieltag 2 sieht die neuen Spiele dagegen schon
    m2 = Match("Bundesliga", "2026/2027", 2, date(2026, 9, 4), "Stuttgart", "Bayern Munich")
    assert 900001 in compute_match(extended, m2, 34).kpi02.heim.ids
