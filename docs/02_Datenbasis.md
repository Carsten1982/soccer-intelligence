# Soccer Intelligence – Datenbasis

**Stand:** 15.11.2026 (Datenbank mit Saisons 2018/19–2025/26 plus laufende Saison 2026/27 bis 08.11.2026, bereinigt mit API-Football und football-data.co.uk, Abschnitt 4e; **Referenzsaison** 2018/19; vier Ligen: Bundesliga, Premier League, Serie A, LaLiga; je 58 Spalten inkl. `Gameday`)
**Datei:** `/docker/football-dashboard/data/Database-Soccer-Intelligence.xlsx`
**SHA-256 (aktiv seit 31.10.2026):** `6b84d8d230f61b02166bead571a72ce599ec8d230cdda8c90f9b258dc8a46014`

**Referenzstand für die KPI-Testfälle:** `6d68583c2e66616e92c1bf3e8a8611b4b517bcf4c0a7a91c68101ea26a2284e2` (Saisons 2020/21–2025/26). Eine Kopie liegt unter `tests/referenz/`, damit die Testfälle unabhängig vom aktuellen Datenstand laufen.

Diese Prüfsumme steht auch in den Testfällen (`docs/tests/`). Nach jeder Änderung an der Datei ändert sie sich. Dann hier und in den Testfällen nachtragen und die Testfälle erneut laufen lassen.

**Bereinigte Fassung (15.11.2026):** 1'932 Zellen korrigiert, wo API-Football und football-data.co.uk übereinstimmen und nur der Altbestand abweicht, dazu offizielle Spieltage (Abschnitt 4e). SHA-256 `3a2589616b2b0625d3a9150484bd0ce24e6340b334756b115d0d4582925822a8`. Prüfung: 0 Fehler, 35 Warnungen, 201 Hinweise. **Aktiv in `data/` seit 15.11.2026** (Prüfung auf dem Server: 0 Fehler, 35 Warnungen, 201 Hinweise; vorherige Fassung `451348b6…` in `backup/Database-Soccer-Intelligence_2026-11-15_vor_Bereinigung.xlsx`). Die KPI-Testfälle bleiben an ihre Referenzkopien gebunden.

**Neue Fassung (10.11.2026, Version 0.11):** Saisons 2018/19 und 2019/20 ergänzt, Spiele 2026/27 bis 10.11.2026 nachgetragen, geprüft und korrigiert (Abschnitt 4d). SHA-256 `451348b6550b91f4df3a26450a26d205e76f69c13ac520d080d3a427ff084904`. Eine Kopie liegt unter `tests/referenz/Database-Soccer-Intelligence_451348b6.xlsx`. **Aktiv in `data/` seit 10.11.2026** (nach dem Einspielen von Version 0.11 von Carsten aufgespielt; Prüfung auf dem Server: 0 Fehler, 24 Warnungen, 64 Hinweise; vorherige Datei in `backup/`). Die KPI-Testfälle bleiben an `6d68583c…` und `f37e36d3…` gebunden.

**Referenzsaison (ab Version 0.11):** Die älteste Saison der Datei (heute 2018/19) liefert nur die Vorsaison für die Saison danach und wird nie ausgewertet (KPI-Regelwerk 1.2). Beim Saisonwechsel wird die älteste Saison aus der Datei entfernt.

**Fassung 07.11.2026:** Serie A und LaLiga befüllt (siehe Abschnitt 4c). Aktive Fassung seit 07.11.2026: SHA-256 `f37e36d301767321575aeadf908c39e288b9a655d02d85d5bcfde0507effdc34` (LaLiga 17.05.2026 korrigiert, *Datenhinweise* ergänzt). Vorstufe `c0454c7f…` liegt in `backup/`. Bundesliga und Premier League sind gegenüber `6b84d8d2…` unverändert.

**Bisher:** Die Fassung `6b84d8d2…` war seit 31.10.2026 in `data/` aktiv. Gegenüber dem Referenzstand neu: die 19 Spiele des 1. Spieltags 2026/27 (Bundesliga 9, Premier League 10). Beim Prüfen korrigiert: id 119365 (FC Koln – Heidenheim) `Home Yellow Cards Full Time` enthielt Leerzeichen statt 2. Ältere Fassungen liegen in `backup/`.

---

## 1. Überblick

| Tabellenblatt | Spiele | Saisons | Teams | Zeitraum |
|---|---|---|---|---|
Stand 10.11.2026 (Saisons 2018/19–2025/26 vollständig, dazu die bis 10.11.2026 gespielten Spiele 2026/27):

| Tabellenblatt | Spiele | davon 2026/27 | Saisons | Teams | Zeitraum |
|---|---|---|---|---|---|
| Bundesliga | 2.529 | 81 (Spieltage 1–9) | 2018/19 – 2025/26 je 306 | 30 | 24.08.2018 – 08.11.2026 |
| Premier League | 3.140 | 100 (Spieltage 1–10) | 2018/19 – 2025/26 je 380 | 32 | 10.08.2018 – 08.11.2026 |
| Serie A | 3.150 | 110 (Spieltage 1–11) | 2018/19 – 2025/26 je 380 | 32 | 18.08.2018 – 08.11.2026 |
| LaLiga | 3.159 | 119 (Spieltage 1–12, eines nachzuholen) | 2018/19 – 2025/26 je 380 | 31 | 17.08.2018 – 08.11.2026 |
| Datenhinweise | 9 Einträge | – | – | – | dokumentierte Sonderfälle und Korrekturen |

Zusammen 11.978 Spiele. Referenzsaison 2018/19 (nur Vorsaison), ausgewertet 2019/20–2026/27 (KPI-Regelwerk 1.2).

Bis 09.11.2026 (Fassung `f37e36d3…`): Saisons 2020/21–2025/26, 2026/27 nur Spieltag 1 (LaLiga 1–3), zusammen 8.730 Spiele.

**Vier Ligen (Entscheidung 06./07.11.2026):** Das Dashboard zeigt seit Etappe F (Version 0.8) alle vier Ligen (`01_Technisches_Setup.md`).

**Pflichtblätter (seit Etappe F):** `Bundesliga`, `Premier League`, `Serie A` und `LaLiga`. Fehlt eines oder ist es leer, ist das ein **Fehler** (Datenbank wird nicht verwendet). Weitere Blätter werden ignoriert (Hinweis). Eine neue Liga kann im Code als optionales Blatt vorbereitet werden, bevor sie aktiv geschaltet wird.

Die laufende Saison 2026/27 wird spieltagweise ergänzt (seit 31.10.2026, zuerst Spieltag 1).

**Herkunft der Daten:** Der Name des bisherigen Anbieters ist noch nicht dokumentiert (wird ermittelt). Eine regelmässige Lieferung durch einen Datenlieferanten wird geprüft: `06_Datenlieferung.md`.

---

## 2. Spaltenaufbau (58 Spalten, in beiden Ligen identisch)

| Spalten | Inhalt | Pflicht? |
|---|---|---|
| A | `Date` | ja |
| B | `Gameday` (Spieltagsnummer, neu seit 28.10.2026) | ja |
| C – I | `id`, `matchDate`, `Country`, `League`, `Season`, `homeTeam`, `awayTeam` | ja |
| J | `referee` | nein |
| K – M | `FT Home Goals`, `FT Away Goals :`, `FT Result :` | ja |
| N – P | `Full-Time Home Goals`, `Full-Time Away Goals`, `Full-Time Result` | ja |
| Q – S | `First-Half Home Goals`, `First-Half Away Goals`, `First-Half Result` | ja |
| T – V | `Second-Half Home Goals`, `Second-Half Away Goals`, `Second-Half Result` | ja |
| W – AB | Ecken (Heim/Auswärts × Gesamt, 1. HZ, 2. HZ) | nein |
| AC – AH | Gelbe Karten (Heim/Auswärts × Gesamt, 1. HZ, 2. HZ); **AC** = `Home Yellow Cards Full Time`, **AD** = `Away Yellow Cards Full Time` (KPI 04) | nein |
| AI – AN | Ballbesitz in % (Heim/Auswärts × Gesamt, 1. HZ, 2. HZ) | nein |
| AO – AT | Schüsse gesamt (Heim/Auswärts × Gesamt, 1. HZ, 2. HZ) | nein |
| AU – AZ | Schüsse aufs Tor (Heim/Auswärts × Gesamt, 1. HZ, 2. HZ) | nein |
| BA – BF | Schüsse daneben (Heim/Auswärts × Gesamt, 1. HZ, 2. HZ) | nein |

### Formate

- `Date`: Datum (ohne Uhrzeit)
- `Gameday`: ganze Zahl, Bundesliga 1–34, Premier League 1–38. Ein **Nachholspiel** behält die Nummer seines ursprünglichen Spieltags (Beispiel: Premier League id 14680, Everton – Liverpool, Spieltag 15 der Saison 2024/25, gespielt am 12.02.2025). Grundlage der Ligareferenz (KPI-Regelwerk, Abschnitt 1.1).
- `matchDate`: Text im Format `TT-MM-JJ HH:MM`, z. B. `14-12-24 15:30`
- `Season`: `JJJJ/JJJJ`, z. B. `2024/2025`
- Ergebnisse: `H` = Heimsieg, `D` = Unentschieden, `A` = Auswärtssieg
- `id`: eindeutig innerhalb eines Blatts (zwischen den Ligen können sich Nummern wiederholen)
- Teamnamen: englische Schreibweise der Quelle, z. B. `Bayern Munich`, `B. Monchengladbach`, `FC Koln`. Neue Einträge müssen exakt gleich geschrieben werden. **Seit Version 0.14** stellt der erste übernommene Import alle Spiele auf die Namen von API-Football um (je Team-ID fest in `app/config/teamnamen.toml`, Entscheidung Carsten 15.11.2026).
- **Neue Spiele ab dem Datenimport** (Version 0.14) haben als `id` die Spiel-ID von API-Football (über 1'000'000); bisherige Spiele behalten ihre `id` und werden vom Import nie verändert.

### Bekannte Eigenheiten

- **Doppelte Torspalten sind beabsichtigt:** Die Spalten K–M (`FT Home Goals`, `FT Away Goals :`, `FT Result :`) und N–P (`Full-Time Home Goals`, `Full-Time Away Goals`, `Full-Time Result`) bilden dasselbe reguläre Endergebnis ab. Das ist kein Datenfehler, an der Excel-Datei ist nichts zu ändern. Die Datenvalidierung darf beide Gruppen miteinander vergleichen (so wurde der Fehler vom 18.10.2025 gefunden). Sie entfernt oder verändert aber nie automatisch Spalten oder Werte.
- Das Blatt für Italien hiess bis 06.11.2026 `Seria A`. Carsten hat es in Datenbank und Spielplan in **`Serie A`** umbenannt (07.11.2026). Der Code erwartet seit Etappe F `Serie A`; ein Blatt `Seria A` wird ignoriert und `Serie A` gilt dann als fehlend (Fehler). Die Spalte `League` enthält `Serie A` bzw. `LaLiga` und passt damit zum Blattnamen.

---

## 3. Regel für fehlende Werte

> **Leere Zelle = keine Daten. Niemals 0 oder Schätzwerte eintragen.**

- Fehlende Statistikwerte bleiben leer.
- Die App lässt leere Werte bei Durchschnitten weg und zeigt an, auf wie vielen Spielen ein Wert beruht.
- Kein Text wie „n/a“ in Zahlenspalten.
- Anzahlen (Tore, Ecken, Karten, Schüsse) sind ganze Zahlen. Steht bei Ecken, Karten oder Schüssen eine Kommazahl, behandelt die App den Wert wie eine leere Zelle und meldet eine Warnung (seit H.1).
- Jeder Sonderfall wird im Blatt **Datenhinweise** dokumentiert.

### Blatt „Datenhinweise“

| Spalte | Inhalt |
|---|---|
| Liga | Blattname, z. B. `Bundesliga` |
| id | Spiel-ID |
| Datum | Spieldatum |
| Begegnung | z. B. `Union Berlin - Bochum` |
| Art | z. B. `Nachtrag / Sonderfall` |
| Hinweis | Beschreibung |
| Geändert am | Datum der Änderung |
| Quelle | woher die Information stammt |

---

## 4. Korrekturen am 25.10.2026

### 4.1 Bundesliga – fehlendes Spiel nachgetragen

- **Problem:** Saison 2024/25 hatte 305 statt 306 Spiele.
- **Ursache:** Union Berlin – Bochum (14.12.2024, 14. Spieltag) fehlte. Das Spiel wurde nach einem Feuerzeugwurf gegen Bochums Torwart Drewes vom DFB-Sportgericht mit 2:0 für Bochum gewertet; vermutlich hatte die Datenquelle deshalb keine Statistiken.
- **Korrektur:** neue Zeile 1344, id 14421 (Lücke in der id-Folge).
  - Ergebnis **auf dem Platz** eingetragen: 1:1 (HZ 1:1, Sissoko 23., Hollerbach 33.), Schiedsrichter Martin Petersen.
  - Nicht die Wertung 2:0, weil für Analysen das Spielgeschehen zählt.
  - Alle 36 Statistikspalten **leer**.
  - Kommentar an der id-Zelle + Eintrag im Blatt Datenhinweise.
- **Achtung für Analysen:** Bochum ab der 12. Minute in Unterzahl (Rot Miyoshi); die 2. Halbzeit wurde nach der Unterbrechung nicht regulär gespielt.

### 4.2 Premier League – Torspalten vertauscht

- **Problem:** Bei den fünf 16-Uhr-Spielen vom 18.10.2025 (ids 67158–67162) waren die Spalten `Full-Time`, `First-Half` und `Second-Half` (damals M–U, heute N–V) zwischen den Spielen vertauscht. Die `FT`-Spalten und alle Statistiken waren korrekt.
- **Korrektur:** 24 Zellen, mit Spielberichten abgeglichen.

| id | Spiel | Endstand | 1. HZ | 2. HZ |
|---|---|---|---|---|
| 67158 | Brighton – Newcastle | 2:1 H | 1:0 H | 1:1 D |
| 67159 | Burnley – Leeds | 2:0 H | 1:0 H | 1:0 H |
| 67160 | Crystal Palace – Bournemouth | 3:3 D | 0:2 A | 3:1 H |
| 67161 | Man City – Everton | 2:0 H | 0:0 D | 2:0 H |
| 67162 | Sunderland – Wolves | 2:0 H | 1:0 H | 1:0 H |

- Kein Eintrag in Datenhinweise, da die Daten jetzt vollständig korrekt sind.
- Lehre: Der Fehler bei Man City – Everton (Halbzeit 1:0 statt 0:0) war in sich stimmig und daher durch Prüfregeln nicht erkennbar. Beim Einfügen neuer Daten immer ganze Zeilen kopieren, nie einzelne Spaltenblöcke.

---

## 4b. Änderungen am 28. und 30.10.2026

### Neue Spalte `Gameday` (ergänzt bis 28.10.2026)

- Spalte B, Spieltagsnummer jedes Spiels. Grund: Das KPI-Regelwerk bestimmt die Ligareferenz über die letzten 20 Spieltage.
- Geprüft am 30.10.2026: alle 4.116 Spiele befüllt; jede Saison hat 34 bzw. 38 Spieltage mit je 9 bzw. 10 Spielen; kein Team kommt in einem Spieltag doppelt vor.
- Die Korrekturen vom 25.10.2026 (Abschnitt 4) sind in der neuen Fassung vollständig enthalten (mit der alten Fassung abgeglichen: ausser `Gameday` keine Unterschiede).

### Korrektur von zwei überschriebenen Zellen (Claude, 30.10.2026)

In der hochgeladenen Fassung stand in zwei Zellen Text statt einer Zahl, vermutlich versehentlich eingetragene Notizen:

| Blatt | id | Spiel | Spalte | stand da | korrigiert auf | Begründung |
|---|---|---|---|---|---|---|
| Premier League | 5393 | Newcastle – Burnley, 03.10.2020 | `Gameday` | „bitte“ | **4** | Spieltag 4 hatte sonst nur 9 Spiele; alle anderen Spiele dieses Wochenendes haben Spieltag 4 |
| Premier League | 99466 | Newcastle – Manchester Utd, 04.03.2026 | `FT Home Goals` | „Ergebnisse stimmen.“ | **2** | Wert der alten Fassung und identisch mit `Full-Time Home Goals` |

- Beide Fehler hätte die Prüfung ab Schritt 1 als **Fehler** gemeldet („Text statt Zahl“) und die Datenbank gesperrt.
- id 99466 (Spieltag 29 der Saison 2025/26) liegt in der Ligareferenz der Testfälle für den 1. Spieltag 2026/27 und gehört zu den letzten 10 Spielen von Newcastle (Testfall PL-1) und Manchester Utd (PL-2). Mit dem Text in der Zelle hätten KPI 02 und 03 dort nicht gerechnet werden können. Die Testfälle wurden mit dem korrekten Wert 2 berechnet.
- Lehre: Notizen nie in Datenzellen schreiben, sondern als Excel-Kommentar oder im Blatt Datenhinweise.

---

## 4c. Serie A und LaLiga befüllt (04.–07.11.2026)

Carsten hat die Spiele von Serie A und LaLiga in die Datei übernommen. Claude hat ergänzt bzw. bereinigt (Protokoll: `Spieltage_pruefen.xlsx`, Blatt *Änderungsprotokoll*, bei Carsten):

- **Spalte A `Date`:** aus Spalte D `matchDate` übernommen (nur das Datum), Format `DD.MM.YYYY`.
- **Spalte B `Gameday`:** berechnet, weil die Quelle keine Spieltage enthält (Ausnahme: 2026/27, von Carsten eingetragen). Methode: Jedes Team spielt genau einmal pro Spieltag; jedes Spiel kommt in den Spieltag, dessen typisches Datum am nächsten liegt (Optimierung über die ganze Saison). Verlegte Spiele landen so in ihrem ursprünglichen Spieltag.
  - Test an Carstens eigenen Spieltagen: Bundesliga 100 %, Premier League in normalen Saisons 100 %, in gestörten Saisons (Corona, ganze Spieltage verlegt) deutlich schlechter.
  - Serie A und LaLiga: alle Spieltage mit genau 10 Spielen, jedes Team einmal; keine Anzeichen für ganze verlegte Spieltage. Geschätzte Genauigkeit 98–99 %, **nicht** gegen eine offizielle Quelle geprüft. Offizielle Werte (z. B. vom Datenlieferanten) ersetzen die berechneten.
  - Für die KPIs ist die Wirkung gering: Ein falsch zugeordnetes, verlegtes Spiel verschiebt die Ligareferenz um höchstens ein Spiel.
- **Leere Zusatzspalten** rechts von Spalte 58 entfernt (Serie A 2, LaLiga 1).
- **Gelöscht:** Serie A, 10 Spiele der Saison 2019/20 (ids 9200–9209, nur letzter Spieltag vorhanden) und das Entscheidungsspiel um den Klassenerhalt Spezia – Verona vom 11.06.2023 (id 8059, kein Ligaspieltag). Entscheidung Carsten.
- **Nachgetragen:** Serie A, Verona – AS Roma, 19.09.2020, Spieltag 1, id 9198 (freie Nummer im 1. Spieltag). Ergebnis auf dem Platz 0:0 (HZ 0:0), gewertet 3:0 für Verona (Fall Diawara). Schiedsrichter und Statistiken leer; dokumentiert im Blatt *Datenhinweise*.

**Offen:**

- ~~LaLiga, 17.05.2026: 7 Spiele mit vertauschten Werten in K–M~~ **korrigiert 07.11.2026:** K–M aus N–P übernommen (stimmt mit den Halbzeiten überein), je Spiel im Blatt *Datenhinweise* dokumentiert. Prüfung aller 8'730 Spiele: sonst keine Abweichung zwischen K–M und N–P. Vermutlich Fehler der ursprünglichen Quelle.
- ~~*Datenhinweise* id 9198 `Seria A`~~ **korrigiert 07.11.2026** (`Serie A`).
- ~~Weitere Warnungen ohne Eile: „Schüsse < aufs Tor + daneben“ (Serie A 2, LaLiga 1).~~ **Seit 0.19.1 nur Hinweis** (Abschnitt 5).

---

## 4d. Neue Datenbank: 2018/19, 2019/20 und 2026/27 bis 10.11.2026 (Version 0.11)

Carsten hat in allen vier Ligen die Saisons 2018/19 und 2019/20 ergänzt und die Spiele 2026/27 bis 10.11.2026 nachgetragen. Claude hat die Datei am 10.11.2026 geprüft und eine korrigierte Fassung erstellt. Die Eingangsdatei blieb unverändert; jede Änderung ist protokolliert (Prüfprotokoll `docs/tests/pruefprotokoll_datenbank_2018-2027.md`).

- **Eingangsdatei** (SHA-256 `a54a9137…`): nicht verwendbar, 868 Fehler (fehlendes Datum und fehlender Spieltag in den neuen Zeilen, „Wert“ statt Zahl).
- **Bundesliga, Spalten N–BF verrutscht (repariert):** Ab 2020/21 passten Full-Time-Tore, Halbzeiten und alle Statistiken nicht mehr zum Spiel in A–M (vermutlich wurden beim Einfügen nur in A–M Zeilen eingeschoben). 2020/21–2025/26 (1.836 Spiele) aus der Fassung `f37e36d3…` übernommen, 2026/27 (81 Spiele) aus der verschobenen Stelle derselben Datei; je Spiel geprüft: Tore K/L = Full-Time = Halbzeit 1 + 2. Stichproben von Carsten mit der Quelle: 25 Spiele Premier League 2021/22 (300 Werte) und 100 Spiele Bundesliga 2022/23 (1.300 Werte), alle gleich.
- **LaLiga id 77856** (Girona – Osasuna, 10.01.2026): „Wert“ in Spalte L durch 0 ersetzt (wie in `f37e36d3…`).
- **Spalte A `Date`:** aus `matchDate` ergänzt (in allen bisherigen Zeilen ist A genau dieses Datum).
- **Spalte B `Gameday`:** rekonstruiert (jedes Team einmal je Spieltag, jedes Spiel in den Spieltag, dessen Termin am nächsten liegt; Nachholspiele in den Spieltag, in dem beide Teams frei sind). Test an den Saisons mit bekanntem Spieltag: Bundesliga und LaLiga 100 %, Serie A 98,9–100 %, Premier League 40–100 % (dort werden Spieltage teils in anderer Reihenfolge gespielt). Alle bekannten Spieltage 2026/27 getroffen.
  - **Premier League 2018/19 und 2019/20: Spieltage rekonstruiert, nicht offiziell.** Einzelne Nummern können abweichen. Entscheidung Carsten 10.11.2026: so übernehmen, weil die Quelle keine offiziellen Spieltage liefert. Wirkung nur am Rand des Fensters der Ligareferenz (letzte 20 Spieltage); 2018/19 dient nur als Referenzsaison.
- **Corona-Saisons** 2019/20 und 2020/21 zählen normal mit (Entscheidung Carsten 10.11.2026).
- **Ergebnis der Prüfung (korrigierte Fassung `451348b6…`):** 0 Fehler, 24 Warnungen, 64 Hinweise. Neu gegenüber `f37e36d3…`: 18 Warnungen „Schüsse < aufs Tor + daneben“ (2018/19: Bundesliga 12, Premier League 4, LaLiga 2; Quelle), 1 Warnung LaLiga 2026/27 Spieltag 8 mit 9 von 10 Spielen (echtes Nachholspiel), 3 Hinweise „Mehr Tore als Schüsse aufs Tor“ (2019/20) und 1 (2026/27). Saisons 2020/21–2025/26 zellgenau gleich wie `f37e36d3…`. Neue Saisons vollständig (306 bzw. 380 Spiele, jede Paarung einmal, jedes Team einmal je Spieltag, keine fehlenden Statistikwerte), Durchschnittswerte plausibel.

## 4e. Bereinigung mit API-Football und football-data.co.uk (15.11.2026)

Vollvergleich aller 11'568 Spiele 2018/19–2025/26 mit API-Football und einer unabhängigen dritten Quelle
(football-data.co.uk); Ergebnisse und Zahlen: `docs/tests/pruefprotokoll_api.md`. Entscheidung Carsten 15.11.2026:
**Altbestand bleibt die Grundlage**; korrigiert wird nur, wo API-Football und football-data.co.uk übereinstimmen und
nur der Altbestand abweicht.

- **Gelbe Karten** 453, **Schüsse gesamt** 147, **Schüsse aufs Tor** 83, **Ecken** 35 Werte korrigiert (je Gesamtwert
  eines Teams). Halbzeitwerte: bleiben, wenn sie zum neuen Gesamtwert passen; sonst von der API (Karten aus den
  Spielereignissen, sonst Halbzeit-Statistik ab 2024); sonst leer (= keine Daten) und im Blatt *Datenhinweise*
  dokumentiert (364 Zellen).
- **LaLiga 2025/26, Spieltag 37 (17.05.2026):** Tore (Endstand und Halbzeit) waren zwischen den Spielen vertauscht, auch
  in N–P; die Korrektur vom 07.11.2026 (Abschnitt 4c) hatte die vertauschten Werte übernommen. Jetzt nach API-Football,
  bestätigt durch football-data.co.uk; die Statistiken waren richtig.
- **Spieltag:** 76 rekonstruierte Spieltage durch die offiziellen ersetzt (Premier League 2018/19, Serie A 2019/20,
  LaLiga 2020/21 und 2025/26).
- **Unverändert:** Ergebnis auf dem Platz bei Verona – Roma (Abschnitt 4c) und Union Berlin – Bochum (4.1); Saison
  2026/27; Teamnamen (die Namen von API-Football kommen erst mit dem automatischen Spielplan, `06`, Abschnitt 7).
- **Bekannt:** Schüsse aufs Tor weichen bei API-Football in Serie A 2018/19–2020/21 und Bundesliga 2019/20–2023/24 oft
  ab; dort bleibt der Altbestand (stimmt mit der dritten Quelle überein). 11 neue Warnungen „Schüsse < aufs Tor +
  daneben“: „Schüsse daneben“ im Altbestand vermutlich falsch, nicht prüfbar, unverändert.

---

## 5. Prüfregeln (werden ab Schritt 1 automatisch angewendet)

### Fehler – Datenbank wird nicht verwendet

- Datei fehlt oder ist nicht lesbar (z. B. Upload unvollständig)
- Pflichtblatt `Bundesliga`, `Premier League`, `Serie A` oder `LaLiga` fehlt oder ist leer (seit Etappe F alle vier)
- Spaltenanzahl, Spaltennamen oder Reihenfolge weichen von den 58 Spalten ab
- Pflichtfeld leer (Datum, Gameday, id, Liga, Saison, Teams, Tore, Ergebnisse)
- Text statt Zahl, Ergebnis nicht H/D/A, ungültiges Datum oder Saisonformat. Auch eine **Zahl in der Spalte `Date`** (z. B. 45800, wenn die Zelle nicht als Datum formatiert ist) gilt als ungültiges Datum (seit H.2), statt still als 01.01.1970 gelesen zu werden.
- Kommazahl bei Toren, `Gameday` oder `id` (nur ganze Zahlen erlaubt; seit H.1, 08.11.2026)
- doppelte id innerhalb eines Blatts
- **negativer Wert bei Toren, `Gameday` oder `id`** (seit 0.15.1, Code-Prüfung 16.11.2026, Entscheidung Carsten; vorher nur Warnung)

### Warnung – wahrscheinlich ein Datenfehler

- `FT` ≠ `Full-Time`
- 1. HZ + 2. HZ ≠ Endstand (Tore)
- Ergebnisbuchstabe passt nicht zu den Toren
- Halbzeitwerte ergeben nicht den Gesamtwert (Ecken, Karten, Schüsse)
- Ballbesitz Heim + Auswärts ≠ 100 %
- Kommazahl bei Ecken, Karten oder Schüssen (seit H.1): Der Wert gilt als **fehlend** – er wird nie abgeschnitten und nie als 0 gerechnet. Der Ballbesitz (in %) darf Kommastellen haben.
- Datenhinweis mit einer id, die keine ganze Zahl ist (z. B. 123,5): Er gilt für **kein** Spiel, auch nicht für 123 (seit H.2).
- fehlende Statistik, die nicht in Datenhinweise dokumentiert ist (je Stufe höchstens 50 Einzelmeldungen, danach eine Sammelzeile „… und n weitere Zeilen“)
- Saison unvollständig (n Teams → n × (n−1) Spiele), doppelte Paarung
- **Saison fehlt** zwischen zwei vorhandenen Saisons (seit Version 0.11): Die Saison danach wird ohne Vorsaison berechnet (Teamwerte zu Saisonbeginn, Ligareferenz über das Saisonende) und trotzdem ausgewertet
- `Date` passt nicht zu `matchDate`
- **negativer Statistikwert** (Ecken, Karten, Schüsse, Ballbesitz; seit 0.15.1): Der Wert gilt als **fehlend** und geht nicht in die KPIs ein – wie eine Kommazahl, nie als 0. Stand 16.11.2026: kein einziger negativer Wert in der Datenbank.
- `Gameday` ausserhalb 1 bis 2 × (Teams − 1), Spieltag mit falscher Anzahl Spiele, Team mehrfach im selben Spieltag

**Zusätzlich beim Datenimport** (seit Version 0.15, `06_Datenlieferung.md`, Abschnitt 10.1): id über **alle** Ligen
eindeutig (Fehler); Plausibilität neuer und geänderter Spiele (Fehler: negative Werte, Halbzeit-Tore grösser als
Endstand, Schüsse aufs Tor grösser als Schüsse gesamt; Warnung: je Team mehr als 30 Ecken, 10 Gelbe, 25 Schüsse aufs
Tor, 9 Tore); Endstand gegen Tor-Ereignisse. Für den Altbestand gelten weiter nur die Regeln dieses Abschnitts.

### Hinweis – kein Handlungsbedarf

- mehr Tore als Schüsse aufs Tor (meist Eigentore)
- Schüsse gesamt < aufs Tor + daneben (seit 0.19.1 Hinweis statt Warnung, Entscheidung Carsten 18.11.2026: kommt in der Quelle vor, z. B. id 11344 in 5.1, und geht in keinen KPI ein; KPI 09 nutzt nur „aufs Tor“)
- dokumentierte Sonderfälle mit leeren Statistikwerten
- leere optionale Blätter, neueste Saison noch laufend

### Ergebnis der Prüfung am 30.10.2026 (Fassung mit 58 Spalten, korrigiert)

Geprüft mit dem Code aus Schritt 1 (angepasst an 58 Spalten). Ergebnis unverändert gegenüber dem 25.10.2026:

| Stufe | Anzahl | Details |
|---|---|---|
| Fehler | 0 | – |
| Warnungen | 2 | Bundesliga id 11344: Schüsse gesamt < aufs Tor + daneben (Gesamt und 2. HZ), siehe 5.1 |
| Hinweise | 17 | 14 × mehr Tore als Schüsse aufs Tor (Eigentore), id 14421 Statistik fehlt (dokumentierte Ausnahme, siehe 4.1), Seria A und LaLiga leer |

### 5.1 Auffälligkeit Spiel-ID 11344 (erledigt 0.19.1)

**Bayer Leverkusen – FC Koln, 08.10.2023, Saison 2023/24, Endstand 3:0** (Blatt Bundesliga, Excel-Zeile 980)

| Heim-Schüsse | gesamt | aufs Tor | daneben | aufs Tor + daneben |
|---|---|---|---|---|
| Gesamt | 12 | 6 | 8 | 14 |
| 1. Halbzeit | 7 | 3 | 4 | 7 ✓ |
| 2. Halbzeit | 5 | 3 | 4 | 7 ✗ |

- Die Summe aus „aufs Tor“ und „daneben“ ist in der 2. Halbzeit und damit auch im Gesamtwert höher als die Gesamtzahl der Schüsse. In der Regel kann das nicht sein.
- Mögliche Ursachen: falscher Wert bei „Schüsse gesamt“ in der 2. HZ (dann wäre 7 statt 5 und gesamt 14 statt 12 richtig) oder falsche Werte bei „aufs Tor“ bzw. „daneben“. Das ist nicht geklärt.
- **Status: erledigt 18.11.2026 (Version 0.19.1, Carsten):** Die Prüfung ist zum **Hinweis** herabgestuft. Die Daten bleiben unverändert; der Wert geht in keinen KPI ein (KPI 09 nutzt nur „aufs Tor“).

---

## 6. KPI-Definitionen

Die KPIs sind im **KPI-Regelwerk** `03_KPI_Regelwerk.md` festgelegt. Diese Datei beschreibt nur die Datenbasis.

Die Ligareferenz verwendet die Spalte `Gameday` (seit 28.10.2026 vorhanden, siehe Abschnitt 4b).

---

## 7. Spielplan

Die angesetzten Begegnungen stehen in einer eigenen Datei `data/Spielplan.xlsx`. Aufbau, Regeln für den aktuellen Spieltag und Prüfregeln: siehe **`04_Spielplan.md`**.
