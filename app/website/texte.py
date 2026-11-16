"""Texte der Website aus der Sprachdatei (Übergabe 9.1, Punkte 1 und 3).

Kein sichtbarer Text steht im Code oder in den Vorlagen: Jeder hat einen Schlüssel („spieltag.h1“) und kommt aus
texte/<sprache>.json. Platzhalter in {geschweiften Klammern}; Mehrzahl als eigene Varianten (null/eins/mehr).
Fehlt ein Text in einer Sprache, gilt Deutsch (Fallback). Fehlt er auch dort, ist das ein Programmfehler (KeyError)
– die Tests prüfen, dass jeder benutzte Schlüssel vorhanden ist.
"""

from __future__ import annotations

import json
from functools import lru_cache

from .einstellungen import SPRACHE, TEXTE

FALLBACK = "de"


@lru_cache(maxsize=8)
def _laden(lang: str) -> dict:
    pfad = TEXTE / f"{lang}.json"
    return json.loads(pfad.read_text(encoding="utf-8")) if pfad.exists() else {}


def _suchen(daten: dict, schluessel: str):
    wert = daten
    for teil in schluessel.split("."):
        if not isinstance(wert, dict) or teil not in wert:
            return None
        wert = wert[teil]
    return wert


def roh(schluessel: str, lang: str = SPRACHE):
    """Eintrag zum Schlüssel (Text oder Gruppe), mit Fallback auf Deutsch."""
    wert = _suchen(_laden(lang), schluessel)
    if wert is None and lang != FALLBACK:
        wert = _suchen(_laden(FALLBACK), schluessel)
    if wert is None:
        raise KeyError(f"Text fehlt in der Sprachdatei: {schluessel}")
    return wert


def t(schluessel: str, lang: str = SPRACHE, **werte) -> str:
    """Text mit eingesetzten Werten: t("spieltag.nummer", n=10) -> „10. Spieltag“."""
    text = roh(schluessel, lang)
    if not isinstance(text, str):
        raise KeyError(f"Schlüssel ist eine Gruppe, kein Text: {schluessel}")
    return text.format(**werte) if werte else text


def tn(schluessel: str, n: int, lang: str = SPRACHE, **werte) -> str:
    """Mehrzahl: Variante „null“ (falls vorhanden), „eins“ oder „mehr“; n steht als {n} zur Verfügung."""
    gruppe = roh(schluessel, lang)
    if not isinstance(gruppe, dict):
        raise KeyError(f"Schlüssel hat keine Mehrzahl-Varianten: {schluessel}")
    variante = "null" if n == 0 and "null" in gruppe else "eins" if n == 1 and "eins" in gruppe else "mehr"
    return gruppe[variante].format(n=n, **werte)
