# Soccer Intelligence – Änderungsprotokoll

Neueste Einträge oben. Format: Datum · Wer · Was.
Wer: **Carsten**, **ChatGPT**, **Claude**

---

## 09.11.2026 – Etappe I.1, Nachtrag (Version 0.10.1, Paket bereit)

- **Carsten** · Rückmeldungen nach dem ersten Ausprobieren: Info-Felder ohne Text, KPI-Spalte zu breit, Schwellen fehlen in „Ergebnisqualität“, Saisonauswahl, Stufe nach oben, linker Bereich schmaler und dunkler.
- **Claude** · Info-Felder: eigenes Fenster beim Darüberfahren statt Browser-Tooltip (der in Streamlit nicht erschien; Fehler von Claude). KPI-Spalte zweizeilig, neue Spalte „Schwellen“ in der Ergebnisqualität (eigene Werte blau, darunter die gültigen), Urteil schmaler. Saisons: alle abgeschlossenen, letzte 4/3/2, letzte Saison, aktuelle Saison (ersetzt Einstellen/Prüfen und das Kästchen „laufende Saison“; Regelwerk 11.4). Stufe über „Je KPI“ mit ⓘ. Einstellungen 10 % schmaler und grau hinterlegt. Rechnung unverändert, Gegenrechnung läuft weiter; lokal 336 Tests bestanden.

## 08.11.2026 – Etappe I.1: Simulation – Spielwiese (Version 0.10, eingespielt)

- **Carsten** · Mini-Briefing „Saison-Kalibrator und Ergebniskontrolle“. **Claude** · kritische Prüfung mit Probelauf (Saisons 2021/22–2025/26): Trefferquote allein täuscht (z. B. KPI 06 positiv 38,5 % gegen 36,7 % ohne Anomalie), darum Mehrwert als Hauptkennzahl; globale Schwellen allein reichen nicht (KPI 05/09 nur 22–80 Fälle); erste Saison ohne Vorsaison ungeeignet.
- **Carsten** · Entscheidungen: Mehrwert als Hauptzahl mit Info-Texten; eingetroffen = tatsächlicher Wert gegen die Ligareferenz vor dem Spiel (KPI 03: 2,5-Marke, KPI 08: beide treffen); Urteil besser/schlechter nur über der Schwankung, unter 100 Fällen grau; Saisons ohne 2020/21, Einstellen 2021/22–2023/24 / Prüfen 2024/25–2025/26; ein Tab mit Ligaauswahl; Aufsteiger/vorläufig raus; leicht und stark getrennt in der Häufigkeit, zwei Tabellen; Schwellen global und je KPI; Überschrift „Spielwiese“; Design **Variante B** (Einstellungen links).
- **Claude** · Umsetzung: `app/core/simulation.py` (Fälle einmal je Datenbankstand, rund 30 s; neu einstufen in 0,2 s), `app/views/simulation.py`, Zwischenspeicher in `state.py`, Navigation, `simulation` als reservierte Adresse. Regelwerk v2.3 Abschnitt 11 (Punkt 13 erledigt), Briefing v4.8 Abschnitt 6.4.
- **Claude** · Prüfung: 26 neue Tests (`tests/test_simulation.py`, Seitentest), lokal 336 bestanden. Unabhängige Gegenrechnung (`tests/gegenrechnung.py`, `sim_events`/`sim_summary`): „eingetroffen“ je Spiel für alle 306 Spiele der Bundesliga 2025/26 sowie alle Tabellenwerte (Anzahl leicht/stark, Fälle, Trefferquote, ohne Anomalie, Mehrwert) für alle vier Ligen 2025/26 bei vier Schwellenpaaren – automatisch bei jedem Einspielen. Einmaliger Vollvergleich 2021/22–2025/26 (7'230 Spiele, je Liga und alle Ligen, fünf Schwellenpaare): 2'000 Vergleichswerte, 0 Abweichungen. Bestehende KPIs, Schwellen und Seiten unverändert.
- **Carsten** · Etappe I.1 eingespielt: Backup `backup/2026-11-08_1626_vor_I1` (Git `291eeac`), 345 Tests bestanden, 1 übersprungen; `/` 200, `/dashboard/` 401; Git `dbd90c5`.

## 08.11.2026 – H.2: Stabilität (Version 0.9.2, eingespielt)

- **Carsten** · Zweite Code-Prüfung durch ChatGPT: 6 Stabilitätsbefunde S1–S6. **Claude** · alle 6 am Code nachvollzogen (S1–S4 selbst nachgestellt), keiner betrifft die KPI-Berechnung mit den echten Daten. **Carsten** · Freigabe zur Umsetzung.
- **Claude** · S1: `ligen.toml`, `teams.toml`, `schwellen.toml` mit falscher Struktur (z. B. `liga = 1`, `standard = 35`) oder als Ordner → Meldung „Konfiguration ungültig“ statt Absturz (`config.table_list`). S2: Zahl in der Spalte `Date` (z. B. 45800) → Fehler „Ungültiges Datum“, statt still als 01.01.1970 gelesen zu werden. S3: id `inf`, `-inf`, NaN, Text → kein Absturz mehr beim Erstellen der Meldungen (`rows.valid_id`). S4: Datenhinweis mit id 1,5 gilt für kein Spiel (vorher für Spiel 1). S5: Zwischenspeicher erkennt eine ersetzte Datei auch bei gleicher Grösse und Änderungszeit (Schlüssel zusätzlich mit ctime und Dateinummer, `files.file_key`; betrifft Datenbank, aufbereitete Ligen, Häufigkeit, Spieltags-KPIs, Schwellen, Spielplan). S6: Datenbank und Spielplan werden nur einmal gelesen; Prüfsumme und Inhalt stammen sicher vom selben Stand, eine verschwundene Datei ergibt „Datei nicht lesbar“ (`files.read_file`). Zudem: `tests/test_ui.py` lässt sich ohne Streamlit laden.
- **Claude** · Prüfung: 32 neue Tests (`tests/test_h2.py`), lokal 311 bestanden; alle 8'808 Begegnungen, Häufigkeit und Prüfmeldungen vor/nach identisch. Formeln, Schwellen, Testfälle und Darstellung unverändert. `02_Datenbasis.md`: Prüfregeln (Zahl statt Datum, Datenhinweis-id).
- **Carsten** · H.2 eingespielt: Backup `backup/2026-11-08_1122_vor_H2` (Git `b5a7ea8`), 319 Tests bestanden, 1 übersprungen; `/` 200, `/dashboard/` 401; Git `291eeac`.

## 08.11.2026 – H.1: Aufräumen und Tempo (Version 0.9.1, eingespielt)

- **Carsten** · Code-Prüfung durch einen zweiten Claude (Opus) beauftragt. Bericht: keine Rechenfehler; 3 mögliche Abstürze, Tempo, Aufräumen. **Freigabe H.1** mit Entscheidungen: (1) Kommazahl bei Toren, `Gameday` oder `id` = Fehler; bei Ecken, Karten, Schüssen = Warnung, der Wert gilt als fehlend, nie abschneiden. (2) Anteile in der Häufigkeit kaufmännisch runden wie alle anderen Werte.
- **Claude** · Abstürze verhindert: Blatt *Datenhinweise* ohne Spalte `Liga` (R1); kaputtes XML in einer Excel-Datei → Meldung „Datei nicht lesbar“ statt Absturz, in Datenbank und Spielplan (R2); ungültige `teams.toml` oder `schwellen.toml` → Meldung „Konfiguration ungültig“ beim Start (R3).
- **Claude** · Tempo: Spiele je Begegnung nur noch einmal in Zeilen umgewandelt (L1); Ligareferenzen in der Häufigkeit je Saison, Spieltag **und Stichtag** geteilt (L2). Häufigkeit vier Ligen 28,7 → 5,8 s, aktueller Spieltag (39 Begegnungen) 0,76 → 0,18 s. KPI-Ergebnisse eines Spieltags werden zwischengespeichert (L3), neu berechnet erst, wenn sich Datenbank, Spielplan, Schwellen, Ligen oder Teamliste ändern.
- **Claude** · Aufbau: Berechnung der Spieltags-KPIs aus der Oberfläche nach `app/core/results.py` (A11, Top Anomalien ruft nicht mehr den Liga-Bereich auf); Top Anomalien rechnet erst nach der Fehlerprüfung (R7); `League.matchdays` statt mehrfach `2 × (Teams − 1)` (A5); gemeinsame Prüfsumme `app/core/files.py` (A4); Meldungen „Statistik fehlt“ je Stufe auf 50 begrenzt wie alle anderen (R8).
- **Claude** · Aufräumen: alte Tabelle aus Etappe C/F samt CSS entfernt (A1), ungenutzte Funktionen und Doppelungen entfernt (A2, A3, A8), Importe in `state.py` (A7), veraltete Kommentare (A9), doppelte und veraltete Tests (A10), Formkurve nutzt die Konstante statt „5“ (A12). Nicht umgesetzt: R9 (`except Exception` um `st.page_link`), weil es sich ohne Streamlit nicht prüfen lässt.
- **Claude** · Prüfung: alle 8'808 Begegnungen und die Häufigkeit vor und nach dem Umbau verglichen, **vollständig identisch** (alle Werte, Texte, ids); Gegenrechnung weiter 0 Abweichungen; Seiten-HTML identisch; 31 neue Tests (`tests/test_h1.py`, Loader, Spielplan), 4 entfernt, lokal 279 bestanden. Protokoll `docs/tests/pruefprotokoll_h1.md`.
- **Claude** · Doku: `03_KPI_Regelwerk.md` v2.2 (Kommazahlen gelten als fehlend), `02_Datenbasis.md` (Prüfregeln), `05_Dashboard.md` v4.7 (6.3, 11), `01_Technisches_Setup.md` (Status, Architektur, Test-Befehl), `CLAUDE.md` v1.7.
- **Carsten** · H.1 eingespielt: Backup `backup/2026-11-08_1042_vor_H1` (Git `51e595b`), 287 Tests bestanden, 1 übersprungen; `/` 200, `/dashboard/` 401; Git `b5a7ea8`.

## 08.11.2026 – Etappe H eingespielt

- **Carsten** · Etappe H eingespielt: 260 Tests bestanden, 1 übersprungen; `/` 200, `/dashboard/` 401; Git `51e595b`. Test-Befehl dabei korrigiert (`tests` am Ende, `SI_DATA_DIR=/src/data`).
- **Claude** · Word-Dokument „KPI-Definitionen“ aus dem Regelwerk neu erzeugt (`Soccer_Intelligence_KPI-Definitionen_2026-11-08.docx` auf Carstens PC, nur Archiv; massgeblich bleibt die md-Datei).

## 08.11.2026 – Neue KPIs 05–13: Spezifikation, Rundgang, Testfälle bestätigt, Freigabe Etappe H

- **Carsten** · Spezifikation „KPI-Regelwerk KPI 05–13, Entwurf“ (Word): 5 Frontend-KPIs (05 Ecken, 06 Tore 1. HZ, 07 Tore 2. HZ, 08 Beide Teams treffen, 09 Schüsse aufs Tor) und 4 Simulations-KPIs nur im Backend (10/11 Angriff gegen Abwehr, 12 Offensivdruck, 13 Abschluss-Effizienz). Ziel: später Schwellen je Liga/KPI schärfen und Ergebniskontrolle („trifft die Anomalie ein?“).
- **Carsten / Claude** · Entscheidungen: Schwellen pro Liga und KPI einstellbar (`schwellen.toml`, Standard ±20/±35 %, kein eigener Tab); kompakte Tabelle mit Details per Aufklappen; einheitlich „Keine statistische Besonderheit“; Datenbasis mit Referenzspielen (KPI 05, 09); KPI 08 relative Abweichung, Text mit Liga-Wert; KPI 10/11 Spielwert = Summe der Richtungen (gleicher Massstab wie Ligareferenz); KPI 12 Ligawert pro Team und Spiel; KPI 13 Eigentore zählen mit.
- **Claude** · Probelauf 2025/26: neue KPIs schlagen mit ±20/±35 % in 14–41 % der Spiele an (KPI 02: 9–15 %), v. a. BTTS und Tore 1. HZ eher zu oft → Klärung im Simulations-Tab. Datenvollständigkeit Ecken/Schüsse aufs Tor: nur die dokumentierten Sonderfälle fehlen.
- **Claude** · `03_KPI_Regelwerk.md` v2.0 (Entwurf): Abschnitte 9 (KPI 05–09) und 10 (KPI 10–13), 2.2 Schwellen-Konfiguration, 2.4 Regel „−0,0 → 0,0“, 2.5 Datenbasis, 2.6 Top-Anomalien, 7 Übersicht, offene Punkte 12–14. `05_Dashboard.md` v4.5 (Entwurf): kompakte Tabelle (4.1), Anzeige der Schwellen (6.3), Bereich Simulation geplant (6.4). `01`: Etappen H und I.
- **Claude** · Testfälle KPI 05–09 (je 9: Standard, Anomalien in allen vier Ligen, Grenzwert genau +20,0 %, Aufsteiger vorläufig, Aufsteiger ohne Spiele, fehlender Wert Union – Bochum, Rundung −0,0) aus einer unabhängigen Berechnung; Excel-Datei zur Nachprüfung mit Formeln (45 von 45 Ergebnissen identisch).
- **Carsten / Claude** · Gemeinsamer Rundgang durch KPI 05–09 (je eine normale Partie und ein Aufsteiger am 1. Spieltag 2026/27). **KPI 05 bestätigt mit Änderung (Carsten):** Nur eigene Ecken zu zählen bevorzugt Top-Teams und verzerrt Spiele zweier starker Teams; ein Abstiegskandidat hat viele Ecken gegen sich. Neu zählen eigene **und** gegnerische Ecken, Hauptwert = Mittelwert (System wie KPI 02). **KPI 09 ebenso umgestellt** (eigene + zugelassene Schüsse aufs Tor). Beispiel Bayern – Stuttgart: KPI 05 bisher 13,2 (+35,4 %, stark), neu 10,8 (+10,3 %, keine).
- **Claude** · Folge der Umstellung: KPI 05 und 09 schlagen mit ±20/±35 % nur noch in 0,5–4 % der Spiele an (vorher 14–32 %); für eine Häufigkeit wie KPI 02 wären etwa ±12/±18 % nötig. **Carsten:** Schwellen werden später bearbeitet (Etappe I).
- **Claude** · `03_KPI_Regelwerk.md`: 9.1 und 9.5 neu (Formel, Begründung, Dashboard-Angaben), Übersicht 7, offener Punkt 12 aktualisiert. Testfälle KPI 05 und 09 neu berechnet; neue Testfälle T10 Bayern – Stuttgart, T11 Elversberg – Leverkusen, T12 Gladbach – Elversberg (KPI 05) sowie T10, T13 West Ham – Wolves (Rundung −0,0, bisher in T9 bei KPI 05) und T14 Paderborn – Freiburg (KPI 09). KPI 06–08: nur Zweck-Spalte von T5 und T9 angepasst, Werte unverändert. Excel-Nachprüfung neu (51 von 51 Ergebnissen identisch).
- **Carsten / Claude** · Rundgang KPI 06 (Newcastle – Liverpool, Hull – Man Utd, Coventry – Hull): Werte bestätigt. Aufsteiger mit 1 Spiel dürfen wie bei KPI 02–04 eine Anomalie zeigen (mit „vorläufig“). **Entscheidung Carsten:** KPI 06 und 07 mit **zwei Nachkommastellen** im Dashboard (Teamwerte, Ligareferenz, Hauptwert, Text); Abweichung weiter eine. Website: später (offener Punkt 15). Spielplan Premier League, 1. Spieltag (16.–20.08. statt gespielt 21.–24.08.): prüft Carsten.
- **Claude** · `03_KPI_Regelwerk.md` 2.3, 9.2, 9.3, Punkt 15; Testfälle KPI 06 und 07 mit zwei Nachkommastellen neu erzeugt, KPI 06 ergänzt um T15–T17; Excel-Nachprüfung neu (54 von 54 identisch).
- **Carsten / Claude** · Rundgang KPI 07 (Torino – AC Milan, Inter – Monza, Monza – Udinese): Werte bestätigt. **Claude** · Testfälle KPI 07 ergänzt um T18–T20; Excel-Nachprüfung neu (57 von 57 identisch).
- **Carsten / Claude** · Rundgang KPI 08 (Real Madrid – Real Sociedad, Atl. Madrid – Malaga, Getafe – Racing): Werte bestätigt. Frage Carsten zur Aussagekraft für Prognosen; Auswertung Claude über 6'182 Spiele: KPI 08 trennt nur um wenige Prozentpunkte (48 % gegen 63 % BTTS), Varianten „Angriff gegen Abwehr“ nicht besser. **Entscheidung Carsten:** KPI 08 bleibt; Prüfung der Varianten in Etappe I (offener Punkt 16); Ergebnisse als Stoff für spätere Blog-Beiträge. **Claude** · Testfälle KPI 08 ergänzt um T21–T22; Excel-Nachprüfung 59 von 59 identisch.
- **Carsten / Claude** · Rundgang KPI 09 (Freiburg – Werder Bremen, Mainz – Paderborn, Paderborn – Freiburg): Werte bestätigt. Frage Carsten, ob eigene Schüsse aussagekräftiger sind; Gegenprobe Claude über 6'689 Spiele: eigene + gegnerische sind für Spiel und Team leicht besser. **Entscheidung Carsten:** KPI 09 bleibt, keine Aufteilung in der Detailansicht. Datenprüfung: 47 von 8'728 Spielen mit mehr Toren als Schüssen aufs Tor (vermutlich Eigentore), kein Datenfehler. **Claude** · Testfälle KPI 09 ergänzt um T23–T24; Excel-Nachprüfung 61 von 61 identisch. Rundgang KPI 05–09 damit abgeschlossen.
- **Carsten** · **Freigabe Etappe H** mit Entscheidungen: (1) **alle KPIs mit zwei Nachkommastellen**, auch die Abweichung, Einstufung nach dem auf zwei Stellen gerundeten Wert (Nachvollziehbarkeit); (2) zuerst überall gleiche Schwellen, danach interner Tab zur Schwellen-Analyse je KPI und Liga und Feintuning; (3) kompaktere Liga-Tabelle; (4) Häufigkeit in Datenqualität wie vorgeschlagen; (5) **Top Anomalien über KPI 02–09** mit der bisherigen Rangfolge, Gewichtung für einen guten Mix je Spieltag später; (6) Tests wie vorgeschlagen; (7) Design-Vorschlag vor der Umsetzung; (8) md-Dateien aktualisieren. Ablauf: md-Dateien → Backup → Design-Vorschlag → Programmieren und Einspielen.
- **Claude** · Probelauf Top Anomalien 2025/26 (vier Ligen): bisherige Regel über KPI 02–09 → KPI 03 39 %, 08 27 %, 06 18 %, 04 10 %, 07 7 %, 02/05/09 nie; Varianten (max. 1 je KPI, Rang nach Seltenheit) als offener Punkt 17 festgehalten.
- **Claude** · Testfälle KPI 02–04 auf zwei Nachkommastellen umgestellt (JSON, Texte, Kontrollpunkte; 24 Testfälle neu nachgerechnet, **keine Einstufung ändert sich**); Testfälle KPI 05–09 neu erzeugt und als bestätigt markiert (T13 West Ham – Wolves zeigt jetzt −0,02 %; den Sonderfall −0,00 gibt es in den echten Daten nicht, er wird im Code mit einem Formattest geprüft). Excel-Nachprüfung mit zwei Nachkommastellen: 61 von 61 identisch.
- **Claude** · `03_KPI_Regelwerk.md` v2.1 (2.1–2.4, 2.6, 7, 8 mit Punkten 6, 9 erledigt und neuem Punkt 17, 9), `05_Dashboard.md` v4.6 (4.1, 5.1, 6.4, 7, 8, 15), `01_Technisches_Setup.md` (Status, Entscheidungen, Etappen H und I), `CLAUDE.md` v1.6.
- **Carsten** · Backup `backup/2026-11-08_0547_vor_Etappe_H` (Git `cc00dd9`). Design-Vorschlag abgenommen; KPI 03 zeigt in der kompakten Zeile die Abweichung zur 2,5-Marke (Prozent statt doppeltem Hauptwert).

## 08.11.2026 – Etappe H: KPI 05–09 (Version 0.9, Paket bereit)

- **Claude** · Rechenkern: KPI 05–09 (`app/core/kpis.py`, ein gemeinsamer Aufbau für alle fünf), zwei Nachkommastellen für alle Werte (auch Abweichung, −0,00 → 0,00), Spiele je Team und Referenzspiele nur noch einmal je Begegnung bestimmt. Neue Schwellen-Datei `app/config/schwellen.toml` mit `app/core/thresholds.py` (Standard ±20/±35 %, Abweichungen je Liga/KPI möglich, Vorrang Liga+KPI > KPI > Liga).
- **Claude** · Oberfläche: kompakte Liga-Tabelle mit Aufklappen (`views/kpi_table.py`, CSS in `components.py`), Top Anomalien über KPI 02–09 (`core/top.py`, bei Gleichstand kleinere KPI-Nummer), Bereich Datenqualität mit gültigen Schwellen und Häufigkeit für KPI 02–09.
- **Claude** · Tests: Testfälle KPI 02–04 mit zwei Nachkommastellen, 61 Testfälle KPI 05–09 (neue Referenz-Datenbank `tests/referenz/…_f37e36d3.xlsx`), Gegenrechnung auf KPI 05–09 erweitert, `test_thresholds.py`, Oberflächentests für die kompakte Tabelle. Lokal 252 bestanden. Vollvergleich aller 8'808 Begegnungen: 0 Abweichungen (`docs/tests/pruefprotokoll_etappe_h.md`).
- **Offen** · Einspielen (Anleitung `ANLEITUNG_ETAPPE_H.md`), Abnahme im Browser, Commit.

## 07.11.2026 – Etappe F: Vier Ligen

- **Carsten** · Etappe F eingespielt (171 Tests bestanden), Git `cc00dd9`.

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
