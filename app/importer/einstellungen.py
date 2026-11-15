"""Einstellungen des Datenimports. Pfade per Umgebungsvariable überschreibbar (Tests, Probelauf)."""

from __future__ import annotations

import os
import tomllib
from datetime import date
from pathlib import Path

from core import settings

IMPORT_DIR = Path(os.environ.get("SI_IMPORT_DIR", "/import"))
BACKUP_DIR = Path(os.environ.get("SI_BACKUP_DIR", "/backup"))
KEY_ENV = "API_FOOTBALL_KEY"                         # Schlüssel nur aus der Umgebung (.env auf dem Server)
BASE_URL = "https://v3.football.api-sports.io/"
TIMEZONE = settings.TIMEZONE

LEAGUE_IDS = {"Bundesliga": 78, "Premier League": 39, "Serie A": 135, "LaLiga": 140}
COUNTRY = {"Bundesliga": "Germany", "Premier League": "England", "Serie A": "Italy", "LaLiga": "Spain"}

DAILY_LIMIT = 500             # eigene Obergrenze je Tag (Spezifikation, Abschnitt 3)
RUN_HOUR = 4                  # Montag bis Freitag um 04:00 (E8)
RECHECK_ROUNDS = 2            # die letzten 2 Spieltage je Lauf neu holen (Entscheidung Carsten 15.11.2026)
OPEN_DAYS = 7                 # Statistik so lange nachholen, danach Warnung
BACKUPS_KEPT = 30             # Fassungen je Datei im Backup
HISTORY_DAYS = 14             # Protokoll im Reiter

CONFIG_FILE = settings.CONFIG_DIR / "import.toml"
TEAM_NAMES_FILE = settings.CONFIG_DIR / "teamnamen.toml"


def automatic_from() -> date | None:
    """Ab diesem Datum wird eine fehlerfreie Fassung automatisch übernommen (E3); None = immer von Hand."""
    if not CONFIG_FILE.exists():
        return None
    value = tomllib.loads(CONFIG_FILE.read_text(encoding="utf-8")).get("automatisch_ab")
    return value if isinstance(value, date) else None
