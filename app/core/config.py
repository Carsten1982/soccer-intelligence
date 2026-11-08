"""Einlesen der Konfiguration: aktive Ligen (ligen.toml) und Teamliste (teams.toml).

Die Dateien liegen in app/config/ und werden mit dem Code versioniert.
Fehler in der Konfiguration führen zu einer klaren Meldung statt zu stillem Fehlverhalten.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from . import settings

URL_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESERVED_URLS = {"datenqualitaet", "dashboard"}


class ConfigError(Exception):
    """Konfigurationsdatei fehlt oder ist ungültig."""


@dataclass(frozen=True)
class League:
    name: str      # Blattname in Datenbank und Spielplan
    url: str       # Adresse des Bereichs
    teams: int     # Anzahl Teams
    aktiv: bool

    @property
    def games_per_matchday(self) -> int:
        return self.teams // 2

    @property
    def matchdays(self) -> int:
        """Spieltage je Saison (Hin- und Rückrunde): 2 × (Teams − 1), z. B. 34 in der Bundesliga."""
        return 2 * (self.teams - 1)


@dataclass(frozen=True)
class Team:
    team_id: str
    team_name: str
    display_name: str = ""


def _read_toml(path: Path) -> dict:
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except FileNotFoundError as exc:
        raise ConfigError(f"Konfigurationsdatei fehlt: {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Konfigurationsdatei {path.name} ist ungültig: {exc}") from exc


def load_leagues(path: Path | str | None = None) -> list[League]:
    """Alle Ligen aus ligen.toml (aktive und inaktive), in Dateireihenfolge."""
    path = Path(path) if path else settings.LEAGUES_FILE
    data = _read_toml(path)
    leagues: list[League] = []
    for i, entry in enumerate(data.get("liga", []), start=1):
        try:
            name = str(entry["name"]).strip()
            url = str(entry["url"]).strip()
            teams = entry["teams"]
            aktiv = entry.get("aktiv", True)
        except KeyError as exc:
            raise ConfigError(f"{path.name}, Liga {i}: Feld {exc} fehlt") from exc
        if not name:
            raise ConfigError(f"{path.name}, Liga {i}: Name ist leer")
        if not URL_PATTERN.match(url) or url in RESERVED_URLS:
            raise ConfigError(f"{path.name}, Liga {name}: ungültige url '{url}' (nur a–z, 0–9 und Bindestrich)")
        if not isinstance(teams, int) or isinstance(teams, bool) or teams < 2 or teams % 2:
            raise ConfigError(f"{path.name}, Liga {name}: teams muss eine gerade Zahl ab 2 sein")
        if not isinstance(aktiv, bool):
            raise ConfigError(f"{path.name}, Liga {name}: aktiv muss true oder false sein")
        leagues.append(League(name=name, url=url, teams=teams, aktiv=aktiv))
    names = [lg.name for lg in leagues]
    urls = [lg.url for lg in leagues]
    if len(set(names)) != len(names) or len(set(urls)) != len(urls):
        raise ConfigError(f"{path.name}: Name oder url einer Liga kommt doppelt vor")
    if not any(lg.aktiv for lg in leagues):
        raise ConfigError(f"{path.name}: keine aktive Liga")
    return leagues


def active_leagues(leagues: list[League]) -> list[League]:
    return [lg for lg in leagues if lg.aktiv]


def load_teams(path: Path | str | None = None) -> list[Team]:
    """Teamliste aus teams.toml. Fehlt die Datei, ist die Liste leer."""
    path = Path(path) if path else settings.TEAMS_FILE
    if not path.exists():
        return []
    data = _read_toml(path)
    teams: list[Team] = []
    for i, entry in enumerate(data.get("team", []), start=1):
        name = str(entry.get("team_name", "")).strip()
        if not name:
            raise ConfigError(f"{path.name}, Team {i}: team_name fehlt")
        teams.append(Team(
            team_id=str(entry.get("team_id", "")).strip() or name.lower(),
            team_name=name,
            display_name=str(entry.get("display_name", "")).strip(),
        ))
    if len({t.team_name for t in teams}) != len(teams):
        raise ConfigError(f"{path.name}: ein team_name kommt doppelt vor")
    return teams
