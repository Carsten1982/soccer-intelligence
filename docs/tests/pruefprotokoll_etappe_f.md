# Prüfprotokoll Etappe F – Vier Ligen

**Datum:** 07.11.2026 · **Geprüft von:** Claude · **Datenbank:** SHA-256 `f37e36d3…` · **Spielplan:** Stand 07.11.2026 (Spieltage 1–2, vier Blätter)

Ziel: Serie A und LaLiga so gründlich prüfen, dass Carsten nur noch dort selbst nachrechnen muss, wo es unbedingt nötig ist.

---

## 1. Unabhängige Gegenrechnung (Kern der Prüfung)

Die KPIs 01–04 wurden ein **zweites Mal** programmiert (`tests/gegenrechnung.py`), direkt aus dem Text von `03_KPI_Regelwerk.md`. Die Gegenrechnung verwendet **keinen** Code der App: Sie liest die Excel-Datei selbst (openpyxl), rechnet mit reinem Python und exakten Brüchen und rundet mit `ROUND_HALF_UP`.

| Schritt | Umfang | Ergebnis |
|---|---|---|
| Gegenrechnung gegen die bestätigten Testfälle (`docs/tests`, Referenz-Datenbank) | alle Testfälle KPI 01–04 (Bundesliga, Premier League) | **alle getroffen** → Gegenrechnung bestätigt |
| App gegen Gegenrechnung, **jedes Spiel der Datenbank** als analysiertes Spiel (Stichtag = Spieldatum, Spieltag = `Gameday`) plus alle Begegnungen des Spielplans (Stichtag = `Datum von`) | Bundesliga 1'863 · Premier League 2'310 · **Serie A 2'310 · LaLiga 2'325** = 8'808 Begegnungen | **0 Abweichungen** |

Verglichen wurden je Begegnung: Formkurve beider Teams, Anzahl Spiele und Summe (Tore, Karten) je Team, Ligareferenz (Spiele, Summe) für Tore und Karten, Hauptwert, Abweichung, Anomalie-Einstufung und „vorläufig“ für KPI 02, 03 und 04.

**Dauerhaft im Testlauf:** `tests/test_gegenrechnung.py` wiederholt den Vergleich bei jedem Einspielen für alle aktiven Ligen (Spielplan komplett + Stichprobe der letzten abgeschlossenen Saison). Gegenprobe: Mit absichtlich falscher 2-Tage-Regel (1 statt 2 Tage) schlägt der Test an.

## 2. Plausibilität der Daten

Durchschnitt je Spiel (abgeschlossene Saisons 2020/21–2025/26):

| Liga | Tore | Over 2,5 | Heimsiege | Remis | Gelbe Karten |
|---|---|---|---|---|---|
| Bundesliga | 3,03–3,24 | 58–64 % | 39–47 % | 24–27 % | 3,3–4,1 |
| Premier League | 2,69–3,28 | 50–65 % | 38–48 % | 22–27 % | 2,9–4,4 |
| Serie A | 2,43–3,05 | 46–57 % | 39–42 % | 26–30 % | 3,7–4,5 |
| LaLiga | 2,50–2,69 | 44–50 % | 42–49 % | 23–29 % | 4,3–5,0 |

Bewertung: plausibel (Serie A und LaLiga torärmer als die Bundesliga, LaLiga mit den meisten Karten). Fehlende Kartenwerte nur bei den dokumentierten Nachträgen (Union – Bochum, Verona – Roma).

Weitere Datenprüfungen (alle 8'730 Spiele): jede Saison 306 bzw. 380 Spiele, jedes Team genau einmal je Spieltag, Endergebnis K–M = N–P, Halbzeiten ergeben das Endergebnis, Ergebnisbuchstabe passt. Offen bleiben 4 kleine Warnungen „Schüsse < aufs Tor + daneben“ (Quelle).

## 3. Häufigkeit der Anomalien (Saison 2025/26)

| Liga | KPI 02 leicht/stark | KPI 03 leicht/stark | KPI 04 leicht/stark |
|---|---|---|---|
| Bundesliga | 12,8 % / 1,6 % | 26,6 % / 32,9 % | 19,1 % / 3,6 % |
| Premier League | 8,2 % / 0,3 % | 17,2 % / 2,7 % | 23,1 % / 4,0 % |
| Serie A | 11,9 % / 0,3 % | 8,8 % / 0,5 % | 16,7 % / 5,6 % |
| LaLiga | 14,6 % / 0,8 % | 13,5 % / 4,8 % | 20,4 % / 4,5 % |

Bewertung: KPI 02 und 04 schlagen in den neuen Ligen ähnlich oft an wie bisher. KPI 03 seltener, weil Serie A und LaLiga nahe an der festen 2,5-Tore-Marke liegen. Die Schwellen bleiben unverändert (offener Punkt 11 im Regelwerk).

## 4. Aktueller Spieltag und Sonderfälle (Stand 07.11.2026)

- Alle vier Ligen zeigen Spieltag 2 der Saison 2026/27 (letzter Spieltag im Spielplan).
- Ligareferenz Spieltag 2: Saison 2025/26 Spieltage 20–38 + 2026/27 Spieltag 1. Serie A: 200 Spiele, 500 Tore (genau 2,50; daher glatte Abweichungen). LaLiga: 196 Spiele, weil 4 Spiele des 1. Spieltags erst nach dem Stichtag gespielt wurden (Regel „vor dem Stichtag“).
- **Aufsteiger** (nur 1 Spiel 2026/27, „vorläufig“, nicht in den Top Anomalien): Serie A Frosinone, Monza, Venezia; LaLiga Racing Santander, Dep. A Coruna, Malaga.
- **Malaga – Dep. A Coruna:** 0 Spiele für Malaga. Grund: Stichtag ist „Datum von“ des Spieltags 2 (20.08.), Malagas erstes Spiel war am 19.08. (2-Tage-Regel). Folge der Zeitraum-Pflege bei LaLiga, kein Rechenfehler.
- Top Anomalien über vier Ligen: Juventus – Parma (KPI 02, −30,0 %), Cagliari – Inter (KPI 02, +26,0 %), Crystal Palace – Manchester City und Aston Villa – Arsenal (KPI 04, je −25,9 %).

## 5. Was Carsten noch prüfen sollte (nur wenn gewünscht)

Rechnerisch ist nichts offen. Sinnvoll wäre höchstens eine kurze **fachliche** Sichtprüfung im Browser: Stimmen Teamnamen und Spieltage der Serie A und LaLiga mit dem echten Spielplan überein? Das kann keine Rechnung prüfen.
