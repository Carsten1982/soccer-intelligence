"""Dienst des Containers soccer-import: Zeitplan, Freigabe und Tausch (Spezifikation, Abschnitt 10).

- Täglich ab 04:00 (Europe/Zurich, seit 0.15 auch am Wochenende) ein Lauf; montags werden alle Spiele der Saison mit
  API-ID neu geprüft, sonst die letzten 2 Spieltage. Ein Lauf erzeugt eine neue Fassung unter /import/laeufe/<lauf>/.
- Entscheide aus dem Reiter (späte Korrekturen, Endstand gegen Tor-Ereignisse) kommen ebenfalls als Anfrage und werden
  in /import/entscheidungen.json festgehalten (entscheide.py); jeder Lauf wendet sie an.
- Rohdaten älter als 12 Monate löscht der Dienst (R9).
- Seit 0.20 einmal je Stunde der Schnappschuss-Lauf (importer/schnappschuss.py, Regeln in core/schnappschuss.py):
  Werte jedes Spiels ab einer Stunde vor dem Anpfiff einfrieren; nach jeder Übernahme sofort ein weiterer Lauf.
- Es wartet immer höchstens eine Fassung; ein neuer Lauf ersetzt die wartende (er baut auf der gültigen auf).
- Freigabe: Das Dashboard legt eine Anfrage in /import/anfragen/ ab („uebernehmen“ oder „verwerfen“); der Dienst prüft
  sie innerhalb von 30 Sekunden. Übernommen wird nur ohne Fehler und nur, wenn die gültigen Dateien seit dem Lauf
  unverändert sind. Vor dem Tausch kommen beide gültigen Dateien mit Datum nach /backup (die letzten 30 bleiben);
  der Tausch selbst ist ein einziger Schritt (os.replace), die App liest nie eine halbe Datei.
- Ab dem Datum automatisch_ab in app/config/import.toml wird eine Fassung sofort übernommen, wenn sie unkritisch ist
  (R5): keine Fehler, keine kritischen Punkte, keine Plausibilitätswarnung, keine neue Warnung der Prüfregeln.

Seit 0.22 (Spezifikation 10.2, Beschlüsse Carsten 20.11.2026): zusätzlich ein Lauf nach jedem Spiel (Anpfiff + 2¼ h,
importer/laufplan.py) mit Wiederholung nach 1 Stunde (höchstens zwei); jede fehlerfreie Fassung wird sofort übernommen
(automatisch_ab = Einspieldatum); Backups gestaffelt statt „die letzten 30“; jeder Lauf schreibt eine Zeile ins
Ereignisprotokoll /import/ereignisse.jsonl (Grundlage für Alarme und Statusmail ab 0.23).

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
from . import laufplan, schnappschuss
from .client import ApiClient, ImportFehler, used_today
from .erzeugen import build, save_report, sha256
from .teams import load_team_names

STATE = "zustand.json"
EVENTS = "ereignisse.jsonl"


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


def event(base: Path, entry: dict) -> None:
    """Eine Zeile ins Ereignisprotokoll (seit 0.22)."""
    with (base / EVENTS).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run(base: Path, data_dir: Path, now: datetime, full_season: bool | None = None, client: ApiClient | None = None,
        anlass: str = "kontrolle") -> dict:
    """Ein Lauf: neue Fassung erzeugen, Bericht speichern, wartende Fassung ersetzen, ggf. automatisch übernehmen.
    anlass: „kontrolle“ (täglich 04:00, letzte 2 Spieltage bzw. montags die ganze Saison), „spiel“ (nach einem Spiel)
    oder „wiederholung“ – die beiden letzten holen nur neue Spiele und Spiele mit fehlenden Werten (seit 0.22)."""
    dirs = _dirs(base)
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    recover(base, data_dir, now)                                   # nie auf einem halben Tausch aufbauen (F1)
    run_id = now.strftime("%Y-%m-%d_%H%M%S")
    out = dirs["laeufe"] / run_id
    client = client or ApiClient(key=os.environ.get(E.KEY_ENV), raw_dir=dirs["roh"],
                                 used_before=used_today(dirs["roh"], now.strftime("%Y-%m-%d")))
    kontrolle = anlass == "kontrolle"
    full = (now.weekday() == 0 and kontrolle) if full_season is None else full_season
    report = {"lauf": run_id, "start": now.isoformat(timespec="seconds"), "anlass": anlass}
    try:
        report.update(build(client, load_team_names(E.TEAM_NAMES_FILE), load_leagues(),
                            data_dir / settings.DATABASE_FILENAME, data_dir / settings.FIXTURES_FILENAME, out,
                            now.date(), full, decisions=entscheide.load(base), recheck=kontrolle,
                            jetzt=now if now.tzinfo else None))
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
    if kontrolle:
        state["letzter_lauf_tag"] = now.strftime("%Y-%m-%d")
    state["letzter_lauf"] = run_id
    save_report(report, out / "bericht.json")
    save_state(base, state)
    _prune_raw(dirs["roh"], now.date())
    auto = E.automatic_from()
    if report["status"] == "wartet" and auto and now.date() >= auto and (report.get("automatik") or {}).get("ok"):
        apply(base, data_dir, E.BACKUP_DIR, run_id, "uebernehmen", "automatisch", now)
    final = load_report(base, run_id) or report
    event(base, {"zeit": now.isoformat(timespec="seconds"), "lauf": run_id, "anlass": anlass, "status": final.get("status"),
                 "neue_spiele": sum(len(v) for v in (final.get("neue_spiele") or {}).values()),
                 "korrekturen": len(final.get("korrekturen") or []), "offen": len(final.get("offen") or []),
                 "kritisch": len(final.get("kritisch") or []), "fehler": final.get("fehler"),
                 "abfragen": (final.get("anfragen") or {}).get("verbraucht"), "meldung": final.get("meldung")})
    return final


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


HANDOVER = "uebergabe.json"      # Übergabe-Protokoll (0.15.1, Code-Prüfung F1): steht nur während des Tauschs


def _files() -> dict[str, str]:
    return {settings.DATABASE_FILENAME: "datenbank", settings.FIXTURES_FILENAME: "spielplan"}


def _target(backup_dir: Path, stem: str, tag: str, suffix: str) -> Path:
    """Backup-Ziel, das es noch nicht gibt (F2: ein vorhandenes Backup wird nie überschrieben).
    Bei Gleichstand wird vor „_vor_import“ _2, _3 … angehängt, damit das Aufräumen die Datei weiter erkennt."""
    n = 1
    while (path := backup_dir / f"{stem}_{tag}{'' if n == 1 else f'_{n}'}_vor_import{suffix}").exists():
        n += 1
    return path


def _backup(base: Path, data_dir: Path, backup_dir: Path, run_id: str, now: datetime) -> None:
    """Gültige Dateien und Entscheide mit Datum (Sekunden) und Lauf ins Backup; seit 0.22 gestaffelt aufgeräumt
    (laufplan.behalten: 14 Tage, 8 Wochen, 12 Monate, je Saison dauerhaft; bis 0.21.2: die letzten 30)."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{now:%Y-%m-%d_%H%M%S}_lauf-{run_id}"
    sources = [(base / E.DECISIONS_FILE, "entscheidungen", ".json")] + [
        (data_dir / name, Path(name).stem, Path(name).suffix) for name in _files()]
    for src, stem, suffix in sources:
        if src.exists():
            shutil.copy2(src, _target(backup_dir, stem, tag, suffix))
    laufplan.backups_aufraeumen(backup_dir, [(stem, suffix) for _, stem, suffix in sources], now.date())


def _finish(base: Path, run_id: str, by: str, stamp: str) -> None:
    """Abschluss nach dem Tausch: Bericht, Fassung aufräumen, Zustand – erst danach fällt das Protokoll weg."""
    _set_status(base, run_id, "übernommen" if by != "automatisch" else "übernommen (automatisch)", f"{stamp} ({by})")
    _drop_files(base, run_id)
    state = load_state(base)
    if state.get("wartend") == run_id:
        state["wartend"] = None
    state["letzter_schnappschuss"] = None          # neue Daten: wartende Schnappschüsse gleich nachholen (0.20)
    save_state(base, state)
    (base / HANDOVER).unlink(missing_ok=True)


def _swap(base: Path, data_dir: Path, handover: dict) -> None:
    """Beide Dateien aus der geprüften Fassung tauschen (je Datei in einem Schritt). Eine Datei, die schon den
    Zielstand hat, wird übersprungen – so kann ein abgebrochener Tausch einfach wiederholt werden."""
    staged = _dirs(base)["laeufe"] / handover["lauf"]
    for name, target in handover["dateien"].items():
        live = data_dir / name
        if live.exists() and sha256(live) == target:
            continue
        if not (staged / name).exists() or sha256(staged / name) != target:
            raise ImportFehler(f"Fassung {handover['lauf']}: {name} fehlt oder stimmt nicht mit der Prüfsumme überein")
        tmp = data_dir / f".{name}.tmp"
        shutil.copy2(staged / name, tmp)
        os.replace(tmp, live)


def recover(base: Path, data_dir: Path, now: datetime) -> str | None:
    """Abgebrochenen Tausch zu Ende führen (F1). Läuft beim Start des Dienstes und vor jedem Lauf.
    Ohne Übergabe-Protokoll: nichts zu tun (None)."""
    p = base / HANDOVER
    if not p.exists():
        return None
    handover = json.loads(p.read_text(encoding="utf-8"))
    _swap(base, data_dir, handover)
    _finish(base, handover["lauf"], handover.get("von", "Dashboard"), handover.get("stempel", now.strftime("%d.%m.%Y %H:%M")))
    return f"Abgebrochene Übernahme {handover['lauf']} zu Ende geführt"


def apply(base: Path, data_dir: Path, backup_dir: Path, run_id: str, action: str, by: str, now: datetime) -> str:
    """Freigabe ausführen. Gibt eine kurze Meldung zurück (steht auch im Bericht).

    Ablauf der Übernahme (seit 0.15.1, Code-Prüfung F1/F2):
    1. Prüfungen: Fassung wartet, ohne Fehler, gültige Dateien unverändert (Basis), **beide Dateien der Fassung
       vorhanden und mit den Prüfsummen aus dem Bericht** – sonst wird nichts getauscht.
    2. Backup mit eindeutigem Namen (Sekunden und Lauf, nie überschrieben).
    3. Übergabe-Protokoll schreiben (welche Fassung, welche Prüfsummen), dann beide Dateien tauschen.
    4. Abschluss; das Protokoll wird zuletzt gelöscht. Bricht der Dienst zwischen 3 und 4 ab, führt recover() den
       Tausch beim nächsten Start zu Ende – ein Mischstand aus alter und neuer Datei bleibt nie bestehen."""
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
    files = _files()
    current = {k: sha256(data_dir / name) if (data_dir / name).exists() else None for name, k in files.items()}
    if current != rep.get("basis"):
        msg = "Gültige Dateien wurden seit dem Lauf geändert – nicht übernommen; nächster Lauf baut darauf auf"
        _set_status(base, run_id, "verworfen", msg)
        _drop_files(base, run_id)
        state["wartend"] = None
        save_state(base, state)
        return msg
    staged = _dirs(base)["laeufe"] / run_id
    expected = rep.get("dateien") or {}
    for name, key in files.items():                       # F2: Fassung unverändert seit dem Lauf?
        f = staged / name
        if not f.exists() or sha256(f) != expected.get(key):
            msg = f"Fassung beschädigt oder verändert ({name}) – nicht übernommen, gültige Dateien unverändert"
            _set_status(base, run_id, "Fehler – nicht übernehmbar", msg)
            state["wartend"] = None
            save_state(base, state)
            return msg
    _backup(base, data_dir, backup_dir, run_id, now)
    handover = {"lauf": run_id, "von": by, "stempel": stamp, "zeit": now.isoformat(timespec="seconds"),
                "dateien": {name: expected[key] for name, key in files.items()}}
    tmp = base / f".{HANDOVER}.tmp"
    tmp.write_text(json.dumps(handover, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, base / HANDOVER)
    _swap(base, data_dir, handover)
    _finish(base, run_id, by, stamp)
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


def naechster(base: Path, data_dir: Path, now: datetime) -> str | None:
    """Welcher Lauf ist fällig? Kontrolllauf vor Lauf nach dem Spiel vor Wiederholung (seit 0.22)."""
    state = load_state(base)
    if due(state, now):
        return "kontrolle"
    if laufplan.faellig(state, now, data_dir / settings.FIXTURES_FILENAME):
        return "spiel"
    if laufplan.wiederholung_faellig(state, now.replace(tzinfo=None)):
        return "wiederholung"
    return None


def run_planned(base: Path, data_dir: Path, now: datetime, anlass: str, client: ApiClient | None = None) -> dict:
    """Lauf ausführen und Laufplan nachführen: erledigte Läufe vermerken, Wiederholung planen."""
    fx = data_dir / settings.FIXTURES_FILENAME
    local = now.replace(tzinfo=None, microsecond=0)
    state = load_state(base)
    laufplan.erledigt(state, local, fx)                    # auch bei Abbruch nicht endlos wiederholen
    save_state(base, state)
    rep = run(base, data_dir, now, client=client, anlass=anlass)
    state = load_state(base)
    if anlass == "kontrolle":
        state["wiederholung"] = None                       # der Kontrolllauf holt alles nach
    else:
        laufplan.wiederholung_planen(state, rep, local, anlass)
    save_state(base, state)
    return rep


def main(argv: list[str]) -> None:
    tz = ZoneInfo(E.TIMEZONE)
    base, data_dir = E.IMPORT_DIR, settings.DATA_DIR
    for d in _dirs(base).values():
        d.mkdir(parents=True, exist_ok=True)
    done = recover(base, data_dir, datetime.now(tz))               # abgebrochenen Tausch zu Ende führen (F1)
    if done:
        print(done, flush=True)
    if "--jetzt" in argv:
        rep = run(base, data_dir, datetime.now(tz))
        print("Lauf", rep["lauf"], "->", rep["status"], rep.get("meldung", ""), flush=True)
        return
    print("soccer-import gestartet", datetime.now(tz).isoformat(timespec="seconds"), flush=True)
    while True:
        now = datetime.now(tz)
        process_requests(base, data_dir, E.BACKUP_DIR, now)
        anlass = naechster(base, data_dir, now)
        if anlass:
            rep = run_planned(base, data_dir, now, anlass)
            print(now.isoformat(timespec="seconds"), "Lauf", rep["lauf"], f"({anlass})", "->", rep["status"],
                  rep.get("meldung", ""), flush=True)
        if schnappschuss.due(load_state(base), now):
            snap_hour(base, data_dir, now)
        time.sleep(30)


def snap_hour(base: Path, data_dir: Path, now: datetime) -> dict:
    """Schnappschuss-Lauf und Stunde im Zustand vermerken (seit 0.20)."""
    rep = schnappschuss.run(base, data_dir, now)
    state = load_state(base)
    state["letzter_schnappschuss"] = now.strftime("%Y-%m-%dT%H")
    save_state(base, state)
    print(now.isoformat(timespec="seconds"), "Schnappschüsse:", rep["neu"], "neu,", rep["wartend_anzahl"], "wartend",
          "–", rep["fehler"] or "ok", flush=True)
    return rep


if __name__ == "__main__":
    main(sys.argv[1:])
