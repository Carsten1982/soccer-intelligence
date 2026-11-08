# Testfall KPI 04 – Gelbe Karten

**Spezifikation v1.2** · Stand 08.11.2026

**Regelwerk:** `03_KPI_Regelwerk.md`, Abschnitte 1, 1.1, 2 und 6
**Datenbasis:** `Database-Soccer-Intelligence.xlsx`, SHA-256 `6d68583c2e66616e92c1bf3e8a8611b4b517bcf4c0a7a91c68101ea26a2284e2`
**Status:** Stand Spieltag 1 (2026/27) bestätigt am 28.10.2026 · Stand Spieltag 3 (2025/26) bestätigt am 29.10.2026 · Zusatztest fehlende Werte vorgeschlagen

**Änderung 08.11.2026 (Carsten, Etappe H): Anzeige mit zwei Nachkommastellen.** Alle angezeigten Werte (Teamwerte, Ligareferenz, Hauptwert, Abweichung) werden auf zwei Nachkommastellen gerundet; die Einstufung richtet sich nach der auf zwei Stellen gerundeten Abweichung (Regelwerk 2.3). Die JSON-Blöcke, Texte und Kontrollpunkte sind angepasst. **Keine Einstufung ändert sich** (24 von 24 geprüft). Exakte Rechenwerte in den Erläuterungen (z. B. „47 Tore / 10 Spiele = 4,7“) bleiben wie sie sind.

**Datenbasis aktualisiert am 30.10.2026:** neue SHA-256 nach Korrektur von zwei versehentlich überschriebenen Zellen in der Premier League (id 5393 `Gameday` „bitte“ → 4; id 99466 `FT Home Goals` „Ergebnisse stimmen.“ → 2). Alle erwarteten Werte wurden mit der neuen Datei nachgerechnet: unverändert (144 Prüfwerte, 0 Abweichungen).

Dieser Testfall ist die verbindliche Referenz für die technische Umsetzung. Der Code muss mit derselben Datenbasis exakt diese Ergebnisse liefern. Die JSON-Blöcke sind für automatische Tests gedacht und müssen exakt übereinstimmen.

---

## 1. Regeln, die dieser Testfall prüft

- Teamwert = Ø **eigene** gelbe Karten des Teams in den letzten 10 Ligaspielen. Gegnerische Karten zählen nicht.
- Quelle: Spalte AC `Home Yellow Cards Full Time`, wenn das Team Heimteam ist; Spalte AD `Away Yellow Cards Full Time`, wenn es Auswärtsteam ist. Rote Karten zählen nicht.
- Erwartete gelbe Karten = Teamwert Heim **+** Teamwert Auswärts (Summe, nicht Durchschnitt).
- Ligareferenz = Ø gelbe Karten **beider** Teams pro Spiel in den letzten 20 Spieltagen laut `Gameday`.
- Relative Abweichung = (Erwartete gelbe Karten − Ligareferenz) / Ligareferenz × 100.
- Fehlender Kartenwert: Spiel wird ausgelassen und nicht durch ein älteres ersetzt (Teamwert und Ligareferenz).
- Anomalie-Schwellenwerte, Rundung und Vorzeichen gemäss Regelwerk Abschnitt 2.

---

## 2. Auswahl- und Rechenschritte (feste Reihenfolge)

### 2.1 Teamwert (für jedes Team einzeln)

1. Ligablatt des analysierten Spiels wählen.
2. Alle Zeilen, in denen das Team `homeTeam` oder `awayTeam` ist (exakte Schreibweise).
3. Nur `Season` = Saison des analysierten Spiels oder Vorsaison.
4. Nur Spiele mit `Date` ≤ Analysedatum − 2 Kalendertage.
5. Sortierung aufsteigend nach `Date`, dann Uhrzeit aus `matchDate`, dann `id`.
6. **Die letzten 10 Spiele nehmen.**
7. **Danach** Spiele ohne Kartenwert des Teams (leere Zelle in AC bzw. AD) entfernen. Es wird **kein** älteres Spiel nachgezogen. Die Stichprobe sinkt (z. B. 9 statt 10).
8. Eigene Karten je Spiel: AC wenn Heimteam, AD wenn Auswärtsteam.
9. Teamwert = Summe eigene Karten / Anzahl verbleibender Spiele (ungerundet weiterrechnen).
10. Bei 0 Spielen: Teamwert nicht verfügbar. Bei 1–9 Spielen: Teamwert berechnen, „vorläufig“.

**Wichtig:** Die Reihenfolge von Schritt 6 und 7 ist entscheidend. Wer zuerst die leeren Werte entfernt und dann die letzten 10 nimmt, zieht ein älteres Spiel nach und verstösst gegen das Regelwerk.

### 2.2 Ligareferenz

1. Die 20 Spieltage vor dem Spieltag des analysierten Spiels bestimmen (`Season` + `Gameday`, über das Saisonende hinweg).
2. Nur abgeschlossene Spiele.
3. Spiele, in denen AC **oder** AD leer ist, auslassen.
4. Ligareferenz = Summe (AC + AD) / Anzahl verbleibender Spiele (ungerundet weiterrechnen).

### 2.3 Erwartungswert, Abweichung, Anomalie

1. Fehlt ein Teamwert → Erwartungswert, Abweichung und Anomalie nicht verfügbar. Ende.
2. Erwartete gelbe Karten = Teamwert Heim + Teamwert Auswärts.
3. Fehlt die Ligareferenz oder ist sie 0 → Abweichung und Anomalie nicht verfügbar.
4. Abweichung = (Erwartungswert − Ligareferenz) / Ligareferenz × 100, mit ungerundeten Werten.
5. Rundung erst am Ende auf eine Nachkommastelle, kaufmännisch, mit Dezimalarithmetik.
6. Anomalie anhand der gerundeten Abweichung (zwei Nachkommastellen): |x| ≤ 20,00 keine · 20,00 < |x| ≤ 35,00 leicht · |x| > 35,00 stark.

---

## 3. Stand Spieltag 1 (Saison 2026/27)

**Ausgangslage:** Die Datenbank enthält noch keine Spiele der Saison 2026/27. Teamwerte und Ligareferenz stammen vollständig aus der Saison 2025/26. In keinem verwendeten Spiel fehlt ein Kartenwert.

### 3.1 Eingabeparameter

| Testfall | Liga | Saison | Spieltag | Analysedatum | Heimteam | Auswärtsteam |
|---|---|---|---|---|---|---|
| BL-1 | Bundesliga | 2026/2027 | 1 | 2026-08-22 | Bayern Munich | Stuttgart |
| BL-2 | Bundesliga | 2026/2027 | 1 | 2026-08-22 | Elversberg | Bayer Leverkusen |
| PL-1 | Premier League | 2026/2027 | 1 | 2026-08-22 | Newcastle | Liverpool |
| PL-2 | Premier League | 2026/2027 | 1 | 2026-08-22 | Hull | Manchester Utd |

Analysedatum 2026-08-22 ist ein Platzhalter (siehe `test_kpi01_formkurve.md`).

### 3.2 Erwartete Ergebnisse (maschinenlesbar)

```json
[
  {
    "testfall": "BL-1",
    "liga": "Bundesliga", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "heim":      {"team": "Bayern Munich",    "spiele": 10, "karten": 17, "teamwert_roh": 1.7, "teamwert": "1.70"},
    "auswaerts": {"team": "Stuttgart",        "spiele": 10, "karten": 16, "teamwert_roh": 1.6, "teamwert": "1.60"},
    "ligareferenz": {"saison_spieltage": "2025/2026: 15-34", "spiele": 180, "karten": 652, "wert_roh": 3.6222222222, "wert": "3.62"},
    "erwartet_roh": 3.3, "erwartet": "3.30",
    "abweichung_roh": -8.8957055215, "abweichung": "-8.90",
    "anomalie": "keine", "richtung": "negativ", "vorlaeufig": false,
    "ueberschrift": "Keine statistische Besonderheit",
    "text": "Der Kartenindikator dieser Begegnung liegt bei 3,30 gelben Karten. Die Abweichung vom Liga-Durchschnitt beträgt −8,90 %."
  },
  {
    "testfall": "BL-2",
    "liga": "Bundesliga", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "heim":      {"team": "Elversberg",       "spiele": 0,  "karten": null, "teamwert_roh": null, "teamwert": null},
    "auswaerts": {"team": "Bayer Leverkusen", "spiele": 10, "karten": 18,   "teamwert_roh": 1.8,  "teamwert": "1.80"},
    "ligareferenz": {"saison_spieltage": "2025/2026: 15-34", "spiele": 180, "karten": 652, "wert_roh": 3.6222222222, "wert": "3.62"},
    "erwartet_roh": null, "erwartet": null,
    "abweichung_roh": null, "abweichung": null,
    "anomalie": null, "richtung": null, "vorlaeufig": true,
    "ueberschrift": null, "text": null
  },
  {
    "testfall": "PL-1",
    "liga": "Premier League", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "heim":      {"team": "Newcastle",        "spiele": 10, "karten": 20, "teamwert_roh": 2.0, "teamwert": "2.00"},
    "auswaerts": {"team": "Liverpool",        "spiele": 10, "karten": 14, "teamwert_roh": 1.4, "teamwert": "1.40"},
    "ligareferenz": {"saison_spieltage": "2025/2026: 19-38", "spiele": 200, "karten": 781, "wert_roh": 3.905, "wert": "3.91"},
    "erwartet_roh": 3.4, "erwartet": "3.40",
    "abweichung_roh": -12.9321382843, "abweichung": "-12.93",
    "anomalie": "keine", "richtung": "negativ", "vorlaeufig": false,
    "ueberschrift": "Keine statistische Besonderheit",
    "text": "Der Kartenindikator dieser Begegnung liegt bei 3,40 gelben Karten. Die Abweichung vom Liga-Durchschnitt beträgt −12,93 %."
  },
  {
    "testfall": "PL-2",
    "liga": "Premier League", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "heim":      {"team": "Hull",             "spiele": 0,  "karten": null, "teamwert_roh": null, "teamwert": null},
    "auswaerts": {"team": "Manchester Utd",   "spiele": 10, "karten": 24,   "teamwert_roh": 2.4,  "teamwert": "2.40"},
    "ligareferenz": {"saison_spieltage": "2025/2026: 19-38", "spiele": 200, "karten": 781, "wert_roh": 3.905, "wert": "3.91"},
    "erwartet_roh": null, "erwartet": null,
    "abweichung_roh": null, "abweichung": null,
    "anomalie": null, "richtung": null, "vorlaeufig": true,
    "ueberschrift": null, "text": null
  }
]
```

Hinweise zum JSON:
- Gerundete Werte als Text mit Punkt; im Dashboard mit Komma. Im Kennzahlenfeld mit Vorzeichen („−8,90 %“), Minuszeichen U+2212 im Frontend-Text.
- `_roh`-Werte mit Toleranz 1e-9 vergleichen, weil Gleitkomma-Rechnungen kleine Ungenauigkeiten erzeugen können.

### 3.3 Eingabedaten zum Nachvollziehen

Spalte „Karten H:A“ zeigt die Werte aus AC:AD, Spalte „Eigene“ den Wert, der für das Team zählt.

#### Ligareferenz Bundesliga (2025/26, Spieltage 15–34)

Je Spieltag 9 Spiele, kein fehlender Wert. Gelbe Karten pro Spieltag:

| Spieltag | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 |
|---|---|---|---|---|---|---|---|---|---|---|
| Karten | 29 | 32 | 22 | 38 | 25 | 40 | 32 | 33 | 47 | 31 |

| Spieltag | 25 | 26 | 27 | 28 | 29 | 30 | 31 | 32 | 33 | 34 |
|---|---|---|---|---|---|---|---|---|---|---|
| Karten | 26 | 32 | 40 | 38 | 36 | 31 | 24 | 37 | 27 | 32 |

Summe: 652 Karten in 180 Spielen → 3,6222…

#### Ligareferenz Premier League (2025/26, Spieltage 19–38)

Je Spieltag 10 Spiele, kein fehlender Wert. Gelbe Karten pro Spieltag:

| Spieltag | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 |
|---|---|---|---|---|---|---|---|---|---|---|
| Karten | 33 | 32 | 44 | 47 | 31 | 43 | 36 | 39 | 43 | 49 |

| Spieltag | 29 | 30 | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 |
|---|---|---|---|---|---|---|---|---|---|---|
| Karten | 43 | 33 | 38 | 35 | 33 | 44 | 44 | 41 | 37 | 36 |

Summe: 781 Karten in 200 Spielen → 3,905

#### BL-1: Bayern Munich (17 Karten / 10 Spiele = 1,7)

| Gameday | Datum | id | Begegnung | Sicht | Karten H:A | Eigene |
|---|---|---|---|---|---|---|
| 25 | 06.03.2026 | 99487 | Bayern Munich – B. Monchengladbach | Heim | 1:0 | 1 |
| 26 | 14.03.2026 | 106579 | Bayer Leverkusen – Bayern Munich | Auswärts | 3:4 | 4 |
| 27 | 21.03.2026 | 114288 | Bayern Munich – Union Berlin | Heim | 1:2 | 1 |
| 28 | 04.04.2026 | 117437 | Freiburg – Bayern Munich | Auswärts | 3:3 | 3 |
| 29 | 11.04.2026 | 117903 | St. Pauli – Bayern Munich | Auswärts | 1:2 | 2 |
| 30 | 19.04.2026 | 118339 | Bayern Munich – Stuttgart | Heim | 0:0 | 0 |
| 31 | 25.04.2026 | 118648 | Mainz – Bayern Munich | Auswärts | 1:2 | 2 |
| 32 | 02.05.2026 | 118984 | Bayern Munich – Heidenheim | Heim | 3:2 | 3 |
| 33 | 09.05.2026 | 119271 | Wolfsburg – Bayern Munich | Auswärts | 1:0 | 0 |
| 34 | 16.05.2026 | 120509 | Bayern Munich – FC Koln | Heim | 1:1 | 1 |

#### BL-1: Stuttgart (16 Karten / 10 Spiele = 1,6)

| Gameday | Datum | id | Begegnung | Sicht | Karten H:A | Eigene |
|---|---|---|---|---|---|---|
| 25 | 07.03.2026 | 99520 | Mainz – Stuttgart | Auswärts | 0:2 | 2 |
| 26 | 15.03.2026 | 107988 | Stuttgart – RB Leipzig | Heim | 1:2 | 1 |
| 27 | 22.03.2026 | 114388 | Augsburg – Stuttgart | Auswärts | 1:3 | 3 |
| 28 | 04.04.2026 | 117441 | Stuttgart – Dortmund | Heim | 2:4 | 2 |
| 29 | 12.04.2026 | 118014 | Stuttgart – Hamburger SV | Heim | 2:1 | 2 |
| 30 | 19.04.2026 | 118339 | Bayern Munich – Stuttgart | Auswärts | 0:0 | 0 |
| 31 | 26.04.2026 | 118750 | Stuttgart – Werder Bremen | Heim | 0:1 | 0 |
| 32 | 02.05.2026 | 118986 | Hoffenheim – Stuttgart | Auswärts | 3:1 | 1 |
| 33 | 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | Heim | 2:1 | 2 |
| 34 | 16.05.2026 | 120510 | Eintracht Frankfurt – Stuttgart | Auswärts | 2:3 | 3 |

#### BL-2: Elversberg

Keine Spiele in der Datenbank (Aufsteiger).

#### BL-2: Bayer Leverkusen (18 Karten / 10 Spiele = 1,8)

| Gameday | Datum | id | Begegnung | Sicht | Karten H:A | Eigene |
|---|---|---|---|---|---|---|
| 25 | 07.03.2026 | 99518 | Freiburg – Bayer Leverkusen | Auswärts | 3:3 | 3 |
| 26 | 14.03.2026 | 106579 | Bayer Leverkusen – Bayern Munich | Heim | 3:4 | 3 |
| 27 | 21.03.2026 | 114290 | Heidenheim – Bayer Leverkusen | Auswärts | 4:4 | 4 |
| 28 | 04.04.2026 | 117436 | Bayer Leverkusen – Wolfsburg | Heim | 1:3 | 1 |
| 29 | 11.04.2026 | 117899 | Dortmund – Bayer Leverkusen | Auswärts | 3:0 | 0 |
| 30 | 18.04.2026 | 118240 | Bayer Leverkusen – Augsburg | Heim | 2:1 | 2 |
| 31 | 25.04.2026 | 118646 | FC Koln – Bayer Leverkusen | Auswärts | 1:2 | 2 |
| 32 | 02.05.2026 | 118989 | Bayer Leverkusen – RB Leipzig | Heim | 1:3 | 1 |
| 33 | 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | Auswärts | 2:1 | 1 |
| 34 | 16.05.2026 | 120508 | Bayer Leverkusen – Hamburger SV | Heim | 1:2 | 1 |

#### PL-1: Newcastle (20 Karten / 10 Spiele = 2,0)

| Gameday | Datum | id | Begegnung | Sicht | Karten H:A | Eigene |
|---|---|---|---|---|---|---|
| 29 | 04.03.2026 | 99466 | Newcastle – Manchester Utd | Heim | 4:3 | 4 |
| 30 | 14.03.2026 | 106538 | Chelsea – Newcastle | Auswärts | 2:2 | 2 |
| 31 | 22.03.2026 | 114378 | Newcastle – Sunderland | Heim | 1:6 | 1 |
| 32 | 12.04.2026 | 118005 | Crystal Palace – Newcastle | Auswärts | 0:3 | 3 |
| 33 | 18.04.2026 | 118200 | Newcastle – Bournemouth | Heim | 2:4 | 2 |
| 34 | 25.04.2026 | 118606 | Arsenal – Newcastle | Auswärts | 2:2 | 2 |
| 35 | 02.05.2026 | 118932 | Newcastle – Brighton | Heim | 3:3 | 3 |
| 36 | 10.05.2026 | 119352 | Nottingham – Newcastle | Auswärts | 2:0 | 0 |
| 37 | 17.05.2026 | 120593 | Newcastle – West Ham | Heim | 1:3 | 1 |
| 38 | 24.05.2026 | 120844 | Fulham – Newcastle | Auswärts | 2:2 | 2 |

#### PL-1: Liverpool (14 Karten / 10 Spiele = 1,4)

| Gameday | Datum | id | Begegnung | Sicht | Karten H:A | Eigene |
|---|---|---|---|---|---|---|
| 29 | 03.03.2026 | 99447 | Wolves – Liverpool | Auswärts | 2:1 | 1 |
| 30 | 15.03.2026 | 107981 | Liverpool – Tottenham | Heim | 0:0 | 0 |
| 31 | 21.03.2026 | 114243 | Brighton – Liverpool | Auswärts | 5:5 | 5 |
| 32 | 11.04.2026 | 117862 | Liverpool – Fulham | Heim | 0:0 | 0 |
| 33 | 19.04.2026 | 118327 | Everton – Liverpool | Auswärts | 2:0 | 0 |
| 34 | 25.04.2026 | 118603 | Liverpool – Crystal Palace | Heim | 1:3 | 1 |
| 35 | 03.05.2026 | 119075 | Manchester Utd – Liverpool | Auswärts | 2:2 | 2 |
| 36 | 09.05.2026 | 119250 | Liverpool – Chelsea | Heim | 2:4 | 2 |
| 37 | 15.05.2026 | 120476 | Aston Villa – Liverpool | Auswärts | 3:1 | 1 |
| 38 | 24.05.2026 | 120845 | Liverpool – Brentford | Heim | 2:3 | 2 |

#### PL-2: Hull

Keine Spiele in der Datenbank (Aufsteiger).

#### PL-2: Manchester Utd (24 Karten / 10 Spiele = 2,4)

| Gameday | Datum | id | Begegnung | Sicht | Karten H:A | Eigene |
|---|---|---|---|---|---|---|
| 29 | 04.03.2026 | 99466 | Newcastle – Manchester Utd | Auswärts | 4:3 | 3 |
| 30 | 15.03.2026 | 107979 | Manchester Utd – Aston Villa | Heim | 3:2 | 3 |
| 31 | 20.03.2026 | 114203 | Bournemouth – Manchester Utd | Auswärts | 2:2 | 2 |
| 32 | 13.04.2026 | 118082 | Manchester Utd – Leeds | Heim | 3:2 | 3 |
| 33 | 18.04.2026 | 118202 | Chelsea – Manchester Utd | Auswärts | 1:3 | 3 |
| 34 | 27.04.2026 | 118824 | Manchester Utd – Brentford | Heim | 2:4 | 2 |
| 35 | 03.05.2026 | 119075 | Manchester Utd – Liverpool | Heim | 2:2 | 2 |
| 36 | 09.05.2026 | 119253 | Sunderland – Manchester Utd | Auswärts | 0:3 | 3 |
| 37 | 17.05.2026 | 120588 | Manchester Utd – Nottingham | Heim | 2:1 | 2 |
| 38 | 24.05.2026 | 120841 | Brighton – Manchester Utd | Auswärts | 0:1 | 1 |

---

## 4. Kontrollpunkte für den Code

### 4.1 Eigene Karten
- Direkte Duelle müssen spiegelbildlich zugeordnet werden: id 106579 (Leverkusen 3 / Bayern 4), id 118339 (Bayern 0 / Stuttgart 0), id 119270 (Stuttgart 2 / Leverkusen 1), id 99466 (Newcastle 4 / Man Utd 3), id 119075 (Man Utd 2 / Liverpool 2).
- Typischer Fehler: Summe beider Teams statt eigener Karten. Bayern hätte dann 37 statt 17 Karten (Teamwert 3,7 statt 1,7).
- Typischer Fehler: Spalte AC immer verwenden, egal ob Heim oder Auswärts.

### 4.2 Summe statt Durchschnitt
- Erwartete gelbe Karten = **Summe** der Teamwerte (BL-1: 3,30), nicht deren Durchschnitt (1,65). Unterschied zu KPI 02 und 03.

### 4.3 Ligareferenz
- Ligareferenz = Karten **beider** Teams pro Spiel (Bundesliga 3,62, Premier League 3,91).
- Bundesliga genau 180, Premier League genau 200 Spiele; kein fehlender Kartenwert.

### 4.4 Negative Abweichungen
- BL-1 (−8,90 %) und PL-1 (−12,93 %) sind die ersten negativen Werte im Testset. `richtung` muss `negativ` sein, das Kennzahlenfeld zeigt das Vorzeichen.

### 4.5 Aufsteiger
- Elversberg und Hull: Teamwert, Erwartungswert, Abweichung und Anomalie `null`, **keine Fehlermeldung**.
- Teamwert des Gegners (Leverkusen 1,80 / Man Utd 2,40) und Ligareferenz werden trotzdem berechnet.

---

## 5. Annahmen und Empfehlungen

1. ~~**Vorzeichen im Text „Keine Anomalie“ (Empfehlung)**~~ **Übernommen am 30.10.2026** (Regelwerk 2.4): Vorzeichen steht immer, bei 0,0 % keins. Gilt einheitlich für KPI 02 und KPI 04.
2. **KPI-Karte bei Aufsteiger-Spielen:** wie bei KPI 02 (Abschnitt 5, Punkt 1): Teamwert des Gegners und Ligareferenz werden angezeigt, Hauptwert, Abweichung und Anomalie als „–“.
3. **Datenquelle:** Name der Datenquelle noch nicht dokumentiert (Regelwerk, offener Punkt 7). Für die Berechnung nicht relevant.

---

## 6. Zusatztest fehlende Kartenwerte (vorgeschlagen, noch nicht berechnet)

**Zweck:** Die Regel „fehlender Kartenwert → Spiel auslassen, nicht nachziehen, vorläufig“ wird durch Spieltag 1 und 3 nicht abgedeckt, weil dort kein Kartenwert fehlt.

**Vorschlag:** Ein Spiel von Union Berlin oder Bochum am 15. Spieltag der Saison 2024/25 analysieren. Das Spiel Union Berlin – Bochum vom 14.12.2024 (id 14421, Spieltag 14) hat keine Statistikwerte (siehe `02_Datenbasis.md`, Abschnitt 4.1).

**Erwartetes Verhalten:**
- Teamwert: Stichprobe 9 statt 10 Spiele, kein älteres Spiel nachgezogen, „vorläufig“.
- Ligareferenz: id 14421 liegt in den letzten 20 Spieltagen und wird ausgelassen, also 179 statt 180 Spiele.
- KPI 02 und 03 desselben Spiels: id 14421 **zählt mit** (Tore 1:1 sind vorhanden), also 10 Spiele und 180 Referenzspiele. Guter Test dafür, dass „fehlender Wert“ je KPI unterschiedlich wirkt.

---

## 7. Stand Spieltag 3 (Saison 2025/26)

**Warum ein historischer Spieltag:** siehe `test_kpi01_formkurve.md`, Abschnitt 4.

**Ausgangslage:** Teamwerte und Ligareferenz setzen sich aus zwei Saisons zusammen. Die analysierten Spiele und alle späteren Spiele stehen in der Datenbank und dürfen nicht verwendet werden. In keinem verwendeten Spiel fehlt ein Kartenwert.

### 7.1 Eingabeparameter

| Testfall | Liga | Saison | Spieltag | Analysedatum | Heimteam | Auswärtsteam | id in DB |
|---|---|---|---|---|---|---|---|
| BL-3a | Bundesliga | 2025/2026 | 3 | 2025-09-13 | Bayern Munich | Hamburger SV | 64955 |
| BL-3b | Bundesliga | 2025/2026 | 3 | 2025-09-13 | Wolfsburg | FC Koln | 64960 |
| PL-3a | Premier League | 2025/2026 | 3 | 2025-08-30 | Manchester Utd | Burnley | 64707 |
| PL-3b | Premier League | 2025/2026 | 3 | 2025-08-30 | Sunderland | Brentford | 64708 |

### 7.2 Erwartete Ergebnisse (maschinenlesbar)

```json
[
  {
    "testfall": "BL-3a",
    "liga": "Bundesliga", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-09-13",
    "heim":      {"team": "Bayern Munich",  "spiele": 10, "karten": 14, "teamwert_roh": 1.4, "teamwert": "1.40"},
    "auswaerts": {"team": "Hamburger SV",   "spiele": 2,  "karten": 4,  "teamwert_roh": 2.0, "teamwert": "2.00"},
    "ligareferenz": {"saison_spieltage": "2024/2025: 17-34 + 2025/2026: 1-2", "spiele": 180, "karten": 672, "wert_roh": 3.7333333333, "wert": "3.73"},
    "erwartet_roh": 3.4, "erwartet": "3.40",
    "abweichung_roh": -8.9285714286, "abweichung": "-8.93",
    "anomalie": "keine", "richtung": "negativ", "vorlaeufig": true,
    "ueberschrift": "Keine statistische Besonderheit",
    "text": "Der Kartenindikator dieser Begegnung liegt bei 3,40 gelben Karten. Die Abweichung vom Liga-Durchschnitt beträgt −8,93 %."
  },
  {
    "testfall": "BL-3b",
    "liga": "Bundesliga", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-09-13",
    "heim":      {"team": "Wolfsburg",      "spiele": 10, "karten": 17, "teamwert_roh": 1.7, "teamwert": "1.70"},
    "auswaerts": {"team": "FC Koln",        "spiele": 2,  "karten": 4,  "teamwert_roh": 2.0, "teamwert": "2.00"},
    "ligareferenz": {"saison_spieltage": "2024/2025: 17-34 + 2025/2026: 1-2", "spiele": 180, "karten": 672, "wert_roh": 3.7333333333, "wert": "3.73"},
    "erwartet_roh": 3.7, "erwartet": "3.70",
    "abweichung_roh": -0.8928571429, "abweichung": "-0.89",
    "anomalie": "keine", "richtung": "negativ", "vorlaeufig": true,
    "ueberschrift": "Keine statistische Besonderheit",
    "text": "Der Kartenindikator dieser Begegnung liegt bei 3,70 gelben Karten. Die Abweichung vom Liga-Durchschnitt beträgt −0,89 %."
  },
  {
    "testfall": "PL-3a",
    "liga": "Premier League", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-08-30",
    "heim":      {"team": "Manchester Utd", "spiele": 10, "karten": 21, "teamwert_roh": 2.1, "teamwert": "2.10"},
    "auswaerts": {"team": "Burnley",        "spiele": 2,  "karten": 0,  "teamwert_roh": 0.0, "teamwert": "0.00"},
    "ligareferenz": {"saison_spieltage": "2024/2025: 21-38 + 2025/2026: 1-2", "spiele": 200, "karten": 692, "wert_roh": 3.46, "wert": "3.46"},
    "erwartet_roh": 2.1, "erwartet": "2.10",
    "abweichung_roh": -39.3063583815, "abweichung": "-39.31",
    "anomalie": "stark", "richtung": "negativ", "vorlaeufig": true,
    "ueberschrift": "Unterdurchschnittlich viele gelbe Karten",
    "text": "In dieser Partie werden 2,10 gelbe Karten erwartet. Das liegt 39,31 % unter dem Liga-Durchschnitt."
  },
  {
    "testfall": "PL-3b",
    "liga": "Premier League", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-08-30",
    "heim":      {"team": "Sunderland",     "spiele": 2,  "karten": 1,  "teamwert_roh": 0.5, "teamwert": "0.50"},
    "auswaerts": {"team": "Brentford",      "spiele": 10, "karten": 20, "teamwert_roh": 2.0, "teamwert": "2.00"},
    "ligareferenz": {"saison_spieltage": "2024/2025: 21-38 + 2025/2026: 1-2", "spiele": 200, "karten": 692, "wert_roh": 3.46, "wert": "3.46"},
    "erwartet_roh": 2.5, "erwartet": "2.50",
    "abweichung_roh": -27.7456647399, "abweichung": "-27.75",
    "anomalie": "leicht", "richtung": "negativ", "vorlaeufig": true,
    "ueberschrift": "Unterdurchschnittlich viele gelbe Karten",
    "text": "In dieser Partie werden 2,50 gelbe Karten erwartet. Das liegt 27,75 % unter dem Liga-Durchschnitt."
  }
]
```

### 7.3 Eingabedaten zum Nachvollziehen

#### Ligareferenz Bundesliga (2024/25 Spieltage 17–34 + 2025/26 Spieltage 1–2)

Je Spieltag 9 Spiele, kein fehlender Wert. Gelbe Karten pro Spieltag:

| Spieltag 24/25 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 |
|---|---|---|---|---|---|---|---|---|---|
| Karten | 36 | 34 | 39 | 47 | 43 | 29 | 36 | 29 | 35 |

| Spieltag 24/25 | 26 | 27 | 28 | 29 | 30 | 31 | 32 | 33 | 34 |
|---|---|---|---|---|---|---|---|---|---|
| Karten | 33 | 31 | 25 | 31 | 37 | 26 | 24 | 22 | 24 |

| Spieltag 25/26 | 1 | 2 |
|---|---|---|
| Karten | 45 | 46 |

Summe: 581 + 91 = 672 Karten in 162 + 18 = 180 Spielen → 3,7333…

#### Ligareferenz Premier League (2024/25 Spieltage 21–38 + 2025/26 Spieltage 1–2)

Je Spieltag 10 Spiele, kein fehlender Wert. Gelbe Karten pro Spieltag:

| Spieltag 24/25 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 |
|---|---|---|---|---|---|---|---|---|---|
| Karten | 31 | 44 | 40 | 36 | 26 | 37 | 31 | 34 | 29 |

| Spieltag 24/25 | 30 | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 |
|---|---|---|---|---|---|---|---|---|---|
| Karten | 32 | 39 | 39 | 39 | 35 | 38 | 32 | 36 | 26 |

| Spieltag 25/26 | 1 | 2 |
|---|---|---|
| Karten | 30 | 38 |

Summe: 624 + 68 = 692 Karten in 180 + 20 = 200 Spielen → 3,46

**Nachholspiele im Zeitraum:** Spieltag 29 enthält zwei Nachholspiele (id 14669 vom 19.02.2025, id 14600 vom 16.04.2025), die korrekt mitzählen. Das Nachholspiel des 15. Spieltags (id 14680, Everton – Liverpool, 12.02.2025, 4:4 Karten) liegt zeitlich im Zeitraum, zählt aber **nicht** mit (siehe 7.4).

#### BL-3a: Bayern Munich (14 Karten / 10 Spiele = 1,4)

| Saison | Gameday | Datum | id | Begegnung | Sicht | Karten H:A | Eigene |
|---|---|---|---|---|---|---|---|
| 24/25 | 27 | 29.03.2025 | 14301 | Bayern Munich – St. Pauli | Heim | 3:0 | 3 |
| 24/25 | 28 | 04.04.2025 | 14296 | Augsburg – Bayern Munich | Auswärts | 4:0 | 0 |
| 24/25 | 29 | 12.04.2025 | 14281 | Bayern Munich – Dortmund | Heim | 0:0 | 0 |
| 24/25 | 30 | 19.04.2025 | 14275 | Heidenheim – Bayern Munich | Auswärts | 3:1 | 1 |
| 24/25 | 31 | 26.04.2025 | 14265 | Bayern Munich – Mainz | Heim | 0:0 | 0 |
| 24/25 | 32 | 03.05.2025 | 14257 | RB Leipzig – Bayern Munich | Auswärts | 3:1 | 1 |
| 24/25 | 33 | 10.05.2025 | 14246 | Bayern Munich – B. Monchengladbach | Heim | 1:1 | 1 |
| 24/25 | 34 | 17.05.2025 | 14239 | Hoffenheim – Bayern Munich | Auswärts | 0:0 | 0 |
| 25/26 | 1 | 22.08.2025 | 64488 | Bayern Munich – RB Leipzig | Heim | 4:1 | 4 |
| 25/26 | 2 | 30.08.2025 | 64722 | Augsburg – Bayern Munich | Auswärts | 3:4 | 4 |

#### BL-3a: Hamburger SV (4 Karten / 2 Spiele = 2,0, vorläufig)

| Saison | Gameday | Datum | id | Begegnung | Sicht | Karten H:A | Eigene |
|---|---|---|---|---|---|---|---|
| 25/26 | 1 | 24.08.2025 | 64592 | B. Monchengladbach – Hamburger SV | Auswärts | 2:1 | 1 |
| 25/26 | 2 | 29.08.2025 | 64659 | Hamburger SV – St. Pauli | Heim | 3:3 | 3 |

#### BL-3b: Wolfsburg (17 Karten / 10 Spiele = 1,7)

| Saison | Gameday | Datum | id | Begegnung | Sicht | Karten H:A | Eigene |
|---|---|---|---|---|---|---|---|
| 24/25 | 27 | 29.03.2025 | 14304 | Wolfsburg – Heidenheim | Heim | 2:4 | 2 |
| 24/25 | 28 | 06.04.2025 | 14288 | Union Berlin – Wolfsburg | Auswärts | 0:1 | 1 |
| 24/25 | 29 | 11.04.2025 | 14287 | Wolfsburg – RB Leipzig | Heim | 2:3 | 2 |
| 24/25 | 30 | 19.04.2025 | 14276 | Mainz – Wolfsburg | Auswärts | 2:3 | 3 |
| 24/25 | 31 | 26.04.2025 | 14268 | Wolfsburg – Freiburg | Heim | 3:1 | 3 |
| 24/25 | 32 | 03.05.2025 | 14255 | Dortmund – Wolfsburg | Auswärts | 0:0 | 0 |
| 24/25 | 33 | 09.05.2025 | 14251 | Wolfsburg – Hoffenheim | Heim | 0:2 | 0 |
| 24/25 | 34 | 17.05.2025 | 14235 | B. Monchengladbach – Wolfsburg | Auswärts | 0:0 | 0 |
| 25/26 | 1 | 23.08.2025 | 64551 | Heidenheim – Wolfsburg | Auswärts | 2:3 | 3 |
| 25/26 | 2 | 31.08.2025 | 64775 | Wolfsburg – Mainz | Heim | 3:5 | 3 |

#### BL-3b: FC Koln (4 Karten / 2 Spiele = 2,0, vorläufig)

| Saison | Gameday | Datum | id | Begegnung | Sicht | Karten H:A | Eigene |
|---|---|---|---|---|---|---|---|
| 25/26 | 1 | 24.08.2025 | 64593 | Mainz – FC Koln | Auswärts | 0:2 | 2 |
| 25/26 | 2 | 31.08.2025 | 64773 | FC Koln – Freiburg | Heim | 2:1 | 2 |

#### PL-3a: Manchester Utd (21 Karten / 10 Spiele = 2,1)

| Saison | Gameday | Datum | id | Begegnung | Sicht | Karten H:A | Eigene |
|---|---|---|---|---|---|---|---|
| 24/25 | 31 | 06.04.2025 | 14612 | Manchester Utd – Manchester City | Heim | 3:2 | 3 |
| 24/25 | 32 | 13.04.2025 | 14602 | Newcastle – Manchester Utd | Auswärts | 0:2 | 2 |
| 24/25 | 33 | 20.04.2025 | 14594 | Manchester Utd – Wolves | Heim | 2:3 | 2 |
| 24/25 | 34 | 27.04.2025 | 14582 | Bournemouth – Manchester Utd | Auswärts | 4:2 | 2 |
| 24/25 | 35 | 04.05.2025 | 14572 | Brentford – Manchester Utd | Auswärts | 0:2 | 2 |
| 24/25 | 36 | 11.05.2025 | 14561 | Manchester Utd – West Ham | Heim | 0:1 | 0 |
| 24/25 | 37 | 16.05.2025 | 14558 | Chelsea – Manchester Utd | Auswärts | 1:6 | 6 |
| 24/25 | 38 | 25.05.2025 | 14544 | Manchester Utd – Aston Villa | Heim | 2:2 | 2 |
| 25/26 | 1 | 17.08.2025 | 64402 | Manchester Utd – Arsenal | Heim | 1:4 | 1 |
| 25/26 | 2 | 24.08.2025 | 64581 | Fulham – Manchester Utd | Auswärts | 1:1 | 1 |

#### PL-3a: Burnley (0 Karten / 2 Spiele = 0,0, vorläufig)

| Saison | Gameday | Datum | id | Begegnung | Sicht | Karten H:A | Eigene |
|---|---|---|---|---|---|---|---|
| 25/26 | 1 | 16.08.2025 | 64373 | Tottenham – Burnley | Auswärts | 0:0 | 0 |
| 25/26 | 2 | 23.08.2025 | 64535 | Burnley – Sunderland | Heim | 0:1 | 0 |

#### PL-3b: Sunderland (1 Karte / 2 Spiele = 0,5, vorläufig)

| Saison | Gameday | Datum | id | Begegnung | Sicht | Karten H:A | Eigene |
|---|---|---|---|---|---|---|---|
| 25/26 | 1 | 16.08.2025 | 64372 | Sunderland – West Ham | Heim | 0:1 | 0 |
| 25/26 | 2 | 23.08.2025 | 64535 | Burnley – Sunderland | Auswärts | 0:1 | 1 |

#### PL-3b: Brentford (20 Karten / 10 Spiele = 2,0)

| Saison | Gameday | Datum | id | Begegnung | Sicht | Karten H:A | Eigene |
|---|---|---|---|---|---|---|---|
| 24/25 | 31 | 06.04.2025 | 14613 | Brentford – Chelsea | Heim | 1:3 | 1 |
| 24/25 | 32 | 12.04.2025 | 14606 | Arsenal – Brentford | Auswärts | 1:3 | 3 |
| 24/25 | 33 | 19.04.2025 | 14596 | Brentford – Brighton | Heim | 3:3 | 3 |
| 24/25 | 34 | 01.05.2025 | 14580 | Nottingham – Brentford | Auswärts | 3:5 | 5 |
| 24/25 | 35 | 04.05.2025 | 14572 | Brentford – Manchester Utd | Heim | 0:2 | 0 |
| 24/25 | 36 | 10.05.2025 | 14567 | Ipswich – Brentford | Auswärts | 2:4 | 4 |
| 24/25 | 37 | 18.05.2025 | 14554 | Brentford – Fulham | Heim | 0:0 | 0 |
| 24/25 | 38 | 25.05.2025 | 14549 | Wolves – Brentford | Auswärts | 2:1 | 1 |
| 25/26 | 1 | 17.08.2025 | 64404 | Nottingham – Brentford | Auswärts | 1:2 | 2 |
| 25/26 | 2 | 23.08.2025 | 64534 | Brentford – Aston Villa | Heim | 1:2 | 1 |

### 7.4 Kontrollpunkte für den Code

**Nachholspiel: Filter nach `Gameday`, nicht nach Datum (wichtig)**
- id 14680 (Everton – Liverpool, Spieltag 15, gespielt am 12.02.2025) darf **nicht** in der Premier-League-Referenz enthalten sein, obwohl es zeitlich zwischen Spieltag 24 und 25 liegt.
- Ein Code, der nach Datum filtert (14.01.2025 bis 25.08.2025), kommt auf **201 Spiele und 700 Karten** (Ø 3,48) statt 200 Spiele und 692 Karten (Ø 3,46). Bei der Testkontrolle am 29.10.2026 tatsächlich so aufgetreten (manuelle Excel-Rechnung).
- Folge hier: PL-3a −39,70 % statt −39,31 %, PL-3b −28,21 % statt −27,75 %. Die Einstufung bleibt gleich, bei grenznahen Werten wäre das aber nicht garantiert.
- Gilt genauso für die Tor-Referenz von KPI 02 (siehe `test_kpi02_erwartete_tore.md`, Abschnitt 6.4).

**Eigene Karten und echte Null (wichtig)**
- Burnley hat in beiden Spielen **0** eigene Karten. Bei id 64535 (Burnley – Sunderland, Karten 0:1) ist Burnley Heimteam, es zählt die linke Zahl (0). Die 1 gehört Sunderland.
- Typischer Fehler: Karten beider Teams statt eigener Karten zählen. Burnley käme auf 1 Karte (0,5), PL-3a auf 2,60 erwartete Karten und −24,86 %, also **leicht statt stark**. Hier ändert der Fehler die Einstufung. Bei der Testkontrolle am 29.10.2026 tatsächlich so aufgetreten.
- Eine echte 0 ist ein gültiger Wert und muss mitgezählt werden. Ein Code, der 0 wie eine leere Zelle behandelt, würde Burnley als „nicht berechenbar“ ausgeben. Gegenstück zur Regel „leere Zelle nie als 0“.
- Weitere spiegelbildliche Duelle: id 14572 (Brentford 0 / Man Utd 2).

**Negative Anomalien**
- PL-3a: starke negative Anomalie (−39,31 %), PL-3b: leichte negative Anomalie (−27,75 %). Damit sind alle Stufen in beide Richtungen mit echten Daten abgedeckt.
- Überschrift „Unterdurchschnittlich viele gelbe Karten“, Abweichung im Text ohne Vorzeichen („39,31 % unter“).

**Ligareferenz über das Saisonende**
- Bundesliga: 162 Spiele aus 2024/25 + 18 aus 2025/26 = 180. Premier League: 180 + 20 = 200.
- Spieltag 3 (2025/26) und alles danach darf nicht enthalten sein.

**Saisonfenster und Aufsteiger**
- FC Koln und Burnley: nur die 2 Spiele aus 2025/26, keine älteren Spiele.
- `vorlaeufig` true für alle vier Begegnungen.

### 7.5 Beobachtungen

- **Kleine Stichproben treiben Anomalien:** Beide Anomalien entstehen überwiegend durch Aufsteiger mit nur 2 Spielen (Burnley 0,0, Sunderland 0,5). Rechnerisch korrekt. Für später zu überlegen: Anomalien bei sehr kleinen Stichproben im Dashboard abgeschwächt darstellen oder deutlich als „vorläufig“ hervorheben.
- **Referenzzeitraum wirkt:** Bundesliga-Referenz 3,73 (Spieltag-1-Test: 3,62), Premier League 3,46 (Spieltag-1-Test: 3,91).
- **2-Tage-Regel nicht wirksam:** Jedes Team hat sein letztes Spiel mindestens 6 Tage vor dem Analysedatum.

---

## 8. Weitere Tests (geplant)

- **Zusatztest fehlende Kartenwerte:** siehe Abschnitt 6.
- **Ausgedachter Testdatensatz** für Sonderfälle: 2-Tage-Regel (Spiele genau 1, 2 und 3 Tage vor dem Analysedatum), Team mit genau 1 Spiel, Abweichung genau ±20,00 % und ±35,00 %.
- **Praxistest 3. Spieltag 2026/27:** optional, sobald die Saison läuft.
