# Testfall KPI 05 – Ecken

**Spezifikation v2.1** · Stand 08.11.2026

**Regelwerk:** `03_KPI_Regelwerk.md`, Abschnitte 1, 1.1, 2, 9.0 und 9.1
**Datenbasis:** `Database-Soccer-Intelligence.xlsx`, SHA-256 `f37e36d301767321575aeadf908c39e288b9a655d02d85d5bcfde0507effdc34`
**Status:** **bestätigt von Carsten am 08.11.2026** (gemeinsamer Rundgang KPI 05–09 mit je einer normalen Partie und einem Aufsteiger). Erzeugt von Claude mit einer unabhängigen Berechnung direkt aus der Excel-Datei. Nachprüfung per Excel: `Testfaelle_KPI05-09_Nachpruefung.xlsx`.

**Änderung 08.11.2026 (Carsten, Rundgang):** Teamwert zählt jetzt eigene **und** gegnerische Ecken, Hauptwert ist der Mittelwert (System wie KPI 02). Alle Werte dieser Datei sind neu berechnet.

**Änderung 08.11.2026 (Carsten):** Alle Werte mit **zwei Nachkommastellen**, auch die Abweichung. Die Einstufung richtet sich nach der auf zwei Stellen gerundeten Abweichung (Regelwerk 2.3).

Dieser Testfall ist die verbindliche Referenz für die Umsetzung (Etappe H). Die JSON-Blöcke werden zu automatischen Tests.

---

## 1. Regeln, die dieser Testfall prüft

- Teamwert = Ø Ecken **beider** Mannschaften (W + X, eigene + gegnerische) in den Spielen des Teams; Spiele mit leerem W oder X werden ausgelassen.
- Erwartete Ecken = (Teamwert Heim + Teamwert Auswärts) / 2 (Mittelwert, wie KPI 02).
- Ligareferenz = Ø Ecken **beider** Teams pro Spiel (W + X); Spiele mit leerem W oder X werden ausgelassen.
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
| T10 | Bundesliga | 2026/2027 | 1 | 2026-08-28 | Bayern Munich | Stuttgart | Rundgang 1. Spieltag 2026/27, normale Partie (KPI 05: nur eigene Ecken hätten +35,4 % ergeben, neu +10,3 %; KPI 09: positive Anomalie) |
| T11 | Bundesliga | 2026/2027 | 1 | 2026-08-28 | Elversberg | Bayer Leverkusen | Rundgang 1. Spieltag 2026/27, Aufsteiger ohne Spiele → nicht berechenbar |
| T12 | Bundesliga | 2026/2027 | 2 | 2026-09-04 | B. Monchengladbach | Elversberg | Rundgang 2. Spieltag 2026/27, Aufsteiger mit 1 Spiel → vorläufig; negative Anomalie (Gladbach: wenige eigene, viele gegnerische Ecken) |

Analysedatum = „Datum von“ des Spieltags im Spielplan (T8: Spieldatum, weil das Spiel aus einer abgeschlossenen Saison stammt).

### Ergebnisse auf einen Blick

| Testfall | Teamwert Heim | Teamwert Auswärts | Ligareferenz | Hauptwert | Abweichung | Anomalie | vorläufig |
|---|---|---|---|---|---|---|---|
| T1 | 11,10 (10 Sp.) | 9,80 (10 Sp.) | 9,77 (180 Sp.) | 10,45 | +6,94 % | keine | nein |
| T2 | 9,90 (10 Sp.) | 10,90 (10 Sp.) | 9,77 (180 Sp.) | 10,40 | +6,42 % | keine | nein |
| T3 | 10,70 (10 Sp.) | 9,30 (10 Sp.) | 8,73 (200 Sp.) | 10,00 | +14,55 % | keine | nein |
| T4 | 11,10 (10 Sp.) | 11,70 (10 Sp.) | 9,60 (196 Sp.) | 11,40 | +18,72 % | keine | nein |
| T5 | 10,00 (10 Sp.) | 13,50 (10 Sp.) | 10,11 (200 Sp.) | 11,75 | +16,22 % | keine | nein |
| T6 | 8,20 (10 Sp.) | 15,00 (1 Sp.) | 8,73 (200 Sp.) | 11,60 | +32,88 % | leicht | ja |
| T7 | – (0 Sp.) | 8,00 (1 Sp.) | 9,60 (196 Sp.) | – | – | – | ja |
| T8 | 8,78 (9 Sp.) | 10,00 (10 Sp.) | 9,73 (179 Sp.) | 9,39 | −3,52 % | keine | ja |
| T9 | 7,40 (10 Sp.) | 16,00 (1 Sp.) | 9,60 (196 Sp.) | 11,70 | +21,85 % | leicht | ja |
| T10 | 10,50 (10 Sp.) | 11,00 (10 Sp.) | 9,75 (180 Sp.) | 10,75 | +10,26 % | keine | nein |
| T11 | – (0 Sp.) | 9,90 (10 Sp.) | 9,75 (180 Sp.) | – | – | – | ja |
| T12 | 8,10 (10 Sp.) | 7,00 (1 Sp.) | 9,77 (180 Sp.) | 7,55 | −22,74 % | leicht | ja |

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
   "summe": 111,
   "teamwert_roh": 11.1,
   "teamwert": "11.10"
  },
  "auswaerts": {
   "team": "FC Koln",
   "spiele": 10,
   "summe": 98,
   "teamwert_roh": 9.8,
   "teamwert": "9.80"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 16-34 + 2026/2027: 1-1",
   "spiele": 180,
   "summe": 1759,
   "wert_roh": 9.7722222222,
   "wert": "9.77"
  },
  "hauptwert_roh": 10.45,
  "hauptwert": "10.45",
  "abweichung_roh": 6.935758954,
  "abweichung": "6.94",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Eckballindikator liegt bei 10,45 Ecken. Die Abweichung vom Liga-Durchschnitt beträgt +6,94 %."
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
   "summe": 99,
   "teamwert_roh": 9.9,
   "teamwert": "9.90"
  },
  "auswaerts": {
   "team": "Union Berlin",
   "spiele": 10,
   "summe": 109,
   "teamwert_roh": 10.9,
   "teamwert": "10.90"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 16-34 + 2026/2027: 1-1",
   "spiele": 180,
   "summe": 1759,
   "wert_roh": 9.7722222222,
   "wert": "9.77"
  },
  "hauptwert_roh": 10.4,
  "hauptwert": "10.40",
  "abweichung_roh": 6.4241046049,
  "abweichung": "6.42",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Eckballindikator liegt bei 10,40 Ecken. Die Abweichung vom Liga-Durchschnitt beträgt +6,42 %."
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
   "summe": 107,
   "teamwert_roh": 10.7,
   "teamwert": "10.70"
  },
  "auswaerts": {
   "team": "Parma",
   "spiele": 10,
   "summe": 93,
   "teamwert_roh": 9.3,
   "teamwert": "9.30"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 1746,
   "wert_roh": 8.73,
   "wert": "8.73"
  },
  "hauptwert_roh": 10.0,
  "hauptwert": "10.00",
  "abweichung_roh": 14.5475372279,
  "abweichung": "14.55",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Eckballindikator liegt bei 10,00 Ecken. Die Abweichung vom Liga-Durchschnitt beträgt +14,55 %."
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
   "summe": 111,
   "teamwert_roh": 11.1,
   "teamwert": "11.10"
  },
  "auswaerts": {
   "team": "Villarreal",
   "spiele": 10,
   "summe": 117,
   "teamwert_roh": 11.7,
   "teamwert": "11.70"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 196,
   "summe": 1882,
   "wert_roh": 9.6020408163,
   "wert": "9.60"
  },
  "hauptwert_roh": 11.4,
  "hauptwert": "11.40",
  "abweichung_roh": 18.7247608927,
  "abweichung": "18.72",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Eckballindikator liegt bei 11,40 Ecken. Die Abweichung vom Liga-Durchschnitt beträgt +18,72 %."
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
   "summe": 100,
   "teamwert_roh": 10.0,
   "teamwert": "10.00"
  },
  "auswaerts": {
   "team": "Manchester City",
   "spiele": 10,
   "summe": 135,
   "teamwert_roh": 13.5,
   "teamwert": "13.50"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 2022,
   "wert_roh": 10.11,
   "wert": "10.11"
  },
  "hauptwert_roh": 11.75,
  "hauptwert": "11.75",
  "abweichung_roh": 16.2215628091,
  "abweichung": "16.22",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Eckballindikator liegt bei 11,75 Ecken. Die Abweichung vom Liga-Durchschnitt beträgt +16,22 %."
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
   "summe": 82,
   "teamwert_roh": 8.2,
   "teamwert": "8.20"
  },
  "auswaerts": {
   "team": "Frosinone",
   "spiele": 1,
   "summe": 15,
   "teamwert_roh": 15.0,
   "teamwert": "15.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 1746,
   "wert_roh": 8.73,
   "wert": "8.73"
  },
  "hauptwert_roh": 11.6,
  "hauptwert": "11.60",
  "abweichung_roh": 32.8751431844,
  "abweichung": "32.88",
  "anomalie": "leicht",
  "richtung": "positiv",
  "vorlaeufig": true,
  "ueberschrift": "Viele Ecken erwartet",
  "text": "Für diese Begegnung werden 11,60 Ecken erwartet. Das liegt 32,88 % über dem Liga-Durchschnitt."
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
   "summe": 8,
   "teamwert_roh": 8.0,
   "teamwert": "8.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 196,
   "summe": 1882,
   "wert_roh": 9.6020408163,
   "wert": "9.60"
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
   "spiele": 9,
   "summe": 79,
   "teamwert_roh": 8.7777777778,
   "teamwert": "8.78"
  },
  "auswaerts": {
   "team": "Mainz",
   "spiele": 10,
   "summe": 100,
   "teamwert_roh": 10.0,
   "teamwert": "10.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2023/2024: 32-34 + 2024/2025: 1-17",
   "spiele": 179,
   "summe": 1742,
   "wert_roh": 9.7318435754,
   "wert": "9.73"
  },
  "hauptwert_roh": 9.3888888889,
  "hauptwert": "9.39",
  "abweichung_roh": -3.5240464345,
  "abweichung": "-3.52",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": true,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Eckballindikator liegt bei 9,39 Ecken. Die Abweichung vom Liga-Durchschnitt beträgt −3,52 %."
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
   "summe": 74,
   "teamwert_roh": 7.4,
   "teamwert": "7.40"
  },
  "auswaerts": {
   "team": "Racing Santander",
   "spiele": 1,
   "summe": 16,
   "teamwert_roh": 16.0,
   "teamwert": "16.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 196,
   "summe": 1882,
   "wert_roh": 9.6020408163,
   "wert": "9.60"
  },
  "hauptwert_roh": 11.7,
  "hauptwert": "11.70",
  "abweichung_roh": 21.8490967056,
  "abweichung": "21.85",
  "anomalie": "leicht",
  "richtung": "positiv",
  "vorlaeufig": true,
  "ueberschrift": "Viele Ecken erwartet",
  "text": "Für diese Begegnung werden 11,70 Ecken erwartet. Das liegt 21,85 % über dem Liga-Durchschnitt."
 },
 {
  "testfall": "T10",
  "liga": "Bundesliga",
  "saison": "2026/2027",
  "spieltag": 1,
  "analysedatum": "2026-08-28",
  "heim": {
   "team": "Bayern Munich",
   "spiele": 10,
   "summe": 105,
   "teamwert_roh": 10.5,
   "teamwert": "10.50"
  },
  "auswaerts": {
   "team": "Stuttgart",
   "spiele": 10,
   "summe": 110,
   "teamwert_roh": 11.0,
   "teamwert": "11.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 15-34",
   "spiele": 180,
   "summe": 1755,
   "wert_roh": 9.75,
   "wert": "9.75"
  },
  "hauptwert_roh": 10.75,
  "hauptwert": "10.75",
  "abweichung_roh": 10.2564102564,
  "abweichung": "10.26",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Eckballindikator liegt bei 10,75 Ecken. Die Abweichung vom Liga-Durchschnitt beträgt +10,26 %."
 },
 {
  "testfall": "T11",
  "liga": "Bundesliga",
  "saison": "2026/2027",
  "spieltag": 1,
  "analysedatum": "2026-08-28",
  "heim": {
   "team": "Elversberg",
   "spiele": 0,
   "summe": null,
   "teamwert_roh": null,
   "teamwert": null
  },
  "auswaerts": {
   "team": "Bayer Leverkusen",
   "spiele": 10,
   "summe": 99,
   "teamwert_roh": 9.9,
   "teamwert": "9.90"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 15-34",
   "spiele": 180,
   "summe": 1755,
   "wert_roh": 9.75,
   "wert": "9.75"
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
  "testfall": "T12",
  "liga": "Bundesliga",
  "saison": "2026/2027",
  "spieltag": 2,
  "analysedatum": "2026-09-04",
  "heim": {
   "team": "B. Monchengladbach",
   "spiele": 10,
   "summe": 81,
   "teamwert_roh": 8.1,
   "teamwert": "8.10"
  },
  "auswaerts": {
   "team": "Elversberg",
   "spiele": 1,
   "summe": 7,
   "teamwert_roh": 7.0,
   "teamwert": "7.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 16-34 + 2026/2027: 1-1",
   "spiele": 180,
   "summe": 1759,
   "wert_roh": 9.7722222222,
   "wert": "9.77"
  },
  "hauptwert_roh": 7.55,
  "hauptwert": "7.55",
  "abweichung_roh": -22.7401932916,
  "abweichung": "-22.74",
  "anomalie": "leicht",
  "richtung": "negativ",
  "vorlaeufig": true,
  "ueberschrift": "Wenige Ecken erwartet",
  "text": "Für diese Begegnung werden 7,55 Ecken erwartet. Das liegt 22,74 % unter dem Liga-Durchschnitt."
 }
]
```

Hinweise: gerundete Werte als Text mit Punkt (im Dashboard mit Komma); `summe` = Summe der Spielwerte (bei KPI 08 Anzahl BTTS-Spiele); `_roh`-Werte mit Toleranz 1e-9 vergleichen.

## 4. Eingabedaten zum Nachvollziehen

### T1 – Stuttgart – FC Koln (Bundesliga, 2026/2027, Spieltag 2, Analysedatum 2026-09-04)

**Stuttgart** – 10 gültige Spiele, Summe 111, Teamwert 11,10

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107988 | Stuttgart – RB Leipzig | 5:6 | 11 |
| 22.03.2026 | 114388 | Augsburg – Stuttgart | 2:5 | 7 |
| 04.04.2026 | 117441 | Stuttgart – Dortmund | 5:2 | 7 |
| 12.04.2026 | 118014 | Stuttgart – Hamburger SV | 8:2 | 10 |
| 19.04.2026 | 118339 | Bayern Munich – Stuttgart | 11:3 | 14 |
| 26.04.2026 | 118750 | Stuttgart – Werder Bremen | 14:2 | 16 |
| 02.05.2026 | 118986 | Hoffenheim – Stuttgart | 4:5 | 9 |
| 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 7:6 | 13 |
| 16.05.2026 | 120510 | Eintracht Frankfurt – Stuttgart | 6:6 | 12 |
| 28.08.2026 | 132783 | Bayern Munich – Stuttgart | 9:3 | 12 |

**FC Koln** – 10 gültige Spiele, Summe 98, Teamwert 9,80

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106583 | Hamburger SV – FC Koln | 1:8 | 9 |
| 21.03.2026 | 114289 | FC Koln – B. Monchengladbach | 5:3 | 8 |
| 05.04.2026 | 117540 | Eintracht Frankfurt – FC Koln | 8:0 | 8 |
| 12.04.2026 | 118013 | FC Koln – Werder Bremen | 8:5 | 13 |
| 17.04.2026 | 118161 | St. Pauli – FC Koln | 8:5 | 13 |
| 25.04.2026 | 118646 | FC Koln – Bayer Leverkusen | 2:5 | 7 |
| 02.05.2026 | 118987 | Union Berlin – FC Koln | 2:5 | 7 |
| 10.05.2026 | 119365 | FC Koln – Heidenheim | 6:4 | 10 |
| 16.05.2026 | 120509 | Bayern Munich – FC Koln | 5:5 | 10 |
| 29.08.2026 | 132873 | FC Koln – Hoffenheim | 6:7 | 13 |

### T2 – Bayer Leverkusen – Union Berlin (Bundesliga, 2026/2027, Spieltag 2, Analysedatum 2026-09-04)

**Bayer Leverkusen** – 10 gültige Spiele, Summe 99, Teamwert 9,90

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106579 | Bayer Leverkusen – Bayern Munich | 4:1 | 5 |
| 21.03.2026 | 114290 | Heidenheim – Bayer Leverkusen | 2:5 | 7 |
| 04.04.2026 | 117436 | Bayer Leverkusen – Wolfsburg | 12:2 | 14 |
| 11.04.2026 | 117899 | Dortmund – Bayer Leverkusen | 5:5 | 10 |
| 18.04.2026 | 118240 | Bayer Leverkusen – Augsburg | 11:4 | 15 |
| 25.04.2026 | 118646 | FC Koln – Bayer Leverkusen | 2:5 | 7 |
| 02.05.2026 | 118989 | Bayer Leverkusen – RB Leipzig | 7:3 | 10 |
| 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 7:6 | 13 |
| 16.05.2026 | 120508 | Bayer Leverkusen – Hamburger SV | 8:3 | 11 |
| 29.08.2026 | 132872 | Elversberg – Bayer Leverkusen | 4:3 | 7 |

**Union Berlin** – 10 gültige Spiele, Summe 109, Teamwert 10,90

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107987 | Freiburg – Union Berlin | 6:2 | 8 |
| 21.03.2026 | 114288 | Bayern Munich – Union Berlin | 12:1 | 13 |
| 05.04.2026 | 117539 | Union Berlin – St. Pauli | 7:2 | 9 |
| 11.04.2026 | 117900 | Heidenheim – Union Berlin | 3:5 | 8 |
| 18.04.2026 | 118242 | Union Berlin – Wolfsburg | 11:4 | 15 |
| 24.04.2026 | 118560 | RB Leipzig – Union Berlin | 10:4 | 14 |
| 02.05.2026 | 118987 | Union Berlin – FC Koln | 2:5 | 7 |
| 10.05.2026 | 119366 | Mainz – Union Berlin | 7:8 | 15 |
| 16.05.2026 | 120514 | Union Berlin – Augsburg | 4:9 | 13 |
| 29.08.2026 | 132876 | Union Berlin – Eintracht Frankfurt | 5:2 | 7 |

### T3 – Juventus – Parma (Serie A, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Juventus** – 10 gültige Spiele, Summe 107, Teamwert 10,70

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 21.03.2026 | 114299 | Juventus – Sassuolo | 9:4 | 13 |
| 06.04.2026 | 117656 | Juventus – Genoa | 5:5 | 10 |
| 11.04.2026 | 117911 | Atalanta – Juventus | 13:2 | 15 |
| 19.04.2026 | 118349 | Juventus – Bologna | 6:1 | 7 |
| 26.04.2026 | 118761 | AC Milan – Juventus | 1:3 | 4 |
| 03.05.2026 | 119096 | Juventus – Verona | 14:1 | 15 |
| 09.05.2026 | 119281 | Lecce – Juventus | 1:7 | 8 |
| 17.05.2026 | 120620 | Juventus – Fiorentina | 6:2 | 8 |
| 24.05.2026 | 120857 | Torino – Juventus | 6:6 | 12 |
| 23.08.2026 | 130758 | Frosinone – Juventus | 3:12 | 15 |

**Parma** – 10 gültige Spiele, Summe 93, Teamwert 9,30

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 21.03.2026 | 114297 | Parma – Cremonese | 3:1 | 4 |
| 04.04.2026 | 117451 | Lazio – Parma | 7:2 | 9 |
| 12.04.2026 | 118020 | Parma – Napoli | 3:7 | 10 |
| 18.04.2026 | 118254 | Udinese – Parma | 10:5 | 15 |
| 25.04.2026 | 118655 | Parma – Pisa | 7:4 | 11 |
| 03.05.2026 | 119097 | Inter – Parma | 8:3 | 11 |
| 10.05.2026 | 119377 | Parma – AS Roma | 3:6 | 9 |
| 17.05.2026 | 120618 | Como – Parma | 15:2 | 17 |
| 24.05.2026 | 120852 | Parma – Sassuolo | 1:1 | 2 |
| 22.08.2026 | 130663 | Parma – Cagliari | 3:2 | 5 |

### T4 – Atl. Madrid – Villarreal (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Atl. Madrid** – 10 gültige Spiele, Summe 111, Teamwert 11,10

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 22.03.2026 | 114444 | Real Madrid – Atl. Madrid | 4:1 | 5 |
| 04.04.2026 | 117485 | Atl. Madrid – Barcelona | 1:9 | 10 |
| 11.04.2026 | 117953 | Sevilla – Atl. Madrid | 6:6 | 12 |
| 22.04.2026 | 118500 | Elche – Atl. Madrid | 13:3 | 16 |
| 25.04.2026 | 118693 | Atl. Madrid – Ath Bilbao | 3:4 | 7 |
| 02.05.2026 | 119028 | Valencia – Atl. Madrid | 1:7 | 8 |
| 09.05.2026 | 119297 | Atl. Madrid – Celta Vigo | 10:0 | 10 |
| 12.05.2026 | 120229 | Osasuna – Atl. Madrid | 8:4 | 12 |
| 17.05.2026 | 120662 | Atl. Madrid – Girona | 9:8 | 17 |
| 24.05.2026 | 120872 | Villarreal – Atl. Madrid | 5:9 | 14 |

**Villarreal** – 10 gültige Spiele, Summe 117, Teamwert 11,70

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 06.04.2026 | 117677 | Girona – Villarreal | 7:4 | 11 |
| 12.04.2026 | 118055 | Ath Bilbao – Villarreal | 15:3 | 18 |
| 23.04.2026 | 118530 | Oviedo – Villarreal | 7:0 | 7 |
| 26.04.2026 | 118794 | Villarreal – Celta Vigo | 7:5 | 12 |
| 02.05.2026 | 119027 | Villarreal – Levante | 7:3 | 10 |
| 10.05.2026 | 119413 | Mallorca – Villarreal | 5:4 | 9 |
| 13.05.2026 | 120439 | Villarreal – Sevilla | 6:4 | 10 |
| 17.05.2026 | 120667 | Rayo Vallecano – Villarreal | 1:9 | 10 |
| 24.05.2026 | 120872 | Villarreal – Atl. Madrid | 5:9 | 14 |
| 16.08.2026 | 129483 | Racing Santander – Villarreal | 6:10 | 16 |

### T5 – Crystal Palace – Manchester City (Premier League, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Crystal Palace** – 10 gültige Spiele, Summe 100, Teamwert 10,00

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107978 | Crystal Palace – Leeds | 8:3 | 11 |
| 12.04.2026 | 118005 | Crystal Palace – Newcastle | 2:4 | 6 |
| 20.04.2026 | 118408 | Crystal Palace – West Ham | 4:6 | 10 |
| 25.04.2026 | 118603 | Liverpool – Crystal Palace | 5:8 | 13 |
| 03.05.2026 | 119074 | Bournemouth – Crystal Palace | 7:1 | 8 |
| 10.05.2026 | 119351 | Crystal Palace – Everton | 5:10 | 15 |
| 13.05.2026 | 120425 | Manchester City – Crystal Palace | 9:4 | 13 |
| 17.05.2026 | 120589 | Brentford – Crystal Palace | 9:4 | 13 |
| 24.05.2026 | 120843 | Crystal Palace – Arsenal | 3:4 | 7 |
| 22.08.2026 | 130611 | Everton – Crystal Palace | 4:0 | 4 |

**Manchester City** – 10 gültige Spiele, Summe 135, Teamwert 13,50

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106539 | West Ham – Manchester City | 1:15 | 16 |
| 12.04.2026 | 118008 | Chelsea – Manchester City | 4:12 | 16 |
| 19.04.2026 | 118329 | Manchester City – Arsenal | 8:5 | 13 |
| 22.04.2026 | 118479 | Burnley – Manchester City | 3:11 | 14 |
| 04.05.2026 | 119163 | Everton – Manchester City | 5:9 | 14 |
| 09.05.2026 | 119254 | Manchester City – Brentford | 10:2 | 12 |
| 13.05.2026 | 120425 | Manchester City – Crystal Palace | 9:4 | 13 |
| 19.05.2026 | 120707 | Bournemouth – Manchester City | 7:6 | 13 |
| 24.05.2026 | 120846 | Manchester City – Aston Villa | 9:4 | 13 |
| 23.08.2026 | 130749 | Manchester City – Bournemouth | 8:3 | 11 |

### T6 – Fiorentina – Frosinone (Serie A, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Fiorentina** – 10 gültige Spiele, Summe 82, Teamwert 8,20

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 22.03.2026 | 114403 | Fiorentina – Inter | 3:5 | 8 |
| 04.04.2026 | 117450 | Verona – Fiorentina | 9:1 | 10 |
| 13.04.2026 | 118084 | Fiorentina – Lazio | 5:6 | 11 |
| 20.04.2026 | 118410 | Lecce – Fiorentina | 5:2 | 7 |
| 26.04.2026 | 118758 | Fiorentina – Sassuolo | 7:4 | 11 |
| 04.05.2026 | 119165 | AS Roma – Fiorentina | 4:5 | 9 |
| 10.05.2026 | 119376 | Fiorentina – Genoa | 4:3 | 7 |
| 17.05.2026 | 120620 | Juventus – Fiorentina | 6:2 | 8 |
| 22.05.2026 | 120772 | Fiorentina – Atalanta | 3:3 | 6 |
| 24.08.2026 | 130861 | AS Roma – Fiorentina | 2:3 | 5 |

**Frosinone** – 1 gültige Spiele, Summe 15, Teamwert 15,00

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 23.08.2026 | 130758 | Frosinone – Juventus | 3:12 | 15 |

### T7 – Malaga – Dep. A Coruna (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Malaga** – 0 gültige Spiele, Summe –, Teamwert –

Keine Ligaspiele im Zeitfenster.

**Dep. A Coruna** – 1 gültige Spiele, Summe 8, Teamwert 8,00

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 17.08.2026 | 130470 | Dep. A Coruna – Elche | 2:6 | 8 |

### T8 – Union Berlin – Mainz (Bundesliga, 2024/2025, Spieltag 18, Analysedatum 2025-01-19)

**Union Berlin** – 9 gültige Spiele, Summe 79, Teamwert 8,78

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 27.10.2024 | 14469 | Union Berlin – Eintracht Frankfurt | 4:5 | 9 |
| 02.11.2024 | 14462 | Bayern Munich – Union Berlin | 7:4 | 11 |
| 08.11.2024 | 14458 | Union Berlin – Freiburg | 4:1 | 5 |
| 23.11.2024 | 14448 | Wolfsburg – Union Berlin | 8:5 | 13 |
| 30.11.2024 | 14438 | Union Berlin – Bayer Leverkusen | 1:3 | 4 |
| 06.12.2024 | 14431 | Stuttgart – Union Berlin | 1:6 | 7 |
| 14.12.2024 | 14421 | Union Berlin – Bochum | –:– | – (fehlt, ausgelassen) |
| 21.12.2024 | 14412 | Werder Bremen – Union Berlin | 4:9 | 13 |
| 11.01.2025 | 14400 | Heidenheim – Union Berlin | 5:4 | 9 |
| 15.01.2025 | 14389 | Union Berlin – Augsburg | 4:4 | 8 |

**Mainz** – 10 gültige Spiele, Summe 100, Teamwert 10,00

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 25.10.2024 | 14476 | Mainz – B. Monchengladbach | 2:4 | 6 |
| 03.11.2024 | 14460 | Freiburg – Mainz | 8:4 | 12 |
| 09.11.2024 | 14455 | Mainz – Dortmund | 8:0 | 8 |
| 24.11.2024 | 14442 | Holstein Kiel – Mainz | 2:6 | 8 |
| 01.12.2024 | 14433 | Mainz – Hoffenheim | 8:3 | 11 |
| 08.12.2024 | 14424 | Wolfsburg – Mainz | 3:5 | 8 |
| 14.12.2024 | 14420 | Mainz – Bayern Munich | 3:2 | 5 |
| 21.12.2024 | 14408 | Eintracht Frankfurt – Mainz | 17:2 | 19 |
| 11.01.2025 | 14402 | Mainz – Bochum | 5:6 | 11 |
| 14.01.2025 | 14392 | Bayer Leverkusen – Mainz | 8:4 | 12 |

### T9 – Getafe – Racing Santander (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Getafe** – 10 gültige Spiele, Summe 74, Teamwert 7,40

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 05.04.2026 | 117581 | Getafe – Ath Bilbao | 4:3 | 7 |
| 13.04.2026 | 118088 | Levante – Getafe | 8:2 | 10 |
| 22.04.2026 | 118501 | Real Sociedad – Getafe | 6:3 | 9 |
| 25.04.2026 | 118691 | Getafe – Barcelona | 6:3 | 9 |
| 03.05.2026 | 119130 | Getafe – Rayo Vallecano | 4:1 | 5 |
| 10.05.2026 | 119415 | Oviedo – Getafe | 1:9 | 10 |
| 13.05.2026 | 120441 | Getafe – Mallorca | 3:3 | 6 |
| 17.05.2026 | 120663 | Elche – Getafe | 4:0 | 4 |
| 23.05.2026 | 120811 | Getafe – Osasuna | 2:4 | 6 |
| 15.08.2026 | 128152 | Alaves – Getafe | 5:3 | 8 |

**Racing Santander** – 1 gültige Spiele, Summe 16, Teamwert 16,00

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 16.08.2026 | 129483 | Racing Santander – Villarreal | 6:10 | 16 |

### T10 – Bayern Munich – Stuttgart (Bundesliga, 2026/2027, Spieltag 1, Analysedatum 2026-08-28)

**Bayern Munich** – 10 gültige Spiele, Summe 105, Teamwert 10,50

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 06.03.2026 | 99487 | Bayern Munich – B. Monchengladbach | 7:1 | 8 |
| 14.03.2026 | 106579 | Bayer Leverkusen – Bayern Munich | 4:1 | 5 |
| 21.03.2026 | 114288 | Bayern Munich – Union Berlin | 12:1 | 13 |
| 04.04.2026 | 117437 | Freiburg – Bayern Munich | 5:8 | 13 |
| 11.04.2026 | 117903 | St. Pauli – Bayern Munich | 3:4 | 7 |
| 19.04.2026 | 118339 | Bayern Munich – Stuttgart | 11:3 | 14 |
| 25.04.2026 | 118648 | Mainz – Bayern Munich | 4:4 | 8 |
| 02.05.2026 | 118984 | Bayern Munich – Heidenheim | 13:5 | 18 |
| 09.05.2026 | 119271 | Wolfsburg – Bayern Munich | 6:3 | 9 |
| 16.05.2026 | 120509 | Bayern Munich – FC Koln | 5:5 | 10 |

**Stuttgart** – 10 gültige Spiele, Summe 110, Teamwert 11,00

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 07.03.2026 | 99520 | Mainz – Stuttgart | 5:6 | 11 |
| 15.03.2026 | 107988 | Stuttgart – RB Leipzig | 5:6 | 11 |
| 22.03.2026 | 114388 | Augsburg – Stuttgart | 2:5 | 7 |
| 04.04.2026 | 117441 | Stuttgart – Dortmund | 5:2 | 7 |
| 12.04.2026 | 118014 | Stuttgart – Hamburger SV | 8:2 | 10 |
| 19.04.2026 | 118339 | Bayern Munich – Stuttgart | 11:3 | 14 |
| 26.04.2026 | 118750 | Stuttgart – Werder Bremen | 14:2 | 16 |
| 02.05.2026 | 118986 | Hoffenheim – Stuttgart | 4:5 | 9 |
| 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 7:6 | 13 |
| 16.05.2026 | 120510 | Eintracht Frankfurt – Stuttgart | 6:6 | 12 |

### T11 – Elversberg – Bayer Leverkusen (Bundesliga, 2026/2027, Spieltag 1, Analysedatum 2026-08-28)

**Elversberg** – 0 gültige Spiele, Summe –, Teamwert –

Keine Ligaspiele im Zeitfenster.

**Bayer Leverkusen** – 10 gültige Spiele, Summe 99, Teamwert 9,90

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 07.03.2026 | 99518 | Freiburg – Bayer Leverkusen | 5:2 | 7 |
| 14.03.2026 | 106579 | Bayer Leverkusen – Bayern Munich | 4:1 | 5 |
| 21.03.2026 | 114290 | Heidenheim – Bayer Leverkusen | 2:5 | 7 |
| 04.04.2026 | 117436 | Bayer Leverkusen – Wolfsburg | 12:2 | 14 |
| 11.04.2026 | 117899 | Dortmund – Bayer Leverkusen | 5:5 | 10 |
| 18.04.2026 | 118240 | Bayer Leverkusen – Augsburg | 11:4 | 15 |
| 25.04.2026 | 118646 | FC Koln – Bayer Leverkusen | 2:5 | 7 |
| 02.05.2026 | 118989 | Bayer Leverkusen – RB Leipzig | 7:3 | 10 |
| 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 7:6 | 13 |
| 16.05.2026 | 120508 | Bayer Leverkusen – Hamburger SV | 8:3 | 11 |

### T12 – B. Monchengladbach – Elversberg (Bundesliga, 2026/2027, Spieltag 2, Analysedatum 2026-09-04)

**B. Monchengladbach** – 10 gültige Spiele, Summe 81, Teamwert 8,10

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 13.03.2026 | 105942 | B. Monchengladbach – St. Pauli | 2:2 | 4 |
| 21.03.2026 | 114289 | FC Koln – B. Monchengladbach | 5:3 | 8 |
| 04.04.2026 | 117435 | B. Monchengladbach – Heidenheim | 2:3 | 5 |
| 11.04.2026 | 117901 | RB Leipzig – B. Monchengladbach | 11:4 | 15 |
| 19.04.2026 | 118340 | B. Monchengladbach – Mainz | 0:6 | 6 |
| 25.04.2026 | 118649 | Wolfsburg – B. Monchengladbach | 8:5 | 13 |
| 03.05.2026 | 119083 | B. Monchengladbach – Dortmund | 1:1 | 2 |
| 09.05.2026 | 119267 | Augsburg – B. Monchengladbach | 2:2 | 4 |
| 16.05.2026 | 120507 | B. Monchengladbach – Hoffenheim | 2:9 | 11 |
| 29.08.2026 | 132875 | RB Leipzig – B. Monchengladbach | 7:6 | 13 |

**Elversberg** – 1 gültige Spiele, Summe 7, Teamwert 7,00

| Datum | id | Begegnung | Ecken W:X | zählt |
|---|---|---|---|---|
| 29.08.2026 | 132872 | Elversberg – Bayer Leverkusen | 4:3 | 7 |

### Ligareferenzen je Liga und Spieltag

**Bundesliga, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-09-04):** 2025/2026: 16-34 + 2026/2027: 1-1 → 180 Spiele, Summe 1759, Ligareferenz 9,77

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 16 | 9 | 62 |  |
| 2025/2026 | 17 | 9 | 76 |  |
| 2025/2026 | 18 | 9 | 99 |  |
| 2025/2026 | 19 | 9 | 87 |  |
| 2025/2026 | 20 | 9 | 95 |  |
| 2025/2026 | 21 | 9 | 91 |  |
| 2025/2026 | 22 | 9 | 81 |  |
| 2025/2026 | 23 | 9 | 82 |  |
| 2025/2026 | 24 | 9 | 90 |  |
| 2025/2026 | 25 | 9 | 85 |  |
| 2025/2026 | 26 | 9 | 93 |  |
| 2025/2026 | 27 | 9 | 78 |  |
| 2025/2026 | 28 | 9 | 78 |  |
| 2025/2026 | 29 | 9 | 95 |  |
| 2025/2026 | 30 | 9 | 99 |  |
| 2025/2026 | 31 | 9 | 104 |  |
| 2025/2026 | 32 | 9 | 91 |  |
| 2025/2026 | 33 | 9 | 84 |  |
| 2025/2026 | 34 | 9 | 95 |  |
| 2026/2027 | 1 | 9 | 94 |  |

**Serie A, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-28):** 2025/2026: 20-38 + 2026/2027: 1-1 → 200 Spiele, Summe 1746, Ligareferenz 8,73

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 74 |  |
| 2025/2026 | 21 | 10 | 93 |  |
| 2025/2026 | 22 | 10 | 84 |  |
| 2025/2026 | 23 | 10 | 82 |  |
| 2025/2026 | 24 | 10 | 99 |  |
| 2025/2026 | 25 | 10 | 86 |  |
| 2025/2026 | 26 | 10 | 87 |  |
| 2025/2026 | 27 | 10 | 97 |  |
| 2025/2026 | 28 | 10 | 87 |  |
| 2025/2026 | 29 | 10 | 87 |  |
| 2025/2026 | 30 | 10 | 81 |  |
| 2025/2026 | 31 | 10 | 75 |  |
| 2025/2026 | 32 | 10 | 91 |  |
| 2025/2026 | 33 | 10 | 104 |  |
| 2025/2026 | 34 | 10 | 92 |  |
| 2025/2026 | 35 | 10 | 82 |  |
| 2025/2026 | 36 | 10 | 89 |  |
| 2025/2026 | 37 | 10 | 96 |  |
| 2025/2026 | 38 | 10 | 72 |  |
| 2026/2027 | 1 | 10 | 88 |  |

**LaLiga, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-20):** 2025/2026: 20-38 + 2026/2027: 1-1 → 196 Spiele, Summe 1882, Ligareferenz 9,60

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 107 |  |
| 2025/2026 | 21 | 10 | 100 |  |
| 2025/2026 | 22 | 10 | 93 |  |
| 2025/2026 | 23 | 10 | 109 |  |
| 2025/2026 | 24 | 10 | 79 |  |
| 2025/2026 | 25 | 10 | 98 |  |
| 2025/2026 | 26 | 10 | 99 |  |
| 2025/2026 | 27 | 10 | 84 |  |
| 2025/2026 | 28 | 10 | 95 |  |
| 2025/2026 | 29 | 10 | 86 |  |
| 2025/2026 | 30 | 10 | 102 |  |
| 2025/2026 | 31 | 10 | 118 |  |
| 2025/2026 | 32 | 10 | 99 |  |
| 2025/2026 | 33 | 10 | 95 |  |
| 2025/2026 | 34 | 10 | 83 |  |
| 2025/2026 | 35 | 10 | 116 |  |
| 2025/2026 | 36 | 10 | 96 |  |
| 2025/2026 | 37 | 10 | 87 |  |
| 2025/2026 | 38 | 10 | 93 |  |
| 2026/2027 | 1 | 6 | 43 |  |

**Premier League, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-28):** 2025/2026: 20-38 + 2026/2027: 1-1 → 200 Spiele, Summe 2022, Ligareferenz 10,11

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 103 |  |
| 2025/2026 | 21 | 10 | 93 |  |
| 2025/2026 | 22 | 10 | 113 |  |
| 2025/2026 | 23 | 10 | 96 |  |
| 2025/2026 | 24 | 10 | 109 |  |
| 2025/2026 | 25 | 10 | 98 |  |
| 2025/2026 | 26 | 10 | 100 |  |
| 2025/2026 | 27 | 10 | 104 |  |
| 2025/2026 | 28 | 10 | 103 |  |
| 2025/2026 | 29 | 10 | 91 |  |
| 2025/2026 | 30 | 10 | 104 |  |
| 2025/2026 | 31 | 10 | 117 |  |
| 2025/2026 | 32 | 10 | 103 |  |
| 2025/2026 | 33 | 10 | 95 |  |
| 2025/2026 | 34 | 10 | 108 |  |
| 2025/2026 | 35 | 10 | 89 |  |
| 2025/2026 | 36 | 10 | 106 |  |
| 2025/2026 | 37 | 10 | 104 |  |
| 2025/2026 | 38 | 10 | 106 |  |
| 2026/2027 | 1 | 10 | 80 |  |

**Bundesliga, analysiert Saison 2024/2025 Spieltag 18 (Stichtag 2025-01-19):** 2023/2024: 32-34 + 2024/2025: 1-17 → 179 Spiele, Summe 1742, Ligareferenz 9,73

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2023/2024 | 32 | 9 | 89 |  |
| 2023/2024 | 33 | 9 | 70 |  |
| 2023/2024 | 34 | 9 | 100 |  |
| 2024/2025 | 1 | 9 | 92 |  |
| 2024/2025 | 2 | 9 | 90 |  |
| 2024/2025 | 3 | 9 | 104 |  |
| 2024/2025 | 4 | 9 | 84 |  |
| 2024/2025 | 5 | 9 | 81 |  |
| 2024/2025 | 6 | 9 | 92 |  |
| 2024/2025 | 7 | 9 | 79 |  |
| 2024/2025 | 8 | 9 | 82 |  |
| 2024/2025 | 9 | 9 | 89 |  |
| 2024/2025 | 10 | 9 | 96 |  |
| 2024/2025 | 11 | 9 | 80 |  |
| 2024/2025 | 12 | 9 | 79 |  |
| 2024/2025 | 13 | 9 | 77 |  |
| 2024/2025 | 14 | 8 | 85 | 1 |
| 2024/2025 | 15 | 9 | 101 |  |
| 2024/2025 | 16 | 9 | 84 |  |
| 2024/2025 | 17 | 9 | 88 |  |

Ausgelassen (Wert fehlt): id 14421 Union Berlin – Bochum

**Bundesliga, analysiert Saison 2026/2027 Spieltag 1 (Stichtag 2026-08-28):** 2025/2026: 15-34 → 180 Spiele, Summe 1755, Ligareferenz 9,75

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 15 | 9 | 90 |  |
| 2025/2026 | 16 | 9 | 62 |  |
| 2025/2026 | 17 | 9 | 76 |  |
| 2025/2026 | 18 | 9 | 99 |  |
| 2025/2026 | 19 | 9 | 87 |  |
| 2025/2026 | 20 | 9 | 95 |  |
| 2025/2026 | 21 | 9 | 91 |  |
| 2025/2026 | 22 | 9 | 81 |  |
| 2025/2026 | 23 | 9 | 82 |  |
| 2025/2026 | 24 | 9 | 90 |  |
| 2025/2026 | 25 | 9 | 85 |  |
| 2025/2026 | 26 | 9 | 93 |  |
| 2025/2026 | 27 | 9 | 78 |  |
| 2025/2026 | 28 | 9 | 78 |  |
| 2025/2026 | 29 | 9 | 95 |  |
| 2025/2026 | 30 | 9 | 99 |  |
| 2025/2026 | 31 | 9 | 104 |  |
| 2025/2026 | 32 | 9 | 91 |  |
| 2025/2026 | 33 | 9 | 84 |  |
| 2025/2026 | 34 | 9 | 95 |  |

