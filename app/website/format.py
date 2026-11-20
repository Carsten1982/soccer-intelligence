"""Zahlen, Datum und Uhrzeit je Sprache (Übergabe 3 „Zahlenformat“ und 9.1 Punkt 4; seit 0.21 Englisch nach dem
Glossar, Abschnitte 1 und 6).

Die Schreibweise je Sprache steht in einer Tabelle; eine neue Sprache bekommt eine eigene Zeile. Die Seiten werden auf
dem Server fertig erzeugt, darum formatiert Python (nicht der Browser mit Intl) – mit derselben Wirkung für die Besucher.

Verbindlich: Prozent mit zwei Nachkommastellen, echtes Minus „−“ (U+2212), Pluszeichen immer, bei genau 0 kein
Vorzeichen. Deutsch mit Komma und Leerzeichen vor „%“ („+47,36 %“), Englisch mit Punkt und ohne Leerzeichen
(„+47.36%“). Datum Deutsch „Sa 21.11.“, Englisch „Sat 21 Nov“; Zeitraum „20.11. – 22.11.2026“ bzw. „20–22 Nov 2026“.
24-Stunden-Uhr. Werte kommen bereits kaufmännisch gerundet aus dem Rechenkern; hier wird nur geschrieben.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

MINUS = "−"
STRICH = "–"          # Halbgeviertstrich für Zeiträume

FORMATE = {
    "de": {
        "wochentage": ("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"),
        "monate": ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
                   "November", "Dezember"),
        "komma": ",",
        "prozent": "{zahl} %",
        "uhr": "{zeit} Uhr",
    },
    "en": {
        "wochentage": ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"),
        "monate": ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                   "November", "December"),
        "komma": ".",
        "prozent": "{zahl}%",
        "uhr": "{zeit}",
    },
}


def _f(lang: str) -> dict:
    return FORMATE.get(lang, FORMATE["de"])


def _mon(d: date, lang: str) -> str:
    """„Nov“ (englische Kurzform: die ersten drei Buchstaben)."""
    return _f(lang)["monate"][d.month - 1][:3]


def tag(d: date, lang: str = "de") -> str:
    """„Sa 21.11.“ / „Sat 21 Nov“"""
    wt = _f(lang)["wochentage"][d.weekday()]
    return f"{wt} {d.day} {_mon(d, lang)}" if lang == "en" else f"{wt} {d:%d.%m.}"


def tag_jahr(d: date, lang: str = "de") -> str:
    """„Sa 21.11.2026“ / „Sat 21 Nov 2026“"""
    return f"{tag(d, lang)} {d.year}" if lang == "en" else f"{tag(d, lang)}{d.year}"


def datum_kurz(d: date, lang: str = "de") -> str:
    """„21.11.“ / „21 Nov“"""
    return f"{d.day} {_mon(d, lang)}" if lang == "en" else f"{d:%d.%m.}"


def tag_monat(d: date, lang: str = "de") -> str:
    """„5.12.“ / „5 Dec“ (Kachel „Werte ab 5.12.“, ohne führende Null; seit 0.20)"""
    return f"{d.day} {_mon(d, lang)}" if lang == "en" else f"{d.day}.{d.month}."


def datum_voll(d: date, lang: str = "de") -> str:
    """„22.11.2026“ / „22 November 2026“ (Fliesstext, Description der Spielseite)"""
    return f"{d.day} {_f(lang)['monate'][d.month - 1]} {d.year}" if lang == "en" else f"{d:%d.%m.%Y}"


def zeitraum(von: date, bis: date, lang: str = "de") -> str:
    """Deutsch „20.11. – 22.11.2026“, ein Tag „20.11.2026“, über den Jahreswechsel „28.12.2026 – 03.01.2027“.
    Englisch „20–22 Nov 2026“, „30 Nov – 2 Dec 2026“, „28 Dec 2026 – 3 Jan 2027“, ein Tag „20 Nov 2026“."""
    if lang == "en":
        if von == bis:
            return f"{von.day} {_mon(von, lang)} {von.year}"
        if von.year != bis.year:
            return f"{von.day} {_mon(von, lang)} {von.year} {STRICH} {bis.day} {_mon(bis, lang)} {bis.year}"
        if von.month == bis.month:
            return f"{von.day}{STRICH}{bis.day} {_mon(bis, lang)} {bis.year}"
        return f"{von.day} {_mon(von, lang)} {STRICH} {bis.day} {_mon(bis, lang)} {bis.year}"
    if von == bis:
        return f"{von:%d.%m.%Y}"
    if von.year == bis.year:
        return f"{von:%d.%m.} {STRICH} {bis:%d.%m.%Y}"
    return f"{von:%d.%m.%Y} {STRICH} {bis:%d.%m.%Y}"


def uhrzeit(text: str | None) -> str:
    return text or ""


def stand(zeit: datetime | None, lang: str = "de") -> str:
    """Fusszeile „Datenstand“: „Mo 16.11.2026, 04:05 Uhr“ / „Mon 16 Nov 2026, 04:05“."""
    if zeit is None:
        return STRICH
    return f"{tag_jahr(zeit.date(), lang)}, " + _f(lang)["uhr"].format(zeit=f"{zeit:%H:%M}")


def prozent(wert, lang: str = "de") -> str:
    """„+47,36 %“ / „+47.36%“, „−22,07 %“, „0,00 %“. wert = bereits gerundete Zahl (float oder Decimal) oder None."""
    if wert is None:
        return STRICH
    d = Decimal(str(wert)).quantize(Decimal("0.01"))
    zeichen = "" if d == 0 else ("+" if d > 0 else MINUS)
    zahl_text = f"{abs(d):.2f}".replace(".", _f(lang)["komma"])
    return _f(lang)["prozent"].format(zahl=zeichen + zahl_text)


def zahl(wert, lang: str = "de", einheit: str = "") -> str:
    """„3,40“ / „3.40“ bzw. „64,00 %“ / „64.00%“ (zwei Nachkommastellen); None -> „–“."""
    if wert is None:
        return STRICH
    d = Decimal(str(wert)).quantize(Decimal("0.01"))
    text = f"{d:.2f}".replace(".", _f(lang)["komma"]).replace("-", MINUS)
    return _f(lang)["prozent"].format(zahl=text) if einheit == "%" else text


def ergebnis(heim: int, gast: int) -> str:
    """„2 : 1“ (Übergabe 6.2, in beiden Sprachen gleich; Spielseite „Endstand 2 : 1“)"""
    return f"{heim} : {gast}"


def ergebnis_kurz(heim: int, gast: int) -> str:
    """„2:1“ für Chips auf Kacheln und im Ranking („Gespielt · 2:1“, Glossar Abschnitt 19)"""
    return f"{heim}:{gast}"


def wochenende(d: date, lang: str = "de") -> str | None:
    """Platzhalter-Termin am Wochenende: „06./07.02.“ bzw. „6/7 Feb“ (Sa/So); sonst None."""
    if d.weekday() not in (5, 6):
        return None
    sa = d if d.weekday() == 5 else d - timedelta(days=1)
    so = sa + timedelta(days=1)
    if lang == "en":
        if sa.month == so.month:
            return f"{sa.day}/{so.day} {_mon(so, lang)}"
        return f"{sa.day} {_mon(sa, lang)}/{so.day} {_mon(so, lang)}"
    erst = f"{sa:%d.}" if sa.month == so.month else f"{sa:%d.%m.}"
    return f"{erst}/{so:%d.%m.}"
