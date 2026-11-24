# Soccer Intelligence – Einstieg für Claude

**Spezifikation v1.9** · Stand 09.11.2026

## Worum es geht
Soccer Intelligence ist eine Fussball-Analyseplattform. Sie berechnet statistische Auffälligkeiten (Anomalien) anstehender
Ligaspiele und stellt sie verständlich dar. Datenbasis ist eine Excel-Datei mit historischen Spielen von Bundesliga,
Premier League, Serie A und LaLiga (Saisons 2020/21–2025/26, dazu spieltagweise die laufende Saison 2026/27).
Lernprojekt, nicht kommerziell: Code soll nachvollziehbar, gut kommentiert und schrittweise aufgebaut sein. Nach jedem
Schritt kurz erklären, was gemacht wurde.

**Aktueller Stand, Versionen, nächste Schritte:** `docs/01_Technisches_Setup.md`, Abschnitt 0 (die einzige Stelle dafür).

## Technischer Rahmen
- Streamlit-App im Docker-Container `football-dashboard` auf einem Hostinger-VPS, Projektordner `/docker/football-dashboard/`.
- Python 3.12, streamlit 1.66.1, pandas 3.1.0, openpyxl 3.1.5.
- Excel-Dateien in `data/`, im Container nur lesbar (`/data`, read-only).
- `https://soccer-intelligence.com/` = öffentliche Platzhalterseite; `/dashboard` = Dashboard mit Anmeldemaske (seit
  0.15.2; Benutzername und Passwort-Hash nur in `.env`). Bereiche: Top Anomalien, je aktive Liga ein Bereich, Datenqualität, Sensitivitätsanalyse
  (intern), Datenimport/API (intern). Seit Version 0.14 holt der Container `soccer-import` die Daten von API-Football
  (Schlüssel nur in `.env`); nur er schreibt nach Freigabe in `data/`.
- Öffentliche Website (seit 0.17, `docs/08_Website.md`): bis zum Livegang nur als Vorschau unter `/vorschau` mit
  Passwortabfrage (Container `soccer-vorschau`, Hash nur in `.env` als `SOCCER_VORSCHAU_AUTH`); Zeitreise `?datum=…`.

## Quellen (verbindlich)
| Datei | Inhalt |
|---|---|
| docs/01_Technisches_Setup.md | Stand und Versionen, Entscheidungen, Server, Schutzregeln, Abläufe (Release einspielen, Excel aufspielen), Architektur, offene Punkte |
| docs/02_Datenbasis.md | Aufbau der Excel-Datei (58 Spalten inkl. `Gameday`), Formate, Prüfregeln, Datenstände |
| docs/03_KPI_Regelwerk.md | Berechnungsregeln KPI 01–13, Anomalie-Logik, Top Anomalien, Texte, Ergebniskontrolle (Abschnitt 11) |
| docs/04_Spielplan.md | Aufbau des Spielplans (`Datum von` / `Datum bis`), aktueller Spieltag, Prüfregeln |
| docs/05_Dashboard.md | Dashboard-Briefing: Aufbau, Navigation, Darstellung, Abnahmekriterien |
| docs/06_Datenlieferung.md | Datenlieferung über API-Football: Feldzuordnung, Tagesbetrieb, Regeln des Ergebnis-Imports (10.1), Entscheidungen |
| docs/07_Spielplan_Anzeige.md | Spielplan aus der API (Status, Termin, Nachholspiele, Zuordnung) und Anzeige kommender Spieltage (Spezifikation v2.1) |
| docs/08_Website.md | Öffentliche Website: Entscheidungen, Technik, Seiten, Zeitreise, Annahmen, Testfälle |
| docs/09_Betrieb_EMail.md | E-Mail, Alarme, Statusmail, Server-Überwachung, Laufzeiten, Versand des Kontaktformulars (ab 0.23) |
| docs/tests/test_kpi*.md | Bestätigte Testfälle mit erwarteten Ergebnissen (JSON) – Referenz für die Korrektheit |
| docs/tests/pruefprotokoll_*.md | Prüfprotokolle grösserer Etappen (Gegenrechnung, Vollvergleich) |
| CHANGELOG.md | Änderungsprotokoll: jede Änderung mit Datum und wer |
| RELEASE.md | Die aktuelle Änderung: Inhalt, Erwartungswerte, was im Browser zu prüfen ist (Ablauf in `01`, Abschnitt 6.1) |

Bei Widersprüchen gilt für Berechnungen das KPI-Regelwerk, für Darstellung und Navigation das Dashboard-Briefing.
Die md-Dateien in `docs/` sind die einzige massgebliche Quelle; `word/` ist nur Archiv. Die Testfälle gelten für die
Datenbank mit der SHA-256, die in ihnen steht (Kopien in `tests/referenz/`).

**Jede Information steht nur an einer Stelle.** Stand und Versionen nur in `01`, Abschnitt 0; Änderungen im CHANGELOG;
Befehle zum Einspielen nur in `01`, Abschnitt 6; das Release-spezifische in `RELEASE.md` (wird mit jeder Änderung ersetzt).

## Arbeitsweise
1. Vorschlag → Freigabe durch Carsten → Umsetzung. Bei Darstellungsänderungen zuerst ein Designentwurf.
2. Neue KPIs: Regeln im Regelwerk festhalten, Testfälle von Carsten bestätigen lassen, dann programmieren.
3. Allgemeine Regeln zentral umsetzen (Stichtag `Datum von`, Saisonfenster, 2-Tage-Regel, fehlende Werte,
   Ligareferenz über `Gameday`, Rundung kaufmännisch mit zwei Nachkommastellen und Dezimalarithmetik, Schwellen aus
   `app/config/schwellen.toml`).
4. **Offene Bereinigungen** (`01`, Abschnitt 8.1): Vor jeder Änderung die Liste prüfen. Betrifft ein Punkt eine
   Datei, die ohnehin geändert wird, die Bereinigung mit erledigen und abhaken. Spätestens bei der Rundum-Prüfung des
   Codes werden alle offenen Punkte abgearbeitet (Entscheidung Carsten 16.11.2026).
5. Jeder gefundene Fehler bekommt einen Test. Rechnungen werden mit der unabhängigen Gegenrechnung
   (`tests/gegenrechnung.py`) geprüft; bei Umbauten Vollvergleich vorher/nachher.
6. **GitHub ist die einzige Quelle** (`Carsten1982/soccer-intelligence`, Ablauf in `01`, Abschnitt 6.1):
   - Arbeiten auf einem eigenen Zweig `claude/…`, nie direkt auf `main`. Carsten prüft den Pull Request und führt
     ihn zusammen („Squash and merge“), erst wenn die automatischen Tests grün sind.
   - Jede Änderung bringt eine neue `RELEASE.md` mit (`**Commit:**`-Zeile, `## Erwartungswerte`, `## Im Browser prüfen`)
     sowie Einträge in CHANGELOG und `01`, Abschnitt 0.
   - Im Repository fehlen `data/`, `backup/`, `import/`, `website-bilder/` (Foto der Startseite) und `.env` (nur auf dem Server). Tests mit echten Daten werden darum
     übersprungen; die Testfälle laufen mit `tests/referenz/`. Nie Excel-Dateien ausser `tests/referenz/` committen.
   - Einspielen auf dem Server: `bash /docker/football-dashboard/tools/einspielen.sh github` (macht Carsten).

## Wichtige Regeln
- Schutzregeln in `docs/01_Technisches_Setup.md`, Abschnitt 5, sind verbindlich (nur im eigenen Ordner arbeiten,
  andere Container und Traefik nicht anfassen, kein `docker compose down`, Backup vor Änderungen, Freigabe durch Carsten).
- Keine eigenen Annahmen bei unklaren Regeln: nachfragen statt raten. Offene Punkte: Regelwerk Abschnitt 8.
- Keine KPIs erfinden oder Formeln abändern.
- Fehlende Werte nie als 0 behandeln, echte Nullen immer mitzählen.
- Die Excel-Dateien werden nur gelesen, nie verändert.
- Keine Passwörter, Tokens, Schlüssel oder geheimen Links in Code, Logs, Doku oder Git.
- Keine Vereinslogos (rechtliche Gründe).
- Benutzeroberfläche und Texte auf Deutsch (Schweizer Schreibweise mit „ss“). Ausnahme: die öffentliche Website
  schreibt mit „ß“ (Entscheidung Carsten 16.11.2026, `docs/08_Website.md`, T5).
