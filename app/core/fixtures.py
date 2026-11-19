"""Einlesen und Prüfen des Spielplans (data/Spielplan.xlsx).

Regeln: docs/04_Spielplan.md, Abschnitte 2, 3 und 5.

Grundsätze:
- Die Datei wird nur gelesen, nie geschrieben.
- Der Spielplan enthält nur angesetzte Begegnungen, keine Ergebnisse.
- Ein Fehler sperrt den ganzen Spielplan (das Dashboard zeigt dann einen Hinweis).
  Warnungen und Hinweise sperren nichts.
"""

from __future__ import annotations

import math
import numbers
import re
import zipfile
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from io import BytesIO
from pathlib import Path

import pandas as pd

from .config import League, Team
from .files import read_file
from .issues import FEHLER, HINWEIS, WARNUNG, Issue

# --- Aufbau der Datei ------------------------------------------------------

COL_SEASON = "Saison"
COL_MATCHDAY = "Spieltag"
COL_FROM = "Datum von"
COL_TO = "Datum bis"
COL_HOME = "Heimmannschaft"
COL_AWAY = "Gastmannschaft"
COL_STATUS = "Status"
# Optionale Spalten, seit 0.14/0.15 vom Datenimport geschrieben (Spezifikation Spielplan v2.1, Abschnitt 3)
COL_KICKOFF = "Anstoss"
COL_TERMIN = "Termin"
COL_HINT = "Hinweis"
COL_API_STATUS = "API-Status"
COL_API_ID = "API-ID"

REQUIRED_COLUMNS = (COL_SEASON, COL_MATCHDAY, COL_FROM, COL_TO, COL_HOME, COL_AWAY)

STATUS_PLANNED = "geplant"
STATUS_POSTPONED = "verschoben"
STATUS_CANCELLED = "abgesagt"
STATUS_ABANDONED = "abgebrochen"          # seit Version 0.14 (Datenimport, E9): wie abgesagt behandelt
STATUS_SUSPENDED = "ausgesetzt"           # seit 0.15 (S1): API SUSP, Fortsetzung an einem anderen Tag
STATUS_AWARDED = "gewertet"               # seit 0.15 (S1): API AWD/WO, am grünen Tisch bzw. kampflos gewertet
ALLOWED_STATUS = (STATUS_PLANNED, STATUS_POSTPONED, STATUS_CANCELLED, STATUS_ABANDONED, STATUS_SUSPENDED,
                  STATUS_AWARDED)
# Spiele mit diesem Status zählen nicht für „Spieltag beendet“ und erhalten keine KPI-Werte
INACTIVE_STATUS = frozenset({STATUS_POSTPONED, STATUS_CANCELLED, STATUS_ABANDONED, STATUS_SUSPENDED, STATUS_AWARDED})
# Vermerke und Terminarten (Spalten Hinweis und Termin); leer ist immer erlaubt
HINT_CATCHUP, HINT_EARLY = "Nachholspiel", "vorgezogen"
ALLOWED_HINTS = (HINT_CATCHUP, HINT_EARLY)
TERMIN_CONFIRMED, TERMIN_TIME_OPEN, TERMIN_PROVISIONAL = "bestätigt", "Zeit offen", "vorläufig"
ALLOWED_TERMIN = (TERMIN_CONFIRMED, TERMIN_TIME_OPEN, TERMIN_PROVISIONAL)

SEASON_PATTERN = re.compile(r"^\d{4}/\d{4}$")

# Spalten des aufbereiteten Spielplans je Liga
FIXTURE_COLUMNS = ["saison", "spieltag", "datum_von", "datum_bis", "heim", "gast", "status", "excel_row", "reihenfolge",
                   "anstoss", "termin", "hinweis", "api_status", "api_id"]

# Hinweise je Team (für Anzeige in der Datenqualität)
NOTE_PROMOTED = "Aufsteiger ohne Daten in der Datenbank"
NOTE_NO_WINDOW = "keine Ligaspiele in Saison und Vorsaison"
NOTE_UNKNOWN = "Name unbekannt"


@dataclass
class FixturesLoad:
    path: Path
    leagues: dict[str, pd.DataFrame] = field(default_factory=dict)
    issues: list[Issue] = field(default_factory=list)
    # (Liga, Saison, Team) -> Hinweistext, z. B. Aufsteiger ohne Daten
    team_notes: dict[tuple[str, str, str], str] = field(default_factory=dict)
    file_modified: datetime | None = None
    sha256: str | None = None
    loaded_at: datetime | None = None

    @property
    def has_errors(self) -> bool:
        return any(i.level == FEHLER for i in self.issues)

    def count(self, level: str) -> int:
        return sum(1 for i in self.issues if i.level == level)

    def issues_frame(self) -> pd.DataFrame:
        cols = ["Stufe", "Blatt", "Prüfung", "Details", "Begegnung", "Excel-Zeile"]
        frame = pd.DataFrame([i.as_dict() for i in self.issues], columns=cols)
        frame["Excel-Zeile"] = pd.array(frame["Excel-Zeile"], dtype="Int64")
        return frame


# --- Hilfsfunktionen -------------------------------------------------------

def _is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if value is pd.NaT:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _as_date(value) -> date | None:
    """Echtes Excel-Datum -> date. Text (z. B. „28.08-30.08“) oder Zahl -> None."""
    if isinstance(value, datetime):          # auch pd.Timestamp
        return None if pd.isna(value) else value.date()
    if isinstance(value, date):
        return value
    return None


def _as_matchday(value) -> int | None:
    if isinstance(value, bool) or not isinstance(value, numbers.Number):
        return None
    number = float(value)
    if not number.is_integer() or number < 1:
        return None
    return int(number)


def _text(row, column: str) -> str:
    """Optionale Textspalte: fehlt sie oder ist sie leer -> ''."""
    if column not in row or _is_empty(row[column]):          # row: Zeile als dict (seit 0.19.1) oder Series
        return ""
    return str(row[column]).strip()


def previous_season(season: str) -> str:
    start, end = season.split("/")
    return f"{int(start) - 1}/{int(end) - 1}"


def _label(home, away, matchday) -> str:
    md = f" (Spieltag {matchday})" if matchday is not None else ""
    return f"{home or '?'} – {away or '?'}{md}"


# --- Einlesen einer Liga ---------------------------------------------------

def _parse_sheet(league: str, raw: pd.DataFrame) -> tuple[pd.DataFrame, list[Issue]]:
    """Prüft Pflichtspalten und Pflichtfelder. Gibt nur gültige Zeilen zurück."""
    issues: list[Issue] = []
    raw = raw.rename(columns=lambda c: str(c).strip())

    missing = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
    if missing:
        issues.append(Issue(
            FEHLER, league, "Pflichtspalte fehlt",
            f"Spalte(n) {', '.join(missing)} fehlen oder sind falsch geschrieben. "
            f"Erwartet: {', '.join(REQUIRED_COLUMNS)} (Status optional)",
        ))
        return pd.DataFrame(columns=FIXTURE_COLUMNS), issues

    has_status = COL_STATUS in raw.columns
    rows = []
    for idx, r in zip(raw.index, raw.to_dict("records")):    # dict statt iterrows: rund doppelt so schnell (B5)
        values = [r[c] for c in REQUIRED_COLUMNS] + ([r[COL_STATUS]] if has_status else [])
        if all(_is_empty(v) for v in values):
            continue                                    # komplett leere Zeile (Formatierung) ignorieren
        excel_row = int(idx) + 2
        home = None if _is_empty(r[COL_HOME]) else str(r[COL_HOME]).strip()
        away = None if _is_empty(r[COL_AWAY]) else str(r[COL_AWAY]).strip()
        md_raw = r[COL_MATCHDAY]
        matchday = _as_matchday(md_raw)
        label = _label(home, away, matchday)

        def err(check: str, msg: str) -> None:
            issues.append(Issue(FEHLER, league, check, msg, match=label, excel_row=excel_row))

        empty = [c for c in REQUIRED_COLUMNS if _is_empty(r[c])]
        if empty:
            err("Pflichtfeld leer", f"Leer: {', '.join(empty)}")
            continue

        ok = True
        season = str(r[COL_SEASON]).strip()
        if not SEASON_PATTERN.match(season):
            err("Saison ungültig", f"Saison = '{r[COL_SEASON]}' (erwartet JJJJ/JJJJ, z. B. 2026/2027)")
            ok = False
        if matchday is None:
            err("Spieltag ungültig", f"Spieltag = '{md_raw}' (erwartet ganze Zahl ab 1)")
            ok = False
        d_from, d_to = _as_date(r[COL_FROM]), _as_date(r[COL_TO])
        if d_from is None:
            err("Datum ungültig", f"Datum von = '{r[COL_FROM]}' ist kein Excel-Datum")
            ok = False
        if d_to is None:
            err("Datum ungültig", f"Datum bis = '{r[COL_TO]}' ist kein Excel-Datum")
            ok = False
        if d_from and d_to and d_to < d_from:
            err("Datum bis vor Datum von", f"Datum bis {d_to:%d.%m.%Y} liegt vor Datum von {d_from:%d.%m.%Y}")
            ok = False
        status = STATUS_PLANNED
        if has_status and not _is_empty(r[COL_STATUS]):
            status = str(r[COL_STATUS]).strip().lower()
            if status not in ALLOWED_STATUS:
                err("Status ungültig", f"Status = '{r[COL_STATUS]}' (erlaubt: leer, {', '.join(ALLOWED_STATUS)})")
                ok = False
        extra = {"anstoss": _text(r, COL_KICKOFF), "termin": _text(r, COL_TERMIN), "hinweis": _text(r, COL_HINT),
                 "api_status": _text(r, COL_API_STATUS).upper(), "api_id": None}
        if extra["hinweis"] and extra["hinweis"] not in ALLOWED_HINTS:
            err("Hinweis ungültig", f"Hinweis = '{extra['hinweis']}' (erlaubt: leer, {', '.join(ALLOWED_HINTS)})")
            ok = False
        if extra["termin"] and extra["termin"] not in ALLOWED_TERMIN:
            err("Termin ungültig", f"Termin = '{extra['termin']}' (erlaubt: leer, {', '.join(ALLOWED_TERMIN)})")
            ok = False
        if COL_API_ID in raw.columns and not _is_empty(r[COL_API_ID]):
            extra["api_id"] = _as_matchday(r[COL_API_ID])          # ganze Zahl ab 1
            if extra["api_id"] is None:
                err("API-ID ungültig", f"API-ID = '{r[COL_API_ID]}' (erwartet ganze Zahl)")
                ok = False
        if ok:
            rows.append({
                "saison": season, "spieltag": matchday, "datum_von": d_from, "datum_bis": d_to,
                "heim": home, "gast": away, "status": status,
                "excel_row": excel_row, "reihenfolge": len(rows), **extra,
            })
    return pd.DataFrame(rows, columns=FIXTURE_COLUMNS), issues


# --- Plausibilität ----------------------------------------------------------

def _plausibility(league: League, df: pd.DataFrame) -> list[Issue]:
    issues: list[Issue] = []
    name = league.name

    def warn(check, msg, r=None):
        label = _label(r["heim"], r["gast"], r["spieltag"]) if r is not None else None
        row = int(r["excel_row"]) if r is not None else None
        issues.append(Issue(WARNUNG, name, check, msg, match=label, excel_row=row))

    for r in df[df["heim"] == df["gast"]].to_dict("records"):
        warn("Heim = Gast", "Heim- und Gastmannschaft identisch", r)

    for (season, md), g in df.groupby(["saison", "spieltag"], sort=True):
        teams = pd.concat([g["heim"], g["gast"]])
        for team in sorted(teams[teams.duplicated()].unique()):
            games = g[(g["heim"] == team) | (g["gast"] == team)]
            if len(games) > 1:                      # „Heim = Gast“ wird oben gemeldet
                warn("Team mehrfach im Spieltag", f"{team} kommt in Saison {season}, Spieltag {md} mehrfach vor",
                     games.iloc[1])
        if len(g) < league.games_per_matchday:
            warn("Spieltag unvollständig",
                 f"Saison {season}, Spieltag {md}: {len(g)} statt {league.games_per_matchday} Spiele "
                 f"({league.teams} Teams laut Konfiguration)")

    pairs = df[df.duplicated(["saison", "heim", "gast"], keep="first")]
    for r in pairs.to_dict("records"):
        warn("Paarung doppelt", f"Paarung kommt in Saison {r['saison']} mehrfach vor", r)
    return issues


def _team_checks(
    league: League,
    df: pd.DataFrame,
    db_games: pd.DataFrame | None,
    known_extra: set[str],
) -> tuple[list[Issue], dict[tuple[str, str, str], str]]:
    """Teamnamen gegen Datenbank und Teamliste.

    Seit 0.15 entfällt der Hinweis „Begegnung bereits gespielt“: Der Spielplan enthält seit dem Datenimport (0.14)
    absichtlich die ganze Saison und die Vorsaison, also auch gespielte Spiele."""
    issues: list[Issue] = []
    notes: dict[tuple[str, str, str], str] = {}
    name = league.name

    if db_games is not None and not db_games.empty:
        db_teams = set(db_games["homeTeam"]) | set(db_games["awayTeam"])
    else:
        db_teams = set()

    for season, g in df.groupby("saison", sort=True):
        window = {season, previous_season(season)}
        if db_games is not None and not db_games.empty:
            in_window = db_games[db_games["Season"].isin(window)]
            window_teams = set(in_window["homeTeam"]) | set(in_window["awayTeam"])
        else:
            window_teams = set()
        for team in sorted(set(g["heim"]) | set(g["gast"])):
            first = g[(g["heim"] == team) | (g["gast"] == team)].iloc[0]
            row = int(first["excel_row"])
            if team not in db_teams and team not in known_extra:
                notes[(name, season, team)] = NOTE_UNKNOWN
                issues.append(Issue(
                    WARNUNG, name, "Teamname unbekannt",
                    f"'{team}' steht weder in der Datenbank noch in der Teamliste (config/teams.toml). "
                    "Aufsteiger oder Schreibfehler?",
                    match=_label(first["heim"], first["gast"], first["spieltag"]), excel_row=row,
                ))
            elif team not in db_teams:
                notes[(name, season, team)] = NOTE_PROMOTED
                issues.append(Issue(
                    HINWEIS, name, "Aufsteiger ohne Daten",
                    f"'{team}' (Teamliste) hat keine Spiele in der Datenbank. KPIs erscheinen als „–“.",
                    excel_row=row,
                ))
            elif team not in window_teams:
                notes[(name, season, team)] = NOTE_NO_WINDOW
                issues.append(Issue(
                    HINWEIS, name, "Keine Ligadaten im Zeitfenster",
                    f"'{team}' hat keine Ligaspiele in {previous_season(season)} oder {season}. "
                    "KPIs erscheinen als „–“.",
                    excel_row=row,
                ))
    return issues, notes


def _awarded_but_played(league: League, df: pd.DataFrame, db_games: pd.DataFrame | None
                        ) -> tuple[pd.DataFrame, list[Issue]]:
    """Absicherung gegen nachträgliches „gewertet“ (seit 0.20, Entscheidungsprotokoll 19.11.2026, Nr. 1; `07`, 4.1).

    „Am grünen Tisch gewertet“ gilt nur für nie gespielte Spiele. Meldet die API für ein Spiel AWD/WO, dessen Ergebnis
    vom Platz schon in der Datenbank steht (das Spiel wurde gespielt und später anders gewertet), bleibt es ein
    gespieltes Spiel mit dem Ergebnis vom Platz: Status „geplant“, die Spalte API-Status behält AWD/WO. Die Datei wird
    dabei nicht verändert, nur die eingelesene Fassung."""
    if db_games is None or db_games.empty or not df["status"].eq(STATUS_AWARDED).any():
        return df, []
    played = set(zip(db_games["Season"], db_games["homeTeam"], db_games["awayTeam"]))
    hit = df["status"].eq(STATUS_AWARDED) & pd.Series(
        [(s, h, a) in played for s, h, a in zip(df["saison"], df["heim"], df["gast"])], index=df.index)
    if not hit.any():
        return df, []
    df = df.copy()
    df.loc[hit, "status"] = STATUS_PLANNED
    issues = [Issue(
        HINWEIS, league.name, "Gewertet, aber gespielt",
        "Der Spielplan meldet „gewertet“, die Datenbank hat das Ergebnis vom Platz: Das Spiel gilt als gespielt "
        "und zeigt dieses Ergebnis.",
        match=_label(r["heim"], r["gast"], r["spieltag"]), excel_row=int(r["excel_row"]),
    ) for _, r in df[hit].iterrows()]
    return df, issues


# --- Hauptfunktion -------------------------------------------------------

def load_fixtures(
    path: Path | str,
    leagues: list[League],
    db_leagues: dict[str, pd.DataFrame] | None = None,
    teams: list[Team] | None = None,
) -> FixturesLoad:
    """Liest den Spielplan für alle aktiven Ligen und prüft ihn.

    leagues     alle Ligen aus der Konfiguration (aktive und inaktive)
    db_leagues  eingelesene Datenbank je Liga (für Teamnamen und gespielte Begegnungen)
    teams       Teamliste (bekannte Teams ohne Datenbankeinträge, z. B. Aufsteiger)
    """
    path = Path(path)
    result = FixturesLoad(path=path, loaded_at=datetime.now(timezone.utc))
    db_leagues = db_leagues or {}
    known_extra = {t.team_name for t in (teams or [])}
    sheet = "Spielplan"

    if not path.exists():
        result.issues.append(Issue(FEHLER, sheet, "Datei fehlt", f"Datei nicht gefunden: {path}"))
        return result
    try:
        # Datei nur einmal lesen: Prüfsumme und Inhalt stammen so sicher vom selben Stand (H.2)
        content = read_file(path)
        result.sha256, result.file_modified = content.sha256, content.modified
        sheets = pd.read_excel(BytesIO(content.data), sheet_name=None, engine="openpyxl", dtype=object)
    # SyntaxError: kaputtes XML in der Datei (xml ParseError und lxml XMLSyntaxError sind beide SyntaxError)
    except (zipfile.BadZipFile, SyntaxError, ValueError, OSError, KeyError) as exc:
        result.issues.append(Issue(
            FEHLER, sheet, "Datei nicht lesbar",
            f"Der Spielplan konnte nicht gelesen werden ({type(exc).__name__}: {exc}). "
            "Möglicherweise ist die Datei beschädigt oder der Upload noch nicht abgeschlossen.",
        ))
        return result

    configured = {lg.name for lg in leagues}
    for name in sheets:
        if name not in configured:
            result.issues.append(Issue(HINWEIS, name, "Unbekanntes Blatt", f"Blatt '{name}' wird ignoriert"))

    for league in leagues:
        raw = sheets.get(league.name)
        if raw is None:
            if league.aktiv:
                result.issues.append(Issue(
                    FEHLER, league.name, "Blatt fehlt",
                    f"Für die aktive Liga '{league.name}' gibt es kein Tabellenblatt im Spielplan",
                ))
            continue
        if raw.dropna(how="all").empty:
            if league.aktiv:
                result.issues.append(Issue(
                    WARNUNG, league.name, "Blatt leer",
                    f"Für die aktive Liga '{league.name}' sind keine Begegnungen eingetragen",
                ))
            else:
                result.issues.append(Issue(
                    HINWEIS, league.name, "Blatt leer", "Leeres Tabellenblatt einer noch nicht aktiven Liga",
                ))
            continue
        if not league.aktiv:
            result.issues.append(Issue(
                HINWEIS, league.name, "Liga nicht aktiv",
                "Blatt enthält Begegnungen, die Liga ist in config/ligen.toml aber nicht aktiv",
            ))
            continue

        df, issues = _parse_sheet(league.name, raw)
        result.issues += issues
        if not df.empty:
            df, awarded = _awarded_but_played(league, df, db_leagues.get(league.name))
            result.issues += awarded
            result.issues += _plausibility(league, df)
            team_issues, notes = _team_checks(league, df, db_leagues.get(league.name), known_extra)
            result.issues += team_issues
            result.team_notes.update(notes)
        result.leagues[league.name] = df

    return result
