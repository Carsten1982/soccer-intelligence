"""Tageswerte für das Dashboard „Datenmonitoring“ des Showcase (seit 0.30; docs/09, Abschnitt 4.1).

Der Import-Dienst schreibt einmal pro Tag (und nach jeder neuen Fassung der Datenbank) in /import/kennzahlen.json:
- das Ergebnis der Datenprüfung (Fehler, Warnungen, Hinweise in Datenbank und Spielplan, wie im Dashboard
  „Datenqualität“) als Verlauf, höchstens 60 Tage – so entsteht die Grafik „Hinweise im Verlauf“ (ab Einführung,
  nicht rückwirkend),
- die Backups: Anzahl der gesicherten Fassungen und Tag der neuesten (die Website sieht den Backup-Ordner nicht).
Die Website liest die Datei nur. Fehler hier stoppen den Import-Dienst nie.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from core import settings
from core.files import file_key
from core.issues import FEHLER, HINWEIS, WARNUNG

from . import alarme

DATEI = "kennzahlen.json"
TAGE = 60
BACKUP_MUSTER = "Database-Soccer-Intelligence_*_vor_import.xlsx"


def _backups(backup_dir: Path) -> dict:
    dateien = sorted(Path(backup_dir).glob(BACKUP_MUSTER)) if Path(backup_dir).exists() else []
    neueste = dateien[-1].name[29:39] if dateien else None         # „…_JJJJ-MM-TT_…“ (wie die Statusmail)
    return {"anzahl": len(dateien), "neueste": neueste}


def pruefung(db_pfad: Path | None = None, fx_pfad: Path | None = None) -> dict:
    """Fehler, Warnungen und Hinweise von Datenbank und Spielplan (dieselben Prüfregeln wie das Dashboard)."""
    from core.config import load_leagues, load_teams
    from core.fixtures import load_fixtures
    from core.loader import load_database
    db = load_database(db_pfad or settings.DATABASE_FILE)
    fx = load_fixtures(fx_pfad or settings.FIXTURES_FILE, load_leagues(settings.LEAGUES_FILE), db.leagues,
                       load_teams(settings.TEAMS_FILE))
    return {k: db.count(s) + fx.count(s) for k, s in (("fehler", FEHLER), ("warnungen", WARNUNG), ("hinweise", HINWEIS))}


def aktualisieren(base: Path, backup_dir: Path, now: datetime, zaehlen=pruefung) -> bool:
    """Tageswert schreiben, wenn heute noch keiner steht oder sich Datenbank/Spielplan geändert haben.
    Gibt zurück, ob geschrieben wurde."""
    pfad = Path(base) / DATEI
    try:
        alt = json.loads(pfad.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        alt = {}
    heute = now.date().isoformat()
    dateien = [list(file_key(Path(settings.DATABASE_FILE))), list(file_key(Path(settings.FIXTURES_FILE)))]
    if alt.get("tag") == heute and alt.get("dateien") == dateien:
        return False
    werte = zaehlen()
    verlauf = [v for v in alt.get("verlauf") or [] if v.get("tag") != heute] + [{"tag": heute, **werte}]
    alarme.speichern(pfad, {"tag": heute, "zeit": now.replace(microsecond=0).isoformat(), "dateien": dateien,
                            "verlauf": verlauf[-TAGE:], "backups": _backups(backup_dir)})
    return True
