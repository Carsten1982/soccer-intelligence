# Release: Version 0.13 – Neue Schwellen und Sensitivitätsanalyse nach Entwurf C

**Stand:** 14.11.2026 · Version 0.13 · Festlegung der Schwellen und Designentwurf C (Freigabe Carsten 14.11.2026)

**Commit:** Version 0.13: neue Schwellen (positiv/negativ getrennt, KPI 03 je Liga) und Sensitivitätsanalyse nach Entwurf C

## Was ändert sich?

- **Neue gültige Schwellen** in `app/config/schwellen.toml`, positiv und negativ getrennt (KPI-Regelwerk 2.2). Alle Angaben in %, leicht positiv / stark positiv / leicht negativ / stark negativ:
  - KPI 02: 20 / 30 / −15 / −25 · KPI 04: 15 / 35 / −20 / −30 · KPI 05: 15 / 20 / −10 / −15 · KPI 06: 15 / 25 / −20 / −30 · KPI 07: 25 / 30 / −20 / −25 · KPI 08: 20 / 25 / −30 / −35 · KPI 09: 15 / 20 / −10 / −15
  - KPI 03 je Liga: Bundesliga 35 / 40 / −5 / −10 · Premier League 30 / 40 / −10 / −15 · Serie A 30 / 40 / −10 / −20 · LaLiga 20 / 30 / −15 / −25
- Damit ändern sich die **Anomalie-Punkte auf den Ligaseiten, die Top Anomalien und die Häufigkeit** im Bereich Datenqualität. KPI-Werte, Abweichungen, Ligareferenzen und die Rangfolge der Top Anomalien bleiben gleich.
- **Datenqualität:** Die Tabelle „Gültige Schwellenwerte“ zeigt je Zeile vier Spalten (Leicht positiv, Stark positiv, Leicht negativ, Stark negativ); KPI 03 erscheint je Liga.
- **Sensitivitätsanalyse nach Entwurf C:** eine Tabelle für alle KPIs mit fester Kopfzeile, je KPI vier Zeilen (leicht positiv, stark positiv, leicht negativ, stark negativ) und Total. Jede Zeile hat ihr eigenes Eingabefeld und ihre eigene Bewertung (Trefferquote, Vergleichsgruppe, Mehrwert, Spanne, Empfehlung), jetzt auch für stark. 1 cm Abstand unter dem gelben Hinweis, ⓘ an allen Spalten, neuer Info-Text zur Empfehlung, Erklärung der sechs Stufen unter „Definitionen und Änderungen“, dort auch der Eintrag vom 14.11.2026.
- **KPI 03 bei „Alle Ligen“:** Die Felder sind leer und zeigen grau „je Liga“; jede Liga zählt mit ihrer gültigen Schwelle. Eine eingetragene Zahl gilt für alle Ligen. Bei einer einzelnen Liga stehen deren Werte im Feld.
- **Unverändert:** KPI-Formeln, Rundung, Testfälle (rechnen weiter mit ±20/±35), Ligareferenzen, Fälle der Sensitivitätsanalyse.
- Doku: KPI-Regelwerk v2.6, Dashboard-Briefing v5.1, CHANGELOG, `01` Abschnitt 0, Prüfprotokoll `docs/tests/pruefprotokoll_schwellen_0-13.md`.

## Erwartungswerte

- Git-Stand vorher: `1482bc3`. Der Doku-Stand von Version 0.12 (Zweig `claude/doku-0-12-eingespielt`) ist in diesem Pull Request enthalten.
- Tests beim Einspielen: rund **@@TESTS_SERVER@@** (bisher 398/12).
- Erster Aufruf der Sensitivitätsanalyse: rund 50 Sekunden, danach sofort.

## Im Browser prüfen

1. **Datenqualität → Häufigkeit der Anomalien:** Tabelle „Gültige Schwellenwerte“ mit 12 Zeilen (Standard, KPI 02, KPI 03 · Bundesliga … LaLiga, KPI 04 … KPI 09) und vier Spalten; z. B. KPI 03 · Bundesliga **+35,00 % / +40,00 % / −5,00 % / −10,00 %**.
2. **Häufigkeit Bundesliga 2025/26:** @@FREQ@@
3. **Sensitivitätsanalyse:** 1 cm Abstand unter dem gelben Hinweis; eine Tabelle mit Kopfzeile KPI · Schwellen · Betroffene Spiele · Prognosewert; ⓘ an allen Spalten.
4. **KPI 02** (Alle Ligen, Alle Saisons): Felder 20.0 / 30.0 / −15.0 / −25.0. Leicht positiv **684** Spiele (0,66 je Spieltag, 48,94 %), 374 eingetroffen, Trefferquote 54,68 %, Vergleichsgruppe 46,56 %, Mehrwert **+8,12**, Funktioniert. Stark positiv **175**, Mehrwert **+12,87**. Total **1'972**, 1'141 eingetroffen, 57,86 %.
5. **KPI 03** (Alle Ligen): vier leere Felder „je Liga“; leicht positiv **1'589** Spiele, Mehrwert **+8,23**. Eine Zahl eintragen (z. B. 30) → blau, Werte ändern sich; „Auf gültige Schwellen zurücksetzen“ → wieder „je Liga“.
6. **Liga Bundesliga:** KPI 03 zeigt 35.0 / 40.0 / −5.0 / −10.0; leicht positiv 589 Spiele, Mehrwert +3,87, Funktioniert leicht.
7. **KPI 06 stark positiv** (Alle Ligen): 983 Spiele, Mehrwert +2,72; stark negativ 553 Spiele, Mehrwert +7,96, Funktioniert.
8. **„Definitionen und Änderungen“** aufklappen: Abschnitt „Wie entsteht die Empfehlung?“ mit den sechs Stufen; Eintrag 14.11.2026.
9. **Ligaseiten und Top Anomalien:** Anomalie-Punkte mit den neuen Schwellen (z. B. mehr Punkte bei KPI 06 positiv); KPI-Werte unverändert.
