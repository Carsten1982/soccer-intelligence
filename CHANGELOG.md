# Soccer Intelligence – Änderungsprotokoll

Neueste Einträge oben. Format: Datum · Wer · Was.
Wer: **Carsten**, **ChatGPT**, **Claude**

---

## 07.11.2026 – Etappe F: Vier Ligen (Paket vorbereitet)

- **Carsten** · Korrigierte Datenbank eingespielt (`f37e36d3…`): LaLiga 17.05.2026 (7 Spiele, K–M aus N–P), *Datenhinweise* ergänzt, id 9198 `Serie A`. Freigabe Etappe F („Bitte programmieren“).
- **Claude** · Serie A (`/dashboard/serie-a`) und LaLiga (`/dashboard/laliga`) aktiv (`app/config/ligen.toml`); Blattname `Serie A` im Code; alle vier Ligablätter sind Pflicht; Ausnahme für „Seria A“ bei der Prüfung „Liga ≠ Blattname“ entfernt; Kopfbereich der Top Anomalien kompakt in zwei Spalten (auf dem Handy untereinander). Version 0.8.
- **Claude** · Prüfung: unabhängige zweite KPI-Berechnung (`tests/gegenrechnung.py`), bestätigt an den Testfällen; Vergleich mit der App für alle 8'808 Begegnungen (alle Spiele der Datenbank + Spielplan, vier Ligen): **0 Abweichungen**. Plausibilität (Tore, Karten, Over 2,5 je Saison) und Häufigkeit der Anomalien geprüft. Protokoll: `docs/tests/pruefprotokoll_etappe_f.md`.
- **Claude** · Tests: `tests/test_gegenrechnung.py` (Gegenrechnung gegen Testfälle; App gegen Gegenrechnung für alle aktiven Ligen), Loader- und Konfigurationstests auf vier Ligen umgestellt, Seitentests für Serie A und LaLiga. 158 Tests lokal grün (ohne Oberflächentests).
- **Claude** · Doku: `01`, `02` (Pflichtblätter), `03` (offener Punkt 11 mit Ergebnis), `04` (Folge des Stichtags bei Zeiträumen), `05` (Kopfbereich), `CLAUDE.md`.

## 07.11.2026 – Vier Ligen beschlossen, Daten Serie A und LaLiga, Regel für verlegte Spiele

- **Carsten** · Gespräch mit Footiqo: fester Download-Link, kumulative Excel-Datei (alle Spiele ab 2020/21), Updates dienstags und donnerstags, dauerhafte Spiel-IDs. Offen u. a.: Spielplan, Spalte `Gameday`, Nutzungsrechte. Konzept `06_Datenlieferung.md` überarbeitet (Etappe G).
- **Carsten / Claude** · Daten Serie A und LaLiga aufbereitet (04.11.): Datum aus `matchDate`, Spieltage berechnet (Methode an Bundesliga/Premier League geprüft), leere Zusatzspalten entfernt; Serie A 2019/20 (10 Spiele) und Entscheidungsspiel Spezia – Verona gelöscht; Verona – Roma (id 9198) nachgetragen und in *Datenhinweise* dokumentiert. Details: `02_Datenbasis.md`, Abschnitt 4c.
- **Carsten** · LaLiga 2026/27 Spieltage 1–2 und Teil von 3 eingetragen; Blatt `Seria A` in `Serie A` umbenannt; Spielplan mit vier Blättern (`LaLiga` ohne Leerzeichen).
- **Carsten / Claude** · Auswertung verzerrter Spieltage 2022/23–2025/26 (ohne Corona): 2+ verlegte Spiele je Saison Bundesliga 0–1, Serie A 0–1, LaLiga 1–3, Premier League 1–5 (meist Supercup bzw. Pokal), unter 2 % der Spiele. **Entscheidung:** bestehende Logik bleibt; Pflegeregel „mehr als 3 Tage ausserhalb des Hauptzeitraums → Status `verschoben`“ (`04_Spielplan.md`, Abschnitt 6). Mehrheitsregel als Idee für später abgelegt.
- **Carsten** · Entscheidung: Dashboard wird auf vier Ligen erweitert (Etappe F), vor der Datenlieferung (Etappe G).
- **Claude** · Doku nachgeführt: `01` (Status, Entscheidungen, Etappen F/G, offene Punkte, Ideen), `02` (vier Ligen, Abschnitt 4c), `03` v1.3 (Ligareferenz für 38 Spieltage, offener Punkt 11 Schwellen), `04` (Blattnamen, Pflegeregel), `05` v4.4 (Bereiche Serie A und LaLiga, Navigation, Regel 4), `06` (Footiqo), `CLAUDE.md` v1.4.
- **Offen** · LaLiga 17.05.2026 korrigieren; *Datenhinweise* id 9198 `Liga` → `Serie A`; Spielplan LaLiga Spieltag 1 nach Pflegeregel anpassen.

## 02.11.2026 – Dokumentation nach Phase 1, Datenlieferung in Klärung *(Paket nicht eingespielt; Inhalt geht im Eintrag vom 07.11.2026 auf)*

- **Carsten** · Angebot eines Datenlieferanten erhalten (Excel per E-Mail dienstags und freitags, vier Ligen ab 2015/16, keine API; 49.99 € inkl. 4 Wochen, danach 9.99 € je 4 Wochen oder 99.99 € pro Jahr). Noch keine Entscheidung.
- **Carsten / Claude** · Reihenfolge festgehalten: zuerst Datenquelle klären (Etappe F), neue KPIs parallel möglich, danach öffentliche Website.
- **Claude** · Neu `docs/06_Datenlieferung.md` (Entwurf): Rückfragen an den Lieferanten, Grundsatz „wir holen ab“, Prüfschranke, Zusammenführen bei Teil- oder Volllieferung, Ergänzung von `Gameday` aus dem Spielplan, Vorgehen in Stufen.
- **Claude** · `01_Technisches_Setup.md` (Status, Entscheidungen, Umsetzungsplan, offene Punkte), `02_Datenbasis.md` (Saison 2026/27 wird ergänzt, Herkunft der Daten), `03_KPI_Regelwerk.md` (Punkt 8.7), `CLAUDE.md` v1.3 nachgeführt.
- **Offen** · Anmeldung im Browser unter `/dashboard` noch zu bestätigen; Name des bisherigen Datenanbieters ermitteln.

## 31.10.2026 (nachts) – Etappe E: Dashboard-Zugang

- **Carsten** · Etappe E eingespielt (152 Tests bestanden; `/` 200, `/robots.txt` 200, `/dashboard/` 401 ohne Passwort), Git `64a684b`.

- **Carsten** · Freigabe Etappe E: Platzhalterseite unter `/` (Variante b), Dashboard unter `/dashboard` mit Passwortschutz, Ziel vor allem: keine Aufnahme in Suchmaschinen. Ein gemeinsamer Zugang (Benutzername und Passwort nur in `.env`).
- **Claude** · `docker-compose.yml`: Dashboard-Router nur noch für `/dashboard`, Passwortabfrage (Traefik BasicAuth, Hash aus `.env`, Variable `SOCCER_DASHBOARD_AUTH`), Kopfzeile `X-Robots-Tag: noindex, nofollow`; Streamlit unter `/dashboard` (`STREAMLIT_SERVER_BASE_URL_PATH`). Fehlt der Eintrag in `.env`, startet Compose nicht.
- **Claude** · Neuer Container `soccer-placeholder` (nginx 1.27, nur lesend) mit `placeholder/index.html` und `robots.txt` (sperrt `/dashboard`). Keine externen Schriften oder Skripte.
- **Claude** · 6 neue Tests (`tests/test_deploy.py`): Pfad, Passwort-Middleware, noindex, keine Zugangsdaten in Git, Daten nur lesbar, Platzhalter vorhanden. Skript `tools/dashboard_passwort.sh` (Zugang setzen/ändern, Passwort verdeckt, nur Hash in `.env`, Abbruch ohne Änderung bei Fehlern). Doku: Architektur, Ordner, Compose, Ablauf „Dashboard-Zugang setzen“. Version 0.7.

## 31.10.2026 (nachts) – Etappe D: Top Anomalien

- **Carsten** · Etappe D eingespielt und abgenommen (145 Tests bestanden, 4 Karten wie erwartet), Git `1a1c527`.

- **Carsten** · Anpassungen nach Abnahme C eingespielt (Git `4c3be5c`). Die vier ergänzten Spielplan-Regeln (`04_Spielplan.md`) bestätigt.
- **ChatGPT** (mit Carsten) · Server-Update: Ubuntu-Pakete und Docker aktualisiert, Neustart erfolgreich, alle vier Anwendungen laufen.
- **Claude** · Auswahl der Top-Anomalien gemäss Regelwerk 2.6 / Briefing 5.1 (`app/core/top.py`): nur KPI 02 und 04, nur leicht/stark, ohne vorläufige Werte und ohne verschobene/abgesagte Spiele; stark vor leicht, dann grösste Abweichung, dann Datum, dann Reihenfolge im Spielplan; höchstens ein Eintrag je Begegnung, höchstens vier, kein Auffüllen.
- **Claude** · Startseite „Top Anomalien“ mit Karten (Rang, Liga, Spieltag, Begegnung, KPI, Hauptwert, Abweichung, Einstufung, Text) und Link zur Liga (`app/views/top_anomalien.py`). 13 neue Tests (`tests/test_top.py`).
- **Claude** · Spieltag-Pfeile grösser, Spieltagsfeld ohne Zeilenumbruch. Version 0.6.

## 31.10.2026 (abends) – Anpassungen nach Abnahme Etappe C (Paket vorbereitet)

- **Carsten** · Abnahme Etappe C: Zahlen FC Köln geprüft, „sieht gut aus“. Etappe C eingespielt als Git `8cb5f0f`.
- **Carsten / Claude** · Neue Datenbank (`6b84d8d2…`, mit Spieltag 1 2026/27) und Spielplan Version 2 (Spieltage 1–2) geprüft und aktiviert. Korrigiert: id 119365 Gelbe Karten (Leerzeichen → 2), PL-Spieltag 2 falsch nummeriert, BL-Spieltag 2 unvollständig. Spieltag 1 alt vs. neu nachgerechnet: 57 KPI-Werte, 0 Unterschiede.
- **Carsten** · Wünsche: (1) Abstand Navigation → Überschrift um 80 % verkleinern, (2) Navigation dunkelgrau mit weisser Schrift, aktiver Tab fett mit blauem Balken, (3) Spieltage mit Pfeilen wählbar, je Liga getrennt, nicht in die Zukunft, Auswahl in der Adresse (`?spieltag=1`), Top Anomalien immer aktueller Spieltag.
- **Claude** · Umgesetzt (`app/views/components.py`, `app/views/liga.py`, `app/core/matchday.py`). Briefing (`05_Dashboard.md`) Kapitel 3.2 und 14 angepasst.
- **Claude** · Tests: Referenz-Datenbank `6d68583c…` als Kopie unter `tests/referenz/`, damit die 32 KPI-Testfälle unabhängig vom aktuellen Datenstand laufen. Neue Tests für die Spieltag-Auswahl und dafür, dass spätere Spiele einen früheren Spieltag nicht verändern.
- **Claude** · `02_Datenbasis.md` und `04_Spielplan.md` auf den neuen Datenstand gebracht.
- **Carsten** · Entscheidung: Die md-Dateien sind ab sofort die einzige massgebliche Quelle, Word nur noch Archiv. **Claude** · Umgestellt in `03_KPI_Regelwerk.md` (v1.2), `05_Dashboard.md` (v4.3), `CLAUDE.md`, `01_Technisches_Setup.md`, `test_kpi04_gelbe_karten.md`; neu `word/README.md` (Archivhinweis).

## 31.10.2026 – Etappe C (Paket vorbereitet)

- **Carsten** · Etappe B abgenommen („Darstellung passt“), eingespielt als Git `ff4fbe8`.
- **Claude** · KPI 01–04 berechnet gemäss `03_KPI_Regelwerk.md` (`app/core/kpis.py`). Exakte Rechnung mit Brüchen, Rundung erst für die Anzeige (kaufmännisch, 4,35 → 4,4). Stichtag = „Datum von“ aus dem Spielplan.
- **Claude** · Alle JSON-Testfälle aus `docs/tests/` laufen als automatische Tests (32 Testfälle, dazu Kontrolle der verwendeten Spiel-IDs, Nachholspiel id 14680, fehlende Karten id 14421, 2-Tage-Regel, Grenzwerte ±20/±35 %): alle bestanden.
- **Claude** · Liga-Tabellen mit KPI-Spalten gemäss Briefing Kapitel 7–9: Formkurve als farbige Punkte, Anomalie-Punkte grau/gelb/rot, Datenbasis mit „V“ für vorläufig, Beschreibung gemäss Regelwerk, Legende unter der Tabelle.
- **Claude** · Datenqualität → Häufigkeit der Anomalien (Briefing 6.3) für die letzte abgeschlossene Saison. Ergebnis 2025/26: KPI 03 Bundesliga 59,5 % Anomalien (Premier League 19,9 %), KPI 02 und 04 zwischen 8,5 % und 27,1 %.
- **Carsten** · Problem gemeldet: Tabelle liess sich nicht nach rechts scrollen. **Claude** · Ursache: Die Scrollbar lag am unteren Tabellenende ausserhalb des sichtbaren Bereichs. Lösung: Tabelle in eigenem Rahmen (max. 72 % der Fensterhöhe) mit immer sichtbarer, breiterer Scrollbar; Kopfzeilen bleiben oben, # und Spiel links fixiert.
- **Claude** · Offene KPI-Punkte umgesetzt wie in den Testfällen angenommen (Regelwerk 8): KPI 03 bei genau 0,0 % nur Überschrift ohne Satz (Punkt 2); Teamabweichungen und Hauptwert mit einer Nachkommastelle (Punkte 6, 9); Aufsteiger-Spiele zeigen Gegnerwert und Ligareferenz, Hauptwert/Abweichung/Anomalie als „–“ (Punkt 10).

## 31.10.2026 – Etappe B (Paket vorbereitet)

- **Claude** · Spielplan einlesen und prüfen (`app/core/fixtures.py`), aktueller Spieltag je Liga (`app/core/matchday.py`), Konfiguration der Ligen und Teamliste (`app/config/ligen.toml`, `app/config/teams.toml`).
- **Claude** · Navigation als Tabs oben: Top Anomalien (Startbereich, Inhalt folgt in Etappe D) · Bundesliga · Premier League · Datenqualität. Die Seite „Übersicht“ entfällt, ihr Inhalt steht jetzt unter Datenqualität → Datenbank.
- **Claude** · Liga-Bereiche zeigen die Begegnungen des aktuellen Spieltags in der Tabelle mit fixierten Spalten # und Spiel (KPI-Spalten folgen in Etappe C). Kopfbereich gemäss Briefing 3.2.
- **Claude** · Datenqualität mit drei Reitern: Datenbank, Spielplan und Spieltage (Übersicht mit Status beendet/aktuell/kommend), Häufigkeit der Anomalien (folgt).
- **Claude** · Zeitzone für „heute“ auf Europe/Zurich korrigiert (vorher Europe/Berlin).
- **Claude** · Tests: 72 (davon 4 Seiten-Tests, die nur auf dem Server mit Streamlit laufen). Tests mit echten Dateien prüfen genaue Werte nur für den bekannten Dateistand (SHA-256), bei neueren Dateien nur noch „keine Fehler“.
- **Claude** · Ergänzte Spielplan-Regeln (bitte bestätigen, Details `04_Spielplan.md`): fehlendes Blatt einer aktiven Liga = Fehler; leeres Blatt einer aktiven Liga = Warnung; Team ohne Ligaspiele in Saison und Vorsaison = Hinweis; Spieltag, dessen Spiele alle verschoben/abgesagt sind, gilt als beendet.
- **Claude** · Doku: `01_Technisches_Setup.md`, `02_Datenbasis.md`, `04_Spielplan.md` auf den Stand nach Etappe A gebracht.

## 31.10.2026 – Etappe A eingespielt

- **Carsten** · Neue Datenbank (58 Spalten, SHA-256 6d68583c…) und Spielplan.xlsx nach data/ übernommen; alte Datenbank gesichert in backup/…_alt_57Spalten.xlsx.
- **Carsten / Claude** · Git eingerichtet (30.10.2026), privates Repository Carsten1982/soccer-intelligence auf GitHub.
- **Carsten / Claude** · Paket Schritt 1 eingespielt: 26 Tests bestanden, nur football-dashboard neu gebaut. App zeigt Übersicht und Datenqualität: 0 Fehler, 2 Warnungen (id 11344), 17 Hinweise.

## 30.10.2026 (abends) – Dokumentation bereinigt

- **Claude** · Neue Datei `docs/05_Dashboard.md`, erzeugt aus dem Dashboard-Briefing v4.2 (Word). Damit liegen alle Vorgaben für Claude Code als md im Projekt. Massgeblich bleibt das Word-Dokument. Verweise in `CLAUDE.md` und `01_Technisches_Setup.md` angepasst.

- **Claude** · Neue Datenbank geprüft (58 Spalten mit `Gameday`). Zwei überschriebene Zellen in der Premier League korrigiert: id 5393 `Gameday` „bitte“ → 4, id 99466 `FT Home Goals` „Ergebnisse stimmen.“ → 2. Neue SHA-256 `6d68583c2e66616e92c1bf3e8a8611b4b517bcf4c0a7a91c68101ea26a2284e2`. Details: `02_Datenbasis.md`, Abschnitt 4b.
- **Claude** · Alle erwarteten Werte der Testfälle KPI 01–04 mit der korrigierten Datenbank nachgerechnet: 144 Prüfwerte, 0 Abweichungen. SHA-256 in allen Testfällen aktualisiert.
- **Carsten / Claude** · Festgelegt: Es gibt nur noch ein KPI-Regelwerk, `docs/03_KPI_Regelwerk.md` (v1.1). `03_KPI_Grundregeln.md` und `docs/kpis/` gelöscht. Die Auswahl der Top-Anomalien wurde als Abschnitt 2.6 übernommen.
- **Claude** · `03_KPI_Regelwerk.md` v1.1: Stichtag = `Datum von`; Reihenfolge bei fehlenden Werten; Sortierung; Rundung mit Dezimalarithmetik; Vorzeichen im Text „Keine Anomalie“; Spalten AC/AD für KPI 04; offene Punkte 1, 3, 8 erledigt, 9 und 10 neu.
- **Claude** · Testfall KPI 02, PL-1: Text auf „+7,0 %“ angepasst (Vorzeichenregel). Annahmen in den Testfällen KPI 02–04 als geklärt markiert.
- **Claude** · Word „Definition der Dashboard-KPIs“: Änderungen mit Änderungsverfolgung (Stichtag, Rundung, Vorzeichen, Hinweis KPI 02 Fall A, Platzhalter KPI 03, „2,5“). Mit der Annahme gelten die Punkte als erledigt.
- **Claude** · Dashboard-Briefing v4.2 (Änderungsverfolgung): Verweis auf `03_KPI_Regelwerk.md`, „Datum von/bis“ in Kapitel 4.4, Abschnittsnummern des Regelwerks, Testfälle als vorhanden markiert.
- **Claude** · `CLAUDE.md` neu: Passwortschutz statt „öffentlich ohne Login“, Etappen A–E, richtige Dateinamen, keine Logos, Top Anomalien und Datenqualität.
- **Claude** · `01_Technisches_Setup.md`, `02_Datenbasis.md`, `04_Spielplan.md` an die Änderungen angepasst. Doppelte Dateien `_1` aufgelöst: es gilt jeweils die neue Fassung.
- **Claude** · Code-Paket Schritt 1 an 58 Spalten angepasst: `Gameday` als Pflicht-Zahlenspalte, neue Prüfung der Spieltage (Bereich, Anzahl Spiele, Team doppelt). 26 Tests, alle bestanden. Die unkorrigierte Datei wird korrekt mit 2 Fehlern abgelehnt.

## 30.10.2026

- **Carsten** · `Spielplan.xlsx` im neuen Format geliefert (Spieltag 1, 2026/27). **Claude** · geprüft: keine Fehler. `04_Spielplan.md` Abschnitt 7 und Umsetzungsplan in `01_Technisches_Setup.md` aktualisiert.
- **Carsten** · Entscheidung: Spielplan mit zwei Datumsspalten „Datum von“ / „Datum bis“ statt eines Datums pro Spiel. Stichtag für KPIs = „Datum von“. `04_Spielplan.md` angepasst (Claude).
- **Claude** · Gesamtprüfung der Dokumentation: Umsetzungsplan in `01_Technisches_Setup.md` auf Etappen A–E umgestellt, Abschnitt 6 in `02_Datenbasis.md` aktualisiert, offene Punkte „Gameday“ und doppelte KPI-Datei eingetragen.
- **Carsten** · Entscheidung: Dashboard unter `/dashboard` mit Passwortschutz, Platzhalterseite bleibt unter `/`. Ersetzt die Entscheidung vom 25.10.2026 („öffentlich ohne Login“).
- **Claude** · `01_Technisches_Setup.md` angepasst (Statusübersicht, Entscheidungen, geplantes Routing, Schutzregel 8, Umsetzungsplan). Am Server wurde nichts geändert.
- **Carsten** · Entscheidung: Spielplan mit einem Datum pro Spiel und Spalte „Saison“. Aktueller Spieltag pro Liga gemäss Regel „nächster nicht beendeter Spieltag, sonst letzter der Datei“.
- **Claude** · KPI-Regelwerk als md erzeugt aus Word (Arbeitsstand 30.10.2026): `03_KPI_Grundregeln.md` und `kpis/KPI_01…04` (am Abend durch `03_KPI_Regelwerk.md` ersetzt, siehe oben).
- **Carsten** · Entscheidung: 2-Tage-Regel statt 3-Tage-Regel, gilt nur für Teamwerte.
- **Carsten** · Entscheidung: keine Vereinslogos (rechtliche Gründe). In `01_Technisches_Setup.md` nachgetragen.
- **Claude** · Neue Datei `04_Spielplan.md` (Aufbau, aktueller Spieltag, Prüfregeln, Stand der hochgeladenen Datei). Abschnitt 7 in `02_Datenbasis.md` verweist jetzt darauf.

## 28./29.10.2026

- **Carsten / ChatGPT** · Spalte `Gameday` in der Datenbank ergänzt. Ligareferenz = letzte 20 Spieltage laut `Gameday`.
- **Carsten / ChatGPT** · Testfälle KPI 01–04 erstellt und bestätigt (Spieltag 1 2026/27 am 28.10., Spieltag 3 2025/26 am 29.10.).
- **ChatGPT** · `03_KPI_Regelwerk.md` und `CLAUDE.md` erstellt.

## 25.10.2026 – Initiale Dokumentation

Ausgangsstand des Projekts: siehe `01_Technisches_Setup.md` und `02_Datenbasis.md`.
Ab dem Einspielen von Schritt 1 wird jede Änderung hier eingetragen.
