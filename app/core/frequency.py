"""Häufigkeit der Anomalien (Dashboard-Briefing, Kapitel 6.3).

Für jede Liga und jeden KPI mit Einstufung (02–09): Wie oft treten keine, leichte und starke
Anomalien auf? Grundlage sind alle Spiele der letzten abgeschlossenen Saison, jeweils so berechnet,
als wären sie noch nicht gespielt (Stichtag = Spieldatum, Spieltag = Gameday).
Dient der Überprüfung der Schwellenwerte (Schwellen aus app/config/schwellen.toml).
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pandas as pd

from .config import League
from .kpis import LIGHT, NONE, PLACEHOLDER, STRONG, Match, ThresholdLookup, compute_match, league_references
from .top import TOP_KPIS

NOT_RATED = None        # Schlüssel im Zähler für „nicht berechenbar“ (Anomalie = None)


def last_complete_season(prepared: pd.DataFrame, league: League) -> str | None:
    """Neueste Saison mit allen Spielen (Teams × (Teams − 1))."""
    expected = league.teams * (league.teams - 1)
    counts = prepared.groupby("season").size()
    complete = sorted(s for s, n in counts.items() if n == expected)
    return complete[-1] if complete else None


def _share(n: int, rated: int) -> str:
    """Anteil in Prozent mit zwei Nachkommastellen, kaufmännisch gerundet (wie alle Werte im Dashboard)."""
    if not rated:
        return PLACEHOLDER
    value = (Decimal(n) * 100 / Decimal(rated)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{value} %".replace(".", ",")


def anomaly_frequency(prepared: pd.DataFrame, league: League, thresholds: ThresholdLookup | None = None
                      ) -> tuple[str | None, pd.DataFrame]:
    season = last_complete_season(prepared, league)
    if season is None:
        return None, pd.DataFrame()
    games = prepared[prepared["season"] == season]
    counts = {k: {NONE: 0, LIGHT: 0, STRONG: 0, NOT_RATED: 0, "vorlaeufig": 0} for k in TOP_KPIS}   # KPI 02–09
    references = {}     # Zwischenspeicher: Ligareferenzen je (Saison, Spieltag, Stichtag), siehe league_references
    for g in games.itertuples():
        match = Match(league.name, season, int(g.gameday), g.date, g.home, g.away)
        key = (match.season, match.matchday, match.stichtag)
        if key not in references:
            references[key] = league_references(prepared, match, league.matchdays)
        result = compute_match(prepared, match, league.matchdays, thresholds, references[key])
        for kpi in TOP_KPIS:
            r = getattr(result, kpi)
            counts[kpi][r.anomalie] += 1
            counts[kpi]["vorlaeufig"] += int(r.vorlaeufig)
    rows = []
    for kpi, c in counts.items():
        rated = c[NONE] + c[LIGHT] + c[STRONG]
        rows.append({
            "KPI": TOP_KPIS[kpi], "Spiele": len(games),
            "keine": c[NONE], "leicht": c[LIGHT], "stark": c[STRONG],
            "nicht berechenbar": c[NOT_RATED], "davon vorläufig": c["vorlaeufig"],
            "Anteil leicht": _share(c[LIGHT], rated), "Anteil stark": _share(c[STRONG], rated),
        })
    return season, pd.DataFrame(rows)
