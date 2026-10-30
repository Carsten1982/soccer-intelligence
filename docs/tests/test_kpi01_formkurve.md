# Testfall KPI 01 – Formkurve (letzte 5 Spiele)

**Spezifikation v1.1** · Stand 30.10.2026

**Regelwerk:** `03_KPI_Regelwerk.md`, Abschnitt 3
**Datenbasis:** `Database-Soccer-Intelligence.xlsx`, SHA-256 `6d68583c2e66616e92c1bf3e8a8611b4b517bcf4c0a7a91c68101ea26a2284e2`
**Status:** Stand Spieltag 1 (2026/27) bestätigt am 28.10.2026 · Stand Spieltag 3 (2025/26) bestätigt am 29.10.2026

**Datenbasis aktualisiert am 30.10.2026:** neue SHA-256 nach Korrektur von zwei versehentlich überschriebenen Zellen in der Premier League (id 5393 `Gameday` „bitte“ → 4; id 99466 `FT Home Goals` „Ergebnisse stimmen.“ → 2). Alle erwarteten Werte wurden mit der neuen Datei nachgerechnet: unverändert (144 Prüfwerte, 0 Abweichungen).

Dieser Testfall ist die verbindliche Referenz für die technische Umsetzung. Der Code muss mit derselben Datenbasis exakt diese Ergebnisse liefern. Die JSON-Blöcke sind für automatische Tests gedacht und müssen exakt übereinstimmen.

---

## 1. Regeln, die dieser Testfall prüft

- Je Team die letzten 5 abgeschlossenen Ligaspiele, Ergebnis aus Sicht des Teams (S / U / N).
- Nur Spiele derselben Liga aus der Saison des analysierten Spiels und der Vorsaison.
- Sortierung nach Datum, vom ältesten zum neuesten.
- Fehlende Positionen als „–“, nie als Niederlage. Anzahl verfügbarer Spiele wird angezeigt.
- Aufsteiger ohne Ligaspiele: 5 × „–“. Ergebnisse aus tieferen Ligen werden nicht übernommen.
- Ergebnis aus Spalten `FT Home Goals` / `FT Away Goals :` (identisch mit `Full-Time`-Spalten).

---

## 2. Auswahlschritte (feste Reihenfolge)

Für jedes Team einzeln:

1. **Ligablatt** des analysierten Spiels wählen (`Bundesliga` oder `Premier League`).
2. **Teamfilter:** alle Zeilen, in denen das Team `homeTeam` oder `awayTeam` ist (exakte Schreibweise).
3. **Saisonfilter:** nur `Season` = Saison des analysierten Spiels oder Vorsaison (hier `2026/2027` und `2025/2026`).
4. **Zeitfilter:** nur Spiele mit `Date` ≤ Analysedatum − 2 Kalendertage. Spiele am selben Tag, am Vortag oder später sind ausgeschlossen.
5. **Abgeschlossen:** nur Spiele mit vollständigem Ergebnis (`FT Home Goals` und `FT Away Goals :` befüllt).
6. **Sortierung:** aufsteigend nach `Date`, bei gleichem Datum nach der Uhrzeit aus `matchDate` (`TT-MM-JJ HH:MM`), danach nach `id`.
7. **Auswahl:** die letzten 5 Spiele dieser Liste.
8. **Ergebnis aus Teamsicht:** eigene Tore > Gegentore → `S`, gleich → `U`, weniger → `N`.
9. **Auffüllen:** Bei weniger als 5 Spielen werden die fehlenden Positionen **links** (am Anfang) mit `–` aufgefüllt, damit das neueste Spiel immer ganz rechts steht.

Ergebnisformat je Team: Liste mit genau 5 Einträgen aus `S`, `U`, `N`, `–` plus Anzahl der tatsächlich verfügbaren Spiele (0–5).

---

## 3. Stand Spieltag 1 (Saison 2026/27)

**Ausgangslage:** Die Datenbank enthält noch keine Spiele der Saison 2026/27. Alle Ergebnisse stammen aus der Saison 2025/26. Letztes Spiel in der Datenbank: Bundesliga 16.05.2026, Premier League 24.05.2026.

### 3.1 Eingabeparameter

| Testfall | Liga | Saison | Spieltag | Analysedatum | Heimteam | Auswärtsteam |
|---|---|---|---|---|---|---|
| BL-1 | Bundesliga | 2026/2027 | 1 | 2026-08-22 | Bayern Munich | Stuttgart |
| BL-2 | Bundesliga | 2026/2027 | 1 | 2026-08-22 | Elversberg | Bayer Leverkusen |
| PL-1 | Premier League | 2026/2027 | 1 | 2026-08-22 | Newcastle | Liverpool |
| PL-2 | Premier League | 2026/2027 | 1 | 2026-08-22 | Hull | Manchester Utd |

**Hinweis zum Analysedatum:** 2026-08-22 ist ein Platzhalter. Für Spieltag 1 ist das Ergebnis identisch für jedes Datum ab dem 26.05.2026 (letztes Spiel + 2 Tage). Wird das echte Datum des 1. Spieltags bekannt, kann es eingesetzt werden, ohne dass sich das Ergebnis ändert.

### 3.2 Erwartete Ergebnisse (maschinenlesbar)

```json
[
  {
    "testfall": "BL-1",
    "liga": "Bundesliga", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "heim":     {"team": "Bayern Munich",    "form": ["S","S","U","S","S"], "anzahl": 5, "vorlaeufig": false},
    "auswaerts":{"team": "Stuttgart",        "form": ["N","U","U","S","U"], "anzahl": 5, "vorlaeufig": false}
  },
  {
    "testfall": "BL-2",
    "liga": "Bundesliga", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "heim":     {"team": "Elversberg",       "form": ["–","–","–","–","–"], "anzahl": 0, "vorlaeufig": true},
    "auswaerts":{"team": "Bayer Leverkusen", "form": ["N","S","S","N","U"], "anzahl": 5, "vorlaeufig": false}
  },
  {
    "testfall": "PL-1",
    "liga": "Premier League", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "heim":     {"team": "Newcastle",        "form": ["N","S","U","S","N"], "anzahl": 5, "vorlaeufig": false},
    "auswaerts":{"team": "Liverpool",        "form": ["S","N","U","N","U"], "anzahl": 5, "vorlaeufig": false}
  },
  {
    "testfall": "PL-2",
    "liga": "Premier League", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "heim":     {"team": "Hull",             "form": ["–","–","–","–","–"], "anzahl": 0, "vorlaeufig": true},
    "auswaerts":{"team": "Manchester Utd",   "form": ["S","S","U","S","S"], "anzahl": 5, "vorlaeufig": false}
  }
]
```

`vorlaeufig` ist `true`, sobald weniger als 5 Spiele verfügbar sind (Regelwerk Abschnitt 1, „Kleinere Stichprobe“). Als Platzhalter wird das Zeichen „–“ (Halbgeviertstrich, U+2013) verwendet.

### 3.3 Eingabedaten zum Nachvollziehen

#### BL-1: Bayern Munich – Stuttgart

**Bayern Munich**

| Gameday | Datum | id | Begegnung | Ergebnis | Sicht | Form |
|---|---|---|---|---|---|---|
| 30 | 19.04.2026 | 118339 | Bayern Munich – Stuttgart | 4:2 | Heim | S |
| 31 | 25.04.2026 | 118648 | Mainz – Bayern Munich | 3:4 | Auswärts | S |
| 32 | 02.05.2026 | 118984 | Bayern Munich – Heidenheim | 3:3 | Heim | U |
| 33 | 09.05.2026 | 119271 | Wolfsburg – Bayern Munich | 0:1 | Auswärts | S |
| 34 | 16.05.2026 | 120509 | Bayern Munich – FC Koln | 5:1 | Heim | S |

**Stuttgart**

| Gameday | Datum | id | Begegnung | Ergebnis | Sicht | Form |
|---|---|---|---|---|---|---|
| 30 | 19.04.2026 | 118339 | Bayern Munich – Stuttgart | 4:2 | Auswärts | N |
| 31 | 26.04.2026 | 118750 | Stuttgart – Werder Bremen | 1:1 | Heim | U |
| 32 | 02.05.2026 | 118986 | Hoffenheim – Stuttgart | 3:3 | Auswärts | U |
| 33 | 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 3:1 | Heim | S |
| 34 | 16.05.2026 | 120510 | Eintracht Frankfurt – Stuttgart | 2:2 | Auswärts | U |

#### BL-2: Elversberg – Bayer Leverkusen

**Elversberg:** keine Spiele in der Datenbank (Aufsteiger).

**Bayer Leverkusen**

| Gameday | Datum | id | Begegnung | Ergebnis | Sicht | Form |
|---|---|---|---|---|---|---|
| 30 | 18.04.2026 | 118240 | Bayer Leverkusen – Augsburg | 1:2 | Heim | N |
| 31 | 25.04.2026 | 118646 | FC Koln – Bayer Leverkusen | 1:2 | Auswärts | S |
| 32 | 02.05.2026 | 118989 | Bayer Leverkusen – RB Leipzig | 4:1 | Heim | S |
| 33 | 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 3:1 | Auswärts | N |
| 34 | 16.05.2026 | 120508 | Bayer Leverkusen – Hamburger SV | 1:1 | Heim | U |

#### PL-1: Newcastle – Liverpool

**Newcastle**

| Gameday | Datum | id | Begegnung | Ergebnis | Sicht | Form |
|---|---|---|---|---|---|---|
| 34 | 25.04.2026 | 118606 | Arsenal – Newcastle | 1:0 | Auswärts | N |
| 35 | 02.05.2026 | 118932 | Newcastle – Brighton | 3:1 | Heim | S |
| 36 | 10.05.2026 | 119352 | Nottingham – Newcastle | 1:1 | Auswärts | U |
| 37 | 17.05.2026 | 120593 | Newcastle – West Ham | 3:1 | Heim | S |
| 38 | 24.05.2026 | 120844 | Fulham – Newcastle | 2:0 | Auswärts | N |

**Liverpool**

| Gameday | Datum | id | Begegnung | Ergebnis | Sicht | Form |
|---|---|---|---|---|---|---|
| 34 | 25.04.2026 | 118603 | Liverpool – Crystal Palace | 3:1 | Heim | S |
| 35 | 03.05.2026 | 119075 | Manchester Utd – Liverpool | 3:2 | Auswärts | N |
| 36 | 09.05.2026 | 119250 | Liverpool – Chelsea | 1:1 | Heim | U |
| 37 | 15.05.2026 | 120476 | Aston Villa – Liverpool | 4:2 | Auswärts | N |
| 38 | 24.05.2026 | 120845 | Liverpool – Brentford | 1:1 | Heim | U |

#### PL-2: Hull – Manchester Utd

**Hull:** keine Spiele in der Datenbank (Aufsteiger).

**Manchester Utd**

| Gameday | Datum | id | Begegnung | Ergebnis | Sicht | Form |
|---|---|---|---|---|---|---|
| 34 | 27.04.2026 | 118824 | Manchester Utd – Brentford | 2:1 | Heim | S |
| 35 | 03.05.2026 | 119075 | Manchester Utd – Liverpool | 3:2 | Heim | S |
| 36 | 09.05.2026 | 119253 | Sunderland – Manchester Utd | 0:0 | Auswärts | U |
| 37 | 17.05.2026 | 120588 | Manchester Utd – Nottingham | 3:2 | Heim | S |
| 38 | 24.05.2026 | 120841 | Brighton – Manchester Utd | 0:3 | Auswärts | S |

### 3.4 Kontrollpunkte für den Code

- Direkte Duelle erscheinen bei beiden Teams spiegelbildlich: id 118339 (Bayern S / Stuttgart N), id 119270 (Stuttgart S / Leverkusen N), id 119075 (Man Utd S / Liverpool N).
- Elversberg und Hull: genau 5 × „–“, `anzahl` 0, `vorlaeufig` true, **keine Fehlermeldung** (ein unbekanntes Team ist bei Aufsteigern erwartet).
- Bei allen 30 verwendeten Spielen stimmen `FT`- und `Full-Time`-Torspalten überein.
- Die verwendeten Spiel-IDs je Team müssen exakt den Tabellen in 3.3 entsprechen (nicht nur die Buchstabenfolge).

---

## 4. Stand Spieltag 3 (Saison 2025/26)

**Warum ein historischer Spieltag:** Statt auf die Saison 2026/27 zu warten und zwei Spieltage von Hand nachzutragen, wird der 3. Spieltag der Saison 2025/26 verwendet. Die Daten sind vollständig vorhanden, die Logik ist identisch: Spiele aus der laufenden Saison (Spieltage 1–2) plus Vorsaison (2024/25).

**Ausgangslage:** Die analysierten Spiele und alle späteren Spiele **stehen in der Datenbank** und dürfen nicht verwendet werden. Als Analysedatum gilt das echte Spieldatum.

### 4.1 Eingabeparameter

| Testfall | Liga | Saison | Spieltag | Analysedatum | Heimteam | Auswärtsteam | id in DB |
|---|---|---|---|---|---|---|---|
| BL-3a | Bundesliga | 2025/2026 | 3 | 2025-09-13 | Bayern Munich | Hamburger SV | 64955 |
| BL-3b | Bundesliga | 2025/2026 | 3 | 2025-09-13 | Wolfsburg | FC Koln | 64960 |
| PL-3a | Premier League | 2025/2026 | 3 | 2025-08-30 | Manchester Utd | Burnley | 64707 |
| PL-3b | Premier League | 2025/2026 | 3 | 2025-08-30 | Sunderland | Brentford | 64708 |

**Was die Partien testen:**

| Testfall | Schwerpunkt |
|---|---|
| BL-3a | Hamburger SV: echter Aufsteiger ohne frühere Spiele in der DB. Bayern: Saisonübergang. Spiel selbst (5:0) in der DB, darf nicht zählen. |
| BL-3b | FC Koln: Spiele 2020/21–2023/24 in der DB, aber nicht 2024/25. Die älteren Spiele dürfen **nicht** nachgezogen werden. |
| PL-3a | Burnley: Spiele 2020/21, 2021/22, 2023/24 in der DB, aber nicht 2024/25. Gleicher Test wie FC Koln. |
| PL-3b | Sunderland: echter Aufsteiger ohne frühere Spiele in der DB. Brentford: Saisonübergang. |

### 4.2 Erwartete Ergebnisse (maschinenlesbar)

```json
[
  {
    "testfall": "BL-3a",
    "liga": "Bundesliga", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-09-13",
    "heim":     {"team": "Bayern Munich",  "form": ["U","S","S","S","S"], "anzahl": 5, "vorlaeufig": false},
    "auswaerts":{"team": "Hamburger SV",   "form": ["–","–","–","U","N"], "anzahl": 2, "vorlaeufig": true}
  },
  {
    "testfall": "BL-3b",
    "liga": "Bundesliga", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-09-13",
    "heim":     {"team": "Wolfsburg",      "form": ["N","U","S","S","U"], "anzahl": 5, "vorlaeufig": false},
    "auswaerts":{"team": "FC Koln",        "form": ["–","–","–","S","S"], "anzahl": 2, "vorlaeufig": true}
  },
  {
    "testfall": "PL-3a",
    "liga": "Premier League", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-08-30",
    "heim":     {"team": "Manchester Utd", "form": ["N","N","S","N","U"], "anzahl": 5, "vorlaeufig": false},
    "auswaerts":{"team": "Burnley",        "form": ["–","–","–","N","S"], "anzahl": 2, "vorlaeufig": true}
  },
  {
    "testfall": "PL-3b",
    "liga": "Premier League", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-08-30",
    "heim":     {"team": "Sunderland",     "form": ["–","–","–","S","N"], "anzahl": 2, "vorlaeufig": true},
    "auswaerts":{"team": "Brentford",      "form": ["S","N","U","N","S"], "anzahl": 5, "vorlaeufig": false}
  }
]
```

### 4.3 Eingabedaten zum Nachvollziehen

#### BL-3a: Bayern Munich

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Sicht | Form |
|---|---|---|---|---|---|---|---|
| 2024/25 | 32 | 03.05.2025 | 14257 | RB Leipzig – Bayern Munich | 3:3 | Auswärts | U |
| 2024/25 | 33 | 10.05.2025 | 14246 | Bayern Munich – B. Monchengladbach | 2:0 | Heim | S |
| 2024/25 | 34 | 17.05.2025 | 14239 | Hoffenheim – Bayern Munich | 0:4 | Auswärts | S |
| 2025/26 | 1 | 22.08.2025 | 64488 | Bayern Munich – RB Leipzig | 6:0 | Heim | S |
| 2025/26 | 2 | 30.08.2025 | 64722 | Augsburg – Bayern Munich | 2:3 | Auswärts | S |

#### BL-3a: Hamburger SV

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Sicht | Form |
|---|---|---|---|---|---|---|---|
| 2025/26 | 1 | 24.08.2025 | 64592 | B. Monchengladbach – Hamburger SV | 0:0 | Auswärts | U |
| 2025/26 | 2 | 29.08.2025 | 64659 | Hamburger SV – St. Pauli | 0:2 | Heim | N |

#### BL-3b: Wolfsburg

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Sicht | Form |
|---|---|---|---|---|---|---|---|
| 2024/25 | 32 | 03.05.2025 | 14255 | Dortmund – Wolfsburg | 4:0 | Auswärts | N |
| 2024/25 | 33 | 09.05.2025 | 14251 | Wolfsburg – Hoffenheim | 2:2 | Heim | U |
| 2024/25 | 34 | 17.05.2025 | 14235 | B. Monchengladbach – Wolfsburg | 0:1 | Auswärts | S |
| 2025/26 | 1 | 23.08.2025 | 64551 | Heidenheim – Wolfsburg | 1:3 | Auswärts | S |
| 2025/26 | 2 | 31.08.2025 | 64775 | Wolfsburg – Mainz | 1:1 | Heim | U |

#### BL-3b: FC Koln

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Sicht | Form |
|---|---|---|---|---|---|---|---|
| 2025/26 | 1 | 24.08.2025 | 64593 | Mainz – FC Koln | 0:1 | Auswärts | S |
| 2025/26 | 2 | 31.08.2025 | 64773 | FC Koln – Freiburg | 4:1 | Heim | S |

#### PL-3a: Manchester Utd

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Sicht | Form |
|---|---|---|---|---|---|---|---|
| 2024/25 | 36 | 11.05.2025 | 14561 | Manchester Utd – West Ham | 0:2 | Heim | N |
| 2024/25 | 37 | 16.05.2025 | 14558 | Chelsea – Manchester Utd | 1:0 | Auswärts | N |
| 2024/25 | 38 | 25.05.2025 | 14544 | Manchester Utd – Aston Villa | 2:0 | Heim | S |
| 2025/26 | 1 | 17.08.2025 | 64402 | Manchester Utd – Arsenal | 0:1 | Heim | N |
| 2025/26 | 2 | 24.08.2025 | 64581 | Fulham – Manchester Utd | 1:1 | Auswärts | U |

#### PL-3a: Burnley

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Sicht | Form |
|---|---|---|---|---|---|---|---|
| 2025/26 | 1 | 16.08.2025 | 64373 | Tottenham – Burnley | 3:0 | Auswärts | N |
| 2025/26 | 2 | 23.08.2025 | 64535 | Burnley – Sunderland | 2:0 | Heim | S |

#### PL-3b: Sunderland

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Sicht | Form |
|---|---|---|---|---|---|---|---|
| 2025/26 | 1 | 16.08.2025 | 64372 | Sunderland – West Ham | 3:0 | Heim | S |
| 2025/26 | 2 | 23.08.2025 | 64535 | Burnley – Sunderland | 2:0 | Auswärts | N |

#### PL-3b: Brentford

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Sicht | Form |
|---|---|---|---|---|---|---|---|
| 2024/25 | 36 | 10.05.2025 | 14567 | Ipswich – Brentford | 0:1 | Auswärts | S |
| 2024/25 | 37 | 18.05.2025 | 14554 | Brentford – Fulham | 2:3 | Heim | N |
| 2024/25 | 38 | 25.05.2025 | 14549 | Wolves – Brentford | 1:1 | Auswärts | U |
| 2025/26 | 1 | 17.08.2025 | 64404 | Nottingham – Brentford | 3:1 | Auswärts | N |
| 2025/26 | 2 | 23.08.2025 | 64534 | Brentford – Aston Villa | 1:0 | Heim | S |

### 4.4 Kontrollpunkte für den Code

- **Saisonübergang:** Bei Bayern, Wolfsburg, Man Utd und Brentford stammen 3 Spiele aus 2024/25 und 2 aus 2025/26, chronologisch korrekt sortiert.
- **Saisonfenster (wichtigster Kontrollpunkt):** FC Koln und Burnley haben Spiele aus 2023/24 und früher in der Datenbank. Diese dürfen **nicht** verwendet werden. Erwartet: `anzahl` 2, drei Platzhalter. Ein Code ohne korrekten Saisonfilter würde hier Ergebnisse aus dem Frühjahr 2024 anzeigen und `anzahl` 5 liefern.
- **Keine Zukunftsdaten:** Das analysierte Spiel (z. B. id 64955, Bayern – HSV 5:0) und alle späteren Spiele dürfen nicht verwendet werden.
- **Teilweise Formkurve:** Alle vier Aufsteiger: Platzhalter links, die beiden echten Ergebnisse rechts, `vorlaeufig` true.
- **Spiegelbild:** id 64535 (Burnley – Sunderland 2:0): Burnley S, Sunderland N.
- **Echte und „unterbrochene“ Aufsteiger gleich behandelt:** HSV und Sunderland (nie zuvor in der DB) liefern dasselbe Muster wie FC Koln und Burnley (früher in der DB). Für den Code darf es keinen Unterschied machen.

### 4.5 Nicht abgedeckt

- **2-Tage-Regel:** Bei keiner Partie liegt ein Spiel weniger als 6 Tage vor dem Analysedatum. Die Regel greift nicht und bleibt ungetestet (Ergebnisse identisch mit der früheren 3-Tage-Regel). Absicherung über einen ausgedachten Testdatensatz (siehe Abschnitt 5).

---

## 5. Weitere Tests (geplant)

- **Ausgedachter Testdatensatz** für Sonderfälle, die in echten Daten kaum gezielt vorkommen: 2-Tage-Regel (Spiele genau 1, 2 und 3 Tage vor dem Analysedatum), Team mit genau 1 Spiel, zwei Spiele am selben Tag (Sortierung nach Uhrzeit).
- **Praxistest 3. Spieltag 2026/27:** optional, sobald die Saison läuft und die Daten nachgetragen sind. Kein Ersatz für Abschnitt 4, sondern ein zusätzlicher Realitätscheck.
