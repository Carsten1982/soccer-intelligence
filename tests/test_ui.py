"""Oberfläche: Bausteine (ohne Streamlit) und Rauchtests der Seiten (mit Streamlit AppTest).

Die AppTest-Tests laufen nur, wenn Streamlit installiert ist (z. B. im Test-Container auf dem Server)
und die echten Dateien vorhanden sind. Sie prüfen, dass jede Seite ohne Fehler aufgebaut wird. Ausnahme: der Test,
dass die Hilfe `_app_logged_in` an der Anmeldemaske vorbeikommt, läuft auch ohne echte Dateien (seit 0.15.2).
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


def _app_logged_in(monkeypatch):
    """Ganze App starten, schon angemeldet. Seit 0.15.2 steht vor dem Dashboard die Anmeldemaske; ohne Test-Zugang
    zeigte der Seitentest nur „Anmeldung … nicht eingerichtet“ (Fehler beim Einspielen von 0.15.2, 16.11.2026 – der
    Test läuft nur auf dem Server, weil er die echten Excel-Dateien braucht). Der Zugang hier ist nur für den Test."""
    import anmeldung
    monkeypatch.setenv("SI_LOGIN_USER", "test")
    monkeypatch.setenv("SI_LOGIN_HASH", anmeldung.make_hash("test-passwort-1", iterations=1_000))
    at = AppTest.from_file(str(APP), default_timeout=TIMEOUT)
    at.session_state[anmeldung.SESSION_KEY] = True
    return at.run()


@pytest.mark.skipif(AppTest is None, reason="Streamlit nicht vorhanden")
def test_app_logged_in_passes_login_mask(monkeypatch):
    """Läuft auch ohne echte Dateien (lokal, GitHub): Die Hilfe oben kommt an der Anmeldemaske vorbei."""
    at = _app_logged_in(monkeypatch)
    assert not at.exception, at.exception
    assert not any(t.label in ("Benutzername", "Passwort") for t in at.text_input)
    assert "nicht eingerichtet" not in "\n".join(str(e.value) for e in at.error)
    assert "Soccer Intelligence" in _texts(at)
    assert [b.label for b in at.button].count("Abmelden") == 1


@needs_files
def test_app_start_page_top_anomalien(monkeypatch):
    at = _app_logged_in(monkeypatch)
    assert not at.exception, at.exception
    text = _texts(at)
    assert "Soccer Intelligence" in text
    for name in ("Bundesliga", "Premier League", "Serie A", "LaLiga"):     # Kopf: Block je Liga (seit 0.16)
        assert f"<b>{name}</b>: " in text, name
    assert "si-chips" in text
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
    assert "Kommende Spiele" in text                                                 # seit 0.16
    if 'class="si-cgrid"' not in text:                # Pause (z. B. Winterpause): nur der Hinweis, je nach Datum
        assert 'class="si-note' in text
        return
    assert "KPI 02" in text and "Erwartete Tore" in text and "si-anom-" in text      # KPI-Spalten (Etappe H)
    assert "KPI 09" in text and "Schüsse aufs Tor" in text                           # KPI 05–09
    assert "<details" in text or "si-cgate" in text   # Details, oder „Werte ab …“ wenn ein Vorspiel noch fehlt


def _simulation():
    from views import simulation
    simulation.render()


@needs_files
def test_simulation_page():
    """Version 0.19: zwei Zeilen je KPI (mehr, weniger) mit je einer Schwelle, Spalte Signalqualität (bis 0.19 Prognosewert), Erklärfeld und
    Schwellenvorschlag. Vorbelegt mit den gültigen Schwellen; bei „Alle Ligen“ leer, wenn die Ligen verschieden sind
    („je Liga“) oder keine haben („keine“), bei einer Liga deren Werte. Eingaben wirken nur hier."""
    at = AppTest.from_function(_simulation, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    text = _texts(at)
    assert "Sensitivitätsanalyse" in text and "keinen Einfluss auf die anderen Dashboard-Tabs" in text
    for label in ("Betroffene Spiele", "Ergebnisqualität und Signalqualität", "Vergleichs", "Empfehlung", "↗ mehr",
                  "↘ weniger", "Mehr Details findest du unter der Tabelle.", "Schüsse aufs Tor", "Schwellenvorschlag"):
        assert label in text, label
    assert "Leicht positiv" not in text and "Stark negativ" not in text
    assert len(at.number_input) == 2 * 8                           # je KPI mehr und weniger
    assert [s.label for s in at.selectbox] == ["Liga", "Saison"]
    value = lambda kpi: [at.number_input(key=f"sth_{kpi}_{p}").value for p in ("mehr", "weniger")]  # noqa: E731
    assert value("kpi09") == [None, None] and value("kpi07") == [None, None]      # je Liga bzw. keine
    assert 'si-perliga">BL 15 · PL 10 · LL 10<' in text and 'si-perliga">PL 10 · SA 15<' in text   # 0.19.1: je Liga
    at.number_input(key="sth_kpi07_mehr").set_value(30.0).run()    # eine Zahl gilt für alle Ligen
    assert not at.exception and ".st-key-sth_kpi07_mehr input" in _texts(at)       # eigener Wert blau
    at.button(key="sens_reset").click().run()
    assert value("kpi07") == [None, None]
    at.selectbox(key="sens_liga").set_value("Bundesliga").run()
    assert not at.exception
    assert value("kpi09") == [15.0, 10.0] and value("kpi08") == [None, 35.0] and value("kpi02") == [None, None]
    at.selectbox(key="sens_liga").set_value("Premier League").run()   # Fehler 0.19: Feld blieb nach dem Wechsel leer
    assert not at.exception and value("kpi02") == [None, 10.0] and value("kpi09") == [10.0, None]
    assert 'class="si-perliga"' not in _texts(at)                     # eine Liga: Zahl im Feld, kein Hinweis
    at.button(key="sens_proposal").click().run()                   # Vorschlag: nur Anzeige und Download
    assert not at.exception, at.exception
    tables = [d.value for d in at.dataframe if "signalqualitaet" in d.value.columns]
    assert tables and len(tables[0]) > 0 and set(tables[0]["signalqualitaet"]) <= {"stark", "mittel", "gering"}
    single = [s for s in at.selectbox(key="sens_saison").options if s.startswith("Saison ")]
    at.selectbox(key="sens_saison").set_value(single[0]).run()     # eine Saison: keine Signalqualität
    assert not at.exception and "nur bei mehreren Saisons" in _texts(at)


@needs_files
def test_datenqualitaet_page():
    at = AppTest.from_function(_datenqualitaet, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    text = _texts(at)
    assert "Datenqualität" in text and "Gültige Schwellen und Signalqualität" in text    # seit 0.20
    assert "Häufigkeit je Liga und KPI" in text
    tables = [d.value for d in at.dataframe if "Signalqualität" in d.value.columns and "Richtung" in d.value.columns]
    assert tables and len(tables[0]) == 23                          # die freigegebenen Schwellen


def test_top_selection_text_and_navigation_order():
    """0.19.1 (Carsten 18.11.2026): Text unter den Top Anomalien mit drei Zwischentiteln; Reiter Sensitivitätsanalyse
    vor Datenqualität."""
    pytest.importorskip("streamlit")
    from views.top_anomalien import selection_text
    text = selection_text()
    titles = ["**Berücksichtigte Spiele**", "**Auswahl der Auffälligkeiten**", "**Verteilung der Spiele**"]
    assert [text.index(t) for t in titles] == sorted(text.index(t) for t in titles)
    for part in ("Je Liga zählt der nächste Spieltag, wenn er innerhalb der nächsten 14 Tage beginnt",
                 "in der Regel höchstens zwei Spiele", "Maximale Anzahl: 4 Spiele", "zuerst stark, dann mittel"):
        assert part in text, part
    app = (Path(__file__).resolve().parents[1] / "app" / "app.py").read_text(encoding="utf-8")
    nav = app[app.index("st.navigation(["):]
    assert nav.index('PAGES["simulation"]') < nav.index('PAGES["datenqualitaet"]') < nav.index('PAGES["datenimport"]')


def test_per_league_hint():
    pytest.importorskip("streamlit")
    from core.sensitivity import Limits
    from views.simulation import per_league_hint
    D = __import__("decimal").Decimal
    per = {"Bundesliga": Limits(None, None), "Premier League": Limits(None, D("10.0")),
           "Serie A": Limits(None, D("15.0")), "LaLiga": Limits(None, None)}
    assert per_league_hint(per, "weniger") == "PL 10 · SA 15" and per_league_hint(per, "mehr") == ""
    assert per_league_hint({"Bundesliga": Limits(D("10"), None), "LaLiga": Limits(D("10"), None)}, "mehr") == ""


def test_rule_numbers_in_texts():
    """Fehler beim Testen von 0.19: Zahlen der Regeln ohne Nachkommastellen verloren ihre Null (10 → 1, 60 → 6)."""
    pytest.importorskip("streamlit")
    from decimal import Decimal

    from views.simulation import _n
    assert [_n(Decimal(x)) for x in ("10", "60", "50", "5", "2", "35")] == ["10", "60", "50", "5", "2", "35"]
    assert [_n(Decimal(x)) for x in ("10.0", "12.50", "0.5", "100")] == ["10", "12,5", "0,5", "100"]
    assert _n(15) == "15"


def _explanation():
    from views import simulation
    simulation.explanation()


@pytest.mark.skipif(AppTest is None, reason="Streamlit nicht vorhanden")
def test_explanation_uses_the_shipped_example():
    """Erklärfeld der Sensitivitätsanalyse: Beispiel Bundesliga, Schüsse aufs Tor, weniger (Schwelle 10 %, 227 Spiele,
    144 eingetroffen, 63,44 % gegen 51,57 %, +11,87 Pp., Spanne +5,06 bis +18,25, 7 von 7, stark) und die Zahlen der
    Regeln. Seit 0.19.1 mit zwei Nachkommastellen, damit die Rechnung aufgeht (vorher 63 − 52 = +12)."""
    at = AppTest.from_function(_explanation, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    text = _texts(at)
    for part in ("mehr als <b>10 %</b> darunter", "In 227 früheren Spielen lag die Erwartung mehr als 10 % unter",
                 "In 144", "<b>63,44 %</b>", "in\n51,57 % der Fälle", "63,44 − 51,57 = <b>+11,87 Prozentpunkte</b>",
                 "in rund 12 von 100", "<b>+5,06 und +18,25\nPp.</b>", "rund 5 Treffer mehr", "7 von 7 Saisons",
                 "Signalqualität <b>stark</b>", "10, 15, 20, 25, 30 und 35 %", "**ab 60 %**", "**ab +8 Pp.**",
                 "**ab 55 %**", "**ab 50 %**", "über +2 Pp.", "rechte (obere) Wert", "weder in den Top Anomalien"):
        assert part in text, part


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
    assert "Kommende Spiele" in _texts(at)
    prev = at.button(key="prev_bundesliga")
    if prev.disabled:
        pytest.skip("im Spielplan gibt es nur einen auswählbaren Spieltag")
    prev.click().run()
    assert not at.exception, at.exception
    assert "Ausgewählter Spieltag" in _texts(at)
    assert at.button(key="current_bundesliga") is not None   # „Zu den kommenden Spielen“
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
    assert "Kommende Spiele" in text and "nicht verfügbar" in text


# --- Kommende Spieltage (Version 0.16): Tabelle, Ligaseite und Top Anomalien ohne echte Dateien -----------------

def test_table_row_date_grey_gate_and_tag():
    from views.kpi_table import COLUMNS, TableRow, compact_table_html
    k = _match_kpis()
    html = compact_table_html([
        TableRow("A", "B", "", k, "Fr 20.11. · <b>2:1</b>", grey=True),                     # gespielt: grau, mit Details
        TableRow("C", "D", "", k, "<b>Sa 21.11. · 18:30</b>", gate="Werte ab So 22.11. – C spielt vorher noch"),
        TableRow("E", "F", "", None, "Sa 21.11. · verschoben", grey=True),
        TableRow("G", "<i>H</i>", "", k, "<b>So 22.11. · 15:30</b>", tag="Nachholspiel"),
    ])
    assert '<div class="si-cc si-cd">Datum</div>' in html                                    # Spalte zwischen Spiel und Form
    assert html.index("si-cd") < html.index("si-cf")
    assert html.count("<details") == 2                                                       # gespielt + normal
    assert html.count("si-grey") == 2 and html.count('class="si-cc si-cgate"') == 1
    assert "Werte ab So 22.11. – C spielt vorher noch" in html
    assert 'class="si-tag si-tag-catchup">Nachholspiel<' in html and "&lt;i&gt;H&lt;/i&gt;" in html
    gate_row = html.split("si-cgate")[0].rsplit("si-crow", 1)[1]
    assert "si-cplain" in gate_row and html.count('class="si-kc"') == 2 * (1 + len(COLUMNS))


def test_liga_address_and_arrows():
    pytest.importorskip("streamlit")
    from core import anzeige as A
    from views import liga
    keys = [("2025/2026", 34), ("2026/2027", 1), ("2026/2027", 2), ("2026/2027", 3), ("2026/2027", 4)]
    anchor = ("2026/2027", 2)
    assert liga.requested({}, keys, anchor) == (None, False)
    assert liga.requested({"spieltag": "1"}, keys, anchor) == (("2026/2027", 1), False)
    assert liga.requested({"spieltag": "34", "saison": "2025-26"}, keys, anchor) == (("2025/2026", 34), False)
    assert liga.requested({"spieltag": "5"}, keys, anchor) == (None, True)                 # weiter als 2 vorwärts
    assert liga.requested({"spieltag": "x"}, keys, anchor) == (None, True)
    assert liga.params_for(("2025/2026", 34), anchor) == {"spieltag": "34", "saison": "2025-26"}
    assert liga.params_for(("2026/2027", 3), anchor) == {"spieltag": "3"} and liga.params_for(None, anchor) == {}
    shown = A.Upcoming([], None, anchor, True, False)
    assert liga.arrows(None, keys, shown) == (("2026/2027", 1), ("2026/2027", 3))
    pause = A.Upcoming([], None, anchor, False, False)                                     # Winterpause: nur Hinweis
    assert liga.arrows(None, keys, pause) == (("2026/2027", 1), ("2026/2027", 2))
    assert liga.arrows(("2026/2027", 4), keys, shown) == (("2026/2027", 3), None)
    assert liga.arrows(("2025/2026", 34), keys, shown) == (None, ("2026/2027", 1))


def test_liga_notice_and_section_head():
    pytest.importorskip("streamlit")
    from datetime import date
    import pandas as pd
    from core import anzeige as A
    from views import liga
    html = liga.notice_html(A.Notice(A.WINTER, "Winterpause", "nächster Spieltag am Fr 08.01.2027", "(Spieltag 15)"))
    assert html == ('<div class="si-note"><b>Winterpause</b> – nächster Spieltag am Fr 08.01.2027 (Spieltag 15)'
                    "</div>")
    stale = liga.notice_html(A.Notice(A.STALE, "Spielplan zuletzt aktualisiert am", "Do 19.11.2026", "<x>"))
    assert "si-note-stale" in stale and "<b>Do 19.11.2026</b>" in stale and "&lt;x&gt;" in stale
    games = pd.DataFrame({"datum_von": [date(2026, 12, 2), date(2026, 12, 2)]})
    sec = A.Section("2026/2027", 23, "vorgezogen", games, rest="übrige Spiele des Spieltags im Februar")
    head = liga.section_head_html(sec, single=False)
    assert "Spieltag 23</span>" in head and "si-tag-early" in head
    assert "Mi 02.12. · 2 Spiele (übrige Spiele des Spieltags im Februar)" in head
    sec = A.Section("2026/2027", 10, "", games, hidden=("verschoben", "verschoben", "abgesagt"))
    assert "(2 Spiele verschoben, 1 Spiel abgesagt – beim Blättern sichtbar)" in liga.section_head_html(sec, False)
    assert "beim Blättern" not in liga.section_head_html(sec, single=True)


def _liga_test_league():
    from core.config import League
    from views import liga
    liga.render(League("Bundesliga", "bundesliga", 4, True))


def _top_page():
    from views import top_anomalien
    top_anomalien.render()


def _patch_display(monkeypatch, module, now, fx, imported):
    from types import SimpleNamespace
    monkeypatch.setattr(module, "get_database", lambda: SimpleNamespace(has_errors=False))
    monkeypatch.setattr(module, "get_fixtures", lambda: SimpleNamespace(has_errors=False, leagues={"Bundesliga": fx}))
    monkeypatch.setattr(module, "get_results", lambda lg: {("2026/2027", "A", "B"): (2, 1)})
    monkeypatch.setattr(module, "get_round_kpis", lambda lg, s, m: {})
    monkeypatch.setattr(module, "last_import", lambda: imported)
    monkeypatch.setattr(module, "now", lambda: now)


@pytest.mark.skipif(AppTest is None, reason="Streamlit nicht vorhanden")
def test_league_page_sections_and_forward_two(monkeypatch):
    """Ligaseite mit festem Spielplan: zwei Abschnitte (englische Woche), gespielt grau mit Ergebnis, ▶ höchstens
    2 Spieltage über den anstehenden hinaus, „Zu den kommenden Spielen“ zurück."""
    from datetime import date, datetime
    from test_anzeige import plan, rnd
    import views.liga as liga
    fx = plan(*[rnd(n, date(2026, 11, 6 + 7 * (n - 1)), date(2026, 11, 8 + 7 * (n - 1))) for n in range(1, 4)],
              rnd(4, date(2026, 11, 24), date(2026, 11, 25)), rnd(5, date(2026, 11, 29), date(2026, 11, 29)),
              rnd(6, date(2026, 12, 4), date(2026, 12, 6)), rnd(7, date(2026, 12, 11), date(2026, 12, 13)))
    _patch_display(monkeypatch, liga, datetime(2026, 11, 22, 12, 0), fx, datetime(2026, 11, 22, 4, 0))
    at = AppTest.from_function(_liga_test_league, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    text = _texts(at)
    assert "Kommende Spiele" in text and "Saison 2026/27 · ab So 22.11." in text
    assert text.count('class="si-sec"') == 2 and "Spieltag 3</span>" in text and "Spieltag 4</span>" in text
    assert "Fr 20.11. · <b>2:1</b>" in text and "si-grey" in text                          # A–B gespielt (2:1)
    nxt = at.button(key="next_bundesliga")
    nxt.click().run()
    assert "Ausgewählter Spieltag" in _texts(at) and "Saison 2026/27 · Spieltag 4" in _texts(at)
    at.button(key="next_bundesliga").click().run()
    assert "Spieltag 5" in _texts(at) and at.button(key="next_bundesliga").disabled      # 3 + 2 = 5
    at.button(key="current_bundesliga").click().run()
    assert "Kommende Spiele" in _texts(at)


@pytest.mark.skipif(AppTest is None, reason="Streamlit nicht vorhanden")
def test_league_page_winter_break_notice_only(monkeypatch):
    from datetime import date, datetime
    from test_anzeige import plan, rnd
    import views.liga as liga
    fx = plan(rnd(14, date(2026, 12, 18), date(2026, 12, 20)), rnd(15, date(2027, 1, 8), date(2027, 1, 10)))
    _patch_display(monkeypatch, liga, datetime(2026, 12, 23, 10, 0), fx, datetime(2026, 12, 23, 4, 0))
    at = AppTest.from_function(_liga_test_league, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    text = _texts(at)
    assert "<b>Winterpause</b> – nächster Spieltag am Fr 08.01.2027 (Spieltag 15)" in text
    assert 'class="si-sec"' not in text
    assert not at.button(key="prev_bundesliga").disabled and not at.button(key="next_bundesliga").disabled
    _patch_display(monkeypatch, liga, datetime(2026, 12, 23, 10, 0), fx, datetime(2026, 12, 19, 4, 0))   # Import 4 Tage alt
    at = AppTest.from_function(_liga_test_league, default_timeout=TIMEOUT).run()
    assert "Spielplan zuletzt aktualisiert am <b>Sa 19.12.2026</b>" in _texts(at) and "Winterpause" not in _texts(at)


@pytest.mark.skipif(AppTest is None, reason="Streamlit nicht vorhanden")
def test_top_page_headers_per_league(monkeypatch):
    from datetime import date, datetime
    from test_anzeige import plan, rnd
    import views.top_anomalien as top
    fx = plan(rnd(10, date(2026, 11, 20), date(2026, 11, 22)), rnd(11, date(2026, 11, 27), date(2026, 11, 29)))
    _patch_display(monkeypatch, top, datetime(2026, 11, 21, 16, 0), fx, datetime(2026, 11, 21, 4, 0))
    from core.config import League
    monkeypatch.setattr(top, "get_active_leagues", lambda: [League("Bundesliga", "bundesliga", 4, True)])
    at = AppTest.from_function(_top_page, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    from core.top import NO_ANOMALIES_TEXT
    assert "<b>Bundesliga</b>: Spieltag 10 · noch 1 Spiel" in _texts(at)
    assert NO_ANOMALIES_TEXT in "\n".join(str(i.value) for i in at.info)


def test_top_card_shows_date_and_kickoff():
    pytest.importorskip("streamlit")
    from datetime import date
    from core.top import Candidate, TopEntry
    from views.top_anomalien import card_html
    k = _match_kpis()
    c = Candidate("Bundesliga", 0, "2026/2027", 10, date(2026, 11, 21), 0, "A", "B", "geplant", k, "Sa 21.11. · 18:30")
    html = card_html(TopEntry(1, c, "kpi02", "KPI 02 – Erwartete Tore", k.kpi02))
    assert "Bundesliga · Spieltag 10 · <b>Sa 21.11. · 18:30</b>" in html and "si-card-played" not in html
    played = Candidate("Bundesliga", 0, "2026/2027", 10, date(2026, 11, 21), 0, "A", "B", "geplant", k,
                       "Sa 21.11. · Gespielt", played=True)                            # seit 0.20: ausgegraut
    html = card_html(TopEntry(1, played, "kpi02", "KPI 02 – Erwartete Tore", k.kpi02))
    assert 'class="si-card si-card-played"' in html and "<b>Sa 21.11. · Gespielt</b>" in html


# --- Datenimport/API (Version 0.14) -------------------------------------------------------

def test_import_tab_snapshot_box():
    """Überwachung der Schnappschüsse im Reiter (seit 0.20)."""
    pytest.importorskip("streamlit")
    from datetime import datetime
    from views.datenimport import snapshot_box
    assert "Noch kein Lauf" in snapshot_box(None, datetime(2026, 11, 21, 15, 0))
    stand = {"lauf": "2026-11-21T14:00:05", "neu": 3, "neu_nachtraeglich": 1, "ergebnisse_neu": 2, "vorhanden": 9,
             "wartend": ["Bundesliga: A – B (21.11.2026)"], "fehler": None, "dauer_s": 6.1,
             "ligen": {"Bundesliga": {"neu": 3, "vorhanden": 9, "wartend": 1}}}
    html = snapshot_box(stand, datetime(2026, 11, 21, 15, 0))
    assert 'class="di-ok"' in html and "neu 3 (davon nachträglich 1)" in html and "Bundesliga: A – B" in html
    assert 'class="di-bad"' in snapshot_box(stand, datetime(2026, 11, 21, 16, 30))       # älter als 2 Stunden
    assert "Fehler: kaputt" in snapshot_box({**stand, "fehler": "kaputt"}, datetime(2026, 11, 21, 15, 0))


def _datenimport():
    from views import datenimport
    datenimport.render()


def _write_import_dir(base, status="wartet", fehler=0):
    import json
    run = "2026-11-17_040000"
    (base / "laeufe" / run).mkdir(parents=True)
    (base / "anfragen").mkdir()
    rep = {"lauf": run, "start": "2026-11-17T04:00:00+01:00", "status": status, "fehler": fehler, "ganze_saison": False,
           "basis": {"datenbank": "3a2589616b2b0625", "spielplan": "x"}, "saison": {"Bundesliga": "2026/2027"},
           "abo": {"plan": "Pro", "bis": "2027-02-15", "aktiv": True}, "anfragen": {"verbraucht": 52, "rest": 7448},
           "neue_spiele": {"Bundesliga": [{"id": 1, "datum": "15.11.2026", "spieltag": 11, "heim": "Bayern München",
                                           "gast": "1. FC Köln", "endstand": "2:1", "halbzeit": "1:0", "ecken": "6:3",
                                           "gelb": "1:2", "aufs_tor": "7:3"}]},
           "korrekturen": [{"liga": "Bundesliga", "id": 2, "spiel": "A - B", "datum": "08.11.2026",
                            "spalte": "Away Yellow Cards Full Time", "alt": 2, "neu": 3}],
           "offen": [{"liga": "LaLiga", "heim": "Valencia", "gast": "Real Betis", "datum": "16.11.2026",
                      "grund": "Statistik noch unvollständig"}],
           "umbenennungen": [{"liga": "Bundesliga", "alt": "FC Koln", "neu": "1. FC Köln", "zeilen": 281}],
           "spielplan_aenderungen": {"neu": 1, "entfallen": 0, "wichtig": 1, "geaendert": [],
                                     "gruppen": {"verschoben": [], "nachholspiel": [
                                         {"liga": "Bundesliga", "spieltag": 9, "spiel": "Mainz - Bremen", "gruppe": "nachholspiel",
                                          "vorher": {"Datum von": "07.11.2026"}, "neu": {"Datum von": "09.12.2026"}}],
                                                 "vorgezogen": [], "termin": [], "status": [], "anstoss": [],
                                                 "festgelegt": [], "vermerk": []}},
           "wertungen": [],
           "kritisch": [{"art": "endstand", "liga": "Serie A", "id": 77, "spiel": "Verona - Roma", "datum": "19.09.2026",
                         "api": "3:0", "ereignisse": "0:0", "text": "x"}],
           "spaete_korrekturen": [{"liga": "Bundesliga", "id": 5, "spiel": "C - D", "datum": "01.11.2026",
                                   "spalte": "Home Corners Full Time", "alt": 6, "neu": 7, "kpi": True}],
           "plausibilitaet": {"fehler": [], "warnungen": []}, "zuordnung": [], "doppelte_ids": [],
           "automatik": {"ok": False, "gruende": ["1 kritische Punkte"]},
           "unbekannte_teams": [], "namensaenderungen_api": [],
           "vollstaendigkeit": {"Bundesliga": [{"spieltag": 11, "faellig": 9, "geliefert": 9, "inaktiv": 0, "fehlt": 0,
                                                "fehlende": [], "inaktive": []}]},
           "pruefung": {"datenbank": {"gueltig": {"fehler": 0, "warnungen": 35, "hinweise": 201},
                                      "neu": {"fehler": fehler, "warnungen": 35, "hinweise": 201}, "neue_meldungen": []},
                        "spielplan": {"gueltig": {"fehler": 0, "warnungen": 0, "hinweise": 0},
                                      "neu": {"fehler": 0, "warnungen": 0, "hinweise": 0}, "meldungen": []}}}
    (base / "laeufe" / run / "bericht.json").write_text(json.dumps(rep), encoding="utf-8")
    (base / "zustand.json").write_text(json.dumps({"wartend": run, "letzter_lauf_tag": "2026-11-17"}), encoding="utf-8")
    return run


@pytest.mark.skipif(AppTest is None, reason="Streamlit nicht vorhanden")
def test_datenimport_page(tmp_path, monkeypatch):
    """Reiter Datenimport/API: Statusleiste, Kasten „Neue Daten bereit“, Protokoll; „Übernehmen“ legt nur eine
    Anfrage ab (das Dashboard schreibt nie in die Excel-Dateien)."""
    from importer import einstellungen
    monkeypatch.setattr(einstellungen, "IMPORT_DIR", tmp_path)
    import views.datenimport as di
    monkeypatch.setattr(di, "reports", lambda base, days: di_reports(base))
    run = _write_import_dir(tmp_path)

    def di_reports(base):
        import json
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((base / "laeufe").glob("*/bericht.json"))]

    at = AppTest.from_function(_datenimport, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    text = _texts(at)
    for label in ("Datenimport/API", "API-Football · Pro", "Neue Daten bereit", "A · Ergebnisse", "B · Spielplan",
                  "Ihre Entscheidung", "Protokoll der letzten 14 Tage", "wartet", "täglich"):
        assert label in text, label
    labels = [b.label for b in at.button]
    assert labels == ["Ergebnis auf dem Platz (Tor-Ereignisse)", "Endstand der API", "API-Wert übernehmen",
                      "bisherigen Wert behalten", "✓ Übernehmen (Ergebnisse und Spielplan)", "✕ Verwerfen"]
    ok = at.button[labels.index("✓ Übernehmen (Ergebnisse und Spielplan)")]
    assert not ok.disabled
    ok.click().run()
    import json
    reqs = [json.loads(p.read_text()) for p in (tmp_path / "anfragen").glob("*.json")]
    assert reqs and reqs[0]["lauf"] == run and reqs[0]["aktion"] == "uebernehmen"
    assert "Freigabe hinterlegt" in "\n".join(str(i.value) for i in at.info)


@pytest.mark.skipif(AppTest is None, reason="Streamlit nicht vorhanden")
def test_datenimport_decision_buttons(tmp_path, monkeypatch):
    """R1/R2: Ein Entscheid-Button legt nur eine Anfrage ab; danach ist der Punkt nicht mehr offen."""
    from importer import einstellungen
    monkeypatch.setattr(einstellungen, "IMPORT_DIR", tmp_path)
    import views.datenimport as di
    import json
    monkeypatch.setattr(di, "reports", lambda base, days: [json.loads(p.read_text(encoding="utf-8"))
                                                          for p in (base / "laeufe").glob("*/bericht.json")])
    _write_import_dir(tmp_path)
    at = AppTest.from_function(_datenimport, default_timeout=TIMEOUT).run()
    at.button[0].click().run()                                    # „Ergebnis auf dem Platz“
    reqs = [json.loads(p.read_text()) for p in (tmp_path / "anfragen").glob("*.json")]
    assert reqs[0]["aktion"] == "entscheid" and (reqs[0]["art"], reqs[0]["id"], reqs[0]["entscheid"]) == ("endstand", 77, "platz")
    assert "Ergebnis auf dem Platz (Tor-Ereignisse)" not in [b.label for b in at.button]


@pytest.mark.skipif(AppTest is None, reason="Streamlit nicht vorhanden")
def test_datenimport_page_blocks_on_errors(tmp_path, monkeypatch):
    from importer import einstellungen
    monkeypatch.setattr(einstellungen, "IMPORT_DIR", tmp_path)
    import views.datenimport as di
    import json
    monkeypatch.setattr(di, "reports", lambda base, days: [json.loads(p.read_text(encoding="utf-8"))
                                                          for p in (base / "laeufe").glob("*/bericht.json")])
    _write_import_dir(tmp_path, status="Fehler – nicht übernehmbar", fehler=2)
    at = AppTest.from_function(_datenimport, default_timeout=TIMEOUT).run()
    assert not at.exception, at.exception
    ok = [b for b in at.button if b.label.startswith("✓ Übernehmen")][0]
    assert "Neue Fassung mit Fehlern" in _texts(at) and ok.disabled
