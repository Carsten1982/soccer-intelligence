# Soccer Intelligence – Technisches Setup

**Stand:** 08.11.2026 · **Status:** Etappen A–F und H in Betrieb (Version 0.9, vier Ligen, KPI 01–09; Etappe H eingespielt 08.11.2026, Git `51e595b`). H.1 (Aufräumen und Tempo, Version 0.9.1) eingespielt 08.11.2026, Git `b5a7ea8`. H.2 (Stabilität, Version 0.9.2) eingespielt 08.11.2026, Git `291eeac`. Etappe I.1 (Simulation, Version 0.10) als Paket bereit. Datenlieferung (Etappe G) in Klärung.
**Verantwortlich:** Carsten Thiele · **Mitwirkende:** ChatGPT (Server-Setup, Review), Claude (Daten, Architektur, Code)

---

## 0. Statusübersicht (Ist-Zustand vs. Planung)

| Bereich | Status | Bemerkung |
|---|---|---|
| Server, Container, Traefik-Routing | ✅ in Betrieb | geprüft am 25.10.2026 |
| Excel-Datei in `data/`, read-only im Container | ✅ in Betrieb | Lesen mit openpyxl im Container getestet |
| Neue Datenbank mit Spalte `Gameday` (58 Spalten) | ✅ in Betrieb | seit 31.10.2026 in `data/`, SHA-256 `6d68583c…`, siehe `02_Datenbasis.md` |
| `Spielplan.xlsx` (Spieltag 1, 2026/27) | ✅ in Betrieb | seit 31.10.2026 in `data/`, gelesen seit Etappe B |
| KPI-Regelwerk und Testfälle KPI 01–04 | ✅ fertig | `03_KPI_Regelwerk.md` v1.1, `docs/tests/` (bestätigt 28./29.10.2026, nachgerechnet 30.10.2026) |
| openpyxl / pandas im Container | ✅ installiert | Versionen in `requirements.txt` festgelegt |
| Website soccer-intelligence.com | ✅ erreichbar | ab Etappe E: `/` öffentliche Platzhalterseite, `/dashboard` mit Passwort |
| Dashboard unter `/dashboard` mit Passwortschutz, Platzhalter unter `/` | ✅ in Betrieb | Etappe E, eingespielt 31.10.2026 (Git `64a684b`), freigegeben von Carsten am 31.10.2026 (Traefik-Labels des eigenen Containers, neuer Container `soccer-placeholder`) |
| Datenladen, Prüfregeln, Seite „Datenqualität“ | ✅ in Betrieb | Etappe A, eingespielt am 31.10.2026 (26 Tests bestanden) |
| Automatisches Neuladen bei neuer Excel-Datei | ✅ in Betrieb | seit Etappe A |
| Versionen festgelegt | ✅ in Betrieb | streamlit 1.66.1, pandas 3.1.0, openpyxl 3.1.5 |
| Versionierung (Git + GitHub) | ✅ in Betrieb | seit 30.10.2026, privates Repository `Carsten1982/soccer-intelligence` |
| Spielplan einlesen, aktueller Spieltag, Tabs | ✅ in Betrieb | Etappe B, eingespielt 31.10.2026 (Git `ff4fbe8`) |
| KPI 01–04 in den Liga-Tabellen, Häufigkeit der Anomalien | ✅ in Betrieb | Etappe C, eingespielt 31.10.2026 (Git `8cb5f0f`) |
| Spieltag-Pfeile, Navigation dunkelgrau, kleinerer Abstand | ✅ in Betrieb | Anpassungen nach Abnahme Etappe C, eingespielt 31.10.2026 (Git `4c3be5c`) |
| Top Anomalien (Startseite) | ✅ in Betrieb | Etappe D, eingespielt 31.10.2026 (Git `1a1c527`, 145 Tests bestanden) |
| KPIs, Top Anomalien | ✅ in Betrieb | Etappen C und D |
| Phase 1 (Etappen A–E) | ✅ abgeschlossen 31.10.2026 | Browser-Anmeldung unter `/dashboard` noch von Carsten zu bestätigen |
| Daten Serie A und LaLiga | ✅ aufbereitet 04.–07.11.2026 | Datum und Spieltag ergänzt, bereinigt (`02_Datenbasis.md`, Abschnitt 4c); Datenbank und Spielplan mit vier Blättern auf dem Server |
| Erweiterung auf vier Ligen (Etappe F) | ✅ in Betrieb | eingespielt 07.11.2026 (Git `cc00dd9`, 171 Tests bestanden), Version 0.8; Gegenrechnung aller 8'808 Begegnungen ohne Abweichung (`docs/tests/pruefprotokoll_etappe_f.md`) |
| Regelmässige Datenlieferung (Etappe G) | 🔎 in Klärung | Footiqo: fester Download-Link, kumulative Excel-Datei, Di/Do; Konzept: `06_Datenlieferung.md` |
| Neue KPIs 05–09 (Frontend) und 10–13 (Simulation) | ✅ KPI 05–09 in Betrieb (Etappe H, eingespielt 08.11.2026, Git `51e595b`, 260 Tests bestanden; Vollvergleich 8'808 Begegnungen ohne Abweichung) | Regelwerk v2.1 Abschnitte 9–10; Testfälle `docs/tests/test_kpi05…09…` (61 Ergebnisse, Excel-Nachprüfung identisch); zwei Nachkommastellen für alle KPIs; KPI 10–13 weiter Entwurf (Etappe I) |
| Code-Prüfung und H.1 (Aufräumen und Tempo) | ✅ in Betrieb (Version 0.9.1, Git `b5a7ea8`, 287 Tests bestanden) | Prüfung durch einen zweiten Claude (08.11.2026): keine Rechenfehler; 3 mögliche Abstürze, Tempo, Aufräumen. H.1 behebt die Funde ohne Änderung an den Ergebnissen (`docs/tests/pruefprotokoll_h1.md`) |
| Öffentliche Website | ⏳ später | nach Etappe F und Klärung der Datenquelle |

---

## 1. Projektziel

Fussball-Analyseplattform auf Basis historischer Spieldaten (Bundesliga, Premier League).
Auffälligkeiten („Anomalien“) anstehender Partien werden erkannt und angezeigt.
Übungsprojekt, nicht kommerziell.

Ausbaustufen:

1. Excel-Datenbank, von Carsten gepflegt
2. Dashboard mit allen anstehenden Partien und Analysen
3. Öffentliche Website (Mobile First) mit Spieltag und den wichtigsten Anomalien auf der Startseite

---

## 2. Getroffene Entscheidungen

| Datum | Entscheidung |
|---|---|
| 30.10.2026 | **Dashboard mit Passwortschutz** unter `https://soccer-intelligence.com/dashboard`. Schutz serverseitig über Traefik für alle Adressen unter `/dashboard`. Zugangsdaten nur als Hash in einer Konfigurationsdatei auf dem Server. Ersetzt die Entscheidung vom 25.10.2026. |
| 30.10.2026 | Startseite `https://soccer-intelligence.com` zeigt bis zur öffentlichen Website weiterhin die **Platzhalterseite** (öffentlich). |
| 30.10.2026 | Bereiche des Dashboards: `/dashboard` = Top Anomalien, `/dashboard/bundesliga`, `/dashboard/premier-league`. Jede weitere aktivierte Liga erhält automatisch einen eigenen Bereich nach demselben Muster (z. B. `/dashboard/laliga`). |
| 30.10.2026 | Das Dashboard bleibt ein reines Ansichts-Werkzeug: keine Funktionen zum Importieren, Bearbeiten oder Verwalten in der App. |
| 30.10.2026 | **Keine Vereinslogos**, weder im Dashboard noch auf der öffentlichen Website (rechtliche Gründe). |
| ~~25.10.2026~~ | ~~Dashboard in Phase 1 öffentlich, ohne Login~~ → **ersetzt am 30.10.2026** (siehe oben). |
| 25.10.2026 | Daten werden **nur über die Datei auf dem Server** geändert, nie über die App. |
| 25.10.2026 | **Einzige gültige Datenquelle:** `data/Database-Soccer-Intelligence.xlsx` |
| 31.10.2026 | **Die md-Dateien in `docs/` sind die einzige massgebliche Quelle.** Die Word-Dokumente (`word/`) sind Archiv und werden nicht mehr gepflegt. Änderungen nur noch in den md-Dateien, mit Eintrag im CHANGELOG. |
| 08.11.2026 | **Neue KPIs:** 5 Frontend-KPIs (05 Ecken, 06 Tore 1. HZ, 07 Tore 2. HZ, 08 Beide Teams treffen, 09 Schüsse aufs Tor) und 4 Simulations-KPIs nur im Backend (10/11 Angriff gegen Abwehr HZ 1/2, 12 Offensivdruck, 13 Abschluss-Effizienz). Schwellen pro Liga und KPI einstellbar (Datei `app/config/schwellen.toml`, Standard ±20/±35 %, kein eigener Tab). Kompakte Liga-Tabelle mit Details per Aufklappen. Reihenfolge: Spezifikation + Testfälle → Etappe H (KPI 05–09) → Etappe I (Simulations-Tab). Details: KPI-Regelwerk v2.0, CHANGELOG. |
| 08.11.2026 | **Etappe H freigegeben (Carsten):** Testfälle KPI 05–09 bestätigt; **alle KPIs mit zwei Nachkommastellen** (auch Abweichung, Einstufung nach gerundetem Wert); **Top Anomalien über KPI 02–09** (bisherige Rangfolge, Gewichtung später); kompaktere Liga-Tabelle mit Aufklappen, Design-Vorschlag vor der Umsetzung. Danach Etappe I: interner Tab zur Schwellen-Analyse je KPI und Liga, Feintuning, Gewichtung der Top Anomalien. Ablauf: md-Dateien → Backup → Design-Vorschlag → Programmieren und Einspielen. |
| 07.11.2026 | **Spieltage mit verlegten Spielen:** Die bestehende Logik für den aktuellen Spieltag bleibt. Spiele, die mehr als 3 Tage ausserhalb des Hauptzeitraums ihres Spieltags liegen, werden im Spielplan als `verschoben` gepflegt (keine KPIs, keine Top Anomalie). Keine Pflege auf Tagesebene, keine Mehrheitsregel. Grundlage: Auswertung 2022/23–2025/26, betroffen unter 2 % der Spiele (`04_Spielplan.md`, Abschnitt 6). |
| 07.11.2026 | Blatt für Italien heisst in Datenbank und Spielplan **`Serie A`** (bisher `Seria A`); der Code wird in Etappe F angepasst. Blattnamen ohne Leerzeichen: `LaLiga`. |
| 06.11.2026 | **Erweiterung auf vier Ligen** (Serie A, LaLiga) als nächster Schritt (Etappe F), vor der Datenlieferung (Etappe G). Reihenfolge: Daten auf den Server → Sicherung in GitHub → Etappe F → Etappe G → neue KPIs → öffentliche Website. |
| 02.11.2026 | **Reihenfolge nach Phase 1:** zuerst die Datenquelle klären, die neuen KPIs können parallel laufen, danach die öffentliche Website. Grund: Teamnamen, IDs, Nutzungsrechte und Spielplan-Pflege beeinflussen die Website. *(Präzisiert am 06.11.2026, siehe oben.)* |
| 31.10.2026 | **Etappe E:** öffentliche Platzhalterseite unter `/` (Variante b), ein gemeinsamer Zugang zum Dashboard (Benutzername und Passwort nur in `.env`), Hinweis `noindex` für Suchmaschinen. |
| 31.10.2026 | Spieltag-Pfeile in den Liga-Bereichen (je Liga, nicht in die Zukunft, Auswahl in der Adresse); Top Anomalien immer aktueller Spieltag. |
| 30.10.2026 | **Ein KPI-Regelwerk:** gültig ist nur `docs/03_KPI_Regelwerk.md`. `03_KPI_Grundregeln.md` und `docs/kpis/` sind gelöscht. ~~Massgebliche Quelle bleibt das Word-Dokument „Definition der Dashboard-KPIs“.~~ (ersetzt am 31.10.2026, siehe oben) |
| 30.10.2026 | Im Text „Keine Anomalie“ (KPI 02 und 04) steht die Abweichung immer mit Vorzeichen, bei 0,0 % ohne. |
| 28.10.2026 | Ligareferenz über die Spalte `Gameday` (letzte 20 Spieltage). Spalte in der Datenbank ergänzt. |
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

### Container auf dem Server (Stand 25.10.2026)

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

### Zugang (beschlossen 30.10.2026, umgesetzt in Etappe E am 31.10.2026)

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
├── Dockerfile                  Bauplan des Containers (Python 3.12, Streamlit)
├── docker-compose.yml          Container-Konfiguration inkl. Traefik-Labels (Dashboard + Platzhalter)
├── .env                        Zugang zum Dashboard (Benutzername + Passwort-Hash), nicht in Git
├── placeholder/                Platzhalterseite unter / (index.html, robots.txt), seit Etappe E
├── tools/                      Hilfsskripte (dashboard_passwort.sh: Zugang setzen/ändern)
├── requirements.txt            Python-Pakete (Versionen fest)
├── requirements-dev.txt        zusätzlich pytest (nur für Tests)
├── app/                        Anwendung (Aufbau siehe Abschnitt 7)
├── tests/                      automatische Tests
├── config/                     leer (Konfiguration liegt in app/config/, siehe Abschnitt 7)
├── data/                       nicht in Git
│   ├── Database-Soccer-Intelligence.xlsx   ← GÜLTIGE Datenbank
│   └── Spielplan.xlsx                      ← GÜLTIGER Spielplan
├── backup/                     Sicherungen, nicht in Git
├── docs/                       Dokumentation, massgebliche Quelle (md)
├── word/                       Archiv der Word-Dokumente (Stand 30.10.2026, nicht mehr gepflegt)
├── CLAUDE.md, CHANGELOG.md
└── .git/, .gitignore           Versionsverlauf (seit 30.10.2026)
```

### docker-compose.yml (Stand 31.10.2026, Etappe E)

```yaml
# Soccer Intelligence – Container-Konfiguration (Stand 31.10.2026, Etappe E)
#
#   https://soccer-intelligence.com/             -> Platzhalterseite, öffentlich (Container soccer-placeholder)
#   https://soccer-intelligence.com/dashboard…   -> Passwortabfrage (Traefik BasicAuth) -> Streamlit-Dashboard
#
# Zugangsdaten: NUR als Hash in .env auf dem Server (Variable SOCCER_DASHBOARD_AUTH), nie in Git.
# Fehlt die Variable, bricht "docker compose" mit einer Fehlermeldung ab (statt ohne Passwortschutz zu starten).
# Betroffen sind nur die Labels dieser beiden Container. Die Traefik-Grundkonfiguration bleibt unverändert.

services:
  football-dashboard:
    build:
      context: /docker/football-dashboard
    container_name: football-dashboard
    restart: unless-stopped
    ports:
      - "127.0.0.1:8501:8501"
    volumes:
      - ./data:/data:ro
    environment:
      # Streamlit läuft unter dem Pfad /dashboard (Seiten: /dashboard/bundesliga usw.)
      - STREAMLIT_SERVER_BASE_URL_PATH=dashboard
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.soccer.rule=Host(`soccer-intelligence.com`) && PathPrefix(`/dashboard`)"
      - "traefik.http.routers.soccer.entrypoints=websecure"
      - "traefik.http.routers.soccer.tls.certresolver=letsencrypt"
      - "traefik.http.routers.soccer.middlewares=soccerintel-auth,soccerintel-noindex"
      - "traefik.http.middlewares.soccerintel-auth.basicauth.users=${SOCCER_DASHBOARD_AUTH:?SOCCER_DASHBOARD_AUTH fehlt in .env}"
      - "traefik.http.middlewares.soccerintel-noindex.headers.customresponseheaders.X-Robots-Tag=noindex, nofollow"
      - "traefik.http.services.soccer.loadbalancer.server.port=8501"

  soccer-placeholder:
    image: nginx:1.27-alpine
    container_name: soccer-placeholder
    restart: unless-stopped
    volumes:
      - ./placeholder:/usr/share/nginx/html:ro
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.soccer-placeholder.rule=Host(`soccer-intelligence.com`)"
      - "traefik.http.routers.soccer-placeholder.entrypoints=websecure"
      - "traefik.http.routers.soccer-placeholder.tls.certresolver=letsencrypt"
      - "traefik.http.services.soccer-placeholder.loadbalancer.server.port=80"
```

- `./data:/data:ro` → Der Ordner `data/` ist im Container unter `/data` **nur lesbar**. Die App kann die Excel-Datei technisch nicht verändern.

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

## 6. Standardabläufe

### Neue Excel-Datei aufspielen

Grundsatz: Die neue Datei wird **erst geprüft und dann** zur gültigen Datenquelle. Die App liest nur `Database-Soccer-Intelligence.xlsx`. Eine Datei mit anderem Namen in `data/` wird ignoriert.

**1. Hochladen unter Zwischennamen** (per SFTP/scp) als `data/upload.xlsx`

**2. Neue Datei prüfen, bevor sie aktiv wird**

*Bis Schritt 1 eingespielt ist* (Grundprüfung: lesbar, Blätter, Spaltenanzahl, Zeilen):

```bash
docker exec football-dashboard python -c "
import openpyxl
wb = openpyxl.load_workbook('/data/upload.xlsx', read_only=True)
print('Blätter:', wb.sheetnames)
for n in ('Bundesliga', 'Premier League'):
    ws = wb[n]; print(n, '- Spalten:', ws.max_column, '- Zeilen:', ws.max_row - 1)
"
```

Erwartet: Blätter `Bundesliga`, `Premier League`, `Serie A`, `LaLiga`, `Datenhinweise` (bis 06.11.2026 hiess das Blatt `Seria A`); je 58 Spalten; Zeilenzahl gleich oder höher als vorher.

*Ab Schritt 1* (vollständige Prüfung mit allen Prüfregeln aus 02_Datenbasis.md):

```bash
docker exec football-dashboard python -c "
from core.loader import load_database
db = load_database('/data/upload.xlsx')
print('Fehler:', db.count('Fehler'), '| Warnungen:', db.count('Warnung'), '| Hinweise:', db.count('Hinweis'))
for i in db.issues:
    if i.level != 'Hinweis': print(i.level, i.sheet, i.check, i.match_id, i.message)
"
```

Erwartet: `Fehler: 0`. Neue Warnungen vor dem Austausch klären.
**Bei Fehlern: STOPP.** Datei nicht aktivieren, `data/upload.xlsx` korrigieren und erneut hochladen.

**3. Sichern und austauschen**

```bash
cd /docker/football-dashboard
cp -p data/Database-Soccer-Intelligence.xlsx backup/Database-Soccer-Intelligence_$(date +%F_%H%M).xlsx
mv data/upload.xlsx data/Database-Soccer-Intelligence.xlsx
sha256sum data/Database-Soccer-Intelligence.xlsx
```

Das `mv` innerhalb desselben Ordners ist sofort komplett, die App liest nie eine halb geschriebene Datei.

**4. Kontrolle:** Website aufrufen. *Ab Schritt 1 geplant:* Die App lädt die neue Datei beim nächsten Seitenaufruf automatisch. Das gilt erst, wenn Schritt 1 eingespielt und dieses Verhalten getestet ist. Bis dahin liest die App die Datei noch gar nicht.

**5. Rückweg, falls nach dem Austausch etwas nicht stimmt**

```bash
cd /docker/football-dashboard
ls -t backup/Database-Soccer-Intelligence_*.xlsx | head -3      # letzte Sicherungen anzeigen
cp -p backup/Database-Soccer-Intelligence_<DATUM_ZEIT>.xlsx data/restore.xlsx
mv data/restore.xlsx data/Database-Soccer-Intelligence.xlsx
```

Danach Website prüfen und den Vorfall im CHANGELOG eintragen.

### Code-Änderung einspielen

```bash
cd /docker/football-dashboard
# 1. Backup der betroffenen Dateien nach backup/<datum>_<name>/
# 2. Dateien ersetzen
docker compose config -q                              # Konfiguration prüfen
docker compose up -d --build football-dashboard       # nur unseren Container neu bauen
docker ps --format "table {{.Names}}\t{{.Status}}"    # alle Container laufen?
docker logs football-dashboard --tail 30              # Fehler im Log?
curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/            # Platzhalter, erwartet: 200
curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/dashboard/   # ohne Passwort, erwartet: 401
```

**Tests vor dem Neubau** (Wegwerf-Container, Projekt nur lesend eingebunden; bewährt seit Etappe H). Wichtig: `tests` am Ende (sonst sammelt pytest auch `backup/`) und `SI_DATA_DIR=/src/data` (sonst finden die Seitentests die Excel-Dateien nicht):

```bash
cd /docker/football-dashboard && docker run --rm -v "$PWD":/src:ro -e SI_DATA_DIR=/src/data -e PYTHONDONTWRITEBYTECODE=1 -w /src python:3.12-slim sh -c "pip install -q --root-user-action=ignore -r requirements-dev.txt && python -m pytest -q -p no:cacheprovider tests" 2>&1 | tail -15
```

### Dashboard-Zugang setzen oder Passwort ändern

```bash
cd /docker/football-dashboard
bash tools/dashboard_passwort.sh                 # fragt Benutzername und Passwort (verdeckt, zweimal)
docker compose up -d football-dashboard          # Zugang neu einlesen (kein Neubau nötig)
```

- Gespeichert wird nur der bcrypt-Hash in `.env` (Zeile `SOCCER_DASHBOARD_AUTH`). Das Passwort erscheint weder auf dem Bildschirm noch im Befehlsverlauf.
- Die alte `.env` wird vorher nach `backup/env_<Datum>` gesichert. Andere Zeilen in `.env` bleiben unverändert.
- Bei verschiedenen Eingaben oder einem Fehler bricht das Skript ab und ändert nichts.

### Zustand prüfen (nur lesend)

```bash
cd /docker/football-dashboard
cat docker-compose.yml requirements.txt
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
docker logs football-dashboard --tail 20
sha256sum data/Database-Soccer-Intelligence.xlsx
```

---

## 7. Architektur (freigegeben am 25.10.2026, Stand H.1)

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

### Umsetzungsplan (Stand 02.11.2026, Etappen gemäss Dashboard-Briefing v4.2)

| Etappe | Inhalt | Voraussetzung | Status |
|---|---|---|---|
| Systemprüfung | Ist-Zustand des Servers geprüft | – | ✅ 25.10.2026 |
| Spezifikation | Dashboard-Briefing v4.2 (`05_Dashboard.md`), `03_KPI_Regelwerk.md` v1.1, `04_Spielplan.md`, Testfälle KPI 01–04 | – | ✅ fertig; offene KPI-Punkte nicht blockierend (Regelwerk, Abschnitt 8) |
| A – Fundament | Datenbank einlesen und prüfen, Versionen fest (Paket Schritt 1) | neue Datenbank (58 Spalten) auf dem Server ✅ | ✅ eingespielt 31.10.2026 (Git `ffec276`) |
| B – Spielplan und Datenqualität | Spielplan einlesen, aktueller Spieltag, Tabs, Bereich Datenqualität | Spielplan auf dem Server ✅ | ✅ eingespielt 31.10.2026 (Git `ff4fbe8`) |
| C – Liga-Tabellen mit KPIs | KPI 01–04 gemäss Regelwerk, JSON-Blöcke der Testfälle als automatische Tests, Häufigkeit der Anomalien | Gameday ✅, Testfälle ✅ | ✅ eingespielt 31.10.2026 (Git `8cb5f0f`) |
| D – Top Anomalien | Auswahl-Logik gemäss Regelwerk, Abschnitt 2.6, Karten auf der Startseite, 13 Tests | Etappe C ✅ | ✅ eingespielt 31.10.2026 (Git `1a1c527`) |
| E – Dashboard-Zugang | Umzug nach `/dashboard`, Passwortschutz über Traefik, `noindex`, Platzhalterseite unter `/` | Freigabe Carsten 31.10.2026 ✅ | ✅ eingespielt 31.10.2026 (Git `64a684b`) |
| **Phase 1 abgeschlossen** | Etappen A–E in Betrieb | – | ✅ 31.10.2026 |
| F – Vier Ligen | Serie A (`/dashboard/serie-a`) und LaLiga (`/dashboard/laliga`): Konfiguration, Blattname `Serie A` im Code, Aufsteiger in der Teamliste, kompakter Kopfbereich, Top Anomalien und Datenqualität über vier Ligen, Tests, Doku | Daten auf dem Server ✅, LaLiga 17.05.2026 korrigiert ✅, Freigabe 07.11.2026 ✅ | ✅ eingespielt 07.11.2026 (Git `cc00dd9`) |
| G – Datenlieferung | regelmässiger Import mit Prüfschranke (Footiqo, Download-Link), Konzept `06_Datenlieferung.md` | Antworten von Footiqo, Testkauf, Freigabe | 🔎 in Klärung |
| H – KPI 05–09 | Frontend-KPIs 05–09 gemäss Regelwerk 9, zwei Nachkommastellen für alle KPIs, Schwellen-Konfiguration (`schwellen.toml`), kompakte Tabelle mit Aufklappen, Top Anomalien über KPI 02–09, Anzeige der Schwellen in Datenqualität, Tests aus den Testfällen + Gegenrechnung | Testfälle bestätigt ✅, Design abgenommen ✅, Backup ✅ (08.11.2026) | ✅ eingespielt 08.11.2026 (Git `51e595b`, 260 Tests bestanden) |
| H.1 – Aufräumen und Tempo | Funde der Code-Prüfung: 3 mögliche Abstürze behoben, KPI-Berechnung etwa 4× schneller (Häufigkeit 30 → 6 s), Zwischenspeicher für die KPIs eines Spieltags, Kommazahlen nie abschneiden, alte Tabelle entfernt; Ergebnisse unverändert | Etappe H ✅, Freigabe Carsten 08.11.2026 ✅ | ✅ eingespielt 08.11.2026 (Git `b5a7ea8`, 287 Tests bestanden) |
| I.1 – Simulation | Bereich „Simulation – Spielwiese“ (intern): Häufigkeit und Ergebnisqualität je KPI mit eigenen Schwellen, Mehrwert gegenüber Spielen ohne Anomalie (Regelwerk 11, Briefing 6.4) | Freigabe und Design Variante B 08.11.2026 ✅ | 📦 Paket bereit (Version 0.10, `ANLEITUNG_ETAPPE_I1.md`) |
| I – weitere Schritte | Feintuning der Schwellen je KPI und Liga, Gewichtung der Top Anomalien (Punkt 17), KPI 10–13 | Etappe I.1 | ⏳ geplant |
| Öffentliche Website | eigener Architekturvorschlag (Mobile First), eigener Ordner und eigenes Repository empfohlen | Etappe F, Datenquelle geklärt (G) | später |

---

## 8. Offene Punkte

- [ ] Wo läuft der Chatbot? (nur zur Dokumentation)
- [x] ~~Alte Excel-Kopie im Hauptverzeichnis nach `backup/` verschieben~~ erledigt 31.10.2026
- [ ] Warnung zu Spiel-ID 11344 (Schusssumme): Wert korrigieren oder als Hinweis herabstufen?
- [x] ~~Server-Updates (57 ausstehend)~~ erledigt 31.10.2026 (Ubuntu-Pakete und Docker aktualisiert, Neustart, alle vier Anwendungen laufen). Weiterhin kein Upgrade auf Ubuntu 26.04 vorerst.
- [x] ~~Git-Repository im Projektordner~~ eingerichtet 30.10.2026 (GitHub, privat)
- [x] ~~Neue Datenbank und `Spielplan.xlsx` auf den Server laden~~ erledigt 31.10.2026
- [x] ~~Ergänzte Spielplan-Regeln aus Etappe B bestätigen~~ bestätigt von Carsten am 31.10.2026
- [ ] Server meldet „1 updates could not be installed automatically“ (unattended-upgrades, 31.10.2026): Log prüfen, betrifft nicht das Dashboard
- [ ] Öffentliche Platzhalterseite: Braucht es ein Impressum bzw. einen Datenschutzhinweis? (vor dem Start der öffentlichen Website klären)
- [ ] Anmeldung im Browser unter `/dashboard` bestätigen (Server-Prüfung ok: `/` 200, `/dashboard/` 401)
- [ ] Name des bisherigen Datenanbieters ermitteln und dokumentieren (`02_Datenbasis.md`, Regelwerk Abschnitt 8, Punkt 7)
- [ ] Offene Fragen an Footiqo, u. a. Spielplan und Spalte `Gameday` (`06_Datenlieferung.md`, Abschnitt 3); Carsten klärt ab
- [ ] LaLiga 17.05.2026: 7 Spiele mit unstimmigen Ergebnissen korrigieren (vor dem Einschalten von LaLiga)
- [ ] Blatt *Datenhinweise*: bei id 9198 `Liga` von `Seria A` auf `Serie A` ändern
- [ ] Spielplan LaLiga 2026/27, Spieltag 1: Hauptzeitraum 15.–19.08., die 4 späten Spiele mit Status `verschoben` (Pflegeregel `04_Spielplan.md`)
- [ ] Optional: Arbeitsweise umstellen auf Cowork-Projekt bzw. Claude Code mit lokaler Kopie des GitHub-Projekts (weniger Zip/WinSCP)
- [ ] Aufräumen in `backup/` nach einigen Wochen stabilen Betriebs
- [ ] Offene KPI-Punkte 2, 6, 7, 9, 10 im Regelwerk, Abschnitt 8 (nicht blockierend)
- [x] ~~Spalte „Gameday“ für die Ligareferenz~~ ergänzt (28.10.2026), geprüft (30.10.2026)
- [x] ~~Doppelte KPI-Datei~~ entschieden am 30.10.2026: gültig ist `03_KPI_Regelwerk.md`, `03_KPI_Grundregeln.md` und `kpis/` gelöscht

---

## 9. Ideen für später (erst nach stabiler erster Version)

| Idee | Notiz |
|---|---|
| ~~Spieltage im Dashboard vor- und zurückblättern~~ | umgesetzt am 31.10.2026 (Briefing 3.2) |
| Mehrheitsregel für den aktuellen Spieltag (07.11.2026 zurückgestellt) | Aktuell = Spieltag mit den meisten Spielen der nächsten 7 Tage; offene Spiele früherer Spieltage in einem Bereich „Nachholspiele“ mit KPIs. Nur nötig, falls verzerrte Spieltage deutlich häufiger werden als heute. |
| Internes Test-Datum (`testdatum` in der Konfiguration) | Dashboard verhält sich wie an einem anderen Tag; praktisch zum Durchspielen vergangener Spieltage |
