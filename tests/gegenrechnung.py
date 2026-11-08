"""Unabhängige Gegenrechnung der KPIs 01–09 (Etappe F, 07.11.2026; KPI 05–09 und zwei Nachkommastellen
seit Etappe H, 08.11.2026; Kommazahlen gelten seit H.1 als fehlend).

Zweck: die Berechnung der App (app/core/kpis.py) mit einer ZWEITEN, getrennt geschriebenen Umsetzung
vergleichen – direkt aus dem Text von docs/03_KPI_Regelwerk.md, ohne Code der App wiederzuverwenden:

- liest die Excel-Datei selbst mit openpyxl (nicht über core.loader, nicht über pandas),
- rechnet mit reinem Python und exakten Brüchen (fractions.Fraction),
- rundet mit decimal.ROUND_HALF_UP auf zwei Nachkommastellen (Regelwerk 2.3, seit 08.11.2026).

Stimmen beide Umsetzungen mit den von Carsten bestätigten Testfällen in docs/tests überein, ist auch die
Gegenrechnung bestätigt. Ihre Übereinstimmung mit der App für alle Ligen zeigt dann, dass die App überall
richtig rechnet.
"""

from __future__ import annotations

import bisect
import datetime as dt
from collections import defaultdict
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

import openpyxl

FORM_N, SAMPLE_N, REF_MATCHDAYS, MIN_GAP, OVER = 5, 10, 20, 2, Fraction(5, 2)
LIGHT_MAX, STRONG_MAX = Decimal(20), Decimal(35)          # Standard-Schwellen (Regelwerk 2.2)

# Spaltenpaare (Heim, Gast) für KPI 05–09 (Regelwerk 9)
STAT_PAIRS = {
    "ecken": ("Home Corners Full Time", "Away Corners Full Time"),
    "hz1": ("First-Half Home Goals", "First-Half Away Goals"),
    "hz2": ("Second-Half Home Goals", "Second-Half Away Goals"),
    "sot": ("Home Shots on Target Full Time", "Away Shots on Target Full Time"),
}
STAT_COLUMNS = [c for pair in STAT_PAIRS.values() for c in pair]


@dataclass(frozen=True)
class Game:
    id: int
    date: dt.date
    time: str
    season: str
    gameday: int
    home: str
    away: str
    hg: int
    ag: int
    hy: int | None
    ay: int | None
    stats: dict = field(default_factory=dict, compare=False, hash=False)   # z. B. "ecken": (5, 3) oder None

    @property
    def order(self):                       # Regelwerk 1: Date, Uhrzeit aus matchDate, id
        return (self.date, self.time, self.id)


def _num(v):
    """Ganze Zahl oder None. Leer oder mit Kommastellen (z. B. 4,5 Ecken) gilt als fehlend, nie abschneiden (H.1)."""
    if v is None or (isinstance(v, str) and not v.strip()):
        return None
    number = float(v)
    return int(number) if number.is_integer() else None


def read_league(path, sheet: str) -> list[Game]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = wb[sheet].iter_rows(values_only=True)
    head = [str(h).strip() if h is not None else "" for h in next(rows)]
    col = {name: head.index(name) for name in (
        "Date", "Gameday", "id", "matchDate", "Season", "homeTeam", "awayTeam", "FT Home Goals", "FT Away Goals :",
        "Home Yellow Cards Full Time", "Away Yellow Cards Full Time", *STAT_COLUMNS)}
    out = []
    for r in rows:
        if r[col["id"]] is None:
            continue
        hg, ag = r[col["FT Home Goals"]], r[col["FT Away Goals :"]]
        if hg is None or ag is None:       # ohne Ergebnis nicht abgeschlossen
            continue
        d = r[col["Date"]]
        d = d.date() if isinstance(d, dt.datetime) else d
        stats = {}
        for name, (h, a) in STAT_PAIRS.items():
            vh, va = _num(r[col[h]]), _num(r[col[a]])
            stats[name] = None if vh is None or va is None else (vh, va)
        out.append(Game(int(r[col["id"]]), d, str(r[col["matchDate"]]).strip()[-5:], str(r[col["Season"]]),
                        int(r[col["Gameday"]]), r[col["homeTeam"]], r[col["awayTeam"]], int(hg), int(ag),
                        _num(r[col["Home Yellow Cards Full Time"]]), _num(r[col["Away Yellow Cards Full Time"]]),
                        stats))
    wb.close()
    return out


def prev_season(s: str) -> str:
    a, b = s.split("/")
    return f"{int(a) - 1}/{int(b) - 1}"


def r2(x: Fraction | None) -> Decimal | None:
    """Zwei Nachkommastellen, kaufmännisch; −0,00 wird 0,00."""
    if x is None:
        return None
    d = (Decimal(x.numerator) / Decimal(x.denominator)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return abs(d) if d == 0 else d


def grade(dev: Decimal | None) -> str | None:
    if dev is None:
        return None
    a = abs(dev)
    return "keine" if a <= LIGHT_MAX else "leicht" if a <= STRONG_MAX else "stark"


class League:
    """Alle abgeschlossenen Spiele einer Liga, vorbereitet für schnelle Abfragen."""

    def __init__(self, games: list[Game], matchdays: int):
        self.matchdays = matchdays
        self.by_team: dict[str, list[Game]] = defaultdict(list)
        self.by_key: dict[tuple[str, int], list[Game]] = defaultdict(list)
        for g in sorted(games, key=lambda g: g.order):
            self.by_team[g.home].append(g)
            self.by_team[g.away].append(g)
            self.by_key[(g.season, g.gameday)].append(g)
        self.dates = {t: [g.date for g in gs] for t, gs in self.by_team.items()}

    def last_games(self, team: str, season: str, stichtag: dt.date, n: int) -> list[Game]:
        """Regelwerk 1: Saison + Vorsaison, mindestens 2 Kalendertage vor dem Stichtag, die n neuesten."""
        games, dates = self.by_team.get(team, []), self.dates.get(team, [])
        upto = bisect.bisect_right(dates, stichtag - dt.timedelta(days=MIN_GAP))
        window = (season, prev_season(season))
        sel = [g for g in games[:upto] if g.season in window]
        return sel[-n:]

    def reference_games(self, season: str, matchday: int, stichtag: dt.date) -> list[Game]:
        """Regelwerk 1.1: die 20 Spieltage vor dem Spieltag (über das Saisonende), nur vor dem Stichtag gespielt."""
        keys, s, md = [], season, matchday
        for _ in range(REF_MATCHDAYS):
            md -= 1
            if md == 0:
                s, md = prev_season(s), self.matchdays
            keys.append((s, md))
        return [g for k in keys for g in self.by_key.get(k, []) if g.date < stichtag]


# Spielwert je KPI 05–09: Summe beider Mannschaften bzw. BTTS 1/0; None = Wert fehlt
def _stat_value(name: str):
    def value(g: Game):
        pair = g.stats.get(name)
        return None if pair is None else pair[0] + pair[1]
    return value


STAT_VALUES = {"kpi05": (_stat_value("ecken"), 1), "kpi06": (_stat_value("hz1"), 1), "kpi07": (_stat_value("hz2"), 1),
               "kpi08": (lambda g: 1 if g.hg > 0 and g.ag > 0 else 0, 100), "kpi09": (_stat_value("sot"), 1)}


def analyse(lg: League, season: str, matchday: int, stichtag: dt.date, home: str, away: str) -> dict:
    """Alle Werte einer Begegnung, so wie sie im Dashboard erscheinen (gerundet) plus Zählwerte zum Vergleich."""
    out = {}
    samples = {}
    for side, team in (("heim", home), ("gast", away)):
        form_games = lg.last_games(team, season, stichtag, FORM_N)
        form = []
        for g in form_games:
            own, other = (g.hg, g.ag) if g.home == team else (g.ag, g.hg)
            form.append("S" if own > other else "U" if own == other else "N")
        out[f"form_{side}"] = ["–"] * (FORM_N - len(form)) + form
        sample = lg.last_games(team, season, stichtag, SAMPLE_N)
        samples[side] = sample
        out[f"tore_{side}"] = (len(sample), sum(g.hg + g.ag for g in sample) if sample else None)
        cards = [(g.hy if g.home == team else g.ay) for g in sample]          # zuerst 10 Spiele, dann leere weg
        cards = [c for c in cards if c is not None]
        out[f"karten_{side}"] = (len(cards), sum(cards) if cards else None)

    ref = lg.reference_games(season, matchday, stichtag)
    ref_goals = (len(ref), sum(g.hg + g.ag for g in ref))
    ref_cards_games = [g for g in ref if g.hy is not None and g.ay is not None]
    ref_cards = (len(ref_cards_games), sum(g.hy + g.ay for g in ref_cards_games))
    out["ref_tore"], out["ref_karten"] = ref_goals, ref_cards

    def avg(pair, scale=1):
        n, s = pair
        return Fraction(s * scale, n) if n else None

    th, ta = avg(out["tore_heim"]), avg(out["tore_gast"])
    kh, ka = avg(out["karten_heim"]), avg(out["karten_gast"])
    rg = avg(ref_goals)
    rk = avg(ref_cards)

    def dev(value, reference):
        if value is None or reference is None or reference == 0:
            return None
        return (value - reference) / reference * 100

    def result(value, reference, n_min):
        d = r2(dev(value, reference))
        return {"hauptwert": r2(value), "abweichung": d, "anomalie": grade(d), "vorlaeufig": n_min < SAMPLE_N}

    k2 = (th + ta) / 2 if th is not None and ta is not None else None
    k4 = kh + ka if kh is not None and ka is not None else None
    n_goals = min(out["tore_heim"][0], out["tore_gast"][0])
    out["kpi02"] = result(k2, rg, n_goals)
    out["kpi03"] = result(k2, OVER, n_goals)
    out["kpi04"] = result(k4, rk, min(out["karten_heim"][0], out["karten_gast"][0]))

    # KPI 05–09: Teamwert = Ø Spielwert in den letzten 10 Spielen (leere weg), Hauptwert = Mittelwert
    for key, (value, scale) in STAT_VALUES.items():
        teams = {}
        for side in ("heim", "gast"):
            vals = [v for g in samples[side] if (v := value(g)) is not None]
            teams[side] = (len(vals), sum(vals) if vals else None)
        rvals = [v for g in ref if (v := value(g)) is not None]
        rpair = (len(rvals), sum(rvals))
        vh, va = avg(teams["heim"], scale), avg(teams["gast"], scale)
        main = (vh + va) / 2 if vh is not None and va is not None else None
        res = result(main, avg(rpair, scale), min(teams["heim"][0], teams["gast"][0]))
        res.update(team_heim=teams["heim"], team_gast=teams["gast"], ref=rpair, wert_heim=r2(vh), wert_gast=r2(va),
                   liga=r2(avg(rpair, scale)))
        out[key] = res
    return out
