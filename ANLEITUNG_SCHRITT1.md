# Soccer Intelligence – Schritt 1: Datenbasis

**Stand 30.10.2026:** angepasst an die Datenbank mit 58 Spalten (neue Spalte `Gameday` in Spalte B).

**Voraussetzung:** Auf dem Server liegt die Datenbank mit 58 Spalten (SHA-256 `6d68583c…`). Mit der alten Datei (57 Spalten) meldet die App einen Strukturfehler und zeigt keine Auswertungen. Ablauf zum Austausch: `01_Technisches_Setup.md`, Abschnitt 6.

## Inhalt des Pakets
- app/app.py                 Navigation (ersetzt den Platzhalter)
- app/state.py               Laden mit Cache (lädt neu, sobald die Excel-Datei ersetzt wird)
- app/core/                  Einlesen, Strukturprüfung, Plausibilitätsprüfungen (ohne Streamlit, testbar)
- app/views/                 Seiten "Übersicht" und "Datenqualität"
- app/.streamlit/config.toml Nutzungsstatistik aus, Entwicklermenü ausgeblendet
- tests/                     26 automatische Tests (pytest)
- requirements.txt           Versionen fest: streamlit 1.66.1, pandas 3.1.0, openpyxl 3.1.5
- requirements-dev.txt       zusätzlich pytest (nur für Tests, nicht im laufenden Image)

Nicht geändert: Dockerfile, docker-compose.yml, Traefik, Excel-Datei, andere Container.

## Ablauf auf dem VPS
Siehe Chat bzw. Abschnitt "Befehle" unten.

### 1. Backup
cd /docker/football-dashboard
mkdir -p backup/vor_schritt1
cp -a app requirements.txt docker-compose.yml Dockerfile backup/vor_schritt1/

### 2. Paket entpacken und einspielen
mkdir -p /root/schritt1
python3 -m zipfile -e /root/soccer-intelligence_schritt1.zip /root/schritt1/
cp -a /root/schritt1/app/. app/
cp -a /root/schritt1/tests /root/schritt1/requirements.txt /root/schritt1/requirements-dev.txt /root/schritt1/ANLEITUNG_SCHRITT1.md .

### 3. Tests in einem temporären Container (beeinflusst nichts)
docker run --rm -v /docker/football-dashboard:/work:ro -w /work \
  -e SI_DATA_DIR=/work/data -e PYTHONDONTWRITEBYTECODE=1 python:3.12-slim \
  sh -c "pip install -q --root-user-action=ignore -r requirements-dev.txt && python -m pytest -q -p no:cacheprovider tests"
Erwartet: 26 passed. Bei Fehlern STOPP -> Ausgabe an Claude.

### 4. Nur football-dashboard neu bauen
docker compose config -q && docker compose up -d --build football-dashboard

### 5. Prüfen
docker ps --format "table {{.Names}}\t{{.Status}}"
docker logs football-dashboard --tail 30
curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com

### Rückweg (falls nötig)
cd /docker/football-dashboard
rm -rf app && cp -a backup/vor_schritt1/app app
cp backup/vor_schritt1/requirements.txt .
docker compose up -d --build football-dashboard
