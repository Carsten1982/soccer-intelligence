# Release: Version 0.16 – Anzeige kommender Spieltage

**Stand:** 16.11.2026 · Version 0.16 · Designentwurf freigegeben von Carsten am 16.11.2026 · Spezifikation `docs/07_Spielplan_Anzeige.md`, Abschnitt 4 (Festlegungen 4.8)

**Commit:** Version 0.16: Anzeige kommender Spieltage (Abschnitte, Datum, Pausen, Werte ab, Top-Block)

## Was ändert sich?

- **Ligaseiten – „Kommende Spiele“:** je Spieltag ein Abschnitt: der anstehende Spieltag, weitere Spieltage, die in den nächsten 7 Tagen beginnen (z. B. englische Woche), und Nachhol- oder vorgezogene Spiele unter ihrer offiziellen Nummer, mit Vermerk (gelb „vorgezogen“, blau „Nachholspiel“).
- **Neue Spalte „Datum“** zwischen Spiel und Form: „Fr 20.11. · 20:30“, „Zeit offen“, „Wochenende 06./07.02. · Termin offen“. Gespielte Spiele bleiben bis zum Ende des Spieltags **grau** mit Ergebnis („Fr 20.11. · 2:1“) bzw. „Ergebnis folgt“; ihre KPI-Werte bleiben stehen.
- **„Werte ab …“:** KPI-Werte erscheinen erst, wenn beide Teams ihr vorheriges Spiel gespielt haben, z. B. „Werte ab Do 03.12. – Real Madrid spielt vorher noch (Mi 02.12.)“.
- **Pausen:** Box „Winterpause – nächster Spieltag am …“, „Spielpause …“, „Sommerpause …“; nur wenn der letzte Importlauf höchstens 3 Tage alt ist, sonst gelbe Box „Spielplan zuletzt aktualisiert am …“.
- **Pfeile:** zurück alle Spieltage dieser und der letzten Saison, vorwärts bis 2 Spieltage über den anstehenden hinaus; „Zu den kommenden Spielen“ führt zurück.
- **Top Anomalien:** je Liga der nächste Block, nur Spiele **vor dem Anpfiff** und mit Werten; oben je Liga ein Kästchen („Bundesliga: Spieltag 10 · noch 4 Spiele“ bzw. „Winterpause bis 07.01.“); Karten mit Datum und Anstoss.
- **Datenimport/API:** neue Tabelle „So sieht das Dashboard nach der Übernahme aus“ in der wartenden Fassung.
- Die **KPI-Berechnung ist unverändert**. Neu entschieden wird nur, welche Spiele wann erscheinen.

## Erwartungswerte

- Git-Stand vorher: `47d54ca`.
- Schritt 4: rund **532 bestanden, 15 übersprungen, 16 ausgelassen** (langsame Tests), keine Fehler; Dauer rund 9 Minuten. (Lokal mit den echten Dateien des Probelaufs: 545 bestanden, 1 übersprungen; auf dem Server fehlen `git`-Tests.)
- Schritt 5 meldet: „Container laufen (Dashboard und Import) · / = 200 · /dashboard/ = 200 (Anmeldemaske)“.
- Nach dem Start rechnet das Vorladen rund 2 Minuten; in dieser Zeit können die ersten Seiten langsamer sein.

## Im Browser prüfen

1. **Bundesliga** (heute Mo/Di 16./17.11.): Kopf „Kommende Spiele · Saison 2026/27 · ab …“, Abschnitt **Spieltag 10** (Fr 20.11. – So 22.11., 9 Spiele) mit Spalte Datum, Anstosszeiten fett, KPI-Werte vorhanden. Ab Samstag 21.11. erscheint zusätzlich Spieltag 11.
2. **LaLiga**: Spieltag 13 (Fr 20.11. – Mo 23.11., 10 Spiele).
3. Pfeil **◀**: „Ausgewählter Spieltag · Spieltag 9“ (bzw. 12 bei LaLiga) mit Ergebnissen, Zeilen grau. Pfeil **▶** von den kommenden Spielen aus: höchstens 2 Spieltage weiter (Bundesliga bis Spieltag 12), dann ist ▶ ausgegraut. „Zu den kommenden Spielen“ führt zurück.
4. **Top Anomalien**: vier Kästchen oben (je Liga Spieltag und „noch … Spiele“), Karten mit Datum und Anstoss.
5. **Datenimport/API** (falls eine Fassung wartet): unten im Kasten die Tabelle „So sieht das Dashboard nach der Übernahme aus“.
6. Fusszeile: „Version 0.16 – Kommende Spieltage“.
7. Am **Wochenende** (21./22.11.): gespielte Spiele grau mit „Ergebnis folgt“, nach der Freigabe am Montag mit Ergebnis; ein angepfiffenes Spiel verschwindet aus den Top Anomalien.
