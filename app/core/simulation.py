"""Simulation – Spielwiese (Etappe I.1, Dashboard-Briefing 6.4, KPI-Regelwerk Abschnitt 11).

Frage: Wie gut funktionieren die Anomalien und ihre Schwellen? Dazu wird jedes historische Spiel so berechnet, als
wäre es noch nicht gespielt (wie in der Häufigkeit: Stichtag = Spieldatum, Spieltag = Gameday). Danach wird geprüft,
ob die Anomalie im Spiel eingetroffen ist.

Ablauf:
1. build_cases: einmal je Datenbankstand alle Spiele berechnen (rund 50 Sekunden). Gespeichert wird je Spiel und KPI
   nur die gerundete Abweichung, ob der Wert vorläufig ist und ob „mehr“ bzw. „weniger“ als die Ligareferenz eintraf.
2. frequency_rows / quality_rows: mit beliebigen Schwellen neu einstufen – das geht in Sekundenbruchteilen.

Die Simulation verändert nie die gültigen Schwellen (app/config/schwellen.toml).
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

import numpy as np
import pandas as pd

from .config import League
from .kpis import (
    OVER_MARK, STAT_KPIS, KpiResult, Match, Thresholds, _both_cards, _goals, compute_match, league_references,
    round_display,
)
from .seasons import analysed_seasons
from .top import TOP_KPIS

MIN_CASES = 100          # darunter: „zu wenige Fälle“ (Regelwerk 11.3)
Z95 = 1.96               # 95 % – Breite der zufälligen Schwankung

# Wert im Spiel je KPI (dieselben Funktionen wie für die KPI-Werte; None = Wert fehlt) und Faktor (KPI 08 in %)
ACTUAL: dict[str, tuple[Callable, int]] = {
    "kpi02": (_goals, 1), "kpi03": (_goals, 1), "kpi04": (_both_cards, 1),
    **{key: (spec.per_game, spec.scale) for key, spec in STAT_KPIS.items()},
}

# Wann eine Anomalie eingetroffen ist (Regelwerk 11.1) – für den Bereich „Definitionen und Änderungen“
EVENT_TEXTS = {
    "kpi02": "Tore im Spiel über (positiv) bzw. unter (negativ) der Ligareferenz vor dem Spiel",
    "kpi03": "mindestens 3 Tore (positiv) bzw. höchstens 2 Tore (negativ) – feste Marke 2,5",
    "kpi04": "gelbe Karten im Spiel (beide Teams) über bzw. unter der Ligareferenz",
    "kpi05": "Ecken im Spiel (beide Teams) über bzw. unter der Ligareferenz",
    "kpi06": "Tore in der 1. Halbzeit über bzw. unter der Ligareferenz",
    "kpi07": "Tore in der 2. Halbzeit über bzw. unter der Ligareferenz",
    "kpi08": "beide Teams treffen (positiv) bzw. nicht beide (negativ)",
    "kpi09": "Schüsse aufs Tor im Spiel (beide Teams) über bzw. unter der Ligareferenz",
}
DEFINITION_CHANGES = [
    ("08.11.2026", "Erste Fassung der Ergebniskontrolle (Etappe I.1, Freigabe Carsten)."),
    ("10.11.2026", "Referenzsaison: Die älteste Saison der Datenbank liefert nur die Vorsaison und wird nicht "
                   "ausgewertet (bisher fest 2020/21). Neue Saisonauswahl; Definition „eingetroffen“ unverändert "
                   "(Version 0.11, Freigabe Carsten)."),
]


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

    Spalten: league, season, complete (Saison vollständig gespielt), game (id), kpi,
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
            out.append((league.name, g.season, g.season in complete, int(g.id), kpi, int(r.abweichung_rund * 100),
                        up, down))
    return pd.DataFrame(out, columns=["league", "season", "complete", "game", "kpi", "dev", "up", "down"])


# --- 2. Neu einstufen (schnell) ------------------------------------------------------------------

def _short(season: str) -> str:
    return f"{season[:4]}/{season[-2:]}"


ALL_SEASONS = "Alle Saisons"     # Anfang der Voreinstellung in der Saisonauswahl


def season_choices(cases: pd.DataFrame) -> dict[str, list[str]]:
    """Saisonauswahl (Briefing „Neue Datenbank“, Abschnitt 4; Regelwerk 11.4), in dieser Reihenfolge:

    1. Aktuelle Saison (vorläufig)            – nur wenn eine Saison läuft
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
        choices[f"Aktuelle Saison ({_short(current[0])}, vorläufig)"] = current
    if done:
        choices[f"{ALL_SEASONS} ({_span(done)})"] = done
    if done and current:
        both = sorted(set(done) | set(current))
        choices[f"{ALL_SEASONS} plus aktuelle ({_span(both)}, inkl. vorläufig)"] = both
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


def _hundredths(value: Decimal) -> float:
    return float(Decimal(value) * 100)


def levels(dev: np.ndarray, light: np.ndarray | float, strong: np.ndarray | float) -> np.ndarray:
    """Stufe je Fall wie classify (Regelwerk 2.2): 0 = keine (|x| ≤ leicht), 1 = leicht (≤ stark), 2 = stark."""
    size = np.abs(dev)
    return np.where(size <= light, 0, np.where(size <= strong, 1, 2))


@dataclass(frozen=True)
class Setting:
    """Schwellen für die Simulation: vorher = gültige Schwellen je Liga, nachher = Einstellungen im Tab."""
    before: Callable[[str, str], Thresholds]       # (Liga, KPI) -> Schwellen, z. B. ThresholdConfig.get
    after: dict[str, Thresholds]                   # KPI -> Schwellen


def _classified(cases: pd.DataFrame, kpi: str, setting: Setting) -> pd.DataFrame:
    c = cases[cases["kpi"] == kpi].copy()
    light_b = c["league"].map(lambda lg: _hundredths(setting.before(lg, kpi).leicht)).to_numpy(dtype=float)
    strong_b = c["league"].map(lambda lg: _hundredths(setting.before(lg, kpi).stark)).to_numpy(dtype=float)
    after = setting.after[kpi]
    dev = c["dev"].to_numpy(dtype=float)
    c["before"] = levels(dev, light_b, strong_b)
    c["after"] = levels(dev, _hundredths(after.leicht), _hundredths(after.stark))
    return c


def unchanged(cases: pd.DataFrame, kpi: str, setting: Setting) -> bool:
    """True, wenn die Schwellen nachher für alle Ligen der Auswahl dieselben sind wie vorher."""
    return all(setting.before(lg, kpi) == setting.after[kpi] for lg in cases["league"].unique())


def frequency_rows(cases: pd.DataFrame, setting: Setting) -> list[dict]:
    """Tabelle Häufigkeit: je KPI Anzahl leichter und starker Anomalien vorher und nachher (beide Richtungen)."""
    rows = []
    for kpi, name in TOP_KPIS.items():
        c = _classified(cases, kpi, setting)
        row = {"kpi": kpi, "name": name, "games": len(c), "unchanged": unchanged(cases, kpi, setting)}
        for when in ("before", "after"):
            row[f"light_{when}"] = int((c[when] == 1).sum())
            row[f"strong_{when}"] = int((c[when] == 2).sum())
            row[f"total_{when}"] = row[f"light_{when}"] + row[f"strong_{when}"]
        rows.append(row)
    return rows


@dataclass(frozen=True)
class Quality:
    cases: int                  # Anomalien in dieser Richtung mit bekanntem Ergebnis
    hit: float | None           # eingetroffen in % (None ohne Fälle)
    control: float | None       # dasselbe Ereignis in Spielen ohne Anomalie, in %
    margin: float | None        # zufällige Schwankung der Trefferquote (±, Prozentpunkte, 95 %)

    @property
    def gain(self) -> float | None:
        """Mehrwert in Prozentpunkten = Trefferquote − Quote ohne Anomalie."""
        return None if self.hit is None or self.control is None else self.hit - self.control


def _quality(c: pd.DataFrame, when: str, direction: str, stage: str) -> Quality:
    event = "up" if direction == "positiv" else "down"
    known = c[c[event].notna()]
    sign = known["dev"] > 0 if direction == "positiv" else known["dev"] < 0
    wanted = {"beide": known[when] >= 1, "leicht": known[when] == 1, "stark": known[when] == 2}[stage]
    hits = known.loc[sign & wanted, event]
    control = known.loc[known[when] == 0, event]
    n = len(hits)
    hit = float(hits.mean() * 100) if n else None
    margin = Z95 * math.sqrt(hit * (100 - hit) / n) if n else None
    return Quality(n, hit, float(control.mean() * 100) if len(control) else None, margin)


BETTER, WORSE, NO_DIFF, SAME, TOO_FEW = "besser", "schlechter", "kein klarer Unterschied", "unverändert", "zu wenige Fälle"


def judge(before: Quality, after: Quality, same_thresholds: bool) -> str:
    """Urteil (Regelwerk 11.3): besser/schlechter nur, wenn sich der Mehrwert stärker verändert als die Schwankung."""
    if same_thresholds:
        return SAME
    if before.cases < MIN_CASES or after.cases < MIN_CASES or before.gain is None or after.gain is None:
        return TOO_FEW
    diff = after.gain - before.gain
    if abs(diff) <= after.margin:
        return NO_DIFF
    return BETTER if diff > 0 else WORSE


def quality_rows(cases: pd.DataFrame, setting: Setting, stage: str = "beide") -> list[dict]:
    """Tabelle Ergebnisqualität: je KPI und Richtung vorher/nachher. stage: „beide“, „leicht“ oder „stark“."""
    rows = []
    for kpi, name in TOP_KPIS.items():
        c = _classified(cases, kpi, setting)
        same = unchanged(cases, kpi, setting)
        for direction in ("positiv", "negativ"):
            before, after = _quality(c, "before", direction, stage), _quality(c, "after", direction, stage)
            rows.append({"kpi": kpi, "name": name, "direction": direction, "before": before, "after": after,
                         "judge": judge(before, after, same)})
    return rows


def pct(value: float | None, signed: bool = False) -> str:
    """Prozentwert/-punkte mit zwei Nachkommastellen, kaufmännisch gerundet (wie alle Zahlen im Dashboard)."""
    if value is None:
        return "–"
    d = round_display(Fraction(Decimal(repr(value))))
    text = f"{d:+.2f}" if signed and d != 0 else f"{d:.2f}"
    return text.replace(".", ",").replace("-", "−")


def quantize_threshold(value: float) -> Decimal:
    """Eingabe aus dem Tab als Dezimalzahl mit höchstens zwei Nachkommastellen."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
