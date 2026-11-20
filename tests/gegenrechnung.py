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


def grade_split(dev: Decimal | None, lp: Decimal, sp: Decimal, ln: Decimal, sn: Decimal) -> str | None:
    """Einstufung mit getrennten Schwellen (seit Version 0.13): positiv über lp (leicht) bzw. sp (stark),
    negativ unter ln bzw. sn (negative Zahlen); genau auf der Schwelle = schwächere Stufe."""
    if dev is None:
        return None
    if dev > 0:
        return "keine" if dev <= lp else "leicht" if dev <= sp else "stark"
    if dev < 0:
        return "keine" if dev >= ln else "leicht" if dev >= sn else "stark"
    return "keine"


def grade_signal(dev: Decimal | None, pos: tuple[Decimal, str] | None, neg: tuple[Decimal, str] | None) -> str | None:
    """Einstufung seit Version 0.19: je Richtung höchstens eine Schwelle (Betrag) mit Signalqualität (bis 0.19 Prognosewert). Auffällig, wenn der
    Betrag der gerundeten Abweichung grösser als die Schwelle ist; dann die Signalqualität, sonst „keine“."""
    if dev is None:
        return None
    side = pos if dev > 0 else neg if dev < 0 else None
    if side is not None and abs(dev) > side[0]:
        return side[1]
    return "keine"


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


# --- Ergebniskontrolle der Simulation (Etappe I.1, Regelwerk 11), unabhängig von app/core/simulation.py ----------

def sim_events(lg: League, game: Game) -> dict:
    """Je KPI 02–09: (Abweichung, vorläufig, mehr, weniger) für ein Spiel, berechnet wie vor dem Spiel.
    mehr/weniger: tatsächlicher Wert im Spiel über/unter der Ligareferenz (KPI 03: Marke 2,5); None = Wert fehlt."""
    res = analyse(lg, game.season, game.gameday, game.date, game.home, game.away)
    refs = {"kpi02": res["ref_tore"], "kpi04": res["ref_karten"]}
    actual = {"kpi02": game.hg + game.ag, "kpi03": game.hg + game.ag,
              "kpi04": None if game.hy is None or game.ay is None else game.hy + game.ay}
    for key, (value, _) in STAT_VALUES.items():
        refs[key] = res[key]["ref"]
        actual[key] = value(game)
    out = {}
    for key in ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08", "kpi09"):
        scale = 100 if key == "kpi08" else 1
        if key == "kpi03":
            ref = OVER
        else:
            n, total = refs[key]
            ref = Fraction(total * scale, n) if n else None
        a = actual[key]
        more = None if a is None or ref is None else a * scale > ref
        less = None if a is None or ref is None else a * scale < ref
        out[key] = (res[key]["abweichung"], res[key]["vorlaeufig"], more, less)
    return out


def sim_summary(events: list[dict], light: Decimal, strong: Decimal) -> dict:
    """Je KPI: Anzahl leicht/stark und je Richtung (Fälle, Treffer, Spiele ohne Anomalie, davon Ereignis).
    Nur Spiele ohne vorläufigen Wert; leicht und stark zusammen (Regelwerk 11.2)."""
    out = {}
    for key in ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08", "kpi09"):
        c = {"leicht": 0, "stark": 0, "positiv": [0, 0], "negativ": [0, 0], "ohne_positiv": [0, 0],
             "ohne_negativ": [0, 0]}
        for ev in events:
            dev, provisional, more, less = ev[key]
            if dev is None or provisional:
                continue
            size = abs(dev)
            level = "keine" if size <= light else "leicht" if size <= strong else "stark"
            if level != "keine":
                c[level] += 1
            for direction, happened, sign in (("positiv", more, dev > 0), ("negativ", less, dev < 0)):
                if happened is None:
                    continue
                if level == "keine":
                    c["ohne_" + direction][0] += 1
                    c["ohne_" + direction][1] += int(happened)
                elif sign:
                    c[direction][0] += 1
                    c[direction][1] += int(happened)
        out[key] = c
    return out


# --- Sensitivitätsanalyse (Version 0.12, Spezifikation 11.11.2026), unabhängig von app/core/sensitivity.py -------------

def sens_closed_matchdays(lg: League, teams: int, seasons: set[str]) -> set[tuple[str, int]]:
    """Abgeschlossene Spieltage (Saison, Spieltag): alle Teams/2 Spiele gespielt; ein unvollständiger Spieltag zählt,
    wenn in derselben Saison ein späterer Spieltag vollständig ist."""
    out = set()
    for season in seasons:
        sizes = {gd: len(gs) for (s, gd), gs in lg.by_key.items() if s == season}
        complete = [gd for gd, n in sizes.items() if n == teams // 2]
        last = max(complete) if complete else 0
        out |= {(season, gd) for gd in sizes if gd in complete or gd < last}
    return out


def _wilson(k: int, n: int) -> tuple[float, float]:
    z = 1.959963984540054
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z / (1 + z * z / n) * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5
    return c - h, c + h


def sens_summary(events: list[tuple[str, tuple, dict]], closed: set[tuple[str, tuple]], lim: dict) -> dict:
    """events: (Liga, (Saison, Spieltag), sim_events-Ergebnis); closed: {(Liga, (Saison, Spieltag))}.
    lim: {"lp", "ln", "sp", "sn"} als Decimal in %, oder je Liga {Liga: {...}} (seit 0.13).
    Je KPI: Anzahl, Spieltage; Ergebnisqualität für leicht (q_) und stark (qs_): Treffer, Grundquote, Mehrwert, Spanne."""
    n_md = len(closed)
    out = {}
    for key in ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08", "kpi09"):
        r = {f"{st}_{d}": [0, set()] for st in ("leicht", "stark") for d in ("pos", "neg", "tot")}
        q = {f"{st}_{d}": [0, 0] for st in ("leicht", "stark") for d in ("pos", "neg")}
        q.update({"alle_pos": [0, 0], "alle_neg": [0, 0]})
        for league, md, ev in events:
            if (league, md) not in closed:
                continue
            dev, provisional, more, less = ev[key]
            if dev is None or provisional:
                continue
            t = lim[league] if league in lim else lim
            day = (league, md)
            for st, hi, lo in (("leicht", t["lp"], t["ln"]), ("stark", t["sp"], t["sn"])):
                for d, hit in (("pos", dev > hi), ("neg", dev < lo), ("tot", dev > hi or dev < lo)):
                    if hit:
                        r[f"{st}_{d}"][0] += 1
                        r[f"{st}_{d}"][1].add(day)
            for d, happened in (("pos", more), ("neg", less)):
                if happened is None:
                    continue
                q["alle_" + d][0] += 1
                q["alle_" + d][1] += int(happened)
                for st, border in (("leicht", t["lp"] if d == "pos" else t["ln"]),
                                   ("stark", t["sp"] if d == "pos" else t["sn"])):
                    if (dev > border) if d == "pos" else (dev < border):
                        q[f"{st}_{d}"][0] += 1
                        q[f"{st}_{d}"][1] += int(happened)
        res = {k: (v[0], v[0] / n_md, len(v[1]) / n_md * 100) for k, v in r.items()}
        for st, prefix in (("leicht", "q_"), ("stark", "qs_")):
            for d in ("pos", "neg"):
                (n, k), (n0, k0) = q[f"{st}_{d}"], q["alle_" + d]
                if n and n0:
                    p1, p2 = k / n, k0 / n0
                    (l1, u1), (l2, u2) = _wilson(k, n), _wilson(k0, n0)
                    low = p1 - p2 - ((p1 - l1) ** 2 + (u2 - p2) ** 2) ** 0.5
                    high = p1 - p2 + ((u1 - p1) ** 2 + (p2 - l2) ** 2) ** 0.5
                    res[prefix + d] = (n, k, 100 * p1, 100 * p2, 100 * (p1 - p2), 100 * low, 100 * high)
                else:                      # keine Anomalie: nur die Grundquote (hängt nicht von den Schwellen ab)
                    res[prefix + d] = (n, k, None, 100 * k0 / n0 if n0 else None, None, None, None)
        out[key] = res
    return out


# --- Empfehlung, Stabilität und Signalqualität (seit 0.19.1, Regelwerk 11.3) ------------------------------------------------

def _two(x: float) -> Decimal:
    """Wie angezeigt: zwei Nachkommastellen, kaufmännisch."""
    return Decimal(repr(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def rate_rule(n: int, gain: float | None, low: float | None, high: float | None) -> str:
    """Empfehlung nach Regelwerk 11.3, eigene Umsetzung (erste zutreffende Stufe gilt)."""
    if n < 50 or gain is None:
        return "Zu wenige Daten"
    g, lo, hi = _two(gain), _two(low), _two(high)
    if hi < 0:
        return "Negativ"
    if g >= 5 and lo > 2:
        return "Funktioniert"
    if g >= 2 and lo >= -5:
        return "Funktioniert leicht"
    if hi < 5:
        return "Keine relevante Verbesserung"
    return "Noch unklar"


def level_rule(recommendation: str, rate: float | None, gain: float | None, positive: int, seasons: int) -> str | None:
    """Signalqualität nach Regelwerk 2.2/11.3: nur bei mehreren Saisons, „Funktioniert“ und Mehrwert in mindestens zwei
    Dritteln der Saisons positiv (aufgerundet); stark ab 60 % und +8 Pp., mittel ab 55 %, gering ab 50 %."""
    if seasons < 2 or recommendation != "Funktioniert" or 3 * positive < 2 * seasons:
        return None
    q, g = _two(rate), _two(gain)
    if q >= 60 and g >= 8:
        return "stark"
    if q >= 55:
        return "mittel"
    if q >= 50:
        return "gering"
    return None


def sens_rating(events: list[tuple[str, tuple, dict]], closed: set[tuple[str, tuple]], lim: dict) -> dict:
    """Je KPI und Richtung (pos/neg): (Empfehlung, Saisons mit positivem Mehrwert, Saisons, Signalqualität).
    Gleiche Eingaben wie sens_summary (Schwelle der Richtung = „leicht“)."""
    out = {}
    for key in ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08", "kpi09"):
        seasons = set()
        per = {d: defaultdict(lambda: [0, 0, 0, 0]) for d in ("pos", "neg")}   # Saison -> n, k, n0, k0
        tot = {d: [0, 0, 0, 0] for d in ("pos", "neg")}
        for league, md, ev in events:
            if (league, md) not in closed:
                continue
            dev, provisional, more, less = ev[key]
            if dev is None or provisional:
                continue
            seasons.add(md[0])
            t = lim[league] if league in lim else lim
            for d, happened, flagged in (("pos", more, dev > t["lp"]), ("neg", less, dev < t["ln"])):
                if happened is None:
                    continue
                for acc in (per[d][md[0]], tot[d]):
                    acc[2] += 1
                    acc[3] += int(happened)
                    if flagged:
                        acc[0] += 1
                        acc[1] += int(happened)
        res = {}
        for d in ("pos", "neg"):
            n, k, n0, k0 = tot[d]
            positive = sum(1 for s in seasons
                           if per[d][s][0] and per[d][s][2] and per[d][s][1] / per[d][s][0] > per[d][s][3] / per[d][s][2])
            if n and n0:
                p1, p2 = k / n, k0 / n0
                (l1, u1), (l2, u2) = _wilson(k, n), _wilson(k0, n0)
                low = 100 * (p1 - p2 - ((p1 - l1) ** 2 + (u2 - p2) ** 2) ** 0.5)
                high = 100 * (p1 - p2 + ((u1 - p1) ** 2 + (p2 - l2) ** 2) ** 0.5)
                rec = rate_rule(n, 100 * (p1 - p2), low, high)
                res[d] = (rec, positive, len(seasons), level_rule(rec, 100 * p1, 100 * (p1 - p2), positive, len(seasons)))
            else:
                res[d] = (rate_rule(n, None, None, None), positive, len(seasons), None)
        out[key] = res
    return out
