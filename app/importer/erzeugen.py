"""Neue Fassung von Datenbank und Spielplan erzeugen, mit Bericht (Spezifikation, Abschnitt 10; Entwurf Datenimport).

Ablauf je Lauf:
1. Gültige Datenbank lesen (nie verändern) und beim ersten Lauf die Teamnamen auf die Namen der API umstellen (E14).
2. Je Liga: laufende Saison und ganze Spielliste holen.
3. Neue beendete Spiele aufnehmen (id = API-Fixture-ID, E2). Spiele mit API-ID der letzten 2 Spieltage – montags der
   ganzen Saison – neu holen und bei Abweichung korrigieren (nur Werte, die die API liefert; Spiele vor dem Stichtag,
   also ohne API-ID, werden nie verändert).
4. Spielplan aus der Spielliste erzeugen.
5. Beide Dateien als neue Fassung speichern, mit den Prüfregeln prüfen und den Bericht schreiben:
   Vollständigkeit (Spielplan gegen Ergebnisse), Qualität (gültig gegen neu), neue Spiele, Korrekturen,
   Spielplan-Änderungen, offene Spiele, unbekannte Teams.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

import openpyxl
from openpyxl.styles import Font

from core import schema, settings
from core.config import League, load_teams
from core.fixtures import load_fixtures
from core.loader import load_database

from . import einstellungen as E
from .client import ApiClient
from .convert import AWARDED, FINISHED, as_list, fixture_row, round_number, season_label
from .spielplan import COLUMNS as FX_COLUMNS
from .spielplan import fixture_rows
from .teams import TeamNames

API_ID_FROM = 1_000_000          # IDs ab hier stammen von API-Football (unsere IDs liegen unter 160'000)
KPI_STATS = ("Corners", "Yellow Cards", "Shots on Target")
HALF_FROM = 2024


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _same(a, b) -> bool:
    if isinstance(a, datetime) and isinstance(b, datetime):
        return a.date() == b.date()
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return float(a) == float(b)
    return a == b


def _short(row: dict) -> dict:
    """Kurzfassung eines Spiels für den Bericht."""
    def pair(key):
        h, a = row.get(f"Home {key} Full Time"), row.get(f"Away {key} Full Time")
        return None if h is None and a is None else f"{'–' if h is None else h}:{'–' if a is None else a}"
    return {"id": row["id"], "datum": row["Date"].strftime("%d.%m.%Y"), "spieltag": row["Gameday"],
            "heim": row["homeTeam"], "gast": row["awayTeam"],
            "endstand": f"{row['FT Home Goals']}:{row['FT Away Goals :']}",
            "halbzeit": f"{row['First-Half Home Goals']}:{row['First-Half Away Goals']}",
            "ecken": pair("Corners"), "gelb": pair("Yellow Cards"), "aufs_tor": pair("Shots on Target")}


def _stats_missing(row: dict) -> bool:
    return any(row.get(f"{s} {k} Full Time") is None for s in ("Home", "Away") for k in KPI_STATS)


def _issues(load) -> dict:
    return {"fehler": load.count("Fehler"), "warnungen": load.count("Warnung"), "hinweise": load.count("Hinweis")}


def build(client: ApiClient, names: TeamNames, leagues: list[League], db_path: Path, fx_path: Path, out_dir: Path,
          today: date, full_season: bool) -> dict:
    """Erzeugt out_dir/Database-Soccer-Intelligence.xlsx und out_dir/Spielplan.xlsx; gibt den Bericht zurück."""
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {"basis": {"datenbank": sha256(db_path), "spielplan": sha256(fx_path) if fx_path.exists() else None},
              "ganze_saison": full_season, "neue_spiele": {}, "korrekturen": [], "offen": [], "wertungen": [],
              "umbenennungen": [], "spielplan_aenderungen": {}, "vollstaendigkeit": {}, "saison": {}}
    try:
        st = client.get("status", {})["response"]
        report["abo"] = {"plan": st["subscription"]["plan"], "bis": st["subscription"]["end"][:10],
                         "aktiv": st["subscription"]["active"]}
    except Exception as exc:                                  # Status ist nur Information
        report["abo"] = {"fehler": str(exc)}
    wb = openpyxl.load_workbook(db_path)
    active = [lg for lg in leagues if lg.aktiv and lg.name in E.LEAGUE_IDS]

    # 1. Umbenennung (erster Lauf): alte Schreibweise -> Name der API
    for lg in active:
        ws, ren = wb[lg.name], names.renames.get(lg.name, {})
        col = {c.value: i for i, c in enumerate(ws[1])}
        counts = Counter()
        for row in ws.iter_rows(min_row=2):
            for key in ("homeTeam", "awayTeam"):
                cell = row[col[key]]
                if cell.value in ren:
                    counts[cell.value] += 1
                    cell.value = ren[cell.value]
        report["umbenennungen"] += [{"liga": lg.name, "alt": a, "neu": ren[a], "zeilen": n} for a, n in sorted(counts.items())]

    fixture_sheets = {}
    for lg in active:
        lid = E.LEAGUE_IDS[lg.name]
        seasons = client.get("leagues", {"id": lid, "current": "true"})["response"][0]["seasons"]
        year = next(s["year"] for s in seasons if s.get("current"))
        label = season_label(year)
        report["saison"][lg.name] = label
        season_list = client.get("fixtures", {"league": lid, "season": year, "timezone": E.TIMEZONE})["response"]
        fixture_sheets[lg.name] = fixture_rows(season_list, names)

        ws = wb[lg.name]
        head = [c.value for c in ws[1]]
        col = {h: i for i, h in enumerate(head)}
        existing = {}
        for row in ws.iter_rows(min_row=2):
            if row[col["id"]].value is not None and row[col["Season"]].value == label:
                existing[(row[col["homeTeam"]].value, row[col["awayTeam"]].value)] = row
        regular = [f for f in season_list if round_number(f["league"]["round"]) is not None]
        done = [f for f in regular if f["fixture"]["status"]["short"] in FINISHED]
        recent = set(sorted({round_number(f["league"]["round"]) for f in done})[-E.RECHECK_ROUNDS:])
        new, check = [], []
        for f in regular:
            short = f["fixture"]["status"]["short"]
            key = (names.name(f["teams"]["home"]), names.name(f["teams"]["away"]))
            if short in AWARDED:
                report["wertungen"].append({"liga": lg.name, "id": f["fixture"]["id"], "spiel": f"{key[0]} - {key[1]}",
                                            "hinweis": "gewertetes Spiel: nie automatisch, Entscheid von Hand (6.3)"})
                continue
            if short not in FINISHED:
                continue
            row = existing.get(key)
            if row is None:
                new.append(f)
            elif (row[col["id"]].value or 0) >= API_ID_FROM:
                values = {h: row[col[h]].value for h in head}
                if full_season or round_number(f["league"]["round"]) in recent or _stats_missing(values):
                    check.append(f)
        wanted = [f["fixture"]["id"] for f in new + check]
        details = {}
        for i in range(0, len(wanted), 20):
            chunk = wanted[i:i + 20]
            for d in client.get("fixtures", {"ids": "-".join(map(str, chunk)), "timezone": E.TIMEZONE})["response"]:
                details[d["fixture"]["id"]] = d
        halves = {}
        if year >= HALF_FROM:
            for f in new + check:
                if f in new or round_number(f["league"]["round"]) in recent:
                    fid = f["fixture"]["id"]
                    halves[fid] = client.get("fixtures/statistics", {"fixture": fid, "half": "true"})["response"]
        # neue Spiele anhängen (nach Datum)
        fmt = ws.cell(row=ws.max_row, column=col["Date"] + 1).number_format
        added = []
        for fid in sorted((f["fixture"]["id"] for f in new), key=lambda x: details[x]["fixture"]["date"] if x in details else ""):
            if fid not in details:
                continue
            row = fixture_row(details[fid], lg.name, names, halves.get(fid))
            ws.append(as_list(row))
            ws.cell(row=ws.max_row, column=col["Date"] + 1).number_format = fmt
            added.append(_short(row))
            if _stats_missing(row):
                report["offen"].append({"liga": lg.name, **_short(row), "grund": "Statistik noch unvollständig"})
        report["neue_spiele"][lg.name] = added
        # Spiele mit API-ID neu prüfen: Abweichungen = Korrekturen (leere API-Werte überschreiben nie)
        for f in check:
            fid = f["fixture"]["id"]
            if fid not in details:
                continue
            new_row = fixture_row(details[fid], lg.name, names, halves.get(fid))
            cells = existing[(new_row["homeTeam"], new_row["awayTeam"])]
            for c in schema.EXPECTED_COLUMNS:
                old, val = cells[col[c]].value, new_row[c]
                if val is not None and not _same(old, val):
                    report["korrekturen"].append({"liga": lg.name, "id": fid, "spiel": f"{new_row['homeTeam']} - {new_row['awayTeam']}",
                                                  "datum": new_row["Date"].strftime("%d.%m.%Y"), "spalte": c,
                                                  "alt": old if not isinstance(old, datetime) else old.strftime("%d.%m.%Y"),
                                                  "neu": val if not isinstance(val, datetime) else val.strftime("%d.%m.%Y")})
                    cells[col[c]].value = val
            merged = {c: cells[col[c]].value for c in schema.EXPECTED_COLUMNS}
            if _stats_missing(merged):
                age = (today - merged["Date"].date()).days
                report["offen"].append({"liga": lg.name, **_short(merged),
                                        "grund": "Statistik noch unvollständig" if age <= E.OPEN_DAYS
                                        else f"Statistik fehlt seit {age} Tagen"})
    db_out = out_dir / settings.DATABASE_FILENAME
    wb.save(db_out)

    # 2. Spielplan
    fx_out = out_dir / settings.FIXTURES_FILENAME
    fwb = openpyxl.Workbook()
    fwb.remove(fwb.active)
    for name, rows in fixture_sheets.items():
        ws = fwb.create_sheet(name)
        ws.append(FX_COLUMNS)
        for c in ws[1]:
            c.font = Font(bold=True)
        for r in rows:
            ws.append([r[c] for c in FX_COLUMNS])
            for c in (3, 4):
                ws.cell(row=ws.max_row, column=c).number_format = "DD.MM.YYYY"
    fwb.save(fx_out)
    report["spielplan_aenderungen"] = _fixture_changes(fx_path, fixture_sheets, names)

    # 3. Prüfung: gültige gegen neue Fassung
    teams = load_teams()
    old_db, new_db = load_database(db_path), load_database(db_out)
    old_fx = load_fixtures(fx_path, leagues, old_db.leagues, teams) if fx_path.exists() else None
    new_fx = load_fixtures(fx_out, leagues, new_db.leagues, teams)
    seen = {(i.level, i.sheet, i.check, i.match_id) for i in old_db.issues}
    report["pruefung"] = {
        "datenbank": {"gueltig": _issues(old_db), "neu": _issues(new_db),
                      "neue_meldungen": [{"stufe": i.level, "liga": i.sheet, "pruefung": i.check, "meldung": i.message}
                                         for i in new_db.issues if i.level != "Hinweis"
                                         and (i.level, i.sheet, i.check, i.match_id) not in seen][:50]},
        "spielplan": {"gueltig": _issues(old_fx) if old_fx else None, "neu": _issues(new_fx),
                      "meldungen": [{"stufe": i.level, "liga": i.sheet, "pruefung": i.check, "meldung": i.message}
                                    for i in new_fx.issues if i.level != "Hinweis"][:50]}}
    report["vollstaendigkeit"] = _completeness(fixture_sheets, new_db, today)
    report["unbekannte_teams"] = [{"api_team_id": k, "name": v} for k, v in names.unknown.items()]
    report["namensaenderungen_api"] = [{"api_team_id": k, "festgehalten": a, "api": b} for k, (a, b) in names.changed.items()]
    report["fehler"] = new_db.count("Fehler") + new_fx.count("Fehler")
    report["dateien"] = {"datenbank": sha256(db_out), "spielplan": sha256(fx_out)}
    return report


def _fixture_changes(fx_path: Path, sheets: dict[str, list[dict]], names: TeamNames) -> dict:
    """Spielplan neu gegen gültig (alte Teamnamen zuerst umbenannt): neue, entfallene und geänderte Spiele."""
    out = {"neu": 0, "entfallen": 0, "geaendert": []}
    if not fx_path.exists():
        return out
    wb = openpyxl.load_workbook(fx_path, read_only=True, data_only=True)
    for name, rows in sheets.items():
        if name not in wb.sheetnames:
            out["neu"] += len(rows)
            continue
        it = wb[name].iter_rows(values_only=True)
        head = [str(h).strip() if h else "" for h in next(it)]
        ren = names.renames.get(name, {})
        old = {}
        for r in it:
            d = dict(zip(head, r))
            if not d.get("Heimmannschaft"):
                continue
            key = (str(d.get("Saison")), ren.get(d["Heimmannschaft"], d["Heimmannschaft"]), ren.get(d["Gastmannschaft"], d["Gastmannschaft"]))
            old[key] = d
        new = {(r["Saison"], r["Heimmannschaft"], r["Gastmannschaft"]): r for r in rows}
        out["neu"] += len(set(new) - set(old))
        seasons = {k[0] for k in new}
        out["entfallen"] += len({k for k in old if k[0] in seasons} - set(new))
        for key in set(new) & set(old):
            a, b = old[key], new[key]
            diff = [f for f in ("Spieltag", "Datum von", "Datum bis", "Status")
                    if not _same(a.get(f) if a.get(f) is not None else "", b[f] if b[f] is not None else "")]
            if diff:
                out["geaendert"].append({"liga": name, "spiel": f"{key[1]} - {key[2]}",
                                         "vorher": {f: _fmt(a.get(f)) for f in diff}, "neu": {f: _fmt(b[f]) for f in diff}})
    out["geaendert"] = out["geaendert"][:200]
    return out


def _fmt(v):
    return v.strftime("%d.%m.%Y") if isinstance(v, datetime) else ("" if v is None else v)


def _completeness(sheets: dict[str, list[dict]], db, today: date) -> dict:
    """Je Liga die Spieltage mit fälligen Spielen der letzten 14 Tage: fällig, geliefert, verschoben/abgesagt, fehlt."""
    out = {}
    for name, rows in sheets.items():
        df = db.leagues.get(name)
        played = set() if df is None else set(zip(df["Season"], df["homeTeam"], df["awayTeam"]))
        per = {}
        for r in rows:
            von, bis = r["Datum von"].date(), r["Datum bis"].date()
            if not (today - timedelta(days=E.HISTORY_DAYS) <= von and bis < today):
                continue
            p = per.setdefault(r["Spieltag"], {"spieltag": r["Spieltag"], "faellig": 0, "geliefert": 0, "inaktiv": 0,
                                               "fehlt": 0, "fehlende": [], "inaktive": []})
            if r["Status"]:
                p["inaktiv"] += 1
                p["inaktive"].append(f"{r['Heimmannschaft']} - {r['Gastmannschaft']} ({r['Status']})")
                continue
            p["faellig"] += 1
            if (r["Saison"], r["Heimmannschaft"], r["Gastmannschaft"]) in played:
                p["geliefert"] += 1
            else:
                p["fehlt"] += 1
                p["fehlende"].append(f"{r['Heimmannschaft']} - {r['Gastmannschaft']} ({r['Datum von'].strftime('%d.%m.')})")
        out[name] = [per[k] for k in sorted(per)]
    return out


def save_report(report: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
