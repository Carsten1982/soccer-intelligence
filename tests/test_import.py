"""Version 0.14: Datenimport über API-Football (Spezifikation docs/06_Datenlieferung.md, Abschnitte 5, 7, 8, 10, 14).

Ohne Netz: Die API wird durch einen Ersatz mit gespeicherten Antworten ersetzt (tests/referenz/api: Spielliste
Bundesliga 2026/27, Details und Halbzeit-Statistik von Spieltag 9, ohne Spielerdaten).
- Umwandlung eines Spiels in die 58 Spalten (Tore, Halbzeiten, Statistik, leere Karten aus Ereignissen, Zeitzone)
- Spielplan: Hauptzeitraum, „verschoben“ ausserhalb von 3 Tagen, Status der API
- Teamnamen: feste Namen je ID, Umbenennung, unbekannte Teams
- Abfragen: Obergrenze, höchstens 3 Versuche, kein Schlüssel im Protokoll
- Ende zu Ende: Spieltag 9 aus der Datenbank entfernen -> der Lauf nimmt ihn wieder auf; Freigabe tauscht beide Dateien
  mit Backup; geänderte gültige Datei verhindert die Übernahme; ein neuer Lauf ersetzt den wartenden.
"""

from __future__ import annotations

import gzip
import json
import shutil
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import openpyxl
import pytest
from conftest import REFERENCE_DATABASE_2018

from core import schema
from importer import dienst
from importer.client import ApiClient, ImportFehler
from importer.convert import fixture_row, number, round_number
from importer.erzeugen import sha256
from importer.spielplan import fixture_rows, main_period
from importer.teams import TeamNames, load_team_names

API = Path(__file__).resolve().parent / "referenz" / "api"
NAMES_FILE = Path(__file__).resolve().parents[1] / "app" / "config" / "teamnamen.toml"
TZ = ZoneInfo("Europe/Zurich")


def load(name: str):
    return json.loads(gzip.decompress((API / name).read_bytes()))


@pytest.fixture(scope="module")
def season_list():
    return load("bundesliga_2026_spielliste.json.gz")["response"]


@pytest.fixture(scope="module")
def details():
    return {f["fixture"]["id"]: f for f in load("bundesliga_2026_spieltag9_details.json.gz")["response"]}


@pytest.fixture(scope="module")
def halves():
    return {int(k): v for k, v in load("bundesliga_2026_spieltag9_halbzeit.json.gz").items()}


# --- Umwandlung ----------------------------------------------------------------------------------------------------

def test_helpers():
    assert round_number("Regular Season - 12") == 12 and round_number("Final") is None
    assert number("55%") == 55 and number("2.14") == 2.14 and number(None) is None and number(0) == 0


def test_fixture_row_has_58_columns_and_consistent_goals(details, halves):
    names = load_team_names(NAMES_FILE)
    for fid, f in details.items():
        row = fixture_row(f, "Bundesliga", names, halves[fid])
        assert list(row) == list(schema.EXPECTED_COLUMNS) or set(row) == set(schema.EXPECTED_COLUMNS)
        assert row["id"] == fid and row["Season"] == "2026/2027" and row["Gameday"] == 9
        assert row["FT Home Goals"] == row["Full-Time Home Goals"] == f["goals"]["home"]
        assert row["First-Half Home Goals"] + row["Second-Half Home Goals"] == row["FT Home Goals"]
        assert row["FT Result :"] == row["Full-Time Result"] in ("H", "D", "A")
        local = datetime.fromisoformat(f["fixture"]["date"]).astimezone(TZ)
        assert row["matchDate"] == local.strftime("%d-%m-%y %H:%M") and row["Date"].date() == local.date()
        for side in ("Home", "Away"):
            for key in ("Corners", "Shots on Target", "Team Shots", "Yellow Cards"):
                full, a, b = (row[f"{side} {key} {p}"] for p in ("Full Time", "First Half", "Second Half"))
                if None not in (full, a, b):
                    assert a + b == full, (fid, side, key)
            assert row[f"{side} Ball Possession Full Time"] is None or 0 <= row[f"{side} Ball Possession Full Time"] <= 100


def test_empty_yellow_cards_are_counted_from_events(details):
    """E13: Die API meldet bei null Karten einen leeren Wert; mit Statistik und Ereignissen ist das eine sichere 0."""
    names = load_team_names(NAMES_FILE)
    f = json.loads(json.dumps(next(iter(details.values()))))
    hid = f["teams"]["home"]["id"]
    for s in f["statistics"]:
        if s["team"]["id"] == hid:
            for x in s["statistics"]:
                if x["type"] in ("Yellow Cards", "Corner Kicks"):
                    x["value"] = None
    f["events"] = [e for e in f["events"] if not (e["type"] == "Card" and e["team"]["id"] == hid)] or [
        {"time": {"elapsed": 10, "extra": None}, "team": {"id": f["teams"]["away"]["id"]}, "type": "subst", "detail": "x"}]
    row = fixture_row(f, "Bundesliga", names, None)
    assert row["Home Yellow Cards Full Time"] == 0 and row["Home Yellow Cards First Half"] == 0
    assert row["Home Corners Full Time"] is None                      # leer bleibt leer (nie 0)
    assert row["Home Corners First Half"] is None                     # ohne Halbzeit-Statistik keine Halbzeitwerte


# --- Spielplan -----------------------------------------------------------------------------------------------------

def _fx(fid, rnd, day, status="NS", home=1, away=2):
    return {"fixture": {"id": fid, "date": f"2026-11-{day:02d}T15:30:00+01:00", "status": {"short": status}},
            "league": {"season": 2026, "round": f"Regular Season - {rnd}"},
            "teams": {"home": {"id": home, "name": f"T{home}"}, "away": {"id": away, "name": f"T{away}"}}}


def test_main_period_and_postponed_rule():
    assert main_period([date(2026, 11, d) for d in (20, 21, 21, 22, 22, 29)]) == (date(2026, 11, 20), date(2026, 11, 22))
    names = TeamNames({}, {})
    rows = fixture_rows([_fx(1, 10, 20), _fx(2, 10, 21), _fx(3, 10, 22), _fx(4, 10, 25), _fx(5, 10, 26),
                         _fx(6, 10, 21, "PST"), _fx(7, 10, 21, "CANC"), _fx(8, 10, 21, "ABD"),
                         {**_fx(9, 1, 21), "league": {"season": 2026, "round": "Final"}}], names)
    by = {r["API-ID"]: r for r in rows}
    assert 9 not in by                                               # Relegation („Final“) gehört nicht dazu
    assert by[1]["Datum von"] == by[1]["Datum bis"] == datetime(2026, 11, 20) and by[1]["Status"] == ""
    assert by[4]["Status"] == "" and by[4]["Datum von"] == datetime(2026, 11, 25)       # 3 Tage danach: bleibt
    assert by[5]["Status"] == "verschoben" and by[5]["Datum von"] == datetime(2026, 11, 20)  # 4 Tage danach
    assert (by[6]["Status"], by[7]["Status"], by[8]["Status"]) == ("verschoben", "abgesagt", "abgebrochen")
    assert by[6]["Datum bis"] == datetime(2026, 11, 22)


def test_fixture_plan_from_real_season_list(season_list):
    rows = fixture_rows(season_list, load_team_names(NAMES_FILE))
    assert len(rows) == 306 and {r["Spieltag"] for r in rows} == set(range(1, 35))
    assert all(r["Datum von"] <= r["Datum bis"] for r in rows)


# --- Teamnamen -------------------------------------------------------------------------------------------------------

def test_team_names_fixed_per_id_and_reported():
    names = load_team_names(NAMES_FILE)
    assert names.renames["Bundesliga"]["FC Koln"] == "1. FC Köln" and names.renames["Bundesliga"]["Bayern Munich"] == "Bayern München"
    assert names.name({"id": 157, "name": "FC Bayern München AG"}) == "Bayern München"          # festgehalten
    assert names.changed[157] == ("Bayern München", "FC Bayern München AG")
    assert names.name({"id": 999999, "name": "Neuer Klub"}) == "Neuer Klub" and names.unknown == {999999: "Neuer Klub"}


# --- Abfragen --------------------------------------------------------------------------------------------------------

class Resp:
    def __init__(self, status, data, remaining="7000"):
        self.status_code, self._data, self.headers = status, data, {"x-ratelimit-requests-remaining": remaining}

    @property
    def ok(self):
        return self.status_code == 200

    def json(self):
        return self._data


class Session:
    def __init__(self, answers):
        self.answers, self.calls = list(answers), []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append((url, params, headers))
        return self.answers.pop(0)


def test_client_limit_retries_and_no_key_in_log(tmp_path):
    s = Session([Resp(500, None), Resp(200, {"errors": [], "response": [1]})])
    c = ApiClient("geheim123", tmp_path, limit=5, session=s, sleep=lambda x: None)
    assert c.get("status", {})["response"] == [1] and c.used == 2 and c.remaining == 7000
    log = (tmp_path / "abfragen.csv").read_text()
    assert "geheim123" not in log and log.count("\n") == 2
    assert "geheim123" not in "".join(p.read_bytes().decode("latin-1") for p in tmp_path.rglob("*.gz"))
    with pytest.raises(ImportFehler, match="3 Versuche"):
        ApiClient("k", tmp_path, session=Session([Resp(500, None)] * 3), sleep=lambda x: None).get("x", {})
    with pytest.raises(ImportFehler, match="Obergrenze"):
        ApiClient("k", tmp_path, limit=3, used_before=3, session=Session([]), sleep=lambda x: None).get("x", {})
    with pytest.raises(ImportFehler, match="Schlüssel fehlt"):
        ApiClient(None, tmp_path).get("x", {})
    with pytest.raises(ImportFehler, match="API meldet"):
        ApiClient("k", tmp_path, session=Session([Resp(200, {"errors": {"plan": "nein"}})]), sleep=lambda x: None).get("x", {})


# --- Ende zu Ende --------------------------------------------------------------------------------------------------------

class FakeApi:
    """Ersatz für ApiClient: Bundesliga aus den gespeicherten Antworten, übrige Ligen ohne Spiele."""
    def __init__(self, season_list, details, halves):
        self.season_list, self.details, self.halves = season_list, details, halves
        self.used, self.remaining, self.calls = 0, 7000, []

    def get(self, endpoint, params):
        self.used += 1
        self.calls.append((endpoint, dict(params)))
        if endpoint == "status":
            return {"response": {"subscription": {"plan": "Pro", "end": "2027-02-15T08:31:35+00:00", "active": True}}}
        if endpoint == "leagues":
            return {"response": [{"seasons": [{"year": 2026, "current": True}]}]}
        if endpoint == "fixtures" and "ids" in params:
            return {"response": [self.details[int(i)] for i in params["ids"].split("-") if int(i) in self.details]}
        if endpoint == "fixtures":
            return {"response": self.season_list if params["league"] == 78 else []}
        if endpoint == "fixtures/statistics":
            return {"response": self.halves.get(int(params["fixture"]), [])}
        raise AssertionError(endpoint)


@pytest.fixture(scope="module")
def setup(tmp_path_factory, season_list, details, halves):
    if not REFERENCE_DATABASE_2018.exists():
        pytest.skip("Referenz-Datenbank 451348b6 nicht vorhanden")
    root = tmp_path_factory.mktemp("import")
    data, base, backup = root / "data", root / "import", root / "backup"
    data.mkdir()
    wb = openpyxl.load_workbook(REFERENCE_DATABASE_2018)
    ws = wb["Bundesliga"]
    col = {c.value: i for i, c in enumerate(ws[1])}
    gone = [r[0].row for r in ws.iter_rows(min_row=2) if r[col["Season"]].value == "2026/2027" and r[col["Gameday"]].value == 9]
    for rr in sorted(gone, reverse=True):
        ws.delete_rows(rr)
    wb.save(data / "Database-Soccer-Intelligence.xlsx")
    fx = openpyxl.Workbook()
    sh = fx.active
    sh.title = "Bundesliga"
    sh.append(["Saison", "Spieltag", "Datum von", "Datum bis", "Heimmannschaft", "Gastmannschaft"])
    sh.append(["2026/2027", 10, datetime(2026, 11, 20), datetime(2026, 11, 22), "Bayern Munich", "FC Koln"])
    fx.save(data / "Spielplan.xlsx")
    api = FakeApi(season_list, details, halves)
    now = datetime(2026, 11, 16, 4, 0, tzinfo=TZ)                    # Montag -> ganze Saison prüfen
    rep = dienst.run(base, data, now, client=api)
    return {"data": data, "base": base, "backup": backup, "rep": rep, "api": api, "removed": len(gone), "now": now}


def test_run_adds_missing_matchday_and_reports(setup):
    rep, api = setup["rep"], setup["api"]
    assert setup["removed"] == 9 and rep["status"] == "wartet" and rep["fehler"] == 0
    assert len(rep["neue_spiele"]["Bundesliga"]) == 9 and rep["korrekturen"] == [] and rep["ganze_saison"] is True
    assert {r["alt"] for r in rep["umbenennungen"]} >= {"FC Koln", "Bayern Munich"}            # erster Lauf: Umbenennung
    assert rep["abo"] == {"plan": "Pro", "bis": "2027-02-15", "aktiv": True}
    assert sum(1 for e, p in api.calls if e == "fixtures" and "ids" in p) == 1                 # 9 Spiele in 1 Abfrage
    assert sum(1 for e, _ in api.calls if e == "fixtures/statistics") == 9
    staged = setup["base"] / "laeufe" / rep["lauf"]
    wb = openpyxl.load_workbook(staged / "Database-Soccer-Intelligence.xlsx", read_only=True)
    names = {r[7] for r in wb["Bundesliga"].iter_rows(min_row=2, values_only=True) if r[2]}
    assert "FC Koln" not in names and "1. FC Köln" in names
    fx = openpyxl.load_workbook(staged / "Spielplan.xlsx", read_only=True)
    assert fx.sheetnames == ["Bundesliga", "Premier League", "Serie A", "LaLiga"] and fx["Bundesliga"].max_row == 307
    assert rep["spielplan_aenderungen"]["entfallen"] == 0                    # alte Zeile (umbenannt) wiedergefunden
    md9 = [m for m in rep["vollstaendigkeit"]["Bundesliga"] if m["spieltag"] == 9]
    assert md9 == [] or md9[0]["fehlt"] == 0


def test_apply_swaps_with_backup_and_refuses_changed_base(setup, season_list, details, halves):
    data, base, backup = setup["data"], setup["base"], setup["backup"]
    before = sha256(data / "Database-Soccer-Intelligence.xlsx")
    run_id = setup["rep"]["lauf"]
    later = datetime(2026, 11, 16, 7, 30, tzinfo=TZ)
    (base / "anfragen").mkdir(exist_ok=True)
    (base / "anfragen" / "1_uebernehmen.json").write_text(json.dumps({"lauf": run_id, "aktion": "uebernehmen"}))
    dienst.process_requests(base, data, backup, later)
    assert not list((base / "anfragen").glob("*.json"))
    assert sha256(data / "Database-Soccer-Intelligence.xlsx") == setup["rep"]["dateien"]["datenbank"] != before
    assert len(list(backup.glob("Database-Soccer-Intelligence_*_vor_import.xlsx"))) == 1
    assert len(list(backup.glob("Spielplan_*_vor_import.xlsx"))) == 1
    assert dienst.load_report(base, run_id)["status"] == "übernommen" and dienst.load_state(base)["wartend"] is None
    # zweiter Lauf: nichts Neues; dritter Lauf ersetzt den wartenden zweiten
    api = FakeApi(season_list, details, halves)
    r2 = dienst.run(base, data, datetime(2026, 11, 17, 4, 0, tzinfo=TZ), client=api)
    assert sum(len(v) for v in r2["neue_spiele"].values()) == 0 and r2["umbenennungen"] == []
    r3 = dienst.run(base, data, datetime(2026, 11, 18, 4, 0, tzinfo=TZ), client=FakeApi(season_list, details, halves))
    assert dienst.load_report(base, r2["lauf"])["status"] == "ersetzt" and dienst.load_state(base)["wartend"] == r3["lauf"]
    # gültige Datei inzwischen von Hand geändert -> keine Übernahme
    shutil.copy2(REFERENCE_DATABASE_2018, data / "Database-Soccer-Intelligence.xlsx")
    msg = dienst.apply(base, data, backup, r3["lauf"], "uebernehmen", "Test", later)
    assert "geändert" in msg and sha256(data / "Database-Soccer-Intelligence.xlsx") == sha256(REFERENCE_DATABASE_2018)


def test_due_schedule():
    st = {"letzter_lauf_tag": "2026-11-16"}
    assert not dienst.due(st, datetime(2026, 11, 16, 9, 0))           # heute schon gelaufen
    assert dienst.due(st, datetime(2026, 11, 17, 4, 0)) and not dienst.due(st, datetime(2026, 11, 17, 3, 59))
    assert not dienst.due({}, datetime(2026, 11, 21, 9, 0))           # Samstag
