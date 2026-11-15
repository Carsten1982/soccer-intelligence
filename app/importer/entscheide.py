"""Entscheide aus dem Reiter „Datenimport/API“ (Spezifikation Ergebnis-Import v1.1, R1/R2; Carsten 15.11.2026).

Niemand schreibt von Hand in eine Datei. Braucht eine Änderung einen Entscheid, zeigt der Reiter zwei Buttons; der Klick
landet als Anfrage beim Dienst, der ihn hier festhält. Jeder Lauf wendet die Entscheide an, und ein entschiedener Punkt
wird nie wieder gefragt.

Arten:
- „korrektur“: späte Änderung der API (Spiel älter als 7 Tage, „eingefroren“) an einem Wert.
  Entscheid „uebernehmen“ oder „ablehnen“, gilt für genau diesen API-Wert. Liefert die API später einen anderen Wert,
  wird wieder gefragt.
- „endstand“: Endstand der API passt nicht zu den Tor-Ereignissen (z. B. Wertung am grünen Tisch).
  Entscheid „platz“ (Ergebnis auf dem Platz = laut Tor-Ereignissen) oder „api“ (Endstand der API).

Die Datei liegt im Import-Ordner (nicht in der Excel-Datei) und kommt bei jeder Übernahme mit Datum ins Backup.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .einstellungen import DECISIONS_FILE

KINDS = {"korrektur": ("uebernehmen", "ablehnen"), "endstand": ("platz", "api")}


def load(base: Path) -> list[dict]:
    p = Path(base) / DECISIONS_FILE
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def add(base: Path, entry: dict) -> None:
    """Entscheid anhängen (Schreiben in einem Schritt)."""
    if entry.get("art") not in KINDS or entry.get("entscheid") not in KINDS[entry["art"]]:
        raise ValueError(f"ungültiger Entscheid: {entry}")
    items = load(base)
    items.append(entry)
    tmp = Path(base) / f".{DECISIONS_FILE}.tmp"
    tmp.write_text(json.dumps(items, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    os.replace(tmp, Path(base) / DECISIONS_FILE)


def _same(a, b) -> bool:
    try:
        return float(a) == float(b)
    except (TypeError, ValueError):
        return str(a) == str(b)


def lookup(items: list[dict], art: str, fixture_id: int, spalte: str | None = None, wert=None) -> str | None:
    """Letzter passender Entscheid oder None. Bei „korrektur“ muss auch der API-Wert gleich sein."""
    for e in reversed(items):
        if e.get("art") != art or int(e.get("id", -1)) != int(fixture_id):
            continue
        if art == "korrektur" and (e.get("spalte") != spalte or not _same(e.get("api_wert"), wert)):
            continue
        return e.get("entscheid")
    return None
