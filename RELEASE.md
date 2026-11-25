# Release: Version 0.25 – Auswertung nach dem Spiel

**Stand:** 25.11.2026 · Version 0.25 · Design-Spezifikation Release_08 (Entwürfe Version 544), Entscheide Carsten 25.11.2026

**Commit:** Version 0.25: Auswertung nach dem Spiel

## Was ändert sich?

- **Ergebnisseite:** Sobald ein Spiel einen Endstand hat, zeigt seine Spielseite (gleiche Adresse) die Auswertung: grosser Spielstand mit Halbzeit, Tabelle „Erwartet und tatsächlich“ (Ligadurchschnitt · Erwartungswert · Tatsächlich), bei Auffälligkeiten „✓ Bestätigt“ / „✗ Nicht bestätigt“ / „Bewertung folgt“ und die Signalqualität, darunter die Box „Statistisch auffällig ab“.
- **Regel:** Bestätigt, wenn der tatsächliche Wert in der erwarteten Richtung über bzw. unter dem Ligadurchschnitt liegt (Regelwerk 11.1, wie die Sensitivitätsanalyse). „Über 2,5 Tore“: mindestens 3 bzw. höchstens 2 Tore; „Beide Teams treffen“: Ja bzw. Nein.
- **Korrekturen:** Ändert sich nach dem Spiel eine Statistik, steht „Ergebnis oder Statistik nachträglich korrigiert“; es gelten immer die aktuellen Werte.
- **Spieltag-Seite:** gespielte Spiele am Ende der Liste, mit Toren je Team und Bilanz („2 von 3 bestätigt“, „Keine Auffälligkeiten“, „Bewertung folgt“, „Endstand folgt“). Antippen öffnet die Ergebnisseite.
- **Spielseite vor dem Spiel:** „Statistisch auffällig ab“, „nicht definiert“, graue Regelzeile, „Nicht eingestuft“ mit Satz „Diese Abweichung ist in der Bundesliga kein verlässlicher Hinweis …“ (ohne ⓘ), „Beide Teams treffen“ ohne Nachkommastellen („35 %“).
- **Texte:** neuer Startseiten-Satz, Methodik „Nicht eingestuft“, Signalqualität-Satz in der Spieltag-Legende und im Glossar.

## Einspielen

```bash
tmux new -s release025
```

```bash
bash /docker/football-dashboard/tools/einspielen.sh github
```

## Erwartungswerte

- Git-Stand vorher: `ea4ac3a` (der erste Versuch hat den Code schon geholt, aber nicht eingespielt; die Website lief weiter mit 0.24). Das Skript holt jetzt nur die Korrektur dazu.
- Schritt 4: rund **750 bestanden**, keine Fehler (hier ohne echte Daten: 749 bestanden, 18 übersprungen).
- Schritt 5: alle Container laufen, `/` = 200, `/dashboard/` = 200, `/vorschau/` = 401; drei Testmails.
- Dashboard-Fusszeile: „Version 0.25 – Auswertung nach dem Spiel“.

## Im Browser prüfen

1. **Spieltag-Seite** einer Liga mit gespielten Spielen (z. B. am Wochenende): gespielte Kacheln am Ende, mit Toren und Bilanz; Kopfzeile zählt alle Spiele mit Auffälligkeit.
2. **Gespielte Kachel antippen:** Ergebnisseite mit Spielstand, „Halbzeit …“, Tabelle, ✓/✗; Box „Statistisch auffällig ab“ auf- und zuklappen. Auch auf Englisch.
3. **Kommendes Spiel öffnen:** „Zahlen im Detail“ – „Statistisch auffällig ab“, graue Regelzeile; bei „Nicht eingestuft“ der neue Satz direkt in der Karte; „Beide Teams treffen“ als „… %“ ohne Nachkommastellen.
4. **Startseite:** neuer Satz unter „Fußballspiele durchleuchtet.“; gespielte Top-Spiele führen zur Ergebnisseite.
5. **Handy:** Ergebnisseite bei 360–412 px ohne Querscrollen, Teamnamen brechen nur zwischen Wörtern um.
6. **Aus 0.24 offen:** Komprimierung und HSTS (F12 → Netzwerk → Strg+F5 → `site.css`: `content-encoding` und `strict-transport-security`), Tempo auf dem Handy mit gutem Netz.
7. Sag mir, ob alles passt.
