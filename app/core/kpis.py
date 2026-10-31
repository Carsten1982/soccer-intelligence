"""Berechnung der KPIs 01–04 gemäss docs/03_KPI_Regelwerk.md.

Grundsätze (Regelwerk, Abschnitte 1 und 2):
- Nur abgeschlossene Spiele derselben Liga; das analysierte Spiel und spätere Spiele zählen nie.
- Teamwerte: Saison des Spiels + Vorsaison, nur Spiele bis 2 Kalendertage vor dem Stichtag.
- Ligareferenz: letzte 20 Spieltage laut `Gameday`, über das Saisonende hinweg.
- Fehlende Werte nie als 0; fehlendes Spiel wird nicht durch ein älteres ersetzt.
- Gerechnet wird exakt mit Brüchen (fractions.Fraction) aus den ganzzahligen Toren und Karten.
  Gerundet wird erst für die Anzeige: eine Nachkommastelle, kaufmännisch (ab ,5 weg von null).
  So entstehen keine Gleitkomma-Fehler wie round(4.35, 1) = 4.3.
- Die Anomalie-Einstufung verwendet die gerundete Abweichung.

Die Testfälle in docs/tests/ sind die verbindliche Referenz (tests/test_kpis.py).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

import pandas as pd

from .fixtures import previous_season

# --- Spalten der Datenbank ----------------------------------------------------------

HG, AG = "FT Home Goals", "FT Away Goals :"
HY, AY = "Home Yellow Cards Full Time", "Away Yellow Cards Full Time"

FORM_SAMPLE = 5          # KPI 01
SAMPLE = 10              # KPI 02–04
REFERENCE_MATCHDAYS = 20
MIN_GAP_DAYS = 2         # 2-Tage-Regel (nur Teamwerte)
OVER_MARK = Fraction(5, 2)   # KPI 03: feste Marke 2,5
PLACEHOLDER = "–"        # U+2013

NONE, LIGHT, STRONG = "keine", "leicht", "stark"
POSITIVE, NEGATIVE = "positiv", "negativ"


# --- Rundung und Formatierung ---------------------------------------------------------

def round1(value: Fraction | None) -> Decimal | None:
    """Kaufmännisch auf eine Nachkommastelle (exakt, ohne Gleitkomma)."""
    if value is None:
        return None
    exact = Decimal(value.numerator) / Decimal(value.denominator)   # 28 Stellen Genauigkeit
    return exact.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def fmt(value: Decimal | None) -> str | None:
    """Zahl als Text mit Punkt, z. B. „4.4“ (Format der Testfälle)."""
    return None if value is None else f"{value:.1f}"


def fmt_signed(value: Decimal | None) -> str | None:
    """Zahl mit Vorzeichen, z. B. „+34.1“, „-13.6“; genau 0 ohne Vorzeichen: „0.0“."""
    if value is None:
        return None
    if value == 0:
        return "0.0"
    return f"{value:+.1f}"


def de(value: Decimal | None) -> str:
    """Anzeige mit Komma: 4,4."""
    return PLACEHOLDER if value is None else f"{value:.1f}".replace(".", ",").replace("-", "−")


def de_signed(value: Decimal | None) -> str:
    """Anzeige mit Vorzeichen und echtem Minuszeichen: +34,1 / −13,6 / 0,0."""
    s = fmt_signed(value)
    return PLACEHOLDER if s is None else s.replace(".", ",").replace("-", "−")


def de_abs(value: Decimal | None) -> str:
    """Betrag ohne Vorzeichen (für Texte mit „mehr/weniger/über/unter“)."""
    return PLACEHOLDER if value is None else f"{abs(value):.1f}".replace(".", ",")


def as_float(value: Fraction | None) -> float | None:
    return None if value is None else float(value)


# --- Einstufung (Regelwerk 2.2) ---------------------------------------------------

def classify(deviation: Decimal | None) -> tuple[str | None, str | None]:
    """(anomalie, richtung) anhand der gerundeten Abweichung."""
    if deviation is None:
        return None, None
    size = abs(deviation)
    anomaly = NONE if size <= 20 else LIGHT if size <= 35 else STRONG
    direction = POSITIVE if deviation > 0 else NEGATIVE if deviation < 0 else None
    return anomaly, direction


def relative_deviation(value: Fraction | None, reference: Fraction | None) -> Fraction | None:
    if value is None or reference is None or reference == 0:
        return None
    return (value - reference) / reference * 100


# --- Aufbereitung einer Liga --------------------------------------------------------

def prepare_league(df: pd.DataFrame) -> pd.DataFrame:
    """Einmal je Datenbank: Hilfsspalten und feste Sortierung (Date, Uhrzeit aus matchDate, id)."""
    out = pd.DataFrame({
        "id": df["id"].astype("int64"),
        "date": pd.to_datetime(df["Date"]).dt.date,
        "time": df["matchDate"].astype(str).str.strip().str[-5:],
        "season": df["Season"].astype(str),
        "gameday": pd.to_numeric(df["Gameday"]).astype("int64"),
        "home": df["homeTeam"],
        "away": df["awayTeam"],
        "hg": pd.to_numeric(df[HG], errors="coerce"),
        "ag": pd.to_numeric(df[AG], errors="coerce"),
        "hy": pd.to_numeric(df[HY], errors="coerce"),
        "ay": pd.to_numeric(df[AY], errors="coerce"),
    })
    out = out[out["hg"].notna() & out["ag"].notna()]          # nur abgeschlossene Spiele
    out["key"] = out["season"] + "#" + out["gameday"].astype(str)   # Saison + Spieltag (für die Ligareferenz)
    return out.sort_values(["date", "time", "id"], kind="stable").reset_index(drop=True)


def team_games(prepared: pd.DataFrame, team: str, season: str, stichtag: date, n: int) -> pd.DataFrame:
    """Die letzten n abgeschlossenen Ligaspiele des Teams (Saisonfenster, 2-Tage-Regel), alt -> neu."""
    window = (season, previous_season(season))
    last_day = stichtag - timedelta(days=MIN_GAP_DAYS)
    home, away = prepared["home"].to_numpy(), prepared["away"].to_numpy()
    seasons, dates = prepared["season"].to_numpy(), prepared["date"].to_numpy()
    mask = ((home == team) | (away == team)) & ((seasons == window[0]) | (seasons == window[1])) & (dates <= last_day)
    return prepared[mask].tail(n)


def reference_keys(season: str, matchday: int, matchdays_per_season: int) -> list[tuple[str, int]]:
    """Die 20 Spieltage vor dem Spieltag des Spiels, über das Saisonende hinweg (alt -> neu)."""
    keys, s, md = [], season, matchday
    for _ in range(REFERENCE_MATCHDAYS):
        md -= 1
        if md == 0:
            s, md = previous_season(s), matchdays_per_season
        keys.append((s, md))
    return list(reversed(keys))


def reference_label(keys: list[tuple[str, int]]) -> str:
    """z. B. „2024/2025: 17-34 + 2025/2026: 1-2“."""
    parts: dict[str, list[int]] = {}
    for s, md in keys:
        parts.setdefault(s, []).append(md)
    return " + ".join(f"{s}: {min(m)}-{max(m)}" for s, m in parts.items())


# --- Ergebnisobjekte ---------------------------------------------------------------

@dataclass(frozen=True)
class Match:
    league: str
    season: str
    matchday: int
    stichtag: date          # „Datum von“ aus dem Spielplan
    home: str
    away: str


@dataclass
class FormTeam:
    team: str
    form: list[str]                 # genau 5 Einträge, alt -> neu, links mit „–“ aufgefüllt
    anzahl: int
    ids: list[int] = field(default_factory=list)

    @property
    def vorlaeufig(self) -> bool:
        return self.anzahl < FORM_SAMPLE


@dataclass
class TeamValue:
    team: str
    spiele: int
    summe: int | None               # Tore bzw. Karten
    wert: Fraction | None
    ids: list[int] = field(default_factory=list)

    @property
    def wert_rund(self) -> Decimal | None:
        return round1(self.wert)


@dataclass
class Reference:
    label: str
    spiele: int
    summe: int
    wert: Fraction | None

    @property
    def wert_rund(self) -> Decimal | None:
        return round1(self.wert)


@dataclass
class KpiResult:
    kpi: str                        # "KPI02" / "KPI03" / "KPI04"
    heim: TeamValue
    auswaerts: TeamValue
    referenz: Reference | None      # Ligareferenz (KPI 02/04); bei KPI 03 None (feste Marke)
    hauptwert: Fraction | None
    abweichung: Fraction | None
    vorlaeufig: bool
    ueberschrift: str | None = None
    text: str | None = None
    teamabweichung: tuple[Fraction | None, Fraction | None] = (None, None)   # nur KPI 03

    @property
    def hauptwert_rund(self) -> Decimal | None:
        return round1(self.hauptwert)

    @property
    def abweichung_rund(self) -> Decimal | None:
        return round1(self.abweichung)

    @property
    def anomalie(self) -> str | None:
        return classify(self.abweichung_rund)[0]

    @property
    def richtung(self) -> str | None:
        return classify(self.abweichung_rund)[1]


# --- KPI 01: Formkurve -----------------------------------------------------------

def kpi01_team(prepared: pd.DataFrame, team: str, season: str, stichtag: date) -> FormTeam:
    games = team_games(prepared, team, season, stichtag, FORM_SAMPLE)
    form = []
    for g in games.itertuples():
        own, other = (g.hg, g.ag) if g.home == team else (g.ag, g.hg)
        form.append("S" if own > other else "U" if own == other else "N")
    padded = [PLACEHOLDER] * (FORM_SAMPLE - len(form)) + form
    return FormTeam(team=team, form=padded, anzahl=len(form), ids=[int(i) for i in games["id"]])


# --- Teamwerte KPI 02/03 (Tore) und KPI 04 (Karten) ----------------------------------

def team_goals(prepared: pd.DataFrame, team: str, season: str, stichtag: date) -> TeamValue:
    games = team_games(prepared, team, season, stichtag, SAMPLE)
    if games.empty:
        return TeamValue(team, 0, None, None)
    total = int((games["hg"] + games["ag"]).sum())
    return TeamValue(team, len(games), total, Fraction(total, len(games)), [int(i) for i in games["id"]])


def team_cards(prepared: pd.DataFrame, team: str, season: str, stichtag: date) -> TeamValue:
    games = team_games(prepared, team, season, stichtag, SAMPLE)        # zuerst die letzten 10 …
    own = [g.hy if g.home == team else g.ay for g in games.itertuples()]
    kept = [(int(gid), c) for gid, c in zip(games["id"], own) if pd.notna(c)]   # … dann leere Werte weg
    if not kept:
        return TeamValue(team, 0, None, None)
    total = int(sum(c for _, c in kept))
    return TeamValue(team, len(kept), total, Fraction(total, len(kept)), [gid for gid, _ in kept])


# --- Ligareferenz -------------------------------------------------------------------

def league_reference(prepared: pd.DataFrame, match: Match, matchdays_per_season: int, cards: bool) -> Reference:
    keys = reference_keys(match.season, match.matchday, matchdays_per_season)
    wanted = {f"{s}#{md}" for s, md in keys}
    games = prepared[prepared["key"].isin(wanted) & (prepared["date"] < match.stichtag)]   # nur bereits gespielte
    if cards:
        games = games[games["hy"].notna() & games["ay"].notna()]
        total = int((games["hy"] + games["ay"]).sum())
    else:
        total = int((games["hg"] + games["ag"]).sum())
    n = len(games)
    return Reference(reference_label(keys), n, total, Fraction(total, n) if n else None)


# --- Texte (Regelwerk, Abschnitte 4–6) -----------------------------------------------

NO_ANOMALY_TITLE = "Keine statistische Besonderheit"


def _text_kpi02(r: KpiResult) -> tuple[str | None, str | None]:
    if r.abweichung_rund is None:
        return None, None
    main, dev = de(r.hauptwert_rund), r.abweichung_rund
    if r.anomalie == NONE:
        return NO_ANOMALY_TITLE, (f"In dieser Partie liegt der Torindikator bei durchschnittlich {main} Toren. "
                                  f"Die Abweichung vom Liga-Durchschnitt beträgt {de_signed(dev)} %.")
    if r.richtung == POSITIVE:
        return "Viele Tore erwartet", (f"In dieser Partie liegt der Torindikator bei durchschnittlich {main} Toren. "
                                       f"Das sind {de_abs(dev)} % mehr als im Liga-Durchschnitt.")
    return "Wenige Tore erwartet", (f"In dieser Partie liegt der Torindikator bei durchschnittlich {main} Toren. "
                                    f"Das sind {de_abs(dev)} % weniger als im Liga-Durchschnitt.")


def _text_kpi03(r: KpiResult) -> tuple[str | None, str | None]:
    if r.abweichung_rund is None:
        return None, None
    dev = r.abweichung_rund
    if r.anomalie == NONE:
        if r.richtung is None:
            # Genau 0,0 %: Text ist im Regelwerk noch offen (offener Punkt 2) -> nur Überschrift
            return NO_ANOMALY_TITLE, None
        word = "mehr" if r.richtung == POSITIVE else "weniger"
        return NO_ANOMALY_TITLE, (f"In den bisherigen Spielen erzielten die beiden Teams im Schnitt {de_abs(dev)} % "
                                  f"{word} Tore als die 2,5-Tore-Marke.")
    if r.richtung == POSITIVE:
        return "Über 2,5 Goals erwartet", (f"In den bisherigen Spielen beider Teams fielen im Schnitt {de_abs(dev)} % "
                                           "mehr Tore als die 2,5-Tore-Marke.")
    return "Unter 2,5 Goals erwartet", (f"In den bisherigen Spielen beider Teams fielen im Schnitt {de_abs(dev)} % "
                                        "weniger Tore als die 2,5-Tore-Marke.")


def _text_kpi04(r: KpiResult) -> tuple[str | None, str | None]:
    if r.abweichung_rund is None:
        return None, None
    main, dev = de(r.hauptwert_rund), r.abweichung_rund
    if r.anomalie == NONE:
        return NO_ANOMALY_TITLE, (f"Der Kartenindikator dieser Begegnung liegt bei {main} gelben Karten. "
                                  f"Die Abweichung vom Liga-Durchschnitt beträgt {de_signed(dev)} %.")
    if r.richtung == POSITIVE:
        return "Überdurchschnittlich viele gelbe Karten", (
            f"In dieser Partie werden {main} gelbe Karten erwartet. Das liegt {de_abs(dev)} % über dem Liga-Durchschnitt.")
    return "Unterdurchschnittlich viele gelbe Karten", (
        f"In dieser Partie werden {main} gelbe Karten erwartet. Das liegt {de_abs(dev)} % unter dem Liga-Durchschnitt.")


# --- KPI 02–04 ----------------------------------------------------------------------

def _both(home: TeamValue, away: TeamValue) -> bool:
    return home.wert is not None and away.wert is not None


def kpi02(prepared: pd.DataFrame, match: Match, matchdays_per_season: int,
          goals: tuple[TeamValue, TeamValue] | None = None) -> KpiResult:
    home, away = goals or (team_goals(prepared, match.home, match.season, match.stichtag),
                           team_goals(prepared, match.away, match.season, match.stichtag))
    ref = league_reference(prepared, match, matchdays_per_season, cards=False)
    main = (home.wert + away.wert) / 2 if _both(home, away) else None
    r = KpiResult("KPI02", home, away, ref, main, relative_deviation(main, ref.wert),
                  vorlaeufig=min(home.spiele, away.spiele) < SAMPLE)
    r.ueberschrift, r.text = _text_kpi02(r)
    return r


def kpi03(prepared: pd.DataFrame, match: Match, goals: tuple[TeamValue, TeamValue] | None = None) -> KpiResult:
    # dieselben Teamwerte wie KPI 02 (werden von compute_match übergeben)
    home, away = goals or (team_goals(prepared, match.home, match.season, match.stichtag),
                           team_goals(prepared, match.away, match.season, match.stichtag))
    main = (home.wert + away.wert) / 2 if _both(home, away) else None
    r = KpiResult("KPI03", home, away, None, main, relative_deviation(main, OVER_MARK),
                  vorlaeufig=min(home.spiele, away.spiele) < SAMPLE,
                  teamabweichung=(relative_deviation(home.wert, OVER_MARK), relative_deviation(away.wert, OVER_MARK)))
    r.ueberschrift, r.text = _text_kpi03(r)
    return r


def kpi04(prepared: pd.DataFrame, match: Match, matchdays_per_season: int) -> KpiResult:
    home = team_cards(prepared, match.home, match.season, match.stichtag)
    away = team_cards(prepared, match.away, match.season, match.stichtag)
    ref = league_reference(prepared, match, matchdays_per_season, cards=True)
    main = home.wert + away.wert if _both(home, away) else None             # Summe, nicht Durchschnitt
    r = KpiResult("KPI04", home, away, ref, main, relative_deviation(main, ref.wert),
                  vorlaeufig=min(home.spiele, away.spiele) < SAMPLE)
    r.ueberschrift, r.text = _text_kpi04(r)
    return r


@dataclass
class MatchKpis:
    match: Match
    form_home: FormTeam
    form_away: FormTeam
    kpi02: KpiResult
    kpi03: KpiResult
    kpi04: KpiResult


def compute_match(prepared: pd.DataFrame, match: Match, matchdays_per_season: int) -> MatchKpis:
    goals = (team_goals(prepared, match.home, match.season, match.stichtag),
             team_goals(prepared, match.away, match.season, match.stichtag))
    return MatchKpis(
        match=match,
        form_home=kpi01_team(prepared, match.home, match.season, match.stichtag),
        form_away=kpi01_team(prepared, match.away, match.season, match.stichtag),
        kpi02=kpi02(prepared, match, matchdays_per_season, goals),
        kpi03=kpi03(prepared, match, goals),
        kpi04=kpi04(prepared, match, matchdays_per_season),
    )
