# Soccer Intelligence – Spielplan

**Stand:** 31.10.2026 · **Status:** Datei seit 31.10.2026 auf dem Server (`data/Spielplan.xlsx`). Einlesen und Prüfen ab Etappe B.
**Datei:** `/docker/football-dashboard/data/Spielplan.xlsx`

---

## 1. Zweck und Abgrenzung

| Datei | Inhalt | Wofür |
|---|---|---|
| `Database-Soccer-Intelligence.xlsx` | **gespielte** Spiele mit Ergebnissen und Statistiken | Berechnung der KPIs |
| `Spielplan.xlsx` | **angesetzte** Begegnungen (ohne Ergebnisse) | Welche Spiele das Dashboard anzeigt |

- Der Spielplan bestimmt, welcher Spieltag im Dashboard angezeigt wird und welche Begegnungen darin stehen.
- Ergebnisse werden **nie** im Spielplan eingetragen. Nach dem Spiel kommt das Ergebnis wie bisher in die Datenbank.
- Einträge im Spielplan werden nach dem Spiel nicht gelöscht. Sie bleiben als Verlauf stehen.

---

## 2. Aufbau der Datei

### Tabellenblätter

- Ein Tabellenblatt pro Liga.
- Der Blattname muss **exakt** dem Blattnamen in der Datenbank entsprechen: `Bundesliga`, `Premier League`, später z. B. `LaLiga`.
- Leere Blätter für noch nicht aktive Ligen sind erlaubt.

### Spalten (erste Zeile = Spaltenüberschriften, genau so geschrieben)

| Spalte | Pflicht | Format | Beispiel | Regel |
|---|---|---|---|---|
| `Saison` | ja | Text `JJJJ/JJJJ` | `2026/2027` | gleiches Format wie in der Datenbank |
| `Spieltag` | ja | ganze Zahl ab 1 | `1` | |
| `Datum von` | ja | Excel-Datum | `28.08.2026` | frühester möglicher Spieltag des Spiels |
| `Datum bis` | ja | Excel-Datum | `30.08.2026` | spätester möglicher Spieltag; bei bekanntem Termin = `Datum von` |
| `Heimmannschaft` | ja | Text | `FC Koln` | Schreibweise exakt wie in der Datenbank |
| `Gastmannschaft` | ja | Text | `Hoffenheim` | Schreibweise exakt wie in der Datenbank |
| `Status` | nein | Text | `verschoben` | leer = geplant; erlaubt: `geplant`, `verschoben`, `abgesagt` |

- Eine Anstosszeit ist nicht nötig und wird nicht angezeigt.
- Weitere Spalten werden ignoriert.

### Warum „Datum von“ und „Datum bis“?

Zu Saisonbeginn steht oft nur der Zeitraum eines Spieltags fest, nicht der genaue Tag jedes Spiels. Deshalb gibt es zwei Spalten:

- **Genauer Termin unbekannt:** Zeitraum des Spieltags eintragen (für alle Spiele des Spieltags gleich).
- **Genauer Termin bekannt:** `Datum von` = `Datum bis` = Spieltag des Spiels. Kann jederzeit nachgepflegt werden.

So rechnet das Programm damit:

- **Stichtag für die KPIs ist `Datum von`** (2-Tage-Regel im KPI-Regelwerk, `03_KPI_Regelwerk.md`, Abschnitt 1). Damit fliessen nie Daten aus der Zukunft ein.
- **Ein Spieltag ist beendet**, wenn das späteste `Datum bis` seiner Spiele vor dem heutigen Datum liegt.
- Beide Spalten müssen echte Excel-Datumswerte sein, kein Text wie „28.08-30.08“.

### Beispiel (Blatt `Bundesliga`)

| Saison | Spieltag | Datum von | Datum bis | Heimmannschaft | Gastmannschaft | Status |
|---|---|---|---|---|---|---|
| 2026/2027 | 1 | 28.08.2026 | 28.08.2026 | Bayern Munich | Stuttgart | |
| 2026/2027 | 1 | 29.08.2026 | 29.08.2026 | FC Koln | Hoffenheim | |
| 2026/2027 | 20 | 22.01.2027 | 24.01.2027 | Dortmund | Hamburger SV | |

---

## 3. Teamnamen

- Teamnamen müssen exakt so geschrieben sein wie in der Datenbank, z. B. `Bayern Munich`, `B. Monchengladbach`, `FC Koln`, `Schalke`.
- **Aufsteiger** ohne Spiele in der Datenbank sind erlaubt. Ihre KPIs erscheinen gemäss KPI-Regelwerk als „--“.
- Ein Name, der in der Datenbank nicht vorkommt, kann ein Aufsteiger oder ein Schreibfehler sein. Das Programm kann das nicht unterscheiden. Deshalb gilt:
  - Unbekannte Namen werden zunächst als **Warnung** angezeigt.
  - Wird der Verein als bekannter Aufsteiger in der Teamliste (`app/config/teams.toml`, ab Etappe B) eingetragen, wird daraus ein **Hinweis**. Eingetragen sind derzeit Elversberg und Paderborn.
  - Die Teamliste ist Teil des Codes: Nach einer Änderung wird der Container neu gebaut (Ablauf wie eine Code-Änderung).
- Anzeigenamen (z. B. „1. FC Köln“ statt „FC Koln“) werden später zentral in der Teamliste gepflegt, nicht im Spielplan.

---

## 4. Aktueller Spieltag

Massgeblich ist das Dashboard-Briefing (v4.2), Kapitel 4.4. Hier zur Information wiederholt.

Der aktuelle Spieltag wird **für jede Liga separat** bestimmt:

1. Ein Spieltag gilt als beendet, sobald das späteste `Datum bis` seiner Spiele vor dem heutigen Datum liegt (Zeitzone Europe/Zurich). Die Anzeige wechselt am Tag nach dem letzten Spiel.
2. Angezeigt wird der Spieltag mit der niedrigsten Nummer, der noch nicht beendet ist.
3. Sind alle Spieltage der Datei beendet, wird der letzte Spieltag der Datei angezeigt.
4. Spiele mit Status `verschoben` oder `abgesagt` zählen nicht für die Frage, ob ein Spieltag beendet ist. Sie werden mit ihrem Status, aber ohne KPI-Werte angezeigt. *Ergänzt 31.10.2026:* Sind **alle** Spiele eines Spieltags verschoben oder abgesagt, gilt der Spieltag als beendet, damit er die Anzeige nicht dauerhaft blockiert.
5. Die KPIs jeder Begegnung werden immer so berechnet, als wäre das Spiel noch nicht gespielt. Stichtag ist `Datum von` der Begegnung.
6. Sortierung innerhalb eines Spieltags: nach `Datum von`, danach in der Reihenfolge der Datei.

**Beispiel:** Heute ist der 30.10.2026. Im Spielplan steht nur Spieltag 1 (Ende August 2026). Spieltag 1 ist beendet, und es gibt keinen neueren. Also wird Spieltag 1 angezeigt (Regel 3). Die Teamwerte werden aus den Spielen bis zwei Kalendertage vor dem jeweiligen Spieldatum berechnet, die Ligareferenz aus den Spieltagen 15–34 (Bundesliga) bzw. 19–38 (Premier League) der Saison 2025/26.

---

## 5. Prüfregeln

Die Ergebnisse erscheinen auf der Seite **Datenqualität**, getrennt von den Prüfungen der Datenbank.

### Fehler – Spielplan wird nicht verwendet, das Dashboard zeigt einen Hinweis statt der Tabelle

- Datei fehlt oder ist nicht lesbar
- Tabellenblatt einer aktiven Liga fehlt (*ergänzt 31.10.2026*)
- Pflichtspalte fehlt oder ist falsch geschrieben
- Pflichtfeld leer
- `Datum von` oder `Datum bis` ist kein gültiges Datum (z. B. Zeitraum als Text)
- `Datum bis` liegt vor `Datum von`
- `Spieltag` ist keine ganze Zahl ab 1
- `Saison` nicht im Format `JJJJ/JJJJ`
- `Status` enthält einen nicht erlaubten Wert

### Warnung – Spielplan wird verwendet, sollte aber geprüft werden

- Teamname unbekannt (Aufsteiger oder Schreibfehler, siehe Abschnitt 3)
- Ein Team kommt im selben Spieltag mehrfach vor
- Heim- und Gastmannschaft identisch
- Weniger Spiele in einem Spieltag als erwartet (Anzahl Teams der Liga / 2, gemäss Konfiguration `app/config/ligen.toml`: Bundesliga 18 Teams → 9 Spiele, Premier League 20 Teams → 10 Spiele)
- Dieselbe Paarung kommt in einer Saison mehrfach vor
- Tabellenblatt einer aktiven Liga ist leer (*ergänzt 31.10.2026*)

### Hinweis – kein Handlungsbedarf

- Bekannter Aufsteiger ohne Daten in der Datenbank
- Team ohne Ligaspiele in der Saison des Spiels und der Vorsaison, z. B. Schalke (*ergänzt 31.10.2026*); KPIs erscheinen als „–“
- Begegnung ist bereits als gespieltes Spiel in der Datenbank vorhanden
- Leeres Tabellenblatt einer noch nicht aktiven Liga

---

## 6. Pflege und Aktualisierung

- Einen neuen Spieltag spätestens am Tag nach dem Ende des vorherigen Spieltags eintragen. Sonst bleibt der alte Spieltag stehen (Regel 3).
- Verschiebungen: Status auf `verschoben` setzen. Steht der neue Termin fest, `Datum von` und `Datum bis` anpassen und den Status leeren.
- Hochladen auf den Server wie bei der Datenbank: zuerst unter einem Zwischennamen hochladen, prüfen, dann mit `mv` austauschen und vorher sichern. Der Ablauf ist in `01_Technisches_Setup.md`, Abschnitt 6, beschrieben, mit dem Dateinamen `Spielplan.xlsx`.
- Die App liest die Datei nur. Sie wird im Container schreibgeschützt eingebunden, wie die Datenbank.

---

## 7. Stand der Datei (geprüft am 30.10.2026, dritte Version)

**Ergebnis: Aufbau korrekt, keine Fehler.**

| Blatt | Spiele | Spieltag | Datum von – bis | Spaltenüberschriften |
|---|---|---|---|---|
| Bundesliga | 9 | 1 | 28.08.2026 – 30.08.2026 | korrekt |
| Premier League | 10 | 1 | 16.08.2026 – 20.08.2026 | korrekt |

Alle Datumswerte sind echte Excel-Datumswerte, die Spalte `Saison` ist vorhanden, alle Teamnamen ausser den Aufsteigern sind in der Datenbank bekannt.

**Zur Information (kein Fehler):**

| Blatt | Punkt | Auswirkung |
|---|---|---|
| beide | Spalte `Status` nicht vorhanden | erlaubt, alle Spiele gelten als „geplant“ |
| Bundesliga | Elversberg, Paderborn nicht in der Datenbank | Aufsteiger, KPIs erscheinen als „–“ (Warnung bis Eintrag in der Teamliste) |
| Bundesliga | Schalke: letzte Bundesliga-Spiele 2022/23 | ausserhalb des Zeitfensters (Saison des Spiels + Vorsaison), KPIs erscheinen als „–“ |
| Premier League | leere siebte Spalte (Formatierung) | unproblematisch, wird ignoriert |
| beide | Spieltag 1 ist beendet, kein neuerer Spieltag eingetragen | Dashboard zeigt Spieltag 1 (Regel 3) |

**Erledigt am 31.10.2026:** Datei liegt unter `data/Spielplan.xlsx` auf dem Server (SHA-256 `5261e916…`).

**Aktualisiert am 31.10.2026 (Version 2):** Spieltage 1 und 2 der Saison 2026/27 (Bundesliga je 9, Premier League je 10 Spiele). Beim Prüfen korrigiert: zweiter PL-Spieltag war als Spieltag 1 erfasst; Bundesliga Spieltag 2 um Augsburg – Eintracht Frankfurt ergänzt. Prüfergebnis: 0 Fehler, 0 Warnungen.
