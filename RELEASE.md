# Release: Version 0.15.1 – Massnahmen aus der Code-Prüfung

**Stand:** 16.11.2026 · Version 0.15.1 · Code-Prüfbericht vom 16.11.2026 (ChatGPT), Entscheidungen Carsten 16.11.2026 (F1–F7)

**Commit:** Version 0.15.1: Massnahmen aus der Code-Prüfung (Übergabe-Protokoll, Prüfsummen, negative Werte, Vorladen)

## Was ändert sich?

- **Übernahme abgesichert:** Datenbank und Spielplan werden mit einem Übergabe-Protokoll getauscht. Bricht der Import mitten im Tausch ab, führt er ihn beim nächsten Start zu Ende; ein Mischstand bleibt nie bestehen. Vor dem Tausch werden beide Dateien gegen die Prüfsummen im Bericht geprüft.
- **Backups** heissen jetzt mit Sekunden und Lauf, z. B. `Database-Soccer-Intelligence_2026-11-17_073012_lauf-2026-11-17_040000_vor_import.xlsx`, und werden nie überschrieben.
- **Negative Werte:** Ein negativer Statistikwert gilt als fehlend (Warnung), negative Tore sind ein Fehler. Heute gibt es keinen solchen Wert, die KPIs bleiben gleich.
- **Vorladen:** Das Dashboard rechnet nach jeder Datenänderung, jedem neuen Tag und beim Start alle Seiten im Hintergrund vor. Danach öffnen sich alle Seiten sofort, auch die Sensitivitätsanalyse.
- **Liste offener Bereinigungen** in `01`, Abschnitt 8.1; schneller Testlauf für zwischendurch.

## Erwartungswerte

- Git-Stand vorher: `a4367eb`.
- Tests beim Einspielen: rund **470 bestanden, 13 übersprungen** (zuletzt rund 461 / 13), keine Fehler. Einspielen in `tmux`.
- Schritt 5: „Container laufen (Dashboard und Import)“.
- **Vorladen:** 2–3 Minuten nach dem Einspielen zeigt
  ```bash
  docker logs football-dashboard --tail 5
  ```
  eine Zeile `Vorladen: … Sekunden`.

## Im Browser prüfen

1. **Etwa 3 Minuten nach dem Einspielen** das Dashboard öffnen: Top Anomalien, die Ligaseiten, Datenqualität und **Sensitivitätsanalyse** erscheinen ohne Wartezeit (bisher rund 40 Sekunden beim ersten Aufruf).
2. **Datenqualität:** Datenbank 0 Fehler, Warnungen und Hinweise wie bisher (35 / 201).
3. **Datenimport/API:** wie bisher. Nach dem nächsten „Übernehmen“ (morgen früh) erscheinen die neuen Backup-Namen in `backup/`.
4. **Fusszeile:** „Version 0.15.1 – Datenimport“.
