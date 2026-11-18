# Release: Version 0.19.1 – Anpassungen nach der Abnahme von 0.19

**Stand:** 18.11.2026 · Version 0.19.1 · Rückmeldungen und Entscheidungen Carsten 18.11.2026 · Prüfprotokoll `docs/tests/pruefprotokoll_prognosewert.md`, Abschnitt 6

**Commit:** Version 0.19.1: Anpassungen nach der Abnahme – Texte, Schwellen je Liga, Cache-Versionsnummer, Bereinigungen B1, B3–B6

## Was ändert sich?

- **Top Anomalien:** Der Text unter der Liste hat drei Zwischentitel: „Berücksichtigte Spiele“, „Auswahl der Auffälligkeiten“, „Verteilung der Spiele“.
- **Navigation:** Sensitivitätsanalyse steht jetzt vor Datenqualität.
- **Sensitivitätsanalyse:**
  - Erklärfeld und aufklappbare Felder nach deinem Vorschlag. Die Rechnung im Beispiel geht jetzt auf (63,44 − 51,57 = +11,87).
  - Bei „Alle Ligen“ stehen die gültigen Schwellen je Liga klein unter dem Feld (z. B. „PL 10 · SA 15“).
  - Bei einer einzelnen Liga steht die Schwelle im Feld. Bisher blieb es nach dem Liga-Wechsel leer (Fehler behoben).
  - Zeilen ohne Schwelle bleiben leer.
- **KPI 03 bei genau 0,00 %:** Unter „Keine statistische Besonderheit“ steht jetzt der Satz „In den bisherigen Spielen beider Teams fielen im Schnitt genau 2,5 Tore – so viele wie die Marke.“
- **Datenqualität:** „Schüsse < aufs Tor + daneben“ ist nur noch ein Hinweis (u. a. Spiel-ID 11344). Darum gibt es deutlich weniger Warnungen.
- **Website-Vorschau:** CSS und JS tragen eine Versionsnummer. Nach einem Release ist kein Strg+F5 mehr nötig.
- **Schneller:** Die Sensitivitätsanalyse rechnet ihre Fälle in rund 5 statt 50 Sekunden; das Vorladen nach dem Start ist entsprechend kürzer. Der Spielplan wird etwas schneller eingelesen. Alle Werte sind unverändert (Vollvergleich).
- **Anmeldung:** Das Anmelde-Cookie wird mit der neuen Streamlit-Funktion gesetzt (die alte fällt bei einem Update weg). Für dich ändert sich nichts.

## Einspielen

Wie immer in `tmux`: `bash /docker/football-dashboard/tools/einspielen.sh github`, mit `j` abschliessen, wenn alles passt. Keine Zusatzschritte.

## Erwartungswerte

- Git-Stand vorher: `cd45076`.
- Schritt 4 des Einspielens: rund **594 bestanden, 15 übersprungen, 18 ausgelassen** (langsame Tests), keine Fehler; Dauer rund 9 Minuten.
- Schritt 5: „Container laufen (Dashboard, Import, Vorschau) · / = 200 · /dashboard/ = 200 (Anmeldemaske)“ und „/vorschau/ = 401 (Passwortabfrage der Vorschau)“.
- Dashboard-Fusszeile: „Version 0.19.1 – Anpassungen nach Abnahme 0.19 (Texte, Schwellen je Liga, Tempo)“.
- Sensitivitätsanalyse nach einem Neustart: Die Meldung „wird vorbereitet“ verschwindet nach rund 10 Sekunden (bisher rund 50).
- Datenqualität: Die Zahl der Warnungen sinkt deutlich (die Schusssummen zählen jetzt als Hinweise).

## Im Browser prüfen

1. **Anmeldung (wichtig, wegen der neuen Cookie-Funktion):**
   - Abmelden und neu anmelden.
   - Dann einen **zweiten Tab** mit `/dashboard` öffnen: Er muss ohne neue Anmeldung direkt das Dashboard zeigen.
2. **Reiter:** Die Reihenfolge ist Top Anomalien · Ligen · **Sensitivitätsanalyse** · **Datenqualität** · Datenimport/API.
3. **Top Anomalien:** Der Text unten hat drei fette Zwischentitel und endet mit „Maximale Anzahl: 4 Spiele“.
4. **Sensitivitätsanalyse:**
   - „Alle Ligen“: Unter den Feldern mit „je Liga“ stehen klein die Schwellen, z. B. bei KPI 02 weniger „PL 10 · SA 15“.
   - Dann Liga **Premier League** wählen: KPI 02 weniger zeigt **10.0** im Feld, KPI 09 mehr **10.0**.
   - Zurück auf „Alle Ligen“: wieder „je Liga“ mit den kleinen Werten.
5. **Erklärfeld:** Im Beispiel stehen „63,44 − 51,57 = +11,87 Prozentpunkte“ und „mit 95 % Sicherheit zwischen +5,06 und +18,25 Pp.“. Die aufklappbaren Felder zeigen deine Texte.
6. **Vorschau** (`/vorschau`): Seiten sehen aus wie vorher, auch **ohne** Strg+F5.
7. Sag mir, ob die Texte so passen.
