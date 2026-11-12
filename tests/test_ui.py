"""Oberfläche: Bausteine (ohne Streamlit) und Rauchtests der Seiten (mit Streamlit AppTest).

Die AppTest-Tests laufen nur, wenn Streamlit installiert ist (z. B. im Test-Container auf dem Server)
und die echten Dateien vorhanden sind. Sie prüfen, dass jede Seite ohne Fehler aufgebaut wird.
"""

from pathlib import Path

import pytest
from conftest import REAL_DATABASE, REAL_FIXTURES

APP = Path(__file__).resolve().parents[1] / "app" / "app.py"
REAL_FILES = REAL_DATABASE.exists() and REAL_FIXTURES.exists()


# --- HTML-Bausteine ---------------------------------------------------------------

def test_header():
    pytest.importorskip("streamlit")                      # components.py braucht Streamlit (H.2)
    from views.components import header_html
    html = header_html("Aktueller Spieltag", "Saison 2026/27 · Spieltag 1")
    assert "Soccer Intelligence" in html and "KPI-Übersicht pro Spiel" in html and "Spieltag 1" in html
    assert "si-matchday" not in header_html("", "")
    from views.components import SUBTITLE, title_html                  # Ligaseiten-Kopf (Fehler beim Bau von 0.12)
    assert SUBTITLE in title_html() and "Sensitivitätsanalyse" in header_html("", "", subtitle="Sensitivitätsanalyse")
    grid = header_html("Aktueller Spieltag", ["Bundesliga: Spieltag 2", "Serie A: Spieltag 1", "<x>"])
    assert grid.count('class="si-grid-item"') == 3 and "si-grid" in grid and "&lt;x&gt;" in grid


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
    for name in ("Bundesliga", "Premier League", "Serie A", "LaLiga"):     # Kopf: Spieltag je Liga (Etappe F)
        assert f"{name}: Spieltag" in text, name
    assert "si-grid" in text
    assert "Top Anomalien" in text
    from core.top import NO_ANOMALIES_TEXT
    assert "si-card" in text or NO_ANOMALIES_TEXT in text + "\n".join(str(i.value) for i in at.info)


def _liga_bundesliga():
    from core.config import active_leagues, load_leagues
    from views import liga
    liga.render(active_leagues(load_leagues())[0])


def _liga_premier_league():
    from core.config import active_leagues, load_leagues
    from views import liga
    liga.render(active_leagues(load_leagues())[1])


def _liga_serie_a():
    from core.config import active_leagues, load_leagues
    from views import liga
    liga.render(active_leagues(load_leagues())[2])


def _liga_laliga():
    from core.config import active_leagues, load_leagues
    from views import liga
    liga.render(active_leagues(load_leagues())[3])


def _datenqualitaet():
    from views import datenqualitaet
    datenqualitaet.render()


@needs_files
@pytest.mark.parametrize("script", [_liga_bundesliga, _liga_premier_league, _liga_serie_a, _liga_laliga])
def test_league_pages(script):
    at = AppTest.from_function(script, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    text = _texts(at)
    assert "Aktueller Spieltag" in text and 'class="si-cgrid"' in text               # kompakte Tabelle (Etappe H)
    assert "KPI 02" in text and "Erwartete Tore" in text and "si-anom-" in text      # KPI-Spalten befüllt
    assert "KPI 09" in text and "Schüsse aufs Tor" in text and "<details" in text    # KPI 05–09 und Details


def _simulation():
    from views import simulation
    simulation.render()


@needs_files
def test_simulation_page():
    """Version 0.12: Sensitivitätsanalyse, eine Karte je KPI mit vier Schwellen; Eingaben wirken nur hier."""
    at = AppTest.from_function(_simulation, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    text = _texts(at)
    assert "Sensitivitätsanalyse" in text and "keinen Einfluss auf die anderen Dashboard-Tabs" in text
    assert "Häufigkeit leicht" in text and "Ergebnisqualität (Schwelle leicht)" in text and "Empfehlung" in text
    assert len(at.number_input) == 4 * 8                           # je KPI leicht/stark, positiv/negativ
    assert [s.label for s in at.selectbox] == ["Liga", "Saison"]
    at.number_input(key="sth_kpi02_lp").set_value(40.0).run()      # leicht über stark -> stark wird nachgezogen
    assert not at.exception and at.number_input(key="sth_kpi02_sp").value == 40.0
    assert ".st-key-sth_kpi02_lp input" in _texts(at)               # eigener Wert blau


@needs_files
def test_datenqualitaet_page():
    at = AppTest.from_function(_datenqualitaet, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    text = _texts(at)
    assert "Datenqualität" in text and "Gültige Schwellenwerte" in text


# --- Kompakte Tabelle (Etappe H) -------------------------------------------------------

def _match_kpis(home_games: int = 10):
    """Echt berechnete KPIs aus einem kleinen ausgedachten Datensatz. Team „Neu“ hat keine Spiele (Aufsteiger)."""
    from datetime import date

    import pandas as pd

    from core.kpis import Match, compute_match, prepare_league
    rows = []
    for i in range(1, 13):
        home, away = ("A", "B") if i % 2 else ("B", "C")
        rows.append({"id": i, "Date": pd.Timestamp(f"2026-08-{i:02d}"), "matchDate": f"{i:02d}-08-26 15:30",
                     "Season": "2026/2027", "Gameday": i, "homeTeam": home, "awayTeam": away,
                     "FT Home Goals": 2, "FT Away Goals :": 1, "Home Yellow Cards Full Time": 2,
                     "Away Yellow Cards Full Time": 1, "First-Half Home Goals": 1, "First-Half Away Goals": 0,
                     "Second-Half Home Goals": 1, "Second-Half Away Goals": 1, "Home Corners Full Time": 6,
                     "Away Corners Full Time": 4, "Home Shots on Target Full Time": 5, "Away Shots on Target Full Time": 3})
    db = prepare_league(pd.DataFrame(rows))
    home = "A" if home_games else "Neu"
    return compute_match(db, Match("Liga", "2026/2027", 13, date(2026, 9, 1), home, "B"), 34)


def test_compact_table_rows_details_and_status():
    from views.kpi_table import COLUMNS, compact_table_html
    html = compact_table_html([("A", "B", "", _match_kpis()), ("X", "<b>Y</b>", "verschoben", None)])
    assert "&lt;b&gt;Y&lt;/b&gt;" in html and "<b>Y" not in html
    assert html.count("<details") == 1 and html.count("si-cplain") == 1          # verschoben: ohne Details
    assert html.count('class="si-badge"') == 1 and "verschoben" in html
    assert html.count('class="si-kc"') == 1 + len(COLUMNS) == 9                   # KPI 01 + KPI 02–09
    assert html.count("si-cs1") == 3 and html.count("si-cs2") == 3               # Kopf + 2 Zeilen, fixiert
    for c in COLUMNS:
        assert f"<small>{c.number}</small>" in html


def test_compact_values_two_decimals_kpi03_percent_kpi08():
    from views.kpi_table import COLUMNS, compact_value
    k = _match_kpis()
    cols = {c.key: c for c in COLUMNS}
    assert compact_value(cols["kpi02"], k.kpi02) == "3,00"                       # 3 Tore je Spiel
    assert compact_value(cols["kpi03"], k.kpi03) == "+20,00 %"                   # Abweichung zur 2,5-Marke
    assert compact_value(cols["kpi05"], k.kpi05) == "10,00"
    assert compact_value(cols["kpi08"], k.kpi08) == "100,00 %"                   # BTTS-Quote in %


def test_promoted_team_shows_dash_opponent_value_and_v():
    from views.kpi_table import COLUMNS, compact_cell, detail_card
    k = _match_kpis(home_games=0)
    col = COLUMNS[0]
    cell = compact_cell(col, k.kpi02)
    assert ">–<" in cell and 'class="si-v"' in cell and "nicht berechenbar" in cell
    card = detail_card(col, k.kpi02, k)
    assert "nicht berechenbar" in card and "3,00" in card and "0 / 10 Spiele" in card   # Gegnerwert sichtbar


def test_form_marks():
    from core.kpis import FormTeam
    from views.kpi_table import form_marks
    html = form_marks(FormTeam("A", ["–", "–", "–", "S", "N"], 2))
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
