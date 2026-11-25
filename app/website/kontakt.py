"""Kontaktformular seit 0.23 (docs/09_Betrieb_EMail.md, Abschnitt 6; Beschluss 8 vom 19.11.2026).

- Prüfung auf dem Server, ohne JavaScript nutzbar: Pflichtfelder, E-Mail-Adresse, Längen, Einwilligung,
  Sicherheitsfrage, verstecktes Feld. Bei Fehlern bleibt die Eingabe stehen, die Fehler stehen je Feld.
- Sicherheitsfrage: zufällig aus zehn Rechenaufgaben; welche gestellt wurde, steht in einem versteckten Feld mit
  Prüfsumme (Geheimnis entsteht beim Start des Dienstes, gilt 2 Stunden). Keine Konfiguration nötig.
- Anfragebremse: höchstens 3 gesendete Nachrichten pro Stunde je Absender-Adresse, nur im Arbeitsspeicher.
- Versand von info@ an info@ (leitet an Carsten weiter), „Antwort an“ = Absender. Nichts wird gespeichert; ins
  Protokoll kommt nur „gesendet“ bzw. „gescheitert“, nie der Inhalt. Scheitert der Versand, legt die Website eine
  kurze Meldung für den Alarm ab (/meldungen, ohne Inhalt).
- Verstecktes Feld ausgefüllt (Bot): Antwort wie bei Erfolg, aber nichts wird gesendet.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import random
import re
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from betrieb import mail

AUFGABEN = [("4 + 3", 7), ("2 + 5", 7), ("6 + 2", 8), ("9 − 4", 5), ("3 + 3", 6),
            ("8 − 3", 5), ("5 + 4", 9), ("7 − 2", 5), ("1 + 8", 9), ("10 − 6", 4)]
GUELTIG_S = 2 * 3600
MAX_JE_STUNDE = 3
NAME_MAX, TEXT_MIN, TEXT_MAX, MAIL_MAX = 100, 10, 5000, 254
MAIL_RE = re.compile(r"^[^@\s<>,;]+@[^@\s<>,;]+\.[^@\s<>,;]{2,}$")
MELDUNGEN = Path(os.environ.get("SI_MELDUNGEN_DIR", "/meldungen"))
_GEHEIM = os.urandom(32)


@dataclass
class Formular:
    werte: dict = field(default_factory=lambda: {"name": "", "email": "", "nachricht": "", "einverstanden": False})
    fehler: dict = field(default_factory=dict)       # Feld -> Schlüssel des Fehlertexts (formular.fehler.<…>)
    frage: str = ""
    token: str = ""
    status: str = ""                                  # "", "gesendet", "versand_fehler", "zu_viele"
    aktiv: bool = False                               # Versand eingerichtet?


def _signatur(idx: int, ts: int) -> str:
    return hmac.new(_GEHEIM, f"{idx}.{ts}".encode(), hashlib.sha256).hexdigest()[:20]


def neue_aufgabe(jetzt: float | None = None, rng=random) -> tuple[str, str]:
    """(Frage, Token) einer zufälligen Rechenaufgabe."""
    idx, ts = rng.randrange(len(AUFGABEN)), int(jetzt if jetzt is not None else time.time())
    return AUFGABEN[idx][0], f"{idx}.{ts}.{_signatur(idx, ts)}"


def aufgabe_aus(token: str, jetzt: float | None = None) -> int | None:
    """Index der Aufgabe, wenn das Token echt und nicht älter als 2 Stunden ist."""
    try:
        idx_s, ts_s, sig = str(token).split(".")
        idx, ts = int(idx_s), int(ts_s)
    except ValueError:
        return None
    jetzt = jetzt if jetzt is not None else time.time()
    if not 0 <= idx < len(AUFGABEN) or not hmac.compare_digest(sig, _signatur(idx, ts)) or not 0 <= jetzt - ts <= GUELTIG_S:
        return None
    return idx


def leer(gesendet: bool = False, env=None) -> Formular:
    frage, token = neue_aufgabe()
    return Formular(frage=frage, token=token, status="gesendet" if gesendet else "", aktiv=mail.eingerichtet("info", env))


class Bremse:
    """Höchstens MAX_JE_STUNDE gesendete Nachrichten je Adresse und Stunde (nur Arbeitsspeicher)."""

    def __init__(self) -> None:
        self._zeiten: dict[str, deque] = {}
        self._lock = threading.Lock()

    def _aufraeumen(self, ip: str, jetzt: float) -> deque:
        d = self._zeiten.setdefault(ip, deque())
        while d and jetzt - d[0] > 3600:
            d.popleft()
        return d

    def erlaubt(self, ip: str, jetzt: float) -> bool:
        with self._lock:
            return len(self._aufraeumen(ip, jetzt)) < MAX_JE_STUNDE

    def reservieren(self, ip: str, jetzt: float) -> bool:
        """Prüfen und Platz belegen in einem Schritt (seit 0.24, Backend-Review A7): zwei gleichzeitige Anfragen
        derselben Adresse können die Grenze so nicht gemeinsam überschreiten. Scheitert der Versand: freigeben()."""
        with self._lock:
            d = self._aufraeumen(ip, jetzt)
            if len(d) >= MAX_JE_STUNDE:
                return False
            d.append(jetzt)
            if len(self._zeiten) > 10_000:                  # Speicher begrenzen: abgelaufene Adressen entfernen (A8)
                for k in [k for k, v in self._zeiten.items() if not v or jetzt - v[-1] > 3600]:
                    del self._zeiten[k]
            return True

    def freigeben(self, ip: str, jetzt: float) -> None:
        with self._lock:
            d = self._zeiten.get(ip)
            if d and jetzt in d:
                d.remove(jetzt)

    def merken(self, ip: str, jetzt: float) -> None:
        """Wie reservieren(), ohne Prüfung (für Tests und Aufrufer ohne Reservierung)."""
        with self._lock:
            self._aufraeumen(ip, jetzt).append(jetzt)


BREMSE = Bremse()


def _eins(form: dict, name: str) -> str:
    v = form.get(name) or [""]
    return (v[0] if isinstance(v, list) else str(v)).replace("\r\n", "\n").strip()


def pruefen(form: dict, jetzt: float | None = None) -> tuple[dict, dict]:
    """Eingaben und Fehler je Feld."""
    werte = {"name": _eins(form, "name"), "email": _eins(form, "email"), "nachricht": _eins(form, "nachricht"),
             "einverstanden": bool(_eins(form, "einverstanden"))}
    fehler = {}
    if not werte["email"]:
        fehler["email"] = "email_fehlt"
    elif len(werte["email"]) > MAIL_MAX or not MAIL_RE.match(werte["email"]):
        fehler["email"] = "email_ungueltig"
    n = len(werte["nachricht"])
    if not n:
        fehler["nachricht"] = "nachricht_fehlt"
    elif n < TEXT_MIN:
        fehler["nachricht"] = "nachricht_kurz"
    elif n > TEXT_MAX:
        fehler["nachricht"] = "nachricht_lang"
    if len(werte["name"]) > NAME_MAX:
        fehler["name"] = "name_lang"
    if not werte["einverstanden"]:
        fehler["einverstanden"] = "einwilligung"
    idx = aufgabe_aus(_eins(form, "aufgabe"), jetzt)
    antwort = _eins(form, "antwort").replace(" ", "")
    if idx is None or not antwort.lstrip("-").isdigit() or int(antwort) != AUFGABEN[idx][1]:
        fehler["antwort"] = "antwort"
    return werte, fehler


def _meldung(text: str, jetzt: datetime) -> None:
    """Kurze Meldung für den Daten-Alarm (ohne Inhalt der Nachricht)."""
    try:
        MELDUNGEN.mkdir(parents=True, exist_ok=True)
        (MELDUNGEN / f"kontakt_{jetzt:%Y%m%d_%H%M%S}.json").write_text(
            json.dumps({"zeit": jetzt.isoformat(timespec="seconds"), "meldung": text[:200]}), encoding="utf-8")
    except OSError:
        pass


def bearbeiten(form: dict, ip: str, lang: str, env=None, senden=None, jetzt: float | None = None) -> Formular | None:
    """Formular verarbeiten. None = gesendet (die Seite leitet weiter); sonst das Formular zum erneuten Anzeigen."""
    jetzt = jetzt if jetzt is not None else time.time()
    if _eins(form, "website"):                          # verstecktes Feld: Bot – so tun, als ob
        return None
    werte, fehler = pruefen(form, jetzt)
    f = leer(env=env)
    f.werte, f.fehler = werte, fehler
    if not f.aktiv or fehler:
        return f
    if not BREMSE.reservieren(ip, jetzt):
        f.status = "zu_viele"
        return f
    zeit = datetime.fromtimestamp(jetzt)
    betreff = "Kontaktformular: " + " ".join(werte["nachricht"].split())[:60]
    text = (f"Neue Nachricht über das Kontaktformular der Website\n\nName: {werte['name'] or '–'}\n"
            f"E-Mail: {werte['email']}\nSprache der Seite: {lang}\nZeit: {zeit:%d.%m.%Y %H:%M}\n\n"
            f"{werte['nachricht']}\n\n– Antworten: einfach auf diese Mail antworten (geht an den Absender).\n")
    senden = senden or (lambda b, t, a: mail.senden("info", b, t, antwort_an=a, env=env))
    ok, meldung = senden(betreff, text, werte["email"])
    print(f"Kontaktformular: {'gesendet' if ok else 'Versand gescheitert'}", flush=True)
    if ok:
        return None
    BREMSE.freigeben(ip, jetzt)                         # nicht gesendet: zählt nicht gegen die Grenze
    _meldung(meldung, zeit)
    f.status = "versand_fehler"
    return f
