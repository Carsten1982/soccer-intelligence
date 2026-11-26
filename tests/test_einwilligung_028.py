"""Einwilligung und Google Analytics 4 (seit 0.28; Entwürfe Cookie_Hinweis und Cookie_Einstellungen, Entscheide Carsten
25./26.11.2026, docs/08_Website.md, Abschnitt 4.3). Testfälle E1–E7:

E1 Cookie-Hinweis in jeder Seite (verborgen), Bereich mit Beschriftung, zwei gleichwertige Knöpfe, kein Link; nicht auf
   der Seite Cookie-Einstellungen; Texte DE/EN nach Entwurf.
E2 Vor der Zustimmung nichts von Google: keine Google-Adresse im HTML; Mess-ID nur auf der öffentlichen Website
   (nie in der Vorschau); site.js lädt Google nur in messen(), und messen() läuft nur nach Zustimmung.
E3 Seite Cookie-Einstellungen: zeigt die gespeicherte Wahl, noindex,follow, nie zwischengespeichert, nicht in der Sitemap.
E4 Ohne Skript: Formular speichert die Wahl (6 Monate), Ablehnen löscht _ga und _ga_*; ungültige Wahl 400.
E5 Sicherheitsrichtlinie: Google-Adressen nur mit Mess-ID; Konfiguration website.toml.
E6 Datenschutzerklärung verweist auf die Cookie-Einstellungen; Footer nicht (Entwurf).
E7 Browser (Chromium über Playwright, nur wenn vorhanden – auf GitHub übersprungen): vor der Zustimmung keine Anfrage
   an Google, nach Zustimmung gtag.js, Widerruf löscht die Analyse-Cookies, ohne Skript kein Hinweis.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest
from test_website_021 import dienst  # noqa: F401 - Fixture (Spielplan mit Spieltag 10/11)

from website import einstellungen as W
from website import sitemap as SM
from website import vorschau
from website.texte import t

ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "app" / "website" / "statisch" / "site.js").read_text(encoding="utf-8")
SEITEN = ["/de/", "/en/", "/de/spieltag/bundesliga/", "/de/methodik/", "/en/glossary/", "/de/impressum/",
          "/de/datenschutz/", "/de/kontakt/", "/de/gibt-es-nicht/"]
GOOGLE = re.compile(r"<script[^>]*google|googletagmanager\.com|google-analytics\.com|analytics\.google\.com|gtag\(", re.I)


def _html(d, pfad, cookies=None) -> str:
    return vorschau.beantworten("/vorschau" + pfad, "", d, cookies=cookies).inhalt.decode()


def _hinweis(html: str) -> str:
    m = re.search(r'<div class="cookie-hinweis"[^>]*>.*?</div>\s*</div>', html, re.S)
    return m.group(0) if m else ""


# --- E1 Cookie-Hinweis -----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("pfad", SEITEN)
def test_e1_hinweis_in_jeder_seite_verborgen(dienst, pfad):
    html = _html(dienst, pfad)
    box = _hinweis(html)
    lang = pfad[1:3]
    assert box, "Cookie-Hinweis fehlt"
    assert 'role="region"' in box and f'aria-label="{t("cookie.region", lang)}"' in box and " hidden>" in box
    assert t("cookie.hinweis", lang) in box and "<a " not in box                      # kein Link im Hinweis
    knoepfe = re.findall(r'<button type="button" class="([^"]+)" data-cookie-wahl="(\w+)">([^<]+)</button>', box)
    assert [(w, txt) for _, w, txt in knoepfe] == [("abgelehnt", t("cookie.ablehnen", lang)),
                                                  ("zugestimmt", t("cookie.zustimmen", lang))]   # Tab-Reihenfolge
    assert all("knopf-wahl" in k for k, _, _ in knoepfe)                              # gleich gross und gewichtet


def test_e1_texte_nach_entwurf_und_nicht_auf_der_einstellungsseite(dienst):
    assert t("cookie.hinweis", "de") == ("Wir verwenden Webanalyse, um Soccer Intelligence zu verbessern. Die Nutzung "
                                         "erfolgt nur mit deiner Zustimmung.")
    assert t("cookie.hinweis", "en") == ("We use web analytics to improve Soccer Intelligence. Analytics are only "
                                         "enabled with your consent.")
    assert (t("cookie.ablehnen", "en"), t("cookie.zustimmen", "en"), t("cookie.region", "en")) == \
        ("Decline", "Accept", "Cookie notice")
    assert not _hinweis(_html(dienst, "/de/cookie-einstellungen/"))
    css = (ROOT / "app" / "website" / "statisch" / "site.css").read_text(encoding="utf-8")
    assert re.search(r"\.cookie-hinweis \{ position: fixed;[^}]*max-width: 560px", css)
    assert re.search(r"\.knopf-wahl \{[^}]*min-height: 48px", css)                       # Tippfläche 48 px


# --- E2 Vor der Zustimmung nichts von Google -------------------------------------------------------------------------

@pytest.mark.parametrize("pfad", SEITEN + ["/de/cookie-einstellungen/"])
def test_e2_kein_google_im_html(dienst, monkeypatch, pfad):
    html = _html(dienst, pfad)                                                         # Vorschau: keine Mess-ID
    assert not GOOGLE.search(html) and "data-ga=" not in html
    monkeypatch.setattr(W, "GA4_ID", "G-9XH0LGQLQ7")                                   # öffentliche Website
    vorschau.SEITEN.leeren()
    html = _html(dienst, pfad, cookies="cookie_wahl=zugestimmt")
    assert 'data-ga="G-9XH0LGQLQ7"' in html and not GOOGLE.search(html)               # geladen wird nur im Browser
    vorschau.SEITEN.leeren()


def test_e2_messung_nur_oeffentlich_und_nur_nach_zustimmung():
    assert W._ga4_mess_id() == "G-9XH0LGQLQ7"
    assert W.VORSCHAU and W.GA4_ID == ""                                               # Tests laufen als Vorschau
    # Die Google-Adresse steht nur in messen(); messen() wird nur nach Zustimmung aufgerufen
    messen = re.search(r"function messen\(\) \{(.*?)\n  \}", JS, re.S).group(1)
    assert JS.count("googletagmanager.com") == 1 and "googletagmanager.com/gtag/js" in messen
    assert "if (!ga) { return; }" in messen
    aufrufe = [m.start() for m in re.finditer(r"messen\(\);", JS)]
    assert len(aufrufe) == 2
    assert "if (w === 'zugestimmt') { messen(); }" in JS and "if (wahl() === 'zugestimmt') { messen(); }" in JS
    assert "Max-Age=' + (180 * 86400)" in JS and "SameSite=Lax" in JS                  # 6 Monate
    assert "_ga_" in JS and "ga-disable-" in JS                                        # Widerruf beendet und löscht


# --- E3 Seite Cookie-Einstellungen -----------------------------------------------------------------------------------

@pytest.mark.parametrize("cookies, wahl", [(None, "offen"), ("cookie_wahl=zugestimmt", "zugestimmt"),
                                           ("_ga=1; cookie_wahl=abgelehnt", "abgelehnt"), ("cookie_wahl=quatsch", "offen")])
def test_e3_seite_zeigt_die_wahl(dienst, cookies, wahl):
    a = vorschau.beantworten("/vorschau/en/cookie-settings/", "", dienst, cookies=cookies)
    html = a.inhalt.decode()
    assert a.status == 200 and a.kopf["Cache-Control"] == "no-store"
    assert f'data-cookie-status\n           data-offen="{t("cookie.status_offen", "en")}"' in html
    assert re.search(rf'data-abgelehnt="[^"]+">{re.escape(t("cookie.status_" + wahl, "en"))}</p>', html)
    for w in ("abgelehnt", "zugestimmt"):
        gedrueckt = "true" if w == wahl else "false"
        assert re.search(rf'data-cookie-wahl="{w}"\s+aria-pressed="{gedrueckt}"', html)
    assert "<title>Cookie settings | Soccer Intelligence</title>" in html
    assert 'href="/vorschau/en/privacy-policy/#google-analytics"' in html


def test_e3_noindex_und_nicht_in_der_sitemap(dienst, monkeypatch):
    monkeypatch.setattr(W, "VORSCHAU", False)
    from website import seiten
    html = seiten.cookie_html(seiten.Kontext(vorschau=False, lang="de"))
    assert '<meta name="robots" content="noindex,follow">' in html
    assert '<link rel="canonical" href="https://soccer-intelligence.com/de/cookie-einstellungen/">' in html
    assert "cookie" not in SM.sitemap("/sitemaps/seiten.xml", dienst)


# --- E4 Ohne Skript: Formular ----------------------------------------------------------------------------------------

def test_e4_formular_speichert_und_loescht(dienst):
    a = vorschau.beantworten_post("/vorschau/de/cookie-einstellungen/", b"wahl=zugestimmt", "1.1.1.1", dienst)
    assert a.status == 303 and a.kopf["Location"] == "/vorschau/de/cookie-einstellungen/"
    assert a.cookies == ["cookie_wahl=zugestimmt; Max-Age=15552000; Path=/vorschau/; SameSite=Lax; Secure"]
    a = vorschau.beantworten_post("/vorschau/de/cookie-einstellungen/", b"wahl=abgelehnt", "1.1.1.1", dienst,
                                  cookies="_ga=GA1.1.1; _ga_9XH0LGQLQ7=GS1; andere=1; cookie_wahl=zugestimmt")
    assert a.cookies == ["cookie_wahl=abgelehnt; Max-Age=15552000; Path=/vorschau/; SameSite=Lax; Secure",
                         "_ga=; Max-Age=0; Path=/; Domain=soccer-intelligence.com",
                         "_ga_9XH0LGQLQ7=; Max-Age=0; Path=/; Domain=soccer-intelligence.com"]
    assert vorschau.beantworten_post("/vorschau/de/cookie-einstellungen/", b"wahl=ja", "1.1.1.1", dienst).status == 400
    assert vorschau.beantworten_post("/vorschau/de/methodik/", b"wahl=ja", "1.1.1.1", dienst).status == 405
    assert vorschau.cookie_wahl('cookie_wahl="zugestimmt"; x') in ("zugestimmt", "")   # kaputte Kopfzeile bricht nie
    assert vorschau.cookie_wahl("a=1; cookie_wahl=abgelehnt") == "abgelehnt" and vorschau.cookie_wahl(None) == ""


# --- E5 Sicherheitsrichtlinie und Konfiguration ----------------------------------------------------------------------

def test_e5_csp_nur_mit_mess_id():
    ohne, mit = vorschau._csp(""), vorschau._csp("G-9XH0LGQLQ7")
    assert "google" not in ohne and "script-src 'self';" in ohne and "connect-src 'self';" in ohne
    assert "script-src 'self' https://*.googletagmanager.com;" in mit
    assert "connect-src 'self' https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com;" in mit
    assert "img-src 'self' data: https://*.google-analytics.com https://*.googletagmanager.com;" in mit
    assert "'unsafe-inline'" not in mit and "'unsafe-eval'" not in mit
    assert vorschau.SICHERHEIT["Content-Security-Policy"] == ohne                     # Vorschau: streng


# --- E6 Datenschutzerklärung und Footer ------------------------------------------------------------------------------

@pytest.mark.parametrize("pfad, lang", [("/de/datenschutz/", "de"), ("/en/privacy-policy/", "en")])
def test_e6_link_in_der_datenschutzerklaerung_nicht_im_footer(dienst, pfad, lang):
    html = _html(dienst, pfad)
    ziel = "/vorschau/de/cookie-einstellungen/" if lang == "de" else "/vorschau/en/cookie-settings/"
    assert f'href="{ziel}"' in html
    fuss = html.split('<footer class="fuss">', 1)[1].split("</footer>", 1)[0]
    assert "cookie" not in fuss.lower()
    assert "14 Monaten" in html if lang == "de" else "14 months" in html               # Aufbewahrung wie in GA4
    assert "verhindern" not in html if lang == "en" else True                          # Fehler gefunden in 0.28


# --- E7 Browser (Playwright) -----------------------------------------------------------------------------------------

def _playwright() -> bool:
    if not shutil.which("node"):
        return False
    return subprocess.run(["node", "-e", "require('playwright')"], capture_output=True).returncode == 0


@pytest.mark.skipif(not _playwright(), reason="Node mit Playwright fehlt (z. B. auf GitHub)")
def test_e7_browser_nichts_vor_der_zustimmung(dienst, monkeypatch):
    monkeypatch.setattr(W, "GA4_ID", "G-TEST12345")
    monkeypatch.setitem(vorschau.SICHERHEIT, "Content-Security-Policy", vorschau._csp("G-TEST12345"))   # wie öffentlich
    original = vorschau.beantworten
    monkeypatch.setattr(vorschau, "beantworten", lambda p, q, daten=None, cookies=None: original(p, q, dienst, cookies))
    vorschau.SEITEN.leeren()
    server = ThreadingHTTPServer(("127.0.0.1", 0), vorschau.Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        aus = subprocess.run(["node", str(ROOT / "tests" / "browser" / "einwilligung.js"),
                              f"http://localhost:{server.server_address[1]}/vorschau"],
                             capture_output=True, text=True, timeout=120)
    finally:
        server.shutdown()
        vorschau.SEITEN.leeren()
    assert aus.returncode == 0, aus.stderr
    r = json.loads(aus.stdout)
    assert r["vorher_google"] == 0 and r["vorher_hinweis"] and r["vorher_cookies"] == []
    assert r["tab_reihenfolge"] == ["Ablehnen", "Zustimmen"]
    assert any("googletagmanager.com/gtag/js?id=G-TEST12345" in u for u in r["nach_zustimmung_google"])
    assert not r["nach_zustimmung_hinweis"] and r["nach_zustimmung_wahl"] == "zugestimmt"
    assert not r["neu_geladen_hinweis"] and r["neu_geladen_google"] >= 2
    assert r["einstellungen_status_vorher"] == t("cookie.status_zugestimmt") and r["einstellungen_hinweis"] == 0
    assert r["widerruf_status"] == t("cookie.status_abgelehnt") and r["widerruf_gedrueckt"] == "true"
    assert r["widerruf_cookies"].get("cookie_wahl") == "abgelehnt"
    assert "_ga" not in r["widerruf_cookies"] and "_ga_TEST12345" not in r["widerruf_cookies"]
    assert r["nach_widerruf_google_neu"] == 0 and not r["nach_widerruf_hinweis"]
    assert not r["ohne_js_hinweis"] and r["ohne_js_google"] == 0
    assert r["ohne_js_status"] == t("cookie.status_zugestimmt") and r["ohne_js_wahl"] == "zugestimmt"
