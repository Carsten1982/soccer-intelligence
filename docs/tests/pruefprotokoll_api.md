# Prüfprotokoll: Vollvergleich API-Football und Bereinigung der Datenbank (15.11.2026)

**Geprüft von:** Claude · **Auftrag und Entscheidungen:** Carsten · Spezifikation: `docs/06_Datenlieferung.md`

| | Datei | SHA-256 |
|---|---|---|
| Ausgangsstand (aktiv seit 10.11.2026, von Carsten am 15.11.2026 vom Server geliefert) | `Database-Soccer-Intelligence.xlsx` | `451348b6550b91f4df3a26450a26d205e76f69c13ac520d080d3a427ff084904` |
| Bereinigte Fassung | `Database-Soccer-Intelligence.xlsx` | `3a2589616b2b0625d3a9150484bd0ce24e6340b334756b115d0d4582925822a8` |

---

## 1. Tests der API (Phase 1)

| Frage | Ergebnis |
|---|---|
| Gratis-Plan | nur Saisons 2022–2024 („Free plans do not have access to this season, try from 2022 to 2024.“) |
| Plan Pro | aktiv bis 15.02.2027, 7'500 Abfragen pro Tag, 300 pro Minute; Kopfzeile `x-ratelimit-requests-remaining` vorhanden |
| Spielliste | `fixtures?league&season` liefert die ganze Saison in einer Abfrage; enthält auch Relegationsspiele (Runde „Final“) → nur Runden „Regular Season“ verwenden |
| Mehrfachabfrage | `fixtures?ids=…` liefert bis 20 Spiele mit `events`, `lineups`, `statistics`, `players` (u. a. xG) |
| Halbzeit-Statistik | `fixtures/statistics?half=true` liefert `statistics_1h` und `statistics_2h` getrennt (wie unsere Datei), geprüft für 2024 und 2025 |
| Zeitzone | `timezone=Europe/Zurich`; Datum und Anstosszeit stimmen mit `matchDate` überein (99,65 %) |
| Leere Werte | Die API liefert bei **null Karten** einen leeren Wert statt 0. Gelbe Karten werden darum bei leerem Wert aus den Spielereignissen gezählt (Entscheidung Carsten 15.11.2026) |
| Wertungsspiele | Union Berlin – Bochum: API mit Ergebnis auf dem Platz (1:1); Verona – Roma: API mit Wertung (3:0) |
| Verbrauch | Vollvergleich 3'534 Abfragen (Spiellisten 36, Mehrfachabfragen 606, Halbzeit-Statistik 2'892), alle erfolgreich; Rohdaten 52 MB komprimiert |

## 2. Vollvergleich Altbestand gegen API-Football (2018/19–2025/26)

Zuordnung: **alle 11'568 Spiele** eindeutig (Saison + Heim + Gast, Teamzuordnung über Datum und Ergebnis); kein Spiel
fehlt auf einer Seite.

| Feld | identisch | Ziel 99 % |
|---|---|---|
| Datum, Land, Saison | 100 % | ✅ |
| Tore Endstand und Halbzeit | 99,95 % | ✅ |
| Spieltag | 99,34 % (Abweichungen nur bei rekonstruierten Spieltagen) | ✅ |
| Ecken gesamt (KPI 05) | 99,5 % | ✅ |
| Gelbe Karten gesamt (KPI 04) | 97,2 % (je Saison 92–99,5 %) | ❌ |
| Schüsse aufs Tor gesamt (KPI 09) | 89,6 % (Serie A 2018/19–2020/21 rund 40 %, Bundesliga 2020/21–2023/24 rund 73 %, sonst meist 97–100 %) | ❌ |
| Ballbesitz / Schüsse gesamt / Schüsse daneben (kein KPI) | 63 % / 81 % / 77 % | – |
| Halbzeitwerte ab 2024: Ecken / Schüsse aufs Tor | 99,5 % / 96–98 % | – |
| Schiedsrichter | 25 % (meist nur andere Schreibweise, z. B. „H. Osmers“) | – |

Damit war die Abnahmeregel für eine vollständige Umstellung (Spezifikation E12) **nicht erfüllt**.

## 3. Dreifachvergleich mit football-data.co.uk

Unabhängige dritte Quelle: freie CSV-Dateien von football-data.co.uk (Endstand, Halbzeit, Schüsse, Schüsse aufs Tor,
Ecken, Karten), Freigabe Carsten 15.11.2026. Zuordnung über Saison, Datum (± 3 Tage) und Teamnamen: 11'567 von 11'568
Spielen. Anzahl Werte (je Spiel Heim und Gast):

| Feld | alle gleich | Altbestand weicht ab | API weicht ab | dritte Quelle weicht ab | alle verschieden |
|---|---|---|---|---|---|
| Gelbe Karten | 22'126 | **453** | 190 | 354 | 9 |
| Schüsse aufs Tor | 20'584 | 83 | **2'297** | 145 | 23 |
| Ecken | 22'885 | 35 | 80 | 132 | 0 |
| Schüsse gesamt | 18'542 | 147 | **4'098** | 267 | 78 |

**Befund:**
- Bei den **Gelben Karten** hat der Altbestand mehr Fehler als die API (häufig 0 Karten, wo es mehrere gab;
  vor allem 2021/22 und 2024/25).
- Bei **Schüssen aufs Tor** weicht die API ab, fast nur in Serie A 2018/19–2020/21 und Bundesliga 2019/20–2023/24.
  Ab 2025/26 stimmen alle drei Quellen überein. Einschränkung: Altbestand und dritte Quelle könnten denselben
  Ursprung haben; „zwei gegen eins“ ist ein starkes Indiz, kein Beweis.
- **Ergebnisse LaLiga 2025/26, Spieltag 37** (17.05.2026, zehn Spiele zur gleichen Zeit): Im Altbestand waren die Tore
  (Endstand und Halbzeit, auch Spalten N–P) zwischen den Spielen vertauscht; die Statistiken waren richtig. API und
  dritte Quelle stimmen für alle zehn Spiele überein. Die Korrektur vom 07.11.2026 (K–M aus N–P) hatte die
  vertauschten Werte übernommen.

Die vollständige Liste (8'419 abweichende Werte und 76 Spieltage, je mit allen drei Werten) hat Carsten als Excel-Datei
erhalten (deutsch und englisch, 15.11.2026).

## 4. Bereinigung (Entscheidung Carsten 15.11.2026)

**Regel:** Ein Wert wird nur korrigiert, wenn **API-Football und football-data.co.uk übereinstimmen** und nur der
Altbestand abweicht. Dazu die offiziellen Spieltage der API. Tore auf dem Platz bleiben (Verona – Roma).

| Änderung | Anzahl |
|---|---|
| Gelbe Karten gesamt | 453 |
| Schüsse gesamt | 147 |
| Schüsse aufs Tor gesamt | 83 |
| Ecken gesamt | 35 |
| Tore (LaLiga 2025/26 Spieltag 37 und Einzelfälle; Endstand, Halbzeit, 2. Halbzeit, Ergebnisbuchstaben stimmig) | 56 Zellen |
| Spieltag (offiziell statt rekonstruiert: Premier League 2018/19, Serie A 2019/20, LaLiga 2020/21 und 2025/26) | 76 |
| Halbzeitwerte zum neuen Gesamtwert aus der API (Karten aus Ereignissen, sonst Halbzeit-Statistik ab 2024) | 718 Zellen |
| Halbzeitwerte unbekannt und darum leer (= keine Daten), im Blatt *Datenhinweise* dokumentiert | 364 Zellen |
| **Geänderte Zellen insgesamt** | **1'932** |
| Neue Einträge im Blatt *Datenhinweise* | 146 |

Änderungsprotokoll (jede Zelle mit altem und neuem Wert und Grund): `Aenderungsprotokoll.csv`, an Carsten übergeben.
Die Saison 2026/27 wurde nicht verändert (nicht Teil des Vergleichs; ab dem Stichtag kommen neue Spiele von der API).

## 5. Prüfung der bereinigten Fassung

| Prüfung | vorher | nachher |
|---|---|---|
| Fehler | 0 | **0** |
| Warnungen | 24 | 35 |
| Hinweise | 64 | 201 |

- **11 neue Warnungen** „Schüsse < aufs Tor + daneben“: Schüsse gesamt wurde korrigiert; dabei zeigt sich, dass im
  Altbestand „Schüsse daneben“ bei diesen Spielen nicht stimmt (z. B. 17 daneben bei 19 Schüssen). „Daneben“ lässt sich
  mit der dritten Quelle nicht prüfen und bleibt unverändert. Kein KPI nutzt diese Felder.
- **137 neue Hinweise**: dokumentierte leere Halbzeitwerte (Blatt *Datenhinweise*).

## 6. Wirkung auf das Dashboard (gültige Schwellen von Version 0.13)

Vollvergleich mit dem App-Code (Stichtag = Spieldatum, alle 11'978 Spiele 2018/19–2026/27):

| KPI | geänderte Abweichung | geänderte Einstufung |
|---|---|---|
| 02 Erwartete Tore | 218 | 19 |
| 03 Über 2,5 Tore | 69 | 15 |
| 04 Gelbe Karten | 9'779 (Teamwerte und Ligareferenz verschieben sich leicht) | **950** |
| 05 Ecken | 3'828 | 27 |
| 06 / 07 Tore Halbzeit | 165 / 218 | 20 / 12 |
| 08 Beide treffen | 203 | 23 |
| 09 Schüsse aufs Tor | 6'103 | 56 |

Top Anomalien: 105 von 316 Spieltagslisten ändern sich. Häufigkeit Datenqualität (2025/26): Änderungen vor allem bei
KPI 04 (z. B. Bundesliga leicht 82 → 69).

**Sensitivitätsanalyse neu** (alle Ligen, 2019/20–2025/26, gültige Schwellen): alle KPIs praktisch unverändert
(Mehrwert ± 0,5 Pp.), ausser **KPI 04 stark**: positiv +10,37 → **+6,45** (Funktioniert → Funktioniert leicht),
negativ +6,70 → **+5,00** (Funktioniert → Funktioniert leicht); KPI 04 leicht positiv +6,58 → +6,68, leicht negativ
+6,25 → +5,87 (beide weiter Funktioniert). Ein Teil der früheren Wirkung der starken Kartenschwelle beruhte auf
fehlerhaften Kartenwerten. Die gültigen Schwellen bleiben unverändert (Entscheidung Carsten: KPI-Anpassungen erst,
wenn die neue Datenbasis steht).

## 7. Nachweis „zwei Quellen gemischt“ für 2025/26 (R7, Version 0.15)

Die KPIs nutzen Saison und Vorsaison: 2025/26 (Altbestand, bereinigt) und ab 2026/27 die API. Übereinstimmung aller drei
Quellen je Teamwert in 2025/26 (vor der Bereinigung; „Altbestand weicht ab“ wurde danach korrigiert):

| Liga | Gelbe Karten | Schüsse aufs Tor | Ecken |
|---|---|---|---|
| Bundesliga | 99,3 % | 99,3 % | 99,7 % |
| Premier League | 96,8 % | 99,0 % | 98,0 % |
| Serie A | 98,6 % | 99,7 % | 99,7 % |
| LaLiga | 96,3 % | 99,1 % | 99,9 % |

Nach der Bereinigung weichen Datenbank und API in 2025/26 nur noch dort ab, wo die API allein abweicht (höchstens 20 von
700 Werten, LaLiga Gelbe Karten). Tore, Datum und Spieltag: über 99,9 %. Feste Zuordnung eigene ID ↔ API-ID für alle
11'978 Spiele (Datum gleich, Endstand gleich ausser Verona – Roma 2020/21, Wertung). Tor-Ereignisse passen bei 11'963 von
11'978 Spielen zum Endstand (Grundlage der Prüfung R2). Entscheidung Carsten 15.11.2026: reicht als Nachweis; keine
rückwirkende Bereinigung mehr.
