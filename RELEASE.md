# Release: Version 0.27.1 – www leitet weiter

**Stand:** 26.11.2026 · Version 0.27.1 · Befund nach dem Livegang (Carsten 26.11.2026), Entscheid Carsten 25.11.2026

**Commit:** Version 0.27.1: www leitet auf die Adresse ohne www weiter

## Was ändert sich?

- **`www.soccer-intelligence.com`** funktioniert: Traefik holt ein Zertifikat für `www` und leitet jede Adresse dauerhaft
  (301) auf dieselbe Adresse ohne www weiter, z. B. `www.soccer-intelligence.com/en/` → `soccer-intelligence.com/en/`.
  Bisher gab es unter `www` kein Zertifikat (Browser-Warnung) und keine Seite (404).
- Umgesetzt nur mit Labels unseres Containers `soccer-website`; die Traefik-Grundkonfiguration bleibt unverändert
  (sie leitet `http://` schon heute auf `https://` um und holt Zertifikate über Port 80).
- Doku: Stand 0.27 eingespielt (Website live, Komprimierung und HSTS geprüft, PageSpeed mobil 100).

## Einspielen

```bash
tmux new -s release0271
```

```bash
bash /docker/football-dashboard/tools/einspielen.sh github
```

Ab jetzt baut das Skript die Website selbst mit (kein eigener Livegang-Befehl mehr).

## Erwartungswerte

- Tests rund **758 bestanden**, keine Fehler (hier ohne echte Daten: 758 bestanden, 18 übersprungen).
- Schritt 5: „Container laufen (Dashboard, Import, Vorschau, Website) · / = 301 · /de/ = 200 …“, `/vorschau/` = 401;
  drei Testmails. Dashboard-Fusszeile: „Version 0.27.1 – www leitet weiter“.
- Nach rund 1 Minute (Zertifikat für www) auf dem Server:
  ```bash
  curl -sI https://www.soccer-intelligence.com/en/ | grep -iE "^HTTP|^location"
  ```
  Erwartet: `HTTP/2 301` und `location: https://soccer-intelligence.com/en/`.
  ```bash
  curl -sI http://www.soccer-intelligence.com/de/methodik/ | grep -iE "^HTTP|^location"
  ```
  Erwartet: `308` auf `https://www.soccer-intelligence.com/de/methodik/` (Traefik), danach wie oben 301 ohne www.

## Im Browser prüfen

1. `www.soccer-intelligence.com` eintippen → landet ohne Warnung auf `https://soccer-intelligence.com/de/`.
2. `www.soccer-intelligence.com/en/` → `https://soccer-intelligence.com/en/`.
3. Startseite, Dashboard (`/dashboard/`) und Vorschau (`/vorschau/`) wie bisher.
