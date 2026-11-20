"""Adressen der Website (seit 0.21; Konzept 08, Abschnitt 4.1; SEO-Briefing Abschnitt 2).

Eine Stelle für alle Regeln: Pfadwörter je Sprache, Slug der Spielseite, Saison in der Adresse, Weiterleitungen.

- Alle Adressen liegen im Sprachverzeichnis und enden mit „/“: /de/, /en/matchday/bundesliga/ …
- Spielseite: /de/spiel/<liga>/<heim>-<gast>-<ID>/; eindeutig ist nur die ID (Fixture-ID von API-Football). Der Slug
  entsteht aus den Namen der Datenquelle und ist in beiden Sprachen gleich. Weicht eine Adresse mit gültiger ID ab
  (alter Name, andere Liga, fehlender Schrägstrich, Grossbuchstaben), leitet der Server dauerhaft (301) weiter.
- /de/spieltag/ und /en/matchday/ leiten vorübergehend (302) auf die Standardliga.
- Alte Vorschau-Adressen (/spieltag/<liga>, /spiel/<ID>) leiten dauerhaft auf die neuen.
- Unbekannte Adresse: Seite „nicht gefunden“ (404) in der Sprache des Verzeichnisses, sonst Deutsch.

Reine Logik ohne Daten: Ob eine Spiel-ID existiert und wie ihr richtiger Slug lautet, prüft die Vorschau mit den
Daten (website/vorschau.py) und leitet dann weiter.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, replace

from . import einstellungen as W

INHALTSSEITEN = ("methodik", "glossar", "kontakt", "impressum", "datenschutz", "cookie")
UMLAUTE = {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "ae", "Ö": "oe", "Ü": "ue", "ß": "ss"}


def slug(text: str) -> str:
    """„1. FC Köln“ → „1-fc-koeln“, „Brighton & Hove Albion“ → „brighton-hove-albion“, „Atlético“ → „atletico“.
    Kleinschreibung, Umlaute ausgeschrieben, übrige Akzente entfernt, Apostrophe ersatzlos, alles ausser a–z und 0–9
    wird ein Bindestrich; keine doppelten Bindestriche, keine am Rand."""
    text = "".join(UMLAUTE.get(c, c) for c in str(text))
    text = re.sub(r"['’`´]", "", text)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def spiel_slug(heim: str, gast: str, spiel_id: int) -> str:
    """„vfb-stuttgart-bayern-muenchen-1550203“"""
    return f"{slug(heim)}-{slug(gast)}-{int(spiel_id)}"


def saison_slug(saison: str) -> str:
    """„2025/2026“ → „2025-26“"""
    a, b = saison.split("/")
    return f"{a}-{b[-2:]}"


def saison_aus_slug(text: str) -> str | None:
    """„2025-26“ → „2025/2026“; ungültig → None (auch wenn die Jahre nicht aufeinander folgen)."""
    m = re.fullmatch(r"(\d{4})-(\d{2})", text)
    if not m:
        return None
    jahr = int(m.group(1))
    return f"{jahr}/{jahr + 1}" if f"{(jahr + 1) % 100:02d}" == m.group(2) else None


@dataclass(frozen=True)
class Ziel:
    """Eine Seite der Website in einer Sprache."""
    art: str                     # start, spieltag, archiv, spiel, methodik, glossar, kontakt, impressum, datenschutz,
                                 # cookie, fehlt
    lang: str = W.SPRACHE
    liga: str | None = None      # Liga-Slug (bundesliga, premier-league, serie-a, la-liga)
    saison: str | None = None    # „2025/2026“ (Archiv)
    nr: int | None = None        # Spieltag (Archiv)
    spiel_id: int | None = None
    slug: str = ""               # Spielseite: „<heim>-<gast>-<id>“

    def in_sprache(self, lang: str) -> "Ziel":
        return replace(self, lang=lang)


def pfad(z: Ziel) -> str:
    """Adresse ohne Vorschau-Präfix, immer mit Schrägstrich am Ende."""
    teile = [z.lang]
    if z.art == "start":
        pass
    elif z.art == "spieltag":
        teile += [W.PFADE["spieltag"][z.lang], z.liga]
    elif z.art == "archiv":
        teile += [W.PFADE["spieltag"][z.lang], z.liga, saison_slug(z.saison), str(int(z.nr))]
    elif z.art == "spiel":
        teile += [W.PFADE["spiel"][z.lang], z.liga, z.slug]
    elif z.art in W.PFADE:
        teile += [W.PFADE[z.art][z.lang]]
    else:
        raise ValueError(f"keine Adresse für die Seite {z.art}")
    return "/" + "/".join(teile) + "/"


@dataclass(frozen=True)
class Erkannt:
    """Ergebnis der Erkennung einer Adresse."""
    ziel: Ziel | None = None     # erkannte Seite (bei der Spielseite: ID, Liga und Slug wie in der Adresse)
    weiter: str | None = None    # Pfad, auf den weitergeleitet wird (ohne Präfix)
    status: int = 200            # 200, 301, 302 oder 404
    lang: str = W.SPRACHE        # Sprache der Seite (auch für „nicht gefunden“)


def _art_zum_wort(lang: str, wort: str) -> str | None:
    return next((art for art, w in W.PFADE.items() if w[lang] == wort), None)


def erkennen(rest: str) -> Erkannt:
    """rest = Pfad ohne Vorschau-Präfix, z. B. „/de/spieltag/bundesliga/“. Prüft nur die Form; ob es die Liga, den
    Spieltag oder die Spiel-ID gibt, entscheidet die Vorschau mit den Daten."""
    roh = rest or "/"
    teile = [t for t in roh.split("/") if t]
    if not teile:
        return Erkannt(weiter=f"/{W.SPRACHE}/", status=301)
    klein = [t.lower() for t in teile]
    if klein[0] not in W.SPRACHEN:
        return _alte_adresse(klein)
    lang = klein[0]
    normal = "/" + "/".join(klein) + "/"
    ergebnis = _form(lang, klein[1:])
    if ergebnis.status == 404:
        return Erkannt(status=404, lang=lang)
    if ergebnis.ziel is not None and ergebnis.status == 200 and roh != normal:
        return Erkannt(ziel=ergebnis.ziel, weiter=normal, status=301, lang=lang)    # Schrägstrich, Grossbuchstaben
    return ergebnis


def _form(lang: str, t: list[str]) -> Erkannt:
    if not t:
        return Erkannt(Ziel("start", lang), lang=lang)
    art = _art_zum_wort(lang, t[0])
    if art is None:
        return Erkannt(status=404, lang=lang)
    if art == "spieltag":
        if len(t) == 1:                                        # ohne Liga: vorübergehend auf die Standardliga
            return Erkannt(weiter=pfad(Ziel("spieltag", lang, liga=W.STANDARD_LIGA)), status=302, lang=lang)
        if W.liga_aus_slug(t[1]) is None:
            return Erkannt(status=404, lang=lang)
        if len(t) == 2:
            return Erkannt(Ziel("spieltag", lang, liga=t[1]), lang=lang)
        if len(t) == 4 and t[3].isdigit() and int(t[3]) > 0 and saison_aus_slug(t[2]):
            return Erkannt(Ziel("archiv", lang, liga=t[1], saison=saison_aus_slug(t[2]), nr=int(t[3])), lang=lang)
        return Erkannt(status=404, lang=lang)
    if art == "spiel":
        m = re.search(r"(?:^|-)(\d+)$", t[-1]) if len(t) >= 2 else None
        if not m or len(t) > 3:
            return Erkannt(status=404, lang=lang)
        liga = t[1] if len(t) == 3 else ""
        return Erkannt(Ziel("spiel", lang, liga=liga, spiel_id=int(m.group(1)), slug=t[-1]), lang=lang)
    if len(t) == 1:
        return Erkannt(Ziel(art, lang), lang=lang)
    return Erkannt(status=404, lang=lang)


def _alte_adresse(t: list[str]) -> Erkannt:
    """Adressen der Vorschau bis 0.20 (ohne Sprachverzeichnis) leiten dauerhaft weiter."""
    if t[0] == "spieltag" and len(t) == 1:
        return Erkannt(weiter=pfad(Ziel("spieltag", liga=W.STANDARD_LIGA)), status=301)
    if t[0] == "spieltag" and len(t) == 2 and W.liga_aus_slug(t[1]):
        return Erkannt(weiter=pfad(Ziel("spieltag", liga=t[1])), status=301)
    if t[0] == "spiel" and len(t) == 2 and t[1].isdigit():
        return Erkannt(Ziel("spiel", spiel_id=int(t[1])), status=301)     # Ziel braucht die Daten (Slug)
    if len(t) == 1 and t[0] in INHALTSSEITEN:
        return Erkannt(weiter=pfad(Ziel(t[0])), status=301)
    return Erkannt(status=404)
