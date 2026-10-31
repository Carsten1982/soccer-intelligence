# Soccer Intelligence – Anpassungen nach Abnahme Etappe C

**Stand:** 31.10.2026

## Was ist neu?

1. **Kleinerer Abstand** zwischen Navigation und Überschrift (rund 80 % weniger).
2. **Navigation dunkelgrau**, Schrift weiss; aktiver Tab fett mit blauem Balken, übrige Tabs hellgrau.
3. **Spieltag-Pfeile ◀ ▶** in Bundesliga und Premier League: frühere Spieltage wählbar (nicht in die Zukunft), je Liga getrennt, Auswahl in der Adresse (`?spieltag=1`), Schaltfläche „Zum aktuellen Spieltag“. Top Anomalien zeigt immer den aktuellen Spieltag.

4. **md-Dateien sind die einzige Quelle:** `03_KPI_Regelwerk.md` (v1.2), `05_Dashboard.md` (v4.3), `CLAUDE.md`, `01_Technisches_Setup.md` angepasst; `word/README.md` markiert die Word-Dateien als Archiv.

Dazu: Referenz-Datenbank für die Tests unter `tests/referenz/` (die 32 KPI-Testfälle laufen damit unabhängig vom aktuellen Datenstand), `.gitignore` erlaubt genau diese eine Excel-Datei.

## Erwartet nach dem Einspielen

- Tests: alle bestanden (rund 140)
- Bundesliga: Spieltag 2, Pfeil ◀ aktiv, Pfeil ▶ grau. Klick auf ◀ → Spieltag 1, Adresse `…/bundesliga?spieltag=1`, Bayern – Stuttgart wieder 4,4 · +34,1 %.

## Rückweg

```bash
cd /docker/football-dashboard
git reset --hard 8cb5f0f          # Stand nach Etappe C
docker compose up -d --build football-dashboard
```
