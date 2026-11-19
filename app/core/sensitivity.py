"""Sensitivitätsanalyse, Teil Auswertung (seit Version 0.12; Version 0.19: Prognosewert, seit 0.20 Signalqualität; KPI-Regelwerk 11).

Wertet die Fälle aus core/simulation.py (build_cases) mit frei einstellbaren Schwellen aus:

- je KPI eine Schwelle je Richtung (mehr / weniger), als Betrag in Prozent (Limits); None = keine Schwelle;
- Häufigkeit: Anzahl, Ø pro Spieltag, Spieltagsabdeckung;
- Ergebnisqualität: Trefferquote, Vergleichsgruppe (alle Spiele), Mehrwert, Spanne (Newcombe aus zwei
  Wilson-Intervallen, 95 %), Empfehlung in sechs Stufen;
- Stabilität (Mehrwert je Saison positiv) und Signalqualität stark / mittel / gering;
- Schwellenvorschlag aller Kombinationen Liga × KPI × Richtung (proposal), Grundlage der Datei schwellen.toml.

Auffällig = Betrag der gerundeten Abweichung grösser als die Schwelle (mehr: > +Schwelle, weniger: < −Schwelle); genau
auf der Schwelle zählt nicht. Verglichen wird in ganzen Hundertsteln (Schwellen mit höchstens einer Nachkommastelle).
Gezählt werden nur Spiele abgeschlossener Spieltage (core.simulation.closed_matchdays).

Alle Grenzwerte der Regeln stehen hier an einer Stelle (RULES); Kurzhilfen und Erklärtexte werden daraus gefüllt.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd

from .kpis import HIGH, LEVELS, LOW, MEDIUM, RANK, Thresholds

MEHR, WENIGER = "mehr", "weniger"
DIRECTIONS = (MEHR, WENIGER)
EVENT = {MEHR: "up", WENIGER: "down"}
Z95 = 1.959963984540054              # 97,5-%-Quantil der Normalverteilung


@dataclass(frozen=True)
class Rules:
    """Grenzwerte (Regelwerk 11.3 und 2.2; Entscheidungen Carsten 18.11.2026)."""
    min_cases: int = 50                     # darunter: „Zu wenige Daten“
    works_gain: Decimal = Decimal(5)        # „Funktioniert“: Mehrwert mindestens … Pp.
    works_low: Decimal = Decimal(2)         # … und linker Rand der Spanne grösser als … Pp.
    light_gain: Decimal = Decimal(2)        # „Funktioniert leicht“: Mehrwert mindestens … Pp.
    light_floor: Decimal = Decimal(-5)      # … und linker Rand nicht unter … Pp.
    relevant_high: Decimal = Decimal(5)     # „Keine relevante Verbesserung“: rechter Rand unter … Pp.
    stable_share: tuple[int, int] = (2, 3)  # stabil: Mehrwert in mindestens 2/3 der Saisons positiv (aufgerundet)
    high_rate: Decimal = Decimal(60)        # Signalqualität stark: Trefferquote ab … %
    high_gain: Decimal = Decimal(8)         # … und Mehrwert ab … Pp.
    medium_rate: Decimal = Decimal(55)      # mittel: Trefferquote ab … %
    low_rate: Decimal = Decimal(50)         # gering: Trefferquote ab … %
    candidates: tuple[int, ...] = (10, 15, 20, 25, 30, 35)   # Schwellen, die der Vorschlag ausprobiert

    def stable_needed(self, seasons: int) -> int:
        a, b = self.stable_share
        return math.ceil(seasons * a / b)


RULES = Rules()

TOO_FEW, NEGATIVE, WORKS = "Zu wenige Daten", "Negativ", "Funktioniert"
WORKS_LIGHT, NOT_RELEVANT, UNCLEAR = "Funktioniert leicht", "Keine relevante Verbesserung", "Noch unklar"
RECOMMENDATIONS = (TOO_FEW, NEGATIVE, WORKS, WORKS_LIGHT, NOT_RELEVANT, UNCLEAR)
ONE_SEASON = "nur bei mehreren Saisons"
MATCH_KEY = ["league", "season", "gameday"]


# --- Schwellen ------------------------------------------------------------------------------------------------------

def limit(value) -> Decimal | None:
    """Eingabe als Betrag mit höchstens einer Nachkommastelle (kaufmännisch gerundet); leer = keine Schwelle."""
    if value is None or value == "":
        return None
    return abs(Decimal(str(value))).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Limits:
    """Schwellen eines KPIs als Betrag in Prozent je Richtung; None = in dieser Richtung keine Schwelle."""
    mehr: Decimal | None
    weniger: Decimal | None

    @classmethod
    def from_thresholds(cls, t: Thresholds) -> Limits:
        """Gültige Schwellen aus schwellen.toml."""
        return cls(t.positiv.schwelle if t.positiv else None, t.negativ.schwelle if t.negativ else None)

    def get(self, direction: str) -> Decimal | None:
        return self.mehr if direction == MEHR else self.weniger

    def errors(self) -> list[str]:
        return [f"Schwelle {d}: muss grösser als 0 sein" for d in DIRECTIONS
                if self.get(d) is not None and self.get(d) <= 0]


LimitsLike = Limits | Mapping[str, Limits]          # gleich für alle Ligen oder je Liga


def _hundredths(value: Decimal) -> int:
    return int(value * 100)


def _mask(rows: pd.DataFrame, lim: LimitsLike, direction: str) -> pd.Series:
    """Auffällig je Fall in einer Richtung. Bei Schwellen je Liga gilt für jeden Fall die Schwelle seiner Liga;
    fehlt sie (Liga ohne Schwelle in dieser Richtung), ist der Fall nicht auffällig."""
    dev = rows["dev"]
    if isinstance(lim, Limits):
        value = lim.get(direction)
        if value is None:
            return pd.Series(False, index=rows.index)
        h = _hundredths(value)
        return (dev > h) if direction == MEHR else (dev < -h)
    per_league = {lg: _hundredths(x.get(direction)) for lg, x in lim.items() if x.get(direction) is not None}
    h = rows["league"].map(per_league)
    out = (dev > h) if direction == MEHR else (dev < -h)
    return out.fillna(False).astype(bool)


# --- Häufigkeit -------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Count:
    count: int                  # Spiele über der Schwelle
    per_matchday: float | None  # Anzahl ÷ abgeschlossene Spieltage
    coverage: float | None      # Spieltage mit mindestens einem solchen Spiel ÷ alle abgeschlossenen Spieltage × 100


def _count(rows: pd.DataFrame, n_matchdays: int) -> Count:
    if not n_matchdays:
        return Count(len(rows), None, None)
    days = rows[MATCH_KEY].drop_duplicates().shape[0]
    return Count(len(rows), len(rows) / n_matchdays, days / n_matchdays * 100)


# --- Ergebnisqualität -------------------------------------------------------------------------------------------------

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


def recommendation(cases: int, gain: float | None, low: float | None, high: float | None,
                   rules: Rules = RULES) -> str:
    """Sechs Stufen; die erste zutreffende Regel gilt (Regelwerk 11.3)."""
    if cases < rules.min_cases or gain is None:
        return TOO_FEW
    g, lo, hi = _round(gain), _round(low), _round(high)
    if hi < 0:
        return NEGATIVE
    if g >= rules.works_gain and lo > rules.works_low:
        return WORKS
    if g >= rules.light_gain and lo >= rules.light_floor:
        return WORKS_LIGHT
    if hi < rules.relevant_high:
        return NOT_RELEVANT
    return UNCLEAR


def prognosis(recommend: str, rate: float | None, gain: float | None, seasons_positive: int, seasons: int,
              rules: Rules = RULES) -> tuple[str | None, str]:
    """(Signalqualität, Grund) einer Zeile: HIGH/MEDIUM/LOW oder None mit Grund (Regelwerk 2.2 und 11.3)."""
    if seasons < 2:
        return None, ONE_SEASON
    if recommend != WORKS:
        return None, f"Empfehlung: {recommend}"
    if seasons_positive < rules.stable_needed(seasons):
        return None, f"nicht stabil ({seasons_positive} von {seasons} Saisons)"
    q, g = _round(rate), _round(gain)
    if q >= rules.high_rate and g >= rules.high_gain:
        return HIGH, ""
    if q >= rules.medium_rate:
        return MEDIUM, ""
    if q >= rules.low_rate:
        return LOW, ""
    return None, f"Trefferquote unter {rules.low_rate} %"


@dataclass(frozen=True)
class Quality:
    cases: int                  # Spiele über der Schwelle mit bekanntem Ergebnis
    hits: int                   # davon eingetroffen
    rate: float | None          # Trefferquote in %
    base: float | None          # Vergleichsgruppe: Quote aller Spiele in %
    gain: float | None          # Mehrwert in Prozentpunkten
    low: float | None           # Spanne links
    high: float | None          # Spanne rechts
    recommendation: str
    seasons_positive: int = 0   # Saisons mit positivem Mehrwert
    seasons: int = 0            # ausgewertete Saisons
    signalqualitaet: str | None = None
    reason: str = ""            # Grund, wenn keine Signalqualität


def _gain(rows: pd.DataFrame, mask: pd.Series, event: str) -> tuple[int, int, int, int]:
    known = rows[event].notna()
    all_n, all_hits = int(known.sum()), int(rows.loc[known, event].sum())
    sel = known & mask
    return int(sel.sum()), int(rows.loc[sel, event].sum()), all_n, all_hits


def _quality(rows: pd.DataFrame, mask: pd.Series, event: str, rules: Rules = RULES) -> Quality:
    n, hits, all_n, all_hits = _gain(rows, mask, event)
    base = all_hits / all_n * 100 if all_n else None
    seasons = sorted(rows["season"].unique()) if "season" in rows else []
    positive = 0
    for season in seasons:
        sel = rows["season"] == season
        sn, sh, san, sah = _gain(rows[sel], mask[sel], event)
        positive += int(sn > 0 and san > 0 and sh / sn > sah / san)
    if not n or not all_n:
        rec = recommendation(n, None, None, None, rules)
        pw, reason = prognosis(rec, None, None, positive, len(seasons), rules)
        return Quality(n, hits, None, base, None, None, None, rec, positive, len(seasons), pw, reason)
    gain, low, high = newcombe(hits, n, all_hits, all_n)
    rec = recommendation(n, gain, low, high, rules)
    pw, reason = prognosis(rec, hits / n * 100, gain, positive, len(seasons), rules)
    return Quality(n, hits, hits / n * 100, base, gain, low, high, rec, positive, len(seasons), pw, reason)


# --- Auswertung je KPI -------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class KpiSensitivity:
    kpi: str
    counts: dict[str, Count]      # mehr, weniger
    quality: dict[str, Quality]   # mehr, weniger


def _closed(cases: pd.DataFrame, matchdays: pd.DataFrame) -> pd.DataFrame:
    return cases.merge(matchdays[MATCH_KEY].drop_duplicates(), on=MATCH_KEY, how="inner")


def evaluate(cases: pd.DataFrame, matchdays: pd.DataFrame, limits: dict[str, LimitsLike],
             rules: Rules = RULES) -> list[KpiSensitivity]:
    """cases: Fälle der Auswahl (Liga, Saisons); matchdays: abgeschlossene Spieltage derselben Auswahl.
    Nur Fälle abgeschlossener Spieltage zählen; Nenner = Anzahl abgeschlossener Spieltage."""
    n_md = len(matchdays)
    closed = _closed(cases, matchdays)
    out = []
    for kpi, lim in limits.items():
        rows = closed[closed["kpi"] == kpi]
        counts, quality = {}, {}
        for d in DIRECTIONS:
            m = _mask(rows, lim, d)
            counts[d] = _count(rows[m], n_md)
            quality[d] = _quality(rows, m, EVENT[d], rules)
        out.append(KpiSensitivity(kpi, counts, quality))
    return out


def matchday_summary(matchdays: pd.DataFrame) -> dict[str, int]:
    """Abgeschlossene Spieltage je Liga (für den Warnhinweis bei „Alle Ligen“)."""
    return {lg: int(n) for lg, n in matchdays.groupby("league", sort=False).size().items()}


# --- Schwellenvorschlag (Grundlage der Datei schwellen.toml) ----------------------------------------------------------

def proposal(cases: pd.DataFrame, matchdays: pd.DataFrame, leagues: list[str], kpis: list[str],
             rules: Rules = RULES) -> pd.DataFrame:
    """Je Liga, KPI und Richtung die gültige Schwelle nach Regelwerk 2.2: Kandidaten (rules.candidates) mit
    Signalqualität; die beste Stufe, bei Gleichstand die mit mehr Spielen. Ohne Kandidaten: keine Zeile.
    Spalten: liga, kpi, richtung, schwelle, signalqualitaet, spiele, eingetroffen, je_spieltag, trefferquote,
    vergleichsgruppe, mehrwert, spanne_links, spanne_rechts, saisons_positiv, saisons."""
    closed = _closed(cases, matchdays)
    out = []
    for league in leagues:
        n_md = len(matchdays[matchdays["league"] == league].drop_duplicates(MATCH_KEY))
        for kpi in kpis:
            rows = closed[(closed["league"] == league) & (closed["kpi"] == kpi)]
            for d in DIRECTIONS:
                best = None
                for c in rules.candidates:
                    m = _mask(rows, Limits(Decimal(c), Decimal(c)), d)
                    q = _quality(rows, m, EVENT[d], rules)
                    if q.signalqualitaet is None:
                        continue
                    key = (RANK[q.signalqualitaet], q.cases)
                    if best is None or key > best[0]:
                        best = (key, c, q, int(m.sum()))
                if best is None:
                    continue
                _, c, q, n_all = best
                out.append(dict(liga=league, kpi=kpi, richtung=d, schwelle=c, signalqualitaet=q.signalqualitaet,
                                spiele=q.cases, eingetroffen=q.hits, je_spieltag=n_all / n_md if n_md else None,
                                trefferquote=q.rate, vergleichsgruppe=q.base, mehrwert=q.gain, spanne_links=q.low,
                                spanne_rechts=q.high, saisons_positiv=q.seasons_positive, saisons=q.seasons))
    return pd.DataFrame(out, columns=["liga", "kpi", "richtung", "schwelle", "signalqualitaet", "spiele", "eingetroffen",
                                      "je_spieltag", "trefferquote", "vergleichsgruppe", "mehrwert", "spanne_links",
                                      "spanne_rechts", "saisons_positiv", "saisons"])


def proposal_toml(df: pd.DataFrame, seasons: str, computed: str) -> str:
    """Der Vorschlag im Format von app/config/schwellen.toml (ohne Freigabe-Datum; Übernahme über GitHub)."""
    lines = ["# Schwellenvorschlag aus der Sensitivitätsanalyse – erst nach Freigabe durch Carsten übernehmen",
             "", "[grundlage]", f'saisons = "{seasons}"', f'berechnet = "{computed}"', 'freigabe = ""', ""]
    for r in df.itertuples(index=False):
        lines += ["[[schwelle]]", f'liga = "{r.liga}"', f'kpi = "{r.kpi}"', f'richtung = "{r.richtung}"',
                  f"schwelle = {r.schwelle}", f'signalqualitaet = "{r.signalqualitaet}"', f"spiele = {r.spiele}",
                  f"trefferquote = {_round(r.trefferquote)}", f"vergleichsgruppe = {_round(r.vergleichsgruppe)}",
                  f"mehrwert = {_round(r.mehrwert)}", f"spanne_links = {_round(r.spanne_links)}",
                  f"spanne_rechts = {_round(r.spanne_rechts)}",
                  f'saisons_positiv = "{r.saisons_positiv}/{r.saisons}"', ""]
    return "\n".join(lines)


__all__ = ["DIRECTIONS", "LEVELS", "Limits", "MEHR", "RECOMMENDATIONS", "RULES", "WENIGER", "evaluate", "limit",
           "newcombe", "prognosis", "proposal", "proposal_toml", "recommendation", "wilson"]
