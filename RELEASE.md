# Release: Version 0.12 – Sensitivitätsanalyse

**Stand:** 11.11.2026 · Version 0.12 · Spezifikation „Sensitivitätsanalyse“ und Designentwurf B (Freigabe Carsten 11.11.2026)

**Commit:** Version 0.12: Sensitivitätsanalyse ersetzt die Spielwiese

## Was ändert sich?

- Der Tab **„Simulation“** heisst jetzt **„Sensitivitätsanalyse“** (Adresse unverändert). Kopf „Soccer Intelligence“, darunter „Sensitivitätsanalyse“; neuer Hinweistext.
- Links nur noch **Liga** und **Saison**. Saisonnamen ohne „vorläufig“, z. B. „Aktuelle Saison (2026/27)“.
- **Eine Karte je KPI 02–09:** vier Schwellen (leicht/stark, positiv/negativ, ungleich möglich), daneben Häufigkeit leicht und stark (Anzahl, Ø pro Spieltag, Spieltagsabdeckung) und Ergebnisqualität mit der leichten Schwelle (Spiele, eingetroffen, Trefferquote, Grundquote aller Spiele, Mehrwert, Spanne 95 %, Empfehlung in sechs Stufen). Info-Texte an allen Kennzahlen.
- Gezählt werden nur abgeschlossene Spieltage; bei „Alle Ligen“ erscheint ein Hinweis mit den Spieltagen je Liga.
- **Unverändert:** KPI-Formeln, Rundung, `schwellen.toml`, Ligaseiten, Top Anomalien, Datenqualität (Vollvergleich gegen 0.11: 0 Abweichungen).
- Doku: KPI-Regelwerk v2.5 (Abschnitt 11), Dashboard-Briefing v5.0 (6.4), CHANGELOG, `01` Abschnitt 0.

## Erwartungswerte

- Git-Stand vorher: `b7d6c8f`.
- Tests beim Einspielen: rund **398 bestanden, 12 übersprungen** (bisher 376/12; 22 Tests mehr). Laufzeit etwa wie bisher.
- Erster Aufruf der Sensitivitätsanalyse: rund 50 Sekunden, danach sofort.

## Im Browser prüfen

1. **Navigation:** Der letzte Tab heisst „Sensitivitätsanalyse“. Kopf: „Soccer Intelligence“, darunter „Sensitivitätsanalyse“; die anderen Tabs unverändert.
2. **Links:** nur „Liga“ und „Saison“; voreingestellt „Alle Ligen“ und „Alle Saisons (2019/20–2025/26)“.
3. **Hinweis „Alle Ligen“:** 1'036 abgeschlossene Spieltage (Bundesliga 238, Premier League 266, Serie A 266, LaLiga 266).
4. **Karte KPI 02** mit ±20 / ±35: Häufigkeit leicht positiv **684** (0,66 je Spieltag, 48,94 %), Total leicht **1'332**, stark **103**; Ergebnisqualität positiv 684 Spiele, 374 eingetroffen, Trefferquote 54,68 %, Grundquote 46,56 %, Mehrwert **+8,12** (+4,24 bis +11,95), **Funktioniert**.
5. **KPI 05 negativ:** 36 Spiele, Zeile grau, „Zu wenige Daten“.
6. **Eingabe:** KPI 02 leicht positiv auf 40 setzen → stark positiv springt auf 40; der Wert erscheint blau. „Auf gültige Schwellen zurücksetzen“ stellt ±20 / ±35 wieder her.
7. **Bundesliga + „Aktuelle Saison (2026/27)“:** 9 abgeschlossene Spieltage, kein Hinweis „Alle Ligen“.
8. **Ligaseiten, Top Anomalien, Datenqualität:** unverändert.
