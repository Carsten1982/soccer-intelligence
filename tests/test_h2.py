"""Tests zu H.2 (Stabilität, Version 0.9.2): unerwartete Inhalte in Konfiguration und Excel-Dateien führen zu
einer klaren Meldung statt zu einem Absturz oder zu still falschen Werten. Befunde S1–S6 der zweiten Code-Prüfung."""

import hashlib
import os

import numpy as np
import pandas as pd
import pytest
from conftest import notes_for, valid_league, write_workbook

from core import files, loader
from core.config import ConfigError, load_leagues, load_teams
from core.issues import FEHLER, HINWEIS, WARNUNG
from core.loader import load_database
from core.rows import id_text, valid_id
from core.thresholds import load_thresholds


def sheets():
    return {name: valid_league(name) for name in ("Bundesliga", "Premier League", "Serie A", "LaLiga")}


def checks(db, level):
    return [i.check for i in db.issues if i.level == level]


# --- S1: TOML mit falscher Struktur -> klare Meldung -----------------------------------------

@pytest.mark.parametrize("text", ["liga = 1\n", "liga = [1]\n", 'liga = "Bundesliga"\n'])
def test_leagues_wrong_structure(tmp_path, text):
    (tmp_path / "ligen.toml").write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError, match=r"\[\[liga\]\]"):
        load_leagues(tmp_path / "ligen.toml")


@pytest.mark.parametrize("text", ["team = 1\n", "team = [1]\n"])
def test_teams_wrong_structure(tmp_path, text):
    (tmp_path / "teams.toml").write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError, match=r"\[\[team\]\]"):
        load_teams(tmp_path / "teams.toml")


@pytest.mark.parametrize("text, message", [
    ("standard = 35\n", "muss ein Abschnitt"),
    ("abweichung = 1\n[standard]\nleicht = 20\nstark = 35\n", r"\[\[abweichung\]\]"),
    ("abweichung = [1]\n[standard]\nleicht = 20\nstark = 35\n", r"\[\[abweichung\]\]"),
])
def test_thresholds_wrong_structure(tmp_path, text, message):
    (tmp_path / "schwellen.toml").write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError, match=message):
        load_thresholds(tmp_path / "schwellen.toml", ["Bundesliga"])


def test_config_is_a_folder(tmp_path):
    (tmp_path / "ligen.toml").mkdir()
    with pytest.raises(ConfigError, match="nicht lesbar"):
        load_leagues(tmp_path / "ligen.toml")


# --- S2: Zahl statt Datum -> Fehler statt still 1970 ------------------------------------------

def test_number_in_date_column_is_error(tmp_path):
    s = sheets()
    s["Bundesliga"]["Date"] = s["Bundesliga"]["Date"].astype(object)
    s["Bundesliga"].loc[0, "Date"] = 45800
    db = load_database(write_workbook(tmp_path / "db.xlsx", s))
    msgs = [i.message for i in db.issues if i.level == FEHLER and i.check == "Ungültiges Datum"]
    assert msgs and "45800" in msgs[0]
    assert "Bundesliga" not in db.leagues                      # kein Spiel mit Datum 1970


def test_real_dates_still_accepted(tmp_path):
    db = load_database(write_workbook(tmp_path / "db.xlsx", sheets()))
    assert not db.has_errors
    assert db.leagues["Bundesliga"]["Date"].iloc[0] == pd.Timestamp("2024-08-24")


# --- S3/S4: ungültige ids -> kein Absturz, nie abschneiden ------------------------------------

@pytest.mark.parametrize("value, expected", [
    (123, 123), (123.0, 123), ("123", 123), (123.5, None), (float("inf"), None), (float("-inf"), None),
    (float("nan"), None), ("abc", None), (None, None), (pd.NA, None),
])
def test_valid_id(value, expected):
    assert valid_id(value) == expected


def test_id_text():
    assert id_text(14421.0) == "14421" and id_text(float("inf")) == "inf" and id_text(1.5) == "1.5"


@pytest.mark.parametrize("value", ["inf", "-inf", 1.5])
def test_invalid_match_id_is_error_without_crash(tmp_path, value):
    s = sheets()
    s["Bundesliga"]["id"] = s["Bundesliga"]["id"].astype(object)
    s["Bundesliga"].loc[0, "id"] = value
    db = load_database(write_workbook(tmp_path / "db.xlsx", s))
    assert "Keine ganze Zahl" in checks(db, FEHLER)
    assert all(i.match_id is None for i in db.issues if i.check == "Keine ganze Zahl")


def test_duplicate_infinite_ids_without_crash(tmp_path):
    s = sheets()
    s["Bundesliga"]["id"] = ["inf", "inf"]
    db = load_database(write_workbook(tmp_path / "db.xlsx", s))
    assert "Doppelte id" in checks(db, FEHLER)


def test_note_with_decimal_id_documents_no_match(tmp_path):
    """Datenhinweis mit id 1,5: Spiel 1 gilt nicht als dokumentiert (vorher wurde 1,5 zu 1)."""
    s = sheets()
    for c in ("Home Corners Full Time", "Away Corners Full Time"):
        s["Bundesliga"][c] = s["Bundesliga"][c].astype(float)
        s["Bundesliga"].loc[0, c] = np.nan
    db = load_database(write_workbook(tmp_path / "db.xlsx", s, notes_for("Bundesliga", 1.5)))
    assert "Statistik fehlt" in checks(db, WARNUNG) and "Statistik fehlt" not in checks(db, HINWEIS)
    assert "Hinweis ohne Spiel" in checks(db, WARNUNG)


# --- S5: Zwischenspeicher erkennt ersetzte Datei ----------------------------------------------

def test_file_key_detects_replacement_with_same_size_and_time(tmp_path):
    path = tmp_path / "db.xlsx"
    path.write_bytes(b"A" * 100)
    before = path.stat()
    key = files.file_key(path)
    replacement = tmp_path / "neu.xlsx"
    replacement.write_bytes(b"B" * 100)                               # gleiche Grösse, anderer Inhalt
    os.replace(replacement, path)                                     # so ersetzt auch WinSCP eine Datei
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))       # alte Änderungszeit wiederhergestellt
    assert path.stat().st_size == before.st_size and path.stat().st_mtime_ns == before.st_mtime_ns
    assert files.file_key(path) != key


def test_file_key_missing_file(tmp_path):
    assert files.file_key(tmp_path / "fehlt.xlsx") == (0, 0, 0, 0)


# --- S6: Datei nur einmal lesen ----------------------------------------------------------------

def test_hash_and_content_from_the_same_read(tmp_path, monkeypatch):
    """Wird die Datei während des Einlesens ersetzt, gehören Prüfsumme und Daten trotzdem zum selben Stand."""
    old_path = write_workbook(tmp_path / "alt.xlsx", sheets())
    s = sheets()
    s["Bundesliga"].loc[1, "awayTeam"] = "Gamma"
    path = write_workbook(tmp_path / "db.xlsx", s)                    # Stand auf der Festplatte: „Gamma“
    old = files.read_file(old_path)
    monkeypatch.setattr(loader, "read_file", lambda p: old)           # gelesen wurde aber noch der alte Stand
    db = load_database(path)
    assert db.sha256 == hashlib.sha256(old.data).hexdigest() and db.file_size == len(old.data)
    assert "Gamma" not in set(db.leagues["Bundesliga"]["awayTeam"])


def test_file_disappears_while_loading(tmp_path, monkeypatch):
    path = write_workbook(tmp_path / "db.xlsx", sheets())

    def gone(p):
        raise FileNotFoundError(2, "No such file or directory", str(p))
    monkeypatch.setattr(loader, "read_file", gone)
    db = load_database(path)
    assert db.has_errors and "Datei nicht lesbar" in checks(db, FEHLER)


def test_read_file_matches_disk(tmp_path):
    path = write_workbook(tmp_path / "db.xlsx", sheets())
    content = files.read_file(path)
    assert content.data == path.read_bytes() and content.sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
