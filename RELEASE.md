# Release: Version 0.15 – Datenimport nach den Reviews

**Stand:** 15.11.2026 · Version 0.15 · Spezifikation Spielplan v2.1 (`docs/07_Spielplan_Anzeige.md`, Abschnitt 3) und Ergebnis-Import v1.1 (`docs/06_Datenlieferung.md`, Abschnitt 10.1), Entscheidungen Carsten 15.11.2026

**Commit:** Version 0.15: Datenimport nach den Reviews (Spielplan v2.1, Ergebnis-Import v1.1)

## Was ändert sich?

- **Spielplan aus der API, genauer:** Status nur noch von der API. Nachholspiele und vorgezogene Spiele sind nicht mehr „verschoben“, sondern geplant mit Vermerk und **bekommen KPI-Werte** (LaLiga 2026/27: 8 Spiele). Der Spielplan enthält jetzt auch die **Vorsaison**. Neue Spalten `Termin`, `Hinweis`, `API-Status`.
- **Import täglich** um 04:00, auch am Wochenende.
- **Korrekturen ohne Handarbeit:** Bis 7 Tage nach dem Spiel übernimmt der Import Korrekturen der API selbst. Danach (und wenn der Endstand nicht zu den Toren passt) erscheint im Reiter **„Ihre Entscheidung“** mit zwei Buttons.
- **Neue Prüfungen:** Plausibilität neuer Spiele, IDs über alle Ligen, Spiel verschwunden, feste Zuordnung eigene ID ↔ API-ID.
- **Reiter „Datenimport/API“:** Blöcke **A · Ergebnisse** und **B · Spielplan** (Änderungen nach Gruppen), Hinweis zum Automatikbetrieb.
- Die Anzeige kommender Spieltage (Abschnitte, Pausen, Datumsspalte) folgt in **Version 0.16** nach dem Designentwurf.

## Erwartungswerte

- Git-Stand vorher: `1408c50`.
- Tests beim Einspielen: rund **461 bestanden, 13 übersprungen** (zuletzt 442 / 13), keine Fehler. Einspielen in `tmux` (`01`, Abschnitt 6.1).
- Schritt 5: „Container laufen (Dashboard und Import)“.
- Danach ein Lauf von Hand:
  ```bash
  docker exec soccer-import python -m importer.dienst --jetzt
  ```
  Erwartet: `Lauf … -> wartet` (rund 56 Abfragen).

## Im Browser prüfen

1. **Datenimport/API → Neue Daten bereit:** 0 Fehler, 0 kritische Punkte; Kachel „Spielplan: wichtige Änderungen“ **9**; „Im Automatikbetrieb: würde ohne Rückfrage übernommen“.
2. **Block B · Spielplan:** „Spiele neu im Spielplan: 1'446“ (Vorsaison); aufgeklappt **Nachholspiel (5)** (LaLiga Sp. 1: Valencia – Betis, Real Madrid – Real Sociedad, Celta – Osasuna, Barcelona – Athletic; Sp. 6: Levante – Athletic), **vorgezogen (3)** (LaLiga Sp. 23: Real Sociedad – Real Madrid und Barcelona – Atlético am 02.12.; Sp. 6: Real Sociedad – Celta), Termin geändert (1, Rayo – Athletic, abgebrochen). Jeweils „Status verschoben → geplant“.
3. **Block A · Ergebnisse:** Vollständigkeit „vollständig“, Qualität 0 Fehler / 35 Warnungen / 201 Hinweise wie bisher.
4. **Übernehmen** klicken, nach einer Minute neu laden: Status „übernommen“.
5. **LaLiga, Pfeil zurück bis Spieltag 1:** Die vier Nachholspiele zeigen jetzt KPI-Werte (bisher leer). Zeitraum „15.08. – 19.08.2026“.
6. **Datenqualität → Spielplan:** 0 Fehler, 0 Warnungen, 0 Hinweise (der Hinweis „Begegnung bereits gespielt“ entfällt).
7. **Fusszeile:** „Version 0.15 – Datenimport“.
