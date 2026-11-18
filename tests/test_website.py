"""Öffentliche Website (seit Version 0.17): Testfälle W1–W16 aus docs/08_Website.md, Abschnitt 8.

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
from core.kpis import HIGH, MEDIUM, NONE
from website import einstellungen as W
from website import format as F
from website import seiten, spiel, spieltag, start, vorschau
from website.daten import Zeitpunkt, letzter_import, zeitreise
from website.texte import roh, t, tn

S = "2026/2027"


# --- Hilfen -----------------------------------------------------------------------------------------------

def kpi(anomalie=NONE, abw=5.0, vorl=False, wert=1.5, heim=1.4, gast=1.6, ref=1.43, prozent=False):
    """KpiResult-Ersatz mit den Feldern, die Spieltag und Matchdetail lesen (gerundete Werte als Decimal)."""
    from decimal import Decimal

    def dez(x):
        return None if x is None else Decimal(str(x))
    return SimpleNamespace(anomalie=anomalie, abweichung_rund=dez(abw), vorlaeufig=vorl, hauptwert_rund=dez(wert),
                           heim=SimpleNamespace(wert_rund=dez(heim)), auswaerts=SimpleNamespace(wert_rund=dez(gast)),
                           referenz=None if ref is None else SimpleNamespace(wert_rund=dez(ref)), prozent=prozent)


KPI_KEYS = ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08", "kpi09")


def match(form_home=None, form_away=None, **werte):
    """MatchKpis-Ersatz: alle 8 Kennzahlen „ohne“, einzelne überschreibbar (kpi03=kpi(HIGH, 44))."""
    return SimpleNamespace(**{k: werte.get(k, kpi()) for k in KPI_KEYS},
                           form_home=None if form_home is None else SimpleNamespace(form=list(form_home)),
                           form_away=None if form_away is None else SimpleNamespace(form=list(form_away)))


class FakeDaten:
    """Daten-Ersatz für spieltag_daten, spiel_daten und start_daten: ein Spielplan je Liga, KPIs je Spiel (nach
    Heimteam), Ergebnisse."""

    def __init__(self, plaene: dict, kpis: dict | None = None, ergebnisse: dict | None = None, gesperrt=False):
        self.plaene, self._kpis, self._erg = plaene, kpis or {}, ergebnisse or {}
        self.gesperrt = gesperrt
        self._plan_cache = {}

    def bestand(self):
        fx = SimpleNamespace(leagues=self.plaene, has_errors=self.gesperrt)
        return SimpleNamespace(gesperrt=self.gesperrt, fx=fx, team_ids={}, leagues=dict.fromkeys(self.plaene))

    def spielplan(self, liga):
        if liga not in self.plaene:
            return None
        if liga not in self._plan_cache:
            self._plan_cache[liga] = A.prepare(self.plaene[liga])
        return self._plan_cache[liga]

    def spiel(self, spiel_id):
        for liga in self.plaene:
            for row in self.spielplan(liga).itertuples():
                if row.api_id is not None and row.api_id == row.api_id and int(row.api_id) == int(spiel_id):
                    return liga, row
        return None

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
    ({"status": "verschoben"}, match(kpi03=kpi(HIGH, 50)), {}, "status"),
    ({}, match(kpi03=kpi(HIGH, 50)), {(S, "A", "B"): (2, 1)}, "gespielt"),          # Ergebnis vor Stufe
    ({}, match(**{k: kpi(HIGH, 50, vorl=True) for k in ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07",
                                                            "kpi08", "kpi09")}), {}, "nicht_gewertet"),
    ({}, None, {}, "nicht_gewertet"),
    ({}, match(**{k: kpi(abw=None) for k in ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08",
                                              "kpi09")}), {}, "nicht_gewertet"),  # Aufsteiger ohne Werte
    ({}, match(kpi03=kpi(HIGH, 44), kpi05=kpi(MEDIUM, 60)), {}, "hoch"),          # stark vor leicht
    ({}, match(kpi05=kpi(MEDIUM, -18)), {}, "mittel"),
    ({}, match(kpi03=kpi(HIGH, 44, vorl=True), kpi05=kpi(MEDIUM, 18)), {}, "mittel"),  # vorläufig zählt nicht
    ({}, match(), {}, "ohne"),
])
def test_w2_classification(kw, kpis, erg, art):
    r = spieltag.einstufen(_row(**kw), kpis, datetime(2026, 11, 20, 10, 0), erg)
    assert r["art"] == art


def test_w2_kickoff_passed_without_result_and_strongest():
    row = _row()
    assert spieltag.einstufen(row, match(), datetime(2026, 11, 21, 15, 30), {}) == \
        {"art": "gespielt", "status": None, "ergebnis": None, "staerkste": None}            # „Ergebnis folgt“
    r = spieltag.einstufen(row, match(kpi03=kpi(HIGH, 44), kpi06=kpi(HIGH, -52)), datetime(2026, 11, 20), {})
    assert r["staerkste"] == {"kpi": "kpi06", "abweichung": -52.0}


def test_w3_w4_sorting_counting_catchup_mixed_in():
    fx = plan(game(10, date(2026, 11, 20), "20:30", "A", "B"), game(10, date(2026, 11, 21), "15:30", "C", "D"),
              game(10, date(2026, 11, 21), "15:30", "E", "F"), game(10, date(2026, 11, 21), "18:30", "G", "H"),
              game(10, date(2026, 11, 22), "15:30", "I", "J", status="verschoben"),
              game(10, date(2026, 11, 22), "17:30", "K", "L"), game(10, date(2026, 11, 22), "19:30", "M", "N"),
              game(1, date(2026, 11, 22), "20:30", "O", "P", hint="Nachholspiel"))
    kpis = {"C": match(kpi05=kpi(MEDIUM, 18)), "E": match(kpi03=kpi(HIGH, 41)), "G": match(kpi03=kpi(HIGH, -60)),
            "K": match(**{k: kpi(vorl=True) for k in ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08",
                                                      "kpi09")}),
            "O": match(kpi02=kpi(MEDIUM, 22))}
    s = spieltag.spieltag_daten(FakeDaten({"Bundesliga": fx}, kpis, {(S, "A", "B"): (2, 1)}), BL,
                                zp("2026-11-21T10:00"))
    tab = s["tabs"][0]
    # Seit 0.18 nach Entwurf 3d: Nachholspiel mitsortiert (O leicht vor C leicht: 22 > 18); nicht gewertet, Status
    # und gespielt in einer Gruppe nach Anstoss (A Fr 20:30, I So 15:30, K So 17:30)
    assert [(x["heim"], x["art"]) for x in tab["spiele"]] == [
        ("G", "hoch"), ("E", "hoch"), ("O", "mittel"), ("C", "mittel"), ("M", "ohne"), ("A", "gespielt"),
        ("I", "status"), ("K", "nicht_gewertet")]
    assert (tab["partien"], tab["auffaellig"], tab["sonderspiele"]) == (7, 4, {"nachholspiel": 1, "vorgezogen": 0})
    assert tab["spiele"][5]["ergebnis"] == [2, 1] and tab["spiele"][2]["sonderspiel"] == "nachholspiel"
    assert not tab["spiele"][6]["link"]                                                   # verschoben: kein Link
    html = seiten.spieltag_html(s, seiten.Kontext())
    assert "10. Spieltag · 20.11. – 22.11.2026 · 7 Partien · 4 mit Auffälligkeit · plus 1 Nachholspiel" in html


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
    assert [x["heim"] for x in s["tabs"][0]["spiele"]][0] == "G"         # ausserhalb: im ersten Tab, nach Anstoss
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
    for lauf, status, beginn in (("2026-11-15_040000", "übernommen", "2026-11-15T04:00:07+01:00"),
                                 ("2026-11-16_040000", "fehlgeschlagen", "2026-11-16T04:00:03+01:00")):
        (tmp_path / "laeufe" / lauf).mkdir(parents=True)
        (tmp_path / "laeufe" / lauf / "bericht.json").write_text(json.dumps({"status": status, "start": beginn}))
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
    keys |= {f"chip.{s}" for s in ("verschoben", "abgesagt", "abgebrochen", "ausgesetzt", "gewertet", "hoch", "mittel",
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
    a = vorschau.beantworten("/vorschau/", "", dienst)                              # seit 0.18: Startseite
    assert a.status == 200 and t("start.ranking_titel").encode() in a.inhalt
    a = vorschau.beantworten("/vorschau", "datum=2026-10-03", dienst)
    assert a.status == 200 and b"Zeitreise: Sa 03.10.2026, 08:00 Uhr" in a.inhalt
    a = vorschau.beantworten("/vorschau/spieltag/", "datum=2026-10-03", dienst)
    assert a.status == 302 and a.kopf["Location"] == "/vorschau/spieltag/bundesliga?datum=2026-10-03"
    a = vorschau.beantworten("/vorschau/spieltag/bundesliga", "", dienst)
    assert a.status == 200 and a.kopf["Content-Type"].startswith("text/html") and b"Alle Spiele im" in a.inhalt
    assert b'href="/vorschau/spiel/1388512"' in a.inhalt and a.kopf["Cache-Control"] == "no-store"
    a = vorschau.beantworten("/vorschau/spieltag/la-liga", "", dienst)              # Liga ohne Spielplan
    assert a.status == 200 and t("pause.keine.titel").encode() in a.inhalt
    assert vorschau.beantworten("/vorschau/spieltag/zweite-liga", "", dienst).status == 404
    assert vorschau.beantworten("/anders", "", dienst).status == 404
    a = vorschau.beantworten("/vorschau/spiel/1388512", "", dienst)                 # Matchdetail (seit 0.18)
    assert a.status == 200 and b'<div class="sb-name">E</div>' in a.inhalt and b'<div class="sb-name">F</div>' in a.inhalt
    assert t("kopf.zurueck_spieltag").encode() in a.inhalt and b'href="/vorschau/spieltag/bundesliga"' in a.inhalt
    for falsch in ("/vorschau/spiel/999", "/vorschau/spiel/abc", "/vorschau/spiel/1388512/x"):
        assert vorschau.beantworten(falsch, "", dienst).status == 404, falsch
    assert vorschau.beantworten("/vorschau/impressum", "", dienst).status == 200
    assert vorschau.beantworten("/vorschau/_gesund", "", dienst).inhalt == b"ok"
    daten = json.loads(vorschau.beantworten("/vorschau/daten/spieltag/bundesliga.json", "", dienst).inhalt)
    assert daten["seite"] == "spieltag" and daten["tabs"][0]["spieltag"] == 10
    daten = json.loads(vorschau.beantworten("/vorschau/daten/start.json", "", dienst).inhalt)
    assert daten["seite"] == "start" and daten["zustand"] == "keine"
    a = vorschau.beantworten("/vorschau/daten/spiel/1388512.json", "", dienst)
    assert a.kopf["Content-Type"].startswith("application/json") and json.loads(a.inhalt)["heim"] == "E"
    assert vorschau.beantworten("/vorschau/daten/spiel/999.json", "", dienst).status == 404


def test_w11_photo_only_from_server_folder(dienst, tmp_path, monkeypatch):
    """Q6: Das Foto liegt nur auf dem Server (website-bilder/); fehlt es, zeigt die Startseite den Platzhalter."""
    monkeypatch.setattr(W, "BILDER", tmp_path)
    html = vorschau.beantworten("/vorschau/", "", dienst).inhalt.decode()
    assert 'class="foto-platz"' in html and "<img" not in html
    assert vorschau.beantworten("/vorschau/bilder/portrait.jpg", "", dienst).status == 404
    (tmp_path / "portrait.jpg").write_bytes(b"\xff\xd8\xff\xe0jpeg")
    html = vorschau.beantworten("/vorschau/", "", dienst).inhalt.decode()
    assert '<img src="/vorschau/bilder/portrait.jpg"' in html and 'class="foto-platz"' not in html
    a = vorschau.beantworten("/vorschau/bilder/portrait.jpg", "", dienst)
    assert a.status == 200 and a.kopf["Content-Type"] == "image/jpeg" and a.inhalt.startswith(b"\xff\xd8")
    for falsch in ("/vorschau/bilder/../einstellungen.py", "/vorschau/bilder/anders.jpg"):
        assert vorschau.beantworten(falsch, "", dienst).status == 404, falsch


def test_w11_preload_fills_cache_and_never_raises(dienst, capsys):
    vorschau.vorladen(dienst)
    assert "vorgeladen" in capsys.readouterr().out
    kaputt = SimpleNamespace(zeitpunkt=lambda: (_ for _ in ()).throw(OSError("weg")))
    vorschau.vorladen(kaputt)                                                         # meldet nur, bricht nicht ab
    assert "OSError" in capsys.readouterr().err


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


# --- W14 Matchdetail (seit 0.18, Entwurf 2i, Entscheidungen Q1–Q5) -----------------------------------------------

@pytest.fixture
def partien():
    """Spieltag 10 mit je einer Partie pro Zustand; Spiel-IDs 101–105."""
    fx = plan(game(10, date(2026, 11, 21), "15:30", "A", "B"),                    # 101 auffällig
              game(10, date(2026, 11, 21), "18:30", "C", "D"),                    # 102 nicht gewertet, ohne Werte
              game(10, date(2026, 11, 22), "15:30", "E", "F", status="verschoben"),   # 103 Status
              game(1, date(2026, 11, 22), "17:30", "G", "H", hint="Nachholspiel"),    # 104 normal, Nachholspiel
              game(10, date(2026, 11, 20), "20:30", "I", "J"))                    # 105 gespielt 2 : 1
    fx["api_id"] = [101, 102, 103, 104, 105]
    kpis = {"A": match(kpi03=kpi(HIGH, 44, wert=3.4, heim=3.2, gast=3.6, ref=None),
                       kpi04=kpi(MEDIUM, -22, wert=3.6, heim=1.4, gast=2.2, ref=4.62),
                       kpi08=kpi(NONE, -8, wert=50, heim=40, gast=60, ref=54.35, prozent=True),
                       kpi05=kpi(HIGH, 70, vorl=True)),
            "C": match(**{k: kpi(abw=None, wert=None, heim=None, gast=None, vorl=True) for k in KPI_KEYS}),
            "E": match(kpi03=kpi(HIGH, 99)),
            "G": match(form_home="SUN-S", form_away="NN---")}
    return FakeDaten({"Bundesliga": fx}, kpis, {(S, "I", "J"): (2, 1)})


def test_w14_values_q1_q2_q4(partien):
    s = spiel.spiel_daten(partien, 101, zp("2026-11-21T10:00"))
    assert (s["seite"], s["id"], s["liga"], s["spieltag"], s["heim"], s["gast"]) == ("spiel", 101, "bundesliga", 10,
                                                                                      "A", "B")
    assert s["zustand"] == "offen" and s["bewertung"] == "auffaellig" and s["anstoss"] == "15:30"
    assert [(k["kpi"], k["stufe"], k["richtung"]) for k in s["auffaellig"]] == [("kpi03", "hoch", "hoch"),
                                                                               ("kpi04", "mittel", "tief")]
    k03, k04 = s["auffaellig"]
    assert (k03["erwartung"], k03["vergleich"], k03["vergleich_art"], k03["summe"]) == (3.4, 2.5, "marke", False)  # Q2
    assert (k04["erwartung"], k04["heim"], k04["gast"], k04["vergleich"], k04["summe"]) == (3.6, 1.4, 2.2, 4.62, True)  # Q1
    k05 = next(k for k in s["uebrige"] if k["kpi"] == "kpi05")                      # Q4: vorläufig, ohne Stufe
    assert k05["stufe"] == "nicht_gewertet" and s["anzahl_gewertet"] == 7
    assert [k["kpi"] for k in s["uebrige"]][0] == "kpi05"                           # nach Betrag (70 > 8 > 5)
    html = seiten.spiel_html(s, seiten.Kontext())
    for text in ("Auffälligstes Merkmal", "+44,00 %", "Über 2,5 Tore", "Mehr als 2,5 Tore erwartet",
                 "Vergleichswert (Marke)", "<b>2,50</b>", "Je Mannschaft · Mittelwert beider Teams", "+ 2,20",
                 'class="w39"', 'class="gast w61"', "Im Normalbereich", '<span class="vermerk">· ', "50,00 %",
                 "54,35 %", "Sa 21.11. · 15:30", "Bundesliga · 10. Spieltag"):
        assert text in html, text
    assert html.count("Je Mannschaft") == 7                                          # alle ausser Gelbe Karten
    assert "Weniger als 2,5 Tore" not in html and t("spiel.hinweis_nicht_gewertet_titel") not in html


def test_w14_not_rated_status_catchup_form(partien):
    z = zp("2026-11-21T10:00")
    s = spiel.spiel_daten(partien, 102, z)                                            # F2: alle vorläufig
    assert s["bewertung"] == "nicht_gewertet" and s["ohne_werte"] and s["auffaellig"] == [] and s["groesste"] is None
    html = seiten.spiel_html(s, seiten.Kontext())
    assert t("spiel.hinweis_nicht_gewertet_leer") in html and t("spiel.nicht_gewertet_leer_text") in html
    assert '<h2 class="h2-klein">Kennzahlen</h2>' in html and 'class="vermerk"' not in html
    s = spiel.spiel_daten(partien, 103, z)                                            # verschoben: keine Werte
    assert (s["zustand"], s["bewertung"], s["status"], s["sonderspiel"]) == ("status", "status", "verschoben", None)
    html = seiten.spiel_html(s, seiten.Kontext())
    assert t("spiel.status_text") in html and 'class="h2-klein"' not in html            # keine Kennzahlen-Listen
    assert t("termin.termin_offen") in html and "+99,00 %" not in html
    s = spiel.spiel_daten(partien, 104, z)
    assert s["bewertung"] == "normal" and s["sonderspiel"] == "nachholspiel" and s["spieltag"] == 1
    assert s["form_heim"] == ["S", "U", "N", "-", "S"] and s["form_gast"] == ["N", "N", "-", "-", "-"]
    html = seiten.spiel_html(s, seiten.Kontext())
    assert "Dieses Spiel gehört zu einem früheren Spieltag und wird am So 22.11. um 17:30 Uhr nachgeholt." in html
    assert "Alle 8 Kennzahlen liegen im Normalbereich. Die größte Abweichung: Erwartete Tore +5,00 %." in html
    assert html.count('class="form-S"') == 2 and html.count('class="form--"') == 4
    assert spiel.spiel_daten(partien, 999, z) is None


def test_w14_played_q5(partien):
    s = spiel.spiel_daten(partien, 105, zp("2026-11-21T10:00"))
    assert s["zustand"] == "gespielt" and s["ergebnis"] == [2, 1]
    html = seiten.spiel_html(s, seiten.Kontext())
    assert "Endstand 2 : 1" in html and "Gespielt:</b> Die Werte wurden vor dem Spiel berechnet." in html
    s = spiel.spiel_daten(partien, 101, zp("2026-11-21T16:00"))                      # Anstoss vorbei, kein Ergebnis
    assert s["zustand"] == "gespielt" and s["ergebnis"] is None and s["bewertung"] == "auffaellig"
    html = seiten.spiel_html(s, seiten.Kontext())
    assert "Ergebnis folgt" in html and "Sa 21.11. · 15:30" not in html and "+44,00 %" in html


def test_w14_every_pairing_has_its_own_page():
    """Wichtig (Carsten 17.11.2026): jede Paarung eines Spieltags hat eine eigene Seite. Echte Saisonliste."""
    for liga, slug, tag in (("laliga", "la-liga", date(2026, 12, 1)), ("bundesliga", "bundesliga", date(2026, 11, 16))):
        web = W.liga_aus_slug(slug)
        fx = real_plan(liga, tag)
        fx["api_id"] = 9_000_000 + fx["reihenfolge"]
        d = FakeDaten({web.name: fx})
        z = zp(f"{tag}T10:00")
        s = spieltag.spieltag_daten(d, web, z)
        html = seiten.spieltag_html(s, seiten.Kontext())
        spiele = [x for tab in s["tabs"] for x in tab["spiele"]]
        assert spiele and len({x["id"] for x in spiele}) == len(spiele)
        for x in spiele:
            m = spiel.spiel_daten(d, x["id"], z)
            assert (m["heim"], m["gast"], m["spieltag"], m["datum"]) == (x["heim"], x["gast"], x["spieltag"],
                                                                         x["datum"])
            assert (f'href="/vorschau/spiel/{x["id"]}"' in html) is x["link"]
            assert "</html>" in seiten.spiel_html(m, seiten.Kontext())
        for row in fx.itertuples():                                               # die ganze Saison
            assert spiel.spiel_daten(d, int(row.api_id), z)["heim"] == row.heim


def test_w14_escaped_and_labels():
    fx = plan(game(10, date(2026, 11, 21), "15:30", "<b>X</b>", "Y&Z"))
    fx["api_id"] = [7]
    html = seiten.spiel_html(spiel.spiel_daten(FakeDaten({"Bundesliga": fx}), 7, zp("2026-11-16T10:00")),
                             seiten.Kontext())
    assert "<b>X</b>" not in html and "&lt;b&gt;X&lt;/b&gt;" in html and "Y&amp;Z" in html


def test_w14_bar_and_number_helpers():
    assert seiten.balken_daten({"abweichung": 44.0, "stufe": "hoch"}) == \
        {"breite": 22, "richtung": "hoch", "klasse": "f-stark-hoch", "kappe": False}
    assert seiten.balken_daten({"abweichung": -130.0, "stufe": "mittel"}) == \
        {"breite": 50, "richtung": "tief", "klasse": "f-leicht-tief", "kappe": True}           # gekappt
    assert seiten.balken_daten({"abweichung": 5.0, "stufe": "normal"})["klasse"] == "f-normal"
    assert seiten.balken_daten({"abweichung": None, "stufe": "nicht_gewertet"})["breite"] == 0
    assert seiten.balken_daten({"abweichung": 70.0, "stufe": "nicht_gewertet"})["klasse"] == "f-schraffiert"
    assert F.zahl(3.4) == "3,40" and F.zahl(64.0, einheit="%") == "64,00 %" and F.zahl(None) == "–"
    assert F.zahl(-0.5) == "−0,50"
    assert seiten.aufteilung({"heim": 1.4, "gast": 2.2}) == 39 and seiten.aufteilung({"heim": 0, "gast": 0}) == 50


# --- W15 Startseite (seit 0.18, Entwurf 1d, F6, Q7) ---------------------------------------------------------------

def _start_daten(**kw):
    bl = plan(game(10, date(2026, 11, 20), "20:30", "A", "B"), game(10, date(2026, 11, 21), "15:30", "C", "D"),
              game(10, date(2026, 11, 21), "18:30", "E", "F"), game(10, date(2026, 11, 22), "15:30", "G", "H"))
    bl["api_id"] = [201, 202, 203, 204]
    ll = plan(game(13, date(2026, 11, 21), "21:00", "K", "L"),
              game(13, date(2026, 11, 22), "18:30", "M", "N", status="verschoben"),
              game(13, date(2026, 11, 22), "21:00", "O", "P"))
    ll["api_id"] = [301, 302, 303]
    kpis = {"A": match(kpi03=kpi(HIGH, 44)), "C": match(kpi05=kpi(MEDIUM, -30)), "E": match(kpi02=kpi(MEDIUM, 18)),
            "G": match(kpi04=kpi(HIGH, -60, vorl=True), kpi09=kpi(MEDIUM, 25)),
            "K": match(kpi08=kpi(HIGH, 50, prozent=True)), "M": match(kpi03=kpi(HIGH, 99)),
            "O": match(kpi06=kpi(MEDIUM, 18))}
    return FakeDaten({"Bundesliga": bl, "LaLiga": ll}, kpis, **kw)


def test_w15_ranking_like_dashboard():
    s = start.start_daten(_start_daten(), zp("2026-11-16T10:00"))
    assert s["zustand"] == "liste" and s["pause"] is None
    assert [(r["rang"], r["heim"], r["kpi"], r["stufe"], r["richtung"]) for r in s["ranking"]] == [
        (1, "K", "kpi08", "hoch", "hoch"), (2, "A", "kpi03", "hoch", "hoch"), (3, "C", "kpi05", "mittel", "tief"),
        (4, "O", "kpi06", "mittel", "hoch")]          # verschoben und vorläufig nie; höchstens 4, einer je Spiel;
    # Liga-Mix (seit 0.19): höchstens zwei je Liga – G (Bundesliga, dritter) weicht O (La Liga) trotz grösserer Abweichung
    assert [r["id"] for r in s["ranking"]] == [301, 201, 202, 303] and s["ranking"][0]["liga"] == "la-liga"
    html = seiten.start_html(s, seiten.Kontext())
    assert html.count('class="rang-zeile"') == 4 and 'href="/vorschau/spiel/301"' in html
    assert "La Liga · Spieltag 13" in html and "Bundesliga · Spieltag 10" in html and "+50,00 %" in html
    assert "−30,00 %" in html and "Sa 21.11. · 21:00" in html and t("start.ranking_text") in html
    s = start.start_daten(_start_daten(), zp("2026-11-21T16:00"))                   # nur Spiele vor dem Anpfiff
    assert [r["heim"] for r in s["ranking"]] == ["K", "G", "E", "O"]


@pytest.mark.parametrize("plaene, now, alter, art, tage, liga, texte", [
    ({"Bundesliga": [rnd(4, date(2026, 9, 4), date(2026, 9, 6)), rnd(5, date(2026, 9, 25))]}, "2026-09-08", 0,
     "spielpause", 17, "bundesliga", ("Nächster Spieltag am Fr 25.09.", "<b>17</b><span>Tage bis zum Spieltag")),
    ({"Bundesliga": [rnd(14, date(2026, 12, 18), date(2026, 12, 20)), rnd(15, date(2027, 1, 8))],
      "LaLiga": [rnd(16, date(2026, 12, 19)), rnd(17, date(2027, 1, 7))]}, "2026-12-23", 0,
     "winterpause", 15, "la-liga", ("Winterpause", "Nächster Spieltag am Do 07.01.", 'href="/vorschau/spieltag/la-liga"')),
    ({"Bundesliga": [rnd(34, date(2027, 5, 22))]}, "2027-06-10", 0, "sommerpause", None, "bundesliga",
     ("Die Saison ist beendet",)),
    ({"Bundesliga": [rnd(34, date(2027, 5, 22)), rnd(1, date(2027, 8, 20), saison="2027/2028")]}, "2027-07-01", 0,
     "saisonstart", 50, "bundesliga", ("Saisonstart am Fr 20.08.", "<b>50</b><span>Tage bis zum Start")),
    ({"Bundesliga": [rnd(4, date(2026, 9, 4), date(2026, 9, 6)), rnd(5, date(2026, 9, 25))]}, "2026-09-08", 4,
     "unbekannt", 17, "bundesliga", ('role="alert"', "Spielplan zuletzt aktualisiert am Fr 04.09.")),
])
def test_w15_pause_states_with_day_counter(plaene, now, alter, art, tage, liga, texte):
    d = FakeDaten({name: plan(*runden) for name, runden in plaene.items()})
    s = start.start_daten(d, zp(f"{now}T10:00", import_alter=alter))
    assert (s["zustand"], s["pause"]["art"], s["pause"]["tage"], s["pause"]["liga"]) == ("pause", art, tage, liga)
    html = seiten.start_html(s, seiten.Kontext())
    assert 'class="pausenkarte"' in html and 'class="ranking"' not in html
    assert ('class="zaehler"' in html) is (tage is not None)
    for text in texte:
        assert text in html, text


def test_w15_no_anomalies_blocked_and_singular():
    d = FakeDaten({"Bundesliga": plan(rnd(10, date(2026, 11, 20), date(2026, 11, 22)))})
    s = start.start_daten(d, zp("2026-11-16T10:00"))
    assert s["zustand"] == "keine" and s["ranking"] == []
    html = seiten.start_html(s, seiten.Kontext())
    assert t("start.pause.keine.titel") in html and 'class="zaehler"' not in html
    s = start.start_daten(_start_daten(gesperrt=True), zp("2026-11-16T10:00"))
    assert s["zustand"] == "gesperrt" and t("fehler.daten_titel") in seiten.start_html(s, seiten.Kontext())
    assert tn("start.tage_spieltag", 1) == "Tag bis zum Spieltag" and tn("start.tage_start", 2) == "Tage bis zum Start"


# --- W16 Sicherheit der Seiten (CSP ohne Inline-Stile) ---------------------------------------------------------------

def test_w16_no_inline_styles_or_scripts(partien):
    """Die Content-Security-Policy erlaubt nur Stile und Skripte aus statisch/ – kein style=, kein <script> im Text."""
    z = zp("2026-11-21T10:00")
    seiten_html = [seiten.spieltag_html(spieltag.spieltag_daten(partien, BL, z), seiten.Kontext()),
                   seiten.start_html(start.start_daten(_start_daten(), zp("2026-11-16T10:00")), seiten.Kontext()),
                   seiten.hinweis_html("folgt", seiten.Kontext())]
    seiten_html += [seiten.spiel_html(spiel.spiel_daten(partien, i, z), seiten.Kontext()) for i in range(101, 106)]
    for html in seiten_html:
        assert "style=" not in html and "<style" not in html
        assert re.findall(r"<script[^>]*>", html) == ['<script src="/vorschau/statisch/site.js" defer>']
        assert not re.search(r"\son[a-z]+=", html)
    breiten = set(re.findall(r'class="(?:gast )?w(\d+)"', "".join(seiten_html)))
    css = (W.STATISCH / "site.css").read_text(encoding="utf-8")
    for b in breiten:
        assert f".w{b}{{" in css.replace(" ", "") or f".w{b}," in css.replace(" ", ""), b


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
    assert [x["sonderspiel"] for x in tab["spiele"][:2]] == ["vorgezogen", "vorgezogen"]     # 02.12., nach Anstoss


@pytest.mark.skipif(not (REAL_DATABASE.exists() and REAL_FIXTURES.exists()), reason="echte Dateien nicht vorhanden")
def test_w13_real_files_all_leagues():
    from website.daten import Daten
    d = Daten()
    echt = d.zeitpunkt()
    for text in (None, "2026-11-21T16:00", "2026-12-23", "2027-01-09"):
        z, _ = zeitreise(text, echt)
        assert "</html>" in seiten.start_html(start.start_daten(d, z), seiten.Kontext()), text      # seit 0.18
        for web in W.LIGEN:
            s = spieltag.spieltag_daten(d, web, z)
            assert "</html>" in seiten.spieltag_html(s, seiten.Kontext()), (web.slug, text)
            for x in (x for tab in s["tabs"] for x in tab["spiele"] if x["link"]):          # jede Paarung (0.18)
                m = spiel.spiel_daten(d, x["id"], z)
                assert m["heim"] == x["heim"] and "</html>" in seiten.spiel_html(m, seiten.Kontext()), x["id"]
