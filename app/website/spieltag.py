"""Datensatz der Seite Spieltag (Konzept 08, Abschnitt 5; Übergabe der Frontend-Entwürfe, Abschnitt 6).

Ergebnis ist ein Wörterbuch mit Codes statt Texten (Übergabe 9.1 Punkt 2), als JSON abrufbar. Welche Spiele
erscheinen, entscheidet core/anzeige.py (wie im Dashboard), die Werte und Stufen der Rechenkern (F6).

Einstufung je Partie (Übergabe 6.4: Status > Stufe > Normal; seit 0.20 Statusmodell des Entscheidungsprotokolls
19.11.2026, Nr. 1–2a, 4a: Prüfreihenfolge Status → gespielt → Werte ab → zu wenig Daten → Stufe):
  status          verschoben, abgesagt, abgebrochen, ausgesetzt, gewertet (F5)
  gespielt        Ergebnis in der Datenbank oder ab Anpfiff + 2 Stunden (ohne Anstosszeit ab Mitternacht); bis dahin
                  normal mit den Werten des Schnappschusses, kein Live-Status (seit 0.20; bis 0.19.1 ab dem Anpfiff)
  werte_ab        vor dem Anstoss, ein Team hat sein vorheriges Ligaspiel noch nicht gespielt oder das Ergebnis ist
                  noch nicht übernommen (core/anzeige.values_from, seit 0.20 auch auf der Website)
  zu_wenig_daten  alle Kennzahlen vorläufig oder keine Werte (bis 0.19.1 „nicht gewertet“)
  stark / mittel / gering  mindestens eine nicht vorläufige Kennzahl ist auffällig; die Art ist der höchste
                  Signalqualität (seit 0.20, Regelwerk 2.2)
  ohne            sonst
"""

from __future__ import annotations

from datetime import date

from core import anzeige as A
from core import schnappschuss as S
from core.fixtures import HINT_CATCHUP, HINT_EARLY, INACTIVE_STATUS, TERMIN_PROVISIONAL, TERMIN_TIME_OPEN
from core.kpis import LEVELS, RANK, MatchKpis
from core.top import TOP_KPIS

from . import adressen as AD
from . import einstellungen as W
from .daten import Bestand, Daten, Zeitpunkt

# Sortierung (Entwurf 3d, seit 0.20 nach Signalqualität): stark → mittel → gering → ohne Auffälligkeit → alles andere
# (nicht gewertet, Status, gespielt) in einer Gruppe; innerhalb der Stufen nach Betrag, sonst nach Anstoss.
REIHENFOLGE = {"stark": 0, "mittel": 1, "gering": 2, "ohne": 3, "zu_wenig_daten": 4, "werte_ab": 4, "status": 4,
               "gespielt": 4}
AUFFAELLIG = LEVELS                       # Arten mit Auffälligkeit (Signalqualität stark / mittel / gering)
SONDERSPIEL = {HINT_CATCHUP: "nachholspiel", HINT_EARLY: "vorgezogen"}
TERMIN = {TERMIN_TIME_OPEN: "zeit_offen", TERMIN_PROVISIONAL: "vorlaeufig"}
PAUSE = {A.WINTER: "winterpause", A.BREAK: "spielpause", A.SUMMER: "sommerpause", A.SEASON_START: "saisonstart"}


# --- Einstufung einer Partie ---------------------------------------------------------------------------

def einstufen(row, kpis: MatchKpis | None, jetzt, ergebnisse: dict, gate: A.Gate | None = None) -> dict:
    """art, status, ergebnis, „Werte ab“ und stärkste Abweichung einer Partie (Konzept 5.3). kpis = die Werte, die
    die Seite zeigt (vor dem Anstoss aktuell berechnet, danach der Schnappschuss); gate = anzeige.values_from."""
    out = {"art": "ohne", "status": None, "ergebnis": None, "staerkste": None, "werte_ab": None, "qualitaet": None}
    if row.status in INACTIVE_STATUS:
        return {**out, "art": "status", "status": row.status}
    score = ergebnisse.get((row.saison, row.heim, row.gast))
    if score is not None or jetzt >= A.played_from(row):
        q = qualitaet(kpis)             # Archiv (seit 0.21): Kachel mit Endstand und der Stufe des Schnappschusses
        return {**out, "art": "gespielt", "ergebnis": list(score) if score else None, "qualitaet": q["art"]}
    if gate is not None:                       # vor dem Anstoss noch ohne Werte (seit 0.20)
        return {**out, "art": "werte_ab", "werte_ab": gate.ab.isoformat() if gate.ab else None}
    return {**out, **qualitaet(kpis)}


def qualitaet(kpis: MatchKpis | None) -> dict:
    """art (stark/mittel/gering/ohne/zu_wenig_daten) und stärkste Abweichung aus den Werten eines Spiels."""
    out = {"art": "ohne", "staerkste": None}
    gewertet = []
    for key in TOP_KPIS:                       # die 8 Kennzahlen KPI 02–09
        r = getattr(kpis, key, None) if kpis is not None else None
        if r is not None and not r.vorlaeufig and r.abweichung_rund is not None:
            gewertet.append((key, r))
    if not gewertet:
        return {**out, "art": "zu_wenig_daten"}
    treffer = [(k, r) for k, r in gewertet if r.anomalie in LEVELS]
    if treffer:                                # höchste Signalqualität, dann grösste Abweichung
        k, r = max(treffer, key=lambda kr: (RANK[kr[1].anomalie], abs(kr[1].abweichung_rund)))
        return {**out, "art": r.anomalie, "staerkste": {"kpi": k, "abweichung": float(r.abweichung_rund)}}
    k, r = max(gewertet, key=lambda kr: abs(kr[1].abweichung_rund))
    return {**out, "staerkste": {"kpi": k, "abweichung": float(r.abweichung_rund)}}


def _termin(row) -> str:
    if row.termin in TERMIN:
        return TERMIN[row.termin]
    return "bestaetigt" if A._clock(row.anstoss) else "ohne_zeit"


def spiel_eintrag(row, kpis: MatchKpis | None, jetzt, ergebnisse: dict, team_ids: dict, liga: str,
                  gate: A.Gate | None = None) -> dict:
    stufe = einstufen(row, kpis, jetzt, ergebnisse, gate)
    api_id = None if row.api_id is None or row.api_id != row.api_id else int(row.api_id)   # NaN -> None
    return {
        "id": api_id, "slug": AD.spiel_slug(row.heim, row.gast, api_id) if api_id is not None else "",
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
                  -abs(stufe["staerkste"]["abweichung"]) if stufe["art"] in AUFFAELLIG else 0,
                  row.anstoss_zeit, int(row.reihenfolge)),
    }


def sortieren(spiele: list[dict]) -> list[dict]:
    """Konzept 5.4 (seit 0.19): hoch → mittel → gering → ohne → übrige; Nachhol- und vorgezogene Spiele
    werden wie im Entwurf mitsortiert (bis 0.17: als Gruppe am Ende, Annahme A2)."""
    return sorted(spiele, key=lambda s: s["_sort"])


# --- Seite ------------------------------------------------------------------------------------------------

def _tab(saison: str, spieltag: int, von: date | None, bis: date | None) -> dict:
    return {"saison": saison, "spieltag": spieltag, "von": von.isoformat() if von else None,
            "bis": bis.isoformat() if bis else None, "spiele": []}


def _liga_kopf(fixtures, zp: Zeitpunkt) -> dict:
    """Liga-Kachel: anstehender Spieltag bzw. Pausenname (Annahme A5)."""
    view = A.upcoming(fixtures, zp.jetzt, zp.stand)
    pause = None
    if not any(not s.hinweis for s in view.sections) and view.notice is not None and view.notice.kind in PAUSE:
        pause = PAUSE[view.notice.kind]
    return {"spieltag": view.anchor[1] if view.anchor else None, "pause": pause}


def spieltag_daten(daten: Daten, web: W.WebLiga, zp: Zeitpunkt) -> dict:
    """Datensatz der Seite Spieltag für eine Liga zum Zeitpunkt zp."""
    b: Bestand = daten.bestand()
    seite = {"seite": "spieltag", "liga": web.slug, "liga_key": web.key, "jetzt": zp.jetzt.isoformat(timespec="minutes"),
             "stand": zp.stand.isoformat(timespec="minutes") if zp.stand else None, "zeitreise": zp.zeitreise,
             "gesperrt": b.gesperrt, "veraltet": A.is_stale(zp.stand, zp.jetzt),
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

    view = A.upcoming(fixtures, zp.jetzt, zp.stand)
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
            werte = daten.werte(web.name, g, zp)
            gate = A.values_from(fxp, g, zp.jetzt, ergebnisse)
            if gate is None and werte.quelle == S.WAITING:              # Schnappschuss wartet auf ein Vorspiel
                gate = A.Gate("Werte folgen nachträglich")
            spiele.append(spiel_eintrag(g, werte.kpis, zp.jetzt, ergebnisse, b.team_ids, web.name, gate))
        spiele = sortieren(spiele)
        for s in spiele:
            s.pop("_sort")
        tab["spiele"] = spiele
        tab["partien"] = sum(1 for s in spiele if not s["sonderspiel"])
        tab["auffaellig"] = sum(1 for s in spiele if s["art"] in AUFFAELLIG)
        tab["bewertet"] = sum(1 for s in spiele if s["art"] in (*AUFFAELLIG, "ohne"))
        tab["sonderspiele"] = {"nachholspiel": sum(1 for s in spiele if s["sonderspiel"] == "nachholspiel"),
                               "vorgezogen": sum(1 for s in spiele if s["sonderspiel"] == "vorgezogen")}
    seite["tabs"] = tabs
    return seite


# --- Archivseite je Spieltag (seit 0.21; Template-Briefing 6, Konzept 08, Abschnitt 10) ------------------------------

def archiv_daten(daten: Daten, web: W.WebLiga, saison: str, nr: int, zp: Zeitpunkt) -> dict | None:
    """Alle Spiele eines vergangenen Spieltags mit Endstand und den Werten vor dem Spiel (Schnappschuss), Pfeile zum
    vorherigen und nächsten Spieltag. None, wenn es den Spieltag nicht gibt oder er noch nicht begonnen hat."""
    b: Bestand = daten.bestand()
    seite = {"seite": "archiv", "liga": web.slug, "liga_key": web.key, "saison": saison, "spieltag": int(nr),
             "jetzt": zp.jetzt.isoformat(timespec="minutes"),
             "stand": zp.stand.isoformat(timespec="minutes") if zp.stand else None, "zeitreise": zp.zeitreise,
             "gesperrt": b.gesperrt, "veraltet": A.is_stale(zp.stand, zp.jetzt), "spiele": [], "vorher": None,
             "nachher": None, "nachher_aktuell": False, "beginn": None, "partien": 0, "auffaellig": 0,
             "sonderspiele": {"nachholspiel": 0, "vorgezogen": 0}}
    fixtures = b.fx.leagues.get(web.name)
    if fixtures is None or fixtures.empty:
        return None
    fxp = daten.spielplan(web.name)
    spiele = fxp[(fxp["saison"] == saison) & (fxp["spieltag"] == int(nr))]
    if spiele.empty or spiele["datum_von"].min() > zp.jetzt.date():           # nur begonnene Spieltage
        return None
    regulaer = spiele[spiele["hinweis"] == ""]
    seite["beginn"] = (regulaer if len(regulaer) else spiele)["datum_von"].min().isoformat()
    ergebnisse = daten.ergebnisse(web.name, zp.bis)
    eintraege = []
    for g in A.sort_games(spiele).itertuples():
        werte = daten.werte(web.name, g, zp)
        gate = A.values_from(fxp, g, zp.jetzt, ergebnisse)
        if gate is None and werte.quelle == S.WAITING:
            gate = A.Gate("Werte folgen nachträglich")
        e = spiel_eintrag(g, werte.kpis, zp.jetzt, ergebnisse, b.team_ids, web.name, gate)
        e.pop("_sort")
        eintraege.append(e)
    seite["spiele"] = eintraege
    seite["partien"] = sum(1 for s in eintraege if not s["sonderspiel"])
    seite["auffaellig"] = sum(1 for s in eintraege if (s["qualitaet"] or s["art"]) in AUFFAELLIG)
    for art in ("nachholspiel", "vorgezogen"):
        seite["sonderspiele"][art] = sum(1 for s in eintraege if s["sonderspiel"] == art)
    nummern = sorted({int(x) for x in fxp.loc[fxp["saison"] == saison, "spieltag"]})
    if int(nr) - 1 in nummern:
        seite["vorher"] = int(nr) - 1
    if int(nr) + 1 in nummern:
        seite["nachher"] = int(nr) + 1
        naechste = fxp[(fxp["saison"] == saison) & (fxp["spieltag"] == int(nr) + 1)]
        seite["nachher_aktuell"] = bool(naechste["datum_von"].min() > zp.jetzt.date())   # noch nicht begonnen
    return seite
