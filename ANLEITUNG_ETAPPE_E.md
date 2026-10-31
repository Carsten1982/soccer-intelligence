# Soccer Intelligence – Etappe E: Dashboard-Zugang

**Stand:** 31.10.2026 · Version 0.7 · freigegeben von Carsten am 31.10.2026

## Was ist neu?

| Adresse | Vorher | Nachher |
|---|---|---|
| `soccer-intelligence.com/` | Dashboard, offen | Platzhalterseite, öffentlich (neuer Container `soccer-placeholder`) |
| `soccer-intelligence.com/dashboard` | – | Dashboard **mit Passwortabfrage** |
| `/dashboard/bundesliga`, `/dashboard/premier-league`, `/dashboard/datenqualitaet` | – | Bereiche, ebenfalls geschützt |

- Suchmaschinen: Passwortabfrage + Hinweis `X-Robots-Tag: noindex, nofollow` + `robots.txt` sperrt `/dashboard`.
- Zugangsdaten nur in `.env` auf dem Server (Passwort als bcrypt-Hash), gesetzt mit `tools/dashboard_passwort.sh`. Nichts davon in Git.
- Fehlt der Eintrag in `.env`, startet Compose nicht (statt ohne Passwort).

Geändert: `docker-compose.yml`, `app/core/settings.py` (Version), Doku (`01`, `05`, `CLAUDE.md`, `CHANGELOG.md`).
Neu: `placeholder/index.html`, `placeholder/robots.txt`, `tools/dashboard_passwort.sh`, `tests/test_deploy.py` (7 Tests).
Nicht geändert: Traefik-Grundkonfiguration, Dockerfile, requirements, Excel-Dateien, andere Container, App-Code (bis auf die Versionsnummer).

## Ablauf (Befehle im Chat)

1. Backup (inkl. `docker-compose.yml` und `.env`)
2. Paket einspielen, Unterschied der `docker-compose.yml` anzeigen → **an Claude schicken, warten**
3. Zugang setzen: `bash tools/dashboard_passwort.sh`
4. Tests im Wegwerf-Container (erwartet rund 152 bestanden, 1 übersprungen)
5. Aktivieren: `docker compose up -d --build football-dashboard soccer-placeholder`
6. Prüfen: `/` → 200, `/robots.txt` → 200, `/dashboard/` → 401 (ohne Passwort); im Browser anmelden
7. Commit, Push, Aufräumen

## Rückweg

```bash
cd /docker/football-dashboard
docker compose rm -sf soccer-placeholder                 # nur unseren Platzhalter-Container entfernen
git reset --hard 1a1c527                                 # Stand nach Etappe D
docker compose up -d --build football-dashboard          # Dashboard wieder unter /
```

`.env` bleibt dabei unverändert (wird ohne Etappe E einfach nicht verwendet).
