"""Englische Texte nach Release_14 (Design 571, Entscheide Carsten 26.11.2026; seit 0.29): «standout» statt «anomaly»,
Standard-Sätze S1–S3, zwei deutsche Klarstellungen in der Methodik (D1, D2). Abnahme-Suche aus Release_14, Abschnitt 6."""

from __future__ import annotations

import json
import re
from pathlib import Path

from website.texte import t

APP = Path(__file__).resolve().parents[1] / "app" / "website"
VERBOTEN = re.compile(r"anomal|confirmed as a forecast|forecasts of potential|Statistical analyses|No affiliation|"
                      r"played by both teams|expected to score|normal rate|metric", re.I)
ERLAUBT = {"Metrics", "All metrics"}          # Gruppenname auf Spiel- und Auswertungsseite


def _texte(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from _texte(v)
    elif isinstance(o, str):
        yield o


def test_e1_keine_alten_begriffe_im_englischen():
    funde = [s for s in _texte(json.loads((APP / "texte" / "en.json").read_text(encoding="utf-8")))
             if VERBOTEN.search(s) and s not in ERLAUBT]
    for datei in sorted((APP / "vorlagen" / "inhalt").glob("*.en.html")):
        funde += [f"{datei.name}: {m.group(0)}" for m in VERBOTEN.finditer(datei.read_text(encoding="utf-8"))]
    assert funde == []


def test_e2_standardsaetze():
    s1 = ("This shows how often similar patterns in past matches were followed by an actual value on the same side "
          "of the league average. The rating has three levels: high, medium or low.")
    assert t("lesen.signal", "en") == s1 == t("spieltag.erklaerung_stufe", "en")
    assert t("fuss.pflicht", "en") == "Statistical analysis, not betting advice. Not affiliated with any leagues or clubs."
    assert t("start.seo_3_fett", "en") == "We provide transparent statistics, but no betting advice or predictions of winnings."
    assert t("spiel.d_schwelle", "en") == t("spiel.a_box_titel", "en") == "Standout threshold"
    assert t("kennzahl.kpi08.hoch", "en") == "Both teams scoring expected more often"
    assert "als Prognose bestätigt" in t("lesen.signal", "de")                     # Deutsch bleibt (Entscheid)


def test_e3_deutsche_klarstellungen_methodik():
    de = (APP / "vorlagen" / "inhalt" / "methodik.de.html").read_text(encoding="utf-8")
    assert "aus den letzten 10 Ligaspielen jeder Mannschaft" in de and "Ligaspielen beider Teams, bis" not in de
    assert "die zeigt, wie unsicher der gemessene Mehrwert ist" in de
    assert "ist keine Prognose und keine Zusage für kommende Spiele" in de
