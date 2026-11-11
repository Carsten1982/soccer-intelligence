"""Sensitivitätsanalyse, Teil Auswertung (Version 0.12; KPI-Regelwerk 11, Dashboard-Briefing 6.4).

Wertet die Fälle aus core/simulation.py (build_cases) mit frei einstellbaren Schwellen aus:

- vier Schwellen je KPI: leicht positiv/negativ, stark positiv/negativ (Limits), ungleich erlaubt;
- Tabelle „Häufigkeit“: Anzahl, Ø pro Spieltag, Spieltagsabdeckung; „leicht“ zählt die starken mit;
- Tabelle „Ergebnisqualität“ mit der leichten Schwelle: Trefferquote, Grundquote aller Spiele, Mehrwert,
  Spanne (Newcombe aus zwei Wilson-Intervallen, 95 %) und Empfehlung in sechs Stufen.

Anomalie = gerundete Abweichung über der Schwelle (positiv: > Schwelle, negativ: < Schwelle); genau auf der Schwelle
zählt nicht. Verglichen wird in ganzen Hundertsteln (Schwellen haben höchstens eine Nachkommastelle), also exakt.
Gezählt werden nur Spiele abgeschlossener Spieltage (core.simulation.closed_matchdays).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd

from .kpis import Thresholds

POS, NEG, TOTAL = "positiv", "negativ", "total"
MIN_CASES = 50                       # darunter: „Zu wenige Daten“
GOAL, SMALL, FLOOR = Decimal(5), Decimal(2), Decimal(-5)   # Pp.: Ziel, kleiner Mehrwert, Untergrenze „leicht“
Z95 = 1.959963984540054              # 97,5-%-Quantil der Normalverteilung

TOO_FEW, NEGATIVE, WORKS = "Zu wenige Daten", "Negativ", "Funktioniert"
WORKS_LIGHT, NOT_RELEVANT, UNCLEAR = "Funktioniert leicht", "Keine relevante Verbesserung", "Noch unklar"
RECOMMENDATIONS = (TOO_FEW, NEGATIVE, WORKS, WORKS_LIGHT, NOT_RELEVANT, UNCLEAR)
MATCH_KEY = ["league", "season", "gameday"]


# --- Schwellen ------------------------------------------------------------------------------------------------------

def limit(value) -> Decimal:
    """Eingabe als Dezimalzahl mit höchstens einer Nachkommastelle (kaufmännisch gerundet)."""
    return Decimal(str(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Limits:
    """Schwellen eines KPIs in Prozent: positive Werte ≥ 0, negative ≤ 0; stark betragsmässig ≥ leicht."""
    light_pos: Decimal
    light_neg: Decimal
    strong_pos: Decimal
    strong_neg: Decimal

    @classmethod
    def from_thresholds(cls, t: Thresholds) -> Limits:
        """Gültige (symmetrische) Schwellen aus schwellen.toml."""
        return cls(t.leicht, -t.leicht, t.stark, -t.stark)

    def errors(self) -> list[str]:
        out = []
        if self.light_pos < 0 or self.strong_pos < 0:
            out.append("positive Schwellen müssen 0 oder grösser sein")
        if self.light_neg > 0 or self.strong_neg > 0:
            out.append("negative Schwellen müssen 0 oder kleiner sein")
        if self.strong_pos < self.light_pos or self.strong_neg > self.light_neg:
            out.append("die starke Schwelle darf nicht unter der leichten liegen")
        return out


def _hundredths(value: Decimal) -> int:
    return int(value * 100)


def _masks(dev: pd.Series, lim: Limits, stage: str) -> dict[str, pd.Series]:
    pos, neg = (lim.light_pos, lim.light_neg) if stage == "leicht" else (lim.strong_pos, lim.strong_neg)
    return {POS: dev > _hundredths(pos), NEG: dev < _hundredths(neg)}


# --- Tabelle 1: Häufigkeit ---------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Count:
    count: int                  # Spiele mit Anomalie
    per_matchday: float | None  # Anzahl ÷ abgeschlossene Spieltage
    coverage: float | None      # Spieltage mit mindestens einer Anomalie ÷ alle abgeschlossenen Spieltage × 100


def _count(rows: pd.DataFrame, n_matchdays: int) -> Count:
    if not n_matchdays:
        return Count(len(rows), None, None)
    days = rows[MATCH_KEY].drop_duplicates().shape[0]
    return Count(len(rows), len(rows) / n_matchdays, days / n_matchdays * 100)


# --- Tabelle 2: Ergebnisqualität ---------------------------------------------------------------------------------------

def wilson(hits: int, n: int) -> tuple[float, float]:
    """Wilson-Intervall (95 %) einer Quote, als Anteile 0–1."""
    p = hits / n
    denom = 1 + Z95 ** 2 / n
    centre = (p + Z95 ** 2 / (2 * n)) / denom
    half = Z95 * math.sqrt(p * (1 - p) / n + Z95 ** 2 / (4 * n * n)) / denom
    return centre - half, centre + half


def newcombe(hits1: int, n1: int, hits2: int, n2: int) -> tuple[float, float, float]:
    """Unterschied p1 − p2 mit 95-%-Spanne (Newcombe, Methode 10), in Prozentpunkten."""
    p1, p2 = hits1 / n1, hits2 / n2
    (l1, u1), (l2, u2) = wilson(hits1, n1), wilson(hits2, n2)
    d = p1 - p2
    return (100 * d, 100 * (d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)),
            100 * (d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)))


def _round(value: float) -> Decimal:
    """Wie angezeigt: zwei Nachkommastellen, kaufmännisch (die Stufe richtet sich nach dem angezeigten Wert)."""
    return Decimal(repr(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def recommendation(cases: int, gain: float | None, low: float | None, high: float | None) -> str:
    """Sechs Stufen; die erste zutreffende Regel gilt (Spezifikation Teil 2)."""
    if cases < MIN_CASES or gain is None:
        return TOO_FEW
    gain, low, high = _round(gain), _round(low), _round(high)
    if high < 0:
        return NEGATIVE
    if gain >= GOAL and low > 0:
        return WORKS
    if gain >= SMALL and low >= FLOOR:
        return WORKS_LIGHT
    if high < GOAL:
        return NOT_RELEVANT
    return UNCLEAR


@dataclass(frozen=True)
class Quality:
    cases: int                  # Spiele mit Anomalie und bekanntem Ergebnis
    hits: int                   # davon eingetroffen
    hit: float | None           # Trefferquote in %
    base: float | None          # Grundquote aller Spiele in %
    gain: float | None          # Mehrwert in Prozentpunkten
    low: float | None           # Spanne unten
    high: float | None          # Spanne oben
    recommendation: str


def _quality(rows: pd.DataFrame, mask: pd.Series, event: str) -> Quality:
    known = rows[event].notna()
    all_n, all_hits = int(known.sum()), int(rows.loc[known, event].sum())
    sel = known & mask
    n, hits = int(sel.sum()), int(rows.loc[sel, event].sum())
    base = all_hits / all_n * 100 if all_n else None
    if not n or not all_n:
        return Quality(n, hits, None, base, None, None, None, recommendation(n, None, None, None))
    gain, low, high = newcombe(hits, n, all_hits, all_n)
    return Quality(n, hits, hits / n * 100, base, gain, low, high, recommendation(n, gain, low, high))


# --- Auswertung je KPI -------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class KpiSensitivity:
    kpi: str
    light: dict[str, Count]      # positiv, negativ, total
    strong: dict[str, Count]
    quality: dict[str, Quality]  # positiv, negativ (Schwelle = leicht)
    total_cases: int             # Ergebnisqualität Total = positiv + negativ
    total_hits: int


def evaluate(cases: pd.DataFrame, matchdays: pd.DataFrame, limits: dict[str, Limits]) -> list[KpiSensitivity]:
    """cases: Fälle der Auswahl (Liga, Saisons); matchdays: abgeschlossene Spieltage derselben Auswahl.
    Nur Fälle abgeschlossener Spieltage zählen; Nenner = Anzahl abgeschlossener Spieltage."""
    n_md = len(matchdays)
    closed = cases.merge(matchdays[MATCH_KEY].drop_duplicates(), on=MATCH_KEY, how="inner")
    out = []
    for kpi, lim in limits.items():
        rows = closed[closed["kpi"] == kpi]
        counts = {}
        for stage in ("leicht", "stark"):
            m = _masks(rows["dev"], lim, stage)
            counts[stage] = {POS: _count(rows[m[POS]], n_md), NEG: _count(rows[m[NEG]], n_md),
                             TOTAL: _count(rows[m[POS] | m[NEG]], n_md)}
        m = _masks(rows["dev"], lim, "leicht")
        quality = {POS: _quality(rows, m[POS], "up"), NEG: _quality(rows, m[NEG], "down")}
        out.append(KpiSensitivity(kpi, counts["leicht"], counts["stark"], quality,
                                  quality[POS].cases + quality[NEG].cases, quality[POS].hits + quality[NEG].hits))
    return out


def matchday_summary(matchdays: pd.DataFrame) -> dict[str, int]:
    """Abgeschlossene Spieltage je Liga (für den Warnhinweis bei „Alle Ligen“)."""
    return {lg: int(n) for lg, n in matchdays.groupby("league", sort=False).size().items()}
