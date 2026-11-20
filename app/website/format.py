"""Zahlen, Datum und Uhrzeit je Sprache (Übergabe 3 „Zahlenformat“ und 9.1 Punkt 4).

Jetzt nur Deutsch. Die Schreibweise je Sprache steht in einer Tabelle; eine neue Sprache bekommt eine eigene Zeile.
Die Seiten werden auf dem Server fertig erzeugt, darum formatiert Python (nicht der Browser mit Intl) – mit
derselben Wirkung für die Besucher.

Verbindlich (Übergabe 3): Prozent mit zwei Nachkommastellen und Komma, Leerzeichen vor „%“, echtes Minus „−“
(U+2212), Pluszeichen immer, bei genau 0 kein Vorzeichen. Werte kommen bereits kaufmännisch gerundet aus dem
Rechenkern (abweichung_rund); hier wird nur noch geschrieben, nicht gerundet.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

MINUS = "−"

FORMATE = {
    "de": {
        "wochentage": ("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"),
        "komma": ",",
        "prozent": "{zahl} %",
        "uhr": "{zeit} Uhr",
    },
}


def _f(lang: str) -> dict:
    return FORMATE.get(lang, FORMATE["de"])


def tag(d: date, lang: str = "de") -> str:
    """„Sa 21.11.“"""
    return f"{_f(lang)['wochentage'][d.weekday()]} {d:%d.%m.}"


def tag_jahr(d: date, lang: str = "de") -> str:
    """„Sa 21.11.2026“"""
    return f"{_f(lang)['wochentage'][d.weekday()]} {d:%d.%m.%Y}"


def datum_kurz(d: date) -> str:
    """„21.11.“"""
    return f"{d:%d.%m.}"


def tag_monat(d: date) -> str:
    """„5.12.“ (Kachel „Werte ab 5.12.“, ohne führende Null; seit 0.20)"""
    return f"{d.day}.{d.month}."


def zeitraum(von: date, bis: date) -> str:
    """„20.11. – 22.11.2026“; ein Tag: „20.11.2026“; über den Jahreswechsel: „28.12.2026 – 03.01.2027“."""
    if von == bis:
        return f"{von:%d.%m.%Y}"
    if von.year == bis.year:
        return f"{von:%d.%m.} – {bis:%d.%m.%Y}"
    return f"{von:%d.%m.%Y} – {bis:%d.%m.%Y}"


def uhrzeit(text: str | None) -> str:
    return text or ""


def stand(zeit: datetime | None, lang: str = "de") -> str:
    """Fusszeile „Stand“: „Mo 16.11.2026, 04:05 Uhr“."""
    if zeit is None:
        return "–"
    return f"{tag_jahr(zeit.date(), lang)}, " + _f(lang)["uhr"].format(zeit=f"{zeit:%H:%M}")


def prozent(wert, lang: str = "de") -> str:
    """„+47,36 %“, „−22,07 %“, „0,00 %“. wert = bereits gerundete Zahl (float oder Decimal) oder None."""
    if wert is None:
        return "–"
    d = Decimal(str(wert)).quantize(Decimal("0.01"))
    zeichen = "" if d == 0 else ("+" if d > 0 else MINUS)
    zahl = f"{abs(d):.2f}".replace(".", _f(lang)["komma"])
    return _f(lang)["prozent"].format(zahl=zeichen + zahl)


def zahl(wert, lang: str = "de", einheit: str = "") -> str:
    """„3,40“ bzw. „64,00 %“ (zwei Nachkommastellen, Werte kommen gerundet aus dem Rechenkern); None -> „–“."""
    if wert is None:
        return "–"
    d = Decimal(str(wert)).quantize(Decimal("0.01"))
    text = f"{d:.2f}".replace(".", _f(lang)["komma"]).replace("-", MINUS)
    return _f(lang)["prozent"].format(zahl=text) if einheit == "%" else text


def ergebnis(heim: int, gast: int) -> str:
    """„2 : 1“ (Übergabe 6.2)"""
    return f"{heim} : {gast}"


def wochenende(d: date, lang: str = "de") -> str | None:
    """Platzhalter-Termin am Wochenende: „06./07.02.“ (Sa/So); sonst None."""
    from datetime import timedelta
    if d.weekday() not in (5, 6):
        return None
    sa = d if d.weekday() == 5 else d - timedelta(days=1)
    so = sa + timedelta(days=1)
    erst = f"{sa:%d.}" if sa.month == so.month else f"{sa:%d.%m.}"
    return f"{erst}/{so:%d.%m.}"
