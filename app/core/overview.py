"""Bestandsübersicht der Datenbank (reine Zählungen, keine KPIs)."""

from __future__ import annotations

import pandas as pd

from .matchday import season_short
from .seasons import analysed_seasons, reference_season


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
        "Referenzsaison": reference_season(df["Season"]),       # nur Vorsaison, nicht ausgewertet (Version 0.11)
        "Ausgewertet": analysed_seasons(df["Season"]),
    }


def games_per_season(leagues: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if not leagues:
        return pd.DataFrame()
    counts = {name: df.groupby("Season").size() for name, df in leagues.items()}
    table = pd.DataFrame(counts).fillna(0).astype(int)  # 0 = Liga hat in dieser Saison keine Spiele
    table.index.name = "Saison"
    return table.sort_index()


def seasons_text(summary: dict) -> str:
    """Referenzsaison und ausgewertete Saisons einer Liga für den Bereich Datenqualität (Version 0.11, Regelwerk 1.2)."""
    ref, analysed = summary["Referenzsaison"], summary["Ausgewertet"]
    if ref is None:
        return "Keine Saison vorhanden."
    text = f"Referenzsaison: {season_short(ref)} (nur Vorsaison, nicht ausgewertet) · Ausgewertet: "
    if not analysed:
        return text + "keine (nur eine Saison in der Datenbank)"
    first, last = season_short(analysed[0]), season_short(analysed[-1])
    return text + (first if first == last else f"{first}–{last}")
