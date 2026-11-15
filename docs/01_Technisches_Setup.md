# Soccer Intelligence – Technisches Setup und Betrieb

**Stand:** 14.11.2026 · **Verantwortlich:** Carsten Thiele · **Mitwirkende:** ChatGPT (Server-Setup, Review), Claude (Daten, Architektur, Code)

Diese Datei ist die **einzige Stelle** für Projektstand, Versionen, Server, Abläufe und Architektur. Fachliche Regeln stehen in `02`–`06`, Änderungen im `CHANGELOG.md`, das aktuelle Release in `RELEASE.md`.

---

## 0. Stand und Versionen

**In Betrieb:** Version 0.13 – Dashboard mit vier Ligen (Bundesliga, Premier League, Serie A, LaLiga), KPI 01–09 mit den festgelegten Schwellen (positiv/negativ getrennt, KPI 03 je Liga), Top Anomalien, Datenqualität und Sensitivitätsanalyse; Datenbank 2018/19–2026/27 mit Referenzsaison 2018/19 (KPI-Regelwerk 1.2). Passwortschutz unter `/dashboard`, Platzhalterseite unter `/`.

**Als Nächstes:** Datenlieferung über API-Football (Spezifikation v0.3 in `06_Datenlieferung.md`, freigegeben 15.11.2026; Pro-Abo aktiv bis 15.02.2027; Vollvergleich und Bereinigung erledigt, bereinigte Datenbank aufspielen; als Nächstes Tagesbetrieb, Vollvergleich aller Saisons, Umstellung bei mindestens 99 % Übereinstimmung, Tagesbetrieb; Etappe G) · Rundum-Prüfung des Codes, bevor das Frontend beginnt · KPI-Erweiterungen und Kombinationen (z. B. xG) · Gewichtung der Top Anomalien (Regelwerk, Punkt 17) · öffentliche Website.

| Version | Etappe | Inhalt | Eingespielt | Git | Tests |
|---|---|---|---|---|---|
| 0.13 | Neue Schwellen | Gültige Schwellen positiv/negativ getrennt, KPI 03 je Liga; Sensitivitätsanalyse nach Entwurf C (vier Zeilen je KPI, Bewertung auch für stark) | 14.11.2026 | `89128e5` | 428 |
| 0.12 | Sensitivitätsanalyse | Spielwiese ersetzt: vier Schwellen je KPI, Häufigkeit mit Spieltagsabdeckung, Ergebnisqualität gegen Grundquote mit Wilson-Spanne und Empfehlung | 12.11.2026 | `1482bc3` | 398 |
| 0.11 | Neue Datenbank | Datenbank 2018/19–2026/27, Referenzsaison, neue Saisonauswahl, Warnung „Saison fehlt“ | 10.11.2026 | `034e57a` | 376 |
| 0.10.1 | GitHub | GitHub als einzige Quelle: einspielen.sh github, automatische Tests, robuster Rückweg | 10.11.2026 | `20275e9` | 350 |
| 0.10.1 | Skript | Einspiel-Skript `tools/einspielen.sh`, Rückweg `tools/zurueck.sh` | 09.11.2026 | `0dafea3` | 348 |
| 0.10.1 | Doku | Dokumentation zusammengeführt (nur Doku, kein Code) | 08.11.2026 | `0d4d856` | – |
| 0.10.1 | I.1 Nachtrag | Simulation: Info-Fenster, Schwellen in der Ergebnisqualität, neue Saisonauswahl | 08.11.2026 | `9684edb` | 345 |
| 0.10 | I.1 | Simulation – Spielwiese: Häufigkeit und Ergebnisqualität je KPI mit eigenen Schwellen (Regelwerk 11) | 08.11.2026 | `dbd90c5` | 345 |
| 0.9.2 | H.2 | Stabilität (zweite Code-Prüfung, S1–S6) | 08.11.2026 | `291eeac` | 319 |
| 0.9.1 | H.1 | Aufräumen und Tempo (erste Code-Prüfung) | 08.11.2026 | `b5a7ea8` | 287 |
| 0.9 | H | KPI 05–09, zwei Nachkommastellen, Top Anomalien über KPI 02–09, Schwellen-Datei | 08.11.2026 | `51e595b` | 260 |
| 0.8 | F | Vier Ligen (Serie A, LaLiga), unabhängige Gegenrechnung | 07.11.2026 | `cc00dd9` | 171 |
| 0.7 | E | Dashboard unter `/dashboard` mit Passwort, Platzhalter unter `/` | 31.10.2026 | `64a684b` | 152 |
| 0.6 | D | Top Anomalien | 31.10.2026 | `1a1c527` | 145 |
| – | C, Anpassungen | Spieltag-Pfeile, Navigation, Referenz-Datenbank für Tests | 31.10.2026 | `4c3be5c` | 140 |
| – | C | KPI 01–04, Häufigkeit der Anomalien | 31.10.2026 | `8cb5f0f` | 126 |
| – | B | Spielplan, aktueller Spieltag, Datenqualität | 31.10.2026 | `ff4fbe8` | 72 |
| – | A | Datenbank einlesen und prüfen (Schritt 1) | 31.10.2026 | `ffec276` | 26 |

- **Rückweg** zu einer Version: Abschnitt 6.1.
- **Prüfprotokolle** grösserer Etappen: `docs/tests/pruefprotokoll_*.md`.
- **Frühere Anleitungen** (`ANLEITUNG_*.md`): seit 09.11.2026 durch `RELEASE.md` und Abschnitt 6.1 ersetzt. Sie bleiben im Git-Verlauf erhalten.
- **Daten:** Datenbank SHA-256 `451348b6…` (2018/19–2026/27, seit 10.11.2026; vorher `f37e36d3…`), `02_Datenbasis.md`; Prüfprotokoll `docs/tests/pruefprotokoll_datenbank_2018-2027.md`. **Bereinigte Fassung `3a258961…` (15.11.2026) zum Aufspielen bereit** (`02`, Abschnitt 4e; Prüfprotokoll `docs/tests/pruefprotokoll_api.md`). Spielplan mit vier Blättern (`04_Spielplan.md`).

---

## 1. Projektziel

Fussball-Analyseplattform auf Basis historischer Spieldaten (Bundesliga, Premier League, Serie A, LaLiga). Auffälligkeiten („Anomalien“) anstehender Partien werden erkannt und angezeigt. Lernprojekt, nicht kommerziell.

Ausbaustufen:
1. Excel-Datenbank, von Carsten gepflegt.
2. Internes Dashboard mit allen anstehenden Partien und Analysen.
3. Öffentliche Website (Mobile First), als eigenes Projekt, das einen Datenexport des Rechenkerns anzeigt.

---

## 2. Grundsatzentscheidungen

| Datum | Entscheidung |
|---|---|
| 09.11.2026 | **GitHub ist die einzige Quelle** (Carsten): Änderungen entstehen nur noch auf GitHub (Claude Code mit dem Repository verbunden, Pull Request mit automatischen Tests, Freigabe durch Carsten mit „Squash and merge“). Der Server holt mit `tools/einspielen.sh github` ab und ändert selbst nichts mehr. Das Paket `release.zip` bleibt als Ersatz (Abschnitt 6.1). |
| 08.11.2026 | **Neue KPIs:** 5 Frontend-KPIs (05 Ecken, 06 Tore 1. HZ, 07 Tore 2. HZ, 08 Beide Teams treffen, 09 Schüsse aufs Tor) und 4 Simulations-KPIs nur im Backend (10/11 Angriff gegen Abwehr HZ 1/2, 12 Offensivdruck, 13 Abschluss-Effizienz). Schwellen pro Liga und KPI einstellbar (Datei `app/config/schwellen.toml`, Standard ±20/±35 %, kein eigener Tab). Kompakte Liga-Tabelle mit Details per Aufklappen. Reihenfolge: Spezifikation + Testfälle → Etappe H (KPI 05–09) → Etappe I (Simulations-Tab). Details: KPI-Regelwerk v2.0, CHANGELOG. |
| 08.11.2026 | **Etappe H freigegeben (Carsten):** Testfälle KPI 05–09 bestätigt; **alle KPIs mit zwei Nachkommastellen** (auch Abweichung, Einstufung nach gerundetem Wert); **Top Anomalien über KPI 02–09** (bisherige Rangfolge, Gewichtung später); kompaktere Liga-Tabelle mit Aufklappen, Design-Vorschlag vor der Umsetzung. Danach Etappe I: interner Tab zur Schwellen-Analyse je KPI und Liga, Feintuning, Gewichtung der Top Anomalien. Ablauf: md-Dateien → Backup → Design-Vorschlag → Programmieren und Einspielen. |
| 07.11.2026 | **Spieltage mit verlegten Spielen:** Die bestehende Logik für den aktuellen Spieltag bleibt. Spiele, die mehr als 3 Tage ausserhalb des Hauptzeitraums ihres Spieltags liegen, werden im Spielplan als `verschoben` gepflegt (keine KPIs, keine Top Anomalie). Keine Pflege auf Tagesebene, keine Mehrheitsregel. Grundlage: Auswertung 2022/23–2025/26, betroffen unter 2 % der Spiele (`04_Spielplan.md`, Abschnitt 6). |
| 07.11.2026 | Blatt für Italien heisst in Datenbank und Spielplan **`Serie A`** (bisher `Seria A`); der Code wird in Etappe F angepasst. Blattnamen ohne Leerzeichen: `LaLiga`. |
| 06.11.2026 | **Erweiterung auf vier Ligen** (Serie A, LaLiga) als nächster Schritt (Etappe F), vor der Datenlieferung (Etappe G). Reihenfolge: Daten auf den Server → Sicherung in GitHub → Etappe F → Etappe G → neue KPIs → öffentliche Website. |
| 02.11.2026 | **Reihenfolge nach Phase 1:** zuerst die Datenquelle klären, die neuen KPIs können parallel laufen, danach die öffentliche Website. Grund: Teamnamen, IDs, Nutzungsrechte und Spielplan-Pflege beeinflussen die Website. *(Präzisiert am 06.11.2026, siehe oben.)* |
| 31.10.2026 | **Die md-Dateien in `docs/` sind die einzige massgebliche Quelle.** Die Word-Dokumente (`word/`) sind Archiv und werden nicht mehr gepflegt. Änderungen nur noch in den md-Dateien, mit Eintrag im CHANGELOG. |
| 31.10.2026 | **Etappe E:** öffentliche Platzhalterseite unter `/` (Variante b), ein gemeinsamer Zugang zum Dashboard (Benutzername und Passwort nur in `.env`), Hinweis `noindex` für Suchmaschinen. |
| 31.10.2026 | Spieltag-Pfeile in den Liga-Bereichen (je Liga, nicht in die Zukunft, Auswahl in der Adresse); Top Anomalien immer aktueller Spieltag. |
| 30.10.2026 | **Dashboard mit Passwortschutz** unter `https://soccer-intelligence.com/dashboard`. Schutz serverseitig über Traefik für alle Adressen unter `/dashboard`. Zugangsdaten nur als Hash in einer Konfigurationsdatei auf dem Server. Ersetzt die Entscheidung vom 25.10.2026. |
| 30.10.2026 | Startseite `https://soccer-intelligence.com` zeigt bis zur öffentlichen Website weiterhin die **Platzhalterseite** (öffentlich). |
| 30.10.2026 | Bereiche des Dashboards: `/dashboard` = Top Anomalien, `/dashboard/bundesliga`, `/dashboard/premier-league`. Jede weitere aktivierte Liga erhält automatisch einen eigenen Bereich nach demselben Muster (z. B. `/dashboard/laliga`). |
| 30.10.2026 | Das Dashboard bleibt ein reines Ansichts-Werkzeug: keine Funktionen zum Importieren, Bearbeiten oder Verwalten in der App. |
| 30.10.2026 | **Keine Vereinslogos**, weder im Dashboard noch auf der öffentlichen Website (rechtliche Gründe). |
| 30.10.2026 | **Ein KPI-Regelwerk:** gültig ist nur `docs/03_KPI_Regelwerk.md`. `03_KPI_Grundregeln.md` und `docs/kpis/` sind gelöscht. ~~Massgebliche Quelle bleibt das Word-Dokument „Definition der Dashboard-KPIs“.~~ (ersetzt am 31.10.2026, siehe oben) |
| 30.10.2026 | Im Text „Keine Anomalie“ (KPI 02 und 04) steht die Abweichung immer mit Vorzeichen, bei 0,0 % ohne. |
| 28.10.2026 | Ligareferenz über die Spalte `Gameday` (letzte 20 Spieltage). Spalte in der Datenbank ergänzt. |
| 25.10.2026 | Daten werden **nur über die Datei auf dem Server** geändert, nie über die App. |
| 25.10.2026 | **Einzige gültige Datenquelle:** `data/Database-Soccer-Intelligence.xlsx` |
| 25.10.2026 | Spielplan (anstehende Partien) kommt als **eigene Datei** `data/Spielplan.xlsx`, getrennt von den historischen Daten. Aufbau: `04_Spielplan.md` (Datum von / Datum bis, beschlossen 30.10.2026). |
| 25.10.2026 | Start mit abgeschlossenen Saisons 2020/21–2025/26. Die laufende Saison 2026/27 wird nach dem Prototyp ergänzt. |
| 25.10.2026 | Keine externe Fussball-API vorerst. *(Stand 02.11.2026: Eine regelmässige Datenlieferung wird geprüft, siehe `06_Datenlieferung.md`. Noch keine Entscheidung.)* |
| 25.10.2026 | KPIs werden von Carsten definiert, bevor Analysen gebaut werden. Keine KPIs ohne Abstimmung. |

---

## 3. Server

| | |
|---|---|
| Anbieter / Host | Hostinger VPS, `srv1774622.hstgr.cloud` |
| IP | 72.60.132.157 |
| Betriebssystem | Ubuntu 24.04.4 LTS |
| Ressourcen | 48 GB Speicher (16 % belegt), 3,8 GB RAM |
| Domain | https://soccer-intelligence.com |

### Container auf dem Server

| Container | Zweck | Gehört zu uns? |
|---|---|---|
| `football-dashboard` | Soccer Intelligence (Streamlit), unter `/dashboard` | **ja** |
| `soccer-placeholder` | Platzhalterseite unter `/` (nginx, statisch), seit Etappe E | **ja** |
| `article-generator` | Artikeltext-Generator | nein – nicht anfassen |
| `n8n-wxit-n8n-1` | n8n Automatisierung | nein – nicht anfassen |
| `traefik-traefik-1` | Webserver / HTTPS für alle Anwendungen | nein – nicht anfassen |
| Chatbot | Ort unklar (kein eigener Container gefunden) | nein – offen |

### So kommt die Website ins Internet

```
Besucher → https://soccer-intelligence.com/            → Traefik → soccer-placeholder (nginx, öffentlich)
Besucher → https://soccer-intelligence.com/dashboard…  → Traefik → Passwortabfrage (BasicAuth)
                                                                  → football-dashboard (Streamlit, Port 8501)
```

- Traefik läuft im Host-Netzwerk, erledigt HTTPS/Zertifikat und findet beide Container automatisch über ihre Docker-Labels.
- Bei gleicher Domain gewinnt die längere Regel: Alles unter `/dashboard` geht zum Dashboard, alles andere zur Platzhalterseite.
- Antworten des Dashboards tragen den Hinweis `X-Robots-Tag: noindex, nofollow` (Suchmaschinen sollen nichts aufnehmen). `robots.txt` der Platzhalterseite sperrt `/dashboard` zusätzlich.

- Port 8501 ist nur lokal gebunden (`127.0.0.1`), also von aussen nicht direkt erreichbar.
- Traefik liest die Container-Adresse selbständig aus Docker. Ein Neubau des Containers bricht das Routing nicht.

### Zugang (Etappe E, 31.10.2026)

- Streamlit läuft unter dem Pfad `/dashboard` (Umgebungsvariable `STREAMLIT_SERVER_BASE_URL_PATH=dashboard` in `docker-compose.yml`).
- Der Passwortschutz schützt alle Unterseiten und die Datenverbindung der App.
- Betroffen sind nur die Labels des eigenen Containers `football-dashboard` und ein neuer, kleiner Container für die Platzhalterseite. Die Traefik-Grundkonfiguration, n8n und alle anderen Anwendungen bleiben unverändert.
- Ein gemeinsamer Zugang (Benutzername und Passwort). Beides steht nur in `.env` auf dem Server: Benutzername im Klartext, Passwort als bcrypt-Hash. Nicht in Git, nicht in der Dokumentation.
- Fehlt die Zeile in `.env`, startet `docker compose` gar nicht erst (Fehlermeldung „SOCCER_DASHBOARD_AUTH fehlt in .env“), statt das Dashboard ungeschützt zu veröffentlichen.
- Einschränkung: Es gibt keinen „Abmelden“-Knopf. Man meldet sich durch Schliessen des Browsers ab.

---

## 4. Projektordner `/docker/football-dashboard/`

```
/docker/football-dashboard/
├── .github/workflows/tests.yml automatische Tests auf GitHub (bei Push und Pull Request)
├── Dockerfile                  Bauplan des Containers (Python 3.12, Streamlit)
├── docker-compose.yml          Container-Konfiguration inkl. Traefik-Labels (Dashboard + Platzhalter)
├── .env                        Zugang zum Dashboard (Benutzername + Passwort-Hash), nicht in Git
├── requirements.txt            Python-Pakete (Versionen fest); requirements-dev.txt zusätzlich pytest
├── app/                        Anwendung (Aufbau Abschnitt 7)
├── tests/                      automatische Tests; tests/referenz/ = feste Datenbank-Stände für die Testfälle
├── placeholder/                Platzhalterseite unter / (index.html, robots.txt)
├── tools/                      einspielen.sh (Release), zurueck.sh (Rückweg), dashboard_passwort.sh (Zugang)
├── data/                       nicht in Git: Database-Soccer-Intelligence.xlsx, Spielplan.xlsx (GÜLTIG)
├── backup/                     Sicherungen, nicht in Git
├── docs/                       Dokumentation, massgebliche Quelle (md)
├── word/                       Archiv der Word-Dokumente (nicht mehr gepflegt)
├── CLAUDE.md                   Einstieg und Regeln für Claude
├── CHANGELOG.md                Änderungsprotokoll
└── RELEASE.md                  das aktuelle Release (wird mit jeder Änderung ersetzt)
```

**docker-compose.yml:** Die Datei selbst ist massgeblich und wird hier nicht kopiert. Sie enthält zwei eigene Container:
- **`football-dashboard`:**
  - `./data:/data:ro`: Die Excel-Dateien sind nur lesbar.
  - Port nur lokal (`127.0.0.1:8501`), Pfad `/dashboard` (`STREAMLIT_SERVER_BASE_URL_PATH`).
  - Traefik-Labels mit Passwortschutz: Hash aus `.env`, Variable `SOCCER_DASHBOARD_AUTH`. Fehlt sie, startet Compose nicht.
  - Kopfzeile `X-Robots-Tag: noindex, nofollow`.
- **`soccer-placeholder`:** nginx 1.27, nur lesend.

Die Tests in `tests/test_deploy.py` prüfen diese Punkte automatisch.

### Installierte Versionen im Container

| Paket | Version |
|---|---|
| Python | 3.12.15 |
| streamlit | 1.66.1 |
| pandas | 3.1.0 |
| openpyxl | 3.1.5 |

Seit Etappe A (31.10.2026) legt `requirements.txt` genau diese Versionen fest (`streamlit==1.66.1`, `pandas==3.1.0`, `openpyxl==3.1.5`).

Kontrolle nach jedem Neubau:

```bash
docker exec football-dashboard pip freeze | grep -iE "^(streamlit|pandas|openpyxl)=="
```

Erwartet: genau die drei Versionen oben. Weicht etwas ab → Ursache klären, bevor weitergearbeitet wird.

---

## 5. Schutzregeln (verbindlich)

1. Nur im Ordner `/docker/football-dashboard/` arbeiten.
2. `article-generator`, Chatbot, n8n und Traefik nicht verändern oder neu starten.
3. Kein `docker compose down`, keine globalen Docker-Befehle, keine Änderungen an gemeinsamen Netzwerken.
4. Traefik-Labels und Ports nicht ändern (nur mit eigener Freigabe). Letzte Freigabe: Etappe E, 31.10.2026.
5. Vor jeder Änderung: Backup der betroffenen Dateien.
6. Neu bauen nur den eigenen Service: `docker compose up -d --build football-dashboard` (die Platzhalterseite `soccer-placeholder` gehört ebenfalls zu uns und muss bei Code-Änderungen nicht neu gestartet werden)
7. Danach immer prüfen: `docker ps` → alle Container laufen weiter.
8. Keine Passwörter, Tokens oder Schlüssel in Code oder Dokumentation. Die Zugangsdaten für den Dashboard-Passwortschutz liegen nur als Hash in einer Konfigurationsdatei auf dem Server (z. B. `.env`, nicht in Git).
9. Fehlende Statistikwerte nie durch 0 oder Schätzungen ersetzen.
10. Änderungen erst nach Freigabe durch Carsten.

---

## 6. Abläufe

### 6.1 Release einspielen

**GitHub ist die einzige Quelle** (seit 09.11.2026). Jede Änderung entsteht auf GitHub, der Server holt nur ab.

1. **Claude arbeitet auf GitHub.** In einer Sitzung von Claude Code (claude.ai/code, mit dem Repository `Carsten1982/soccer-intelligence` verbunden). Claude legt die Änderung auf einem eigenen Zweig ab (`claude/…`), mit neuer `RELEASE.md` (Inhalt, Erwartungswerte, was im Browser zu prüfen ist).
2. **Carsten prüft auf GitHub.** „Create PR“ (Pull Request) öffnen. Dort stehen alle Änderungen Zeile für Zeile, und die **automatischen Tests** laufen (`.github/workflows/tests.yml`, rund 3 Minuten). Erst bei grünem Haken: „Squash and merge“ (ein Commit je Änderung, gut lesbarer Verlauf).
3. **Server holt ab:**
   ```bash
   bash /docker/football-dashboard/tools/einspielen.sh github
   ```
   Das Skript zeigt, was neu ist, macht ein Backup, übernimmt genau den Stand von GitHub (nur „fast-forward“, kein eigener Commit), testet noch einmal mit den echten Excel-Dateien, baut nur `football-dashboard` neu und prüft `200`/`401`. Danach im Browser prüfen, was in `RELEASE.md` steht, und mit `j` bestätigen.

Das Skript stoppt, wenn auf dem Server etwas geändert wurde, das nicht auf GitHub ist (`git status` nicht leer oder eigene Commits). Bei einem Fehler hält es an, setzt nichts selbst zurück und nennt den Rückweg. Protokolle (Tests, Neubau) liegen im Backup-Ordner. Die automatischen Tests auf GitHub laufen ohne die Excel-Dateien aus `data/` (die liegen nur auf dem Server); dafür prüfen sie auch die Einspiel-Skripte in einem Probelauf (`tests/test_einspielen.py`, im Test-Container auf dem Server übersprungen, weil dort `git` fehlt).

**Rückweg zum Stand vor dem letzten Release:**

```bash
bash /docker/football-dashboard/tools/zurueck.sh
```

Fragt vorher nach. Schon übernommen oder committet: Ein Gegen-Commit stellt genau den alten Stand wieder her und wird gepusht (nichts geht verloren, Server und GitHub bleiben gleich). Noch nicht committet (Weg Paket, Antwort `n`): Dateien zurücksetzen, neue Dateien aus dem Paket entfernen. Danach Neubau und Prüfung. Die Excel-Dateien bleiben unberührt.

**Ersatz: Paket `release.zip`** (wenn GitHub nicht geht). Das Paket enthält `RELEASE.md` mit dem Commit-Text (Zeile `**Commit:** …`); sollen Dateien gelöscht werden, liegt `release_loeschen.txt` bei (eine Datei je Zeile). Mit WinSCP hochladen (Projektordner oder `/root`, auch als `release_2.zip`), dann `bash /docker/football-dashboard/tools/einspielen.sh` (ohne `github`). Am Schluss fragt es „Commit und Push machen (j/n)“. Das Skript stoppt, wenn GitHub schon weiter ist als der Server.

**Ohne Skript** (Notfall) – die Schritte für ein Paket einzeln:

1. **Backup.** `git status` muss leer sein. Am Schluss steht der Git-Stand vorher.
   ```bash
   cd /docker/football-dashboard && git status --short && B=backup/$(date +%F_%H%M)_vor_release && mkdir -p "$B" && git rev-parse --short HEAD > "$B/git_stand.txt" && tar czf "$B/code_docs.tgz" app tests docs *.md && ls -la "$B" && cat "$B/git_stand.txt"
   ```
2. **Paket** `release.zip` mit WinSCP hochladen und entpacken. Der Befehl holt die Datei auch aus `/root`:
   ```bash
   cd /docker/football-dashboard && { [ -f release.zip ] || mv /root/release.zip . ; } && python3 -m zipfile -e release.zip . && rm release.zip && git status --short
   ```
3. **Tests** im Wegwerf-Container (Projekt nur lesend eingebunden).
   - `tests` am Ende ist wichtig, sonst sammelt pytest auch `backup/`.
   - `SI_DATA_DIR=/src/data` ist wichtig, sonst finden die Seitentests die Excel-Dateien nicht.
   - Bei Fehlern: **Stopp**, Ausgabe an Claude.
   ```bash
   cd /docker/football-dashboard && docker run --rm -v "$PWD":/src:ro -e SI_DATA_DIR=/src/data -e PYTHONDONTWRITEBYTECODE=1 -w /src python:3.12-slim sh -c "pip install -q --root-user-action=ignore -r requirements-dev.txt && python -m pytest -q -p no:cacheprovider tests" 2>&1 | tail -15
   ```
4. **Aktivieren** (nur unser Container) und **prüfen**. Erwartet: `200` und `401`.
   ```bash
   cd /docker/football-dashboard && docker compose up -d --build football-dashboard && sleep 5 && docker ps --format "table {{.Names}}\t{{.Status}}" && docker logs football-dashboard --tail 8 && curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/ ; curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/dashboard/
   ```
5. **Im Browser** prüfen, was in `RELEASE.md` steht.
6. **Commit und Push** mit dem Text aus `RELEASE.md`. Die Git-Nummer der letzten Zeile an Claude schicken.
   ```bash
   cd /docker/football-dashboard && git add -A && git commit -m "<Text aus RELEASE.md>" && git push && git log -1 --oneline
   ```

Rückweg ohne Skript (noch nicht committet): `cd /docker/football-dashboard && git reset --hard <Git-Stand vorher> && docker compose up -d --build football-dashboard`

### 6.2 Neue Excel-Datei aufspielen

Grundsatz: Die neue Datei wird **erst geprüft und dann** zur gültigen Datenquelle. Die App liest nur `Database-Soccer-Intelligence.xlsx`. Eine Datei mit anderem Namen in `data/` wird ignoriert.

1. **Hochladen unter Zwischennamen:** `data/upload.xlsx` (WinSCP).
2. **Prüfen** mit allen Prüfregeln aus `02_Datenbasis.md`:
   ```bash
   docker exec football-dashboard python -c "
   from pathlib import Path
   from core.loader import load_database
   db = load_database(Path('/data/upload.xlsx'))
   print('Fehler:', db.count('Fehler'), '| Warnungen:', db.count('Warnung'), '| Hinweise:', db.count('Hinweis'))
   for i in db.issues:
       if i.level != 'Hinweis': print(i.level, i.sheet, i.check, i.match_id, i.message)
   "
   ```
   Erwartet: `Fehler: 0`. Neue Warnungen vor dem Austausch klären. **Bei Fehlern: Stopp**, Datei korrigieren und erneut hochladen.
3. **Sichern und austauschen.** `mv` im selben Ordner ist sofort komplett, die App liest nie eine halbe Datei.
   ```bash
   cd /docker/football-dashboard && cp -p data/Database-Soccer-Intelligence.xlsx backup/Database-Soccer-Intelligence_$(date +%F_%H%M).xlsx && mv data/upload.xlsx data/Database-Soccer-Intelligence.xlsx && sha256sum data/Database-Soccer-Intelligence.xlsx
   ```
4. **Kontrolle:** Die App liest die neue Datei beim nächsten Seitenaufruf automatisch, ohne Neustart. Bereich Datenqualität ansehen und die Prüfsumme in `02_Datenbasis.md` und im CHANGELOG eintragen.
5. **Rückweg:** letzte Sicherung zurückkopieren.
   ```bash
   cd /docker/football-dashboard && ls -t backup/Database-Soccer-Intelligence_*.xlsx | head -3
   cp -p backup/Database-Soccer-Intelligence_<DATUM_ZEIT>.xlsx data/restore.xlsx && mv data/restore.xlsx data/Database-Soccer-Intelligence.xlsx
   ```

Für `Spielplan.xlsx` gilt derselbe Ablauf. Die Prüfregeln stehen in `04_Spielplan.md`.

**Saisonwechsel (seit Version 0.11, KPI-Regelwerk 1.2):** Die älteste Saison der Datenbank ist die Referenzsaison: Sie liefert nur die Vorsaison und wird nie ausgewertet. Beginnt eine neue Saison (z. B. 2027/28):

1. In der Excel-Datei in allen vier Ligablättern die Zeilen der ältesten Saison löschen (z. B. 2018/19). Nur ganze Zeilen löschen, nie einzelne Zellen, sonst verrutschen die Spalten (Fehler vom 10.11.2026, `02_Datenbasis.md`, Abschnitt 4d). Einträge im Blatt *Datenhinweise* zu gelöschten Spielen ebenfalls löschen.
2. Die neue Saison wie gewohnt ergänzen und die Datei nach den Schritten 1–4 oben aufspielen.
3. Kontrolle im Bereich Datenqualität: je Liga „Referenzsaison: 2019/20 (nur Vorsaison, nicht ausgewertet)“, keine Warnung „Saison fehlt“. Im Code ist nichts zu ändern.

### 6.3 Dashboard-Zugang setzen oder Passwort ändern

```bash
cd /docker/football-dashboard
bash tools/dashboard_passwort.sh                 # fragt Benutzername und Passwort (verdeckt, zweimal)
docker compose up -d football-dashboard          # Zugang neu einlesen (kein Neubau nötig)
```

- Gespeichert wird nur der bcrypt-Hash in `.env` (Zeile `SOCCER_DASHBOARD_AUTH`). Das Passwort erscheint weder auf dem Bildschirm noch im Befehlsverlauf.
- Die alte `.env` wird vorher nach `backup/env_<Datum>` gesichert. Andere Zeilen in `.env` bleiben unverändert.
- Bei verschiedenen Eingaben oder einem Fehler bricht das Skript ab und ändert nichts.

### 6.4 Zustand prüfen (nur lesend)

```bash
cd /docker/football-dashboard && git log -1 --oneline && docker ps --format "table {{.Names}}\t{{.Status}}" && docker logs football-dashboard --tail 20 && sha256sum data/*.xlsx
```

---

## 7. Architektur

Grundsatz (freigegeben 25.10.2026): Die Rechenlogik steht in `app/core`, ohne Oberfläche und testbar. `app/views` zeigt nur an. Dieselbe Logik soll später die öffentliche Website über einen Datenexport bedienen.

```
app/
├── app.py                Navigation; prüft beim Start ligen.toml, teams.toml und schwellen.toml
├── state.py              Laden mit Cache (neu laden bei geänderter Datei), KPI-Ergebnisse je Spieltag (H.1)
├── config/               Konfiguration, mit dem Code versioniert (Änderung -> Container neu bauen)
│   ├── ligen.toml        aktive Ligen, Adresse, Anzahl Teams (Etappe B)
│   ├── teams.toml        Teamliste: bekannte Teams ohne Datenbankeinträge, z. B. Aufsteiger (Etappe B)
│   └── schwellen.toml    Schwellen der Anomalie-Einstufung je Liga und KPI (Etappe H)
├── core/                 Kernlogik ohne Oberfläche (testbar)
│   ├── settings.py       Pfade, Pflichtblätter, Version
│   ├── schema.py         erwartete Struktur der Excel-Datei
│   ├── files.py          Prüfsumme einer Datei (H.1)
│   ├── loader.py         Einlesen + Strukturprüfung
│   ├── validation.py     Plausibilitätsprüfungen
│   ├── rows.py, issues.py  Prüfmeldungen (Fehler, Warnung, Hinweis)
│   ├── config.py         Einlesen der Konfiguration (Etappe B)
│   ├── fixtures.py       Spielplan einlesen und prüfen (Etappe B)
│   ├── matchday.py       aktueller Spieltag, Spieltagsübersicht (Etappe B)
│   ├── overview.py       Übersicht der Datenbank (Spiele je Saison)
│   ├── kpis.py           KPI 01–09 gemäss Regelwerk (Etappen C und H)
│   ├── thresholds.py     Schwellen aus schwellen.toml (Etappe H)
│   ├── results.py        KPI-Ergebnisse aller Begegnungen eines Spieltags (H.1)
│   ├── top.py            Auswahl der Top Anomalien (Etappe D, ab H über KPI 02–09)
│   ├── simulation.py     Ergebniskontrolle und Simulation der Schwellen (Etappe I.1)
│   └── frequency.py      Häufigkeit der Anomalien (Etappe C)
└── views/                Bereiche: Top Anomalien, je Liga, Datenqualität; components.py = Stil, Kopfbereich,
                          Sperrhinweis; kpi_table.py = kompakte Liga-Tabelle mit Aufklappen (Etappe H);
                          simulation.py = Bereich Simulation – Spielwiese (Etappe I.1)
tests/                    automatische Tests; gegenrechnung.py = unabhängige zweite KPI-Berechnung (Etappe F)
data/Spielplan.xlsx       anstehende Partien
docs/                     Dokumentation (01–06, tests/)
CLAUDE.md                 Projektübersicht für Claude Code
CHANGELOG.md              Änderungsprotokoll
```

---

## 8. Offene Punkte

- [ ] Ablauf: Knopf „Run workflow“ auf GitHub zum Einspielen (GitHub als einzige Quelle und automatische Tests erledigt 09.11.2026)
- [ ] Spielplan LaLiga 2026/27, Spieltag 1: späte Spiele mit Status `verschoben` pflegen (Pflegeregel `04_Spielplan.md`, Abschnitt 6). Prüfen, ob erledigt.
- [ ] Spielplan Premier League, Spieltag 1 (16.–20.08. statt gespielt 21.–24.08.): prüft Carsten
- [ ] Warnung zu Spiel-ID 11344 (Schusssumme): Wert korrigieren oder als Hinweis herabstufen?
- [ ] Offene Fragen an Footiqo, u. a. Spielplan, Spalte `Gameday`, Nutzungsrechte (`06_Datenlieferung.md`)
- [ ] Name des bisherigen Datenanbieters dokumentieren (`02_Datenbasis.md`, Regelwerk Abschnitt 8, Punkt 7)
- [ ] Öffentliche Website: Impressum und Datenschutzhinweis klären
- [ ] Server: Meldung „1 updates could not be installed automatically“ (unattended-upgrades) prüfen. Kein Upgrade auf Ubuntu 26.04 vorerst.
- [ ] Wo läuft der Chatbot? (nur zur Dokumentation)
- [ ] Aufräumen in `backup/` nach einigen Wochen stabilen Betriebs
- [ ] Offene KPI-Punkte im Regelwerk, Abschnitt 8 (nicht blockierend)

Erledigte Punkte stehen im CHANGELOG.

---

## 9. Ideen für später (erst nach stabiler erster Version)

| Idee | Notiz |
|---|---|
| ~~Spieltage im Dashboard vor- und zurückblättern~~ | umgesetzt am 31.10.2026 (Briefing 3.2) |
| Mehrheitsregel für den aktuellen Spieltag (07.11.2026 zurückgestellt) | Aktuell = Spieltag mit den meisten Spielen der nächsten 7 Tage; offene Spiele früherer Spieltage in einem Bereich „Nachholspiele“ mit KPIs. Nur nötig, falls verzerrte Spieltage deutlich häufiger werden als heute. |
| Internes Test-Datum (`testdatum` in der Konfiguration) | Dashboard verhält sich wie an einem anderen Tag; praktisch zum Durchspielen vergangener Spieltage |

