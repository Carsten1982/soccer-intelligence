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


def _regular(games: pd.DataFrame) -> pd.DataFrame:
    """Reguläre Spiele (Spielplan v2.1, 4.1): Status geplant und ohne Vermerk Nachholspiel/vorgezogen.

    Sonderspiele zählen seit 0.15 nicht für das Ende eines Spieltags, sonst bliebe ein Spieltag mit einem späten
    Nachholspiel wochenlang „aktuell“. Ältere Spielpläne ohne Spalte Hinweis verhalten sich wie bisher."""
    keep = ~games["status"].isin(INACTIVE_STATUS)
    if "hinweis" in games.columns:
        keep &= games["hinweis"].fillna("").eq("")
    return games[keep]


def _is_ended(games: pd.DataFrame, today: date) -> bool:
    counted = _regular(games)
    if counted.empty:
        # Keine regulären Spiele (alle verschoben/abgesagt oder Sonderspiele): Der Spieltag blockiert die Anzeige nicht.
        return True
    return counted["datum_bis"].max() < today


def matchday_overview(fixtures: pd.DataFrame, today: date) -> list[Matchday]:
    """Alle Spieltage einer Liga, sortiert nach Saison und Spieltag, mit Status.

    Erstes und letztes Datum stammen aus den regulären Spielen (sonst aus allen), damit z. B. ein vorgezogenes Spiel
    den Zeitraum des Spieltags nicht über Wochen streckt."""
    if fixtures is None or fixtures.empty:
        return []
    raw = []
    for (season, md), games in fixtures.groupby(["saison", "spieltag"], sort=True):
        span = _regular(games)
        span = games if span.empty else span
        raw.append((season, int(md), span["datum_von"].min(), span["datum_bis"].max(),
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


# --- Spieltag-Auswahl mit Pfeilen (Änderung 31.10.2026) --------------------------------
#
# Je Liga lassen sich alle Spieltage bis einschliesslich des aktuellen auswählen, nicht in die Zukunft.
# Die Auswahl steht in der Adresse: ?spieltag=1 (bei einer anderen Saison zusätzlich &saison=2025-26).
# Ohne Angabe oder bei ungültiger Angabe gilt der aktuelle Spieltag.

PARAM_MATCHDAY = "spieltag"
PARAM_SEASON = "saison"


@dataclass(frozen=True)
class Selection:
    selected: Matchday
    current: Matchday
    choices: list[Matchday]          # auswählbar, alt -> neu; der letzte ist der aktuelle
    requested_invalid: bool = False  # Adresse nannte einen nicht verfügbaren Spieltag

    @property
    def index(self) -> int:
        return self.choices.index(self.selected)

    @property
    def is_current(self) -> bool:
        return self.selected == self.current

    @property
    def previous(self) -> Matchday | None:
        return self.choices[self.index - 1] if self.index > 0 else None

    @property
    def next(self) -> Matchday | None:
        return self.choices[self.index + 1] if self.index < len(self.choices) - 1 else None


def season_param(season: str) -> str:
    """„2026/2027“ -> „2026-27“ (Schreibweise in der Adresse)."""
    start, end = season.split("/")
    return f"{start}-{end[-2:]}"


def params_for(md: Matchday, current: Matchday) -> dict[str, str]:
    """Adress-Parameter für einen Spieltag; der aktuelle Spieltag braucht keine."""
    if md == current:
        return {}
    params = {PARAM_MATCHDAY: str(md.spieltag)}
    if md.saison != current.saison:
        params[PARAM_SEASON] = season_param(md.saison)
    return params


def select_matchday(overview: list[Matchday], params: dict) -> Selection | None:
    current = next((m for m in overview if m.status == CURRENT), None)
    if current is None:
        return None
    choices = [m for m in overview if m.key <= current.key]
    raw_md, raw_season = params.get(PARAM_MATCHDAY), params.get(PARAM_SEASON)
    if raw_md is None and raw_season is None:
        return Selection(current, current, choices)
    season = current.saison
    if raw_season is not None:
        season = next((m.saison for m in choices if season_param(m.saison) == str(raw_season)), None)
    try:
        wanted = int(str(raw_md))
    except (TypeError, ValueError):
        wanted = None
    match = next((m for m in choices if m.saison == season and m.spieltag == wanted), None)
    if match is None:
        return Selection(current, current, choices, requested_invalid=True)
    return Selection(match, current, choices)
