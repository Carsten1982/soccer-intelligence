"""Sensitivitätsanalyse, Teil Fälle (Version 0.12; KPI-Regelwerk Abschnitt 11, Dashboard-Briefing 6.4).

Jedes historische Spiel wird so berechnet, als wäre es noch nicht gespielt (Stichtag = Spieldatum, Spieltag = Gameday),
und es wird festgehalten, ob im Spiel „mehr“ bzw. „weniger“ als die Ligareferenz vor dem Spiel eintraf.

- build_cases: einmal je Datenbankstand alle Spiele berechnen (rund 5 Sekunden seit 0.19.1, vorher 50). Gespeichert wird je Spiel und KPI nur
  die gerundete Abweichung und das Ereignis; vorläufige und nicht berechenbare Werte fallen weg.
- closed_matchdays: abgeschlossene Spieltage (Nenner für „Ø pro Spieltag“ und „Spieltagsabdeckung“).
- season_choices: Saisonauswahl ohne Referenzsaison.

Ausgewertet wird mit beliebigen Schwellen in core/sensitivity.py (in Sekundenbruchteilen). Die Auswertung verändert
nie die gültigen Schwellen (app/config/schwellen.toml).
"""

from __future__ import annotations

import math
from collections.abc import Callable
from decimal import Decimal
from fractions import Fraction

import pandas as pd

from .config import League
from .kpis import (
    OVER_MARK, STAT_KPIS, KpiResult, Match, _both_cards, _goals, compute_match, league_references, round_display,
)
from .seasons import analysed_seasons
from .top import TOP_KPIS

# Wert im Spiel je KPI (dieselben Funktionen wie für die KPI-Werte; None = Wert fehlt) und Faktor (KPI 08 in %)
ACTUAL: dict[str, tuple[Callable, int]] = {
    "kpi02": (_goals, 1), "kpi03": (_goals, 1), "kpi04": (_both_cards, 1),
    **{key: (spec.per_game, spec.scale) for key, spec in STAT_KPIS.items()},
}

# Wann eine Auffälligkeit eingetroffen ist (Regelwerk 11.1) – für das Erklärfeld der Sensitivitätsanalyse
EVENT_TEXTS = {
    "kpi02": "Tore im Spiel über bzw. unter dem Ligaschnitt",
    "kpi03": "mindestens 3 bzw. höchstens 2 Tore (feste Marke 2,5)",
    "kpi04": "gelbe Karten beider Teams über bzw. unter dem Ligaschnitt",
    "kpi05": "Ecken beider Teams über bzw. unter dem Ligaschnitt",
    "kpi06": "Tore der 1. Halbzeit über bzw. unter dem Ligaschnitt",
    "kpi07": "Tore der 2. Halbzeit über bzw. unter dem Ligaschnitt",
    "kpi08": "beide Teams treffen bzw. nicht beide",
    "kpi09": "Schüsse aufs Tor beider Teams über bzw. unter dem Ligaschnitt",
}
# Die Änderungen an den Definitionen stehen seit Version 0.19 nur noch im KPI-Regelwerk, Abschnitt 11.5.


# --- 1. Fälle aufbauen (teuer, einmal je Datenbankstand) -----------------------------------------

def _event(r: KpiResult, value: int | None, scale: int, key: str) -> tuple[float, float]:
    """(mehr, weniger) als die Referenz: 1.0 / 0.0, NaN wenn der Wert im Spiel fehlt. Gleichstand = keins von beiden."""
    reference = OVER_MARK if key == "kpi03" else (r.referenz.wert if r.referenz else None)
    if value is None or reference is None:
        return math.nan, math.nan
    actual = Fraction(value * scale)
    return float(actual > reference), float(actual < reference)


def build_cases(prepared: pd.DataFrame, league: League) -> pd.DataFrame:
    """Ein Fall je Spiel und KPI 02–09 aller ausgewerteten Saisons, also ohne Referenzsaison (core/seasons.py).

    Spalten: league, season, gameday, complete (Saison vollständig gespielt), game (id), kpi,
    dev (gerundete Abweichung in Hundertsteln, z. B. 2228 = 22,28 %),
    up / down (1.0 = mehr / weniger als die Referenz eingetroffen, NaN = Wert fehlt).
    Weggelassen werden nicht berechenbare und vorläufige Werte (z. B. Aufsteiger, Entscheidung 08.11.2026)."""
    seasons = set(analysed_seasons(prepared["season"]))
    games = prepared[prepared["season"].isin(seasons)]
    per_season = games.groupby("season").size()
    complete = {season for season, n in per_season.items() if n == league.teams * (league.teams - 1)}
    references = {}
    out = []
    for g in games.itertuples(index=False):
        match = Match(league.name, g.season, int(g.gameday), g.date, g.home, g.away)
        key = (match.season, match.matchday, match.stichtag)
        if key not in references:
            references[key] = league_references(prepared, match, league.matchdays)
        result = compute_match(prepared, match, league.matchdays, references=references[key])
        for kpi in TOP_KPIS:
            r: KpiResult = getattr(result, kpi)
            if r.vorlaeufig or r.abweichung_rund is None:
                continue
            per_game, scale = ACTUAL[kpi]
            up, down = _event(r, per_game(g), scale, kpi)
            out.append((league.name, g.season, int(g.gameday), g.season in complete, int(g.id), kpi,
                        int(r.abweichung_rund * 100), up, down))
    return pd.DataFrame(out, columns=["league", "season", "gameday", "complete", "game", "kpi", "dev", "up", "down"])


def closed_matchdays(prepared: pd.DataFrame, league: League) -> pd.DataFrame:
    """Abgeschlossene Spieltage der ausgewerteten Saisons (Spalten league, season, gameday; Spezifikation R7).

    Abgeschlossen = alle Spiele gespielt (Teams / 2). Fehlen Spiele (offenes Nachholspiel), zählt der Spieltag trotzdem,
    sobald ein späterer Spieltag derselben Saison vollständig ist. Ein halb gespielter letzter Spieltag zählt nicht."""
    rows = []
    games = prepared[prepared["season"].isin(set(analysed_seasons(prepared["season"])))]
    for season, g in games.groupby("season"):
        per = g.groupby("gameday").size()
        full = per.index[per == league.teams // 2]
        last_full = full.max() if len(full) else 0
        rows += [(league.name, season, int(gd)) for gd in per.index if gd in full or gd < last_full]
    return pd.DataFrame(rows, columns=["league", "season", "gameday"])


# --- 2. Saisonauswahl und Zahlenformat ----------------------------------------------------------

def _short(season: str) -> str:
    return f"{season[:4]}/{season[-2:]}"


ALL_SEASONS = "Alle Saisons"     # Anfang der Voreinstellung in der Saisonauswahl


def season_choices(cases: pd.DataFrame) -> dict[str, list[str]]:
    """Saisonauswahl (Regelwerk 11.4; Namen seit Version 0.12 ohne „vorläufig“), in dieser Reihenfolge:

    1. Aktuelle Saison                        – nur wenn eine Saison läuft
    2. Alle Saisons                          – alle abgeschlossenen (Voreinstellung, siehe default_choice)
    3. Alle Saisons plus aktuelle            – nur wenn eine Saison läuft
    4. Letzte 2, 3 … n−1 Saisons              – nur abgeschlossene
    5. jede abgeschlossene Saison einzeln     – neueste zuerst

    Die Referenzsaison ist nie dabei, weil build_cases sie gar nicht berechnet. Die Beschriftung zeigt immer die Jahre.
    Zählt eine Saison in einer Liga als abgeschlossen und in einer anderen als laufend, erscheint sie in beiden
    Gruppen."""
    done = sorted(cases.loc[cases["complete"], "season"].unique())
    running = running_seasons(cases)
    current = running[-1:] if running else []
    choices: dict[str, list[str]] = {}
    if current:
        choices[f"Aktuelle Saison ({_short(current[0])})"] = current
    if done:
        choices[f"{ALL_SEASONS} ({_span(done)})"] = done
    if done and current:
        both = sorted(set(done) | set(current))
        choices[f"{ALL_SEASONS} plus aktuelle ({_span(both)})"] = both
    for n in range(2, len(done)):
        choices[f"Letzte {n} Saisons ({_span(done[-n:])})"] = done[-n:]
    for season in reversed(done):
        choices[f"Saison {_short(season)}"] = [season]
    return choices


def default_choice(choices: dict[str, list[str]]) -> str | None:
    """Voreinstellung der Saisonauswahl: „Alle Saisons (…)“, sonst der erste Eintrag."""
    for label in choices:
        if label.startswith(f"{ALL_SEASONS} ("):
            return label
    return next(iter(choices), None)


def _span(seasons: list[str]) -> str:
    return _short(seasons[0]) if len(seasons) == 1 else f"{_short(seasons[0])}–{_short(seasons[-1])}"


def running_seasons(cases: pd.DataFrame) -> list[str]:
    """Noch nicht abgeschlossene Saisons (laufende Saison, wird als „vorläufig“ gekennzeichnet)."""
    return sorted(cases.loc[~cases["complete"], "season"].unique())


def pct(value: float | None, signed: bool = False) -> str:
    """Prozentwert/-punkte mit zwei Nachkommastellen, kaufmännisch gerundet (wie alle Zahlen im Dashboard)."""
    if value is None:
        return "–"
    d = round_display(Fraction(Decimal(repr(value))))
    text = f"{d:+.2f}" if signed and d != 0 else f"{d:.2f}"
    return text.replace(".", ",").replace("-", "−")
