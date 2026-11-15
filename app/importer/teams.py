"""Teamnamen von API-Football, je Team-ID fest hinterlegt (app/config/teamnamen.toml; E6, E14).

name: gültige Schreibweise (Name der API, einmal festgehalten) · alt: bisherige Schreibweise der Datenbank, nur für die
einmalige Umbenennung beim ersten Import. Unbekannte Teams (z. B. Aufsteiger) erhalten den Namen der API und werden
gemeldet; eine Namensänderung der API bei bekannter ID wird ebenfalls gemeldet, der festgehaltene Name gilt weiter.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from core.config import ConfigError


@dataclass
class TeamNames:
    by_id: dict[int, str]                                  # API-Team-ID -> Name
    renames: dict[str, dict[str, str]]                     # Liga -> {alter Name: neuer Name}
    unknown: dict[int, str] = field(default_factory=dict)  # beim Lauf gefunden: ID -> API-Name
    changed: dict[int, tuple[str, str]] = field(default_factory=dict)   # ID -> (festgehalten, neu bei der API)
    aliases: dict[int, set[str]] = field(default_factory=dict)          # ID -> bekannte Schreibweisen (alt)

    def name(self, team: dict) -> str:
        """team = {"id": …, "name": …} aus der API."""
        tid, api_name = int(team["id"]), team["name"]
        known = self.by_id.get(tid)
        if known is None:
            self.unknown[tid] = api_name
            return api_name
        if api_name != known and api_name not in self.aliases.get(tid, set()):   # z. B. „Atletico“ für „Atlético“
            self.changed[tid] = (known, api_name)
        return known


def load_team_names(path: Path) -> TeamNames:
    try:
        data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"{Path(path).name}: nicht lesbar ({exc})") from exc
    by_id, renames, aliases = {}, {}, {}
    for i, t in enumerate(data.get("team", []), start=1):
        try:
            tid, name, league = int(t["api_team_id"]), str(t["name"]), str(t["liga"])
        except (KeyError, ValueError) as exc:
            raise ConfigError(f"teamnamen.toml, Eintrag {i}: liga, api_team_id und name nötig") from exc
        if tid in by_id:
            raise ConfigError(f"teamnamen.toml: api_team_id {tid} doppelt")
        by_id[tid] = name
        alts = t.get("alt") or []
        for alt in ([alts] if isinstance(alts, str) else alts):    # eine Schreibweise oder eine Liste
            if str(alt) != name:
                renames.setdefault(league, {})[str(alt)] = name
                aliases.setdefault(tid, set()).add(str(alt))
    return TeamNames(by_id, renames, aliases=aliases)
