"""Feste Zuordnung eigene Spiel-ID <-> API-Football-Fixture-ID (Spezifikation Spielplan v2.1, Abschnitt 3.5; S6).

- Spiele bis zum Umstieg (15.11.2026) tragen in der Datenbank eigene IDs (unter 160'000). Ihre API-ID steht in
  config/zuordnung_api.csv, einmal erzeugt und geprüft (Datum und Endstand, 11'978 Spiele).
- Neu importierte Spiele tragen als id die API-ID selbst (ab 1'000'000); sie brauchen keinen Eintrag.
- Verknüpft wird darum immer zuerst über die API-ID: Zuordnungsdatei, sonst die ID selbst.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

from . import settings

MAPPING_FILE = settings.CONFIG_DIR / "zuordnung_api.csv"
API_ID_FROM = 1_000_000          # IDs ab hier stammen von API-Football (eigene IDs liegen unter 160'000)


@lru_cache(maxsize=4)
def load_mapping(path: Path = MAPPING_FILE) -> dict[str, dict[int, int]]:
    """Liga -> {API-ID: eigene ID}. Zeilen mit # sind Kommentare."""
    out: dict[str, dict[int, int]] = {}
    with Path(path).open(encoding="utf-8") as fh:
        rows = csv.DictReader((line for line in fh if not line.startswith("#")), delimiter=";")
        for r in rows:
            out.setdefault(r["liga"], {})[int(r["api_id"])] = int(r["id"])
    return out


def db_id(league: str, api_id: int | None, mapping: dict[str, dict[int, int]] | None = None) -> int | None:
    """Die id in der Datenbank für ein API-Spiel: aus der Zuordnungsdatei, sonst die API-ID selbst."""
    if api_id is None:
        return None
    mapping = load_mapping() if mapping is None else mapping
    return mapping.get(league, {}).get(int(api_id), int(api_id))
