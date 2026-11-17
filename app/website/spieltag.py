"""Datensatz der Seite Spieltag (Konzept 08, Abschnitt 5; Übergabe der Frontend-Entwürfe, Abschnitt 6).

Ergebnis ist ein Wörterbuch mit Codes statt Texten (Übergabe 9.1 Punkt 2), als JSON abrufbar. Welche Spiele
erscheinen, entscheidet core/anzeige.py (wie im Dashboard), die Werte und Stufen der Rechenkern (F6).

Einstufung je Partie (Übergabe 6.4: Status > Stufe > Normal, dazu „gespielt“ und „nicht gewertet“):
  status          verschoben, abgesagt, abgebrochen, ausgesetzt, gewertet (F5)
  gespielt        Ergebnis in der Datenbank oder Anstoss vorbei („Ergebnis folgt“)
  nicht_gewertet  alle Kennzahlen vorläufig oder keine Werte (F2: „Nicht gewertet“ = „vorläufig“)
  stark / leicht  mindestens eine nicht vorläufige Kennzahl mit starker bzw. leichter Abweichung
  ohne            sonst
"""

from __future__ import annotations

from datetime import date

from core import anzeige as A
from core.fixtures import HINT_CATCHUP, HINT_EARLY, INACTIVE_STATUS, TERMIN_PROVISIONAL, TERMIN_TIME_OPEN
from core.kpis import LIGHT, STRONG, MatchKpis
from core.top import TOP_KPIS

from . import einstellungen as W
from .daten import Bestand, Daten, Zeitpunkt

# Sortierung wie im Entwurf 3d (Skript renderVals): Stark → Leicht → ohne Auffälligkeit → alles andere (nicht
# gewertet, Status, gespielt) in einer Gruppe; innerhalb Stark/Leicht nach Betrag, sonst nach Anstoss.
REIHENFOLGE = {"stark": 0, "leicht": 1, "ohne": 2, "nicht_gewertet": 3, "status": 3, "gespielt": 3}
SONDERSPIEL = {HINT_CATCHUP: "nachholspiel", HINT_EARLY: "vorgezogen"}
TERMIN = {TERMIN_TIME_OPEN: "zeit_offen", TERMIN_PROVISIONAL: "vorlaeufig"}
PAUSE = {A.WINTER: "winterpause", A.BREAK: "spielpause", A.SUMMER: "sommerpause", A.SEASON_START: "saisonstart"}


# --- Einstufung einer Partie ---------------------------------------------------------------------------

def einstufen(row, kpis: MatchKpis | None, jetzt, ergebnisse: dict) -> dict:
    """art, status, ergebnis und stärkste Abweichung einer Partie (Konzept 5.3)."""
    out = {"art": "ohne", "status": None, "ergebnis": None, "staerkste": None}
    if row.status in INACTIVE_STATUS:
        return {**out, "art": "status", "status": row.status}
    score = ergebnisse.get((row.saison, row.heim, row.gast))
    if score is not None or jetzt >= row.anstoss_zeit:
        return {**out, "art": "gespielt", "ergebnis": list(score) if score else None}
    gewertet = []
    for key in TOP_KPIS:                       # die 8 Kennzahlen KPI 02–09
        r = getattr(kpis, key, None) if kpis is not None else None
        if r is not None and not r.vorlaeufig and r.abweichung_rund is not None:
            gewertet.append((key, r))
    if not gewertet:
        return {**out, "art": "nicht_gewertet"}
    for stufe, art in ((STRONG, "stark"), (LIGHT, "leicht")):
        treffer = [(k, r) for k, r in gewertet if r.anomalie == stufe]
        if treffer:
            k, r = max(treffer, key=lambda kr: abs(kr[1].abweichung_rund))
            return {**out, "art": art, "staerkste": {"kpi": k, "abweichung": float(r.abweichung_rund)}}
    k, r = max(gewertet, key=lambda kr: abs(kr[1].abweichung_rund))
    return {**out, "staerkste": {"kpi": k, "abweichung": float(r.abweichung_rund)}}


def _termin(row) -> str:
    if row.termin in TERMIN:
        return TERMIN[row.termin]
    return "bestaetigt" if A._clock(row.anstoss) else "ohne_zeit"


def spiel_eintrag(row, kpis: MatchKpis | None, jetzt, ergebnisse: dict, team_ids: dict, liga: str) -> dict:
    stufe = einstufen(row, kpis, jetzt, ergebnisse)
    api_id = None if row.api_id is None or row.api_id != row.api_id else int(row.api_id)   # NaN -> None
    return {
        "id": api_id,
        "heim": row.heim, "gast": row.gast,
        "heim_id": team_ids.get((liga, row.heim)), "gast_id": team_ids.get((liga, row.gast)),
        "saison": row.saison, "spieltag": int(row.spieltag),
        "datum": row.datum_von.isoformat(),
        "anstoss": A._clock(row.anstoss).strftime("%H:%M") if A._clock(row.anstoss) else None,
        "termin": _termin(row),
        **stufe,
        "sonderspiel": SONDERSPIEL.get(row.hinweis) if row.status not in INACTIVE_STATUS else None,
        "link": api_id is not None and stufe["art"] != "status",          # F8: verschobene nicht verlinkt
        "_sort": (REIHENFOLGE[stufe["art"]],
                  -abs(stufe["staerkste"]["abweichung"]) if stufe["art"] in ("stark", "leicht") else 0,
                  row.anstoss_zeit, int(row.reihenfolge)),
    }


def sortieren(spiele: list[dict]) -> list[dict]:
    """Konzept 5.4 (seit 0.18 nach Entwurf 3d): Stark → Leicht → Ohne → übrige; Nachhol- und vorgezogene Spiele
    werden wie im Entwurf mitsortiert (bis 0.17: als Gruppe am Ende, Annahme A2)."""
    return sorted(spiele, key=lambda s: s["_sort"])


# --- Seite ------------------------------------------------------------------------------------------------

def _tab(saison: str, spieltag: int, von: date | None, bis: date | None) -> dict:
    return {"saison": saison, "spieltag": spieltag, "von": von.isoformat() if von else None,
            "bis": bis.isoformat() if bis else None, "spiele": []}


def _liga_kopf(fixtures, zp: Zeitpunkt) -> dict:
    """Liga-Kachel: anstehender Spieltag bzw. Pausenname (Annahme A5)."""
    view = A.upcoming(fixtures, zp.jetzt, zp.import_tag)
    pause = None
    if not any(not s.hinweis for s in view.sections) and view.notice is not None and view.notice.kind in PAUSE:
        pause = PAUSE[view.notice.kind]
    return {"spieltag": view.anchor[1] if view.anchor else None, "pause": pause}


def spieltag_daten(daten: Daten, web: W.WebLiga, zp: Zeitpunkt) -> dict:
    """Datensatz der Seite Spieltag für eine Liga zum Zeitpunkt zp."""
    b: Bestand = daten.bestand()
    seite = {"seite": "spieltag", "liga": web.slug, "liga_key": web.key, "jetzt": zp.jetzt.isoformat(timespec="minutes"),
             "stand": zp.stand.isoformat(timespec="minutes") if zp.stand else None, "zeitreise": zp.zeitreise,
             "gesperrt": b.gesperrt, "veraltet": A.is_stale(zp.import_tag, zp.jetzt.date()),
             "zustand": "liste", "pause": None, "ligen": [], "tabs": []}
    for lg in W.LIGEN:
        f = b.fx.leagues.get(lg.name)
        kopf = _liga_kopf(f, zp) if f is not None and not f.empty else {"spieltag": None, "pause": None}
        seite["ligen"].append({"liga": lg.slug, "key": lg.key, **kopf})
    if b.gesperrt:
        seite["zustand"] = "gesperrt"
        return seite
    fixtures = b.fx.leagues.get(web.name)
    if fixtures is None or fixtures.empty:
        seite["zustand"] = "pause"
        seite["pause"] = {"art": "keine", "datum": None, "spieltag": None}
        return seite

    view = A.upcoming(fixtures, zp.jetzt, zp.import_tag)
    fxp = A.prepare(fixtures)
    rounds = sorted((s for s in view.sections if not s.hinweis), key=lambda s: (s.first, s.saison, s.spieltag))
    specials = [s for s in view.sections if s.hinweis]
    notice = view.notice

    if notice is not None and notice.kind in (A.SUMMER, A.SEASON_START):
        nxt = A.next_round(A.rounds(fxp), zp.jetzt.date())
        seite["zustand"] = "pause"
        seite["pause"] = {"art": PAUSE[notice.kind], "datum": nxt.first.isoformat() if nxt else None,
                          "spieltag": nxt.spieltag if nxt else None}
        return seite
    if not rounds and not specials:
        nxt = A.next_round(A.rounds(fxp), zp.jetzt.date())
        art = PAUSE.get(notice.kind, "unbekannt") if notice is not None else ("unbekannt" if nxt else "keine")
        if notice is not None and notice.kind == A.STALE:
            art = "unbekannt" if nxt else "keine"                          # Annahme A6
        seite["zustand"] = "pause"
        seite["pause"] = {"art": art, "datum": nxt.first.isoformat() if nxt else None,
                          "spieltag": nxt.spieltag if nxt else None}
        return seite

    # Tabs = die Spieltage, die das Dashboard als Abschnitte zeigt; Sonderspiele in den Tab ihres Zeitraums (F4)
    tabs, fenster = [], []
    for s in rounds:
        tabs.append(_tab(s.saison, s.spieltag, s.first, s.last))
        fenster.append((s.first, s.last))
        games = fxp[(fxp["saison"] == s.saison) & (fxp["spieltag"] == s.spieltag)
                    & ((fxp["hinweis"] == "") | ~fxp["aktiv"])]           # reguläre und Status-Spiele (F5)
        tabs[-1]["_games"] = list(games.itertuples())
    for s in specials:
        for g in s.games.itertuples():
            ziel = next((i for i, (von, bis) in enumerate(fenster) if von <= g.datum_von <= bis), None)
            if ziel is None:
                if not tabs:                                                   # nur Sonderspiele (Saisonende)
                    tabs.append(_tab(s.saison, s.spieltag, None, None))
                    tabs[-1]["_games"] = []
                    fenster.append((g.datum_von, g.datum_von))
                ziel = 0
            tabs[ziel]["_games"].append(g)

    ergebnisse = daten.ergebnisse(web.name, zp.bis)
    for tab in tabs:
        spiele = []
        for g in tab.pop("_games"):
            k = daten.kpis(web.name, g.saison, int(g.spieltag), zp.bis).get(int(g.reihenfolge))
            spiele.append(spiel_eintrag(g, k, zp.jetzt, ergebnisse, b.team_ids, web.name))
        spiele = sortieren(spiele)
        for s in spiele:
            s.pop("_sort")
        tab["spiele"] = spiele
        tab["partien"] = sum(1 for s in spiele if not s["sonderspiel"])
        tab["auffaellig"] = sum(1 for s in spiele if s["art"] in ("stark", "leicht"))
        tab["bewertet"] = sum(1 for s in spiele if s["art"] in ("stark", "leicht", "ohne"))
        tab["sonderspiele"] = {"nachholspiel": sum(1 for s in spiele if s["sonderspiel"] == "nachholspiel"),
                               "vorgezogen": sum(1 for s in spiele if s["sonderspiel"] == "vorgezogen")}
    seite["tabs"] = tabs
    return seite
