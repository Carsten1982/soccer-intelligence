# Soccer Intelligence – Etappe C: KPIs 01–04

**Stand:** 31.10.2026

## Was ist neu?

- **Liga-Tabellen mit allen KPI-Spalten** (Briefing Kapitel 7): Formkurve (farbige Punkte), Erwartete Tore, Over 2.5 Goals, Gelbe Karten – je mit Team 1, Team 2, Hauptwert, Referenz, Abweichung, Anomalie-Punkt, Datenbasis und Beschreibung. Legende unter der Tabelle.
- **Berechnung** gemäss `docs/03_KPI_Regelwerk.md`, so als wären die Spiele noch nicht gespielt (Stichtag „Datum von“).
- **Datenqualität → Häufigkeit der Anomalien:** KPI 02–04 für alle Spiele der Saison 2025/26.
- **Tests:** 126 (alle JSON-Testfälle aus `docs/tests/` werden automatisch geprüft).

## Inhalt des Pakets

- `app/`, `tests/` – kompletter Code und alle Tests
- `docs/01_Technisches_Setup.md`, `docs/03_KPI_Regelwerk.md`, `CHANGELOG.md` – aktualisiert

Nicht geändert: Dockerfile, docker-compose.yml, requirements.txt, Traefik, Excel-Dateien, andere Container.

## Erwartete Werte zur Kontrolle (Bundesliga, Spieltag 1)

Bayern Munich – Stuttgart: Formkurve Bayern S S U S S, Stuttgart N U U S U · KPI 02: 4,4 / +34,1 % / gelb · KPI 03: 4,4 / +74,0 % / rot · KPI 04: 3,3 / −8,9 % / grau.
Mainz – Paderborn und Elversberg – Bayer Leverkusen: Aufsteiger, Hauptwerte „–“, Datenbasis mit „V“.

## Rückweg

```bash
cd /docker/football-dashboard
git reset --hard ff4fbe8          # Stand nach Etappe B
docker compose up -d --build football-dashboard
```
