# Soccer Intelligence – Etappe B: Spielplan und Datenqualität

**Stand:** 31.10.2026

## Was ist neu?

- **Tabs oben:** Top Anomalien · Bundesliga · Premier League · Datenqualität
- **Liga-Bereiche:** alle Begegnungen des aktuellen Spieltags (aus `data/Spielplan.xlsx`), Tabelle mit fixierten Spalten # und Spiel. KPI-Spalten folgen in Etappe C.
- **Kopfbereich:** Titel, Untertitel und rechts „Aktueller Spieltag“ (z. B. „Saison 2026/27 · Spieltag 1“)
- **Top Anomalien:** vorerst nur Kopfbereich mit dem Spieltag je Liga (Auswahl folgt in Etappe D)
- **Datenqualität:** drei Reiter – Datenbank (bisherige Seite „Übersicht“ + Prüfungen), Spielplan und Spieltage, Häufigkeit der Anomalien (folgt)
- **Konfiguration:** `app/config/ligen.toml` (aktive Ligen) und `app/config/teams.toml` (Aufsteiger Elversberg, Paderborn)
- **Tests:** 72 (4 davon prüfen die Seiten mit Streamlit und laufen nur auf dem Server)

## Inhalt des Pakets

- `app/` – kompletter Code (ersetzt den bisherigen Stand; `app/views/uebersicht.py` entfällt)
- `tests/` – alle Tests
- `docs/01_Technisches_Setup.md`, `docs/02_Datenbasis.md`, `docs/04_Spielplan.md` – aktualisiert
- `CHANGELOG.md` – mit Einträgen Etappe A und B

Nicht geändert: Dockerfile, docker-compose.yml, requirements.txt, Traefik, Excel-Dateien, andere Container.

## Erwartete Prüfergebnisse nach dem Einspielen

- Tests: **72 passed**
- Datenqualität → Datenbank: 0 Fehler, 2 Warnungen (id 11344), 17 Hinweise
- Datenqualität → Spielplan: 0 Fehler, 0 Warnungen, 3 Hinweise (Elversberg, Paderborn: Aufsteiger; Schalke: keine Ligaspiele in 2025/26 und 2026/27)
- Bundesliga und Premier League: Spieltag 1 der Saison 2026/27 (alle Spieltage der Datei sind beendet → letzter Spieltag der Datei)

## Rückweg

```bash
cd /docker/football-dashboard
git reset --hard ffec276          # Stand nach Etappe A
docker compose up -d --build football-dashboard
```
