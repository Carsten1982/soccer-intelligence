"""Schwellenwerte der Anomalie-Einstufung (KPI-Regelwerk 2.2), eingelesen aus app/config/schwellen.toml.

Aufbau der Datei:

    [standard]
    leicht = 20      # |Abweichung| bis 20,00 % -> keine Anomalie
    stark = 35       # bis 35,00 % -> leichte, darüber starke Anomalie

    [[abweichung]]   # optional, beliebig oft
    liga = "Serie A" # optional (ohne: alle Ligen)
    kpi = "kpi03"    # optional (ohne: alle KPIs)
    leicht = 15      # gleich für positiv und negativ (±15 / ±30) …
    stark = 30

    [[abweichung]]
    kpi = "kpi02"    # … oder positiv und negativ getrennt (seit Version 0.13)
    leicht_positiv = 20     # über +20,00 % leicht
    stark_positiv = 30      # über +30,00 % stark
    leicht_negativ = -15    # unter −15,00 % leicht
    stark_negativ = -25     # unter −25,00 % stark

Vorrang: Liga und KPI > nur KPI > nur Liga > Standard. Die Datei wird mit dem Code versioniert; Änderungen nur
bewusst über die Datei (Neubau, Git, CHANGELOG), nie über das Dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

from . import settings
from .config import ConfigError, _read_toml, table_list
from .kpis import KPI_KEYS, STANDARD_THRESHOLDS, Thresholds


@dataclass(frozen=True)
class Override:
    liga: str | None
    kpi: str | None
    thresholds: Thresholds

    @property
    def rank(self) -> int:
        """Je genauer, desto höher: Liga und KPI (3) > KPI (2) > Liga (1)."""
        return (2 if self.kpi else 0) + (1 if self.liga else 0)


@dataclass(frozen=True)
class ThresholdConfig:
    standard: Thresholds = STANDARD_THRESHOLDS
    overrides: tuple[Override, ...] = field(default_factory=tuple)

    def get(self, league: str, kpi: str) -> Thresholds:
        """Schwellen für Liga und KPI. config.get wird als Nachschlage-Funktion an compute_match übergeben."""
        matching = [o for o in self.overrides
                    if (o.liga is None or o.liga == league) and (o.kpi is None or o.kpi == kpi)]
        return max(matching, key=lambda o: o.rank).thresholds if matching else self.standard


def _number(value, where: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ConfigError(f"schwellen.toml, {where}: Zahl erwartet")
    try:
        number = Decimal(str(value))            # über Text, damit 20.1 genau 20,1 bleibt
    except InvalidOperation as exc:
        raise ConfigError(f"schwellen.toml, {where}: ungültige Zahl '{value}'") from exc
    if not number.is_finite():
        raise ConfigError(f"schwellen.toml, {where}: ungültige Zahl '{value}'")
    return number


SYMMETRIC = ("leicht", "stark")
SPLIT = ("leicht_positiv", "stark_positiv", "leicht_negativ", "stark_negativ")


def _pair(entry: dict, where: str) -> Thresholds:
    """Entweder leicht/stark (für beide Richtungen) oder alle vier Felder leicht/stark × positiv/negativ."""
    split = [k for k in SPLIT if k in entry]
    if split:
        if any(k in entry for k in SYMMETRIC):
            raise ConfigError(f"schwellen.toml, {where}: entweder leicht/stark oder die vier Felder "
                              f"{', '.join(SPLIT)} angeben, nicht beides")
        for key in SPLIT:
            if key not in entry:
                raise ConfigError(f"schwellen.toml, {where}: Feld '{key}' fehlt")
        lp, sp, ln, sn = (_number(entry[k], where) for k in SPLIT)
        if not (0 < lp < sp):
            raise ConfigError(f"schwellen.toml, {where}: es muss gelten 0 < leicht_positiv < stark_positiv")
        if not (sn < ln < 0):
            raise ConfigError(f"schwellen.toml, {where}: es muss gelten stark_negativ < leicht_negativ < 0")
        return Thresholds(lp, sp, ln, sn)
    for key in SYMMETRIC:
        if key not in entry:
            raise ConfigError(f"schwellen.toml, {where}: Feld '{key}' fehlt")
    light, strong = _number(entry["leicht"], where), _number(entry["stark"], where)
    if not (0 < light < strong):
        raise ConfigError(f"schwellen.toml, {where}: es muss gelten 0 < leicht < stark")
    return Thresholds(light, strong)


def load_thresholds(path: Path | str | None = None, league_names: list[str] | None = None) -> ThresholdConfig:
    path = Path(path) if path else settings.THRESHOLDS_FILE
    data = _read_toml(path)
    if "standard" not in data:
        raise ConfigError(f"{path.name}: Abschnitt [standard] fehlt")
    if not isinstance(data["standard"], dict):
        raise ConfigError(f"{path.name}: [standard] muss ein Abschnitt mit leicht und stark sein")
    standard = _pair(data["standard"], "[standard]")
    overrides = []
    seen = set()
    for i, entry in enumerate(table_list(data, "abweichung", path), start=1):
        where = f"Abweichung {i}"
        liga = str(entry["liga"]).strip() if "liga" in entry else None
        kpi = str(entry["kpi"]).strip().lower() if "kpi" in entry else None
        if liga is None and kpi is None:
            raise ConfigError(f"schwellen.toml, {where}: 'liga' oder 'kpi' angeben (sonst [standard] ändern)")
        if kpi is not None and kpi not in KPI_KEYS:
            raise ConfigError(f"schwellen.toml, {where}: unbekannter KPI '{kpi}' (erlaubt: {', '.join(KPI_KEYS)})")
        if liga is not None and league_names is not None and liga not in league_names:
            raise ConfigError(f"schwellen.toml, {where}: unbekannte Liga '{liga}'")
        if (liga, kpi) in seen:
            raise ConfigError(f"schwellen.toml, {where}: Liga/KPI-Kombination kommt doppelt vor")
        seen.add((liga, kpi))
        overrides.append(Override(liga, kpi, _pair(entry, where)))
    return ThresholdConfig(standard, tuple(overrides))


def _pct(value: Decimal) -> str:
    return f"{value:+.2f} %".replace(".", ",").replace("-", "−")


def describe(config: ThresholdConfig) -> list[dict]:
    """Zeilen für die Anzeige im Bereich Datenqualität: je Geltungsbereich die vier Schwellen.
    Eine Anomalie liegt vor, wenn die gerundete Abweichung über (positiv) bzw. unter (negativ) der Schwelle liegt."""
    def row(scope: str, t: Thresholds) -> dict:
        return {"Gilt für": scope, "Leicht positiv": _pct(t.leicht), "Stark positiv": _pct(t.stark),
                "Leicht negativ": _pct(t.leicht_negativ), "Stark negativ": _pct(t.stark_negativ)}
    rows = [row("Standard (alle übrigen)", config.standard)]
    for o in sorted(config.overrides, key=lambda o: o.kpi or ""):     # je KPI, Ligen in Dateireihenfolge
        scope = " · ".join(x for x in (o.kpi.upper().replace("KPI", "KPI ") if o.kpi else None, o.liga) if x)
        rows.append(row(scope, o.thresholds))
    return rows
