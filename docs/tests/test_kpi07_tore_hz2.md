# Testfall KPI 07 – Tore 2. Halbzeit

**Spezifikation v2.1** · Stand 08.11.2026

**Regelwerk:** `03_KPI_Regelwerk.md`, Abschnitte 1, 1.1, 2, 9.0 und 9.3
**Datenbasis:** `Database-Soccer-Intelligence.xlsx`, SHA-256 `f37e36d301767321575aeadf908c39e288b9a655d02d85d5bcfde0507effdc34`
**Status:** **bestätigt von Carsten am 08.11.2026** (gemeinsamer Rundgang KPI 05–09 mit je einer normalen Partie und einem Aufsteiger). Erzeugt von Claude mit einer unabhängigen Berechnung direkt aus der Excel-Datei. Nachprüfung per Excel: `Testfaelle_KPI05-09_Nachpruefung.xlsx`.

**Änderung 08.11.2026 (Carsten):** Alle Werte mit **zwei Nachkommastellen**, auch die Abweichung. Die Einstufung richtet sich nach der auf zwei Stellen gerundeten Abweichung (Regelwerk 2.3).

Dieser Testfall ist die verbindliche Referenz für die Umsetzung (Etappe H). Die JSON-Blöcke werden zu automatischen Tests.

---

## 1. Regeln, die dieser Testfall prüft

- Teamwert = Ø Tore **beider** Mannschaften in Halbzeit 2 (T + U) in den Spielen des Teams. Nicht der Endstand.
- Hauptwert = (Teamwert Heim + Teamwert Auswärts) / 2 (Mittelwert).
- Ligareferenz = Ø Tore beider Teams in Halbzeit 2 pro Spiel (T + U).
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
| T18 | Serie A | 2026/2027 | 1 | 2026-08-22 | Torino | AC Milan | Rundgang 1. Spieltag 2026/27, normale Partie |
| T19 | Serie A | 2026/2027 | 1 | 2026-08-22 | Inter | Monza | Rundgang 1. Spieltag 2026/27, Aufsteiger ohne Spiele → nicht berechenbar |
| T20 | Serie A | 2026/2027 | 2 | 2026-08-28 | Monza | Udinese | Rundgang 2. Spieltag 2026/27, Aufsteiger mit 1 Spiel → vorläufig; starke positive Anomalie |

Analysedatum = „Datum von“ des Spieltags im Spielplan (T8: Spieldatum, weil das Spiel aus einer abgeschlossenen Saison stammt).

### Ergebnisse auf einen Blick

| Testfall | Teamwert Heim | Teamwert Auswärts | Ligareferenz | Hauptwert | Abweichung | Anomalie | vorläufig |
|---|---|---|---|---|---|---|---|
| T1 | 2,30 (10 Sp.) | 2,30 (10 Sp.) | 1,88 (180 Sp.) | 2,30 | +22,12 % | leicht | nein |
| T2 | 2,10 (10 Sp.) | 2,10 (10 Sp.) | 1,88 (180 Sp.) | 2,10 | +11,50 % | keine | nein |
| T3 | 0,80 (10 Sp.) | 1,40 (10 Sp.) | 1,47 (200 Sp.) | 1,10 | −25,17 % | leicht | nein |
| T4 | 1,60 (10 Sp.) | 1,00 (10 Sp.) | 1,60 (196 Sp.) | 1,30 | −18,59 % | keine | nein |
| T5 | 1,30 (10 Sp.) | 1,80 (10 Sp.) | 1,52 (200 Sp.) | 1,55 | +1,97 % | keine | nein |
| T6 | 0,90 (10 Sp.) | 0,00 (1 Sp.) | 1,47 (200 Sp.) | 0,45 | −69,39 % | stark | ja |
| T7 | – (0 Sp.) | 1,00 (1 Sp.) | 1,60 (196 Sp.) | – | – | – | ja |
| T8 | 1,00 (10 Sp.) | 1,40 (10 Sp.) | 1,71 (180 Sp.) | 1,20 | −29,64 % | leicht | nein |
| T9 | 1,40 (10 Sp.) | 0,00 (1 Sp.) | 1,60 (196 Sp.) | 0,70 | −56,17 % | stark | ja |
| T18 | 1,80 (10 Sp.) | 1,30 (10 Sp.) | 1,48 (200 Sp.) | 1,55 | +4,73 % | keine | nein |
| T19 | 2,30 (10 Sp.) | – (0 Sp.) | 1,48 (200 Sp.) | – | – | – | ja |
| T20 | 3,00 (1 Sp.) | 1,30 (10 Sp.) | 1,47 (200 Sp.) | 2,15 | +46,26 % | stark | ja |

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
   "summe": 23,
   "teamwert_roh": 2.3,
   "teamwert": "2.30"
  },
  "auswaerts": {
   "team": "FC Koln",
   "spiele": 10,
   "summe": 23,
   "teamwert_roh": 2.3,
   "teamwert": "2.30"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 16-34 + 2026/2027: 1-1",
   "spiele": 180,
   "summe": 339,
   "wert_roh": 1.8833333333,
   "wert": "1.88"
  },
  "hauptwert_roh": 2.3,
  "hauptwert": "2.30",
  "abweichung_roh": 22.1238938053,
  "abweichung": "22.12",
  "anomalie": "leicht",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Viele Tore in Halbzeit 2",
  "text": "In den bisherigen Spielen beider Teams fielen in Halbzeit zwei durchschnittlich 2,30 Tore. Das sind 22,12 % mehr als im Liga-Durchschnitt."
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
   "summe": 21,
   "teamwert_roh": 2.1,
   "teamwert": "2.10"
  },
  "auswaerts": {
   "team": "Union Berlin",
   "spiele": 10,
   "summe": 21,
   "teamwert_roh": 2.1,
   "teamwert": "2.10"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 16-34 + 2026/2027: 1-1",
   "spiele": 180,
   "summe": 339,
   "wert_roh": 1.8833333333,
   "wert": "1.88"
  },
  "hauptwert_roh": 2.1,
  "hauptwert": "2.10",
  "abweichung_roh": 11.5044247788,
  "abweichung": "11.50",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "In den bisherigen Spielen fielen in Halbzeit zwei im Schnitt 2,10 Tore. Die Abweichung vom Liga-Durchschnitt beträgt +11,50 %."
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
   "summe": 8,
   "teamwert_roh": 0.8,
   "teamwert": "0.80"
  },
  "auswaerts": {
   "team": "Parma",
   "spiele": 10,
   "summe": 14,
   "teamwert_roh": 1.4,
   "teamwert": "1.40"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 294,
   "wert_roh": 1.47,
   "wert": "1.47"
  },
  "hauptwert_roh": 1.1,
  "hauptwert": "1.10",
  "abweichung_roh": -25.1700680272,
  "abweichung": "-25.17",
  "anomalie": "leicht",
  "richtung": "negativ",
  "vorlaeufig": false,
  "ueberschrift": "Wenige Tore in Halbzeit 2",
  "text": "In den bisherigen Spielen beider Teams fielen in Halbzeit zwei durchschnittlich 1,10 Tore. Das sind 25,17 % weniger als im Liga-Durchschnitt."
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
   "summe": 16,
   "teamwert_roh": 1.6,
   "teamwert": "1.60"
  },
  "auswaerts": {
   "team": "Villarreal",
   "spiele": 10,
   "summe": 10,
   "teamwert_roh": 1.0,
   "teamwert": "1.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 196,
   "summe": 313,
   "wert_roh": 1.5969387755,
   "wert": "1.60"
  },
  "hauptwert_roh": 1.3,
  "hauptwert": "1.30",
  "abweichung_roh": -18.5942492013,
  "abweichung": "-18.59",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "In den bisherigen Spielen fielen in Halbzeit zwei im Schnitt 1,30 Tore. Die Abweichung vom Liga-Durchschnitt beträgt −18,59 %."
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
   "summe": 13,
   "teamwert_roh": 1.3,
   "teamwert": "1.30"
  },
  "auswaerts": {
   "team": "Manchester City",
   "spiele": 10,
   "summe": 18,
   "teamwert_roh": 1.8,
   "teamwert": "1.80"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 304,
   "wert_roh": 1.52,
   "wert": "1.52"
  },
  "hauptwert_roh": 1.55,
  "hauptwert": "1.55",
  "abweichung_roh": 1.9736842105,
  "abweichung": "1.97",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "In den bisherigen Spielen fielen in Halbzeit zwei im Schnitt 1,55 Tore. Die Abweichung vom Liga-Durchschnitt beträgt +1,97 %."
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
   "summe": 9,
   "teamwert_roh": 0.9,
   "teamwert": "0.90"
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
   "summe": 294,
   "wert_roh": 1.47,
   "wert": "1.47"
  },
  "hauptwert_roh": 0.45,
  "hauptwert": "0.45",
  "abweichung_roh": -69.387755102,
  "abweichung": "-69.39",
  "anomalie": "stark",
  "richtung": "negativ",
  "vorlaeufig": true,
  "ueberschrift": "Wenige Tore in Halbzeit 2",
  "text": "In den bisherigen Spielen beider Teams fielen in Halbzeit zwei durchschnittlich 0,45 Tore. Das sind 69,39 % weniger als im Liga-Durchschnitt."
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
   "teamwert_roh": 1.0,
   "teamwert": "1.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 196,
   "summe": 313,
   "wert_roh": 1.5969387755,
   "wert": "1.60"
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
   "summe": 10,
   "teamwert_roh": 1.0,
   "teamwert": "1.00"
  },
  "auswaerts": {
   "team": "Mainz",
   "spiele": 10,
   "summe": 14,
   "teamwert_roh": 1.4,
   "teamwert": "1.40"
  },
  "ligareferenz": {
   "saison_spieltage": "2023/2024: 32-34 + 2024/2025: 1-17",
   "spiele": 180,
   "summe": 307,
   "wert_roh": 1.7055555556,
   "wert": "1.71"
  },
  "hauptwert_roh": 1.2,
  "hauptwert": "1.20",
  "abweichung_roh": -29.6416938111,
  "abweichung": "-29.64",
  "anomalie": "leicht",
  "richtung": "negativ",
  "vorlaeufig": false,
  "ueberschrift": "Wenige Tore in Halbzeit 2",
  "text": "In den bisherigen Spielen beider Teams fielen in Halbzeit zwei durchschnittlich 1,20 Tore. Das sind 29,64 % weniger als im Liga-Durchschnitt."
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
   "summe": 14,
   "teamwert_roh": 1.4,
   "teamwert": "1.40"
  },
  "auswaerts": {
   "team": "Racing Santander",
   "spiele": 1,
   "summe": 0,
   "teamwert_roh": 0.0,
   "teamwert": "0.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 196,
   "summe": 313,
   "wert_roh": 1.5969387755,
   "wert": "1.60"
  },
  "hauptwert_roh": 0.7,
  "hauptwert": "0.70",
  "abweichung_roh": -56.1661341853,
  "abweichung": "-56.17",
  "anomalie": "stark",
  "richtung": "negativ",
  "vorlaeufig": true,
  "ueberschrift": "Wenige Tore in Halbzeit 2",
  "text": "In den bisherigen Spielen beider Teams fielen in Halbzeit zwei durchschnittlich 0,70 Tore. Das sind 56,17 % weniger als im Liga-Durchschnitt."
 },
 {
  "testfall": "T18",
  "liga": "Serie A",
  "saison": "2026/2027",
  "spieltag": 1,
  "analysedatum": "2026-08-22",
  "heim": {
   "team": "Torino",
   "spiele": 10,
   "summe": 18,
   "teamwert_roh": 1.8,
   "teamwert": "1.80"
  },
  "auswaerts": {
   "team": "AC Milan",
   "spiele": 10,
   "summe": 13,
   "teamwert_roh": 1.3,
   "teamwert": "1.30"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 19-38",
   "spiele": 200,
   "summe": 296,
   "wert_roh": 1.48,
   "wert": "1.48"
  },
  "hauptwert_roh": 1.55,
  "hauptwert": "1.55",
  "abweichung_roh": 4.7297297297,
  "abweichung": "4.73",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "In den bisherigen Spielen fielen in Halbzeit zwei im Schnitt 1,55 Tore. Die Abweichung vom Liga-Durchschnitt beträgt +4,73 %."
 },
 {
  "testfall": "T19",
  "liga": "Serie A",
  "saison": "2026/2027",
  "spieltag": 1,
  "analysedatum": "2026-08-22",
  "heim": {
   "team": "Inter",
   "spiele": 10,
   "summe": 23,
   "teamwert_roh": 2.3,
   "teamwert": "2.30"
  },
  "auswaerts": {
   "team": "Monza",
   "spiele": 0,
   "summe": null,
   "teamwert_roh": null,
   "teamwert": null
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 19-38",
   "spiele": 200,
   "summe": 296,
   "wert_roh": 1.48,
   "wert": "1.48"
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
  "testfall": "T20",
  "liga": "Serie A",
  "saison": "2026/2027",
  "spieltag": 2,
  "analysedatum": "2026-08-28",
  "heim": {
   "team": "Monza",
   "spiele": 1,
   "summe": 3,
   "teamwert_roh": 3.0,
   "teamwert": "3.00"
  },
  "auswaerts": {
   "team": "Udinese",
   "spiele": 10,
   "summe": 13,
   "teamwert_roh": 1.3,
   "teamwert": "1.30"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 294,
   "wert_roh": 1.47,
   "wert": "1.47"
  },
  "hauptwert_roh": 2.15,
  "hauptwert": "2.15",
  "abweichung_roh": 46.2585034014,
  "abweichung": "46.26",
  "anomalie": "stark",
  "richtung": "positiv",
  "vorlaeufig": true,
  "ueberschrift": "Viele Tore in Halbzeit 2",
  "text": "In den bisherigen Spielen beider Teams fielen in Halbzeit zwei durchschnittlich 2,15 Tore. Das sind 46,26 % mehr als im Liga-Durchschnitt."
 }
]
```

Hinweise: gerundete Werte als Text mit Punkt (im Dashboard mit Komma); `summe` = Summe der Spielwerte (bei KPI 08 Anzahl BTTS-Spiele); `_roh`-Werte mit Toleranz 1e-9 vergleichen.

## 4. Eingabedaten zum Nachvollziehen

### T1 – Stuttgart – FC Koln (Bundesliga, 2026/2027, Spieltag 2, Analysedatum 2026-09-04)

**Stuttgart** – 10 gültige Spiele, Summe 23, Teamwert 2,30

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107988 | Stuttgart – RB Leipzig | 1:0 | 1 |
| 22.03.2026 | 114388 | Augsburg – Stuttgart | 2:2 | 4 |
| 04.04.2026 | 117441 | Stuttgart – Dortmund | 0:2 | 2 |
| 12.04.2026 | 118014 | Stuttgart – Hamburger SV | 2:0 | 2 |
| 19.04.2026 | 118339 | Bayern Munich – Stuttgart | 1:1 | 2 |
| 26.04.2026 | 118750 | Stuttgart – Werder Bremen | 1:0 | 1 |
| 02.05.2026 | 118986 | Hoffenheim – Stuttgart | 1:2 | 3 |
| 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 1:0 | 1 |
| 16.05.2026 | 120510 | Eintracht Frankfurt – Stuttgart | 2:0 | 2 |
| 28.08.2026 | 132783 | Bayern Munich – Stuttgart | 4:1 | 5 |

**FC Koln** – 10 gültige Spiele, Summe 23, Teamwert 2,30

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106583 | Hamburger SV – FC Koln | 0:0 | 0 |
| 21.03.2026 | 114289 | FC Koln – B. Monchengladbach | 1:1 | 2 |
| 05.04.2026 | 117540 | Eintracht Frankfurt – FC Koln | 2:2 | 4 |
| 12.04.2026 | 118013 | FC Koln – Werder Bremen | 2:1 | 3 |
| 17.04.2026 | 118161 | St. Pauli – FC Koln | 1:1 | 2 |
| 25.04.2026 | 118646 | FC Koln – Bayer Leverkusen | 1:1 | 2 |
| 02.05.2026 | 118987 | Union Berlin – FC Koln | 2:1 | 3 |
| 10.05.2026 | 119365 | FC Koln – Heidenheim | 0:1 | 1 |
| 16.05.2026 | 120509 | Bayern Munich – FC Koln | 2:0 | 2 |
| 29.08.2026 | 132873 | FC Koln – Hoffenheim | 3:1 | 4 |

### T2 – Bayer Leverkusen – Union Berlin (Bundesliga, 2026/2027, Spieltag 2, Analysedatum 2026-09-04)

**Bayer Leverkusen** – 10 gültige Spiele, Summe 21, Teamwert 2,10

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106579 | Bayer Leverkusen – Bayern Munich | 0:1 | 1 |
| 21.03.2026 | 114290 | Heidenheim – Bayer Leverkusen | 3:1 | 4 |
| 04.04.2026 | 117436 | Bayer Leverkusen – Wolfsburg | 4:0 | 4 |
| 11.04.2026 | 117899 | Dortmund – Bayer Leverkusen | 0:0 | 0 |
| 18.04.2026 | 118240 | Bayer Leverkusen – Augsburg | 0:1 | 1 |
| 25.04.2026 | 118646 | FC Koln – Bayer Leverkusen | 1:1 | 2 |
| 02.05.2026 | 118989 | Bayer Leverkusen – RB Leipzig | 2:1 | 3 |
| 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 1:0 | 1 |
| 16.05.2026 | 120508 | Bayer Leverkusen – Hamburger SV | 1:1 | 2 |
| 29.08.2026 | 132872 | Elversberg – Bayer Leverkusen | 1:2 | 3 |

**Union Berlin** – 10 gültige Spiele, Summe 21, Teamwert 2,10

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107987 | Freiburg – Union Berlin | 0:1 | 1 |
| 21.03.2026 | 114288 | Bayern Munich – Union Berlin | 2:0 | 2 |
| 05.04.2026 | 117539 | Union Berlin – St. Pauli | 1:0 | 1 |
| 11.04.2026 | 117900 | Heidenheim – Union Berlin | 1:1 | 2 |
| 18.04.2026 | 118242 | Union Berlin – Wolfsburg | 1:1 | 2 |
| 24.04.2026 | 118560 | RB Leipzig – Union Berlin | 1:1 | 2 |
| 02.05.2026 | 118987 | Union Berlin – FC Koln | 2:1 | 3 |
| 10.05.2026 | 119366 | Mainz – Union Berlin | 1:2 | 3 |
| 16.05.2026 | 120514 | Union Berlin – Augsburg | 2:0 | 2 |
| 29.08.2026 | 132876 | Union Berlin – Eintracht Frankfurt | 2:1 | 3 |

### T3 – Juventus – Parma (Serie A, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Juventus** – 10 gültige Spiele, Summe 8, Teamwert 0,80

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 21.03.2026 | 114299 | Juventus – Sassuolo | 0:1 | 1 |
| 06.04.2026 | 117656 | Juventus – Genoa | 0:0 | 0 |
| 11.04.2026 | 117911 | Atalanta – Juventus | 0:1 | 1 |
| 19.04.2026 | 118349 | Juventus – Bologna | 1:0 | 1 |
| 26.04.2026 | 118761 | AC Milan – Juventus | 0:0 | 0 |
| 03.05.2026 | 119096 | Juventus – Verona | 1:0 | 1 |
| 09.05.2026 | 119281 | Lecce – Juventus | 0:0 | 0 |
| 17.05.2026 | 120620 | Juventus – Fiorentina | 0:1 | 1 |
| 24.05.2026 | 120857 | Torino – Juventus | 2:1 | 3 |
| 23.08.2026 | 130758 | Frosinone – Juventus | 0:0 | 0 |

**Parma** – 10 gültige Spiele, Summe 14, Teamwert 1,40

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 21.03.2026 | 114297 | Parma – Cremonese | 0:2 | 2 |
| 04.04.2026 | 117451 | Lazio – Parma | 1:0 | 1 |
| 12.04.2026 | 118020 | Parma – Napoli | 0:1 | 1 |
| 18.04.2026 | 118254 | Udinese – Parma | 0:1 | 1 |
| 25.04.2026 | 118655 | Parma – Pisa | 1:0 | 1 |
| 03.05.2026 | 119097 | Inter – Parma | 1:0 | 1 |
| 10.05.2026 | 119377 | Parma – AS Roma | 2:2 | 4 |
| 17.05.2026 | 120618 | Como – Parma | 1:0 | 1 |
| 24.05.2026 | 120852 | Parma – Sassuolo | 1:0 | 1 |
| 22.08.2026 | 130663 | Parma – Cagliari | 0:1 | 1 |

### T4 – Atl. Madrid – Villarreal (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Atl. Madrid** – 10 gültige Spiele, Summe 16, Teamwert 1,60

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 22.03.2026 | 114444 | Real Madrid – Atl. Madrid | 3:1 | 4 |
| 04.04.2026 | 117485 | Atl. Madrid – Barcelona | 0:1 | 1 |
| 11.04.2026 | 117953 | Sevilla – Atl. Madrid | 0:0 | 0 |
| 22.04.2026 | 118500 | Elche – Atl. Madrid | 1:0 | 1 |
| 25.04.2026 | 118693 | Atl. Madrid – Ath Bilbao | 3:1 | 4 |
| 02.05.2026 | 119028 | Valencia – Atl. Madrid | 0:2 | 2 |
| 09.05.2026 | 119297 | Atl. Madrid – Celta Vigo | 0:1 | 1 |
| 12.05.2026 | 120229 | Osasuna – Atl. Madrid | 1:1 | 2 |
| 17.05.2026 | 120662 | Atl. Madrid – Girona | 0:0 | 0 |
| 24.05.2026 | 120872 | Villarreal – Atl. Madrid | 1:0 | 1 |

**Villarreal** – 10 gültige Spiele, Summe 10, Teamwert 1,00

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 06.04.2026 | 117677 | Girona – Villarreal | 0:0 | 0 |
| 12.04.2026 | 118055 | Ath Bilbao – Villarreal | 1:0 | 1 |
| 23.04.2026 | 118530 | Oviedo – Villarreal | 1:0 | 1 |
| 26.04.2026 | 118794 | Villarreal – Celta Vigo | 0:1 | 1 |
| 02.05.2026 | 119027 | Villarreal – Levante | 4:1 | 5 |
| 10.05.2026 | 119413 | Mallorca – Villarreal | 0:0 | 0 |
| 13.05.2026 | 120439 | Villarreal – Sevilla | 0:1 | 1 |
| 17.05.2026 | 120667 | Rayo Vallecano – Villarreal | 0:0 | 0 |
| 24.05.2026 | 120872 | Villarreal – Atl. Madrid | 1:0 | 1 |
| 16.08.2026 | 129483 | Racing Santander – Villarreal | 0:0 | 0 |

### T5 – Crystal Palace – Manchester City (Premier League, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Crystal Palace** – 10 gültige Spiele, Summe 13, Teamwert 1,30

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107978 | Crystal Palace – Leeds | 0:0 | 0 |
| 12.04.2026 | 118005 | Crystal Palace – Newcastle | 2:0 | 2 |
| 20.04.2026 | 118408 | Crystal Palace – West Ham | 0:0 | 0 |
| 25.04.2026 | 118603 | Liverpool – Crystal Palace | 1:1 | 2 |
| 03.05.2026 | 119074 | Bournemouth – Crystal Palace | 1:0 | 1 |
| 10.05.2026 | 119351 | Crystal Palace – Everton | 1:1 | 2 |
| 13.05.2026 | 120425 | Manchester City – Crystal Palace | 1:0 | 1 |
| 17.05.2026 | 120589 | Brentford – Crystal Palace | 1:1 | 2 |
| 24.05.2026 | 120843 | Crystal Palace – Arsenal | 1:1 | 2 |
| 22.08.2026 | 130611 | Everton – Crystal Palace | 1:0 | 1 |

**Manchester City** – 10 gültige Spiele, Summe 18, Teamwert 1,80

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106539 | West Ham – Manchester City | 0:0 | 0 |
| 12.04.2026 | 118008 | Chelsea – Manchester City | 0:3 | 3 |
| 19.04.2026 | 118329 | Manchester City – Arsenal | 1:0 | 1 |
| 22.04.2026 | 118479 | Burnley – Manchester City | 0:0 | 0 |
| 04.05.2026 | 119163 | Everton – Manchester City | 3:2 | 5 |
| 09.05.2026 | 119254 | Manchester City – Brentford | 3:0 | 3 |
| 13.05.2026 | 120425 | Manchester City – Crystal Palace | 1:0 | 1 |
| 19.05.2026 | 120707 | Bournemouth – Manchester City | 0:1 | 1 |
| 24.05.2026 | 120846 | Manchester City – Aston Villa | 0:2 | 2 |
| 23.08.2026 | 130749 | Manchester City – Bournemouth | 2:0 | 2 |

### T6 – Fiorentina – Frosinone (Serie A, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Fiorentina** – 10 gültige Spiele, Summe 9, Teamwert 0,90

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 22.03.2026 | 114403 | Fiorentina – Inter | 1:0 | 1 |
| 04.04.2026 | 117450 | Verona – Fiorentina | 0:1 | 1 |
| 13.04.2026 | 118084 | Fiorentina – Lazio | 0:0 | 0 |
| 20.04.2026 | 118410 | Lecce – Fiorentina | 1:0 | 1 |
| 26.04.2026 | 118758 | Fiorentina – Sassuolo | 0:0 | 0 |
| 04.05.2026 | 119165 | AS Roma – Fiorentina | 1:0 | 1 |
| 10.05.2026 | 119376 | Fiorentina – Genoa | 0:0 | 0 |
| 17.05.2026 | 120620 | Juventus – Fiorentina | 0:1 | 1 |
| 22.05.2026 | 120772 | Fiorentina – Atalanta | 0:1 | 1 |
| 24.08.2026 | 130861 | AS Roma – Fiorentina | 3:0 | 3 |

**Frosinone** – 1 gültige Spiele, Summe 0, Teamwert 0,00

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 23.08.2026 | 130758 | Frosinone – Juventus | 0:0 | 0 |

### T7 – Malaga – Dep. A Coruna (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Malaga** – 0 gültige Spiele, Summe –, Teamwert –

Keine Ligaspiele im Zeitfenster.

**Dep. A Coruna** – 1 gültige Spiele, Summe 1, Teamwert 1,00

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 17.08.2026 | 130470 | Dep. A Coruna – Elche | 0:1 | 1 |

### T8 – Union Berlin – Mainz (Bundesliga, 2024/2025, Spieltag 18, Analysedatum 2025-01-19)

**Union Berlin** – 10 gültige Spiele, Summe 10, Teamwert 1,00

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 27.10.2024 | 14469 | Union Berlin – Eintracht Frankfurt | 1:0 | 1 |
| 02.11.2024 | 14462 | Bayern Munich – Union Berlin | 1:0 | 1 |
| 08.11.2024 | 14458 | Union Berlin – Freiburg | 0:0 | 0 |
| 23.11.2024 | 14448 | Wolfsburg – Union Berlin | 1:0 | 1 |
| 30.11.2024 | 14438 | Union Berlin – Bayer Leverkusen | 0:1 | 1 |
| 06.12.2024 | 14431 | Stuttgart – Union Berlin | 3:1 | 4 |
| 14.12.2024 | 14421 | Union Berlin – Bochum | 0:0 | 0 |
| 21.12.2024 | 14412 | Werder Bremen – Union Berlin | 1:0 | 1 |
| 11.01.2025 | 14400 | Heidenheim – Union Berlin | 1:0 | 1 |
| 15.01.2025 | 14389 | Union Berlin – Augsburg | 0:0 | 0 |

**Mainz** – 10 gültige Spiele, Summe 14, Teamwert 1,40

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 25.10.2024 | 14476 | Mainz – B. Monchengladbach | 1:1 | 2 |
| 03.11.2024 | 14460 | Freiburg – Mainz | 0:0 | 0 |
| 09.11.2024 | 14455 | Mainz – Dortmund | 1:0 | 1 |
| 24.11.2024 | 14442 | Holstein Kiel – Mainz | 0:1 | 1 |
| 01.12.2024 | 14433 | Mainz – Hoffenheim | 0:0 | 0 |
| 08.12.2024 | 14424 | Wolfsburg – Mainz | 3:1 | 4 |
| 14.12.2024 | 14420 | Mainz – Bayern Munich | 1:1 | 2 |
| 21.12.2024 | 14408 | Eintracht Frankfurt – Mainz | 1:1 | 2 |
| 11.01.2025 | 14402 | Mainz – Bochum | 1:0 | 1 |
| 14.01.2025 | 14392 | Bayer Leverkusen – Mainz | 1:0 | 1 |

### T9 – Getafe – Racing Santander (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Getafe** – 10 gültige Spiele, Summe 14, Teamwert 1,40

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 05.04.2026 | 117581 | Getafe – Ath Bilbao | 1:0 | 1 |
| 13.04.2026 | 118088 | Levante – Getafe | 1:0 | 1 |
| 22.04.2026 | 118501 | Real Sociedad – Getafe | 0:0 | 0 |
| 25.04.2026 | 118691 | Getafe – Barcelona | 0:1 | 1 |
| 03.05.2026 | 119130 | Getafe – Rayo Vallecano | 0:1 | 1 |
| 10.05.2026 | 119415 | Oviedo – Getafe | 0:0 | 0 |
| 13.05.2026 | 120441 | Getafe – Mallorca | 1:1 | 2 |
| 17.05.2026 | 120663 | Elche – Getafe | 2:2 | 4 |
| 23.05.2026 | 120811 | Getafe – Osasuna | 1:0 | 1 |
| 15.08.2026 | 128152 | Alaves – Getafe | 3:0 | 3 |

**Racing Santander** – 1 gültige Spiele, Summe 0, Teamwert 0,00

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 16.08.2026 | 129483 | Racing Santander – Villarreal | 0:0 | 0 |

### T18 – Torino – AC Milan (Serie A, 2026/2027, Spieltag 1, Analysedatum 2026-08-22)

**Torino** – 10 gültige Spiele, Summe 18, Teamwert 1,80

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 13.03.2026 | 105945 | Torino – Parma | 3:0 | 3 |
| 21.03.2026 | 114298 | AC Milan – Torino | 2:1 | 3 |
| 05.04.2026 | 117551 | Pisa – Torino | 0:1 | 1 |
| 11.04.2026 | 117909 | Torino – Verona | 1:0 | 1 |
| 19.04.2026 | 118346 | Cremonese – Torino | 0:0 | 0 |
| 26.04.2026 | 118760 | Torino – Inter | 2:1 | 3 |
| 02.05.2026 | 118997 | Udinese – Torino | 1:0 | 1 |
| 08.05.2026 | 119215 | Torino – Sassuolo | 2:1 | 3 |
| 17.05.2026 | 120624 | Cagliari – Torino | 0:0 | 0 |
| 24.05.2026 | 120857 | Torino – Juventus | 2:1 | 3 |

**AC Milan** – 10 gültige Spiele, Summe 13, Teamwert 1,30

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 15.03.2026 | 108000 | Lazio – AC Milan | 0:0 | 0 |
| 21.03.2026 | 114298 | AC Milan – Torino | 2:1 | 3 |
| 06.04.2026 | 117657 | Napoli – AC Milan | 1:0 | 1 |
| 11.04.2026 | 117910 | AC Milan – Udinese | 0:1 | 1 |
| 19.04.2026 | 118347 | Verona – AC Milan | 0:0 | 0 |
| 26.04.2026 | 118761 | AC Milan – Juventus | 0:0 | 0 |
| 03.05.2026 | 119095 | Sassuolo – AC Milan | 1:0 | 1 |
| 10.05.2026 | 119378 | AC Milan – Atalanta | 2:1 | 3 |
| 17.05.2026 | 120619 | Genoa – AC Milan | 1:2 | 3 |
| 24.05.2026 | 120854 | AC Milan – Cagliari | 0:1 | 1 |

### T19 – Inter – Monza (Serie A, 2026/2027, Spieltag 1, Analysedatum 2026-08-22)

**Inter** – 10 gültige Spiele, Summe 23, Teamwert 2,30

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106591 | Inter – Atalanta | 0:1 | 1 |
| 22.03.2026 | 114403 | Fiorentina – Inter | 1:0 | 1 |
| 05.04.2026 | 117552 | Inter – AS Roma | 3:1 | 4 |
| 12.04.2026 | 118022 | Como – Inter | 1:3 | 4 |
| 17.04.2026 | 118165 | Inter – Cagliari | 3:0 | 3 |
| 26.04.2026 | 118760 | Torino – Inter | 2:1 | 3 |
| 03.05.2026 | 119097 | Inter – Parma | 1:0 | 1 |
| 09.05.2026 | 119280 | Lazio – Inter | 0:1 | 1 |
| 17.05.2026 | 120622 | Inter – Verona | 1:1 | 2 |
| 23.05.2026 | 120798 | Bologna – Inter | 1:2 | 3 |

**Monza** – 0 gültige Spiele, Summe –, Teamwert –

Keine Ligaspiele im Zeitfenster.

### T20 – Monza – Udinese (Serie A, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Monza** – 1 gültige Spiele, Summe 3, Teamwert 3,00

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 22.08.2026 | 130660 | Inter – Monza | 3:0 | 3 |

**Udinese** – 10 gültige Spiele, Summe 13, Teamwert 1,30

| Datum | id | Begegnung | HZ2 T:U | zählt |
|---|---|---|---|---|
| 20.03.2026 | 114216 | Genoa – Udinese | 0:2 | 2 |
| 06.04.2026 | 117654 | Udinese – Como | 0:0 | 0 |
| 11.04.2026 | 117910 | AC Milan – Udinese | 0:1 | 1 |
| 18.04.2026 | 118254 | Udinese – Parma | 0:1 | 1 |
| 27.04.2026 | 118827 | Lazio – Udinese | 3:2 | 5 |
| 02.05.2026 | 118997 | Udinese – Torino | 1:0 | 1 |
| 09.05.2026 | 119279 | Cagliari – Udinese | 0:2 | 2 |
| 17.05.2026 | 120626 | Udinese – Cremonese | 0:0 | 0 |
| 24.05.2026 | 120853 | Napoli – Udinese | 0:0 | 0 |
| 22.08.2026 | 130661 | Udinese – Como | 0:1 | 1 |

### Ligareferenzen je Liga und Spieltag

**Bundesliga, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-09-04):** 2025/2026: 16-34 + 2026/2027: 1-1 → 180 Spiele, Summe 339, Ligareferenz 1,88

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 16 | 9 | 22 |  |
| 2025/2026 | 17 | 9 | 15 |  |
| 2025/2026 | 18 | 9 | 22 |  |
| 2025/2026 | 19 | 9 | 15 |  |
| 2025/2026 | 20 | 9 | 14 |  |
| 2025/2026 | 21 | 9 | 12 |  |
| 2025/2026 | 22 | 9 | 18 |  |
| 2025/2026 | 23 | 9 | 19 |  |
| 2025/2026 | 24 | 9 | 15 |  |
| 2025/2026 | 25 | 9 | 19 |  |
| 2025/2026 | 26 | 9 | 9 |  |
| 2025/2026 | 27 | 9 | 20 |  |
| 2025/2026 | 28 | 9 | 22 |  |
| 2025/2026 | 29 | 9 | 14 |  |
| 2025/2026 | 30 | 9 | 16 |  |
| 2025/2026 | 31 | 9 | 12 |  |
| 2025/2026 | 32 | 9 | 21 |  |
| 2025/2026 | 33 | 9 | 15 |  |
| 2025/2026 | 34 | 9 | 17 |  |
| 2026/2027 | 1 | 9 | 22 |  |

**Serie A, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-28):** 2025/2026: 20-38 + 2026/2027: 1-1 → 200 Spiele, Summe 294, Ligareferenz 1,47

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 17 |  |
| 2025/2026 | 21 | 10 | 7 |  |
| 2025/2026 | 22 | 10 | 21 |  |
| 2025/2026 | 23 | 10 | 16 |  |
| 2025/2026 | 24 | 10 | 16 |  |
| 2025/2026 | 25 | 10 | 18 |  |
| 2025/2026 | 26 | 10 | 12 |  |
| 2025/2026 | 27 | 10 | 18 |  |
| 2025/2026 | 28 | 10 | 19 |  |
| 2025/2026 | 29 | 10 | 16 |  |
| 2025/2026 | 30 | 10 | 15 |  |
| 2025/2026 | 31 | 10 | 13 |  |
| 2025/2026 | 32 | 10 | 13 |  |
| 2025/2026 | 33 | 10 | 8 |  |
| 2025/2026 | 34 | 10 | 12 |  |
| 2025/2026 | 35 | 10 | 10 |  |
| 2025/2026 | 36 | 10 | 18 |  |
| 2025/2026 | 37 | 10 | 12 |  |
| 2025/2026 | 38 | 10 | 15 |  |
| 2026/2027 | 1 | 10 | 18 |  |

**LaLiga, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-20):** 2025/2026: 20-38 + 2026/2027: 1-1 → 196 Spiele, Summe 313, Ligareferenz 1,60

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 18 |  |
| 2025/2026 | 21 | 10 | 26 |  |
| 2025/2026 | 22 | 10 | 11 |  |
| 2025/2026 | 23 | 10 | 19 |  |
| 2025/2026 | 24 | 10 | 16 |  |
| 2025/2026 | 25 | 10 | 21 |  |
| 2025/2026 | 26 | 10 | 14 |  |
| 2025/2026 | 27 | 10 | 16 |  |
| 2025/2026 | 28 | 10 | 15 |  |
| 2025/2026 | 29 | 10 | 16 |  |
| 2025/2026 | 30 | 10 | 12 |  |
| 2025/2026 | 31 | 10 | 12 |  |
| 2025/2026 | 32 | 10 | 11 |  |
| 2025/2026 | 33 | 10 | 20 |  |
| 2025/2026 | 34 | 10 | 22 |  |
| 2025/2026 | 35 | 10 | 13 |  |
| 2025/2026 | 36 | 10 | 13 |  |
| 2025/2026 | 37 | 10 | 12 |  |
| 2025/2026 | 38 | 10 | 17 |  |
| 2026/2027 | 1 | 6 | 9 |  |

**Premier League, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-28):** 2025/2026: 20-38 + 2026/2027: 1-1 → 200 Spiele, Summe 304, Ligareferenz 1,52

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 21 |  |
| 2025/2026 | 21 | 10 | 18 |  |
| 2025/2026 | 22 | 10 | 10 |  |
| 2025/2026 | 23 | 10 | 16 |  |
| 2025/2026 | 24 | 10 | 17 |  |
| 2025/2026 | 25 | 10 | 15 |  |
| 2025/2026 | 26 | 10 | 13 |  |
| 2025/2026 | 27 | 10 | 12 |  |
| 2025/2026 | 28 | 10 | 16 |  |
| 2025/2026 | 29 | 10 | 12 |  |
| 2025/2026 | 30 | 10 | 9 |  |
| 2025/2026 | 31 | 10 | 20 |  |
| 2025/2026 | 32 | 10 | 14 |  |
| 2025/2026 | 33 | 10 | 16 |  |
| 2025/2026 | 34 | 10 | 14 |  |
| 2025/2026 | 35 | 10 | 20 |  |
| 2025/2026 | 36 | 10 | 14 |  |
| 2025/2026 | 37 | 10 | 20 |  |
| 2025/2026 | 38 | 10 | 15 |  |
| 2026/2027 | 1 | 10 | 12 |  |

**Bundesliga, analysiert Saison 2024/2025 Spieltag 18 (Stichtag 2025-01-19):** 2023/2024: 32-34 + 2024/2025: 1-17 → 180 Spiele, Summe 307, Ligareferenz 1,71

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2023/2024 | 32 | 9 | 15 |  |
| 2023/2024 | 33 | 9 | 8 |  |
| 2023/2024 | 34 | 9 | 22 |  |
| 2024/2025 | 1 | 9 | 20 |  |
| 2024/2025 | 2 | 9 | 12 |  |
| 2024/2025 | 3 | 9 | 18 |  |
| 2024/2025 | 4 | 9 | 17 |  |
| 2024/2025 | 5 | 9 | 15 |  |
| 2024/2025 | 6 | 9 | 12 |  |
| 2024/2025 | 7 | 9 | 19 |  |
| 2024/2025 | 8 | 9 | 15 |  |
| 2024/2025 | 9 | 9 | 10 |  |
| 2024/2025 | 10 | 9 | 10 |  |
| 2024/2025 | 11 | 9 | 16 |  |
| 2024/2025 | 12 | 9 | 16 |  |
| 2024/2025 | 13 | 9 | 24 |  |
| 2024/2025 | 14 | 9 | 12 |  |
| 2024/2025 | 15 | 9 | 14 |  |
| 2024/2025 | 16 | 9 | 11 |  |
| 2024/2025 | 17 | 9 | 21 |  |

**Serie A, analysiert Saison 2026/2027 Spieltag 1 (Stichtag 2026-08-22):** 2025/2026: 19-38 → 200 Spiele, Summe 296, Ligareferenz 1,48

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 19 | 10 | 20 |  |
| 2025/2026 | 20 | 10 | 17 |  |
| 2025/2026 | 21 | 10 | 7 |  |
| 2025/2026 | 22 | 10 | 21 |  |
| 2025/2026 | 23 | 10 | 16 |  |
| 2025/2026 | 24 | 10 | 16 |  |
| 2025/2026 | 25 | 10 | 18 |  |
| 2025/2026 | 26 | 10 | 12 |  |
| 2025/2026 | 27 | 10 | 18 |  |
| 2025/2026 | 28 | 10 | 19 |  |
| 2025/2026 | 29 | 10 | 16 |  |
| 2025/2026 | 30 | 10 | 15 |  |
| 2025/2026 | 31 | 10 | 13 |  |
| 2025/2026 | 32 | 10 | 13 |  |
| 2025/2026 | 33 | 10 | 8 |  |
| 2025/2026 | 34 | 10 | 12 |  |
| 2025/2026 | 35 | 10 | 10 |  |
| 2025/2026 | 36 | 10 | 18 |  |
| 2025/2026 | 37 | 10 | 12 |  |
| 2025/2026 | 38 | 10 | 15 |  |

