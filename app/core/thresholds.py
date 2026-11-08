"""Schwellenwerte der Anomalie-Einstufung (KPI-Regelwerk 2.2), eingelesen aus app/config/schwellen.toml.

Aufbau der Datei:

    [standard]
    leicht = 20      # |Abweichung| bis 20,00 % -> keine Anomalie
    stark = 35       # bis 35,00 % -> leichte, darüber starke Anomalie

    [[abweichung]]   # optional, beliebig oft
    liga = "Serie A" # optional (ohne: alle Ligen)
    kpi = "kpi03"    # optional (ohne: alle KPIs)
    leicht = 15
    stark = 30

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


def _pair(entry: dict, where: str) -> Thresholds:
    for key in ("leicht", "stark"):
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


def describe(config: ThresholdConfig) -> list[dict]:
    """Zeilen für die Anzeige im Bereich Datenqualität."""
    def fmt(t: Thresholds) -> str:
        return (f"keine bis ±{t.leicht:.2f} % · leicht bis ±{t.stark:.2f} % · stark darüber"
                .replace(".", ","))
    rows = [{"Gilt für": "Standard (alle Ligen, alle KPIs)", "Schwellen": fmt(config.standard)}]
    for o in sorted(config.overrides, key=lambda o: (-o.rank, o.liga or "", o.kpi or "")):
        scope = " · ".join(x for x in (o.liga, o.kpi.upper().replace("KPI", "KPI ") if o.kpi else None) if x)
        rows.append({"Gilt für": scope, "Schwellen": fmt(o.thresholds)})
    return rows
