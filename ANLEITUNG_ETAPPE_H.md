# Soccer Intelligence – Etappe H: KPI 05–09

**Stand:** 08.11.2026 · Version 0.9 · Design abgenommen und Freigabe von Carsten am 08.11.2026

## Was ist neu?

- **KPI 05–09** in allen Liga-Bereichen: Ecken, Tore 1. Halbzeit, Tore 2. Halbzeit, Beide Teams treffen (BTTS), Schüsse aufs Tor (Regelwerk, Abschnitt 9).
- **Kompakte Tabelle** (abgenommenes Design): eine Zeile je Begegnung mit Formkurve und je KPI 02–09 Hauptwert und Anomalie-Punkt. KPI 03 zeigt die Abweichung zur 2,5-Marke. **Klick auf die Zeile** klappt alle Details auf (neun Kärtchen mit Teamwerten, Liga, Abweichung, Datenbasis, Text).
- **Zwei Nachkommastellen** bei allen KPIs, auch bei der Abweichung; Einstufung nach dem auf zwei Stellen gerundeten Wert.
- **Top Anomalien über KPI 02–09** (bisherige Rangfolge; Gewichtung folgt mit der Schwellen-Analyse).
- **Schwellen-Datei** `app/config/schwellen.toml` (überall ±20 % / ±35 %). Der Bereich Datenqualität zeigt die gültigen Schwellen und die Häufigkeit für KPI 02–09.
- Tests: alle 61 Testfälle KPI 05–09 und die 24 angepassten Testfälle KPI 02–04 automatisch; Gegenrechnung auf KPI 05–09 erweitert; einmaliger Vollvergleich aller Spiele ohne Abweichung (`docs/tests/pruefprotokoll_etappe_h.md`).

Geändert: `app/core/kpis.py`, `top.py`, `frequency.py`, `settings.py`, `app/state.py`, `app/views/kpi_table.py`, `components.py`, `liga.py`, `top_anomalien.py`, `datenqualitaet.py`, Tests, Doku.
Neu: `app/core/thresholds.py`, `app/config/schwellen.toml`, `tests/test_thresholds.py`, `tests/referenz/Database-Soccer-Intelligence_f37e36d3.xlsx` (fester Stand für die Testfälle KPI 05–09), `docs/tests/pruefprotokoll_etappe_h.md`.
Nicht geändert: `docker-compose.yml`, Traefik, Passwortschutz, Platzhalterseite, Dockerfile, requirements, Excel-Dateien in `data/`, andere Container.

## Ablauf

1. **Backup** – erledigt: `backup/2026-11-08_0547_vor_Etappe_H` (Git-Stand `cc00dd9`).
2. **Paket einspielen:** `etappe_H.zip` mit WinSCP nach `/docker/football-dashboard/` hochladen, dann
   ```bash
   cd /docker/football-dashboard && python3 -m zipfile -e etappe_H.zip . && rm etappe_H.zip && git status --short
   ```
3. **Tests im Wegwerf-Container** (Projekt nur lesend eingebunden, Container wird danach gelöscht):
   ```bash
   cd /docker/football-dashboard && docker run --rm -v "$PWD":/src:ro -e SI_DATA_DIR=/src/data -e PYTHONDONTWRITEBYTECODE=1 -w /src python:3.12-slim sh -c "pip install -q --root-user-action=ignore -r requirements-dev.txt && python -m pytest -q -p no:cacheprovider tests" 2>&1 | tail -15
   ```
   Erwartet: rund 260 bestanden, 1 übersprungen, keine Fehler.
4. **Aktivieren** (nur unser Container):
   ```bash
   cd /docker/football-dashboard && docker compose up -d --build football-dashboard && docker ps --format "table {{.Names}}\t{{.Status}}" && docker logs football-dashboard --tail 15
   ```
5. **Prüfen:**
   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/ ; curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/dashboard/
   ```
   Erwartet: `200` und `401`. Danach im Browser anmelden (Abnahme siehe unten).
6. **Commit und Push:**
   ```bash
   cd /docker/football-dashboard && git add -A && git commit -m "Etappe H: KPI 05-09, zwei Nachkommastellen, Top Anomalien 02-09" && git push && git log -1 --oneline
   ```

## Abnahme im Browser

- **Bundesliga, 2. Spieltag:** Zeile 1 Stuttgart – FC Koln: 4,10 · +64,00 % · 4,20 · 10,45 · 1,80 · 2,30 · 85,00 % · 10,90. Klick auf die Zeile zeigt neun Kärtchen.
- **Top Anomalien:** Atl. Madrid – Villarreal (KPI 06, +66,72 %), Stuttgart – FC Koln (KPI 03, +64,00 %), Sassuolo – Torino (KPI 08, +60,92 %), Bayer Leverkusen – Union Berlin (KPI 03, +52,00 %).
- **Datenqualität → Häufigkeit der Anomalien:** oben „Gültige Schwellenwerte“ (Standard ±20,00 % / ±35,00 %), darunter je Liga KPI 02–09.
- Handy: Tabelle seitlich schiebbar, # und Spiel bleiben stehen; Details untereinander.

## Rückweg

```bash
cd /docker/football-dashboard
git reset --hard cc00dd9                         # Stand Etappe F (falls schon committet)
docker compose up -d --build football-dashboard
```
Neue, noch nicht committete Dateien (z. B. `app/core/thresholds.py`) stören den alten Stand nicht.
