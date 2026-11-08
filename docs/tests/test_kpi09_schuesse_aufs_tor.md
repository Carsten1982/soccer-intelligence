# Testfall KPI 09 – Schüsse aufs Tor

**Spezifikation v2.1** · Stand 08.11.2026

**Regelwerk:** `03_KPI_Regelwerk.md`, Abschnitte 1, 1.1, 2, 9.0 und 9.5
**Datenbasis:** `Database-Soccer-Intelligence.xlsx`, SHA-256 `f37e36d301767321575aeadf908c39e288b9a655d02d85d5bcfde0507effdc34`
**Status:** **bestätigt von Carsten am 08.11.2026** (gemeinsamer Rundgang KPI 05–09 mit je einer normalen Partie und einem Aufsteiger). Erzeugt von Claude mit einer unabhängigen Berechnung direkt aus der Excel-Datei. Nachprüfung per Excel: `Testfaelle_KPI05-09_Nachpruefung.xlsx`.

**Änderung 08.11.2026 (Carsten, Rundgang):** Teamwert zählt jetzt eigene **und** gegnerische Schüsse aufs Tor, Hauptwert ist der Mittelwert (System wie KPI 02). Alle Werte dieser Datei sind neu berechnet.

**Änderung 08.11.2026 (Carsten):** Alle Werte mit **zwei Nachkommastellen**, auch die Abweichung. Die Einstufung richtet sich nach der auf zwei Stellen gerundeten Abweichung (Regelwerk 2.3).

Dieser Testfall ist die verbindliche Referenz für die Umsetzung (Etappe H). Die JSON-Blöcke werden zu automatischen Tests.

---

## 1. Regeln, die dieser Testfall prüft

- Teamwert = Ø Schüsse aufs Tor **beider** Mannschaften (AU + AV, eigene + gegnerische) in den Spielen des Teams; Spiele mit leerem AU oder AV werden ausgelassen.
- Erwartete Schüsse aufs Tor = (Teamwert Heim + Teamwert Auswärts) / 2 (Mittelwert, wie KPI 02).
- Ligareferenz = Ø Schüsse aufs Tor **beider** Teams pro Spiel (AU + AV); Spiele mit leerem AU oder AV werden ausgelassen.
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
| T13 | Premier League | 2025/2026 | 32 | 2026-04-10 | West Ham | Wolves | Sehr kleine negative Abweichung (−0,02 %): Vorzeichen bleibt. Den Sonderfall −0,00 → 0,00 gibt es in den echten Daten nicht; er wird im Code mit einem eigenen Formattest geprüft |
| T14 | Bundesliga | 2026/2027 | 2 | 2026-09-04 | Paderborn | Freiburg | Aufsteiger mit 1 Spiel → vorläufig; starke negative Anomalie |
| T23 | Bundesliga | 2026/2027 | 1 | 2026-08-28 | Freiburg | Werder Bremen | Rundgang 1. Spieltag 2026/27, normale Partie |
| T24 | Bundesliga | 2026/2027 | 1 | 2026-08-28 | Mainz | Paderborn | Rundgang 1. Spieltag 2026/27, Aufsteiger ohne Spiele → nicht berechenbar |

Analysedatum = „Datum von“ des Spieltags im Spielplan (T8, T13: Spieldatum, weil das Spiel aus einer abgeschlossenen Saison stammt).

### Ergebnisse auf einen Blick

| Testfall | Teamwert Heim | Teamwert Auswärts | Ligareferenz | Hauptwert | Abweichung | Anomalie | vorläufig |
|---|---|---|---|---|---|---|---|
| T1 | 12,30 (10 Sp.) | 9,50 (10 Sp.) | 9,99 (180 Sp.) | 10,90 | +9,12 % | keine | nein |
| T2 | 12,30 (10 Sp.) | 10,00 (10 Sp.) | 9,99 (180 Sp.) | 11,15 | +11,62 % | keine | nein |
| T3 | 8,00 (10 Sp.) | 6,70 (10 Sp.) | 7,98 (200 Sp.) | 7,35 | −7,89 % | keine | nein |
| T4 | 9,40 (10 Sp.) | 8,90 (10 Sp.) | 8,71 (196 Sp.) | 9,15 | +5,00 % | keine | nein |
| T5 | 7,90 (10 Sp.) | 8,90 (10 Sp.) | 8,51 (200 Sp.) | 8,40 | −1,29 % | keine | nein |
| T6 | 8,70 (10 Sp.) | 7,00 (1 Sp.) | 7,98 (200 Sp.) | 7,85 | −1,63 % | keine | ja |
| T7 | – (0 Sp.) | 9,00 (1 Sp.) | 8,71 (196 Sp.) | – | – | – | ja |
| T8 | 9,11 (9 Sp.) | 9,10 (10 Sp.) | 9,74 (179 Sp.) | 9,11 | −6,54 % | keine | ja |
| T9 | 6,30 (10 Sp.) | 10,00 (1 Sp.) | 8,71 (196 Sp.) | 8,15 | −6,48 % | keine | ja |
| T10 | 12,50 (10 Sp.) | 12,00 (10 Sp.) | 9,82 (180 Sp.) | 12,25 | +24,79 % | leicht | nein |
| T13 | 8,60 (10 Sp.) | 8,20 (10 Sp.) | 8,40 (199 Sp.) | 8,40 | −0,02 % | keine | nein |
| T14 | 4,00 (1 Sp.) | 8,90 (10 Sp.) | 9,99 (180 Sp.) | 6,45 | −35,43 % | stark | ja |
| T23 | 9,50 (10 Sp.) | 8,50 (10 Sp.) | 9,82 (180 Sp.) | 9,00 | −8,32 % | keine | nein |
| T24 | 10,00 (10 Sp.) | – (0 Sp.) | 9,82 (180 Sp.) | – | – | – | ja |

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
   "summe": 123,
   "teamwert_roh": 12.3,
   "teamwert": "12.30"
  },
  "auswaerts": {
   "team": "FC Koln",
   "spiele": 10,
   "summe": 95,
   "teamwert_roh": 9.5,
   "teamwert": "9.50"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 16-34 + 2026/2027: 1-1",
   "spiele": 180,
   "summe": 1798,
   "wert_roh": 9.9888888889,
   "wert": "9.99"
  },
  "hauptwert_roh": 10.9,
  "hauptwert": "10.90",
  "abweichung_roh": 9.1212458287,
  "abweichung": "9.12",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Indikator liegt bei 10,90 Schüssen aufs Tor. Die Abweichung vom Liga-Durchschnitt beträgt +9,12 %."
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
   "summe": 123,
   "teamwert_roh": 12.3,
   "teamwert": "12.30"
  },
  "auswaerts": {
   "team": "Union Berlin",
   "spiele": 10,
   "summe": 100,
   "teamwert_roh": 10.0,
   "teamwert": "10.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 16-34 + 2026/2027: 1-1",
   "spiele": 180,
   "summe": 1798,
   "wert_roh": 9.9888888889,
   "wert": "9.99"
  },
  "hauptwert_roh": 11.15,
  "hauptwert": "11.15",
  "abweichung_roh": 11.6240266963,
  "abweichung": "11.62",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Indikator liegt bei 11,15 Schüssen aufs Tor. Die Abweichung vom Liga-Durchschnitt beträgt +11,62 %."
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
   "summe": 80,
   "teamwert_roh": 8.0,
   "teamwert": "8.00"
  },
  "auswaerts": {
   "team": "Parma",
   "spiele": 10,
   "summe": 67,
   "teamwert_roh": 6.7,
   "teamwert": "6.70"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 1596,
   "wert_roh": 7.98,
   "wert": "7.98"
  },
  "hauptwert_roh": 7.35,
  "hauptwert": "7.35",
  "abweichung_roh": -7.8947368421,
  "abweichung": "-7.89",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Indikator liegt bei 7,35 Schüssen aufs Tor. Die Abweichung vom Liga-Durchschnitt beträgt −7,89 %."
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
   "summe": 94,
   "teamwert_roh": 9.4,
   "teamwert": "9.40"
  },
  "auswaerts": {
   "team": "Villarreal",
   "spiele": 10,
   "summe": 89,
   "teamwert_roh": 8.9,
   "teamwert": "8.90"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 196,
   "summe": 1708,
   "wert_roh": 8.7142857143,
   "wert": "8.71"
  },
  "hauptwert_roh": 9.15,
  "hauptwert": "9.15",
  "abweichung_roh": 5.0,
  "abweichung": "5.00",
  "anomalie": "keine",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Indikator liegt bei 9,15 Schüssen aufs Tor. Die Abweichung vom Liga-Durchschnitt beträgt +5,00 %."
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
   "summe": 79,
   "teamwert_roh": 7.9,
   "teamwert": "7.90"
  },
  "auswaerts": {
   "team": "Manchester City",
   "spiele": 10,
   "summe": 89,
   "teamwert_roh": 8.9,
   "teamwert": "8.90"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 1702,
   "wert_roh": 8.51,
   "wert": "8.51"
  },
  "hauptwert_roh": 8.4,
  "hauptwert": "8.40",
  "abweichung_roh": -1.2925969448,
  "abweichung": "-1.29",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Indikator liegt bei 8,40 Schüssen aufs Tor. Die Abweichung vom Liga-Durchschnitt beträgt −1,29 %."
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
   "summe": 87,
   "teamwert_roh": 8.7,
   "teamwert": "8.70"
  },
  "auswaerts": {
   "team": "Frosinone",
   "spiele": 1,
   "summe": 7,
   "teamwert_roh": 7.0,
   "teamwert": "7.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 200,
   "summe": 1596,
   "wert_roh": 7.98,
   "wert": "7.98"
  },
  "hauptwert_roh": 7.85,
  "hauptwert": "7.85",
  "abweichung_roh": -1.6290726817,
  "abweichung": "-1.63",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": true,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Indikator liegt bei 7,85 Schüssen aufs Tor. Die Abweichung vom Liga-Durchschnitt beträgt −1,63 %."
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
   "summe": 9,
   "teamwert_roh": 9.0,
   "teamwert": "9.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 196,
   "summe": 1708,
   "wert_roh": 8.7142857143,
   "wert": "8.71"
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
   "summe": 82,
   "teamwert_roh": 9.1111111111,
   "teamwert": "9.11"
  },
  "auswaerts": {
   "team": "Mainz",
   "spiele": 10,
   "summe": 91,
   "teamwert_roh": 9.1,
   "teamwert": "9.10"
  },
  "ligareferenz": {
   "saison_spieltage": "2023/2024: 32-34 + 2024/2025: 1-17",
   "spiele": 179,
   "summe": 1744,
   "wert_roh": 9.7430167598,
   "wert": "9.74"
  },
  "hauptwert_roh": 9.1055555556,
  "hauptwert": "9.11",
  "abweichung_roh": -6.5427497452,
  "abweichung": "-6.54",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": true,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Indikator liegt bei 9,11 Schüssen aufs Tor. Die Abweichung vom Liga-Durchschnitt beträgt −6,54 %."
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
   "summe": 63,
   "teamwert_roh": 6.3,
   "teamwert": "6.30"
  },
  "auswaerts": {
   "team": "Racing Santander",
   "spiele": 1,
   "summe": 10,
   "teamwert_roh": 10.0,
   "teamwert": "10.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 20-38 + 2026/2027: 1-1",
   "spiele": 196,
   "summe": 1708,
   "wert_roh": 8.7142857143,
   "wert": "8.71"
  },
  "hauptwert_roh": 8.15,
  "hauptwert": "8.15",
  "abweichung_roh": -6.4754098361,
  "abweichung": "-6.48",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": true,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Indikator liegt bei 8,15 Schüssen aufs Tor. Die Abweichung vom Liga-Durchschnitt beträgt −6,48 %."
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
   "summe": 125,
   "teamwert_roh": 12.5,
   "teamwert": "12.50"
  },
  "auswaerts": {
   "team": "Stuttgart",
   "spiele": 10,
   "summe": 120,
   "teamwert_roh": 12.0,
   "teamwert": "12.00"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 15-34",
   "spiele": 180,
   "summe": 1767,
   "wert_roh": 9.8166666667,
   "wert": "9.82"
  },
  "hauptwert_roh": 12.25,
  "hauptwert": "12.25",
  "abweichung_roh": 24.7877758913,
  "abweichung": "24.79",
  "anomalie": "leicht",
  "richtung": "positiv",
  "vorlaeufig": false,
  "ueberschrift": "Viele Schüsse aufs Tor erwartet",
  "text": "Der Indikator liegt bei 12,25 Schüssen aufs Tor. Das liegt 24,79 % über dem Liga-Durchschnitt."
 },
 {
  "testfall": "T13",
  "liga": "Premier League",
  "saison": "2025/2026",
  "spieltag": 32,
  "analysedatum": "2026-04-10",
  "heim": {
   "team": "West Ham",
   "spiele": 10,
   "summe": 86,
   "teamwert_roh": 8.6,
   "teamwert": "8.60"
  },
  "auswaerts": {
   "team": "Wolves",
   "spiele": 10,
   "summe": 82,
   "teamwert_roh": 8.2,
   "teamwert": "8.20"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 12-31",
   "spiele": 199,
   "summe": 1672,
   "wert_roh": 8.4020100503,
   "wert": "8.40"
  },
  "hauptwert_roh": 8.4,
  "hauptwert": "8.40",
  "abweichung_roh": -0.023923445,
  "abweichung": "-0.02",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Indikator liegt bei 8,40 Schüssen aufs Tor. Die Abweichung vom Liga-Durchschnitt beträgt −0,02 %."
 },
 {
  "testfall": "T14",
  "liga": "Bundesliga",
  "saison": "2026/2027",
  "spieltag": 2,
  "analysedatum": "2026-09-04",
  "heim": {
   "team": "Paderborn",
   "spiele": 1,
   "summe": 4,
   "teamwert_roh": 4.0,
   "teamwert": "4.00"
  },
  "auswaerts": {
   "team": "Freiburg",
   "spiele": 10,
   "summe": 89,
   "teamwert_roh": 8.9,
   "teamwert": "8.90"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 16-34 + 2026/2027: 1-1",
   "spiele": 180,
   "summe": 1798,
   "wert_roh": 9.9888888889,
   "wert": "9.99"
  },
  "hauptwert_roh": 6.45,
  "hauptwert": "6.45",
  "abweichung_roh": -35.4282536151,
  "abweichung": "-35.43",
  "anomalie": "stark",
  "richtung": "negativ",
  "vorlaeufig": true,
  "ueberschrift": "Wenige Schüsse aufs Tor erwartet",
  "text": "Der Indikator liegt bei 6,45 Schüssen aufs Tor. Das liegt 35,43 % unter dem Liga-Durchschnitt."
 },
 {
  "testfall": "T23",
  "liga": "Bundesliga",
  "saison": "2026/2027",
  "spieltag": 1,
  "analysedatum": "2026-08-28",
  "heim": {
   "team": "Freiburg",
   "spiele": 10,
   "summe": 95,
   "teamwert_roh": 9.5,
   "teamwert": "9.50"
  },
  "auswaerts": {
   "team": "Werder Bremen",
   "spiele": 10,
   "summe": 85,
   "teamwert_roh": 8.5,
   "teamwert": "8.50"
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 15-34",
   "spiele": 180,
   "summe": 1767,
   "wert_roh": 9.8166666667,
   "wert": "9.82"
  },
  "hauptwert_roh": 9.0,
  "hauptwert": "9.00",
  "abweichung_roh": -8.3191850594,
  "abweichung": "-8.32",
  "anomalie": "keine",
  "richtung": "negativ",
  "vorlaeufig": false,
  "ueberschrift": "Keine statistische Besonderheit",
  "text": "Der Indikator liegt bei 9,00 Schüssen aufs Tor. Die Abweichung vom Liga-Durchschnitt beträgt −8,32 %."
 },
 {
  "testfall": "T24",
  "liga": "Bundesliga",
  "saison": "2026/2027",
  "spieltag": 1,
  "analysedatum": "2026-08-28",
  "heim": {
   "team": "Mainz",
   "spiele": 10,
   "summe": 100,
   "teamwert_roh": 10.0,
   "teamwert": "10.00"
  },
  "auswaerts": {
   "team": "Paderborn",
   "spiele": 0,
   "summe": null,
   "teamwert_roh": null,
   "teamwert": null
  },
  "ligareferenz": {
   "saison_spieltage": "2025/2026: 15-34",
   "spiele": 180,
   "summe": 1767,
   "wert_roh": 9.8166666667,
   "wert": "9.82"
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

**Stuttgart** – 10 gültige Spiele, Summe 123, Teamwert 12,30

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107988 | Stuttgart – RB Leipzig | 4:4 | 8 |
| 22.03.2026 | 114388 | Augsburg – Stuttgart | 7:8 | 15 |
| 04.04.2026 | 117441 | Stuttgart – Dortmund | 3:3 | 6 |
| 12.04.2026 | 118014 | Stuttgart – Hamburger SV | 11:5 | 16 |
| 19.04.2026 | 118339 | Bayern Munich – Stuttgart | 9:7 | 16 |
| 26.04.2026 | 118750 | Stuttgart – Werder Bremen | 4:3 | 7 |
| 02.05.2026 | 118986 | Hoffenheim – Stuttgart | 9:5 | 14 |
| 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 9:5 | 14 |
| 16.05.2026 | 120510 | Eintracht Frankfurt – Stuttgart | 7:7 | 14 |
| 28.08.2026 | 132783 | Bayern Munich – Stuttgart | 9:4 | 13 |

**FC Koln** – 10 gültige Spiele, Summe 95, Teamwert 9,50

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106583 | Hamburger SV – FC Koln | 1:2 | 3 |
| 21.03.2026 | 114289 | FC Koln – B. Monchengladbach | 5:3 | 8 |
| 05.04.2026 | 117540 | Eintracht Frankfurt – FC Koln | 7:9 | 16 |
| 12.04.2026 | 118013 | FC Koln – Werder Bremen | 8:2 | 10 |
| 17.04.2026 | 118161 | St. Pauli – FC Koln | 6:1 | 7 |
| 25.04.2026 | 118646 | FC Koln – Bayer Leverkusen | 10:3 | 13 |
| 02.05.2026 | 118987 | Union Berlin – FC Koln | 3:4 | 7 |
| 10.05.2026 | 119365 | FC Koln – Heidenheim | 7:5 | 12 |
| 16.05.2026 | 120509 | Bayern Munich – FC Koln | 7:2 | 9 |
| 29.08.2026 | 132873 | FC Koln – Hoffenheim | 6:4 | 10 |

### T2 – Bayer Leverkusen – Union Berlin (Bundesliga, 2026/2027, Spieltag 2, Analysedatum 2026-09-04)

**Bayer Leverkusen** – 10 gültige Spiele, Summe 123, Teamwert 12,30

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106579 | Bayer Leverkusen – Bayern Munich | 7:5 | 12 |
| 21.03.2026 | 114290 | Heidenheim – Bayer Leverkusen | 5:5 | 10 |
| 04.04.2026 | 117436 | Bayer Leverkusen – Wolfsburg | 11:5 | 16 |
| 11.04.2026 | 117899 | Dortmund – Bayer Leverkusen | 1:4 | 5 |
| 18.04.2026 | 118240 | Bayer Leverkusen – Augsburg | 10:5 | 15 |
| 25.04.2026 | 118646 | FC Koln – Bayer Leverkusen | 10:3 | 13 |
| 02.05.2026 | 118989 | Bayer Leverkusen – RB Leipzig | 8:5 | 13 |
| 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 9:5 | 14 |
| 16.05.2026 | 120508 | Bayer Leverkusen – Hamburger SV | 9:6 | 15 |
| 29.08.2026 | 132872 | Elversberg – Bayer Leverkusen | 6:4 | 10 |

**Union Berlin** – 10 gültige Spiele, Summe 100, Teamwert 10,00

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107987 | Freiburg – Union Berlin | 6:4 | 10 |
| 21.03.2026 | 114288 | Bayern Munich – Union Berlin | 9:1 | 10 |
| 05.04.2026 | 117539 | Union Berlin – St. Pauli | 8:2 | 10 |
| 11.04.2026 | 117900 | Heidenheim – Union Berlin | 3:3 | 6 |
| 18.04.2026 | 118242 | Union Berlin – Wolfsburg | 7:4 | 11 |
| 24.04.2026 | 118560 | RB Leipzig – Union Berlin | 10:1 | 11 |
| 02.05.2026 | 118987 | Union Berlin – FC Koln | 3:4 | 7 |
| 10.05.2026 | 119366 | Mainz – Union Berlin | 3:9 | 12 |
| 16.05.2026 | 120514 | Union Berlin – Augsburg | 9:1 | 10 |
| 29.08.2026 | 132876 | Union Berlin – Eintracht Frankfurt | 10:3 | 13 |

### T3 – Juventus – Parma (Serie A, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Juventus** – 10 gültige Spiele, Summe 80, Teamwert 8,00

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 21.03.2026 | 114299 | Juventus – Sassuolo | 8:1 | 9 |
| 06.04.2026 | 117656 | Juventus – Genoa | 5:3 | 8 |
| 11.04.2026 | 117911 | Atalanta – Juventus | 3:2 | 5 |
| 19.04.2026 | 118349 | Juventus – Bologna | 4:0 | 4 |
| 26.04.2026 | 118761 | AC Milan – Juventus | 1:5 | 6 |
| 03.05.2026 | 119096 | Juventus – Verona | 7:3 | 10 |
| 09.05.2026 | 119281 | Lecce – Juventus | 3:6 | 9 |
| 17.05.2026 | 120620 | Juventus – Fiorentina | 9:4 | 13 |
| 24.05.2026 | 120857 | Torino – Juventus | 5:4 | 9 |
| 23.08.2026 | 130758 | Frosinone – Juventus | 2:5 | 7 |

**Parma** – 10 gültige Spiele, Summe 67, Teamwert 6,70

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 21.03.2026 | 114297 | Parma – Cremonese | 1:4 | 5 |
| 04.04.2026 | 117451 | Lazio – Parma | 3:4 | 7 |
| 12.04.2026 | 118020 | Parma – Napoli | 2:6 | 8 |
| 18.04.2026 | 118254 | Udinese – Parma | 3:1 | 4 |
| 25.04.2026 | 118655 | Parma – Pisa | 5:3 | 8 |
| 03.05.2026 | 119097 | Inter – Parma | 5:0 | 5 |
| 10.05.2026 | 119377 | Parma – AS Roma | 3:7 | 10 |
| 17.05.2026 | 120618 | Como – Parma | 7:2 | 9 |
| 24.05.2026 | 120852 | Parma – Sassuolo | 3:1 | 4 |
| 22.08.2026 | 130663 | Parma – Cagliari | 2:5 | 7 |

### T4 – Atl. Madrid – Villarreal (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Atl. Madrid** – 10 gültige Spiele, Summe 94, Teamwert 9,40

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 22.03.2026 | 114444 | Real Madrid – Atl. Madrid | 10:7 | 17 |
| 04.04.2026 | 117485 | Atl. Madrid – Barcelona | 2:8 | 10 |
| 11.04.2026 | 117953 | Sevilla – Atl. Madrid | 2:2 | 4 |
| 22.04.2026 | 118500 | Elche – Atl. Madrid | 6:3 | 9 |
| 25.04.2026 | 118693 | Atl. Madrid – Ath Bilbao | 4:4 | 8 |
| 02.05.2026 | 119028 | Valencia – Atl. Madrid | 0:5 | 5 |
| 09.05.2026 | 119297 | Atl. Madrid – Celta Vigo | 4:1 | 5 |
| 12.05.2026 | 120229 | Osasuna – Atl. Madrid | 5:4 | 9 |
| 17.05.2026 | 120662 | Atl. Madrid – Girona | 4:11 | 15 |
| 24.05.2026 | 120872 | Villarreal – Atl. Madrid | 8:4 | 12 |

**Villarreal** – 10 gültige Spiele, Summe 89, Teamwert 8,90

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 06.04.2026 | 117677 | Girona – Villarreal | 2:0 | 2 |
| 12.04.2026 | 118055 | Ath Bilbao – Villarreal | 6:6 | 12 |
| 23.04.2026 | 118530 | Oviedo – Villarreal | 4:3 | 7 |
| 26.04.2026 | 118794 | Villarreal – Celta Vigo | 4:3 | 7 |
| 02.05.2026 | 119027 | Villarreal – Levante | 8:3 | 11 |
| 10.05.2026 | 119413 | Mallorca – Villarreal | 8:2 | 10 |
| 13.05.2026 | 120439 | Villarreal – Sevilla | 4:5 | 9 |
| 17.05.2026 | 120667 | Rayo Vallecano – Villarreal | 7:2 | 9 |
| 24.05.2026 | 120872 | Villarreal – Atl. Madrid | 8:4 | 12 |
| 16.08.2026 | 129483 | Racing Santander – Villarreal | 3:7 | 10 |

### T5 – Crystal Palace – Manchester City (Premier League, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Crystal Palace** – 10 gültige Spiele, Summe 79, Teamwert 7,90

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107978 | Crystal Palace – Leeds | 0:3 | 3 |
| 12.04.2026 | 118005 | Crystal Palace – Newcastle | 5:3 | 8 |
| 20.04.2026 | 118408 | Crystal Palace – West Ham | 1:4 | 5 |
| 25.04.2026 | 118603 | Liverpool – Crystal Palace | 3:7 | 10 |
| 03.05.2026 | 119074 | Bournemouth – Crystal Palace | 5:1 | 6 |
| 10.05.2026 | 119351 | Crystal Palace – Everton | 8:6 | 14 |
| 13.05.2026 | 120425 | Manchester City – Crystal Palace | 4:2 | 6 |
| 17.05.2026 | 120589 | Brentford – Crystal Palace | 3:5 | 8 |
| 24.05.2026 | 120843 | Crystal Palace – Arsenal | 3:7 | 10 |
| 22.08.2026 | 130611 | Everton – Crystal Palace | 5:4 | 9 |

**Manchester City** – 10 gültige Spiele, Summe 89, Teamwert 8,90

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 14.03.2026 | 106539 | West Ham – Manchester City | 1:6 | 7 |
| 12.04.2026 | 118008 | Chelsea – Manchester City | 3:8 | 11 |
| 19.04.2026 | 118329 | Manchester City – Arsenal | 5:3 | 8 |
| 22.04.2026 | 118479 | Burnley – Manchester City | 1:9 | 10 |
| 04.05.2026 | 119163 | Everton – Manchester City | 6:4 | 10 |
| 09.05.2026 | 119254 | Manchester City – Brentford | 10:2 | 12 |
| 13.05.2026 | 120425 | Manchester City – Crystal Palace | 4:2 | 6 |
| 19.05.2026 | 120707 | Bournemouth – Manchester City | 2:5 | 7 |
| 24.05.2026 | 120846 | Manchester City – Aston Villa | 3:5 | 8 |
| 23.08.2026 | 130749 | Manchester City – Bournemouth | 6:4 | 10 |

### T6 – Fiorentina – Frosinone (Serie A, 2026/2027, Spieltag 2, Analysedatum 2026-08-28)

**Fiorentina** – 10 gültige Spiele, Summe 87, Teamwert 8,70

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 22.03.2026 | 114403 | Fiorentina – Inter | 6:4 | 10 |
| 04.04.2026 | 117450 | Verona – Fiorentina | 8:1 | 9 |
| 13.04.2026 | 118084 | Fiorentina – Lazio | 2:6 | 8 |
| 20.04.2026 | 118410 | Lecce – Fiorentina | 4:3 | 7 |
| 26.04.2026 | 118758 | Fiorentina – Sassuolo | 5:1 | 6 |
| 04.05.2026 | 119165 | AS Roma – Fiorentina | 7:1 | 8 |
| 10.05.2026 | 119376 | Fiorentina – Genoa | 1:3 | 4 |
| 17.05.2026 | 120620 | Juventus – Fiorentina | 9:4 | 13 |
| 22.05.2026 | 120772 | Fiorentina – Atalanta | 4:6 | 10 |
| 24.08.2026 | 130861 | AS Roma – Fiorentina | 8:4 | 12 |

**Frosinone** – 1 gültige Spiele, Summe 7, Teamwert 7,00

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 23.08.2026 | 130758 | Frosinone – Juventus | 2:5 | 7 |

### T7 – Malaga – Dep. A Coruna (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Malaga** – 0 gültige Spiele, Summe –, Teamwert –

Keine Ligaspiele im Zeitfenster.

**Dep. A Coruna** – 1 gültige Spiele, Summe 9, Teamwert 9,00

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 17.08.2026 | 130470 | Dep. A Coruna – Elche | 3:6 | 9 |

### T8 – Union Berlin – Mainz (Bundesliga, 2024/2025, Spieltag 18, Analysedatum 2025-01-19)

**Union Berlin** – 9 gültige Spiele, Summe 82, Teamwert 9,11

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 27.10.2024 | 14469 | Union Berlin – Eintracht Frankfurt | 4:5 | 9 |
| 02.11.2024 | 14462 | Bayern Munich – Union Berlin | 7:1 | 8 |
| 08.11.2024 | 14458 | Union Berlin – Freiburg | 6:4 | 10 |
| 23.11.2024 | 14448 | Wolfsburg – Union Berlin | 5:4 | 9 |
| 30.11.2024 | 14438 | Union Berlin – Bayer Leverkusen | 2:3 | 5 |
| 06.12.2024 | 14431 | Stuttgart – Union Berlin | 5:3 | 8 |
| 14.12.2024 | 14421 | Union Berlin – Bochum | –:– | – (fehlt, ausgelassen) |
| 21.12.2024 | 14412 | Werder Bremen – Union Berlin | 5:4 | 9 |
| 11.01.2025 | 14400 | Heidenheim – Union Berlin | 9:6 | 15 |
| 15.01.2025 | 14389 | Union Berlin – Augsburg | 4:5 | 9 |

**Mainz** – 10 gültige Spiele, Summe 91, Teamwert 9,10

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 25.10.2024 | 14476 | Mainz – B. Monchengladbach | 6:5 | 11 |
| 03.11.2024 | 14460 | Freiburg – Mainz | 2:2 | 4 |
| 09.11.2024 | 14455 | Mainz – Dortmund | 9:1 | 10 |
| 24.11.2024 | 14442 | Holstein Kiel – Mainz | 2:7 | 9 |
| 01.12.2024 | 14433 | Mainz – Hoffenheim | 8:2 | 10 |
| 08.12.2024 | 14424 | Wolfsburg – Mainz | 5:5 | 10 |
| 14.12.2024 | 14420 | Mainz – Bayern Munich | 4:1 | 5 |
| 21.12.2024 | 14408 | Eintracht Frankfurt – Mainz | 9:3 | 12 |
| 11.01.2025 | 14402 | Mainz – Bochum | 5:2 | 7 |
| 14.01.2025 | 14392 | Bayer Leverkusen – Mainz | 9:4 | 13 |

### T9 – Getafe – Racing Santander (LaLiga, 2026/2027, Spieltag 2, Analysedatum 2026-08-20)

**Getafe** – 10 gültige Spiele, Summe 63, Teamwert 6,30

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 05.04.2026 | 117581 | Getafe – Ath Bilbao | 6:0 | 6 |
| 13.04.2026 | 118088 | Levante – Getafe | 4:1 | 5 |
| 22.04.2026 | 118501 | Real Sociedad – Getafe | 4:0 | 4 |
| 25.04.2026 | 118691 | Getafe – Barcelona | 0:4 | 4 |
| 03.05.2026 | 119130 | Getafe – Rayo Vallecano | 3:6 | 9 |
| 10.05.2026 | 119415 | Oviedo – Getafe | 4:4 | 8 |
| 13.05.2026 | 120441 | Getafe – Mallorca | 4:2 | 6 |
| 17.05.2026 | 120663 | Elche – Getafe | 3:0 | 3 |
| 23.05.2026 | 120811 | Getafe – Osasuna | 3:5 | 8 |
| 15.08.2026 | 128152 | Alaves – Getafe | 8:2 | 10 |

**Racing Santander** – 1 gültige Spiele, Summe 10, Teamwert 10,00

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 16.08.2026 | 129483 | Racing Santander – Villarreal | 3:7 | 10 |

### T10 – Bayern Munich – Stuttgart (Bundesliga, 2026/2027, Spieltag 1, Analysedatum 2026-08-28)

**Bayern Munich** – 10 gültige Spiele, Summe 125, Teamwert 12,50

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 06.03.2026 | 99487 | Bayern Munich – B. Monchengladbach | 9:5 | 14 |
| 14.03.2026 | 106579 | Bayer Leverkusen – Bayern Munich | 7:5 | 12 |
| 21.03.2026 | 114288 | Bayern Munich – Union Berlin | 9:1 | 10 |
| 04.04.2026 | 117437 | Freiburg – Bayern Munich | 4:9 | 13 |
| 11.04.2026 | 117903 | St. Pauli – Bayern Munich | 3:8 | 11 |
| 19.04.2026 | 118339 | Bayern Munich – Stuttgart | 9:7 | 16 |
| 25.04.2026 | 118648 | Mainz – Bayern Munich | 8:6 | 14 |
| 02.05.2026 | 118984 | Bayern Munich – Heidenheim | 7:5 | 12 |
| 09.05.2026 | 119271 | Wolfsburg – Bayern Munich | 5:9 | 14 |
| 16.05.2026 | 120509 | Bayern Munich – FC Koln | 7:2 | 9 |

**Stuttgart** – 10 gültige Spiele, Summe 120, Teamwert 12,00

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 07.03.2026 | 99520 | Mainz – Stuttgart | 6:4 | 10 |
| 15.03.2026 | 107988 | Stuttgart – RB Leipzig | 4:4 | 8 |
| 22.03.2026 | 114388 | Augsburg – Stuttgart | 7:8 | 15 |
| 04.04.2026 | 117441 | Stuttgart – Dortmund | 3:3 | 6 |
| 12.04.2026 | 118014 | Stuttgart – Hamburger SV | 11:5 | 16 |
| 19.04.2026 | 118339 | Bayern Munich – Stuttgart | 9:7 | 16 |
| 26.04.2026 | 118750 | Stuttgart – Werder Bremen | 4:3 | 7 |
| 02.05.2026 | 118986 | Hoffenheim – Stuttgart | 9:5 | 14 |
| 09.05.2026 | 119270 | Stuttgart – Bayer Leverkusen | 9:5 | 14 |
| 16.05.2026 | 120510 | Eintracht Frankfurt – Stuttgart | 7:7 | 14 |

### T13 – West Ham – Wolves (Premier League, 2025/2026, Spieltag 32, Analysedatum 2026-04-10)

**West Ham** – 10 gültige Spiele, Summe 86, Teamwert 8,60

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 17.01.2026 | 79614 | Tottenham – West Ham | 6:4 | 10 |
| 24.01.2026 | 84245 | West Ham – Sunderland | 5:2 | 7 |
| 31.01.2026 | 88934 | Chelsea – West Ham | 6:6 | 12 |
| 07.02.2026 | 90887 | Burnley – West Ham | 5:4 | 9 |
| 10.02.2026 | 91721 | West Ham – Manchester Utd | 3:3 | 6 |
| 21.02.2026 | 97156 | West Ham – Bournemouth | 3:5 | 8 |
| 28.02.2026 | 97422 | Liverpool – West Ham | 7:4 | 11 |
| 04.03.2026 | 99462 | Fulham – West Ham | 5:3 | 8 |
| 14.03.2026 | 106539 | West Ham – Manchester City | 1:6 | 7 |
| 22.03.2026 | 114379 | Aston Villa – West Ham | 7:1 | 8 |

**Wolves** – 10 gültige Spiele, Summe 82, Teamwert 8,20

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 18.01.2026 | 79682 | Wolves – Newcastle | 2:2 | 4 |
| 24.01.2026 | 84271 | Manchester City – Wolves | 4:1 | 5 |
| 31.01.2026 | 88891 | Wolves – Bournemouth | 7:4 | 11 |
| 07.02.2026 | 90889 | Wolves – Chelsea | 3:6 | 9 |
| 11.02.2026 | 91734 | Nottingham – Wolves | 10:3 | 13 |
| 18.02.2026 | 97023 | Wolves – Arsenal | 2:4 | 6 |
| 22.02.2026 | 97224 | Crystal Palace – Wolves | 3:7 | 10 |
| 27.02.2026 | 97381 | Wolves – Aston Villa | 2:5 | 7 |
| 03.03.2026 | 99447 | Wolves – Liverpool | 3:7 | 10 |
| 16.03.2026 | 110046 | Brentford – Wolves | 3:4 | 7 |

### T14 – Paderborn – Freiburg (Bundesliga, 2026/2027, Spieltag 2, Analysedatum 2026-09-04)

**Paderborn** – 1 gültige Spiele, Summe 4, Teamwert 4,00

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 29.08.2026 | 132874 | Mainz – Paderborn | 4:0 | 4 |

**Freiburg** – 10 gültige Spiele, Summe 89, Teamwert 8,90

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 15.03.2026 | 107987 | Freiburg – Union Berlin | 6:4 | 10 |
| 22.03.2026 | 114387 | St. Pauli – Freiburg | 5:6 | 11 |
| 04.04.2026 | 117437 | Freiburg – Bayern Munich | 4:9 | 13 |
| 12.04.2026 | 118015 | Mainz – Freiburg | 3:3 | 6 |
| 19.04.2026 | 118338 | Freiburg – Heidenheim | 4:2 | 6 |
| 26.04.2026 | 118751 | Dortmund – Freiburg | 5:4 | 9 |
| 03.05.2026 | 119084 | Freiburg – Wolfsburg | 3:4 | 7 |
| 10.05.2026 | 119364 | Hamburger SV – Freiburg | 5:3 | 8 |
| 16.05.2026 | 120511 | Freiburg – RB Leipzig | 5:6 | 11 |
| 30.08.2026 | 132993 | Freiburg – Werder Bremen | 5:3 | 8 |

### T23 – Freiburg – Werder Bremen (Bundesliga, 2026/2027, Spieltag 1, Analysedatum 2026-08-28)

**Freiburg** – 10 gültige Spiele, Summe 95, Teamwert 9,50

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 07.03.2026 | 99518 | Freiburg – Bayer Leverkusen | 9:5 | 14 |
| 15.03.2026 | 107987 | Freiburg – Union Berlin | 6:4 | 10 |
| 22.03.2026 | 114387 | St. Pauli – Freiburg | 5:6 | 11 |
| 04.04.2026 | 117437 | Freiburg – Bayern Munich | 4:9 | 13 |
| 12.04.2026 | 118015 | Mainz – Freiburg | 3:3 | 6 |
| 19.04.2026 | 118338 | Freiburg – Heidenheim | 4:2 | 6 |
| 26.04.2026 | 118751 | Dortmund – Freiburg | 5:4 | 9 |
| 03.05.2026 | 119084 | Freiburg – Wolfsburg | 3:4 | 7 |
| 10.05.2026 | 119364 | Hamburger SV – Freiburg | 5:3 | 8 |
| 16.05.2026 | 120511 | Freiburg – RB Leipzig | 5:6 | 11 |

**Werder Bremen** – 10 gültige Spiele, Summe 85, Teamwert 8,50

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 08.03.2026 | 99639 | Union Berlin – Werder Bremen | 2:5 | 7 |
| 15.03.2026 | 107986 | Werder Bremen – Mainz | 3:2 | 5 |
| 21.03.2026 | 114291 | Wolfsburg – Werder Bremen | 4:3 | 7 |
| 04.04.2026 | 117440 | Werder Bremen – RB Leipzig | 5:2 | 7 |
| 12.04.2026 | 118013 | FC Koln – Werder Bremen | 8:2 | 10 |
| 18.04.2026 | 118243 | Werder Bremen – Hamburger SV | 10:3 | 13 |
| 26.04.2026 | 118750 | Stuttgart – Werder Bremen | 4:3 | 7 |
| 02.05.2026 | 118988 | Werder Bremen – Augsburg | 4:7 | 11 |
| 09.05.2026 | 119268 | Hoffenheim – Werder Bremen | 4:2 | 6 |
| 16.05.2026 | 120515 | Werder Bremen – Dortmund | 3:9 | 12 |

### T24 – Mainz – Paderborn (Bundesliga, 2026/2027, Spieltag 1, Analysedatum 2026-08-28)

**Mainz** – 10 gültige Spiele, Summe 100, Teamwert 10,00

| Datum | id | Begegnung | Schüsse aufs Tor AU:AV | zählt |
|---|---|---|---|---|
| 07.03.2026 | 99520 | Mainz – Stuttgart | 6:4 | 10 |
| 15.03.2026 | 107986 | Werder Bremen – Mainz | 3:2 | 5 |
| 22.03.2026 | 114386 | Mainz – Eintracht Frankfurt | 5:4 | 9 |
| 04.04.2026 | 117439 | Hoffenheim – Mainz | 5:5 | 10 |
| 12.04.2026 | 118015 | Mainz – Freiburg | 3:3 | 6 |
| 19.04.2026 | 118340 | B. Monchengladbach – Mainz | 4:7 | 11 |
| 25.04.2026 | 118648 | Mainz – Bayern Munich | 8:6 | 14 |
| 03.05.2026 | 119082 | St. Pauli – Mainz | 3:6 | 9 |
| 10.05.2026 | 119366 | Mainz – Union Berlin | 3:9 | 12 |
| 16.05.2026 | 120512 | Heidenheim – Mainz | 5:9 | 14 |

**Paderborn** – 0 gültige Spiele, Summe –, Teamwert –

Keine Ligaspiele im Zeitfenster.

### Ligareferenzen je Liga und Spieltag

**Bundesliga, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-09-04):** 2025/2026: 16-34 + 2026/2027: 1-1 → 180 Spiele, Summe 1798, Ligareferenz 9,99

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 16 | 9 | 96 |  |
| 2025/2026 | 17 | 9 | 95 |  |
| 2025/2026 | 18 | 9 | 94 |  |
| 2025/2026 | 19 | 9 | 81 |  |
| 2025/2026 | 20 | 9 | 76 |  |
| 2025/2026 | 21 | 9 | 81 |  |
| 2025/2026 | 22 | 9 | 89 |  |
| 2025/2026 | 23 | 9 | 85 |  |
| 2025/2026 | 24 | 9 | 84 |  |
| 2025/2026 | 25 | 9 | 91 |  |
| 2025/2026 | 26 | 9 | 64 |  |
| 2025/2026 | 27 | 9 | 93 |  |
| 2025/2026 | 28 | 9 | 99 |  |
| 2025/2026 | 29 | 9 | 91 |  |
| 2025/2026 | 30 | 9 | 99 |  |
| 2025/2026 | 31 | 9 | 87 |  |
| 2025/2026 | 32 | 9 | 87 |  |
| 2025/2026 | 33 | 9 | 100 |  |
| 2025/2026 | 34 | 9 | 106 |  |
| 2026/2027 | 1 | 9 | 100 |  |

**Serie A, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-28):** 2025/2026: 20-38 + 2026/2027: 1-1 → 200 Spiele, Summe 1596, Ligareferenz 7,98

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 78 |  |
| 2025/2026 | 21 | 10 | 72 |  |
| 2025/2026 | 22 | 10 | 95 |  |
| 2025/2026 | 23 | 10 | 93 |  |
| 2025/2026 | 24 | 10 | 77 |  |
| 2025/2026 | 25 | 10 | 86 |  |
| 2025/2026 | 26 | 10 | 72 |  |
| 2025/2026 | 27 | 10 | 83 |  |
| 2025/2026 | 28 | 10 | 68 |  |
| 2025/2026 | 29 | 10 | 73 |  |
| 2025/2026 | 30 | 10 | 75 |  |
| 2025/2026 | 31 | 10 | 72 |  |
| 2025/2026 | 32 | 10 | 82 |  |
| 2025/2026 | 33 | 10 | 65 |  |
| 2025/2026 | 34 | 10 | 74 |  |
| 2025/2026 | 35 | 10 | 77 |  |
| 2025/2026 | 36 | 10 | 91 |  |
| 2025/2026 | 37 | 10 | 88 |  |
| 2025/2026 | 38 | 10 | 86 |  |
| 2026/2027 | 1 | 10 | 89 |  |

**LaLiga, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-20):** 2025/2026: 20-38 + 2026/2027: 1-1 → 196 Spiele, Summe 1708, Ligareferenz 8,71

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 104 |  |
| 2025/2026 | 21 | 10 | 90 |  |
| 2025/2026 | 22 | 10 | 82 |  |
| 2025/2026 | 23 | 10 | 83 |  |
| 2025/2026 | 24 | 10 | 75 |  |
| 2025/2026 | 25 | 10 | 89 |  |
| 2025/2026 | 26 | 10 | 84 |  |
| 2025/2026 | 27 | 10 | 93 |  |
| 2025/2026 | 28 | 10 | 97 |  |
| 2025/2026 | 29 | 10 | 104 |  |
| 2025/2026 | 30 | 10 | 75 |  |
| 2025/2026 | 31 | 10 | 85 |  |
| 2025/2026 | 32 | 10 | 73 |  |
| 2025/2026 | 33 | 10 | 84 |  |
| 2025/2026 | 34 | 10 | 81 |  |
| 2025/2026 | 35 | 10 | 95 |  |
| 2025/2026 | 36 | 10 | 77 |  |
| 2025/2026 | 37 | 10 | 83 |  |
| 2025/2026 | 38 | 10 | 105 |  |
| 2026/2027 | 1 | 6 | 49 |  |

**Premier League, analysiert Saison 2026/2027 Spieltag 2 (Stichtag 2026-08-28):** 2025/2026: 20-38 + 2026/2027: 1-1 → 200 Spiele, Summe 1702, Ligareferenz 8,51

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 20 | 10 | 76 |  |
| 2025/2026 | 21 | 10 | 87 |  |
| 2025/2026 | 22 | 10 | 74 |  |
| 2025/2026 | 23 | 10 | 87 |  |
| 2025/2026 | 24 | 10 | 84 |  |
| 2025/2026 | 25 | 10 | 93 |  |
| 2025/2026 | 26 | 10 | 70 |  |
| 2025/2026 | 27 | 10 | 87 |  |
| 2025/2026 | 28 | 10 | 94 |  |
| 2025/2026 | 29 | 10 | 80 |  |
| 2025/2026 | 30 | 10 | 70 |  |
| 2025/2026 | 31 | 10 | 93 |  |
| 2025/2026 | 32 | 10 | 99 |  |
| 2025/2026 | 33 | 10 | 75 |  |
| 2025/2026 | 34 | 10 | 83 |  |
| 2025/2026 | 35 | 10 | 92 |  |
| 2025/2026 | 36 | 10 | 90 |  |
| 2025/2026 | 37 | 10 | 90 |  |
| 2025/2026 | 38 | 10 | 90 |  |
| 2026/2027 | 1 | 10 | 88 |  |

**Bundesliga, analysiert Saison 2024/2025 Spieltag 18 (Stichtag 2025-01-19):** 2023/2024: 32-34 + 2024/2025: 1-17 → 179 Spiele, Summe 1744, Ligareferenz 9,74

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2023/2024 | 32 | 9 | 100 |  |
| 2023/2024 | 33 | 9 | 66 |  |
| 2023/2024 | 34 | 9 | 117 |  |
| 2024/2025 | 1 | 9 | 82 |  |
| 2024/2025 | 2 | 9 | 93 |  |
| 2024/2025 | 3 | 9 | 103 |  |
| 2024/2025 | 4 | 9 | 81 |  |
| 2024/2025 | 5 | 9 | 85 |  |
| 2024/2025 | 6 | 9 | 90 |  |
| 2024/2025 | 7 | 9 | 97 |  |
| 2024/2025 | 8 | 9 | 92 |  |
| 2024/2025 | 9 | 9 | 84 |  |
| 2024/2025 | 10 | 9 | 82 |  |
| 2024/2025 | 11 | 9 | 89 |  |
| 2024/2025 | 12 | 9 | 76 |  |
| 2024/2025 | 13 | 9 | 71 |  |
| 2024/2025 | 14 | 8 | 67 | 1 |
| 2024/2025 | 15 | 9 | 91 |  |
| 2024/2025 | 16 | 9 | 85 |  |
| 2024/2025 | 17 | 9 | 93 |  |

Ausgelassen (Wert fehlt): id 14421 Union Berlin – Bochum

**Bundesliga, analysiert Saison 2026/2027 Spieltag 1 (Stichtag 2026-08-28):** 2025/2026: 15-34 → 180 Spiele, Summe 1767, Ligareferenz 9,82

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 15 | 9 | 69 |  |
| 2025/2026 | 16 | 9 | 96 |  |
| 2025/2026 | 17 | 9 | 95 |  |
| 2025/2026 | 18 | 9 | 94 |  |
| 2025/2026 | 19 | 9 | 81 |  |
| 2025/2026 | 20 | 9 | 76 |  |
| 2025/2026 | 21 | 9 | 81 |  |
| 2025/2026 | 22 | 9 | 89 |  |
| 2025/2026 | 23 | 9 | 85 |  |
| 2025/2026 | 24 | 9 | 84 |  |
| 2025/2026 | 25 | 9 | 91 |  |
| 2025/2026 | 26 | 9 | 64 |  |
| 2025/2026 | 27 | 9 | 93 |  |
| 2025/2026 | 28 | 9 | 99 |  |
| 2025/2026 | 29 | 9 | 91 |  |
| 2025/2026 | 30 | 9 | 99 |  |
| 2025/2026 | 31 | 9 | 87 |  |
| 2025/2026 | 32 | 9 | 87 |  |
| 2025/2026 | 33 | 9 | 100 |  |
| 2025/2026 | 34 | 9 | 106 |  |

**Premier League, analysiert Saison 2025/2026 Spieltag 32 (Stichtag 2026-04-10):** 2025/2026: 12-31 → 199 Spiele, Summe 1672, Ligareferenz 8,40

| Saison | Spieltag | Spiele | Summe | ausgelassen |
|---|---|---|---|---|
| 2025/2026 | 12 | 10 | 86 |  |
| 2025/2026 | 13 | 10 | 87 |  |
| 2025/2026 | 14 | 10 | 84 |  |
| 2025/2026 | 15 | 10 | 99 |  |
| 2025/2026 | 16 | 10 | 79 |  |
| 2025/2026 | 17 | 10 | 75 |  |
| 2025/2026 | 18 | 10 | 86 |  |
| 2025/2026 | 19 | 10 | 87 |  |
| 2025/2026 | 20 | 10 | 76 |  |
| 2025/2026 | 21 | 10 | 87 |  |
| 2025/2026 | 22 | 10 | 74 |  |
| 2025/2026 | 23 | 10 | 87 |  |
| 2025/2026 | 24 | 10 | 84 |  |
| 2025/2026 | 25 | 10 | 93 |  |
| 2025/2026 | 26 | 10 | 70 |  |
| 2025/2026 | 27 | 10 | 87 |  |
| 2025/2026 | 28 | 10 | 94 |  |
| 2025/2026 | 29 | 10 | 80 |  |
| 2025/2026 | 30 | 10 | 70 |  |
| 2025/2026 | 31 | 9 | 87 |  |

