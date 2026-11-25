"""Auswertung nach dem Spiel (seit 0.25; Design Release_08, Abschnitt 4.2; KPI-Regelwerk 11.1).

Vergleicht den tatsächlichen Wert eines gespielten Spiels mit dem Ligadurchschnitt, der **vor** dem Spiel galt (aus dem
Schnappschuss). Es ist dieselbe Regel wie in der Ergebniskontrolle der Sensitivitätsanalyse (core/simulation._event),
daraus ist die Signalqualität berechnet; ein Test prüft, dass beide immer gleich entscheiden (Beschluss Carsten
25.11.2026: Vergleich mit dem Ligadurchschnitt, nicht mit dem Grenzwert).

- Bestätigt wird nur eine Auffälligkeit (Fall A). Richtung „mehr“: tatsächlicher Wert strikt über dem Vergleichswert,
  „weniger“: strikt darunter. Gleichstand zählt in keiner Richtung (= nicht bestätigt).
- „Über 2,5 Tore“: Vergleichswert ist die feste Marke 2,5 (mindestens 3 bzw. höchstens 2 Tore).
- „Beide Teams treffen“: tatsächlicher Wert 100 (beide trafen) oder 0, verglichen mit dem Ligadurchschnitt in %.
- Fehlt der tatsächliche Wert: keine Bewertung („Bewertung folgt“). Ein fehlender Wert zählt nie als 0.
- Gerechnet wird ungerundet (Brüche); die tatsächlichen Werte sind ganze Zahlen.
"""

from __future__ import annotations

from fractions import Fraction

from .simulation import ACTUAL, OVER_MARK

BESTAETIGT, NICHT_BESTAETIGT, FOLGT = "bestaetigt", "nicht_bestaetigt", "folgt"


def ist_wert(kpi: str, spiel) -> int | None:
    """Tatsächlicher Wert im Spiel (Zeile der aufbereiteten Datenbank, core.kpis.prepare_league); None = fehlt.
    „Beide Teams treffen“: 1 = beide trafen, 0 = nicht beide (ohne Faktor 100)."""
    per_game, _scale = ACTUAL[kpi]
    return per_game(spiel)


def bewertung(kpi: str, richtung: str | None, ist: int | None, referenz) -> str | None:
    """Ergebnis einer Auffälligkeit nach dem Spiel. richtung = "hoch" (mehr) / "tief" (weniger); referenz =
    Ligadurchschnitt vor dem Spiel (exakt, Fraction oder Zahl). None ohne Richtung oder ohne Vergleichswert."""
    vergleich = OVER_MARK if kpi == "kpi03" else referenz
    if richtung not in ("hoch", "tief") or vergleich is None:
        return None
    if ist is None:
        return FOLGT
    _per_game, scale = ACTUAL[kpi]
    wert = Fraction(ist * scale)
    vergleich = Fraction(vergleich) if not isinstance(vergleich, Fraction) else vergleich
    getroffen = wert > vergleich if richtung == "hoch" else wert < vergleich
    return BESTAETIGT if getroffen else NICHT_BESTAETIGT
