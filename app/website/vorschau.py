"""Vorschau der Website unter https://soccer-intelligence.com/vorschau (Konzept 08, Abschnitte 3, 4 und 6; seit 0.21
Adressen /de/ und /en/ nach adressen.py, Sitemap und robots.txt nach sitemap.py).

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
from urllib.parse import parse_qs, quote, urlsplit

from . import adressen as AD
from . import einstellungen as W
from . import kontakt as KT
from . import methodik as MT
from . import seo
from . import sitemap as SM
from .daten import Daten, zeitreise
from .seiten import Kontext, archiv_html, fehlt_html, hinweis_html, inhalt_html, spiel_html, spieltag_html, start_html
from .spiel import spiel_daten
from .spieltag import archiv_daten, spieltag_daten
from .start import start_daten

KT_MAX_BYTES = 20_000             # Kontaktformular: grösste Anfrage (5'000 Zeichen Nachricht plus Felder)

DATEN = Daten()
SICHERHEIT = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "same-origin",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": ("default-src 'self'; script-src 'self'; style-src 'self'; font-src 'self'; "
                                "img-src 'self' data:; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"),
}
WURZEL = W.STATISCH / "wurzel"                  # Icons und og-image (im Livebetrieb im Hauptverzeichnis der Domain)
WURZEL_DATEIEN = {"favicon.ico": "image/x-icon", "favicon.svg": "image/svg+xml", "favicon-64.png": "image/png",
                  "apple-touch-icon.png": "image/png", "og-image.png": "image/png",
                  # seit 0.24: Icons des Web-App-Manifests (aus favicon.svg abgeleitet, Entscheid Carsten 24.11.2026)
                  "icon-192.png": "image/png", "icon-512.png": "image/png", "icon-maskable-512.png": "image/png"}
THEME_FARBE = "#0B3D2E"                         # Markengrün (--gruen), auch <meta name="theme-color">
HINTERGRUND = "#F4F7F2"                         # Seitenhintergrund (--bg)
SEITE_CACHE = "public, max-age=300"             # Browser 5 Minuten (Beschluss 19.11.2026); Vorschau ohne Cache
DATENSEITEN = ("start", "spieltag", "archiv", "spiel")


class Antwort:
    def __init__(self, status: int, inhalt: bytes = b"", typ: str = "text/html; charset=utf-8", **kopf):
        self.status, self.inhalt, self.kopf = status, inhalt, {"Content-Type": typ, **kopf}


def _html(status: int, text: str, vorschau: bool | None = None) -> Antwort:
    vorschau = W.VORSCHAU if vorschau is None else vorschau
    cache = "no-store" if vorschau or status >= 400 else SEITE_CACHE
    return Antwort(status, text.encode("utf-8"), **{"Cache-Control": cache})


def _json(daten: dict) -> Antwort:
    inhalt = json.dumps(daten, ensure_ascii=False, indent=1).encode("utf-8")
    return Antwort(200, inhalt, "application/json; charset=utf-8", **{"Cache-Control": "no-store"})


def _weiter(ziel: str, status: int, query: str = "") -> Antwort:
    """Weiterleitung in einem Schritt (301 dauerhaft, 302 vorübergehend); die Zeitreise (?datum=) bleibt erhalten."""
    return Antwort(status, b"", **{"Location": ziel + (f"?{query}" if query else ""), "Cache-Control": "no-store"})


def _datei(rest: str) -> Antwort:
    """Dateien aus statisch/ – nur von dort, keine Pfade nach oben. CSS und JS tragen eine Versionsnummer (?v=), darum
    30 Tage im Browser (Beschluss 19.11.2026)."""
    ziel = (W.STATISCH / rest).resolve()
    if W.STATISCH.resolve() not in ziel.parents or not ziel.is_file():
        return Antwort(404, b"nicht gefunden", "text/plain; charset=utf-8")
    typ = {".woff2": "font/woff2", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8",
           ".txt": "text/plain; charset=utf-8"}.get(ziel.suffix, mimetypes.guess_type(ziel.name)[0] or "application/octet-stream")
    return Antwort(200, ziel.read_bytes(), typ, **{"Cache-Control": "public, max-age=2592000"})


def _wurzel(name: str) -> Antwort:
    datei = WURZEL / name
    if not datei.is_file():
        return Antwort(404, b"nicht gefunden", "text/plain; charset=utf-8")
    return Antwort(200, datei.read_bytes(), WURZEL_DATEIEN[name], **{"Cache-Control": "public, max-age=2592000"})


def _manifest(prefix: str) -> Antwort:
    """Web-App-Manifest (seit 0.24, Frontend-Review Punkt 10; Entscheid Carsten 24.11.2026): „Zum Home-Bildschirm“
    mit Icon und Namen. display „browser“ statt „standalone“, damit der Zurück-Knopf des Browsers bleibt."""
    daten = {"name": "Soccer Intelligence", "short_name": "Soccer Intel", "lang": "de",
             "start_url": f"{prefix}/", "scope": f"{prefix}/", "display": "browser",
             "theme_color": THEME_FARBE, "background_color": HINTERGRUND,
             "icons": [{"src": f"{prefix}/icon-192.png", "sizes": "192x192", "type": "image/png"},
                       {"src": f"{prefix}/icon-512.png", "sizes": "512x512", "type": "image/png"},
                       {"src": f"{prefix}/icon-maskable-512.png", "sizes": "512x512", "type": "image/png",
                        "purpose": "maskable"}]}
    return Antwort(200, json.dumps(daten, ensure_ascii=False).encode("utf-8"), "application/manifest+json",
                   **{"Cache-Control": "public, max-age=86400"})


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
    if rest.lstrip("/") in WURZEL_DATEIEN:
        return _wurzel(rest.lstrip("/"))
    if rest == "/manifest.webmanifest":
        return _manifest(prefix)
    if rest == "/robots.txt":
        return Antwort(200, SM.robots().encode("utf-8"), "text/plain; charset=utf-8", **{"Cache-Control": "public, max-age=3600"})
    if rest == "/sitemap.xml" or rest.startswith("/sitemaps/"):
        return _sitemap(rest, daten)
    if rest == f"/bilder/{W.FOTO}":                         # Foto der Startseite, nur vom Server (Q6)
        foto = W.BILDER / W.FOTO
        if not foto.is_file():
            return Antwort(404, b"nicht gefunden", "text/plain; charset=utf-8")
        return Antwort(200, foto.read_bytes(), "image/jpeg", **{"Cache-Control": "public, max-age=3600"})

    werte = parse_qs(query)
    datum = (werte.get("datum") or [None])[0] or None
    echt = daten.zeitpunkt()
    zp, ungueltig = zeitreise(datum, echt)
    k = Kontext(datum=None if ungueltig else datum, ungueltig=ungueltig, jetzt=zp.jetzt, zeitreise=zp.zeitreise,
                vorschau=W.VORSCHAU)
    stand = zp.stand.isoformat(timespec="minutes") if zp.stand else None
    q = f"datum={quote(datum)}" if datum and not ungueltig else ""

    if rest.startswith("/daten/"):                           # Datensätze als JSON (Prüfung, Vorschau)
        return _daten_json(rest, daten, zp)

    datei = MT.download_sprache(rest)                       # Excel-Datei der Methodik (seit 0.21)
    if datei:
        return Antwort(200, MT.excel(datei), MT.XLSX, **{
            "Cache-Control": "no-store" if W.VORSCHAU else "public, max-age=86400",
            "Content-Disposition": f'attachment; filename="{MT.DATEI[datei]}"'})

    erk = AD.erkennen(rest)
    if erk.weiter and erk.status in (301, 302) and (erk.ziel is None or erk.ziel.art != "spiel"):
        return _weiter(prefix + erk.weiter, erk.status, q)
    if erk.status == 404 or erk.ziel is None:
        return _html(404, fehlt_html(k.mit(lang=erk.lang), stand))
    z = erk.ziel
    k = k.mit(lang=z.lang)
    if z.art in DATENSEITEN and daten.bestand().gesperrt:     # Dateifehler: 503 mit Retry-After, nie zwischengespeichert
        return Antwort(503, hinweis_html("daten", k, stand).encode("utf-8"),
                       **{"Cache-Control": "no-store", "Retry-After": "600"})

    if z.art == "start":
        foto = f"{prefix}/bilder/{W.FOTO}" if (W.BILDER / W.FOTO).is_file() else None
        return _html(200, start_html(start_daten(daten, zp), k, foto))
    if z.art == "spieltag":
        return _html(200, spieltag_html(spieltag_daten(daten, W.liga_aus_slug(z.liga), zp), k))
    if z.art == "archiv":
        seite = archiv_daten(daten, W.liga_aus_slug(z.liga), z.saison, z.nr, zp) if seo.saison_hat_seiten(z.saison) else None
        if seite is None:
            return _html(404, fehlt_html(k, stand))
        return _html(200, archiv_html(seite, k))
    if z.art == "spiel":
        return _spiel(z, rest, daten, zp, k, stand, prefix, q)
    if z.art == "cookie":                                    # Cookie-Einstellungen folgen mit 0.22
        return _html(200, hinweis_html("folgt", k, stand, aktiv=z.art))
    if z.art == "kontakt":                                   # seit 0.23: Formular mit Sicherheitsfrage, nie zwischenspeichern
        f = KT.leer(gesendet="gesendet" in werte)
        return Antwort(200, inhalt_html(z.art, k, stand, f=f).encode("utf-8"), **{"Cache-Control": "no-store"})
    return _html(200, inhalt_html(z.art, k, stand))


def beantworten_post(pfad: str, inhalt: bytes, ip: str, daten: Daten = DATEN, senden=None) -> Antwort:
    """POST: nur das Kontaktformular (seit 0.23). Erfolg -> 303 auf die Seite mit ?gesendet=1 (kein doppeltes Senden
    beim Neuladen); Fehler -> Seite mit Eingaben und Fehlern je Feld."""
    prefix = W.PREFIX.rstrip("/")
    rest = pfad[len(prefix):] if pfad.startswith(prefix + "/") else None
    erk = AD.erkennen(rest) if rest else None
    if erk is None or erk.ziel is None or erk.ziel.art != "kontakt" or erk.weiter:
        return Antwort(405, b"nicht erlaubt", "text/plain; charset=utf-8", **{"Allow": "GET, HEAD"})
    if len(inhalt) > KT_MAX_BYTES:
        return Antwort(413, b"zu gross", "text/plain; charset=utf-8")
    form = parse_qs(inhalt.decode("utf-8", errors="replace"), keep_blank_values=True)
    k = Kontext(vorschau=W.VORSCHAU).mit(lang=erk.ziel.lang)
    f = KT.bearbeiten(form, ip, erk.ziel.lang, senden=senden)
    if f is None:
        return _weiter(pfad, 303, "gesendet=1")
    zp = daten.zeitpunkt()
    k = k.mit(jetzt=zp.jetzt)
    stand = zp.stand.isoformat(timespec="minutes") if zp.stand else None
    return Antwort(200, inhalt_html("kontakt", k, stand, f=f).encode("utf-8"), **{"Cache-Control": "no-store"})


def _spiel(z: AD.Ziel, rest: str, daten: Daten, zp, k: Kontext, stand, prefix: str, q: str) -> Antwort:
    """Spielseite: unbekannte ID → 404; ältere Saisons ohne Seiten → 404; abweichende Adresse → 301 auf die richtige."""
    treffer = daten.spiel(z.spiel_id)
    if treffer is None:
        return _html(404, fehlt_html(k, stand))
    liga, row = treffer
    web = next((lg for lg in W.LIGEN if lg.name == liga), None)
    if web is None or not seo.saison_hat_seiten(row.saison):
        return _html(404, fehlt_html(k, stand))
    richtig = AD.pfad(AD.Ziel("spiel", z.lang, liga=web.slug, slug=AD.spiel_slug(row.heim, row.gast, z.spiel_id)))
    if rest != richtig:
        return _weiter(prefix + richtig, 301, q)
    seite = spiel_daten(daten, z.spiel_id, zp)
    if seite is None:
        return _html(404, fehlt_html(k, stand))
    return _html(200, spiel_html(seite, k))


def _daten_json(rest: str, daten: Daten, zp) -> Antwort:
    teile = [x for x in rest.split("/") if x]
    if teile == ["daten", "start.json"]:
        return _json(start_daten(daten, zp))
    if len(teile) == 3 and teile[1] == "spieltag" and teile[2].endswith(".json"):
        web = W.liga_aus_slug(teile[2][:-5])
        return _json(spieltag_daten(daten, web, zp)) if web else Antwort(404, b"{}", "application/json")
    if len(teile) == 3 and teile[1] == "spiel" and teile[2].endswith(".json") and teile[2][:-5].isdigit():
        seite = spiel_daten(daten, int(teile[2][:-5]), zp)
        return _json(seite) if seite is not None else Antwort(404, b"{}", "application/json")
    return Antwort(404, b"{}", "application/json")


def _sitemap(rest: str, daten: Daten) -> Antwort:
    xml = SM.sitemap(rest, daten)
    if xml is None:
        return Antwort(404, b"nicht gefunden", "text/plain; charset=utf-8")
    return Antwort(200, xml.encode("utf-8"), "application/xml; charset=utf-8", **{"Cache-Control": "public, max-age=3600"})


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
                a = Antwort(503, hinweis_html("daten", Kontext()).encode("utf-8"),
                            **{"Cache-Control": "no-store", "Retry-After": "600"})
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

    def do_POST(self) -> None:  # noqa: N802 - nur das Kontaktformular (seit 0.23)
        try:
            laenge = min(int(self.headers.get("Content-Length") or 0), KT_MAX_BYTES + 1)
        except ValueError:
            laenge = 0
        inhalt = self.rfile.read(laenge) if laenge else b""
        # Absender-Adresse für die Anfragebremse: der letzte Eintrag stammt von Traefik (nicht vom Besucher fälschbar)
        weiter = [x.strip() for x in (self.headers.get("X-Forwarded-For") or "").split(",") if x.strip()]
        ip = weiter[-1] if weiter else self.client_address[0]
        try:
            a = beantworten_post(urlsplit(self.path).path, inhalt, ip)
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            a = Antwort(503, b"Bitte spaeter noch einmal versuchen.", "text/plain; charset=utf-8")
        self.send_response(a.status)
        for name, wert in {**SICHERHEIT, **a.kopf, "Content-Length": str(len(a.inhalt))}.items():
            self.send_header(name, wert)
        self.end_headers()
        self.wfile.write(a.inhalt)

    def log_message(self, fmt, *args) -> None:  # kurzes Protokoll ohne Adresse des Besuchers
        sys.stdout.write("%s %s\n" % (self.log_date_time_string(), fmt % args))
        sys.stdout.flush()


def vorladen(daten: Daten = DATEN) -> None:
    """Beim Start alles einmal rechnen (Daten, Startseite, Spieltag je Liga), damit schon der erste Aufruf schnell
    ist. Fehler hier stoppen den Dienst nicht; die Seite meldet sie dann selbst."""
    try:
        zp = daten.zeitpunkt()
        start_daten(daten, zp)
        for web in W.LIGEN:
            spieltag_daten(daten, web, zp)
        print("Vorschau: Daten vorgeladen", flush=True)
    except Exception:  # noqa: BLE001
        traceback.print_exc()


def main() -> None:
    threading.Thread(target=vorladen, daemon=True).start()            # Daten im Hintergrund vorladen
    server = ThreadingHTTPServer(("0.0.0.0", W.PORT), Handler)
    print(f"Vorschau läuft auf Port {W.PORT} unter {W.PREFIX}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
