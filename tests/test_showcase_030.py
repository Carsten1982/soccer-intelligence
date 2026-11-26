"""Showcase-Seiten (seit 0.30; Release_15, Entwürfe Showcase_G*, Design 575; docs/08_Website.md, Abschnitt 12).

S1 Adressen: vier Seiten DE (mit und ohne Schrägstrich), Englisch noch nicht freigeschaltet (404); noindex im HTML und
   im Kopf X-Robots-Tag; keine eingebetteten Stile oder Skripte; eine h1; eindeutige IDs.
S2 Navigation und Verlinkung: aktiver Reiter, Plattform-, Kontakt-, Impressum- und Datenschutz-Links, Karte 01 auf
   das Dashboard, Karten 02–04 ohne Link; keine Verweise auf Entwurfsdateien.
S3 Keine Verlinkung von der Plattform auf den Showcase (Seiten, Sitemap, robots.txt).
S4 Seite „Projekt“: Version aus der Plattform, Spiele aus der Datenbank, 23 Kombinationen, feste Zahlen nach Entscheid.
S5 Dashboard: Werte aus den Betriebsdateien (Läufe, Server, Alarme, Verlauf, Release), echte Tabelle.
S6 Leere Zustände und Ausfall: Hinweise statt Zahlen; nie interne Namen, Pfade oder Fehlertexte.
S7 Backend: Tageswerte (kennzahlen.json), Verfügbarkeit je Tag (server.json), release.json im Einspiel-Skript.
S8 Linkvorschau: og:image nur, wenn das Bild auf dem Server liegt; Foto mit alt-Text.
"""

from __future__ import annotations

import json
import os
import re
import sys
from html import escape
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_website_021 import dienst  # noqa: F401 - Fixture

from core import settings
from website import einstellungen as W
from website import showcase as SC
from website import sitemap as SM
from website import vorschau
from website.daten import Zeitpunkt
from website.texte import t

ROOT = Path(__file__).resolve().parents[1]
SEITEN = {"start": "/showcase", "projekt": "/showcase/project", "ki": "/showcase/ki-automation",
          "daten": "/showcase/ki-automation/data"}
JETZT = datetime(2026, 11, 26, 14, 0)


def _seite(d, pfad):
    vorschau.SEITEN.leeren()
    return vorschau.beantworten("/vorschau" + pfad, "", d)


# --- S1 Adressen und Index -----------------------------------------------------------------------------------------

@pytest.mark.parametrize("seite, pfad", SEITEN.items())
def test_s1_seiten_noindex_und_sauber(dienst, seite, pfad):
    for p in (pfad, pfad + "/"):
        a = _seite(dienst, p)
        html = a.inhalt.decode()
        assert a.status == 200 and a.kopf["X-Robots-Tag"] == "noindex, nofollow"
        assert '<meta name="robots" content="noindex, nofollow">' in html and '<html lang="de">' in html
        assert html.count("<h1") == 1 and "style=" not in html and "<style" not in html and "<script" not in html
        assert not re.search(r"\son[a-z]+=", html)
        ids = re.findall(r'\sid="([^"]+)"', html)
        assert len(ids) == len(set(ids))
        assert f"<title>{escape(t(f'showcase.{seite}.title'))}</title>" in html
        assert f'<meta name="description" content="{escape(t(f"showcase.{seite}.description"))}">' in html


def test_s1_englisch_noch_nicht_frei(dienst):
    assert SC.SPRACHEN_FREI == ("de",)
    for p in ("/en/showcase", "/en/showcase/project", "/en/showcase/ai-automation/data"):
        assert _seite(dienst, p).status == 404
    assert SC.erkennen("/showcase/gibt-es-nicht") is None and SC.erkennen("/showcases") is None


def test_s1_oeffentlich_ohne_vorschau(dienst, monkeypatch):
    monkeypatch.setattr(W, "VORSCHAU", False)
    a = _seite(dienst, "/showcase")
    assert a.kopf["Cache-Control"] == "public, max-age=60" and a.kopf["X-Robots-Tag"] == "noindex, nofollow"


# --- S2 Navigation und Verlinkung ----------------------------------------------------------------------------------

@pytest.mark.parametrize("seite, aktiv", [("start", "Showcase"), ("projekt", "Projekt"), ("ki", "KI &amp; Automatisierung"),
                                          ("daten", "KI &amp; Automatisierung")])
def test_s2_navigation(dienst, seite, aktiv):
    html = _seite(dienst, SEITEN[seite]).inhalt.decode()
    nav = html.split('<nav class="sc-nav"', 1)[1].split("</nav>", 1)[0]
    assert re.findall(r'aria-current="page">([^<]+)</a>', nav) == [aktiv]
    reiter = re.findall(r'<a class="sc-reiter" href="([^"]+)"', nav)
    assert reiter == ["/vorschau/showcase", "/vorschau/showcase/project", "/vorschau/de/", "/vorschau/showcase/ki-automation"]
    assert 'href="/vorschau/de/kontakt/"' in nav
    fuss = html.split('<footer class="sc-fuss">', 1)[1]
    for ziel in ("/vorschau/showcase", "/vorschau/de/kontakt/", "/vorschau/de/impressum/", "/vorschau/de/datenschutz/"):
        assert f'href="{ziel}"' in fuss
    assert ".dc.html" not in html and 'href="#' not in html.replace('href="#inhalt"', "")


def test_s2_karten(dienst):
    start = _seite(dienst, "/showcase").inhalt.decode()
    karten = re.findall(r'<a id="(\w+)" class="sg-card[^"]*" href="([^"]+)"', start)
    assert karten == [("projekt", "/vorschau/showcase/project"), ("plattform", "/vorschau/de/"),
                      ("ki", "/vorschau/showcase/ki-automation")]
    ki = _seite(dienst, "/showcase/ki-automation").inhalt.decode()
    assert re.findall(r'<a id="([\w-]+)" class="sg-card', ki) == ["datenmonitoring"]
    assert 'href="/vorschau/showcase/ki-automation/data"' in ki
    for kid in ("besuchermonitoring", "seo-agent", "competitor-agent"):
        assert f'<div id="{kid}" class="sg-card' in ki
    assert ki.count("sc-chip-live") == 1 and ki.count("sc-chip-dev") == 3
    assert "● Im Betrieb" in ki and ki.count("○ In Entwicklung") == 3
    daten = _seite(dienst, "/showcase/ki-automation/data").inhalt.decode()
    assert 'href="/vorschau/showcase/ki-automation"' in daten                   # Rücklink


# --- S3 Keine Verlinkung von der Plattform -----------------------------------------------------------------------

@pytest.mark.parametrize("pfad", ["/de/", "/en/", "/de/spieltag/bundesliga/", "/de/methodik/", "/de/glossar/",
                                  "/de/kontakt/", "/de/impressum/", "/de/datenschutz/", "/de/cookie-einstellungen/",
                                  "/de/gibt-es-nicht/"])
def test_s3_plattform_verlinkt_nie_auf_den_showcase(dienst, pfad):
    assert "showcase" not in _seite(dienst, pfad).inhalt.decode().lower()


def test_s3_nicht_in_sitemap_und_robots(dienst):
    assert "showcase" not in SM.robots()
    assert "showcase" not in SM.sitemap("/sitemap.xml", dienst) and "showcase" not in SM.sitemap("/sitemaps/seiten.xml", dienst)


# --- S4 Seite „Projekt“ -----------------------------------------------------------------------------------------

def test_s4_projekt_zahlen(dienst, monkeypatch):
    zahlen = {"Bundesliga": 2538, "Premier League": 3150, "Serie A": 3160, "LaLiga": 3169}
    db = SimpleNamespace(leagues={k: [0] * n for k, n in zahlen.items()})
    monkeypatch.setattr(dienst, "bestand", lambda: SimpleNamespace(db=db, gesperrt=False), raising=False)
    html = _seite(dienst, "/showcase/project").inhalt.decode()
    assert SC.version() == settings.APP_VERSION.split(" ")[0] == "0.30"
    assert f">{SC.version()}</b>" in html                                         # Version aus einer Quelle
    assert html.count(">12’017<") == 2                                            # Produkt und „Projekt in Zahlen“
    assert html.count(">23<") == 2 and html.count(">4<") >= 2
    assert ">7’524<" in html and ">4’621<" in html and html.count("&gt;\u00a0800<") == 2
    assert "○ In Entwicklung" in html                                             # Wettbewerbsmonitoring
    assert t("showcase.projekt.lead") == t("showcase.start.lead")                 # gleicher Hero-Satz (Entscheid)
    assert "n8n" in html                                                          # bleibt (Entscheid Carsten)


def test_s4_ohne_datenbank(dienst):
    html = _seite(dienst, "/showcase/project").inhalt.decode()                   # Attrappe ohne Datenbank
    assert html.count(">–<") == 2


# --- S5 Dashboard mit Werten aus dem Backend ----------------------------------------------------------------------

def _betrieb(ordner: Path) -> None:
    ev = [{"zeit": "2026-11-26T04:00:00", "lauf": "a", "anlass": "kontrolle", "status": "übernommen (automatisch)"},
          {"zeit": "2026-11-25T22:15:00", "lauf": "b", "anlass": "spiel", "status": "übernommen (automatisch)"},
          {"zeit": "2026-11-25T04:00:00", "lauf": "c", "anlass": "kontrolle", "status": "wartet"},
          {"zeit": "2026-11-24T23:15:00", "lauf": "d", "anlass": "wiederholung", "status": "fehlgeschlagen"},
          {"zeit": "2026-11-24T04:00:00", "art": "alarm", "alarm": "x"},
          {"zeit": "2026-11-10T04:00:00", "lauf": "e", "anlass": "kontrolle", "status": "übernommen"}]
    (ordner / "ereignisse.jsonl").write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in ev) + "\n", encoding="utf-8")
    (ordner / "server.json").write_text(json.dumps({
        "zeit": "2026-11-26T13:59:00", "festplatte": 17, "speicher": 55, "cpu": 8,
        "container": {"football-dashboard": {"status": "running"}, "soccer-import": {"status": "running"}},
        "website": {"/de/": 200, "/sitemap.xml": 200}, "verfuegbarkeit": {"2026-11-25": [1440, 1440], "2026-11-26": [840, 830]}}),
        encoding="utf-8")
    _alter(ordner / "server.json", datetime(2026, 11, 26, 13, 59))
    (ordner / "kennzahlen.json").write_text(json.dumps({
        "verlauf": [{"tag": f"2026-11-{20 + i}", "fehler": 0, "warnungen": 0, "hinweise": 230 + i} for i in range(7)],
        "backups": {"anzahl": 12, "neueste": "2026-11-26"}}), encoding="utf-8")
    (ordner / "release.json").write_text(json.dumps({"version": "0.30", "tests": 810, "ergebnis": "bestanden"}), encoding="utf-8")


def _alter(datei: Path, ortszeit: datetime) -> None:
    """Änderungszeit der Datei auf diese Schweizer Ortszeit setzen (das Dashboard prüft die Aktualität daran)."""
    ts = ortszeit.replace(tzinfo=SC.ZONE).timestamp()
    os.utime(datei, (ts, ts))


def _daten(dienst, ordner, monkeypatch):
    zahlen = {"Bundesliga": 2538, "Premier League": 3150, "Serie A": 3160, "LaLiga": 3169}
    db = SimpleNamespace(leagues={k: [0] * n for k, n in zahlen.items()},
                         file_modified=datetime(2026, 11, 26, 3, 2, tzinfo=timezone.utc),   # Dateizeit in UTC
                         count=lambda s: {"Fehler": 0, "Warnung": 1}.get(s, 236))
    fx = SimpleNamespace(count=lambda s: 0)
    monkeypatch.setattr(dienst, "bestand", lambda: SimpleNamespace(db=db, fx=fx, gesperrt=False), raising=False)
    monkeypatch.setattr(dienst, "zeitpunkt", lambda: Zeitpunkt(JETZT, datetime(2026, 11, 26, 4, 0), None), raising=False)
    monkeypatch.setattr(dienst, "import_dir", ordner, raising=False)
    monkeypatch.setattr(settings, "FIXTURES_FILE", ordner / "gibt-es-nicht.xlsx")
    return _seite(dienst, "/showcase/ki-automation/data").inhalt.decode()


def test_s5_dashboard_werte(dienst, tmp_path, monkeypatch):
    _betrieb(tmp_path)
    html = _daten(dienst, tmp_path, monkeypatch)
    assert "Systemstatus: Alles im grünen Bereich" in html and "Stand: 26.11.2026 · 14:00" in html
    assert ">12’017<" in html and ">3’169<" in html and "26.11.2026" in html and "04:02 Uhr" in html
    assert ">0 Fehler<" in html and ">1 Warnungen<" in html and ">236<" in html
    assert ">810<" in html and "Version 0.30 · Tests bestanden" in html
    tabelle = html.split('<table class="sc-tabelle">', 1)[1].split("</table>", 1)[0]
    assert tabelle.count('<th scope="col">') == 4 and tabelle.count("<tr>") == 6       # Kopf + 5 Läufe
    assert "<td>Do 26.11.2026</td><td>04:00</td><td>Kontrolllauf</td>" in tabelle
    assert "sc-ergebnis-warte" in tabelle and "sc-ergebnis-fehler" in tabelle and "Wiederholung" in tabelle
    assert "Diese Woche: 4 Läufe, davon 2 übernommen" in html                      # Lauf vom 10.11. zählt nicht
    assert "Nächster geplanter Lauf: morgen 04:00" in html
    assert html.count('<circle cx="') >= 7 and "Hinweise der letzten 7 Tage" in html
    for wert in (">Erreichbar<", ">Normal<", ">Alle laufen<", ">Aktuell<", ">Keine<", "Diese Woche: 0", "99,6 %",
                 "Gemessen seit 25.11.2026", "Stand: 26.11.2026 · 13:59"):
        assert wert in html, wert
    for alt in ("Beispiel", "Entwurf:", "~790", "236</div><div class=\"sx-173\">Verlauf ab"):
        assert alt not in html, alt


def test_s5_status_aus_alarmen(dienst, tmp_path, monkeypatch):
    _betrieb(tmp_path)
    (tmp_path / "alarme.json").write_text(json.dumps({"aktiv": {"import": {"titel": "x", "stufe": "kritisch", "seit": "2026-11-26T05:00:00"}}}), encoding="utf-8")
    html = _daten(dienst, tmp_path, monkeypatch)
    assert "sc-status-kritisch" in html and "Systemstatus: Störung" in html and ">1<" in html


# --- S6 Leere Zustände, keine internen Angaben ----------------------------------------------------------------------

def test_s6_leere_zustaende(dienst, tmp_path, monkeypatch):
    html = _daten(dienst, tmp_path, monkeypatch)                                  # keine Betriebsdateien
    for text in ("Wird beim nächsten Release erfasst", "Noch keine Läufe im Protokoll.", "Diese Woche: noch keine Läufe",
                 "Werte vorübergehend nicht verfügbar", "Verlauf ab – (tägliche Aufzeichnung).", "Messung ab diesem Release"):
        assert text in html, text
    _betrieb(tmp_path)
    _alter(tmp_path / "server.json", datetime(2026, 11, 26, 10, 0))               # Prüfskript meldet sich nicht mehr
    html = _daten(dienst, tmp_path, monkeypatch)
    assert "Werte vorübergehend nicht verfügbar" in html and ">Erreichbar<" not in html


def test_s6_keine_internen_angaben(dienst, tmp_path, monkeypatch):
    _betrieb(tmp_path)
    html = _daten(dienst, tmp_path, monkeypatch)
    for intern in ("football-dashboard", "soccer-import", "soccer-website", "traefik", "/import/", "/data/", "/backup/",
                   "72.60.", "srv1774622", "@soccer-intelligence", "fehlgeschlagen:"):
        assert intern not in html, intern


# --- S7 Backend ------------------------------------------------------------------------------------------------------

def test_s7_tageswerte(tmp_path, monkeypatch):
    from betrieb import kennzahlen
    monkeypatch.setattr(settings, "DATABASE_FILE", tmp_path / "db.xlsx")
    monkeypatch.setattr(settings, "FIXTURES_FILE", tmp_path / "fx.xlsx")
    (tmp_path / "db.xlsx").write_bytes(b"a")
    sicherung = tmp_path / "backup"
    sicherung.mkdir()
    for tag in ("2026-11-24", "2026-11-26"):
        (sicherung / f"Database-Soccer-Intelligence_{tag}_040000_x_vor_import.xlsx").write_bytes(b"x")
    zaehler = iter([{"fehler": 0, "warnungen": 0, "hinweise": 236}, {"fehler": 0, "warnungen": 0, "hinweise": 240},
                    {"fehler": 0, "warnungen": 0, "hinweise": 241}])
    zaehlen = lambda: next(zaehler)                                                  # noqa: E731
    assert kennzahlen.aktualisieren(tmp_path, sicherung, datetime(2026, 11, 26, 4, 30), zaehlen)
    assert not kennzahlen.aktualisieren(tmp_path, sicherung, datetime(2026, 11, 26, 9, 0), zaehlen)   # einmal am Tag
    (tmp_path / "db.xlsx").write_bytes(b"neu")                                       # neue Fassung: neu zählen
    assert kennzahlen.aktualisieren(tmp_path, sicherung, datetime(2026, 11, 26, 22, 0), zaehlen)
    assert kennzahlen.aktualisieren(tmp_path, sicherung, datetime(2026, 11, 27, 4, 30), zaehlen)
    k = json.loads((tmp_path / "kennzahlen.json").read_text())
    assert [(v["tag"], v["hinweise"]) for v in k["verlauf"]] == [("2026-11-26", 240), ("2026-11-27", 241)]
    assert k["backups"] == {"anzahl": 2, "neueste": "2026-11-26"}


def test_s7_verfuegbarkeit_je_tag(tmp_path):
    sys.path.insert(0, str(ROOT / "tools"))
    import ueberwachen as U
    datei = tmp_path / "server.json"
    for i, code in enumerate((200, 200, 502)):
        U.server_json(datei, {"website": {"/de/": code}}, datetime(2026, 11, 26, 10, i))
    U.server_json(datei, {"website": {"/": 200}}, datetime(2026, 11, 27, 0, 1))        # vor dem Livegang: „/“
    assert json.loads(datei.read_text())["verfuegbarkeit"] == {"2026-11-26": [3, 2], "2026-11-27": [1, 1]}


def test_s7_release_json_im_einspiel_skript():
    skript = (ROOT / "tools" / "einspielen.sh").read_text(encoding="utf-8")
    assert '"import/release.json"' in skript and 'zahl("passed") + zahl("skipped") + zahl("deselected")' in skript
    assert skript.index("release.json") < skript.index("6/6: Prüfung im Browser")
    dienst_py = (ROOT / "app" / "importer" / "dienst.py").read_text(encoding="utf-8")
    assert "kennzahlen.aktualisieren(base, E.BACKUP_DIR, local)" in dienst_py


# --- S8 Linkvorschau und Foto -------------------------------------------------------------------------------------

def test_s8_vorschau_bild_und_foto(dienst, tmp_path, monkeypatch):
    monkeypatch.setattr(W, "BILDER", tmp_path)
    html = _seite(dienst, "/showcase").inhalt.decode()
    assert "og:image" not in html and "sc-foto-leer" in html and "<img" not in html
    (tmp_path / SC.FOTO).write_bytes(b"RIFF....WEBP")
    (tmp_path / SC.VORSCHAU_BILD).write_bytes(b"\xff\xd8")
    html = _seite(dienst, "/showcase").inhalt.decode()
    assert '<meta property="og:image" content="https://soccer-intelligence.com/bilder/showcase-vorschau.jpg">' in html
    assert '<img src="/vorschau/bilder/showcase-portrait.webp" alt="Porträt von Carsten Thiele"' in html
    a = vorschau.beantworten("/vorschau/bilder/showcase-portrait.webp", "", dienst)
    assert a.status == 200 and a.kopf["Content-Type"] == "image/webp"
    assert vorschau.beantworten("/vorschau/bilder/andere.jpg", "", dienst).status == 404
    assert '<meta property="og:url" content="https://soccer-intelligence.com/showcase">' in html


def test_s9_zeitzonen(dienst, tmp_path, monkeypatch):
    """Fehler gefunden nach dem Einspielen von 0.30 (Carsten, 26.11.2026): Datenstand in UTC (03:01 statt 04:01) und
    Server-Werte „nicht verfügbar“, weil das Prüfskript „zeit“ in der Uhrzeit des Servers (UTC) schreibt."""
    _betrieb(tmp_path)
    alt = json.loads((tmp_path / "server.json").read_text())
    alt["zeit"] = "2026-11-26T12:59:00"                                           # UTC des Servers, eine Stunde „zurück“
    (tmp_path / "server.json").write_text(json.dumps(alt))
    _alter(tmp_path / "server.json", datetime(2026, 11, 26, 13, 59))
    html = _daten(dienst, tmp_path, monkeypatch)
    assert "04:02 Uhr" in html and "03:02 Uhr" not in html                       # Datenstand in Schweizer Zeit
    assert ">Erreichbar<" in html and "Stand: 26.11.2026 · 13:59" in html        # Server-Werte frisch
    assert SC.ortszeit(datetime(2026, 7, 1, 2, 0, tzinfo=timezone.utc)) == datetime(2026, 7, 1, 4, 0)    # Sommerzeit
    assert SC.ortszeit(datetime(2026, 11, 26, 4, 0)) == datetime(2026, 11, 26, 4, 0)                    # ohne Zone

