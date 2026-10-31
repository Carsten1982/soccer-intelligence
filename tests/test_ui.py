"""Oberfläche: Bausteine (ohne Streamlit) und Rauchtests der Seiten (mit Streamlit AppTest).

Die AppTest-Tests laufen nur, wenn Streamlit installiert ist (z. B. im Test-Container auf dem Server)
und die echten Dateien vorhanden sind. Sie prüfen, dass jede Seite ohne Fehler aufgebaut wird.
"""

from fractions import Fraction
from pathlib import Path

import pytest
from conftest import REAL_DATABASE, REAL_FIXTURES

from views.components import ColumnGroup, MatchRow, header_html, match_table_html

APP = Path(__file__).resolve().parents[1] / "app" / "app.py"
REAL_FILES = REAL_DATABASE.exists() and REAL_FIXTURES.exists()


# --- HTML-Bausteine ---------------------------------------------------------------

def test_table_escapes_names_and_marks_status():
    html = match_table_html([MatchRow("Bayern Munich", "<b>Stuttgart</b>", "verschoben"), MatchRow("A", "B")])
    assert "&lt;b&gt;Stuttgart&lt;/b&gt;" in html and "<b>Stuttgart" not in html
    assert html.count('class="si-badge"') == 1 and "verschoben" in html
    assert html.count("<tr>") == 3                       # Kopf + 2 Begegnungen


def test_table_has_two_sticky_columns_and_groups():
    groups = [ColumnGroup("KPI 01", ["Heim", "Gast"]), ColumnGroup("KPI 02", ["Team 1", "Team 2", "Hauptwert"])]
    html = match_table_html([MatchRow("A", "B", cells=["x", "y", "1,7"])], groups)
    assert html.count('si-sticky si-c1') == 2 and html.count('si-sticky si-c2') == 2   # Kopf + Zeile
    assert 'colspan="2"' in html and 'colspan="3"' in html
    assert html.count("<td") == 2 + 5 and html.count(">–<") == 2                       # fehlende Zellen -> „–“


def test_header():
    html = header_html("Aktueller Spieltag", "Saison 2026/27 · Spieltag 1")
    assert "Soccer Intelligence" in html and "KPI-Übersicht pro Spiel" in html and "Spieltag 1" in html
    assert "si-matchday" not in header_html("", "")


# --- Seiten (Streamlit AppTest) ---------------------------------------------------

try:
    from streamlit.testing.v1 import AppTest
except ImportError:  # lokal ohne Streamlit
    AppTest = None
needs_files = pytest.mark.skipif(AppTest is None or not REAL_FILES,
                                 reason="Streamlit oder echte Datenbank/Spielplan nicht vorhanden")
TIMEOUT = 180


def _texts(at) -> str:
    return "\n".join(str(m.value) for m in at.markdown)


@needs_files
def test_app_start_page_top_anomalien():
    at = AppTest.from_file(str(APP), default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    text = _texts(at)
    assert "Soccer Intelligence" in text
    assert "Bundesliga: Spieltag" in text and "Premier League: Spieltag" in text


def _liga_bundesliga():
    from core.config import active_leagues, load_leagues
    from views import liga
    liga.render(active_leagues(load_leagues())[0])


def _liga_premier_league():
    from core.config import active_leagues, load_leagues
    from views import liga
    liga.render(active_leagues(load_leagues())[1])


def _datenqualitaet():
    from views import datenqualitaet
    datenqualitaet.render()


@needs_files
@pytest.mark.parametrize("script", [_liga_bundesliga, _liga_premier_league])
def test_league_pages(script):
    at = AppTest.from_function(script, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    text = _texts(at)
    assert "Aktueller Spieltag" in text and 'class="si-table"' in text
    assert "KPI 02" in text and "Erwartete Tore" in text and "si-anom-" in text      # KPI-Spalten befüllt


@needs_files
def test_datenqualitaet_page():
    at = AppTest.from_function(_datenqualitaet, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    assert "Datenqualität" in _texts(at)


# --- KPI-Zellen (Etappe C) ----------------------------------------------------------

def _kpis(home_games=10, away_games=10, deviation=Fraction(341, 10)):
    from core.kpis import KpiResult, Reference, TeamValue
    h = TeamValue("A", home_games, 47 if home_games else None, Fraction(47, 10) if home_games else None)
    a = TeamValue("B", away_games, 40, Fraction(4))
    main = (h.wert + a.wert) / 2 if h.wert is not None else None
    r = KpiResult("KPI02", h, a, Reference("x", 180, 584, Fraction(584, 180)), main,
                  deviation if main is not None else None, vorlaeufig=min(home_games, away_games) < 10)
    return r


def test_kpi_cells_complete_and_promoted_team():
    from views.kpi_table import N_CELLS, data_basis_cell, empty_cells, kpi_cells
    full = kpi_cells(_kpis(), "3,2")
    assert len(full) == 8 and "+34,1 %" in full[4] and "si-anom-leicht" in full[5] and full[6].endswith("10</span>")
    promoted = kpi_cells(_kpis(home_games=0), "3,2")
    assert promoted[0] == "–" and promoted[1] == "4,0"                 # Gegnerwert wird angezeigt
    assert "–" in promoted[2] and promoted[4] == "–" and promoted[5] == "–"
    assert "0 / 10" in data_basis_cell(_kpis(home_games=0)) and 'class="si-v"' in data_basis_cell(_kpis(home_games=0))
    assert len(empty_cells()) == N_CELLS == 2 + 3 * 8


def test_form_cell():
    from core.kpis import FormTeam
    from views.kpi_table import form_cell
    html = form_cell(FormTeam("A", ["–", "–", "–", "S", "N"], 2))
    assert html.count("si-form-none") == 3 and "si-form-S" in html and "si-form-N" in html


# --- Spieltag-Auswahl mit Pfeilen (Seiten-Test) ----------------------------------------

@needs_files
def test_league_page_arrow_back_and_address():
    at = AppTest.from_function(_liga_bundesliga, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    prev = at.button(key="prev_bundesliga")
    nxt = at.button(key="next_bundesliga")
    assert nxt.disabled                                   # vom aktuellen Spieltag nicht in die Zukunft
    if prev.disabled:
        pytest.skip("im Spielplan gibt es nur einen auswählbaren Spieltag")
    prev.click().run()
    assert not at.exception, at.exception
    assert "Ausgewählter Spieltag" in _texts(at)
    assert at.button(key="current_bundesliga") is not None   # „Zum aktuellen Spieltag“
    if hasattr(at, "query_params"):
        assert "spieltag" in at.query_params


@needs_files
def test_league_page_invalid_address_falls_back_to_current():
    at = AppTest.from_function(_liga_bundesliga, default_timeout=TIMEOUT)
    if not hasattr(at, "query_params"):
        pytest.skip("AppTest ohne query_params")
    at.query_params["spieltag"] = "999"
    at.run()
    assert not at.exception, at.exception
    text = _texts(at) + "\n".join(str(c.value) for c in at.caption)
    assert "Aktueller Spieltag" in text and "nicht verfügbar" in text
