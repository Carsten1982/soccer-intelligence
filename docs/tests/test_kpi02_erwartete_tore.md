# Testfall KPI 02 – Erwartete Tore (Gesamtspiel)

**Spezifikation v1.1** · Stand 30.10.2026

**Regelwerk:** `03_KPI_Regelwerk.md`, Abschnitte 1, 1.1, 2 und 4
**Datenbasis:** `Database-Soccer-Intelligence.xlsx`, SHA-256 `6d68583c2e66616e92c1bf3e8a8611b4b517bcf4c0a7a91c68101ea26a2284e2`
**Status:** Stand Spieltag 1 (2026/27) bestätigt am 28.10.2026 · Stand Spieltag 3 (2025/26) bestätigt am 29.10.2026

**Datenbasis aktualisiert am 30.10.2026:** neue SHA-256 nach Korrektur von zwei versehentlich überschriebenen Zellen in der Premier League (id 5393 `Gameday` „bitte“ → 4; id 99466 `FT Home Goals` „Ergebnisse stimmen.“ → 2). Alle erwarteten Werte wurden mit der neuen Datei nachgerechnet: unverändert (144 Prüfwerte, 0 Abweichungen).

Dieser Testfall ist die verbindliche Referenz für die technische Umsetzung. Der Code muss mit derselben Datenbasis exakt diese Ergebnisse liefern. Die JSON-Blöcke sind für automatische Tests gedacht und müssen exakt übereinstimmen.

---

## 1. Regeln, die dieser Testfall prüft

- Teamwert = Ø Gesamttore (beider Mannschaften) in den letzten 10 Ligaspielen des Teams.
- Torindikator = (Teamwert Heim + Teamwert Auswärts) / 2.
- Ligareferenz = Ø Gesamttore pro Spiel in den letzten 20 Spieltagen laut `Gameday`, auch über das Saisonende hinweg.
- Relative Abweichung = (Torindikator − Ligareferenz) / Ligareferenz × 100.
- Anomalie-Schwellenwerte, Rundung und Vorzeichen gemäss Regelwerk Abschnitt 2.
- Aufsteiger ohne Ligaspiele: kein Torindikator, keine Abweichung, keine Anomalie.

---

## 2. Auswahl- und Rechenschritte (feste Reihenfolge)

### 2.1 Teamwert (für jedes Team einzeln)

1. Ligablatt des analysierten Spiels wählen.
2. Alle Zeilen, in denen das Team `homeTeam` oder `awayTeam` ist (exakte Schreibweise).
3. Nur `Season` = Saison des analysierten Spiels oder Vorsaison (hier `2026/2027` und `2025/2026`).
4. Nur Spiele mit `Date` ≤ Analysedatum − 2 Kalendertage.
5. Nur Spiele mit befüllten Torspalten `FT Home Goals` und `FT Away Goals :`. Fehlt ein Wert, wird das Spiel ausgelassen und nicht durch ein älteres ersetzt.
6. Sortierung aufsteigend nach `Date`, dann Uhrzeit aus `matchDate`, dann `id`.
7. Die letzten 10 Spiele nehmen.
8. Gesamttore je Spiel = `FT Home Goals` + `FT Away Goals :`.
9. Teamwert = Summe Gesamttore / Anzahl Spiele (ungerundet weiterrechnen).
10. Bei 0 Spielen: Teamwert nicht verfügbar. Bei 1–9 Spielen: Teamwert berechnen, KPI als „vorläufig“ kennzeichnen.

### 2.2 Ligareferenz

1. Ligablatt des analysierten Spiels wählen.
2. Die 20 Spieltage vor dem Spieltag des analysierten Spiels bestimmen (über `Season` und `Gameday`, über das Saisonende hinweg).
3. Davon nur abgeschlossene Spiele mit befüllten Torspalten.
4. Ligareferenz = Summe Gesamttore / tatsächliche Anzahl Spiele (ungerundet weiterrechnen).

### 2.3 Torindikator, Abweichung, Anomalie

1. Fehlt ein Teamwert → Torindikator, Abweichung und Anomalie nicht verfügbar. Ende.
2. Torindikator = (Teamwert Heim + Teamwert Auswärts) / 2.
3. Fehlt die Ligareferenz oder ist sie 0 → Abweichung und Anomalie nicht verfügbar.
4. Abweichung = (Torindikator − Ligareferenz) / Ligareferenz × 100, mit ungerundeten Werten.
5. Rundung erst am Ende: alle angezeigten Werte auf eine Nachkommastelle, kaufmännisch (ab ,5 aufrunden). **Dezimalarithmetik verwenden, keine binäre Gleitkomma-Rundung** (siehe Kontrollpunkt 4.4).
6. Anomalie anhand der **gerundeten** Abweichung: |x| ≤ 20,0 keine · 20,0 < |x| ≤ 35,0 leicht · |x| > 35,0 stark. Richtung: positiv wenn x > 0, negativ wenn x < 0.

---

## 3. Stand Spieltag 1 (Saison 2026/27)

**Ausgangslage:** Die Datenbank enthält noch keine Spiele der Saison 2026/27. Teamwerte und Ligareferenz stammen vollständig aus der Saison 2025/26.

### 3.1 Eingabeparameter

| Testfall | Liga | Saison | Spieltag | Analysedatum | Heimteam | Auswärtsteam |
|---|---|---|---|---|---|---|
| BL-1 | Bundesliga | 2026/2027 | 1 | 2026-08-22 | Bayern Munich | Stuttgart |
| BL-2 | Bundesliga | 2026/2027 | 1 | 2026-08-22 | Elversberg | Bayer Leverkusen |
| PL-1 | Premier League | 2026/2027 | 1 | 2026-08-22 | Newcastle | Liverpool |
| PL-2 | Premier League | 2026/2027 | 1 | 2026-08-22 | Hull | Manchester Utd |

Analysedatum 2026-08-22 ist ein Platzhalter (siehe `test_kpi01_formkurve.md`). Das Ergebnis ist für jedes Datum ab dem 26.05.2026 identisch.

### 3.2 Erwartete Ergebnisse (maschinenlesbar)

Ungerundete Werte (`_roh`) dienen der Kontrolle der Rechenschritte, gerundete Werte sind die Anzeige. Nicht verfügbare Werte sind `null`.

```json
[
  {
    "testfall": "BL-1",
    "liga": "Bundesliga", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "heim":      {"team": "Bayern Munich",    "spiele": 10, "tore": 47, "teamwert_roh": 4.7, "teamwert": "4.7"},
    "auswaerts": {"team": "Stuttgart",        "spiele": 10, "tore": 40, "teamwert_roh": 4.0, "teamwert": "4.0"},
    "ligareferenz": {"saison_spieltage": "2025/2026: 15-34", "spiele": 180, "tore": 584, "wert_roh": 3.2444444444, "wert": "3.2"},
    "torindikator_roh": 4.35, "torindikator": "4.4",
    "abweichung_roh": 34.0753424658, "abweichung": "+34.1",
    "anomalie": "leicht", "richtung": "positiv", "vorlaeufig": false,
    "ueberschrift": "Viele Tore erwartet",
    "text": "In dieser Partie liegt der Torindikator bei durchschnittlich 4,4 Toren. Das sind 34,1 % mehr als im Liga-Durchschnitt."
  },
  {
    "testfall": "BL-2",
    "liga": "Bundesliga", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "heim":      {"team": "Elversberg",       "spiele": 0,  "tore": null, "teamwert_roh": null, "teamwert": null},
    "auswaerts": {"team": "Bayer Leverkusen", "spiele": 10, "tore": 41,   "teamwert_roh": 4.1,  "teamwert": "4.1"},
    "ligareferenz": {"saison_spieltage": "2025/2026: 15-34", "spiele": 180, "tore": 584, "wert_roh": 3.2444444444, "wert": "3.2"},
    "torindikator_roh": null, "torindikator": null,
    "abweichung_roh": null, "abweichung": null,
    "anomalie": null, "richtung": null, "vorlaeufig": true,
    "ueberschrift": null, "text": null
  },
  {
    "testfall": "PL-1",
    "liga": "Premier League", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "heim":      {"team": "Newcastle",        "spiele": 10, "tore": 26, "teamwert_roh": 2.6, "teamwert": "2.6"},
    "auswaerts": {"team": "Liverpool",        "spiele": 10, "tore": 32, "teamwert_roh": 3.2, "teamwert": "3.2"},
    "ligareferenz": {"saison_spieltage": "2025/2026: 19-38", "spiele": 200, "tore": 542, "wert_roh": 2.71, "wert": "2.7"},
    "torindikator_roh": 2.9, "torindikator": "2.9",
    "abweichung_roh": 7.0110701107, "abweichung": "+7.0",
    "anomalie": "keine", "richtung": "positiv", "vorlaeufig": false,
    "ueberschrift": "Keine statistische Besonderheit",
    "text": "In dieser Partie liegt der Torindikator bei durchschnittlich 2,9 Toren. Die Abweichung vom Liga-Durchschnitt beträgt +7,0 %."
  },
  {
    "testfall": "PL-2",
    "liga": "Premier League", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "heim":      {"team": "Hull",             "spiele": 0,  "tore": null, "teamwert_roh": null, "teamwert": null},
    "auswaerts": {"team": "Manchester Utd",   "spiele": 10, "tore": 31,   "teamwert_roh": 3.1,  "teamwert": "3.1"},
    "ligareferenz": {"saison_spieltage": "2025/2026: 19-38", "spiele": 200, "tore": 542, "wert_roh": 2.71, "wert": "2.7"},
    "torindikator_roh": null, "torindikator": null,
    "abweichung_roh": null, "abweichung": null,
    "anomalie": null, "richtung": null, "vorlaeufig": true,
    "ueberschrift": null, "text": null
  }
]
```

Hinweise zum JSON:
- Gerundete Werte sind als Text mit Punkt angegeben, damit kein Rundungsfehler beim Einlesen entsteht. Im Dashboard werden sie mit Komma angezeigt (4,4).
- `_roh`-Werte bei periodischen Zahlen sind auf 10 Nachkommastellen abgeschnitten; beim Vergleich eine Toleranz von 1e-9 verwenden.
- `richtung` wird auch bei „keine Anomalie“ ausgegeben, damit das Dashboard die Abweichung korrekt einordnen kann.

### 3.3 Eingabedaten zum Nachvollziehen

#### Ligareferenz Bundesliga (2025/26, Spieltage 15–34)

Je Spieltag 9 Spiele. Tore pro Spieltag:

| Spieltag | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 |
|---|---|---|---|---|---|---|---|---|---|---|
| Tore | 20 | 39 | 29 | 29 | 24 | 27 | 24 | 31 | 33 | 22 |

| Spieltag | 25 | 26 | 27 | 28 | 29 | 30 | 31 | 32 | 33 | 34 |
|---|---|---|---|---|---|---|---|---|---|---|
| Tore | 35 | 15 | 40 | 34 | 27 | 30 | 27 | 34 | 31 | 33 |

Summe: 584 Tore in 180 Spielen → 3,2444…

#### Ligareferenz Premier League (2025/26, Spieltage 19–38)

Je Spieltag 10 Spiele. Tore pro Spieltag:

| Spieltag | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 |
|---|---|---|---|---|---|---|---|---|---|---|
| Tore | 23 | 32 | 29 | 16 | 33 | 33 | 29 | 24 | 21 | 36 |

| Spieltag | 29 | 30 | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 |
|---|---|---|---|---|---|---|---|---|---|---|
| Tore | 24 | 16 | 29 | 27 | 29 | 26 | 37 | 22 | 32 | 24 |

Summe: 542 Tore in 200 Spielen → 2,71

#### BL-1: Bayern Munich (47 Tore / 10 Spiele = 4,7)

| Gameday | Datum | id | Begegnung | Ergebnis | Gesamttore |
|---|---|---|---|---|---|
| 25 | 06.03.2026 | 99487 | Bayern Munich – B. Monchengladbach | 4:1 | 5 |
| 26 | 14.03.2026 | 106579 | Bayer Leverkusen – Bayern Munich | 1:1 | 2 |
| 27 | 21.03.2026 | 114288 | Bayern Munich – Union Berlin | 4:0 | 4 |
| 28 | 04.04.2026 | 117437 | Freiburg – Bayern Munich | 2:3 | 5 |
| 29 | 11.04.2026 | 117903 | St. Pauli – Bayern Munich | 0:5 | 5 |
| 30 | 19.04.2026 | 118339 | Bayern Munich – Stuttgart | 4:2 | 6 |
| 31 | 25.04.2026 | 118648 | Mainz – Bayern Munich | 3:4 | 7 |
| 32 | 02.05.2026 | 118984 | Bayern Munich – Heidenheim | 3:3 | 6 |
| 33 | 09.05.2026 | 119271 | Wolfsburg – Bayern Munich | 0:1 | 1 |
| 34 | 16.05.2026 | 120509 | Bayern Munich – FC Koln | 5:1 | 6 |

#### BL-1: Stuttgart (40 Tore / 10 Spiele = 4,0)

| Gameday | Datum | id | Begegnung | Ergebnis | Gesamttore |
|---|---|---|---|---|---|
| 25 | 07.03.2026 | 99520 | Mainz – Stuttgart | 2:2 | 4 |
| 26 | 15.03.2026 | 107988 | Stuttgart – RB Leipzig | 1:0 | 1 |
| 27 | 22.03.2026 | 114388 | Augsburg – Stuttgart | 2:5 | 7 |
| 28 | 04.04.2026 | 117441 | Stuttgart – Dortmund | 0:2 | 2 |
| 29 | 12.04.2026 | 118014 | Stuttgart – Hamburger SV | 4:0 | 4 |
| 30 | 19.04.2026 | 118339 | Bayern Munich – Stuttgart | 4:2 | 6 |
| 31 | 26.04.2026 | 118750 | Stuttgart – Werder Bremen | 1:1 | 2 |
| 32 | 02.05.2026 | 118986 | Hoffenheim – Stuttgart | 3:3 | 6 |
| 33 | 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 3:1 | 4 |
| 34 | 16.05.2026 | 120510 | Eintracht Frankfurt – Stuttgart | 2:2 | 4 |

#### BL-2: Elversberg

Keine Spiele in der Datenbank (Aufsteiger).

#### BL-2: Bayer Leverkusen (41 Tore / 10 Spiele = 4,1)

| Gameday | Datum | id | Begegnung | Ergebnis | Gesamttore |
|---|---|---|---|---|---|
| 25 | 07.03.2026 | 99518 | Freiburg – Bayer Leverkusen | 3:3 | 6 |
| 26 | 14.03.2026 | 106579 | Bayer Leverkusen – Bayern Munich | 1:1 | 2 |
| 27 | 21.03.2026 | 114290 | Heidenheim – Bayer Leverkusen | 3:3 | 6 |
| 28 | 04.04.2026 | 117436 | Bayer Leverkusen – Wolfsburg | 6:3 | 9 |
| 29 | 11.04.2026 | 117899 | Dortmund – Bayer Leverkusen | 0:1 | 1 |
| 30 | 18.04.2026 | 118240 | Bayer Leverkusen – Augsburg | 1:2 | 3 |
| 31 | 25.04.2026 | 118646 | FC Koln – Bayer Leverkusen | 1:2 | 3 |
| 32 | 02.05.2026 | 118989 | Bayer Leverkusen – RB Leipzig | 4:1 | 5 |
| 33 | 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 3:1 | 4 |
| 34 | 16.05.2026 | 120508 | Bayer Leverkusen – Hamburger SV | 1:1 | 2 |

#### PL-1: Newcastle (26 Tore / 10 Spiele = 2,6)

| Gameday | Datum | id | Begegnung | Ergebnis | Gesamttore |
|---|---|---|---|---|---|
| 29 | 04.03.2026 | 99466 | Newcastle – Manchester Utd | 2:1 | 3 |
| 30 | 14.03.2026 | 106538 | Chelsea – Newcastle | 0:1 | 1 |
| 31 | 22.03.2026 | 114378 | Newcastle – Sunderland | 1:2 | 3 |
| 32 | 12.04.2026 | 118005 | Crystal Palace – Newcastle | 2:1 | 3 |
| 33 | 18.04.2026 | 118200 | Newcastle – Bournemouth | 1:2 | 3 |
| 34 | 25.04.2026 | 118606 | Arsenal – Newcastle | 1:0 | 1 |
| 35 | 02.05.2026 | 118932 | Newcastle – Brighton | 3:1 | 4 |
| 36 | 10.05.2026 | 119352 | Nottingham – Newcastle | 1:1 | 2 |
| 37 | 17.05.2026 | 120593 | Newcastle – West Ham | 3:1 | 4 |
| 38 | 24.05.2026 | 120844 | Fulham – Newcastle | 2:0 | 2 |

#### PL-1: Liverpool (32 Tore / 10 Spiele = 3,2)

| Gameday | Datum | id | Begegnung | Ergebnis | Gesamttore |
|---|---|---|---|---|---|
| 29 | 03.03.2026 | 99447 | Wolves – Liverpool | 2:1 | 3 |
| 30 | 15.03.2026 | 107981 | Liverpool – Tottenham | 1:1 | 2 |
| 31 | 21.03.2026 | 114243 | Brighton – Liverpool | 2:1 | 3 |
| 32 | 11.04.2026 | 117862 | Liverpool – Fulham | 2:0 | 2 |
| 33 | 19.04.2026 | 118327 | Everton – Liverpool | 1:2 | 3 |
| 34 | 25.04.2026 | 118603 | Liverpool – Crystal Palace | 3:1 | 4 |
| 35 | 03.05.2026 | 119075 | Manchester Utd – Liverpool | 3:2 | 5 |
| 36 | 09.05.2026 | 119250 | Liverpool – Chelsea | 1:1 | 2 |
| 37 | 15.05.2026 | 120476 | Aston Villa – Liverpool | 4:2 | 6 |
| 38 | 24.05.2026 | 120845 | Liverpool – Brentford | 1:1 | 2 |

#### PL-2: Hull

Keine Spiele in der Datenbank (Aufsteiger).

#### PL-2: Manchester Utd (31 Tore / 10 Spiele = 3,1)

| Gameday | Datum | id | Begegnung | Ergebnis | Gesamttore |
|---|---|---|---|---|---|
| 29 | 04.03.2026 | 99466 | Newcastle – Manchester Utd | 2:1 | 3 |
| 30 | 15.03.2026 | 107979 | Manchester Utd – Aston Villa | 3:1 | 4 |
| 31 | 20.03.2026 | 114203 | Bournemouth – Manchester Utd | 2:2 | 4 |
| 32 | 13.04.2026 | 118082 | Manchester Utd – Leeds | 1:2 | 3 |
| 33 | 18.04.2026 | 118202 | Chelsea – Manchester Utd | 0:1 | 1 |
| 34 | 27.04.2026 | 118824 | Manchester Utd – Brentford | 2:1 | 3 |
| 35 | 03.05.2026 | 119075 | Manchester Utd – Liverpool | 3:2 | 5 |
| 36 | 09.05.2026 | 119253 | Sunderland – Manchester Utd | 0:0 | 0 |
| 37 | 17.05.2026 | 120588 | Manchester Utd – Nottingham | 3:2 | 5 |
| 38 | 24.05.2026 | 120841 | Brighton – Manchester Utd | 0:3 | 3 |

---

## 4. Kontrollpunkte für den Code

### 4.1 Ligareferenz
- Bundesliga: genau 180 Spiele (Spieltage 15–34, je 9), Premier League: genau 200 Spiele (Spieltage 19–38, je 10).
- Spieltag 14 (Bundesliga) bzw. 18 (Premier League) darf **nicht** enthalten sein.
- In allen 380 Referenzspielen stimmen `FT`- und `Full-Time`-Torspalten überein.

### 4.2 Teamwerte
- Die verwendeten Spiel-IDs je Team müssen exakt den Tabellen in 3.3 entsprechen.
- Direkte Duelle zählen bei beiden Teams mit denselben Gesamttoren: id 118339 (Bayern / Stuttgart, 6), id 119270 (Stuttgart / Leverkusen, 4), id 106579 (Leverkusen / Bayern, 2), id 99466 (Newcastle / Man Utd, 3), id 119075 (Man Utd / Liverpool, 5).
- Teamwert = Gesamttore **beider** Mannschaften, nicht nur eigene Tore.

### 4.3 Aufsteiger
- Elversberg und Hull: Teamwert `null`, Torindikator, Abweichung und Anomalie `null`, **keine Fehlermeldung**.
- Der Teamwert des Gegners (Leverkusen 4,1 / Man Utd 3,1) und die Ligareferenz werden trotzdem berechnet.
- Der Gegnerwert darf **nicht** als Torindikator ausgegeben werden.

### 4.4 Rundung (wichtigster Kontrollpunkt)
- BL-1: Torindikator 4,35 muss als **4,4** angezeigt werden.
- Mit binärer Gleitkomma-Rundung (z. B. `round(4.35, 1)` in Python) ergibt sich fälschlich 4,3, weil 4,35 intern als 4,34999… gespeichert wird. Für die Anzeige-Rundung Dezimalarithmetik verwenden (z. B. Python `decimal` mit `ROUND_HALF_UP`).
- Die Anomalie-Einstufung erfolgt mit der gerundeten Abweichung (+34,1 → leicht), gerechnet wird aber mit dem ungerundeten Torindikator 4,35, **nicht** mit 4,4. Mit 4,4 ergäbe sich fälschlich +35,6 % → stark.

### 4.5 Grenznähe
- BL-1 liegt mit +34,1 % knapp unter der Grenze zur starken Anomalie (35,0 %). Ein Fehler bei Rundung oder Spielauswahl führt hier schnell zu einer falschen Einstufung.

---

## 5. Annahmen, die noch zu bestätigen sind

1. **KPI-Karte bei Aufsteiger-Spielen:** Teamwert des Gegners und Ligareferenz werden angezeigt, Hauptwert, Abweichung und Anomalie als „–“. Grundlage: Das Regelwerk verbietet nur, den Gegnerwert als Gesamtindikator auszugeben.
2. ~~**Vorzeichen im Text „Keine Anomalie“**~~ **Geklärt am 30.10.2026** (Regelwerk 2.4): Vorzeichen steht immer, bei 0,0 % keins. PL-1-Text auf „+7,0 %“ angepasst.

---

## 6. Stand Spieltag 3 (Saison 2025/26)

**Warum ein historischer Spieltag:** siehe `test_kpi01_formkurve.md`, Abschnitt 4. Die Daten sind vollständig vorhanden, die Logik ist identisch mit einem 3. Spieltag der laufenden Saison.

**Ausgangslage:** Teamwerte und Ligareferenz setzen sich aus zwei Saisons zusammen. Die analysierten Spiele und alle späteren Spiele stehen in der Datenbank und dürfen nicht verwendet werden.

### 6.1 Eingabeparameter

| Testfall | Liga | Saison | Spieltag | Analysedatum | Heimteam | Auswärtsteam | id in DB |
|---|---|---|---|---|---|---|---|
| BL-3a | Bundesliga | 2025/2026 | 3 | 2025-09-13 | Bayern Munich | Hamburger SV | 64955 |
| BL-3b | Bundesliga | 2025/2026 | 3 | 2025-09-13 | Wolfsburg | FC Koln | 64960 |
| PL-3a | Premier League | 2025/2026 | 3 | 2025-08-30 | Manchester Utd | Burnley | 64707 |
| PL-3b | Premier League | 2025/2026 | 3 | 2025-08-30 | Sunderland | Brentford | 64708 |

### 6.2 Erwartete Ergebnisse (maschinenlesbar)

```json
[
  {
    "testfall": "BL-3a",
    "liga": "Bundesliga", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-09-13",
    "heim":      {"team": "Bayern Munich",  "spiele": 10, "tore": 43, "teamwert_roh": 4.3, "teamwert": "4.3"},
    "auswaerts": {"team": "Hamburger SV",   "spiele": 2,  "tore": 2,  "teamwert_roh": 1.0, "teamwert": "1.0"},
    "ligareferenz": {"saison_spieltage": "2024/2025: 17-34 + 2025/2026: 1-2", "spiele": 180, "tore": 552, "wert_roh": 3.0666666667, "wert": "3.1"},
    "torindikator_roh": 2.65, "torindikator": "2.7",
    "abweichung_roh": -13.5869565217, "abweichung": "-13.6",
    "anomalie": "keine", "richtung": "negativ", "vorlaeufig": true,
    "ueberschrift": "Keine statistische Besonderheit",
    "text": "In dieser Partie liegt der Torindikator bei durchschnittlich 2,7 Toren. Die Abweichung vom Liga-Durchschnitt beträgt −13,6 %."
  },
  {
    "testfall": "BL-3b",
    "liga": "Bundesliga", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-09-13",
    "heim":      {"team": "Wolfsburg",      "spiele": 10, "tore": 27, "teamwert_roh": 2.7, "teamwert": "2.7"},
    "auswaerts": {"team": "FC Koln",        "spiele": 2,  "tore": 6,  "teamwert_roh": 3.0, "teamwert": "3.0"},
    "ligareferenz": {"saison_spieltage": "2024/2025: 17-34 + 2025/2026: 1-2", "spiele": 180, "tore": 552, "wert_roh": 3.0666666667, "wert": "3.1"},
    "torindikator_roh": 2.85, "torindikator": "2.9",
    "abweichung_roh": -7.0652173913, "abweichung": "-7.1",
    "anomalie": "keine", "richtung": "negativ", "vorlaeufig": true,
    "ueberschrift": "Keine statistische Besonderheit",
    "text": "In dieser Partie liegt der Torindikator bei durchschnittlich 2,9 Toren. Die Abweichung vom Liga-Durchschnitt beträgt −7,1 %."
  },
  {
    "testfall": "PL-3a",
    "liga": "Premier League", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-08-30",
    "heim":      {"team": "Manchester Utd", "spiele": 10, "tore": 23, "teamwert_roh": 2.3, "teamwert": "2.3"},
    "auswaerts": {"team": "Burnley",        "spiele": 2,  "tore": 5,  "teamwert_roh": 2.5, "teamwert": "2.5"},
    "ligareferenz": {"saison_spieltage": "2024/2025: 21-38 + 2025/2026: 1-2", "spiele": 200, "tore": 570, "wert_roh": 2.85, "wert": "2.9"},
    "torindikator_roh": 2.4, "torindikator": "2.4",
    "abweichung_roh": -15.7894736842, "abweichung": "-15.8",
    "anomalie": "keine", "richtung": "negativ", "vorlaeufig": true,
    "ueberschrift": "Keine statistische Besonderheit",
    "text": "In dieser Partie liegt der Torindikator bei durchschnittlich 2,4 Toren. Die Abweichung vom Liga-Durchschnitt beträgt −15,8 %."
  },
  {
    "testfall": "PL-3b",
    "liga": "Premier League", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-08-30",
    "heim":      {"team": "Sunderland",     "spiele": 2,  "tore": 5,  "teamwert_roh": 2.5, "teamwert": "2.5"},
    "auswaerts": {"team": "Brentford",      "spiele": 10, "tore": 30, "teamwert_roh": 3.0, "teamwert": "3.0"},
    "ligareferenz": {"saison_spieltage": "2024/2025: 21-38 + 2025/2026: 1-2", "spiele": 200, "tore": 570, "wert_roh": 2.85, "wert": "2.9"},
    "torindikator_roh": 2.75, "torindikator": "2.8",
    "abweichung_roh": -3.5087719298, "abweichung": "-3.5",
    "anomalie": "keine", "richtung": "negativ", "vorlaeufig": true,
    "ueberschrift": "Keine statistische Besonderheit",
    "text": "In dieser Partie liegt der Torindikator bei durchschnittlich 2,8 Toren. Die Abweichung vom Liga-Durchschnitt beträgt −3,5 %."
  }
]
```

Texte mit Vorzeichen gemäss Empfehlung in `test_kpi04_gelbe_karten.md`, Abschnitt 5 (noch zu bestätigen).

### 6.3 Eingabedaten zum Nachvollziehen

#### Ligareferenz Bundesliga (2024/25 Spieltage 17–34 + 2025/26 Spieltage 1–2)

Je Spieltag 9 Spiele. Tore pro Spieltag:

| Spieltag 24/25 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 |
|---|---|---|---|---|---|---|---|---|---|
| Tore | 35 | 32 | 30 | 23 | 19 | 19 | 30 | 22 | 23 |

| Spieltag 24/25 | 26 | 27 | 28 | 29 | 30 | 31 | 32 | 33 | 34 |
|---|---|---|---|---|---|---|---|---|---|
| Tore | 31 | 24 | 25 | 26 | 31 | 25 | 33 | 31 | 31 |

| Spieltag 25/26 | 1 | 2 |
|---|---|---|
| Tore | 32 | 30 |

Summe: 490 + 62 = 552 Tore in 162 + 18 = 180 Spielen → 3,0666…

#### Ligareferenz Premier League (2024/25 Spieltage 21–38 + 2025/26 Spieltage 1–2)

Je Spieltag 10 Spiele. Tore pro Spieltag:

| Spieltag 24/25 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 |
|---|---|---|---|---|---|---|---|---|---|
| Tore | 30 | 39 | 29 | 34 | 26 | 33 | 27 | 20 | 33 |

| Spieltag 24/25 | 30 | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 |
|---|---|---|---|---|---|---|---|---|---|
| Tore | 20 | 27 | 36 | 27 | 32 | 28 | 22 | 31 | 24 |

| Spieltag 25/26 | 1 | 2 |
|---|---|---|
| Tore | 24 | 28 |

Summe: 518 + 52 = 570 Tore in 180 + 20 = 200 Spielen → 2,85

#### BL-3a: Bayern Munich (43 Tore / 10 Spiele = 4,3)

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Gesamttore |
|---|---|---|---|---|---|---|
| 2024/25 | 27 | 29.03.2025 | 14301 | Bayern Munich – St. Pauli | 3:2 | 5 |
| 2024/25 | 28 | 04.04.2025 | 14296 | Augsburg – Bayern Munich | 1:3 | 4 |
| 2024/25 | 29 | 12.04.2025 | 14281 | Bayern Munich – Dortmund | 2:2 | 4 |
| 2024/25 | 30 | 19.04.2025 | 14275 | Heidenheim – Bayern Munich | 0:4 | 4 |
| 2024/25 | 31 | 26.04.2025 | 14265 | Bayern Munich – Mainz | 3:0 | 3 |
| 2024/25 | 32 | 03.05.2025 | 14257 | RB Leipzig – Bayern Munich | 3:3 | 6 |
| 2024/25 | 33 | 10.05.2025 | 14246 | Bayern Munich – B. Monchengladbach | 2:0 | 2 |
| 2024/25 | 34 | 17.05.2025 | 14239 | Hoffenheim – Bayern Munich | 0:4 | 4 |
| 2025/26 | 1 | 22.08.2025 | 64488 | Bayern Munich – RB Leipzig | 6:0 | 6 |
| 2025/26 | 2 | 30.08.2025 | 64722 | Augsburg – Bayern Munich | 2:3 | 5 |

#### BL-3a: Hamburger SV (2 Tore / 2 Spiele = 1,0, vorläufig)

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Gesamttore |
|---|---|---|---|---|---|---|
| 2025/26 | 1 | 24.08.2025 | 64592 | B. Monchengladbach – Hamburger SV | 0:0 | 0 |
| 2025/26 | 2 | 29.08.2025 | 64659 | Hamburger SV – St. Pauli | 0:2 | 2 |

#### BL-3b: Wolfsburg (27 Tore / 10 Spiele = 2,7)

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Gesamttore |
|---|---|---|---|---|---|---|
| 2024/25 | 27 | 29.03.2025 | 14304 | Wolfsburg – Heidenheim | 0:1 | 1 |
| 2024/25 | 28 | 06.04.2025 | 14288 | Union Berlin – Wolfsburg | 1:0 | 1 |
| 2024/25 | 29 | 11.04.2025 | 14287 | Wolfsburg – RB Leipzig | 2:3 | 5 |
| 2024/25 | 30 | 19.04.2025 | 14276 | Mainz – Wolfsburg | 2:2 | 4 |
| 2024/25 | 31 | 26.04.2025 | 14268 | Wolfsburg – Freiburg | 0:1 | 1 |
| 2024/25 | 32 | 03.05.2025 | 14255 | Dortmund – Wolfsburg | 4:0 | 4 |
| 2024/25 | 33 | 09.05.2025 | 14251 | Wolfsburg – Hoffenheim | 2:2 | 4 |
| 2024/25 | 34 | 17.05.2025 | 14235 | B. Monchengladbach – Wolfsburg | 0:1 | 1 |
| 2025/26 | 1 | 23.08.2025 | 64551 | Heidenheim – Wolfsburg | 1:3 | 4 |
| 2025/26 | 2 | 31.08.2025 | 64775 | Wolfsburg – Mainz | 1:1 | 2 |

Kontrollsumme: Heimspiele 13 Tore + Auswärtsspiele 14 Tore = 27.

#### BL-3b: FC Koln (6 Tore / 2 Spiele = 3,0, vorläufig)

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Gesamttore |
|---|---|---|---|---|---|---|
| 2025/26 | 1 | 24.08.2025 | 64593 | Mainz – FC Koln | 0:1 | 1 |
| 2025/26 | 2 | 31.08.2025 | 64773 | FC Koln – Freiburg | 4:1 | 5 |

#### PL-3a: Manchester Utd (23 Tore / 10 Spiele = 2,3)

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Gesamttore |
|---|---|---|---|---|---|---|
| 2024/25 | 31 | 06.04.2025 | 14612 | Manchester Utd – Manchester City | 0:0 | 0 |
| 2024/25 | 32 | 13.04.2025 | 14602 | Newcastle – Manchester Utd | 4:1 | 5 |
| 2024/25 | 33 | 20.04.2025 | 14594 | Manchester Utd – Wolves | 0:1 | 1 |
| 2024/25 | 34 | 27.04.2025 | 14582 | Bournemouth – Manchester Utd | 1:1 | 2 |
| 2024/25 | 35 | 04.05.2025 | 14572 | Brentford – Manchester Utd | 4:3 | 7 |
| 2024/25 | 36 | 11.05.2025 | 14561 | Manchester Utd – West Ham | 0:2 | 2 |
| 2024/25 | 37 | 16.05.2025 | 14558 | Chelsea – Manchester Utd | 1:0 | 1 |
| 2024/25 | 38 | 25.05.2025 | 14544 | Manchester Utd – Aston Villa | 2:0 | 2 |
| 2025/26 | 1 | 17.08.2025 | 64402 | Manchester Utd – Arsenal | 0:1 | 1 |
| 2025/26 | 2 | 24.08.2025 | 64581 | Fulham – Manchester Utd | 1:1 | 2 |

#### PL-3a: Burnley (5 Tore / 2 Spiele = 2,5, vorläufig)

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Gesamttore |
|---|---|---|---|---|---|---|
| 2025/26 | 1 | 16.08.2025 | 64373 | Tottenham – Burnley | 3:0 | 3 |
| 2025/26 | 2 | 23.08.2025 | 64535 | Burnley – Sunderland | 2:0 | 2 |

#### PL-3b: Sunderland (5 Tore / 2 Spiele = 2,5, vorläufig)

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Gesamttore |
|---|---|---|---|---|---|---|
| 2025/26 | 1 | 16.08.2025 | 64372 | Sunderland – West Ham | 3:0 | 3 |
| 2025/26 | 2 | 23.08.2025 | 64535 | Burnley – Sunderland | 2:0 | 2 |

#### PL-3b: Brentford (30 Tore / 10 Spiele = 3,0)

| Saison | Gameday | Datum | id | Begegnung | Ergebnis | Gesamttore |
|---|---|---|---|---|---|---|
| 2024/25 | 31 | 06.04.2025 | 14613 | Brentford – Chelsea | 0:0 | 0 |
| 2024/25 | 32 | 12.04.2025 | 14606 | Arsenal – Brentford | 1:1 | 2 |
| 2024/25 | 33 | 19.04.2025 | 14596 | Brentford – Brighton | 4:2 | 6 |
| 2024/25 | 34 | 01.05.2025 | 14580 | Nottingham – Brentford | 0:2 | 2 |
| 2024/25 | 35 | 04.05.2025 | 14572 | Brentford – Manchester Utd | 4:3 | 7 |
| 2024/25 | 36 | 10.05.2025 | 14567 | Ipswich – Brentford | 0:1 | 1 |
| 2024/25 | 37 | 18.05.2025 | 14554 | Brentford – Fulham | 2:3 | 5 |
| 2024/25 | 38 | 25.05.2025 | 14549 | Wolves – Brentford | 1:1 | 2 |
| 2025/26 | 1 | 17.08.2025 | 64404 | Nottingham – Brentford | 3:1 | 4 |
| 2025/26 | 2 | 23.08.2025 | 64534 | Brentford – Aston Villa | 1:0 | 1 |

### 6.4 Kontrollpunkte für den Code

**Ligareferenz über das Saisonende**
- Bundesliga: 162 Spiele aus 2024/25 (Spieltage 17–34) + 18 aus 2025/26 (Spieltage 1–2) = 180.
- Premier League: 180 Spiele aus 2024/25 (Spieltage 21–38) + 20 aus 2025/26 (Spieltage 1–2) = 200.
- Spieltag 3 (2025/26) und alles danach darf nicht enthalten sein.
- Das Spiel ohne Statistik vom 14.12.2024 (id 14421, Spieltag 14) liegt ausserhalb des Referenzzeitraums und spielt hier keine Rolle.

**Nachholspiel: Filter nach `Gameday`, nicht nach Datum**
- id 14680 (Everton – Liverpool, Spieltag 15, gespielt am 12.02.2025) darf **nicht** in der Premier-League-Referenz enthalten sein, obwohl es zeitlich im Referenzzeitraum liegt. Ein Datumsfilter liefert 201 statt 200 Spiele.
- Die Nachholspiele des 29. Spieltags (id 14669, 14600) zählen korrekt mit.
- Bei der Kontrolle von KPI 04 am 29.10.2026 entdeckt, siehe `test_kpi04_gelbe_karten.md`, Abschnitt 7.4.

**Teamwerte über das Saisonende**
- Etablierte Teams: 8 Spiele aus 2024/25 + 2 aus 2025/26.
- FC Koln und Burnley: nur 2 Spiele, obwohl ältere Spiele (2023/24 und früher) in der Datenbank stehen. Saisonfenster wie bei KPI 01.
- Typischer Fehler bei Wolfsburg: Werden 11 statt 10 Spiele genommen (zusätzlich Augsburg – Wolfsburg 1:0, Spieltag 26), ergibt sich 28 / 10 = 2,8 oder 28 / 11 = 2,5 statt 2,7.
- Typischer Fehler: nur Heim- oder nur Auswärtsspiele summieren. Wolfsburg ergäbe dann 2,6 bzw. 2,8. Bei der Testkontrolle am 29.10.2026 tatsächlich aufgetreten (manuelle Excel-Rechnung), daher hier als Kontrollpunkt festgehalten.

**Aufsteiger mit Werten**
- Erstmals wird ein Torindikator mit einem Aufsteiger berechnet. Grundlage nur 2 Spiele → `vorlaeufig` true.
- `vorlaeufig` ist für die gesamte Begegnung true, sobald **ein** Team weniger als 10 Spiele hat.
- Burnley und Sunderland haben beide 2,5, weil ihr direktes Duell (id 64535, 2:0) in beiden Stichproben steckt.

**Rundung (zweiter Kontrollfall)**
- BL-3a: Torindikator 2,65 muss als **2,7** angezeigt werden. Python `round(2.65, 1)` ergibt fälschlich 2,6.
- BL-3b (2,85 → 2,9), PL-3b (2,75 → 2,8) und die PL-Ligareferenz (2,85 → 2,9) rundet `round()` zufällig richtig. Der Fehler tritt also nur bei manchen Werten auf. Darum braucht es mehrere Kontrollfälle (4,35 aus Abschnitt 3 und 2,65 hier).

**Zukunftsdaten**
- Das analysierte Spiel selbst darf nicht zählen. Beispiel: Wolfsburg – FC Koln 3:3 (id 64960). Mit diesem Spiel ergäbe sich für Wolfsburg 3,2 statt 2,7.

### 6.5 Beobachtungen

- **Referenzzeitraum wirkt stark:** Die Bundesliga-Referenz liegt hier bei 3,07, im Test zu Spieltag 1 bei 3,24. Dasselbe Spiel kann je nach Zeitpunkt anders eingestuft werden.
- **Keine Anomalie in diesem Durchgang:** Alle vier Abweichungen sind negativ und liegen im Normalbereich. Anomalien sind durch Abschnitt 3 abgedeckt.
- **Kleine Stichproben:** Der HSV-Wert von 1,0 beruht auf 2 Spielen. Die Kennzeichnung „vorläufig“ ist hier inhaltlich wichtig und muss im Dashboard gut sichtbar sein.
- **2-Tage-Regel nicht wirksam:** Jedes Team hat sein letztes Spiel mindestens 6 Tage vor dem Analysedatum. Absicherung über den geplanten ausgedachten Testdatensatz.

---

## 7. Weitere Tests (geplant)

- **Ausgedachter Testdatensatz** für Sonderfälle: 2-Tage-Regel (Spiele genau 1, 2 und 3 Tage vor dem Analysedatum), Team mit genau 1 Spiel, Abweichung genau ±20,0 % und ±35,0 % (Grenzfälle der Einstufung), fehlende Torwerte.
- **Praxistest 3. Spieltag 2026/27:** optional, sobald die Saison läuft. Zusätzlicher Realitätscheck, kein Ersatz für Abschnitt 6.
