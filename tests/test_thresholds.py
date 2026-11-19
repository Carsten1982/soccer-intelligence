"""Schwellen und Signalqualität aus app/config/schwellen.toml (KPI-Regelwerk 2.2, seit Version 0.19)."""

from decimal import Decimal
from pathlib import Path

import pytest

from core.config import ConfigError
from core.kpis import HIGH, LOW, NO_THRESHOLDS, Signal, Thresholds
from core.thresholds import describe, load_thresholds

CONFIG = Path(__file__).resolve().parents[1] / "app" / "config" / "schwellen.toml"
ARCHIVE = CONFIG.parent / "archiv" / "schwellen_2026-11-14.toml"
LEAGUES = ["Bundesliga", "Premier League", "Serie A", "LaLiga"]


def write(tmp_path, text: str) -> Path:
    p = tmp_path / "schwellen.toml"
    p.write_text(text, encoding="utf-8")
    return p


ENTRY = '[[schwelle]]\nliga = "Bundesliga"\nkpi = "kpi09"\nrichtung = "weniger"\nschwelle = 10\nsignalqualitaet = "stark"\n'


def test_lookup_per_league_kpi_direction(tmp_path):
    cfg = load_thresholds(write(tmp_path, '[grundlage]\nsaisons = "2019/2020-2025/2026"\nfreigabe = "2026-11-18"\n'
                                + ENTRY + ENTRY.replace('"weniger"', '"mehr"').replace("10", "15.5")
                                .replace('"stark"', '"gering"') + 'spiele = 86\ntrefferquote = 65.12\n'), LEAGUES)
    t = cfg.get("Bundesliga", "kpi09")
    assert t.negativ == Signal(Decimal(10), HIGH)
    assert t.positiv.schwelle == Decimal("15.5") and t.positiv.signalqualitaet == LOW and t.positiv.spiele == 86
    assert t.positiv.trefferquote == Decimal("65.12")
    assert cfg.get("Bundesliga", "kpi02") == NO_THRESHOLDS == Thresholds()          # ohne Eintrag: nie auffällig
    assert cfg.get("Serie A", "kpi09") == NO_THRESHOLDS
    assert (cfg.saisons, cfg.freigabe) == ("2019/2020-2025/2026", "2026-11-18")
    rows = describe(cfg, LEAGUES)
    assert [r["Richtung"] for r in rows] == ["mehr", "weniger"]
    assert rows[0]["Schwelle"] == "+15,50 %" and rows[1]["Schwelle"] == "−10,00 %" and rows[1]["Signalqualität"] == "stark"


@pytest.mark.parametrize("text, message", [
    ("[standard]\nleicht = 20\nstark = 35\n", "altes Format"),
    ('[[schwelle]]\nkpi = "kpi09"\nrichtung = "mehr"\nschwelle = 10\nsignalqualitaet = "stark"\n', "'liga' fehlt"),
    (ENTRY.replace('richtung = "weniger"\n', ""), "'richtung' fehlt"),
    (ENTRY.replace("schwelle = 10\n", ""), "'schwelle' fehlt"),
    (ENTRY.replace('signalqualitaet = "stark"\n', ""), "'signalqualitaet' fehlt"),
    (ENTRY.replace('"weniger"', '"negativ"'), "Richtung 'negativ' unbekannt"),
    (ENTRY.replace('"stark"', '"hoch"'), "Signalqualität 'hoch' unbekannt"),
    (ENTRY.replace("signalqualitaet", "prognosewert"), "heisst seit Version 0.20"),
    (ENTRY.replace("schwelle = 10", "schwelle = 0"), "grösser als 0"),
    (ENTRY.replace("schwelle = 10", "schwelle = true"), "Zahl erwartet"),
    (ENTRY.replace('"kpi09"', '"kpi01"'), "unbekannter KPI"),
    (ENTRY.replace('"Bundesliga"', '"Ligue 1"'), "unbekannte Liga"),
    (ENTRY + ENTRY, "doppelt"),
    ("[[schwelle\n", "ungültig"),
])
def test_invalid_files_give_clear_message(tmp_path, text, message):
    with pytest.raises(ConfigError, match=message.replace("[", r"\[").replace("(", r"\(")):
        load_thresholds(write(tmp_path, text), LEAGUES)


def test_empty_file_means_nothing_is_flagged(tmp_path):
    cfg = load_thresholds(write(tmp_path, ""), LEAGUES)
    assert cfg.entries() == [] and cfg.get("Bundesliga", "kpi02") == NO_THRESHOLDS and describe(cfg) == []


def test_missing_file(tmp_path):
    with pytest.raises(ConfigError, match="fehlt"):
        load_thresholds(tmp_path / "gibt_es_nicht.toml")


def test_old_file_is_archived_and_rejected():
    assert ARCHIVE.exists()
    with pytest.raises(ConfigError, match="altes Format"):
        load_thresholds(ARCHIVE, LEAGUES)
