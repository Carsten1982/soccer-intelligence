"""HTML der Website aus den Vorlagen (vorlagen/*.html, Jinja2) und den Datensätzen (Codes).

Alle Texte kommen aus der Sprachdatei (texte.py), alle Zahlen und Daten aus format.py. Jinja maskiert jeden Wert
(autoescape), StrictUndefined macht einen fehlenden Wert zum Fehler statt zu einer leeren Stelle. Seit 0.18 drei
Seiten nach den Entwürfen: Startseite (1d), Spieltag (3d), Matchdetail (2i).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date, datetime
from functools import lru_cache
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from . import einstellungen as W
from . import format as F
from .texte import t, tn


@dataclass(frozen=True)
class Kontext:
    """Rahmen einer Seite: Adresse (Vorschau-Präfix), Zeitreise, Vorschau-Leiste."""
    prefix: str = W.PREFIX
    vorschau: bool = True
    datum: str | None = None          # ?datum=… der Zeitreise (wird an alle Links gehängt)
    ungueltig: bool = False
    jetzt: datetime | None = None
    zeitreise: bool = False

    def url(self, pfad: str) -> str:
        pfad = pfad if pfad.startswith("/") else "/" + pfad
        ziel = self.prefix.rstrip("/") + pfad
        return ziel + (f"?datum={quote(self.datum)}" if self.datum else "")

    def statisch(self, pfad: str) -> str:
        """Adresse einer Datei aus statisch/ mit Versionsnummer (?v=…, Prüfsumme des Inhalts; seit 0.19.1): Nach einem
        Release mit geänderter CSS- oder JS-Datei lädt der Browser sie neu, ohne Strg+F5."""
        return f"{self.prefix.rstrip('/')}/statisch/{pfad}" + version(pfad)


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


# --- Darstellungshilfen -----------------------------------------------------------------------------------

def termin(s: dict) -> str:
    """Zeile unter der Paarung bzw. im Scoreboard (Konzept 5.5)."""
    d = date.fromisoformat(s["datum"])
    if s.get("status") == "verschoben":
        return t("termin.termin_offen")
    if s.get("termin") == "vorlaeufig":
        tage = F.wochenende(d)
        anfang = t("termin.wochenende", tage=tage) if tage else F.tag(d)
        return f"{anfang} · {t('termin.termin_offen')}"
    if s.get("termin") == "zeit_offen":
        return f"{F.tag(d)} · {t('termin.zeit_offen')}"
    return f"{F.tag(d)} · {s['anstoss']}" if s.get("anstoss") else F.tag(d)


# Gestaltung bis zum Designentwurf der Website (seit 0.19): Signalqualität stark dunkel (CSS-Klasse „stark“),
# mittel und gering hell (CSS-Klasse „leicht“, bis 0.18 „leicht“). Die Wörter zeigen die Signalqualität.
STIL = {"stark": "stark", "mittel": "leicht", "gering": "leicht"}


def stil(stufe: str | None) -> str:
    return STIL.get(stufe or "", "")


def balken_daten(k: dict) -> dict:
    """Balken nach Übergabe 4.2: Länge = Betrag/100 × 50 % der Breite, höchstens 50 %; über 100 % gekappt mit
    gestricheltem Streifen. Farbe: dunkel = stark, hell = leicht, grau = normal, schraffiert = nicht gewertet."""
    wert = k.get("abweichung")
    if wert is None:
        return {"breite": 0, "richtung": "hoch", "klasse": "f-schraffiert", "kappe": False}
    betrag = abs(wert)
    richtung = "hoch" if wert >= 0 else "tief"
    stufe = k.get("stufe")
    if stufe in STIL:
        klasse = f"f-{STIL[stufe]}-{richtung}"
    elif stufe == "zu_wenig_daten":
        klasse = "f-schraffiert"
    else:
        klasse = "f-normal"
    return {"breite": int(round(min(50.0, betrag / 2))), "richtung": richtung, "klasse": klasse,
            "kappe": betrag > 100}


def zaehlform(tab: dict) -> str:
    """„9 Spiele“, „9 Spiele + 1 Nachholspiel“, „8 Spiele + 2 Nachholspiele“, nur Sonderspiele „1 Nachholspiel“ bzw.
    „1 Spiel vorgezogen“ (Template-Briefing 3.3, seit 0.20)."""
    teile = [tn("spieltag.partien", tab["partien"])] if tab["partien"] else []
    for art in ("nachholspiel", "vorgezogen"):
        n = tab["sonderspiele"][art]
        if n:
            teile.append(tn(f"spieltag.{art}", n) if teile else tn(f"spieltag.nur_sonderspiele.{art}", n))
    return " + ".join(teile) or tn("spieltag.partien", 0)


def zahl(wert, k: dict | None = None) -> str:
    return F.zahl(wert, einheit="%" if k and k.get("prozent") else "")


def aufteilung(k: dict) -> int:
    """Anteil des Heimteams in Prozent der Leiste (nur Gelbe Karten, Summe der Teamwerte, Q1)."""
    summe = (k["heim"] or 0) + (k["gast"] or 0)
    return int(round(100 * (k["heim"] or 0) / summe)) if summe else 50


def _env() -> Environment:
    env = Environment(loader=FileSystemLoader(str(W.VORLAGEN)), autoescape=select_autoescape(["html"]),
                      undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    env.globals.update(
        t=t, tn=tn, termin=termin, standard_liga=W.STANDARD_LIGA, prozent=F.prozent, zahl=zahl,
        balken_daten=balken_daten, aufteilung=aufteilung, ligen=W.LIGEN, stil=stil, zaehlform=zaehlform,
        ergebnis=lambda e: F.ergebnis(*e),
        zeitraum=lambda von, bis: F.zeitraum(date.fromisoformat(von), date.fromisoformat(bis)),
        datum_kurz=lambda iso: F.datum_kurz(date.fromisoformat(iso)) if iso else "",
        tag_monat=lambda iso: F.tag_monat(date.fromisoformat(iso)) if iso else "",
    )
    return env


ENV = _env()


def _rahmen(k: Kontext, stand_iso: str | None) -> dict:
    stand = datetime.fromisoformat(stand_iso) if stand_iso else None
    return {
        "vorschau": k.vorschau, "url": k.url, "statisch": k.statisch, "ungueltig": k.ungueltig,
        "zeitreise": F.stand(k.jetzt) if k.zeitreise and k.jetzt else None,
        "datum_wert": k.jetzt.strftime("%Y-%m-%dT%H:%M") if k.zeitreise and k.jetzt else "",
        "stand_text": F.stand(stand),
        "datenstand_text": F.tag_jahr(stand.date()) if stand else "–",
        "veraltet_text": F.tag(stand.date()) if stand else "–",
    }


# --- Seiten --------------------------------------------------------------------------------------------------

def spieltag_html(seite: dict, k: Kontext) -> str:
    liga = t(f"liga.{seite['liga_key']}")
    pause = seite.get("pause") or {}
    return ENV.get_template("spieltag.html").render(
        seite=seite, aktiv="spieltag", seitentitel=t("spieltag.seitentitel", liga=liga),
        beschreibung=t("spieltag.beschreibung", liga=liga),
        pause_datum=F.tag(date.fromisoformat(pause["datum"])) if pause.get("datum") else "–",
        **_rahmen(k, seite.get("stand")))


def _zeitpunkt(seite: dict) -> str:
    d = F.tag(date.fromisoformat(seite["datum"]))
    return t("spiel.zeitpunkt_uhr", tag=d, uhr=seite["anstoss"]) if seite.get("anstoss") else d


def spiel_kern(seite: dict) -> dict:
    """Kernaussage im Scoreboard (Entwurf 2i, Übergabe 7.3)."""
    if seite["bewertung"] == "status":
        return {"label": t("spiel.status_titel"), "wert": "", "richtung": "", "titel": t(f"chip.{seite['status']}"),
                "text": t("spiel.status_text")}
    if seite["bewertung"] == "werte_ab":                      # noch ohne Werte (seit 0.20, Template-Briefing 3.6)
        if seite.get("werte_ab"):
            text = t("spiel.werte_ab", datum=F.tag(date.fromisoformat(seite["werte_ab"])))
        elif seite.get("ergebnis_vom"):
            text = t("spiel.werte_folgen", datum=F.datum_kurz(date.fromisoformat(seite["ergebnis_vom"])))
        else:
            text = t("spiel.werte_wartet")
        return {"label": t("spiel.bewertung"), "wert": "", "richtung": "", "titel": t("spiel.werte_ab_titel"),
                "text": text}
    if seite["bewertung"] == "zu_wenig_daten":
        return {"label": t("spiel.bewertung"), "wert": "", "richtung": "", "titel": t("spiel.zu_wenig_daten"),
                "text": t("spiel.zu_wenig_daten_leer_text") if seite["ohne_werte"] else t("spiel.zu_wenig_daten_text")}
    if seite["auffaellig"]:
        top = seite["auffaellig"][0]
        return {"label": t("spiel.auffaelligstes"), "wert": F.prozent(top["abweichung"]), "richtung": top["richtung"],
                "titel": t(f"kennzahl.{top['kpi']}.name"), "text": t(f"kennzahl.{top['kpi']}.{top['richtung']}")}
    g = seite["groesste"]
    schluessel = "spiel.keine_text_eins" if seite["anzahl_gewertet"] == 1 else "spiel.keine_text"   # 0.20: n dynamisch
    return {"label": t("spiel.gesamtbild"), "wert": "", "richtung": "", "titel": t("spiel.keine_titel"),
            "text": t(schluessel, n=seite["anzahl_gewertet"], name=t(f"kennzahl.{g['kpi']}.name"),
                      wert=F.prozent(g["abweichung"])) if g else ""}


def spiel_notizen(seite: dict) -> list[dict]:
    """Hinweisboxen unter dem Scoreboard: Nachholspiel / vorgezogen, gespielt (Q5; seit 0.20 mit Schnappschuss:
    nachträglich berechnet, Ergebnis korrigiert)."""
    out = []
    if seite["sonderspiel"] == "nachholspiel":
        out.append({"titel": t("spiel.hinweis_nachholspiel_titel"),
                    "text": t("spiel.hinweis_nachholspiel", datum=_zeitpunkt(seite))})
    elif seite["sonderspiel"] == "vorgezogen":
        out.append({"titel": t("spiel.hinweis_vorgezogen_titel"),
                    "text": t("spiel.hinweis_vorgezogen", spieltag=t("spieltag.nummer", n=seite["spieltag"]),
                              datum=_zeitpunkt(seite))})
    if seite["zustand"] == "gespielt" and seite["bewertung"] not in ("status", "werte_ab"):
        out.append({"titel": t("spiel.hinweis_gespielt_titel"),
                    "text": t("spiel.hinweis_nachtraeglich") if seite.get("nachtraeglich") else t("spiel.hinweis_gespielt")})
    if seite.get("korrigiert"):
        out.append({"titel": t("spiel.hinweis_korrigiert_titel"), "text": t("spiel.hinweis_korrigiert")})
    return out


def spiel_html(seite: dict, k: Kontext) -> str:
    liga = t(f"liga.{seite['liga_key']}")
    if seite["zustand"] == "gespielt":
        wann = t("spiel.endstand", ergebnis=F.ergebnis(*seite["ergebnis"])) if seite["ergebnis"] else \
            t("spiel.gespielt")
    else:
        wann = termin(seite)
    return ENV.get_template("spiel.html").render(
        seite=seite, aktiv="spieltag", held=spiel_kern(seite), notizen=spiel_notizen(seite), wann=wann,
        seitentitel=t("spiel.seitentitel", heim=seite["heim"], gast=seite["gast"], liga=liga),
        beschreibung=t("spiel.beschreibung", heim=seite["heim"], gast=seite["gast"], liga=liga,
                       spieltag=t("spieltag.nummer", n=seite["spieltag"])),
        **_rahmen(k, seite.get("stand")))


def start_html(seite: dict, k: Kontext, foto: str | None = None) -> str:
    pause = seite.get("pause") or {}
    return ENV.get_template("start.html").render(
        seite=seite, aktiv="", foto=foto, seitentitel=t("start.seitentitel"), beschreibung=t("start.beschreibung"),
        pause_datum=F.tag(date.fromisoformat(pause["datum"])) if pause.get("datum") else "–",
        **_rahmen(k, seite.get("stand")))


def hinweis_html(art: str, k: Kontext, stand_iso: str | None = None, aktiv: str = "") -> str:
    """art: folgt (Annahme A8), fehlt (404), daten (Fehler in den Daten)."""
    if art == "folgt":
        titel, text, seitentitel = t("folgt.titel"), t("folgt.text"), t("folgt.seitentitel")
        zurueck = t("folgt.zurueck")
    elif art == "daten":
        titel, text, seitentitel = t("fehler.daten_titel"), t("fehler.daten_text"), t("fehler.seitentitel")
        zurueck = t("fehler.zurueck")
    else:
        titel, text, seitentitel = t("fehler.titel"), t("fehler.text"), t("fehler.seitentitel")
        zurueck = t("fehler.zurueck")
    return ENV.get_template("hinweis.html").render(
        titel=titel, text=text, zurueck=zurueck, seitentitel=seitentitel, beschreibung="", aktiv=aktiv,
        **_rahmen(k, stand_iso))
