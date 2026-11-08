"""KPI-Ergebnisse aller Begegnungen eines Spieltags (für Liga-Bereich und Top Anomalien).

Reine Logik ohne Oberfläche (Dashboard-Briefing, Kapitel 11): Der Liga-Bereich und die Top Anomalien nutzen
dieselbe Funktion, später auch die öffentliche Website. Zwischengespeichert wird in state.get_matchday_kpis.
"""

from __future__ import annotations

import pandas as pd

from .config import League
from .fixtures import INACTIVE_STATUS
from .kpis import Match, MatchKpis, ThresholdLookup, compute_match


def matchday_kpis(prepared: pd.DataFrame | None, league: League, season: str, matchday: int, games: pd.DataFrame,
                  thresholds: ThresholdLookup | None = None) -> list[MatchKpis | None]:
    """Ein Ergebnis je Begegnung, in der Reihenfolge von games (Spielplan).

    None für verschobene oder abgesagte Spiele (Briefing 4.4, Regel 4) und wenn die Liga nicht in der Datenbank
    steht. Stichtag ist „Datum von“: gerechnet wird so, als wäre der Spieltag noch nicht gespielt."""
    results: list[MatchKpis | None] = []
    for g in games.itertuples():
        if prepared is None or g.status in INACTIVE_STATUS:
            results.append(None)
            continue
        match = Match(league.name, season, matchday, g.datum_von, g.heim, g.gast)
        results.append(compute_match(prepared, match, league.matchdays, thresholds))
    return results
