# Release: Version 0.17 – Öffentliche Website, Vorschau mit Seite Spieltag

**Stand:** 16.11.2026 · Version 0.17 · Entscheidungen Carsten 16.11.2026 (T1–T5, F1–F8, Datenstand, Zeitreise) · Konzept und Protokoll `docs/08_Website.md`

**Commit:** Version 0.17: Öffentliche Website als Vorschau unter /vorschau (Grundgerüst, Seite Spieltag, Zeitreise)

## Was ändert sich?

- **Neu: Vorschau der öffentlichen Website** unter `https://soccer-intelligence.com/vorschau`, mit Passwortabfrage des Browsers. Die öffentliche Adresse `/` (Platzhalter) und das Dashboard bleiben unverändert.
- **Seite Spieltag** nach der Übergabe-Datei (die Entwürfe Spieltag/Matchdetail kamen nicht an; Annahmen in `08`, Abschnitt 9): Liga-Auswahl, Zusammenfassung, Legende, „Wie lese ich das?“, Kacheln (Stark, Leicht, ohne Auffälligkeit, Nicht gewertet, Status, gespielt mit Ergebnis), Tabs bei englischer Woche, Nachhol- und vorgezogene Spiele mit Chip, Pausen-Karten, gelbe Warnbox bei altem Datenstand. Texte mit ß.
- **Zeitreise:** Auf jeder Seite der Vorschau `?datum=2026-12-01` oder `?datum=2026-11-21T16:00`, oder oben in der gelben Leiste einen Zeitpunkt wählen. Angenommen wird, dass der Import an diesem Tag um 04:00 gelaufen ist.
- Die Kacheln verlinken schon auf das Matchdetail; dort steht bis Version 0.18 „Diese Seite folgt später.“ Ebenso Methodik und Impressum.
- Neuer Container `soccer-vorschau`. Wie bei 0.15.2 arbeitet der laufende Einspiel-Aufruf noch mit der alten Fassung von `einspielen.sh` und baut den neuen Container beim ersten Mal **nicht** mit, daher die Schritte unten.

## Einspielen (einmalig zwei Schritte mehr)

1. Wie immer in `tmux`: `bash /docker/football-dashboard/tools/einspielen.sh github` und mit `j` abschliessen, wenn das Dashboard läuft.
2. **Danach** das Passwort der Vorschau setzen (Benutzername und Passwort frei wählbar, mindestens 10 Zeichen):
   ```bash
   bash /docker/football-dashboard/tools/vorschau_passwort.sh
   ```
   Erwartet: „Gespeichert in .env (Benutzer: …, Passwort nur als Hash).“
3. Den Vorschau-Container bauen und starten:
   ```bash
   cd /docker/football-dashboard && docker compose up -d --build soccer-vorschau
   ```
4. Prüfen (erwartet `401`, also Passwortabfrage):
   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/vorschau/
   ```

## Erwartungswerte

- Git-Stand vorher: `5b1e949`.
- Schritt 4 des Einspielens: rund **569 bestanden, 15 übersprungen, 16 ausgelassen**, keine Fehler; Dauer rund 9 Minuten.
- Schritt 5: „Container laufen (Dashboard und Import) · / = 200 · /dashboard/ = 200“ (noch die alte Prüfung).
- Nach Schritt 3 oben: `docker ps` zeigt `soccer-vorschau` „Up“; `curl … /vorschau/` = `401`.
- Dashboard-Fusszeile: „Version 0.17 – Website-Vorschau (Spieltag)“.

## Im Browser prüfen

1. `https://soccer-intelligence.com/vorschau` öffnen → Passwortabfrage → weiter auf **Spieltag Bundesliga**. Oben die gelbe Leiste „Vorschau – nicht öffentlich“.
2. Liga-Kacheln wechseln (La Liga, Premier League, Serie A); die gewählte ist hellgrün. „Aktueller Datenstand“ = Tag des letzten erfolgreichen Imports, Fusszeile „Stand: … Uhr“.
3. Kacheln: grün „Stark“/„Leicht“, weiss ohne Auffälligkeit, grau gestrichelt „Nicht gewertet“ (Aufsteiger), Pfeil rechts.
4. **Zeitreise** (Adresse ergänzen oder oben wählen):
   - `/vorschau/spieltag/bundesliga?datum=2026-11-21T16:00` → zwei Tabs (10. und 11. Spieltag), gespielte Spiele grau mit Ergebnis bzw. „Ergebnis folgt“.
   - `/vorschau/spieltag/la-liga?datum=2026-12-01` → 15. Spieltag „plus 2 vorgezogene Spiele“, am Ende mit Chip „Vorgezogen“.
   - `/vorschau/spieltag/bundesliga?datum=2026-12-23` → Karte „Winterpause – Nächster Spieltag am Fr 08.01.“.
   - `/vorschau/spieltag/bundesliga?datum=2027-01-09` → englische Woche mit drei Tabs.
5. Auf dem Handy öffnen: alles untereinander, kein seitliches Scrollen.
6. Die Annahmen A1–A9 in `docs/08_Website.md`, Abschnitt 9, ansehen und sagen, was anders sein soll.
