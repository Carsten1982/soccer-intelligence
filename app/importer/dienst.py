"""Dienst des Containers soccer-import: Zeitplan, Freigabe und Tausch (Spezifikation, Abschnitt 10).

- Täglich ab 04:00 (Europe/Zurich, seit 0.15 auch am Wochenende) ein Lauf; montags werden alle Spiele der Saison mit
  API-ID neu geprüft, sonst die letzten 2 Spieltage. Ein Lauf erzeugt eine neue Fassung unter /import/laeufe/<lauf>/.
- Entscheide aus dem Reiter (späte Korrekturen, Endstand gegen Tor-Ereignisse) kommen ebenfalls als Anfrage und werden
  in /import/entscheidungen.json festgehalten (entscheide.py); jeder Lauf wendet sie an.
- Rohdaten älter als 12 Monate löscht der Dienst (R9).
- Es wartet immer höchstens eine Fassung; ein neuer Lauf ersetzt die wartende (er baut auf der gültigen auf).
- Freigabe: Das Dashboard legt eine Anfrage in /import/anfragen/ ab („uebernehmen“ oder „verwerfen“); der Dienst prüft
  sie innerhalb von 30 Sekunden. Übernommen wird nur ohne Fehler und nur, wenn die gültigen Dateien seit dem Lauf
  unverändert sind. Vor dem Tausch kommen beide gültigen Dateien mit Datum nach /backup (die letzten 30 bleiben);
  der Tausch selbst ist ein einziger Schritt (os.replace), die App liest nie eine halbe Datei.
- Ab dem Datum automatisch_ab in app/config/import.toml wird eine Fassung sofort übernommen, wenn sie unkritisch ist
  (R5): keine Fehler, keine kritischen Punkte, keine Plausibilitätswarnung, keine neue Warnung der Prüfregeln.

Aufruf: python -m importer.dienst            Dauerbetrieb im Container
        python -m importer.dienst --jetzt    sofort einen Lauf (z. B. nach dem Einspielen)
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from core import settings
from core.config import load_leagues

from . import einstellungen as E
from . import entscheide
from .client import ApiClient, ImportFehler, used_today
from .erzeugen import build, save_report, sha256
from .teams import load_team_names

STATE = "zustand.json"


def _dirs(base: Path) -> dict[str, Path]:
    return {"laeufe": base / "laeufe", "anfragen": base / "anfragen", "roh": base / "roh"}


def load_state(base: Path) -> dict:
    p = base / STATE
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"wartend": None, "letzter_lauf_tag": None}


def save_state(base: Path, state: dict) -> None:
    tmp = base / f".{STATE}.tmp"
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, base / STATE)


def load_report(base: Path, run_id: str) -> dict | None:
    p = _dirs(base)["laeufe"] / run_id / "bericht.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _drop_files(base: Path, run_id: str) -> None:
    d = _dirs(base)["laeufe"] / run_id
    for name in (settings.DATABASE_FILENAME, settings.FIXTURES_FILENAME):
        (d / name).unlink(missing_ok=True)


def run(base: Path, data_dir: Path, now: datetime, full_season: bool | None = None, client: ApiClient | None = None) -> dict:
    """Ein Lauf: neue Fassung erzeugen, Bericht speichern, wartende Fassung ersetzen, ggf. automatisch übernehmen."""
    dirs = _dirs(base)
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    run_id = now.strftime("%Y-%m-%d_%H%M%S")
    out = dirs["laeufe"] / run_id
    client = client or ApiClient(key=os.environ.get(E.KEY_ENV), raw_dir=dirs["roh"],
                                 used_before=used_today(dirs["roh"], now.strftime("%Y-%m-%d")))
    full = now.weekday() == 0 if full_season is None else full_season
    report = {"lauf": run_id, "start": now.isoformat(timespec="seconds")}
    try:
        report.update(build(client, load_team_names(E.TEAM_NAMES_FILE), load_leagues(),
                            data_dir / settings.DATABASE_FILENAME, data_dir / settings.FIXTURES_FILENAME, out,
                            now.date(), full, decisions=entscheide.load(base)))
        report["status"] = "wartet" if report["fehler"] == 0 else "Fehler – nicht übernehmbar"
    except Exception as exc:                                  # Lauf fehlgeschlagen: gültige Dateien bleiben
        report["status"] = "fehlgeschlagen"
        report["meldung"] = str(exc) if isinstance(exc, ImportFehler) else f"{type(exc).__name__}: {exc}"
        report["details"] = traceback.format_exc(limit=5)
        _drop_files(base, run_id)
    report["ende"] = datetime.now(now.tzinfo).isoformat(timespec="seconds")
    report["anfragen"] = {"verbraucht": client.used, "rest": client.remaining}
    state = load_state(base)
    if report["status"] in ("wartet", "Fehler – nicht übernehmbar"):
        old = state.get("wartend")
        if old and old != run_id:
            _set_status(base, old, "ersetzt", f"ersetzt durch Lauf {run_id}")
            _drop_files(base, old)
        state["wartend"] = run_id
    state["letzter_lauf_tag"] = now.strftime("%Y-%m-%d")
    state["letzter_lauf"] = run_id
    save_report(report, out / "bericht.json")
    save_state(base, state)
    _prune_raw(dirs["roh"], now.date())
    auto = E.automatic_from()
    if report["status"] == "wartet" and auto and now.date() >= auto and (report.get("automatik") or {}).get("ok"):
        apply(base, data_dir, E.BACKUP_DIR, run_id, "uebernehmen", "automatisch", now)
    return load_report(base, run_id)


def _prune_raw(raw: Path, today) -> None:
    """Rohdaten-Tagesordner (JJJJ-MM-TT) älter als 12 Monate löschen (R9)."""
    for d in raw.glob("????-??-??"):
        try:
            day = datetime.strptime(d.name, "%Y-%m-%d").date()
        except ValueError:
            continue
        if (today - day).days > E.RAW_KEEP_DAYS and d.is_dir():
            for f in d.iterdir():
                f.unlink()
            d.rmdir()


def _set_status(base: Path, run_id: str, status: str, note: str | None = None, **extra) -> None:
    rep = load_report(base, run_id)
    if rep is None:
        return
    rep["status"] = status
    if note:
        rep["meldung"] = note
    rep.update(extra)
    save_report(rep, _dirs(base)["laeufe"] / run_id / "bericht.json")


def apply(base: Path, data_dir: Path, backup_dir: Path, run_id: str, action: str, by: str, now: datetime) -> str:
    """Freigabe ausführen. Gibt eine kurze Meldung zurück (steht auch im Bericht)."""
    state = load_state(base)
    rep = load_report(base, run_id)
    stamp = now.strftime("%d.%m.%Y %H:%M")
    if rep is None or state.get("wartend") != run_id:
        return "Lauf wartet nicht (mehr) – nichts getan"
    if action == "verwerfen":
        _set_status(base, run_id, "verworfen", f"{stamp} ({by})")
        _drop_files(base, run_id)
        state["wartend"] = None
        save_state(base, state)
        return "verworfen"
    if rep.get("fehler", 1) > 0:
        return "Fassung hat Fehler – Übernahme gesperrt"
    files = {settings.DATABASE_FILENAME: "datenbank", settings.FIXTURES_FILENAME: "spielplan"}
    current = {k: sha256(data_dir / name) if (data_dir / name).exists() else None for name, k in files.items()}
    if current != rep.get("basis"):
        msg = "Gültige Dateien wurden seit dem Lauf geändert – nicht übernommen; nächster Lauf baut darauf auf"
        _set_status(base, run_id, "verworfen", msg)
        _drop_files(base, run_id)
        state["wartend"] = None
        save_state(base, state)
        return msg
    backup_dir.mkdir(parents=True, exist_ok=True)
    tag = now.strftime("%Y-%m-%d_%H%M")
    decisions = base / E.DECISIONS_FILE
    if decisions.exists():                                     # Entscheide mit sichern (R1)
        shutil.copy2(decisions, backup_dir / f"entscheidungen_{tag}_vor_import.json")
        for old in sorted(backup_dir.glob("entscheidungen_*_vor_import.json"))[:-E.BACKUPS_KEPT]:
            old.unlink()
    for name in files:
        src = data_dir / name
        if src.exists():
            shutil.copy2(src, backup_dir / f"{Path(name).stem}_{tag}_vor_import{Path(name).suffix}")
        kept = sorted(backup_dir.glob(f"{Path(name).stem}_*_vor_import{Path(name).suffix}"))
        for old in kept[:-E.BACKUPS_KEPT]:
            old.unlink()
    staged = _dirs(base)["laeufe"] / run_id
    for name in files:
        tmp = data_dir / f".{name}.tmp"
        shutil.copy2(staged / name, tmp)
        os.replace(tmp, data_dir / name)
    _set_status(base, run_id, "übernommen" if by != "automatisch" else "übernommen (automatisch)",
                f"{stamp} ({by})")
    _drop_files(base, run_id)
    state["wartend"] = None
    save_state(base, state)
    return "übernommen"


def process_requests(base: Path, data_dir: Path, backup_dir: Path, now: datetime) -> None:
    """Anfragen aus dem Dashboard abarbeiten (älteste zuerst) und danach löschen."""
    for p in sorted(_dirs(base)["anfragen"].glob("*.json")):
        try:
            req = json.loads(p.read_text(encoding="utf-8"))
            if req.get("aktion") in ("uebernehmen", "verwerfen"):
                print(now.isoformat(timespec="seconds"), "Anfrage", req["aktion"], req.get("lauf"), "->",
                      apply(base, data_dir, backup_dir, str(req.get("lauf")), req["aktion"], "Dashboard", now), flush=True)
            elif req.get("aktion") == "entscheid":
                entry = {k: req.get(k) for k in ("art", "id", "liga", "spiel", "spalte", "api_wert", "alt_wert", "entscheid")}
                entry.update({"zeit": now.isoformat(timespec="seconds"), "quelle": "Dashboard"})
                entscheide.add(base, entry)
                print(now.isoformat(timespec="seconds"), "Entscheid", entry["art"], entry["id"], entry.get("spalte") or "",
                      "->", entry["entscheid"], flush=True)
        except (ValueError, KeyError, OSError) as exc:
            print("Anfrage ungültig:", p.name, exc, flush=True)
        p.unlink(missing_ok=True)


def due(state: dict, now: datetime) -> bool:
    """Täglich ab 04:00 ein Lauf (seit 0.15 auch am Wochenende, Spielplan v2.1, 3.7)."""
    return now.hour >= E.RUN_HOUR and state.get("letzter_lauf_tag") != now.strftime("%Y-%m-%d")


def main(argv: list[str]) -> None:
    tz = ZoneInfo(E.TIMEZONE)
    base, data_dir = E.IMPORT_DIR, settings.DATA_DIR
    for d in _dirs(base).values():
        d.mkdir(parents=True, exist_ok=True)
    if "--jetzt" in argv:
        rep = run(base, data_dir, datetime.now(tz))
        print("Lauf", rep["lauf"], "->", rep["status"], rep.get("meldung", ""), flush=True)
        return
    print("soccer-import gestartet", datetime.now(tz).isoformat(timespec="seconds"), flush=True)
    while True:
        now = datetime.now(tz)
        process_requests(base, data_dir, E.BACKUP_DIR, now)
        if due(load_state(base), now):
            rep = run(base, data_dir, now)
            print(now.isoformat(timespec="seconds"), "Lauf", rep["lauf"], "->", rep["status"], rep.get("meldung", ""), flush=True)
        time.sleep(30)


if __name__ == "__main__":
    main(sys.argv[1:])
