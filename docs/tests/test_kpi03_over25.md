# Testfall KPI 03 – Over 2.5 Goals

**Spezifikation v1.2** · Stand 08.11.2026

**Regelwerk:** `03_KPI_Regelwerk.md`, Abschnitte 1, 2 und 5
**Datenbasis:** `Database-Soccer-Intelligence.xlsx`, SHA-256 `6d68583c2e66616e92c1bf3e8a8611b4b517bcf4c0a7a91c68101ea26a2284e2`
**Status:** Stand Spieltag 1 (2026/27) bestätigt am 28.10.2026 · Stand Spieltag 3 (2025/26) bestätigt am 29.10.2026

**Änderung 08.11.2026 (Carsten, Etappe H): Anzeige mit zwei Nachkommastellen.** Alle angezeigten Werte (Teamwerte, Ligareferenz, Hauptwert, Abweichung, Teamabweichungen) werden auf zwei Nachkommastellen gerundet; die Einstufung richtet sich nach der auf zwei Stellen gerundeten Abweichung (Regelwerk 2.3). Die JSON-Blöcke, Texte und Kontrollpunkte sind angepasst. **Keine Einstufung ändert sich** (24 von 24 geprüft). Exakte Rechenwerte in den Erläuterungen (z. B. „47 Tore / 10 Spiele = 4,7“) bleiben wie sie sind.

**Datenbasis aktualisiert am 30.10.2026:** neue SHA-256 nach Korrektur von zwei versehentlich überschriebenen Zellen in der Premier League (id 5393 `Gameday` „bitte“ → 4; id 99466 `FT Home Goals` „Ergebnisse stimmen.“ → 2). Alle erwarteten Werte wurden mit der neuen Datei nachgerechnet: unverändert (144 Prüfwerte, 0 Abweichungen).

Dieser Testfall ist die verbindliche Referenz für die technische Umsetzung. Der Code muss mit derselben Datenbasis exakt diese Ergebnisse liefern. Die JSON-Blöcke sind für automatische Tests gedacht und müssen exakt übereinstimmen.

---

## 1. Regeln, die dieser Testfall prüft

- Teamwert = Ø Gesamttore (beider Mannschaften) in den letzten 10 Ligaspielen des Teams, **identisch mit KPI 02**.
- Teamabweichung = (Teamwert − 2,5) / 2,5 × 100.
- Gemeinsamer Teamdurchschnitt = (Teamwert Heim + Teamwert Auswärts) / 2 (Hauptwert).
- Gemeinsame Over-2.5-Abweichung = (Gemeinsamer Teamdurchschnitt − 2,5) / 2,5 × 100.
- Referenz ist der **feste Wert 2,5**, keine Ligareferenz.
- Anomalie-Einstufung nur auf Basis der gemeinsamen Abweichung, Schwellenwerte gemäss Regelwerk Abschnitt 2.
- Aufsteiger ohne Ligaspiele: kein gemeinsamer Wert, keine Abweichung, keine Anomalie.

---

## 2. Auswahl- und Rechenschritte (feste Reihenfolge)

### 2.1 Teamwert

Exakt wie in `test_kpi02_erwartete_tore.md`, Abschnitt 2.1. Der Code soll dafür **dieselbe Funktion** verwenden wie KPI 02, damit beide KPIs immer auf identischen Teamwerten beruhen.

### 2.2 Abweichungen, Anomalie

1. Teamabweichung je Team mit verfügbarem Teamwert berechnen (auch beim Gegner eines Aufsteigers).
2. Fehlt ein Teamwert → gemeinsamer Teamdurchschnitt, gemeinsame Abweichung und Anomalie nicht verfügbar. Ende.
3. Gemeinsamer Teamdurchschnitt = (Teamwert Heim + Teamwert Auswärts) / 2.
4. Gemeinsame Abweichung = (Gemeinsamer Teamdurchschnitt − 2,5) / 2,5 × 100, mit ungerundeten Werten.
5. Rundung erst am Ende: alle angezeigten Werte auf eine Nachkommastelle, kaufmännisch, **mit Dezimalarithmetik** (siehe KPI 02, Kontrollpunkt 4.4).
6. Anomalie anhand der **gerundeten** gemeinsamen Abweichung: |x| ≤ 20,00 keine · 20,00 < |x| ≤ 35,00 leicht · |x| > 35,00 stark. Teamabweichungen werden **nicht** eingestuft.

---

## 3. Stand Spieltag 1 (Saison 2026/27)

**Ausgangslage:** Die Datenbank enthält noch keine Spiele der Saison 2026/27. Alle Teamwerte stammen aus der Saison 2025/26.

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
    "referenzwert": "2.5",
    "heim":      {"team": "Bayern Munich",    "spiele": 10, "tore": 47, "teamwert_roh": 4.7, "teamwert": "4.70", "teamabweichung_roh": 88.0, "teamabweichung": "+88.00"},
    "auswaerts": {"team": "Stuttgart",        "spiele": 10, "tore": 40, "teamwert_roh": 4.0, "teamwert": "4.00", "teamabweichung_roh": 60.0, "teamabweichung": "+60.00"},
    "gemeinsam_roh": 4.35, "gemeinsam": "4.35",
    "abweichung_roh": 74.0, "abweichung": "+74.00",
    "anomalie": "stark", "richtung": "positiv", "vorlaeufig": false,
    "ueberschrift": "Über 2,5 Goals erwartet",
    "text": "In den bisherigen Spielen beider Teams fielen im Schnitt 74,00 % mehr Tore als die 2,5-Tore-Marke."
  },
  {
    "testfall": "BL-2",
    "liga": "Bundesliga", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "referenzwert": "2.5",
    "heim":      {"team": "Elversberg",       "spiele": 0,  "tore": null, "teamwert_roh": null, "teamwert": null, "teamabweichung_roh": null, "teamabweichung": null},
    "auswaerts": {"team": "Bayer Leverkusen", "spiele": 10, "tore": 41,   "teamwert_roh": 4.1,  "teamwert": "4.10", "teamabweichung_roh": 64.0, "teamabweichung": "+64.00"},
    "gemeinsam_roh": null, "gemeinsam": null,
    "abweichung_roh": null, "abweichung": null,
    "anomalie": null, "richtung": null, "vorlaeufig": true,
    "ueberschrift": null, "text": null
  },
  {
    "testfall": "PL-1",
    "liga": "Premier League", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "referenzwert": "2.5",
    "heim":      {"team": "Newcastle",        "spiele": 10, "tore": 26, "teamwert_roh": 2.6, "teamwert": "2.60", "teamabweichung_roh": 4.0,  "teamabweichung": "+4.00"},
    "auswaerts": {"team": "Liverpool",        "spiele": 10, "tore": 32, "teamwert_roh": 3.2, "teamwert": "3.20", "teamabweichung_roh": 28.0, "teamabweichung": "+28.00"},
    "gemeinsam_roh": 2.9, "gemeinsam": "2.90",
    "abweichung_roh": 16.0, "abweichung": "+16.00",
    "anomalie": "keine", "richtung": "positiv", "vorlaeufig": false,
    "ueberschrift": "Keine statistische Besonderheit",
    "text": "In den bisherigen Spielen erzielten die beiden Teams im Schnitt 16,00 % mehr Tore als die 2,5-Tore-Marke."
  },
  {
    "testfall": "PL-2",
    "liga": "Premier League", "saison": "2026/2027", "spieltag": 1, "analysedatum": "2026-08-22",
    "referenzwert": "2.5",
    "heim":      {"team": "Hull",             "spiele": 0,  "tore": null, "teamwert_roh": null, "teamwert": null, "teamabweichung_roh": null, "teamabweichung": null},
    "auswaerts": {"team": "Manchester Utd",   "spiele": 10, "tore": 31,   "teamwert_roh": 3.1,  "teamwert": "3.10", "teamabweichung_roh": 24.0, "teamabweichung": "+24.00"},
    "gemeinsam_roh": null, "gemeinsam": null,
    "abweichung_roh": null, "abweichung": null,
    "anomalie": null, "richtung": null, "vorlaeufig": true,
    "ueberschrift": null, "text": null
  }
]
```

Hinweise zum JSON:
- Gerundete Werte als Text mit Punkt; im Dashboard mit Komma (4,35).
- `_roh`-Werte mit Toleranz 1e-9 vergleichen (z. B. ergibt (2,6 + 3,2) / 2 in Gleitkomma 2,9000000000000004).
- `teamabweichung` wird im Dashboard in Klammern hinter dem Teamwert angezeigt, z. B. „4,70 (+88,00 %)“.

### 3.3 Eingabedaten

Die Spiele je Team sind **identisch** mit `test_kpi02_erwartete_tore.md`, Abschnitt 3.3. Zusammenfassung zur Kontrolle:

| Team | Spiele | Gesamttore | Teamwert | Spiel-IDs |
|---|---|---|---|---|
| Bayern Munich | 10 | 47 | 4,7 | 99487, 106579, 114288, 117437, 117903, 118339, 118648, 118984, 119271, 120509 |
| Stuttgart | 10 | 40 | 4,0 | 99520, 107988, 114388, 117441, 118014, 118339, 118750, 118986, 119270, 120510 |
| Elversberg | 0 | – | – | – |
| Bayer Leverkusen | 10 | 41 | 4,1 | 99518, 106579, 114290, 117436, 117899, 118240, 118646, 118989, 119270, 120508 |
| Newcastle | 10 | 26 | 2,6 | 99466, 106538, 114378, 118005, 118200, 118606, 118932, 119352, 120593, 120844 |
| Liverpool | 10 | 32 | 3,2 | 99447, 107981, 114243, 117862, 118327, 118603, 119075, 119250, 120476, 120845 |
| Hull | 0 | – | – | – |
| Manchester Utd | 10 | 31 | 3,1 | 99466, 107979, 114203, 118082, 118202, 118824, 119075, 119253, 120588, 120841 |

---

## 4. Kontrollpunkte für den Code

### 4.1 Konsistenz mit KPI 02
- Teamwerte und gemeinsamer Teamdurchschnitt müssen exakt dem Teamwert bzw. Torindikator aus KPI 02 entsprechen (BL-1: 4,35 · PL-1: 2,90).
- KPI 02 und KPI 03 unterscheiden sich **nur** im Referenzwert: BL-1 ergibt bei KPI 02 +34,08 % (leicht), bei KPI 03 +74,00 % (stark).

### 4.2 Referenzwert
- KPI 03 verwendet immer 2,5, **nie** die Ligareferenz. Ein Code, der versehentlich die Ligareferenz einsetzt, liefert für BL-1 +34,08 % statt +74,00 %.

### 4.3 Teamabweichungen
- Werden auch beim Gegner eines Aufsteigers berechnet (Leverkusen +64,00 %, Man Utd +24,00 %).
- Werden **nicht** als Anomalie eingestuft. Liverpool (+28,00 %) ist für sich keine „leichte Anomalie“; massgeblich ist nur die gemeinsame Abweichung (PL-1: +16,00 % → keine).

### 4.4 Aufsteiger
- Elversberg und Hull: gemeinsamer Wert, Abweichung und Anomalie `null`, **keine Fehlermeldung**.
- Der Teamwert des Gegners darf nicht als gemeinsamer Wert ausgegeben werden.

### 4.5 Rundung
- BL-1: gemeinsamer Teamdurchschnitt 4,35 → Anzeige **4,35** (zwei Nachkommastellen seit 08.11.2026; bis dahin 4,4). Gerundet wird weiterhin mit Dezimalarithmetik, nicht mit `round()`.
- Die Abweichung wird mit dem ungerundeten Wert 4,35 berechnet (+74,00 %); mit dem früheren Anzeigewert 4,4 ergäbe sich fälschlich +76,00 %.

---

## 5. Annahmen und Beobachtungen

1. ~~**Nachkommastellen Hauptwert** (Regelwerk, offener Punkt 9)~~ **Geklärt am 08.11.2026:** zwei Nachkommastellen für alle Werte (Regelwerk 2.3). Ursprünglicher Text: Das Regelwerk nennt als Beispiel „3,10“ (zwei Nachkommastellen), die allgemeine Rundungsregel eine Nachkommastelle. Der Testfall verwendet **eine** Nachkommastelle. Wird auf zwei umgestellt, ändern sich die Anzeigewerte (BL-1: 4,35; Teamwerte 4,70 / 4,00 usw.), nicht aber Abweichungen und Einstufungen.
2. **Frontend-Text:** `{Abweichung}` statt `{Hauptwert}` ist seit 30.10.2026 festgelegt (Regelwerk, Punkt 1 erledigt). Text bei genau 0,00 % noch offen (offener Punkt 2).
3. **Rundung Teamabweichungen:** auf eine Nachkommastelle angenommen (offener Punkt 6).
4. **Beobachtung 2,5-Marke:** Die Bundesliga-Ligareferenz liegt bei 3,24 Toren (+29,78 % gegenüber 2,5). Ein durchschnittliches Bundesliga-Spiel wäre bei KPI 03 bereits eine leichte Anomalie, in der Premier League (2,71, +8,40 %) nicht. Rechnerisch korrekt; mögliche spätere Anpassung über KPI-spezifische Schwellenwerte (Regelwerk Abschnitt 2.2).

---

## 6. Stand Spieltag 3 (Saison 2025/26)

**Warum ein historischer Spieltag:** siehe `test_kpi01_formkurve.md`, Abschnitt 4.

**Ausgangslage:** Die Teamwerte setzen sich aus zwei Saisons zusammen und sind **identisch** mit `test_kpi02_erwartete_tore.md`, Abschnitt 6. Die analysierten Spiele und alle späteren Spiele stehen in der Datenbank und dürfen nicht verwendet werden.

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
    "referenzwert": "2.5",
    "heim":      {"team": "Bayern Munich",  "spiele": 10, "tore": 43, "teamwert_roh": 4.3, "teamwert": "4.30", "teamabweichung_roh": 72.0,  "teamabweichung": "+72.00"},
    "auswaerts": {"team": "Hamburger SV",   "spiele": 2,  "tore": 2,  "teamwert_roh": 1.0, "teamwert": "1.00", "teamabweichung_roh": -60.0, "teamabweichung": "-60.00"},
    "gemeinsam_roh": 2.65, "gemeinsam": "2.65",
    "abweichung_roh": 6.0, "abweichung": "+6.00",
    "anomalie": "keine", "richtung": "positiv", "vorlaeufig": true,
    "ueberschrift": "Keine statistische Besonderheit",
    "text": "In den bisherigen Spielen erzielten die beiden Teams im Schnitt 6,00 % mehr Tore als die 2,5-Tore-Marke."
  },
  {
    "testfall": "BL-3b",
    "liga": "Bundesliga", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-09-13",
    "referenzwert": "2.5",
    "heim":      {"team": "Wolfsburg",      "spiele": 10, "tore": 27, "teamwert_roh": 2.7, "teamwert": "2.70", "teamabweichung_roh": 8.0,  "teamabweichung": "+8.00"},
    "auswaerts": {"team": "FC Koln",        "spiele": 2,  "tore": 6,  "teamwert_roh": 3.0, "teamwert": "3.00", "teamabweichung_roh": 20.0, "teamabweichung": "+20.00"},
    "gemeinsam_roh": 2.85, "gemeinsam": "2.85",
    "abweichung_roh": 14.0, "abweichung": "+14.00",
    "anomalie": "keine", "richtung": "positiv", "vorlaeufig": true,
    "ueberschrift": "Keine statistische Besonderheit",
    "text": "In den bisherigen Spielen erzielten die beiden Teams im Schnitt 14,00 % mehr Tore als die 2,5-Tore-Marke."
  },
  {
    "testfall": "PL-3a",
    "liga": "Premier League", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-08-30",
    "referenzwert": "2.5",
    "heim":      {"team": "Manchester Utd", "spiele": 10, "tore": 23, "teamwert_roh": 2.3, "teamwert": "2.30", "teamabweichung_roh": -8.0, "teamabweichung": "-8.00"},
    "auswaerts": {"team": "Burnley",        "spiele": 2,  "tore": 5,  "teamwert_roh": 2.5, "teamwert": "2.50", "teamabweichung_roh": 0.0,  "teamabweichung": "0.00"},
    "gemeinsam_roh": 2.4, "gemeinsam": "2.40",
    "abweichung_roh": -4.0, "abweichung": "-4.00",
    "anomalie": "keine", "richtung": "negativ", "vorlaeufig": true,
    "ueberschrift": "Keine statistische Besonderheit",
    "text": "In den bisherigen Spielen erzielten die beiden Teams im Schnitt 4,00 % weniger Tore als die 2,5-Tore-Marke."
  },
  {
    "testfall": "PL-3b",
    "liga": "Premier League", "saison": "2025/2026", "spieltag": 3, "analysedatum": "2025-08-30",
    "referenzwert": "2.5",
    "heim":      {"team": "Sunderland",     "spiele": 2,  "tore": 5,  "teamwert_roh": 2.5, "teamwert": "2.50", "teamabweichung_roh": 0.0,  "teamabweichung": "0.00"},
    "auswaerts": {"team": "Brentford",      "spiele": 10, "tore": 30, "teamwert_roh": 3.0, "teamwert": "3.00", "teamabweichung_roh": 20.0, "teamabweichung": "+20.00"},
    "gemeinsam_roh": 2.75, "gemeinsam": "2.75",
    "abweichung_roh": 10.0, "abweichung": "+10.00",
    "anomalie": "keine", "richtung": "positiv", "vorlaeufig": true,
    "ueberschrift": "Keine statistische Besonderheit",
    "text": "In den bisherigen Spielen erzielten die beiden Teams im Schnitt 10,00 % mehr Tore als die 2,5-Tore-Marke."
  }
]
```

Hinweise zum JSON:
- `_roh`-Werte sind die mathematisch exakten Werte. In Gleitkomma weichen sie minimal ab (siehe Kontrollpunkt 6.4, Rundung); Vergleich mit Toleranz 1e-9.
- Teamabweichung genau 0,00 wird ohne Vorzeichen angegeben (Annahme, siehe 6.5).

### 6.3 Eingabedaten

Die Spiele je Team sind **identisch** mit `test_kpi02_erwartete_tore.md`, Abschnitt 6.3. Zusammenfassung zur Kontrolle:

| Team | Spiele | Gesamttore | Teamwert | Spiel-IDs |
|---|---|---|---|---|
| Bayern Munich | 10 | 43 | 4,3 | 14301, 14296, 14281, 14275, 14265, 14257, 14246, 14239, 64488, 64722 |
| Hamburger SV | 2 | 2 | 1,0 | 64592, 64659 |
| Wolfsburg | 10 | 27 | 2,7 | 14304, 14288, 14287, 14276, 14268, 14255, 14251, 14235, 64551, 64775 |
| FC Koln | 2 | 6 | 3,0 | 64593, 64773 |
| Manchester Utd | 10 | 23 | 2,3 | 14612, 14602, 14594, 14582, 14572, 14561, 14558, 14544, 64402, 64581 |
| Burnley | 2 | 5 | 2,5 | 64373, 64535 |
| Sunderland | 2 | 5 | 2,5 | 64372, 64535 |
| Brentford | 10 | 30 | 3,0 | 14613, 14606, 14596, 14580, 14572, 14567, 14554, 14549, 64404, 64534 |

### 6.4 Kontrollpunkte für den Code

**Konsistenz mit KPI 02**
- Teamwerte und gemeinsamer Teamdurchschnitt müssen exakt KPI 02, Abschnitt 6 entsprechen (2,65 · 2,85 · 2,40 · 2,75).

**Richtung kann sich zwischen KPI 02 und KPI 03 umkehren**
- BL-3a: KPI 02 −13,59 % (unter Liga-Durchschnitt), KPI 03 +6,00 % (über 2,5-Marke). Ebenso BL-3b (−7,07 % / +14,00 %) und PL-3b (−3,51 % / +10,00 %).
- Ursache: Ligareferenz liegt über 2,5 (Bundesliga 3,07, Premier League 2,85). Das ist **korrekt** und darf vom Code nicht „angeglichen“ werden.

**Teamabweichungen auf den Grenzen**
- FC Koln und Brentford liegen mit +20,00 % genau auf der Anomalie-Grenze, Burnley und Sunderland mit 0,00 % genau auf der Marke.
- Teamabweichungen werden **nicht** eingestuft. Es darf keine Team-Anomalie angezeigt werden.

**Rundung**
- BL-3a: gemeinsamer Wert 2,65 → Anzeige **2,65** (bis 08.11.2026: 2,7; Python `round(2.65, 1)` ergab fälschlich 2,6).
- **Abschneiden statt Runden:** In Gleitkomma ergibt die Abweichung bei BL-3a 5,9999999999999964 statt 6,0 und bei Man Utd −8,000000000000007 statt −8,0. Korrekt gerundet: +6,00 % und −8,00 %. Schneidet der Code ab statt zu runden, erscheint fälschlich 5,99 %. Der Fehler fällt optisch kaum auf.
- Rechenbasis ist immer der ungerundete Wert: Mit 2,7 statt 2,65 ergäbe sich bei BL-3a +8,00 % statt +6,00 %.

**Aufsteiger und Saisonfenster**
- HSV, FC Koln, Burnley, Sunderland: je 2 Spiele, `vorlaeufig` true für die gesamte Begegnung.
- FC Koln und Burnley: ältere Spiele (2023/24 und früher) dürfen nicht einfliessen.

### 6.5 Beobachtungen und Annahmen

- **Durchschnitt verdeckt Gegensätze:** Bayern +72,00 % und HSV −60,00 % ergeben gemeinsam nur +6,00 %. Korrekt nach Regelwerk, aber eine inhaltliche Grenze des KPI: Er zeigt nicht, dass zwei sehr unterschiedliche Teams aufeinandertreffen. Mögliche spätere Ergänzung im Dashboard (z. B. Teamabweichungen gut sichtbar anzeigen).
- **Scheinbarer Widerspruch zu KPI 02:** Zwei Karten nebeneinander können in entgegengesetzte Richtungen zeigen. Für die spätere Gestaltung der Erklärtexte berücksichtigen (z. B. Hinweis „Vergleich mit fester Marke, nicht mit dem Liga-Durchschnitt“).
- **Annahme Anzeige 0,0 %:** Teamabweichung genau 0,00 wird als „2,50 (0,00 %)“ ohne Vorzeichen angezeigt. Zu bestätigen im Zusammenhang mit offenem Punkt 2 im Regelwerk.
- **Keine Anomalie in diesem Durchgang:** Alle vier Partien im Normalbereich. Die starke Anomalie ist durch Abschnitt 3 (BL-1, +74,00 %) abgedeckt.

---

## 7. Weitere Tests (geplant)

- **Ausgedachter Testdatensatz** für Sonderfälle: gemeinsame Abweichung genau ±20,00 % und ±35,00 % (Grenzfälle der Einstufung), gemeinsame Abweichung genau 0,00 % (Text-Sonderfall), Team mit genau 1 Spiel, 2-Tage-Regel.
- **Praxistest 3. Spieltag 2026/27:** optional, sobald die Saison läuft.
