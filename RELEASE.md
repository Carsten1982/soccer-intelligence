# Release: Version 0.21 – Neue Website

**Stand:** 20.11.2026 · Version 0.21 · Releaseplan in `01`, Abschnitt 0 (Freigabe Carsten 19.11.2026) · Einzelheiten `docs/08_Website.md` (4, 4.1, 4.2, 7.3, 8, 9)

**Commit:** Version 0.21: Neue Website – Deutsch/Englisch, Adressen, SEO, Inhaltsseiten

## Was ändert sich?

- **Alle Seiten der Vorschau nach den Entwürfen P1** (19.11.2026): Startseite (Ranking als Karten mit Signalqualität-Balken), Spieltag (Kacheln je Stufe, Legende, „Wie lese ich das?“), Spielseite (Karten, „Weitere Spiele dieses Spieltags“), dazu Sprunglink „Zum Inhalt springen“, sichtbarer Fokus und Zeitzonen-Hinweis.
- **Deutsch und Englisch:** Sprachmenü oben rechts, jede Seite in beiden Sprachen, Vereinsnamen je Sprache (z. B. „Inter Mailand“ / „Inter Milan“). Für 12 Aufsteiger fehlt der Anzeigename noch; dort steht der Name der Datenquelle (Liste unten).
- **Neue Adressen:** `/vorschau/de/…` und `/vorschau/en/…` (z. B. `/vorschau/de/spiel/serie-a/monza-fiorentina-1550203/`). Alte Adressen leiten automatisch weiter.
- **Archivseite je Spieltag** (z. B. `/vorschau/de/spieltag/bundesliga/2026-27/10/`): alle Spiele mit Endstand und den Werten vor dem Spiel, Pfeile zum vorherigen und nächsten Spieltag. „Zurück zum Spieltag“ führt bei gespielten Spielen hierher.
- **Inhaltsseiten:** Methodik (drei Ebenen, Tabellen je Liga direkt aus der Schwellendatei, **Excel-Download**), Glossar (neu, Vorschlag), Kontakt (Formular sichtbar, Versand erst 0.22), Impressum, Datenschutz, Seite „nicht gefunden“.
- **Für Suchmaschinen vorbereitet:** Title, Description, canonical, hreflang, Open Graph, strukturierte Daten, robots.txt, Sitemap. Solange `index_ab` in `app/config/website.toml` leer ist (bis zum Livegang), kommt keine Spiel- oder Archivseite in den Index; die Vorschau bleibt ohnehin „noindex“. Die gelbe Vorschau-Leiste zeigt neu „Index: ja/nein“, also was nach dem Livegang gälte.
- **Betrieb:** Seiten 5 Minuten im Browser-Zwischenspeicher (Vorschau nie), bei Datenfehlern Status 503; Icons und Vorschaubild für Links in sozialen Netzwerken.
- **Dashboard, Reiter Datenimport/API:** neuer Kasten „Anzeigenamen der Website“ mit den Vereinen ohne Anzeigenamen.
- **Geprüft:** axe-core (Barrierefreiheit) auf allen Seitenarten in beiden Sprachen, Desktop und Handy: keine Befunde. Ohne JavaScript bleibt alles lesbar (alle Tabs untereinander).

## Einspielen

1. **Optional vorher, Betreiberangaben für Impressum und Datenschutz** (sonst steht dort ein gelber Platzhalter): in `/docker/football-dashboard/.env` drei Zeilen ergänzen, mit deinen Angaben statt der Beispiele (nie in Git, nie in den Chat):

   ```
   SI_IMPRESSUM_NAME="Vorname Nachname"
   SI_IMPRESSUM_ADRESSE="Strasse Nr|PLZ Ort|Schweiz"
   SI_KONTAKT_EMAIL="adresse@beispiel.ch"
   ```

   Laut Releaseplan gehört vor dem Livegang eine Projektadresse ins Impressum; für die Vorschau genügt, was du dort zeigen möchtest.
2. Wie immer in `tmux`: `bash /docker/football-dashboard/tools/einspielen.sh github`, mit `j` abschliessen, wenn alles passt.

## Erwartungswerte

- Git-Stand vorher: `10fa028`.
- Schritt 4 des Einspielens: rund **662 bestanden, 16 übersprungen, 18 ausgelassen** (langsame Tests; bisher 612; je nach echten Dateien auf dem Server leicht anders), keine Fehler; Dauer rund 9 Minuten.
- Schritt 5: „Container laufen (Dashboard, Import, Vorschau) · / = 200 · /dashboard/ = 200 (Anmeldemaske)“ und „/vorschau/ = 401 (Passwortabfrage der Vorschau)“.
- Dashboard-Fusszeile: „Version 0.21 – Neue Website (Deutsch/Englisch, Adressen, SEO, Inhaltsseiten)“.
- Nach der Anmeldung leitet `https://soccer-intelligence.com/vorschau/` auf `/vorschau/de/` weiter.
- Excel-Datei der Methodik: 23 Zeilen (eine je Schwelle) plus Blatt „Grundlage“.

## Im Browser prüfen

Den Browser-Zwischenspeicher musst du nicht leeren: CSS und JS tragen eine neue Versionsnummer.

1. **Startseite** `/vorschau/de/`: Ranking als Karten mit „Signalqualität stark“ und drei Balken, darunter „Alle Anstoßzeiten in mitteleuropäischer Zeit (MEZ/MESZ).“ Oben rechts das Sprachmenü „Deutsch“.
2. **Sprachwechsel:** Sprachmenü → „English“: dieselbe Seite auf Englisch (`/vorschau/en/`), Vereinsnamen englisch. Zurück mit „Deutsch“. Mit der Tastatur: Tab-Taste zeigt einen deutlichen dunkelgrünen Rahmen; als Erstes erscheint „Zum Inhalt springen“.
3. **Spieltag** (z. B. Serie A): grün gestreifte Kacheln je Stufe, Legende „Signalqualität: stark · mittel · gering“, „Wie lese ich das?“ klappt auf. Auf dem Handy steht die Legende in zwei Zeilen.
4. **Spielseite** einer Kachel: Scoreboard, Karten der Auffälligkeiten, unten „Weitere Spiele dieses Spieltags“. Mit der Zeitreise (z. B. `?datum=2026-11-24`) ein gespieltes Spiel öffnen: „Zurück zum Spieltag“ führt auf die **Archivseite** des Spieltags mit „Gespielt · 2:1“ auf den Kacheln.
5. **Methodik** (Navigation): drei Ebenen, Liga-Knöpfe über der Tabelle wechseln die Liga, „Excel-Datei herunterladen“ lädt die Datei herunter (in Excel öffnen: 23 Zeilen).
6. **Glossar** (Fusszeile), **Kontakt** (Schaltfläche grau mit Hinweis, Versand folgt mit 0.22), **Impressum** und **Datenschutz** (mit deinen Angaben aus `.env` oder gelbem Platzhalter), **Seite nicht gefunden** unter `/vorschau/de/xyz/`.
7. **Dashboard, Reiter Datenimport/API:** unten der Kasten „Anzeigenamen der Website“ mit 12 Vereinen.
8. **Zum Absegnen (Vorschläge von mir):**
   - **Glossar** DE/EN (ganze Seite).
   - **Archivseite:** Einleitung „Alle Spiele dieses Spieltags mit Endstand und den Werten, die vor dem Anpfiff berechnet wurden.“ / „All matches of this matchday with the final score and the values calculated before kick-off.“; Hinweis unten „Die Werte wurden mit den Daten vor dem jeweiligen Spiel berechnet.“; Title „Bundesliga Spieltag 10, Saison 2026/27: Spiele & Analysen | Soccer Intelligence“, Description „Alle Spiele des 10. Spieltags der Bundesliga 2026/27 mit Endständen und den Werten vor dem Anpfiff.“ (EN entsprechend).
   - **Methodik:** Satz „Begriffe wie Abweichung, Schwelle oder Mehrwert erklärt das Glossar.“ (Verlinkung zum Glossar, wie beschlossen).
   - **Vorschaubild** für soziale Netzwerke (`/vorschau/og-image.png`): Logo, „Soccer Intelligence“, die vier Ligen – sprachneutral.
   - **Anzeigenamen der 12 Aufsteiger** (Deutsch / Englisch): FC Schalke 04 / Schalke 04 · SC Paderborn 07 / SC Paderborn · SV Elversberg / SV Elversberg · Coventry City / Coventry City · Hull City / Hull City · Ipswich Town / Ipswich Town · Frosinone Calcio / Frosinone · AC Monza / Monza · FC Venedig / Venezia · Deportivo La Coruña / Deportivo La Coruña · FC Málaga / Málaga CF · Racing Santander / Racing Santander. Nach deinem OK trage ich sie ein.
9. **Eine Frage zur Methodik:** Der Entwurf zeigt je Liga „Auffällige Spiele je Spieltag“ (z. B. Bundesliga stark 1,4 · mittel 1,9 · gering 1,4). Diese Zahlen stehen nicht in der Schwellendatei und lassen sich daraus nicht berechnen; ich habe sie darum vorerst weggelassen. Woher stammen sie? Mein Vorschlag: Ich rechne sie bei der nächsten Neuberechnung der Schwellen mit und lege sie in `schwellen.toml` ab, dann erscheinen sie automatisch.
10. Sag mir, ob alles passt.
