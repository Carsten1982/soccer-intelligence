# Soccer Intelligence – Etappe D: Top Anomalien

**Stand:** 31.10.2026 · Version 0.6

## Was ist neu?

1. **Startseite „Top Anomalien“:** höchstens vier Karten aus beiden Ligen zusammen (aktueller Spieltag). Regeln gemäss Regelwerk 2.6: nur KPI 02 und KPI 04, nur leichte/starke Anomalien, ohne vorläufige Werte und ohne verschobene/abgesagte Spiele; stark vor leicht, dann grösste Abweichung; pro Begegnung höchstens ein Eintrag; kein Auffüllen. Ohne Anomalien erscheint: „Für den aktuellen Spieltag liegen keine Anomalien vor.“
2. Jede Karte: Rang, Liga · Spieltag, Begegnung, KPI, Hauptwert, Abweichung, Einstufung, Text gemäss Regelwerk, Link „Zur Liga“.
3. **Spieltag-Pfeile grösser**, Spieltagsfeld ohne Zeilenumbruch.
4. Doku: Spielplan-Regeln als bestätigt markiert, Server-Update vermerkt, Status Etappe D, CHANGELOG.

Geänderte Dateien: `app/core/top.py` (neu), `app/views/top_anomalien.py`, `app/views/components.py`, `app/app.py`, `app/core/settings.py`, `tests/test_top.py` (neu, 13 Tests), `tests/test_ui.py`, `docs/01`, `docs/04`, `docs/05`, `CHANGELOG.md`.

Nicht geändert: Dockerfile, docker-compose.yml, requirements.txt, Traefik, Excel-Dateien, andere Container.

## Erwartet nach dem Einspielen

- Tests: alle bestanden (rund 146, 1 übersprungen)
- Startseite: Überschrift „Top Anomalien“, bis zu 4 Karten. Mit dem lokalen Prüfstand (ohne Augsburg – Frankfurt) waren es:
  1. Crystal Palace – Manchester City · KPI 04 · −25,9 % · leicht
  2. Aston Villa – Arsenal · KPI 04 · −25,9 % · leicht
  3. Hoffenheim – Dortmund · KPI 04 · +24,6 % · leicht
  4. Stuttgart – FC Koln · KPI 02 · +23,2 % · leicht
  Auf dem Server ist Augsburg – Frankfurt zusätzlich im Spielplan; das kann die Bundesliga-Einträge verändern.

## Rückweg

```bash
cd /docker/football-dashboard
git reset --hard 4c3be5c          # Stand nach den Anpassungen zu Etappe C
docker compose up -d --build football-dashboard
```
