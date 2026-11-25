# Release: Version 0.26 – Frühere Spieltage und Feinschliff

**Stand:** 25.11.2026 · Version 0.26 · Design Version 550 (Beschlüsse 53–58), Entscheide Carsten 25.11.2026

**Commit:** Version 0.26: Frühere Spieltage und Feinschliff

## Was ändert sich?

- **Spieltag-Seite:** unter der Liste der Link „Frühere Spieltage ansehen“ (zum vorherigen Spieltag im Archiv; am 1. Spieltag einer Saison nicht).
- **Archivseiten:** gespielte Spiele mit der neuen Kachel (Tore je Team, „2 von 3 bestätigt“).
- **Ergebnisseite:** Hinweisfeld nur noch bei Ausnahmen (fehlende Statistik, Korrektur, nachträglich berechnet, Aufsteiger, Nachholspiel); zwei getrennte Tabellen; „Kein Ligadurchschnitt – feste Marke 2,5.“
- **Spielseite:** „… kein verlässlicher Hinweis für kommende Spiele“; Chips immer rechtsbündig; lange Teamnamen brechen sauber um.
- **Impressum:** neues Skript `tools/impressum_einrichten.sh` – deine Angaben kommen nur in `.env` auf dem Server.

## Einspielen

```bash
tmux new -s release026
```

```bash
bash /docker/football-dashboard/tools/einspielen.sh github
```

Danach einmalig das Impressum eintragen (fragt Name, Strasse, PLZ und Ort, Land ab und zeigt das Ergebnis vor dem Speichern):

```bash
bash /docker/football-dashboard/tools/impressum_einrichten.sh
```

## Erwartungswerte

- Git-Stand vorher: `9b84183` (oder der Stand mit den Doku-Commits).
- Schritt 4: rund **750 bestanden**, keine Fehler (hier ohne echte Daten: 751 bestanden, 18 übersprungen).
- Schritt 5: alle Container laufen, `/` = 200, `/dashboard/` = 200, `/vorschau/` = 401; drei Testmails.
- Dashboard-Fusszeile: „Version 0.26 – Frühere Spieltage und Feinschliff“.
- `impressum_einrichten.sh`: „✅ Gespeichert in .env.“ und „✅ Vorschau übernimmt die Angaben …“.

## Im Browser prüfen

1. **Spieltag-Seite:** unten „Frühere Spieltage ansehen“ → Archivseite des vorherigen Spieltags.
2. **Archivseite:** gespielte Spiele mit Toren und Bilanz; mit den Pfeilen blättern; Kachel antippen → Ergebnisseite.
3. **Ergebnisseite:** im Normalfall kein Hinweisfeld; zwei getrennte Tabellen („Auffälligkeiten“, „Ohne Auffälligkeit“).
4. **Spielseite (Handy):** Chips rechtsbündig, lange Namen (z. B. „Borussia Mönchengladbach“) brechen zwischen den Wörtern um.
5. **Impressum** (`/vorschau/de/impressum/`): deine Angaben statt Platzhalter.
6. **Aus 0.24 offen:** HSTS (F12 → Netzwerk → Strg+F5 → `site.css` → Headers: `strict-transport-security`).
7. Sag mir, ob alles passt – dann bereite ich den Livegang (0.27) vor.
