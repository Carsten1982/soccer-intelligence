"""Alarme seit 0.23: Zustand, Drosselung und Mails (docs/09_Betrieb_EMail.md, Abschnitt 3.3).

Eine Prüfung liefert die gerade zutreffenden Befunde (Schlüssel, Stufe, Titel, Text). verarbeiten() vergleicht sie mit
dem gespeicherten Zustand und entscheidet, ob eine Mail geht:
- neuer Alarm → Mail; tritt dieselbe Alarmart innerhalb einer Stunde nach ihrer letzten Mail neu auf, wartet die
  Meldung, bis die Stunde um ist (höchstens eine Mail pro Stunde je Alarmart, M5);
- Stufe steigt (Warnung → Kritisch) → sofort Mail;
- besteht er weiter → Erinnerung alle 24 Stunden;
- behoben → Mail „BEHOBEN“;
- höchstens 3 Mails je Alarm, egal was sonst passiert (F5, Carsten 20.11.2026).
Der Zustand liegt in einer JSON-Datei (Container: /import/alarme.json, Prüfskript: /import/ueberwachung.json); der
Verlauf (letzte 200 Alarme) dient Dashboard und Statusmail.

Nur Standardbibliothek (auch für tools/ueberwachen.py auf dem Server).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

MAX_MAILS = 3
DROSSEL = timedelta(hours=1)
ERINNERUNG = timedelta(hours=24)
RANG = {"warnung": 1, "kritisch": 2}
STUFE_TEXT = {"warnung": "WARNUNG", "kritisch": "KRITISCH"}
VERLAUF_MAX = 200
VERSAND_PAUSE = timedelta(minutes=15)    # nach einem gescheiterten Versand erst wieder nach 15 Minuten
DASHBOARD = "https://soccer-intelligence.com/dashboard/ (Reiter Datenimport/API)"


@dataclass
class Befund:
    schluessel: str          # Alarmart, z. B. „import“, „festplatte“, „container:soccer-vorschau“
    stufe: str               # „warnung“ oder „kritisch“
    titel: str               # kurz, für den Betreff
    text: str                # Einzelheiten und was zu tun ist


def laden(pfad: Path) -> dict:
    try:
        return json.loads(Path(pfad).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def speichern(pfad: Path, zustand: dict) -> None:
    pfad = Path(pfad)
    pfad.parent.mkdir(parents=True, exist_ok=True)
    tmp = pfad.with_name(f".{pfad.name}.tmp")
    tmp.write_text(json.dumps(zustand, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, pfad)


def _zeit(iso: str | None) -> datetime | None:
    return datetime.fromisoformat(iso) if iso else None


def _text(art: str, a: dict, b: Befund | None, now: datetime) -> tuple[str, str]:
    """Betreff und Text einer Alarm-Mail."""
    nr = a["mails"] + 1
    seit = _zeit(a["seit"])
    if art == "behoben":
        dauer = now - seit
        std, rest = divmod(int(dauer.total_seconds()) // 60, 60)
        betreff = f"BEHOBEN: {a['titel']}"
        text = (f"{a['titel']} ist behoben.\n\nBestand seit {seit:%d.%m.%Y %H:%M} ({std} h {rest} min), "
                f"höchste Stufe: {STUFE_TEXT[a['hoechste']]}.\n")
    else:
        zusatz = {"neu": "", "hoeher": " (Stufe gestiegen)", "erinnerung": " (Erinnerung)"}[art]
        betreff = f"{STUFE_TEXT[b.stufe]}: {b.titel}{zusatz}"
        text = f"{b.text}\n\nSeit: {seit:%d.%m.%Y %H:%M}\nStufe: {STUFE_TEXT[b.stufe]}\n"
    text += (f"\nMail {nr} von höchstens {MAX_MAILS} zu diesem Alarm. Danach steht er nur noch im Dashboard und in der "
             f"wöchentlichen Statusmail.\nDashboard: {DASHBOARD}\n")
    return betreff, text


def verarbeiten(pfad: Path, befunde: list[Befund], now: datetime, senden, protokoll=None) -> list[dict]:
    """Befunde mit dem Zustand abgleichen, Mails senden, Zustand speichern. senden(betreff, text) -> (ok, meldung);
    protokoll(eintrag) schreibt ins Ereignisprotokoll. Gibt die Aktionen zurück (für Tests und Protokoll)."""
    now = now.replace(microsecond=0)
    zustand = laden(pfad)
    aktiv: dict = zustand.setdefault("aktiv", {})
    letzte: dict = zustand.setdefault("letzte_mail_je_art", {})
    verlauf: list = zustand.setdefault("verlauf", [])
    aktionen = []

    def mail(art: str, key: str, a: dict, b: Befund | None) -> None:
        v = zustand.get("versand") or {}
        if v and not v.get("ok") and now - _zeit(v["zeit"]) < VERSAND_PAUSE:    # Versand gestört: nicht jede Minute
            return
        betreff, text = _text(art, a, b, now)
        ok, meldung = senden(betreff, text)
        eintrag = {"zeit": now.isoformat(), "art": "alarm_mail", "alarm": key, "anlass": art, "ok": ok,
                   "meldung": meldung, "betreff": betreff}
        aktionen.append(eintrag)
        if protokoll:
            protokoll(eintrag)
        zustand["versand"] = {"zeit": now.isoformat(), "ok": ok, "meldung": meldung}
        if ok:
            a["mails"] += 1
            a["letzte_mail"] = now.isoformat()
            letzte[key] = now.isoformat()

    jetzt = {b.schluessel: b for b in befunde}
    for key, b in jetzt.items():
        a = aktiv.get(key)
        if a is None:
            a = aktiv[key] = {"titel": b.titel, "stufe": b.stufe, "hoechste": b.stufe, "seit": now.isoformat(),
                              "mails": 0, "letzte_mail": None, "text": b.text}
            if protokoll:
                protokoll({"zeit": now.isoformat(), "art": "alarm", "alarm": key, "stufe": b.stufe, "titel": b.titel})
            frueher = _zeit(letzte.get(key))
            if frueher is None or now - frueher >= DROSSEL:
                mail("neu", key, a, b)
            continue
        hoeher = RANG[b.stufe] > RANG[a["stufe"]]
        a.update(titel=b.titel, stufe=b.stufe, text=b.text)
        if RANG[b.stufe] > RANG[a["hoechste"]]:
            a["hoechste"] = b.stufe
        if a["mails"] >= MAX_MAILS:
            continue
        frueher = _zeit(a["letzte_mail"])
        if a["mails"] == 0:                                           # erste Meldung war gedrosselt
            letzte_art = _zeit(letzte.get(key))
            if letzte_art is None or now - letzte_art >= DROSSEL:
                mail("neu", key, a, b)
        elif hoeher:
            mail("hoeher", key, a, b)
        elif frueher is not None and now - frueher >= ERINNERUNG:
            mail("erinnerung", key, a, b)
    for key in [k for k in aktiv if k not in jetzt]:
        a = aktiv.pop(key)
        if 0 < a["mails"] < MAX_MAILS:
            mail("behoben", key, a, None)
        verlauf.append({"alarm": key, "titel": a["titel"], "stufe": a["hoechste"], "seit": a["seit"],
                        "bis": now.isoformat(), "mails": a["mails"]})
        if protokoll:
            protokoll({"zeit": now.isoformat(), "art": "alarm_behoben", "alarm": key, "titel": a["titel"]})
    zustand["verlauf"] = verlauf[-VERLAUF_MAX:]
    zustand["geprueft"] = now.isoformat()
    speichern(pfad, zustand)
    return aktionen


def ereignis(datei: Path, eintrag: dict) -> None:
    """Eine Zeile ins Ereignisprotokoll (/import/ereignisse.jsonl, seit 0.22)."""
    try:
        with Path(datei).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(eintrag, ensure_ascii=False) + "\n")
    except OSError:
        pass
