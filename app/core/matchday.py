"""Aktueller Spieltag und Spieltagsübersicht.

Regeln: Dashboard-Briefing (docs/05_Dashboard.md), Kapitel 4.4, und docs/04_Spielplan.md, Abschnitt 4.

1. Ein Spieltag ist beendet, sobald das späteste „Datum bis“ seiner Spiele vor dem heutigen Datum liegt.
2. Angezeigt wird der Spieltag mit der niedrigsten Nummer, der noch nicht beendet ist.
3. Sind alle Spieltage beendet, wird der letzte Spieltag der Datei angezeigt.
4. Spiele mit Status „verschoben“ oder „abgesagt“ zählen nicht für die Frage, ob ein Spieltag beendet ist.
8. Sortierung innerhalb eines Spieltags: nach „Datum von“, danach Reihenfolge der Datei.

„Heute“ wird immer als Parameter übergeben (Zeitzone Europe/Zurich, siehe state.today()).
So lassen sich alle Regeln mit festen Daten testen.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from .fixtures import INACTIVE_STATUS

ENDED = "beendet"
CURRENT = "aktuell"
UPCOMING = "kommend"


@dataclass(frozen=True)
class Matchday:
    saison: str
    spieltag: int
    erstes_datum: date      # frühestes „Datum von“
    letztes_datum: date     # spätestes „Datum bis“
    anzahl: int             # Anzahl Begegnungen in der Datei
    beendet: bool
    status: str             # beendet / aktuell / kommend

    @property
    def key(self) -> tuple[str, int]:
        return self.saison, self.spieltag


def _is_ended(games: pd.DataFrame, today: date) -> bool:
    counted = games[~games["status"].isin(INACTIVE_STATUS)]
    if counted.empty:
        # Alle Spiele verschoben/abgesagt: Der Spieltag blockiert die Anzeige nicht.
        return True
    return counted["datum_bis"].max() < today


def matchday_overview(fixtures: pd.DataFrame, today: date) -> list[Matchday]:
    """Alle Spieltage einer Liga, sortiert nach Saison und Spieltag, mit Status."""
    if fixtures is None or fixtures.empty:
        return []
    raw = []
    for (season, md), games in fixtures.groupby(["saison", "spieltag"], sort=True):
        raw.append((season, int(md), games["datum_von"].min(), games["datum_bis"].max(),
                    len(games), _is_ended(games, today)))
    current = _current_key(raw)
    return [
        Matchday(s, md, first, last, n, ended,
                 CURRENT if (s, md) == current else ENDED if ended else UPCOMING)
        for s, md, first, last, n, ended in raw
    ]


def _current_key(raw: list[tuple]) -> tuple[str, int] | None:
    if not raw:
        return None
    for season, md, *_rest, ended in raw:          # raw ist nach (Saison, Spieltag) sortiert
        if not ended:
            return season, md                       # Regel 2
    return raw[-1][0], raw[-1][1]                   # Regel 3


def current_matchday(fixtures: pd.DataFrame, today: date) -> Matchday | None:
    for md in matchday_overview(fixtures, today):
        if md.status == CURRENT:
            return md
    return None


def matchday_games(fixtures: pd.DataFrame, saison: str, spieltag: int) -> pd.DataFrame:
    """Begegnungen eines Spieltags, sortiert nach „Datum von“, dann Reihenfolge der Datei (Regel 8)."""
    games = fixtures[(fixtures["saison"] == saison) & (fixtures["spieltag"] == spieltag)]
    return games.sort_values(["datum_von", "reihenfolge"], kind="stable").reset_index(drop=True)


def season_short(season: str) -> str:
    """„2026/2027“ -> „2026/27“."""
    start, end = season.split("/")
    return f"{start}/{end[-2:]}"


def date_range(first: date, last: date) -> str:
    if first == last:
        return f"{first:%d.%m.%Y}"
    if first.year == last.year:
        return f"{first:%d.%m.} – {last:%d.%m.%Y}"
    return f"{first:%d.%m.%Y} – {last:%d.%m.%Y}"
