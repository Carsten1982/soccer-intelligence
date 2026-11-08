# Testfall KPI 06 – Tore 1. Halbzeit

**Spezifikation v2.1** · Stand 08.11.2026

**Regelwerk:** `03_KPI_Regelwerk.md`, Abschnitte 1, 1.1, 2, 9.0 und 9.2
**Datenbasis:** `Database-Soccer-Intelligence.xlsx`, SHA-256 `f37e36d301767321575aeadf908c39e288b9a655d02d85d5bcfde0507effdc34`
**Status:** **bestätigt von Carsten am 08.11.2026** (gemeinsamer Rundgang KPI 05–09 mit je einer normalen Partie und einem Aufsteiger). Erzeugt von Claude mit einer unabhängigen Berechnung direkt aus der Excel-Datei. Nachprüfung per Excel: `Testfaelle_KPI05-09_Nachpruefung.xlsx`.

**Änderung 08.11.2026 (Carsten):** Alle Werte mit **zwei Nachkommastellen**, auch die Abweichung. Die Einstufung richtet sich nach der auf zwei Stellen gerundeten Abweichung (Regelwerk 2.3).

Dieser Testfall ist die verbindliche Referenz für die Umsetzung (Etappe H). Die JSON-Blöcke werden zu automatischen Tests.

---

## 1. Regeln, die dieser Testfall prüft

- Teamwert = Ø Tore **beider** Mannschaften in Halbzeit 1 (Q + R) in den Spielen des Teams.
- Hauptwert = (Teamwert Heim + Teamwert Auswärts) / 2 (Mittelwert).
- Ligareferenz = Ø Tore beider Teams in Halbzeit 1 pro Spiel (Q + R).
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
| T15 | Premier League | 2026/2027 | 1 | 2026-08-16 | Newcastle | Liverpool | Rundgang 1. Spieltag 2026/27, normale Partie; zwei Nachkommastellen (1,25 gegen 1,21 statt 1,3 gegen 1,2) |
| T16 | Premier League | 2026/2027 | 1 | 2026-08-16 | Hull | Manchester Utd | Rundgang 1. Spieltag 2026/27, Aufsteiger ohne Spiele → nicht berechenbar |
| T17 | Premier League | 2026/2027 | 2 | 2026-08-28 | Coventry | Hull | Rundgang 2. Spieltag 2026/27, zwei Aufsteiger mit je 1 Spiel → vorläufig; starke positive Anomalie |

Analysedatum = „Datum von“ des Spieltags im Spielplan (T8: Spieldatum, weil das Spiel aus einer abgeschlossenen Saison stammt).

### Ergebnisse auf einen Blick

| Testfall | Teamwert Heim | Teamwert Auswärts | Ligareferenz | Hauptwert | Abweichung | Anomalie | vorläufig |
|---|---|---|---|---|---|---|---|
| T1 | 1,90 (10 Sp.) | 1,70 (10 Sp.) | 1,44 (180 Sp.) | 1,80 | +24,62 % | leicht | nein |
| T2 | 1,90 (10 Sp.) | 1,50 (10 Sp.) | 1,44 (180 Sp.) | 1,70 | +17,69 % | keine | nein |
| T3 | 0,90 (10 Sp.) | 0,40 (10 Sp.) | 1,03 (200 Sp.) | 0,65 | −36,89 % | stark | nein |
| T4 | 1,80 (10 Sp.) | 2,30 (10 Sp.) | 1,23 (196 Sp.) | 2,05 | +66,72 % | stark | nein |
| T5 | 1,30 (10 Sp.) | 1,10 (10 Sp.) | 1,23 (200 Sp.) | 1,20 | −2,04 % | keine | nein |
| T6 | 0,90 (10 Sp.) | 1,00 (1 Sp.) | 1,03 (200 Sp.) | 0,95 | −7,77 % | keine | ja |
| T7 | – (0 Sp.) | 1,00 (1 Sp.) | 1,23 (196 Sp.) | – | – | – | ja |
| T8 | 1,50 (10 Sp.) | 1,40 (10 Sp.) | 1,65 (180 Sp.) | 1,45 | −12,12 % | keine | nein |
| T9 | 0,90 (10 Sp.) | 4,00 (1 Sp.) | 1,23 (196 Sp.) | 2,45 | +99,25 % | stark | ja |
| T15 | 1,20 (10 Sp.) | 1,30 (10 Sp.) | 1,21 (200 Sp.) | 1,25 | +3,73 % | keine | nein |
| T16 | – (0 Sp.) | 1,20 (10 Sp.) | 1,21 (200 Sp.) | – | – | – | ja |
| T17 | 2,00 (1 Sp.) | 2,00 (1 Sp.) | 1,23 (200 Sp.) | 2,00 | +63,27 % | stark | ja |

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
   "summe": 19,
   "teamwert_roh": 1.9,
   "teamwert": "1.90"
  },
  "auswaerts": {
   "team": "FC Koln",
   "spiele": 10,
   "summe": 17,
   "teamwert_roh": 1.7,
   "teamwert": "1.70"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 16-34 + 2026/2027: 1-1",
   "spiele": 180,
   "summe": 260,
   "wert_roh": 1.4444444444,
   "wert": "1.44"
  },
  "hauptwert_roh": 1.8,
  "hauptwert": "1.80",
  "abweichung_roh": 24.6153846154,
  "abweichung": "24.62",
  "anomalie": "leicht",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Viele Tore in Halbzeit 1",
  "text": "In den bisherigen Spielen beider Teams fielen in Halbzeit eins durchschnittlich 1,80 Tore. Das sind 24,62 % mehr als im Liga-Durchschnitt."
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
   "summe": 19,
   "teamwert_roh": 1.9,
   "teamwert": "1.90"
  },
  "auswaerts": {
   "team": "Union Berlin",
   "spiele": 10,
   "summe": 15,
   "teamwert_roh": 1.5,
   "teamwert": "1.50"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 16-34 + 2026/2027: 1-1",
   "spiele": 180,
   "summe": 260,
   "wert_roh": 1.4444444444,
   "wert": "1.44"
  },
  "hauptwert_roh": 1.7,
  "hauptwert": "1.70",
  "abweichung_roh": 17.6923076923,
  "abweichung": "17.69",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "In den bisherigen Spielen fielen in Halbzeit eins im Schnitt 1,70 Tore. Die Abweichung vom Liga-Durchschnitt beträgt +17,69 %."
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
   "summe": 9,
   "teamwert_roh": 0.9,
   "teamwert": "0.90"
  },
  "auswaerts": {
   "team": "Parma",
   "spiele": 10,
   "summe": 4,
   "teamwert_roh": 0.4,
   "teamwert": "0.40"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 206,
   "wert_roh": 1.03,
   "wert": "1.03"
  },
  "hauptwert_roh": 0.65,
  "hauptwert": "0.65",
  "abweichung_roh": -36.8932038835,
  "abweichung": "-36.89",
  "anomalie": "stark",
  "richtung": "negativ",
  "vorlaeufig": false,
  "ueberschrift": "Wenige Tore in Halbzeit 1",
  "text": "In den bisherigen Spielen beider Teams fielen in Halbzeit eins durchschnittlich 0,65 Tore. Das sind 36,89 % weniger als im Liga-Durchschnitt."
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
   "summe": 18,
   "teamwert_roh": 1.8,
   "teamwert": "1.80"
  },
  "auswaerts": {
   "team": "Villarreal",
   "spiele": 10,
   "summe": 23,
   "teamwert_roh": 2.3,
   "teamwert": "2.30"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 196,
   "summe": 241,
   "wert_roh": 1.2295918367,
   "wert": "1.23"
  },
  "hauptwert_roh": 2.05,
  "hauptwert": "2.05",
  "abweichung_roh": 66.7219917012,
  "abweichung": "66.72",
  "anomalie": "stark",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Viele Tore in Halbzeit 1",
  "text": "In den bisherigen Spielen beider Teams fielen in Halbzeit eins durchschnittlich 2,05 Tore. Das sind 66,72 % mehr als im Liga-Durchschnitt."
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
   "summe": 11,
   "teamwert_roh": 1.1,
   "teamwert": "1.10"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 245,
   "wert_roh": 1.225,
   "wert": "1.23"
  },
  "hauptwert_roh": 1.2,
  "hauptwert": "1.20",
  "abweichung_roh": -2.0408163265,
  "abweichung": "-2.04",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "In den bisherigen Spielen fielen in Halbzeit eins im Schnitt 1,20 Tore. Die Abweichung vom Liga-Durchschnitt beträgt −2,04 %."
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
   "summe": 1,
   "teamwert_roh": 1.0,
   "teamwert": "1.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 206,
   "wert_roh": 1.03,
   "wert": "1.03"
  },
  "hauptwert_roh": 0.95,
  "hauptwert": "0.95",
  "abweichung_roh": -7.7669902913,
  "abweichung": "-7.77",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": true,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "In den bisherigen Spielen fielen in Halbzeit eins im Schnitt 0,95 Tore. Die Abweichung vom Liga-Durchschnitt beträgt −7,77 %."
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
   "summe": 241,
   "wert_roh": 1.2295918367,
   "wert": "1.23"
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
   "summe": 15,
   "teamwert_roh": 1.5,
   "teamwert": "1.50"
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
   "summe": 297,
   "wert_roh": 1.65,
   "wert": "1.65"
  },
  "hauptwert_roh": 1.45,
  "hauptwert": "1.45",
  "abweichung_roh": -12.1212121212,
  "abweichung": "-12.12",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "In den bisherigen Spielen fielen in Halbzeit eins im Schnitt 1,45 Tore. Die Abweichung vom Liga-Durchschnitt beträgt −12,12 %."
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
   "summe": 9,
   "teamwert_roh": 0.9,
   "teamwert": "0.90"
  },
  "auswaerts": {
   "team": "Racing Santander",
   "spiele": 1,
   "summe": 4,
   "teamwert_roh": 4.0,
   "teamwert": "4.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 196,
   "summe": 241,
   "wert_roh": 1.2295918367,
   "wert": "1.23"
  },
  "hauptwert_roh": 2.45,
  "hauptwert": "2.45",
  "abweichung_roh": 99.2531120332,
  "abweichung": "99.25",
  "anomalie": "stark",
  "richtung": "positiv",
  "vorlaeufig": true,
  "ueberschrift": "Viele Tore in Halbzeit 1",
  "text": "In den bisherigen Spielen beider Teams fielen in Halbzeit eins durchschnittlich 2,45 Tore. Das sind 99,25 % mehr als im Liga-Durchschnitt."
 },
 {
  "testfall": "T15",
  "liga": "Premier League",
  "saison": "2026/2027",
  "spieltag": 1,
  "analysedatum": "2026-08-16",
  "heim": {
   "team": "Newcastle",
   "spiele": 10,
   "summe": 12,
   "teamwert_roh": 1.2,
   "teamwert": "1.20"
  },
  "auswaerts": {
   "team": "Liverpool",
   "spiele": 10,
   "summe": 13,
   "teamwert_roh": 1.3,
   "teamwert": "1.30"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 19-38",
   "spiele": 200,
   "summe": 241,
   "wert_roh": 1.205,
   "wert": "1.21"
  },
  "hauptwert_roh": 1.25,
  "hauptwert": "1.25",
  "abweichung_roh": 3.734439834,
  "abweichung": "3.73",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "In den bisherigen Spielen fielen in Halbzeit eins im Schnitt 1,25 Tore. Die Abweichung vom Liga-Durchschnitt beträgt +3,73 %."
 },
 {
  "testfall": "T16",
  "liga": "Premier League",
  "saison": "2026/2027",
  "spieltag": 1,
  "analysedatum": "2026-08-16",
  "heim": {
   "team": "Hull",
   "spiele": 0,
   "summe": null,
   "teamwert_roh": null,
   "teamwert": null
  },
  "auswaerts": {
   "team": "Manchester Utd",
   "spiele": 10,
   "summe": 12,
   "teamwert_roh": 1.2,
   "teamwert": "1.20"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 19-38",
   "spiele": 200,
   "summe": 241,
   "wert_roh": 1.205,
   "wert": "1.21"
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
  "testfall": "T17",
  "liga": "Premier League",
  "saison": "2026/2027",
  "spieltag": 2,
  "analysedatum": "2026-08-28",
  "heim": {
   "team": "Coventry",
   "spiele": 1,
   "summe": 2,
   "teamwert_roh": 2.0,
   "teamwert": "2.00"
  },
  "auswaerts": {
   "team": "Hull",
   "spiele": 1,
   "summe": 2,
   "teamwert_roh": 2.0,
   "teamwert": "2.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 245,
   "wert_roh": 1.225,
   "wert": "1.23"
  },
  "hauptwert_roh": 2.0,
  "hauptwert": "2.00",
  "abweichung_roh": 63.2653061224,
  "abweichung": "63.27",
  "anomalie": "stark",
  "richtung": "positiv",
  "vorlaeufig": true,
  "ueberschrift": "Viele Tore in Halbzeit 1",
  "text": "In den bisherigen Spielen beider Teams fielen in Halbzeit eins durchschnittlich 2,00 Tore. Das sind 63,27 % mehr als im Liga-Durchschnitt."
 }
]
```

Hinweise: gerundete Werte als Text mit Punkt (im Dashboard mit Komma); `summe` = Summe der Spielwerte (bei KPI 08 Anzahl BTTS-Spiele); `_roh`-Werte mit Toleranz 1e-9 vergleichen.

## 4. Eingabedaten zum Nachvollziehen

### T1 – Stuttgart – FC Koln (Bundesliga, 2026/2027, Spieltag 2, Analysedatum 2026-09-04)

**Stuttgart** – 10 gültige Spiele, Summe 19, Teamwert 1,90

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107988 | Stuttgart – RB Leipzig | 0:0 | 0 |
| 22.03.2026 | 114388 | Augsburg – Stuttgart | 0:3 | 3 |
| 04.04.2026 | 117441 | Stuttgart – Dortmund | 0:0 | 0 |
| 12.04.2026 | 118014 | Stuttgart – Hamburger SV | 2:0 | 2 |
| 19.04.2026 | 118339 | Bayern Munich – Stuttgart | 3:1 | 4 |
| 26.04.2026 | 118750 | Stuttgart – Werder Bremen | 0:1 | 1 |
| 02.05.2026 | 118986 | Hoffenheim – Stuttgart | 2:1 | 3 |
| 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 2:1 | 3 |
| 16.05.2026 | 120510 | Eintracht Frankfurt – Stuttgart | 0:2 | 2 |
| 28.08.2026 | 132783 | Bayern Munich – Stuttgart | 1:0 | 1 |

**FC Koln** – 10 gültige Spiele, Summe 17, Teamwert 1,70

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106583 | Hamburger SV – FC Koln | 1:1 | 2 |
| 21.03.2026 | 114289 | FC Koln – B. Monchengladbach | 2:2 | 4 |
| 05.04.2026 | 117540 | Eintracht Frankfurt – FC Koln | 0:0 | 0 |
| 12.04.2026 | 118013 | FC Koln – Werder Bremen | 1:0 | 1 |
| 17.04.2026 | 118161 | St. Pauli – FC Koln | 0:0 | 0 |
| 25.04.2026 | 118646 | FC Koln – Bayer Leverkusen | 0:1 | 1 |
| 02.05.2026 | 118987 | Union Berlin – FC Koln | 0:1 | 1 |
| 10.05.2026 | 119365 | FC Koln – Heidenheim | 1:2 | 3 |
| 16.05.2026 | 120509 | Bayern Munich – FC Koln | 3:1 | 4 |
| 29.08.2026 | 132873 | FC Koln – Hoffenheim | 0:1 | 1 |

### T2 – Bayer Leverkusen – Union Berlin (Bundesliga, 2026/2027, Spieltag 2, Analysedatum 2026-09-04)

**Bayer Leverkusen** – 10 gültige Spiele, Summe 19, Teamwert 1,90

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106579 | Bayer Leverkusen – Bayern Munich | 1:0 | 1 |
| 21.03.2026 | 114290 | Heidenheim – Bayer Leverkusen | 0:2 | 2 |
| 04.04.2026 | 117436 | Bayer Leverkusen – Wolfsburg | 2:3 | 5 |
| 11.04.2026 | 117899 | Dortmund – Bayer Leverkusen | 0:1 | 1 |
| 18.04.2026 | 118240 | Bayer Leverkusen – Augsburg | 1:1 | 2 |
| 25.04.2026 | 118646 | FC Koln – Bayer Leverkusen | 0:1 | 1 |
| 02.05.2026 | 118989 | Bayer Leverkusen – RB Leipzig | 2:0 | 2 |
| 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 2:1 | 3 |
| 16.05.2026 | 120508 | Bayer Leverkusen – Hamburger SV | 0:0 | 0 |
| 29.08.2026 | 132872 | Elversberg – Bayer Leverkusen | 2:0 | 2 |

**Union Berlin** – 10 gültige Spiele, Summe 15, Teamwert 1,50

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107987 | Freiburg – Union Berlin | 0:0 | 0 |
| 21.03.2026 | 114288 | Bayern Munich – Union Berlin | 2:0 | 2 |
| 05.04.2026 | 117539 | Union Berlin – St. Pauli | 0:1 | 1 |
| 11.04.2026 | 117900 | Heidenheim – Union Berlin | 2:0 | 2 |
| 18.04.2026 | 118242 | Union Berlin – Wolfsburg | 0:1 | 1 |
| 24.04.2026 | 118560 | RB Leipzig – Union Berlin | 2:0 | 2 |
| 02.05.2026 | 118987 | Union Berlin – FC Koln | 0:1 | 1 |
| 10.05.2026 | 119366 | Mainz – Union Berlin | 0:1 | 1 |
| 16.05.2026 | 120514 | Union Berlin – Augsburg | 2:0 | 2 |
| 29.08.2026 | 132876 | Union Berlin – Eintracht Frankfurt | 1:2 | 3 |

### T3 – Juventus – Parma (Serie A, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Juventus** – 10 gültige Spiele, Summe 9, Teamwert 0,90

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 21.03.2026 | 114299 | Juventus – Sassuolo | 1:0 | 1 |
| 06.04.2026 | 117656 | Juventus – Genoa | 2:0 | 2 |
| 11.04.2026 | 117911 | Atalanta – Juventus | 0:0 | 0 |
| 19.04.2026 | 118349 | Juventus – Bologna | 1:0 | 1 |
| 26.04.2026 | 118761 | AC Milan – Juventus | 0:0 | 0 |
| 03.05.2026 | 119096 | Juventus – Verona | 0:1 | 1 |
| 09.05.2026 | 119281 | Lecce – Juventus | 0:1 | 1 |
| 17.05.2026 | 120620 | Juventus – Fiorentina | 0:1 | 1 |
| 24.05.2026 | 120857 | Torino – Juventus | 0:1 | 1 |
| 23.08.2026 | 130758 | Frosinone – Juventus | 0:1 | 1 |

**Parma** – 10 gültige Spiele, Summe 4, Teamwert 0,40

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 21.03.2026 | 114297 | Parma – Cremonese | 0:0 | 0 |
| 04.04.2026 | 117451 | Lazio – Parma | 0:1 | 1 |
| 12.04.2026 | 118020 | Parma – Napoli | 1:0 | 1 |
| 18.04.2026 | 118254 | Udinese – Parma | 0:0 | 0 |
| 25.04.2026 | 118655 | Parma – Pisa | 0:0 | 0 |
| 03.05.2026 | 119097 | Inter – Parma | 1:0 | 1 |
| 10.05.2026 | 119377 | Parma – AS Roma | 0:1 | 1 |
| 17.05.2026 | 120618 | Como – Parma | 0:0 | 0 |
| 24.05.2026 | 120852 | Parma – Sassuolo | 0:0 | 0 |
| 22.08.2026 | 130663 | Parma – Cagliari | 0:0 | 0 |

### T4 – Atl. Madrid – Villarreal (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Atl. Madrid** – 10 gültige Spiele, Summe 18, Teamwert 1,80

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 22.03.2026 | 114444 | Real Madrid – Atl. Madrid | 0:1 | 1 |
| 04.04.2026 | 117485 | Atl. Madrid – Barcelona | 1:1 | 2 |
| 11.04.2026 | 117953 | Sevilla – Atl. Madrid | 2:1 | 3 |
| 22.04.2026 | 118500 | Elche – Atl. Madrid | 2:2 | 4 |
| 25.04.2026 | 118693 | Atl. Madrid – Ath Bilbao | 0:1 | 1 |
| 02.05.2026 | 119028 | Valencia – Atl. Madrid | 0:0 | 0 |
| 09.05.2026 | 119297 | Atl. Madrid – Celta Vigo | 0:0 | 0 |
| 12.05.2026 | 120229 | Osasuna – Atl. Madrid | 0:1 | 1 |
| 17.05.2026 | 120662 | Atl. Madrid – Girona | 0:1 | 1 |
| 24.05.2026 | 120872 | Villarreal – Atl. Madrid | 4:1 | 5 |

**Villarreal** – 10 gültige Spiele, Summe 23, Teamwert 2,30

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 06.04.2026 | 117677 | Girona – Villarreal | 1:0 | 1 |
| 12.04.2026 | 118055 | Ath Bilbao – Villarreal | 0:2 | 2 |
| 23.04.2026 | 118530 | Oviedo – Villarreal | 0:1 | 1 |
| 26.04.2026 | 118794 | Villarreal – Celta Vigo | 2:0 | 2 |
| 02.05.2026 | 119027 | Villarreal – Levante | 1:0 | 1 |
| 10.05.2026 | 119413 | Mallorca – Villarreal | 1:1 | 2 |
| 13.05.2026 | 120439 | Villarreal – Sevilla | 2:2 | 4 |
| 17.05.2026 | 120667 | Rayo Vallecano – Villarreal | 1:0 | 1 |
| 24.05.2026 | 120872 | Villarreal – Atl. Madrid | 4:1 | 5 |
| 16.08.2026 | 129483 | Racing Santander – Villarreal | 2:2 | 4 |

### T5 – Crystal Palace – Manchester City (Premier League, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Crystal Palace** – 10 gültige Spiele, Summe 13, Teamwert 1,30

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107978 | Crystal Palace – Leeds | 0:0 | 0 |
| 12.04.2026 | 118005 | Crystal Palace – Newcastle | 0:1 | 1 |
| 20.04.2026 | 118408 | Crystal Palace – West Ham | 0:0 | 0 |
| 25.04.2026 | 118603 | Liverpool – Crystal Palace | 2:0 | 2 |
| 03.05.2026 | 119074 | Bournemouth – Crystal Palace | 2:0 | 2 |
| 10.05.2026 | 119351 | Crystal Palace – Everton | 1:1 | 2 |
| 13.05.2026 | 120425 | Manchester City – Crystal Palace | 2:0 | 2 |
| 17.05.2026 | 120589 | Brentford – Crystal Palace | 1:1 | 2 |
| 24.05.2026 | 120843 | Crystal Palace – Arsenal | 0:1 | 1 |
| 22.08.2026 | 130611 | Everton – Crystal Palace | 1:0 | 1 |

**Manchester City** – 10 gültige Spiele, Summe 11, Teamwert 1,10

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106539 | West Ham – Manchester City | 1:1 | 2 |
| 12.04.2026 | 118008 | Chelsea – Manchester City | 0:0 | 0 |
| 19.04.2026 | 118329 | Manchester City – Arsenal | 1:1 | 2 |
| 22.04.2026 | 118479 | Burnley – Manchester City | 0:1 | 1 |
| 04.05.2026 | 119163 | Everton – Manchester City | 0:1 | 1 |
| 09.05.2026 | 119254 | Manchester City – Brentford | 0:0 | 0 |
| 13.05.2026 | 120425 | Manchester City – Crystal Palace | 2:0 | 2 |
| 19.05.2026 | 120707 | Bournemouth – Manchester City | 1:0 | 1 |
| 24.05.2026 | 120846 | Manchester City – Aston Villa | 1:0 | 1 |
| 23.08.2026 | 130749 | Manchester City – Bournemouth | 0:1 | 1 |

### T6 – Fiorentina – Frosinone (Serie A, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Fiorentina** – 10 gültige Spiele, Summe 9, Teamwert 0,90

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 22.03.2026 | 114403 | Fiorentina – Inter | 0:1 | 1 |
| 04.04.2026 | 117450 | Verona – Fiorentina | 0:0 | 0 |
| 13.04.2026 | 118084 | Fiorentina – Lazio | 1:0 | 1 |
| 20.04.2026 | 118410 | Lecce – Fiorentina | 0:1 | 1 |
| 26.04.2026 | 118758 | Fiorentina – Sassuolo | 0:0 | 0 |
| 04.05.2026 | 119165 | AS Roma – Fiorentina | 3:0 | 3 |
| 10.05.2026 | 119376 | Fiorentina – Genoa | 0:0 | 0 |
| 17.05.2026 | 120620 | Juventus – Fiorentina | 0:1 | 1 |
| 22.05.2026 | 120772 | Fiorentina – Atalanta | 1:0 | 1 |
| 24.08.2026 | 130861 | AS Roma – Fiorentina | 1:0 | 1 |

**Frosinone** – 1 gültige Spiele, Summe 1, Teamwert 1,00

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 23.08.2026 | 130758 | Frosinone – Juventus | 0:1 | 1 |

### T7 – Malaga – Dep. A Coruna (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Malaga** – 0 gültige Spiele, Summe –, Teamwert –

Keine Ligaspiele im Zeitfenster.

**Dep. A Coruna** – 1 gültige Spiele, Summe 1, Teamwert 1,00

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 17.08.2026 | 130470 | Dep. A Coruna – Elche | 1:0 | 1 |

### T8 – Union Berlin – Mainz (Bundesliga, 2024/2025, Spieltag 18, Analysedatum 2025-01-19)

**Union Berlin** – 10 gültige Spiele, Summe 15, Teamwert 1,50

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 27.10.2024 | 14469 | Union Berlin – Eintracht Frankfurt | 0:1 | 1 |
| 02.11.2024 | 14462 | Bayern Munich – Union Berlin | 2:0 | 2 |
| 08.11.2024 | 14458 | Union Berlin – Freiburg | 0:0 | 0 |
| 23.11.2024 | 14448 | Wolfsburg – Union Berlin | 0:0 | 0 |
| 30.11.2024 | 14438 | Union Berlin – Bayer Leverkusen | 1:1 | 2 |
| 06.12.2024 | 14431 | Stuttgart – Union Berlin | 0:1 | 1 |
| 14.12.2024 | 14421 | Union Berlin – Bochum | 1:1 | 2 |
| 21.12.2024 | 14412 | Werder Bremen – Union Berlin | 3:1 | 4 |
| 11.01.2025 | 14400 | Heidenheim – Union Berlin | 1:0 | 1 |
| 15.01.2025 | 14389 | Union Berlin – Augsburg | 0:2 | 2 |

**Mainz** – 10 gültige Spiele, Summe 14, Teamwert 1,40

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 25.10.2024 | 14476 | Mainz – B. Monchengladbach | 0:0 | 0 |
| 03.11.2024 | 14460 | Freiburg – Mainz | 0:0 | 0 |
| 09.11.2024 | 14455 | Mainz – Dortmund | 2:1 | 3 |
| 24.11.2024 | 14442 | Holstein Kiel – Mainz | 0:2 | 2 |
| 01.12.2024 | 14433 | Mainz – Hoffenheim | 2:0 | 2 |
| 08.12.2024 | 14424 | Wolfsburg – Mainz | 1:2 | 3 |
| 14.12.2024 | 14420 | Mainz – Bayern Munich | 1:0 | 1 |
| 21.12.2024 | 14408 | Eintracht Frankfurt – Mainz | 0:2 | 2 |
| 11.01.2025 | 14402 | Mainz – Bochum | 1:0 | 1 |
| 14.01.2025 | 14392 | Bayer Leverkusen – Mainz | 0:0 | 0 |

### T9 – Getafe – Racing Santander (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Getafe** – 10 gültige Spiele, Summe 9, Teamwert 0,90

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 05.04.2026 | 117581 | Getafe – Ath Bilbao | 1:0 | 1 |
| 13.04.2026 | 118088 | Levante – Getafe | 0:0 | 0 |
| 22.04.2026 | 118501 | Real Sociedad – Getafe | 0:1 | 1 |
| 25.04.2026 | 118691 | Getafe – Barcelona | 0:1 | 1 |
| 03.05.2026 | 119130 | Getafe – Rayo Vallecano | 0:1 | 1 |
| 10.05.2026 | 119415 | Oviedo – Getafe | 0:0 | 0 |
| 13.05.2026 | 120441 | Getafe – Mallorca | 2:0 | 2 |
| 17.05.2026 | 120663 | Elche – Getafe | 1:2 | 3 |
| 23.05.2026 | 120811 | Getafe – Osasuna | 0:0 | 0 |
| 15.08.2026 | 128152 | Alaves – Getafe | 0:0 | 0 |

**Racing Santander** – 1 gültige Spiele, Summe 4, Teamwert 4,00

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 16.08.2026 | 129483 | Racing Santander – Villarreal | 2:2 | 4 |

### T15 – Newcastle – Liverpool (Premier League, 2026/2027, Spieltag 1, Analysedatum 2026-08-16)

**Newcastle** – 10 gültige Spiele, Summe 12, Teamwert 1,20

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 04.03.2026 | 99466 | Newcastle – Manchester Utd | 1:1 | 2 |
| 14.03.2026 | 106538 | Chelsea – Newcastle | 0:1 | 1 |
| 22.03.2026 | 114378 | Newcastle – Sunderland | 1:0 | 1 |
| 12.04.2026 | 118005 | Crystal Palace – Newcastle | 0:1 | 1 |
| 18.04.2026 | 118200 | Newcastle – Bournemouth | 0:1 | 1 |
| 25.04.2026 | 118606 | Arsenal – Newcastle | 1:0 | 1 |
| 02.05.2026 | 118932 | Newcastle – Brighton | 2:0 | 2 |
| 10.05.2026 | 119352 | Nottingham – Newcastle | 0:0 | 0 |
| 17.05.2026 | 120593 | Newcastle – West Ham | 2:0 | 2 |
| 24.05.2026 | 120844 | Fulham – Newcastle | 1:0 | 1 |

**Liverpool** – 10 gültige Spiele, Summe 13, Teamwert 1,30

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 03.03.2026 | 99447 | Wolves – Liverpool | 0:0 | 0 |
| 15.03.2026 | 107981 | Liverpool – Tottenham | 1:0 | 1 |
| 21.03.2026 | 114243 | Brighton – Liverpool | 1:1 | 2 |
| 11.04.2026 | 117862 | Liverpool – Fulham | 2:0 | 2 |
| 19.04.2026 | 118327 | Everton – Liverpool | 0:1 | 1 |
| 25.04.2026 | 118603 | Liverpool – Crystal Palace | 2:0 | 2 |
| 03.05.2026 | 119075 | Manchester Utd – Liverpool | 2:0 | 2 |
| 09.05.2026 | 119250 | Liverpool – Chelsea | 1:1 | 2 |
| 15.05.2026 | 120476 | Aston Villa – Liverpool | 1:0 | 1 |
| 24.05.2026 | 120845 | Liverpool – Brentford | 0:0 | 0 |

### T16 – Hull – Manchester Utd (Premier League, 2026/2027, Spieltag 1, Analysedatum 2026-08-16)

**Hull** – 0 gültige Spiele, Summe –, Teamwert –

Keine Ligaspiele im Zeitfenster.

**Manchester Utd** – 10 gültige Spiele, Summe 12, Teamwert 1,20

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 04.03.2026 | 99466 | Newcastle – Manchester Utd | 1:1 | 2 |
| 15.03.2026 | 107979 | Manchester Utd – Aston Villa | 0:0 | 0 |
| 20.03.2026 | 114203 | Bournemouth – Manchester Utd | 0:0 | 0 |
| 13.04.2026 | 118082 | Manchester Utd – Leeds | 0:2 | 2 |
| 18.04.2026 | 118202 | Chelsea – Manchester Utd | 0:1 | 1 |
| 27.04.2026 | 118824 | Manchester Utd – Brentford | 2:0 | 2 |
| 03.05.2026 | 119075 | Manchester Utd – Liverpool | 2:0 | 2 |
| 09.05.2026 | 119253 | Sunderland – Manchester Utd | 0:0 | 0 |
| 17.05.2026 | 120588 | Manchester Utd – Nottingham | 1:0 | 1 |
| 24.05.2026 | 120841 | Brighton – Manchester Utd | 0:2 | 2 |

### T17 – Coventry – Hull (Premier League, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Coventry** – 1 gültige Spiele, Summe 2, Teamwert 2,00

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 21.08.2026 | 130520 | Arsenal – Coventry | 2:0 | 2 |

**Hull** – 1 gültige Spiele, Summe 2, Teamwert 2,00

| Datum | id | Begegnung | HZ1 Q:R | zählt |
|---|---|---|---|---|
| 22.08.2026 | 130610 | Hull – Manchester Utd | 2:0 | 2 |

### Ligareferenzen je Liga und Spieltag

**Bundesliga, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-09-04):** 2025/2026: 16-34 + 2026/2027: 1-1 → 180 Spiele, Summe 260, Ligareferenz 1,44

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 16 | 9 | 17 |  |
| 2025/2026 | 17 | 9 | 14 |  |
| 2025/2026 | 18 | 9 | 7 |  |
| 2025/2026 | 19 | 9 | 9 |  |
| 2025/2026 | 20 | 9 | 13 |  |
| 2025/2026 | 21 | 9 | 12 |  |
| 2025/2026 | 22 | 9 | 13 |  |
| 2025/2026 | 23 | 9 | 14 |  |
| 2025/2026 | 24 | 9 | 7 |  |
| 2025/2026 | 25 | 9 | 16 |  |
| 2025/2026 | 26 | 9 | 6 |  |
| 2025/2026 | 27 | 9 | 20 |  |
| 2025/2026 | 28 | 9 | 12 |  |
| 2025/2026 | 29 | 9 | 13 |  |
| 2025/2026 | 30 | 9 | 14 |  |
| 2025/2026 | 31 | 9 | 15 |  |
| 2025/2026 | 32 | 9 | 13 |  |
| 2025/2026 | 33 | 9 | 16 |  |
| 2025/2026 | 34 | 9 | 16 |  |
| 2026/2027 | 1 | 9 | 13 |  |

**Serie A, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-28):** 2025/2026: 20-38 + 2026/2027: 1-1 → 200 Spiele, Summe 206, Ligareferenz 1,03

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 11 |  |
| 2025/2026 | 21 | 10 | 7 |  |
| 2025/2026 | 22 | 10 | 15 |  |
| 2025/2026 | 23 | 10 | 12 |  |
| 2025/2026 | 24 | 10 | 13 |  |
| 2025/2026 | 25 | 10 | 10 |  |
| 2025/2026 | 26 | 10 | 7 |  |
| 2025/2026 | 27 | 10 | 10 |  |
| 2025/2026 | 28 | 10 | 8 |  |
| 2025/2026 | 29 | 10 | 11 |  |
| 2025/2026 | 30 | 10 | 8 |  |
| 2025/2026 | 31 | 10 | 10 |  |
| 2025/2026 | 32 | 10 | 13 |  |
| 2025/2026 | 33 | 10 | 11 |  |
| 2025/2026 | 34 | 10 | 12 |  |
| 2025/2026 | 35 | 10 | 8 |  |
| 2025/2026 | 36 | 10 | 10 |  |
| 2025/2026 | 37 | 10 | 11 |  |
| 2025/2026 | 38 | 10 | 13 |  |
| 2026/2027 | 1 | 10 | 6 |  |

**LaLiga, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-20):** 2025/2026: 20-38 + 2026/2027: 1-1 → 196 Spiele, Summe 241, Ligareferenz 1,23

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 10 |  |
| 2025/2026 | 21 | 10 | 8 |  |
| 2025/2026 | 22 | 10 | 14 |  |
| 2025/2026 | 23 | 10 | 12 |  |
| 2025/2026 | 24 | 10 | 12 |  |
| 2025/2026 | 25 | 10 | 12 |  |
| 2025/2026 | 26 | 10 | 10 |  |
| 2025/2026 | 27 | 10 | 13 |  |
| 2025/2026 | 28 | 10 | 15 |  |
| 2025/2026 | 29 | 10 | 19 |  |
| 2025/2026 | 30 | 10 | 10 |  |
| 2025/2026 | 31 | 10 | 17 |  |
| 2025/2026 | 32 | 10 | 12 |  |
| 2025/2026 | 33 | 10 | 10 |  |
| 2025/2026 | 34 | 10 | 8 |  |
| 2025/2026 | 35 | 10 | 9 |  |
| 2025/2026 | 36 | 10 | 16 |  |
| 2025/2026 | 37 | 10 | 12 |  |
| 2025/2026 | 38 | 10 | 14 |  |
| 2026/2027 | 1 | 6 | 8 |  |

**Premier League, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-28):** 2025/2026: 20-38 + 2026/2027: 1-1 → 200 Spiele, Summe 245, Ligareferenz 1,23

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 11 |  |
| 2025/2026 | 21 | 10 | 11 |  |
| 2025/2026 | 22 | 10 | 6 |  |
| 2025/2026 | 23 | 10 | 17 |  |
| 2025/2026 | 24 | 10 | 16 |  |
| 2025/2026 | 25 | 10 | 14 |  |
| 2025/2026 | 26 | 10 | 11 |  |
| 2025/2026 | 27 | 10 | 9 |  |
| 2025/2026 | 28 | 10 | 20 |  |
| 2025/2026 | 29 | 10 | 12 |  |
| 2025/2026 | 30 | 10 | 7 |  |
| 2025/2026 | 31 | 10 | 9 |  |
| 2025/2026 | 32 | 10 | 13 |  |
| 2025/2026 | 33 | 10 | 13 |  |
| 2025/2026 | 34 | 10 | 12 |  |
| 2025/2026 | 35 | 10 | 17 |  |
| 2025/2026 | 36 | 10 | 8 |  |
| 2025/2026 | 37 | 10 | 12 |  |
| 2025/2026 | 38 | 10 | 9 |  |
| 2026/2027 | 1 | 10 | 18 |  |

**Bundesliga, analysiert Saison 2024/2025 Spieltag 18 (Stichtag 2025-01-19):** 2023/2024: 32-34 + 2024/2025: 1-17 → 180 Spiele, Summe 297, Ligareferenz 1,65

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2023/2024 | 32 | 9 | 19 |  |
| 2023/2024 | 33 | 9 | 20 |  |
| 2023/2024 | 34 | 9 | 16 |  |
| 2024/2025 | 1 | 9 | 10 |  |
| 2024/2025 | 2 | 9 | 14 |  |
| 2024/2025 | 3 | 9 | 17 |  |
| 2024/2025 | 4 | 9 | 18 |  |
| 2024/2025 | 5 | 9 | 20 |  |
| 2024/2025 | 6 | 9 | 15 |  |
| 2024/2025 | 7 | 9 | 14 |  |
| 2024/2025 | 8 | 9 | 8 |  |
| 2024/2025 | 9 | 9 | 15 |  |
| 2024/2025 | 10 | 9 | 9 |  |
| 2024/2025 | 11 | 9 | 14 |  |
| 2024/2025 | 12 | 9 | 14 |  |
| 2024/2025 | 13 | 9 | 8 |  |
| 2024/2025 | 14 | 9 | 16 |  |
| 2024/2025 | 15 | 9 | 23 |  |
| 2024/2025 | 16 | 9 | 13 |  |
| 2024/2025 | 17 | 9 | 14 |  |

**Premier League, analysiert Saison 2026/2027 Spieltag 1 (Stichtag 2026-08-16):** 2025/2026: 19-38 → 200 Spiele, Summe 241, Ligareferenz 1,21

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 19 | 10 | 14 |  |
| 2025/2026 | 20 | 10 | 11 |  |
| 2025/2026 | 21 | 10 | 11 |  |
| 2025/2026 | 22 | 10 | 6 |  |
| 2025/2026 | 23 | 10 | 17 |  |
| 2025/2026 | 24 | 10 | 16 |  |
| 2025/2026 | 25 | 10 | 14 |  |
| 2025/2026 | 26 | 10 | 11 |  |
| 2025/2026 | 27 | 10 | 9 |  |
| 2025/2026 | 28 | 10 | 20 |  |
| 2025/2026 | 29 | 10 | 12 |  |
| 2025/2026 | 30 | 10 | 7 |  |
| 2025/2026 | 31 | 10 | 9 |  |
| 2025/2026 | 32 | 10 | 13 |  |
| 2025/2026 | 33 | 10 | 13 |  |
| 2025/2026 | 34 | 10 | 12 |  |
| 2025/2026 | 35 | 10 | 17 |  |
| 2025/2026 | 36 | 10 | 8 |  |
| 2025/2026 | 37 | 10 | 12 |  |
| 2025/2026 | 38 | 10 | 9 |  |

