# Soccer Intelligence – Technisches Setup

**Stand:** 31.10.2026 · **Status:** Etappe A in Betrieb, Etappe B als Paket bereit, Passwortschutz beschlossen (noch nicht umgesetzt)
**Verantwortlich:** Carsten Thiele · **Mitwirkende:** ChatGPT (Server-Setup, Review), Claude (Daten, Architektur, Code)

---

## 0. Statusübersicht (Ist-Zustand vs. Planung)

| Bereich | Status | Bemerkung |
|---|---|---|
| Server, Container, Traefik-Routing | ✅ in Betrieb | geprüft am 25.10.2026 |
| Excel-Datei in `data/`, read-only im Container | ✅ in Betrieb | Lesen mit openpyxl im Container getestet |
| Neue Datenbank mit Spalte `Gameday` (58 Spalten) | ✅ in Betrieb | seit 31.10.2026 in `data/`, SHA-256 `6d68583c…`, siehe `02_Datenbasis.md` |
| `Spielplan.xlsx` (Spieltag 1, 2026/27) | ✅ auf dem Server | seit 31.10.2026 in `data/`, wird ab Etappe B gelesen |
| KPI-Regelwerk und Testfälle KPI 01–04 | ✅ fertig | `03_KPI_Regelwerk.md` v1.1, `docs/tests/` (bestätigt 28./29.10.2026, nachgerechnet 30.10.2026) |
| openpyxl / pandas im Container | ✅ installiert | Versionen in `requirements.txt` festgelegt |
| Website soccer-intelligence.com | ✅ erreichbar | zeigt **noch die Platzhalterseite** |
| Dashboard unter `/dashboard` mit Passwortschutz, Platzhalter bleibt unter `/` | 📦 beschlossen 30.10.2026 | **noch nicht umgesetzt**, benötigt separate Freigabe (siehe Abschnitt 7) |
| Datenladen, Prüfregeln, Seite „Datenqualität“ | ✅ in Betrieb | Etappe A, eingespielt am 31.10.2026 (26 Tests bestanden) |
| Automatisches Neuladen bei neuer Excel-Datei | ✅ in Betrieb | seit Etappe A |
| Versionen festgelegt | ✅ in Betrieb | streamlit 1.66.1, pandas 3.1.0, openpyxl 3.1.5 |
| Versionierung (Git + GitHub) | ✅ in Betrieb | seit 30.10.2026, privates Repository `Carsten1982/soccer-intelligence` |
| Spielplan einlesen, aktueller Spieltag, Tabs | 📦 Paket bereit | Etappe B, siehe Abschnitt 7 |
| KPIs, Top Anomalien, öffentliche Website | ⏳ offen | siehe Abschnitt 7 |

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
| 30.10.2026 | **Ein KPI-Regelwerk:** gültig ist nur `docs/03_KPI_Regelwerk.md`. `03_KPI_Grundregeln.md` und `docs/kpis/` sind gelöscht. Massgebliche Quelle bleibt das Word-Dokument „Definition der Dashboard-KPIs“. |
| 30.10.2026 | Im Text „Keine Anomalie“ (KPI 02 und 04) steht die Abweichung immer mit Vorzeichen, bei 0,0 % ohne. |
| 28.10.2026 | Ligareferenz über die Spalte `Gameday` (letzte 20 Spieltage). Spalte in der Datenbank ergänzt. |
| 25.10.2026 | Spielplan (anstehende Partien) kommt als **eigene Datei** `data/Spielplan.xlsx`, getrennt von den historischen Daten. Aufbau: `04_Spielplan.md` (Datum von / Datum bis, beschlossen 30.10.2026). |
| 25.10.2026 | Start mit abgeschlossenen Saisons 2020/21–2025/26. Die laufende Saison 2026/27 wird nach dem Prototyp ergänzt. |
| 25.10.2026 | Keine externe Fussball-API vorerst. |
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
| `football-dashboard` | Soccer Intelligence (Streamlit) | **ja** |
| `article-generator` | Artikeltext-Generator | nein – nicht anfassen |
| `n8n-wxit-n8n-1` | n8n Automatisierung | nein – nicht anfassen |
| `traefik-traefik-1` | Webserver / HTTPS für alle Anwendungen | nein – nicht anfassen |
| Chatbot | Ort unklar (kein eigener Container gefunden) | nein – offen |

### So kommt die Website ins Internet

```
Besucher → https://soccer-intelligence.com
        → Traefik (läuft im Host-Netzwerk, erledigt HTTPS/Zertifikat)
        → findet den Container football-dashboard automatisch über die Docker-Labels
        → Streamlit auf Port 8501
```

- Port 8501 ist nur lokal gebunden (`127.0.0.1`), also von aussen nicht direkt erreichbar.
- Traefik liest die Container-Adresse selbständig aus Docker. Ein Neubau des Containers bricht das Routing nicht.

### Geplant (beschlossen 30.10.2026, noch nicht umgesetzt)

```
Besucher → https://soccer-intelligence.com/            → Platzhalterseite (kleiner statischer Webserver, öffentlich)
Besucher → https://soccer-intelligence.com/dashboard…  → Passwortabfrage (Traefik) → Streamlit-Dashboard
```

- Streamlit läuft dann unter dem Pfad `/dashboard` (Einstellung `baseUrlPath`).
- Der Passwortschutz schützt alle Unterseiten und die Datenverbindung der App.
- Betroffen sind nur die Labels des eigenen Containers `football-dashboard` und ein neuer, kleiner Container für die Platzhalterseite. Die Traefik-Grundkonfiguration, n8n und alle anderen Anwendungen bleiben unverändert.
- Einschränkung: Es gibt keinen „Abmelden“-Knopf. Man meldet sich durch Schliessen des Browsers ab.

---

## 4. Projektordner `/docker/football-dashboard/`

```
/docker/football-dashboard/
├── Dockerfile                  Bauplan des Containers (Python 3.12, Streamlit)
├── docker-compose.yml          Container-Konfiguration inkl. Traefik-Labels
├── requirements.txt            Python-Pakete (Versionen fest)
├── requirements-dev.txt        zusätzlich pytest (nur für Tests)
├── app/                        Anwendung (Aufbau siehe Abschnitt 7)
├── tests/                      automatische Tests
├── config/                     leer (Konfiguration liegt in app/config/, siehe Abschnitt 7)
├── data/                       nicht in Git
│   ├── Database-Soccer-Intelligence.xlsx   ← GÜLTIGE Datenbank
│   └── Spielplan.xlsx                      ← GÜLTIGER Spielplan
├── backup/                     Sicherungen, nicht in Git
├── docs/, word/                Dokumentation
├── CLAUDE.md, CHANGELOG.md
└── .git/, .gitignore           Versionsverlauf (seit 30.10.2026)
```

### docker-compose.yml (Stand 25.10.2026)

```yaml
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
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.soccer.rule=Host(`soccer-intelligence.com`)"
      - "traefik.http.routers.soccer.entrypoints=websecure"
      - "traefik.http.routers.soccer.tls.certresolver=letsencrypt"
      - "traefik.http.services.soccer.loadbalancer.server.port=8501"
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
4. Traefik-Labels und Ports nicht ändern (nur mit eigener Freigabe).
5. Vor jeder Änderung: Backup der betroffenen Dateien.
6. Neu bauen nur den eigenen Service: `docker compose up -d --build football-dashboard`
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

Erwartet: Blätter `Bundesliga`, `Premier League`, `Seria A`, `LaLiga`, `Datenhinweise`; je 58 Spalten; Zeilenzahl gleich oder höher als vorher.

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
curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com   # erwartet: 200
```

### Zustand prüfen (nur lesend)

```bash
cd /docker/football-dashboard
cat docker-compose.yml requirements.txt
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
docker logs football-dashboard --tail 20
sha256sum data/Database-Soccer-Intelligence.xlsx
```

---

## 7. Geplante Architektur (freigegeben am 25.10.2026)

```
app/
├── app.py                Navigation
├── state.py              Laden mit Cache (neu laden bei geänderter Datei)
├── config/               Konfiguration, mit dem Code versioniert (Änderung -> Container neu bauen)
│   ├── ligen.toml        aktive Ligen, Adresse, Anzahl Teams (Etappe B)
│   └── teams.toml        Teamliste: bekannte Teams ohne Datenbankeinträge, z. B. Aufsteiger (Etappe B)
├── core/                 Kernlogik ohne Oberfläche (testbar)
│   ├── schema.py         erwartete Struktur der Excel-Datei
│   ├── loader.py         Einlesen + Strukturprüfung
│   ├── validation.py     Plausibilitätsprüfungen
│   ├── config.py         Einlesen der Konfiguration (Etappe B)
│   ├── fixtures.py       Spielplan einlesen und prüfen (Etappe B)
│   └── matchday.py       aktueller Spieltag, Spieltagsübersicht (Etappe B)
└── views/                Bereiche: Top Anomalien, je Liga, Datenqualität; components.py = Kopfbereich, Tabelle
tests/                    automatische Tests
data/Spielplan.xlsx       anstehende Partien
docs/                     Dokumentation (01–05, tests/)
CLAUDE.md                 Projektübersicht für Claude Code
CHANGELOG.md              Änderungsprotokoll
```

### Umsetzungsplan (Stand 31.10.2026, Etappen gemäss Dashboard-Briefing v4.2)

| Etappe | Inhalt | Voraussetzung | Status |
|---|---|---|---|
| Systemprüfung | Ist-Zustand des Servers geprüft | – | ✅ 25.10.2026 |
| Spezifikation | Dashboard-Briefing v4.2 (`05_Dashboard.md`), `03_KPI_Regelwerk.md` v1.1, `04_Spielplan.md`, Testfälle KPI 01–04 | – | ✅ fertig; offene KPI-Punkte nicht blockierend (Regelwerk, Abschnitt 8) |
| A – Fundament | Datenbank einlesen und prüfen, Versionen fest (Paket Schritt 1) | neue Datenbank (58 Spalten) auf dem Server ✅ | ✅ eingespielt 31.10.2026 (Git `ffec276`) |
| B – Spielplan und Datenqualität | Spielplan einlesen, aktueller Spieltag, Tabs, Bereich Datenqualität | Spielplan auf dem Server ✅ | 📦 Paket bereit (31.10.2026) |
| C – Liga-Tabellen mit KPIs | KPI 01–04 gemäss Regelwerk, JSON-Blöcke der Testfälle als automatische Tests | Gameday ✅, Testfälle ✅ | offen, startklar nach Etappe B |
| D – Top Anomalien | Auswahl-Logik gemäss Regelwerk, Abschnitt 2.6 | Etappe C | offen |
| E – Dashboard-Zugang | Umzug nach `/dashboard`, Passwortschutz über Traefik, Platzhalterseite unter `/` | separate Freigabe (Traefik-Labels) | beschlossen, offen |
| Öffentliche Website | eigener Architekturvorschlag (Mobile First) | – | später |

---

## 8. Offene Punkte

- [ ] Wo läuft der Chatbot? (nur zur Dokumentation)
- [x] ~~Alte Excel-Kopie im Hauptverzeichnis nach `backup/` verschieben~~ erledigt 31.10.2026
- [ ] Warnung zu Spiel-ID 11344 (Schusssumme): Wert korrigieren oder als Hinweis herabstufen?
- [ ] Server-Updates (57 ausstehend): getrennt und bewusst einplanen, betrifft alle Anwendungen. Kein Upgrade auf Ubuntu 26.04 vorerst.
- [x] ~~Git-Repository im Projektordner~~ eingerichtet 30.10.2026 (GitHub, privat)
- [x] ~~Neue Datenbank und `Spielplan.xlsx` auf den Server laden~~ erledigt 31.10.2026
- [ ] Ergänzte Spielplan-Regeln aus Etappe B bestätigen (`04_Spielplan.md`, Abschnitte 4 und 5, markiert mit „ergänzt 31.10.2026“)
- [ ] Aufräumen in `backup/` nach einigen Wochen stabilen Betriebs
- [ ] Offene KPI-Punkte 2, 6, 7, 9, 10 im Regelwerk, Abschnitt 8 (nicht blockierend)
- [x] ~~Spalte „Gameday“ für die Ligareferenz~~ ergänzt (28.10.2026), geprüft (30.10.2026)
- [x] ~~Doppelte KPI-Datei~~ entschieden am 30.10.2026: gültig ist `03_KPI_Regelwerk.md`, `03_KPI_Grundregeln.md` und `kpis/` gelöscht

---

## 9. Ideen für später (erst nach stabiler erster Version)

| Idee | Notiz |
|---|---|
| Spieltage im Dashboard vor- und zurückblättern | eigene kleine Spezifikation (Bedienung, Adressen, Verhalten der Top Anomalien) |
| Internes Test-Datum (`testdatum` in der Konfiguration) | Dashboard verhält sich wie an einem anderen Tag; praktisch zum Durchspielen vergangener Spieltage |
