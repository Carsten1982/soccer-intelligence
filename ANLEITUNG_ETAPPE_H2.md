# Soccer Intelligence – H.2: Stabilität

**Stand:** 08.11.2026 · Version 0.9.2 · Freigabe von Carsten am 08.11.2026 · Grundlage: zweite Code-Prüfung (ChatGPT), Befunde S1–S6

## Was ist neu?

Für dich sieht das Dashboard aus wie bisher. **Alle Zahlen bleiben gleich.** Geprüft wurden alle 8'808 Begegnungen, die Häufigkeit und die Prüfmeldungen, jeweils vorher und nachher. Es gibt keinen Unterschied.

Bei unerwarteten Inhalten zeigt die App jetzt eine klare Meldung statt abzustürzen oder still falsch zu rechnen:

| Fall | Vorher | Jetzt |
|---|---|---|
| Konfigurationsdatei mit falscher Struktur (z. B. `liga = 1`) | Absturz | „Konfiguration ungültig: …“ |
| Zahl statt Datum in der Spalte `Date` (z. B. 45800) | still als 01.01.1970 gelesen | Fehler „Ungültiges Datum“ |
| id `inf` oder Text | Absturz | Fehler „Keine ganze Zahl“ |
| Datenhinweis mit id 123,5 | galt für Spiel 123 | gilt für kein Spiel |
| Excel-Datei ersetzt, mit gleicher Grösse und gleicher Zeit | evtl. alter Stand aus dem Zwischenspeicher | wird erkannt und neu eingelesen |
| Datei wird während des Einlesens ersetzt | Prüfsumme und Daten evtl. von zwei Ständen | Datei wird nur einmal gelesen |

Die Fusszeile zeigt „Version 0.9.2 – H.2: Stabilität“.

**Geändert:**
- `app/state.py`
- `app/core/`: `config.py`, `files.py`, `fixtures.py`, `loader.py`, `rows.py`, `settings.py`, `thresholds.py`
- `app/views/datenqualitaet.py` (Text der Prüfregeln)
- `tests/test_ui.py`, Doku

**Neu:** `tests/test_h2.py` (32 Tests), diese Anleitung.

**Nicht geändert:** KPI-Formeln, Schwellen, Testfälle, Darstellung, `docker-compose.yml`, Traefik, Dockerfile, requirements, `app/config/*.toml`, Excel-Dateien, andere Container.

## Ablauf

1. **Backup.** `git status` sollte leer sein:
   ```bash
   cd /docker/football-dashboard && git status --short && B=backup/$(date +%F_%H%M)_vor_H2 && mkdir -p "$B" && git rev-parse --short HEAD > "$B/git_stand.txt" && tar czf "$B/code_docs.tgz" app tests docs CLAUDE.md CHANGELOG.md && cp -a data "$B/" && ls -la "$B" && cat "$B/git_stand.txt"
   ```
   Erwartet: keine Zeile von `git status`, dann der Backup-Ordner und zuletzt der Git-Stand `b5a7ea8`.

2. **Paket einspielen:** `etappe_H2.zip` mit WinSCP hochladen. Der Befehl holt die Datei auch aus `/root`, falls sie dort landet:
   ```bash
   cd /docker/football-dashboard && { [ -f etappe_H2.zip ] || mv /root/etappe_H2.zip . ; } && python3 -m zipfile -e etappe_H2.zip . && rm etappe_H2.zip && git status --short
   ```
   Erwartet: 14 Zeilen mit `M` und 2 Zeilen mit `??`.

3. **Tests im Wegwerf-Container:**
   ```bash
   cd /docker/football-dashboard && docker run --rm -v "$PWD":/src:ro -e SI_DATA_DIR=/src/data -e PYTHONDONTWRITEBYTECODE=1 -w /src python:3.12-slim sh -c "pip install -q --root-user-action=ignore -r requirements-dev.txt && python -m pytest -q -p no:cacheprovider tests" 2>&1 | tail -15
   ```
   Erwartet: **319 bestanden, 1 übersprungen**.

4. **Aktivieren** (nur unser Container):
   ```bash
   cd /docker/football-dashboard && docker compose up -d --build football-dashboard && docker ps --format "table {{.Names}}\t{{.Status}}"
   ```

5. **Prüfen:**
   ```bash
   sleep 5; docker logs football-dashboard --tail 8; curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/ ; curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/dashboard/
   ```
   Erwartet: Startmeldung ohne Fehler, dann `200` und `401`. Im Browser kurz nachschauen: Die Fusszeile zeigt 0.9.2, die Werte sind wie bisher.

6. **Commit und Push:**
   ```bash
   cd /docker/football-dashboard && git add -A && git commit -m "H.2: Stabilität (0.9.2)" && git push && git log -1 --oneline
   ```

## Rückweg

```bash
cd /docker/football-dashboard && git reset --hard b5a7ea8 && docker compose up -d --build football-dashboard
```
