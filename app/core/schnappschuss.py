"""Schnappschuss je Spiel: die Werte vor dem Anpfiff einfrieren (seit 0.20).

Regeln: Entscheidungsprotokoll 19.11.2026, Nr. 2; Template-Briefing 3.4; `07_Spielplan_Anzeige.md`, Abschnitt 4.9.

- Stündlich (Container soccer-import) entsteht für jedes angesetzte Spiel mit Anpfiff in der nächsten Stunde ein
  Schnappschuss der Werte, die Dashboard und Website zeigen: alle KPI-Ergebnisse mit Teamwerten, Ligareferenz,
  Formkurve und Einstufung (Schwellen und Signalqualität zum Zeitpunkt des Schnappschusses).
- Er wird **genau einmal geschrieben und nie verändert** (eine Datei je Spiel, Anlegen schlägt fehl, wenn es sie
  schon gibt). Er trägt eine Formatnummer, die App-Version und die Prüfsummen von Datenbank und Schwellen.
- Er wartet, bis die Ergebnisse der vorherigen Spiele beider Teams in der Datenbank stehen („Werte ab“, 4.5).
- Fehlt er beim Anpfiff (Dienst ausgefallen, Vorspiel-Ergebnis noch nicht übernommen), wird er nachgeholt, sobald es
  geht, und als **nachträglich** markiert. So entstehen auch die Schnappschüsse der laufenden Saison und der Vorsaison
  (einmalig beim ersten Lauf). Gerechnet wird in beiden Fällen mit den Daten vor dem Spiel (Stichtag „Datum von“).
- Das erste Ergebnis, das die Datenbank für ein Spiel liefert, wird ebenfalls einmal festgehalten. Weicht das
  Ergebnis der Datenbank später davon ab (Korrektur der Quelle, bis 7 Tage), zeigt die Seite den neuen Endstand mit
  dem Hinweis „Ergebnis nachträglich korrigiert“; die Werte bleiben die des Schnappschusses.

Ablage: /import/schnappschuesse/<liga>/<saison>/<API-ID>.json und <API-ID>.ergebnis.json (<liga> = Adresse aus
ligen.toml, <saison> = „2026-2027“). Dashboard und Website lesen nur.
"""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pandas as pd

from .fixtures import STATUS_PLANNED
from .kpis import FormTeam, KpiResult, Match, MatchKpis, Reference, Signal, TeamValue, Thresholds

FORMAT = 1                          # Aufbau der Datei; bei einer Änderung erhöhen und das Lesen erweitern
DIRNAME = "schnappschuesse"
STATUS_FILE = "stand.json"          # Ergebnis des letzten Laufs (Überwachung im Reiter Datenimport/API)
LEAD = timedelta(hours=1)           # Schnappschuss ab einer Stunde vor dem Anpfiff

_CLASSES = {c.__name__: c for c in (MatchKpis, Match, FormTeam, TeamValue, Reference, KpiResult, Thresholds, Signal)}


# --- Genaue Speicherung (Brüche und Dezimalzahlen als Text, nichts gerundet) -------------------------------

def encode(value):
    """Datenklassen und Zahlen verlustfrei in JSON-Werte. Brüche als „Zähler/Nenner“, Dezimalzahlen als Text."""
    if is_dataclass(value) and not isinstance(value, type):
        name = type(value).__name__
        if name not in _CLASSES:
            raise TypeError(f"Schnappschuss: unbekannte Klasse {name}")
        return {"$k": name, **{f.name: encode(getattr(value, f.name)) for f in fields(value)}}
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    if isinstance(value, Fraction):
        return {"$b": f"{value.numerator}/{value.denominator}"}
    if isinstance(value, Decimal):
        return {"$d": str(value)}
    if isinstance(value, datetime):
        raise TypeError("Schnappschuss: Zeitpunkte werden nicht gespeichert")
    if isinstance(value, date):
        return {"$t": value.isoformat()}
    if isinstance(value, tuple):
        return {"$tupel": [encode(v) for v in value]}
    if isinstance(value, list):
        return [encode(v) for v in value]
    raise TypeError(f"Schnappschuss: Wert vom Typ {type(value).__name__} nicht speicherbar")


def decode(value):
    """Umkehrung von encode: decode(encode(x)) == x."""
    if isinstance(value, list):
        return [decode(v) for v in value]
    if not isinstance(value, dict):
        return value
    if "$k" in value:
        cls = _CLASSES[value["$k"]]
        return cls(**{k: decode(v) for k, v in value.items() if k != "$k"})
    if "$b" in value:
        return Fraction(value["$b"])
    if "$d" in value:
        return Decimal(value["$d"])
    if "$t" in value:
        return date.fromisoformat(value["$t"])
    if "$tupel" in value:
        return tuple(decode(v) for v in value["$tupel"])
    raise ValueError(f"Schnappschuss: unbekannter Eintrag {sorted(value)}")


# --- Ablage --------------------------------------------------------------------------------------------

def season_dir(saison: str) -> str:
    return saison.replace("/", "-")


def folder(base: Path, league_url: str, saison: str) -> Path:
    return Path(base) / DIRNAME / league_url / season_dir(saison)


def snapshot_path(base: Path, league_url: str, saison: str, api_id: int) -> Path:
    return folder(base, league_url, saison) / f"{int(api_id)}.json"


def result_path(base: Path, league_url: str, saison: str, api_id: int) -> Path:
    return folder(base, league_url, saison) / f"{int(api_id)}.ergebnis.json"


def write_once(path: Path, data: dict) -> bool:
    """Datei anlegen, nie überschreiben. False, wenn es sie schon gibt. Erst vollständig in eine Hilfsdatei, dann in
    einem Schritt unter dem Zielnamen verlinkt: Leser sehen nie eine halbe Datei."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return False
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    try:
        os.link(tmp, path)               # schlägt fehl, wenn die Zieldatei existiert
        return True
    except FileExistsError:
        return False
    finally:
        tmp.unlink(missing_ok=True)


@dataclass(frozen=True)
class Snapshot:
    kpis: MatchKpis
    erstellt: datetime
    nachtraeglich: bool
    meta: dict


_cache: dict[str, Snapshot] = {}         # Schnappschüsse ändern sich nie: einmal gelesen, bleibt der Eintrag
_lock = threading.Lock()
_MAX = 20000


def read(base: Path, league_url: str, saison: str, api_id) -> Snapshot | None:
    """Schnappschuss eines Spiels oder None (keiner vorhanden, Datei unlesbar oder Format unbekannt)."""
    if api_id is None or api_id != api_id:                       # NaN: Spiel ohne API-ID
        return None
    path = snapshot_path(base, league_url, saison, api_id)
    key = str(path)
    with _lock:
        hit = _cache.get(key)
    if hit is not None:
        return hit
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("format") != FORMAT:
            return None
        snap = Snapshot(decode(data["werte"]), datetime.fromisoformat(data["erstellt"]),
                        bool(data["nachtraeglich"]), {k: v for k, v in data.items() if k != "werte"})
    except (OSError, ValueError, KeyError, TypeError):
        return None
    with _lock:
        if len(_cache) >= _MAX:
            _cache.clear()
        _cache[key] = snap
    return snap


def first_result(base: Path, league_url: str, saison: str, api_id) -> tuple[int, int] | None:
    """Das zuerst festgehaltene Ergebnis eines Spiels (für „Ergebnis nachträglich korrigiert“)."""
    if api_id is None or api_id != api_id:
        return None
    try:
        data = json.loads(result_path(base, league_url, saison, api_id).read_text(encoding="utf-8"))
        return int(data["ergebnis"][0]), int(data["ergebnis"][1])
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        return None


def stats_path(base: Path, league_url: str, saison: str, api_id: int) -> Path:
    """Seit 0.25: die zuerst bekannten tatsächlichen Werte je Kennzahl (für „Statistik nachträglich korrigiert“)."""
    return folder(base, league_url, saison) / f"{int(api_id)}.ist.json"


def first_stats(base: Path, league_url: str, saison: str, api_id) -> dict:
    """Zuerst bekannte tatsächliche Werte {kpi: Wert}; leer, wenn es noch keine gibt."""
    if api_id is None or api_id != api_id:
        return {}
    try:
        data = json.loads(stats_path(base, league_url, saison, api_id).read_text(encoding="utf-8"))
        return {str(k): v for k, v in (data.get("werte") or {}).items() if v is not None}
    except (OSError, ValueError, AttributeError, TypeError):
        return {}


def record_stats(base: Path, league_url: str, saison: str, api_id, werte: dict, now: datetime) -> bool:
    """Neu bekannte Werte festhalten (seit 0.25, Beschluss 42). Ein schon festgehaltener Wert wird nie überschrieben;
    ein bisher fehlender kommt dazu, sobald er da ist. Schreibt nur bei einer Änderung, in einem Schritt (os.replace).
    True, wenn etwas dazukam."""
    bisher = first_stats(base, league_url, saison, api_id)
    neu = {k: int(v) for k, v in werte.items() if v is not None and k not in bisher}
    if not neu:
        return False
    path = stats_path(base, league_url, saison, api_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps({"werte": {**bisher, **neu}, "geaendert": now.isoformat(timespec="seconds")},
                              ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    os.replace(tmp, path)
    return True


def stats_corrected(base: Path, league_url: str, saison: str, api_id, werte: dict) -> bool:
    """Weicht ein aktueller tatsächlicher Wert vom zuerst festgehaltenen ab? Fehlt er jetzt, zählt das nicht."""
    erst = first_stats(base, league_url, saison, api_id)
    return any(k in erst and v is not None and int(v) != int(erst[k]) for k, v in werte.items())


def corrected(base: Path, league_url: str, saison: str, api_id, score: tuple[int, int] | None) -> bool:
    """Weicht das Ergebnis der Datenbank vom zuerst festgehaltenen ab?"""
    first = first_result(base, league_url, saison, api_id)
    return score is not None and first is not None and tuple(score) != first


# --- Welche Spiele einen Schnappschuss bekommen --------------------------------------------------------

def api_id_of(row) -> int | None:
    v = getattr(row, "api_id", None)
    return None if v is None or v != v else int(v)


def candidates(fx: pd.DataFrame, now: datetime) -> pd.DataFrame:
    """Angesetzte Spiele mit API-ID der laufenden Saison und der Vorsaison, deren Anpfiff höchstens eine Stunde
    entfernt ist oder schon vorbei (fx = anzeige.prepare). Ob es den Schnappschuss schon gibt, prüft der Lauf."""
    if fx.empty:
        return fx
    seasons = sorted(fx["saison"].unique())[-2:]
    ids = fx["api_id"].map(lambda v: v is not None and v == v)
    return fx[fx["status"].eq(STATUS_PLANNED) & ids & fx["saison"].isin(seasons)
              & (fx["anstoss_zeit"] - LEAD <= now)]


def payload(kpis: MatchKpis, row, now: datetime, league: str, meta: dict) -> dict:
    """Inhalt der Datei. nachträglich = erst nach dem Anstoss erstellt (ohne Uhrzeit: nach dem Tagesende)."""
    return {
        "format": FORMAT, "erstellt": now.isoformat(timespec="seconds"),
        "nachtraeglich": now >= row.anstoss_zeit,
        "liga": league, "saison": row.saison, "spieltag": int(row.spieltag), "api_id": api_id_of(row),
        "heim": row.heim, "gast": row.gast, "datum": row.datum_von.isoformat(),
        "anstoss": row.anstoss_zeit.isoformat(timespec="minutes"),
        **meta,
        "werte": encode(kpis),
    }


# --- Welche Werte Dashboard und Website zeigen -----------------------------------------------------------

LIVE, SNAPSHOT, LATE, WAITING, NONE = "live", "schnappschuss", "nachtraeglich", "wartet", "keine"


@dataclass(frozen=True)
class Shown:
    """Die Werte eines Spiels auf den Seiten und woher sie stammen."""
    kpis: MatchKpis | None
    quelle: str                   # live / schnappschuss / nachtraeglich / wartet / keine
    korrigiert: bool = False      # Ergebnis nach dem ersten Import geändert

    @property
    def nachtraeglich(self) -> bool:
        return self.quelle == LATE


def shown_values(base: Path, league_url: str, row, live: MatchKpis | None, now: datetime, results: dict,
                 fx: pd.DataFrame) -> Shown:
    """Vor dem Anstoss die aktuell berechneten Werte (live; ob sie schon erscheinen, entscheidet „Werte ab“).
    Ab dem Anstoss der Schnappschuss; fehlt er, die Werte mit den Daten vor dem Spiel, als nachträglich markiert –
    ausser ein Vorspiel-Ergebnis fehlt noch: dann keine Werte (wartet), bis der Schnappschuss nachgeholt ist.
    row: Zeile aus anzeige.prepare, fx: derselbe aufbereitete Spielplan, results: Ergebnisse der Datenbank."""
    from .anzeige import missing_previous             # hier, damit core.anzeige nicht von hier abhängt
    from .fixtures import INACTIVE_STATUS
    if row.status in INACTIVE_STATUS:
        return Shown(None, NONE)
    if now < row.anstoss_zeit:
        return Shown(live, LIVE)
    api_id = api_id_of(row)
    korr = corrected(base, league_url, row.saison, api_id, results.get((row.saison, row.heim, row.gast)))
    snap = read(base, league_url, row.saison, api_id)
    if snap is not None:
        return Shown(snap.kpis, LATE if snap.nachtraeglich else SNAPSHOT, korr)
    if live is None or missing_previous(fx, row, results):
        return Shown(None, WAITING, korr)
    return Shown(live, LATE, korr)
