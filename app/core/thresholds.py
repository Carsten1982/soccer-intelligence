"""Schwellen und Prognosewerte (KPI-Regelwerk 2.2, seit Version 0.19), eingelesen aus app/config/schwellen.toml.

Je Liga, KPI und Richtung (mehr / weniger) gibt es höchstens eine Schwelle mit ihrem Prognosewert. Kombinationen ohne
Eintrag haben keine Schwelle: Die Kennzahl ist dort nie auffällig. Aufbau der Datei:

    [grundlage]
    saisons = "2019/2020-2025/2026"   # womit die Schwellen berechnet wurden (Sensitivitätsanalyse, Regelwerk 11)
    berechnet = "2026-11-18"
    freigabe = "2026-11-18"           # Freigabe durch Carsten

    [[schwelle]]
    liga = "Bundesliga"
    kpi = "kpi09"
    richtung = "weniger"              # mehr | weniger
    schwelle = 10                     # auffällig, wenn die Abweichung unter −10,00 % liegt
    prognosewert = "hoch"             # hoch | mittel | gering
    spiele = 227                      # Herleitung (Anzeige im Dashboard), optional
    trefferquote = 63.44
    vergleichsgruppe = 51.57
    mehrwert = 11.87
    spanne_links = 5.06
    spanne_rechts = 18.25
    saisons_positiv = "7/7"

Die Datei wird einmal pro Saison nach Saisonende aus dem Schwellenvorschlag der Sensitivitätsanalyse erzeugt, von
Carsten freigegeben und über GitHub übernommen (nie aus dem Dashboard gespeichert). Die Fassung bis Version 0.18
(leicht/stark) liegt in app/config/archiv/.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

from . import settings
from .config import ConfigError, _read_toml, table_list
from .kpis import KPI_KEYS, LEVELS, NO_THRESHOLDS, Signal, Thresholds

DIRECTIONS = ("mehr", "weniger")
STATS = ("spiele", "trefferquote", "vergleichsgruppe", "mehrwert", "spanne_links", "spanne_rechts")


@dataclass(frozen=True)
class ThresholdConfig:
    """Gültige Schwellen: (Liga, KPI) -> Thresholds(positiv, negativ)."""
    by_league_kpi: dict[tuple[str, str], Thresholds] = field(default_factory=dict)
    saisons: str = ""
    berechnet: str = ""
    freigabe: str = ""

    def get(self, league: str, kpi: str) -> Thresholds:
        """Schwellen für Liga und KPI; ohne Eintrag NO_THRESHOLDS (nie auffällig). Wird als Nachschlage-Funktion an
        compute_match übergeben."""
        return self.by_league_kpi.get((league, kpi), NO_THRESHOLDS)

    def entries(self) -> list[tuple[str, str, str, Signal]]:
        """(Liga, KPI, Richtung, Signal) aller Einträge, für Anzeige und Prüfung."""
        out = []
        for (league, kpi), t in self.by_league_kpi.items():
            if t.positiv is not None:
                out.append((league, kpi, "mehr", t.positiv))
            if t.negativ is not None:
                out.append((league, kpi, "weniger", t.negativ))
        return out


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


def _signal(entry: dict, where: str) -> Signal:
    for key in ("schwelle", "prognosewert"):
        if key not in entry:
            raise ConfigError(f"schwellen.toml, {where}: Feld '{key}' fehlt")
    threshold = _number(entry["schwelle"], where)
    if threshold <= 0:
        raise ConfigError(f"schwellen.toml, {where}: die Schwelle muss grösser als 0 sein (Betrag in %)")
    level = str(entry["prognosewert"]).strip().lower()
    if level not in LEVELS:
        raise ConfigError(f"schwellen.toml, {where}: Prognosewert '{level}' unbekannt (erlaubt: {', '.join(LEVELS)})")
    stats = {k: (int(_number(entry[k], where)) if k == "spiele" else _number(entry[k], where))
             for k in STATS if k in entry}
    seasons = str(entry["saisons_positiv"]) if "saisons_positiv" in entry else None
    return Signal(threshold, level, saisons_positiv=seasons, **stats)


def load_thresholds(path: Path | str | None = None, league_names: list[str] | None = None) -> ThresholdConfig:
    path = Path(path) if path else settings.THRESHOLDS_FILE
    data = _read_toml(path)
    if "standard" in data or "abweichung" in data:
        raise ConfigError(f"{path.name}: altes Format (leicht/stark) – seit Version 0.19 gilt [[schwelle]] je Liga, "
                          "KPI und Richtung (Regelwerk 2.2)")
    basis = data.get("grundlage", {})
    if not isinstance(basis, dict):
        raise ConfigError(f"{path.name}: [grundlage] muss ein Abschnitt sein")
    found: dict[tuple[str, str], dict[str, Signal]] = {}
    for i, entry in enumerate(table_list(data, "schwelle", path), start=1):
        where = f"Schwelle {i}"
        for key in ("liga", "kpi", "richtung"):
            if key not in entry:
                raise ConfigError(f"schwellen.toml, {where}: Feld '{key}' fehlt")
        liga, kpi = str(entry["liga"]).strip(), str(entry["kpi"]).strip().lower()
        direction = str(entry["richtung"]).strip().lower()
        if kpi not in KPI_KEYS or kpi == "kpi01":
            raise ConfigError(f"schwellen.toml, {where}: unbekannter KPI '{kpi}' (erlaubt: kpi02 … kpi09)")
        if league_names is not None and liga not in league_names:
            raise ConfigError(f"schwellen.toml, {where}: unbekannte Liga '{liga}'")
        if direction not in DIRECTIONS:
            raise ConfigError(f"schwellen.toml, {where}: Richtung '{direction}' unbekannt (erlaubt: mehr, weniger)")
        slot = found.setdefault((liga, kpi), {})
        if direction in slot:
            raise ConfigError(f"schwellen.toml, {where}: {liga} / {kpi} / {direction} kommt doppelt vor")
        slot[direction] = _signal(entry, where)
    by = {key: Thresholds(d.get("mehr"), d.get("weniger")) for key, d in found.items()}
    return ThresholdConfig(by, str(basis.get("saisons", "")), str(basis.get("berechnet", "")),
                           str(basis.get("freigabe", "")))


def _pct(value: Decimal | None, signed: bool = False) -> str:
    if value is None:
        return "–"
    text = f"{value:+.2f}" if signed else f"{value:.2f}"
    return text.replace(".", ",").replace("-", "−")


def describe(config: ThresholdConfig, league_order: list[str] | None = None) -> list[dict]:
    """Zeilen für die Anzeige im Bereich Datenqualität: je Liga, KPI und Richtung die gültige Schwelle mit Prognosewert
    und Herleitung (Trefferquote, Vergleichsgruppe, Mehrwert)."""
    from .top import TOP_KPIS
    order = {name: i for i, name in enumerate(league_order or [])}
    kpi_order = {k: i for i, k in enumerate(TOP_KPIS)}
    rows = []
    for league, kpi, direction, s in sorted(config.entries(), key=lambda e: (order.get(e[0], 99), e[0],
                                                                                kpi_order.get(e[1], 99), e[2])):
        rows.append({"Liga": league, "KPI": TOP_KPIS.get(kpi, kpi), "Richtung": direction,
                     "Schwelle": f"{'+' if direction == 'mehr' else '−'}{_pct(s.schwelle)} %",
                     "Prognosewert": s.prognosewert,
                     "Spiele": s.spiele if s.spiele is not None else "–",
                     "Trefferquote": f"{_pct(s.trefferquote)} %" if s.trefferquote is not None else "–",
                     "Vergleichsgruppe": f"{_pct(s.vergleichsgruppe)} %" if s.vergleichsgruppe is not None else "–",
                     "Mehrwert in Pp.": _pct(s.mehrwert, signed=True)})
    return rows
