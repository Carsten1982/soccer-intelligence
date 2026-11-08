# Soccer Intelligence – Etappe I.1: Simulation – Spielwiese

**Stand:** 08.11.2026 · Version 0.10 · Freigabe und Design (Variante B) von Carsten am 08.11.2026

## Was ist neu?

- **Neuer Bereich „Simulation“** ganz rechts in der Navigation (`/dashboard/simulation`, nur intern).
- **Links:** die Einstellungen.
  - Liga und Saisons, laufende Saison zuschaltbar.
  - Schwellen für alle KPIs und je KPI.
  - Zurücksetzen und Stufe.
- **Rechts:** zwei Tabellen.
  - **Häufigkeit:** leicht und stark, vorher und nachher.
  - **Ergebnisqualität:** Fälle, eingetroffen, ohne Anomalie, **Mehrwert**, Urteil.
- **Info-Symbole ⓘ** mit Erklärungen und einen aufklappbaren Bereich „Definitionen und Änderungen“.
- **Spielwiese:** Hier geänderte Schwellen wirken nie auf das Dashboard. Gültig bleibt `schwellen.toml`.
- **Erster Aufruf:** Er dauert einmal je Datenbankstand rund 30 Sekunden. Danach rechnet jede Änderung sofort.
- **Regeln:** KPI-Regelwerk Abschnitt 11, Dashboard-Briefing 6.4.

**Geändert:**
- `app/app.py`, `app/state.py`
- `app/core/config.py` (reservierte Adresse), `app/core/settings.py`
- `tests/test_ui.py`, `tests/gegenrechnung.py` (unabhängige Gegenrechnung der Simulation), Doku

**Neu:** `app/core/simulation.py`, `app/views/simulation.py`, `tests/test_simulation.py`, diese Anleitung.

**Nicht geändert:** KPI-Berechnung, Schwellen, Liga-Bereiche, Top Anomalien, Datenqualität, Docker, Traefik, Excel-Dateien, andere Container.

## Ablauf

1. **Backup:**
   ```bash
   cd /docker/football-dashboard && git status --short && B=backup/$(date +%F_%H%M)_vor_I1 && mkdir -p "$B" && git rev-parse --short HEAD > "$B/git_stand.txt" && tar czf "$B/code_docs.tgz" app tests docs CLAUDE.md CHANGELOG.md && cp -a data "$B/" && ls -la "$B" && cat "$B/git_stand.txt"
   ```
   Erwartet: keine Zeile von `git status`, am Schluss `291eeac`.

2. **Paket einspielen:** `etappe_I1.zip` mit WinSCP hochladen, dann:
   ```bash
   cd /docker/football-dashboard && { [ -f etappe_I1.zip ] || mv /root/etappe_I1.zip . ; } && python3 -m zipfile -e etappe_I1.zip . && rm etappe_I1.zip && git status --short
   ```
   Erwartet: 11 Zeilen mit `M` und 4 Zeilen mit `??`.

3. **Tests** (rund 3 Minuten):
   ```bash
   cd /docker/football-dashboard && docker run --rm -v "$PWD":/src:ro -e SI_DATA_DIR=/src/data -e PYTHONDONTWRITEBYTECODE=1 -w /src python:3.12-slim sh -c "pip install -q --root-user-action=ignore -r requirements-dev.txt && python -m pytest -q -p no:cacheprovider tests" 2>&1 | tail -15
   ```
   Erwartet: **345 bestanden, 1 übersprungen**.

4. **Aktivieren:**
   ```bash
   cd /docker/football-dashboard && docker compose up -d --build football-dashboard && docker ps --format "table {{.Names}}\t{{.Status}}"
   ```

5. **Prüfen:**
   ```bash
   sleep 5; docker logs football-dashboard --tail 8; curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/ ; curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/dashboard/
   ```
   Erwartet: `200` und `401`.

6. **Commit** (nach der Abnahme):
   ```bash
   cd /docker/football-dashboard && git add -A && git commit -m "Etappe I.1: Simulation - Spielwiese (0.10)" && git push && git log -1 --oneline
   ```

## Abnahme im Browser

1. **Simulation öffnen:** Beim ersten Aufruf rechnet die App rund 30 Sekunden. Danach erscheinen beide Tabellen.
2. **Unveränderte Schwellen:** Bei „Alle Ligen“ und „Alle abgeschlossenen“ steht beim Urteil überall „unverändert“. Kontrollwerte:
   - Grundlage: 6'710 Spiele.
   - KPI 02 positiv: 515 Fälle, eingetroffen 54,56 %, Mehrwert +8,43.
3. **KPI 09 ändern:** Links bei KPI 09 leicht = 12 und stark = 18 eintragen.
   - Häufigkeit KPI 09: 129 → 1'093.
   - Ergebnisqualität KPI 09 positiv: 558 Fälle, Mehrwert +10,43, Urteil „zu wenige Fälle“, weil vorher nur 80 Fälle.
4. **Zurücksetzen** klicken: Alles steht wieder auf ±20 / ±35.
5. **Info-Symbole ⓘ:** Mit der Maus darüberfahren zeigt die Erklärung. „Definitionen und Änderungen“ lässt sich aufklappen.
6. **Liga-Bereiche und Top Anomalien:** unverändert.

## Rückweg

```bash
cd /docker/football-dashboard && git reset --hard 291eeac && docker compose up -d --build football-dashboard
```
