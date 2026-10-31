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

# Pflicht-Ligablätter (müssen vorhanden und gefüllt sein)
REQUIRED_LEAGUE_SHEETS = ("Bundesliga", "Premier League")
# Optionale Ligablätter (dürfen leer sein)
OPTIONAL_LEAGUE_SHEETS = ("Seria A", "LaLiga")
NOTES_SHEET = "Datenhinweise"

LEAGUE_SHEETS = REQUIRED_LEAGUE_SHEETS + OPTIONAL_LEAGUE_SHEETS

# Anzeige-Zeitzone
TIMEZONE = "Europe/Zurich"  # massgeblich für „heute“ (aktueller Spieltag)

APP_VERSION = "0.6 – Etappe D: Top Anomalien"
