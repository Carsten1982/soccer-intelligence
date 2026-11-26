# Release: Version 0.30.1 – Showcase-Dashboard Zeitzonen

**Stand:** 26.11.2026 · Version 0.30.1 · Befund Carsten nach dem Einspielen von 0.30

**Commit:** Version 0.30.1: Zeitzonen im Showcase-Dashboard

## Was ändert sich?

- **„Letzter Datenstand“** zeigt die Schweizer Zeit (z. B. 04:01 Uhr statt 03:01 Uhr). Die Änderungszeit der Datei
  kommt in UTC und wurde nicht umgerechnet.
- **„Website & Server“** zeigt wieder Werte. Das Prüfskript schreibt seine Uhrzeit in der Zeit des Servers (UTC); das
  Dashboard hielt die Werte deshalb für eine Stunde alt. Jetzt zählt die Änderungszeit der Datei.

## Einspielen

```bash
bash /docker/football-dashboard/tools/einspielen.sh github
```

## Erwartungswerte

- Tests rund **811 bestanden**, keine Fehler. Dashboard-Fusszeile: „Version 0.30.1 – Showcase Zeitzonen“.
- Kurz prüfen, in welcher Zeitzone der Server läuft (nur lesend):
  ```bash
  date; ls -l --time-style=+%H:%M /docker/football-dashboard/import/server.json
  ```
  Erwartet: Die Zeit von `server.json` ist höchstens 1–2 Minuten alt.

## Im Browser prüfen

1. `https://soccer-intelligence.com/showcase/ki-automation/data`: „Letzter Datenstand“ kurz nach 04:00 Uhr.
2. „Website & Server“: Erreichbar, Normal, Alle laufen, Aktuell, Abfragen heute, Offene Alarme, Verfügbarkeit
   (zu Beginn „Gemessen seit 26.11.2026“); oben rechts „Stand: …“ mit der aktuellen Uhrzeit.
