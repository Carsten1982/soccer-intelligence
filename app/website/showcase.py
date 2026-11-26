"""Showcase-Seiten (seit 0.30; Release_15 des Design-Chats, Entwürfe Showcase_G*, Design 575; docs/08, Abschnitt 12).

Vier Seiten über das Projekt, nicht Teil der Spiel-Plattform: /showcase, /showcase/project, /showcase/ki-automation
und /showcase/ki-automation/data (Dashboard „Datenmonitoring“). Nur Desktop, nie im Index, keine Messung. Englisch ist
vorbereitet (/en/showcase/…), aber erst nach der Übersetzungsprüfung freigeschaltet (Entscheid Carsten 26.11.2026).

Das Dashboard liest die Werte serverseitig aus dem Backend (Entscheid Carsten 26.11.2026, keine öffentliche
Schnittstelle) und zeigt nur zusammengefasste Angaben – nie Container- oder Servernamen, Pfade oder Fehlertexte:
- Datenbank und Datenprüfung aus dem geladenen Bestand (wie das Dashboard „Datenqualität“),
- Läufe aus dem Ereignisprotokoll, Alarme aus alarme.json/ueberwachung.json, Server aus server.json (Prüfskript),
- Tagesverlauf der Prüfung und Backups aus kennzahlen.json (Import-Dienst, täglich, betrieb/kennzahlen.py),
- Testfälle und letztes Release aus release.json (Einspiel-Skript).
Fehlt eine Quelle, steht ein kurzer Hinweis statt einer Zahl (leere Zustände, Entscheid Carsten 26.11.2026).
"""

from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta
from pathlib import Path

from core import settings
from core.issues import FEHLER, HINWEIS, WARNUNG

from . import einstellungen as W
from .texte import t

SEITEN = ("start", "projekt", "ki", "daten")
PFADE = {"de": {"start": "/showcase", "projekt": "/showcase/project", "ki": "/showcase/ki-automation",
                "daten": "/showcase/ki-automation/data"},
         "en": {"start": "/en/showcase", "projekt": "/en/showcase/project", "ki": "/en/showcase/ai-automation",
                "daten": "/en/showcase/ai-automation/data"}}
SPRACHEN_FREI = ("de",)              # Englisch erst nach der Übersetzungsprüfung (Entscheid Carsten 26.11.2026)
REITER = {"start": "start", "projekt": "projekt", "ki": "ki", "daten": "ki"}
STATUS = {"s1": "live", "s2": "dev", "s3": "dev", "s4": "dev"}   # nur das Datenmonitoring ist im Betrieb (26.11.2026)
FOTO = "showcase-portrait.webp"                                   # nur auf dem Server (website-bilder/), nie in Git
VORSCHAU_BILD = "showcase-vorschau.jpg"                           # Linkvorschau 1200 × 630, ebenfalls nur auf dem Server
LIGEN = ("Bundesliga", "Premier League", "Serie A", "LaLiga")     # Reihenfolge wie im Entwurf
RING = ("#C6F26B", "#7CCB1F", "#2E8B2A", "#0B3D2E")
ANLASS = ("kontrolle", "spiel", "wiederholung")
SERVER_ALT = timedelta(minutes=10)    # server.json älter: Werte gelten als nicht verfügbar
BACKUP_AKTUELL = timedelta(days=2)


def erkennen(rest: str) -> tuple[str, str] | None:
    """Adresse → (Seite, Sprache) oder None. Mit oder ohne Schrägstrich am Ende; nur freigeschaltete Sprachen."""
    pfad = rest.rstrip("/") or "/"
    for lang in SPRACHEN_FREI:
        for seite, p in PFADE[lang].items():
            if pfad == p:
                return seite, lang
    return None


def url(prefix: str, seite: str, lang: str = "de") -> str:
    return prefix.rstrip("/") + PFADE[lang][seite]


# --- Formate (Briefing: Schweizer Tausenderzeichen ’, Englisch Komma; 24 Stunden) ---------------------------------

def zahl(n: int | None, lang: str) -> str:
    if n is None:
        return "–"
    return f"{n:,}".replace(",", "’" if lang == "de" else ",")


def prozent(p: float | None, lang: str, stellen: int = 1) -> str:
    if p is None:
        return "–"
    text = f"{p:.{stellen}f}"
    return text.replace(".", ",") + " %" if lang == "de" else text + "%"


TAGE = {"de": ("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"), "en": ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")}
MONATE = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def datum(d: date, lang: str, wochentag: bool = False) -> str:
    text = f"{d:%d.%m.%Y}" if lang == "de" else f"{d.day} {MONATE[d.month - 1]} {d.year}"
    return f"{TAGE[lang][d.weekday()]} {text}" if wochentag else text


def _json(p: Path):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


# --- Seite „Projekt“: Zahlen aus einer Quelle (dieselben wie im Dashboard) ---------------------------------------

def version() -> str:
    """„0.30“ aus der Versionsangabe der Plattform (core/settings.APP_VERSION), nie von Hand gepflegt."""
    return settings.APP_VERSION.split(" ")[0]


def spiele(daten) -> dict[str, int] | None:
    """Spiele in der Datenbank je Liga (Reihenfolge wie im Entwurf); None, wenn die Datenbank nicht lesbar ist."""
    try:
        ligen = daten.bestand().db.leagues
    except Exception:  # noqa: BLE001 - Showcase zeigt dann „–“
        return None
    return {name: len(ligen[name]) for name in LIGEN if name in ligen} or None


def projekt(daten, lang: str) -> dict:
    from . import methodik as MT
    je = spiele(daten)
    try:
        m = MT.daten(lang)
        kombinationen, ligen = m["kombinationen"], m["ligen_zahl"]
    except Exception:  # noqa: BLE001
        kombinationen, ligen = None, len(LIGEN)
    return {"version": version(), "spiele": zahl(sum(je.values()) if je else None, lang),
            "ligen": ligen, "kombinationen": kombinationen if kombinationen is not None else "–"}


# --- Dashboard „Datenmonitoring“ ---------------------------------------------------------------------------------

def _laeufe(import_dir: Path, jetzt: datetime, lang: str) -> tuple[list[dict], str]:
    """Die letzten fünf Läufe (Datum, Zeit, Anlass, Ergebnis) und die Zeile „Diese Woche: …“."""
    ev = []
    try:
        for zeile in (import_dir / "ereignisse.jsonl").read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(zeile)
            except ValueError:
                continue
            if e.get("lauf") and e.get("anlass") in ANLASS and e.get("zeit"):
                ev.append(e)
    except OSError:
        pass
    ev.sort(key=lambda e: e["zeit"], reverse=True)

    def art(status) -> str:
        s = str(status or "")
        return "ok" if s.startswith("übernommen") else ("warte" if s.startswith("wartet") else "fehler")

    zeilen = []
    for e in ev[:5]:
        z = datetime.fromisoformat(e["zeit"]).replace(tzinfo=None)
        a = art(e.get("status"))
        zeilen.append({"datum": datum(z.date(), lang, True), "zeit": f"{z:%H:%M}", "art": a,
                       "anlass": t(f"showcase.daten.anlass_{e['anlass']}", lang),
                       "ergebnis": t(f"showcase.daten.ergebnis_{a}", lang)})
    woche = [e for e in ev if datetime.fromisoformat(e["zeit"]).replace(tzinfo=None) >= jetzt - timedelta(days=7)]
    ok = sum(1 for e in woche if art(e.get("status")) == "ok")
    if not woche:
        text = t("showcase.daten.woche_keine", lang)
    elif ok == len(woche):
        text = t("showcase.daten.woche_alle", lang, n=len(woche))
    else:
        text = t("showcase.daten.woche_teil", lang, n=len(woche), ok=ok)
    return zeilen, text


def naechster_lauf(daten, import_dir: Path, jetzt: datetime) -> datetime:
    """Nächster geplanter Lauf: nach dem Spiel (Anpfiff + 2¼ h), Wiederholung oder Kontrolllauf 04:00 (06, 10.2)."""
    from importer import einstellungen as E
    from importer import laufplan
    kandidaten = [datetime.combine(jetzt.date() + timedelta(days=0 if jetzt.hour < E.RUN_HOUR else 1), time(E.RUN_HOUR))]
    fx = Path(settings.FIXTURES_FILE)
    if fx.exists():
        try:
            for tag in (jetzt.date(), jetzt.date() + timedelta(days=1)):
                kandidaten += [z for z in laufplan.plan(fx, tag) if z > jetzt]
        except Exception:  # noqa: BLE001 - Spielplan nicht lesbar: nur der Kontrolllauf
            pass
    w = ((_json(import_dir / "zustand.json") or {}).get("wiederholung") or {}).get("um")
    if w and datetime.fromisoformat(w) > jetzt:
        kandidaten.append(datetime.fromisoformat(w))
    return min(kandidaten)


def _wann(z: datetime, jetzt: datetime, lang: str) -> str:
    if z.date() == jetzt.date():
        return t("showcase.daten.heute", lang, zeit=f"{z:%H:%M}")
    if z.date() == jetzt.date() + timedelta(days=1):
        return t("showcase.daten.morgen", lang, zeit=f"{z:%H:%M}")
    return f"{datum(z.date(), lang, True)} {z:%H:%M}"


def _verlauf(kz: dict, lang: str) -> dict:
    """Hinweise im Verlauf (letzte 7 Tage aus kennzahlen.json): Punkte für die Grafik oder ein Hinweis „ab …“."""
    punkte = [v for v in (kz.get("verlauf") or []) if isinstance(v.get("hinweise"), int)][-7:]
    if len(punkte) < 2:
        ab = punkte[0]["tag"] if punkte else None
        return {"punkte": [], "hinweis": t("showcase.daten.verlauf_ab", lang,
                                           datum=datum(date.fromisoformat(ab), lang) if ab else "–")}
    werte = [p["hinweise"] for p in punkte]
    lo, hi = min(werte), max(werte)
    breite, x0, x1, y0, y1 = 420, 14.0, 406.0, 22.0, 96.0
    out = []
    for i, p in enumerate(punkte):
        x = x0 + (x1 - x0) * i / (len(punkte) - 1)
        y = (y0 + y1) / 2 if hi == lo else y1 - (p["hinweise"] - lo) / (hi - lo) * (y1 - y0)
        d = date.fromisoformat(p["tag"])
        out.append({"x": f"{x:.1f}", "y": f"{y:.1f}", "label": f"{d:%d.%m.}" if lang == "de" else f"{d.day} {MONATE[d.month - 1]}",
                    "wert": p["hinweise"]})
    return {"punkte": out, "linie": " ".join(f"{p['x']},{p['y']}" for p in out), "breite": breite,
            "hinweis": t("showcase.daten.verlauf_tage", lang, n=len(out))}


def _server(import_dir: Path, kz: dict, jetzt: datetime, lang: str) -> dict:
    """Website & Server: acht zusammengefasste Werte. Ohne frische Messung des Prüfskripts: „nicht verfügbar“."""
    from betrieb import alarme
    tx = lambda k, **w: t(f"showcase.daten.{k}", lang, **w)   # noqa: E731
    srv = _json(import_dir / "server.json") or {}
    zeit = datetime.fromisoformat(srv["zeit"]).replace(tzinfo=None) if srv.get("zeit") else None
    frisch = zeit is not None and jetzt - zeit <= SERVER_ALT
    out = {"frisch": frisch, "stand": tx("stand_server", zeit=f"{datum(zeit.date(), lang)} · {zeit:%H:%M}") if frisch
           else tx("nicht_verfuegbar")}
    na = tx("na")
    web = srv.get("website") or {}
    seite = web.get("/de/", web.get("/"))
    out["website"] = (tx("erreichbar") if seite == 200 else tx("nicht_erreichbar")) if frisch else na
    karte = web.get("/sitemap.xml")
    out["sitemap"] = ((tx("erreichbar") if karte == 200 else tx("nicht_erreichbar")) if karte is not None else na) if frisch else na
    if frisch and srv.get("festplatte") is not None:
        hoch = srv.get("festplatte", 0) >= 85 or (srv.get("speicher") or 0) >= 90 or (srv.get("cpu") or 0) >= 90
        out["last"] = tx("erhoeht") if hoch else tx("normal")
    else:
        out["last"] = na
    cont = [c for c in (srv.get("container") or {}).values() if c.get("status") != "fehlt"]
    out["dienste"] = (tx("alle_laufen") if cont and all(c.get("status") == "running" for c in cont)
                      else tx("eingeschraenkt")) if frisch and cont else na
    neu = (kz.get("backups") or {}).get("neueste")
    out["backup"] = (tx("aktuell") if jetzt.date() - date.fromisoformat(neu) <= BACKUP_AKTUELL else tx("veraltet")) if neu else na
    # API-Kontingent heute (eigene Tagesgrenze des Import-Dienstes)
    from importer import einstellungen as E
    from importer.client import used_today
    try:
        anteil = min(100, round(100 * used_today(import_dir / "roh", jetzt.strftime("%Y-%m-%d")) / E.DAILY_LIMIT))
    except Exception:  # noqa: BLE001
        anteil = None
    out["kontingent"] = na if anteil is None else (tx("gruener_bereich") if anteil < 80 else tx("erhoeht") if anteil < 100
                                                   else tx("ausgeschoepft"))
    out["kontingent_text"] = "" if anteil is None else tx("kontingent_anteil", p=anteil)
    out["kontingent_stufe"] = 0 if anteil is None else min(100, 5 * round(anteil / 5))
    # Alarme (Daten und Server)
    aktiv, woche = 0, 0
    for name in ("alarme.json", "ueberwachung.json"):
        z = alarme.laden(import_dir / name)
        aktiv += len(z.get("aktiv") or {})
        woche += sum(1 for v in z.get("verlauf") or []
                     if datetime.fromisoformat(v["bis"]).replace(tzinfo=None) >= jetzt - timedelta(days=7))
    out["alarme"] = tx("keine") if aktiv == 0 else str(aktiv)
    out["alarme_woche"] = tx("alarme_woche", n=aktiv + woche)
    # Verfügbarkeit der Website (30 Tage, Prüfung jede Minute; Aufzeichnung seit 0.30)
    tage = sorted((srv.get("verfuegbarkeit") or {}).items())[-30:]
    n = sum(v[0] for _, v in tage)
    ok = sum(v[1] for _, v in tage)
    out["verfuegbarkeit"] = prozent(100 * ok / n, lang) if n else na
    out["verfuegbarkeit_text"] = (tx("verfuegbar_seit", datum=datum(date.fromisoformat(tage[0][0]), lang))
                                  if n and len(tage) < 30 else tx("verfuegbar_30") if n else tx("verlauf_folgt"))
    return out


def _status(import_dir: Path) -> str:
    """gruen / warnung / kritisch aus den offenen Alarmen (Daten und Server)."""
    from betrieb import alarme
    stufen = [a.get("stufe") for name in ("alarme.json", "ueberwachung.json")
              for a in (alarme.laden(import_dir / name).get("aktiv") or {}).values()]
    return "kritisch" if "kritisch" in stufen else ("warnung" if stufen else "gruen")


def monitoring(daten, jetzt: datetime, lang: str) -> dict:
    """Alle Werte des Dashboards „Datenmonitoring“ (zusammengefasst, je Sprache formatiert)."""
    from importer.einstellungen import IMPORT_DIR
    import_dir = Path(getattr(daten, "import_dir", None) or IMPORT_DIR)
    tx = lambda k, **w: t(f"showcase.daten.{k}", lang, **w)   # noqa: E731
    kz = _json(import_dir / "kennzahlen.json") or {}
    m: dict = {"stand": tx("stand", zeit=f"{datum(jetzt.date(), lang)} · {jetzt:%H:%M}"), "status": _status(import_dir)}
    m["status_text"] = tx(f"status_{m['status']}")

    je = spiele(daten)
    gesamt = sum(je.values()) if je else None
    m["spiele"] = zahl(gesamt, lang)
    m["ligen"] = len(je) if je else "–"
    umfang = 2 * 3.14159265 * 70
    ring, start = [], 0.0
    for i, name in enumerate(LIGEN):
        n = (je or {}).get(name)
        teil = umfang * n / gesamt if n and gesamt else 0.0
        ring.append({"liga": name, "farbe": RING[i], "text": zahl(n, lang), "strich": f"{max(teil - 2, 0):.2f}",
                     "rest": f"{umfang - max(teil - 2, 0):.2f}", "versatz": f"{-start:.2f}"})
        start += teil
    m["ring"] = ring

    try:
        b = daten.bestand()
        db_zeit = b.db.file_modified
        m["pruefung"] = {k: b.db.count(s) + b.fx.count(s) for k, s in
                         (("fehler", FEHLER), ("warnungen", WARNUNG), ("hinweise", HINWEIS))}
    except Exception:  # noqa: BLE001
        db_zeit, m["pruefung"] = None, {"fehler": "–", "warnungen": "–", "hinweise": "–"}
    if isinstance(m["pruefung"]["hinweise"], int):
        m["pruefung"] = {k: zahl(v, lang) for k, v in m["pruefung"].items()}
    db_zeit = db_zeit.replace(tzinfo=None) if db_zeit else None
    m["datenstand"] = {"datum": datum(db_zeit.date(), lang) if db_zeit else "–",
                       "zeit": tx("uhr", zeit=f"{db_zeit:%H:%M}") if db_zeit else ""}
    imp = daten.zeitpunkt().stand
    m["import"] = {"datum": datum(imp.date(), lang) if imp else "–", "zeit": tx("uhr", zeit=f"{imp:%H:%M}") if imp else ""}

    rel = _json(import_dir / "release.json") or {}
    if isinstance(rel.get("tests"), int):
        m["tests"] = {"vorhanden": True, "anzahl": zahl(rel["tests"], lang),
                      "text": tx("release", version=rel.get("version", "–"))}
    else:
        m["tests"] = {"vorhanden": False, "anzahl": "–", "text": tx("release_folgt")}

    m["laeufe"], m["woche"] = _laeufe(import_dir, jetzt, lang)
    m["naechster"] = tx("naechster", wann=_wann(naechster_lauf(daten, import_dir, jetzt), jetzt, lang))
    m["verlauf"] = _verlauf(kz, lang)
    m["server"] = _server(import_dir, kz, jetzt, lang)
    return m


# --- Seiten erzeugen ------------------------------------------------------------------------------------------------

def html(seite: str, lang: str, k, daten, jetzt: datetime) -> str:
    """HTML einer Showcase-Seite. k: Kontext der Website (Präfix, Vorschau); daten: geladener Bestand."""
    from .seiten import ENV, _werte
    k = k.mit(lang=lang, ziel=None)
    foto = W.BILDER / FOTO
    bild = W.BILDER / VORSCHAU_BILD
    werte = {
        **_werte(k),
        "s": lambda key, **w: t(f"showcase.{seite}.{key}", lang, **w),
        "k": lambda key, **w: t(f"showcase.kopf.{key}", lang, **w),
        "sc_url": lambda ziel: url(k.prefix, ziel, lang),
        "reiter": REITER[seite],
        "absolut": W.DOMAIN + PFADE[lang][seite],
        "og_locale": W.OG_LOCALE[lang],
        "foto": k.url(f"/bilder/{FOTO}") if foto.is_file() else None,
        "vorschau_bild": W.DOMAIN + f"/bilder/{VORSCHAU_BILD}" if bild.is_file() else None,
        "status": STATUS,
        "chip_text": lambda key: ("● " if STATUS[key] == "live" else "○ ")
        + t(f"showcase.ki.{'st_live' if STATUS[key] == 'live' else 'st_dev'}", lang),
    }
    if seite == "projekt":
        werte["sp"] = projekt(daten, lang)
    if seite == "daten":
        werte["m"] = monitoring(daten, jetzt, lang)
    return ENV.get_template(f"showcase/{seite}.html").render(**werte)
