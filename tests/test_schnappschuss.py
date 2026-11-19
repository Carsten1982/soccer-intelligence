"""Schnappschuss je Spiel (seit 0.20; core/schnappschuss.py, importer/schnappschuss.py). Testfälle SN1–SN10.

Kleine, feste Daten: die Mini-Datenbank aus conftest (je Liga zwei Teams, Saison 2024/2025) und ein passender
Spielplan mit API-IDs. Gerechnet wird mit denselben Funktionen wie Dashboard und Website.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from fractions import Fraction

import pandas as pd
import pytest
from conftest import make_match, write_workbook

from core import anzeige as A
from core import schnappschuss as S
from core import schema
from core.kpis import Match, compute_match, prepare_league

SEASON = "2024/2025"
LEAGUES = (("Bundesliga", 1), ("Premier League", 2), ("Serie A", 3), ("LaLiga", 4))


def _db_sheets() -> dict[str, pd.DataFrame]:
    """Je Liga drei gespielte Spiele (Spieltag 1–3) dreier Teams; jede Paarung einmal je Saison."""
    out = {}
    for name, n in LEAGUES:
        rows = [make_match(n * 100 + 1, "Alpha", "Beta", "2024-08-24", league=name, gameday=1),
                make_match(n * 100 + 2, "Gamma", "Alpha", "2024-09-01", ft=(2, 2), ht=(0, 1), league=name, gameday=2),
                make_match(n * 100 + 3, "Beta", "Gamma", "2024-09-14", ft=(3, 1), ht=(1, 0), league=name, gameday=3)]
        out[name] = pd.DataFrame(rows, columns=list(schema.EXPECTED_COLUMNS))
    return out


PLAN_COLUMNS = ["Saison", "Spieltag", "Datum von", "Datum bis", "Heimmannschaft", "Gastmannschaft", "Status",
                "Anstoss", "Termin", "Hinweis", "API-Status", "API-ID"]


def _plan_sheets() -> dict[str, pd.DataFrame]:
    """Spieltag 1–3 gespielt (in der Datenbank), 4 am 21.09. um 15:30, 5 am 28.09. ohne Uhrzeit (Alpha spielt
    vorher Spieltag 4)."""
    out = {}
    for name, n in LEAGUES:
        games = [(1, "2024-08-24", "Alpha", "Beta", "15:30", "FT"), (2, "2024-09-01", "Gamma", "Alpha", "15:30", "FT"),
                 (3, "2024-09-14", "Beta", "Gamma", "15:30", "FT"), (4, "2024-09-21", "Alpha", "Gamma", "15:30", "NS"),
                 (5, "2024-09-28", "Beta", "Alpha", "", "TBD")]
        rows = [[SEASON, md, pd.Timestamp(day), pd.Timestamp(day), h, a, "geplant", clock,
                 "Zeit offen" if not clock else "bestätigt", "", api, n * 1000 + md]
                for md, day, h, a, clock, api in games]
        out[name] = pd.DataFrame(rows, columns=PLAN_COLUMNS)
    return out


@pytest.fixture
def data_dir(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    write_workbook(d / "Database-Soccer-Intelligence.xlsx", _db_sheets())
    write_workbook(d / "Spielplan.xlsx", _plan_sheets())
    return d


_PREPARED: dict = {}


def _kpis(day: str = "2024-09-21", home="Alpha", away="Gamma", md=4):
    """KPIs eines Bundesliga-Spiels der Mini-Datenbank (eingelesen wie im Betrieb, mit den echten Schwellen)."""
    if "bl" not in _PREPARED:
        import tempfile
        from pathlib import Path

        from core.loader import load_database
        with tempfile.TemporaryDirectory() as d:
            db = load_database(write_workbook(Path(d) / "db.xlsx", _db_sheets()))
        assert not db.has_errors, db.issues
        _PREPARED["bl"] = prepare_league(db.leagues["Bundesliga"])
    from core import settings
    from core.thresholds import load_thresholds
    th = load_thresholds(settings.THRESHOLDS_FILE, [n for n, _ in LEAGUES])
    from core.config import load_leagues
    matchdays = {lg.name: lg.matchdays for lg in load_leagues()}["Bundesliga"]
    return compute_match(_PREPARED["bl"], Match("Bundesliga", SEASON, md, date.fromisoformat(day), home, away),
                         matchdays, th.get)


# --- SN1–SN3: Speichern, Lesen, nie überschreiben -------------------------------------------------------------

def test_sn1_roundtrip_is_exact():
    k = _kpis()
    assert isinstance(k.kpi02.hauptwert, Fraction)
    back = S.decode(json.loads(json.dumps(S.encode(k))))
    assert back == k and back.kpi02.anomalie == k.kpi02.anomalie and back.kpi02.schwellen == k.kpi02.schwellen
    assert S.encode(Fraction(1, 3)) == {"$b": "1/3"}
    with pytest.raises(TypeError):
        S.encode(object())


def test_sn2_write_once_never_overwrites(tmp_path):
    p = tmp_path / "a" / "1.json"
    assert S.write_once(p, {"x": 1}) and not S.write_once(p, {"x": 2})
    assert json.loads(p.read_text()) == {"x": 1} and not list(p.parent.glob(".*.tmp"))


def test_sn3_read_missing_unknown_format_and_cache(tmp_path):
    assert S.read(tmp_path, "bundesliga", SEASON, 7) is None and S.read(tmp_path, "bundesliga", SEASON, None) is None
    row = next(A.prepare(pd.DataFrame([{"saison": SEASON, "spieltag": 4, "datum_von": date(2024, 9, 21),
                                         "datum_bis": date(2024, 9, 21), "heim": "Beta", "gast": "Alpha",
                                         "status": "geplant", "excel_row": 2, "reihenfolge": 0, "anstoss": "15:30",
                                         "termin": "bestätigt", "hinweis": "", "api_status": "NS",
                                         "api_id": 7}])).itertuples())
    data = S.payload(_kpis(), row, datetime(2024, 9, 21, 14, 31), "Bundesliga", {"app": "test"})
    assert data["nachtraeglich"] is False and data["anstoss"] == "2024-09-21T15:30"
    path = S.snapshot_path(tmp_path, "bundesliga", SEASON, 7)
    assert path.as_posix().endswith("schnappschuesse/bundesliga/2024-2025/7.json")
    S.write_once(path, data)
    snap = S.read(tmp_path, "bundesliga", SEASON, 7)
    assert snap.kpis == _kpis() and not snap.nachtraeglich and snap.meta["app"] == "test"
    other = S.snapshot_path(tmp_path, "bundesliga", SEASON, 8)
    S.write_once(other, {**data, "format": 99})
    assert S.read(tmp_path, "bundesliga", SEASON, 8) is None                    # unbekanntes Format: nicht lesen


# --- SN4–SN8: der stündliche Lauf ---------------------------------------------------------------------------

def _files(base):
    return sorted(p.relative_to(base / S.DIRNAME).as_posix() for p in (base / S.DIRNAME).rglob("*.json")
                  if p.name != S.STATUS_FILE)


def test_sn4_run_backfills_played_and_snapshots_next_hour(tmp_path, data_dir):
    from importer import schnappschuss as R
    base = tmp_path / "import"
    rep = R.run(base, data_dir, datetime(2024, 9, 21, 14, 31))
    assert rep["fehler"] is None, rep.get("details")
    # je Liga: Spieltag 1–3 nachträglich (mit Ergebnis), Spieltag 4 regulär (Anpfiff in der nächsten Stunde)
    assert (rep["neu"], rep["neu_nachtraeglich"], rep["ergebnisse_neu"], rep["wartend_anzahl"]) == (16, 12, 12, 0)
    assert "bundesliga/2024-2025/1004.json" in _files(base) and "bundesliga/2024-2025/1005.json" not in _files(base)
    snap = S.read(base, "bundesliga", SEASON, 1004)
    assert not snap.nachtraeglich and snap.kpis == _kpis()
    assert snap.meta["schwellen_berechnet"] and len(snap.meta["datenbank_sha256"]) == 64
    assert S.read(base, "bundesliga", SEASON, 1002).nachtraeglich
    assert S.first_result(base, "bundesliga", SEASON, 1002) == (2, 2)
    stand = R.load_status(base)
    assert stand["neu"] == 16 and stand["ligen"]["LaLiga"]["neu"] == 4
    rep = R.run(base, data_dir, datetime(2024, 9, 21, 15, 31))                   # zweiter Lauf: nichts Neues
    assert (rep["neu"], rep["vorhanden"], rep["ergebnisse_neu"]) == (0, 16, 0)


def test_sn5_too_early_and_without_kickoff_time(tmp_path, data_dir):
    from importer import schnappschuss as R
    base = tmp_path / "import"
    rep = R.run(base, data_dir, datetime(2024, 9, 21, 14, 29))                   # mehr als eine Stunde vor 15:30
    assert rep["neu"] == 12 and "bundesliga/2024-2025/1004.json" not in _files(base)
    # Spieltag 5 ohne Uhrzeit: Anstoss gilt als 23:59, Schnappschuss ab 22:59 am Spieltag
    rep = R.run(base, data_dir, datetime(2024, 9, 28, 22, 58))
    assert "bundesliga/2024-2025/1005.json" not in _files(base)
    assert rep["wartend_anzahl"] == 0


def test_sn6_waits_for_previous_result_then_late(tmp_path, data_dir):
    """Spieltag 5 wartet, solange das Ergebnis von Spieltag 4 fehlt; danach nachträglich."""
    from importer import schnappschuss as R
    base = tmp_path / "import"
    rep = R.run(base, data_dir, datetime(2024, 9, 28, 23, 0))
    assert rep["wartend_anzahl"] == 4 and "Bundesliga: Beta – Alpha (28.09.2024)" in rep["wartend"]
    assert "bundesliga/2024-2025/1005.json" not in _files(base)
    sheets = _db_sheets()                                                         # Ergebnis von Spieltag 4 kommt
    for name, n in LEAGUES:
        sheets[name] = pd.concat([sheets[name], pd.DataFrame(
            [make_match(n * 100 + 4, "Alpha", "Gamma", "2024-09-21", ft=(0, 1), ht=(0, 0), league=name, gameday=4)],
            columns=list(schema.EXPECTED_COLUMNS))], ignore_index=True)
    write_workbook(data_dir / "Database-Soccer-Intelligence.xlsx", sheets)
    rep = R.run(base, data_dir, datetime(2024, 9, 29, 10, 0))
    assert rep["wartend_anzahl"] == 0 and rep["neu"] == 4 and rep["neu_nachtraeglich"] == 4
    assert S.read(base, "bundesliga", SEASON, 1005).nachtraeglich
    assert S.first_result(base, "bundesliga", SEASON, 1004) == (0, 1)


def test_sn7_errors_in_data_create_nothing(tmp_path, data_dir):
    from importer import schnappschuss as R
    (data_dir / "Spielplan.xlsx").write_bytes(b"kaputt")
    rep = R.run(tmp_path / "import", data_dir, datetime(2024, 9, 21, 14, 31))
    assert rep["neu"] == 0 and rep["fehler"] and R.load_status(tmp_path / "import")["fehler"] == rep["fehler"]


def test_sn8_due_once_per_hour_and_after_takeover():
    from importer import schnappschuss as R
    assert R.due({}, datetime(2026, 11, 21, 14, 0, 20))
    assert not R.due({"letzter_schnappschuss": "2026-11-21T14"}, datetime(2026, 11, 21, 14, 59))
    assert R.due({"letzter_schnappschuss": "2026-11-21T14"}, datetime(2026, 11, 21, 15, 0, 5))
    assert R.due({"letzter_schnappschuss": None}, datetime(2026, 11, 21, 14, 59))   # nach einer Übernahme


# --- SN9–SN10: was die Seiten zeigen --------------------------------------------------------------------------

def _row(api_id=7, clock="15:30"):
    fx = A.prepare(pd.DataFrame([
        {"saison": SEASON, "spieltag": 3, "datum_von": date(2024, 9, 14), "datum_bis": date(2024, 9, 14),
         "heim": "Alpha", "gast": "Beta", "status": "geplant", "excel_row": 2, "reihenfolge": 0, "anstoss": "15:30",
         "termin": "bestätigt", "hinweis": "", "api_status": "FT", "api_id": 6},
        {"saison": SEASON, "spieltag": 4, "datum_von": date(2024, 9, 21), "datum_bis": date(2024, 9, 21),
         "heim": "Beta", "gast": "Alpha", "status": "geplant", "excel_row": 3, "reihenfolge": 1, "anstoss": clock,
         "termin": "bestätigt", "hinweis": "", "api_status": "NS", "api_id": api_id}]))
    return fx, list(fx.itertuples())[1]


def test_sn9_shown_values_before_and_after_kickoff(tmp_path):
    fx, row = _row()
    live, frozen = _kpis(), _kpis(day="2024-09-20")
    res = {(SEASON, "Alpha", "Beta"): (3, 1)}
    assert S.shown_values(tmp_path, "bundesliga", row, live, datetime(2024, 9, 21, 15, 29), res, fx) == \
        S.Shown(live, S.LIVE)
    after = datetime(2024, 9, 21, 15, 30)
    assert S.shown_values(tmp_path, "bundesliga", row, live, after, res, fx) == S.Shown(live, S.LATE)   # fehlt
    assert S.shown_values(tmp_path, "bundesliga", row, live, after, {}, fx).quelle == S.WAITING          # Vorspiel
    S.write_once(S.snapshot_path(tmp_path, "bundesliga", SEASON, 7),
                 S.payload(frozen, row, datetime(2024, 9, 21, 14, 31), "Bundesliga", {}))
    shown = S.shown_values(tmp_path, "bundesliga", row, live, after, res, fx)
    assert shown.kpis == frozen and shown.quelle == S.SNAPSHOT and not shown.korrigiert


def test_sn10_corrected_result(tmp_path):
    fx, row = _row()
    S.write_once(S.result_path(tmp_path, "bundesliga", SEASON, 7), {"ergebnis": [1, 0]})
    res = {(SEASON, "Alpha", "Beta"): (3, 1), (SEASON, "Beta", "Alpha"): (1, 0)}
    later = datetime(2024, 9, 22, 10, 0)
    assert not S.shown_values(tmp_path, "bundesliga", row, _kpis(), later, res, fx).korrigiert
    res[(SEASON, "Beta", "Alpha")] = (2, 0)                                       # Quelle korrigiert
    assert S.shown_values(tmp_path, "bundesliga", row, _kpis(), later, res, fx).korrigiert
    inactive = row._replace(status="verschoben")
    assert S.shown_values(tmp_path, "bundesliga", inactive, _kpis(), later, res, fx) == S.Shown(None, S.NONE)
