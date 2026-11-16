"""Tests für Einlesen, Strukturprüfung und Plausibilität."""

import numpy as np
import pandas as pd
import pytest
from conftest import (
    KNOWN_DB_SHA, REAL_DATABASE, REFERENCE_DATABASE, break_xml, make_match, notes_for, write_workbook,
)

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
    assert set(db.leagues) == {"Bundesliga", "Premier League", "Serie A", "LaLiga"}
    assert len(db.leagues["Bundesliga"]) == 2


def test_all_four_league_sheets_are_required(tmp_path, valid_sheets):
    """Seit Etappe F sind Serie A und LaLiga aktiv und damit Pflicht (leer oder fehlend = Fehler)."""
    valid_sheets["LaLiga"] = pd.DataFrame()
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert ("LaLiga", "Blatt leer") in {(i.sheet, i.check) for i in db.issues if i.level == FEHLER}


def test_old_sheet_name_seria_a(tmp_path, valid_sheets):
    """Altes Blatt „Seria A“: wird ignoriert (Hinweis), „Serie A“ fehlt dann (Fehler)."""
    valid_sheets["Seria A"] = valid_sheets.pop("Serie A")
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert ("Serie A", "Blatt fehlt") in {(i.sheet, i.check) for i in db.issues if i.level == FEHLER}
    assert ("Seria A", "Unbekanntes Blatt") in {(i.sheet, i.check) for i in db.issues if i.level == HINWEIS}


def test_league_column_must_match_sheet(tmp_path, valid_sheets):
    """Spalte League passt nicht zum Blattnamen -> Warnung (gilt jetzt auch für Serie A)."""
    valid_sheets["Serie A"]["League"] = "Seria A"
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert ("Serie A", "Liga ≠ Blattname") in {(i.sheet, i.check) for i in db.issues if i.level == WARNUNG}


# --- Harte Fehler --------------------------------------------------------

def test_missing_file(tmp_path):
    db = load_database(tmp_path / "gibt-es-nicht.xlsx")
    assert db.has_errors and "Datei fehlt" in checks(db, FEHLER)


def test_corrupt_or_incomplete_file(tmp_path):
    path = tmp_path / "db.xlsx"
    path.write_bytes(b"PK\x03\x04 halb hochgeladen")
    db = load_database(path)
    assert db.has_errors and "Datei nicht lesbar" in checks(db, FEHLER)


def test_broken_xml_inside_file(tmp_path, valid_sheets):
    """Gültiges ZIP, aber kaputtes XML: klare Meldung statt Absturz (H.1, Punkt R2)."""
    db = load_database(break_xml(write_workbook(tmp_path / "db.xlsx", valid_sheets)))
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


@pytest.mark.parametrize("col", ["FT Home Goals", "Gameday", "id"])
def test_decimal_in_goals_gameday_id_is_error(tmp_path, valid_sheets, col):
    """Kommazahl bei Toren, Spieltag oder id: Fehler, nie abschneiden (H.1, Punkt R4)."""
    df = valid_sheets["Bundesliga"]
    df[col] = df[col].astype(float)
    df.loc[0, col] = 1.5
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert "Keine ganze Zahl" in checks(db, FEHLER)
    assert "Bundesliga" not in db.leagues


def test_decimal_in_count_stat_is_warning_and_missing(tmp_path, valid_sheets):
    """Kommazahl bei Ecken/Karten/Schüssen: Warnung, der Wert gilt als fehlend (nie abgeschnitten, nie 0)."""
    df = valid_sheets["Bundesliga"]
    df["Home Corners Full Time"] = df["Home Corners Full Time"].astype(float)
    df.loc[0, "Home Corners Full Time"] = 4.5
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert not db.has_errors
    msgs = [i.message for i in db.issues if i.level == WARNUNG and i.check == "Keine ganze Zahl"]
    assert len(msgs) == 1 and "Home Corners Full Time" in msgs[0] and "4.5" in msgs[0]
    bl = db.leagues["Bundesliga"].set_index("id")
    assert pd.isna(bl.loc[1, "Home Corners Full Time"]) and bl.loc[2, "Home Corners Full Time"] == 5


def test_negative_stat_is_warning_and_missing(tmp_path, valid_sheets):
    """0.15.1 (F3, Carsten 16.11.2026): negativer Statistikwert -> Warnung, gilt als fehlend und geht nicht in die KPIs."""
    df = valid_sheets["Bundesliga"]
    df.loc[0, "Home Corners Full Time"] = -3
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert not db.has_errors
    msgs = [i.message for i in db.issues if i.level == WARNUNG and i.check == "Negativer Wert"]
    assert len(msgs) == 1 and "wird als fehlender Wert behandelt" in msgs[0]
    bl = db.leagues["Bundesliga"].set_index("id")
    assert pd.isna(bl.loc[1, "Home Corners Full Time"]) and bl.loc[2, "Home Corners Full Time"] == 5


def test_negative_goals_are_error(tmp_path, valid_sheets):
    """0.15.1 (F3): negative Tore sind ein Fehler (bisher nur eine Warnung) – die Datenbank wird nicht verwendet."""
    df = valid_sheets["Bundesliga"]
    df.loc[0, "Second-Half Home Goals"] = -1
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert "Negativer Wert" in checks(db, FEHLER) and db.has_errors


def test_decimal_possession_is_allowed(tmp_path, valid_sheets):
    """Ballbesitz in Prozent darf Kommastellen haben."""
    df = valid_sheets["Bundesliga"]
    for side, value in (("Home", 55.5), ("Away", 44.5)):
        df[f"{side} Ball Possession Full Time"] = df[f"{side} Ball Possession Full Time"].astype(float)
        df.loc[0, f"{side} Ball Possession Full Time"] = value
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets))
    assert "Keine ganze Zahl" not in checks(db, WARNUNG) + checks(db, FEHLER)
    assert db.leagues["Bundesliga"].iloc[0]["Home Ball Possession Full Time"] == 55.5


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


def test_notes_without_liga_column_do_not_crash(tmp_path, valid_sheets):
    """Blatt Datenhinweise ohne Spalte Liga: Warnung zur Spaltenstruktur, kein Absturz (H.1, Punkt R1)."""
    notes = notes_for("Bundesliga", 1).drop(columns=["Liga"])
    db = load_database(write_workbook(tmp_path / "db.xlsx", _blank_stats(valid_sheets), notes))
    assert ("Datenhinweise", "Spaltenstruktur") in {(i.sheet, i.check) for i in db.issues if i.level == WARNUNG}
    assert "Statistik fehlt" in checks(db, WARNUNG)          # nichts gilt als dokumentiert


def test_missing_stats_messages_are_limited(tmp_path, valid_sheets):
    """Viele Spiele ohne Statistik: je Stufe höchstens 50 Einzelmeldungen plus eine Sammelzeile (H.1, Punkt R8)."""
    games = [make_match(i, f"T{i}", f"U{i}", "2024-08-24") for i in range(1, 62)]   # 61 Spiele
    df = pd.DataFrame(games, columns=list(schema.EXPECTED_COLUMNS))
    for c in schema.STAT_COLUMNS:
        df[c] = np.nan
    valid_sheets["Bundesliga"] = df
    notes = pd.concat([notes_for("Bundesliga", i) for i in (1, 2, 3)], ignore_index=True)   # 3 dokumentiert
    db = load_database(write_workbook(tmp_path / "db.xlsx", valid_sheets, notes))
    warn = [i.message for i in db.issues if i.level == WARNUNG and i.check == "Statistik fehlt"]
    hint = [i.message for i in db.issues if i.level == HINWEIS and i.check == "Statistik fehlt"]
    assert len(warn) == 51 and warn[-1] == "… und 8 weitere Zeilen"
    assert len(hint) == 3 and all("dokumentiert im Blatt Datenhinweise" in m for m in hint)


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
def test_current_database_has_no_errors():
    """Die Datenbank in data/ (jeder Stand) muss fehlerfrei sein."""
    db = load_database(REAL_DATABASE)
    assert not db.has_errors, [i for i in db.issues if i.level == FEHLER]


@pytest.mark.skipif(not REFERENCE_DATABASE.exists(), reason="Referenz-Datenbank nicht vorhanden")
def test_real_database():
    """Genaue Erwartungswerte für den Referenzstand (SHA-256 6d68583c…)."""
    db = load_database(REFERENCE_DATABASE)
    assert db.sha256 == KNOWN_DB_SHA
    # Der Referenzstand stammt vom 31.10.2026, also vor Etappe F: Blatt „Seria A“ (alter Name) und leeres
    # Blatt „LaLiga“. Seit Etappe F sind beide Ligen Pflicht; andere Fehler darf es nicht geben.
    errors = {(i.sheet, i.check) for i in db.issues if i.level == FEHLER}
    assert errors == {("Serie A", "Blatt fehlt"), ("LaLiga", "Blatt leer")}, errors
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
