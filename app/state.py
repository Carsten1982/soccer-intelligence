"""Laden von Datenbank, Spielplan und Konfiguration mit Cache.

Der Cache-Schlüssel enthält Änderungszeit und Grösse der Dateien. Wird eine Excel-Datei
auf dem Server ersetzt, liest die App sie beim nächsten Seitenaufruf automatisch neu ein –
ohne Neustart des Containers.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

from core import settings
from core.config import League, Team, active_leagues, load_leagues, load_teams  # noqa: F401
from core.fixtures import FixturesLoad, load_fixtures
from core.issues import FEHLER, HINWEIS, WARNUNG
from core.loader import DatabaseLoad, load_database

TZ = ZoneInfo(settings.TIMEZONE)


def _file_key(path: Path) -> tuple[int, int]:
    try:
        stat = path.stat()
        return stat.st_mtime_ns, stat.st_size
    except OSError:
        return 0, 0


def today() -> date:
    """Heutiges Datum in der Zeitzone Europe/Zurich (massgeblich für den aktuellen Spieltag)."""
    return datetime.now(TZ).date()


# --- Datenbank ---------------------------------------------------------------

@st.cache_data(show_spinner="Datenbank wird eingelesen …", max_entries=2)
def _cached_load(path: str, mtime_ns: int, size: int) -> DatabaseLoad:  # noqa: ARG001 - Teil des Cache-Schlüssels
    return load_database(path)


def get_database() -> DatabaseLoad:
    path = settings.DATABASE_FILE
    return _cached_load(str(path), *_file_key(path))


@st.cache_data(show_spinner=False, max_entries=2)
def _cached_prepared(path: str, mtime_ns: int, size: int) -> dict:  # noqa: ARG001
    from core.kpis import prepare_league
    db = _cached_load(path, mtime_ns, size)
    return {name: prepare_league(df) for name, df in db.leagues.items()}


def get_prepared() -> dict:
    """Aufbereitete Ligen für die KPI-Berechnung (einmal je Datenbankstand)."""
    path = settings.DATABASE_FILE
    return _cached_prepared(str(path), *_file_key(path))


@st.cache_data(show_spinner="Häufigkeit der Anomalien wird berechnet (einmal je Datenbankstand) …", max_entries=4)
def _cached_frequency(path: str, mtime_ns: int, size: int, league_name: str, teams: int):  # noqa: ARG001
    from core.config import League
    from core.frequency import anomaly_frequency
    prepared = _cached_prepared(path, mtime_ns, size).get(league_name)
    if prepared is None:
        return None, None
    return anomaly_frequency(prepared, League(league_name, "x", teams, True))


def get_frequency(league: League):
    path = settings.DATABASE_FILE
    return _cached_frequency(str(path), *_file_key(path), league.name, league.teams)


# --- Konfiguration -------------------------------------------------------------

def get_leagues() -> list[League]:
    """Alle Ligen aus config/ligen.toml (wirft ConfigError bei ungültiger Datei)."""
    return load_leagues(settings.LEAGUES_FILE)


def get_active_leagues() -> list[League]:
    return active_leagues(get_leagues())


def get_teams() -> list[Team]:
    return load_teams(settings.TEAMS_FILE)


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
