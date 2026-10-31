"""Oberfläche: Bausteine (ohne Streamlit) und Rauchtests der Seiten (mit Streamlit AppTest).

Die AppTest-Tests laufen nur, wenn Streamlit installiert ist (z. B. im Test-Container auf dem Server)
und die echten Dateien vorhanden sind. Sie prüfen, dass jede Seite ohne Fehler aufgebaut wird.
"""

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


@needs_files
def test_datenqualitaet_page():
    at = AppTest.from_function(_datenqualitaet, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    assert "Datenqualität" in _texts(at)
