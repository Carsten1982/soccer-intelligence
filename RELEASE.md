# Release: Version 0.22 – Daten nach jedem Spiel

**Stand:** 20.11.2026 · Version 0.22 · Spezifikation `docs/06_Datenlieferung.md`, Abschnitt 10.2 (Beschlüsse Carsten 20.11.2026: B1–B5, F1–F3)

**Commit:** Version 0.22: Daten nach jedem Spiel

## Was ändert sich?

- **Lauf nach jedem Spiel:** Je Anstosszeit holt der Import bei **Anpfiff + 2¼ Stunden** Endstand, Status und alle Statistiken der beendeten Spiele. Läufe, die weniger als 30 Minuten auseinanderliegen, werden zusammengelegt; am Samstag 21.11. sind es 8 Läufe.
- **Keine Freigabe mehr:** Jede fehlerfreie Fassung wird sofort übernommen, mit Backup vorher.
  - Nur eine Fassung mit **Fehlern oder neuen Warnungen** wartet im Reiter Datenimport/API auf „Übernehmen“ oder „Verwerfen“.
  - **Kritische Spiele** werden einzeln zurückgehalten und warten auf deinen Entscheid; alles andere wird übernommen. Kritisch heisst: Endstand passt nicht zu den Toren, späte Korrektur, Zuordnung.
- **Wiederholung:** Scheitert ein Lauf oder fehlen danach noch Werte, folgt 1 Stunde später eine Wiederholung, höchstens zwei.
- **Kontrolllauf** täglich um 04:00 wie bisher, montags über die ganze Saison.
- **Backups gestaffelt:** alle der letzten 14 Tage, je Woche das letzte (8 Wochen), je Monat das letzte (12 Monate), je Saison das letzte dauerhaft. Bisher waren es die letzten 30.
- **Reiter Datenimport/API:**
  - Neuer Block „Läufe heute“ mit gelaufenen und geplanten Läufen.
  - Im Protokoll eine Spalte „Anlass“.
  - In der Statusleiste der nächste Lauf mit Anlass.
- **Website:**
  - Anzeigenamen der 12 Aufsteiger, wie freigegeben.
  - „Athletic Bilbao“ statt „Athletic Club“; die Adressen bleiben gleich.
  - Startseite ohne „Aktueller Datenstand“ unter den Top-Spielen.
  - Glossar freigegeben.
- **Für 0.23 vorbereitet:** Jeder Lauf schreibt eine Zeile ins Ereignisprotokoll (`import/ereignisse.jsonl`). Daraus entstehen später Alarme und Statusmail.

## Einspielen

```bash
tmux new -s release022
```

```bash
bash /docker/football-dashboard/tools/einspielen.sh github
```

Später wieder verbinden mit `tmux attach -t release022`. **Während der Tests keine Tasten drücken.** Am Ende `j`, danach `exit`.

**Bitte vor dem Zusammenführen warten, bis der Testlauf im Pull Request grün ist.**

## Erwartungswerte

- Git-Stand vorher: `9efe682`.
- Schritt 4: rund **680 bestanden, 16 übersprungen, 18 ausgelassen**, keine Fehler.
- Schritt 5: alle Container laufen, `/` = 200, `/dashboard/` = 200, `/vorschau/` = 401.
- Dashboard-Fusszeile: „Version 0.22 – Daten nach jedem Spiel“.
- Ein Lauf nach dem Spiel braucht rund 15–30 Abfragen. Am Samstag sind es zusammen rund 150–250, unter der eigenen Grenze von 500.

## Im Browser prüfen

1. **Reiter Datenimport/API** gleich nach dem Einspielen:
   - Betriebsart „automatisch – nach jedem Spiel und um 04:00, ohne Freigabe“.
   - „nächster“ mit Uhrzeit und Anlass.
   - Block „Läufe heute“ mit den geplanten Läufen: je Anstosszeit des Tages ein Lauf 2¼ Stunden später (Anpfiff 20:30 → Lauf 22:45).
2. **Nach dem ersten Spiel des Abends**, etwa 2¼ Stunden nach Anpfiff plus einige Minuten:
   - Im Protokoll eine Zeile „nach dem Spiel“ mit Status „übernommen (automatisch)“.
   - Auf der Spieltag-Seite (Dashboard und Website) der Endstand des Spiels, ohne Warten bis 04:00.
3. **Am nächsten Morgen:**
   - Im Protokoll ein „Kontrolllauf“ um 04:00.
   - Im Ordner `backup/` neue Dateien `…_vor_import.xlsx`. Nachsehen, nur lesend:

   ```bash
   ls -lt /docker/football-dashboard/backup | head
   ```
4. **Website:**
   - Athletic Bilbao bei einem LaLiga-Spiel.
   - Ein Aufsteiger mit dem neuen Namen, zum Beispiel „FC Schalke 04“ bzw. „Schalke 04“ auf Englisch.
   - Startseite ohne „Aktueller Datenstand“ unter den Top-Spielen.
5. **Erscheint „Ihre Entscheidung“**, einen der beiden Knöpfe wählen. Der Entscheid wirkt ab dem nächsten Lauf.
6. Sag mir, ob alles passt. Parallel richtest du die zwei Postfächer für 0.23 ein.
