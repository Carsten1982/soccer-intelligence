"""Vorschau der Website unter https://soccer-intelligence.com/vorschau (Konzept 08, Abschnitte 3, 4 und 6).

Kleiner Webserver aus der Python-Standardbibliothek. Er erzeugt jede Seite beim Aufruf neu – nötig für die
Zeitreise (?datum=2026-10-03 oder ?datum=2026-10-03T16:00). Die Daten bleiben im Speicher, bis sich eine Datei
ändert. Zugang nur über Traefik mit Passwortabfrage (Container soccer-vorschau, docker-compose.yml); der Dienst
liest data/ und import/ nur.

Start im Container:   python -m website.vorschau
"""

from __future__ import annotations

import json
import mimetypes
import sys
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from . import einstellungen as W
from .daten import Daten, zeitreise
from .seiten import Kontext, hinweis_html, spieltag_html
from .spieltag import spieltag_daten

DATEN = Daten()
FOLGT = ("/methodik", "/impressum", "/datenschutz")
SICHERHEIT = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "same-origin",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": ("default-src 'self'; script-src 'self'; style-src 'self'; font-src 'self'; "
                                "img-src 'self' data:; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"),
}


class Antwort:
    def __init__(self, status: int, inhalt: bytes = b"", typ: str = "text/html; charset=utf-8", **kopf):
        self.status, self.inhalt, self.kopf = status, inhalt, {"Content-Type": typ, **kopf}


def _html(status: int, text: str) -> Antwort:
    return Antwort(status, text.encode("utf-8"), **{"Cache-Control": "no-store"})


def _datei(rest: str) -> Antwort:
    """Dateien aus statisch/ – nur von dort, keine Pfade nach oben."""
    ziel = (W.STATISCH / rest).resolve()
    if W.STATISCH.resolve() not in ziel.parents or not ziel.is_file():
        return Antwort(404, b"nicht gefunden", "text/plain; charset=utf-8")
    typ = {".woff2": "font/woff2", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8",
           ".txt": "text/plain; charset=utf-8"}.get(ziel.suffix, mimetypes.guess_type(ziel.name)[0] or "application/octet-stream")
    dauer = 2592000 if ziel.suffix == ".woff2" else 3600
    return Antwort(200, ziel.read_bytes(), typ, **{"Cache-Control": f"public, max-age={dauer}"})


def beantworten(pfad: str, query: str, daten: Daten = DATEN) -> Antwort:
    """Antwort für einen Aufruf (ohne Netzwerk testbar)."""
    prefix = W.PREFIX.rstrip("/")
    if pfad == f"{prefix}/_gesund":
        return Antwort(200, b"ok", "text/plain; charset=utf-8")
    if pfad != prefix and not pfad.startswith(prefix + "/"):
        return Antwort(404, b"nicht gefunden", "text/plain; charset=utf-8")
    rest = pfad[len(prefix):] or "/"
    if rest.startswith("/statisch/"):
        return _datei(rest[len("/statisch/"):])

    werte = parse_qs(query)
    datum = (werte.get("datum") or [None])[0] or None
    echt = daten.zeitpunkt()
    zp, ungueltig = zeitreise(datum, echt)
    k = Kontext(datum=None if ungueltig else datum, ungueltig=ungueltig, jetzt=zp.jetzt, zeitreise=zp.zeitreise)
    stand = zp.stand.isoformat(timespec="minutes") if zp.stand else None

    if rest in ("/", "/spieltag", "/spieltag/"):          # bis 0.19 ohne Startseite: weiter zum Spieltag
        return Antwort(302, b"", **{"Location": k.url(f"/spieltag/{W.STANDARD_LIGA}"), "Cache-Control": "no-store"})
    teile = [x for x in rest.split("/") if x]
    if len(teile) == 2 and teile[0] == "spieltag":
        web = W.liga_aus_slug(teile[1])
        if web is None:
            return _html(404, hinweis_html("fehlt", k, stand))
        return _html(200, spieltag_html(spieltag_daten(daten, web, zp), k))
    if len(teile) == 3 and teile[:2] == ["daten", "spieltag"] and teile[2].endswith(".json"):
        web = W.liga_aus_slug(teile[2][:-5])
        if web is None:
            return Antwort(404, b"{}", "application/json")
        inhalt = json.dumps(spieltag_daten(daten, web, zp), ensure_ascii=False, indent=1).encode("utf-8")
        return Antwort(200, inhalt, "application/json; charset=utf-8", **{"Cache-Control": "no-store"})
    if len(teile) == 2 and teile[0] == "spiel" and teile[1].isdigit():
        return _html(200, hinweis_html("folgt", k, stand))                 # Matchdetail folgt mit 0.18
    if rest.rstrip("/") in FOLGT:
        return _html(200, hinweis_html("folgt", k, stand, aktiv=rest.strip("/")))
    return _html(404, hinweis_html("fehlt", k, stand))


class Handler(BaseHTTPRequestHandler):
    server_version = "SoccerIntelligence"
    sys_version = ""

    def _senden(self, kopf_nur: bool = False) -> None:
        teile = urlsplit(self.path)
        try:
            a = beantworten(teile.path, teile.query)
        except Exception:  # noqa: BLE001 - jede Störung als Hinweisseite, Einzelheiten nur im Protokoll
            traceback.print_exc()
            try:
                a = _html(503, hinweis_html("daten", Kontext()))
            except Exception:  # noqa: BLE001
                a = Antwort(503, b"Daten werden gerade geprueft.", "text/plain; charset=utf-8")
        self.send_response(a.status)
        for name, wert in {**SICHERHEIT, **a.kopf, "Content-Length": str(len(a.inhalt))}.items():
            self.send_header(name, wert)
        self.end_headers()
        if not kopf_nur:
            self.wfile.write(a.inhalt)

    def do_GET(self) -> None:  # noqa: N802 - Name von BaseHTTPRequestHandler
        self._senden()

    def do_HEAD(self) -> None:  # noqa: N802
        self._senden(kopf_nur=True)

    def log_message(self, fmt, *args) -> None:  # kurzes Protokoll ohne Adresse des Besuchers
        sys.stdout.write("%s %s\n" % (self.log_date_time_string(), fmt % args))
        sys.stdout.flush()


def main() -> None:
    threading.Thread(target=DATEN.bestand, daemon=True).start()       # Daten im Hintergrund vorladen
    server = ThreadingHTTPServer(("0.0.0.0", W.PORT), Handler)
    print(f"Vorschau läuft auf Port {W.PORT} unter {W.PREFIX}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
