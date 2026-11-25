"""Website 0.21 (docs/08_Website.md, Abschnitt 8, Testfälle W17–W28): Adressen und Sprachen, Indexierung, Sitemap und
robots.txt, Kopfbereich (canonical, hreflang, JSON-LD), Englisch (Schlüssel, Formate, Anzeigenamen), Caching und
503, Inhaltsseiten (Methodik mit Excel-Download, Glossar, Impressum, Kontakt), keine privaten Daten im Code.

Ohne Netz, ohne Streamlit; Hilfen aus test_website.py und test_anzeige.py.
"""

from __future__ import annotations

import io
import json
import re
import tomllib
from datetime import date, datetime
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest
from test_anzeige import game, plan, rnd
from test_website import BL, HIGH, MEDIUM, FakeDaten, kpi, match, zp

from website import adressen as AD
from website import einstellungen as W
from website import format as F
from website import methodik as MT
from website import namen, seiten, seo, spiel, spieltag, vorschau
from website import sitemap as SM
from website.texte import t

S = "2026/2027"
APP = Path(__file__).resolve().parents[1] / "app"


@pytest.fixture
def dienst():
    fx = plan(rnd(10, date(2026, 11, 20), date(2026, 11, 22)), game(10, date(2026, 11, 21), "18:30", "E", "F"),
              rnd(11, date(2026, 11, 27)))
    fx["api_id"] = range(1, len(fx) + 1)
    fx.loc[fx["heim"] == "E", "api_id"] = 1388512
    return FakeDaten({"Bundesliga": fx}, {"E": match(kpi03=kpi(HIGH, 44))})


# --- W17 Adressen -------------------------------------------------------------------------------------------------

def test_w17_slugs_and_paths():
    assert AD.slug("1. FC Köln") == "1-fc-koeln" and AD.slug("Brighton & Hove Albion") == "brighton-hove-albion"
    assert AD.slug("Atlético Madrid") == "atletico-madrid" and AD.slug("Nott'm Forest") == "nottm-forest"
    assert AD.spiel_slug("VfB Stuttgart", "Bayern München", 1550203) == "vfb-stuttgart-bayern-muenchen-1550203"
    assert AD.saison_slug("2025/2026") == "2025-26" and AD.saison_aus_slug("2025-26") == "2025/2026"
    assert AD.saison_aus_slug("2025-27") is None and AD.saison_aus_slug("25-26") is None
    pfade = {(art, lang): AD.pfad(AD.Ziel(art, lang)) for art in ("start", "methodik", "glossar", "kontakt",
                                                               "impressum", "datenschutz", "cookie") for lang in ("de", "en")}
    assert pfade[("start", "de")] == "/de/" and pfade[("methodik", "en")] == "/en/methodology/"
    assert pfade[("impressum", "en")] == "/en/legal-notice/" and pfade[("datenschutz", "en")] == "/en/privacy-policy/"
    assert pfade[("cookie", "de")] == "/de/cookie-einstellungen/" and pfade[("glossar", "en")] == "/en/glossary/"
    assert AD.pfad(AD.Ziel("spieltag", "en", liga="la-liga")) == "/en/matchday/la-liga/"
    assert AD.pfad(AD.Ziel("archiv", "de", liga="bundesliga", saison="2025/2026", nr=13)) == "/de/spieltag/bundesliga/2025-26/13/"
    assert AD.pfad(AD.Ziel("spiel", "en", liga="serie-a", slug="inter-milan-1")) == "/en/match/serie-a/inter-milan-1/"


@pytest.mark.parametrize("pfad, status, weiter, art, lang", [
    ("/", 301, "/de/", None, "de"),
    ("/de/", 200, None, "start", "de"),
    ("/de", 301, "/de/", "start", "de"),                                  # fehlender Schrägstrich
    ("/DE/Methodik/", 301, "/de/methodik/", "methodik", "de"),            # Grossbuchstaben
    ("/de/spieltag/", 302, "/de/spieltag/bundesliga/", None, "de"),
    ("/en/matchday/", 302, "/en/matchday/bundesliga/", None, "en"),
    ("/de/spieltag/serie-a/2025-26/7/", 200, None, "archiv", "de"),
    ("/de/spieltag/serie-a/2025-27/7/", 404, None, None, "de"),
    ("/de/spieltag/serie-a/2025-26/0/", 404, None, None, "de"),
    ("/de/spieltag/zweite-liga/", 404, None, None, "de"),
    ("/en/methodik/", 404, None, None, "en"),                             # deutsches Wort im englischen Verzeichnis
    ("/en/gibt-es-nicht/", 404, None, None, "en"),
    ("/fr/", 404, None, None, "de"),
    ("/spieltag/la-liga", 301, "/de/spieltag/la-liga/", None, "de"),     # alte Vorschau-Adressen
    ("/impressum", 301, "/de/impressum/", None, "de"),
    ("/de/spiel/bundesliga/a-b-17/", 200, None, "spiel", "de"),
])
def test_w17_recognise(pfad, status, weiter, art, lang):
    e = AD.erkennen(pfad)
    assert (e.status, e.weiter, e.ziel.art if e.ziel else None, e.lang) == (status, weiter, art, lang)


def test_w17_language_switch_and_links_keep_the_page(dienst):
    k = seiten.Kontext(lang="en", ziel=AD.Ziel("methodik", "en"))
    assert k.sprach_url("de") == "/vorschau/de/methodik/" and k.link("glossar") == "/vorschau/en/glossary/"
    k = seiten.Kontext(datum="2026-10-03", ziel=AD.Ziel("spieltag", liga="serie-a"))
    assert k.sprach_url("en") == "/vorschau/en/matchday/serie-a/?datum=2026-10-03"
    html = vorschau.beantworten("/vorschau/en/match/bundesliga/e-f-1388512/", "", dienst).inhalt.decode()
    assert 'href="/vorschau/de/spiel/bundesliga/e-f-1388512/" lang="de" hreflang="de" aria-current="false"' in html
    assert 'lang="en"' in html and "E vs F" in html and t("kopf.zurueck_spieltag", "en") in html


def test_w17_match_page_old_season_and_unknown_id(dienst, monkeypatch):
    fx = plan(game(5, date(2024, 10, 5), "15:30", "A", "B", saison="2024/2025"))
    fx["api_id"] = [77]
    d = FakeDaten({"Bundesliga": fx})
    assert vorschau.beantworten("/vorschau/de/spiel/bundesliga/a-b-77/", "", d).status == 404     # vor 2025/26
    assert vorschau.beantworten("/vorschau/de/spiel/bundesliga/a-b-78/", "", dienst).status == 404


# --- W18 Archiv -----------------------------------------------------------------------------------------------------

def test_w18_archive_page(dienst):
    d = dienst
    d._erg = {(S, "E", "F"): (2, 1)}
    a = vorschau.beantworten("/vorschau/de/spieltag/bundesliga/2026-27/10/", "datum=2026-11-24", d)
    html = a.inhalt.decode()
    assert a.status == 200 and t("archiv.kopf", liga="Bundesliga", n=10, saison="2026/27") in html
    assert '<b class="kg-tor" aria-hidden="true">2</b>' in html and 'href="/vorschau/de/spieltag/bundesliga/?datum=2026-11-24"' in html   # seit 0.26: neue Kachel auch im Archiv
    assert t("archiv.spieltag", n=11) in html                                       # Pfeil zum nächsten Spieltag
    assert vorschau.beantworten("/vorschau/de/spieltag/bundesliga/2026-27/12/", "", d).status == 404   # gibt es nicht
    assert vorschau.beantworten("/vorschau/de/spieltag/bundesliga/2026-27/11/", "datum=2026-11-24", d).status == 404
    a = vorschau.beantworten("/vorschau/de/spiel/bundesliga/e-f-1388512/", "datum=2026-11-24", d)
    assert b'href="/vorschau/de/spieltag/bundesliga/2026-27/10/?datum=2026-11-24"' in a.inhalt    # zurück ins Archiv


# --- W19 Indexierung, Sitemap, robots.txt ---------------------------------------------------------------------------

def _seite(**kw):
    s = {"saison": S, "anstoss_zeit": "2026-12-05T15:30", "zustand": "offen", "im_fenster": True,
         "bewertung": "auffaellig", "anzahl_gewertet": 8}
    s.update(kw)
    return s


def test_w19_index_rules():
    vorher = seo.Konfig(None)
    live = seo.Konfig(datetime(2026, 12, 1, 0, 0))
    assert not seo.spiel_indexierbar(_seite(), vorher)                             # vor dem Livegang nie
    assert seo.spiel_indexierbar(_seite(), live)
    assert not seo.spiel_indexierbar(_seite(anstoss_zeit="2026-11-28T15:30"), live)  # Anstoss vor dem Livegang
    assert not seo.spiel_indexierbar(_seite(im_fenster=False), live)                 # noch nicht im Spieltag-Tab
    assert seo.spiel_indexierbar(_seite(im_fenster=False, zustand="gespielt"), live)
    for bewertung in ("status", "werte_ab"):
        assert not seo.spiel_indexierbar(_seite(bewertung=bewertung), live)
    assert not seo.spiel_indexierbar(_seite(anzahl_gewertet=0, bewertung="zu_wenig_daten"), live)
    # seit 0.24 (Entscheid Carsten 24.11.2026): mindestens 6 der 8 Kennzahlen bewertet
    assert not seo.spiel_indexierbar(_seite(bewertung="zu_wenig_daten", anzahl_gewertet=5), live)
    assert seo.spiel_indexierbar(_seite(bewertung="zu_wenig_daten", anzahl_gewertet=6), live)
    assert not seo.spiel_indexierbar(_seite(anzahl_gewertet=7), seo.Konfig(datetime(2026, 12, 1), index_min_kennzahlen=8))
    assert not seo.spiel_indexierbar(_seite(saison="2024/2025"), live)
    assert seo.archiv_indexierbar(date(2026, 12, 4), live) and not seo.archiv_indexierbar(date(2026, 11, 27), live)
    assert not seo.archiv_indexierbar(date(2026, 12, 4), vorher)
    konfig = tomllib.loads((APP / "config" / "website.toml").read_text(encoding="utf-8"))
    assert konfig["index_ab"] == "2026-11-26T00:00" and konfig["seiten_ab_saison"] == "2025/2026"   # Livegang (0.27)
    # seit 0.27 (Entscheid Carsten 25.11.2026): Archiv der laufenden Saison indexierbar, auch vor dem Livegang
    assert seo.archiv_indexierbar(date(2026, 8, 22), live, "2026/2027", "2026/2027")
    assert not seo.archiv_indexierbar(date(2026, 2, 1), live, "2025/2026", "2026/2027")
    assert not seo.archiv_indexierbar(date(2026, 8, 22), vorher, "2026/2027", "2026/2027")
    assert konfig["index_min_kennzahlen"] == 6 and seo.konfig().index_min_kennzahlen == 6


def test_w19_robots_and_sitemap(dienst, monkeypatch):
    assert SM.robots() == "User-agent: *\nAllow: /\n\nSitemap: https://soccer-intelligence.com/sitemap.xml\n"
    a = vorschau.beantworten("/vorschau/robots.txt", "", dienst)
    assert a.status == 200 and a.kopf["Content-Type"].startswith("text/plain")
    index = vorschau.beantworten("/vorschau/sitemap.xml", "", dienst).inhalt.decode()
    assert "<sitemapindex" in index and "/sitemaps/seiten.xml" in index and "/sitemaps/bundesliga-2026-27.xml" in index
    seiten_xml = SM.sitemap("/sitemaps/seiten.xml", dienst)
    for pfad in ("/de/", "/en/", "/de/methodik/", "/en/methodology/", "/de/spieltag/serie-a/", "/en/legal-notice/"):
        assert f"<loc>https://soccer-intelligence.com{pfad}</loc>" in seiten_xml, pfad
    assert "cookie" not in seiten_xml
    assert seiten_xml.count('hreflang="x-default"') == seiten_xml.count("<loc>")
    assert 'hreflang="x-default" href="https://soccer-intelligence.com/de/methodik/"' in seiten_xml
    assert "<url>" not in SM.sitemap("/sitemaps/bundesliga-2026-27.xml", dienst)       # vor dem Livegang leer
    assert SM.sitemap("/sitemaps/bundesliga-2019-20.xml", dienst) is None
    assert vorschau.beantworten("/vorschau/sitemaps/gibt-es-nicht.xml", "", dienst).status == 404
    monkeypatch.setattr(seo, "konfig", lambda: seo.Konfig(datetime(2026, 11, 1)))
    teil = SM.sitemap("/sitemaps/bundesliga-2026-27.xml", dienst)
    assert "/de/spiel/bundesliga/e-f-1388512/" in teil and "/en/match/bundesliga/e-f-1388512/" in teil


# --- W20 Kopfbereich ------------------------------------------------------------------------------------------------

def test_w20_head_canonical_hreflang_jsonld(dienst):
    html = vorschau.beantworten("/vorschau/en/methodology/", "", dienst).inhalt.decode()
    assert '<link rel="canonical" href="https://soccer-intelligence.com/en/methodology/">' in html
    for hl, pfad in (("de", "/de/methodik/"), ("en", "/en/methodology/"), ("x-default", "/de/methodik/")):
        assert f'<link rel="alternate" hreflang="{hl}" href="https://soccer-intelligence.com{pfad}">' in html
    assert 'name="robots" content="noindex, nofollow"' in html                        # Vorschau immer noindex
    assert '<meta property="og:locale" content="en_GB">' in html and 'content="de_CH"' in html     # SEO-Briefing
    assert "<title>" + t("seo.methodik_titel", "en") + "</title>" in html
    daten = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
    typen = {x["@type"] for x in (daten if isinstance(daten, list) else daten.get("@graph", [daten]))}
    assert {"BreadcrumbList", "WebPage"} <= typen
    fehlt = vorschau.beantworten("/vorschau/de/gibt-es-nicht/", "", dienst).inhalt.decode()
    assert 'rel="canonical"' not in fehlt and "hreflang" not in fehlt.split("</head>")[0]


def test_w20_titles_and_descriptions():
    werte = dict(liga_key="bundesliga", spieltag=13, saison="2025/2026", datum="2026-04-19", sonderspiel=None,
                 status=None)
    lang_namen = "Borussia Mönchengladbach", "1. FC Heidenheim 1846"
    s = {**werte, "bewertung": "auffaellig", "auffaellig": [{"kpi": "kpi07", "stufe": "stark"},
                                                            {"kpi": "kpi06", "stufe": "mittel"}]}
    for lang in ("de", "en"):
        titel = seo.spiel_titel(s, *lang_namen, lang)
        assert titel.endswith("| Soccer Intelligence") and ("vs" in titel) is (lang == "en")
        for bew in ("auffaellig", "normal", "zu_wenig_daten", "werte_ab"):
            text = seo.spiel_beschreibung({**s, "bewertung": bew}, *lang_namen, lang)
            assert 0 < len(text) <= 155, (lang, bew, len(text))                      # Fehler bis 0.21: ungekürzt
            assert not re.search(r"Wettberatung|Tipp|Prognose|Quote|betting|tip|odds", text, re.I), text
        text = seo.spiel_beschreibung({**s, "bewertung": "status", "status": "verschoben"}, *lang_namen, lang)
        assert 0 < len(text) <= 155


# --- W21 Englisch -----------------------------------------------------------------------------------------------------

def _schluessel(d, vorne=""):
    out = {}
    for k, v in d.items():
        if k.startswith("_"):
            continue
        if isinstance(v, dict):
            out.update(_schluessel(v, f"{vorne}{k}."))
        else:
            out[f"{vorne}{k}"] = v
    return out


def test_w21_english_has_every_key_and_the_same_placeholders():
    de = _schluessel(json.loads((W.TEXTE / "de.json").read_text(encoding="utf-8")))
    en = _schluessel(json.loads((W.TEXTE / "en.json").read_text(encoding="utf-8")))
    assert set(de) == set(en), sorted(set(de) ^ set(en))
    for key in de:
        assert en[key].strip() or not de[key].strip(), key                       # leer nur, wo auch Deutsch leer ist
        assert set(re.findall(r"\{(\w+)\}", de[key])) == set(re.findall(r"\{(\w+)\}", en[key])), key
    assert "ß" not in "".join(v for k, v in en.items() if not k.startswith(("liga", "kennzahl")))


def test_w21_english_formats():
    assert F.tag(date(2026, 11, 21), "en") == "Sat 21 Nov" and F.prozent(47.36, "en") == "+47.36%"
    assert F.prozent(-22.07, "en") == "−22.07%" and F.zahl(3.4, "en") == "3.40"
    assert F.zeitraum(date(2026, 11, 20), date(2026, 11, 22), "en") == "20–22 Nov 2026"
    assert F.zeitraum(date(2026, 11, 30), date(2026, 12, 2), "en") == "30 Nov – 2 Dec 2026"
    assert F.wochenende(date(2027, 2, 6), "en") == "6/7 Feb" and F.ergebnis_kurz(2, 1) == "2:1"
    assert F.datum_voll(date(2026, 11, 22), "en") == "22 November 2026"


def test_w21_display_names_per_language():
    assert namen.anzeige("Serie A", "Inter", "de") == "Inter Mailand" and namen.anzeige("Serie A", "Inter", "en") == "Inter Milan"
    assert namen.anzeige("Bundesliga", "1899 Hoffenheim", "de") == "TSG Hoffenheim"
    assert namen.anzeige("Bundesliga", "Neu-Aufsteiger", "en") == "Neu-Aufsteiger"          # Rückfall: Datenquelle
    assert namen.fehlende([("Bundesliga", "Neu-Aufsteiger"), ("Serie A", "Inter")]) == [("Bundesliga", "Neu-Aufsteiger")]
    tabelle = namen.tabelle()
    assert len(tabelle) >= 78 and all(v["de"] and v["en"] for v in tabelle.values())
    assert AD.spiel_slug("1899 Hoffenheim", "Inter", 5) == "1899-hoffenheim-inter-5"        # Slug aus der Datenquelle


# --- W22 Caching, 503, Weiterleitungen ---------------------------------------------------------------------------------

def test_w22_cache_headers(dienst, monkeypatch):
    assert vorschau.beantworten("/vorschau/de/", "", dienst).kopf["Cache-Control"] == "no-store"   # Vorschau
    monkeypatch.setattr(W, "VORSCHAU", False)
    assert vorschau.beantworten("/vorschau/de/", "", dienst).kopf["Cache-Control"] == "public, max-age=300"
    assert vorschau.beantworten("/vorschau/de/methodik/", "", dienst).kopf["Cache-Control"] == "public, max-age=300"
    assert vorschau.beantworten("/vorschau/de/x/", "", dienst).kopf["Cache-Control"] == "no-store"   # 404
    a = vorschau.beantworten("/vorschau/statisch/site.css", "", dienst)
    assert a.kopf["Cache-Control"] == "public, max-age=2592000"
    for datei in ("favicon.ico", "favicon.svg", "apple-touch-icon.png", "og-image.png", "favicon-64.png"):
        a = vorschau.beantworten(f"/vorschau/{datei}", "", dienst)
        assert a.status == 200 and a.inhalt and "max-age=2592000" in a.kopf["Cache-Control"], datei
    a = vorschau.beantworten("/vorschau/", "", dienst)
    assert a.status == 301 and a.kopf["Cache-Control"] == "no-store"
    gesperrt = FakeDaten({"Bundesliga": plan(rnd(10, date(2026, 11, 20)))}, gesperrt=True)
    a = vorschau.beantworten("/vorschau/de/spieltag/bundesliga/", "", gesperrt)
    assert (a.status, a.kopf["Cache-Control"], a.kopf["Retry-After"]) == (503, "no-store", "600")


def test_w22_og_image_size():
    from PIL import Image
    with Image.open(W.STATISCH / "wurzel" / "og-image.png") as bild:
        assert bild.size == (1200, 630)
    with Image.open(W.STATISCH / "wurzel" / "apple-touch-icon.png") as bild:
        assert bild.size == (180, 180)


# --- W23 Tabs ohne JavaScript, Signalqualität -------------------------------------------------------------------------

def test_w23_tabs_work_without_javascript():
    fx = plan(rnd(12, date(2026, 12, 5), date(2026, 12, 6)), rnd(13, date(2026, 12, 8), date(2026, 12, 9)))
    s = spieltag.spieltag_daten(FakeDaten({"Bundesliga": fx}), BL, zp("2026-12-04T10:00"))
    assert len(s["tabs"]) == 2
    html = seiten.spieltag_html(s, seiten.Kontext())
    assert 'data-sprungliste' in html and '<a href="#tab-2">Zu Spieltag 13</a>' in html
    assert re.search(r'<div class="tabs" role="group"[^>]*hidden>', html)               # Tab-Leiste erst mit Skript
    assert html.count("data-tabtitel") == 2 and 'id="tab-1"' in html and 'id="tab-2"' in html
    assert not re.search(r'<section id="tab-2"[^>]*hidden', html)                         # alles sichtbar
    js = (W.STATISCH / "site.js").read_text(encoding="utf-8")
    assert "data-sprungliste" in js and "data-tabtitel" in js and "Escape" in js


def test_w23_quality_chip_and_tile_classes():
    fx = plan(game(10, date(2026, 11, 21), "15:30", "A", "B"), game(10, date(2026, 11, 21), "18:30", "C", "D"))
    fx["api_id"] = [1, 2]
    d = FakeDaten({"Bundesliga": fx}, {"A": match(kpi03=kpi(HIGH, 44)), "C": match(kpi05=kpi(MEDIUM, -30))})
    html = seiten.spieltag_html(spieltag.spieltag_daten(d, BL, zp("2026-11-16T10:00")), seiten.Kontext())
    assert 'class="kachel kachel--stark"' in html and 'class="kachel kachel--mittel"' in html
    assert html.count('class="q-balken q-stark"') >= 2                                    # Kachel und Legende
    assert '<span class="unsichtbar"> (Signalqualität)</span>' in html
    css = (W.STATISCH / "site.css").read_text(encoding="utf-8")
    for klasse in (".kachel--stark", ".kachel--mittel", ".kachel--gering", ".q-chip.q-stark", ".q-stark .an",
                   ".mc-card", "@container", ".sprung", ".sprachmenue", ".tabelle", ".begriffe"):
        assert klasse in css, klasse


# --- W24 Methodik und Excel-Download -------------------------------------------------------------------------------------

def test_w24_methodik_numbers_from_threshold_file():
    m = MT.daten("de")
    roh = tomllib.loads((APP / "config" / "schwellen.toml").read_text(encoding="utf-8"))["schwelle"]
    assert m["kombinationen"] == len(roh) and m["moeglich"] == 64 and m["saisons"] == 7
    assert (m["stark"], m["mittel"], m["gering"]) == tuple(sum(1 for r in roh if r["signalqualitaet"] == st)
                                                          for st in ("stark", "mittel", "gering"))
    assert [lg["key"] for lg in m["ligen"]] == ["bundesliga", "premier_league", "serie_a", "la_liga"]
    assert sum(lg["anzahl"] for lg in m["ligen"]) == len(roh)
    assert MT.saisons("2019/2020-2025/2026") == (7, "2019/20", "2025/26") and MT.saisons("x")[0] == 0
    assert MT.schwelle_text(Decimal("10"), "de") == "10 %" and MT.schwelle_text(Decimal("12.5"), "en") == "12.50%"


def test_w24_worked_example_matches_threshold_file():
    """Das Rechenbeispiel (fester Text, Bayern – Stuttgart) muss zur Schwellendatei passen: ändert sie sich zur neuen
    Saison, schlägt dieser Test an und der Text wird nachgeführt."""
    roh = tomllib.loads((APP / "config" / "schwellen.toml").read_text(encoding="utf-8"))["schwelle"]
    s = next(r for r in roh if (r["liga"], r["kpi"], r["richtung"]) == ("Bundesliga", "kpi09", "mehr"))
    de = (W.VORLAGEN / "inhalt" / "methodik.de.html").read_text(encoding="utf-8")
    en = (W.VORLAGEN / "inhalt" / "methodik.en.html").read_text(encoding="utf-8")
    zahl_de = lambda x: f"{x:.2f}".replace(".", ",")                              # noqa: E731
    for text in (f'"{s["spiele"]}"', f'"{round(s["spiele"] * s["trefferquote"] / 100)}"', f"{zahl_de(s['trefferquote'])} %",
                 f"{zahl_de(s['vergleichsgruppe'])} %", f"+{zahl_de(s['mehrwert'])} Prozentpunkte", f'"{s["schwelle"]} % → auffällig"'):
        assert text in de, text
    for text in (f"{s['trefferquote']:.2f}%", f"{s['vergleichsgruppe']:.2f}%", f"+{s['mehrwert']:.2f} percentage points",
                 f'"{s["schwelle"]}% → Statistical anomaly"'):
        assert text in en, text
    assert s["signalqualitaet"] == "stark" and s["saisons_positiv"] == "7/7"


@pytest.mark.parametrize("lang, pfad, kopf", [
    ("de", "/vorschau/de/methodik/soccer-intelligence-schwellen.xlsx", "Kennzahl"),
    ("en", "/vorschau/en/methodology/soccer-intelligence-thresholds.xlsx", "Metric"),
])
def test_w24_excel_download(dienst, lang, pfad, kopf):
    from openpyxl import load_workbook
    a = vorschau.beantworten(pfad, "", dienst)
    assert a.status == 200 and a.kopf["Content-Type"] == MT.XLSX and "attachment" in a.kopf["Content-Disposition"]
    wb = load_workbook(io.BytesIO(a.inhalt))
    blatt = wb.worksheets[0]
    zeilen = list(blatt.iter_rows(values_only=True))
    roh = tomllib.loads((APP / "config" / "schwellen.toml").read_text(encoding="utf-8"))["schwelle"]
    assert zeilen[0][1] == kopf and len(zeilen) == len(roh) + 1
    assert all(isinstance(z[3], (int, float)) and isinstance(z[6], (int, float)) for z in zeilen[1:])
    html = vorschau.beantworten(f"/vorschau/{lang}/{W.PFADE['methodik'][lang]}/", "", dienst).inhalt.decode()
    assert f'href="{pfad}" download=' in html
    for i in (1, 2, 3):
        assert f'id="ebene{i}"' in html and f'href="#ebene{i}"' in html
    assert html.count("<table") == 5 and html.count('<th scope="row">') == len(roh) + 4    # 4 Ligen + Übersicht


# --- W25 Inhaltsseiten -----------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("pfad", ["/de/methodik/", "/en/methodology/", "/de/glossar/", "/en/glossary/", "/de/kontakt/",
                                  "/en/contact/", "/de/impressum/", "/en/legal-notice/", "/de/datenschutz/",
                                  "/en/privacy-policy/", "/de/cookie-einstellungen/", "/en/cookie-settings/",
                                  "/de/gibt-es-nicht/"])
def test_w25_content_pages_render_cleanly(dienst, pfad):
    a = vorschau.beantworten("/vorschau" + pfad, "", dienst)
    html = a.inhalt.decode()
    assert a.status in (200, 404) and html.count("<h1") == 1 and f'<html lang="{pfad[1:3]}">' in html
    assert "style=" not in html and "<style" not in html and not re.search(r"\son[a-z]+=", html)
    ids = re.findall(r'\sid="([^"]+)"', html)
    assert len(ids) == len(set(ids)), "doppelte id"
    for anker in re.findall(r'href="#([^"]+)"', html):
        assert anker in ids, anker


def test_w25_operator_details_only_from_server_settings(dienst, monkeypatch):
    html = vorschau.beantworten("/vorschau/de/impressum/", "", dienst).inhalt.decode()
    assert t("inhalt.adresse_folgt") in html and t("inhalt.email_folgt") in html
    monkeypatch.setattr(W, "BETREIBER_NAME", "Erika Muster")
    monkeypatch.setattr(W, "BETREIBER_ADRESSE", ["Musterweg 1", "9999 Musterhausen", "Schweiz"])
    monkeypatch.setattr(W, "KONTAKT_EMAIL", "kontakt@example.com")
    html = vorschau.beantworten("/vorschau/en/legal-notice/", "", dienst).inhalt.decode()
    assert "Erika Muster<br>Musterweg 1<br>9999 Musterhausen<br>Schweiz" in html
    assert 'href="mailto:kontakt@example.com"' in html and t("inhalt.adresse_folgt", "en") not in html
    kontakt = vorschau.beantworten("/vorschau/de/kontakt/", "", dienst).inhalt.decode()
    assert re.search(r'<button type="submit" class="knopf-voll" disabled>', kontakt)        # Versand erst 0.22
    assert 'name="website"' in kontakt and 'tabindex="-1"' in kontakt                      # Honigtopf


def test_w25_no_personal_data_in_code_or_texts():
    """Betreiberangaben stehen nur in .env auf dem Server (Schutzregel). Im Code nur Platzhalter-Adressen."""
    erlaubt = {"name@beispiel.ch", "name@example.com", "noreply@anthropic.com",
               "info@soccer-intelligence.com"}                      # öffentliche Projektadresse (seit 0.23)
    for datei in [*W.VORLAGEN.rglob("*.html"), *W.TEXTE.glob("*.json"), *(APP / "website").glob("*.py"),
                  APP / "config" / "teamnamen_anzeige.csv", APP / "config" / "website.toml"]:
        text = datei.read_text(encoding="utf-8")
        for mail in re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text):
            assert mail.rstrip(".") in erlaubt, (datei.name, mail)
        assert not re.search(r"\b\d{4} [A-ZÄÖÜ][a-zäöü]+(see|dorf|berg|ingen)\b", text), datei.name   # PLZ Ort


# --- W26 Anzeige des Endstands ----------------------------------------------------------------------------------------------

def test_w26_compact_score_on_tiles_and_long_on_match_page():
    fx = plan(game(10, date(2026, 11, 20), "20:30", "A", "B"), game(10, date(2026, 11, 22), "15:30", "C", "D"))
    fx["api_id"] = [9, 10]
    d = FakeDaten({"Bundesliga": fx}, {}, {(S, "A", "B"): (2, 1)})
    z = zp("2026-11-21T10:00")
    # seit 0.25 (Release_08, 16.2): gespielte Kachel mit Toren je Team, „Endstand 2 : 1“ für Screenreader
    kachel = seiten.spieltag_html(spieltag.spieltag_daten(d, BL, z), seiten.Kontext())
    assert '<b class="kg-tor" aria-hidden="true">2</b>' in kachel and "Endstand 2 : 1" in kachel
    assert "Fr 20.11. · 20:30 · Gespielt" in kachel and "Keine Auffälligkeiten" in kachel
    html = seiten.spiel_html(spiel.spiel_daten(d, 9, z), seiten.Kontext(lang="en"))
    assert '<span class="a-tore">2 : 1</span>' in html and "Final score" in html      # Auswertung (Screenreader)


# --- W27 Entwurfsrunde 20.11.2026 (0.21.1) ------------------------------------------------------------------------------

def test_w27_drafts_of_20_november(dienst):
    """Spielseite ohne „Weitere Spiele“; Spieltag ohne SEO-Satz „Wir bieten …“;
    Methodik mit drei Einstiegskarten und Ebenen zum Ein- und Ausblenden; kräftigere Grüntöne; Sprachknopf mobil kurz."""
    spiel_html = vorschau.beantworten("/vorschau/de/spiel/bundesliga/e-f-1388512/", "", dienst).inhalt.decode()
    assert "weitere-liste" not in spiel_html and "Weitere Spiele" not in spiel_html   # Rollen seit 0.21.2: W28
    spieltag_html = vorschau.beantworten("/vorschau/de/spieltag/bundesliga/", "", dienst).inhalt.decode()
    assert "Wettberatung oder Gewinnprognosen" not in spieltag_html.split('id="seo-titel"')[1]
    m = vorschau.beantworten("/vorschau/de/methodik/", "", dienst).inhalt.decode()
    assert m.count('class="tiefe-karte"') == 3 and "Das Prinzip in einer Minute." in m and "Ebene 2" in m
    assert all(f'data-ebene="{n}"' in m for n in (1, 2, 3)) and 'class="download" aria-labelledby="download-titel" data-ebene="3"' in m
    assert 'class="knopf-voll knopf-weiter" href="#ebene2" data-tiefe-wahl="2" data-springen' in m
    js = (W.STATISCH / "site.js").read_text(encoding="utf-8")
    assert "data-tiefe-wahl" in js and "data-aufklappen" in js
    css = (W.STATISCH / "site.css").read_text(encoding="utf-8")
    for regel in (".q-chip.q-stark { background: #C8DECE; color: #2F4A3C; border-color: #8FB59D; }",
                  ".kachel--stark { min-height: 104px; background: #D6E8DB;", ".f-stark { background: #4F8268; }",
                  ".kopf-rechts { flex-wrap: nowrap;", "@media (max-width: 440px) {\n  .sprache-lang { display: none; }",
                  ".tabelle--breit { min-width: 0;"):
        assert regel in css, regel
    assert '<span class="sprache-kurz" aria-hidden="true">DE</span>' in m


# --- W28 Entwurfsrunde 20.11.2026, zweite Lieferung (0.21.2) --------------------------------------------------------------

def test_w28_second_round_of_drafts(dienst):
    """Spielseite: grüne Schaltfläche „Alle Spiele des Spieltags“, darunter Textlink zur Methodik, kein Zeitzonen-Hinweis.
    Spieltag: Hero ohne „Aktueller Datenstand“, niedriger. Startseite: SEO-Box eigener Block; Kennzahl bricht um, Chip
    bleibt daneben. Methodik: Weiter-Schaltfläche mit festem Umbruch nur mobil, Desktop einzeilig."""
    spiel_html = vorschau.beantworten("/vorschau/de/spiel/bundesliga/e-f-1388512/", "", dienst).inhalt.decode()
    knopf = re.search(r'<div class="eng abschluss"><a href="([^"]+)">([^<]+)<svg', spiel_html)
    assert knopf.group(1) == "/vorschau/de/spieltag/bundesliga/" and knopf.group(2) == t("spiel.alle_spiele")
    link = re.search(r'<div class="eng methodik-link"><a href="([^"]+)">([^<]+)</a></div>', spiel_html)
    assert link.group(1) == "/vorschau/de/methodik/" and link.group(2) == t("spiel.methodik")
    assert spiel_html.index('class="eng abschluss"') < spiel_html.index('class="eng methodik-link"')
    assert "zeitzone-hinweis" not in spiel_html and t("allgemein.zeitzone") not in spiel_html

    for lang in ("de", "en"):
        spieltag_html = vorschau.beantworten(f"/vorschau/{lang}/{'spieltag' if lang == 'de' else 'matchday'}/bundesliga/",
                                             "", dienst)
        text = spieltag_html.inhalt.decode()
        hero = text.split('class="hero hero-spieltag"')[1].split("</nav>")[1].split('<div class="eng')[0]
        assert 'class="datenstand"' not in hero and "Datenstand" not in hero and "data as of" not in hero
        assert t("allgemein.zeitzone", lang=lang) in text                        # bleibt auf der Spieltag-Seite

    start = vorschau.beantworten("/vorschau/de/", "", dienst).inhalt.decode()
    fan, rest = start.split('<div class="wrap abschnitt-fan">')[1].split('<div class="wrap abschnitt-seo">')
    assert 'class="seo"' not in fan and rest.lstrip().startswith('<section class="seo" aria-labelledby="seo-titel">')

    m_de = vorschau.beantworten("/vorschau/de/methodik/", "", dienst).inhalt.decode()
    m_en = vorschau.beantworten("/vorschau/en/methodology/", "", dienst).inhalt.decode()
    assert '<span>Weiter mit Zahlen:<span class="umbruch-mobil"> </span>Ein Spiel durchgerechnet</span>' in m_de
    assert '<span>Continue with numbers:<span class="umbruch-mobil"> </span>a worked example</span>' in m_en

    css = (W.STATISCH / "site.css").read_text(encoding="utf-8")
    for regel in (".hero-spieltag { padding: clamp(12px, 2.5vw, 24px) clamp(18px, 4vw, 40px) clamp(18px, 3vw, 28px); }",
                  ".abschnitt-fan { padding: clamp(48px, 7vw, 88px) 0 0; }",
                  ".abschnitt-seo { padding-bottom: clamp(48px, 7vw, 88px); }",
                  ".mc-kpirow { display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: nowrap;",
                  ".mc-kpi { flex: 1 1 0; min-width: 0; overflow-wrap: break-word;",
                  ".q-chip.mc-chip { flex: 0 0 auto;",
                  ".knopf-weiter { justify-content: space-between; gap: 12px; max-width: 100%;",
                  "@media (max-width: 520px) {\n  .knopf-weiter { max-width: min(100%, 300px); }\n  .umbruch-mobil { display: block; }"):
        assert regel in css, regel
    assert ".hero .datenstand" not in css


# --- W29 Wünsche Carsten 20.11.2026 (0.22) ---------------------------------------------------------------------------------

def test_w29_start_without_data_line_and_athletic_bilbao(dienst):
    """Startseite ohne „Aktueller Datenstand“ unter dem Ranking (steht in der Fusszeile); Athletic Club heisst auf der
    Website „Athletic Bilbao“ (DE und EN), die Adresse bleibt beim API-Namen."""
    for pfad in ("/vorschau/de/", "/vorschau/en/"):
        start = vorschau.beantworten(pfad, "", dienst).inhalt.decode()
        assert "Aktueller Datenstand" not in start and "Current data as of" not in start
        assert 'class="datenstand-hell zeitzone"' in start
    for lang in ("de", "en"):
        assert namen.anzeige("LaLiga", "Athletic Club", lang) == "Athletic Bilbao"
    assert AD.slug("Athletic Club") == "athletic-club"


# --- W30 Spielseite nach Entwurf „2k final“ (0.23, Beschlüsse 25–32 vom 24.11.2026) ------------------------------------

def _k(abw, anomalie="", vorl=False, pos=None, neg=None, ref=Fraction(64), prozent=False):
    from decimal import Decimal as D
    from types import SimpleNamespace as N
    sig = lambda s: None if s is None else N(schwelle=D(str(s)))                     # noqa: E731
    return N(anomalie=anomalie, abweichung_rund=None if abw is None else D(str(abw)), vorlaeufig=vorl,
             hauptwert_rund=D("40"), heim=N(wert_rund=D("38")), auswaerts=N(wert_rund=D("42")),
             referenz=N(wert=ref, wert_rund=D(str(float(ref)))), prozent=prozent,
             schwellen=N(positiv=sig(pos), negativ=sig(neg)))


def test_w30_cases_and_limit_value():
    """Fall A–D aus der Schwellendatei je Richtung; Grenzwert = Ligadurchschnitt × (1 ± Schwelle), exakt gerundet."""
    from website.spiel import kennzahl
    a = kennzahl("kpi08", _k(-38.35, "stark", neg=35, prozent=True))
    assert (a["fall"], a["grenzwert"], a["schwelle_ganz"]) == ("A", 41.6, 35)          # 64 × 0,65 = 41,60
    b = kennzahl("kpi09", _k(-8.4, neg=10, ref=Fraction(10)))
    assert (b["fall"], b["grenzwert"]) == ("B", 9.0)
    c = kennzahl("kpi02", _k(9.07, neg=20))                                            # nur Schwelle für „weniger“
    assert (c["fall"], c["grenzwert"], c["schwelle_ganz"]) == ("C", None, None)
    d = kennzahl("kpi06", _k(5.18, vorl=True, pos=10))
    assert d["fall"] == "D"
    m = kennzahl("kpi03", _k(34.0, pos=35))                                            # feste Marke 2,5
    assert (m["fall"], m["grenzwert"]) == ("B", 3.38)                                  # 2,5 × 1,35 = 3,375 → 3,38
    gerundet = kennzahl("kpi05", _k(1.0, pos=15, ref=Fraction(943, 100)))
    assert gerundet["grenzwert"] == 10.84                                              # 9,43 × 1,15 = 10,8445 → 10,84


def test_w30_page_cards_chip_button_and_texts(monkeypatch):
    from website import seiten, spiel
    s = {"seite": "spiel", "id": 1, "liga": "bundesliga", "liga_key": "bundesliga", "slug": "a-b-1", "saison": "2026/2027",
         "spieltag": 12, "heim": "A", "gast": "B", "datum": "2026-11-28", "anstoss": "15:30", "termin": "bestaetigt",
         "status": None, "sonderspiel": None, "zustand": "offen", "ergebnis": None, "form_heim": ["-"] * 5,
         "form_gast": ["-"] * 5, "bewertung": "auffaellig", "werte_ab": None, "ergebnis_vom": None, "nachtraeglich": False,
         "korrigiert": False, "ohne_werte": False, "neu_in_liga": [], "anzahl_gewertet": 3, "im_fenster": True,
         "anstoss_zeit": "2026-11-28T15:30", "heim_id": None, "gast_id": None, "jetzt": "2026-11-25T10:00",
         "stand": None, "zeitreise": False}
    a = spiel.kennzahl("kpi08", _k(-38.35, "stark", neg=35, prozent=True))
    b = spiel.kennzahl("kpi09", _k(-8.4, neg=10, ref=Fraction(10)))
    c = spiel.kennzahl("kpi02", _k(9.07, neg=20))
    s.update(auffaellig=[a], uebrige=[c, b], groesste=a)
    html = seiten.spiel_html(s, seiten.Kontext())
    for text in ("Auffälligkeiten", "Ohne Auffälligkeit", "Beide Teams treffen (in %)",
                 '<span class="pct-zusatz"> (in %)</span>', "Tore beider Teams seltener erwartet",
                 "unter 41,60 %", "mehr als 35 % unter dem Ligadurchschnitt",
                 "Keine Auffälligkeit", "unter 9,00", "mehr als 10 % unter dem Ligadurchschnitt",
                 "Nicht eingestuft", "Mehr Tore erwartet", "Diese Abweichung ist in der Bundesliga kein verlässlicher",
                 "Erwarteter Anteil", "Ligadurchschnitt pro Spiel", "Statistisch auffällig ab",
                 "Anteil der letzten 10 Ligaspiele, in denen beide Teams trafen", "nicht definiert",
                 "Für diese Abweichung gibt es in der Bundesliga keine Schwelle."):   # seit 0.25 (Release_08, 9)
        assert text in html, text
    assert "Nicht auffällig" not in html and "Abweichung</span>" not in html          # Abweichung nicht wiederholt
    assert 'data-aufklapp="c-kpi02"' not in html and "Statistisch auffällig. Schwelle" not in html  # seit 0.25 ohne ⓘ
    en = seiten.spiel_html(s, seiten.Kontext(lang="en"))
    for text in ("No anomaly flagged", "Not assessed", "below 41.60%", "Expected percentage",
                 "more than 35% below the league average", "In the Bundesliga, this deviation is not a reliable guide"):
        assert text in en, text


def test_w30_not_enough_data_names_the_new_team():
    from website import seiten
    seite = {"bewertung": "zu_wenig_daten", "ohne_werte": True, "status": None}
    assert seiten.spiel_kern(seite, "de", ["SV Elversberg"])["text"] == \
        "Da SV Elversberg neu in der Liga ist, reicht die Datenbasis für eine Bewertung noch nicht aus."
    assert seiten.zu_wenig_hinweis(seite, "en", ["SV Elversberg", "Hull City"]) == \
        "There are no values for this match yet because SV Elversberg and Hull City are new to the league."


def test_w31_hinweistexte_design_508():
    """Design 24.11.2026 (Version 508): Hinweistexte Startseite (Signalqualität) und Spielseite (Fall C) in DE und EN."""
    de = json.loads((APP / "website" / "texte" / "de.json").read_text(encoding="utf-8"))
    en = json.loads((APP / "website" / "texte" / "en.json").read_text(encoding="utf-8"))
    assert de["lesen"]["signal"].startswith("Sie zeigt, wie häufig sich vergleichbare Auffälligkeiten in früheren Spielen als Prognose")
    assert en["lesen"]["signal"].endswith("The rating has three levels: high, medium or low.")
    # Fall-C-Satz seit 0.25 ersetzt (Release_08, Abschnitt 9; Liga als Feld je Liga und Sprache, Beschluss 44)
    assert de["spiel"]["c_notiz"] == "Diese Abweichung ist {liga_in} kein verlässlicher Hinweis für kommende Spiele."   # 0.26: „für“ (Beschluss 57)
    assert de["liga_in"]["la_liga"] == "in der La Liga" and en["liga_in"]["serie_a"] == "in Serie A"


def test_w32_frontend_review_024():
    """0.24, Entscheide Carsten 24.11.2026 zum Frontend-Review: Manifest mit display „browser“ und Icons, theme-color,
    kein SportsEvent mehr, „Zahlen im Detail“ mindestens 44 px hoch."""
    m = vorschau.beantworten("/vorschau/manifest.webmanifest", "")
    assert m.status == 200 and m.kopf["Content-Type"] == "application/manifest+json"
    daten = json.loads(m.inhalt)
    assert daten["display"] == "browser" and daten["start_url"] == "/vorschau/" and daten["theme_color"] == "#0B3D2E"
    for icon in daten["icons"]:
        bild = vorschau.beantworten(icon["src"], "")
        assert bild.status == 200 and bild.inhalt[:4] == b"\x89PNG"
        breite, hoehe = int.from_bytes(bild.inhalt[16:20], "big"), int.from_bytes(bild.inhalt[20:24], "big")
        assert f"{breite}x{hoehe}" == icon["sizes"]
    html = vorschau.beantworten("/vorschau/de/methodik/", "").inhalt.decode()
    assert '<meta name="theme-color" content="#0B3D2E">' in html and 'rel="manifest"' in html
    assert not hasattr(seo, "sportsevent") and "SportsEvent" not in (APP / "website" / "seiten.py").read_text(encoding="utf-8").replace("# SportsEvent", "")
    css = (APP / "website" / "statisch" / "site.css").read_text(encoding="utf-8")
    assert re.search(r"\.karte details\.detail > summary \{[^}]*min-height: 44px", css)



def test_w33_oeffentliche_website_ohne_zeitreise(monkeypatch):
    """Seit 0.27 (Livegang): ohne Präfix keine Vorschau – kein noindex, Browser-Cache 5 Minuten, ?datum= wird ignoriert."""
    monkeypatch.setattr(W, "PREFIX", "")
    monkeypatch.setattr(W, "VORSCHAU", False)
    a = vorschau.beantworten("/", "")
    assert a.status in (301, 302) and a.kopf["Location"].endswith("/de/")
    m = vorschau.beantworten("/de/methodik/", "datum=2026-08-01")
    html = m.inhalt.decode()
    assert m.status == 200 and m.kopf["Cache-Control"] == "public, max-age=300"
    assert "noindex" not in html and "Zeitreise" not in html and "datum=" not in html
    assert vorschau.beantworten("/robots.txt", "").status == 200


def test_w19_sitemap_archiv_laufende_saison():
    """0.27 (Entscheid Carsten 25.11.2026, 1a): Archivseiten der laufenden Saison sind in der Sitemap, auch Spieltage
    vor dem Livegang (index_ab 26.11.2026); begonnen muss der Spieltag sein. Frühere Saisons: keine Archivseiten."""
    fx = plan(rnd(30, date(2026, 5, 16), saison="2025/2026"), rnd(10, date(2026, 11, 20), date(2026, 11, 22)),
              rnd(11, date(2026, 11, 27)))
    fx["api_id"] = range(1, len(fx) + 1)

    class Spaeter(FakeDaten):
        def zeitpunkt(self):
            return zp("2026-11-23T10:00")

    d = Spaeter({"Bundesliga": fx}, {})
    assert seo.konfig().index_ab == datetime(2026, 11, 26)
    teil = SM.sitemap("/sitemaps/bundesliga-2026-27.xml", d)
    assert "<loc>https://soccer-intelligence.com/de/spieltag/bundesliga/2026-27/10/</loc>" in teil
    assert "<loc>https://soccer-intelligence.com/en/matchday/bundesliga/2026-27/10/</loc>" in teil
    assert "/2026-27/11/" not in teil                                                 # noch nicht begonnen
    alt = SM.sitemap("/sitemaps/bundesliga-2025-26.xml", d)
    assert alt is not None and "/2025-26/" not in alt                                 # Vorsaison: kein Archiv
