# Soccer Intelligence – Projektübersicht

**Spezifikation v1.1** · Stand 30.10.2026

## Worum es geht
Soccer Intelligence ist eine Fussball-Analyseplattform. Sie berechnet statistische Auffälligkeiten
(Anomalien) anstehender Ligaspiele und stellt sie verständlich dar. Datenbasis ist eine Excel-Datei
mit historischen Spieldaten der Bundesliga und der Premier League, Saisons 2020/21–2025/26.
Das Projekt ist zugleich ein Lernprojekt und nicht kommerziell. Code soll nachvollziehbar, gut
kommentiert und schrittweise aufgebaut sein. Nach jedem Schritt kurz erklären, was gemacht wurde.

## Technischer Rahmen
- Streamlit-App im Docker-Container `football-dashboard` auf einem Hostinger-VPS.
- Projektordner auf dem Server: `/docker/football-dashboard/` (Details: `docs/01_Technisches_Setup.md`).
- Excel-Dateien liegen in `data/` und sind im Container nur lesbar (`/data`, read-only).
- Python 3.12, streamlit 1.66.1, pandas 3.1.0, openpyxl 3.1.5.

## Zugang (beschlossen 30.10.2026, Umsetzung in Etappe E)
- `https://soccer-intelligence.com/` zeigt weiterhin die öffentliche Platzhalterseite.
- Das Dashboard liegt unter `/dashboard` und ist **passwortgeschützt** (Traefik, BasicAuth).
  Zugangsdaten nur als Hash in `.env` auf dem Server, nie im Code oder in Git.
- Bereiche: `/dashboard` (Top Anomalien), `/dashboard/bundesliga`, `/dashboard/premier-league`,
  `/dashboard/datenqualitaet`. Jede weitere Liga erhält automatisch einen eigenen Bereich.

## Ziel der ersten Phase
Ein internes Dashboard, das für den aktuellen Spieltag jeder Liga alle Begegnungen mit den
KPIs 01–04 zeigt, dazu die Top Anomalien und die Datenqualität. Aufbau und Darstellung:
`docs/05_Dashboard.md` (Dashboard-Briefing v4.2).

Umsetzung in Etappen gemäss `docs/01_Technisches_Setup.md`, Abschnitt 7:
- **A – Fundament:** Datenbank einlesen und prüfen, Versionen festlegen (Paket Schritt 1)
- **B – Spielplan und Datenqualität:** `data/Spielplan.xlsx` einlesen, aktueller Spieltag, Bereich Datenqualität
- **C – Liga-Tabellen mit KPIs:** KPI 01–04, ein KPI nach dem anderen, jeweils gegen die Testfälle geprüft
- **D – Top Anomalien:** Auswahl-Logik gemäss KPI-Regelwerk, Abschnitt 2.6
- **E – Dashboard-Zugang:** Umzug nach `/dashboard`, Passwortschutz, Platzhalter unter `/` (separate Freigabe)

Nicht Teil dieser Phase:
- Öffentliche, gestaltete Website (Mobile First), eigener Schritt danach
- Weitere KPIs ausser 01–04
- Externe Fussball-APIs, Bearbeiten oder Importieren von Daten in der App
- **Vereinslogos** (nicht erlaubt, rechtliche Gründe)

## Quellen (verbindlich)
| Datei | Inhalt |
|---|---|
| docs/01_Technisches_Setup.md | Server, Container, Ordner, Schutzregeln, Abläufe, Architektur, Etappen |
| docs/02_Datenbasis.md | Aufbau der Excel-Datei (58 Spalten inkl. `Gameday`), Formate, Prüfregeln |
| docs/03_KPI_Regelwerk.md | Berechnungsregeln, Anomalie-Logik, Top-Anomalien, Dashboard-Texte |
| docs/04_Spielplan.md | Aufbau des Spielplans (`Datum von` / `Datum bis`), aktueller Spieltag, Prüfregeln |
| docs/05_Dashboard.md | Dashboard-Briefing v4.2: Aufbau, Navigation, Darstellung, Abnahmekriterien |
| docs/tests/test_kpi01_formkurve.md … test_kpi04_gelbe_karten.md | Bestätigte Testfälle mit erwarteten Ergebnissen (JSON) |
| data/Database-Soccer-Intelligence.xlsx | Einzige gültige Datenquelle für gespielte Spiele |
| data/Spielplan.xlsx | Angesetzte Begegnungen |
| CHANGELOG.md | Änderungsprotokoll, jede Änderung wird dort eingetragen |

Bei Widersprüchen zu Berechnungen gilt das KPI-Regelwerk, bei Darstellung und Navigation das
Dashboard-Briefing. `03_KPI_Regelwerk.md` und `05_Dashboard.md` sind aus Word-Dokumenten erzeugt
und werden nicht direkt bearbeitet. Die Testfälle sind die Referenz dafür, ob eine Berechnung korrekt ist; ihre
JSON-Blöcke werden zu automatischen Tests. Sie gelten für die Datenbank mit der SHA-256, die in
den Testfällen steht.

## Arbeitsweise für die KPIs
1. Allgemeine Regeln zentral umsetzen: Stichtag (`Datum von`), Saisonfenster, 2-Tage-Regel,
   fehlende Werte, Ligareferenz über `Gameday`, Rundung (kaufmännisch, Dezimalarithmetik, nicht `round()`),
   Vorzeichen, Anomalie-Schwellenwerte.
2. Testfälle aus den JSON-Blöcken als automatische Tests anlegen, bevor der KPI-Code entsteht.
3. KPI für KPI umsetzen, bis alle Tests grün sind.
4. Erst danach die Darstellung im Dashboard.

## Wichtige Regeln
- Die Schutzregeln in `docs/01_Technisches_Setup.md`, Abschnitt 5, sind verbindlich
  (nur im eigenen Ordner arbeiten, andere Container und Traefik nicht anfassen, kein
  `docker compose down`, Backup vor Änderungen, Änderungen erst nach Freigabe durch Carsten).
- Keine eigenen Annahmen bei unklaren Regeln: nachfragen statt raten.
  Offene Punkte stehen in Abschnitt 8 des KPI-Regelwerks.
- Keine KPIs erfinden oder Formeln abändern.
- Fehlende Werte nie als 0 behandeln, echte Nullen immer mitzählen.
- Die Excel-Dateien werden nur gelesen, nie verändert.
- Keine Passwörter, Tokens oder Schlüssel in Code, Logs oder Git.
- Benutzeroberfläche und Texte auf Deutsch.

## Fertig ist Phase 1, wenn
- alle vier KPIs exakt die Ergebnisse aus den Testfällen liefern,
- jede Liga ihren aktuellen Spieltag gemäss Spielplan mit allen Begegnungen und KPI-Spalten zeigt,
- der Bereich Top Anomalien die Auswahl gemäss Regelwerk 2.6 zeigt,
- Sonderfälle (Aufsteiger, „vorläufig“, nicht berechenbar, verschoben/abgesagt) korrekt dargestellt werden,
- das Dashboard unter `/dashboard` nur mit Passwort erreichbar ist.
