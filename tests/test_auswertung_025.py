"""Version 0.25 – Auswertung nach dem Spiel (Release_08 des Design-Chats, Beschlüsse 35–52; Regelwerk 11.1).

A1 Bestätigungsregel: Vergleich mit dem Ligadurchschnitt, strikt; Gleichstand nicht bestätigt; fehlt der Wert: folgt.
A2 Dieselbe Entscheidung wie die Ergebniskontrolle der Sensitivitätsanalyse (core/simulation._event), Zufallsprüfung.
A3 Zuerst bekannte Ist-Werte festhalten, spätere Korrektur einer Statistik erkennen (Beschluss 42).
A4 „Beide Teams treffen“ ohne Nachkommastellen (Beschluss 48), Grenzwert weiter mit zwei Stellen.
A5 Ergebnisseite: Tabelle, Bestätigt/Nicht bestätigt/Bewertung folgt, Ja/Nein, Halbzeit, Box, Liga im Satz (DE/EN).
A6 Bilanz der gespielten Kachel („2 von 3 bestätigt“, „Bewertung folgt“).
"""

from __future__ import annotations

import random
from datetime import datetime
from fractions import Fraction
from types import SimpleNamespace as NS

from core import auswertung as AW
from core import schnappschuss as SN
from core import simulation as SIM
from website import format as F
from website import seiten, spiel, spieltag
from website.texte import t


def _ref(wert):
    return NS(referenz=NS(wert=Fraction(wert)))


def test_a1_regel():
    b = AW.bewertung
    assert b("kpi02", "hoch", 4, Fraction(307, 100)) == AW.BESTAETIGT          # 4 Tore > 3,07
    assert b("kpi02", "hoch", 3, Fraction(307, 100)) == AW.NICHT_BESTAETIGT
    assert b("kpi02", "tief", 3, Fraction(307, 100)) == AW.BESTAETIGT
    assert b("kpi04", "hoch", 4, Fraction(4)) == AW.NICHT_BESTAETIGT           # Gleichstand zählt nicht
    assert b("kpi04", "tief", 4, Fraction(4)) == AW.NICHT_BESTAETIGT
    assert b("kpi05", "hoch", None, Fraction(9)) == AW.FOLGT                   # fehlt nie als 0
    assert b("kpi03", "hoch", 3, None) == AW.BESTAETIGT                        # feste Marke 2,5
    assert b("kpi03", "hoch", 2, None) == AW.NICHT_BESTAETIGT
    assert b("kpi03", "tief", 2, None) == AW.BESTAETIGT
    assert b("kpi08", "hoch", 1, Fraction(64)) == AW.BESTAETIGT                # beide trafen (100 > 64)
    assert b("kpi08", "tief", 0, Fraction(64)) == AW.BESTAETIGT                # nicht beide
    assert b("kpi08", "tief", 1, Fraction(64)) == AW.NICHT_BESTAETIGT
    assert b("kpi02", None, 3, Fraction(3)) is None and b("kpi02", "hoch", 3, None) is None


def test_a2_gleich_wie_sensitivitaetsanalyse():
    rnd = random.Random(25)
    for _ in range(2000):
        kpi = rnd.choice(["kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08", "kpi09"])
        ist = rnd.choice([None, 0, 1, 2, 3, 4, 5, 8, 12])
        if kpi == "kpi08" and ist is not None:
            ist = ist % 2
        ref = Fraction(rnd.randint(0, 1200), 100) if kpi != "kpi08" else Fraction(rnd.randint(1, 99))
        mehr, weniger = SIM._event(_ref(ref), ist, SIM.ACTUAL[kpi][1], kpi)
        for richtung, erwartet in (("hoch", mehr), ("tief", weniger)):
            e = AW.bewertung(kpi, richtung, ist, ref)
            if ist is None:
                assert e == AW.FOLGT and erwartet != erwartet                     # NaN in der Analyse
            else:
                assert (e == AW.BESTAETIGT) == (erwartet == 1.0), (kpi, ist, ref, richtung)


def test_a3_statistik_korrektur(tmp_path):
    now = datetime(2026, 11, 25, 22, 0)
    assert SN.record_stats(tmp_path, "bundesliga", "2026/2027", 7, {"kpi05": 9, "kpi09": None}, now)
    assert not SN.record_stats(tmp_path, "bundesliga", "2026/2027", 7, {"kpi05": 9}, now)         # nichts Neues
    assert SN.record_stats(tmp_path, "bundesliga", "2026/2027", 7, {"kpi05": 11, "kpi09": 8}, now)  # 9 bleibt
    assert SN.first_stats(tmp_path, "bundesliga", "2026/2027", 7) == {"kpi05": 9, "kpi09": 8}
    assert SN.stats_corrected(tmp_path, "bundesliga", "2026/2027", 7, {"kpi05": 11, "kpi09": 8})
    assert not SN.stats_corrected(tmp_path, "bundesliga", "2026/2027", 7, {"kpi05": 9, "kpi09": None})
    assert not SN.stats_corrected(tmp_path, "bundesliga", "2026/2027", 8, {"kpi05": 1})          # unbekanntes Spiel


def test_a4_format_beide_teams_treffen():
    assert F.zahl(35.0, "de", "%", 0) == "35 %" and F.zahl(64.5, "de", "%", 0) == "65 %"     # kaufmännisch
    assert F.zahl(64.49, "en", "%", 0) == "64%" and F.zahl(41.6, "de", "%") == "41,60 %"


def _kennzahl(key, abw, stufe="", ref=Fraction(3), prozent=False, neg=None, pos=None):
    sw = NS(positiv=NS(schwelle=pos, signalqualitaet=stufe) if pos else None,
            negativ=NS(schwelle=neg, signalqualitaet=stufe) if neg else None)
    r = NS(abweichung_rund=abw, vorlaeufig=False, anomalie=stufe, hauptwert_rund=2.0, prozent=prozent, schwellen=sw,
           heim=NS(wert_rund=2.0), auswaerts=NS(wert_rund=2.0),
           referenz=NS(wert=ref, wert_rund=float(ref)))
    return spiel.kennzahl(key, r)


def _seite(**kw):
    s = {"seite": "spiel", "id": 9, "liga": "bundesliga", "liga_key": "bundesliga", "slug": "a-b-9", "heim": "A",
         "gast": "B", "saison": "2026/2027", "spieltag": 10, "datum": "2026-11-20", "anstoss": "20:30",
         "termin": "bestaetigt", "status": None, "sonderspiel": None, "zustand": "gespielt", "ergebnis": [2, 1],
         "halbzeit": [1, 0], "form_heim": ["-"] * 5, "form_gast": ["-"] * 5, "bewertung": "auffaellig",
         "werte_ab": None, "ergebnis_vom": None, "nachtraeglich": False, "korrigiert": False, "ohne_werte": False,
         "neu_in_liga": [], "anzahl_gewertet": 8, "im_fenster": False, "anstoss_zeit": "2026-11-20T20:30",
         "heim_id": None, "gast_id": None, "jetzt": "2026-11-25T10:00", "stand": None, "zeitreise": False,
         "ansicht": "auswertung", "statistik_fehlt": False, "bilanz": {"n": 2, "ok": 1, "folgt": 0}}
    s.update(kw)
    return s


def test_a5_ergebnisseite_de_en():
    a = _kennzahl("kpi02", 30.0, "stark", pos=20)
    a.update(ist=4, ergebnis=AW.BESTAETIGT)
    b = _kennzahl("kpi08", -38.0, "mittel", ref=Fraction(64), prozent=True, neg=35)
    b.update(ist=1, ergebnis=AW.NICHT_BESTAETIGT)
    c = _kennzahl("kpi05", 5.0, ref=Fraction(9))
    c.update(ist=None, ergebnis=None)
    m = _kennzahl("kpi03", 10.0, ref=Fraction(3))
    m.update(ist=3, ergebnis=None)
    s = _seite(auffaellig=[a, b], uebrige=[c, m], groesste=a, statistik_fehlt=True)
    html = seiten.spiel_html(s, seiten.Kontext())
    for text in ('<span class="a-tore">2 : 1</span>', "Halbzeit 1 : 0", "Erwartet und tatsächlich",
                 '<th scope="col" class="a-zahl" role="columnheader">Ligadurchschnitt</th>', "✓</span> Bestätigt",
                 "✗</span> Nicht bestätigt", ">Ja<", "Wird nachgeliefert", "Signalqualität stark",
                 "Kein Ligadurchschnitt – feste Marke 2,5.", "Statistisch auffällig ab",
                 "Vor dem Spiel gilt ein Wert in der Bundesliga ab dieser Abweichung", "über 3,60", "keine Schwelle",
                 'aria-controls="a-box" data-aufklapp="a-box"',
                 "Einige Statistikwerte liegen noch nicht vor.", "64 %", "Ohne Auffälligkeit"):
        assert text in html, text
    assert "Auffälligstes Merkmal" not in html and 'class="karte' not in html            # keine Karten
    assert 'class="sb-form"' not in html                                                  # keine Formkurve
    en = seiten.spiel_html(s, seiten.Kontext(lang="en"))
    for text in ("Expected and actual", "Half-time 1 : 0", "Confirmed", "Not confirmed", "Yes<", "Data to follow",
                 "Before the match, a value counts as a standout statistic in the Bundesliga"):
        assert text in en, text
    assert "Endstand 2 : 1" in seiten.seo.spiel_beschreibung(s, "A", "B", "de")              # Description (Abschn. 12)


def test_a5_ohne_auffaelligkeiten_heisst_kennzahlen():
    c = _kennzahl("kpi05", 5.0, ref=Fraction(9))
    c.update(ist=10, ergebnis=None)
    html = seiten.spiel_html(_seite(auffaellig=[], uebrige=[c], groesste=c, bewertung="normal"), seiten.Kontext())
    assert '>Kennzahlen</th>' in html and "Bestätigt" not in html.split("a-tabelle")[1].split("</table>")[0]


def test_a6_bilanz():
    def r(abw, stufe, ref):
        return NS(vorlaeufig=False, abweichung_rund=abw, anomalie=stufe, referenz=NS(wert=Fraction(ref)))
    kpis = NS(kpi02=r(30, "stark", 3), kpi05=r(-20, "mittel", 9), kpi09=r(5, "normal", 8))
    zeile = NS(hg=3, ag=1, ch=4, ca=3, sh=5, sa=4)
    b = spieltag.bilanz(kpis, zeile)
    assert b["n"] == 2 and b["folgt"] == 0
    assert spieltag.bilanz(kpis, None) == {"n": 2, "ok": 0, "folgt": 2}                   # Werte fehlen noch
    assert spieltag.bilanz(None, None) == {"n": 0, "ok": 0, "folgt": 0}
    assert t("spieltag.bilanz", ok=2, n=3) == "2 von 3 bestätigt"


def test_a7_gespielt_ohne_endstand():
    """Befund beim Einspielen 25.11.2026 (Test mit echten Daten): gespielt, aber noch ohne Endstand – die Kachel zeigt
    „Endstand folgt“ statt abzubrechen; die Spielseite bleibt in der Erwartungsansicht mit Hinweis."""
    from test_website import BL, FakeDaten, game, plan, zp
    from datetime import date
    fx = plan(game(10, date(2026, 11, 20), "20:30", "A", "B"), game(10, date(2026, 11, 22), "15:30", "C", "D"))
    fx["api_id"] = [9, 10]
    d = FakeDaten({"Bundesliga": fx}, {}, {})
    s = spieltag.spieltag_daten(d, BL, zp("2026-11-21T10:00"))
    eintrag = next(x for x in s["tabs"][0]["spiele"] if x["heim"] == "A")
    assert eintrag["art"] == "gespielt" and eintrag["ergebnis"] is None and eintrag["bilanz"] is None
    html = seiten.spieltag_html(s, seiten.Kontext())
    assert "Endstand folgt" in html and "kg-tor" not in html
    seite = spiel.spiel_daten(d, 9, zp("2026-11-21T10:00"))
    assert seite["ansicht"] == "erwartung"
    assert "Gespielt · Endstand folgt" in seiten.spiel_html(seite, seiten.Kontext())


def test_a8_design_550():
    """0.26 (Beschlüsse 53–58): Link „Frühere Spieltage ansehen“ (Spieltag − 1, am 1. Spieltag keiner), zwei getrennte
    Tabellen, Hinweis nur bei Ausnahmen, Chips rechtsbündig, Satz „für kommende Spiele“."""
    from datetime import date
    from test_website import BL, FakeDaten, game, plan, zp
    fx = plan(game(10, date(2026, 11, 22), "15:30", "C", "D"))
    fx["api_id"] = [10]
    s = spieltag.spieltag_daten(FakeDaten({"Bundesliga": fx}, {}, {}), BL, zp("2026-11-21T10:00"))
    assert s["frueher"]["nr"] == 9
    html = seiten.spieltag_html(s, seiten.Kontext())
    assert "Frühere Spieltage ansehen" in html and "/de/spieltag/bundesliga/2026-27/9/" in html
    fx1 = plan(game(1, date(2026, 11, 22), "15:30", "C", "D"))
    fx1["api_id"] = [11]
    s1 = spieltag.spieltag_daten(FakeDaten({"Bundesliga": fx1}, {}, {}), BL, zp("2026-11-21T10:00"))
    assert s1["frueher"] is None and "Frühere Spieltage ansehen" not in seiten.spieltag_html(s1, seiten.Kontext())
    a = _kennzahl("kpi02", 30.0, "stark", pos=20)
    a.update(ist=4, ergebnis=AW.BESTAETIGT)
    c = _kennzahl("kpi05", 5.0, ref=Fraction(9))
    c.update(ist=10, ergebnis=None)
    html = seiten.spiel_html(_seite(auffaellig=[a], uebrige=[c], groesste=a), seiten.Kontext())
    assert html.count('<table class="a-tabelle"') == 2                       # zwei Karten
    assert "Hinweis:" not in html and "Die Werte wurden mit den Daten vor dem Spiel berechnet." not in html
    css = (spiel.W.STATISCH / "site.css").read_text(encoding="utf-8")
    assert ".karte .kopf-k > .q-chip { margin-left: auto; }" in css
    assert t("spiel.c_notiz", liga_in="in der Bundesliga").endswith("kein verlässlicher Hinweis für kommende Spiele.")
