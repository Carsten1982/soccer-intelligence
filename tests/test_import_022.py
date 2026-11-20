"""Version 0.22: Lauf nach jedem Spiel, Wiederholung, Übernahme ohne Freigabe, gestaffelte Backups.

Spezifikation `docs/06_Datenlieferung.md`, Abschnitt 10.2 (Beschlüsse Carsten 20.11.2026, F1–F3).
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta

import openpyxl
import pytest

from importer import dienst, laufplan
from importer import einstellungen as E
from importer.erzeugen import _automatic
from importer.spielplan import COLUMNS


def _spielplan(path, spiele):
    """Spielplan.xlsx mit einem Blatt: spiele = [(tag, "HH:MM", status, termin), …]."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bundesliga"
    ws.append(COLUMNS)
    for i, (tag, zeit, status, termin) in enumerate(spiele):
        row = {c: None for c in COLUMNS}
        row.update({"Saison": "2026/27", "Spieltag": 12, "Datum von": tag, "Datum bis": tag, "Heimmannschaft": f"H{i}",
                    "Gastmannschaft": f"G{i}", "Status": status, "Anstoss": zeit, "Termin": termin})
        ws.append([row[c] for c in COLUMNS])
    wb.save(path)
    return path


SA = date(2026, 11, 21)


# --- L1 Laufzeiten -------------------------------------------------------------------------------------------------

def test_l1_run_times_example_saturday():
    """Beispiel der Spezifikation: Samstag 21.11.2026, 10 Anstosszeiten → 8 Läufe."""
    anstoesse = [datetime.combine(SA, datetime.strptime(z, "%H:%M").time()) for z in
                 ("13:30", "14:00", "15:00", "15:30", "16:00", "16:15", "18:00", "18:30", "20:45", "21:00")]
    zeiten = [z.strftime("%H:%M") for z in laufplan.laufzeiten(anstoesse)]
    assert zeiten == ["15:45", "16:15", "17:15", "17:45", "18:30", "20:15", "20:45", "23:15"]


def test_l1_no_run_in_control_hour_and_after_midnight(tmp_path):
    """Lauf in der Stunde 04:00 entfällt; ein Spiel um 22:00 ergibt einen Lauf am Folgetag um 00:15."""
    assert laufplan.laufzeiten([datetime(2026, 11, 21, 2, 0)]) == []
    fx = _spielplan(tmp_path / "Spielplan.xlsx", [(SA, "22:00", None, "bestätigt")])
    assert laufplan.plan(fx, SA) == []
    assert laufplan.plan(fx, SA + timedelta(days=1)) == [datetime(2026, 11, 22, 0, 15)]


def test_l1_only_planned_games_with_time(tmp_path):
    """Verschobene Spiele und „Zeit offen“ lösen keinen Lauf aus; „vorläufig“ schon."""
    fx = _spielplan(tmp_path / "Spielplan.xlsx", [
        (SA, "15:30", None, "bestätigt"), (SA, "18:30", "verschoben", "bestätigt"),
        (SA, "15:30", None, "Zeit offen"), (SA, "20:30", None, "vorläufig")])
    assert [z.strftime("%H:%M") for z in laufplan.plan(fx, SA)] == ["17:45", "22:45"]


# --- L2 Fälligkeit und Wiederholung ----------------------------------------------------------------------------------

def test_l2_due_once_and_missed_runs_merge(tmp_path):
    """Fällig ab der Laufzeit, einmal; nach einem Neustart wird der späteste verpasste Lauf nachgeholt (bis 6 h)."""
    fx = _spielplan(tmp_path / "Spielplan.xlsx", [(SA, "15:30", None, "bestätigt"), (SA, "18:30", None, "bestätigt")])
    state = {}
    assert laufplan.faellig(state, datetime(2026, 11, 21, 17, 44), fx) is None
    assert laufplan.faellig(state, datetime(2026, 11, 21, 21, 0), fx) == datetime(2026, 11, 21, 20, 45)
    laufplan.erledigt(state, datetime(2026, 11, 21, 21, 0), fx)
    assert laufplan.faellig(state, datetime(2026, 11, 21, 21, 1), fx) is None
    assert laufplan.faellig({}, datetime(2026, 11, 22, 3, 0), fx) is None          # älter als 6 h: Kontrolllauf


def test_l2_retry_at_most_twice():
    now = datetime(2026, 11, 21, 17, 45)
    offen = {"status": "übernommen (automatisch)", "offen": [{"datum": "21.11.2026"}]}
    state = {}
    laufplan.wiederholung_planen(state, offen, now, "spiel")
    assert state["wiederholung"] == {"um": "2026-11-21T18:45:00", "nr": 1}
    assert not laufplan.wiederholung_faellig(state, datetime(2026, 11, 21, 18, 44))
    assert laufplan.wiederholung_faellig(state, datetime(2026, 11, 21, 18, 45))
    laufplan.wiederholung_planen(state, offen, datetime(2026, 11, 21, 18, 45), "wiederholung")
    assert state["wiederholung"]["nr"] == 2
    laufplan.wiederholung_planen(state, offen, datetime(2026, 11, 21, 19, 45), "wiederholung")
    assert state["wiederholung"] is None                                            # höchstens zwei
    laufplan.wiederholung_planen(state, {"status": "fehlgeschlagen"}, now, "spiel")
    assert state["wiederholung"]["nr"] == 1                                         # neuer Lauf: neu zählen
    laufplan.wiederholung_planen(state, {"status": "übernommen (automatisch)", "offen": [{"datum": "10.11.2026"}]},
                                 now, "spiel")
    assert state["wiederholung"] is None                                            # altes offenes Spiel: Kontrolllauf


def test_l2_service_picks_control_before_game_before_retry(tmp_path, monkeypatch):
    base, data = tmp_path / "import", tmp_path / "data"
    base.mkdir(), data.mkdir()
    _spielplan(data / "Spielplan.xlsx", [(SA, "15:30", None, "bestätigt")])
    tz = dienst.ZoneInfo(E.TIMEZONE)
    dienst.save_state(base, {"letzter_lauf_tag": "2026-11-21", "wiederholung": {"um": "2026-11-21T17:00:00", "nr": 1}})
    assert dienst.naechster(base, data, datetime(2026, 11, 21, 17, 50, tzinfo=tz)) == "spiel"
    assert dienst.naechster(base, data, datetime(2026, 11, 22, 4, 0, tzinfo=tz)) == "kontrolle"
    calls = []
    monkeypatch.setattr(dienst, "run", lambda b, d, now, client=None, anlass="": calls.append(anlass) or
                        {"lauf": "x", "status": "übernommen (automatisch)", "offen": [{"datum": "21.11.2026"}]})
    dienst.run_planned(base, data, datetime(2026, 11, 21, 17, 50, tzinfo=tz), "spiel")
    state = dienst.load_state(base)
    assert calls == ["spiel"] and "2026-11-21T17:45" in state["spiel_laeufe"]
    assert state["wiederholung"] == {"um": "2026-11-21T18:50:00", "nr": 1}
    assert dienst.naechster(base, data, datetime(2026, 11, 21, 18, 0, tzinfo=tz)) is None
    assert dienst.naechster(base, data, datetime(2026, 11, 21, 18, 50, tzinfo=tz)) == "wiederholung"


# --- L3 Übernahme ohne Freigabe (B2, F1) ----------------------------------------------------------------------------

def test_l3_automatic_mode_active_in_config():
    import tomllib
    cfg = tomllib.loads(E.CONFIG_FILE.read_text(encoding="utf-8"))
    assert cfg["automatisch_ab"] == date(2026, 11, 20)


def test_l3_critical_points_no_longer_block_errors_and_warnings_do():
    """F1: kritische Spiele sind schon zurückgehalten und sperren die Fassung nicht mehr."""
    rep = {"fehler": 0, "kritisch": [{"art": "endstand"}], "plausibilitaet": {"warnungen": []}}
    assert _automatic(rep, [])["ok"] is True
    assert _automatic({**rep, "fehler": 1}, [])["ok"] is False
    assert _automatic({**rep, "plausibilitaet": {"warnungen": [{}]}}, [])["ok"] is False
    assert _automatic(rep, [{"meldung": "neu"}])["ok"] is False


def test_l3_event_log(tmp_path):
    dienst.event(tmp_path, {"lauf": "a", "anlass": "spiel"})
    dienst.event(tmp_path, {"lauf": "b", "anlass": "kontrolle"})
    zeilen = [json.loads(z) for z in (tmp_path / dienst.EVENTS).read_text(encoding="utf-8").splitlines()]
    assert [z["anlass"] for z in zeilen] == ["spiel", "kontrolle"]


# --- L4 Backups (Regel 7) -------------------------------------------------------------------------------------------

def test_l4_backup_tiers():
    heute = date(2027, 3, 15)
    alle = [datetime(2025, 6, 28, 4), datetime(2025, 6, 30, 23)]                    # Saison 2024/25
    alle += [datetime(2026, 2, 1, 4), datetime(2026, 2, 27, 4)]                     # über 12 Monate alt
    alle += [datetime(2026, 6, 29, 4)]                                              # Saisonende 2025/26
    alle += [datetime(2026, 8, 3, 4), datetime(2026, 8, 30, 4)]                     # Monat 08/2026
    alle += [datetime(2027, 1, 4, 4), datetime(2027, 1, 6, 4)]                      # gleiche Woche (KW 1)
    alle += [datetime(2027, 3, 2, 4), datetime(2027, 3, 3, 4)]                      # 12–13 Tage alt
    keep = laufplan.behalten(alle, heute)
    assert datetime(2025, 6, 30, 23) in keep and datetime(2025, 6, 28, 4) not in keep   # Saisonende dauerhaft
    assert datetime(2026, 2, 27, 4) not in keep and datetime(2026, 2, 1, 4) not in keep
    assert datetime(2026, 6, 29, 4) in keep
    assert datetime(2026, 8, 30, 4) in keep and datetime(2026, 8, 3, 4) not in keep      # je Monat das letzte
    assert datetime(2027, 1, 6, 4) in keep and datetime(2027, 1, 4, 4) not in keep        # je Woche das letzte
    assert {datetime(2027, 3, 2, 4), datetime(2027, 3, 3, 4)} <= keep                     # 14 Tage alle


def test_l4_prune_files_only_known_names(tmp_path):
    for stamp in ("2026-01-05_040000", "2026-01-06_040000", "2027-03-14_040000"):
        (tmp_path / f"Spielplan_{stamp}_lauf-x_vor_import.xlsx").write_text("x")
    (tmp_path / "Spielplan_handarbeit.xlsx").write_text("x")
    weg = laufplan.backups_aufraeumen(tmp_path, [("Spielplan", ".xlsx")], date(2027, 3, 15))
    namen = sorted(p.name for p in tmp_path.iterdir())
    assert weg == 1 and "Spielplan_2026-01-05_040000_lauf-x_vor_import.xlsx" not in namen
    assert "Spielplan_handarbeit.xlsx" in namen and "Spielplan_2027-03-14_040000_lauf-x_vor_import.xlsx" in namen


@pytest.mark.parametrize("anlass,erwartet", [("kontrolle", True), ("spiel", False), ("wiederholung", False)])
def test_l5_game_runs_skip_recheck_and_full_season(tmp_path, monkeypatch, anlass, erwartet):
    """Läufe nach dem Spiel holen nur neue Spiele und fehlende Werte (recheck=False), nie die ganze Saison."""
    gesehen = {}

    def fake_build(*args, **kw):
        gesehen.update(full=args[7], recheck=kw.get("recheck"))
        raise dienst.ImportFehler("Test")
    monkeypatch.setattr(dienst, "build", fake_build)
    monkeypatch.setattr(dienst, "load_team_names", lambda p: None)
    monkeypatch.setattr(dienst, "load_leagues", lambda: [])

    class Client:
        used, remaining = 0, None
    mon = datetime(2026, 11, 23, 4, 0, tzinfo=dienst.ZoneInfo(E.TIMEZONE))           # Montag
    rep = dienst.run(tmp_path / "import", tmp_path / "data", mon, client=Client(), anlass=anlass)
    assert rep["status"] == "fehlgeschlagen" and rep["anlass"] == anlass
    assert gesehen == {"full": erwartet, "recheck": erwartet}
    state = dienst.load_state(tmp_path / "import")
    assert (state.get("letzter_lauf_tag") == "2026-11-23") is erwartet                # nur der Kontrolllauf zählt


# --- L6 Nachprüfung 20.11.2026 ----------------------------------------------------------------------------------------

def test_l6_fresh_game_warnings_do_not_block():
    """Befund 1: „Statistik fehlt“ und „Spieltag unvollständig“ sind direkt nach dem Spiel normal und sperren nicht
    (Regel 5); andere neue Warnungen weiterhin."""
    from importer.erzeugen import NICHT_SPERREND
    assert NICHT_SPERREND == {"Statistik fehlt", "Spieltag unvollständig"}
    import inspect
    from importer import erzeugen
    assert "w[\"pruefung\"] not in NICHT_SPERREND" in inspect.getsource(erzeugen.build)


def test_l6_not_finished_games_trigger_retry():
    """Befund 2: Ein Spiel, das beim Lauf noch läuft oder verspätet ist, löst die Wiederholung aus."""
    from importer.erzeugen import _not_finished
    tz = dienst.ZoneInfo(E.TIMEZONE)
    jetzt = datetime(2026, 11, 21, 17, 45, tzinfo=tz)

    def fx(fid, short, hh):
        return {"fixture": {"id": fid, "status": {"short": short}, "date": f"2026-11-21T{hh}:00+01:00"},
                "teams": {"home": {"name": "A"}, "away": {"name": "B"}}}
    lst = [fx(1, "FT", "15:30"), fx(2, "ET", "15:30"), fx(3, "NS", "15:30"), fx(4, "NS", "18:30"), fx(5, "TBD", "00:00")]
    assert [x["id"] for x in _not_finished(lst, "Bundesliga", jetzt)] == [2, 3]
    assert _not_finished(lst, "Bundesliga", None) == []
    state = {}
    laufplan.wiederholung_planen(state, {"status": "übernommen (automatisch)", "nicht_beendet": [{"id": 2}]},
                                 jetzt.replace(tzinfo=None), "spiel")
    assert state["wiederholung"]["nr"] == 1
