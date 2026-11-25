"""Stündlicher Schnappschuss-Lauf des Containers soccer-import (seit 0.20; Regeln in core/schnappschuss.py).

Liest die gültigen Dateien in data/ (nur lesen), rechnet mit denselben Funktionen wie Dashboard und Website und
legt fehlende Schnappschüsse und erste Ergebnisse unter /import/schnappschuesse/ an. Nichts wird überschrieben.
Der Stand des Laufs (Anzahl, wartende Spiele, Fehler) steht in /import/schnappschuesse/stand.json und im Reiter
Datenimport/API (Überwachung; E-Mail-Alarm ab 0.22).

Aufruf: python -m importer.schnappschuss      ein Lauf sofort (z. B. nach dem Einspielen)
"""

from __future__ import annotations

import json
import os
import time
import traceback
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from core import anzeige as A
from core import auswertung as AW
from core import schnappschuss as S
from core import settings
from core.config import load_leagues, load_teams
from core.fixtures import load_fixtures
from core.kpis import KPI_KEYS, Match, compute_match, prepare_league
from core.loader import load_database
from core.thresholds import load_thresholds

from . import einstellungen as E
from .erzeugen import sha256

MAX_LIST = 50                    # so viele wartende Spiele stehen höchstens im Stand


def _app_version() -> str:
    return settings.APP_VERSION.split(" ")[0]


def run(base: Path, data_dir: Path, now: datetime) -> dict:
    """Ein Lauf. now = Europe/Zurich (mit oder ohne Zeitzone). Gibt den Stand zurück (wird auch gespeichert)."""
    local = now.astimezone(ZoneInfo(E.TIMEZONE)).replace(tzinfo=None) if now.tzinfo else now
    local = local.replace(microsecond=0)
    started = time.monotonic()
    stand = {"lauf": local.isoformat(timespec="seconds"), "neu": 0, "neu_nachtraeglich": 0, "ergebnisse_neu": 0,
             "vorhanden": 0, "wartend_anzahl": 0, "wartend": [], "fehler": None, "dauer_s": None, "ligen": {}}
    try:
        db_path, fx_path = data_dir / settings.DATABASE_FILENAME, data_dir / settings.FIXTURES_FILENAME
        db = load_database(db_path)
        leagues = load_leagues()
        fx = load_fixtures(fx_path, leagues, db.leagues, load_teams(settings.TEAMS_FILE))
        if db.has_errors or fx.has_errors:
            raise RuntimeError("Datenbank oder Spielplan mit Fehlern – keine Schnappschüsse (wie die Seiten gesperrt)")
        thresholds = load_thresholds(settings.THRESHOLDS_FILE, [lg.name for lg in leagues])
        meta = {"app": _app_version(), "datenbank_sha256": db.sha256 or sha256(db_path),
                "schwellen_sha256": sha256(settings.THRESHOLDS_FILE), "schwellen_berechnet": thresholds.berechnet}
        for league in (lg for lg in leagues if lg.aktiv):
            fixtures, df = fx.leagues.get(league.name), db.leagues.get(league.name)
            if fixtures is None or fixtures.empty or df is None:
                continue
            prepared = prepare_league(df)
            fxp, results = A.prepare(fixtures), A.results_index(prepared)
            zeilen = {(g.season, g.home, g.away): g for g in prepared.itertuples(index=False)}   # für die Ist-Werte
            count = {"neu": 0, "vorhanden": 0, "wartend": 0}
            for row in S.candidates(fxp, local).itertuples():
                api_id = S.api_id_of(row)
                path = S.snapshot_path(base, league.url, row.saison, api_id)
                score = results.get((row.saison, row.heim, row.gast))
                if score is not None:
                    if S.write_once(S.result_path(base, league.url, row.saison, api_id),
                                    {"ergebnis": list(score), "erfasst": local.isoformat(timespec="seconds")}):
                        stand["ergebnisse_neu"] += 1
                    g = zeilen.get((row.saison, row.heim, row.gast))  # seit 0.25: erste Ist-Werte je Kennzahl
                    if g is not None:
                        S.record_stats(base, league.url, row.saison, api_id,
                                       {k: AW.ist_wert(k, g) for k in KPI_KEYS}, local)
                if path.exists():
                    count["vorhanden"] += 1
                    continue
                if A.missing_previous(fxp, row, results):          # wartet auf die Vorspiel-Ergebnisse
                    count["wartend"] += 1
                    if len(stand["wartend"]) < MAX_LIST:
                        stand["wartend"].append(f"{league.name}: {row.heim} – {row.gast} ({row.datum_von:%d.%m.%Y})")
                    continue
                kpis = compute_match(prepared, Match(league.name, row.saison, int(row.spieltag), row.datum_von,
                                                     row.heim, row.gast), league.matchdays, thresholds.get)
                data = S.payload(kpis, row, local, league.name, meta)
                if S.write_once(path, data):
                    count["neu"] += 1
                    stand["neu_nachtraeglich"] += int(data["nachtraeglich"])
            stand["ligen"][league.name] = count
            stand["neu"] += count["neu"]
            stand["vorhanden"] += count["vorhanden"]
            stand["wartend_anzahl"] += count["wartend"]
    except Exception as exc:                      # Lauf fehlgeschlagen: vorhandene Schnappschüsse bleiben unberührt
        stand["fehler"] = f"{type(exc).__name__}: {exc}"
        stand["details"] = traceback.format_exc(limit=5)
    stand["dauer_s"] = round(time.monotonic() - started, 1)
    save_status(base, stand)
    return stand


def save_status(base: Path, stand: dict) -> None:
    folder = Path(base) / S.DIRNAME
    folder.mkdir(parents=True, exist_ok=True)
    tmp = folder / f".{S.STATUS_FILE}.tmp"
    tmp.write_text(json.dumps(stand, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, folder / S.STATUS_FILE)


def load_status(base: Path) -> dict | None:
    try:
        return json.loads((Path(base) / S.DIRNAME / S.STATUS_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def due(state: dict, now: datetime) -> bool:
    """Einmal je volle Stunde (der Dienst prüft alle 30 Sekunden)."""
    return state.get("letzter_schnappschuss") != now.strftime("%Y-%m-%dT%H")


def main() -> None:
    rep = run(E.IMPORT_DIR, settings.DATA_DIR, datetime.now(ZoneInfo(E.TIMEZONE)))
    print("Schnappschüsse:", rep["neu"], "neu (davon", rep["neu_nachtraeglich"], "nachträglich),", rep["vorhanden"],
          "vorhanden,", rep["wartend_anzahl"], "wartend", "–", rep["fehler"] or "ok", f"({rep['dauer_s']} s)", flush=True)


if __name__ == "__main__":
    main()
