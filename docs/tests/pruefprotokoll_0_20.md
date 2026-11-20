# Prüfprotokoll Version 0.20 „Fundament“

**Stand:** 19.11.2026 · **Geprüft von:** Claude · **Grundlage:** Entscheidungsprotokoll 19.11.2026, `07`, Abschnitt 4.9

## 1. Vollvergleich vorher/nachher (Umbenennung Signalqualität)

- **Vorgehen:** Alle Spiele der Referenz-Datenbank `Database-Soccer-Intelligence_451348b6.xlsx` (Saisons 2018/19–2026/27,
  vier Ligen) einmal mit dem Code von 0.19.1 (Git `27f7a6a`, eigener Arbeitsordner) und einmal mit 0.20 berechnet, je
  mit der eigenen `schwellen.toml`. Gespeichert je Spiel und KPI: Teamwerte mit Spiel-IDs, Ligareferenz, Hauptwert,
  Abweichung (genau und gerundet), vorläufig, Formkurve, Einstufung, Richtung, Überschrift und Text.
- **Ergebnis:** 11'978 Spiele, 95'824 Kennzahlen.

| Prüfung | Abweichungen |
|---|---|
| Werte (Teamwerte, Referenz, Hauptwert, Abweichung, vorläufig) | 0 |
| Formkurve | 0 |
| Richtung | 0 |
| Überschrift und Text | 0 |
| Einstufung nach Umbenennung (hoch → stark) | 0 |

| Einstufung 0.19.1 → 0.20 | Kennzahlen |
|---|---:|
| keine → keine | 84'567 |
| hoch → **stark** | 5'504 |
| mittel → mittel | 3'987 |
| gering → gering | 712 |
| nicht berechenbar → nicht berechenbar | 1'054 |

## 2. Schnappschuss mit echten Daten

- **Daten:** Probe-Stand vom 19.11.2026 (Datenbank und Spielplan aus dem Probelauf, Saisons 2025/26 und 2026/27 im
  Spielplan), Import-Ordner als Kopie im Arbeitsbereich.
- **Erster Lauf** (19.11.2026, 15:00): 1'856 Schnappschüsse (alle gespielten Spiele beider Saisons, alle nachträglich),
  1'856 erste Ergebnisse, 0 wartend, keine Fehler, **15 s**. Ablage 16 MB (rund 9 KB je Spiel).
- **Zweiter Lauf:** 0 neu, 1'856 vorhanden, 5,6 s (nur Laden der Dateien).
- **Speichern und Lesen:** 266 Stichproben (jede siebte Datei) gelesen und mit einer neuen Berechnung verglichen:
  0 Abweichungen (Brüche und Dezimalzahlen exakt).

## 3. Website und Dashboard mit echten Daten

- **Website:** Startseite, alle vier Spieltag-Seiten und alle verlinkten Spielseiten zu vier Zeitpunkten (21.11. 16:00,
  22.11. 10:00, 24.11. 10:00, jetzt) ohne Fehler erzeugt. Beispiel 21.11. 16:00: 39 Kacheln des Folgespieltags mit
  „Werte ab …“ (die am 19.11. gefundene Lücke ist geschlossen); Ranking vor und nach den ersten Anpfiffen gleich.
- **Dashboard im Browser** (lokal, Probe-Daten): Top Anomalien, Bundesliga und Datenimport/API ohne Fehler, nirgends
  mehr „Prognosewert“; Text „Die Liste steht vor dem ersten Anpfiff fest …“; Reiter mit Kasten „Schnappschüsse“.

## 4. Automatische Tests

Neu: A28–A33 (`tests/test_anzeige.py`), SN1–SN10 (`tests/test_schnappschuss.py`), Website (Schnappschuss, nachträglich,
korrigiert, „Werte ab“ auf der Spielseite und der Kachel, Ranking ohne Nachrücken, Zählform), Reiter Datenimport/API.
Angepasst an die Beschlüsse: A2, A19, A23, A25, W2–W5, W8, W14, W15.
