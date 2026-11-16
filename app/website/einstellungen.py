"""Einstellungen der Website (Konzept docs/08_Website.md, Abschnitte 3 und 4)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ORDNER = Path(__file__).resolve().parent
VORLAGEN = ORDNER / "vorlagen"
STATISCH = ORDNER / "statisch"
TEXTE = ORDNER / "texte"

SPRACHE = "de"                     # erste Fassung nur Deutsch (Übergabe 9); Struktur für en, it, es angelegt
PREFIX = os.environ.get("SI_VORSCHAU_PREFIX", "/vorschau")    # Adresse der Vorschau (Traefik-Regel PathPrefix)
PORT = int(os.environ.get("SI_VORSCHAU_PORT", "8080"))

VORMITTAG = (8, 0)                 # Zeitreise ohne Uhrzeit: 08:00, also nach dem Import um 04:00
IMPORT_STUNDE = 4                  # täglicher Importlauf (importer/einstellungen.py, RUN_HOUR)


@dataclass(frozen=True)
class WebLiga:
    name: str      # Name in Datenbank und Spielplan (Blattname)
    slug: str      # Adresse auf der Website
    key: str       # Schlüssel in der Sprachdatei (liga.<key>)


# Reihenfolge wie im Entwurf (Übergabe 5.1 und 6.1): Bundesliga, La Liga, Premier League, Serie A
LIGEN = (
    WebLiga("Bundesliga", "bundesliga", "bundesliga"),
    WebLiga("LaLiga", "la-liga", "la_liga"),
    WebLiga("Premier League", "premier-league", "premier_league"),
    WebLiga("Serie A", "serie-a", "serie_a"),
)
STANDARD_LIGA = "bundesliga"       # F8


def liga_aus_slug(slug: str) -> WebLiga | None:
    return next((lg for lg in LIGEN if lg.slug == slug), None)
