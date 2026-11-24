"""Mailversand über SMTP (Hostinger) seit 0.23 (docs/09_Betrieb_EMail.md, Abschnitt 2).

- Ein Postfach (info@), alert@ ist ein Alias darauf (Carsten 20.11.2026). Angemeldet wird immer mit dem Postfach;
  Zugangsdaten NUR aus der Umgebung (.env auf dem Server): SI_SMTP_HOST, SI_SMTP_PORT, SI_SMTP_USER, SI_SMTP_PASSWORT.
  Nie in Code, Git, Logs oder Meldungen.
- Zwei Wege: „alert“ (Alarme, Statusmail, Testmails) geht an SI_ALARM_AN (Standard alert@, der Alias), „info“
  (Kontaktformular) an SI_KONTAKT_AN (Standard info@). Absender ist immer das Postfach, mit eigenem Namen je Weg.
  Das Postfach leitet an die private Adresse weiter (M8); sie steht nirgends im Programm.
- Fehlt die Konfiguration, wird nichts versendet (Rückgabe „nicht eingerichtet“).

Nur Standardbibliothek (auch für tools/ueberwachen.py auf dem Server).

Aufruf: python -m betrieb.mail --test alert|info [--release "0.23 (abc1234)"] [--weg "Container soccer-import"]
"""

from __future__ import annotations

import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

PRAEFIX = "[Soccer Intelligence] "
STANDARD_HOST = "smtp.hostinger.com"
STANDARD_PORT = 465
ZUGANG = ("SI_SMTP_USER", "SI_SMTP_PASSWORT")
EMPFAENGER = {"alert": ("SI_ALARM_AN", "alert@soccer-intelligence.com"),
              "info": ("SI_KONTAKT_AN", "info@soccer-intelligence.com")}
ABSENDERNAME = {"alert": "Soccer Intelligence Alarm", "info": "Soccer Intelligence Kontakt"}
NICHT_EINGERICHTET = "nicht eingerichtet"


def konfig(weg: str, env=None) -> dict | None:
    """Zugang und Empfänger für „alert“ oder „info“; None, wenn Benutzer oder Passwort fehlen."""
    env = os.environ if env is None else env
    user, pw = (env.get(ZUGANG[0]) or "").strip(), env.get(ZUGANG[1]) or ""
    an_key, an_standard = EMPFAENGER[weg]
    if not user or not pw:
        return None
    try:
        port = int(env.get("SI_SMTP_PORT") or STANDARD_PORT)
    except ValueError:
        port = STANDARD_PORT
    return {"host": (env.get("SI_SMTP_HOST") or STANDARD_HOST).strip(), "port": port, "user": user, "pw": pw,
            "an": (env.get(an_key) or an_standard).strip(), "name": ABSENDERNAME[weg]}


def eingerichtet(weg: str, env=None) -> bool:
    return konfig(weg, env) is not None


def _einzeilig(text: str) -> str:
    """Kopfzeilen ohne Zeilenumbrüche (keine eingeschleusten Kopfzeilen)."""
    return " ".join(str(text).split())


def nachricht(cfg: dict, betreff: str, text: str, an: str | None = None, antwort_an: str | None = None) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = f"{cfg.get('name', 'Soccer Intelligence')} <{cfg['user']}>"
    msg["To"] = _einzeilig(an or cfg.get("an") or cfg["user"])
    msg["Subject"] = _einzeilig(PRAEFIX + betreff)
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=cfg["user"].split("@")[-1])
    if antwort_an:
        msg["Reply-To"] = _einzeilig(antwort_an)
    msg.set_content(text)
    return msg


def senden(weg: str, betreff: str, text: str, an: str | None = None, antwort_an: str | None = None, env=None,
           smtp_klasse=None) -> tuple[bool, str]:
    """Mail senden. Rückgabe (ok, kurze Meldung ohne Zugangsdaten). smtp_klasse nur für Tests."""
    cfg = konfig(weg, env)
    if cfg is None:
        return False, NICHT_EINGERICHTET
    msg = nachricht(cfg, betreff, text, an, antwort_an)
    try:
        if smtp_klasse is not None:
            server = smtp_klasse(cfg["host"], cfg["port"], timeout=20)
        elif cfg["port"] == 587:
            server = smtplib.SMTP(cfg["host"], cfg["port"], timeout=20)
        else:
            server = smtplib.SMTP_SSL(cfg["host"], cfg["port"], timeout=20, context=ssl.create_default_context())
        with server as s:
            if cfg["port"] == 587 and smtp_klasse is None:
                s.starttls(context=ssl.create_default_context())
            s.login(cfg["user"], cfg["pw"])
            s.send_message(msg)
    except Exception as exc:  # noqa: BLE001 - jede Störung als kurze Meldung, nie mit Passwort
        text_fehler = str(exc).replace(cfg["pw"], "***") if cfg["pw"] else str(exc)
        return False, f"{type(exc).__name__}: {text_fehler}"[:200]
    return True, "gesendet"


def testmail(weg: str, release: str = "", ort: str = "", env=None, smtp_klasse=None) -> tuple[bool, str]:
    """Testmail nach einem Release oder von Hand (M9)."""
    wo = ort or {"alert": "Alarme (an alert@)", "info": "Kontaktformular (an info@)"}[weg]
    betreff = f"Test nach Release {release} – {wo}" if release else f"Testmail – {wo}"
    text = (f"Diese Testmail bestätigt, dass der Mailversand funktioniert.\n\nVersandweg: {wo}\n"
            + (f"Release: {release}\n" if release else "")
            + "\nKeine Aktion nötig. Kommt nach einem Release eine der drei Testmails nicht an, bitte melden.\n")
    return senden(weg, betreff, text, env=env, smtp_klasse=smtp_klasse)


def main(argv: list[str]) -> int:
    args = dict(zip(argv[::2], argv[1::2]))
    weg = args.get("--test")
    if weg not in EMPFAENGER:
        print("Aufruf: python -m betrieb.mail --test alert|info [--release TEXT] [--weg TEXT]")
        return 2
    ok, meldung = testmail(weg, args.get("--release", ""), args.get("--weg", ""))
    print(("✅ " if ok else "✖ ") + f"Testmail {weg}@: {meldung}")
    return 0 if ok else (3 if meldung == NICHT_EINGERICHTET else 1)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
