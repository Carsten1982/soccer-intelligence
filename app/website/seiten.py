"""HTML der Website aus den Vorlagen (vorlagen/*.html, Jinja2) und den Datensätzen (Codes).

Alle Texte kommen aus der Sprachdatei (texte.py), alle Zahlen und Daten aus format.py. Jinja maskiert jeden Wert
(autoescape), StrictUndefined macht einen fehlenden Wert zum Fehler statt zu einer leeren Stelle.
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


def termin(s: dict) -> str:
    """Zeile unter der Paarung (Konzept 5.5)."""
    d = date.fromisoformat(s["datum"])
    if s["art"] == "status" and s["status"] == "verschoben":
        return t("termin.termin_offen")
    if s["termin"] == "vorlaeufig":
        tage = F.wochenende(d)
        anfang = t("termin.wochenende", tage=tage) if tage else F.tag(d)
        return f"{anfang} · {t('termin.termin_offen')}"
    if s["termin"] == "zeit_offen":
        return f"{F.tag(d)} · {t('termin.zeit_offen')}"
    return f"{F.tag(d)} · {s['anstoss']}" if s["anstoss"] else F.tag(d)


def _env() -> Environment:
    env = Environment(loader=FileSystemLoader(str(W.VORLAGEN)), autoescape=select_autoescape(["html"]),
                      undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    env.globals.update(
        t=t, tn=tn, termin=termin, standard_liga=W.STANDARD_LIGA,
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


def spieltag_html(seite: dict, k: Kontext) -> str:
    liga = t(f"liga.{seite['liga_key']}")
    pause = seite.get("pause") or {}
    return ENV.get_template("spieltag.html").render(
        seite=seite, aktiv="spieltag", seitentitel=t("spieltag.seitentitel", liga=liga),
        beschreibung=t("spieltag.beschreibung", liga=liga),
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
