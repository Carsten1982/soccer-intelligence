# Soccer Intelligence – Etappe I.1, Nachtrag (Version 0.10.1)

**Stand:** 09.11.2026 · Freigabe Carsten am 09.11.2026

## Was ist neu? (nur Bereich Simulation)

1. **Info-Felder ⓘ:** Fährst du mit der Maus darüber, erscheint sofort ein Fenster mit der Erklärung.
2. **Tabellen:**
   - Die KPI-Spalte ist schmaler und zweizeilig.
   - „Ergebnisqualität“ hat neu die Spalte **Schwellen**. Eigene Werte sind blau, darunter stehen die gültigen.
   - Die Spalte „Urteil“ ist schmaler.
3. **Saisons:** Zur Auswahl stehen alle abgeschlossenen, die letzten 4, 3 oder 2 Saisons, die letzte Saison und die aktuelle Saison (vorläufig).
4. **Stufe:** Das Feld steht jetzt über „Je KPI“ und hat ein ⓘ.
5. **Einstellungen:** Der linke Bereich ist 10 % schmaler und grau hinterlegt.

Die Rechnung ist unverändert, die anderen Bereiche ebenso.

## Ablauf

1. **Backup:**
   ```bash
   cd /docker/football-dashboard && git status --short && B=backup/$(date +%F_%H%M)_vor_I1b && mkdir -p "$B" && git rev-parse --short HEAD > "$B/git_stand.txt" && tar czf "$B/code_docs.tgz" app tests docs CLAUDE.md CHANGELOG.md && ls -la "$B" && cat "$B/git_stand.txt"
   ```
   Erwartet: keine Zeile von `git status`, am Schluss `dbd90c5`.
2. **Paket** `etappe_I1b.zip` hochladen und entpacken:
   ```bash
   cd /docker/football-dashboard && { [ -f etappe_I1b.zip ] || mv /root/etappe_I1b.zip . ; } && python3 -m zipfile -e etappe_I1b.zip . && rm etappe_I1b.zip && git status --short
   ```
   Erwartet: 9 Zeilen mit `M` und 1 Zeile mit `??`.
3. **Tests** (rund 4 Minuten): Erwartet **345 bestanden, 1 übersprungen**.
   ```bash
   cd /docker/football-dashboard && docker run --rm -v "$PWD":/src:ro -e SI_DATA_DIR=/src/data -e PYTHONDONTWRITEBYTECODE=1 -w /src python:3.12-slim sh -c "pip install -q --root-user-action=ignore -r requirements-dev.txt && python -m pytest -q -p no:cacheprovider tests" 2>&1 | tail -15
   ```
4. **Aktivieren und prüfen:**
   ```bash
   cd /docker/football-dashboard && docker compose up -d --build football-dashboard && sleep 5 && docker logs football-dashboard --tail 8 && curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/ ; curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/dashboard/
   ```
   Erwartet: `200` und `401`. Danach im Browser den Bereich Simulation anschauen.
5. **Commit:**
   ```bash
   cd /docker/football-dashboard && git add -A && git commit -m "Etappe I.1 Nachtrag: Simulation (0.10.1)" && git push && git log -1 --oneline
   ```

## Rückweg

```bash
cd /docker/football-dashboard && git reset --hard dbd90c5 && docker compose up -d --build football-dashboard
```
