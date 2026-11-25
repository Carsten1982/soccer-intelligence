"""HTML der Website aus den Vorlagen (vorlagen/*.html, Jinja2) und den Datensätzen (Codes).

Alle Texte kommen aus der Sprachdatei (texte.py), alle Zahlen und Daten aus format.py, alle Adressen aus adressen.py.
Jinja maskiert jeden Wert (autoescape), StrictUndefined macht einen fehlenden Wert zum Fehler statt zu einer leeren
Stelle. Seit 0.21 jede Seite in Deutsch und Englisch (Kontext.lang) mit Kopfbereich nach dem SEO-Briefing: Title,
Description, canonical, hreflang (de, en, x-default), Open Graph, Twitter-Karte, Icons, JSON-LD, robots.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from datetime import date, datetime
from functools import lru_cache
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import Markup

from . import adressen as A
from . import einstellungen as W
from . import format as F
from . import namen as N
from . import seo
from . import texte as T


@dataclass(frozen=True)
class Kontext:
    """Rahmen einer Seite: Sprache, Seite (für Sprachwechsel und canonical), Adresse (Vorschau-Präfix), Zeitreise."""
    prefix: str = W.PREFIX
    vorschau: bool = True
    datum: str | None = None          # ?datum=… der Zeitreise (wird an alle Links gehängt)
    ungueltig: bool = False
    jetzt: datetime | None = None
    zeitreise: bool = False
    lang: str = W.SPRACHE
    ziel: A.Ziel | None = None        # aktuelle Seite; None bei „nicht gefunden“

    def url(self, pfad: str) -> str:
        pfad = pfad if pfad.startswith("/") else "/" + pfad
        ziel = self.prefix.rstrip("/") + pfad
        return ziel + (f"?datum={quote(self.datum)}" if self.datum else "")

    def link(self, art: str, **teile) -> str:
        """Adresse einer Seite in der Sprache dieser Seite: link('spieltag', liga='bundesliga')."""
        return self.url(A.pfad(A.Ziel(art, self.lang, **teile)))

    def sprach_url(self, lang: str) -> str:
        """Dieselbe Seite in der anderen Sprache; ohne Seite (404) die Startseite der Sprache."""
        ziel = self.ziel.in_sprache(lang) if self.ziel is not None else A.Ziel("start", lang)
        return self.url(A.pfad(ziel))

    def absolut(self, lang: str | None = None) -> str | None:
        """Absolute Adresse auf der Domain (canonical, hreflang, og:url)."""
        if self.ziel is None:
            return None
        return W.DOMAIN + A.pfad(self.ziel.in_sprache(lang or self.lang))

    def statisch(self, pfad: str) -> str:
        """Adresse einer Datei aus statisch/ mit Versionsnummer (?v=…, Prüfsumme des Inhalts; seit 0.19.1): Nach einem
        Release mit geänderter CSS- oder JS-Datei lädt der Browser sie neu, ohne Strg+F5."""
        return f"{self.prefix.rstrip('/')}/statisch/{pfad}" + version(pfad)

    def mit(self, **werte) -> "Kontext":
        return replace(self, **werte)


def version(pfad: str) -> str:
    """„?v=“ und die ersten 10 Zeichen der SHA-256 der Datei; leer, wenn die Datei fehlt. Nur CSS und JS: Schriften
    ändern sich nicht, und ihre Vorlade-Adresse muss genau der Adresse in site.css entsprechen (sonst doppelt geladen)."""
    if not pfad.endswith((".css", ".js")):
        return ""
    try:
        st = (W.STATISCH / pfad).stat()
    except OSError:
        return ""
    return f"?v={_pruefsumme(pfad, st.st_mtime_ns, st.st_size)}"


@lru_cache(maxsize=64)
def _pruefsumme(pfad: str, mtime_ns: int, groesse: int) -> str:
    """Einmal je Dateistand gerechnet (Zeit und Grösse im Schlüssel)."""
    return hashlib.sha256((W.STATISCH / pfad).read_bytes()).hexdigest()[:10]


# --- Darstellungshilfen ---------------------------------------------------------------------------------------

def liga_name(slug: str) -> str:
    """Liga-Slug → Name in Datenbank und Spielplan („la-liga“ → „LaLiga“)."""
    web = W.liga_aus_slug(slug)
    return web.name if web else slug


def team(liga_slug: str, name: str, lang: str) -> str:
    """Anzeigename des Vereins in der Sprache (Glossar 11); sonst der Name der Datenquelle."""
    return N.anzeige(liga_name(liga_slug), name, lang)


def termin(s: dict, lang: str = W.SPRACHE) -> str:
    """Zeile unter der Paarung bzw. im Scoreboard (Konzept 5.5)."""
    d = date.fromisoformat(s["datum"])
    if s.get("status") == "verschoben":
        return T.t("termin.termin_offen", lang)
    if s.get("termin") == "vorlaeufig":
        tage = F.wochenende(d, lang)
        anfang = T.t("termin.wochenende", lang, tage=tage) if tage else F.tag(d, lang)
        return f"{anfang} · {T.t('termin.termin_offen', lang)}"
    if s.get("termin") == "zeit_offen":
        return f"{F.tag(d, lang)} · {T.t('termin.zeit_offen', lang)}"
    return f"{F.tag(d, lang)} · {s['anstoss']}" if s.get("anstoss") else F.tag(d, lang)


# Signalqualität (seit 0.21 nach den Entwürfen P1): eine Farbfamilie in drei Stufen, unabhängig von der Richtung.
STUFEN = ("stark", "mittel", "gering")
BALKEN_ZAHL = {"stark": 3, "mittel": 2, "gering": 1}
STIL = {"stark": "stark", "mittel": "mittel", "gering": "gering"}


def stil(stufe: str | None) -> str:
    return STIL.get(stufe or "", "")


def balken_daten(k: dict) -> dict:
    """Balken nach Übergabe 4.2: Länge = Betrag/100 × 50 % der Breite, höchstens 50 %; über 100 % gekappt mit
    gestricheltem Streifen. Farbe: über dem Schnitt die Stufe (stark/mittel/gering), darunter rot; normal hell;
    schraffiert = zu wenig Daten."""
    wert = k.get("abweichung")
    if wert is None:
        return {"breite": 0, "richtung": "hoch", "klasse": "f-schraffiert", "kappe": False}
    betrag = abs(wert)
    richtung = "hoch" if wert >= 0 else "tief"
    stufe = k.get("stufe")
    if stufe in STIL:
        klasse = f"f-{STIL[stufe]}" if richtung == "hoch" else "f-tief"
    elif stufe == "zu_wenig_daten":
        klasse = "f-schraffiert"
    else:
        klasse = f"f-normal-{richtung}"
    return {"breite": int(round(min(50.0, betrag / 2))), "richtung": richtung, "klasse": klasse,
            "kappe": betrag > 100}


def aufteilung(k: dict) -> int:
    """Anteil des Heimteams in Prozent der Leiste (nur Gelbe Karten, Summe der Teamwerte, Q1)."""
    summe = (k["heim"] or 0) + (k["gast"] or 0)
    return int(round(100 * (k["heim"] or 0) / summe)) if summe else 50


def zaehlform(tab: dict, lang: str = W.SPRACHE) -> str:
    """„9 Spiele“, „9 Spiele + 1 Nachholspiel“, „8 Spiele + 2 Nachholspiele“, nur Sonderspiele „1 Nachholspiel“ bzw.
    „1 Spiel vorgezogen“ (Template-Briefing 3.3, Glossar 9)."""
    teile = [T.tn("spieltag.partien", tab["partien"], lang)] if tab["partien"] else []
    for art in ("nachholspiel", "vorgezogen"):
        n = tab["sonderspiele"][art]
        if n:
            teile.append(T.tn(f"spieltag.{art}", n, lang) if teile else T.tn(f"spieltag.nur_sonderspiele.{art}", n, lang))
    return " + ".join(teile) or T.tn("spieltag.partien", 0, lang)


def _env() -> Environment:
    return Environment(loader=FileSystemLoader(str(W.VORLAGEN)), autoescape=select_autoescape(["html"]),
                       undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)


ENV = _env()


def _werte(k: Kontext) -> dict:
    """Alles, was die Vorlagen brauchen, an die Sprache der Seite gebunden."""
    lang = k.lang

    def iso(fn):
        return lambda wert: fn(date.fromisoformat(wert), lang) if wert else ""

    return {
        "lang": lang, "sprachen": W.SPRACHEN, "sprachname": W.SPRACHNAME,
        "t": lambda s, **w: T.t(s, lang, **w), "tn": lambda s, n, **w: T.tn(s, n, lang, **w),
        "prozent": lambda v: F.prozent(v, lang),
        "zahl": lambda v, kk=None: F.zahl(v, lang, "%" if kk and kk.get("prozent") else ""),
        "tag": iso(F.tag), "datum_kurz": iso(F.datum_kurz), "tag_monat": iso(F.tag_monat), "datum_voll": iso(F.datum_voll),
        "zeitraum": lambda von, bis: F.zeitraum(date.fromisoformat(von), date.fromisoformat(bis), lang),
        "ergebnis": lambda e: F.ergebnis(*e), "ergebnis_kurz": lambda e: F.ergebnis_kurz(*e),
        "termin": lambda s: termin(s, lang),
        "team": lambda liga, name: team(liga, name, lang), "zaehlform": lambda tab: zaehlform(tab, lang),
        "url": k.url, "link": k.link, "sprach_url": k.sprach_url, "statisch": k.statisch,
        "standard_liga": W.STANDARD_LIGA, "ligen": W.LIGEN, "stil": stil, "stufen": STUFEN, "balken_zahl": BALKEN_ZAHL,
        "balken_daten": balken_daten, "aufteilung": aufteilung,
    }


def _rahmen(k: Kontext, stand_iso: str | None) -> dict:
    stand = datetime.fromisoformat(stand_iso) if stand_iso else None
    return {
        "vorschau": k.vorschau, "ungueltig": k.ungueltig,
        "zeitreise": F.stand(k.jetzt, k.lang) if k.zeitreise and k.jetzt else None,
        "datum_wert": k.jetzt.strftime("%Y-%m-%dT%H:%M") if k.zeitreise and k.jetzt else "",
        "stand_text": F.stand(stand, k.lang),
        "veraltet_text": F.tag(stand.date(), k.lang) if stand else F.STRICH,
    }


def _kopf(k: Kontext, titel: str, beschreibung: str = "", *, index: bool = True, jsonld: list | None = None,
          og_titel: str | None = None) -> dict:
    """Kopfbereich (SEO-Briefing 4). Ohne Seite (404): kein canonical, kein hreflang. Die Vorschau ist immer
    „noindex, nofollow“; der Index-Status der Seite steht dann in der Vorschau-Leiste."""
    canonical = k.absolut()
    alternates = []
    if canonical:
        alternates = [(lg, k.absolut(lg)) for lg in W.SPRACHEN] + [("x-default", k.absolut(W.SPRACHE))]
    robots = "noindex, nofollow" if k.vorschau else (None if index else "noindex,follow")
    return {
        "seitentitel": titel, "beschreibung": beschreibung, "canonical": canonical, "alternates": alternates,
        "robots": robots, "index": index, "og_titel": og_titel or titel, "og_locale": W.OG_LOCALE[k.lang],
        "og_locale_alt": [W.OG_LOCALE[x] for x in W.SPRACHEN if x != k.lang], "domain": W.DOMAIN,
        "jsonld": Markup(seo.als_skript(jsonld)) if jsonld else None,
    }


def _rendern(vorlage: str, k: Kontext, kopf: dict, stand_iso: str | None, **werte) -> str:
    return ENV.get_template(vorlage).render(**_werte(k), **_rahmen(k, stand_iso), **kopf, **werte)


def _bc(k: Kontext, *punkte: tuple[str, str]) -> dict:
    """BreadcrumbList: Startseite, dann die übergebenen Punkte (Name, Pfad-Ziel)."""
    start = (T.t("kopf.startseite", k.lang), W.DOMAIN + A.pfad(A.Ziel("start", k.lang)))
    return seo.breadcrumbs([start, *punkte])


# --- Startseite -----------------------------------------------------------------------------------------------

def start_html(seite: dict, k: Kontext, foto: str | None = None) -> str:
    k = k.mit(ziel=A.Ziel("start", k.lang))
    pause = seite.get("pause") or {}
    kopf = _kopf(k, T.t("seo.start_titel", k.lang), T.t("seo.start_beschreibung", k.lang),
                 jsonld=seo.start_jsonld(k.absolut(), k.lang))
    return _rendern("start.html", k, kopf, seite.get("stand"), seite=seite, aktiv="", foto=foto,
                    pause_datum=F.tag(date.fromisoformat(pause["datum"]), k.lang) if pause.get("datum") else F.STRICH)


# --- Spieltag und Archiv --------------------------------------------------------------------------------------

def spieltag_html(seite: dict, k: Kontext) -> str:
    k = k.mit(ziel=A.Ziel("spieltag", k.lang, liga=seite["liga"]))
    liga = T.t(f"liga.{seite['liga_key']}", k.lang)
    pause = seite.get("pause") or {}
    titel = T.t("seo.spieltag_titel", k.lang, liga=liga)
    jsonld = [_bc(k, (liga, k.absolut())), seo.webseite(k.absolut(), titel, k.lang)]
    kopf = _kopf(k, titel, T.t("seo.spieltag_beschreibung", k.lang, liga=liga), jsonld=jsonld)
    return _rendern("spieltag.html", k, kopf, seite.get("stand"), seite=seite, aktiv="spieltag",
                    pause_datum=F.tag(date.fromisoformat(pause["datum"]), k.lang) if pause.get("datum") else F.STRICH)


def archiv_html(seite: dict, k: Kontext) -> str:
    k = k.mit(ziel=A.Ziel("archiv", k.lang, liga=seite["liga"], saison=seite["saison"], nr=seite["spieltag"]))
    liga = T.t(f"liga.{seite['liga_key']}", k.lang)
    saison = seo.saison_kurz(seite["saison"])
    titel = T.t("seo.archiv_titel", k.lang, liga=liga, n=seite["spieltag"], saison=saison)
    index = seo.archiv_indexierbar(date.fromisoformat(seite["beginn"]) if seite.get("beginn") else None)
    spieltag_url = W.DOMAIN + A.pfad(A.Ziel("spieltag", k.lang, liga=seite["liga"]))
    jsonld = [_bc(k, (liga, spieltag_url), (T.t("archiv.kopf", k.lang, liga=liga, n=seite["spieltag"], saison=saison),
                                             k.absolut())), seo.webseite(k.absolut(), titel, k.lang)]
    kopf = _kopf(k, titel, T.t("seo.archiv_beschreibung", k.lang, liga=liga, n=seite["spieltag"], saison=saison),
                 index=index, jsonld=jsonld)
    return _rendern("archiv.html", k, kopf, seite.get("stand"), seite=seite, aktiv="spieltag", saison_text=saison)


# --- Spielseite -----------------------------------------------------------------------------------------------

def _zeitpunkt(seite: dict, lang: str) -> str:
    d = F.tag(date.fromisoformat(seite["datum"]), lang)
    return T.t("spiel.zeitpunkt_uhr", lang, tag=d, uhr=seite["anstoss"]) if seite.get("anstoss") else d


def _neu_text(schluessel: str, namen: list[str], lang: str) -> str | None:
    """„… weil X neu in der Liga ist“ bzw. mit zwei Teams (seit 0.23, Glossar 20a/20b)."""
    if len(namen) == 1:
        return T.t(schluessel, lang, team=namen[0])
    if len(namen) == 2:
        return T.t(schluessel + "_zwei", lang, team1=namen[0], team2=namen[1])
    return None


def zu_wenig_hinweis(seite: dict, lang: str, namen: list[str]) -> str:
    """Hinweisbox „Zu wenig Daten:“ (Entwurf 2k): ohne Werte mit dem neuen Team, sonst der allgemeine Satz."""
    if seite["ohne_werte"]:
        return _neu_text("spiel.hinweis_zu_wenig_daten_neu", namen, lang) or T.t("spiel.hinweis_zu_wenig_daten_leer", lang)
    return T.t("spiel.hinweis_zu_wenig_daten", lang)


def spiel_kern(seite: dict, lang: str = W.SPRACHE, neu: list[str] | None = None) -> dict:
    """Kernaussage im Scoreboard (Entwurf Spiel_P1, Übergabe 7.3; seit 0.23 Entwurf 2k: „Zu wenig Daten“ nennt das
    neue Team, bei „Beide Teams treffen“ der Zusatz „(in %)“, auf dem Handy ausgeblendet)."""
    def tt(s, **w):
        return T.t(s, lang, **w)

    if seite["bewertung"] == "status":
        return {"label": tt("spiel.status_titel"), "wert": "", "richtung": "", "titel": tt(f"chip.{seite['status']}"),
                "text": tt("spiel.status_text")}
    if seite["bewertung"] == "werte_ab":                      # noch ohne Werte (Template-Briefing 3.6)
        if seite.get("werte_ab"):
            titel = tt("spiel.werte_ab_kurz", datum=F.tag(date.fromisoformat(seite["werte_ab"]), lang))
            text = tt("spiel.werte_ab_sub")
        elif seite.get("ergebnis_vom"):
            titel = tt("spiel.werte_ab_titel")
            text = tt("spiel.werte_folgen", datum=F.datum_kurz(date.fromisoformat(seite["ergebnis_vom"]), lang))
        else:
            titel, text = tt("spiel.werte_ab_titel"), tt("spiel.werte_wartet")
        return {"label": tt("spiel.werte_label"), "wert": "", "richtung": "", "titel": titel, "text": text}
    if seite["bewertung"] == "zu_wenig_daten":
        return {"label": tt("spiel.bewertung"), "wert": "", "richtung": "", "titel": tt("spiel.zu_wenig_daten"),
                "text": _neu_text("spiel.zu_wenig_daten_neu", neu or [], lang) or tt("spiel.zu_wenig_daten_text")}
    if seite["auffaellig"]:
        top = seite["auffaellig"][0]
        return {"label": tt("spiel.auffaelligstes"), "wert": F.prozent(top["abweichung"], lang), "richtung": top["richtung"],
                "titel": tt(f"kennzahl.{top['kpi']}.name"), "text": tt(f"kennzahl.{top['kpi']}.{top['richtung']}"),
                "zusatz": tt("spiel.prozent_zusatz") if top.get("prozent") else ""}
    g = seite["groesste"]
    schluessel = "spiel.keine_text_eins" if seite["anzahl_gewertet"] == 1 else "spiel.keine_text"
    if seite["anzahl_gewertet"] not in (1, 8):
        schluessel = "spiel.keine_text_gewertet"
    return {"label": tt("spiel.gesamtbild"), "wert": "", "richtung": "", "titel": tt("spiel.keine_titel"),
            "text": tt(schluessel, n=seite["anzahl_gewertet"], name=tt(f"kennzahl.{g['kpi']}.name"),
                       wert=F.prozent(g["abweichung"], lang)) if g else ""}


def spiel_notizen(seite: dict, lang: str = W.SPRACHE) -> list[dict]:
    """Hinweisboxen unter dem Scoreboard: Nachholspiel / vorgezogen, gespielt (Q5; seit 0.20 mit Schnappschuss:
    nachträglich berechnet, Ergebnis korrigiert), „Werte folgen“ bei fehlendem Vorspiel-Ergebnis."""
    def tt(s, **w):
        return T.t(s, lang, **w)

    out = []
    if seite["sonderspiel"] == "nachholspiel":
        out.append({"titel": tt("spiel.hinweis_nachholspiel_titel"),
                    "text": tt("spiel.hinweis_nachholspiel", datum=_zeitpunkt(seite, lang))})
    elif seite["sonderspiel"] == "vorgezogen":
        out.append({"titel": tt("spiel.hinweis_vorgezogen_titel"),
                    "text": tt("spiel.hinweis_vorgezogen", spieltag=tt("spieltag.nummer", n=seite["spieltag"]),
                               datum=_zeitpunkt(seite, lang))})
    if seite["zustand"] == "gespielt" and seite["bewertung"] not in ("status", "werte_ab"):
        text = tt("spiel.hinweis_nachtraeglich") if seite.get("nachtraeglich") else tt("spiel.hinweis_gespielt")
        if seite.get("korrigiert"):
            text += " " + tt("spiel.hinweis_korrigiert") + "."
        out.append({"titel": tt("spiel.hinweis_gespielt_titel"), "text": text})
    return out


def spiel_html(seite: dict, k: Kontext) -> str:
    lang = k.lang
    k = k.mit(ziel=A.Ziel("spiel", lang, liga=seite["liga"], spiel_id=seite["id"], slug=seite["slug"]))
    heim, gast = team(seite["liga"], seite["heim"], lang), team(seite["liga"], seite["gast"], lang)
    liga = T.t(f"liga.{seite['liga_key']}", lang)
    if seite["zustand"] == "gespielt" and seite["bewertung"] != "status":
        wann = T.t("spiel.endstand", lang, ergebnis=F.ergebnis(*seite["ergebnis"])) if seite["ergebnis"] else \
            T.t("chip.gespielt", lang)
    else:
        wann = termin(seite, lang)
    index = seo.spiel_indexierbar(seite)
    titel = seo.spiel_titel(seite, heim, gast, lang)
    beschreibung = seo.spiel_beschreibung(seite, heim, gast, lang)
    zurueck = (k.link("archiv", liga=seite["liga"], saison=seite["saison"], nr=seite["spieltag"])
               if seite["zustand"] == "gespielt" and seo.saison_hat_seiten(seite["saison"])
               else k.link("spieltag", liga=seite["liga"]))
    spieltag_abs = W.DOMAIN + A.pfad(A.Ziel("spieltag", lang, liga=seite["liga"]))
    jsonld = [_bc(k, (liga, spieltag_abs), (f"{heim} – {gast}" if lang == "de" else f"{heim} vs {gast}", k.absolut()))]
    # SportsEvent seit 0.24 entfernt (Entscheid Carsten 24.11.2026): ohne Ort ungültig für Google, kein Nutzen
    og_titel = f"{heim} – {gast}" if seite["bewertung"] == "werte_ab" else None
    kopf = _kopf(k, titel, beschreibung, index=index, jsonld=jsonld, og_titel=og_titel)
    neu = [team(seite["liga"], n, lang) for n in seite.get("neu_in_liga") or []]
    return _rendern("spiel.html", k, kopf, seite.get("stand"), seite=seite, aktiv="spieltag",
                    held=spiel_kern(seite, lang, neu), notizen=spiel_notizen(seite, lang), wann=wann,
                    zu_wenig_hinweis=zu_wenig_hinweis(seite, lang, neu),
                    heim_name=heim, gast_name=gast, zurueck_url=zurueck,
                    h1=T.t("spiel.h1", lang, heim=heim, gast=gast))


# --- Inhaltsseiten, Hinweise und Fehler ---------------------------------------------------------------------

INHALT = {"methodik": "WebPage", "glossar": "WebPage", "impressum": "WebPage", "datenschutz": "WebPage",
          "kontakt": "ContactPage"}


def inhalt_html(art: str, k: Kontext, stand_iso: str | None = None, **werte) -> str:
    """Methodik, Glossar, Kontakt, Impressum, Datenschutz: Rahmen aus inhalt.html, Text je Sprache aus
    vorlagen/inhalt/<seite>.<sprache>.html (lange Texte, darum nicht in der Sprachdatei; Rückfall Deutsch)."""
    k = k.mit(ziel=A.Ziel(art, k.lang))
    titel = T.t(f"seo.{art}_titel", k.lang)
    name = T.t(f"seite.{art}", k.lang)
    jsonld = [_bc(k, (name, k.absolut())), seo.webseite(k.absolut(), titel, k.lang, INHALT[art])]
    kopf = _kopf(k, titel, T.t(f"seo.{art}_beschreibung", k.lang), jsonld=jsonld)
    teil = f"inhalt/{art}.{k.lang}.html"
    if not (W.VORLAGEN / teil).exists():
        teil = f"inhalt/{art}.{W.SPRACHE}.html"
    if art == "methodik" and "m" not in werte:              # Zahlen aus der Schwellendatei (website/methodik.py)
        from . import methodik as MT
        werte["m"] = MT.daten(k.lang)
    if art == "kontakt" and "f" not in werte:              # Formular (seit 0.23, website/kontakt.py)
        from . import kontakt as KT
        werte["f"] = KT.leer()
    return _rendern("inhalt.html", k, kopf, stand_iso, art=art, teil=teil, aktiv=art,
                    betreiber={"name": W.BETREIBER_NAME, "adresse": W.BETREIBER_ADRESSE, "email": W.KONTAKT_EMAIL},
                    **werte)


def fehlt_html(k: Kontext, stand_iso: str | None = None) -> str:
    """Seite „nicht gefunden“ (404, noindex, ohne canonical und hreflang), in der Sprache des Verzeichnisses."""
    k = k.mit(ziel=None)
    kopf = _kopf(k, T.t("seo.fehlt_titel", k.lang), "", index=False)
    return _rendern("fehlt.html", k, kopf, stand_iso, aktiv="")


def hinweis_html(art: str, k: Kontext, stand_iso: str | None = None, aktiv: str = "") -> str:
    """art: folgt (Seite kommt mit einem späteren Release) oder daten (Daten werden geprüft, Status 503)."""
    k = k.mit(ziel=None)
    if art == "folgt":
        titel, text, seitentitel = T.t("folgt.titel", k.lang), T.t("folgt.text", k.lang), T.t("folgt.seitentitel", k.lang)
    else:
        titel, text = T.t("fehler.daten_titel", k.lang), T.t("fehler.daten_text", k.lang)
        seitentitel = T.t("fehler.seitentitel", k.lang)
    kopf = _kopf(k, seitentitel, "", index=False)
    return _rendern("hinweis.html", k, kopf, stand_iso, titel=titel, text=text, aktiv=aktiv)
