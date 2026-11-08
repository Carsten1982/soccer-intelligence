# Soccer Intelligence – H.1: Aufräumen und Tempo

**Stand:** 08.11.2026 · Version 0.9.1 · Freigabe von Carsten am 08.11.2026 · Grundlage: Code-Prüfung vom 08.11.2026

## Was ist neu?

Für dich sieht das Dashboard aus wie bisher. **Alle Zahlen bleiben gleich.** Geprüft wurden alle 8'808 Begegnungen vor und nach dem Umbau, ohne einen einzigen Unterschied (`docs/tests/pruefprotokoll_h1.md`).

- **Schneller:** Die Häufigkeit der Anomalien braucht beim ersten Aufruf rund 6 statt 30 Sekunden. Die KPIs eines Spieltags werden zwischengespeichert und erst neu berechnet, wenn sich eine Datei ändert.
- **Robuster:** Drei mögliche Abstürze sind behoben. Statt abzustürzen zeigt die App jetzt eine klare Meldung:
  - beschädigte Excel-Datei,
  - Blatt *Datenhinweise* ohne Spalte `Liga`,
  - ungültige `teams.toml` oder `schwellen.toml`.
- **Kommazahlen:**
  - Bei Toren, `Gameday` oder `id` ist eine Kommazahl ein Fehler.
  - Bei Ecken, Karten und Schüssen gibt es eine Warnung, und der Wert gilt als fehlend. Es wird nie abgeschnitten.
  - Die Anteile in der Häufigkeit werden kaufmännisch gerundet.
- **Aufgeräumt:**
  - Die alte Tabelle ist entfernt.
  - Die Berechnung der Spieltags-KPIs liegt jetzt in `app/core/results.py`, nicht mehr in der Oberfläche.
  - Doppelte Teile und Tests sind entfernt.
  - Die Fusszeile zeigt „Version 0.9.1 – H.1: Aufräumen und Tempo“.

**Geändert:**
- `app/app.py`, `app/state.py`
- `app/core/`: `config.py`, `fixtures.py`, `frequency.py`, `kpis.py`, `loader.py`, `schema.py`, `settings.py`, `thresholds.py`, `validation.py`
- `app/views/`: `components.py`, `datenqualitaet.py`, `kpi_table.py`, `liga.py`, `top_anomalien.py`
- Tests und Doku

**Neu:** `app/core/files.py`, `app/core/results.py`, `tests/test_h1.py`, `docs/tests/pruefprotokoll_h1.md`, diese Anleitung.

**Nicht geändert:** `docker-compose.yml`, Traefik, Passwortschutz, Platzhalterseite, Dockerfile, requirements, `app/config/*.toml`, Excel-Dateien in `data/`, andere Container.

## Ablauf

1. **Backup** (Code, Doku, Daten und Git-Stand; vorher sollte `git status` leer sein):
   ```bash
   cd /docker/football-dashboard && git status --short && B=backup/$(date +%F_%H%M)_vor_H1 && mkdir -p "$B" && git rev-parse --short HEAD > "$B/git_stand.txt" && tar czf "$B/code_docs.tgz" app tests docs CLAUDE.md CHANGELOG.md ANLEITUNG_ETAPPE_H.md && cp -a data "$B/" && ls -la "$B" && cat "$B/git_stand.txt"
   ```
   Erwartet: keine Zeile von `git status`, danach der Ordner mit `code_docs.tgz`, `data` und dem Git-Stand `51e595b`.

2. **Paket einspielen:** `etappe_H1.zip` mit WinSCP nach `/docker/football-dashboard/` hochladen. Falls die Datei in `/root` landet: `mv /root/etappe_H1.zip /docker/football-dashboard/`. Dann:
   ```bash
   cd /docker/football-dashboard && python3 -m zipfile -e etappe_H1.zip . && rm etappe_H1.zip && git status --short
   ```
   Erwartet: rund 30 Zeilen mit `M` und 5 neue Dateien mit `??`.

3. **Tests im Wegwerf-Container.** Das Projekt ist darin nur lesend eingebunden, der Container wird danach gelöscht:
   ```bash
   cd /docker/football-dashboard && docker run --rm -v "$PWD":/src:ro -e SI_DATA_DIR=/src/data -e PYTHONDONTWRITEBYTECODE=1 -w /src python:3.12-slim sh -c "pip install -q --root-user-action=ignore -r requirements-dev.txt && python -m pytest -q -p no:cacheprovider tests" 2>&1 | tail -15
   ```
   Erwartet: **287 bestanden, 1 übersprungen**, keine Fehler.

4. **Aktivieren** (nur unser Container):
   ```bash
   cd /docker/football-dashboard && docker compose up -d --build football-dashboard && docker ps --format "table {{.Names}}\t{{.Status}}" && docker logs football-dashboard --tail 15
   ```

5. **Prüfen:**
   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/ ; curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/dashboard/
   ```
   Erwartet: `200` und `401`. Danach im Browser anmelden (Kurzprüfung siehe unten).

6. **Commit und Push:**
   ```bash
   cd /docker/football-dashboard && git add -A && git commit -m "H.1: Aufräumen und Tempo (0.9.1)" && git push && git log -1 --oneline
   ```

## Kurzprüfung im Browser

- **Fusszeile:** „Version 0.9.1 – H.1: Aufräumen und Tempo“.
- **Top Anomalien:** dieselben vier Einträge wie vorher.
- **Bundesliga:** gleiche Werte wie vorher, z. B. Zeile Stuttgart – FC Koln: 4,10 · +64,00 % · 4,20 · 10,45 · 1,80 · 2,30 · 85,00 % · 10,90. Eine Zeile aufklappen.
- **Datenqualität:**
  - Unter „Häufigkeit der Anomalien“ erscheinen die Tabellen nach wenigen Sekunden.
  - Unter „Welche Prüfungen laufen?“ stehen die neuen Regeln zu Kommazahlen.

## Rückweg

```bash
cd /docker/football-dashboard
git reset --hard 51e595b                         # Stand Etappe H (auch wenn H.1 schon committet ist)
docker compose up -d --build football-dashboard
```

Wurde H.1 noch nicht committet, bleiben die zwei neuen Dateien `app/core/files.py` und `app/core/results.py` liegen. Sie stören den alten Stand nicht.
