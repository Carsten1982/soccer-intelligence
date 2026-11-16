"""Daten für die Website: Datenbank, Spielplan, Schwellen und Stand des Imports (Konzept 08, Abschnitte 3 und 6).

Geladen wird mit denselben Funktionen wie im Dashboard (core.loader, core.fixtures, core.kpis, core.thresholds).
Ein Zwischenspeicher hält den Bestand, bis sich eine der Dateien ändert (core.files.file_key, wie state.py).

Zeitreise (nur Vorschau, Konzept 6): Für einen Zeitpunkt in der Vergangenheit gilt die Annahme, dass der Import an
diesem Tag um 04:00 gelaufen ist (vor 04:00: am Vortag). Ergebnisse und KPI-Werte stammen dann nur aus Spielen vor
dem Importtag; der Spielplan ist der heutige.
"""

from __future__ import annotations

import json
import re
import threading
import tomllib
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from core import settings
from core.anzeige import results_index
from core.config import League, load_leagues, load_teams
from core.files import file_key
from core.fixtures import FixturesLoad, load_fixtures
from core.kpis import MatchKpis, prepare_league
from core.loader import DatabaseLoad, load_database
from core.matchday import matchday_games
from core.results import matchday_kpis
from core.thresholds import ThresholdConfig, load_thresholds

from . import einstellungen as W

TZ = ZoneInfo(settings.TIMEZONE)
FEHLGESCHLAGEN = ("fehlgeschlagen", "Fehler – nicht übernehmbar")     # wie state.FAILED_RUNS
DATUM = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?$")


def jetzt_echt() -> datetime:
    """Jetzt in Europe/Zurich, ohne Zeitzonenangabe (wie die Anstosszeiten im Spielplan)."""
    return datetime.now(TZ).replace(tzinfo=None)


# --- Zeitpunkt und Zeitreise ----------------------------------------------------------------------------

@dataclass(frozen=True)
class Zeitpunkt:
    jetzt: datetime                 # massgebender Zeitpunkt der Anzeige
    stand: datetime | None          # letzter erfolgreicher Importlauf (D1)
    bis: date | None                # Zeitreise: nur Spiele vor diesem Tag; None = Datenbank wie sie ist
    zeitreise: bool = False

    @property
    def import_tag(self) -> date | None:
        return self.stand.date() if self.stand else None


def zeitreise(text: str | None, echt: Zeitpunkt) -> tuple[Zeitpunkt, bool]:
    """(Zeitpunkt, Eingabe ungültig?). Ohne Angabe gilt der echte Zeitpunkt."""
    if not text:
        return echt, False
    m = DATUM.match(str(text).strip())
    if not m:
        return echt, True
    y, mo, d, hh, mm = m.groups()
    try:
        tag = date(int(y), int(mo), int(d))
        uhr = time(int(hh), int(mm)) if hh is not None else time(*W.VORMITTAG)
    except ValueError:
        return echt, True
    jetzt = datetime.combine(tag, uhr)
    import_tag = tag if uhr >= time(W.IMPORT_STUNDE) else tag - timedelta(days=1)
    return Zeitpunkt(jetzt, datetime.combine(import_tag, time(W.IMPORT_STUNDE)), import_tag, True), False


def letzter_import(import_dir) -> datetime | None:
    """Beginn des letzten erfolgreichen Importlaufs (Europe/Zurich), None ohne Lauf. Liest nur /import."""
    for bericht in sorted((import_dir / "laeufe").glob("*/bericht.json"), reverse=True):
        try:
            rep = json.loads(bericht.read_text(encoding="utf-8"))
            if rep.get("status") in FEHLGESCHLAGEN or not rep.get("start"):
                continue
            start = datetime.fromisoformat(rep["start"])
            return (start.astimezone(TZ) if start.tzinfo else start).replace(tzinfo=None, microsecond=0)
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    return None


# --- Bestand -------------------------------------------------------------------------------------------

@dataclass
class Bestand:
    db: DatabaseLoad
    fx: FixturesLoad
    leagues: dict[str, League]
    prepared: dict[str, pd.DataFrame]
    thresholds: ThresholdConfig
    team_ids: dict[tuple[str, str], int] = field(default_factory=dict)

    @property
    def gesperrt(self) -> bool:
        """Fehler in Datenbank oder Spielplan: Die Seiten zeigen nur einen Hinweis (wie das Dashboard)."""
        return self.db.has_errors or self.fx.has_errors


def _team_ids() -> dict[tuple[str, str], int]:
    """(Liga, Name) -> feste Team-ID von API-Football (Namenstabelle, Übergabe 9.1 Punkt 5)."""
    from importer.einstellungen import TEAM_NAMES_FILE
    try:
        daten = tomllib.loads(TEAM_NAMES_FILE.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return {(t["liga"], t["name"]): int(t["api_team_id"]) for t in daten.get("team", [])
            if "liga" in t and "name" in t and "api_team_id" in t}


class Daten:
    """Hält den geladenen Bestand und die berechneten Werte. Thread-sicher (Vorschau-Webserver)."""

    MAX_EINTRAEGE = 400

    def __init__(self, import_dir=None):
        from importer.einstellungen import IMPORT_DIR
        self.import_dir = import_dir or IMPORT_DIR
        self._lock = threading.RLock()
        self._schluessel = None
        self._bestand: Bestand | None = None
        self._cache: dict = {}

    def _dateien(self) -> tuple:
        return tuple(file_key(f) for f in (settings.DATABASE_FILE, settings.FIXTURES_FILE, settings.THRESHOLDS_FILE,
                                            settings.LEAGUES_FILE, settings.TEAMS_FILE))

    def bestand(self) -> Bestand:
        schluessel = self._dateien()
        with self._lock:
            if self._bestand is None or schluessel != self._schluessel:
                leagues = load_leagues(settings.LEAGUES_FILE)
                db = load_database(settings.DATABASE_FILE)
                fx = load_fixtures(settings.FIXTURES_FILE, leagues, db.leagues, load_teams(settings.TEAMS_FILE))
                self._bestand = Bestand(
                    db, fx, {lg.name: lg for lg in leagues},
                    {name: prepare_league(df) for name, df in db.leagues.items()},
                    load_thresholds(settings.THRESHOLDS_FILE, [lg.name for lg in leagues]), _team_ids())
                self._schluessel = schluessel
                self._cache.clear()
            return self._bestand

    def zeitpunkt(self) -> Zeitpunkt:
        return Zeitpunkt(jetzt_echt(), letzter_import(self.import_dir), None)

    def _merken(self, key, rechnen):
        with self._lock:
            if key in self._cache:
                return self._cache[key]
        wert = rechnen()
        with self._lock:
            if len(self._cache) >= self.MAX_EINTRAEGE:
                self._cache.clear()
            self._cache[key] = wert
        return wert

    def prepared(self, liga: str, bis: date | None) -> pd.DataFrame | None:
        """Aufbereitete Spiele der Liga; Zeitreise: nur Spiele vor dem Importtag."""
        df = self.bestand().prepared.get(liga)
        if df is None or bis is None:
            return df
        return self._merken(("prepared", self._schluessel, liga, bis), lambda: df[df["date"] < bis])

    def ergebnisse(self, liga: str, bis: date | None) -> dict:
        self.bestand()                                     # Dateistand prüfen, bevor der Schlüssel gebildet wird
        return self._merken(("ergebnisse", self._schluessel, liga, bis),
                            lambda: results_index(self.prepared(liga, bis)))

    def kpis(self, liga: str, saison: str, spieltag: int, bis: date | None) -> dict[int, MatchKpis | None]:
        """KPI-Ergebnisse je Spiel eines Spieltags (Schlüssel: Reihenfolge im Spielplan-Blatt)."""
        def rechnen():
            b = self.bestand()
            league, fixtures = b.leagues.get(liga), b.fx.leagues.get(liga)
            if league is None or fixtures is None:
                return {}
            games = matchday_games(fixtures, saison, spieltag)
            res = matchday_kpis(self.prepared(liga, bis), league, saison, spieltag, games, b.thresholds.get)
            return dict(zip(games["reihenfolge"].astype(int), res))
        self.bestand()
        return self._merken(("kpis", self._schluessel, liga, saison, int(spieltag), bis), rechnen)
