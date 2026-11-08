# Prüfprotokoll Etappe H – KPI 05–09, zwei Nachkommastellen

**Datum:** 08.11.2026 · **Geprüft von:** Claude · **Datenbank:** SHA-256 `f37e36d3…` · **Spielplan:** Stand 07.11.2026 (Spieltage 1–2, vier Blätter)

Ziel: KPI 05–09 und die Umstellung auf zwei Nachkommastellen so gründlich prüfen, dass Carsten nur noch die Darstellung im Browser abnehmen muss.

---

## 1. Testfälle (automatisch bei jedem Einspielen)

| Prüfung | Umfang | Ergebnis |
|---|---|---|
| KPI 01–04 gegen die bestätigten Testfälle (Referenz-Datenbank `6d68583c`), jetzt mit zwei Nachkommastellen | 8 + 8 + 8 + 8 Testfälle | alle bestanden, **keine Einstufung geändert** |
| KPI 05–09 gegen die bestätigten Testfälle (Referenz-Datenbank `f37e36d3`, neu in `tests/referenz/`) | 12 + 12 + 12 + 11 + 14 = 61 Testfälle | alle bestanden (Teamwerte, Ligareferenz, Hauptwert, Abweichung, Einstufung, „vorläufig“, Überschrift, Text) |
| Gegenrechnung (`tests/gegenrechnung.py`) gegen dieselben Testfälle | KPI 01–09 | alle getroffen → Gegenrechnung bestätigt |
| App gegen Gegenrechnung, alle aktiven Ligen | Spielplan komplett + Stichprobe der Saison 2025/26 | 0 Abweichungen |
| Rundung, −0,00 → 0,00, Grenzen ±20,00 / ±35,00, eigene Schwellen | Formattests ohne Daten | bestanden |
| Schwellen-Datei `schwellen.toml` (Vorrang, Fehlermeldungen) | 13 Tests | bestanden |

Lokal: 252 bestanden, 9 übersprungen (8 Seitentests brauchen Streamlit, 1 Spielplan-Test gilt nur für den alten Stand). Auf dem Server laufen die 8 Seitentests mit: erwartet rund 260 bestanden, 1 übersprungen.

## 2. Einmaliger Vollvergleich (wie Etappe F)

Jedes Spiel der Datenbank als analysiertes Spiel (Stichtag = Spieldatum, Spieltag = `Gameday`) plus alle Begegnungen des Spielplans (Stichtag = `Datum von`). Verglichen je Begegnung: Formkurve, Spiele und Summen je Team, Ligareferenz, Hauptwert, Abweichung, Einstufung und „vorläufig“ für KPI 02–09, bei KPI 05–09 zusätzlich die gerundeten Team- und Ligawerte.

| Liga | Begegnungen | Abweichungen |
|---|---|---|
| Bundesliga | 1'863 | 0 |
| Premier League | 2'310 | 0 |
| Serie A | 2'310 | 0 |
| LaLiga | 2'325 | 0 |
| **Gesamt** | **8'808** | **0** |

## 3. Häufigkeit der Anomalien (Saison 2025/26, Anteil leicht / stark, Schwellen ±20 / ±35 %)

| Liga | KPI 02 | KPI 03 | KPI 04 | KPI 05 | KPI 06 | KPI 07 | KPI 08 | KPI 09 |
|---|---|---|---|---|---|---|---|---|
| Bundesliga | 12,83 / 1,64 | 26,64 / 32,89 | 19,08 / 3,62 | 1,97 / 0,00 | 21,38 / 6,91 | 19,74 / 4,93 | 17,11 / 5,92 | 3,95 / 0,00 |
| Premier League | 8,22 / 0,27 | 17,24 / 2,65 | 23,08 / 3,98 | 0,53 / 0,00 | 23,61 / 5,31 | 14,85 / 2,39 | 25,99 / 6,63 | 1,86 / 0,00 |
| Serie A | 11,94 / 0,27 | 8,75 / 0,53 | 16,71 / 5,57 | 1,06 / 0,00 | 20,16 / 4,77 | 18,30 / 4,24 | 20,95 / 13,26 | 0,80 / 0,00 |
| LaLiga | 14,59 / 0,80 | 13,53 / 4,77 | 20,42 / 4,51 | 0,80 / 0,27 | 27,06 / 13,79 | 20,16 / 2,65 | 23,34 / 15,12 | 2,12 / 0,27 |

Bewertung: KPI 02–04 unverändert gegenüber Etappe F. KPI 05 und 09 schlagen wie erwartet selten an, KPI 06 und 08 oft (besonders LaLiga und Serie A). Grundlage für die Schwellen-Analyse in Etappe I (Regelwerk, offene Punkte 12 und 17).

## 4. Darstellung (Stand 08.11.2026)

- Die echte App erzeugt dieselben Zahlen wie der abgenommene Design-Vorschlag (z. B. Stuttgart – FC Koln: 4,10 · +64,00 % · 4,20 · 10,45 · 1,80 · 2,30 · 85,00 % · 10,90).
- Top Anomalien über KPI 02–09: Atl. Madrid – Villarreal (KPI 06, +66,72 %), Stuttgart – FC Koln (KPI 03, +64,00 %), Sassuolo – Torino (KPI 08, +60,92 %), Bayer Leverkusen – Union Berlin (KPI 03, +52,00 %).
- Die Häufigkeit für alle vier Ligen braucht beim ersten Aufruf rund 30 Sekunden (danach aus dem Zwischenspeicher, bis sich die Datenbank ändert).

## 5. Was Carsten noch prüfen sollte

Nur die Darstellung im Browser (Desktop und Handy): Aufklappen einer Zeile, Lesbarkeit der Kärtchen, Top Anomalien, Schwellen im Bereich Datenqualität. Rechnerisch ist nichts offen.
