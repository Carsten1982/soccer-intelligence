"""Laden von Datenbank, Spielplan und Konfiguration mit Cache, dazu die zwischengespeicherten KPI-Ergebnisse.

Der Cache-Schlüssel enthält je Datei Änderungszeit, Grösse, ctime und Dateinummer (core.files.file_key).
Wird eine Excel- oder Konfigurationsdatei auf dem Server ersetzt, liest die App sie beim nächsten Seitenaufruf
automatisch neu ein – ohne Neustart des Containers, auch bei gleicher Grösse und gleicher Änderungszeit (seit H.2).
"""

from __future__ import annotations

import json
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from core import settings
from core.config import League, Team, active_leagues, load_leagues, load_teams
from core.files import file_key as _file_key
from core.fixtures import FixturesLoad, load_fixtures
from core.frequency import anomaly_frequency
from core.issues import FEHLER, HINWEIS, WARNUNG
from core.kpis import MatchKpis, prepare_league
from core.loader import DatabaseLoad, load_database
from core.anzeige import results_index
from core.matchday import matchday_games
from core.results import matchday_kpis
from core.simulation import build_cases, closed_matchdays
from core.thresholds import ThresholdConfig, load_thresholds

TZ = ZoneInfo(settings.TIMEZONE)


def today() -> date:
    """Heutiges Datum in der Zeitzone Europe/Zurich (massgeblich für den aktuellen Spieltag)."""
    return datetime.now(TZ).date()


def now() -> datetime:
    """Jetzt in Europe/Zurich, ohne Zeitzonenangabe (wie die Anstosszeiten im Spielplan; seit 0.16)."""
    return datetime.now(TZ).replace(tzinfo=None)


# --- Datenbank ---------------------------------------------------------------

@st.cache_data(show_spinner="Datenbank wird eingelesen …", max_entries=2)
def _cached_load(path: str, key: tuple) -> DatabaseLoad:  # noqa: ARG001 - key ist Teil des Cache-Schlüssels
    return load_database(path)


def get_database() -> DatabaseLoad:
    path = settings.DATABASE_FILE
    return _cached_load(str(path), _file_key(path))


@st.cache_data(show_spinner=False, max_entries=2)
def _cached_prepared(path: str, key: tuple) -> dict:
    db = _cached_load(path, key)
    return {name: prepare_league(df) for name, df in db.leagues.items()}


def get_prepared() -> dict:
    """Aufbereitete Ligen für die KPI-Berechnung (einmal je Datenbankstand)."""
    path = settings.DATABASE_FILE
    return _cached_prepared(str(path), _file_key(path))


@st.cache_data(show_spinner="Häufigkeit der Anomalien wird berechnet (einmal je Datenbankstand) …", max_entries=8)
def _cached_frequency(path: str, key: tuple, league_name: str,
                      thresholds_key: tuple, leagues_key: tuple):  # noqa: ARG001 - Teil des Cache-Schlüssels
    prepared = _cached_prepared(path, key).get(league_name)
    if prepared is None:
        return None, None
    return anomaly_frequency(prepared, _league(league_name), get_thresholds().get)


def get_frequency(league: League):
    path = settings.DATABASE_FILE
    return _cached_frequency(str(path), _file_key(path), league.name,
                             _file_key(settings.THRESHOLDS_FILE), _file_key(settings.LEAGUES_FILE))


# --- Sensitivitätsanalyse (Etappe I.1, seit Version 0.12) ------------------------------------------------

@st.cache_data(show_spinner="Sensitivitätsanalyse wird vorbereitet: alle Spiele werden berechnet (einmal je "
                            "Datenbankstand, rund 10 Sekunden) …", max_entries=2)
def _cached_simulation(path: str, key: tuple, leagues_key: tuple) -> pd.DataFrame:  # noqa: ARG001
    prepared = _cached_prepared(path, key)
    frames = [build_cases(prepared[lg.name], lg) for lg in get_active_leagues() if lg.name in prepared]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def get_simulation_cases() -> pd.DataFrame:
    """Alle Fälle der Simulation (je Spiel und KPI), unabhängig von den Schwellen. Siehe core/simulation.py."""
    path = settings.DATABASE_FILE
    return _cached_simulation(str(path), _file_key(path), _file_key(settings.LEAGUES_FILE))


@st.cache_data(show_spinner=False, max_entries=2)
def _cached_matchdays(path: str, key: tuple, leagues_key: tuple) -> pd.DataFrame:  # noqa: ARG001
    prepared = _cached_prepared(path, key)
    frames = [closed_matchdays(prepared[lg.name], lg) for lg in get_active_leagues() if lg.name in prepared]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["league", "season", "gameday"])


def get_closed_matchdays() -> pd.DataFrame:
    """Abgeschlossene Spieltage der ausgewerteten Saisons (Nenner der Sensitivitätsanalyse)."""
    path = settings.DATABASE_FILE
    return _cached_matchdays(str(path), _file_key(path), _file_key(settings.LEAGUES_FILE))


# --- KPI-Ergebnisse eines Spieltags (seit H.1) ------------------------------------------

@st.cache_data(show_spinner="KPIs werden berechnet …", max_entries=64)
def _cached_matchday_kpis(league_name: str, season: str, matchday: int,
                          files_key: tuple) -> list[MatchKpis | None]:  # noqa: ARG001 - Teil des Cache-Schlüssels
    fixtures = get_fixtures().leagues.get(league_name)
    if fixtures is None:
        return []
    games = matchday_games(fixtures, season, matchday)
    return matchday_kpis(get_prepared().get(league_name), _league(league_name), season, matchday, games,
                         get_thresholds().get)


def get_matchday_kpis(league: League, season: str, matchday: int) -> list[MatchKpis | None]:
    """KPI-Ergebnisse je Begegnung des Spieltags, in der Reihenfolge von matchday_games (None = verschoben/abgesagt).

    Einmal berechnet und dann aus dem Zwischenspeicher, bis sich eine der Dateien ändert, von denen die Werte
    abhängen: Datenbank, Spielplan (Stichtag, Teams, Status), Schwellen, Ligen und Teamliste. „Heute“ gehört nicht
    in den Schlüssel: Die Werte eines Spieltags hängen nicht vom heutigen Datum ab."""
    files_key = tuple(_file_key(f) for f in (settings.DATABASE_FILE, settings.FIXTURES_FILE, settings.THRESHOLDS_FILE,
                                             settings.LEAGUES_FILE, settings.TEAMS_FILE))
    return _cached_matchday_kpis(league.name, season, matchday, files_key)


def get_round_kpis(league: League, season: str, matchday: int) -> dict[int, MatchKpis | None]:
    """Wie get_matchday_kpis, aber je Spiel über die Reihenfolge im Spielplan-Blatt ansprechbar (seit 0.16:
    Abschnitte und Top-Anomalien-Blöcke mischen Spiele verschiedener Spieltage)."""
    games = matchday_games(get_fixtures().leagues[league.name], season, matchday)
    return dict(zip(games["reihenfolge"].astype(int), get_matchday_kpis(league, season, matchday)))


# --- Ergebnisse und Datenstand für die Anzeige kommender Spieltage (seit 0.16) ----------------------

@st.cache_data(show_spinner=False, max_entries=2)
def _cached_results(path: str, key: tuple) -> dict:  # noqa: ARG001 - key ist Teil des Cache-Schlüssels
    return {name: results_index(df) for name, df in _cached_prepared(path, key).items()}


def get_results(league: League) -> dict:
    """Ergebnisse der Datenbank je (Saison, Heim, Gast) einer Liga (Spalte „Datum“, „Werte ab“)."""
    path = settings.DATABASE_FILE
    return _cached_results(str(path), _file_key(path)).get(league.name, {})


FAILED_RUNS = ("fehlgeschlagen", "Fehler – nicht übernehmbar")


def last_import_day() -> date | None:
    """Tag des letzten erfolgreichen Importlaufs (Spielplan v2.1, S9), None ohne Lauf. Liest nur /import."""
    from importer.einstellungen import IMPORT_DIR
    for report in sorted((IMPORT_DIR / "laeufe").glob("*/bericht.json"), reverse=True):
        try:
            rep = json.loads(report.read_text(encoding="utf-8"))
            if rep.get("status") not in FAILED_RUNS and rep.get("start"):
                return datetime.fromisoformat(rep["start"]).date()
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    return None


# --- Schwellenwerte (app/config/schwellen.toml) ------------------------------------------

@st.cache_data(show_spinner=False, max_entries=2)
def _cached_thresholds(path: str, key: tuple, leagues_key: tuple) -> ThresholdConfig:  # noqa: ARG001
    return load_thresholds(path, [lg.name for lg in get_leagues()])


def get_thresholds() -> ThresholdConfig:
    """Schwellen je Liga und KPI (wirft ConfigError bei ungültiger Datei)."""
    path = settings.THRESHOLDS_FILE
    return _cached_thresholds(str(path), _file_key(path), _file_key(settings.LEAGUES_FILE))


# --- Konfiguration -------------------------------------------------------------

def get_leagues() -> list[League]:
    """Alle Ligen aus config/ligen.toml (wirft ConfigError bei ungültiger Datei)."""
    return load_leagues(settings.LEAGUES_FILE)


def get_active_leagues() -> list[League]:
    return active_leagues(get_leagues())


def get_teams() -> list[Team]:
    """Teamliste aus config/teams.toml (wirft ConfigError bei ungültiger Datei)."""
    return load_teams(settings.TEAMS_FILE)


def _league(name: str) -> League:
    """Liga aus der Konfiguration (für die Zwischenspeicher, die nur den Namen im Schlüssel haben)."""
    return {lg.name: lg for lg in get_leagues()}[name]


# --- Spielplan -----------------------------------------------------------------

@st.cache_data(show_spinner="Spielplan wird eingelesen …", max_entries=2)
def _cached_fixtures(path: str, key: tuple, db_key: tuple, cfg_key: tuple) -> FixturesLoad:  # noqa: ARG001
    db = get_database()
    return load_fixtures(path, get_leagues(), db.leagues, get_teams())


def get_fixtures() -> FixturesLoad:
    path = settings.FIXTURES_FILE
    cfg_key = (_file_key(settings.LEAGUES_FILE), _file_key(settings.TEAMS_FILE))
    return _cached_fixtures(str(path), _file_key(path), _file_key(settings.DATABASE_FILE), cfg_key)


# --- Anzeige-Hilfen --------------------------------------------------------------

def fmt_dt(dt) -> str:
    return dt.astimezone(TZ).strftime("%d.%m.%Y, %H:%M Uhr") if dt else "-"


def status_banner(db: DatabaseLoad) -> None:
    e, w, h = db.count(FEHLER), db.count(WARNUNG), db.count(HINWEIS)
    if e:
        st.error(f"**Datenbank nicht verwendbar:** {e} Fehler gefunden. Details unter *Datenqualität*.", icon="⛔")
    elif w:
        st.warning(f"Datenbank geladen mit {w} Warnung(en) und {h} Hinweis(en). Details unter *Datenqualität*.", icon="⚠️")
    else:
        st.success(f"Datenbank geprüft: keine Fehler, keine Warnungen ({h} Hinweis(e)).", icon="✅")


def fixtures_banner(fx: FixturesLoad) -> None:
    e, w, h = fx.count(FEHLER), fx.count(WARNUNG), fx.count(HINWEIS)
    if e:
        st.error(f"**Spielplan nicht verwendbar:** {e} Fehler gefunden.", icon="⛔")
    elif w:
        st.warning(f"Spielplan geladen mit {w} Warnung(en) und {h} Hinweis(en).", icon="⚠️")
    else:
        st.success(f"Spielplan geprüft: keine Fehler, keine Warnungen ({h} Hinweis(e)).", icon="✅")
