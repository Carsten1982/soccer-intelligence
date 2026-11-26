#!/usr/bin/env python3
"""Server-Überwachung seit 0.23 (docs/09_Betrieb_EMail.md, Abschnitt 3.2). Läuft jede Minute über den Zeitplan des
Servers (cron, Entscheid Carsten 20.11.2026, F1) direkt auf dem Server – nicht im Container, damit eine Meldung auch
kommt, wenn ein Container ausgefallen ist.

Es liest nur: /proc (Arbeitsspeicher, CPU), die Belegung der Festplatte, `docker inspect` unserer vier Container,
einen Abruf der eigenen Adressen und das Lebenszeichen des Import-Dienstes. Es startet, stoppt oder ändert nichts
(Schutzregeln 01, Abschnitt 5). Zugangsdaten für den Mailversand aus .env (nur SI_SMTP_*, SI_ALARM_AN).

Schreibt: import/server.json (letzte Messwerte, Höchstwerte der Woche), import/ueberwachung.json (Zustand der Alarme,
Dauer über der Schwelle) und Zeilen ins Ereignisprotokoll import/ereignisse.jsonl.

Aufruf:  python3 tools/ueberwachen.py                     eine Prüfung (Zeitplan: jede Minute)
         python3 tools/ueberwachen.py --test [--release X]  Testmail über diesen Weg (M9)
Nur Standardbibliothek (Python 3.8 oder neuer).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

PROJEKT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJEKT / "app"))

from betrieb import alarme, mail  # noqa: E402

# Seit 0.27 (Livegang): die öffentliche Website statt der Platzhalterseite (die darf später abgeschaltet werden)
CONTAINER = ("football-dashboard", "soccer-import", "soccer-vorschau", "soccer-website")
URL = "https://soccer-intelligence.com"
ADRESSEN = {"/de/": (200,), "/sitemap.xml": (200,), "/dashboard/": (200,), "/vorschau/": (200, 401)}   # seit 0.27 Website und Sitemap
# Übergang zum Livegang (0.27): Solange der Container soccer-website noch nie angelegt wurde ("fehlt"), ist die Website
# noch nicht live – dann wird wie bis 0.26 geprüft (Platzhalterseite unter /, ohne Website-Container). So kommen beim
# Einspielen von 0.27 keine Alarme, bevor der Livegang-Befehl gelaufen ist. Ein gestoppter Container ist nicht "fehlt".
WEBSITE = "soccer-website"
ADRESSEN_VOR_LIVEGANG = {"/": (200,), "/dashboard/": (200,), "/vorschau/": (200, 401)}
ENV_SCHLUESSEL = ("SI_SMTP_HOST", "SI_SMTP_PORT", "SI_SMTP_USER", "SI_SMTP_PASSWORT", "SI_ALARM_AN")

# Schwellen (Entscheid Carsten 20.11.2026, M4): (Prozent, Minuten)
FESTPLATTE = {"warnung": 85, "kritisch": 95}
SPEICHER = {"warnung": (90, 15), "kritisch": (95, 5)}
CPU = {"warnung": (90, 30)}
NEUSTARTS = (3, 10)                 # mehr als 3 Neustarts in 10 Minuten
NICHT_VERFUEGBAR = 5                # Minuten
WEBSITE_AUS = 5                     # Minuten
LEBENSZEICHEN = 30                  # Minuten (ein langer Kontrolllauf am Montag erneuert es nicht)


def env_lesen(datei: Path) -> dict:
    """Nur die Einträge für den Mailversand aus .env (keine anderen Werte im Speicher)."""
    out = {}
    try:
        for zeile in Path(datei).read_text(encoding="utf-8").splitlines():
            if "=" not in zeile or zeile.lstrip().startswith("#"):
                continue
            k, v = zeile.split("=", 1)
            k, v = k.strip(), v.strip()
            if k in ENV_SCHLUESSEL:
                out[k] = v[1:-1] if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"" else v
    except OSError:
        pass
    return out


# --- Messen ----------------------------------------------------------------------------------------------------------

def speicher(proc: Path = Path("/proc")) -> float:
    werte = {}
    for zeile in (proc / "meminfo").read_text().splitlines():
        teile = zeile.split()
        if len(teile) >= 2:
            werte[teile[0].rstrip(":")] = int(teile[1])
    return round(100 * (1 - werte["MemAvailable"] / werte["MemTotal"]), 1)


def cpu_zaehler(proc: Path = Path("/proc")) -> tuple[int, int]:
    """(gesamt, leerlauf) aus der ersten Zeile von /proc/stat."""
    zahlen = [int(x) for x in (proc / "stat").read_text().splitlines()[0].split()[1:]]
    return sum(zahlen), zahlen[3] + (zahlen[4] if len(zahlen) > 4 else 0)


def cpu_prozent(vorher: list | None, jetzt: tuple[int, int]) -> float | None:
    if not vorher:
        return None
    gesamt, leer = jetzt[0] - vorher[0], jetzt[1] - vorher[1]
    return round(100 * (1 - leer / gesamt), 1) if gesamt > 0 else None


def festplatte(pfad: Path = PROJEKT) -> float:
    u = shutil.disk_usage(pfad)
    return round(100 * u.used / u.total, 1)


def docker_inspect(name: str) -> dict:
    """Status, Neustarts und Health eines Containers (nur lesen)."""
    try:
        aus = subprocess.run(["docker", "inspect", "-f",
                              "{{.State.Status}}|{{.RestartCount}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}",
                              name], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return {"status": "unbekannt", "neustarts": None, "health": ""}
    if aus.returncode != 0:
        return {"status": "fehlt", "neustarts": None, "health": ""}
    status, neustarts, health = (aus.stdout.strip().split("|") + ["", "", ""])[:3]
    return {"status": status, "neustarts": int(neustarts) if neustarts.isdigit() else None, "health": health}


def http_status(url: str) -> int | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="GET"), timeout=15) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:  # noqa: BLE001 - nicht erreichbar
        return None


# --- Auswerten -------------------------------------------------------------------------------------------------------

def _seit(zustand: dict, name: str, bedingung: bool, now: datetime) -> float:
    """Minuten, seit die Bedingung ununterbrochen gilt (0, wenn sie nicht gilt)."""
    seit = zustand.setdefault("seit", {})
    if not bedingung:
        seit.pop(name, None)
        return 0.0
    start = datetime.fromisoformat(seit.setdefault(name, now.isoformat()))
    return (now - start).total_seconds() / 60


def auswerten(m: dict, zustand: dict, now: datetime) -> list[alarme.Befund]:
    """Messwerte m -> Befunde (Schwellen M4). zustand merkt sich Dauer und Neustart-Verlauf."""
    out = []
    fp = m["festplatte"]
    if fp > FESTPLATTE["kritisch"]:
        out.append(alarme.Befund("festplatte", "kritisch", f"Festplatte zu {fp} % belegt", _fp_text(fp)))
    elif fp > FESTPLATTE["warnung"]:
        out.append(alarme.Befund("festplatte", "warnung", f"Festplatte zu {fp} % belegt", _fp_text(fp)))

    sp = m["speicher"]
    krit = _seit(zustand, "speicher95", sp > SPEICHER["kritisch"][0], now) >= SPEICHER["kritisch"][1]
    warn = _seit(zustand, "speicher90", sp > SPEICHER["warnung"][0], now) >= SPEICHER["warnung"][1]
    if krit or warn:
        out.append(alarme.Befund("speicher", "kritisch" if krit else "warnung", f"Arbeitsspeicher zu {sp} % belegt",
                                 f"Der Arbeitsspeicher ist seit einiger Zeit zu über {90 if warn and not krit else 95} % "
                                 "belegt. Welcher Container viel braucht: docker stats --no-stream"))

    c = m.get("cpu")
    if c is not None and _seit(zustand, "cpu90", c > CPU["warnung"][0], now) >= CPU["warnung"][1]:
        out.append(alarme.Befund("cpu", "warnung", f"CPU seit über 30 Minuten über 90 % ({c} %)",
                                 "Die CPU ist dauerhaft ausgelastet. Welcher Container viel braucht: docker stats --no-stream"))

    verlauf = zustand.setdefault("neustarts", {})
    for name, info in m["container"].items():
        if name == WEBSITE and info["status"] == "fehlt":
            continue                                    # vor dem Livegang (Übergang 0.27)
        punkte = [p for p in verlauf.get(name, [])
                  if now - datetime.fromisoformat(p[0]) <= timedelta(minutes=NEUSTARTS[1])]
        if info["neustarts"] is not None:
            punkte.append([now.isoformat(), info["neustarts"]])
        verlauf[name] = punkte
        anstieg = (punkte[-1][1] - punkte[0][1]) if len(punkte) >= 2 else 0
        weg = info["status"] != "running" or info["health"] == "unhealthy"
        if _seit(zustand, f"weg:{name}", weg, now) >= NICHT_VERFUEGBAR:
            out.append(alarme.Befund(f"container:{name}", "kritisch", f"Container {name} nicht verfügbar",
                                     f"Der Container {name} ist seit über {NICHT_VERFUEGBAR} Minuten nicht verfügbar "
                                     f"(Status: {info['status']} {info['health']}).\nLetzte Meldungen: docker logs "
                                     f"{name} --tail 50\nNeu starten (nur unser Container): cd /docker/football-dashboard "
                                     f"&& docker compose up -d {name}"))
        elif anstieg > NEUSTARTS[0]:
            out.append(alarme.Befund(f"container:{name}", "warnung", f"Container {name} startet immer wieder neu",
                                     f"{anstieg} Neustarts in {NEUSTARTS[1]} Minuten. Letzte Meldungen: docker logs "
                                     f"{name} --tail 50"))

    erwartet = {**ADRESSEN, **ADRESSEN_VOR_LIVEGANG}
    falsch = {a: s for a, s in m["website"].items() if s not in erwartet[a]}
    if _seit(zustand, "website", bool(falsch), now) >= WEBSITE_AUS:
        out.append(alarme.Befund("website", "kritisch", "Website nicht erreichbar",
                                 "Seit über 5 Minuten antworten diese Adressen nicht wie erwartet: "
                                 + ", ".join(f"{URL}{a} → {s or 'keine Antwort'}" for a, s in falsch.items())
                                 + "\nLaufen die Container und Traefik? docker ps"))

    leben = m.get("lebenszeichen_min")
    if leben is not None and leben > LEBENSZEICHEN:
        out.append(alarme.Befund("lebenszeichen", "kritisch", "Import-Dienst meldet sich nicht",
                                 f"Der Dienst soccer-import hat sich seit {int(leben)} Minuten nicht gemeldet "
                                 "(Datei import/lebenszeichen). Letzte Meldungen: docker logs soccer-import --tail 50"))
    return out


def _fp_text(fp: float) -> str:
    return (f"Die Festplatte ist zu {fp} % belegt. Grösste Ordner im Projekt: du -sh /docker/football-dashboard/* | "
            "sort -h | tail\nAlte Backups räumt der Import selbst auf (gestaffelt); Docker-Reste: docker image prune "
            "(nur nach Rücksprache).")


def messen(projekt: Path, zustand: dict, now: datetime) -> dict:
    jetzt = cpu_zaehler()
    m = {"zeit": now.isoformat(), "festplatte": festplatte(projekt), "speicher": speicher(),
         "cpu": cpu_prozent(zustand.get("cpu_zaehler"), jetzt),
         "container": {n: docker_inspect(n) for n in CONTAINER}}
    live = m["container"][WEBSITE]["status"] != "fehlt"
    m["website"] = {a: http_status(URL + a) for a in (ADRESSEN if live else ADRESSEN_VOR_LIVEGANG)}
    zustand["cpu_zaehler"] = list(jetzt)
    leben = projekt / "import" / "lebenszeichen"
    m["lebenszeichen_min"] = round((now.timestamp() - leben.stat().st_mtime) / 60, 1) if leben.exists() else None
    return m


def server_json(datei: Path, m: dict, now: datetime) -> None:
    """Letzte Messwerte und Höchstwerte der laufenden Woche (für Dashboard und Statusmail)."""
    alt = alarme.laden(datei)
    kw = "{}-{:02d}".format(*now.isocalendar()[:2])
    woche = alt.get("woche") if alt.get("woche", {}).get("kw") == kw else {"kw": kw}
    for k in ("festplatte", "speicher", "cpu"):
        if m.get(k) is not None:
            woche[k] = max(woche.get(k) or 0, m[k])
    # Seit 0.30 (Showcase, Datenmonitoring): Verfügbarkeit der Website je Tag – [Prüfungen, davon erreichbar], 35 Tage.
    # Erreichbar heisst: die Startseite (/de/, vor dem Livegang /) antwortet mit 200.
    tage = dict(alt.get("verfuegbarkeit") or {})
    tag = now.date().isoformat()
    web = m.get("website") or {}
    n, ok = tage.get(tag, [0, 0])
    tage[tag] = [n + 1, ok + (1 if web.get("/de/", web.get("/")) == 200 else 0)]
    tage = dict(sorted(tage.items())[-35:])
    alarme.speichern(datei, {**m, "woche": woche, "verfuegbarkeit": tage})


def pruefen(projekt: Path = PROJEKT, now: datetime | None = None, senden=None) -> list[alarme.Befund]:
    now = (now or datetime.now()).replace(microsecond=0)
    imp = projekt / "import"
    env = env_lesen(projekt / ".env")
    senden = senden or (lambda betreff, text: mail.senden("alert", betreff, text, env=env))
    zustand_datei = imp / "ueberwachung_messung.json"
    zustand = alarme.laden(zustand_datei)
    m = messen(projekt, zustand, now)
    befunde = auswerten(m, zustand, now)
    alarme.speichern(zustand_datei, zustand)
    server_json(imp / "server.json", m, now)
    alarme.verarbeiten(imp / "ueberwachung.json", befunde, now, senden,
                       lambda e: alarme.ereignis(imp / "ereignisse.jsonl", {**e, "quelle": "server"}))
    return befunde


def main(argv: list[str]) -> int:
    if "--test" in argv:
        release = argv[argv.index("--release") + 1] if "--release" in argv and argv.index("--release") + 1 < len(argv) else ""
        ok, meldung = mail.testmail("alert", release, "Prüfskript auf dem Server (an alert@)",
                                    env=env_lesen(PROJEKT / ".env"))
        print(("✅ " if ok else "✖ ") + f"Testmail Server: {meldung}")
        alarme.ereignis(PROJEKT / "import" / "ereignisse.jsonl",
                        {"zeit": datetime.now().replace(microsecond=0).isoformat(), "art": "testmail",
                         "weg": "server", "ok": ok, "meldung": meldung, "release": release})
        return 0 if ok else (3 if meldung == mail.NICHT_EINGERICHTET else 1)
    if argv:
        print(__doc__.split("Aufruf:")[1].split("Nur Standard")[0].strip())
        return 2
    pruefen()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
