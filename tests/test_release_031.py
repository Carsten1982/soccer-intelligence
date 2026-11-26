"""Release 0.31 (Paket Release_20 des Design-Chats, Entscheide Carsten 26.11.2026; docs/08_Website.md, Abschnitt 12).

A1 Showcase Englisch freigeschaltet: vier EN-Seiten (/en/showcase, …/project, …/ai-automation, …/ai-automation/data),
   noindex, eigene Linkvorschau (og:locale, Beschreibung, Bild je Sprache), hreflang zwischen DE und EN.
A2 Sprachauswahl auf allen vier Seiten: Globus «Deutsch / English» zwischen «KI & Automatisierung» und «Kontakt»,
   Wechsel auf dieselbe Seite, Screenreader-Beschriftung je Sprache, ohne Skript bedienbar (<details>).
B  Kompakter Hero (Design 581): Masse aus dem Entwurf in den Stildateien; Fuss der Startseite mit 40 px Abstand.
C  Englische Texte nach Release_16 (Spalte Englisch) mit den Entscheiden aus Release_18.
D  Archiv-Spieltag (Release_17): Sind alle Partien gespielt, entfallen Legende, „Wie lese ich das?“ und die Zahl
   der Auffälligkeiten; sonst bleibt die Seite wie bisher. Aktuelle Spieltag-Seite unverändert.
E  „Wie lese ich das?“ nach dem Spiel (Release_19 mit den Korrekturen a–c, Entscheid Carsten 26.11.2026).
"""

from __future__ import annotations

import re
from html import escape
from pathlib import Path

import pytest
from test_auswertung_025 import _kennzahl
from test_auswertung_025 import _seite as _spielseite
from test_website_021 import dienst  # noqa: F401 - Fixture

from core import auswertung as AW
from website import einstellungen as W
from website import seiten
from website import showcase as SC
from website import sitemap as SM
from website import vorschau
from website.texte import t

APP = Path(__file__).resolve().parents[1] / "app"
EN = {"start": "/en/showcase", "projekt": "/en/showcase/project", "ki": "/en/showcase/ai-automation",
      "daten": "/en/showcase/ai-automation/data"}
DE = {"start": "/showcase", "projekt": "/showcase/project", "ki": "/showcase/ki-automation",
      "daten": "/showcase/ki-automation/data"}


def _seite(d, pfad, query=""):
    vorschau.SEITEN.leeren()
    return vorschau.beantworten("/vorschau" + pfad, query, d)


# --- A1 Englisch freigeschaltet --------------------------------------------------------------------------------------

@pytest.mark.parametrize("seite", list(EN))
def test_a1_englische_seiten(dienst, seite):
    assert SC.SPRACHEN_FREI == ("de", "en") and SC.PFADE["en"] == EN and SC.PFADE["de"] == DE
    for p in (EN[seite], EN[seite] + "/"):
        a = _seite(dienst, p)
        html = a.inhalt.decode()
        assert a.status == 200 and a.kopf["X-Robots-Tag"] == "noindex, nofollow"
        assert '<html lang="en">' in html and '<meta name="robots" content="noindex, nofollow">' in html
        assert f"<title>{escape(t(f'showcase.{seite}.title', 'en'))}</title>" in html
        assert f'<meta property="og:description" content="{escape(t(f"showcase.{seite}.description", "en"))}">' in html
        assert '<meta property="og:locale" content="en_GB">' in html
        assert f'<link rel="alternate" hreflang="de" href="{W.DOMAIN}{DE[seite]}">' in html
        assert f'<link rel="alternate" hreflang="en" href="{W.DOMAIN}{EN[seite]}">' in html
        assert "style=" not in html and not re.search(r"\son[a-z]+=", html)
    de = _seite(dienst, DE[seite]).inhalt.decode()
    assert '<meta property="og:locale" content="de_CH">' in de or '<meta property="og:locale" content="de_DE">' in de


def test_a1_englische_navigation(dienst):
    html = _seite(dienst, EN["daten"]).inhalt.decode()
    nav = html.split('<nav class="sc-nav"', 1)[1].split("</nav>", 1)[0]
    reiter = re.findall(r'<a class="sc-reiter" href="([^"]+)"', nav)
    assert reiter == ["/vorschau/en/showcase", "/vorschau/en/showcase/project", "/vorschau/en/",
                      "/vorschau/en/showcase/ai-automation"]
    assert re.findall(r'aria-current="page">([^<]+)</a>', nav) == ["AI &amp; Automation"]
    assert 'href="/vorschau/en/contact/"' in nav and 'href="/vorschau/en/showcase/ai-automation"' in html


def test_a1_nie_im_index_und_nicht_von_der_plattform(dienst):
    xml = SM.sitemap_xml(dienst) if hasattr(SM, "sitemap_xml") else _seite(dienst, "/sitemap.xml").inhalt.decode()
    assert "showcase" not in xml
    for p in ("/de/", "/en/"):
        assert "showcase" not in _seite(dienst, p).inhalt.decode()


def test_a1_vorschau_bild_je_sprache(dienst, tmp_path, monkeypatch):
    monkeypatch.setattr(W, "BILDER", tmp_path)
    (tmp_path / SC.VORSCHAU_BILD["de"]).write_bytes(b"\xff\xd8")
    en = _seite(dienst, EN["start"]).inhalt.decode()
    assert "og:image" not in en                                    # englisches Bild fehlt: keine Vorschau, kein Ersatz
    (tmp_path / SC.VORSCHAU_BILD["en"]).write_bytes(b"\xff\xd8")
    en = _seite(dienst, EN["start"]).inhalt.decode()
    assert f'<meta property="og:image" content="{W.DOMAIN}/bilder/showcase-vorschau-en.jpg">' in en
    assert f'content="{escape(t("showcase.kopf.vorschau_alt", "en"))}"' in en
    assert _seite(dienst, "/bilder/showcase-vorschau-en.jpg").status == 200
    de = _seite(dienst, DE["start"]).inhalt.decode()
    assert f'<meta property="og:image" content="{W.DOMAIN}/bilder/showcase-vorschau.jpg">' in de


# --- A2 Sprachauswahl ------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("seite", list(EN))
@pytest.mark.parametrize("lang", ["de", "en"])
def test_a2_sprachauswahl(dienst, seite, lang):
    html = _seite(dienst, (DE if lang == "de" else EN)[seite]).inhalt.decode()
    nav = html.split('<nav class="sc-nav"', 1)[1].split("</nav>", 1)[0]
    # Position: nach «KI & Automatisierung», vor «Kontakt»
    assert nav.index('class="sc-reiter" href="/vorschau/' + ("showcase/ki" if lang == "de" else "en/showcase/ai")) \
        < nav.index('<details class="sc-sprache" data-sprachmenue>') < nav.index('class="sc-kontakt"')
    menue = nav.split('<details class="sc-sprache"', 1)[1].split("</details>", 1)[0]
    label = "Sprache wählen" if lang == "de" else "Choose language"
    name = "Deutsch" if lang == "de" else "English"
    assert f'aria-haspopup="true" aria-label="{label}: {name}"' in menue
    assert f'role="group" aria-label="{label}"' in menue
    links = re.findall(r'<a href="([^"]+)" lang="(\w+)" hreflang="\w+" aria-current="(\w+)">(\w+)</a>', menue)
    assert links == [("/vorschau" + DE[seite], "de", "true" if lang == "de" else "false", "Deutsch"),
                     ("/vorschau" + EN[seite], "en", "true" if lang == "en" else "false", "English")]
    # Skript nur für aria-expanded, Esc und Klick daneben (site.js), keine Messung auf dem Showcase
    assert re.search(r'<script src="/vorschau/statisch/site\.js\?v=\w+" defer></script>', html)
    assert "data-ga" not in html and "googletagmanager" not in html


def test_a2_skript_kennt_das_menue():
    js = (APP / "website" / "statisch" / "site.js").read_text(encoding="utf-8")
    assert "document.querySelectorAll('[data-sprachmenue]')" in js and "aria-expanded" in js and "Escape" in js


# --- B Kompakter Hero ------------------------------------------------------------------------------------------------

def _regel(css: str, sel: str) -> str:
    m = re.search(re.escape(sel) + r"\s*\{([^}]*)\}", css)
    assert m, sel
    return m.group(1).replace(" ", "")


def test_b_kompakter_hero():
    e = (APP / "website" / "statisch" / "showcase-entwurf.css").read_text(encoding="utf-8")
    s = (APP / "website" / "statisch" / "showcase.css").read_text(encoding="utf-8")
    assert "border-radius:32px;padding:40px64px0" in _regel(e, ".sx-1")                  # Hero-Rahmen
    assert "font-size:72px" in _regel(e, ".sx-8") and "font-size:32px" in _regel(e, ".sx-9")   # Titel, Untertitel
    assert "font-size:18px" in _regel(e, ".sx-10") and "font-size:56px" in _regel(e, ".sx-102")  # Einleitung, KI-Titel
    assert "height:430px" in _regel(s, ".sg-vis") and "height:100%" in _regel(s, ".sg-photo")
    assert "width:58%" in _regel(s, ".sg-lap") and "padding:22px30px" in _regel(s, ".sg-card")
    assert "width:56px;height:56px" in _regel(e, ".sx-k34") and "width:44px;height:44px" in _regel(e, ".sx-k40")
    assert "margin-top:40px" in _regel(s, ".sc-fuss-eng")


def test_b_kacheln_und_fuss(dienst):
    start = _seite(dienst, DE["start"]).inhalt.decode()
    assert start.count('class="sx-k34"') == 3 and '<footer class="sc-fuss sc-fuss-eng">' in start
    ki = _seite(dienst, DE["ki"]).inhalt.decode()
    assert 'class="sx-k34"' not in ki and '<footer class="sc-fuss">' in ki                  # KI-Seite: Kacheln wie bisher


# --- C Englische Texte (Release_16, Spalte Englisch; Release_18) ----------------------------------------------------

@pytest.mark.parametrize("schluessel, text", [
    ("start.sub", "An AI project – from data analysis to a working platform."),
    ("start.c2", "Experience Soccer Intelligence live. Visit the website and see for yourself."),
    ("start.c3", "AI-powered monitoring, quality checks and automated processes at work."),
    ("start.lapLabel", "Example view of the platform on a tablet: Bundesliga, matchday 24, VfB Stuttgart v Bayern Munich, corners +38.81%, signal quality: High"),
    ("projekt.p_big", "Analyse matches. Identify standout statistics. Assess possible match developments."),
    ("projekt.k_sub", "A complete platform, built with Claude Code."),
    ("projekt.r_sub", "From an idea to a working product."),
    ("projekt.ana_s", "(Standout statistics & interpretation)"),
    ("ki.gB_s", "Analyse changes and turn them into recommendations."),
    ("daten.m_o3", "Server utilisation"),
    ("daten.status_gruen", "System status: all systems operational"),
    ("daten.status_warnung", "System status: Warning"),
    ("daten.status_kritisch", "System status: Critical issue"),
    ("daten.ergebnis_ok", "Imported"),
    ("daten.anlass_kontrolle", "Control run"),
    ("daten.release_folgt", "Included in the next release"),
    ("daten.ausgeschoepft", "Quota exhausted"),
    ("daten.alle_laufen", "All services running"),
    ("projekt.description", "The project behind Soccer Intelligence: its product, data, AI-assisted development, technology and key figures."),
    ("ki.description", "Automated monitoring processes and AI agents behind Soccer Intelligence – turning monitoring data into actionable insights."),
    ("kopf.sprache_label", "Choose language"),
])
def test_c_englische_texte(schluessel, text):
    assert t(f"showcase.{schluessel}", "en") == text


def test_c_zeitangaben_englisch():
    from datetime import datetime
    jetzt = datetime(2026, 11, 26, 14, 0)
    assert SC._wann(datetime(2026, 11, 26, 22, 15), jetzt, "en") == "today at 22:15"
    assert SC._wann(datetime(2026, 11, 27, 4, 0), jetzt, "en") == "tomorrow at 04:00"
    assert SC._wann(datetime(2026, 11, 28, 18, 15), jetzt, "en") == "Sat 28 Nov 2026 at 18:15"
    assert SC._wann(datetime(2026, 11, 28, 18, 15), jetzt, "de") == "Sa 28.11.2026 18:15"
    assert t("showcase.daten.woche_teil", "en", n=6, ok=5) == "This week: 6 runs, 5 imported"


def test_c_keine_alten_begriffe():
    import json
    def werte(x):
        return [w for v in x.values() for w in werte(v)] if isinstance(x, dict) else [x]
    en = " | ".join(werte(json.loads((APP / "website" / "texte" / "en.json").read_text(encoding="utf-8"))["showcase"]))
    for alt in ("Applied", "applied", "Daily check", "All systems normal", "Disruption", "Used up", "finished platform",
                "Excerpt from the platform", "History of notes"):
        assert alt not in en, alt


# --- D Archiv-Spieltag (Release_17) ----------------------------------------------------------------------------------

def test_d_archiv_abgeschlossen_ohne_legende(dienst):
    a = _seite(dienst, "/de/spieltag/bundesliga/2026-27/10/", "datum=2026-11-24")
    html = a.inhalt.decode()
    assert a.status == 200
    zusammenfassung = html.split('<p class="zusammenfassung">', 1)[1].split("</p>", 1)[0]
    assert zusammenfassung == "10. Spieltag · 20.11.2026 · 3 Spiele"                 # ohne „· n auffällig“
    assert 'class="legende"' not in html and t("spieltag.wie_lesen") not in html
    assert t("spieltag.keine_abweichungen") not in html
    en = _seite(dienst, "/en/matchday/bundesliga/2026-27/10/", "datum=2026-11-24").inhalt.decode()
    assert 'class="legende"' not in en and t("spieltag.wie_lesen", "en") not in en


def test_d_archiv_mit_offener_partie_unveraendert(dienst):
    a = _seite(dienst, "/de/spieltag/bundesliga/2026-27/10/", "datum=2026-11-21")
    html = a.inhalt.decode()
    assert a.status == 200
    zusammenfassung = html.split('<p class="zusammenfassung">', 1)[1].split("</p>", 1)[0]
    assert zusammenfassung == "10. Spieltag · 20.11.2026 · 3 Spiele · 1 auffälliges Spiel"
    assert 'class="legende"' in html and t("spieltag.wie_lesen") in html


def test_d_aktuelle_spieltag_seite_unveraendert(dienst):
    html = _seite(dienst, "/de/spieltag/bundesliga/", "datum=2026-11-24").inhalt.decode()
    assert 'class="legende"' in html and t("spieltag.wie_lesen") in html


# --- E „Wie lese ich das?“ nach dem Spiel (Release_19) ---------------------------------------------------------------

DE_E = [("Ligadurchschnitt / Vergleichswert:", "Der Wert, an dem wir uns orientieren. Meist der Ligadurchschnitt, bei „Über 2,5 Tore“ der feste Wert von 2,5."),
        ("Erwartungswert:", "Der Wert, den wir aus den letzten 10 Ligaspielen jeder Mannschaft berechnet haben."),
        ("Tatsächlich:", "Der im Spiel erreichte Wert."),
        ("Signalqualität:", "Zeigt, wie häufig sich vergleichbare Auffälligkeiten in der Vergangenheit bestätigt haben (stark, mittel oder gering)."),
        ("Bestätigt:", "Wir prüfen, ob der tatsächliche Wert in die erwartete Richtung vom Ligadurchschnitt aus geht. Beispiel: Bei 12 erwarteten Ecken und einem Ligadurchschnitt von 10,9 ist die Tendenz auch bei 11 Ecken bestätigt. Der Erwartungswert muss also nicht exakt erreicht werden.")]
EN_E = [("League average / reference value:", "The value we use as a benchmark. Usually the league average; for “Over 2.5 goals”, the fixed value of 2.5."),
        ("Expected value:", "The value we calculate based on each team’s last 10 league matches."),
        ("Actual:", "The value recorded in the match."),
        ("Signal quality:", "Shows how often similar standout statistics were confirmed in past matches (high, medium or low)."),
        ("Confirmed:", "We check whether the actual value follows the expected direction from the league average. Example: If 12 corners are expected and the league average is 10.9, the trend is also confirmed if the match has 11 corners. The actual value does not have to match the expected value exactly.")]
SCHLUSS = {"de": "Bei „Über 2,5 Tore“ und „Beide Teams treffen“ gelten die jeweiligen Torgrenzen bzw. Ja-/Nein-Ergebnisse.",
           "en": "For “Over 2.5 goals” and “Both teams to score”, we use the relevant goal threshold or Yes/No result."}


@pytest.mark.parametrize("lang, eintraege", [("de", DE_E), ("en", EN_E)])
def test_e_wie_lese_ich_das_nach_dem_spiel(lang, eintraege):
    a = _kennzahl("kpi02", 30.0, "stark", pos=20)
    a.update(ist=4, ergebnis=AW.BESTAETIGT)
    html = seiten.spiel_html(_spielseite(auffaellig=[a], uebrige=[], groesste=a), seiten.Kontext(lang=lang))
    box = html.split('<div class="eng abschnitt-detail auswertung">', 1)[1].split("</details>", 1)[0]
    punkte = re.findall(r"<li>(.*?)</li>", box, flags=re.S)
    erwartet = [f"<b>{escape(k, quote=False)}</b> {escape(v, quote=False)}" for k, v in eintraege]
    assert [p.strip() for p in punkte] == erwartet + [escape(SCHLUSS[lang], quote=False)]
    assert 'class="hinweisbox"' in box and "<summary" in box                              # Auf-/Zuklappen wie bisher
