"""Gemeinsame Test-Hilfen. Fast alle Tests laufen ohne Streamlit; nur die Seitentests in test_ui.py
brauchen Streamlit und laufen darum nur im Test-Container auf dem Server."""

import datetime as dt
import os
import sys
import zipfile
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from core import schema  # noqa: E402

REAL_DATA_DIR = Path(os.environ.get("SI_DATA_DIR", ROOT / "data"))
REAL_DATABASE = REAL_DATA_DIR / "Database-Soccer-Intelligence.xlsx"
REAL_FIXTURES = REAL_DATA_DIR / "Spielplan.xlsx"

# Stand der Dateien, für den die genauen Erwartungswerte gelten (siehe docs/02_Datenbasis.md, 04_Spielplan.md).
# Bei einer neueren Datei prüfen die Tests mit echten Daten nur noch, dass keine Fehler auftreten.
KNOWN_DB_SHA = "6d68583c2e66616e92c1bf3e8a8611b4b517bcf4c0a7a91c68101ea26a2284e2"
# Fester Referenzstand der Datenbank für die KPI-Testfälle (docs/tests). Liegt im Repository, damit die
# Testfälle auch dann laufen, wenn data/ schon eine neuere Datenbank enthält.
REFERENCE_DATABASE = ROOT / "tests" / "referenz" / "Database-Soccer-Intelligence_6d68583c.xlsx"
KNOWN_FIXTURES_SHA = "5261e91646d0de697da145e77d85cf874681ccdd562187feb5395bb8c0eb4877"
# Referenzstand für die Testfälle KPI 05–09 (bestätigt 08.11.2026, docs/tests/test_kpi05…09…): Datenbank mit vier Ligen.
REFERENCE_DATABASE_H = ROOT / "tests" / "referenz" / "Database-Soccer-Intelligence_f37e36d3.xlsx"
KNOWN_DB_SHA_H = "f37e36d301767321575aeadf908c39e288b9a655d02d85d5bcfde0507effdc34"
# Neue Datenbank (Version 0.11, Prüfbericht 10.11.2026): Saisons 2018/19–2025/26, 2026/27 bis 10.11.2026.
# Referenzsaison 2018/19 (nur Vorsaison). Dient den Tests der Referenzsaison und dem Vollvergleich alt/neu.
REFERENCE_DATABASE_2018 = ROOT / "tests" / "referenz" / "Database-Soccer-Intelligence_451348b6.xlsx"
KNOWN_DB_SHA_2018 = "451348b6550b91f4df3a26450a26d205e76f69c13ac520d080d3a427ff084904"
LEAGUE_TEAMS = {"Bundesliga": 18, "Premier League": 20, "Serie A": 20, "LaLiga": 20}


def make_match(mid, home, away, date, ft=(1, 0), ht=(1, 0), league="Bundesliga", gameday=1):
    """Ein in sich stimmiges Spiel mit allen 58 Spalten."""

    def res(h, a):
        return "H" if h > a else "A" if h < a else "D"

    sh = (ft[0] - ht[0], ft[1] - ht[1])
    row = {
        "Date": pd.Timestamp(date), "Gameday": gameday, "id": mid,
        "matchDate": pd.Timestamp(date).strftime("%d-%m-%y 15:30"),
        "Country": "Germany", "League": league, "Season": "2024/2025",
        "homeTeam": home, "awayTeam": away, "referee": "Test Referee",
        "FT Home Goals": ft[0], "FT Away Goals :": ft[1], "FT Result :": res(*ft),
        "Full-Time Home Goals": ft[0], "Full-Time Away Goals": ft[1], "Full-Time Result": res(*ft),
        "First-Half Home Goals": ht[0], "First-Half Away Goals": ht[1], "First-Half Result": res(*ht),
        "Second-Half Home Goals": sh[0], "Second-Half Away Goals": sh[1], "Second-Half Result": res(*sh),
    }
    # Statistiken: HZ1 + HZ2 = Gesamt, Ballbesitz 55/45, Schüsse >= aufs Tor + daneben
    for _, hp, ap in schema.SUMMABLE_STATS:
        for prefix in (hp, ap):
            row[f"{prefix} First Half"], row[f"{prefix} Second Half"] = 2, 3
            row[f"{prefix} Full Time"] = 5
    for p in ("Full Time", "First Half", "Second Half"):
        row[f"Home Team Shots {p}"] = row[f"Away Team Shots {p}"] = {"Full Time": 12, "First Half": 6, "Second Half": 6}[p]
        row[f"Home Ball Possession {p}"], row[f"Away Ball Possession {p}"] = 55, 45
    return {c: row[c] for c in schema.EXPECTED_COLUMNS}


def valid_league(league="Bundesliga"):
    """Vollständige Mini-Saison: 2 Teams, Hin- und Rückspiel."""
    return pd.DataFrame(
        [
            make_match(1, "Alpha", "Beta", "2024-08-24", league=league),
            make_match(2, "Beta", "Alpha", "2025-01-18", ft=(2, 2), ht=(0, 1), league=league, gameday=2),
        ],
        columns=list(schema.EXPECTED_COLUMNS),
    )


def write_workbook(path, sheets: dict[str, pd.DataFrame], notes: pd.DataFrame | None = None):
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        for name, df in sheets.items():
            df.to_excel(xw, sheet_name=name, index=False)
        if notes is not None:
            notes.to_excel(xw, sheet_name="Datenhinweise", index=False)
    return path


@pytest.fixture
def valid_sheets():
    return {
        "Bundesliga": valid_league("Bundesliga"),
        "Premier League": valid_league("Premier League"),
        "Serie A": valid_league("Serie A"),
        "LaLiga": valid_league("LaLiga"),
    }


def notes_for(league, mid):
    return pd.DataFrame([{
        "Liga": league, "id": mid, "Datum": dt.datetime(2024, 12, 14), "Begegnung": "Test",
        "Art": "Sonderfall", "Hinweis": "Statistiken fehlen", "Geändert am": dt.datetime(2026, 10, 25), "Quelle": "Test",
    }])


def break_xml(path, member="xl/worksheets/sheet1.xml"):
    """Gültige ZIP-Datei mit kaputtem XML im ersten Tabellenblatt (z. B. beschädigte Datei, H.1)."""
    path = Path(path)
    with zipfile.ZipFile(path) as zin:
        parts = [(item, zin.read(item.filename)) for item in zin.infolist()]
    with zipfile.ZipFile(path, "w") as zout:
        for item, data in parts:
            zout.writestr(item, b"<worksheet><row>kaputt" if item.filename == member else data)
    return path


# --- Fälle der Simulation, einmal je Testlauf (teuer: rund 40 bzw. 55 Sekunden) -------------------------------

def _all_cases(path: Path, sha: str) -> pd.DataFrame:
    from core.config import League
    from core.kpis import prepare_league
    from core.loader import load_database
    from core.simulation import build_cases

    if not path.exists():
        pytest.skip(f"Referenz-Datenbank {path.name} nicht vorhanden")
    db = load_database(path)
    assert db.sha256 == sha and not db.has_errors
    frames = [build_cases(prepare_league(db.leagues[name]), League(name, "x", teams, True))
              for name, teams in LEAGUE_TEAMS.items()]
    return pd.concat(frames, ignore_index=True)


@pytest.fixture(scope="session")
def cases_h() -> pd.DataFrame:
    """build_cases aller vier Ligen mit der Referenz-Datenbank H (f37e36d3, Referenzsaison 2020/21)."""
    return _all_cases(REFERENCE_DATABASE_H, KNOWN_DB_SHA_H)


@pytest.fixture(scope="session")
def cases_2018() -> pd.DataFrame:
    """build_cases aller vier Ligen mit der neuen Datenbank (451348b6, Referenzsaison 2018/19)."""
    return _all_cases(REFERENCE_DATABASE_2018, KNOWN_DB_SHA_2018)
