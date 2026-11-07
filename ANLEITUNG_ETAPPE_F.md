# Soccer Intelligence – Etappe F: Vier Ligen

**Stand:** 07.11.2026 · Version 0.8 · freigegeben von Carsten am 07.11.2026

## Was ist neu?

- Zwei neue Bereiche: **Serie A** (`/dashboard/serie-a`) und **LaLiga** (`/dashboard/laliga`). Navigation: Top Anomalien · Bundesliga · Premier League · Serie A · LaLiga · Datenqualität.
- Top Anomalien und Datenqualität (inkl. Häufigkeit der Anomalien) über alle vier Ligen. Kopfbereich der Top Anomalien kompakt in zwei Spalten.
- Alle vier Ligablätter sind jetzt Pflicht; das Blatt heisst `Serie A`.
- Neue unabhängige Gegenrechnung der KPIs (`tests/gegenrechnung.py`, `tests/test_gegenrechnung.py`). Einmaliger Vollvergleich aller 8'808 Begegnungen: 0 Abweichungen. Protokoll: `docs/tests/pruefprotokoll_etappe_f.md`.

Geändert: `app/config/ligen.toml`, `app/core/settings.py`, `app/core/loader.py`, `app/views/components.py`, `app/views/top_anomalien.py`, `app/views/datenqualitaet.py`, Tests, Doku.
Nicht geändert: docker-compose.yml, Traefik, Passwortschutz, Platzhalterseite, Excel-Dateien, andere Container.

## Erwartet nach dem Einspielen

- Tests: rund 171 bestanden, 1 übersprungen
- Startseite: Kopf „Aktueller Spieltag“ mit vier Ligen (je Spieltag 2). Top Anomalien: Juventus – Parma (KPI 02, −30,0 %), Cagliari – Inter (KPI 02, +26,0 %), Crystal Palace – Manchester City, Aston Villa – Arsenal (KPI 04, je −25,9 %).
- Serie A und LaLiga: Tabelle des 2. Spieltags mit allen KPI-Spalten. Aufsteiger (z. B. Frosinone, Malaga) mit „V“ bzw. „–“.

## Rückweg

```bash
cd /docker/football-dashboard
git reset --hard 8c1c5d3          # Stand vor Etappe F
docker compose up -d --build football-dashboard
```
Die Datenbank mit Blatt `Serie A` funktioniert auch mit dem alten Stand (nur Hinweise im Bereich Datenqualität).
