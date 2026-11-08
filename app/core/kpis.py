"""Berechnung der KPIs 01–09 gemäss docs/03_KPI_Regelwerk.md.

Grundsätze (Regelwerk, Abschnitte 1, 2 und 9):
- Nur abgeschlossene Spiele derselben Liga; das analysierte Spiel und spätere Spiele zählen nie.
- Teamwerte: Saison des Spiels + Vorsaison, nur Spiele bis 2 Kalendertage vor dem Stichtag.
  Zuerst die letzten 10 Spiele bestimmen, danach Spiele ohne Wert auslassen (kein älteres Spiel nachziehen).
- Ligareferenz: letzte 20 Spieltage laut `Gameday`, über das Saisonende hinweg, nur Spiele vor dem Stichtag.
- Fehlende Werte nie als 0; echte Nullen zählen mit.
- Gerechnet wird exakt mit Brüchen (fractions.Fraction) aus den ganzzahligen Werten. Ein Wert mit Kommastellen
  (z. B. 4,5 Ecken) gilt als fehlend; er wird nie abgeschnitten (seit H.1).
  Gerundet wird erst für die Anzeige: **zwei Nachkommastellen** (seit Etappe H, 08.11.2026), kaufmännisch
  (ab 5 weg von null), mit Dezimalarithmetik. So entstehen keine Gleitkomma-Fehler wie round(2.675, 2) = 2.67.
- Die Anomalie-Einstufung verwendet die auf zwei Stellen gerundete Abweichung und die Schwellen aus
  app/config/schwellen.toml (Standard ±20 % / ±35 %, Regelwerk 2.2).

Tempo (seit H.1): Die Spiele eines Teams und die Referenzspiele werden je Begegnung nur einmal bestimmt und nur
einmal in eine Liste von Zeilen umgewandelt (rows_of). Alle Werte werden dann aus diesen Listen gelesen.

Die Testfälle in docs/tests/ sind die verbindliche Referenz (tests/test_kpis.py).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

import pandas as pd

from .fixtures import previous_season

# --- Spalten der Datenbank ----------------------------------------------------------

HG, AG = "FT Home Goals", "FT Away Goals :"
HY, AY = "Home Yellow Cards Full Time", "Away Yellow Cards Full Time"
# KPI 05–09 (Regelwerk 9): Halbzeit-Tore, Ecken, Schüsse aufs Tor
EXTRA_COLUMNS = {
    "h1h": "First-Half Home Goals", "h1a": "First-Half Away Goals",
    "h2h": "Second-Half Home Goals", "h2a": "Second-Half Away Goals",
    "ch": "Home Corners Full Time", "ca": "Away Corners Full Time",
    "sh": "Home Shots on Target Full Time", "sa": "Away Shots on Target Full Time",
}

FORM_SAMPLE = 5          # KPI 01
SAMPLE = 10              # KPI 02–09
REFERENCE_MATCHDAYS = 20
MIN_GAP_DAYS = 2         # 2-Tage-Regel (nur Teamwerte)
OVER_MARK = Fraction(5, 2)   # KPI 03: feste Marke 2,5
PLACEHOLDER = "–"        # U+2013
DECIMALS = 2             # Anzeige-Rundung (Regelwerk 2.3, seit 08.11.2026)

NONE, LIGHT, STRONG = "keine", "leicht", "stark"
POSITIVE, NEGATIVE = "positiv", "negativ"


# --- Rundung und Formatierung ---------------------------------------------------------

_QUANT = Decimal(1).scaleb(-DECIMALS)          # 0.01


def round_display(value: Fraction | None) -> Decimal | None:
    """Kaufmännisch auf zwei Nachkommastellen (exakt, ohne Gleitkomma).
    Ein kleiner negativer Wert, der auf −0,00 fällt, wird zu 0,00 (Regelwerk 2.4)."""
    if value is None:
        return None
    exact = Decimal(value.numerator) / Decimal(value.denominator)   # 28 Stellen Genauigkeit
    rounded = exact.quantize(_QUANT, rounding=ROUND_HALF_UP)
    return abs(rounded) if rounded == 0 else rounded


def fmt(value: Decimal | None) -> str | None:
    """Zahl als Text mit Punkt, z. B. „4.35“ (Format der Testfälle)."""
    return None if value is None else f"{value:.{DECIMALS}f}"


def fmt_signed(value: Decimal | None) -> str | None:
    """Zahl mit Vorzeichen, z. B. „+34.08“, „-13.59“; genau 0 ohne Vorzeichen: „0.00“."""
    if value is None:
        return None
    if value == 0:
        return f"{0:.{DECIMALS}f}"
    return f"{value:+.{DECIMALS}f}"


def de(value: Decimal | None) -> str:
    """Anzeige mit Komma: 4,35."""
    return PLACEHOLDER if value is None else f"{value:.{DECIMALS}f}".replace(".", ",").replace("-", "−")


def de_signed(value: Decimal | None) -> str:
    """Anzeige mit Vorzeichen und echtem Minuszeichen: +34,08 / −13,59 / 0,00."""
    s = fmt_signed(value)
    return PLACEHOLDER if s is None else s.replace(".", ",").replace("-", "−")


def de_abs(value: Decimal | None) -> str:
    """Betrag ohne Vorzeichen (für Texte mit „mehr/weniger/über/unter“)."""
    return PLACEHOLDER if value is None else f"{abs(value):.{DECIMALS}f}".replace(".", ",")


# --- Einstufung (Regelwerk 2.2) ---------------------------------------------------

@dataclass(frozen=True)
class Thresholds:
    """Schwellen nach Betrag: |x| ≤ leicht → keine · ≤ stark → leicht · darüber → stark."""
    leicht: Decimal = Decimal("20")
    stark: Decimal = Decimal("35")


STANDARD_THRESHOLDS = Thresholds()


def classify(deviation: Decimal | None, thresholds: Thresholds = STANDARD_THRESHOLDS
             ) -> tuple[str | None, str | None]:
    """(anomalie, richtung) anhand der gerundeten Abweichung."""
    if deviation is None:
        return None, None
    size = abs(deviation)
    anomaly = NONE if size <= thresholds.leicht else LIGHT if size <= thresholds.stark else STRONG
    direction = POSITIVE if deviation > 0 else NEGATIVE if deviation < 0 else None
    return anomaly, direction


def relative_deviation(value: Fraction | None, reference: Fraction | None) -> Fraction | None:
    if value is None or reference is None or reference == 0:
        return None
    return (value - reference) / reference * 100


# --- Aufbereitung einer Liga --------------------------------------------------------

def _numeric(df: pd.DataFrame, column: str) -> pd.Series:
    """Spalte als Zahl; fehlt die Spalte (z. B. in Mini-Testdaten), sind alle Werte leer."""
    if column in df.columns:
        return pd.to_numeric(df[column], errors="coerce")
    return pd.Series([float("nan")] * len(df), index=df.index, dtype="float64")


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
        "hg": _numeric(df, HG),
        "ag": _numeric(df, AG),
        "hy": _numeric(df, HY),
        "ay": _numeric(df, AY),
        **{short: _numeric(df, column) for short, column in EXTRA_COLUMNS.items()},
    })
    out = out[out["hg"].notna() & out["ag"].notna()]          # nur abgeschlossene Spiele
    out["key"] = out["season"] + "#" + out["gameday"].astype(str)   # Saison + Spieltag (für die Ligareferenz)
    return out.sort_values(["date", "time", "id"], kind="stable").reset_index(drop=True)


Rows = list          # Liste von Spielzeilen (benannte Tupel mit g.id, g.hg, g.home …), siehe rows_of


def rows_of(games: pd.DataFrame) -> Rows:
    """Spiele als Liste von Zeilen. Einmal je Begegnung aufgerufen; das spart die meiste Rechenzeit (H.1)."""
    return list(games.itertuples(index=False))


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
    summe: int | None               # Tore, Karten, Ecken … bzw. Anzahl BTTS-Spiele (KPI 08)
    wert: Fraction | None
    ids: list[int] = field(default_factory=list)

    @property
    def wert_rund(self) -> Decimal | None:
        return round_display(self.wert)


@dataclass
class Reference:
    label: str
    spiele: int
    summe: int
    wert: Fraction | None

    @property
    def wert_rund(self) -> Decimal | None:
        return round_display(self.wert)


@dataclass
class KpiResult:
    kpi: str                        # "KPI02" … "KPI09"
    heim: TeamValue
    auswaerts: TeamValue
    referenz: Reference | None      # Ligareferenz; bei KPI 03 None (feste Marke 2,5)
    hauptwert: Fraction | None
    abweichung: Fraction | None
    vorlaeufig: bool
    ueberschrift: str | None = None
    text: str | None = None
    teamabweichung: tuple[Fraction | None, Fraction | None] = (None, None)   # nur KPI 03
    schwellen: Thresholds = STANDARD_THRESHOLDS
    prozent: bool = False           # KPI 08: Werte in %

    @property
    def hauptwert_rund(self) -> Decimal | None:
        return round_display(self.hauptwert)

    @property
    def abweichung_rund(self) -> Decimal | None:
        return round_display(self.abweichung)

    @property
    def anomalie(self) -> str | None:
        return classify(self.abweichung_rund, self.schwellen)[0]

    @property
    def richtung(self) -> str | None:
        return classify(self.abweichung_rund, self.schwellen)[1]


# --- Werte je Spiel ---------------------------------------------------------------

def _int_or_none(*values) -> list[int] | None:
    """Alle Werte vorhanden und ganzzahlig -> als ganze Zahlen; sonst None (fehlender Wert, nie 0, nie abgeschnitten)."""
    out = []
    for v in values:
        if pd.isna(v) or not float(v).is_integer():
            return None
        out.append(int(v))
    return out


def _goals(g) -> int | None:
    v = _int_or_none(g.hg, g.ag)
    return None if v is None else v[0] + v[1]


def _both_cards(g) -> int | None:
    v = _int_or_none(g.hy, g.ay)
    return None if v is None else v[0] + v[1]


def _own_cards(team: str) -> Callable:
    def value(g) -> int | None:
        v = _int_or_none(g.hy if g.home == team else g.ay)
        return None if v is None else v[0]
    return value


def team_value(team: str, rows: Rows, per_game: Callable, scale: int = 1) -> TeamValue:
    """Teamwert aus den bereits bestimmten (höchstens 10) Spielen: Spiele ohne Wert fallen weg."""
    kept = [(int(g.id), v) for g in rows if (v := per_game(g)) is not None]
    if not kept:
        return TeamValue(team, 0, None, None)
    total = sum(v for _, v in kept)
    return TeamValue(team, len(kept), total, Fraction(total * scale, len(kept)), [gid for gid, _ in kept])


def reference_value(label: str, rows: Rows, per_game: Callable, scale: int = 1) -> Reference:
    """Ligareferenz aus den Referenzspielen: Spiele ohne Wert fallen weg."""
    values = [v for g in rows if (v := per_game(g)) is not None]
    n, total = len(values), sum(values)
    return Reference(label, n, total, Fraction(total * scale, n) if n else None)


def reference_games(prepared: pd.DataFrame, match: Match, matchdays_per_season: int) -> tuple[str, pd.DataFrame]:
    """Spiele der 20 Referenz-Spieltage, die vor dem Stichtag gespielt wurden."""
    keys = reference_keys(match.season, match.matchday, matchdays_per_season)
    wanted = {f"{s}#{md}" for s, md in keys}
    games = prepared[prepared["key"].isin(wanted) & (prepared["date"] < match.stichtag)]
    return reference_label(keys), games


# --- KPI 01: Formkurve -----------------------------------------------------------

def _form(team: str, rows: Rows) -> FormTeam:
    form = []
    for g in rows:
        own, other = (g.hg, g.ag) if g.home == team else (g.ag, g.hg)
        form.append("S" if own > other else "U" if own == other else "N")
    padded = [PLACEHOLDER] * (FORM_SAMPLE - len(form)) + form
    return FormTeam(team=team, form=padded, anzahl=len(form), ids=[int(g.id) for g in rows])


def kpi01_team(prepared: pd.DataFrame, team: str, season: str, stichtag: date) -> FormTeam:
    return _form(team, rows_of(team_games(prepared, team, season, stichtag, FORM_SAMPLE)))


# --- Teamwerte KPI 02/03 (Tore) und KPI 04 (Karten) ----------------------------------

def team_goals(prepared: pd.DataFrame, team: str, season: str, stichtag: date) -> TeamValue:
    return team_value(team, rows_of(team_games(prepared, team, season, stichtag, SAMPLE)), _goals)


def team_cards(prepared: pd.DataFrame, team: str, season: str, stichtag: date) -> TeamValue:
    # zuerst die letzten 10 Spiele, dann leere Werte weg (kein älteres Spiel nachziehen)
    return team_value(team, rows_of(team_games(prepared, team, season, stichtag, SAMPLE)), _own_cards(team))


# --- Ligareferenz -------------------------------------------------------------------

def league_reference(prepared: pd.DataFrame, match: Match, matchdays_per_season: int, cards: bool) -> Reference:
    label, games = reference_games(prepared, match, matchdays_per_season)
    return reference_value(label, rows_of(games), _both_cards if cards else _goals)


# --- Texte (Regelwerk, Abschnitte 4–6 und 9) ------------------------------------------

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
            # Genau 0,00 %: Text ist im Regelwerk noch offen (offener Punkt 2) -> nur Überschrift
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


# --- KPI 05–09 (Regelwerk, Abschnitt 9) ------------------------------------------------
# Alle fünf haben denselben Aufbau: Teamwert = Ø eines Spielwerts beider Mannschaften in den Spielen des Teams,
# Hauptwert = Mittelwert der beiden Teamwerte, Ligareferenz = Ø desselben Spielwerts in den Referenzspielen.
# Platzhalter in den Texten: {H} Hauptwert · {S} Abweichung mit Vorzeichen · {A} Betrag · {R} Ligareferenz.

@dataclass(frozen=True)
class StatKpi:
    key: str                     # Attribut in MatchKpis, z. B. "kpi05"
    code: str                    # "KPI05"
    name: str
    per_game: Callable           # Spielwert (beide Mannschaften) oder None, wenn ein Wert fehlt
    titles: tuple[str, str]      # Überschrift positiv / negativ
    texts: tuple[str, str, str]  # Text keine / positiv / negativ
    percent: bool = False        # KPI 08: Quote in %

    @property
    def scale(self) -> int:
        """KPI 08 rechnet die Quote in Prozent (×100), alle anderen mit dem Wert selbst."""
        return 100 if self.percent else 1


def _pair_sum(a: str, b: str) -> Callable:
    def value(g) -> int | None:
        v = _int_or_none(getattr(g, a), getattr(g, b))
        return None if v is None else v[0] + v[1]
    return value


def _btts(g) -> int | None:
    v = _int_or_none(g.hg, g.ag)
    return None if v is None else int(v[0] > 0 and v[1] > 0)


STAT_KPIS: dict[str, StatKpi] = {k.key: k for k in (
    StatKpi("kpi05", "KPI05", "Ecken", _pair_sum("ch", "ca"),
            ("Viele Ecken erwartet", "Wenige Ecken erwartet"),
            ("Der Eckballindikator liegt bei {H} Ecken. Die Abweichung vom Liga-Durchschnitt beträgt {S} %.",
             "Für diese Begegnung werden {H} Ecken erwartet. Das liegt {A} % über dem Liga-Durchschnitt.",
             "Für diese Begegnung werden {H} Ecken erwartet. Das liegt {A} % unter dem Liga-Durchschnitt.")),
    StatKpi("kpi06", "KPI06", "Tore 1. Halbzeit", _pair_sum("h1h", "h1a"),
            ("Viele Tore in Halbzeit 1", "Wenige Tore in Halbzeit 1"),
            ("In den bisherigen Spielen fielen in Halbzeit eins im Schnitt {H} Tore. "
             "Die Abweichung vom Liga-Durchschnitt beträgt {S} %.",
             "In den bisherigen Spielen beider Teams fielen in Halbzeit eins durchschnittlich {H} Tore. "
             "Das sind {A} % mehr als im Liga-Durchschnitt.",
             "In den bisherigen Spielen beider Teams fielen in Halbzeit eins durchschnittlich {H} Tore. "
             "Das sind {A} % weniger als im Liga-Durchschnitt.")),
    StatKpi("kpi07", "KPI07", "Tore 2. Halbzeit", _pair_sum("h2h", "h2a"),
            ("Viele Tore in Halbzeit 2", "Wenige Tore in Halbzeit 2"),
            ("In den bisherigen Spielen fielen in Halbzeit zwei im Schnitt {H} Tore. "
             "Die Abweichung vom Liga-Durchschnitt beträgt {S} %.",
             "In den bisherigen Spielen beider Teams fielen in Halbzeit zwei durchschnittlich {H} Tore. "
             "Das sind {A} % mehr als im Liga-Durchschnitt.",
             "In den bisherigen Spielen beider Teams fielen in Halbzeit zwei durchschnittlich {H} Tore. "
             "Das sind {A} % weniger als im Liga-Durchschnitt.")),
    StatKpi("kpi08", "KPI08", "Beide Teams treffen", _btts,
            ("Beide Teams treffen häufig", "Beide Teams treffen seltener"),
            ("Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von {H} % auf. "
             "Die Abweichung vom Liga-Durchschnitt von {R} % beträgt {S} %.",
             "Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von {H} % auf. "
             "Das liegt {A} % über dem Liga-Durchschnitt von {R} %.",
             "Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von {H} % auf. "
             "Das liegt {A} % unter dem Liga-Durchschnitt von {R} %."), percent=True),
    StatKpi("kpi09", "KPI09", "Schüsse aufs Tor", _pair_sum("sh", "sa"),
            ("Viele Schüsse aufs Tor erwartet", "Wenige Schüsse aufs Tor erwartet"),
            ("Der Indikator liegt bei {H} Schüssen aufs Tor. Die Abweichung vom Liga-Durchschnitt beträgt {S} %.",
             "Der Indikator liegt bei {H} Schüssen aufs Tor. Das liegt {A} % über dem Liga-Durchschnitt.",
             "Der Indikator liegt bei {H} Schüssen aufs Tor. Das liegt {A} % unter dem Liga-Durchschnitt.")),
)}


def _text_stat(spec: StatKpi, r: KpiResult) -> tuple[str | None, str | None]:
    if r.abweichung_rund is None:
        return None, None
    dev = r.abweichung_rund
    values = {"H": de(r.hauptwert_rund), "S": de_signed(dev), "A": de_abs(dev),
              "R": de(r.referenz.wert_rund) if r.referenz else PLACEHOLDER}
    if r.anomalie == NONE:
        return NO_ANOMALY_TITLE, spec.texts[0].format(**values)
    if r.richtung == POSITIVE:
        return spec.titles[0], spec.texts[1].format(**values)
    return spec.titles[1], spec.texts[2].format(**values)


# --- KPI 02–09 ----------------------------------------------------------------------

def _both(home: TeamValue, away: TeamValue) -> bool:
    return home.wert is not None and away.wert is not None


def _mean(home: TeamValue, away: TeamValue) -> Fraction | None:
    return (home.wert + away.wert) / 2 if _both(home, away) else None


def _vorlaeufig(home: TeamValue, away: TeamValue) -> bool:
    return min(home.spiele, away.spiele) < SAMPLE


def kpi02(prepared: pd.DataFrame, match: Match, matchdays_per_season: int,
          goals: tuple[TeamValue, TeamValue] | None = None, ref: Reference | None = None,
          thresholds: Thresholds = STANDARD_THRESHOLDS) -> KpiResult:
    home, away = goals or (team_goals(prepared, match.home, match.season, match.stichtag),
                           team_goals(prepared, match.away, match.season, match.stichtag))
    ref = ref or league_reference(prepared, match, matchdays_per_season, cards=False)
    main = _mean(home, away)
    r = KpiResult("KPI02", home, away, ref, main, relative_deviation(main, ref.wert),
                  vorlaeufig=_vorlaeufig(home, away), schwellen=thresholds)
    r.ueberschrift, r.text = _text_kpi02(r)
    return r


def kpi03(prepared: pd.DataFrame, match: Match, goals: tuple[TeamValue, TeamValue] | None = None,
          thresholds: Thresholds = STANDARD_THRESHOLDS) -> KpiResult:
    # dieselben Teamwerte wie KPI 02 (werden von compute_match übergeben)
    home, away = goals or (team_goals(prepared, match.home, match.season, match.stichtag),
                           team_goals(prepared, match.away, match.season, match.stichtag))
    main = _mean(home, away)
    r = KpiResult("KPI03", home, away, None, main, relative_deviation(main, OVER_MARK),
                  vorlaeufig=_vorlaeufig(home, away),
                  teamabweichung=(relative_deviation(home.wert, OVER_MARK), relative_deviation(away.wert, OVER_MARK)),
                  schwellen=thresholds)
    r.ueberschrift, r.text = _text_kpi03(r)
    return r


def kpi04(prepared: pd.DataFrame, match: Match, matchdays_per_season: int,
          cards: tuple[TeamValue, TeamValue] | None = None, ref: Reference | None = None,
          thresholds: Thresholds = STANDARD_THRESHOLDS) -> KpiResult:
    home, away = cards or (team_cards(prepared, match.home, match.season, match.stichtag),
                           team_cards(prepared, match.away, match.season, match.stichtag))
    ref = ref or league_reference(prepared, match, matchdays_per_season, cards=True)
    main = home.wert + away.wert if _both(home, away) else None             # Summe, nicht Durchschnitt
    r = KpiResult("KPI04", home, away, ref, main, relative_deviation(main, ref.wert),
                  vorlaeufig=_vorlaeufig(home, away), schwellen=thresholds)
    r.ueberschrift, r.text = _text_kpi04(r)
    return r


def kpi_stat(spec: StatKpi, home: TeamValue, away: TeamValue, ref: Reference,
             thresholds: Thresholds = STANDARD_THRESHOLDS) -> KpiResult:
    """KPI 05–09 aus fertigen Teamwerten und Ligareferenz."""
    main = _mean(home, away)
    r = KpiResult(spec.code, home, away, ref, main, relative_deviation(main, ref.wert),
                  vorlaeufig=_vorlaeufig(home, away), schwellen=thresholds, prozent=spec.percent)
    r.ueberschrift, r.text = _text_stat(spec, r)
    return r


def stat_kpi(prepared: pd.DataFrame, match: Match, matchdays_per_season: int, key: str,
             thresholds: Thresholds = STANDARD_THRESHOLDS) -> KpiResult:
    """Ein einzelner KPI 05–09 (für Tests und Auswertungen; compute_match rechnet alle auf einmal)."""
    spec = STAT_KPIS[key]
    teams = [team_value(t, rows_of(team_games(prepared, t, match.season, match.stichtag, SAMPLE)), spec.per_game,
                        spec.scale) for t in (match.home, match.away)]
    label, games = reference_games(prepared, match, matchdays_per_season)
    return kpi_stat(spec, *teams, reference_value(label, rows_of(games), spec.per_game, spec.scale), thresholds)


# --- Alle KPIs einer Begegnung ---------------------------------------------------------

KPI_KEYS = ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08", "kpi09")


@dataclass
class MatchKpis:
    match: Match
    form_home: FormTeam
    form_away: FormTeam
    kpi02: KpiResult
    kpi03: KpiResult
    kpi04: KpiResult
    kpi05: KpiResult
    kpi06: KpiResult
    kpi07: KpiResult
    kpi08: KpiResult
    kpi09: KpiResult

    def results(self) -> list[tuple[str, KpiResult]]:
        return [(key, getattr(self, key)) for key in KPI_KEYS]


ThresholdLookup = Callable[[str, str], Thresholds]   # (Liga, KPI-Schlüssel) -> Schwellen, z. B. ThresholdConfig.get
References = dict[str, Reference]                    # Ligareferenz je KPI ("kpi02", "kpi04", "kpi05" … "kpi09")


def league_references(prepared: pd.DataFrame, match: Match, matchdays_per_season: int) -> References:
    """Alle Ligareferenzen einer Begegnung (KPI 02, 04 und 05–09; KPI 03 hat die feste Marke 2,5).

    Sie hängen nur von Saison, Spieltag und Stichtag ab. Die Häufigkeit nutzt sie darum für alle Spiele mit
    gleichem (Saison, Spieltag, Stichtag) gemeinsam. Der Stichtag gehört dazu: Wegen Nachholspielen kann sich die
    Referenz innerhalb eines Spieltags unterscheiden (Code-Prüfung 08.11.2026, Punkt L2)."""
    label, games = reference_games(prepared, match, matchdays_per_season)
    rows = rows_of(games)
    refs = {"kpi02": reference_value(label, rows, _goals), "kpi04": reference_value(label, rows, _both_cards)}
    for key, spec in STAT_KPIS.items():
        refs[key] = reference_value(label, rows, spec.per_game, spec.scale)
    return refs


def compute_match(prepared: pd.DataFrame, match: Match, matchdays_per_season: int,
                  thresholds: ThresholdLookup | None = None, references: References | None = None) -> MatchKpis:
    """Alle KPIs einer Begegnung. Die Spiele der Teams und die Referenzspiele werden nur einmal bestimmt.
    references: fertige Ligareferenzen (league_references), sonst werden sie hier berechnet."""
    def th(key: str) -> Thresholds:
        return thresholds(match.league, key) if thresholds else STANDARD_THRESHOLDS

    teams = (match.home, match.away)
    rows = {t: rows_of(team_games(prepared, t, match.season, match.stichtag, SAMPLE)) for t in teams}
    refs = references if references is not None else league_references(prepared, match, matchdays_per_season)
    goals = tuple(team_value(t, rows[t], _goals) for t in teams)
    cards = tuple(team_value(t, rows[t], _own_cards(t)) for t in teams)
    stats = {}
    for key, spec in STAT_KPIS.items():
        home, away = (team_value(t, rows[t], spec.per_game, spec.scale) for t in teams)
        stats[key] = kpi_stat(spec, home, away, refs[key], th(key))
    return MatchKpis(
        match=match,
        form_home=_form(match.home, rows[match.home][-FORM_SAMPLE:]),   # die letzten 5 der letzten 10
        form_away=_form(match.away, rows[match.away][-FORM_SAMPLE:]),
        kpi02=kpi02(prepared, match, matchdays_per_season, goals, refs["kpi02"], th("kpi02")),
        kpi03=kpi03(prepared, match, goals, th("kpi03")),
        kpi04=kpi04(prepared, match, matchdays_per_season, cards, refs["kpi04"], th("kpi04")),
        **stats,
    )
