"""Spielplan aus den Spiellisten der API (Format 04_Spielplan.md; Spezifikation Spielplan v2.1, Abschnitt 3).

Seit Version 0.15 (Entscheidungen Carsten 15.11.2026, S1–S6):
- Ein Blatt je Liga mit der **laufenden Saison und der Vorsaison** (Runden „Regular Season“), auch gespielte Spiele.
- **Status nur aus der API** (S1). Der Originalcode steht in der Spalte `API-Status`; daraus wird der Spielplan-Status
  abgeleitet. Die frühere Regel „mehr als 3 Tage ausserhalb = verschoben“ gibt es nicht mehr: Nachholspiele haben bei der
  API keinen eigenen Status und bekamen so fälschlich keine KPIs.
- **Datum von = Datum bis = Termin laut API**, für alle Spiele (auch verschobene: die API liefert den alten Termin weiter).
- **Hinweis** (nur Anzeige): „Nachholspiel“ bzw. „vorgezogen“, wenn der Termin mehr als 3 Tage nach bzw. vor dem
  Hauptzeitraum liegt. Hauptzeitraum = Fenster von höchstens 4 Tagen mit den meisten regulären Spielen, bei Gleichstand
  das frühere. Ohne reguläre Spiele gibt es keinen Hauptzeitraum und keinen Hinweis (S5).
- **Termin** (S2): „Zeit offen“ bei API-Status TBD; „vorläufig“, wenn alle Spiele des Spieltags denselben Termin haben
  und dieser mehr als 14 Tage entfernt ist (Platzhalter der API; am letzten Spieltag spielen alle tatsächlich gleich-
  zeitig, darum die 14-Tage-Grenze); sonst „bestätigt“.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from .convert import round_number, season_label
from .einstellungen import PLACEHOLDER_DAYS
from .teams import TeamNames

COLUMNS = ["Saison", "Spieltag", "Datum von", "Datum bis", "Heimmannschaft", "Gastmannschaft", "Status", "Anstoss",
           "Termin", "Hinweis", "API-Status", "API-ID"]
# API-Status -> Spielplan-Status (S1); alle anderen Codes (NS, TBD, laufend, FT …) -> geplant (leer)
STATUS = {"PST": "verschoben", "CANC": "abgesagt", "ABD": "abgebrochen", "SUSP": "ausgesetzt",
          "AWD": "gewertet", "WO": "gewertet"}
CATCHUP, EARLY = "Nachholspiel", "vorgezogen"
CONFIRMED, TIME_OPEN, PROVISIONAL = "bestätigt", "Zeit offen", "vorläufig"
WINDOW = 3          # Fenster: Starttag + 3 Tage (4 Kalendertage)
TOLERANCE = 3       # bis 3 Tage ausserhalb gehört ein Spiel regulär zum Spieltag


def main_period(days: list[date]) -> tuple[date, date] | None:
    """Fenster von höchstens 4 Tagen mit den meisten Spielen (bei Gleichstand das früheste); None ohne Spiele."""
    if not days:
        return None
    best = None
    for start in sorted(set(days)):
        inside = [d for d in days if start <= d <= start + timedelta(days=WINDOW)]
        if best is None or len(inside) > len(best):
            best = inside
    return min(best), max(best)


def fixture_rows(season_list: list[dict], names: TeamNames, today: date) -> list[dict]:
    """Zeilen des Spielplans (Spalten COLUMNS) aus einer Spielliste der API."""
    games = [f for f in season_list if round_number(f["league"]["round"]) is not None]
    by_round: dict[int, list[dict]] = {}
    for f in games:
        by_round.setdefault(round_number(f["league"]["round"]), []).append(f)
    rows = []
    for rnd in sorted(by_round):
        fs = by_round[rnd]
        when = {f["fixture"]["id"]: datetime.fromisoformat(f["fixture"]["date"]) for f in fs}
        regular = [when[f["fixture"]["id"]].date() for f in fs if f["fixture"]["status"]["short"] not in STATUS]
        period = main_period(regular)                                    # S5: ohne reguläre Spiele kein Zeitraum
        placeholder = len(fs) > 1 and len({f["fixture"]["date"] for f in fs}) == 1
        for f in sorted(fs, key=lambda x: (when[x["fixture"]["id"]], x["fixture"]["id"])):
            d = when[f["fixture"]["id"]]
            short = f["fixture"]["status"]["short"]
            status = STATUS.get(short, "")
            hint = ""
            if period and not status:
                if d.date() > period[1] + timedelta(days=TOLERANCE):
                    hint = CATCHUP
                elif d.date() < period[0] - timedelta(days=TOLERANCE):
                    hint = EARLY
            if short == "TBD":
                termin = TIME_OPEN
            elif placeholder and (d.date() - today).days > PLACEHOLDER_DAYS:
                termin = PROVISIONAL
            else:
                termin = CONFIRMED
            day = datetime(d.year, d.month, d.day)
            rows.append({"Saison": season_label(int(f["league"]["season"])), "Spieltag": rnd,
                         "Datum von": day, "Datum bis": day,
                         "Heimmannschaft": names.name(f["teams"]["home"]), "Gastmannschaft": names.name(f["teams"]["away"]),
                         "Status": status, "Anstoss": d.strftime("%H:%M"), "Termin": termin, "Hinweis": hint,
                         "API-Status": short, "API-ID": int(f["fixture"]["id"])})
    return rows
