# Testfall KPI 08 – Beide Teams treffen

**Spezifikation v2.1** · Stand 08.11.2026

**Regelwerk:** `03_KPI_Regelwerk.md`, Abschnitte 1, 1.1, 2, 9.0 und 9.4
**Datenbasis:** `Database-Soccer-Intelligence.xlsx`, SHA-256 `f37e36d301767321575aeadf908c39e288b9a655d02d85d5bcfde0507effdc34`
**Status:** **bestätigt von Carsten am 08.11.2026** (gemeinsamer Rundgang KPI 05–09 mit je einer normalen Partie und einem Aufsteiger). Erzeugt von Claude mit einer unabhängigen Berechnung direkt aus der Excel-Datei. Nachprüfung per Excel: `Testfaelle_KPI05-09_Nachpruefung.xlsx`.

**Änderung 08.11.2026 (Carsten):** Alle Werte mit **zwei Nachkommastellen**, auch die Abweichung. Die Einstufung richtet sich nach der auf zwei Stellen gerundeten Abweichung (Regelwerk 2.3).

Dieser Testfall ist die verbindliche Referenz für die Umsetzung (Etappe H). Die JSON-Blöcke werden zu automatischen Tests.

---

## 1. Regeln, die dieser Testfall prüft

- BTTS in einem Spiel = beide Mannschaften mindestens 1 Tor (K > 0 und L > 0).
- Teamwert (BTTS-Quote) = Anzahl BTTS-Spiele / Anzahl Spiele × 100.
- Hauptwert (BTTS-Indikator) = (Quote Heim + Quote Auswärts) / 2, in %.
- Ligareferenz = BTTS-Spiele / Referenzspiele × 100. Abweichung relativ (nicht in Prozentpunkten).
- Stichprobe: letzte 10 Ligaspiele je Team (Saison + Vorsaison, mindestens 2 Kalendertage vor dem Stichtag). **Zuerst** die letzten 10 Spiele bestimmen, **danach** Spiele ohne Wert auslassen; kein älteres Spiel nachziehen. Weniger als 10 Spiele → „vorläufig“.
- Ligareferenz: letzte 20 Spieltage laut `Gameday` vor dem Spieltag des Spiels, nur Spiele vor dem Stichtag.
- Abweichung = (Hauptwert − Ligareferenz) / Ligareferenz × 100. Rundung erst am Ende, kaufmännisch, alle angezeigten Werte mit **zwei Nachkommastellen**. Einstufung nach der gerundeten Abweichung: |x| ≤ 20,00 keine · ≤ 35,00 leicht · > 35,00 stark. Gerundet „−0,00“ wird als „0,00“ ohne Vorzeichen und ohne Richtung ausgegeben.
- Ein Team ohne Spiele → kein Hauptwert, keine Abweichung, keine Anomalie (Gegnerwert und Ligareferenz werden trotzdem angezeigt).

---

## 2. Testfälle

| Testfall | Liga | Saison | Spieltag | Analysedatum | Heimteam | Auswärtsteam | Zweck |
|---|---|---|---|---|---|---|---|
| T1 | Bundesliga | 2026/2027 | 2 | 2026-09-04 | Stuttgart | FC Koln | Standardfall, volle Datenbasis |
| T2 | Bundesliga | 2026/2027 | 2 | 2026-09-04 | Bayer Leverkusen | Union Berlin | Standardfall; KPI 08 genau +20,00 % (Grenzwert → keine Anomalie) |
| T3 | Serie A | 2026/2027 | 2 | 2026-08-28 | Juventus | Parma | Serie A; Anomalien negativ |
| T4 | LaLiga | 2026/2027 | 2 | 2026-08-20 | Atl. Madrid | Villarreal | LaLiga; starke positive Anomalie bei KPI 06 |
| T5 | Premier League | 2026/2027 | 2 | 2026-08-28 | Crystal Palace | Manchester City | Premier League; Standardfall |
| T6 | Serie A | 2026/2027 | 2 | 2026-08-28 | Fiorentina | Frosinone | Aufsteiger mit 1 Spiel → vorläufig |
| T7 | LaLiga | 2026/2027 | 2 | 2026-08-20 | Malaga | Dep. A Coruna | Aufsteiger mit 0 Spielen (Stichtag 20.08., Spiel vom 19.08. zählt nicht) → nicht berechenbar |
| T8 | Bundesliga | 2024/2025 | 18 | 2025-01-19 | Union Berlin | Mainz | Fehlender Statistikwert: Union – Bochum (id 14421) ohne Ecken/Schüsse |
| T9 | LaLiga | 2026/2027 | 2 | 2026-08-20 | Getafe | Racing Santander | LaLiga; Aufsteiger mit 1 Spiel → vorläufig |
| T21 | LaLiga | 2026/2027 | 1 | 2026-08-15 | Real Madrid | Real Sociedad | Rundgang 1. Spieltag 2026/27, normale Partie |
| T22 | LaLiga | 2026/2027 | 1 | 2026-08-15 | Atl. Madrid | Malaga | Rundgang 1. Spieltag 2026/27, Aufsteiger ohne Spiele → nicht berechenbar |

Analysedatum = „Datum von“ des Spieltags im Spielplan (T8: Spieldatum, weil das Spiel aus einer abgeschlossenen Saison stammt).

### Ergebnisse auf einen Blick

| Testfall | Teamwert Heim | Teamwert Auswärts | Ligareferenz | Hauptwert | Abweichung | Anomalie | vorläufig |
|---|---|---|---|---|---|---|---|
| T1 | 70,00 % (10 Sp.) | 100,00 % (10 Sp.) | 66,67 % (180 Sp.) | 85,00 % | +27,50 % | leicht | nein |
| T2 | 90,00 % (10 Sp.) | 70,00 % (10 Sp.) | 66,67 % (180 Sp.) | 80,00 % | +20,00 % | keine | nein |
| T3 | 30,00 % (10 Sp.) | 30,00 % (10 Sp.) | 43,50 % (200 Sp.) | 30,00 % | −31,03 % | leicht | nein |
| T4 | 70,00 % (10 Sp.) | 80,00 % (10 Sp.) | 60,20 % (196 Sp.) | 75,00 % | +24,58 % | leicht | nein |
| T5 | 50,00 % (10 Sp.) | 60,00 % (10 Sp.) | 57,50 % (200 Sp.) | 55,00 % | −4,35 % | keine | nein |
| T6 | 30,00 % (10 Sp.) | 0,00 % (1 Sp.) | 43,50 % (200 Sp.) | 15,00 % | −65,52 % | stark | ja |
| T7 | – (0 Sp.) | 100,00 % (1 Sp.) | 60,20 % (196 Sp.) | – | – | – | ja |
| T8 | 50,00 % (10 Sp.) | 50,00 % (10 Sp.) | 60,56 % (180 Sp.) | 50,00 % | −17,43 % | keine | nein |
| T9 | 20,00 % (10 Sp.) | 100,00 % (1 Sp.) | 60,20 % (196 Sp.) | 60,00 % | −0,34 % | keine | ja |
| T21 | 70,00 % (10 Sp.) | 60,00 % (10 Sp.) | 61,00 % (200 Sp.) | 65,00 % | +6,56 % | keine | nein |
| T22 | 70,00 % (10 Sp.) | – (0 Sp.) | 61,00 % (200 Sp.) | – | – | – | ja |

## 3. Erwartete Ergebnisse (maschinenlesbar)

```json
[
 {
  "testfall": "T1",
  "liga": "Bundesliga",
  "saison": "2026/2027",
  "spieltag": 2,
  "analysedatum": "2026-09-04",
  "heim": {
   "team": "Stuttgart",
   "spiele": 10,
   "summe": 7,
   "teamwert_roh": 70.0,
   "teamwert": "70.00"
  },
  "auswaerts": {
   "team": "FC Koln",
   "spiele": 10,
   "summe": 10,
   "teamwert_roh": 100.0,
   "teamwert": "100.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 16-34 + 2026/2027: 1-1",
   "spiele": 180,
   "summe": 120,
   "wert_roh": 66.6666666667,
   "wert": "66.67"
  },
  "hauptwert_roh": 85.0,
  "hauptwert": "85.00",
  "abweichung_roh": 27.5,
  "abweichung": "27.50",
  "anomalie": "leicht",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Beide Teams treffen häufig",
  "text": "Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von 85,00 % auf. Das liegt 27,50 % über dem Liga-Durchschnitt von 66,67 %."
 },
 {
  "testfall": "T2",
  "liga": "Bundesliga",
  "saison": "2026/2027",
  "spieltag": 2,
  "analysedatum": "2026-09-04",
  "heim": {
   "team": "Bayer Leverkusen",
   "spiele": 10,
   "summe": 9,
   "teamwert_roh": 90.0,
   "teamwert": "90.00"
  },
  "auswaerts": {
   "team": "Union Berlin",
   "spiele": 10,
   "summe": 7,
   "teamwert_roh": 70.0,
   "teamwert": "70.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 16-34 + 2026/2027: 1-1",
   "spiele": 180,
   "summe": 120,
   "wert_roh": 66.6666666667,
   "wert": "66.67"
  },
  "hauptwert_roh": 80.0,
  "hauptwert": "80.00",
  "abweichung_roh": 20.0,
  "abweichung": "20.00",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von 80,00 % auf. Die Abweichung vom Liga-Durchschnitt von 66,67 % beträgt +20,00 %."
 },
 {
  "testfall": "T3",
  "liga": "Serie A",
  "saison": "2026/2027",
  "spieltag": 2,
  "analysedatum": "2026-08-28",
  "heim": {
   "team": "Juventus",
   "spiele": 10,
   "summe": 3,
   "teamwert_roh": 30.0,
   "teamwert": "30.00"
  },
  "auswaerts": {
   "team": "Parma",
   "spiele": 10,
   "summe": 3,
   "teamwert_roh": 30.0,
   "teamwert": "30.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 87,
   "wert_roh": 43.5,
   "wert": "43.50"
  },
  "hauptwert_roh": 30.0,
  "hauptwert": "30.00",
  "abweichung_roh": -31.0344827586,
  "abweichung": "-31.03",
  "anomalie": "leicht",
  "richtung": "negativ",
  "vorlaeufig": false,
  "ueberschrift": "Beide Teams treffen seltener",
  "text": "Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von 30,00 % auf. Das liegt 31,03 % unter dem Liga-Durchschnitt von 43,50 %."
 },
 {
  "testfall": "T4",
  "liga": "LaLiga",
  "saison": "2026/2027",
  "spieltag": 2,
  "analysedatum": "2026-08-20",
  "heim": {
   "team": "Atl. Madrid",
   "spiele": 10,
   "summe": 7,
   "teamwert_roh": 70.0,
   "teamwert": "70.00"
  },
  "auswaerts": {
   "team": "Villarreal",
   "spiele": 10,
   "summe": 8,
   "teamwert_roh": 80.0,
   "teamwert": "80.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 196,
   "summe": 118,
   "wert_roh": 60.2040816327,
   "wert": "60.20"
  },
  "hauptwert_roh": 75.0,
  "hauptwert": "75.00",
  "abweichung_roh": 24.5762711864,
  "abweichung": "24.58",
  "anomalie": "leicht",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Beide Teams treffen häufig",
  "text": "Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von 75,00 % auf. Das liegt 24,58 % über dem Liga-Durchschnitt von 60,20 %."
 },
 {
  "testfall": "T5",
  "liga": "Premier League",
  "saison": "2026/2027",
  "spieltag": 2,
  "analysedatum": "2026-08-28",
  "heim": {
   "team": "Crystal Palace",
   "spiele": 10,
   "summe": 5,
   "teamwert_roh": 50.0,
   "teamwert": "50.00"
  },
  "auswaerts": {
   "team": "Manchester City",
   "spiele": 10,
   "summe": 6,
   "teamwert_roh": 60.0,
   "teamwert": "60.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 115,
   "wert_roh": 57.5,
   "wert": "57.50"
  },
  "hauptwert_roh": 55.0,
  "hauptwert": "55.00",
  "abweichung_roh": -4.347826087,
  "abweichung": "-4.35",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von 55,00 % auf. Die Abweichung vom Liga-Durchschnitt von 57,50 % beträgt −4,35 %."
 },
 {
  "testfall": "T6",
  "liga": "Serie A",
  "saison": "2026/2027",
  "spieltag": 2,
  "analysedatum": "2026-08-28",
  "heim": {
   "team": "Fiorentina",
   "spiele": 10,
   "summe": 3,
   "teamwert_roh": 30.0,
   "teamwert": "30.00"
  },
  "auswaerts": {
   "team": "Frosinone",
   "spiele": 1,
   "summe": 0,
   "teamwert_roh": 0.0,
   "teamwert": "0.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 87,
   "wert_roh": 43.5,
   "wert": "43.50"
  },
  "hauptwert_roh": 15.0,
  "hauptwert": "15.00",
  "abweichung_roh": -65.5172413793,
  "abweichung": "-65.52",
  "anomalie": "stark",
  "richtung": "negativ",
  "vorlaeufig": true,
  "ueberschrift": "Beide Teams treffen seltener",
  "text": "Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von 15,00 % auf. Das liegt 65,52 % unter dem Liga-Durchschnitt von 43,50 %."
 },
 {
  "testfall": "T7",
  "liga": "LaLiga",
  "saison": "2026/2027",
  "spieltag": 2,
  "analysedatum": "2026-08-20",
  "heim": {
   "team": "Malaga",
   "spiele": 0,
   "summe": null,
   "teamwert_roh": null,
   "teamwert": null
  },
  "auswaerts": {
   "team": "Dep. A Coruna",
   "spiele": 1,
   "summe": 1,
   "teamwert_roh": 100.0,
   "teamwert": "100.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 196,
   "summe": 118,
   "wert_roh": 60.2040816327,
   "wert": "60.20"
  },
  "hauptwert_roh": null,
  "hauptwert": null,
  "abweichung_roh": null,
  "abweichung": null,
  "anomalie": null,
  "richtung": null,
  "vorlaeufig": true,
  "ueberschrift": null,
  "text": null
 },
 {
  "testfall": "T8",
  "liga": "Bundesliga",
  "saison": "2024/2025",
  "spieltag": 18,
  "analysedatum": "2025-01-19",
  "heim": {
   "team": "Union Berlin",
   "spiele": 10,
   "summe": 5,
   "teamwert_roh": 50.0,
   "teamwert": "50.00"
  },
  "auswaerts": {
   "team": "Mainz",
   "spiele": 10,
   "summe": 5,
   "teamwert_roh": 50.0,
   "teamwert": "50.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2023/2024: 32-34 + 2024/2025: 1-17",
   "spiele": 180,
   "summe": 109,
   "wert_roh": 60.5555555556,
   "wert": "60.56"
  },
  "hauptwert_roh": 50.0,
  "hauptwert": "50.00",
  "abweichung_roh": -17.4311926606,
  "abweichung": "-17.43",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von 50,00 % auf. Die Abweichung vom Liga-Durchschnitt von 60,56 % beträgt −17,43 %."
 },
 {
  "testfall": "T9",
  "liga": "LaLiga",
  "saison": "2026/2027",
  "spieltag": 2,
  "analysedatum": "2026-08-20",
  "heim": {
   "team": "Getafe",
   "spiele": 10,
   "summe": 2,
   "teamwert_roh": 20.0,
   "teamwert": "20.00"
  },
  "auswaerts": {
   "team": "Racing Santander",
   "spiele": 1,
   "summe": 1,
   "teamwert_roh": 100.0,
   "teamwert": "100.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 196,
   "summe": 118,
   "wert_roh": 60.2040816327,
   "wert": "60.20"
  },
  "hauptwert_roh": 60.0,
  "hauptwert": "60.00",
  "abweichung_roh": -0.3389830508,
  "abweichung": "-0.34",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": true,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von 60,00 % auf. Die Abweichung vom Liga-Durchschnitt von 60,20 % beträgt −0,34 %."
 },
 {
  "testfall": "T21",
  "liga": "LaLiga",
  "saison": "2026/2027",
  "spieltag": 1,
  "analysedatum": "2026-08-15",
  "heim": {
   "team": "Real Madrid",
   "spiele": 10,
   "summe": 7,
   "teamwert_roh": 70.0,
   "teamwert": "70.00"
  },
  "auswaerts": {
   "team": "Real Sociedad",
   "spiele": 10,
   "summe": 6,
   "teamwert_roh": 60.0,
   "teamwert": "60.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 19-38",
   "spiele": 200,
   "summe": 122,
   "wert_roh": 61.0,
   "wert": "61.00"
  },
  "hauptwert_roh": 65.0,
  "hauptwert": "65.00",
  "abweichung_roh": 6.5573770492,
  "abweichung": "6.56",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von 65,00 % auf. Die Abweichung vom Liga-Durchschnitt von 61,00 % beträgt +6,56 %."
 },
 {
  "testfall": "T22",
  "liga": "LaLiga",
  "saison": "2026/2027",
  "spieltag": 1,
  "analysedatum": "2026-08-15",
  "heim": {
   "team": "Atl. Madrid",
   "spiele": 10,
   "summe": 7,
   "teamwert_roh": 70.0,
   "teamwert": "70.00"
  },
  "auswaerts": {
   "team": "Malaga",
   "spiele": 0,
   "summe": null,
   "teamwert_roh": null,
   "teamwert": null
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 19-38",
   "spiele": 200,
   "summe": 122,
   "wert_roh": 61.0,
   "wert": "61.00"
  },
  "hauptwert_roh": null,
  "hauptwert": null,
  "abweichung_roh": null,
  "abweichung": null,
  "anomalie": null,
  "richtung": null,
  "vorlaeufig": true,
  "ueberschrift": null,
  "text": null
 }
]
```

Hinweise: gerundete Werte als Text mit Punkt (im Dashboard mit Komma); `summe` = Summe der Spielwerte (bei KPI 08 Anzahl BTTS-Spiele); `_roh`-Werte mit Toleranz 1e-9 vergleichen.

## 4. Eingabedaten zum Nachvollziehen

### T1 – Stuttgart – FC Koln (Bundesliga, 2026/2027, Spieltag 2, Analysedatum 2026-09-04)

**Stuttgart** – 10 gültige Spiele, Summe 7, Teamwert 70,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107988 | Stuttgart – RB Leipzig | 1:0 | nein |
| 22.03.2026 | 114388 | Augsburg – Stuttgart | 2:5 | ja |
| 04.04.2026 | 117441 | Stuttgart – Dortmund | 0:2 | nein |
| 12.04.2026 | 118014 | Stuttgart – Hamburger SV | 4:0 | nein |
| 19.04.2026 | 118339 | Bayern Munich – Stuttgart | 4:2 | ja |
| 26.04.2026 | 118750 | Stuttgart – Werder Bremen | 1:1 | ja |
| 02.05.2026 | 118986 | Hoffenheim – Stuttgart | 3:3 | ja |
| 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 3:1 | ja |
| 16.05.2026 | 120510 | Eintracht Frankfurt – Stuttgart | 2:2 | ja |
| 28.08.2026 | 132783 | Bayern Munich – Stuttgart | 5:1 | ja |

**FC Koln** – 10 gültige Spiele, Summe 10, Teamwert 100,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106583 | Hamburger SV – FC Koln | 1:1 | ja |
| 21.03.2026 | 114289 | FC Koln – B. Monchengladbach | 3:3 | ja |
| 05.04.2026 | 117540 | Eintracht Frankfurt – FC Koln | 2:2 | ja |
| 12.04.2026 | 118013 | FC Koln – Werder Bremen | 3:1 | ja |
| 17.04.2026 | 118161 | St. Pauli – FC Koln | 1:1 | ja |
| 25.04.2026 | 118646 | FC Koln – Bayer Leverkusen | 1:2 | ja |
| 02.05.2026 | 118987 | Union Berlin – FC Koln | 2:2 | ja |
| 10.05.2026 | 119365 | FC Koln – Heidenheim | 1:3 | ja |
| 16.05.2026 | 120509 | Bayern Munich – FC Koln | 5:1 | ja |
| 29.08.2026 | 132873 | FC Koln – Hoffenheim | 3:2 | ja |

### T2 – Bayer Leverkusen – Union Berlin (Bundesliga, 2026/2027, Spieltag 2, Analysedatum 2026-09-04)

**Bayer Leverkusen** – 10 gültige Spiele, Summe 9, Teamwert 90,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106579 | Bayer Leverkusen – Bayern Munich | 1:1 | ja |
| 21.03.2026 | 114290 | Heidenheim – Bayer Leverkusen | 3:3 | ja |
| 04.04.2026 | 117436 | Bayer Leverkusen – Wolfsburg | 6:3 | ja |
| 11.04.2026 | 117899 | Dortmund – Bayer Leverkusen | 0:1 | nein |
| 18.04.2026 | 118240 | Bayer Leverkusen – Augsburg | 1:2 | ja |
| 25.04.2026 | 118646 | FC Koln – Bayer Leverkusen | 1:2 | ja |
| 02.05.2026 | 118989 | Bayer Leverkusen – RB Leipzig | 4:1 | ja |
| 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 3:1 | ja |
| 16.05.2026 | 120508 | Bayer Leverkusen – Hamburger SV | 1:1 | ja |
| 29.08.2026 | 132872 | Elversberg – Bayer Leverkusen | 3:2 | ja |

**Union Berlin** – 10 gültige Spiele, Summe 7, Teamwert 70,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107987 | Freiburg – Union Berlin | 0:1 | nein |
| 21.03.2026 | 114288 | Bayern Munich – Union Berlin | 4:0 | nein |
| 05.04.2026 | 117539 | Union Berlin – St. Pauli | 1:1 | ja |
| 11.04.2026 | 117900 | Heidenheim – Union Berlin | 3:1 | ja |
| 18.04.2026 | 118242 | Union Berlin – Wolfsburg | 1:2 | ja |
| 24.04.2026 | 118560 | RB Leipzig – Union Berlin | 3:1 | ja |
| 02.05.2026 | 118987 | Union Berlin – FC Koln | 2:2 | ja |
| 10.05.2026 | 119366 | Mainz – Union Berlin | 1:3 | ja |
| 16.05.2026 | 120514 | Union Berlin – Augsburg | 4:0 | nein |
| 29.08.2026 | 132876 | Union Berlin – Eintracht Frankfurt | 3:3 | ja |

### T3 – Juventus – Parma (Serie A, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Juventus** – 10 gültige Spiele, Summe 3, Teamwert 30,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 21.03.2026 | 114299 | Juventus – Sassuolo | 1:1 | ja |
| 06.04.2026 | 117656 | Juventus – Genoa | 2:0 | nein |
| 11.04.2026 | 117911 | Atalanta – Juventus | 0:1 | nein |
| 19.04.2026 | 118349 | Juventus – Bologna | 2:0 | nein |
| 26.04.2026 | 118761 | AC Milan – Juventus | 0:0 | nein |
| 03.05.2026 | 119096 | Juventus – Verona | 1:1 | ja |
| 09.05.2026 | 119281 | Lecce – Juventus | 0:1 | nein |
| 17.05.2026 | 120620 | Juventus – Fiorentina | 0:2 | nein |
| 24.05.2026 | 120857 | Torino – Juventus | 2:2 | ja |
| 23.08.2026 | 130758 | Frosinone – Juventus | 0:1 | nein |

**Parma** – 10 gültige Spiele, Summe 3, Teamwert 30,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 21.03.2026 | 114297 | Parma – Cremonese | 0:2 | nein |
| 04.04.2026 | 117451 | Lazio – Parma | 1:1 | ja |
| 12.04.2026 | 118020 | Parma – Napoli | 1:1 | ja |
| 18.04.2026 | 118254 | Udinese – Parma | 0:1 | nein |
| 25.04.2026 | 118655 | Parma – Pisa | 1:0 | nein |
| 03.05.2026 | 119097 | Inter – Parma | 2:0 | nein |
| 10.05.2026 | 119377 | Parma – AS Roma | 2:3 | ja |
| 17.05.2026 | 120618 | Como – Parma | 1:0 | nein |
| 24.05.2026 | 120852 | Parma – Sassuolo | 1:0 | nein |
| 22.08.2026 | 130663 | Parma – Cagliari | 0:1 | nein |

### T4 – Atl. Madrid – Villarreal (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Atl. Madrid** – 10 gültige Spiele, Summe 7, Teamwert 70,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 22.03.2026 | 114444 | Real Madrid – Atl. Madrid | 3:2 | ja |
| 04.04.2026 | 117485 | Atl. Madrid – Barcelona | 1:2 | ja |
| 11.04.2026 | 117953 | Sevilla – Atl. Madrid | 2:1 | ja |
| 22.04.2026 | 118500 | Elche – Atl. Madrid | 3:2 | ja |
| 25.04.2026 | 118693 | Atl. Madrid – Ath Bilbao | 3:2 | ja |
| 02.05.2026 | 119028 | Valencia – Atl. Madrid | 0:2 | nein |
| 09.05.2026 | 119297 | Atl. Madrid – Celta Vigo | 0:1 | nein |
| 12.05.2026 | 120229 | Osasuna – Atl. Madrid | 1:2 | ja |
| 17.05.2026 | 120662 | Atl. Madrid – Girona | 0:1 | nein |
| 24.05.2026 | 120872 | Villarreal – Atl. Madrid | 5:1 | ja |

**Villarreal** – 10 gültige Spiele, Summe 8, Teamwert 80,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 06.04.2026 | 117677 | Girona – Villarreal | 1:0 | nein |
| 12.04.2026 | 118055 | Ath Bilbao – Villarreal | 1:2 | ja |
| 23.04.2026 | 118530 | Oviedo – Villarreal | 1:1 | ja |
| 26.04.2026 | 118794 | Villarreal – Celta Vigo | 2:1 | ja |
| 02.05.2026 | 119027 | Villarreal – Levante | 5:1 | ja |
| 10.05.2026 | 119413 | Mallorca – Villarreal | 1:1 | ja |
| 13.05.2026 | 120439 | Villarreal – Sevilla | 2:3 | ja |
| 17.05.2026 | 120667 | Rayo Vallecano – Villarreal | 1:0 | nein |
| 24.05.2026 | 120872 | Villarreal – Atl. Madrid | 5:1 | ja |
| 16.08.2026 | 129483 | Racing Santander – Villarreal | 2:2 | ja |

### T5 – Crystal Palace – Manchester City (Premier League, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Crystal Palace** – 10 gültige Spiele, Summe 5, Teamwert 50,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107978 | Crystal Palace – Leeds | 0:0 | nein |
| 12.04.2026 | 118005 | Crystal Palace – Newcastle | 2:1 | ja |
| 20.04.2026 | 118408 | Crystal Palace – West Ham | 0:0 | nein |
| 25.04.2026 | 118603 | Liverpool – Crystal Palace | 3:1 | ja |
| 03.05.2026 | 119074 | Bournemouth – Crystal Palace | 3:0 | nein |
| 10.05.2026 | 119351 | Crystal Palace – Everton | 2:2 | ja |
| 13.05.2026 | 120425 | Manchester City – Crystal Palace | 3:0 | nein |
| 17.05.2026 | 120589 | Brentford – Crystal Palace | 2:2 | ja |
| 24.05.2026 | 120843 | Crystal Palace – Arsenal | 1:2 | ja |
| 22.08.2026 | 130611 | Everton – Crystal Palace | 2:0 | nein |

**Manchester City** – 10 gültige Spiele, Summe 6, Teamwert 60,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106539 | West Ham – Manchester City | 1:1 | ja |
| 12.04.2026 | 118008 | Chelsea – Manchester City | 0:3 | nein |
| 19.04.2026 | 118329 | Manchester City – Arsenal | 2:1 | ja |
| 22.04.2026 | 118479 | Burnley – Manchester City | 0:1 | nein |
| 04.05.2026 | 119163 | Everton – Manchester City | 3:3 | ja |
| 09.05.2026 | 119254 | Manchester City – Brentford | 3:0 | nein |
| 13.05.2026 | 120425 | Manchester City – Crystal Palace | 3:0 | nein |
| 19.05.2026 | 120707 | Bournemouth – Manchester City | 1:1 | ja |
| 24.05.2026 | 120846 | Manchester City – Aston Villa | 1:2 | ja |
| 23.08.2026 | 130749 | Manchester City – Bournemouth | 2:1 | ja |

### T6 – Fiorentina – Frosinone (Serie A, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Fiorentina** – 10 gültige Spiele, Summe 3, Teamwert 30,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 22.03.2026 | 114403 | Fiorentina – Inter | 1:1 | ja |
| 04.04.2026 | 117450 | Verona – Fiorentina | 0:1 | nein |
| 13.04.2026 | 118084 | Fiorentina – Lazio | 1:0 | nein |
| 20.04.2026 | 118410 | Lecce – Fiorentina | 1:1 | ja |
| 26.04.2026 | 118758 | Fiorentina – Sassuolo | 0:0 | nein |
| 04.05.2026 | 119165 | AS Roma – Fiorentina | 4:0 | nein |
| 10.05.2026 | 119376 | Fiorentina – Genoa | 0:0 | nein |
| 17.05.2026 | 120620 | Juventus – Fiorentina | 0:2 | nein |
| 22.05.2026 | 120772 | Fiorentina – Atalanta | 1:1 | ja |
| 24.08.2026 | 130861 | AS Roma – Fiorentina | 4:0 | nein |

**Frosinone** – 1 gültige Spiele, Summe 0, Teamwert 0,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 23.08.2026 | 130758 | Frosinone – Juventus | 0:1 | nein |

### T7 – Malaga – Dep. A Coruna (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Malaga** – 0 gültige Spiele, Summe –, Teamwert –

Keine Ligaspiele im Zeitfenster.

**Dep. A Coruna** – 1 gültige Spiele, Summe 1, Teamwert 100,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 17.08.2026 | 130470 | Dep. A Coruna – Elche | 1:1 | ja |

### T8 – Union Berlin – Mainz (Bundesliga, 2024/2025, Spieltag 18, Analysedatum 2025-01-19)

**Union Berlin** – 10 gültige Spiele, Summe 5, Teamwert 50,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 27.10.2024 | 14469 | Union Berlin – Eintracht Frankfurt | 1:1 | ja |
| 02.11.2024 | 14462 | Bayern Munich – Union Berlin | 3:0 | nein |
| 08.11.2024 | 14458 | Union Berlin – Freiburg | 0:0 | nein |
| 23.11.2024 | 14448 | Wolfsburg – Union Berlin | 1:0 | nein |
| 30.11.2024 | 14438 | Union Berlin – Bayer Leverkusen | 1:2 | ja |
| 06.12.2024 | 14431 | Stuttgart – Union Berlin | 3:2 | ja |
| 14.12.2024 | 14421 | Union Berlin – Bochum | 1:1 | ja |
| 21.12.2024 | 14412 | Werder Bremen – Union Berlin | 4:1 | ja |
| 11.01.2025 | 14400 | Heidenheim – Union Berlin | 2:0 | nein |
| 15.01.2025 | 14389 | Union Berlin – Augsburg | 0:2 | nein |

**Mainz** – 10 gültige Spiele, Summe 5, Teamwert 50,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 25.10.2024 | 14476 | Mainz – B. Monchengladbach | 1:1 | ja |
| 03.11.2024 | 14460 | Freiburg – Mainz | 0:0 | nein |
| 09.11.2024 | 14455 | Mainz – Dortmund | 3:1 | ja |
| 24.11.2024 | 14442 | Holstein Kiel – Mainz | 0:3 | nein |
| 01.12.2024 | 14433 | Mainz – Hoffenheim | 2:0 | nein |
| 08.12.2024 | 14424 | Wolfsburg – Mainz | 4:3 | ja |
| 14.12.2024 | 14420 | Mainz – Bayern Munich | 2:1 | ja |
| 21.12.2024 | 14408 | Eintracht Frankfurt – Mainz | 1:3 | ja |
| 11.01.2025 | 14402 | Mainz – Bochum | 2:0 | nein |
| 14.01.2025 | 14392 | Bayer Leverkusen – Mainz | 1:0 | nein |

### T9 – Getafe – Racing Santander (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Getafe** – 10 gültige Spiele, Summe 2, Teamwert 20,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 05.04.2026 | 117581 | Getafe – Ath Bilbao | 2:0 | nein |
| 13.04.2026 | 118088 | Levante – Getafe | 1:0 | nein |
| 22.04.2026 | 118501 | Real Sociedad – Getafe | 0:1 | nein |
| 25.04.2026 | 118691 | Getafe – Barcelona | 0:2 | nein |
| 03.05.2026 | 119130 | Getafe – Rayo Vallecano | 0:2 | nein |
| 10.05.2026 | 119415 | Oviedo – Getafe | 0:0 | nein |
| 13.05.2026 | 120441 | Getafe – Mallorca | 3:1 | ja |
| 17.05.2026 | 120663 | Elche – Getafe | 3:4 | ja |
| 23.05.2026 | 120811 | Getafe – Osasuna | 1:0 | nein |
| 15.08.2026 | 128152 | Alaves – Getafe | 3:0 | nein |

**Racing Santander** – 1 gültige Spiele, Summe 1, Teamwert 100,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 16.08.2026 | 129483 | Racing Santander – Villarreal | 2:2 | ja |

### T21 – Real Madrid – Real Sociedad (LaLiga, 2026/2027, Spieltag 1, Analysedatum 2026-08-15)

**Real Madrid** – 10 gültige Spiele, Summe 7, Teamwert 70,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 22.03.2026 | 114444 | Real Madrid – Atl. Madrid | 3:2 | ja |
| 04.04.2026 | 117483 | Mallorca – Real Madrid | 2:1 | ja |
| 10.04.2026 | 117827 | Real Madrid – Girona | 1:1 | ja |
| 21.04.2026 | 118458 | Real Madrid – Alaves | 2:1 | ja |
| 24.04.2026 | 118571 | Betis – Real Madrid | 1:1 | ja |
| 03.05.2026 | 119132 | Espanyol – Real Madrid | 0:2 | nein |
| 10.05.2026 | 119416 | Barcelona – Real Madrid | 2:0 | nein |
| 14.05.2026 | 120452 | Real Madrid – Oviedo | 2:0 | nein |
| 17.05.2026 | 120669 | Sevilla – Real Madrid | 1:1 | ja |
| 23.05.2026 | 120814 | Real Madrid – Ath Bilbao | 4:2 | ja |

**Real Sociedad** – 10 gültige Spiele, Summe 6, Teamwert 60,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 20.03.2026 | 114220 | Villarreal – Real Sociedad | 3:1 | ja |
| 04.04.2026 | 117482 | Real Sociedad – Levante | 2:0 | nein |
| 11.04.2026 | 117950 | Real Sociedad – Alaves | 3:3 | ja |
| 22.04.2026 | 118501 | Real Sociedad – Getafe | 0:1 | nein |
| 26.04.2026 | 118791 | Rayo Vallecano – Real Sociedad | 3:3 | ja |
| 04.05.2026 | 119176 | Sevilla – Real Sociedad | 1:0 | nein |
| 09.05.2026 | 119298 | Real Sociedad – Betis | 2:2 | ja |
| 14.05.2026 | 120451 | Girona – Real Sociedad | 1:1 | ja |
| 17.05.2026 | 120668 | Real Sociedad – Valencia | 1:0 | nein |
| 23.05.2026 | 120810 | Espanyol – Real Sociedad | 1:1 | ja |

### T22 – Atl. Madrid – Malaga (LaLiga, 2026/2027, Spieltag 1, Analysedatum 2026-08-15)

**Atl. Madrid** – 10 gültige Spiele, Summe 7, Teamwert 70,00 %

| Datum | id | Begegnung | Endstand K:L | zählt |
|---|---|---|---|---|
| 22.03.2026 | 114444 | Real Madrid – Atl. Madrid | 3:2 | ja |
| 04.04.2026 | 117485 | Atl. Madrid – Barcelona | 1:2 | ja |
| 11.04.2026 | 117953 | Sevilla – Atl. Madrid | 2:1 | ja |
| 22.04.2026 | 118500 | Elche – Atl. Madrid | 3:2 | ja |
| 25.04.2026 | 118693 | Atl. Madrid – Ath Bilbao | 3:2 | ja |
| 02.05.2026 | 119028 | Valencia – Atl. Madrid | 0:2 | nein |
| 09.05.2026 | 119297 | Atl. Madrid – Celta Vigo | 0:1 | nein |
| 12.05.2026 | 120229 | Osasuna – Atl. Madrid | 1:2 | ja |
| 17.05.2026 | 120662 | Atl. Madrid – Girona | 0:1 | nein |
| 24.05.2026 | 120872 | Villarreal – Atl. Madrid | 5:1 | ja |

**Malaga** – 0 gültige Spiele, Summe –, Teamwert –

Keine Ligaspiele im Zeitfenster.

### Ligareferenzen je Liga und Spieltag

**Bundesliga, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-09-04):** 2025/2026: 16-34 + 2026/2027: 1-1 → 180 Spiele, Summe 120 BTTS-Spiele, Ligareferenz 66,67 %

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 16 | 9 | 7 |  |
| 2025/2026 | 17 | 9 | 6 |  |
| 2025/2026 | 18 | 9 | 7 |  |
| 2025/2026 | 19 | 9 | 4 |  |
| 2025/2026 | 20 | 9 | 7 |  |
| 2025/2026 | 21 | 9 | 6 |  |
| 2025/2026 | 22 | 9 | 3 |  |
| 2025/2026 | 23 | 9 | 8 |  |
| 2025/2026 | 24 | 9 | 3 |  |
| 2025/2026 | 25 | 9 | 8 |  |
| 2025/2026 | 26 | 9 | 3 |  |
| 2025/2026 | 27 | 9 | 6 |  |
| 2025/2026 | 28 | 9 | 8 |  |
| 2025/2026 | 29 | 9 | 4 |  |
| 2025/2026 | 30 | 9 | 9 |  |
| 2025/2026 | 31 | 9 | 6 |  |
| 2025/2026 | 32 | 9 | 8 |  |
| 2025/2026 | 33 | 9 | 7 |  |
| 2025/2026 | 34 | 9 | 5 |  |
| 2026/2027 | 1 | 9 | 5 |  |

**Serie A, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-28):** 2025/2026: 20-38 + 2026/2027: 1-1 → 200 Spiele, Summe 87 BTTS-Spiele, Ligareferenz 43,50 %

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 5 |  |
| 2025/2026 | 21 | 10 | 2 |  |
| 2025/2026 | 22 | 10 | 5 |  |
| 2025/2026 | 23 | 10 | 4 |  |
| 2025/2026 | 24 | 10 | 6 |  |
| 2025/2026 | 25 | 10 | 7 |  |
| 2025/2026 | 26 | 10 | 1 |  |
| 2025/2026 | 27 | 10 | 5 |  |
| 2025/2026 | 28 | 10 | 7 |  |
| 2025/2026 | 29 | 10 | 6 |  |
| 2025/2026 | 30 | 10 | 3 |  |
| 2025/2026 | 31 | 10 | 4 |  |
| 2025/2026 | 32 | 10 | 4 |  |
| 2025/2026 | 33 | 10 | 4 |  |
| 2025/2026 | 34 | 10 | 3 |  |
| 2025/2026 | 35 | 10 | 3 |  |
| 2025/2026 | 36 | 10 | 4 |  |
| 2025/2026 | 37 | 10 | 4 |  |
| 2025/2026 | 38 | 10 | 6 |  |
| 2026/2027 | 1 | 10 | 4 |  |

**LaLiga, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-20):** 2025/2026: 20-38 + 2026/2027: 1-1 → 196 Spiele, Summe 118 BTTS-Spiele, Ligareferenz 60,20 %

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 4 |  |
| 2025/2026 | 21 | 10 | 7 |  |
| 2025/2026 | 22 | 10 | 7 |  |
| 2025/2026 | 23 | 10 | 5 |  |
| 2025/2026 | 24 | 10 | 7 |  |
| 2025/2026 | 25 | 10 | 7 |  |
| 2025/2026 | 26 | 10 | 5 |  |
| 2025/2026 | 27 | 10 | 8 |  |
| 2025/2026 | 28 | 10 | 7 |  |
| 2025/2026 | 29 | 10 | 7 |  |
| 2025/2026 | 30 | 10 | 4 |  |
| 2025/2026 | 31 | 10 | 6 |  |
| 2025/2026 | 32 | 10 | 5 |  |
| 2025/2026 | 33 | 10 | 8 |  |
| 2025/2026 | 34 | 10 | 4 |  |
| 2025/2026 | 35 | 10 | 6 |  |
| 2025/2026 | 36 | 10 | 7 |  |
| 2025/2026 | 37 | 10 | 4 |  |
| 2025/2026 | 38 | 10 | 7 |  |
| 2026/2027 | 1 | 6 | 3 |  |

**Premier League, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-28):** 2025/2026: 20-38 + 2026/2027: 1-1 → 200 Spiele, Summe 115 BTTS-Spiele, Ligareferenz 57,50 %

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 7 |  |
| 2025/2026 | 21 | 10 | 7 |  |
| 2025/2026 | 22 | 10 | 4 |  |
| 2025/2026 | 23 | 10 | 7 |  |
| 2025/2026 | 24 | 10 | 6 |  |
| 2025/2026 | 25 | 10 | 6 |  |
| 2025/2026 | 26 | 10 | 6 |  |
| 2025/2026 | 27 | 10 | 5 |  |
| 2025/2026 | 28 | 10 | 8 |  |
| 2025/2026 | 29 | 10 | 5 |  |
| 2025/2026 | 30 | 10 | 4 |  |
| 2025/2026 | 31 | 10 | 5 |  |
| 2025/2026 | 32 | 10 | 5 |  |
| 2025/2026 | 33 | 10 | 6 |  |
| 2025/2026 | 34 | 10 | 4 |  |
| 2025/2026 | 35 | 10 | 7 |  |
| 2025/2026 | 36 | 10 | 5 |  |
| 2025/2026 | 37 | 10 | 8 |  |
| 2025/2026 | 38 | 10 | 6 |  |
| 2026/2027 | 1 | 10 | 4 |  |

**Bundesliga, analysiert Saison 2024/2025 Spieltag 18 (Stichtag 2025-01-19):** 2023/2024: 32-34 + 2024/2025: 1-17 → 180 Spiele, Summe 109 BTTS-Spiele, Ligareferenz 60,56 %

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2023/2024 | 32 | 9 | 7 |  |
| 2023/2024 | 33 | 9 | 4 |  |
| 2023/2024 | 34 | 9 | 7 |  |
| 2024/2025 | 1 | 9 | 6 |  |
| 2024/2025 | 2 | 9 | 3 |  |
| 2024/2025 | 3 | 9 | 8 |  |
| 2024/2025 | 4 | 9 | 5 |  |
| 2024/2025 | 5 | 9 | 5 |  |
| 2024/2025 | 6 | 9 | 6 |  |
| 2024/2025 | 7 | 9 | 6 |  |
| 2024/2025 | 8 | 9 | 6 |  |
| 2024/2025 | 9 | 9 | 4 |  |
| 2024/2025 | 10 | 9 | 5 |  |
| 2024/2025 | 11 | 9 | 2 |  |
| 2024/2025 | 12 | 9 | 6 |  |
| 2024/2025 | 13 | 9 | 7 |  |
| 2024/2025 | 14 | 9 | 7 |  |
| 2024/2025 | 15 | 9 | 7 |  |
| 2024/2025 | 16 | 9 | 3 |  |
| 2024/2025 | 17 | 9 | 5 |  |

**LaLiga, analysiert Saison 2026/2027 Spieltag 1 (Stichtag 2026-08-15):** 2025/2026: 19-38 → 200 Spiele, Summe 122 BTTS-Spiele, Ligareferenz 61,00 %

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 19 | 10 | 7 |  |
| 2025/2026 | 20 | 10 | 4 |  |
| 2025/2026 | 21 | 10 | 7 |  |
| 2025/2026 | 22 | 10 | 7 |  |
| 2025/2026 | 23 | 10 | 5 |  |
| 2025/2026 | 24 | 10 | 7 |  |
| 2025/2026 | 25 | 10 | 7 |  |
| 2025/2026 | 26 | 10 | 5 |  |
| 2025/2026 | 27 | 10 | 8 |  |
| 2025/2026 | 28 | 10 | 7 |  |
| 2025/2026 | 29 | 10 | 7 |  |
| 2025/2026 | 30 | 10 | 4 |  |
| 2025/2026 | 31 | 10 | 6 |  |
| 2025/2026 | 32 | 10 | 5 |  |
| 2025/2026 | 33 | 10 | 8 |  |
| 2025/2026 | 34 | 10 | 4 |  |
| 2025/2026 | 35 | 10 | 6 |  |
| 2025/2026 | 36 | 10 | 7 |  |
| 2025/2026 | 37 | 10 | 4 |  |
| 2025/2026 | 38 | 10 | 7 |  |

