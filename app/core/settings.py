"""Zentrale Einstellungen. Pfade lassen sich per Umgebungsvariable überschreiben (z. B. für Tests)."""

import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("SI_DATA_DIR", "/data"))
DATABASE_FILENAME = "Database-Soccer-Intelligence.xlsx"
DATABASE_FILE = DATA_DIR / DATABASE_FILENAME

# Pflicht-Ligablätter (müssen vorhanden und gefüllt sein)
REQUIRED_LEAGUE_SHEETS = ("Bundesliga", "Premier League")
# Optionale Ligablätter (dürfen leer sein)
OPTIONAL_LEAGUE_SHEETS = ("Seria A", "LaLiga")
NOTES_SHEET = "Datenhinweise"

LEAGUE_SHEETS = REQUIRED_LEAGUE_SHEETS + OPTIONAL_LEAGUE_SHEETS

# Anzeige-Zeitzone
TIMEZONE = "Europe/Berlin"

APP_VERSION = "0.2 – Schritt 1: Datenbasis"
