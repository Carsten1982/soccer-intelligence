# Release: Version 0.18 – Website nach den Entwürfen (Startseite, Spieltag, Matchdetail)

**Stand:** 17.11.2026 · Version 0.18 · Entscheidungen Carsten 17.11.2026 (Q1–Q7) · Konzept und Protokoll `docs/08_Website.md` v1.1

**Commit:** Version 0.18: Website nach den Entwürfen – Startseite, Spieltag und Matchdetail je Paarung

## Was ändert sich?

- **Startseite** der Vorschau (`/vorschau/`, bisher Weiterleitung auf den Spieltag) nach Entwurf 1d: „Fußballspiele durchleuchtet.“, Ranking **„Die auffälligsten Spiele“** = genau die Top Anomalien des Dashboards (höchstens 4), in Pausen eine Karte mit **Tage-Zähler**, Liga-Knöpfe, „So funktioniert’s“, Block „Von einem Fußballfan gebaut“ mit Foto bzw. Platzhalter, SEO-Text.
- **Spieltag** genau nach Entwurf 3d (dunkler Kopfbereich mit Liga-Auswahl, Kacheln im Raster). Neu sortiert wie im Entwurf: Stark → Leicht → Ohne → übrige nach Anstoss; Nachhol- und vorgezogene Spiele stehen nicht mehr gesammelt am Ende, sondern mittendrin.
- **Matchdetail**: **jede Paarung hat eine eigene Seite** `/vorschau/spiel/<Spiel-ID>` (Klick auf eine Kachel oder einen Eintrag im Ranking). Scoreboard mit Formkurve, Kernaussage, Auffälligkeiten mit Balken und „Zahlen im Detail“, Liste „Im Normalbereich“, Hinweise für Nachholspiel, vorgezogen, gespielt und nicht gewertet. Umgesetzt nach Q1–Q5 (Gelbe Karten als Summe Heim + Gast, sonst Mittelwert; Über 2,5 Tore mit Marke 2,50; einzelne vorläufige Kennzahl schraffiert unter Normalbereich; Endstand bzw. „Ergebnis folgt“).
- Die Vorschau rechnet beim Start alles einmal vor: Schon der erste Aufruf ist schnell.
- Neuer Ordner auf dem Server **`website-bilder/`** für das Foto (nur lesend eingebunden, nicht in Git). Dashboard, Import und Platzhalter unverändert.

## Einspielen

1. Wie immer in `tmux`: `bash /docker/football-dashboard/tools/einspielen.sh github`, mit `j` abschliessen, wenn alles passt. Keine Zusatzschritte: Das Skript baut die Vorschau seit 0.17 selbst mit.
2. **Foto (Q6), wann du willst:** Datei `portrait.jpg` (JPEG, quadratisch, mindestens 230 × 230 Pixel) mit WinSCP nach
   **`/docker/football-dashboard/website-bilder/`** hochladen. Kein Neustart nötig. Genaue Schritte: `docs/01_Technisches_Setup.md`, Abschnitt 6.3 „Foto der Startseite“. Prüfen:
   ```bash
   ls -l /docker/football-dashboard/website-bilder/portrait.jpg
   ```

## Erwartungswerte

- Git-Stand vorher: `49c2056`.
- Schritt 4 des Einspielens: rund **586 bestanden, 15 übersprungen, 16 ausgelassen**, keine Fehler; Dauer rund 9 Minuten.
- Schritt 5: „Container laufen (Dashboard, Import, Vorschau) · / = 200 · /dashboard/ = 200 (Anmeldemaske)“ und „/vorschau/ = 401 (Passwortabfrage der Vorschau)“.
- `docker logs soccer-vorschau --tail 5` zeigt „Vorschau: Daten vorgeladen“ (rund 10–30 Sekunden nach dem Start).
- Dashboard-Fusszeile: „Version 0.18 – Website (Startseite, Spieltag, Matchdetail)“.
- Lokal mit den echten Dateien des Probelaufs (Stand 15.11.) gemessen: Startseite 0,4 s, Spieltag 0,2 s, Matchdetail unter 0,2 s; Ranking am Sa 21.11. 10:00: 1. Monza – Fiorentina (Beide Teams treffen +71,72 %), 2. FC Augsburg – FSV Mainz 05 (Über 2,5 Tore +66,00 %), 3. Barcelona – Villarreal, 4. Union Berlin – RB Leipzig. Mit den neueren Daten auf dem Server können die Werte abweichen.

## Im Browser prüfen

1. `https://soccer-intelligence.com/vorschau` → Passwortabfrage → **Startseite**. Ranking mit bis zu 4 Spielen; der Eintrag stimmt mit dem Dashboard überein (Top Anomalien: gleiche Spiele, gleiche Kennzahl, gleicher Prozentwert). Klick auf einen Eintrag → Matchdetail.
2. Ohne Foto: runder grauer Platzhalter beim Block „Von einem Fußballfan gebaut“. Nach dem Hochladen: dein Foto (Seite neu laden).
3. „Spieltag ansehen“ → **Spieltag Bundesliga**: Kacheln im Raster, oben die stärksten. Liga wechseln (La Liga, Premier League, Serie A).
4. Eine Kachel anklicken → **Matchdetail**: oben „Zurück zum Spieltag“, Scoreboard mit „Letzte 5 Spiele“, darunter Auffälligkeiten. „Zahlen im Detail“ aufklappen: Bei **Gelben Karten** „Heim + Gast“ mit zweiteiliger Leiste, bei allen anderen „Je Mannschaft · Mittelwert beider Teams“; bei **Über 2,5 Tore** „Vergleichswert (Marke) 2,50“. „Zuklappen“ schliesst wieder.
5. **Zeitreise** (Adresse ergänzen):
   - `/vorschau/spieltag/bundesliga?datum=2026-11-21T16:00` → gespielte Spiele mit Ergebnis bzw. „Ergebnis folgt“; Klick darauf → Matchdetail mit „Endstand …“ bzw. „Ergebnis folgt“ und dem Hinweis „Gespielt: Die Werte wurden vor dem Spiel berechnet.“
   - Bayer Leverkusen – SC Paderborn 07 (Aufsteiger): `/vorschau/spiel/1575222` → „Nicht gewertet“ mit Hinweisbox.
   - `/vorschau/spieltag/la-liga?datum=2026-12-01` → zwei vorgezogene Spiele (Chip „Vorgezogen“), nach Anstoss einsortiert; Klick → Hinweis „Vorgezogen: Dieses Spiel gehört zum 23. Spieltag …“.
   - `/vorschau/?datum=2027-06-15` → Startseite mit Karte „Sommerpause – Die Saison ist beendet“.
6. Auf dem Handy: alle drei Seiten untereinander, kein seitliches Scrollen; Kacheln einspaltig.
7. Sag mir, was im Vergleich zu den Entwürfen noch anders aussehen soll.
