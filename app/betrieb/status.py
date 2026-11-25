"""Wöchentliche Statusmail seit 0.23 (docs/09_Betrieb_EMail.md, Abschnitt 4): jeden Montag um 06:00 (F7).

Inhalt aus dem, was ohnehin geschrieben wird: Ereignisprotokoll (Läufe), Alarm-Zustände (Container und Prüfskript),
letzte Messwerte des Servers (server.json), Backups, Laufzeiten, offene Entscheide, Vereine ohne Anzeigenamen.
"""

from __future__ import annotations

import json
import re
import urllib.request
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from . import alarme, laufzeiten, pruefungen

STUNDE = 6
ANLASS = {"kontrolle": "Kontrolllauf", "spiel": "nach dem Spiel", "wiederholung": "Wiederholung"}


SITEMAP = "https://soccer-intelligence.com/sitemap.xml"


def _laden(url: str) -> str:
    with urllib.request.urlopen(url, timeout=20) as r:          # nur lesen, öffentliche Adresse
        return r.read().decode("utf-8", "replace")


def sitemap_zeile(holen=_laden, url: str = SITEMAP) -> str:
    """Seit 0.27 (Wunsch Carsten 25.11.2026): Ist die Sitemap erreichbar und wie viele Seiten nennt sie?
    Die Sitemap entsteht bei jedem Abruf neu aus den Daten; hier wird nur nachgesehen."""
    try:
        index = holen(url)
        teile = re.findall(r"<loc>([^<]+)</loc>", index)
        seiten = sum(len(re.findall(r"<url>", holen(t))) for t in teile)
    except Exception as exc:  # noqa: BLE001 - jede Störung als Hinweis in der Mail
        return f"- Sitemap nicht erreichbar ({type(exc).__name__}). Bitte {url} im Browser prüfen."
    return f"- Website und Sitemap erreichbar: {seiten} Seiten in {len(teile)} Teil-Sitemaps."


def faellig(state: dict, now: datetime) -> bool:
    """Montag ab 06:00, einmal je Kalenderwoche."""
    kw = "{}-{:02d}".format(*now.isocalendar()[:2])
    return now.weekday() == 0 and now.hour >= STUNDE and state.get("letzte_statusmail") != kw


def _ereignisse(base: Path, seit: datetime) -> list[dict]:
    out = []
    try:
        for zeile in (Path(base) / "ereignisse.jsonl").read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(zeile)
            except ValueError:
                continue
            if e.get("zeit") and datetime.fromisoformat(e["zeit"]).replace(tzinfo=None) >= seit:
                out.append(e)
    except OSError:
        pass
    return out


def _mb(n: int) -> str:
    return f"{n / 1_000_000:.1f} MB"


def text(base: Path, data_dir: Path, backup_dir: Path, now: datetime, fehlende_namen: list[str] | None = None,
         website: str | None = None) -> tuple[str, str]:
    """Betreff und Text der Statusmail."""
    base, now = Path(base), now.replace(tzinfo=None, microsecond=0)
    seit = now - timedelta(days=7)
    kw = now.isocalendar()[1]
    ev = _ereignisse(base, seit)
    laeufe = [e for e in ev if e.get("lauf") and e.get("anlass") in ANLASS]
    c_zust = alarme.laden(base / "alarme.json")
    s_zust = alarme.laden(base / "ueberwachung.json")
    aktiv = {**(c_zust.get("aktiv") or {}), **(s_zust.get("aktiv") or {})}
    verlauf = [v for v in (c_zust.get("verlauf") or []) + (s_zust.get("verlauf") or [])
               if datetime.fromisoformat(v["bis"]) >= seit]

    zeilen = [("Alles in Ordnung." if not aktiv else f"{len(aktiv)} offene(r) Alarm(e) – siehe unten."), ""]

    zeilen.append("LÄUFE DER WOCHE")
    if laeufe:
        je = Counter(ANLASS[e["anlass"]] for e in laeufe)
        st = Counter("übernommen" if str(e.get("status", "")).startswith("übernommen") else e.get("status") for e in laeufe)
        zeilen.append("- " + ", ".join(f"{n} {a}" for a, n in je.items()))
        zeilen.append("- Status: " + ", ".join(f"{n} {s}" for s, n in st.items()))
        zeilen.append(f"- Neue Spiele: {sum(e.get('neue_spiele') or 0 for e in laeufe)}, Korrekturen: "
                      f"{sum(e.get('korrekturen') or 0 for e in laeufe)}, Abfragen: "
                      f"{sum(e.get('abfragen') or 0 for e in laeufe)}")
    else:
        zeilen.append("- Keine Läufe im Protokoll (läuft der Container soccer-import?).")
    zeilen.append("")

    zeilen.append("ALARME")
    for key, a in aktiv.items():
        zeilen.append(f"- OFFEN {alarme.STUFE_TEXT.get(a['stufe'], a['stufe'])}: {a['titel']} (seit "
                      f"{datetime.fromisoformat(a['seit']):%d.%m. %H:%M})")
    for v in verlauf:
        zeilen.append(f"- behoben: {v['titel']} ({datetime.fromisoformat(v['seit']):%d.%m. %H:%M} – "
                      f"{datetime.fromisoformat(v['bis']):%d.%m. %H:%M})")
    if not aktiv and not verlauf:
        zeilen.append("- Keine Alarme in dieser Woche.")
    zeilen.append("")

    zeilen.append("SERVER")
    srv = pruefungen._json(base / "server.json")
    if srv:
        w = srv.get("woche") or {}
        zeilen.append(f"- Stand {srv.get('zeit', '–')[:16].replace('T', ' ')}: Festplatte {srv.get('festplatte')} %, "
                      f"Arbeitsspeicher {srv.get('speicher')} %, CPU {srv.get('cpu')} %")
        if w:
            zeilen.append(f"- Höchstwerte der Woche: Festplatte {w.get('festplatte')} %, Arbeitsspeicher "
                          f"{w.get('speicher')} %, CPU {w.get('cpu')} %")
        neustarts = {n: c.get("neustarts") for n, c in (srv.get("container") or {}).items()}
        zeilen.append("- Neustarts der Container (gesamt): " + ", ".join(f"{n} {v}" for n, v in neustarts.items()))
    else:
        zeilen.append("- Keine Messwerte (Prüfskript tools/ueberwachen.py im Zeitplan des Servers eingetragen?).")
    zeilen.append("")

    if website:                                          # seit 0.27: Sitemap-Zeile (vom Dienst übergeben)
        zeilen += ["WEBSITE", website, ""]

    zeilen.append("BACKUPS")
    dateien = sorted(Path(backup_dir).glob("Database-Soccer-Intelligence_*_vor_import.xlsx")) if Path(backup_dir).exists() else []
    if dateien:
        groesse = sum(p.stat().st_size for p in Path(backup_dir).glob("*_vor_import.*"))
        zeilen.append(f"- {len(dateien)} Fassungen der Datenbank, zusammen mit Spielplan und Entscheiden {_mb(groesse)}")
        zeilen.append(f"- älteste: {dateien[0].name[29:39]}, neueste: {dateien[-1].name[29:39]}")
    else:
        zeilen.append("- Noch keine Backups.")
    if now.day <= 7:
        zeilen.append("- Erster Montag im Monat: Bitte die Monatssicherung auf den Laptop laden (Befehl in "
                      "docs/01_Technisches_Setup.md, Abschnitt 6.5).")
    zeilen.append("")

    zeilen.append("LAUFZEITEN")
    reps = pruefungen.berichte(base)
    abo = next((r.get("abo") for r in reps if (r.get("abo") or {}).get("bis")), None)
    for lz in laufzeiten.laden(abo=abo):
        zeilen.append(f"- {lz.name}: bis {lz.bis:%d.%m.%Y} (noch {lz.rest(now.date())} Tage)"
                      + (", verlängert sich automatisch" if lz.automatisch else ""))
    zeilen.append("")

    hinweise = [f"Entscheid offen: {x}" for x in pruefungen.offene_entscheide(base, reps)]
    hinweise += [f"Verein ohne Anzeigenamen der Website: {x}" for x in (fehlende_namen or [])]
    if hinweise:
        zeilen.append("HINWEISE")
        zeilen += [f"- {h}" for h in hinweise[:20]]
        zeilen.append("")
    zeilen.append(f"Dashboard: {alarme.DASHBOARD}")
    betreff = f"Wochenstatus KW {kw}" + ("" if not aktiv else f" – {len(aktiv)} offene Alarme")
    return betreff, "\n".join(zeilen) + "\n"
