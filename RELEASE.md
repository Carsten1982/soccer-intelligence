# Release: Version 0.21.1 – Entwürfe vom 20.11. und Vorschau 5 Tage

**Stand:** 20.11.2026 · Version 0.21.1 · Entscheidungen Carsten 20.11.2026 · Entwürfe und Briefings vom 20.11.2026 (Template-Briefing 2, 7, 8; Entscheidungsprotokoll Beschluss 13)

**Commit:** Version 0.21.1: Entwürfe vom 20.11. und Vorschau 5 Tage

## Was ändert sich?

- **Vorschau 5 statt 7 Tage** (Dashboard und Website): Ein weiterer Spieltag erscheint erst, wenn sein erstes Spiel höchstens 5 Tage entfernt ist. Ein Spieltag ab Freitag kommt also am Sonntag davor, einer ab Samstag am Montag. Ausnahme bleibt die englische Woche: Ein Dienstag-Spieltag erscheint am Donnerstag davor. Nachhol- und vorgezogene Spiele ebenfalls erst 5 Tage vorher.
- **Signalqualität kräftiger:** Chips, Balken, Kacheln und Karten in den neuen Grüntönen aus dem Entwurf.
- **Spielseite:** Der Block „Weitere Spiele dieses Spieltags“ ist weg. „Alle Spiele des Spieltags“ ist jetzt ein Textlink, „Wie entstehen diese Werte?“ die grosse Schaltfläche am Ende.
- **Spieltag:** Im SEO-Text unten fehlt der Satz „Wir bieten transparente Fußball-Statistiken …“.
- **Methodik:** Einstieg „Wie tief möchtest du einsteigen?“ als drei Karten (Ebene 1–3). Die gewählte Karte ist dunkelgrün; tiefere Ebenen werden ausgeblendet. „Weiter mit Zahlen“ und „Zur ausführlichen Auswertung“ öffnen die nächste Ebene. Die Ligen-Tabellen haben auf dem Handy keinen Scrollbalken mehr.
- **Handy:** Navigation und Sprachmenü in einer Zeile; auf schmalen Geräten steht im Sprachknopf „DE“ bzw. „EN“. Footer mit gleichmässigem Abstand.
- **Für 0.22 vorbereitet:** Entwurf des Abfrageplans in `docs/06_Datenlieferung.md`, Abschnitt 10.2 (Läufe bei Anpfiff + 2¼ Stunden). Noch nichts davon ist aktiv.

## Einspielen

Wie immer in `tmux`, aber diesmal mit einem neuen Sitzungsnamen, damit keine alte Sitzung im Weg ist:

```bash
tmux new -s release0211
```

```bash
bash /docker/football-dashboard/tools/einspielen.sh github
```

Später wieder verbinden mit `tmux attach -t release0211`. **Während der Tests keine Tasten drücken**, auch keine Pfeiltasten. Am Ende `j`, danach `exit`.

## Erwartungswerte

- Git-Stand vorher: `006a150` (bzw. `ddf4578`, falls der Doku-Nachtrag zu 0.21 schon zusammengeführt ist).
- Schritt 4: rund **663 bestanden, 16 übersprungen, 18 ausgelassen**, keine Fehler.
- Schritt 5: alle Container laufen, `/` = 200, `/dashboard/` = 200, `/vorschau/` = 401.
- Dashboard-Fusszeile: „Version 0.21.1 – Entwürfe 20.11. und Vorschau 5 Tage“.

## Im Browser prüfen

1. **Vorschau 5 Tage:** Am Freitag oder Samstag zeigt die Spieltag-Seite (Dashboard und Website) nur den laufenden Spieltag, ausser bei englischen Wochen. Der nächste Wochenend-Spieltag erscheint am Sonntag bzw. Montag. Mit der Zeitreise prüfbar, z. B. Bundesliga `?datum=2027-01-09` (zwei Tabs: 15 und 16) und `?datum=2027-01-10` (drei Tabs: 15, 16 und 17).
2. **Kacheln und Chips** der Signalqualität: deutlich kräftigeres Grün als bisher.
3. **Spielseite:** unten kein „Weitere Spiele dieses Spieltags“ mehr; zuerst der Textlink „Alle Spiele des Spieltags“, darunter die dunkle Schaltfläche „Wie entstehen diese Werte?“.
4. **Methodik:** Die drei Karten oben anklicken: „Kurz erklärt“ zeigt nur Ebene 1, „Mit Zahlen“ Ebene 1 und 2, „Alles im Detail“ alles inklusive Excel-Download. Unter Ebene 1 führt „Weiter mit Zahlen …“ zu Ebene 2.
5. **Handy:** Navigation in einer Zeile, Sprachknopf „DE“; Methodik-Tabellen ohne seitliches Scrollen.
6. **Noch offen aus 0.21** (gerne mit dieser Prüfung): Glossar, Texte der Archivseite, Namen der 12 Aufsteiger, Frage „Auffällige Spiele je Spieltag“ (alte RELEASE.md, Punkte 8 und 9; Text steht im Git-Verlauf und in meiner Nachricht).
7. **Zum Abfrageplan** (`06`, 10.2) brauche ich vor 0.22 deine Entscheidungen: automatische Übernahme der Abendläufe (nur Endstand und Status), Sicherheitslauf, Inhalt der E-Mail-Alarme.
8. Sag mir, ob alles passt.
