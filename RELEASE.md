# Release: Version 0.24 – Layout-Anpassungen und Qualitätsrunde (in Arbeit)

**Stand:** 24.11.2026 · Version 0.24 · Designanpassungen 24.11.2026 (Version 508) · Reviews Front- und Backend folgen

**Commit:** Version 0.24: Layout-Anpassungen und Qualitätsrunde

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

Noch nicht – das Release ist in Arbeit.

## Erwartungswerte

- Testreihe (Stand 24.11.2026, ohne echte Daten): 744 bestanden, 18 übersprungen. Auf dem Server kommen die Tests mit echten Daten dazu.

## Im Browser prüfen

1. Startseite (DE/EN): „Wie lese ich das?“ aufklappen – neuer Satz bei „Signalqualität“.
2. Spielseite mit einer Karte „Nicht eingestuft ⓘ“: ⓘ antippen – neuer Erklärsatz.
3. Handy: Spielseite – „Zahlen im Detail“ etwas höher; Browserleiste grün (Android). Im Browser-Menü „Zum Startbildschirm“: Icon mit den drei Balken, Name „Soccer Intel“.
4. **Komprimierung und HSTS** (Computer, Chrome): Vorschau öffnen, **F12** → Reiter „Netzwerk“ → **Strg+F5** (ohne Zwischenspeicher neu laden) → `site.css` anklicken → Antwort-Header. Erwartet: `content-encoding: gzip` (oder `br`) und `strict-transport-security: max-age=31536000`. Vorher (24.11.): beides fehlte, `content-length: 61064`.
