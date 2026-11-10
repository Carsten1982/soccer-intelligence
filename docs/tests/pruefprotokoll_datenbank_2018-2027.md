# Prüfprotokoll: Neue Datenbank 2018/19–2026/27 (Version 0.11)

**Datum:** 10.11.2026 · **Geprüft von:** Claude · **Auftrag und Freigabe:** Carsten

Teil A ist der Prüfbericht zur neuen Excel-Datei, Teil B der Vollvergleich vorher/nachher für Version 0.11
(Referenzsaison, neue Saisonauswahl). Datenbasis: `docs/02_Datenbasis.md`, Abschnitt 4d; Regel: KPI-Regelwerk 1.2.

| | Datei | SHA-256 |
|---|---|---|
| Eingang (von Carsten) | `Database-Soccer-Intelligence.xlsx` | `a54a91374be2c312cb2e35dac35c9ce8121291c355d4a3cea0f554c009a5b9f2` |
| Ausgang (korrigiert, neue Datenbank) | Kopie `tests/referenz/Database-Soccer-Intelligence_451348b6.xlsx` | `451348b6550b91f4df3a26450a26d205e76f69c13ac520d080d3a427ff084904` |
| Vergleich (bisherige Datenbank) | `tests/referenz/Database-Soccer-Intelligence_f37e36d3.xlsx` | `f37e36d301767321575aeadf908c39e288b9a655d02d85d5bcfde0507effdc34` |

---

## Teil A – Prüfung der Excel-Datei

### A.1 Ergebnis

| Prüfpunkt | Ergebnis |
|---|---|
| Eingangsdatei mit der App-Prüfung | nicht verwendbar: 868 Fehler (Datum und Spieltag leer, „Wert“ statt Zahl) |
| Bundesliga, Spalten N–BF | ab 2020/21 verrutscht, repariert (A.2) |
| LaLiga, Girona – Osasuna, 10.01.2026 (id 77856) | „Wert“ statt 0 in Spalte L, repariert |
| Spalte A `Date` leer | ergänzt aus `matchDate`, sicher |
| Spalte B `Gameday` leer | rekonstruiert (A.3); Premier League 2018/19 und 2019/20 unsicher |
| Neue Datenbank mit der App-Prüfung | **0 Fehler**, 24 Warnungen, 64 Hinweise |
| Saisons 2020/21–2025/26 gegen `f37e36d3` | **zellgenau identisch** in allen vier Ligen |
| Neue Saisons: Teams, Spiele, Paarungen | vollständig und stimmig |
| Blatt *Datenhinweise* (9 Einträge) | unverändert, alle Spiele gefunden |

### A.2 Bundesliga: verrutschte Spalten N–BF

In der Eingangsdatei passten bei den Bundesliga-Spielen ab 2020/21 die Spalten N–BF (Full-Time-Tore, Halbzeiten, alle
Statistiken) nicht zum Spiel in A–M. Beispiel Bayern – Schalke, 18.09.2020: K–M 8:0, N–P 3:2. Vermutlich wurden beim
Einfügen der neuen Saisons nur in A–M Zeilen eingeschoben.

| Saisons | Zustand in der Eingangsdatei | Reparatur |
|---|---|---|
| 2018/19, 2019/20 | in Ordnung (K–M = N–P = Halbzeit 1 + 2, 100 %) | keine |
| 2020/21 bis Mitte 2022/23 | überschrieben, nicht mehr in der Datei | aus `f37e36d3` per id |
| Mitte 2022/23 bis 2025/26 | 679 Zeilen zu weit oben | aus `f37e36d3` per id (1.836 Spiele 2020/21–2025/26) |
| 2026/27 | 670 Zeilen zu weit oben, eigene Zeilen leer | aus der verschobenen Stelle (Zeilen 1780–1860, 81 Spiele) |

Kontrolle bei jedem Spiel: Tore K/L = Full-Time N/O = Halbzeit 1 + 2; die 9 Spiele des 1. Spieltags 2026/27 zusätzlich
gleich wie in `f37e36d3`. Stichproben von Carsten mit seiner Quelle: Premier League 2021/22, 25 Spiele (300 Werte:
Ecken und gelbe Karten je Halbzeit) und Bundesliga 2022/23, 100 Spiele (1.300 Werte: Ballbesitz, Schüsse, Schüsse aufs
Tor) – alle gleich wie in der neuen Datenbank; in der Eingangsdatei waren alle 100 Bundesliga-Spiele falsch.

### A.3 Spieldatum und Spieltag

- **Spalte A:** Datum aus `matchDate` (in allen 6.745 bisherigen Zeilen ist A genau dieses Datum). Ergänzt: 2018/19 und
  2019/20 je 306 bzw. 380 Spiele je Liga, 2026/27 Bundesliga 72, Premier League 90, Serie A 100, LaLiga 94.
- **Spalte B:** rekonstruiert als Optimierung über die ganze Saison: Jedes Team spielt genau einmal je Spieltag; jedes
  Spiel kommt in den Spieltag, dessen Termin am nächsten liegt; ein Nachholspiel in den Spieltag, in dem beide Teams frei
  sind (Regelwerk 1.1).

Test an den Saisons mit bekanntem Spieltag (2020/21–2025/26):

| Liga | richtig rekonstruiert |
|---|---|
| Bundesliga | 100 % in allen 6 Saisons |
| Serie A | 98,9–100 % (10 Fehler in 2.280 Spielen) |
| LaLiga | 100 % in allen 6 Saisons |
| Premier League | 40–100 % (2024/25, 2025/26: 100 %; 2020/21: 87 %; 2021/22: 52 %; 2022/23: 40 %; 2023/24: 86 %) |

Die Premier League spielt Spieltage teils in anderer Reihenfolge (2020/21 Spieltag 19 vor 18; 2022/23 ganzer Spieltag 7
nach dem Tod der Queen Monate später). Die offizielle Nummer ist dann aus Datum und Teams nicht eindeutig bestimmbar.
Alle bekannten Spieltage 2026/27 werden in allen vier Ligen getroffen; bekannte Nachholspiele in den neuen Saisons richtig
zugeordnet (Gladbach – Köln, Sturmtief Sabine, Feb. 2020; Genua- und Sampdoria-Spiele nach dem Brückeneinsturz, Aug.
2018; Clásico-Verschiebung, Okt. 2019).

**Premier League 2018/19 und 2019/20: rekonstruiert, nicht offiziell.** Entscheidung Carsten 10.11.2026: übernehmen,
weil die Quelle keine offiziellen Spieltage liefert. Wirkung nur am Rand des Fensters der Ligareferenz (letzte 20
Spieltage); 2018/19 ist Referenzsaison.

### A.4 Meldungen der App-Prüfung (neue Datenbank)

0 Fehler. Neu gegenüber `f37e36d3`:

| Meldung | Anzahl | Saison | Bewertung |
|---|---:|---|---|
| Warnung „Schüsse < aufs Tor + daneben“ | 18 | 2018/19 (Bundesliga 12, Premier League 4, LaLiga 2) | Quelle; zählt nur für die Schüsse |
| Warnung „Spieltag unvollständig“ | 1 | LaLiga 2026/27, Spieltag 8: 9 von 10 | echtes Nachholspiel, noch nicht gespielt |
| Hinweis „Mehr Tore als Schüsse aufs Tor“ | 4 | 2019/20 (3), 2026/27 (1) | meist Eigentore |
| Hinweis „Saison unvollständig“ | 4 | 2026/27 | laufende Saison |

### A.5 Struktur und Plausibilität der neuen Saisons

2018/19 und 2019/20 in allen vier Ligen vollständig: 306 bzw. 380 Spiele, 18 bzw. 20 Teams, jede Paarung genau einmal,
jedes Team genau einmal je Spieltag, keine fehlenden Statistikwerte, alle Schiedsrichter eingetragen. Teams nur in
2018/19–2019/20 (historisch korrekt): Bundesliga Düsseldorf, Hannover, Nürnberg; Premier League Cardiff, Huddersfield;
Serie A Brescia, Chievo, Spal.

Durchschnitt je Spiel (2018/19 · 2019/20, in Klammern 2020/21–2025/26):

| Liga | Tore | Gelbe Karten | Ecken | Schüsse aufs Tor |
|---|---|---|---|---|
| Bundesliga | 3,18 · 3,21 (3,03–3,24) | 3,30 · 3,86 (3,29–4,14) | 10,06 · 10,10 (9,17–9,88) | 9,67 · 9,59 (9,24–9,90) |
| Premier League | 2,82 · 2,72 (2,69–3,28) | 3,26 · 3,38 (2,93–4,36) | 10,28 · 10,70 (9,98–10,81) | 8,71 · 8,57 (8,38–9,89) |
| Serie A | 2,68 · 3,04 (2,43–3,05) | 4,65 · 4,96 (3,70–4,50) | 10,69 · 10,64 (8,82–9,68) | 10,48 · 11,40 (8,07–10,60) |
| LaLiga | 2,59 · 2,48 (2,50–2,69) | 5,16 · 5,11 (4,34–5,03) | 9,59 · 9,24 (8,74–9,54) | 8,43 · 7,85 (7,43–8,68) |

Plausibel; Serie A und LaLiga hatten 2018–2020 etwas mehr Karten, Ecken und Schüsse aufs Tor (seither sinkend).

---

## Teil B – Vollvergleich vorher/nachher (Version 0.11)

Gerechnet wurde, was das Dashboard zeigt:
- **Ligaseite** je Spiel und je Spieltag: alle KPI 01–09 mit Teamwerten, Ligareferenz, Hauptwert, Abweichung, Anomalie und
  „vorläufig“; Stichtag = erstes Datum des Spieltags wie „Datum von“; gültige Schwellen aus `schwellen.toml`.
- **Top Anomalien** je Saison und Spieltag über alle vier Ligen.
- **Häufigkeit der Anomalien** je Liga.
- **Simulation**: alle Fälle von `build_cases` (Abweichung, eingetroffen).

### B.1 Code vorher (`origin/main`, 0.10.1) gegen nachher (0.11), gleiche Datenbank

| Datenbank | Spiele | Spieltage | Top-Listen | Häufigkeit | Simulationsfälle | Abweichungen |
|---|---:|---:|---:|---|---:|---:|
| neu `451348b6` | 11.978 | 1.226 | 316 | 4 Ligen, je 2025/26 | 77.318 | **0** |
| alt `f37e36d3` | 8.730 | 894 | 231 | 4 Ligen, je 2025/26 | 53.932 | **0** |

KPI-Formeln, Rundung, Schwellen, Ligaseiten, Top Anomalien und Häufigkeit sind durch den neuen Code unverändert.
Die bisherige Regel (Saisons mit Vorsaison) und die neue (alle ausser der ältesten) wählen bei beiden Dateien dieselben
Saisons, weil keine Saison fehlt.

### B.2 Datenbank alt gegen neu, neuer Code

| Bereich | verglichen | Abweichungen |
|---|---|---:|
| Ligaseite je Spiel, 2021/22 bis 1. Spieltag 2026/27 | 7.284 Spiele | **0** |
| Ligaseite je Spieltag | 745 Spieltage | **0** |
| Top Anomalien je Spieltag (vier Ligen) | 171 Spieltage, 684 Einträge | **0** |
| Häufigkeit der Anomalien (2025/26) | 4 Ligen × 8 KPIs | **0** |
| Simulation, alle Fälle der alten Datenbank | 53.932 Fälle | **0** |

Nicht vergleichbar: LaLiga 2026/27, Spieltag 3 (in der alten Datei nur 5 von 10 Spielen). **Erwartete Änderung:**
2020/21 war bisher die Referenzsaison ohne Vorsaison; jetzt steht 2019/20 davor. Von den 1.446 Spielen 2020/21 haben
780 jetzt andere Werte (Teamwerte und Ligareferenz zu Saisonbeginn vollständig, weniger „vorläufig“). 2020/21 wird
neu ausgewertet. Die Ligaseiten zeigen nur Spieltage aus dem Spielplan (2026/27) und sind davon nicht betroffen.

### B.3 Unabhängige Gegenrechnung der neu ausgewerteten Spiele (`tests/gegenrechnung.py`)

Alle Spiele 2019/20, 2020/21 und 2026/27 (bis 10.11.2026) mit der neuen Datenbank:

| Liga | Spiele | Werte Ligaseite | Fälle Simulation | Abweichungen |
|---|---:|---:|---:|---:|
| Bundesliga | 693 | 11.088 | 4.944 | 0 |
| Premier League | 860 | 13.760 | 6.200 | 0 |
| Serie A | 870 | 13.920 | 6.210 | 0 |
| LaLiga | 879 | 14.064 | 6.344 | 0 |
| **Summe** | **3.302** | **52.832** | **23.698** | **0** |

Die Saisons 2021/22–2025/26 sind identisch mit `f37e36d3` (B.2) und wurden dort am 07./08.11.2026 vollständig
gegengerechnet (`pruefprotokoll_etappe_f.md`, `pruefprotokoll_etappe_h.md`).

### B.4 Rechenzeit (C6)

`build_cases` für alle vier Ligen, nacheinander, ohne andere Last (Claude-Umgebung):

| Datenbank | ausgewertete Spiele | Bundesliga | Premier League | Serie A | LaLiga | Summe |
|---|---:|---:|---:|---:|---:|---:|
| alt `f37e36d3` (2021/22–2026/27) | 7.284 | 8,5 s | 10,6 s | 11,6 s | 11,5 s | **42 s** |
| neu `451348b6` (2019/20–2026/27) | 10.532 | 13,1 s | 18,0 s | 17,6 s | 18,2 s | **67 s** |

+59 % bei +45 % Spielen: Jede Teamabfrage durchsucht zusätzlich die längere Tabelle. Auf dem Server dauerte die
bisherige Rechnung rund 30 s (Dashboard-Briefing 6.4); erwartet werden jetzt rund 50 s, einmal je Datenbankstand (danach
aus dem Zwischenspeicher). Kein Handlungsbedarf; ein Beschleunigen (nur Saison und Vorsaison durchsuchen) wäre ein
eigener Schritt.

### B.5 Automatische Tests

Neu `tests/test_seasons.py` (Briefing T1–T6) mit Stichproben aus Teil B; bei jedem Pull Request und jedem Einspielen.
Laufzeit und Anzahl siehe `RELEASE.md`.
