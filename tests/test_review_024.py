"""Version 0.24 – Absicherungen nach dem Backend- und Frontend-Review (24.11.2026).

R1 HTTP-Dienst: Zeitlimit, strenge Prüfung von Content-Length (negativ, zu gross, keine Zahl), Permissions-Policy.
R2 Dashboard-Anmeldung: Besucher-Adresse aus dem letzten X-Forwarded-For-Eintrag (nicht fälschbar).
R3 Kontaktformular: Bremse prüft und belegt in einem Schritt; gescheiterter Versand zählt nicht.
R4 Seitenspeicher: gleiche Seite in derselben Minute nur einmal gerechnet, auch bei gleichzeitigen Aufrufen.
R5 Datentausch: Während das Übergabe-Protokoll steht, bleibt der bisherige Datenstand der Website.
"""

from __future__ import annotations

import os
import socket
import threading
import time
from http.server import ThreadingHTTPServer

import anmeldung
from website import kontakt as KT
from website import vorschau as V
from website.daten import Daten, UEBERGABE


def _roh(port: int, anfrage: bytes) -> bytes:
    with socket.create_connection(("127.0.0.1", port), timeout=5) as s:
        s.sendall(anfrage)
        return s.recv(4096)


def test_r1_http_content_length_und_zeitlimit():
    assert V.Handler.timeout and V.Handler.timeout <= 30
    assert "Permissions-Policy" in V.SICHERHEIT and "camera=()" in V.SICHERHEIT["Permissions-Policy"]
    server = ThreadingHTTPServer(("127.0.0.1", 0), V.Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    try:
        kopf = b"POST /vorschau/de/kontakt/ HTTP/1.1\r\nHost: x\r\n"
        t = time.time()
        assert b" 400 " in _roh(port, kopf + b"Content-Length: -5\r\n\r\n")       # früher: Lesen bis Verbindungsende
        assert b" 400 " in _roh(port, kopf + b"Content-Length: abc\r\n\r\n")
        assert b" 413 " in _roh(port, kopf + b"Content-Length: 999999\r\n\r\n")
        assert time.time() - t < 3                                                  # sofort, ohne zu warten
    finally:
        server.shutdown()


def test_r2_dashboard_adresse_nicht_faelschbar():
    assert anmeldung.adresse_aus({"X-Forwarded-For": "6.6.6.6, 203.0.113.7"}) == "203.0.113.7"   # 6.6.6.6 = gefälscht
    assert anmeldung.adresse_aus({"X-Forwarded-For": "203.0.113.7"}) == "203.0.113.7"
    assert anmeldung.adresse_aus({"X-Real-Ip": "198.51.100.1"}) == "198.51.100.1"
    assert anmeldung.adresse_aus({}) == "unbekannt"


def test_r3_bremse_reserviert_in_einem_schritt():
    b = KT.Bremse()
    ergebnisse = []
    faeden = [threading.Thread(target=lambda: ergebnisse.append(b.reservieren("1.2.3.4", 1000.0))) for _ in range(10)]
    for f in faeden:
        f.start()
    for f in faeden:
        f.join()
    assert ergebnisse.count(True) == KT.MAX_JE_STUNDE                      # nie mehr als 3, auch gleichzeitig
    b.freigeben("1.2.3.4", 1000.0)
    assert b.reservieren("1.2.3.4", 1000.0)                                 # freigegebener Platz ist wieder frei
    assert b.reservieren("1.2.3.4", 1000.0 + 3601)                          # nach einer Stunde wieder erlaubt


def test_r3_gescheiterter_versand_zaehlt_nicht(monkeypatch):
    monkeypatch.setattr(KT, "BREMSE", KT.Bremse())
    form = {"email": ["a@b.ch"], "nachricht": ["Eine Nachricht mit Inhalt"], "einverstanden": ["ja"]}
    frage, token = KT.neue_aufgabe(1000.0)
    form.update(aufgabe=[token], antwort=[str(dict(KT.AUFGABEN)[frage])])
    env = {"SI_SMTP_HOST": "h", "SI_SMTP_USER": "u", "SI_SMTP_PASSWORT": "p", "SI_KONTAKT_AN": "info@x.ch"}
    for _ in range(5):                                                       # 5 gescheiterte Versuche …
        f = KT.bearbeiten(form, "9.9.9.9", "de", env=env, senden=lambda b, t, a: (False, "x"), jetzt=1000.0)
        assert f is not None and f.status == "versand_fehler"
    assert KT.bearbeiten(form, "9.9.9.9", "de", env=env, senden=lambda b, t, a: (True, "ok"), jetzt=1000.0) is None


def test_r4_seitenspeicher_rechnet_einmal():
    sp = V.Seitenspeicher()
    zaehler = []

    def rechnen():
        zaehler.append(1)
        time.sleep(0.05)
        return V.Antwort(200, b"seite")

    faeden = [threading.Thread(target=lambda: sp.holen(("a",), rechnen)) for _ in range(8)]
    for f in faeden:
        f.start()
    for f in faeden:
        f.join()
    assert len(zaehler) == 1                                                 # 8 gleichzeitige Aufrufe, eine Rechnung
    assert sp.holen(("a",), rechnen).inhalt == b"seite" and len(zaehler) == 1
    assert sp.holen(("b",), lambda: V.Antwort(404, b"")).status == 404
    assert ("b",) not in sp._seiten                                          # Fehlerseiten nie speichern


def test_r5_kein_gemischter_datenstand_waehrend_des_tauschs(tmp_path):
    d = Daten(import_dir=tmp_path)
    assert not d._tausch_laeuft()
    (tmp_path / UEBERGABE).write_text("{}", encoding="utf-8")
    assert d._tausch_laeuft()
    alt = time.time() - 700                                                  # älter als 10 Minuten: nicht mehr beachten
    os.utime(tmp_path / UEBERGABE, (alt, alt))
    assert not d._tausch_laeuft()
