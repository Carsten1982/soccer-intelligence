"""Tests für Einlesen, Strukturprüfung und Plausibilität."""

import numpy as np
import pandas as pd
import pytest
from conftest import REAL_DATABASE, notes_for, write_workbook

from core import schema
from core.issues import FEHLER, HINWEIS, WARNUNG
from core.loader import load_database


def checks(db, level):
    return [i.check for i in db.issues if i.level == level]


# --- Gültige Datei -------------------------------------------------------

def test_valid_file_has_no_errors_or_warnings(tmp_path, valid_sheets):
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert not db.has_errors, db.issues
    assert checks(db, WARNUNG) == []
    assert set(db.leagues) == {"Bundesliga", "Premier League"}
    assert len(db.leagues["Bundesliga"]) == 2


def test_empty_optional_sheets_are_only_hints(tmp_path, valid_sheets):
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    empty = [i for i in db.issues if i.check == "Blatt leer"]
    assert {i.sheet for i in empty} == {"Seria A", "LaLiga"}
    assert all(i.level == HINWEIS for i in empty)


# --- Harte Fehler --------------------------------------------------------

def test_missing_file(tmp_path):
    db = load_database(tmp_path / "gibt-es-nicht.xlsx")
    assert db.has_errors and "Datei fehlt" in checks(db, FEHLER)


def test_corrupt_or_incomplete_file(tmp_path):
    path = tmp_path / "db.xlsx"
    path.write_bytes(b"PK\x03\x04 halb hochgeladen")
    db = load_database(path)
    assert db.has_errors and "Datei nicht lesbar" in checks(db, FEHLER)


def test_missing_required_sheet(tmp_path, valid_sheets):
    del valid_sheets["Premier League"]
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert "Blatt fehlt" in checks(db, FEHLER)


def test_required_sheet_empty(tmp_path, valid_sheets):
    valid_sheets["Bundesliga"] = pd.DataFrame()
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert "Blatt leer" in checks(db, FEHLER)


def test_57_columns_one_missing(tmp_path, valid_sheets):
    valid_sheets["Bundesliga"] = valid_sheets["Bundesliga"].drop(columns=["referee"])
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert "Spaltenstruktur" in checks(db, FEHLER)
    assert "Bundesliga" not in db.leagues


def test_swapped_column_order(tmp_path, valid_sheets):
    cols = list(schema.EXPECTED_COLUMNS)
    cols[9], cols[10] = cols[10], cols[9]
    valid_sheets["Bundesliga"] = valid_sheets["Bundesliga"][cols]
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    msg = [i.message for i in db.issues if i.check == "Spaltenstruktur"]
    assert msg and "reihenfolge" in msg[0] and "Spalte 10" in msg[0]


def test_duplicate_id(tmp_path, valid_sheets):
    valid_sheets["Bundesliga"].loc[1, "id"] = 1
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert "Doppelte id" in checks(db, FEHLER)


def test_text_instead_of_number(tmp_path, valid_sheets):
    df = valid_sheets["Bundesliga"]
    df["Home Corners Full Time"] = df["Home Corners Full Time"].astype(object)
    df.loc[0, "Home Corners Full Time"] = "fünf"
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert "Keine Zahl" in checks(db, FEHLER)


def test_required_field_empty(tmp_path, valid_sheets):
    valid_sheets["Bundesliga"].loc[0, "homeTeam"] = None
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert "Pflichtfeld leer" in checks(db, FEHLER)


def test_invalid_result_letter(tmp_path, valid_sheets):
    valid_sheets["Bundesliga"].loc[0, "Full-Time Result"] = "X"
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert "Ungültiges Ergebnis" in checks(db, FEHLER)


# --- Warnungen -----------------------------------------------------------

def test_ft_differs_from_full_time(tmp_path, valid_sheets):
    """Entspricht dem Fehler vom 18.10.2025 in der Premier League."""
    df = valid_sheets["Premier League"]
    df.loc[0, ["Full-Time Home Goals", "Full-Time Away Goals", "Full-Time Result"]] = [3, 3, "D"]
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert not db.has_errors
    assert "FT ≠ Full-Time" in checks(db, WARNUNG)
    assert "Halbzeiten ≠ Endstand" in checks(db, WARNUNG)


def test_possession_not_100(tmp_path, valid_sheets):
    valid_sheets["Bundesliga"].loc[0, "Home Ball Possession Full Time"] = 60
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert "Ballbesitz ≠ 100 %" in checks(db, WARNUNG)


def test_corner_halves_do_not_sum(tmp_path, valid_sheets):
    valid_sheets["Bundesliga"].loc[0, "Home Corners Full Time"] = 9
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert "Ecken: Halbzeiten ≠ Gesamt" in checks(db, WARNUNG)


def test_incomplete_older_season(tmp_path, valid_sheets):
    df = valid_sheets["Bundesliga"]
    extra = df.copy()
    extra["Season"] = "2025/2026"
    extra["id"] = [3, 4]
    df = pd.concat([df.iloc[[0]], extra], ignore_index=True)  # 2024/25 nur 1 von 2 Spielen
    valid_sheets["Bundesliga"] = df
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert "Saison unvollständig" in checks(db, WARNUNG)


# --- Fehlende Statistik: leer bleibt leer, nie 0 -------------------------

def _blank_stats(sheets):
    df = sheets["Bundesliga"]
    for c in schema.STAT_COLUMNS:
        df[c] = df[c].astype(float)
        df.loc[0, c] = np.nan
    return sheets


def test_missing_stats_stay_empty_not_zero(tmp_path, valid_sheets):
    db = load_database(write_workbook(tmp_path / "db.xlsx", _blank_stats(valid_sheets)))
    assert not db.has_errors
    df = db.leagues["Bundesliga"]
    row = df[df["id"] == 1].iloc[0]
    assert all(pd.isna(row[c]) for c in schema.STAT_COLUMNS)
    # Durchschnitt nutzt nur das Spiel mit Daten (5), nicht (0 + 5) / 2
    assert df["Home Corners Full Time"].mean() == 5
    # Keine falschen Warnungen durch leere Werte
    assert "Ballbesitz ≠ 100 %" not in checks(db, WARNUNG)
    assert not any("Halbzeiten ≠ Gesamt" in c for c in checks(db, WARNUNG))


def test_undocumented_missing_stats_warn(tmp_path, valid_sheets):
    db = load_database(write_workbook(tmp_path / "db.xlsx", _blank_stats(valid_sheets)))
    assert "Statistik fehlt" in checks(db, WARNUNG)


def test_documented_missing_stats_are_hint(tmp_path, valid_sheets):
    path = write_workbook(tmp_path / "db.xlsx", _blank_stats(valid_sheets), notes_for("Bundesliga", 1))
    db = load_database(path)
    assert "Statistik fehlt" in checks(db, HINWEIS)
    assert "Statistik fehlt" not in checks(db, WARNUNG)


def test_note_for_unknown_match_warns(tmp_path, valid_sheets):
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets, notes_for("Bundesliga", 999)))
    assert "Hinweis ohne Spiel" in checks(db, WARNUNG)


# --- Datei wird ersetzt -> neuer Stand -----------------------------------

def test_reload_after_file_replaced(tmp_path, valid_sheets):
    path = write_workbook(tmp_path / "db.xlsx", valid_sheets)
    first = load_database(path)
    valid_sheets["Bundesliga"].loc[1, "awayTeam"] = "Gamma"
    write_workbook(path, valid_sheets)
    second = load_database(path)
    assert first.sha256 != second.sha256
    assert "Gamma" in set(second.leagues["Bundesliga"]["awayTeam"])


# --- Echte Datenbank -----------------------------------------------------

@pytest.mark.skipif(not REAL_DATABASE.exists(), reason="echte Datenbank nicht vorhanden")
def test_real_database():
    db = load_database(REAL_DATABASE)
    assert not db.has_errors, [i for i in db.issues if i.level == FEHLER]
    assert len(db.leagues["Bundesliga"]) == 1836
    assert len(db.leagues["Premier League"]) == 2280
    bl = db.leagues["Bundesliga"]
    union = bl[bl["id"] == 14421].iloc[0]
    assert (union["homeTeam"], union["awayTeam"]) == ("Union Berlin", "Bochum")
    assert (union["Full-Time Home Goals"], union["Full-Time Away Goals"]) == (1, 1)
    assert all(pd.isna(union[c]) for c in schema.STAT_COLUMNS)
    # Einzige bekannte Warnung: Schusssumme bei id 11344
    assert {i.match_id for i in db.issues if i.level == WARNUNG} <= {11344}
    # Korrigierte Premier-League-Spiele vom 18.10.2025
    pl = db.leagues["Premier League"].set_index("id")
    assert tuple(pl.loc[67161, ["First-Half Home Goals", "First-Half Away Goals"]]) == (0, 0)
    assert tuple(pl.loc[67160, ["Full-Time Home Goals", "Full-Time Away Goals"]]) == (3, 3)


# --- Spalte Gameday (Grundlage der Ligareferenz) ---------------------------

def test_gameday_text_is_error(tmp_path, valid_sheets):
    valid_sheets["Premier League"]["Gameday"] = valid_sheets["Premier League"]["Gameday"].astype(object)
    valid_sheets["Premier League"].loc[0, "Gameday"] = "bitte"
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert db.has_errors


def test_gameday_empty_is_error(tmp_path, valid_sheets):
    valid_sheets["Bundesliga"].loc[0, "Gameday"] = np.nan
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert db.has_errors


def test_gameday_out_of_range_is_warning(tmp_path, valid_sheets):
    valid_sheets["Bundesliga"].loc[1, "Gameday"] = 3   # 2 Teams -> nur Spieltage 1–2
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert not db.has_errors
    assert "Gameday ausserhalb Bereich" in checks(db, WARNUNG)


def test_gameday_team_twice_is_warning(tmp_path, valid_sheets):
    valid_sheets["Bundesliga"].loc[1, "Gameday"] = 1
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    w = checks(db, WARNUNG)
    assert "Team mehrfach im Spieltag" in w and "Spieltag unvollständig" in w
