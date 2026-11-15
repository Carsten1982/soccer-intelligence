"""Spielplan aus der Spielliste der API (Format 04_Spielplan.md; Entscheidungen Carsten 15.11.2026).

- Ein Blatt je Liga, alle Spiele der laufenden Saison (Runden „Regular Season“), auch die gespielten.
- Hauptzeitraum je Spieltag: das Fenster von höchstens 4 Tagen (z. B. Freitag bis Montag) mit den meisten Spielen;
  Datum von/bis = erster und letzter Tag dieses Fensters.
- Bekannter Termin innerhalb von 3 Tagen um den Hauptzeitraum: Datum von = Datum bis = Spieltag des Spiels.
- Termin mehr als 3 Tage ausserhalb (vorgezogen oder nachgeholt): Status „verschoben“, Datum von/bis = Hauptzeitraum
  (Regel 04, Abschnitt 6).
- Status der API: PST -> verschoben, CANC -> abgesagt, ABD -> abgebrochen (E9); sonst leer (= geplant).
- Zusätzliche Spalten Anstoss und API-ID (werden von der App ignoriert).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from .convert import round_number, season_label
from .teams import TeamNames

COLUMNS = ["Saison", "Spieltag", "Datum von", "Datum bis", "Heimmannschaft", "Gastmannschaft", "Status", "Anstoss",
           "API-ID"]
STATUS = {"PST": "verschoben", "CANC": "abgesagt", "ABD": "abgebrochen"}
WINDOW = 3          # Fenster: Starttag + 3 Tage (4 Kalendertage)
TOLERANCE = 3       # bis 3 Tage ausserhalb bleibt ein Spiel im Spieltag


def main_period(days: list[date]) -> tuple[date, date] | None:
    """Fenster von höchstens 4 Tagen mit den meisten Spielen (bei Gleichstand das früheste)."""
    if not days:
        return None
    best = None
    for start in sorted(set(days)):
        inside = [d for d in days if start <= d <= start + timedelta(days=WINDOW)]
        if best is None or len(inside) > len(best):
            best = inside
    return min(best), max(best)


def fixture_rows(season_list: list[dict], names: TeamNames) -> list[dict]:
    games = [f for f in season_list if round_number(f["league"]["round"]) is not None]
    by_round: dict[int, list[dict]] = {}
    for f in games:
        by_round.setdefault(round_number(f["league"]["round"]), []).append(f)
    rows = []
    for rnd in sorted(by_round):
        fs = by_round[rnd]
        when = {f["fixture"]["id"]: datetime.fromisoformat(f["fixture"]["date"]) for f in fs}
        regular = [when[f["fixture"]["id"]].date() for f in fs if f["fixture"]["status"]["short"] not in STATUS]
        period = main_period(regular) or main_period([w.date() for w in when.values()])
        for f in sorted(fs, key=lambda x: (when[x["fixture"]["id"]], x["fixture"]["id"])):
            d = when[f["fixture"]["id"]]
            status = STATUS.get(f["fixture"]["status"]["short"], "")
            outside = d.date() < period[0] - timedelta(days=TOLERANCE) or d.date() > period[1] + timedelta(days=TOLERANCE)
            if status or outside:
                von, bis = period
                status = status or "verschoben"
            else:
                von = bis = d.date()
            rows.append({"Saison": season_label(int(f["league"]["season"])), "Spieltag": rnd,
                         "Datum von": datetime(von.year, von.month, von.day), "Datum bis": datetime(bis.year, bis.month, bis.day),
                         "Heimmannschaft": names.name(f["teams"]["home"]), "Gastmannschaft": names.name(f["teams"]["away"]),
                         "Status": status, "Anstoss": d.strftime("%H:%M"), "API-ID": int(f["fixture"]["id"])})
    return rows
