"""Datensatz der Seite Matchdetail (seit 0.18; Entwurf 2i „Spiel_P1“, Übergabe Abschnitt 7, Konzept 08).

Je Paarung des Spielplans eine Seite unter /spiel/<Spiel-ID von API-Football>. Die Werte kommen unverändert aus dem
Rechenkern (core/kpis.py, F6); hier wird nur zusammengestellt und eingestuft. Codes statt Texte (Übergabe 9.1).

Festlegungen Carsten 17.11.2026:
- Q1  Erwartungswert = Hauptwert der Kennzahl. Nur bei Gelben Karten ist er die Summe der Teamwerte (zweiteilige
      Leiste „Heim + Gast“); bei allen anderen der Mittelwert, dargestellt als „Je Mannschaft“.
- Q2  Über 2,5 Tore: Vergleichswert ist die feste Marke 2,5 (kein Ligaschnitt), Erwartungswert in Toren.
- Q4  Einzelne vorläufige Kennzahl: ohne Stufe, schraffiert, unter „Im Normalbereich“. Das Spiel hat nur dann
      „zu wenig Daten“ (bis 0.19.1 „nicht gewertet“), wenn alle Kennzahlen vorläufig sind (F2).
- Q5  Gespieltes Spiel: Endstand bzw. „Gespielt“ statt Anstoss, Werte wie vor dem Spiel.

Seit 0.20 (Entscheidungsprotokoll 19.11.2026, Nr. 2, 2a, 4a): gespielt ab Anpfiff + 2 Stunden; ab dem Anstoss die
Werte des Schnappschusses (Hinweis, wenn sie nachträglich berechnet wurden oder das Ergebnis korrigiert wurde); vor
dem Anstoss statt der Kennzahlen „Werte ab …“, solange ein Vorspiel aussteht.
"""

from __future__ import annotations

from core import anzeige as A
from core import schnappschuss as S
from core.fixtures import INACTIVE_STATUS
from core.kpis import LEVELS, RANK, MatchKpis
from core.top import TOP_KPIS

from . import einstellungen as W
from .daten import Daten, Zeitpunkt
from .spieltag import SONDERSPIEL, _termin

# Kennzahlen in der festen Reihenfolge des Datensatzes (Übergabe 4.3) mit Symbol des Entwurfs
ICONS = {"kpi02": "bars", "kpi03": "target", "kpi04": "card", "kpi05": "flag", "kpi06": "clock", "kpi07": "clock2",
         "kpi08": "both", "kpi09": "goal"}
MARKE_UEBER25 = 2.5          # KPI 03: feste Marke (Regelwerk, Abschnitt 5)


def _f(wert) -> float | None:
    return None if wert is None else float(wert)


def kennzahl(key: str, r) -> dict:
    """Eine Kennzahl für das Matchdetail."""
    abw = _f(r.abweichung_rund) if r is not None else None
    vorl = r is None or r.vorlaeufig or abw is None
    if vorl:
        stufe = "zu_wenig_daten"
    elif r.anomalie in LEVELS:
        stufe = r.anomalie                     # Signalqualität stark / mittel / gering (seit 0.20)
    else:
        stufe = "normal"
    return {
        "kpi": key, "icon": ICONS[key],
        "abweichung": abw,
        "betrag": abs(abw) if abw is not None else 0.0,
        "richtung": None if abw is None else ("hoch" if abw >= 0 else "tief"),
        "stufe": stufe,
        "erwartung": _f(r.hauptwert_rund) if r is not None else None,
        "heim": _f(r.heim.wert_rund) if r is not None else None,
        "gast": _f(r.auswaerts.wert_rund) if r is not None else None,
        "vergleich": MARKE_UEBER25 if key == "kpi03" else (_f(r.referenz.wert_rund) if r is not None and r.referenz else None),
        "vergleich_art": "marke" if key == "kpi03" else "liga",
        "summe": key == "kpi04",                       # Q1: nur Gelbe Karten sind eine Summe der Teamwerte
        "prozent": bool(getattr(r, "prozent", False)),
    }


def form(ft) -> list[str]:
    """Formkurve (KPI 01): fünf Einträge alt → neu, „-“ = noch kein Spiel."""
    if ft is None:
        return ["-"] * 5
    return ["-" if x not in ("S", "U", "N") else x for x in ft.form]


def spiel_daten(daten: Daten, spiel_id: int, zp: Zeitpunkt) -> dict | None:
    """Datensatz einer Paarung; None, wenn die Spiel-ID nicht im Spielplan steht."""
    treffer = daten.spiel(spiel_id)
    if treffer is None:
        return None
    liga, row = treffer
    web = next((lg for lg in W.LIGEN if lg.name == liga), None)
    if web is None:
        return None
    b = daten.bestand()
    werte = daten.werte(liga, row, zp)
    kpis: MatchKpis | None = werte.kpis
    ergebnisse = daten.ergebnisse(liga, zp.bis)
    score = ergebnisse.get((row.saison, row.heim, row.gast))
    gate = A.values_from(daten.spielplan(liga), row, zp.jetzt, ergebnisse)
    ohne = gate is not None or werte.quelle == S.WAITING          # „Werte ab …“ bzw. Schnappschuss wartet

    if row.status in INACTIVE_STATUS:
        zustand = "status"
    elif score is not None or zp.jetzt >= A.played_from(row):
        zustand = "gespielt"
    else:
        zustand = "offen"

    kennzahlen = [kennzahl(k, getattr(kpis, k, None) if kpis is not None else None) for k in TOP_KPIS]
    if zustand == "status" or ohne:             # verschoben, abgesagt … bzw. noch ohne Werte (wie Kachel, F5)
        kennzahlen = []
    ohne_werte = all(k["erwartung"] is None for k in kennzahlen)
    zu_wenig_daten = all(k["stufe"] == "zu_wenig_daten" for k in kennzahlen)
    auffaellig = sorted((k for k in kennzahlen if k["stufe"] in LEVELS), key=lambda k: (-RANK[k["stufe"]], -k["betrag"]))
    uebrige = sorted((k for k in kennzahlen if k["stufe"] not in LEVELS), key=lambda k: -k["betrag"])
    gewertet = [k for k in kennzahlen if k["stufe"] != "zu_wenig_daten"]
    groesste = max(gewertet, key=lambda k: k["betrag"]) if gewertet else None

    return {
        "seite": "spiel", "id": int(spiel_id), "liga": web.slug, "liga_key": web.key,
        "saison": row.saison, "spieltag": int(row.spieltag),
        "heim": row.heim, "gast": row.gast,
        "heim_id": b.team_ids.get((liga, row.heim)), "gast_id": b.team_ids.get((liga, row.gast)),
        "datum": row.datum_von.isoformat(),
        "anstoss": row.anstoss_zeit.strftime("%H:%M") if _termin(row) not in ("zeit_offen", "ohne_zeit") else None,
        "termin": _termin(row),
        "status": row.status if zustand == "status" else None,
        "sonderspiel": SONDERSPIEL.get(row.hinweis) if row.status not in INACTIVE_STATUS else None,
        "zustand": zustand,
        "ergebnis": list(score) if score else None,
        "form_heim": form(kpis.form_home if kpis is not None else None),
        "form_gast": form(kpis.form_away if kpis is not None else None),
        "bewertung": "status" if zustand == "status" else "werte_ab" if ohne else
                     "zu_wenig_daten" if zu_wenig_daten else "auffaellig" if auffaellig else "normal",
        "werte_ab": gate.ab.isoformat() if gate is not None and gate.ab else None,
        "ergebnis_vom": gate.ergebnis_vom.isoformat() if gate is not None and gate.ergebnis_vom else None,
        "nachtraeglich": zustand == "gespielt" and werte.quelle in (S.LATE, S.WAITING),
        "korrigiert": zustand == "gespielt" and werte.korrigiert,
        "ohne_werte": ohne_werte,
        "auffaellig": auffaellig,
        "uebrige": uebrige,
        "anzahl_gewertet": len(gewertet),
        "groesste": groesste,
        "jetzt": zp.jetzt.isoformat(timespec="minutes"),
        "stand": zp.stand.isoformat(timespec="minutes") if zp.stand else None,
        "zeitreise": zp.zeitreise,
    }
