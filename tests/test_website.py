"""Öffentliche Website (Version 0.17): Testfälle W1–W13 aus docs/08_Website.md, Abschnitt 8.

Ohne Netz, ohne Streamlit. Feste kleine Spielpläne (Hilfen aus test_anzeige.py), die echten Saisonlisten 2026/27
(tests/referenz/api) und – wenn vorhanden – die echten Excel-Dateien.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from types import SimpleNamespace

import pytest
from conftest import REAL_DATABASE, REAL_FIXTURES
from test_anzeige import game, plan, real_plan, rnd

from core import anzeige as A
from core.kpis import LIGHT, NONE, STRONG
from website import einstellungen as W
from website import format as F
from website import seiten, spieltag, vorschau
from website.daten import Zeitpunkt, letzter_import, zeitreise
from website.texte import roh, t, tn

S = "2026/2027"


# --- Hilfen -----------------------------------------------------------------------------------------------

def kpi(anomalie=NONE, abw=5.0, vorl=False):
    from decimal import Decimal
    return SimpleNamespace(anomalie=anomalie, abweichung_rund=None if abw is None else Decimal(str(abw)), vorlaeufig=vorl)


def match(**werte):
    """MatchKpis-Ersatz: alle 8 Kennzahlen „ohne“, einzelne überschreibbar (kpi03=kpi(STRONG, 44))."""
    keys = ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08", "kpi09")
    return SimpleNamespace(**{k: werte.get(k, kpi()) for k in keys})


class FakeDaten:
    """Daten-Ersatz für spieltag_daten: ein Spielplan je Liga, KPIs je Spiel (nach Heimteam), Ergebnisse."""

    def __init__(self, plaene: dict, kpis: dict | None = None, ergebnisse: dict | None = None, gesperrt=False):
        self.plaene, self._kpis, self._erg = plaene, kpis or {}, ergebnisse or {}
        self.gesperrt = gesperrt

    def bestand(self):
        fx = SimpleNamespace(leagues=self.plaene, has_errors=self.gesperrt)
        return SimpleNamespace(gesperrt=self.gesperrt, fx=fx, team_ids={})

    def ergebnisse(self, liga, bis):
        return self._erg

    def kpis(self, liga, saison, md, bis):
        f = self.plaene[liga]
        games = f[(f["saison"] == saison) & (f["spieltag"] == md)]
        return {int(g.reihenfolge): self._kpis.get(g.heim, match()) for g in games.itertuples()}

    def zeitpunkt(self):
        return Zeitpunkt(datetime(2026, 11, 16, 10, 0), datetime(2026, 11, 16, 4, 5), None)


def zp(text: str, import_alter: int = 0) -> Zeitpunkt:
    jetzt = datetime.fromisoformat(text)
    return Zeitpunkt(jetzt, datetime.combine(jetzt.date() - timedelta(days=import_alter), datetime.min.time()), None)


BL = W.liga_aus_slug("bundesliga")


# --- W1 Formate -------------------------------------------------------------------------------------------

def test_w1_formats():
    assert F.tag(date(2026, 11, 21)) == "Sa 21.11." and F.tag_jahr(date(2027, 1, 8)) == "Fr 08.01.2027"
    assert F.prozent(47.36) == "+47,36 %" and F.prozent(-22.07) == "−22,07 %" and F.prozent(0) == "0,00 %"
    assert F.prozent(5) == "+5,00 %" and F.prozent(None) == "–"
    assert F.ergebnis(2, 1) == "2 : 1"
    assert F.zeitraum(date(2026, 11, 20), date(2026, 11, 22)) == "20.11. – 22.11.2026"
    assert F.zeitraum(date(2026, 11, 20), date(2026, 11, 20)) == "20.11.2026"
    assert F.zeitraum(date(2026, 12, 28), date(2027, 1, 3)) == "28.12.2026 – 03.01.2027"
    assert F.stand(datetime(2026, 11, 16, 4, 5)) == "Mo 16.11.2026, 04:05 Uhr" and F.stand(None) == "–"
    assert F.wochenende(date(2027, 2, 6)) == "06./07.02." and F.wochenende(date(2026, 10, 31)) == "31.10./01.11."
    assert F.wochenende(date(2027, 1, 12)) is None


# --- W2–W4 Einstufung, Sortierung, Zählung --------------------------------------------------------------------

def _row(**kw):
    return next(A.prepare(plan(game(1, date(2026, 11, 21), **kw))).itertuples())


@pytest.mark.parametrize("kw, kpis, erg, art", [
    ({"status": "verschoben"}, match(kpi03=kpi(STRONG, 50)), {}, "status"),
    ({}, match(kpi03=kpi(STRONG, 50)), {(S, "A", "B"): (2, 1)}, "gespielt"),          # Ergebnis vor Stufe
    ({}, match(**{k: kpi(STRONG, 50, vorl=True) for k in ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07",
                                                            "kpi08", "kpi09")}), {}, "nicht_gewertet"),
    ({}, None, {}, "nicht_gewertet"),
    ({}, match(**{k: kpi(abw=None) for k in ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08",
                                              "kpi09")}), {}, "nicht_gewertet"),  # Aufsteiger ohne Werte
    ({}, match(kpi03=kpi(STRONG, 44), kpi05=kpi(LIGHT, 60)), {}, "stark"),          # stark vor leicht
    ({}, match(kpi05=kpi(LIGHT, -18)), {}, "leicht"),
    ({}, match(kpi03=kpi(STRONG, 44, vorl=True), kpi05=kpi(LIGHT, 18)), {}, "leicht"),  # vorläufig zählt nicht
    ({}, match(), {}, "ohne"),
])
def test_w2_classification(kw, kpis, erg, art):
    r = spieltag.einstufen(_row(**kw), kpis, datetime(2026, 11, 20, 10, 0), erg)
    assert r["art"] == art


def test_w2_kickoff_passed_without_result_and_strongest():
    row = _row()
    assert spieltag.einstufen(row, match(), datetime(2026, 11, 21, 15, 30), {}) == \
        {"art": "gespielt", "status": None, "ergebnis": None, "staerkste": None}            # „Ergebnis folgt“
    r = spieltag.einstufen(row, match(kpi03=kpi(STRONG, 44), kpi06=kpi(STRONG, -52)), datetime(2026, 11, 20), {})
    assert r["staerkste"] == {"kpi": "kpi06", "abweichung": -52.0}


def test_w3_w4_sorting_counting_and_catchup_at_end():
    fx = plan(game(10, date(2026, 11, 20), "20:30", "A", "B"), game(10, date(2026, 11, 21), "15:30", "C", "D"),
              game(10, date(2026, 11, 21), "15:30", "E", "F"), game(10, date(2026, 11, 21), "18:30", "G", "H"),
              game(10, date(2026, 11, 22), "15:30", "I", "J", status="verschoben"),
              game(10, date(2026, 11, 22), "17:30", "K", "L"), game(10, date(2026, 11, 22), "19:30", "M", "N"),
              game(1, date(2026, 11, 22), "20:30", "O", "P", hint="Nachholspiel"))
    kpis = {"C": match(kpi05=kpi(LIGHT, 18)), "E": match(kpi03=kpi(STRONG, 41)), "G": match(kpi03=kpi(STRONG, -60)),
            "K": match(**{k: kpi(vorl=True) for k in ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08",
                                                      "kpi09")}),
            "O": match(kpi02=kpi(LIGHT, 22))}
    s = spieltag.spieltag_daten(FakeDaten({"Bundesliga": fx}, kpis, {(S, "A", "B"): (2, 1)}), BL,
                                zp("2026-11-21T10:00"))
    tab = s["tabs"][0]
    assert [(x["heim"], x["art"]) for x in tab["spiele"]] == [
        ("G", "stark"), ("E", "stark"), ("C", "leicht"), ("M", "ohne"), ("K", "nicht_gewertet"), ("I", "status"),
        ("A", "gespielt"), ("O", "leicht")]                                 # Nachholspiel am Ende (Annahme A2)
    assert (tab["partien"], tab["auffaellig"], tab["sonderspiele"]) == (7, 4, {"nachholspiel": 1, "vorgezogen": 0})
    assert tab["spiele"][6]["ergebnis"] == [2, 1] and tab["spiele"][7]["sonderspiel"] == "nachholspiel"
    assert not tab["spiele"][5]["link"] or tab["spiele"][5]["id"] is None              # verschoben: kein Link
    html = seiten.spieltag_html(s, seiten.Kontext())
    assert "10. Spieltag</b> · 20.11. – 22.11.2026 · 7 Partien · 4 mit Auffälligkeit · plus 1 Nachholspiel" in html


def test_w4_no_anomalies_sentence_and_plural():
    s = spieltag.spieltag_daten(FakeDaten({"Bundesliga": plan(rnd(10, date(2026, 11, 20), date(2026, 11, 22)))}), BL,
                                zp("2026-11-16T10:00"))
    html = seiten.spieltag_html(s, seiten.Kontext())
    assert "keine mit Auffälligkeit" in html and t("spieltag.keine_abweichungen") in html and "2 Partien" in html
    assert tn("spieltag.partien", 1) == "1 Partie" and tn("spieltag.nachholspiel", 2) == "plus 2 Nachholspiele"
    assert tn("spieltag.vorgezogen", 1) == "plus 1 vorgezogenes Spiel"


# --- W5–W7 Nachholspiel, englische Woche, Pausen ---------------------------------------------------------------

def test_w5_catchup_goes_to_tab_of_its_dates():
    fx = plan(rnd(12, date(2026, 12, 5)), rnd(13, date(2026, 12, 8), date(2026, 12, 9)),
              game(1, date(2026, 12, 9), "18:30", "E", "F", hint="Nachholspiel"),
              game(23, date(2026, 12, 3), "21:00", "G", "H", hint="vorgezogen"))
    s = spieltag.spieltag_daten(FakeDaten({"Bundesliga": fx}), BL, zp("2026-12-03T10:00"))
    assert [t_["spieltag"] for t_ in s["tabs"]] == [12, 13]
    assert [x["heim"] for x in s["tabs"][1]["spiele"]][-1] == "E"        # Nachholspiel im Tab seines Zeitraums
    assert [x["heim"] for x in s["tabs"][0]["spiele"]][-1] == "G"        # ausserhalb: im ersten Tab
    assert s["tabs"][0]["sonderspiele"] == {"nachholspiel": 0, "vorgezogen": 1}


def test_w6_english_week_tabs_markup():
    fx = plan(rnd(12, date(2026, 12, 5)), rnd(13, date(2026, 12, 8), date(2026, 12, 9)))
    s = spieltag.spieltag_daten(FakeDaten({"Bundesliga": fx}), BL, zp("2026-12-05T10:00"))
    html = seiten.spieltag_html(s, seiten.Kontext())
    assert "12. Spieltag · ab 05.12." in html and "13. Spieltag · ab 08.12." in html
    assert html.count('aria-pressed="true"') == 1 and 'class="tabs" role="group"' in html and " hidden>" in html
    assert html.count("data-panel") == 2 and "site.js" in html                      # ohne JS: beide sichtbar


@pytest.mark.parametrize("now, art, titel", [
    ("2026-12-23T10:00", "winterpause", "Nächster Spieltag am Fr 08.01."),
    ("2026-09-08T10:00", "spielpause", "Nächster Spieltag am Fr 25.09."),
    ("2027-06-10T10:00", "sommerpause", "Die Saison ist beendet"),
])
def test_w7_pause_cards(now, art, titel):
    fx = plan(rnd(3, date(2026, 8, 28)), rnd(4, date(2026, 9, 4), date(2026, 9, 6)), rnd(5, date(2026, 9, 25)),
              rnd(14, date(2026, 12, 18), date(2026, 12, 20)), rnd(15, date(2027, 1, 8), date(2027, 1, 10)),
              rnd(34, date(2027, 5, 22)))
    s = spieltag.spieltag_daten(FakeDaten({"Bundesliga": fx}), BL, zp(now))
    assert s["zustand"] == "pause" and s["pause"]["art"] == art and s["tabs"] == []
    html = seiten.spieltag_html(s, seiten.Kontext())
    assert titel in html and 'class="partien"' not in html and t(f"pause.{art}.zeile") in html
    assert "In der Bundesliga ruht" in html or art == "sommerpause"


def test_w7_season_start_and_list_from_fourteen_days():
    fx = plan(rnd(34, date(2027, 5, 22)), rnd(1, date(2027, 8, 20), date(2027, 8, 22), saison="2027/2028"))
    s = spieltag.spieltag_daten(FakeDaten({"Bundesliga": fx}), BL, zp("2027-07-01T10:00"))
    assert s["pause"]["art"] == "saisonstart"
    assert "Saisonstart am Fr 20.08." in seiten.spieltag_html(s, seiten.Kontext())
    s = spieltag.spieltag_daten(FakeDaten({"Bundesliga": fx}), BL, zp("2027-08-06T10:00"))
    assert s["zustand"] == "liste" and s["tabs"][0]["spieltag"] == 1


# --- W8 Datenstand ---------------------------------------------------------------------------------------------

def test_w8_stale_warning_keeps_list_and_shows_import_date():
    fx = plan(rnd(10, date(2026, 11, 20), date(2026, 11, 22)))
    jetzt = datetime(2026, 11, 16, 10, 0)
    for alter, veraltet in ((3, False), (4, True)):
        z = Zeitpunkt(jetzt, datetime(2026, 11, 16 - alter, 4, 5), None)
        s = spieltag.spieltag_daten(FakeDaten({"Bundesliga": fx}), BL, z)
        html = seiten.spieltag_html(s, seiten.Kontext())
        assert s["veraltet"] is veraltet and ('role="alert"' in html) is veraltet and 'class="partien"' in html
    assert "Spielplan zuletzt aktualisiert am Do 12.11." in html
    assert "Aktueller Datenstand: Do 12.11.2026" in html and "Stand: Do 12.11.2026, 04:05 Uhr" in html


def test_w8_last_import_reads_only_successful_runs(tmp_path):
    for lauf, status, start in (("2026-11-15_040000", "übernommen", "2026-11-15T04:00:07+01:00"),
                                ("2026-11-16_040000", "fehlgeschlagen", "2026-11-16T04:00:03+01:00")):
        (tmp_path / "laeufe" / lauf).mkdir(parents=True)
        (tmp_path / "laeufe" / lauf / "bericht.json").write_text(json.dumps({"status": status, "start": start}))
    assert letzter_import(tmp_path) == datetime(2026, 11, 15, 4, 0, 7)
    assert letzter_import(tmp_path / "fehlt") is None


# --- W9 Zeitreise ----------------------------------------------------------------------------------------------

def test_w9_time_travel_parsing():
    echt = Zeitpunkt(datetime(2026, 11, 16, 10, 0), datetime(2026, 11, 16, 4, 5), None)
    z, bad = zeitreise("2026-10-03", echt)
    assert (z.jetzt, z.stand, z.bis, z.zeitreise, bad) == (datetime(2026, 10, 3, 8, 0), datetime(2026, 10, 3, 4, 0),
                                                           date(2026, 10, 3), True, False)
    z, _ = zeitreise("2026-10-03T16:30", echt)
    assert z.jetzt == datetime(2026, 10, 3, 16, 30) and z.bis == date(2026, 10, 3)
    z, _ = zeitreise("2026-10-03T02:00", echt)                     # vor dem Import: Stand vom Vortag
    assert z.bis == date(2026, 10, 2) and z.stand == datetime(2026, 10, 2, 4, 0)
    for falsch in ("2026-02-30", "03.10.2026", "x", "2026-10-03T25:00"):
        assert zeitreise(falsch, echt) == (echt, True)
    assert zeitreise(None, echt) == (echt, False) and zeitreise("", echt) == (echt, False)


def test_w9_links_carry_date_and_results_filtered(monkeypatch):
    k = seiten.Kontext(datum="2026-10-03T16:30")
    assert k.url("/spieltag/la-liga") == "/vorschau/spieltag/la-liga?datum=2026-10-03T16%3A30"
    assert seiten.Kontext().url("/spiel/5") == "/vorschau/spiel/5" and k.statisch("site.css") == "/vorschau/statisch/site.css"
    import pandas as pd
    from website.daten import Daten
    d = Daten(import_dir=None)
    prepared = pd.DataFrame({"date": [date(2026, 10, 2), date(2026, 10, 3)], "season": [S, S], "home": ["A", "C"],
                             "away": ["B", "D"], "hg": [1.0, 2.0], "ag": [0.0, 2.0]})
    monkeypatch.setattr(d, "bestand", lambda: SimpleNamespace(prepared={"Bundesliga": prepared}))
    assert d.ergebnisse("Bundesliga", date(2026, 10, 3)) == {(S, "A", "B"): (1, 0)}
    assert len(d.ergebnisse("Bundesliga", None)) == 2


# --- W10 Texte -------------------------------------------------------------------------------------------------

def test_w10_every_template_key_exists_and_eszett():
    keys = set()
    for vorlage in W.VORLAGEN.glob("*.html"):
        keys |= set(re.findall(r"\bt\('([a-z_.]+)'\s*[,)]", vorlage.read_text(encoding="utf-8")))   # feste Schlüssel
    keys |= {f"chip.{s}" for s in ("verschoben", "abgesagt", "abgebrochen", "ausgesetzt", "gewertet", "stark", "leicht",
                                   "nachholspiel", "vorgezogen", "nicht_gewertet", "ergebnis_folgt")}
    keys |= {f"pause.{a}.{f}" for a in ("spielpause", "winterpause", "sommerpause", "saisonstart", "unbekannt", "keine")
             for f in ("zeile", "titel", "text")}
    keys |= {f"liga.{lg.key}" for lg in W.LIGEN}
    for key in keys:
        assert isinstance(roh(key), str), key
    texte = json.dumps(json.loads((W.TEXTE / "de.json").read_text(encoding="utf-8")), ensure_ascii=False)
    assert "Weiße" in texte and "Weisse" not in texte                              # T5: ß
    with pytest.raises(KeyError):
        t("gibt.es.nicht")


def test_w10_everything_escaped():
    fx = plan(game(10, date(2026, 11, 20), "20:30", "<script>x</script>", "B&B"))
    html = seiten.spieltag_html(spieltag.spieltag_daten(FakeDaten({"Bundesliga": fx}), BL, zp("2026-11-16T10:00")),
                                seiten.Kontext())
    assert "<script>x" not in html and "&lt;script&gt;x&lt;/script&gt;" in html and "B&amp;B" in html


# --- W11 Vorschau-Dienst -------------------------------------------------------------------------------------------

@pytest.fixture
def dienst():
    fx = plan(rnd(10, date(2026, 11, 20), date(2026, 11, 22)), game(10, date(2026, 11, 21), "18:30", "E", "F"))
    fx.loc[fx["heim"] == "E", "api_id"] = 1388512
    return FakeDaten({"Bundesliga": fx})


def test_w11_routes(dienst):
    a = vorschau.beantworten("/vorschau/", "", dienst)
    assert a.status == 302 and a.kopf["Location"] == "/vorschau/spieltag/bundesliga"
    a = vorschau.beantworten("/vorschau", "datum=2026-10-03", dienst)
    assert a.kopf["Location"] == "/vorschau/spieltag/bundesliga?datum=2026-10-03"
    a = vorschau.beantworten("/vorschau/spieltag/bundesliga", "", dienst)
    assert a.status == 200 and a.kopf["Content-Type"].startswith("text/html") and b"Alle Spiele im" in a.inhalt
    assert b'href="/vorschau/spiel/1388512"' in a.inhalt and a.kopf["Cache-Control"] == "no-store"
    a = vorschau.beantworten("/vorschau/spieltag/la-liga", "", dienst)              # Liga ohne Spielplan
    assert a.status == 200 and t("pause.keine.titel").encode() in a.inhalt
    assert vorschau.beantworten("/vorschau/spieltag/zweite-liga", "", dienst).status == 404
    assert vorschau.beantworten("/anders", "", dienst).status == 404
    assert vorschau.beantworten("/vorschau/spiel/1388512", "", dienst).status == 200      # folgt mit 0.18
    assert vorschau.beantworten("/vorschau/impressum", "", dienst).status == 200
    assert vorschau.beantworten("/vorschau/_gesund", "", dienst).inhalt == b"ok"
    daten = json.loads(vorschau.beantworten("/vorschau/daten/spieltag/bundesliga.json", "", dienst).inhalt)
    assert daten["seite"] == "spieltag" and daten["tabs"][0]["spieltag"] == 10


def test_w11_static_files_only_from_own_folder(dienst):
    a = vorschau.beantworten("/vorschau/statisch/site.css", "", dienst)
    assert a.status == 200 and a.kopf["Content-Type"].startswith("text/css")
    a = vorschau.beantworten("/vorschau/statisch/schriften/inter-latin-wght-normal.woff2", "", dienst)
    assert a.status == 200 and a.kopf["Content-Type"] == "font/woff2" and "max-age=2592000" in a.kopf["Cache-Control"]
    for pfad in ("/vorschau/statisch/../vorschau.py", "/vorschau/statisch/../../core/settings.py",
                 "/vorschau/statisch/fehlt.css", "/vorschau/statisch/"):
        assert vorschau.beantworten(pfad, "", dienst).status == 404, pfad
    assert "script-src 'self'" in vorschau.SICHERHEIT["Content-Security-Policy"]


def test_w11_invalid_date_and_time_travel_bar(dienst):
    a = vorschau.beantworten("/vorschau/spieltag/bundesliga", "datum=morgen", dienst)
    assert a.status == 200 and t("vorschau.ungueltig").encode() in a.inhalt
    a = vorschau.beantworten("/vorschau/spieltag/bundesliga", "datum=2026-11-21T16:00", dienst)
    html = a.inhalt.decode()
    assert "Zeitreise: Sa 21.11.2026, 16:00 Uhr" in html and 'value="2026-11-21T16:00"' in html
    assert "?datum=2026-11-21T16%3A00" in html and 'name="robots" content="noindex, nofollow"' in html


def test_w11_data_errors_show_notice():
    fx = plan(rnd(10, date(2026, 11, 20)))
    a = vorschau.beantworten("/vorschau/spieltag/bundesliga", "", FakeDaten({"Bundesliga": fx}, gesperrt=True))
    assert a.status == 200 and t("fehler.daten_titel").encode() in a.inhalt and b'class="partien"' not in a.inhalt


# --- W13 Echte Saisonlisten und echte Dateien ----------------------------------------------------------------------

@pytest.mark.parametrize("liga, slug", [("bundesliga", "bundesliga"), ("laliga", "la-liga"),
                                        ("premier_league", "premier-league"), ("serie_a", "serie-a")])
def test_w13_real_season_lists_all_dates(liga, slug):
    web = W.liga_aus_slug(slug)
    for offset in range(0, 280, 9):
        tag = date(2026, 8, 10) + timedelta(days=offset)
        fx = real_plan(liga, tag)
        s = spieltag.spieltag_daten(FakeDaten({web.name: fx}), web, zp(f"{tag}T10:00"))
        html = seiten.spieltag_html(s, seiten.Kontext())
        assert s["zustand"] in ("liste", "pause") and "</html>" in html, (liga, tag)
        if s["zustand"] == "liste":
            assert all(tab["spiele"] for tab in s["tabs"]), (liga, tag)


def test_w13_real_laliga_early_games_in_first_tab():
    web = W.liga_aus_slug("la-liga")
    s = spieltag.spieltag_daten(FakeDaten({web.name: real_plan("laliga", date(2026, 12, 1))}), web, zp("2026-12-01T10:00"))
    tab = s["tabs"][0]
    assert tab["spieltag"] == 15 and tab["sonderspiele"]["vorgezogen"] == 2 and tab["partien"] == 10
    assert [x["sonderspiel"] for x in tab["spiele"][-2:]] == ["vorgezogen", "vorgezogen"]


@pytest.mark.skipif(not (REAL_DATABASE.exists() and REAL_FIXTURES.exists()), reason="echte Dateien nicht vorhanden")
def test_w13_real_files_all_leagues():
    from website.daten import Daten
    d = Daten()
    echt = d.zeitpunkt()
    for text in (None, "2026-11-21T16:00", "2026-12-23", "2027-01-09"):
        z, _ = zeitreise(text, echt)
        for web in W.LIGEN:
            s = spieltag.spieltag_daten(d, web, z)
            assert "</html>" in seiten.spieltag_html(s, seiten.Kontext()), (web.slug, text)
