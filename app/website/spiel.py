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

Seit 0.23 (Entwurf „2k final“, Beschlüsse 25–32 vom 24.11.2026): jede Kennzahl hat einen Fall A–D
- A Schwelle überschritten (Signalqualität), B Schwelle in dieser Richtung vorhanden, nicht erreicht, C für diese
  Richtung keine Schwelle in der Liga, D zu wenig Daten. Der Fall kommt aus der Schwellendatei je Kennzahl und Richtung
  (Punkt für die Entwicklung 9), nicht aus der Abweichung allein.
- Grenzwert = Ligadurchschnitt (bei „Über 2,5 Tore“ die Marke 2,5) × (1 ± Schwelle), exakt gerechnet, kaufmännisch
  auf zwei Stellen; gezeigt in Richtung der Abweichung (Entscheid Carsten 24.11.2026).

Seit 0.20 (Entscheidungsprotokoll 19.11.2026, Nr. 2, 2a, 4a): gespielt ab Anpfiff + 2 Stunden; ab dem Anstoss die
Werte des Schnappschusses (Hinweis, wenn sie nachträglich berechnet wurden oder das Ergebnis korrigiert wurde); vor
dem Anstoss statt der Kennzahlen „Werte ab …“, solange ein Vorspiel aussteht.
"""

from __future__ import annotations

from fractions import Fraction

from core import anzeige as A
from core import auswertung as AW
from core import schnappschuss as S
from core.fixtures import INACTIVE_STATUS
from core.kpis import LEVELS, RANK, SAMPLE, MatchKpis, round_display
from core.top import TOP_KPIS

from . import adressen as AD
from . import einstellungen as W
from .daten import Daten, Zeitpunkt
from .spieltag import SONDERSPIEL, _termin, spielzeile

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
    signal = _signal(r, abw)
    fall = "D" if vorl else "A" if stufe in LEVELS else "B" if signal is not None else "C"
    return {
        "kpi": key, "icon": ICONS[key],
        "fall": fall,
        "grenzwert": _grenzwert(key, r, abw, signal),
        "schwelle_ganz": None if signal is None else _ganz(signal.schwelle),
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
        "schwelle": _schwelle(r, abw),                 # seit 0.21 (Entwurf Spiel_P1): Schwelle in Richtung der Abweichung
        "hat_schwelle": bool(getattr(r, "schwellen", None) is not None
                             and (r.schwellen.positiv is not None or r.schwellen.negativ is not None)),
    }


def _signal(r, abw):
    """Schwelle (Signal) der Liga in Richtung der Abweichung; None, wenn es in dieser Richtung keine gibt."""
    schwellen = getattr(r, "schwellen", None)
    if schwellen is None or abw is None:
        return None
    return schwellen.positiv if abw >= 0 else schwellen.negativ


def _schwelle(r, abw) -> float | None:
    """Schwelle der Liga in Richtung der Abweichung (positiv: über +x %, negativ: unter −x %); None ohne Schwelle."""
    signal = _signal(r, abw)
    return float(signal.schwelle) if signal is not None else None


def _ganz(wert) -> int | float:
    """Schwelle für den Satz: ganze Zahl wie in der Schwellendatei (35, nicht 35,00)."""
    f = float(wert)
    return int(f) if f == int(f) else f


def _grenzwert(key: str, r, abw, signal) -> float | None:
    """Grenzwert in Richtung der Abweichung: Vergleichswert × (1 ± Schwelle / 100), exakt, auf zwei Stellen."""
    if signal is None or r is None:
        return None
    ref = getattr(r, "referenz", None)
    if key == "kpi03":
        basis = Fraction(MARKE_UEBER25)
    elif ref is not None and getattr(ref, "wert", None) is not None:
        basis = Fraction(ref.wert)                                  # exakt aus dem Rechenkern
    elif ref is not None and getattr(ref, "wert_rund", None) is not None:
        basis = Fraction(str(ref.wert_rund))                        # Rückfall: gerundeter Wert
    else:
        basis = None
    if basis is None:
        return None
    faktor = 1 + Fraction(str(signal.schwelle)) / 100 * (1 if abw >= 0 else -1)
    return float(round_display(basis * faktor))


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
    # Seit 0.25 (Release_08, Beschluss 35): Liegt der Endstand vor, zeigt die Seite die Auswertung (gleiche Adresse).
    auswertung = zustand == "gespielt" and score is not None
    if ohne:                                    # ohne Erwartungswerte (Werte ab …, Schnappschuss wartet)
        kennzahlen = [kennzahl(k, None) for k in TOP_KPIS] if auswertung else []
    if zustand == "status":                     # verschoben, abgesagt …: nie Werte (wie Kachel, F5)
        kennzahlen = []
    spiel = spielzeile(daten, liga, row.saison, row.heim, row.gast, zp.bis) if auswertung else None
    for k in kennzahlen:
        r = getattr(kpis, k["kpi"], None) if kpis is not None and not ohne else None
        k["ist"] = AW.ist_wert(k["kpi"], spiel) if spiel is not None else None
        ref = getattr(getattr(r, "referenz", None), "wert", None)
        k["ergebnis"] = AW.bewertung(k["kpi"], k["richtung"], k["ist"], ref) if auswertung and k["fall"] == "A" else None
    ohne_werte = all(k["erwartung"] is None for k in kennzahlen)
    zu_wenig_daten = all(k["stufe"] == "zu_wenig_daten" for k in kennzahlen)
    auffaellig = sorted((k for k in kennzahlen if k["stufe"] in LEVELS), key=lambda k: (-RANK[k["stufe"]], -k["betrag"]))
    uebrige = sorted((k for k in kennzahlen if k["stufe"] not in LEVELS), key=lambda k: -k["betrag"])
    gewertet = [k for k in kennzahlen if k["stufe"] != "zu_wenig_daten"]
    groesste = max(gewertet, key=lambda k: k["betrag"]) if gewertet else None

    # „Zu wenig Daten“ nennt das Team bzw. die Teams mit weniger als 10 Spielen (Beschluss 24, Glossar 20a/20b)
    neu = []
    if kpis is not None:
        r0 = next((getattr(kpis, k, None) for k in TOP_KPIS if getattr(kpis, k, None) is not None), None)
        if r0 is not None:
            neu = [t.team for t in (r0.heim, r0.auswaerts)
                   if getattr(t, "spiele", None) is not None and t.spiele < SAMPLE and getattr(t, "team", None)]

    halbzeit = None
    if spiel is not None:
        try:
            halbzeit = [int(spiel.h1h), int(spiel.h1a)] if spiel.h1h == spiel.h1h and spiel.h1a == spiel.h1a else None
        except (AttributeError, TypeError, ValueError):
            halbzeit = None
    korrigiert = zustand == "gespielt" and werte.korrigiert
    if auswertung and not korrigiert:          # seit 0.25 (Beschluss 42): auch geänderte Statistik melden
        league = b.leagues.get(liga)
        korrigiert = league is not None and hasattr(daten, "import_dir") and S.stats_corrected(
            daten.import_dir, league.url, row.saison, S.api_id_of(row), {k["kpi"]: k["ist"] for k in kennzahlen})
    bewertet = [k for k in auffaellig if k.get("ergebnis")]
    bilanz = {"n": len(bewertet), "ok": sum(k["ergebnis"] == AW.BESTAETIGT for k in bewertet),
              "folgt": sum(k["ergebnis"] == AW.FOLGT for k in bewertet)}

    sicht = A.upcoming(b.fx.leagues[liga], zp.jetzt, zp.stand)
    im_fenster = any(int(row.reihenfolge) in set(sec.games["reihenfolge"].astype(int)) for sec in sicht.sections)
    return {
        "seite": "spiel", "id": int(spiel_id), "liga": web.slug, "liga_key": web.key,
        "slug": AD.spiel_slug(row.heim, row.gast, int(spiel_id)),
        "anstoss_zeit": row.anstoss_zeit.isoformat(timespec="minutes"),
        "im_fenster": im_fenster,
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
        "korrigiert": korrigiert,
        "ansicht": "auswertung" if auswertung else "erwartung",
        "halbzeit": halbzeit,
        "statistik_fehlt": auswertung and any(k["ist"] is None for k in kennzahlen),
        "bilanz": bilanz,
        "ohne_werte": ohne_werte,
        "neu_in_liga": neu,
        "auffaellig": auffaellig,
        "uebrige": uebrige,
        "anzahl_gewertet": len(gewertet),
        "groesste": groesste,
        "jetzt": zp.jetzt.isoformat(timespec="minutes"),
        "stand": zp.stand.isoformat(timespec="minutes") if zp.stand else None,
        "zeitreise": zp.zeitreise,
    }
