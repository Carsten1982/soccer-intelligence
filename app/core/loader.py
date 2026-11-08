"""Einlesen und Strukturprüfung der Excel-Datenbank.

Grundsätze:
- Die Datei wird nur gelesen, nie geschrieben.
- Leere Statistikzellen bleiben leer (NaN). Es wird nie mit 0 aufgefüllt.
- Strukturfehler werden als FEHLER gemeldet; die App zeigt dann keine Auswertungen.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from . import schema, settings
from .files import sha256_of
from .issues import FEHLER, HINWEIS, WARNUNG, Issue
from .rows import row_issues
from .validation import run_plausibility_checks


@dataclass
class DatabaseLoad:
    path: Path
    leagues: dict[str, pd.DataFrame] = field(default_factory=dict)
    notes: pd.DataFrame | None = None
    issues: list[Issue] = field(default_factory=list)
    file_size: int | None = None
    file_modified: datetime | None = None
    sha256: str | None = None
    loaded_at: datetime | None = None

    @property
    def has_errors(self) -> bool:
        return any(i.level == FEHLER for i in self.issues)

    def count(self, level: str) -> int:
        return sum(1 for i in self.issues if i.level == level)

    def issues_frame(self) -> pd.DataFrame:
        cols = ["Stufe", "Blatt", "Prüfung", "Details", "id", "Begegnung", "Excel-Zeile"]
        frame = pd.DataFrame([i.as_dict() for i in self.issues], columns=cols)
        for c in ("id", "Excel-Zeile"):
            frame[c] = pd.array(frame[c], dtype="Int64")
        return frame


# --- Strukturprüfung eines Ligablatts --------------------------------------

def _check_columns(sheet: str, df: pd.DataFrame) -> list[Issue]:
    actual = [str(c) for c in df.columns]
    expected = list(schema.EXPECTED_COLUMNS)
    if actual == expected:
        return []
    missing = [c for c in expected if c not in actual]
    extra = [c for c in actual if c not in expected]
    parts = [f"{len(actual)} statt {len(expected)} Spalten"]
    if missing:
        parts.append("fehlend: " + ", ".join(missing[:10]))
    if extra:
        parts.append("unerwartet: " + ", ".join(extra[:10]))
    if not missing and not extra:
        pos = next(i for i, (a, e) in enumerate(zip(actual, expected)) if a != e)
        parts = [
            f"Spaltenreihenfolge weicht ab ab Spalte {pos + 1}: "
            f"gefunden '{actual[pos]}', erwartet '{expected[pos]}'"
        ]
    return [Issue(FEHLER, sheet, "Spaltenstruktur", "; ".join(parts))]


def _prepare_league(sheet: str, raw: pd.DataFrame) -> tuple[pd.DataFrame, list[Issue]]:
    """Typen umwandeln und harte Fehler sammeln. Gibt eine bereinigte Kopie zurück."""
    issues: list[Issue] = []
    df = raw.copy()

    # Pflichtfelder dürfen nicht leer sein
    for col in schema.REQUIRED_COLUMNS:
        empty = df[df[col].isna() | (df[col].astype("string").str.strip() == "")]
        if len(empty):
            issues += row_issues(FEHLER, sheet, "Pflichtfeld leer", empty, f"Spalte '{col}' ist leer")

    # Zahlen: Pflicht-Ganzzahlen und optionale Statistikwerte
    for col in schema.INTEGER_REQUIRED + schema.NUMERIC_OPTIONAL:
        converted = pd.to_numeric(df[col], errors="coerce")
        bad = df[df[col].notna() & converted.isna()]
        if len(bad):
            issues += row_issues(
                FEHLER, sheet, "Keine Zahl", bad,
                lambda r, c=col: f"Spalte '{c}' enthält '{r[c]}' statt einer Zahl",
            )
        # Kommazahl, wo eine ganze Zahl stehen muss (seit H.1). Es wird nie abgeschnitten:
        # Gameday, id, Tore -> Fehler. Ecken, Karten, Schüsse -> Warnung, der Wert gilt als fehlend (nie als 0).
        if col in schema.INTEGER_REQUIRED or col in schema.COUNT_COLUMNS:
            fraction = converted.notna() & (converted % 1 != 0)
            if fraction.any():
                required = col in schema.INTEGER_REQUIRED
                issues += row_issues(
                    FEHLER if required else WARNUNG, sheet, "Keine ganze Zahl", df[fraction],
                    lambda r, c=col, req=required: f"Spalte '{c}' enthält {r[c]} statt einer ganzen Zahl"
                    + ("" if req else " (wird als fehlender Wert behandelt)"),
                )
                if not required:
                    converted = converted.mask(fraction)
        df[col] = converted
        neg = df[df[col] < 0]
        if len(neg):
            issues += row_issues(WARNUNG, sheet, "Negativer Wert", neg,
                                 lambda r, c=col: f"Spalte '{c}' = {r[c]}")

    # Ergebnis-Buchstaben
    for col in schema.RESULT_COLUMNS:
        s = df[col].astype("string").str.strip()
        bad = df[s.notna() & ~s.isin(schema.VALID_RESULTS)]
        if len(bad):
            issues += row_issues(FEHLER, sheet, "Ungültiges Ergebnis", bad,
                                 lambda r, c=col: f"Spalte '{c}' = '{r[c]}' (erlaubt: H, D, A)")
        df[col] = s

    # Datum
    dates = pd.to_datetime(df["Date"], errors="coerce")
    bad = df[df["Date"].notna() & dates.isna()]
    if len(bad):
        issues += row_issues(FEHLER, sheet, "Ungültiges Datum", bad, lambda r: f"Date = '{r['Date']}'")
    df["Date"] = dates

    md = pd.to_datetime(df["matchDate"].astype("string"), format=schema.MATCHDATE_FORMAT, errors="coerce")
    bad = df[df["matchDate"].notna() & md.isna()]
    if len(bad):
        issues += row_issues(WARNUNG, sheet, "matchDate-Format", bad,
                             lambda r: f"matchDate = '{r['matchDate']}' (erwartet TT-MM-JJ HH:MM)")
    mismatch = df[md.notna() & dates.notna() & (md.dt.normalize() != dates.dt.normalize())]
    if len(mismatch):
        issues += row_issues(WARNUNG, sheet, "Datum ≠ matchDate", mismatch,
                             lambda r: f"Date {pd.Timestamp(r['Date']):%d.%m.%Y} vs. matchDate {r['matchDate']}")
    df["kickoff"] = md

    # Saison-Format
    season = df["Season"].astype("string").str.strip()
    bad = df[season.notna() & ~season.str.match(schema.SEASON_PATTERN)]
    if len(bad):
        issues += row_issues(FEHLER, sheet, "Saison-Format", bad,
                             lambda r: f"Season = '{r['Season']}' (erwartet JJJJ/JJJJ)")
    df["Season"] = season

    for col in ("Country", "League", "homeTeam", "awayTeam", "referee"):
        df[col] = df[col].astype("string").str.strip()

    # Doppelte IDs
    dup = df[df["id"].notna() & df["id"].duplicated(keep=False)]
    if len(dup):
        issues += row_issues(FEHLER, sheet, "Doppelte id", dup, lambda r: f"id {int(r['id'])} kommt mehrfach vor")

    # Liga-Spalte passt zum Blattnamen?
    wrong_league = df[df["League"].notna() & (df["League"] != sheet)]
    if len(wrong_league):
        issues += row_issues(WARNUNG, sheet, "Liga ≠ Blattname", wrong_league,
                             lambda r: f"League = '{r['League']}'")

    if not any(i.level == FEHLER for i in issues):
        df["id"] = df["id"].astype("int64")
        for col in schema.GOAL_COLUMNS:
            df[col] = df[col].astype("int64")
    return df, issues


def _read_notes(raw: pd.DataFrame, leagues: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, list[Issue]]:
    sheet = settings.NOTES_SHEET
    issues: list[Issue] = []
    missing = [c for c in schema.NOTES_COLUMNS if c not in raw.columns]
    if missing:
        issues.append(Issue(WARNUNG, sheet, "Spaltenstruktur", "fehlende Spalten: " + ", ".join(missing)))
        return raw, issues
    notes = raw.dropna(how="all").copy()
    for _, r in notes.iterrows():
        liga, mid = r["Liga"], pd.to_numeric(r["id"], errors="coerce")
        df = leagues.get(liga)
        if df is None or pd.isna(mid) or not (df["id"] == mid).any():
            issues.append(Issue(WARNUNG, sheet, "Hinweis ohne Spiel",
                                f"Kein Spiel mit id {r['id']} im Blatt '{liga}' gefunden"))
    return notes, issues


def _noted_ids(notes: pd.DataFrame | None) -> set[tuple[str, int]]:
    """(Liga, id) aller Spiele, die im Blatt Datenhinweise dokumentiert sind.
    Fehlt dort die Spalte Liga oder id, gibt es keine dokumentierten Spiele (die Warnung kommt aus _read_notes)."""
    if notes is None or not {"Liga", "id"} <= set(notes.columns):
        return set()
    ids = set()
    for _, r in notes.iterrows():
        mid = pd.to_numeric(r["id"], errors="coerce")
        if pd.notna(mid):
            ids.add((str(r["Liga"]), int(mid)))
    return ids


# --- Hauptfunktion -------------------------------------------------------

def load_database(path: Path | str | None = None) -> DatabaseLoad:
    path = Path(path) if path else settings.DATABASE_FILE
    result = DatabaseLoad(path=path, loaded_at=datetime.now(timezone.utc))

    if not path.exists():
        result.issues.append(Issue(FEHLER, "-", "Datei fehlt", f"Datei nicht gefunden: {path}"))
        return result

    stat = path.stat()
    result.file_size = stat.st_size
    result.file_modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

    try:
        result.sha256 = sha256_of(path)
        sheets = pd.read_excel(path, sheet_name=None, engine="openpyxl")
    # SyntaxError: kaputtes XML in der Datei (xml ParseError und lxml XMLSyntaxError sind beide SyntaxError)
    except (zipfile.BadZipFile, SyntaxError, ValueError, OSError, KeyError) as exc:
        result.issues.append(Issue(
            FEHLER, "-", "Datei nicht lesbar",
            f"Die Excel-Datei konnte nicht gelesen werden ({type(exc).__name__}: {exc}). "
            "Möglicherweise ist sie beschädigt oder der Upload noch nicht abgeschlossen.",
        ))
        return result

    # Blätter
    for name in settings.REQUIRED_LEAGUE_SHEETS:
        if name not in sheets:
            result.issues.append(Issue(FEHLER, name, "Blatt fehlt", f"Pflichtblatt '{name}' nicht gefunden"))
    for name in settings.OPTIONAL_LEAGUE_SHEETS:
        if name not in sheets:
            result.issues.append(Issue(HINWEIS, name, "Blatt fehlt", f"Optionales Blatt '{name}' nicht vorhanden"))
    known = set(settings.LEAGUE_SHEETS) | {settings.NOTES_SHEET}
    for name in sheets:
        if name not in known:
            result.issues.append(Issue(HINWEIS, name, "Unbekanntes Blatt", f"Blatt '{name}' wird ignoriert"))

    # Ligablätter
    for name in settings.LEAGUE_SHEETS:
        raw = sheets.get(name)
        if raw is None:
            continue
        if raw.dropna(how="all").empty:
            level = FEHLER if name in settings.REQUIRED_LEAGUE_SHEETS else HINWEIS
            result.issues.append(Issue(level, name, "Blatt leer", f"Blatt '{name}' enthält keine Spiele"))
            continue
        col_issues = _check_columns(name, raw)
        result.issues += col_issues
        if col_issues:
            continue
        df, issues = _prepare_league(name, raw.dropna(how="all"))
        result.issues += issues
        if any(i.level == FEHLER for i in issues):
            continue
        result.leagues[name] = df

    # Datenhinweise
    if settings.NOTES_SHEET in sheets:
        result.notes, issues = _read_notes(sheets[settings.NOTES_SHEET], result.leagues)
        result.issues += issues
    noted_ids = _noted_ids(result.notes)

    # Plausibilität (nur für fehlerfreie Blätter)
    for name, df in result.leagues.items():
        result.issues += run_plausibility_checks(name, df, noted_ids)

    return result
