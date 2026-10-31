"""Bestandsübersicht der Datenbank (reine Zählungen, keine KPIs)."""

from __future__ import annotations

import pandas as pd


def league_summary(df: pd.DataFrame) -> dict:
    teams = pd.unique(pd.concat([df["homeTeam"], df["awayTeam"]]))
    seasons = sorted(df["Season"].unique())
    return {
        "Spiele": len(df),
        "Saisons": len(seasons),
        "Erste Saison": seasons[0] if seasons else "-",
        "Letzte Saison": seasons[-1] if seasons else "-",
        "Teams": len(teams),
        "Erstes Spiel": df["Date"].min(),
        "Letztes Spiel": df["Date"].max(),
    }


def games_per_season(leagues: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if not leagues:
        return pd.DataFrame()
    counts = {name: df.groupby("Season").size() for name, df in leagues.items()}
    table = pd.DataFrame(counts).fillna(0).astype(int)  # 0 = Liga hat in dieser Saison keine Spiele
    table.index.name = "Saison"
    return table.sort_index()
