"""Neue Fassung von Datenbank und Spielplan erzeugen, mit Bericht.

Grundlagen: Spezifikation Datenlieferung (`06`, Abschnitt 10), Spezifikation Ergebnis-Import v1.1 (R1–R9) und
Spezifikation Spielplan v2.1 (Abschnitt 3), Entscheidungen Carsten 15.11.2026.

Ablauf je Lauf:
1. Gültige Datenbank lesen (nie verändern); Teamnamen nach `teamnamen.toml` vereinheitlichen.
2. Je Liga: laufende Saison bestimmen, Spielliste der laufenden Saison und der Vorsaison holen.
3. Neue beendete Spiele aufnehmen (id = API-Fixture-ID). Passt der Endstand nicht zu den Tor-Ereignissen, wartet das
   Spiel auf einen Entscheid im Reiter (R2).
4. Spiele mit API-ID neu prüfen (letzte 2 Spieltage, montags die ganze Saison, unvollständige Statistik):
   - bis 7 Tage nach dem Spiel übernimmt der Import Korrekturen selbst (Korrekturfenster, R1);
   - danach ist das Spiel eingefroren: Eine Änderung wird nur mit Entscheid übernommen;
   - ein leerer API-Wert überschreibt nie einen vorhandenen; der Altbestand (eigene IDs) wird nie verändert.
5. Spielplan aus den Spiellisten erzeugen (Status nur aus der API, Hinweis, Termin, Vorsaison).
6. Beide Dateien als neue Fassung speichern und prüfen: Prüfregeln aus `02` und `04`, Plausibilität neuer und
   geänderter Spiele (R6), IDs über alle Ligen (R8), Zuordnung Spielplan ↔ Datenbank (S6), verschwundene Spiele.
7. Bericht: Vollständigkeit, Qualität, neue Spiele, Korrekturen, späte Korrekturen, kritische Punkte, Spielplan-
   Änderungen nach Gruppen, offene Spiele mit fehlenden KPI-Feldern, Freigabe-Klasse für den Automatikbetrieb (R5).
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

import openpyxl
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from core import schema, settings
from core.config import League, load_teams
from core.fixtures import load_fixtures
from core.loader import load_database
from core.zuordnung import API_ID_FROM, db_id, load_mapping

from . import einstellungen as E
from . import entscheide
from .client import ApiClient
from .convert import AWARDED, FINISHED, as_list, fixture_row, goal_events, final_score, round_number, season_label
from .spielplan import COLUMNS as FX_COLUMNS
from .spielplan import fixture_rows
from .teams import TeamNames

KPI_STATS = ("Corners", "Yellow Cards", "Shots on Target")
KPI_STAT_LABEL = {"Corners": "Ecken", "Yellow Cards": "Gelbe Karten", "Shots on Target": "Schüsse aufs Tor"}
HALF_FROM = 2024                 # Halbzeit-Statistik liefert die API ab Saison 2024/25
GOAL_COLUMNS = ("FT Home Goals", "FT Away Goals :", "FT Result :", "Full-Time Home Goals", "Full-Time Away Goals",
                "Full-Time Result", "First-Half Home Goals", "First-Half Away Goals", "First-Half Result",
                "Second-Half Home Goals", "Second-Half Away Goals", "Second-Half Result")
# KPI-relevante Spalten (R5): Änderungen daran werden im Bericht hervorgehoben
KPI_COLUMNS = set(GOAL_COLUMNS) | {f"{s} {k} Full Time" for s in ("Home", "Away") for k in KPI_STATS} | {
    "Date", "Gameday", "homeTeam", "awayTeam"}


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _same(a, b) -> bool:
    if isinstance(a, datetime) and isinstance(b, datetime):
        return a.date() == b.date()
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return float(a) == float(b)
    return a == b


def _out(v):
    return v.strftime("%d.%m.%Y") if isinstance(v, datetime) else v


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


def missing_kpi_fields(row: dict) -> list[str]:
    """Welche KPI-Statistiken fehlen (R4: der Bericht nennt sie)."""
    return [KPI_STAT_LABEL[k] for k in KPI_STATS if any(row.get(f"{s} {k} Full Time") is None for s in ("Home", "Away"))]


def plausibility(row: dict) -> tuple[list[str], list[str]]:
    """Plausibilität eines neuen oder geänderten Spiels (R6). Gibt (Fehler, Warnungen) zurück."""
    errors, warnings = [], []
    for c in schema.EXPECTED_COLUMNS:
        v = row.get(c)
        if isinstance(v, (int, float)) and not isinstance(v, bool) and v < 0:
            errors.append(f"negativer Wert in {c}")
    for side, ft, ht in (("Heim", "FT Home Goals", "First-Half Home Goals"), ("Gast", "FT Away Goals :", "First-Half Away Goals")):
        if row.get(ft) is not None and row.get(ht) is not None and row[ht] > row[ft]:
            errors.append(f"{side}: Halbzeit-Tore ({row[ht]}) grösser als Endstand ({row[ft]})")
    for s in ("Home", "Away"):
        on, total = row.get(f"{s} Shots on Target Full Time"), row.get(f"{s} Team Shots Full Time")
        if on is not None and total is not None and on > total:
            errors.append(f"{s}: Schüsse aufs Tor ({on}) grösser als Schüsse gesamt ({total})")
        for key, limit in E.LIMITS.items():
            v = row.get(("FT Home Goals" if s == "Home" else "FT Away Goals :") if key == "Goals" else f"{s} {key} Full Time")
            if v is not None and v > limit:
                warnings.append(f"{s}: {key} {v} (mehr als {limit})")
    return errors, warnings


def _issues(load) -> dict:
    return {"fehler": load.count("Fehler"), "warnungen": load.count("Warnung"), "hinweise": load.count("Hinweis")}


def _season_list(client: ApiClient, lid: int, year: int) -> list[dict]:
    return client.get("fixtures", {"league": lid, "season": year, "timezone": E.TIMEZONE})["response"]


def build(client: ApiClient, names: TeamNames, leagues: list[League], db_path: Path, fx_path: Path, out_dir: Path,
          today: date, full_season: bool, decisions: list[dict] | None = None,
          mapping: dict[str, dict[int, int]] | None = None, recheck: bool = True, jetzt: datetime | None = None) -> dict:
    """Erzeugt out_dir/Database-Soccer-Intelligence.xlsx und out_dir/Spielplan.xlsx; gibt den Bericht zurück.
    recheck=False (seit 0.22, Lauf nach dem Spiel): nur neue Spiele und Spiele mit fehlenden Werten holen, die letzten
    2 Spieltage nicht neu prüfen (das macht der Kontrolllauf um 04:00)."""
    decisions = decisions or []
    mapping = load_mapping() if mapping is None else mapping
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {"basis": {"datenbank": sha256(db_path), "spielplan": sha256(fx_path) if fx_path.exists() else None},
              "ganze_saison": full_season, "neupruefung": recheck, "nicht_beendet": [], "neue_spiele": {}, "korrekturen": [], "spaete_korrekturen": [],
              "kritisch": [], "plausibilitaet": {"fehler": [], "warnungen": []}, "offen": [], "wertungen": [],
              "umbenennungen": [], "spielplan_aenderungen": {}, "vollstaendigkeit": {}, "saison": {}}
    try:
        st = client.get("status", {})["response"]
        report["abo"] = {"plan": st["subscription"]["plan"], "bis": st["subscription"]["end"][:10],
                         "aktiv": st["subscription"]["active"]}
    except Exception as exc:                                  # Status ist nur Information
        report["abo"] = {"fehler": str(exc)}
    wb = openpyxl.load_workbook(db_path)
    active = [lg for lg in leagues if lg.aktiv and lg.name in E.LEAGUE_IDS]

    # 1. Teamnamen vereinheitlichen (erste Übernahme und spätere Schreibweisen, z. B. mit Akzent)
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

    fixture_sheets, api_lists = {}, {}
    for lg in active:
        lid = E.LEAGUE_IDS[lg.name]
        seasons = client.get("leagues", {"id": lid, "current": "true"})["response"][0]["seasons"]
        year = next(s["year"] for s in seasons if s.get("current"))
        label = season_label(year)
        report["saison"][lg.name] = label
        season_list = _season_list(client, lid, year)
        previous = _season_list(client, lid, year - 1)                 # Vorsaison für den Spielplan (3.6)
        api_lists[lg.name] = previous + season_list
        fixture_sheets[lg.name] = fixture_rows(previous, names, today) + fixture_rows(season_list, names, today)
        _league(client, names, lg, wb[lg.name], season_list, label, year, today, full_season, decisions, mapping, report,
                recheck)
        report["nicht_beendet"] += _not_finished(season_list, lg.name, jetzt)

    db_out = out_dir / settings.DATABASE_FILENAME
    for lg in active:                                       # Filterbereich wächst mit (L9)
        ws = wb[lg.name]
        if ws.auto_filter.ref:
            ws.auto_filter.ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"
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
    new_warnings = [{"stufe": i.level, "liga": i.sheet, "pruefung": i.check, "meldung": i.message}
                    for i in new_db.issues if i.level != "Hinweis" and (i.level, i.sheet, i.check, i.match_id) not in seen]
    report["pruefung"] = {
        "datenbank": {"gueltig": _issues(old_db), "neu": _issues(new_db), "neue_meldungen": new_warnings[:50]},
        "spielplan": {"gueltig": _issues(old_fx) if old_fx else None, "neu": _issues(new_fx),
                      "meldungen": [{"stufe": i.level, "liga": i.sheet, "pruefung": i.check, "meldung": i.message}
                                    for i in new_fx.issues if i.level != "Hinweis"][:50]}}
    waiting = {k["id"] for k in report["kritisch"] if k["art"] in ("endstand", "zuordnung")}
    links = _links(fixture_sheets, new_db, mapping, waiting)
    report["zuordnung"] = links["fehler"][:50]
    report["doppelte_ids"] = _duplicate_ids(new_db)
    report["vollstaendigkeit"] = _completeness(fixture_sheets, links["ids"], today, report)
    report["unbekannte_teams"] = [{"api_team_id": k, "name": v} for k, v in names.unknown.items()]
    report["namensaenderungen_api"] = [{"api_team_id": k, "festgehalten": a, "api": b} for k, (a, b) in names.changed.items()]
    report["fehler"] = (new_db.count("Fehler") + new_fx.count("Fehler") + len(report["plausibilitaet"]["fehler"])
                        + len(links["fehler"]) + len(report["doppelte_ids"]))
    report["automatik"] = _automatic(report, [w for w in new_warnings if w["pruefung"] not in NICHT_SPERREND])
    report["dateien"] = {"datenbank": sha256(db_out), "spielplan": sha256(fx_out)}
    return report


def _league(client, names, lg, ws, season_list, label, year, today, full_season, decisions, mapping, report,
            recheck=True) -> None:
    """Neue Spiele, Neuprüfung, Korrekturen und kritische Punkte einer Liga (Datenbankblatt ws wird verändert)."""
    head = [c.value for c in ws[1]]
    col = {h: i for i, h in enumerate(head)}
    by_id, by_pair = {}, {}
    for row in ws.iter_rows(min_row=2):
        rid = row[col["id"]].value
        if rid is None:
            continue
        by_id[int(rid)] = row
        if row[col["Season"]].value == label:
            by_pair[(row[col["homeTeam"]].value, row[col["awayTeam"]].value)] = row
    regular = [f for f in season_list if round_number(f["league"]["round"]) is not None]
    done = [f for f in regular if f["fixture"]["status"]["short"] in FINISHED]
    recent = set(sorted({round_number(f["league"]["round"]) for f in done})[-E.RECHECK_ROUNDS:])
    api_ids = {f["fixture"]["id"] for f in season_list}
    new, check = [], []
    for f in regular:
        fid, short = f["fixture"]["id"], f["fixture"]["status"]["short"]
        key = (names.name(f["teams"]["home"]), names.name(f["teams"]["away"]))
        when = datetime.fromisoformat(f["fixture"]["date"])
        if short in ("NS", "TBD") and when.date() < today - timedelta(days=1):
            report["kritisch"].append({"art": "status_offen", "liga": lg.name, "id": fid, "spiel": f"{key[0]} - {key[1]}",
                                       "text": f"API meldet „noch nicht gespielt“, Termin war {when:%d.%m.%Y}"})
        if short in AWARDED:
            report["wertungen"].append({"liga": lg.name, "id": fid, "spiel": f"{key[0]} - {key[1]}",
                                        "hinweis": "gewertet (AWD/WO): nicht in die Datenbank, Spielplan-Status „gewertet“ (R2)"})
            continue
        if short not in FINISHED:
            continue
        row = _find(by_id, lg.name, fid, mapping)
        if row is None and key in by_pair:                    # Paarung vorhanden, aber ID passt nicht (S6)
            report["kritisch"].append({"art": "zuordnung", "liga": lg.name, "id": fid, "spiel": f"{key[0]} - {key[1]}",
                                       "text": f"Paarung steht mit id {by_pair[key][col['id']].value} in der Datenbank, "
                                               f"die API-ID {fid} ist aber nicht zugeordnet"})
            continue
        if row is None:
            new.append(f)
        elif int(row[col["id"]].value) >= API_ID_FROM:
            values = {h: row[col[h]].value for h in head}
            if full_season or (recheck and round_number(f["league"]["round"]) in recent) or missing_kpi_fields(values):
                check.append(f)
    # verschwundene Spiele (R5, L12): API-Spiel der laufenden Saison in der Datenbank, aber nicht mehr in der Liste
    for rid, row in by_id.items():
        if rid >= API_ID_FROM and row[col["Season"]].value == label and rid not in api_ids:
            report["kritisch"].append({"art": "verschwunden", "liga": lg.name, "id": rid,
                                       "spiel": f"{row[col['homeTeam']].value} - {row[col['awayTeam']].value}",
                                       "text": "Spiel steht in der Datenbank, fehlt aber in der Spielliste der API "
                                               "(nicht gelöscht; bitte prüfen)"})
    wanted = [f["fixture"]["id"] for f in new + check]
    details = {}
    for i in range(0, len(wanted), 20):
        chunk = wanted[i:i + 20]
        for d in client.get("fixtures", {"ids": "-".join(map(str, chunk)), "timezone": E.TIMEZONE})["response"]:
            details[d["fixture"]["id"]] = d
    halves = {}
    if year >= HALF_FROM:
        for f in new + check:
            if f in new or not recheck or round_number(f["league"]["round"]) in recent:
                fid = f["fixture"]["id"]
                halves[fid] = client.get("fixtures/statistics", {"fixture": fid, "half": "true"})["response"]

    # neue Spiele anhängen (nach Datum)
    fmt = ws.cell(row=ws.max_row, column=col["Date"] + 1).number_format
    added = []
    for fid in sorted((f["fixture"]["id"] for f in new), key=lambda x: details[x]["fixture"]["date"] if x in details else ""):
        if fid not in details:
            continue
        d = details[fid]
        mode = _score_mode(d, lg.name, decisions, report)
        if mode is None:                                      # wartet auf Entscheid (R2): nicht aufnehmen
            continue
        row = fixture_row(d, lg.name, names, halves.get(fid), score_from_events=mode == "platz")
        _check_row(row, lg.name, report)
        ws.append(as_list(row))
        ws.cell(row=ws.max_row, column=col["Date"] + 1).number_format = fmt
        added.append(_short(row))
        if missing_kpi_fields(row):
            report["offen"].append({"liga": lg.name, **_short(row), "fehlt": missing_kpi_fields(row),
                                    "grund": "Statistik noch unvollständig"})
    report["neue_spiele"][lg.name] = added

    # Spiele mit API-ID neu prüfen
    for f in check:
        fid = f["fixture"]["id"]
        if fid not in details:
            continue
        d = details[fid]
        cells = _find(by_id, lg.name, fid, mapping)
        old = {c: cells[col[c]].value for c in schema.EXPECTED_COLUMNS}
        api_row = fixture_row(d, lg.name, names, halves.get(fid))
        age = (today - old["Date"].date()).days if isinstance(old["Date"], datetime) else 0
        goal_change = any(api_row[c] is not None and not _same(old[c], api_row[c]) for c in GOAL_COLUMNS)
        decided_platz = False
        if goal_change and _events_disagree(d):
            mode = _score_mode(d, lg.name, decisions, report)
            if mode == "platz":
                decided_platz = True
            elif mode is None:
                goal_change = None                            # Tore nicht ändern, bis entschieden ist
        if decided_platz:
            api_row = fixture_row(d, lg.name, names, halves.get(fid), score_from_events=True)
        changed = False
        for c in schema.EXPECTED_COLUMNS:
            val = api_row[c]
            if val is None or _same(old[c], val):             # leerer API-Wert überschreibt nie (Grundsatz 4)
                continue
            if goal_change is None and c in GOAL_COLUMNS:
                continue
            entry = {"liga": lg.name, "id": fid, "spiel": f"{api_row['homeTeam']} - {api_row['awayTeam']}",
                     "datum": api_row["Date"].strftime("%d.%m.%Y"), "spalte": c, "alt": _out(old[c]), "neu": _out(val),
                     "kpi": c in KPI_COLUMNS}
            filled = old[c] is None                           # leerer Wert wird gefüllt: immer übernehmen
            if filled or age <= E.CORRECTION_DAYS:
                report["korrekturen"].append({**entry, "art": "nachgeliefert" if filled else "im Korrekturfenster"})
            else:
                decision = entscheide.lookup(decisions, "korrektur", fid, c, _out(val))
                if decision == "ablehnen":
                    continue
                if decision != "uebernehmen":
                    report["spaete_korrekturen"].append(entry)            # eingefroren: wartet auf Entscheid
                    continue
                report["korrekturen"].append({**entry, "art": "Entscheid: übernommen"})
            cells[col[c]].value = val
            changed = True
        merged = {c: cells[col[c]].value for c in schema.EXPECTED_COLUMNS}
        if changed:
            _check_row(merged, lg.name, report)
        if missing_kpi_fields(merged):
            age_txt = "Statistik noch unvollständig" if age <= E.OPEN_DAYS else f"Statistik fehlt seit {age} Tagen"
            report["offen"].append({"liga": lg.name, **_short(merged), "fehlt": missing_kpi_fields(merged), "grund": age_txt})


def _not_finished(season_list: list[dict], league: str, jetzt: datetime | None) -> list[dict]:
    """Spiele, die laufen oder seit über 2 Stunden angepfiffen sein müssten und noch nicht begonnen haben (seit 0.22)."""
    if jetzt is None:
        return []
    out = []
    for f in season_list:
        short = f["fixture"]["status"]["short"]
        when = datetime.fromisoformat(f["fixture"]["date"])
        late = short == "NS" and timedelta(hours=2) < jetzt - when < timedelta(hours=12)   # TBD: ohne Uhrzeit
        if short in LAUFEND or late:
            out.append({"liga": league, "id": f["fixture"]["id"], "status": short, "datum": when.strftime("%d.%m.%Y"),
                        "spiel": f"{f['teams']['home']['name']} - {f['teams']['away']['name']}"})
    return out


def _find(by_id: dict, league: str, fid: int, mapping) -> object | None:
    """Datenbankzeile zu einem API-Spiel: über die Zuordnungsdatei, sonst über die API-ID selbst (neu importiert)."""
    row = by_id.get(db_id(league, fid, mapping))
    return row if row is not None else by_id.get(int(fid))


def _events_disagree(fixture: dict) -> bool:
    goals = goal_events(fixture)
    return goals is not None and goals["Full Time"] != final_score(fixture)


def _score_mode(fixture: dict, league: str, decisions: list[dict], report: dict) -> str | None:
    """Endstand gegen Tor-Ereignisse (R2): „api“ = wie geliefert, „platz“ = aus den Tor-Ereignissen,
    None = Widerspruch ohne Entscheid (Spiel wartet; kritischer Punkt im Bericht)."""
    if not _events_disagree(fixture):
        return "api"
    fid = fixture["fixture"]["id"]
    decision = entscheide.lookup(decisions, "endstand", fid)
    if decision in ("api", "platz"):
        return decision
    goals = goal_events(fixture)
    h, a = final_score(fixture)
    report["kritisch"].append({
        "art": "endstand", "liga": league, "id": fid,
        "spiel": f"{fixture['teams']['home']['name']} - {fixture['teams']['away']['name']}",
        "datum": datetime.fromisoformat(fixture["fixture"]["date"]).strftime("%d.%m.%Y"),
        "api": f"{h}:{a}", "ereignisse": "{}:{}".format(*goals["Full Time"]),
        "text": f"Endstand der API {h}:{a}, laut Tor-Ereignissen {goals['Full Time'][0]}:{goals['Full Time'][1]} "
                "(Wertung am grünen Tisch oder Datenfehler)"})
    return None


def _check_row(row: dict, league: str, report: dict) -> None:
    errors, warnings = plausibility(row)
    who = f"{row['homeTeam']} - {row['awayTeam']} ({row['Date'].strftime('%d.%m.%Y')})"
    report["plausibilitaet"]["fehler"] += [{"liga": league, "id": row["id"], "spiel": who, "meldung": m} for m in errors]
    report["plausibilitaet"]["warnungen"] += [{"liga": league, "id": row["id"], "spiel": who, "meldung": m} for m in warnings]


# Seit 0.22 (Regel 5): Warnungen, die bei frisch gespielten Spielen normal sind, sperren die Übernahme nicht. Leere
# Statistikwerte werden später nachgefüllt (Bericht „offen“), ein angefangener Spieltag wird mit den nächsten Läufen
# vollständig. Sie stehen weiter im Bericht und im Bereich Datenqualität.
NICHT_SPERREND = {"Statistik fehlt", "Spieltag unvollständig"}

# Seit 0.22 (B4): Spiele, die beim Lauf noch laufen oder trotz vergangener Anstosszeit nicht begonnen haben, lösen eine
# Wiederholung aus (Verlängerung, Unterbrechung, Verspätung).
LAUFEND = ("1H", "HT", "2H", "ET", "BT", "P", "INT", "LIVE")


def _automatic(report: dict, new_warnings: list[dict]) -> dict:
    """Freigabe-Klasse für den Automatikbetrieb (R5). Seit 0.22 (F1, Carsten 20.11.2026) sperren kritische Punkte die
    Fassung nicht mehr: Das betroffene Spiel bzw. der Wert ist schon zurückgehalten (Endstand gegen Tor-Ereignisse und
    Zuordnung: nicht aufgenommen; späte Korrektur: nicht geändert; „verschwunden“ und „Status offen“ ändern nichts)
    und wartet im Reiter auf den Entscheid. Fehler und neue Warnungen sperren weiterhin."""
    reasons = []
    if report["fehler"]:
        reasons.append(f"{report['fehler']} Fehler")
    if report["plausibilitaet"]["warnungen"]:
        reasons.append(f"{len(report['plausibilitaet']['warnungen'])} Plausibilitätswarnungen")
    if new_warnings:
        reasons.append(f"{len(new_warnings)} neue Warnungen der Prüfregeln")
    return {"ok": not reasons, "gruende": reasons}


def _duplicate_ids(db) -> list[dict]:
    """Jede id nur einmal, über alle Ligen (R8)."""
    seen: dict[int, str] = {}
    out = []
    for name, df in db.leagues.items():
        for rid in df["id"].dropna():
            rid = int(rid)
            if rid in seen:
                out.append({"id": rid, "ligen": f"{seen[rid]} / {name}"})
            seen[rid] = name
    return out[:50]


def _links(sheets: dict[str, list[dict]], db, mapping, waiting: set | frozenset = frozenset()) -> dict:
    """Verknüpfung Spielplan ↔ Datenbank über die API-ID (S6) und Gegenprüfung der Paarung.
    waiting: Spiele, die auf einen Entscheid warten (kein Fehler, wenn sie noch fehlen)."""
    ids, errors = {}, []
    for name, rows in sheets.items():
        df = db.leagues.get(name)
        if df is None:
            continue
        by_id = {int(r.id): (r.Season, r.homeTeam, r.awayTeam) for r in df[["id", "Season", "homeTeam", "awayTeam"]].itertuples()
                 if r.id == r.id}
        known = mapping.get(name, {})
        linked = set()
        for r in rows:
            api_id = r["API-ID"]
            rid = db_id(name, api_id, mapping)
            game = by_id.get(rid)
            if game is None and int(api_id) in by_id:           # neu importiert (id = API-ID)
                rid, game = int(api_id), by_id[int(api_id)]
            if game is None:                                    # gewertete usw. Spiele fehlen absichtlich (R2)
                if api_id in known and api_id not in waiting and not r["Status"]:
                    errors.append({"liga": name, "api_id": api_id, "id": rid,
                                   "meldung": "zugeordnete id fehlt in der Datenbank"})
                continue
            if game != (r["Saison"], r["Heimmannschaft"], r["Gastmannschaft"]):
                errors.append({"liga": name, "api_id": api_id, "id": rid,
                               "meldung": f"Paarung passt nicht: Spielplan {r['Heimmannschaft']} - {r['Gastmannschaft']}, "
                                          f"Datenbank {game[1]} - {game[2]}"})
                continue
            linked.add(api_id)
        ids[name] = linked
    return {"ids": ids, "fehler": errors}


# --- Spielplan-Änderungen nach Gruppen (Spezifikation Spielplan v2.1, Abschnitt 5) ---------------------------------

GROUPS = {"verschoben": "verschoben", "nachholspiel": "Nachholspiel (neuer Termin)", "vorgezogen": "vorgezogen",
          "termin": "Termin geändert", "status": "ausgesetzt / abgesagt / abgebrochen / gewertet",
          "anstoss": "Anstosszeit geändert", "festgelegt": "Anstosszeiten festgelegt", "vermerk": "Vermerk geändert"}
IMPORTANT = ("verschoben", "nachholspiel", "vorgezogen", "termin", "status")
FIELDS = ("Spieltag", "Datum von", "Datum bis", "Status", "Anstoss", "Termin", "Hinweis")


def _group(a: dict, b: dict, diff: list[str]) -> str:
    if "Status" in diff and b["Status"] == "verschoben":
        return "verschoben"
    if "Status" in diff and b["Status"]:
        return "status"
    if {"Datum von", "Datum bis"} & set(diff):
        return {"Nachholspiel": "nachholspiel", "vorgezogen": "vorgezogen"}.get(b["Hinweis"], "termin")
    if "Anstoss" in diff:
        return "festgelegt" if a.get("Termin") in ("vorläufig", "Zeit offen") and b["Termin"] == "bestätigt" else "anstoss"
    if "Status" in diff or "Hinweis" in diff:
        return {"Nachholspiel": "nachholspiel", "vorgezogen": "vorgezogen"}.get(b["Hinweis"], "vermerk")
    return "vermerk"


def _fixture_changes(fx_path: Path, sheets: dict[str, list[dict]], names: TeamNames) -> dict:
    """Spielplan neu gegen gültig (alte Teamnamen zuerst umbenannt): neue, entfallene und geänderte Spiele in Gruppen."""
    out = {"neu": 0, "entfallen": 0, "gruppen": {k: [] for k in GROUPS}, "wichtig": 0, "geaendert": []}
    if not fx_path.exists():
        out["neu"] = sum(len(r) for r in sheets.values())
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
        fields = [f for f in FIELDS if f in head]               # ältere Spielpläne haben noch nicht alle Spalten
        for key in sorted(set(new) & set(old)):
            a, b = old[key], new[key]
            diff = [f for f in fields if not _same(_blank(a.get(f)), _blank(b[f]))]
            if not diff:
                continue
            group = _group(a, b, diff)
            item = {"liga": name, "spieltag": b["Spieltag"], "spiel": f"{key[1]} - {key[2]}", "gruppe": group,
                    "vorher": {f: _fmt(a.get(f)) for f in diff}, "neu": {f: _fmt(b[f]) for f in diff}}
            out["gruppen"][group].append(item)
            out["geaendert"].append(item)
    out["wichtig"] = sum(len(out["gruppen"][g]) for g in IMPORTANT)
    for g in out["gruppen"]:
        out["gruppen"][g] = out["gruppen"][g][:200]
    out["geaendert"] = out["geaendert"][:200]
    return out


def _blank(v):
    return "" if v is None else v


def _fmt(v):
    return v.strftime("%d.%m.%Y") if isinstance(v, datetime) else ("" if v is None else v)


def _completeness(sheets: dict[str, list[dict]], linked: dict[str, set], today: date, report: dict) -> dict:
    """Je Liga die Spieltage mit fälligen Spielen der letzten 14 Tage: fällig, geliefert, inaktiv, fehlt.
    „Geliefert“ heisst: das Spiel ist über seine API-ID mit einem Datenbank-Eintrag verknüpft (S6)."""
    waiting = {(k["liga"], k["id"]) for k in report.get("kritisch", []) if k["art"] == "endstand"}
    out = {}
    for name, rows in sheets.items():
        done = linked.get(name, set())
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
            if r["API-ID"] in done:
                p["geliefert"] += 1
            else:
                p["fehlt"] += 1
                why = " – wartet auf Entscheid" if (name, r["API-ID"]) in waiting else ""
                p["fehlende"].append(f"{r['Heimmannschaft']} - {r['Gastmannschaft']} ({r['Datum von'].strftime('%d.%m.')}){why}")
        out[name] = [per[k] for k in sorted(per)]
    return out


def save_report(report: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
