# Release: Version 0.20 – Fundament

**Stand:** 19.11.2026 · Version 0.20 · Entscheidungen Carsten 19.11.2026 (Entscheidungsprotokoll, Releaseplan in `01`, Abschnitt 0) · Prüfprotokoll `docs/tests/pruefprotokoll_0_20.md`

**Commit:** Version 0.20: Fundament – Signalqualität, Schnappschuss je Spiel, Statusmodell, 48-Stunden-Grenze

## Was ändert sich?

- **Signalqualität statt Prognosewert:** überall „Signalqualität stark / mittel / gering“ (bisher „Prognosewert hoch / mittel / gering“). Die Zahlen bleiben gleich: Vollvergleich über alle 11'978 Spiele, einzige Änderung „hoch“ → „stark“. In `schwellen.toml` heisst das Feld jetzt `signalqualitaet`.
- **Schnappschuss je Spiel:** Der Container `soccer-import` friert jede Stunde die Werte der Spiele ein, die in der nächsten Stunde angepfiffen werden. Eine Datei je Spiel, nie überschrieben. Beim ersten Lauf entstehen die Schnappschüsse aller gespielten Spiele beider Saisons (als „nachträglich“ markiert, rund 15 Sekunden). Gespielte Spiele zeigen diese Werte.
- **Gespielt erst nach 2 Stunden:** Bis Anpfiff + 2 Stunden bleibt ein Spiel normal (mit Termin), danach grau mit „Gespielt“, nach dem Import mit Ergebnis. Ohne Anstosszeit ab Mitternacht. „Ergebnis folgt“ gibt es nicht mehr.
- **Top Anomalien ohne Nachrücken:** Die Liste steht vor dem ersten Anpfiff fest. Gespielte Spiele bleiben grau an ihrem Platz (Dashboard und Startseite der Vorschau).
- **„Werte ab …“ auch auf der Website:** Spieltag-Seite (Kachel „Werte ab 5.12.“) und Spielseite (Text statt Kennzahlen). Damit ist die Lücke vom 19.11. geschlossen.
- **Datenstand:** Der Hinweis „Spielplan zuletzt aktualisiert am …“ erscheint erst, wenn der letzte erfolgreiche Import mehr als **48 Stunden** zurückliegt (bisher 3 Tage).
- **Website-Vorschau, nur Texte:** „Zu wenig Daten“ statt „Nicht gewertet“; „Nachholspiel · Spieltag 13“; Zählform „9 Spiele + 1 Nachholspiel · 4 auffällige Spiele“; „Keine der 7 Kennzahlen überschreitet ihre Schwelle.“ (Zahl dynamisch). Das Aussehen bleibt bis 0.21.
- **Absicherung „gewertet“:** Meldet die API für ein schon gespieltes Spiel nachträglich „am grünen Tisch gewertet“, bleibt es gespielt mit dem Ergebnis vom Platz (Hinweis in der Datenqualität).
- **Reiter Datenimport/API:** neuer Kasten „Schnappschüsse“ (letzter Lauf, neu, wartend, Fehler).

## Einspielen

Wie immer in `tmux`: `bash /docker/football-dashboard/tools/einspielen.sh github`, mit `j` abschliessen, wenn alles passt. Keine Zusatzschritte: Der Container `soccer-import` startet den ersten Schnappschuss-Lauf von selbst gleich nach dem Neustart.

## Erwartungswerte

- Git-Stand vorher: `537b4a4`.
- Schritt 4 des Einspielens: rund **612 bestanden, 15 übersprungen, 18 ausgelassen** (langsame Tests; bisher 594), keine Fehler; Dauer rund 9 Minuten.
- Schritt 5: „Container laufen (Dashboard, Import, Vorschau) · / = 200 · /dashboard/ = 200 (Anmeldemaske)“ und „/vorschau/ = 401 (Passwortabfrage der Vorschau)“.
- Dashboard-Fusszeile: „Version 0.20 – Fundament (Signalqualität, Schnappschuss, Statusmodell)“.
- Rund eine Minute nach dem Einspielen: `docker logs soccer-import --tail 5` zeigt eine Zeile „Schnappschüsse: … neu, 0 wartend – ok“ mit rund 1'900 neuen Schnappschüssen (alle gespielten Spiele beider Saisons). Danach jede volle Stunde eine Zeile, meist mit „0 neu“.
- Platz auf dem Server: rund 16 MB unter `import/schnappschuesse/`.

## Im Browser prüfen

1. **Dashboard, Top Anomalien:** Die Karten zeigen „Signalqualität stark / mittel / gering“. Der Text unten enthält „Die Liste steht vor dem ersten Anpfiff fest: Gespielte Spiele bleiben ausgegraut an ihrem Platz, es rückt kein anderes Spiel nach.“ Am Wochenende: Ein Spiel bleibt bis 2 Stunden nach Anpfiff normal und ist danach grau mit „Gespielt“.
2. **Dashboard, Reiter Datenimport/API:** Unten steht „Schnappschüsse (Werte vor dem Anpfiff)“ mit grünem ✓ und je Liga der Zahl „vorhanden“ (zusammen rund 1'900).
3. **Dashboard, Ligaseite und Sensitivitätsanalyse:** nirgends mehr „Prognosewert“; Spalte bzw. Legende „Signalqualität“.
4. **Vorschau, Spieltag-Seite** (z. B. Bundesliga): Kacheln des übernächsten Spieltags zeigen „Werte ab …“ statt einer Bewertung; Zusammenfassung „… 9 Spiele · 3 auffällige Spiele“.
5. **Vorschau, Spielseite eines gespielten Spiels** (über die Zeitreise, z. B. `?datum=2026-11-23`): „Endstand …“, darunter „Gespielt: Die Werte wurden mit den Daten vor dem Spiel berechnet.“ bzw. bei den nachgeholten „Werte nachträglich mit den Daten vor dem Spiel berechnet.“
6. **Neue Texte zum Absegnen** (bisher ohne Wortlaut von dir):
   - Hinweis bei korrigiertem Ergebnis: „**Endstand:** Ergebnis nachträglich korrigiert“.
   - Spiel angepfiffen, aber das Ergebnis des vorherigen Spiels fehlt noch (selten): „Die Werte werden nachträglich mit den Daten vor dem Spiel berechnet, sobald das Ergebnis des vorherigen Ligaspiels übernommen ist.“ (Kachel: „Werte folgen“).
   - Dashboard-Ligaseite im selben Fall: „Werte folgen nachträglich, sobald das Ergebnis des vorherigen Spiels übernommen ist“.
7. Sag mir, ob alles passt.
