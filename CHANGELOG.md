# Soccer Intelligence – Änderungsprotokoll

Neueste Einträge oben. Format: Datum · Wer · Was.
Wer: **Carsten**, **ChatGPT**, **Claude**

---

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
