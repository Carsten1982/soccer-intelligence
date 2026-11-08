"""Schwellenwerte aus app/config/schwellen.toml (KPI-Regelwerk 2.2, seit Etappe H)."""

from decimal import Decimal
from pathlib import Path

import pytest

from core.config import ConfigError
from core.kpis import STANDARD_THRESHOLDS, Thresholds
from core.thresholds import describe, load_thresholds

CONFIG = Path(__file__).resolve().parents[1] / "app" / "config" / "schwellen.toml"
LEAGUES = ["Bundesliga", "Premier League", "Serie A", "LaLiga"]


def write(tmp_path, text: str) -> Path:
    p = tmp_path / "schwellen.toml"
    p.write_text(text, encoding="utf-8")
    return p


def test_shipped_file_is_standard_everywhere():
    """Vorgehen 08.11.2026: zuerst überall ±20 % / ±35 %, keine Abweichungen."""
    cfg = load_thresholds(CONFIG, LEAGUES)
    assert cfg.standard == STANDARD_THRESHOLDS == Thresholds(Decimal("20"), Decimal("35"))
    assert cfg.overrides == ()
    for league in LEAGUES:
        for kpi in ("kpi02", "kpi05", "kpi09"):
            assert cfg.get(league, kpi) == STANDARD_THRESHOLDS
    assert describe(cfg) == [{"Gilt für": "Standard (alle Ligen, alle KPIs)",
                              "Schwellen": "keine bis ±20,00 % · leicht bis ±35,00 % · stark darüber"}]


def test_precedence_league_and_kpi_before_kpi_before_league(tmp_path):
    cfg = load_thresholds(write(tmp_path, """
[standard]
leicht = 20
stark = 35
[[abweichung]]
liga = "Serie A"
leicht = 18
stark = 30
[[abweichung]]
kpi = "kpi05"
leicht = 12
stark = 18
[[abweichung]]
liga = "Serie A"
kpi = "kpi05"
leicht = 10.5
stark = 16
"""), LEAGUES)
    assert cfg.get("Bundesliga", "kpi02") == Thresholds(Decimal(20), Decimal(35))
    assert cfg.get("Serie A", "kpi02") == Thresholds(Decimal(18), Decimal(30))
    assert cfg.get("Bundesliga", "kpi05") == Thresholds(Decimal(12), Decimal(18))
    assert cfg.get("Serie A", "kpi05") == Thresholds(Decimal("10.5"), Decimal(16))     # 10.5 bleibt genau 10,5
    assert cfg("Serie A", "kpi05") == cfg.get("Serie A", "kpi05")                      # als Nachschlage-Funktion
    rows = describe(cfg)
    assert rows[1] == {"Gilt für": "Serie A · KPI 05",
                       "Schwellen": "keine bis ±10,50 % · leicht bis ±16,00 % · stark darüber"}


@pytest.mark.parametrize("text, message", [
    ("", "[standard] fehlt"),
    ("[standard]\nleicht = 20\n", "'stark' fehlt"),
    ("[standard]\nleicht = 35\nstark = 20\n", "0 < leicht < stark"),
    ("[standard]\nleicht = 0\nstark = 20\n", "0 < leicht < stark"),
    ("[standard]\nleicht = true\nstark = 35\n", "Zahl erwartet"),
    ("[standard]\nleicht = 20\nstark = 35\n[[abweichung]]\nleicht = 10\nstark = 20\n", "'liga' oder 'kpi'"),
    ("[standard]\nleicht = 20\nstark = 35\n[[abweichung]]\nkpi = \"kpi01\"\nleicht = 10\nstark = 20\n",
     "unbekannter KPI"),
    ("[standard]\nleicht = 20\nstark = 35\n[[abweichung]]\nliga = \"Ligue 1\"\nleicht = 10\nstark = 20\n",
     "unbekannte Liga"),
    ("[standard]\nleicht = 20\nstark = 35\n[[abweichung]]\nkpi = \"kpi05\"\nleicht = 10\nstark = 20\n"
     "[[abweichung]]\nkpi = \"kpi05\"\nleicht = 11\nstark = 21\n", "doppelt"),
    ("[standard\n", "ungültig"),
])
def test_invalid_files_give_clear_message(tmp_path, text, message):
    with pytest.raises(ConfigError, match=message.replace("[", r"\[").replace("(", r"\(")):
        load_thresholds(write(tmp_path, text), LEAGUES)


def test_missing_file(tmp_path):
    with pytest.raises(ConfigError, match="fehlt"):
        load_thresholds(tmp_path / "gibt_es_nicht.toml")
