# Soccer Intelligence – Projektübersicht

**Spezifikation v1.7** · Stand 08.11.2026

## Worum es geht
Soccer Intelligence ist eine Fussball-Analyseplattform. Sie berechnet statistische Auffälligkeiten
(Anomalien) anstehender Ligaspiele und stellt sie verständlich dar. Datenbasis ist eine Excel-Datei
mit historischen Spieldaten von Bundesliga, Premier League, Serie A und LaLiga, Saisons 2020/21–2025/26, dazu
spieltagweise die laufende Saison 2026/27. Im Dashboard aktiv: alle vier Ligen (seit Etappe F) mit KPI 01–09 (seit Etappe H, Version 0.9).
Das Projekt ist zugleich ein Lernprojekt und nicht kommerziell. Code soll nachvollziehbar, gut
kommentiert und schrittweise aufgebaut sein. Nach jedem Schritt kurz erklären, was gemacht wurde.

## Technischer Rahmen
- Streamlit-App im Docker-Container `football-dashboard` auf einem Hostinger-VPS.
- Projektordner auf dem Server: `/docker/football-dashboard/` (Details: `docs/01_Technisches_Setup.md`).
- Excel-Dateien liegen in `data/` und sind im Container nur lesbar (`/data`, read-only).
- Python 3.12, streamlit 1.66.1, pandas 3.1.0, openpyxl 3.1.5.

## Zugang (beschlossen 30.10.2026, umgesetzt in Etappe E am 31.10.2026)
- `https://soccer-intelligence.com/` zeigt die öffentliche Platzhalterseite (Container `soccer-placeholder`, Ordner `placeholder/`).
- Das Dashboard liegt unter `/dashboard` und ist **passwortgeschützt** (Traefik, BasicAuth).
  Zugangsdaten nur als Hash in `.env` auf dem Server, nie im Code oder in Git.
- Bereiche: `/dashboard` (Top Anomalien), `/dashboard/bundesliga`, `/dashboard/premier-league`,
  `/dashboard/serie-a`, `/dashboard/laliga`, `/dashboard/datenqualitaet`. Jede weitere Liga erhält automatisch einen eigenen Bereich.

## Ziel der ersten Phase (abgeschlossen 31.10.2026)
Ein internes Dashboard, das für den aktuellen Spieltag jeder Liga alle Begegnungen mit den
KPIs 01–04 zeigt, dazu die Top Anomalien und die Datenqualität. Aufbau und Darstellung:
`docs/05_Dashboard.md` (Dashboard-Briefing).

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

## Nach Phase 1 (Stand 08.11.2026)
Erledigt: **Etappe F – Vier Ligen** (07.11.2026) und **Etappe H – KPI 05–09** (Version 0.9, eingespielt 08.11.2026, Git `51e595b`).
Als Paket bereit: **H.2 – Stabilität** (Version 0.9.2, Befunde der zweiten Code-Prüfung). Eingespielt: **H.1 – Aufräumen und Tempo** (Version 0.9.1, Git `b5a7ea8`, Funde der Code-Prüfung vom 08.11.2026, Ergebnisse unverändert,
`docs/tests/pruefprotokoll_h1.md`). Zu Etappe H (Frontend; KPI-Regelwerk v2.2,
Abschnitt 9; Testfälle `docs/tests/test_kpi05…09…` **bestätigt am 08.11.2026**). Mit Etappe H gilt ausserdem:
**alle KPIs mit zwei Nachkommastellen** (auch die Abweichung; Einstufung nach dem auf zwei Stellen gerundeten Wert, Regelwerk 2.3),
**Top Anomalien über KPI 02–09** (bisherige Rangfolge, Regelwerk 2.6), kompaktere Liga-Tabelle mit Details per Aufklappen,
Schwellen in `app/config/schwellen.toml` (überall Standard ±20/±35 %). Ablauf: md-Dateien → Backup → Design-Vorschlag →
Programmieren und Einspielen. Danach **Etappe I – Simulation** (intern): zuerst Schwellen-Analyse je KPI und Liga mit Feintuning
und Gewichtung der Top Anomalien (Regelwerk, offener Punkt 17), danach KPI 10–13 und Ergebniskontrolle. Parallel in Klärung:
**Etappe G – Datenlieferung** (Footiqo, `docs/06_Datenlieferung.md`). Danach die **öffentliche Website**. Die Logik für den aktuellen Spieltag bleibt; verlegte Spiele
werden im Spielplan als `verschoben` gepflegt (`docs/04_Spielplan.md`, Abschnitt 6). Ein Import ändert die Datenbank nur kontrolliert (Prüfschranke,
Backup, Korrekturen an alten Spielen nie still übernehmen); das Dashboard bleibt nur lesend.

## Quellen (verbindlich)
| Datei | Inhalt |
|---|---|
| docs/01_Technisches_Setup.md | Server, Container, Ordner, Schutzregeln, Abläufe, Architektur, Etappen |
| docs/02_Datenbasis.md | Aufbau der Excel-Datei (58 Spalten inkl. `Gameday`), Formate, Prüfregeln |
| docs/03_KPI_Regelwerk.md | Berechnungsregeln, Anomalie-Logik, Top-Anomalien, Dashboard-Texte |
| docs/04_Spielplan.md | Aufbau des Spielplans (`Datum von` / `Datum bis`), aktueller Spieltag, Prüfregeln |
| docs/05_Dashboard.md | Dashboard-Briefing (v4.7): Aufbau, Navigation, Darstellung, Abnahmekriterien |
| docs/06_Datenlieferung.md | Konzept regelmässige Datenlieferung / Import, Footiqo (Entwurf, nicht freigegeben) |
| docs/tests/test_kpi01_formkurve.md … test_kpi04_gelbe_karten.md | Bestätigte Testfälle mit erwarteten Ergebnissen (JSON) |
| docs/tests/test_kpi05_ecken.md … test_kpi09_schuesse_aufs_tor.md | Bestätigte Testfälle KPI 05–09 (08.11.2026), Nachprüfung `Testfaelle_KPI05-09_Nachpruefung.xlsx` |
| docs/tests/pruefprotokoll_etappe_f.md | Prüfung der vier Ligen: Gegenrechnung, Plausibilität, Häufigkeit (07.11.2026) |
| docs/tests/pruefprotokoll_etappe_h.md | Prüfung KPI 05–09 und zwei Nachkommastellen: Testfälle, Gegenrechnung, Vollvergleich (08.11.2026) |
| docs/tests/pruefprotokoll_h1.md | Prüfung H.1: alle Ergebnisse vor/nach dem Umbau identisch, Zeitmessung (08.11.2026) |
| data/Database-Soccer-Intelligence.xlsx | Einzige gültige Datenquelle für gespielte Spiele |
| data/Spielplan.xlsx | Angesetzte Begegnungen |
| CHANGELOG.md | Änderungsprotokoll, jede Änderung wird dort eingetragen |

Bei Widersprüchen zu Berechnungen gilt das KPI-Regelwerk, bei Darstellung und Navigation das
Dashboard-Briefing. **Seit 31.10.2026 sind die md-Dateien in `docs/` die einzige massgebliche Quelle.**
Die Word-Dokumente im Ordner `word/` sind nur noch Archiv und werden nicht mehr gepflegt. Die Testfälle sind die Referenz dafür, ob eine Berechnung korrekt ist; ihre
JSON-Blöcke werden zu automatischen Tests. Sie gelten für die Datenbank mit der SHA-256, die in
den Testfällen steht.

## Arbeitsweise für die KPIs
1. Allgemeine Regeln zentral umsetzen: Stichtag (`Datum von`), Saisonfenster, 2-Tage-Regel,
   fehlende Werte, Ligareferenz über `Gameday`, Rundung (kaufmännisch, zwei Nachkommastellen ab Etappe H, Dezimalarithmetik, nicht `round()`),
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
