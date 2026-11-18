"""Version 0.15: Spielplan-Import nach Spezifikation Spielplan v2.1 und Ergebnis-Import nach Spezifikation v1.1
(Entscheidungen Carsten 15.11.2026: S1–S10, O1, O2, R1–R9).

Ohne Netz, mit den gespeicherten echten API-Antworten (Bundesliga 2026/27, Spieltag 9) und daraus abgeleiteten Fällen.
Spielplan (I…): Status nur aus der API, Nachholspiel/vorgezogen, Termin bestätigt/Zeit offen/vorläufig, Hauptzeitraum.
Ergebnisse (R…): Korrekturfenster 7 Tage, späte Korrekturen mit Entscheid, leere Werte überschreiben nie, Endstand gegen
Tor-Ereignisse, gewertete Spiele, unbekannte Teams, verschwundene Spiele, Plausibilität, IDs über alle Ligen,
Automatik nur bei unkritischen Fassungen, Zuordnungsdatei, Rohdaten-Aufbewahrung.
"""

from __future__ import annotations

import copy
import json
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

import openpyxl
import pandas as pd
import pytest
from conftest import REFERENCE_DATABASE_2018
from test_import import FakeApi, TZ, _fx, details, halves, season_list  # noqa: F401 (Fixtures)

from core.config import League
from core.fixtures import FEHLER, load_fixtures
from core.matchday import matchday_overview
from core.zuordnung import load_mapping
from importer import dienst, entscheide
from importer import einstellungen as E
from importer.convert import fixture_row
from importer.erzeugen import _links
from importer.spielplan import fixture_rows, main_period
from importer.teams import TeamNames

TODAY = date(2026, 11, 15)
NAMES = TeamNames({}, {})


def rows_by_id(fixtures, today=TODAY):
    return {r["API-ID"]: r for r in fixture_rows(fixtures, NAMES, today)}


def _at(fid, rnd, day: str, status="NS", home=1, away=2):
    """Spiel mit genauem Termin („2026-12-02T19:00:00+01:00“)."""
    f = _fx(fid, rnd, 1, status, home, away)
    f["fixture"]["date"] = day
    return f


# --- Spielplan (Spezifikation v2.1, Abschnitt 3) ----------------------------------------------------------------------

def test_statuses_from_api_only():
    """I1, I8, I9, I10 (S1): Originalstatus gespeichert; INT läuft weiter; SUSP ausgesetzt; AWD/WO gewertet."""
    games = [_fx(i, 10, 21, st, home=i, away=100 + i) for i, st in
             enumerate(["NS", "TBD", "INT", "SUSP", "PST", "CANC", "ABD", "AWD", "WO", "FT"], start=1)]
    by = rows_by_id(games)
    assert [by[i]["Status"] for i in range(1, 11)] == ["", "", "", "ausgesetzt", "verschoben", "abgesagt", "abgebrochen",
                                                      "gewertet", "gewertet", ""]
    assert [by[i]["API-Status"] for i in (2, 3, 4, 8)] == ["TBD", "INT", "SUSP", "AWD"]
    assert by[2]["Termin"] == "Zeit offen"                                 # TBD: Datum bekannt, Zeit offen


def test_catchup_and_early_games_keep_their_matchday():
    """I2, I3, I4 (S5): Nachholspiel (auch schon gespielt) und vorgezogenes Spiel – nie „verschoben“, Spieltag bleibt."""
    games = [_at(1, 23, "2027-02-06T15:30:00+01:00"), _at(2, 23, "2027-02-07T16:00:00+01:00", home=3, away=4),
             _at(3, 23, "2027-02-07T18:30:00+01:00", home=5, away=6),
             _at(4, 23, "2026-12-02T19:00:00+01:00", home=7, away=8),                     # vorgezogen (Supercopa)
             _at(5, 1, "2026-08-15T19:30:00+02:00", "FT"), _at(6, 1, "2026-08-16T21:00:00+02:00", "FT", 3, 4),
             _at(7, 1, "2026-08-27T21:00:00+02:00", "FT", 5, 6)]                          # gespieltes Nachholspiel
    by = rows_by_id(games)
    assert (by[4]["Status"], by[4]["Hinweis"], by[4]["Spieltag"]) == ("", "vorgezogen", 23)
    assert by[4]["Datum von"] == datetime(2026, 12, 2) and by[4]["Anstoss"] == "19:00"
    assert (by[7]["Status"], by[7]["Hinweis"], by[7]["Spieltag"]) == ("", "Nachholspiel", 1)
    assert by[1]["Hinweis"] == by[5]["Hinweis"] == ""


def test_termin_placeholder_needs_14_days():
    """I5, I6, I7 (S2): gleicher Termin aller Spiele ist nur weiter als 14 Tage weg ein Platzhalter; TBD je Spiel."""
    far = [_at(i, 30, "2027-04-10T15:30:00+02:00", home=i, away=50 + i) for i in range(1, 4)]
    last = [_at(10 + i, 34, "2026-11-20T15:30:00+01:00", home=10 + i, away=60 + i) for i in range(1, 4)]   # in 5 Tagen
    mixed = [_at(21, 12, "2026-12-05T15:30:00+01:00", "TBD", 21, 71), _at(22, 12, "2026-12-05T18:30:00+01:00", "NS", 22, 72)]
    by = rows_by_id(far + last + mixed)
    assert {by[i]["Termin"] for i in (1, 2, 3)} == {"vorläufig"}
    assert {by[i]["Termin"] for i in (11, 12, 13)} == {"bestätigt"}                # letzter Spieltag, gleichzeitig
    assert (by[21]["Termin"], by[22]["Termin"]) == ("Zeit offen", "bestätigt")
    assert by[11]["Status"] == "" and by[1]["Status"] == ""


def test_main_period_tie_and_no_regular_games():
    """I12, I13 (S5): Gleichstand -> früheres Fenster; ohne reguläre Spiele kein Hauptzeitraum und kein Vermerk."""
    tie = [_at(1, 5, "2026-10-01T20:00:00+02:00"), _at(2, 5, "2026-10-02T20:00:00+02:00", home=3, away=4),
           _at(3, 5, "2026-10-20T20:00:00+02:00", home=5, away=6), _at(4, 5, "2026-10-21T20:00:00+02:00", home=7, away=8)]
    by = rows_by_id(tie)
    assert by[1]["Hinweis"] == by[2]["Hinweis"] == "" and by[3]["Hinweis"] == by[4]["Hinweis"] == "Nachholspiel"
    only_pst = [_at(5, 6, "2026-10-03T15:30:00+02:00", "PST"), _at(6, 6, "2026-10-25T15:30:00+01:00", "PST", 3, 4)]
    by = rows_by_id(only_pst)
    assert by[5]["Hinweis"] == by[6]["Hinweis"] == "" and by[6]["Datum von"] == datetime(2026, 10, 25)


def test_laliga_friday_to_tuesday_is_regular_and_swiss_date():
    """I14, I19: Freitag bis Dienstag gehört regulär zum Spieltag; das Datum ist das Schweizer Datum der API-Zeit."""
    days = ["2026-11-20T21:00:00+01:00", "2026-11-21T14:00:00+01:00", "2026-11-22T21:00:00+01:00",
            "2026-11-23T21:00:00+01:00", "2026-11-24T21:00:00+01:00", "2026-11-21T00:30:00+01:00"]
    by = rows_by_id([_at(i, 13, d, home=i, away=40 + i) for i, d in enumerate(days, start=1)])
    assert {r["Hinweis"] for r in by.values()} == {""}
    assert by[6]["Datum von"] == datetime(2026, 11, 21) and by[6]["Anstoss"] == "00:30"   # in UTC noch der 20.11.


def _plan(path: Path, rows: list[list], header: list[str]) -> Path:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bundesliga"
    ws.append(header)
    for r in rows:
        ws.append(r)
    wb.save(path)
    return path


HEAD = ["Saison", "Spieltag", "Datum von", "Datum bis", "Heimmannschaft", "Gastmannschaft", "Status", "Anstoss",
        "Termin", "Hinweis", "API-Status", "API-ID"]
LEAGUE = [League("Bundesliga", "bundesliga", 4, True)]


def test_fixture_file_new_columns_and_statuses(tmp_path):
    """I20: neue Spalten und Status werden gelesen; ungültige Werte sind Fehler; alte Dateien bleiben lesbar."""
    d = datetime(2026, 11, 21)
    ok = [["2026/2027", 10, d, d, "A", "B", "ausgesetzt", "15:30", "bestätigt", "", "SUSP", 1],
          ["2026/2027", 10, d, d, "C", "D", "gewertet", "15:30", "Zeit offen", "Nachholspiel", "AWD", 2]]
    fx = load_fixtures(_plan(tmp_path / "a.xlsx", ok, HEAD), LEAGUE, {}, [])
    assert not fx.has_errors
    df = fx.leagues["Bundesliga"]
    assert list(df["status"]) == ["ausgesetzt", "gewertet"] and list(df["api_id"]) == [1, 2]
    assert list(df["hinweis"]) == ["", "Nachholspiel"] and list(df["termin"]) == ["bestätigt", "Zeit offen"]
    bad = [["2026/2027", 10, d, d, "A", "B", "", "15:30", "irgendwann", "später", "NS", 1]]
    fx = load_fixtures(_plan(tmp_path / "b.xlsx", bad, HEAD), LEAGUE, {}, [])
    assert {i.check for i in fx.issues if i.level == FEHLER} >= {"Termin ungültig", "Hinweis ungültig"}
    old = load_fixtures(_plan(tmp_path / "c.xlsx", [r[:6] for r in ok], HEAD[:6]), LEAGUE, {}, [])
    assert not old.has_errors and list(old.leagues["Bundesliga"]["hinweis"]) == ["", ""]


def test_catchup_game_does_not_keep_matchday_open(tmp_path):
    """Spielplan v2.1, 4.1: Ein spätes Nachholspiel hält seinen Spieltag nicht offen (sonst bliebe er „aktuell“)."""
    rows = [["2026/2027", 9, datetime(2026, 11, 7), datetime(2026, 11, 7), "A", "B", "", "15:30", "bestätigt", "", "FT", 1],
            ["2026/2027", 9, datetime(2026, 12, 9), datetime(2026, 12, 9), "C", "D", "", "20:30", "bestätigt", "Nachholspiel", "NS", 2],
            ["2026/2027", 10, datetime(2026, 11, 21), datetime(2026, 11, 21), "A", "C", "", "15:30", "bestätigt", "", "NS", 3]]
    fx = load_fixtures(_plan(tmp_path / "n.xlsx", rows, HEAD), LEAGUE, {}, [])
    md = {m.spieltag: m for m in matchday_overview(fx.leagues["Bundesliga"], date(2026, 11, 16))}
    assert md[9].beendet and md[10].status == "aktuell"
    assert md[9].letztes_datum == date(2026, 11, 7)                       # Zeitraum ohne das Nachholspiel


# --- Zuordnung (S6) --------------------------------------------------------------------------------------------------

def test_mapping_file_complete_and_unique():
    mapping = load_mapping()
    assert sum(len(v) for v in mapping.values()) == 11978
    for league, m in mapping.items():
        assert len(set(m.values())) == len(m)                               # jede eigene ID genau einmal
    if REFERENCE_DATABASE_2018.exists():
        own = {lg: set(pd.read_excel(REFERENCE_DATABASE_2018, sheet_name=lg, usecols=["id"])["id"].astype(int))
               for lg in mapping}
        for lg, m in mapping.items():
            assert set(m.values()) <= own[lg] or lg                         # Referenz 451348b6: gleiche IDs


def test_links_detect_pairing_conflict():
    class Db:
        leagues = {"Bundesliga": pd.DataFrame([{"id": 10, "Season": "2025/2026", "homeTeam": "A", "awayTeam": "B"}])}
    mapping = {"Bundesliga": {555: 10}}
    good = {"Bundesliga": [{"API-ID": 555, "Saison": "2025/2026", "Heimmannschaft": "A", "Gastmannschaft": "B"}]}
    bad = {"Bundesliga": [{"API-ID": 555, "Saison": "2025/2026", "Heimmannschaft": "A", "Gastmannschaft": "C"}]}
    assert _links(good, Db, mapping) == {"ids": {"Bundesliga": {555}}, "fehler": []}
    assert "Paarung passt nicht" in _links(bad, Db, mapping)["fehler"][0]["meldung"]


# --- Umwandlung: Gelbe Karten aus Ereignissen nur bei stimmigen Ereignissen (R3) ----------------------------------------

def _stat(d, team_id, kind, value):
    for s in d["statistics"]:
        if s["team"]["id"] == team_id:
            for x in s["statistics"]:
                if x["type"] == kind:
                    x["value"] = value


def test_yellow_fallback_only_with_consistent_events(details):
    fid = sorted(details)[0]
    d = copy.deepcopy(details[fid])
    hid = d["teams"]["home"]["id"]
    _stat(d, hid, "Yellow Cards", None)
    names = TeamNames({}, {})
    counted = fixture_row(d, "Bundesliga", names)["Home Yellow Cards Full Time"]
    assert counted is not None                                              # stimmige Ereignisse: gezählt (E13)
    d["score"]["fulltime"] = {"home": 9, "away": 9}
    d["goals"] = {"home": 9, "away": 9}
    assert fixture_row(d, "Bundesliga", names)["Home Yellow Cards Full Time"] is None   # unstimmig: bleibt leer


# --- Ende zu Ende: Ergebnis-Import -------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def base_db(tmp_path_factory):
    """Referenz-Datenbank 451348b6 ohne Bundesliga 2026/27 Spieltag 9 (wird von der API wieder geholt)."""
    if not REFERENCE_DATABASE_2018.exists():
        pytest.skip("Referenz-Datenbank 451348b6 nicht vorhanden")
    path = tmp_path_factory.mktemp("basis") / "Database-Soccer-Intelligence.xlsx"
    wb = openpyxl.load_workbook(REFERENCE_DATABASE_2018)
    ws = wb["Bundesliga"]
    col = {c.value: i for i, c in enumerate(ws[1])}
    gone = [r[0].row for r in ws.iter_rows(min_row=2) if r[col["Season"]].value == "2026/2027" and r[col["Gameday"]].value == 9]
    for rr in sorted(gone, reverse=True):
        ws.delete_rows(rr)
    wb.save(path)
    return path


def env(tmp_path: Path, base_db: Path, change=None) -> dict:
    data, base, backup = tmp_path / "data", tmp_path / "import", tmp_path / "backup"
    data.mkdir()
    if change:
        wb = openpyxl.load_workbook(base_db)
        change(wb)
        wb.save(data / "Database-Soccer-Intelligence.xlsx")
    else:
        shutil.copy2(base_db, data / "Database-Soccer-Intelligence.xlsx")
    fx = openpyxl.Workbook()
    fx.active.title = "Bundesliga"
    fx.active.append(HEAD[:6])
    fx.save(data / "Spielplan.xlsx")
    return {"data": data, "base": base, "backup": backup}


def run(e, when, api):
    return dienst.run(e["base"], e["data"], when, client=api)


def take(e, rep, when):
    assert dienst.apply(e["base"], e["data"], e["backup"], rep["lauf"], "uebernehmen", "Test", when) == "übernommen"


def decide(e, **req):
    folder = e["base"] / "anfragen"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{len(list(folder.iterdir()))}_entscheid.json").write_text(json.dumps({"aktion": "entscheid", **req}))
    dienst.process_requests(e["base"], e["data"], e["backup"], datetime(2026, 11, 30, 9, 0, tzinfo=TZ))


def db_value(e, fid, column):
    wb = openpyxl.load_workbook(e["data"] / "Database-Soccer-Intelligence.xlsx", read_only=True)
    ws = wb["Bundesliga"]
    head = [c.value for c in next(ws.iter_rows(max_row=1))]
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[head.index("id")] == fid:
            return r[head.index(column)]
    return "fehlt"


@pytest.mark.langsam
def test_correction_window_late_decision_and_empty_values(base_db, season_list, details, halves, tmp_path):
    """R1: Korrekturen bis 7 Tage selbst; danach Entscheid per Button; ein leerer API-Wert überschreibt nie."""
    e = env(tmp_path, base_db)
    f0, f1 = sorted(details)[:2]
    r1 = run(e, datetime(2026, 11, 10, 4, 0, tzinfo=TZ), FakeApi(season_list, details, halves))   # Spieltag 9: 6.–8.11.
    assert len(r1["neue_spiele"]["Bundesliga"]) == 9 and r1["status"] == "wartet"
    take(e, r1, datetime(2026, 11, 10, 8, 0, tzinfo=TZ))
    corners = db_value(e, f0, "Home Corners Full Time")
    d2 = copy.deepcopy(details)
    _stat(d2[f0], d2[f0]["teams"]["home"]["id"], "Corner Kicks", corners + 1)
    _stat(d2[f1], d2[f1]["teams"]["home"]["id"], "Shots on Goal", None)                      # leer: überschreibt nicht
    r2 = run(e, datetime(2026, 11, 11, 4, 0, tzinfo=TZ), FakeApi(season_list, d2, halves))
    corr = [c for c in r2["korrekturen"] if c["id"] == f0 and c["spalte"] == "Home Corners Full Time"]
    assert corr and corr[0]["art"] == "im Korrekturfenster" and corr[0]["kpi"] is True
    assert not [c for c in r2["korrekturen"] if c["id"] == f1]
    take(e, r2, datetime(2026, 11, 11, 8, 0, tzinfo=TZ))
    assert db_value(e, f0, "Home Corners Full Time") == corners + 1
    # nach 7 Tagen eingefroren: späte Korrektur wartet auf Entscheid
    d3 = copy.deepcopy(details)
    _stat(d3[f0], d3[f0]["teams"]["home"]["id"], "Corner Kicks", corners + 2)
    r3 = run(e, datetime(2026, 11, 20, 4, 0, tzinfo=TZ), FakeApi(season_list, d3, halves))
    late = [c for c in r3["spaete_korrekturen"] if c["id"] == f0]
    assert late and late[0]["neu"] == corners + 2 and not [c for c in r3["korrekturen"] if c["id"] == f0]
    decide(e, art="korrektur", id=f0, liga="Bundesliga", spiel="x", spalte="Home Corners Full Time",
           api_wert=corners + 2, entscheid="uebernehmen")
    assert entscheide.lookup(entscheide.load(e["base"]), "korrektur", f0, "Home Corners Full Time", corners + 2) == "uebernehmen"
    r4 = run(e, datetime(2026, 11, 21, 4, 0, tzinfo=TZ), FakeApi(season_list, d3, halves))
    assert [c["art"] for c in r4["korrekturen"] if c["id"] == f0] == ["Entscheid: übernommen"] and not r4["spaete_korrekturen"]
    take(e, r4, datetime(2026, 11, 21, 8, 0, tzinfo=TZ))
    assert db_value(e, f0, "Home Corners Full Time") == corners + 2
    assert list(e["backup"].glob("entscheidungen_*_vor_import.json"))                 # Entscheide gesichert
    # abgelehnt: dieser Wert wird nie wieder gefragt
    d5 = copy.deepcopy(details)
    _stat(d5[f0], d5[f0]["teams"]["home"]["id"], "Corner Kicks", corners + 5)
    decide(e, art="korrektur", id=f0, spalte="Home Corners Full Time", api_wert=corners + 5, entscheid="ablehnen")
    r5 = run(e, datetime(2026, 11, 22, 4, 0, tzinfo=TZ), FakeApi(season_list, d5, halves))
    assert not [c for c in r5["spaete_korrekturen"] + r5["korrekturen"] if c["id"] == f0]


@pytest.mark.langsam
def test_score_against_goal_events_waits_for_decision(base_db, season_list, details, halves, tmp_path, monkeypatch):
    """R2 und R5: Endstand ≠ Tor-Ereignisse -> Spiel wartet, kein Automatik-Tausch; „platz“ bzw. „api“ entscheiden."""
    monkeypatch.setattr(E, "automatic_from", lambda: date(2026, 1, 1))     # Automatikbetrieb
    e = env(tmp_path, base_db)
    f0, f1 = sorted(details)[:2]
    d = copy.deepcopy(details)
    for fid in (f0, f1):
        d[fid]["score"]["fulltime"] = {"home": 3, "away": 0}
        d[fid]["goals"] = {"home": 3, "away": 0}
    when = datetime(2026, 11, 10, 4, 0, tzinfo=TZ)
    r1 = run(e, when, FakeApi(season_list, d, halves))
    crit = {k["id"]: k for k in r1["kritisch"] if k["art"] == "endstand"}
    assert set(crit) == {f0, f1} and crit[f0]["api"] == "3:0"
    assert {g["id"] for g in r1["neue_spiele"]["Bundesliga"]} == set(sorted(details)[2:])
    assert r1["status"] == "wartet" and r1["automatik"]["ok"] is False             # nicht automatisch übernommen
    md9 = [m for m in r1["vollstaendigkeit"]["Bundesliga"] if m["spieltag"] == 9]
    assert md9 and any("wartet auf Entscheid" in x for x in md9[0]["fehlende"])
    events = crit[f0]["ereignisse"]
    decide(e, art="endstand", id=f0, entscheid="platz")
    decide(e, art="endstand", id=f1, entscheid="api")
    r2 = run(e, when.replace(hour=5), FakeApi(season_list, d, halves))
    new = {g["id"]: g for g in r2["neue_spiele"]["Bundesliga"]}
    assert new[f0]["endstand"] == events and new[f1]["endstand"] == "3:0" and not r2["kritisch"]


@pytest.mark.langsam
def test_awarded_unknown_team_status_open_and_vanished(base_db, season_list, details, halves, tmp_path):
    """R2 (gewertet), unbekanntes Team, NS mit vergangenem Termin, verschwundenes Spiel (alle im Bericht)."""
    e = env(tmp_path, base_db)
    f2, f3, f4 = sorted(details)[2:5]
    sl, d = copy.deepcopy(season_list), copy.deepcopy(details)
    for f in sl:
        if f["fixture"]["id"] == f2:
            f["fixture"]["status"]["short"] = "AWD"
    for src in ([f for f in sl if f["fixture"]["id"] == f3][0], d[f3]):
        src["teams"]["home"] = {"id": 999999, "name": "Neuer Klub"}
    for s in d[f3]["statistics"]:
        if s["team"]["id"] == details[f3]["teams"]["home"]["id"]:
            s["team"]["id"] = 999999
    r1 = run(e, datetime(2026, 11, 25, 4, 0, tzinfo=TZ), FakeApi(sl, d, halves))
    assert [w["id"] for w in r1["wertungen"]] == [f2] and f2 not in {g["id"] for g in r1["neue_spiele"]["Bundesliga"]}
    assert r1["unbekannte_teams"] == [{"api_team_id": 999999, "name": "Neuer Klub"}]
    assert any(k["art"] == "status_offen" for k in r1["kritisch"])                  # Spieltag 10 (20.–22.11.) ohne FT
    staged = openpyxl.load_workbook(e["base"] / "laeufe" / r1["lauf"] / "Spielplan.xlsx", read_only=True)
    sh = list(staged["Bundesliga"].iter_rows(values_only=True))
    status = {r[sh[0].index("API-ID")]: r[sh[0].index("Status")] for r in sh[1:]}
    assert status[f2] == "gewertet"
    take(e, r1, datetime(2026, 11, 25, 8, 0, tzinfo=TZ))
    sl2 = [f for f in sl if f["fixture"]["id"] != f4]
    r2 = run(e, datetime(2026, 11, 26, 4, 0, tzinfo=TZ), FakeApi(sl2, d, halves))
    assert [k["id"] for k in r2["kritisch"] if k["art"] == "verschwunden"] == [f4]


@pytest.mark.langsam
def test_plausibility_errors_warnings_and_open_fields(base_db, season_list, details, halves, tmp_path):
    """R6 (Grenzen Carsten: Ecken 30, aufs Tor 25) und R4 (offene Spiele nennen die fehlenden KPI-Felder)."""
    e = env(tmp_path, base_db)
    f0, f1, f2 = sorted(details)[:3]
    d = copy.deepcopy(details)
    _stat(d[f0], d[f0]["teams"]["home"]["id"], "Corner Kicks", 31)
    _stat(d[f1], d[f1]["teams"]["home"]["id"], "Shots on Goal", 26)
    _stat(d[f1], d[f1]["teams"]["home"]["id"], "Total Shots", 20)
    _stat(d[f2], d[f2]["teams"]["home"]["id"], "Corner Kicks", None)
    r = run(e, datetime(2026, 11, 10, 4, 0, tzinfo=TZ), FakeApi(season_list, d, halves))
    warn = [w["meldung"] for w in r["plausibilitaet"]["warnungen"]]
    err = [w["meldung"] for w in r["plausibilitaet"]["fehler"]]
    assert any("Corners 31" in w for w in warn) and any("Shots on Target 26" in w for w in warn)
    assert any("grösser als Schüsse gesamt" in m for m in err) and r["fehler"] >= 1
    assert r["status"] == "Fehler – nicht übernehmbar"
    offen = [o for o in r["offen"] if o["id"] == f2]
    assert offen and offen[0]["fehlt"] == ["Ecken"]


@pytest.mark.langsam
def test_duplicate_id_across_leagues_blocks(base_db, season_list, details, halves, tmp_path):
    """R8: Jede id nur einmal über alle Ligen; eine Kollision ist ein Fehler und sperrt die Übernahme."""
    target = sorted(details)[0]

    def collide(wb):
        ws = wb["Premier League"]
        col = [c.value for c in ws[1]].index("id")
        ws.cell(row=2, column=col + 1).value = target
    e = env(tmp_path, base_db, collide)
    r = run(e, datetime(2026, 11, 10, 4, 0, tzinfo=TZ), FakeApi(season_list, details, halves))
    assert [x["id"] for x in r["doppelte_ids"]] == [target] and r["fehler"] >= 1


def test_raw_data_kept_12_months(tmp_path):
    """R9: Rohdaten-Tagesordner älter als 365 Tage werden gelöscht."""
    old, new = tmp_path / "2025-11-01", tmp_path / "2026-11-01"
    for d in (old, new):
        d.mkdir()
        (d / "x.json.gz").write_bytes(b"x")
    dienst._prune_raw(tmp_path, date(2026, 11, 15))
    assert not old.exists() and new.exists()


def test_decisions_only_valid_values(tmp_path):
    with pytest.raises(ValueError):
        entscheide.add(tmp_path, {"art": "korrektur", "id": 1, "entscheid": "vielleicht"})
    entscheide.add(tmp_path, {"art": "endstand", "id": 7, "entscheid": "platz"})
    assert entscheide.lookup(entscheide.load(tmp_path), "endstand", 7) == "platz"
    assert entscheide.lookup(entscheide.load(tmp_path), "endstand", 8) is None


def test_daily_schedule_and_next_run():
    """Spielplan v2.1, 3.7: täglich um 04:00, auch am Wochenende."""
    from views.datenimport import next_run
    sat = datetime(2026, 11, 21, 3, 0, tzinfo=TZ)
    assert next_run(sat, {}).date() == date(2026, 11, 21)
    assert next_run(sat, {"letzter_lauf_tag": "2026-11-21"}) == datetime(2026, 11, 22, 4, 0, tzinfo=TZ)
    assert dienst.due({}, datetime(2026, 11, 22, 4, 0, tzinfo=TZ)) and not dienst.due({}, sat)
    assert timedelta(days=E.CORRECTION_DAYS) == timedelta(days=7)


def test_main_period_sliding_window_equals_previous_version():
    """Bereinigung B3 (0.19.1): gleitendes Fenster statt Neufiltern je Starttag – gleiches Ergebnis wie vorher,
    auch bei Gleichstand (früheres Fenster gewinnt). Vergleich mit der bisherigen Umsetzung an Zufallsdaten."""
    import random
    from datetime import timedelta

    from importer.spielplan import WINDOW

    def before(days):
        if not days:
            return None
        best = None
        for start in sorted(set(days)):
            inside = [d for d in days if start <= d <= start + timedelta(days=WINDOW)]
            if best is None or len(inside) > len(best):
                best = inside
        return min(best), max(best)

    rnd = random.Random(19)
    for _ in range(3000):
        days = [date(2026, 8, 1) + timedelta(days=rnd.randint(0, 40)) for _ in range(rnd.randint(0, 12))]
        assert main_period(days) == before(days), days
