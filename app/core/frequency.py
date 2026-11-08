"""Häufigkeit der Anomalien (Dashboard-Briefing, Kapitel 6.3).

Für jede Liga und jeden KPI mit Einstufung (02–09): Wie oft treten keine, leichte und starke
Anomalien auf? Grundlage sind alle Spiele der letzten abgeschlossenen Saison, jeweils so berechnet,
als wären sie noch nicht gespielt (Stichtag = Spieldatum, Spieltag = Gameday).
Dient der Überprüfung der Schwellenwerte (Schwellen aus app/config/schwellen.toml).
"""

from __future__ import annotations

import pandas as pd

from .config import League
from .kpis import LIGHT, NONE, STRONG, Match, ThresholdLookup, compute_match
from .top import TOP_KPIS

KPI_NAMES = dict(TOP_KPIS)          # KPI 02–09


def last_complete_season(prepared: pd.DataFrame, league: League) -> str | None:
    """Neueste Saison mit allen Spielen (Teams × (Teams − 1))."""
    expected = league.teams * (league.teams - 1)
    counts = prepared.groupby("season").size()
    complete = sorted(s for s, n in counts.items() if n == expected)
    return complete[-1] if complete else None


def anomaly_frequency(prepared: pd.DataFrame, league: League, thresholds: ThresholdLookup | None = None
                      ) -> tuple[str | None, pd.DataFrame]:
    season = last_complete_season(prepared, league)
    if season is None:
        return None, pd.DataFrame()
    games = prepared[prepared["season"] == season]
    matchdays = 2 * (league.teams - 1)
    counts = {k: {NONE: 0, LIGHT: 0, STRONG: 0, None: 0, "vorlaeufig": 0} for k in KPI_NAMES}
    for g in games.itertuples():
        result = compute_match(prepared, Match(league.name, season, int(g.gameday), g.date, g.home, g.away), matchdays,
                               thresholds)
        for key in KPI_NAMES:
            r = getattr(result, key)
            counts[key][r.anomalie] += 1
            counts[key]["vorlaeufig"] += int(r.vorlaeufig)
    rows = []
    for key, c in counts.items():
        rated = c[NONE] + c[LIGHT] + c[STRONG]
        share = lambda n: f"{n / rated * 100:.2f} %".replace(".", ",") if rated else "–"  # noqa: E731
        rows.append({
            "KPI": KPI_NAMES[key], "Spiele": len(games),
            "keine": c[NONE], "leicht": c[LIGHT], "stark": c[STRONG],
            "nicht berechenbar": c[None], "davon vorläufig": c["vorlaeufig"],
            "Anteil leicht": share(c[LIGHT]), "Anteil stark": share(c[STRONG]),
        })
    return season, pd.DataFrame(rows)
