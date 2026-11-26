"""Einstellungen der Website (Konzept docs/08_Website.md, Abschnitte 3 und 4; seit 0.21 Sprachen und Adressen)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ORDNER = Path(__file__).resolve().parent
VORLAGEN = ORDNER / "vorlagen"
STATISCH = ORDNER / "statisch"
TEXTE = ORDNER / "texte"

SPRACHE = "de"                     # Standardsprache und Rückfall der Sprachdatei
SPRACHEN = ("de", "en")            # seit 0.21 Deutsch und Englisch, je Sprache ein Verzeichnis /de/, /en/
DOMAIN = "https://soccer-intelligence.com"   # absolute Adressen für canonical, hreflang, Sitemap (SEO-Briefing 4)
OG_LOCALE = {"de": "de_CH", "en": "en_GB"}
IN_LANGUAGE = {"de": "de-CH", "en": "en-GB"}
SPRACHNAME = {"de": "Deutsch", "en": "English"}

# Pfadwörter je Seite und Sprache (Konzept 08, Abschnitt 4.1; SEO-Briefing 2). Der Liga-Teil und der Slug einer
# Spielseite sind in beiden Sprachen gleich; nur diese Wörter werden übersetzt.
PFADE = {
    "spieltag": {"de": "spieltag", "en": "matchday"},
    "spiel": {"de": "spiel", "en": "match"},
    "methodik": {"de": "methodik", "en": "methodology"},
    "glossar": {"de": "glossar", "en": "glossary"},
    "kontakt": {"de": "kontakt", "en": "contact"},
    "impressum": {"de": "impressum", "en": "legal-notice"},
    "datenschutz": {"de": "datenschutz", "en": "privacy-policy"},
    "cookie": {"de": "cookie-einstellungen", "en": "cookie-settings"},
}
PREFIX = os.environ.get("SI_VORSCHAU_PREFIX", "/vorschau")    # Adresse der Vorschau (Traefik-Regel PathPrefix)
PORT = int(os.environ.get("SI_VORSCHAU_PORT", "8080"))
# Foto für die Startseite (seit 0.18, Entscheidung Q6): nur auf dem Server, nicht in Git. Fehlt es, zeigt die Seite
# einen neutralen Platzhalter. Ablage: /docker/football-dashboard/website-bilder/portrait.jpg
BILDER = Path(os.environ.get("SI_BILDER_DIR", "/bilder"))
FOTO = "portrait.jpg"

WEBSITE_KONFIG = Path(__file__).resolve().parents[1] / "config" / "website.toml"     # index_ab, seiten_ab_saison
TEAMNAMEN = Path(__file__).resolve().parents[1] / "config" / "teamnamen_anzeige.csv"  # Anzeigenamen DE/EN (0.21)

# Betreiberangaben (Impressum, Kontakt) nur aus der Umgebung (.env auf dem Server), nie im Code (CLAUDE.md, Regeln)
BETREIBER_NAME = os.environ.get("SI_IMPRESSUM_NAME", "").strip()
BETREIBER_ADRESSE = [z.strip() for z in os.environ.get("SI_IMPRESSUM_ADRESSE", "").split("|") if z.strip()]
KONTAKT_EMAIL = os.environ.get("SI_KONTAKT_EMAIL", "").strip()
VORSCHAU = bool(PREFIX.strip("/"))          # Vorschau unter /vorschau: noindex, kein Browser-Cache, Zeitreise


def _ga4_mess_id() -> str:
    """Mess-ID von Google Analytics 4 aus website.toml (seit 0.28). Nur die öffentliche Website misst (Entscheid Carsten
    26.11.2026: nicht die Vorschau); ungültige oder leere Angabe = keine Messung."""
    import re
    import tomllib
    try:
        wert = str(tomllib.loads(WEBSITE_KONFIG.read_text(encoding="utf-8")).get("ga4_mess_id", "")).strip()
    except (OSError, ValueError):
        return ""
    return wert if re.fullmatch(r"G-[A-Z0-9]{4,20}", wert) else ""


GA4_ID = "" if VORSCHAU else _ga4_mess_id()      # leer = kein Google-Code, auch nach Zustimmung nicht
COOKIE_WAHL = "cookie_wahl"                       # eigenes Cookie mit der Wahl (zugestimmt / abgelehnt), 6 Monate
COOKIE_TAGE = 180

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
