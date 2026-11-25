"""Suchmaschinen-Angaben der Website (seit 0.21; SEO-Briefing Abschnitte 3, 5, 7 und 8; Konzept 08, Abschnitt 10).

- **Index-Regel:** eine Funktion je Seitenart, die Seite (robots) und Sitemap gemeinsam nutzen, damit beide nie
  auseinanderlaufen. Vor dem Livegang (index_ab leer in app/config/website.toml) ist nichts indexierbar; die Vorschau
  ist ohnehin immer „noindex, nofollow“.
- **Title und Description** der Spielseite je Zustand, Description höchstens 155 Zeichen (zuerst auf eine Kennzahl
  kürzen, dann den Satz zur Signalqualität weglassen); nie leer.
- **JSON-LD** je Seite: Organization + WebSite (Startseite), BreadcrumbList + WebPage bzw. ContactPage. SportsEvent
  bis 0.23 auf indexierbaren Spielseiten, seit 0.24 entfernt (ohne Ort für Google ungültig; Entscheid Carsten 24.11.2026).
"""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass
from datetime import date, datetime
from functools import lru_cache

from core.files import file_key

from . import einstellungen as W
from . import format as F
from .texte import t

MAX_BESCHREIBUNG = 155


# --- Konfiguration (index_ab, seiten_ab_saison) ----------------------------------------------------------------

@dataclass(frozen=True)
class Konfig:
    index_ab: datetime | None = None          # Livegang (Europe/Zurich, ohne Zeitzonenangabe); None = nichts im Index
    seiten_ab_saison: str = "2025/2026"       # ältere Saisons haben (noch) keine Seiten
    index_min_kennzahlen: int = 6             # seit 0.24: so viele der 8 Kennzahlen müssen bewertet sein


@lru_cache(maxsize=4)
def _konfig(pfad: str, schluessel: tuple) -> Konfig:  # noqa: ARG001 - Teil des Cache-Schlüssels
    try:
        daten = tomllib.loads(open(pfad, encoding="utf-8").read())
    except (OSError, tomllib.TOMLDecodeError):
        return Konfig()
    roh = str(daten.get("index_ab", "") or "").strip()
    try:
        index_ab = datetime.fromisoformat(roh) if roh else None
    except ValueError:
        index_ab = None
    return Konfig(index_ab, str(daten.get("seiten_ab_saison", "2025/2026")),
                  int(daten.get("index_min_kennzahlen", 6)))


def konfig() -> Konfig:
    return _konfig(str(W.WEBSITE_KONFIG), file_key(W.WEBSITE_KONFIG))


def saison_hat_seiten(saison: str, k: Konfig | None = None) -> bool:
    return saison >= (k or konfig()).seiten_ab_saison


# --- Index-Regeln (SEO-Briefing 3.1, 3.2) -------------------------------------------------------------------

def spiel_indexierbar(seite: dict, k: Konfig | None = None) -> bool:
    """Spielseite im Index und in der Sitemap, wenn alle drei Bedingungen gelten: im Index-Fenster (Anstoss ab dem
    Livegang und in einem Tab der Spieltag-Seite oder schon gespielt), kein ausschliessender Status und
    genug bewertete Kennzahlen (seit 0.24 mindestens `index_min_kennzahlen` von 8, bis 0.23 eine; Entscheid Carsten
    24.11.2026). „Werte ab …“ ist nie indexierbar."""
    k = k or konfig()
    if k.index_ab is None or not saison_hat_seiten(seite["saison"], k):
        return False
    if datetime.fromisoformat(seite["anstoss_zeit"]) < k.index_ab:
        return False
    if not (seite["zustand"] == "gespielt" or seite.get("im_fenster")):
        return False
    if seite["bewertung"] in ("status", "werte_ab"):
        return False
    return seite["anzahl_gewertet"] >= max(1, k.index_min_kennzahlen)


def archiv_indexierbar(beginn: date | None, k: Konfig | None = None) -> bool:
    """Archivseite: indexierbar, wenn der Spieltag nach dem Livegang begonnen hat (unabhängig von einzelnen Spielen)."""
    k = k or konfig()
    return k.index_ab is not None and beginn is not None and beginn >= k.index_ab.date()


# --- Title und Description ------------------------------------------------------------------------------------

def saison_kurz(saison: str) -> str:
    """„2025/2026“ → „2025/26“"""
    a, b = saison.split("/")
    return f"{a}/{b[-2:]}"


def spiel_titel(seite: dict, heim: str, gast: str, lang: str) -> str:
    """DE „VfB Stuttgart – Bayern München · Bundesliga, 13. Spieltag 2025/26 | Soccer Intelligence“,
    EN „VfB Stuttgart vs Bayern Munich · Bundesliga, Matchday 13 2025/26 | Soccer Intelligence“ (Beschluss 19.11.)."""
    return t("seo.spiel_titel", lang, heim=heim, gast=gast, liga=t(f"liga.{seite['liga_key']}", lang),
             n=seite["spieltag"], saison=saison_kurz(seite["saison"]))


def _kennzahlen(namen: list[str], lang: str) -> str:
    if len(namen) <= 1:
        return "".join(namen)
    return t("seo.und", lang, a=namen[0], b=namen[1])


def spiel_beschreibung(seite: dict, heim: str, gast: str, lang: str) -> str:
    """Description je Zustand (SEO-Briefing 7), höchstens 155 Zeichen, nie leer."""
    liga = t(f"liga.{seite['liga_key']}", lang)
    spieltag = t("spieltag.nummer", lang, n=seite["spieltag"])
    datum = F.datum_voll(date.fromisoformat(seite["datum"]), lang)
    werte = dict(heim=heim, gast=gast, liga=liga, spieltag=spieltag, n=seite["spieltag"], datum=datum)
    bewertung = seite["bewertung"]
    if seite.get("ansicht") == "auswertung" and bewertung != "status":   # seit 0.25 (Release_08, Abschnitt 12)
        return _kuerzen(t("seo.spiel_auswertung", lang, ergebnis=F.ergebnis(*seite["ergebnis"]), **werte))
    if bewertung == "status":
        if seite.get("status") == "verschoben":
            return _kuerzen(t("seo.spiel_verschoben", lang, **werte))
        return _kuerzen(t("seo.spiel_status", lang, status=t(f"chip.{seite['status']}", lang), **werte))
    if bewertung == "werte_ab":
        return _kuerzen(t("seo.spiel_werte_ab", lang, **werte))
    if bewertung == "zu_wenig_daten":
        return _kuerzen(t("seo.spiel_zu_wenig_daten", lang, **werte))
    sonder = seite.get("sonderspiel")
    kopf = (t("seo.spiel_kopf_sonder", lang, zustand=t(f"seo.zustand_{sonder}", lang), **werte) if sonder
            else t("seo.spiel_kopf", lang, **werte))
    if bewertung != "auffaellig":
        satz = t("seo.spiel_keine_sonder" if sonder else "seo.spiel_keine", lang)
        return _kuerzen(f"{kopf} {satz}")
    namen = [t(f"kennzahl.{k['kpi']}.name", lang) for k in seite["auffaellig"][:2]]
    stufe = t(f"seo.stufe_{seite['auffaellig'][0]['stufe']}", lang)
    for n_kpi, mit_stufe in ((2, True), (1, True), (1, False)):
        teile = [kopf, t("seo.spiel_auffaellig", lang, kennzahlen=_kennzahlen(namen[:n_kpi], lang))]
        if mit_stufe and not sonder:
            teile.append(t("seo.spiel_signal", lang, stufe=stufe))
        text = " ".join(teile)
        if len(text) <= MAX_BESCHREIBUNG:
            return text
    return _kuerzen(text)


def _kuerzen(text: str) -> str:
    """Notbremse: über 155 Zeichen am letzten Wort vor der Grenze kürzen (kommt bei sehr langen Vereinsnamen vor)."""
    if len(text) <= MAX_BESCHREIBUNG:
        return text
    return text[:MAX_BESCHREIBUNG - 1].rsplit(" ", 1)[0].rstrip(",.:;–") + "…"


# --- JSON-LD (SEO-Briefing 8) -----------------------------------------------------------------------------------

def _org() -> dict:
    return {"@type": "Organization", "@id": f"{W.DOMAIN}/#org", "name": "Soccer Intelligence", "url": f"{W.DOMAIN}/"}


def breadcrumbs(punkte: list[tuple[str, str]]) -> dict:
    """[(Name, absolute Adresse), …] → BreadcrumbList"""
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": name, "item": url} for i, (name, url) in enumerate(punkte, 1)]}


def webseite(url: str, name: str, lang: str, art: str = "WebPage") -> dict:
    return {"@type": art, "@id": url, "url": url, "name": name, "inLanguage": W.IN_LANGUAGE[lang],
            "isPartOf": {"@id": f"{W.DOMAIN}/#website"}}


def start_jsonld(url: str, lang: str) -> list[dict]:
    return [_org(), {"@type": "WebSite", "@id": f"{W.DOMAIN}/#website", "name": "Soccer Intelligence", "url": url,
                     "inLanguage": W.IN_LANGUAGE[lang], "publisher": {"@id": f"{W.DOMAIN}/#org"}}]


def als_skript(teile: list[dict]) -> str:
    """JSON-LD als Text für <script type="application/ld+json"> („</“ entschärft)."""
    daten = {"@context": "https://schema.org", "@graph": [x for x in teile if x]}
    return json.dumps(daten, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
