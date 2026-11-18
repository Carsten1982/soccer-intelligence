"""KPI 01–09 gegen die bestätigten Testfälle in docs/tests/*.md (JSON-Blöcke).

Die Testfälle KPI 01–04 gelten für die Datenbank mit der SHA-256 aus conftest.KNOWN_DB_SHA,
die Testfälle KPI 05–09 für conftest.KNOWN_DB_SHA_H (beide liegen in tests/referenz).
Seit Etappe H (08.11.2026) werden alle Werte auf zwei Nachkommastellen gerundet.
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
from conftest import KNOWN_DB_SHA, KNOWN_DB_SHA_H, REFERENCE_DATABASE, REFERENCE_DATABASE_H

from core.kpis import (
    HIGH, KPI_KEYS, LOW, MEDIUM, NONE, Match, Signal, Thresholds, classify, compute_match, de, de_abs, de_signed, fmt,
    fmt_signed, kpi01_team, kpi02, kpi04, prepare_league, reference_keys, reference_label, round_display, stat_kpi,
    team_cards, team_goals,
)
from core.loader import load_database

DOCS = Path(__file__).resolve().parents[1] / "docs" / "tests"
MATCHDAYS = {"Bundesliga": 34, "Premier League": 38, "Serie A": 38, "LaLiga": 38}
TOL = 1e-9

# Die bestätigten Testfälle (docs/tests) wurden mit der Standardschwelle ±20 % (bis Version 0.18 „leicht“) erstellt.
# Seit Version 0.19 gibt es je Richtung eine Schwelle mit Prognosewert. Für die Testfälle gilt darum die Schwelle 20 %
# in beiden Richtungen: Texte und Überschriften der Fälle bleiben gültig; „leicht“ und „stark“ heissen dort „auffällig“.
LEGACY = Thresholds(Signal(Decimal(20), LOW), Signal(Decimal(20), LOW))


def legacy(_league: str, _kpi: str) -> Thresholds:
    return LEGACY


def same_flag(anomaly, expected) -> bool:
    """Bisherige Erwartung (keine/leicht/stark) gegen die neue Einstufung (keine / auffällig)."""
    if expected is None:
        return anomaly is None
    return (anomaly == NONE) == (expected == "keine")


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
    assert same_flag(r.anomalie, case["anomalie"]), (case["testfall"], r.anomalie)
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
    r = kpi02(prepared[m.league], m, MATCHDAYS[m.league], thresholds=LEGACY)
    check_team(r.heim, case["heim"], "tore")
    check_team(r.auswaerts, case["auswaerts"], "tore")
    check_reference(r.referenz, case["ligareferenz"], "tore")
    check_result(r, case, "torindikator")


@pytest.mark.parametrize("case", json_cases("test_kpi03_over25.md"), ids=lambda c: c["testfall"])
def test_kpi03(prepared, case):
    m = match_of(case)
    r = compute_match(prepared[m.league], m, MATCHDAYS[m.league], legacy).kpi03
    assert case["referenzwert"] == "2.5"
    check_team(r.heim, case["heim"], "tore")
    check_team(r.auswaerts, case["auswaerts"], "tore")
    for dev, side in zip(r.teamabweichung, ("heim", "auswaerts")):
        assert close(dev, case[side]["teamabweichung_roh"])
        assert fmt_signed(round_display(dev)) == case[side]["teamabweichung"]
    check_result(r, case, "gemeinsam")


@pytest.mark.parametrize("case", json_cases("test_kpi04_gelbe_karten.md"), ids=lambda c: c["testfall"])
def test_kpi04(prepared, case):
    m = match_of(case)
    r = kpi04(prepared[m.league], m, MATCHDAYS[m.league], thresholds=LEGACY)
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
    (Fraction(2675, 1000), "2.68"),  # round(2.675, 2) ergäbe fälschlich 2,67
    (Fraction(87, 20), "4.35"),      # bis 08.11.2026 mit einer Stelle 4,4
    (Fraction(-2675, 1000), "-2.68"),  # kaufmännisch weg von null
    (Fraction(20004, 1000), "20.00"),
    (Fraction(6), "6.00"),
    (Fraction(-4, 1000), "0.00"),    # −0,00 -> 0,00 (Regelwerk 2.4)
    (Fraction(-5, 1000), "-0.01"),
])
def test_round_display(value, expected):
    assert fmt(round_display(value)) == expected


@pytest.mark.parametrize("dev, expected", [
    ("20.00", (NONE, "positiv")), ("-20.00", (NONE, "negativ")), ("20.01", (LOW, "positiv")),
    ("-20.01", (LOW, "negativ")), ("0.00", (NONE, None)),
])
def test_classify_boundaries(dev, expected):
    assert classify(Decimal(dev), LEGACY) == expected


def test_classify_without_thresholds_never_flags():
    assert classify(Decimal("99.00")) == (NONE, "positiv") and classify(Decimal("-99.00")) == (NONE, "negativ")


def test_classify_with_own_thresholds_per_direction():
    t = Thresholds(Signal(Decimal("12"), HIGH), Signal(Decimal("18"), MEDIUM))
    assert classify(Decimal("12.00"), t)[0] == NONE and classify(Decimal("12.01"), t)[0] == HIGH
    assert classify(Decimal("-18.00"), t)[0] == NONE and classify(Decimal("-18.01"), t) == (MEDIUM, "negativ")


def test_display_formats():
    assert de(Decimal("4.35")) == "4,35" and de(None) == "–"
    assert de_signed(Decimal("-8.90")) == "−8,90" and de_signed(Decimal("7.01")) == "+7,01"
    assert de_signed(Decimal("0.00")) == "0,00" and de_abs(Decimal("-39.31")) == "39,31"
    assert de_signed(round_display(Fraction(-1, 1000))) == "0,00"      # kein „−0,00“


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
    assert fmt_signed(r.abweichung_rund) == "0.00"
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
    for key in KPI_KEYS:
        a, b = getattr(before, key), getattr(after, key)
        assert (a.hauptwert, a.abweichung, a.vorlaeufig) == (b.hauptwert, b.abweichung, b.vorlaeufig)
        if a.referenz:
            assert (a.referenz.spiele, a.referenz.summe) == (b.referenz.spiele, b.referenz.summe)
    assert before.form_home.form == after.form_home.form
    # Spieltag 2 sieht die neuen Spiele dagegen schon
    m2 = Match("Bundesliga", "2026/2027", 2, date(2026, 9, 4), "Stuttgart", "Bayern Munich")
    assert 900001 in compute_match(extended, m2, 34).kpi02.heim.ids


# --- KPI 05–09 (Regelwerk 9) gegen die bestätigten Testfälle -----------------------------

STAT_FILES = {"kpi05": "test_kpi05_ecken.md", "kpi06": "test_kpi06_tore_hz1.md", "kpi07": "test_kpi07_tore_hz2.md",
              "kpi08": "test_kpi08_btts.md", "kpi09": "test_kpi09_schuesse_aufs_tor.md"}


@pytest.fixture(scope="module")
def prepared_h():
    if not REFERENCE_DATABASE_H.exists() or not DOCS.exists():
        pytest.skip("Referenz-Datenbank (Etappe H) oder docs/tests nicht vorhanden")
    db = load_database(REFERENCE_DATABASE_H)
    assert db.sha256 == KNOWN_DB_SHA_H, "Referenz-Datenbank (Etappe H) wurde verändert"
    return {name: prepare_league(df) for name, df in db.leagues.items()}


def stat_cases():
    if not DOCS.exists():
        return []
    return [(key, case) for key, f in STAT_FILES.items() for case in json_cases(f)]


def check_stat(r, case):
    for tv, side in ((r.heim, "heim"), (r.auswaerts, "auswaerts")):
        exp = case[side]
        assert (tv.team, tv.spiele, tv.summe) == (exp["team"], exp["spiele"], exp["summe"]), (case["testfall"], side)
        assert close(tv.wert, exp["teamwert_roh"]) and fmt(tv.wert_rund) == exp["teamwert"], (case["testfall"], side)
    ref = case["ligareferenz"]
    assert (r.referenz.label, r.referenz.spiele, r.referenz.summe) == (ref["saison_spieltage"], ref["spiele"], ref["summe"])
    assert close(r.referenz.wert, ref["wert_roh"]) and fmt(r.referenz.wert_rund) == ref["wert"]
    assert close(r.hauptwert, case["hauptwert_roh"]) and fmt(r.hauptwert_rund) == case["hauptwert"]
    assert close(r.abweichung, case["abweichung_roh"]), (case["testfall"], r.abweichung)
    assert fmt(r.abweichung_rund) == case["abweichung"], (case["testfall"], r.abweichung_rund)
    assert same_flag(r.anomalie, case["anomalie"]), (case["testfall"], r.anomalie)
    assert (r.richtung, r.vorlaeufig) == (case["richtung"], case["vorlaeufig"])
    assert r.ueberschrift == case["ueberschrift"] and r.text == case["text"], case["testfall"]


@pytest.mark.parametrize("key, case", stat_cases(), ids=lambda x: x if isinstance(x, str) else x["testfall"])
def test_kpi05_to_09(prepared_h, key, case):
    m = match_of(case)
    r = stat_kpi(prepared_h[m.league], m, MATCHDAYS[m.league], key, thresholds=LEGACY)
    check_stat(r, case)
    # compute_match liefert für alle KPIs auf einmal dasselbe
    assert vars(getattr(compute_match(prepared_h[m.league], m, MATCHDAYS[m.league], legacy), key)) == vars(r)


def test_stat_cases_cover_all_files():
    keys = [k for k, _ in stat_cases()]
    assert {k: keys.count(k) for k in STAT_FILES} == {"kpi05": 12, "kpi06": 12, "kpi07": 12, "kpi08": 11, "kpi09": 14}


def test_stat_kpis_skip_missing_values_never_zero():
    """Ecken fehlen in einem Spiel: Spiel fällt weg (kein älteres nachziehen), echte Nullen zählen mit."""
    rows = [(i, f"2026-08-{i:02d}", "2026/2027", i, "A" if i % 2 else "B", "B" if i % 2 else "A", 1, 1, 0, 0)
            for i in range(1, 13)]
    df = pd.DataFrame([{
        "id": r[0], "Date": pd.Timestamp(r[1]), "matchDate": pd.Timestamp(r[1]).strftime("%d-%m-%y 15:30"),
        "Season": r[2], "Gameday": r[3], "homeTeam": r[4], "awayTeam": r[5], "FT Home Goals": r[6],
        "FT Away Goals :": r[7], "Home Corners Full Time": (None if r[0] == 12 else 0 if r[0] == 11 else 4),
        "Away Corners Full Time": 2,
    } for r in rows])
    db = prepare_league(df)
    m = Match("Liga", "2026/2027", 20, date(2026, 9, 30), "A", "B")
    r = stat_kpi(db, m, 34, "kpi05")
    assert r.heim.spiele == 9 and 12 not in r.heim.ids and 2 not in r.heim.ids     # 10 letzte, davon 1 leer
    assert r.heim.summe == 8 * 6 + 2                                              # Spiel 11: echte Null zählt
    assert r.vorlaeufig
    r8 = stat_kpi(db, m, 34, "kpi08")
    assert r8.prozent and r8.heim.wert == Fraction(100) and r8.heim.summe == 10   # 1:1 -> immer BTTS
