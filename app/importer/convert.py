"""Ein Spiel von API-Football -> eine Zeile mit den 58 Spalten der Datenbank (Spezifikation, Abschnitt 5).

Regeln:
- Datum und Anstosszeit in Europe/Zurich (die API wird mit timezone=Europe/Zurich abgefragt).
- Spieltag aus der Runde „Regular Season – N“; Saison „2026“ -> „2026/2027“.
- Tore: Endstand (K/L = N/O), Halbzeit, 2. Halbzeit = Endstand − Halbzeit, Ergebnisbuchstaben H/D/A.
- Statistik: leerer Wert bleibt leer (nie 0). Ausnahme Gelbe Karten (E13): ist der Wert leer, aber das Spiel hat
  Statistik und Ereignisse, werden die Karten aus den Ereignissen gezählt (keine Karte = sichere 0).
- Halbzeitwerte aus der Halbzeit-Statistik (ab 2024); Gelbe Karten sonst aus den Ereignissen (Minute ≤ 45 = 1. HZ,
  auch Nachspielzeit der 1. Halbzeit).
"""

from __future__ import annotations

from datetime import datetime

from core import schema

from . import einstellungen as E
from .teams import TeamNames

FINISHED = ("FT", "AET", "PEN")
AWARDED = ("AWD", "WO")
STATS = {"Corners": "Corner Kicks", "Yellow Cards": "Yellow Cards", "Ball Possession": "Ball Possession",
         "Team Shots": "Total Shots", "Shots on Target": "Shots on Goal", "Shots off Target": "Shots off Goal"}
PERIOD = {"Full Time": "statistics", "First Half": "statistics_1h", "Second Half": "statistics_2h"}


def season_label(api_season: int) -> str:
    return f"{api_season}/{api_season + 1}"


def round_number(round_name: str) -> int | None:
    """„Regular Season - 12“ -> 12; andere Runden (z. B. Relegation „Final“) -> None."""
    if not round_name.startswith("Regular Season"):
        return None
    tail = round_name.rsplit("-", 1)[-1].strip()
    return int(tail) if tail.isdigit() else None


def result(home, away) -> str | None:
    if home is None or away is None:
        return None
    return "H" if home > away else "A" if home < away else "D"


def number(value):
    """API-Wert als Zahl: '55%' -> 55, '2.14' -> 2.14; leer bleibt None."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return value
    text = str(value).strip().rstrip("%")
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return None


def yellow_from_events(fixture: dict, team_id: int) -> dict[str, int]:
    out = {"Full Time": 0, "First Half": 0, "Second Half": 0}
    for e in fixture.get("events") or []:
        if e.get("type") == "Card" and e.get("detail") == "Yellow Card" and (e.get("team") or {}).get("id") == team_id:
            out["Full Time"] += 1
            minute = (e.get("time") or {}).get("elapsed") or 0
            out["First Half" if minute <= 45 else "Second Half"] += 1
    return out


def fixture_row(fixture: dict, league: str, names: TeamNames, half: dict | None = None) -> dict:
    """fixture: Spiel aus fixtures?ids=… (mit statistics und events); half: Antwort von fixtures/statistics?half=true
    (Liste je Team mit statistics_1h/statistics_2h) oder None. Gibt {Spalte: Wert} für alle 58 Spalten zurück."""
    fx, sc, lg = fixture["fixture"], fixture["score"], fixture["league"]
    when = datetime.fromisoformat(fx["date"])
    home, away = fixture["teams"]["home"], fixture["teams"]["away"]
    ft, ht = sc.get("fulltime") or {}, sc.get("halftime") or {}
    fth, fta = ft.get("home"), ft.get("away")
    if fth is None or fta is None:
        fth, fta = fixture["goals"]["home"], fixture["goals"]["away"]
    hth, hta = ht.get("home"), ht.get("away")
    sh = fth - hth if None not in (fth, hth) else None
    sa = fta - hta if None not in (fta, hta) else None
    referee = (fx.get("referee") or "").split(",")[0].strip() or None
    row = {
        "Date": datetime(when.year, when.month, when.day), "Gameday": round_number(lg["round"]), "id": int(fx["id"]),
        "matchDate": when.strftime("%d-%m-%y %H:%M"), "Country": E.COUNTRY[league], "League": league,
        "Season": season_label(int(lg["season"])), "homeTeam": names.name(home), "awayTeam": names.name(away),
        "referee": referee,
        "FT Home Goals": fth, "FT Away Goals :": fta, "FT Result :": result(fth, fta),
        "Full-Time Home Goals": fth, "Full-Time Away Goals": fta, "Full-Time Result": result(fth, fta),
        "First-Half Home Goals": hth, "First-Half Away Goals": hta, "First-Half Result": result(hth, hta),
        "Second-Half Home Goals": sh, "Second-Half Away Goals": sa, "Second-Half Result": result(sh, sa),
    }
    stats = {s["team"]["id"]: {x["type"]: x["value"] for x in s.get("statistics") or []}
             for s in fixture.get("statistics") or []}
    halves = {}
    for t in half or []:
        halves[t["team"]["id"]] = {p: {x["type"]: x["value"] for x in t.get(key) or []}
                                   for p, key in PERIOD.items() if p != "Full Time"}
    has_events = bool(fixture.get("events"))
    for side, team in (("Home", home), ("Away", away)):
        tid = team["id"]
        st, hv = stats.get(tid), halves.get(tid)
        cards = yellow_from_events(fixture, tid) if has_events else None
        for col_key, api_name in STATS.items():
            for period in PERIOD:
                if period == "Full Time":
                    value = number(st.get(api_name)) if st else None
                else:
                    value = number(hv[period].get(api_name)) if hv else None
                if col_key == "Yellow Cards" and value is None and cards is not None and st is not None:
                    value = cards[period]
                row[f"{side} {col_key} {period}"] = value
    assert set(row) == set(schema.EXPECTED_COLUMNS), set(schema.EXPECTED_COLUMNS) ^ set(row)
    return row


def as_list(row: dict) -> list:
    """Zeile in der Spaltenreihenfolge der Datenbank."""
    return [row[c] for c in schema.EXPECTED_COLUMNS]
