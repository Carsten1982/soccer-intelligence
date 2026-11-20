"""Anzeige kommender Spieltage: Ligaseite und Top Anomalien (Version 0.16).

Regeln: docs/07_Spielplan_Anzeige.md (Spezifikation v2.1), Abschnitt 4, und der freigegebene Designentwurf vom
16.11.2026. Reine Funktionen ohne Oberfläche: „jetzt“ (Europe/Zurich, ohne Zeitzonenangabe) und der Tag des letzten
erfolgreichen Importlaufs werden übergeben. Dashboard und spätere öffentliche Website verwenden dieselben Funktionen;
die Oberfläche entscheidet nur über die Darstellung, nie darüber, welche Spiele erscheinen.

Begriffe (4.1):
- reguläres Spiel: Status „geplant“, ohne Vermerk
- Sonderspiel: Status „geplant“ mit Vermerk „Nachholspiel“ oder „vorgezogen“; es behält seine Spieltagsnummer
- Ende eines Spieltags: Tagesende des letzten Tages mit einem regulären Spiel
- anstehender Spieltag: der Spieltag mit dem frühesten Termin, dessen Ende noch nicht erreicht ist

Seit 0.20 (Entscheidungen Carsten 19.11.2026, `07`, 4.3 und 4.7):
- gespielt: ab Anpfiff + 2 Stunden (ohne bekannte Anstosszeit ab Mitternacht nach dem Spieltag) ausgegraut mit
  „Gespielt“, nach dem Import mit dem Endstand; bis dahin normal, ohne Live-Status und ohne „Ergebnis folgt“
- Datenstand: veraltet erst, wenn der letzte erfolgreiche Importlauf mehr als 48 Stunden zurückliegt
- Top Anomalien: die Spiele des Blocks bleiben bis zu seinem Ende stehen, gespielte ausgegraut; es rückt keines nach
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

import pandas as pd

from .fixtures import (
    HINT_CATCHUP, HINT_EARLY, INACTIVE_STATUS, STATUS_PLANNED, STATUS_POSTPONED, STATUS_SUSPENDED, TERMIN_PROVISIONAL,
    TERMIN_TIME_OPEN,
)

WINDOW_DAYS = 5       # weitere Spieltage und Sonderspiele: erstes Spiel heute bis heute + 5 (O2; seit 0.21.1,
                      # Entscheidung Carsten 20.11.2026; bis 0.21: heute + 6). Freitag-Spieltag ab Sonntag davor
PAUSE_DAYS = 14       # Pause: mehr als 14 Tage (O1); der nächste Spieltag erscheint ab 14 Tagen vorher
STALE_HOURS = 48      # Pausenhinweise nur, wenn der letzte erfolgreiche Importlauf höchstens 48 Stunden alt ist
                      # (S9; seit 0.20, bis 0.19.1: 3 Tage)
PLAYED_AFTER = timedelta(hours=2)   # ab Anpfiff + 2 Stunden „Gespielt“ (seit 0.20)
FORWARD = 2           # Navigation: höchstens 2 Spieltage über den anstehenden hinaus (4.4)

WEEKDAYS = ("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So")
MONTHS = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
          "November", "Dezember")
DAY_END = time(23, 59)

# Arten der Hinweis-Box über den Abschnitten
WINTER, BREAK, SUMMER, SEASON_START, STALE = "winterpause", "spielpause", "sommerpause", "saisonstart", "veraltet"


# --- Texte ---------------------------------------------------------------------------------

def day_text(d: date) -> str:
    """„Fr 20.11.“"""
    return f"{WEEKDAYS[d.weekday()]} {d:%d.%m.}"


def day_text_year(d: date) -> str:
    """„Fr 08.01.2027“"""
    return f"{WEEKDAYS[d.weekday()]} {d:%d.%m.%Y}"


def days_text(first: date, last: date) -> str:
    """„Fr 20.11. – So 22.11.“ bzw. „Mi 02.12.“"""
    return day_text(first) if first == last else f"{day_text(first)} – {day_text(last)}"


def games_text(n: int) -> str:
    return "1 Spiel" if n == 1 else f"{n} Spiele"


# --- Vorbereitung ----------------------------------------------------------------------------

def _clock(text) -> time | None:
    """„20:30“ -> 20:30; leer oder ungültig -> None."""
    try:
        hh, mm = str(text or "").strip().split(":")
        return time(int(hh), int(mm))
    except (TypeError, ValueError):
        return None


def _known_clock(row) -> time | None:
    return None if row.termin == TERMIN_TIME_OPEN else _clock(row.anstoss)


def kickoff(row) -> datetime:
    """Geplanter Anstoss. Ohne bekannte Uhrzeit (Zeit offen, alter Spielplan ohne Spalte Anstoss) gilt das
    Tagesende: Das Spiel bleibt den ganzen Tag „kommend“."""
    return datetime.combine(row.datum_von, _known_clock(row) or DAY_END)


def played_from(row) -> datetime:
    """Ab wann ein Spiel als gespielt gilt (seit 0.20): Anpfiff + 2 Stunden; ohne bekannte Anstosszeit ab
    Mitternacht nach dem Spieltag (keine angenommene Uhrzeit)."""
    clock = _known_clock(row)
    if clock is None:
        return datetime.combine(row.datum_von + timedelta(days=1), time(0, 0))
    return datetime.combine(row.datum_von, clock) + PLAYED_AFTER


def prepare(fixtures: pd.DataFrame) -> pd.DataFrame:
    """Spielplan einer Liga mit Hilfsspalten: anstoss_zeit, gespielt_ab, regulaer, sonderspiel, aktiv."""
    fx = fixtures.copy()
    for col in ("anstoss", "termin", "hinweis"):
        if col not in fx.columns:
            fx[col] = ""
        fx[col] = fx[col].fillna("")
    fx["anstoss_zeit"] = [kickoff(r) for r in fx.itertuples()] if len(fx) else pd.Series(dtype="object")
    fx["gespielt_ab"] = [played_from(r) for r in fx.itertuples()] if len(fx) else pd.Series(dtype="object")
    fx["aktiv"] = fx["status"].eq(STATUS_PLANNED)
    fx["regulaer"] = fx["aktiv"] & fx["hinweis"].eq("")
    fx["sonderspiel"] = fx["aktiv"] & fx["hinweis"].isin((HINT_CATCHUP, HINT_EARLY))
    return fx


def sort_games(games: pd.DataFrame) -> pd.DataFrame:
    """Innerhalb eines Abschnitts: nach Datum, dann Anstoss, dann Reihenfolge der Datei (4.2.7)."""
    return games.sort_values(["datum_von", "anstoss_zeit", "reihenfolge"], kind="stable").reset_index(drop=True)


@dataclass(frozen=True)
class Round:
    """Ein offizieller Spieltag mit dem Zeitraum seiner regulären Spiele."""
    saison: str
    spieltag: int
    first: date
    last: date

    @property
    def key(self) -> tuple[str, int]:
        return self.saison, self.spieltag


def rounds(fx: pd.DataFrame) -> list[Round]:
    """Spieltage mit mindestens einem regulären Spiel, nach Saison und Nummer."""
    reg = fx[fx["regulaer"]]
    if reg.empty:
        return []
    agg = reg.groupby(["saison", "spieltag"], sort=True).agg(first=("datum_von", "min"), last=("datum_bis", "max"))
    return [Round(s, int(md), r["first"], r["last"]) for (s, md), r in agg.iterrows()]


def next_round(all_rounds: list[Round], today: date) -> Round | None:
    """Anstehender Spieltag: frühester Termin, Ende noch nicht erreicht; bei gleichem Termin die kleinere Nummer."""
    pending = [r for r in all_rounds if r.last >= today]
    return min(pending, key=lambda r: (r.first, r.saison, r.spieltag)) if pending else None


def previous_round(all_rounds: list[Round], today: date) -> Round | None:
    """Zuletzt beendeter Spieltag (nach seinem Ende)."""
    ended = [r for r in all_rounds if r.last < today]
    return max(ended, key=lambda r: (r.last, r.saison, r.spieltag)) if ended else None


# --- Abschnitte und Hinweise der Ligaseite (4.2, 4.3) ------------------------------------------

@dataclass(frozen=True, eq=False)
class Section:
    """Ein Abschnitt der Ligaseite: genau ein offizieller Spieltag (bzw. seine Sonderspiele)."""
    saison: str
    spieltag: int
    hinweis: str                 # "" oder „Nachholspiel“ / „vorgezogen“
    games: pd.DataFrame          # sortiert (Datum, Anstoss, Datei)
    hidden: tuple[str, ...] = ()  # Status der nicht gezeigten Spiele (verschoben usw.), nur im Normalabschnitt
    rest: str = ""               # bei Sonderspielen: wann die übrigen Spiele des Spieltags sind („im Februar“)

    @property
    def key(self) -> tuple[str, int]:
        return self.saison, self.spieltag

    @property
    def first(self) -> date:
        return self.games["datum_von"].min()

    @property
    def last(self) -> date:
        return self.games["datum_von"].max()


@dataclass(frozen=True)
class Notice:
    kind: str                    # winterpause / spielpause / sommerpause / saisonstart / veraltet
    title: str                   # „Winterpause“
    text: str                    # „nächster Spieltag am Fr 08.01.2027“
    detail: str = ""             # „(Spieltag 15)“


@dataclass(frozen=True, eq=False)
class Upcoming:
    """Was die Ligaseite ohne Auswahl zeigt („Kommende Spiele“)."""
    sections: list[Section]
    notice: Notice | None
    anchor: tuple[str, int] | None      # anstehender Spieltag, sonst der letzte; Ausgangspunkt der Pfeile
    anchor_shown: bool                  # steht der Anker als Abschnitt auf der Seite?
    stale: bool                         # Datenstand älter als 48 Stunden (S9, seit 0.20)


def round_section(fx: pd.DataFrame, saison: str, spieltag: int, full: bool = False) -> Section:
    """Abschnitt eines Spieltags. full=True (Blättern, letzter Spieltag in der Sommerpause): alle Spiele mit
    Vermerken; sonst nur die regulären Spiele, die übrigen werden als „hidden“ gezählt."""
    games = fx[(fx["saison"] == saison) & (fx["spieltag"] == spieltag)]
    if full:
        return Section(saison, spieltag, "", sort_games(games))
    hidden = tuple(games.loc[~games["aktiv"], "status"])
    return Section(saison, spieltag, "", sort_games(games[games["regulaer"]]), hidden=hidden)


def _special_sections(fx: pd.DataFrame, specials: pd.DataFrame, all_rounds: list[Round]) -> list[Section]:
    by_key = {r.key: r for r in all_rounds}
    out = []
    for (saison, spieltag, hint), games in specials.groupby(["saison", "spieltag", "hinweis"], sort=True):
        r = by_key.get((saison, int(spieltag)))
        rest = f"übrige Spiele des Spieltags im {MONTHS[r.first.month - 1]}" if r else ""
        out.append(Section(saison, int(spieltag), hint, sort_games(games), rest=rest))
    return out


def is_stale(last_import: datetime | None, now: datetime) -> bool:
    """Datenstand veraltet: kein erfolgreicher Importlauf oder der letzte liegt mehr als 48 Stunden zurück (S9).
    last_import = Beginn des letzten erfolgreichen Laufs (Europe/Zurich, ohne Zeitzonenangabe)."""
    return last_import is None or now - last_import > timedelta(hours=STALE_HOURS)


def _has_christmas(start: date, end: date) -> bool:
    """Liegt ein 25.12. zwischen den beiden Tagen (Pause schliesst Weihnachten ein)?"""
    return any(start < date(y, 12, 25) < end for y in range(start.year, end.year + 1))


def _open_games(fx: pd.DataFrame, today: date) -> bool:
    """Noch offene Spiele der neuesten Saison: angesetzt (heute oder später) oder verschoben/ausgesetzt."""
    latest = fx[fx["saison"] == fx["saison"].max()]
    planned = latest["aktiv"] & (latest["datum_von"] >= today)
    return bool((planned | latest["status"].isin((STATUS_POSTPONED, STATUS_SUSPENDED))).any())


def upcoming(fixtures: pd.DataFrame, now: datetime, last_import: datetime | None) -> Upcoming:
    """Abschnitte und Hinweis der Ligaseite ohne Auswahl (Spezifikation 4.2 und 4.3)."""
    fx = prepare(fixtures)
    today = now.date()
    if fx.empty:
        return Upcoming([], None, None, False, is_stale(last_import, now))
    all_rounds = rounds(fx)
    nxt, prev = next_round(all_rounds, today), previous_round(all_rounds, today)
    window_end = today + timedelta(days=WINDOW_DAYS)

    sections: list[Section] = []
    if nxt is not None and (nxt.first - today).days <= PAUSE_DAYS:
        sections.append(round_section(fx, nxt.saison, nxt.spieltag))
        for r in all_rounds:                       # weitere Spieltage, die heute bis heute + 5 beginnen (O2)
            if r != nxt and r.last >= today and r.first <= window_end:
                sections.append(round_section(fx, r.saison, r.spieltag))
    specials = fx[fx["sonderspiel"] & (fx["datum_von"] >= today)]
    no_more_rounds = nxt is None
    if not no_more_rounds:
        specials = specials[specials["datum_von"] <= window_end]    # Sonderspiele ab heute + 5 (4.2.4)
    sections += _special_sections(fx, specials, all_rounds)

    notice, show_previous = None, False
    if nxt is None:
        if not _open_games(fx, today):
            notice, show_previous = Notice(SUMMER, "Sommerpause", ""), True
    elif prev is not None and nxt.saison != prev.saison:
        if (nxt.first - today).days > PAUSE_DAYS:                 # neue Saison angesetzt, Start in mehr als 14 Tagen
            notice = Notice(SEASON_START, "Sommerpause", f"Saisonstart am {day_text_year(nxt.first)}")
            show_previous = True
    elif prev is not None and (nxt.first - prev.last).days > PAUSE_DAYS and today < nxt.first:
        shown = any(s.key == nxt.key and not s.hinweis for s in sections)
        winter = _has_christmas(prev.last, nxt.first)
        notice = Notice(WINTER if winter else BREAK, "Winterpause" if winter else "Spielpause",
                        f"nächster Spieltag am {day_text_year(nxt.first)}",
                        "" if shown else f"(Spieltag {nxt.spieltag})")
    elif prev is None and (nxt.first - today).days > PAUSE_DAYS:
        notice = Notice(SEASON_START, "Sommerpause", f"Saisonstart am {day_text_year(nxt.first)}")

    if show_previous and prev is not None:
        sections.insert(0, round_section(fx, prev.saison, prev.spieltag, full=True))

    stale = is_stale(last_import, now)
    if stale:                                     # S9: keine Pausenhinweise, stattdessen der Datenstand
        when = day_text_year(last_import.date()) if last_import else "unbekannt (kein Importlauf gefunden)"
        notice = Notice(STALE, "Spielplan zuletzt aktualisiert am", when,
                        "Pausenhinweise ausgeblendet, bis der Import wieder läuft")
    if not sections and notice is None and prev is not None:       # nichts anstehend: letzter Spieltag
        sections.append(round_section(fx, prev.saison, prev.spieltag, full=True))

    sections.sort(key=lambda s: (s.first, s.saison, s.spieltag, s.hinweis))   # zeitlich, dann Nummer (S3)
    anchor = nxt.key if nxt else prev.key if prev else None
    anchor_shown = any(s.key == anchor and not s.hinweis for s in sections)
    return Upcoming(sections, notice, anchor, anchor_shown, stale)


# --- Navigation (4.4) ----------------------------------------------------------------------------

def choices(fixtures: pd.DataFrame, anchor: tuple[str, int] | None) -> list[tuple[str, int]]:
    """Wählbare Spieltage, alt -> neu: alle bis zum anstehenden, dazu höchstens 2 weitere."""
    keys = sorted({(s, int(m)) for s, m in zip(fixtures["saison"], fixtures["spieltag"])})
    if anchor is None or anchor not in keys:
        return keys
    return keys[:keys.index(anchor) + 1 + FORWARD]


# --- Spalte „Datum“ und Ergebnis (4.6) -----------------------------------------------------------

def results_index(prepared: pd.DataFrame | None) -> dict[tuple[str, str, str], tuple[int, int]]:
    """Ergebnisse der Datenbank je (Saison, Heim, Gast). Eine Paarung kommt je Saison genau einmal vor."""
    if prepared is None or prepared.empty:
        return {}
    return {(s, h, a): (int(hg), int(ag)) for s, h, a, hg, ag
            in zip(prepared["season"], prepared["home"], prepared["away"], prepared["hg"], prepared["ag"])}


@dataclass(frozen=True)
class DateCell:
    text: str            # „Fr 20.11. · 20:30“
    strong: str = ""     # fett hervorgehobener Teil („20:30“, „2:1“, „Gespielt“)
    grey: bool = False   # gespielt oder nicht aktiv: ganze Zeile grau
    active: bool = True  # False: verschoben usw., ohne KPI-Werte
    played: bool = False


def _weekend(d: date) -> str:
    """Platzhalter-Termin: „Wochenende 06./07.02.“ (Sa/So), sonst der Tag."""
    if d.weekday() not in (5, 6):
        return day_text(d)
    sat = d if d.weekday() == 5 else d - timedelta(days=1)
    sun = sat + timedelta(days=1)
    first = f"{sat:%d.}" if sat.month == sun.month else f"{sat:%d.%m.}"
    return f"Wochenende {first}/{sun:%d.%m.}"


def is_played(row, now: datetime, results: dict) -> bool:
    """Gilt das Spiel als gespielt (ausgegraut)? Mit Ergebnis in der Datenbank immer, sonst ab Anpfiff + 2 Stunden
    bzw. ab Mitternacht (seit 0.20). Verschobene usw. Spiele sind nie gespielt."""
    if row.status in INACTIVE_STATUS:
        return False
    return (row.saison, row.heim, row.gast) in results or now >= played_from(row)


def date_cell(row, now: datetime, results: dict) -> DateCell:
    """Spalte „Datum“: bis Anpfiff + 2 Stunden der Termin (auch während des Spiels), danach ausgegraut „Gespielt“,
    nach dem Import der Endstand (seit 0.20; bis 0.19.1 ab dem Anpfiff „Ergebnis folgt“)."""
    day = day_text(row.datum_von)
    if row.status in INACTIVE_STATUS:
        return DateCell(f"{day} · {row.status}", grey=True, active=False)
    score = results.get((row.saison, row.heim, row.gast))
    if score is not None:
        return DateCell(f"{day} · ", f"{score[0]}:{score[1]}", grey=True, played=True)
    if now >= played_from(row):
        return DateCell(f"{day} · ", "Gespielt", grey=True, played=True)
    if row.termin == TERMIN_PROVISIONAL:
        return DateCell(f"{_weekend(row.datum_von)} · Termin offen")
    if row.termin == TERMIN_TIME_OPEN:
        return DateCell("", f"{day} · Zeit offen")
    clock = _clock(row.anstoss)
    return DateCell("", f"{day} · {clock:%H:%M}" if clock else day)


# --- Wann KPI-Werte erscheinen (4.5) ----------------------------------------------------------

def _previous_game(fx: pd.DataFrame, team: str, before: datetime):
    """Das zeitlich letzte Ligaspiel des Teams vor dem Anstoss (nach echtem Termin, nicht nach Spieltagsnummer).
    Verschobene, abgesagte, abgebrochene, ausgesetzte und gewertete Spiele zählen nicht."""
    games = fx[fx["aktiv"] & ((fx["heim"] == team) | (fx["gast"] == team)) & (fx["anstoss_zeit"] < before)]
    if games.empty:
        return None
    return games.sort_values(["anstoss_zeit", "reihenfolge"], kind="stable").iloc[-1]


def missing_previous(fx: pd.DataFrame, row, results: dict) -> list[tuple[str, pd.Series]]:
    """Teams, deren vorheriges Ligaspiel noch kein Ergebnis in der Datenbank hat, mit diesem Spiel. Leer: Die Werte
    sind vollständig berechenbar (auch für den Schnappschuss, der darauf wartet)."""
    missing = []
    for team in (row.heim, row.gast):
        prev = _previous_game(fx, team, row.anstoss_zeit)
        if prev is not None and (prev["saison"], prev["heim"], prev["gast"]) not in results:
            missing.append((team, prev))
    return missing


@dataclass(frozen=True)
class Gate:
    """Warum ein Spiel noch keine Werte zeigt (4.5). Genau eines der beiden Datumsfelder ist gesetzt."""
    text: str                    # Text des Dashboards („Werte ab Do 03.12. – Real Madrid spielt vorher noch …“)
    ab: date | None = None       # „Werte ab“: Tag nach dem späteren der ausstehenden Vorspiele
    ergebnis_vom: date | None = None   # Vorspiel an einem früheren Tag gespielt, Ergebnis noch nicht übernommen


def values_from(fx: pd.DataFrame, row, now: datetime, results: dict) -> Gate | None:
    """None: Werte zeigen. Sonst warum noch nicht. Werte erscheinen erst, wenn beide Teams ihr vorheriges Ligaspiel
    gespielt haben und das Ergebnis in der Datenbank steht. Nach dem Anstoss nie (seit 0.20, Entscheidungsprotokoll
    4a: dann gilt der Schnappschuss bzw. die nachträgliche Berechnung). fx = prepare(...) mit beiden Saisons."""
    if now >= row.anstoss_zeit:
        return None
    missing = missing_previous(fx, row, results)
    if not missing:
        return None
    latest = max(p["datum_von"] for _, p in missing)
    if latest < now.date():                       # Vorspiel an einem früheren Tag, Ergebnis noch nicht übernommen
        return Gate(f"Werte folgen, sobald das Ergebnis vom {day_text(latest)} übernommen ist", ergebnis_vom=latest)
    ab = latest + timedelta(days=1)
    return Gate(_gate_text(missing, now, f"Werte ab {day_text(ab)} – "), ab=ab)


def values_gate(fx: pd.DataFrame, row, now: datetime, results: dict) -> str | None:
    """Wie values_from, nur der Text des Dashboards („Werte ab Do 03.12. – Real Madrid spielt vorher noch
    (Mi 02.12.)“); None: Werte zeigen."""
    gate = values_from(fx, row, now, results)
    return gate.text if gate else None


def _gate_text(missing: list, now: datetime, head: str) -> str:
    ahead = [(team, p) for team, p in missing if p["datum_von"] >= now.date()]   # nur wer wirklich noch spielt
    if len(ahead) == 1:
        team, p = ahead[0]
        return f"{head}{team} spielt vorher noch ({day_text(p['datum_von'])})"
    (a, pa), (b, pb) = ahead
    if (pa["saison"], pa["spieltag"]) == (pb["saison"], pb["spieltag"]):
        return f"{head}beide Teams spielen vorher noch (Spieltag {int(pa['spieltag'])})"
    return f"{head}{a} ({day_text(pa['datum_von'])}) und {b} ({day_text(pb['datum_von'])}) spielen vorher noch"


# --- Top Anomalien: Block je Liga (4.7) ----------------------------------------------------------

@dataclass(frozen=True, eq=False)
class Block:
    """Der zeitlich nächste Block einer Liga für die Top Anomalien."""
    label: str                 # „Spieltag 10“ bzw. „Spieltag 23 · vorgezogen“
    games: pd.DataFrame        # alle angesetzten Spiele des Blocks, auch angepfiffene (seit 0.20: kein Nachrücken)
    remaining: int             # davon noch nicht angepfiffen
    takes_part: bool           # höchstens 14 Tage entfernt
    header: str                # Kopfzeile ohne Liganame: „Spieltag 10 · noch 4 Spiele“


def top_block(fixtures: pd.DataFrame, now: datetime, last_import: datetime | None) -> Block | None:
    """Je Liga ein Block: normal der anstehende Spieltag samt Sonderspielen an seinen Tagen; Sonderspiele vor dem
    nächsten Spieltag bilden einen eigenen Block bis zu ihrem Tagesende. Seit 0.20 bleiben angepfiffene Spiele im
    Block (ausgegraut), damit die Liste bis zum Ende des Blocks gleich bleibt (bis 0.19.1: nur vor dem Anpfiff, S7)."""
    fx = prepare(fixtures)
    today = now.date()
    if fx.empty:
        return None
    all_rounds = rounds(fx)
    nxt = next_round(all_rounds, today)
    specials = fx[fx["sonderspiel"] & (fx["datum_von"] >= today)]
    early = specials if nxt is None else specials[specials["datum_von"] < nxt.first]
    if not early.empty:                                   # Sonderspiele vor dem nächsten Spieltag
        day = early["datum_von"].min()
        games = early[early["datum_von"] == day]
        keys = sorted({(s, int(m), h) for s, m, h in zip(games["saison"], games["spieltag"], games["hinweis"])})
        label = " · ".join(f"Spieltag {m} · {h}" for _, m, h in keys)
        start = day
    elif nxt is not None:
        in_round = fx["regulaer"] & (fx["saison"] == nxt.saison) & (fx["spieltag"] == nxt.spieltag)
        same_days = fx["sonderspiel"] & fx["datum_von"].between(nxt.first, nxt.last)
        games = fx[in_round | same_days]
        label, start = f"Spieltag {nxt.spieltag}", nxt.first
    else:
        return None
    games = sort_games(games)
    remaining = int((games["anstoss_zeit"] > now).sum())
    takes_part = (start - today).days <= PAUSE_DAYS
    if takes_part:
        state = f"noch {games_text(remaining)}" if remaining else "alle Spiele angepfiffen"
        header = f"{label} · {state}"
    else:
        header = _pause_header(fixtures, now, last_import, start)
    return Block(label, games, remaining, takes_part, header)


def _pause_header(fixtures: pd.DataFrame, now: datetime, last_import: datetime | None, start: date) -> str:
    """Kopfzeile einer Liga, deren Block mehr als 14 Tage entfernt ist: „Winterpause bis 07.01.“."""
    view = upcoming(fixtures, now, last_import)
    until = f"{start - timedelta(days=1):%d.%m.}"
    n = view.notice
    if n is not None and n.kind in (WINTER, BREAK, SEASON_START):
        return f"{n.title} bis {until}"
    if n is not None and n.kind == SUMMER:
        return "Sommerpause"
    return f"nächster Spieltag am {day_text(start)}"


# --- Vorschau im Reiter Datenimport/API (Spielplan v2.1, Abschnitt 5) ----------------------------------

@dataclass(frozen=True)
class Preview:
    """Eine Zeile „So sieht das Dashboard nach der Übernahme aus“."""
    shown: str      # „Spieltag 12 · Fr 04.12. – So 06.12.“ bzw. der Hinweis
    games: str      # „9“ bzw. „2 + 10“
    top: str        # Block der Top Anomalien
    until: str      # „So 06.12., Tagesende“


def preview(fixtures: pd.DataFrame, now: datetime) -> Preview:
    """Was die Ligaseite und die Top Anomalien mit diesem Spielplan zeigen würden (Datenstand = heute)."""
    view = upcoming(fixtures, now, now)
    parts = []
    for s in view.sections:
        tag = f" ({s.hinweis})" if s.hinweis else ""
        hidden = f" ({games_text(len(s.hidden))} {'/'.join(dict.fromkeys(s.hidden))})" if s.hidden else ""
        parts.append(f"Spieltag {s.spieltag}{tag} · {days_text(s.first, s.last)}{hidden}")
    if view.notice is not None:
        text = " – ".join(x for x in (view.notice.title, view.notice.text) if x)
        parts.insert(0, f"{text} {view.notice.detail}".strip())
    block = top_block(fixtures, now, now)
    return Preview("; ".join(parts) or "–", " + ".join(str(len(s.games)) for s in view.sections) or "–",
                   block.header if block else "–",
                   " bzw. ".join(f"{day_text(s.last)}, Tagesende" for s in view.sections) or "–")
