"""Datensatz der Startseite (seit 0.18; Entwurf 1d „Main_P1“, Übergabe Abschnitt 5, Konzept 08).

Das Ranking „Die auffälligsten Spiele“ ist genau die Auswahl der Top Anomalien im Dashboard (F6: das Dashboard ist der
Datenlieferant): je Liga der zeitlich nächste Block (core/anzeige.top_block), nur Spiele vor dem Anpfiff und mit
Werten, Auswahl und Rangfolge nach Regelwerk 2.6 (core/top.select_top, höchstens 4 Einträge, einer je Spiel).

Zustände (Übergabe 5.3): liste · keine (Spieltag steht an, aber keine Abweichung) · spielpause / winterpause (keine
Liga spielt in den nächsten 14 Tagen) · sommerpause (keine Liga hat ein angesetztes Spiel) · saisonstart (neue Saison
angesetzt) · unbekannt (Datenstand veraltet, Pause nicht belegbar, S9). Dazu die Warnbox bei veraltetem Datenstand.
"""

from __future__ import annotations

from core import anzeige as A
from core.kpis import STRONG
from core.top import Candidate, select_top

from . import einstellungen as W
from .daten import Daten, Zeitpunkt
from .spieltag import _termin


def _ligen_in_reihenfolge(daten: Daten) -> list[W.WebLiga]:
    """Ligen in der Reihenfolge der Konfiguration (wie im Dashboard: entscheidet bei Gleichstand im Ranking)."""
    namen = list(daten.bestand().leagues)
    return sorted(W.LIGEN, key=lambda lg: namen.index(lg.name) if lg.name in namen else 99)


def start_daten(daten: Daten, zp: Zeitpunkt) -> dict:
    b = daten.bestand()
    heute = zp.jetzt.date()
    seite = {"seite": "start", "jetzt": zp.jetzt.isoformat(timespec="minutes"),
             "stand": zp.stand.isoformat(timespec="minutes") if zp.stand else None, "zeitreise": zp.zeitreise,
             "gesperrt": b.gesperrt, "veraltet": A.is_stale(zp.import_tag, heute),
             "zustand": "liste", "pause": None, "ranking": []}
    if b.gesperrt:
        seite["zustand"] = "gesperrt"
        return seite

    kandidaten, teilnahme, naechste = [], False, []
    for order, web in enumerate(_ligen_in_reihenfolge(daten)):
        fixtures = b.fx.leagues.get(web.name)
        if fixtures is None or fixtures.empty:
            continue
        plan = daten.spielplan(web.name)
        runden = A.rounds(plan)
        nxt, prev = A.next_round(runden, heute), A.previous_round(runden, heute)
        if nxt is not None:
            naechste.append((nxt.first, order, web, nxt, prev))
        block = A.top_block(fixtures, zp.jetzt, zp.import_tag)
        if block is None or not block.takes_part:
            continue
        teilnahme = True
        ergebnisse = daten.ergebnisse(web.name, zp.bis)
        for g in block.games.itertuples():
            if A.values_gate(plan, g, zp.jetzt, ergebnisse) is not None:    # wie Dashboard: nur Spiele mit Werten
                continue
            k = daten.kpis(web.name, g.saison, int(g.spieltag), zp.bis).get(int(g.reihenfolge))
            kandidaten.append(Candidate(web.name, order, g.saison, int(g.spieltag), g.datum_von, int(g.reihenfolge),
                                        g.heim, g.gast, g.status, k, ""))
    for e in select_top(kandidaten):
        c = e.candidate
        web = next(lg for lg in W.LIGEN if lg.name == c.league)
        row = _zeile(daten, c.league, c.file_order)
        seite["ranking"].append({
            "rang": e.rank, "liga": web.slug, "liga_key": web.key, "spieltag": c.matchday,
            "id": None if row is None or row.api_id is None or row.api_id != row.api_id else int(row.api_id),
            "heim": c.home, "gast": c.away, "datum": c.datum_von.isoformat(),
            "anstoss": row.anstoss if row is not None and _termin(row) == "bestaetigt" else None,
            "termin": _termin(row) if row is not None else "bestaetigt",
            "kpi": e.kpi_key, "abweichung": float(e.result.abweichung_rund),
            "stufe": "stark" if e.result.anomalie == STRONG else "leicht",
            "richtung": "hoch" if e.result.abweichung_rund >= 0 else "tief",
        })
    if seite["ranking"]:
        return seite
    if teilnahme:
        seite["zustand"] = "keine"
        seite["pause"] = {"art": "keine", "datum": None, "tage": None, "liga": W.STANDARD_LIGA}
        return seite

    # Keine Liga spielt in den nächsten 14 Tagen: Pause (Übergabe 5.3)
    seite["zustand"] = "pause"
    if not naechste:
        seite["pause"] = {"art": "sommerpause", "datum": None, "tage": None, "liga": W.STANDARD_LIGA}
        return seite
    erst, _order, web, nxt, prev = min(naechste, key=lambda x: (x[0], x[1]))
    if seite["veraltet"]:
        art = "unbekannt"                                    # S9: keine Pausenhinweise bei veraltetem Datenstand
    elif all(p is None or n.saison != p.saison for _, _, _, n, p in naechste):
        art = "saisonstart"
    elif prev is not None and A._has_christmas(prev.last, nxt.first):
        art = "winterpause"
    else:
        art = "spielpause"
    seite["pause"] = {"art": art, "datum": erst.isoformat(), "tage": (erst - heute).days, "liga": web.slug}
    return seite


def _zeile(daten: Daten, liga: str, reihenfolge: int):
    plan = daten.spielplan(liga)
    if plan is None:
        return None
    treffer = plan[plan["reihenfolge"] == reihenfolge]
    return next(treffer.itertuples()) if len(treffer) else None
