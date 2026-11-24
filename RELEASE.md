# Release: Version 0.24 – Qualität und Sicherheit

**Stand:** 24.11.2026 · Version 0.24 · Designanpassungen 24.11.2026 (Version 508) · Reviews Front- und Backend (Prüfprotokoll `docs/tests/pruefprotokoll_0.24_reviews.md`)

**Commit:** Version 0.24: Qualität und Sicherheit

## Was ändert sich?

- **Startseite, „Wie lese ich das?“:** neuer Satz zur Signalqualität („… in früheren Spielen als Prognose bestätigt …“), Deutsch und Englisch.
- **Spielseite, Chip „Nicht eingestuft ⓘ“:** neue Erklärung („Ein Blick auf vergangene Spiele zeigt: …“), Deutsch und Englisch.
- **Suchmaschinen:** Spielseiten kommen erst in den Index, wenn mindestens 6 der 8 Kennzahlen bewertet sind (gilt ab dem Livegang). Die Auszeichnung `SportsEvent` entfällt.
- **Handy:** Die Seite lässt sich mit eigenem Icon „zum Home-Bildschirm hinzufügen“ (Web-App-Manifest), die Browserleiste wird grün (`theme-color`), „Zahlen im Detail“ ist mit 44 px leichter anzutippen.
- **Schneller bei vielen Besuchern:** Die Website speichert fertige Seiten je Minute. Die Startseite kommt in rund 0,001 s statt 0,4 s; 10 gleichzeitige Besucher warten nicht mehr bis zu 7,6 s.
- **Sicherheit (Backend-Review):** Zeitlimit und strenge Längenprüfung im Website-Dienst, Sperre nach Fehlversuchen im Dashboard nicht mehr umgehbar, Kontakt-Bremse ohne Lücke, kein gemischter Datenstand während des Tauschs, ZIP-Weg entfernt (nur noch `einspielen.sh github`), `no-new-privileges` und Speichergrenzen für unsere Container, `requests` 2.32.5.
- **Traefik-Labels (nur unsere Container):** Komprimierung und HSTS. Prüfung erst nach dem Livegang (`01`, Abschnitt 8).
- Bewertung beider Reviews: `docs/tests/pruefprotokoll_0.24_reviews.md`.

## Einspielen

Wie immer in tmux:

```bash
tmux new -s release024
```

```bash
bash /docker/football-dashboard/tools/einspielen.sh github
```

Neu: Es gibt nur noch den Weg über GitHub (der ZIP-Weg ist entfernt). Ohne Angabe gilt ebenfalls `github`.

## Erwartungswerte

- Git-Stand vorher: `efcc976`.
- Schritt 4: rund **740 bestanden**, einige übersprungen und ausgelassen, keine Fehler (hier ohne echte Daten: 742 bestanden, 18 übersprungen).
- Schritt 5: alle Container laufen, `/` = 200, `/dashboard/` = 200, `/vorschau/` = 401; drei Testmails.
- Dashboard-Fusszeile: „Version 0.24 – Qualität und Sicherheit“.

## Im Browser prüfen

1. Startseite (DE/EN): „Wie lese ich das?“ aufklappen – neuer Satz bei „Signalqualität“.
2. Spielseite mit einer Karte „Nicht eingestuft ⓘ“: ⓘ antippen – neuer Erklärsatz.
3. Handy: Spielseite – „Zahlen im Detail“ etwas höher; Browserleiste grün (Android). Im Browser-Menü „Zum Startbildschirm“: Icon mit den drei Balken, Name „Soccer Intel“.
4. **Komprimierung und HSTS** (Computer, Chrome): Vorschau öffnen, **F12** → Reiter „Netzwerk“ → **Strg+F5** (ohne Zwischenspeicher neu laden) → `site.css` anklicken → Antwort-Header. Erwartet: `content-encoding: gzip` (oder `br`) und `strict-transport-security: max-age=31536000`. Vorher (24.11.): beides fehlte, `content-length: 61064`.
5. **Tempo:** Startseite und Spieltag-Seite mehrmals schnell hintereinander aufrufen – sie sollten sofort da sein.
6. Sag mir, ob alles passt.
