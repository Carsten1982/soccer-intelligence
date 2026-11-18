# Prüfprotokoll: Auffälligkeit und Prognosewert (Version 0.19)

**Datum:** 18.11.2026 · **Geprüft von:** Claude · **Gegenprüfung:** ChatGPT · **Auftrag und Freigabe:** Carsten

Regeln: KPI-Regelwerk 2.2 (Auffälligkeit, Prognosewert, gültige Schwellen), 2.6 (Top Anomalien) und 11.3
(Sensitivitätsanalyse). Hier stehen nur die Auswertungen, die zur Festlegung geführt haben, und die Prüfung der
Umsetzung.

---

## 1. Ausgangslage

Bis 0.18 gab es je KPI die Stufen „leicht“ und „stark“ (feste Schwellen, z. B. ±20 / ±35 %). Auf der Startseite
stand damit oft ein Spiel oben, das stark abwich, dessen Kennzahl aber in der Vergangenheit kaum besser traf als ein
beliebiges Spiel. Ziel des neuen Modells: Ein Spiel ist **auffällig**, wenn die Abweichung eine Schwelle überschreitet,
die sich für diese Liga, diese Kennzahl und diese Richtung **nachweislich bewährt hat**; der **Prognosewert** sagt, wie
gut.

Ablauf: Auswertung mit allen Kandidaten (10–35 %) → Entwurf „Abweichung + Verlässlichkeit“ → Gegenprüfung durch ChatGPT
(Punkte 1–6) → Prüfrunde mit Lern- und Prüfsaisons (Abschnitt 2) → Entscheidungen Carsten 17./18.11.2026 →
Spezifikation mit Testfällen P1–P25 → Freigabe → Umsetzung.

## 2. Prüfrunde (Lernsaisons gegen Prüfsaisons)

- **Lernsaisons** (Schwellenwahl): 2019/20–2024/25, 888 Liga-Spieltage.
- **Prüfsaisons** (erstmals angeschaut, Schwellen unverändert): 2025/26 und 2026/27 bis Spieltag 9–12, 190 Liga-Spieltage.
- Mehrwert in den Prüfsaisons immer gegen die Grundquote **aller Spiele** derselben Liga, Kennzahl und Richtung.

| Variante | Stufe | Kombinationen | Lern: Treffer | Prüf: Treffer | Prüf: Grundquote | Prüf: Mehrwert | Prüf: Spiele je Spieltag |
|---|---|---:|---:|---:|---:|---:|---:|
| Rand > 0, mit Handanpassung | hoch | 21 | 64,4 % | 58,4 % | 52,1 % | +6,4 | 2,1 |
| Rand > 0, ohne Handanpassung | hoch | 21 | 63,5 % | 58,2 % | 51,5 % | +6,7 | 2,9 |
| Rand > +3 | hoch | 14 | 64,0 % | 57,0 % | 51,5 % | +5,5 | 2,5 |
| Rand > +5 | hoch | 10 | 64,4 % | 58,4 % | 50,8 % | +7,6 | 1,9 |
| gegen nicht auffällige Spiele | hoch | 26 | 62,9 % | 60,3 % | 55,6 % | +4,7 | 4,9 |
| Cluster-Bootstrap über Spieltage | hoch | 26 | 62,9 % | 60,3 % | 55,6 % | +4,7 | 4,9 |
| **bisher** stark (0.18) | – | – | – | 57,0 % | 51,4 % | +5,6 | 3,6 |
| **bisher** leicht inkl. stark (0.18) | – | – | – | 54,2 % | 50,7 % | +3,5 | 6,9 |

Ergebnisse und Folgerungen:

1. **Echter, aber moderater Effekt.** „Hoch“ trifft auf ungesehenen Saisons in rund 58 % der Fälle, 6–8 Prozentpunkte
   öfter als beliebige Spiele (Lernsaisons: 64 %). Die angezeigten Werte sind darum etwas zu optimistisch
   (Hinweis im Regelwerk 11.3 und im Erklärfeld der Sensitivitätsanalyse).
2. **Vergleichsgruppe:** gegen die nicht auffälligen Spiele wäre statistisch sauberer, wählt hier aber schlechter aus
   (zusätzliche Kombinationen mit hoher Grundquote). Entscheidung: **alle Spiele**.
3. **Handanpassung** ändert die Qualität nicht (+6,7 gegen +6,4), nur die Menge → **gestrichen**.
4. **Abhängigkeit innerhalb eines Spieltags** ist für die Spanne vernachlässigbar (Bootstrap wählt dieselben
   Kombinationen wie Newcombe).
5. **Je Liga** (Prüfsaisons, hoch): Bundesliga +9,2, La Liga +10,1, Serie A +4,5, Premier League +0,8 Pp.
6. **Datenzeitpunkt am Code geprüft, kein Datenleck:** Teamwerte nur aus Spielen bis Spieldatum − 2 Tage (2-Tage-Regel),
   Ligaschnitt aus den 20 Spieltagen vor dem Spieltag und nur aus Spielen vor dem Spieldatum, Treffer gegen den
   Vergleichswert vor dem Spiel (Regelwerk 11.1), Schwellenwahl nur auf Lernsaisons.
7. **Tor-Kennzahlen hängen zusammen** (Korrelation der Abweichungen bis 0,80). Darstellung einer primären
   Auffälligkeit je Spiel: Phase 3 (Entscheidung Carsten).

## 3. Wahl der Grenze „linker Rand“ (Entscheidung O1: +2 Pp.)

Erste Schwellendatei mit allen abgeschlossenen Saisons 2019/20–2025/26, Regeln nach Regelwerk 2.2 und 11.3, nur die
Grenze für den linken Rand der Spanne verschieden:

| Linker Rand > | Kombinationen | hoch / mittel / gering | Spiele je Spieltag mit „hoch“: BL / PL / SA / LL | mit „mittel“: BL / PL / SA / LL |
|---|---:|---|---|---|
| 0 Pp. | 33 | 18 / 11 / 4 | 2,2 / 2,8 / 4,8 / 3,6 | 2,1 / 4,9 / 0,7 / 2,3 |
| +1 Pp. | 29 | 18 / 8 / 3 | 2,2 / 2,8 / 4,8 / 3,6 | 2,1 / 4,5 / 0,7 / 1,7 |
| **+2 Pp. (beschlossen)** | **23** | **16 / 6 / 1** | **1,4 / 2,6 / 4,8 / 3,6** | **1,9 / 3,4 / 0,7 / 1,7** |
| +3 Pp. | 15 | 13 / 2 / 0 | 1,4 / 0,5 / 4,2 / 3,6 | 0,0 / 3,3 / 0,0 / 0,0 |

+2 dünnt die unsichersten Kombinationen aus, lässt allen vier Ligen „hoch“ und behält alle drei Stufen. Serie A und
La Liga liefern deutlich mehr „hoch“ als Bundesliga und Premier League – darum der **Liga-Mix** (höchstens zwei je Liga)
in den Top Anomalien.

Mit +2 Pp. (Lernsaisons 2019/20–2025/26, je Liga-Spieltag):

| Liga | Spiele mit „hoch“ | mit „mittel“ | mit „gering“ | Spieltage ohne „hoch“ | mit 1–3 „hoch“ | mit mehr als 3 „hoch“ |
|---|---:|---:|---:|---:|---:|---:|
| Bundesliga | 1,4 | 1,9 | 1,4 | 20 % | 77 % | 3 % |
| Premier League | 2,6 | 3,4 | 0,0 | 7 % | 68 % | 26 % |
| Serie A | 4,8 | 0,7 | 0,0 | 0 % | 21 % | 79 % |
| La Liga | 3,6 | 1,7 | 0,0 | 1 % | 51 % | 48 % |

Nur zur Information, keine Anpassung (laufende Saison 2026/27, abgeschlossene Spieltage, mit diesen Schwellen):
hoch 163 Fälle, 66,3 % Treffer gegen 54,3 % (+12,0 Pp.) · mittel 86 Fälle, 66,3 % gegen 55,9 % (+10,4) · gering 15
Fälle, 60,0 % gegen 50,9 % (+9,1).

Die 23 freigegebenen Schwellen stehen im Regelwerk 2.2, die Herleitung je Zeile (Spiele, Trefferquote,
Vergleichsgruppe, Mehrwert, Spanne, Saisons positiv) in `app/config/schwellen.toml`.

## 4. Vollvergleich 0.18 gegen 0.19

Datenbank: `tests/referenz/Database-Soccer-Intelligence_451348b6.xlsx` (Saisons 2018/19–2026/27). Jedes Spiel mit
Stichtag = Spieldatum, einmal mit dem Code von 0.18 (`fbdd5d9`, Schwellen leicht/stark) und einmal mit dem Code von
0.19 (neue `schwellen.toml`). Die Einstufung wurde ohne App-Code aus der Schwellendatei (mit `tomllib` gelesen)
nachgerechnet, die Top Anomalien nach Regelwerk 2.6 selbst ausgewählt.

| Vergleich | Umfang | Ergebnis |
|---|---|---|
| KPI-Werte, Teamwerte, Spiel-IDs, Ligareferenzen, Abweichungen, „vorläufig“, Teamabweichungen KPI 03 | 95'824 KPI-Werte (11'978 Spiele × 8 KPIs) | **identisch** |
| Formkurve | 11'978 Spiele | **identisch** |
| Einstufung 0.19 gegen eigene Einstufung aus der Datei | 95'824 | **0 Abweichungen** |
| Überschrift und Text | 95'824 | gleich, wo sich „auffällig“ nicht ändert; sonst „Keine statistische Besonderheit“ genau bei nicht auffällig |
| Top Anomalien gegen eigene Auswahl (Saison × Spieltag über vier Ligen) | 316 Runden | **0 Abweichungen** |

Wechsel der Einstufung je KPI (alle Spiele):

| KPI | leicht → keine | stark → keine | keine → hoch | keine → mittel | keine → gering | leicht → hoch | leicht → mittel | leicht → gering | stark → hoch | stark → mittel | stark → gering |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 02 | 1'097 | 387 | – | 312 | – | 542 | 324 | – | 184 | 87 | – |
| 03 | 1'256 | 909 | – | – | – | 520 | – | – | 517 | – | – |
| 04 | 1'313 | 335 | 216 | 775 | 194 | 390 | 803 | 435 | 201 | 251 | 83 |
| 05 | 889 | 349 | – | 218 | – | 272 | 78 | – | 126 | 40 | – |
| 06 | 2'141 | 1'816 | – | 383 | – | 145 | 221 | – | 202 | 133 | – |
| 07 | 1'012 | 1'373 | – | – | – | – | – | – | – | – | – |
| 08 | 955 | 1'470 | – | – | – | – | – | – | 421 | – | – |
| 09 | 353 | 163 | 251 | 229 | – | 1'012 | 90 | – | 505 | 43 | – |

Auffällige KPI-Werte (ohne vorläufige, alle Saisons): vorher leicht und stark zusammen 20'065, neu 4'743 hoch,
3'522 mittel, 628 gering (nur Bundesliga, Gelbe Karten mehr).

| Liga | vorher leicht + stark | hoch | mittel | gering |
|---|---:|---:|---:|---:|
| Bundesliga | 4'135 | 414 | 658 | 628 |
| Premier League | 5'086 | 884 | 1'783 | 0 |
| Serie A | 5'046 | 1'893 | 284 | 0 |
| La Liga | 5'798 | 1'552 | 797 | 0 |

Top Anomalien (316 Runden): 306 mit vier Einträgen, 10 ohne (Saisonbeginn 2018/19 ohne Werte); alle 1'224 Einträge
„hoch“. Je Liga: Premier League 463, Serie A 373, La Liga 314, Bundesliga 74. Je KPI: 03 546, 04 232, 08 187, 06 139,
02 65, 09 50, 05 5 (vorher fehlten KPI 02, 05 und 09 fast ganz; Regelwerk Punkt 17 erledigt).

## 5. Automatische Tests

- `tests/test_schwellen.py`: ausgelieferte `schwellen.toml` = freigegebene 23 Schwellen (unabhängig mit `tomllib`),
  Herleitung P21 in der Datei, P1–P3 (Grenzen, ohne Schwelle, vorläufig), Dashboard gegen die Gegenrechnung
  (`gegenrechnung.grade_signal`) für die letzten fünf Spieltage 2025/26 in vier Ligen; mit der echten Datenbank P21/P22:
  der Schwellenvorschlag der Sensitivitätsanalyse ergibt genau die ausgelieferte Datei.
- `tests/test_sensitivity.py`: T1–T15 (Zählung, Spanne, Empfehlung, Gegenrechnung) und P4–P16 (Funktioniert mit Rand
  > +2, Stabilität in zwei Dritteln, Prognosewert, eine Saison, Wahl der Schwelle, Vorschlag, TOML).
- `tests/test_top.py`: P17–P20, P23–P25 (Reihenfolge nach Prognosewert, Auffüllen mit „gering“, Liga-Mix, weniger als vier).
- `tests/test_thresholds.py`, `tests/test_h2.py`: neues Dateiformat, klare Meldungen, altes Format abgelehnt und archiviert.
- `tests/test_kpis.py`, `test_gegenrechnung.py`, `test_seasons.py`: die bestätigten Testfälle (`docs/tests/test_kpi*.md`)
  rechnen weiter mit der Schwelle 20 % (`LEGACY`) und sind alle grün.
- `tests/test_website.py`, `test_ui.py`, `test_simulation.py`: Codes hoch/mittel/gering, Sortierung und Ranking mit
  Liga-Mix, Seite Sensitivitätsanalyse.
