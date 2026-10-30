# Soccer Intelligence – Datenbasis

**Stand:** 30.10.2026 (Datenbank mit Spalte `Gameday`, 58 Spalten)
**Datei:** `/docker/football-dashboard/data/Database-Soccer-Intelligence.xlsx`
**SHA-256:** `6d68583c2e66616e92c1bf3e8a8611b4b517bcf4c0a7a91c68101ea26a2284e2`

Diese Prüfsumme steht auch in den Testfällen (`docs/tests/`). Nach jeder Änderung an der Datei ändert sie sich. Dann hier und in den Testfällen nachtragen und die Testfälle erneut laufen lassen.

**Server:** Dort liegt vermutlich noch eine ältere Fassung mit 57 Spalten (zuletzt bekannt: SHA-256 `510886ed…`). Vor Etappe A die neue Fassung hochladen, Ablauf gemäss `01_Technisches_Setup.md`, Abschnitt 6. Kontrolle: `sha256sum` muss den Wert oben ergeben.

---

## 1. Überblick

| Tabellenblatt | Spiele | Saisons | Teams | Zeitraum |
|---|---|---|---|---|
| Bundesliga | 1.836 | 2020/21 – 2025/26 (je 306) | 25 | 18.09.2020 – 16.05.2026 |
| Premier League | 2.280 | 2020/21 – 2025/26 (je 380) | 28 | 12.09.2020 – 24.05.2026 |
| Seria A | leer | – | – | vorgesehen |
| LaLiga | leer | – | – | vorgesehen |
| Datenhinweise | 1 Eintrag | – | – | dokumentierte Sonderfälle |

**Leere Liga-Tabellen:** `Seria A` und `LaLiga` sind bewusst leer angelegt und für spätere Ligen vorgesehen. Ein leeres optionales Ligablatt ist **kein Fehler**, es wird nur als Hinweis angezeigt. Ein Fehler liegt nur vor, wenn ein Pflichtblatt (`Bundesliga`, `Premier League`) fehlt oder leer ist.

Die laufende Saison 2026/27 ist noch nicht enthalten (bewusste Entscheidung, siehe 01_Technisches_Setup.md).

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
- Teamnamen: englische Schreibweise der Quelle, z. B. `Bayern Munich`, `B. Monchengladbach`, `FC Koln`. Neue Einträge müssen exakt gleich geschrieben werden.

### Bekannte Eigenheiten

- **Doppelte Torspalten sind beabsichtigt:** Die Spalten K–M (`FT Home Goals`, `FT Away Goals :`, `FT Result :`) und N–P (`Full-Time Home Goals`, `Full-Time Away Goals`, `Full-Time Result`) bilden dasselbe reguläre Endergebnis ab. Das ist kein Datenfehler, an der Excel-Datei ist nichts zu ändern. Die Datenvalidierung darf beide Gruppen miteinander vergleichen (so wurde der Fehler vom 18.10.2025 gefunden). Sie entfernt oder verändert aber nie automatisch Spalten oder Werte.
- Das Blatt heisst `Seria A` (statt „Serie A“), bewusst unverändert gelassen.

---

## 3. Regel für fehlende Werte

> **Leere Zelle = keine Daten. Niemals 0 oder Schätzwerte eintragen.**

- Fehlende Statistikwerte bleiben leer.
- Die App lässt leere Werte bei Durchschnitten weg und zeigt an, auf wie vielen Spielen ein Wert beruht.
- Kein Text wie „n/a“ in Zahlenspalten.
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

## 5. Prüfregeln (werden ab Schritt 1 automatisch angewendet)

### Fehler – Datenbank wird nicht verwendet

- Datei fehlt oder ist nicht lesbar (z. B. Upload unvollständig)
- Pflichtblatt `Bundesliga` oder `Premier League` fehlt oder ist leer
- Spaltenanzahl, Spaltennamen oder Reihenfolge weichen von den 58 Spalten ab
- Pflichtfeld leer (Datum, Gameday, id, Liga, Saison, Teams, Tore, Ergebnisse)
- Text statt Zahl, Ergebnis nicht H/D/A, ungültiges Datum oder Saisonformat
- doppelte id innerhalb eines Blatts

### Warnung – wahrscheinlich ein Datenfehler

- `FT` ≠ `Full-Time`
- 1. HZ + 2. HZ ≠ Endstand (Tore)
- Ergebnisbuchstabe passt nicht zu den Toren
- Halbzeitwerte ergeben nicht den Gesamtwert (Ecken, Karten, Schüsse)
- Ballbesitz Heim + Auswärts ≠ 100 %
- Schüsse gesamt < aufs Tor + daneben
- fehlende Statistik, die nicht in Datenhinweise dokumentiert ist
- Saison unvollständig (n Teams → n × (n−1) Spiele), doppelte Paarung
- `Date` passt nicht zu `matchDate`, negativer Wert
- `Gameday` ausserhalb 1 bis 2 × (Teams − 1), Spieltag mit falscher Anzahl Spiele, Team mehrfach im selben Spieltag

### Hinweis – kein Handlungsbedarf

- mehr Tore als Schüsse aufs Tor (meist Eigentore)
- dokumentierte Sonderfälle mit leeren Statistikwerten
- leere optionale Blätter, neueste Saison noch laufend

### Ergebnis der Prüfung am 30.10.2026 (Fassung mit 58 Spalten, korrigiert)

Geprüft mit dem Code aus Schritt 1 (angepasst an 58 Spalten). Ergebnis unverändert gegenüber dem 25.10.2026:

| Stufe | Anzahl | Details |
|---|---|---|
| Fehler | 0 | – |
| Warnungen | 2 | Bundesliga id 11344: Schüsse gesamt < aufs Tor + daneben (Gesamt und 2. HZ), siehe 5.1 |
| Hinweise | 17 | 14 × mehr Tore als Schüsse aufs Tor (Eigentore), id 14421 Statistik fehlt (dokumentierte Ausnahme, siehe 4.1), Seria A und LaLiga leer |

### 5.1 Offene Auffälligkeit: Spiel-ID 11344

**Bayer Leverkusen – FC Koln, 08.10.2023, Saison 2023/24, Endstand 3:0** (Blatt Bundesliga, Excel-Zeile 980)

| Heim-Schüsse | gesamt | aufs Tor | daneben | aufs Tor + daneben |
|---|---|---|---|---|
| Gesamt | 12 | 6 | 8 | 14 |
| 1. Halbzeit | 7 | 3 | 4 | 7 ✓ |
| 2. Halbzeit | 5 | 3 | 4 | 7 ✗ |

- Die Summe aus „aufs Tor“ und „daneben“ ist in der 2. Halbzeit und damit auch im Gesamtwert höher als die Gesamtzahl der Schüsse. In der Regel kann das nicht sein.
- Mögliche Ursachen: falscher Wert bei „Schüsse gesamt“ in der 2. HZ (dann wäre 7 statt 5 und gesamt 14 statt 12 richtig) oder falsche Werte bei „aufs Tor“ bzw. „daneben“. Das ist nicht geklärt.
- **Status: offen.** Die Daten bleiben unverändert. Die Auffälligkeit wird bis zu einer Entscheidung als Warnung angezeigt. Möglich sind: korrigieren (mit Quelle), im Blatt Datenhinweise dokumentieren oder die Prüfung zum Hinweis herabstufen.

---

## 6. KPI-Definitionen

Die KPIs sind im **KPI-Regelwerk** `03_KPI_Regelwerk.md` festgelegt. Diese Datei beschreibt nur die Datenbasis.

Die Ligareferenz verwendet die Spalte `Gameday` (seit 28.10.2026 vorhanden, siehe Abschnitt 4b).

---

## 7. Spielplan

Die angesetzten Begegnungen stehen in einer eigenen Datei `data/Spielplan.xlsx`. Aufbau, Regeln für den aktuellen Spieltag und Prüfregeln: siehe **`04_Spielplan.md`**.
