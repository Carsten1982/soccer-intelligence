"""Stand des Datenimports: Beginn des letzten erfolgreichen Importlaufs (Spielplan v2.1, S9).

Seit 0.20 an einer Stelle für Dashboard und Website (bis 0.19.1 je eine eigene Fassung in state.py und
website/daten.py). Gelesen wird nur /import/laeufe/<lauf>/bericht.json; ein Lauf zählt als erfolgreich, wenn er
nicht fehlgeschlagen ist und keine Fehler hat (übernommen, wartend, verworfen oder ersetzt: die API hat geliefert).
Die 48-Stunden-Grenze gilt ab diesem Zeitpunkt (Entscheidung Carsten 19.11.2026, `07`, 4.3).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import settings

FAILED_RUNS = ("fehlgeschlagen", "Fehler – nicht übernehmbar")
TZ = ZoneInfo(settings.TIMEZONE)


def last_successful_run(import_dir: Path) -> datetime | None:
    """Beginn des letzten erfolgreichen Importlaufs in Europe/Zurich ohne Zeitzonenangabe (wie die Anstosszeiten
    im Spielplan), auf Sekunden; None, wenn es keinen gibt."""
    for report in sorted((Path(import_dir) / "laeufe").glob("*/bericht.json"), reverse=True):
        try:
            rep = json.loads(report.read_text(encoding="utf-8"))
            if rep.get("status") in FAILED_RUNS or not rep.get("start"):
                continue
            start = datetime.fromisoformat(rep["start"])
            return (start.astimezone(TZ) if start.tzinfo else start).replace(tzinfo=None, microsecond=0)
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    return None
