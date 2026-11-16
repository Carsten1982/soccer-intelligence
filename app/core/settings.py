"""Zentrale Einstellungen. Pfade lassen sich per Umgebungsvariable überschreiben (z. B. für Tests)."""

import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("SI_DATA_DIR", "/data"))
DATABASE_FILENAME = "Database-Soccer-Intelligence.xlsx"
DATABASE_FILE = DATA_DIR / DATABASE_FILENAME
FIXTURES_FILENAME = "Spielplan.xlsx"
FIXTURES_FILE = DATA_DIR / FIXTURES_FILENAME

# Konfiguration (aktive Ligen, Teamliste). Liegt im Image unter /app/config,
# wird mit dem Code versioniert. Für Tests per Umgebungsvariable überschreibbar.
CONFIG_DIR = Path(os.environ.get("SI_CONFIG_DIR", Path(__file__).resolve().parents[1] / "config"))
LEAGUES_FILE = CONFIG_DIR / "ligen.toml"
TEAMS_FILE = CONFIG_DIR / "teams.toml"
# Schwellenwerte der Anomalie-Einstufung je Liga und KPI (KPI-Regelwerk 2.2, seit Etappe H)
THRESHOLDS_FILE = CONFIG_DIR / "schwellen.toml"

# Pflicht-Ligablätter (müssen vorhanden und gefüllt sein). Seit Etappe F (07.11.2026) alle vier Ligen,
# weil alle vier im Dashboard aktiv sind. Das Blatt für Italien heisst seit 07.11.2026 „Serie A“ (vorher „Seria A“).
REQUIRED_LEAGUE_SHEETS = ("Bundesliga", "Premier League", "Serie A", "LaLiga")
# Optionale Ligablätter (dürfen fehlen oder leer sein) – derzeit keine. Eine neue Liga kann hier
# vorbereitet werden, bevor sie in app/config/ligen.toml aktiv geschaltet wird.
OPTIONAL_LEAGUE_SHEETS: tuple[str, ...] = ()
NOTES_SHEET = "Datenhinweise"

LEAGUE_SHEETS = REQUIRED_LEAGUE_SHEETS + OPTIONAL_LEAGUE_SHEETS

# Anzeige-Zeitzone
TIMEZONE = "Europe/Zurich"  # massgeblich für „heute“ (aktueller Spieltag)

APP_VERSION = "0.15.1 – Datenimport"
