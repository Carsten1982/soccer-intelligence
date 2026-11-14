# Prüfprotokoll: Neue Schwellen und Sensitivitätsanalyse nach Entwurf C (Version 0.13)

**Datum:** 14.11.2026 · **Geprüft von:** Claude · **Auftrag und Freigabe:** Carsten

Datenbank für alle Vergleiche: `tests/referenz/Database-Soccer-Intelligence_451348b6.xlsx` (aktive Datenbank, SHA-256
`451348b6…`, Saisons 2018/19–2026/27). Regeln: KPI-Regelwerk 2.2 (Schwellen) und 11 (Sensitivitätsanalyse).

---

## 1. Grundlage der Schwellen (Auswertung vor der Festlegung)

| Prüfung | Ergebnis |
|---|---|
| Mehrwert je Liga bei ±20 % (alle KPIs, beide Richtungen) | Ligen teils sichtbar auseinander (Abstand bis 10,5 Pp.), bei keinem KPI statistisch gesichert (Test auf gleiche Mehrwerte, p ≥ 0,08) |
| Test „Vergangenheit gegen Zukunft“: beste Schwelle aus 2019/20–2023/24 (untere Grenze der Spanne, mind. 50 Fälle, Schwellen 5–40 %), angewendet auf 2024/25–2025/26 | gemeinsame Schwelle **+4,31 Pp.** je Anomalie, Schwelle je Liga **+3,41 Pp.**; gemeinsame Schwelle in 15 von 16 KPI-Richtungen besser |
| KPI 03 (feste Marke 2,5): Ø Abweichung aller Paarungen | Bundesliga +26,1 %, Premier League +14,3 %, Serie A +9,1 %, LaLiga +2,6 % → bei gemeinsamer Schwelle +20 % in der Bundesliga 5,1 Anomalien je Spieltag, in LaLiga 1,1. Darum KPI 03 je Liga |

Die festgelegten Werte stehen im KPI-Regelwerk 2.2 und in `app/config/schwellen.toml`.

## 2. Vollvergleich

Gerechnet wurde alles, was das Dashboard zeigt (Ligaseite je Spieltag, jedes Spiel mit Stichtag = Spieldatum, Top
Anomalien je Spieltag über vier Ligen, Häufigkeit im Bereich Datenqualität, Fälle der Sensitivitätsanalyse), einmal mit
dem Code von Version 0.12 und zweimal mit dem Code von Version 0.13 (alte Standardschwellen ±20/±35 und neue Schwellen).
Ausgewertet wurde der gespeicherte Text der Ergebnisse mit einer eigenen Einstufung und einer eigenen Auswahl der
Top Anomalien, nicht mit dem App-Code.

| Vergleich | Umfang | Ergebnis |
|---|---|---|
| Code 0.12 gegen 0.13, alte Schwellen: Einzelspiele | 11'978 Spiele | **0 Abweichungen** |
| … Ligaseiten | 1'226 Spieltage | **0 Abweichungen** |
| … Top Anomalien | 316 Spieltage | **0 Abweichungen** |
| … Häufigkeit Datenqualität, Fälle der Sensitivitätsanalyse | 4 Ligen, 77'318 Fälle | **identisch** |
| Code 0.13, alte gegen neue Schwellen: KPI-Werte, Abweichungen, Ligareferenzen | 95'824 KPI-Werte (11'978 Spiele × 8 KPIs) | **identisch** |
| … Einstufung | 95'824 | 14'509 Einstufungen geändert, **jede wie nach den festgelegten Schwellen erwartet** |
| … Überschrift und Text | 95'824 | ändern sich **genau dort**, wo „keine Anomalie“ zu „Anomalie“ wird oder umgekehrt (die Texte unterscheiden nicht zwischen leicht und stark) |
| Top Anomalien mit neuen Schwellen, eigene Auswahl nach Regelwerk 2.6 | 306 Spieltage mit Liste | **0 Abweichungen** |
| Häufigkeit Datenqualität mit neuen Schwellen, eigene Zählung | 4 Ligen × 8 KPIs, Saison 2025/26 | **0 Abweichungen** |

Geänderte Einstufungen je KPI (alle Spiele 2018/19–2026/27):

| KPI | keine → leicht | keine → stark | leicht → stark | leicht → keine | stark → leicht |
|---|---|---|---|---|---|
| 02 | 800 | – | 451 | – | – |
| 03 | 653 | 103 | 306 | 1'673 | 536 |
| 04 | 788 | – | 257 | – | – |
| 05 | 1'239 | 304 | 201 | – | – |
| 06 | 779 | – | 1'054 | – | – |
| 07 | – | – | 812 | 573 | – |
| 08 | – | – | 716 | 1'116 | – |
| 09 | 1'455 | 375 | 318 | – | – |

Top Anomalien (alle 316 Spieltage, Einträge je KPI): vorher KPI 03 487 · 04 128 · 06 248 · 07 83 · 08 278; nachher
KPI 03 465 · 04 134 · 05 1 · 06 252 · 07 86 · 08 286. Die Rangfolge (Stufe, dann Prozent) bleibt; KPI 02, 05 und 09
kommen weiterhin kaum vor (Regelwerk, offener Punkt 17).

Häufigkeit Saison 2025/26 mit den neuen Schwellen (leicht / stark):

| Liga | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 |
|---|---|---|---|---|---|---|---|---|
| Bundesliga | 52 / 8 | 31 / 70 | 82 / 14 | 36 / 14 | 58 / 45 | 29 / 29 | 12 / 36 | 28 / 20 |
| Premier League | 51 / 8 | 26 / 13 | 119 / 22 | 32 / 5 | 80 / 54 | 30 / 26 | 41 / 52 | 37 / 14 |
| Serie A | 59 / 8 | 82 / 22 | 84 / 25 | 38 / 7 | 79 / 45 | 26 / 33 | 18 / 70 | 29 / 12 |
| LaLiga | 66 / 19 | 53 / 32 | 99 / 21 | 50 / 14 | 75 / 102 | 27 / 32 | 40 / 83 | 43 / 18 |

## 3. Automatische Tests (neu oder geändert)

- `tests/test_schwellen.py`: ausgelieferte `schwellen.toml` gegen die Festlegung (unabhängig mit `tomllib` gelesen),
  Anzeige in Datenqualität, Grenzfälle der Einstufung (genau auf der Schwelle), symmetrische Schwellen wie bisher,
  Dateiformat und Fehlermeldungen, Dashboard mit den gültigen Schwellen gegen die Gegenrechnung (`grade_split`) für alle
  Spiele der letzten fünf Spieltage 2025/26 in vier Ligen.
- `tests/test_sensitivity.py`: T13 (Gegenrechnung) zusätzlich mit Ergebnisqualität für stark und mit Schwellen je Liga;
  T14 Bewertung der starken Schwelle, T15 Schwellen je Liga, T16 Übernahme getrennter Schwellen.
- `tests/test_thresholds.py`, `tests/test_ui.py` angepasst (Seite nach Entwurf C: Vorbelegung, „je Liga“, blaue
  Eingaben, Zurücksetzen, Ligawechsel).
- Die bestätigten Testfälle (`docs/tests/test_kpi*.md`) rechnen unverändert mit ±20/±35 und sind alle grün.
