"""Daten-Alarme seit 0.23 (docs/09_Betrieb_EMail.md, Abschnitt 3.1). Läuft im Container soccer-import.

Jede Prüfung liest nur, was der Import ohnehin schreibt (Berichte der Läufe, Zustand, Schnappschuss-Stand, Protokoll
der Abfragen, Entscheide, Meldungen des Kontaktformulars) und liefert die gerade zutreffenden Befunde.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from importer import einstellungen as E
from importer.client import used_today
from importer.schnappschuss import load_status

from . import laufzeiten
from .alarme import Befund

KONTINGENT_WARNUNG = 0.8          # 80 % der eigenen Tagesgrenze
API_REST_KRITISCH = 0.1           # weniger als 10 % des Tageskontingents laut API
SCHNAPPSCHUSS_ALT = timedelta(hours=2)
MELDUNG_DAUER = timedelta(hours=24)   # gescheiterter Versand des Kontaktformulars bleibt 24 h ein Alarm
DATEIFEHLER = "mit Fehlern"           # Text des Schnappschuss-Laufs, wenn die gültigen Dateien Fehler haben


def _json(p: Path):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def berichte(base: Path, anzahl: int = 40) -> list[dict]:
    """Die neuesten Berichte der Läufe (Standard 40, reicht für letzten Lauf, Kontrolllauf, Abo), neueste zuerst."""
    out = []
    for p in sorted((Path(base) / "laeufe").glob("*/bericht.json"), reverse=True)[:anzahl]:
        rep = _json(p)
        if rep:
            out.append(rep)
    return out


def _uebernommen(rep: dict) -> bool:
    return str(rep.get("status", "")).startswith("übernommen")


def offene_entscheide(base: Path, reps: list[dict]) -> list[str]:
    """Zurückgehaltene Spiele und späte Korrekturen ohne Entscheid (wie der Kasten „Ihre Entscheidung“)."""
    erledigt = set()
    for e in _json(Path(base) / E.DECISIONS_FILE) or []:
        erledigt.add((e.get("art"), int(e.get("id", -1)), e.get("spalte")))
    for p in (Path(base) / "anfragen").glob("*.json"):
        r = _json(p) or {}
        if r.get("aktion") == "entscheid":
            erledigt.add((r.get("art"), int(r.get("id", -1)), r.get("spalte")))
    letzter = next((r for r in reps if _uebernommen(r) or r.get("status") == "wartet"), None)
    kontrolle = next((r for r in reps if (_uebernommen(r) or r.get("status") == "wartet")
                      and r.get("anlass", "kontrolle") == "kontrolle"), None)
    out = []
    for k in (letzter or {}).get("kritisch") or []:
        if k.get("art") == "endstand" and ("endstand", int(k["id"]), None) not in erledigt:
            out.append(f"{k.get('liga')}: {k.get('spiel')} – Endstand der API {k.get('api')}, laut Tor-Ereignissen "
                       f"{k.get('ereignisse')}")
    for k in (kontrolle or {}).get("spaete_korrekturen") or []:
        if ("korrektur", int(k["id"]), k.get("spalte")) not in erledigt:
            out.append(f"{k.get('liga')}: {k.get('spiel')} – späte Korrektur {k.get('spalte')} {k.get('alt')} → {k.get('neu')}")
    return out


def befunde(base: Path, data_dir: Path, now: datetime) -> list[Befund]:
    """Alle Daten-Befunde. now = Ortszeit Europe/Zurich (ohne Zeitzone)."""
    base = Path(base)
    now = now.replace(tzinfo=None)
    out: list[Befund] = []
    reps = berichte(base)
    state = _json(base / "zustand.json") or {}

    # Import fehlgeschlagen: Kontrolllauf, oder Lauf nach dem Spiel ohne weitere Wiederholung
    if reps and reps[0].get("status") == "fehlgeschlagen":
        r = reps[0]
        if r.get("anlass", "kontrolle") == "kontrolle" or not state.get("wiederholung"):
            out.append(Befund("import", "kritisch", "Import fehlgeschlagen",
                              f"Der Lauf {r.get('lauf')} ({r.get('anlass', 'kontrolle')}) ist fehlgeschlagen: "
                              f"{r.get('meldung', '–')}\nDie gültigen Dateien sind unverändert. Der nächste Lauf "
                              "versucht es wieder; Einzelheiten im Reiter Datenimport/API."))

    # API-Kontingent
    heute = now.strftime("%Y-%m-%d")
    verbraucht = used_today(base / "roh", heute)
    rest = ((reps[0] if reps else {}).get("anfragen") or {}).get("rest") if reps and (reps[0].get("start") or "")[:10] == heute else None
    if verbraucht >= E.DAILY_LIMIT or (isinstance(rest, int) and rest < 7500 * API_REST_KRITISCH):
        out.append(Befund("kontingent", "kritisch", "API-Kontingent aufgebraucht",
                          f"Heute {verbraucht} Abfragen (eigene Grenze {E.DAILY_LIMIT}), Rest laut API: {rest}.\n"
                          "Weitere Läufe des Tages entfallen bis auf den Kontrolllauf um 04:00."))
    elif verbraucht >= E.DAILY_LIMIT * KONTINGENT_WARNUNG:
        out.append(Befund("kontingent", "warnung", "API-Kontingent fast aufgebraucht",
                          f"Heute {verbraucht} von {E.DAILY_LIMIT} Abfragen (eigene Grenze) verbraucht."))

    # Schnappschuss und Datei-Prüfung (der stündliche Schnappschuss-Lauf prüft die gültigen Dateien)
    snap = load_status(base)
    if snap:
        fehler = snap.get("fehler") or ""
        lauf = datetime.fromisoformat(snap["lauf"]) if snap.get("lauf") else None
        if DATEIFEHLER in fehler:
            out.append(Befund("dateien", "kritisch", "Datei-Prüfung gescheitert – Website zeigt „Daten werden geprüft“",
                              "Die gültige Datenbank oder der Spielplan hat Fehler der Prüfregeln. Die Website zeigt "
                              "auf den Datenseiten „Die Daten werden gerade geprüft“ (503). Einzelheiten im Bereich "
                              "Datenqualität; Rückweg zur letzten Fassung: 01, Abschnitt 6.5."))
        elif fehler:
            out.append(Befund("schnappschuss", "kritisch", "Schnappschuss fehlgeschlagen",
                              f"Der Schnappschuss-Lauf {snap.get('lauf')} ist fehlgeschlagen: {fehler[:300]}\n"
                              "Werte vor dem Anpfiff werden dann nachträglich berechnet (mit Hinweis)."))
        elif lauf and now - lauf > SCHNAPPSCHUSS_ALT:
            out.append(Befund("schnappschuss", "kritisch", "Schnappschuss-Lauf seit über 2 Stunden nicht gelaufen",
                              f"Letzter Schnappschuss-Lauf: {lauf:%d.%m.%Y %H:%M}. Läuft der Container soccer-import?"))

    # Fassung wartet auf Freigabe (F4)
    wartend = state.get("wartend")
    if wartend:
        rep = next((r for r in reps if r.get("lauf") == wartend), {})
        gruende = "; ".join((rep.get("automatik") or {}).get("gruende") or []) or rep.get("status", "")
        out.append(Befund("freigabe", "warnung", "Neue Daten warten auf Freigabe",
                          f"Die Fassung {wartend} wurde nicht automatisch übernommen ({gruende}). Bitte im Reiter "
                          "Datenimport/API prüfen und übernehmen oder verwerfen."))

    # Entscheid offen (F4)
    offen = offene_entscheide(base, reps)
    if offen:
        out.append(Befund("entscheid", "warnung", f"{len(offen)} Entscheid(e) offen",
                          "Diese Spiele bzw. Werte werden zurückgehalten, bis du im Reiter Datenimport/API "
                          "entscheidest:\n- " + "\n- ".join(offen[:10])))

    # Statistik fehlt dauerhaft (7 Tage nach dem Spiel)
    kontrolle = next((r for r in reps if r.get("anlass", "kontrolle") == "kontrolle" and r.get("status") != "fehlgeschlagen"), None)
    lange = [o for o in (kontrolle or {}).get("offen") or [] if str(o.get("grund", "")).startswith("Statistik fehlt seit")]
    if lange:
        out.append(Befund("statistik", "warnung", f"Statistik fehlt dauerhaft ({len(lange)} Spiele)",
                          "Diese Spiele haben auch 7 Tage nach dem Spiel noch leere Werte (fehlende Werte zählen nie "
                          "als 0):\n- " + "\n- ".join(f"{o.get('liga')}: {o.get('heim')} – {o.get('gast')} "
                                                       f"({o.get('datum')}): {', '.join(o.get('fehlt') or [])}"
                                                       for o in lange[:10])))

    # Laufzeiten (VPS, Domain, Postfach, API-Abo)
    abo = next((r.get("abo") for r in reps if (r.get("abo") or {}).get("bis")), None)
    for lz in laufzeiten.laden(abo=abo):
        stufe = lz.stufe(now.date())
        if stufe:
            if lz.automatisch:
                text = (f"{lz.name} läuft am {lz.bis:%d.%m.%Y} ab (noch {lz.rest(now.date())} Tage). Die automatische "
                        "Verlängerung ist eingeschaltet: Bitte bei Hostinger prüfen, ob verlängert wurde (Zahlungsart "
                        "gültig?), und das neue Datum in app/config/laufzeiten.toml nachtragen.")
            else:
                text = (f"{lz.name} läuft am {lz.bis:%d.%m.%Y} ab (noch {lz.rest(now.date())} Tage) und verlängert "
                        "sich nicht selbst. Bitte rechtzeitig verlängern.")
            out.append(Befund(f"laufzeit:{lz.name}", stufe, f"Laufzeit endet: {lz.name}", text))

    # Kontaktformular: Versand gescheitert (Meldung des Containers soccer-vorschau)
    for p in sorted((base / "meldungen").glob("kontakt_*.json"), reverse=True)[:1]:
        m = _json(p) or {}
        zeit = datetime.fromisoformat(m["zeit"]) if m.get("zeit") else None
        if zeit and now - zeit < MELDUNG_DAUER:
            out.append(Befund("kontakt", "warnung", "Kontaktformular: Versand gescheitert",
                              f"Am {zeit:%d.%m.%Y %H:%M} konnte eine Nachricht des Kontaktformulars nicht gesendet "
                              f"werden ({m.get('meldung', '–')}). Der Besucher hat einen Hinweis mit der Adresse "
                              "info@soccer-intelligence.com bekommen. Zugangsdaten in .env prüfen."))
    return out

