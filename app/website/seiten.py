"""HTML der Website aus den Vorlagen (vorlagen/*.html, Jinja2) und den Datensätzen (Codes).

Alle Texte kommen aus der Sprachdatei (texte.py), alle Zahlen und Daten aus format.py. Jinja maskiert jeden Wert
(autoescape), StrictUndefined macht einen fehlenden Wert zum Fehler statt zu einer leeren Stelle. Seit 0.18 drei
Seiten nach den Entwürfen: Startseite (1d), Spieltag (3d), Matchdetail (2i).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
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
        return f"{self.prefix.rstrip('/')}/statisch/{pfad}"


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


def balken_daten(k: dict) -> dict:
    """Balken nach Übergabe 4.2: Länge = Betrag/100 × 50 % der Breite, höchstens 50 %; über 100 % gekappt mit
    gestricheltem Streifen. Farbe: dunkel = stark, hell = leicht, grau = normal, schraffiert = nicht gewertet."""
    wert = k.get("abweichung")
    if wert is None:
        return {"breite": 0, "richtung": "hoch", "klasse": "f-schraffiert", "kappe": False}
    betrag = abs(wert)
    richtung = "hoch" if wert >= 0 else "tief"
    stufe = k.get("stufe")
    if stufe in ("stark", "leicht"):
        klasse = f"f-{stufe}-{richtung}"
    elif stufe == "nicht_gewertet":
        klasse = "f-schraffiert"
    else:
        klasse = "f-normal"
    return {"breite": int(round(min(50.0, betrag / 2))), "richtung": richtung, "klasse": klasse,
            "kappe": betrag > 100}


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
        balken_daten=balken_daten, aufteilung=aufteilung, ligen=W.LIGEN,
        ergebnis=lambda e: F.ergebnis(*e),
        zeitraum=lambda von, bis: F.zeitraum(date.fromisoformat(von), date.fromisoformat(bis)),
        datum_kurz=lambda iso: F.datum_kurz(date.fromisoformat(iso)) if iso else "",
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
    if seite["bewertung"] == "nicht_gewertet":
        return {"label": t("spiel.bewertung"), "wert": "", "richtung": "", "titel": t("spiel.nicht_gewertet"),
                "text": t("spiel.nicht_gewertet_leer_text") if seite["ohne_werte"] else t("spiel.nicht_gewertet_text")}
    if seite["auffaellig"]:
        top = seite["auffaellig"][0]
        return {"label": t("spiel.auffaelligstes"), "wert": F.prozent(top["abweichung"]), "richtung": top["richtung"],
                "titel": t(f"kennzahl.{top['kpi']}.name"), "text": t(f"kennzahl.{top['kpi']}.{top['richtung']}")}
    g = seite["groesste"]
    return {"label": t("spiel.gesamtbild"), "wert": "", "richtung": "", "titel": t("spiel.keine_titel"),
            "text": t("spiel.keine_text", n=seite["anzahl_gewertet"], name=t(f"kennzahl.{g['kpi']}.name"),
                      wert=F.prozent(g["abweichung"])) if g else ""}


def spiel_notizen(seite: dict) -> list[dict]:
    """Hinweisboxen unter dem Scoreboard: Nachholspiel / vorgezogen, gespielt (Q5)."""
    out = []
    if seite["sonderspiel"] == "nachholspiel":
        out.append({"titel": t("spiel.hinweis_nachholspiel_titel"),
                    "text": t("spiel.hinweis_nachholspiel", datum=_zeitpunkt(seite))})
    elif seite["sonderspiel"] == "vorgezogen":
        out.append({"titel": t("spiel.hinweis_vorgezogen_titel"),
                    "text": t("spiel.hinweis_vorgezogen", spieltag=t("spieltag.nummer", n=seite["spieltag"]),
                              datum=_zeitpunkt(seite))})
    if seite["zustand"] == "gespielt":
        out.append({"titel": t("spiel.hinweis_gespielt_titel"), "text": t("spiel.hinweis_gespielt")})
    return out


def spiel_html(seite: dict, k: Kontext) -> str:
    liga = t(f"liga.{seite['liga_key']}")
    if seite["zustand"] == "gespielt":
        wann = t("spiel.endstand", ergebnis=F.ergebnis(*seite["ergebnis"])) if seite["ergebnis"] else \
            t("spiel.ergebnis_folgt")
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
