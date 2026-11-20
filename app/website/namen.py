"""Anzeigenamen der Vereine je Sprache (seit 0.21; Glossar Abschnitt 11, Konzept 08, Abschnitt 4.1).

Grundlage ist die Tabelle app/config/teamnamen_anzeige.csv (Liga; Name der Datenquelle; Deutsch; Englisch). Der Name der
Datenquelle bleibt in Datenbank, Spielplan, Schnappschuss und Adresse (Slug) unverändert; nur die Anzeige wechselt.
Fehlt ein Verein in der Tabelle (z. B. ein Aufsteiger), erscheint der Name der Datenquelle; welche fehlen, zeigt
fehlende() (Meldung im Reiter Datenimport/API). Die Veröffentlichung wird dadurch nicht blockiert.
"""

from __future__ import annotations

import csv
import io
from functools import lru_cache
from pathlib import Path

from core.files import file_key

from . import einstellungen as W


@lru_cache(maxsize=4)
def _tabelle(pfad: str, schluessel: tuple) -> dict[tuple[str, str], dict[str, str]]:  # noqa: ARG001 - Cache-Schlüssel
    text = Path(pfad).read_text(encoding="utf-8")
    zeilen = [z for z in text.splitlines() if z.strip() and not z.lstrip().startswith("#")]
    out = {}
    for r in csv.DictReader(io.StringIO("\n".join(zeilen)), delimiter=";"):
        out[(r["liga"].strip(), r["name"].strip())] = {"de": r["de"].strip(), "en": r["en"].strip()}
    return out


def tabelle(pfad: Path | None = None) -> dict[tuple[str, str], dict[str, str]]:
    pfad = Path(pfad or W.TEAMNAMEN)
    try:
        return _tabelle(str(pfad), file_key(pfad))
    except (OSError, KeyError, csv.Error):
        return {}


def anzeige(liga: str, name: str, lang: str) -> str:
    """Anzeigename in der Sprache; ohne Eintrag der Name der Datenquelle."""
    eintrag = tabelle().get((liga, name))
    return (eintrag.get(lang) or name) if eintrag else name


def fehlende(paare) -> list[tuple[str, str]]:
    """(Liga, Name) aus paare, für die noch kein Anzeigename festgelegt ist, sortiert."""
    t = tabelle()
    return sorted({(liga, name) for liga, name in paare if (liga, name) not in t})
