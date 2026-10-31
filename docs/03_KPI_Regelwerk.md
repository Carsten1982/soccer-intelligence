# Soccer Intelligence – KPI-Regelwerk

**Spezifikation v1.2** · Stand 31.10.2026

> **Massgebliche Quelle seit 31.10.2026.** Änderungen werden nur noch in dieser Datei gemacht, mit Datum in der Änderungshistorie bzw. im `CHANGELOG.md`.
> Das Word-Dokument „Definition der Dashboard-KPIs (final)“ (Arbeitsstand 30.10.2026) liegt nur noch als Archiv im Ordner `word/` und wird nicht mehr gepflegt.

Abschnitt 8 sammelt offene Punkte.

**Dies ist die einzige gültige md-Fassung des KPI-Regelwerks.** Sie ersetzt `03_KPI_Grundregeln.md` und den Ordner `docs/kpis/` (beide gelöscht am 30.10.2026). Weitere KPIs werden als neue Abschnitte in dieser Datei ergänzt.

**Änderungshistorie**

| Datum | Änderung | Abschnitt |
|---|---|---|
| 27.10.2026 | Erstfassung KPIs 01–04 | alle |
| 28.10.2026 | Ligareferenz über Spalte `Gameday` (letzte 20 Spieltage), Regel für Nachholspiele, fehlende Kartenwerte in Referenzspielen; offener Punkt 5 erledigt | 1.1, 6 |
| 30.10.2026 | Zeitlicher Abstand von 3 auf 2 Kalendertage reduziert, gilt nur für Teamwerte; offener Punkt 4 erledigt | 1 |
| 31.10.2026 | v1.2: Diese Datei ist die massgebliche Quelle, Word nur noch Archiv | Kopf |
| 30.10.2026 | v1.1: Stichtag = „Datum von“ aus dem Spielplan; Reihenfolge bei fehlenden Werten und Sortierung festgehalten; Rundung mit Dezimalarithmetik; Vorzeichen im Text „Keine Anomalie“; Auswahl der Top-Anomalien übernommen (bisher nur in `03_KPI_Grundregeln.md`); Spalten AC/AD für KPI 04; offene Punkte 1, 3 und 8 erledigt, neue Punkte 9 und 10 | 1, 2.3, 2.4, 2.6, 4, 5, 6, 8 |

Weitere KPIs werden im Projektverlauf ergänzt. Beispielrechnungen und Testfälle stehen in `docs/tests/test_kpi01_formkurve.md` bis `test_kpi04_gelbe_karten.md` (je zwei bestätigte Durchgänge: 1. Spieltag 2026/27 und 3. Spieltag 2025/26). Sie sind die verbindliche Referenz für die technische Umsetzung.

---

## 1. Allgemeine Daten- und Berechnungsregeln (gelten für alle KPIs)

| Regel | Festlegung |
|---|---|
| Spielauswahl | Nur **abgeschlossene Spiele derselben Liga**. Das analysierte Spiel selbst zählt nie mit. |
| Zeitfenster Teamwerte | Nur Ligaspiele aus der **Saison des analysierten Spiels und der Vorsaison**. Ältere Spiele werden nie nachgezogen. |
| Stichtag | Datum des analysierten Spiels ist **`Datum von`** aus dem Spielplan (`04_Spielplan.md`). In den Testfällen heisst dieser Wert „Analysedatum“. |
| Zeitlicher Abstand | Nur Spiele, die **mindestens 2 Kalendertage vor** dem Stichtag stattfanden. Beispiel: Spiel am Fr 30.10.2026 → Spiele bis einschliesslich Mi 28.10.2026. Spiele vom selben Tag oder vom Vortag zählen nie. Die Regel gilt für die **Teamwerte**, nicht für die Ligareferenz; diese wird ausschliesslich über die Spalte `Gameday` bestimmt (Abschnitt 1.1). |
| Keine Zukunftsdaten | Das analysierte Spiel und alle späteren Spiele fliessen weder in Teamwerte noch in die Ligareferenz ein. |
| Ergebnis | Massgeblich ist das **Ergebnis auf dem Platz**, nicht eine spätere Wertung am grünen Tisch (z. B. Union Berlin – Bochum, 14.12.2024: 1:1). |
| Fehlende Werte | Darstellung als „–“. **Niemals automatisch als 0** interpretieren. |
| Fehlender KPI-Wert in einem Spiel | Spiel wird für diesen KPI ausgelassen, **kein älteres Spiel nachgezogen**. Stichprobe sinkt (z. B. 9 statt 10) → „vorläufig“. Reihenfolge: **zuerst** die letzten 5 bzw. 10 Spiele bestimmen, **danach** Spiele ohne Wert entfernen. Ein Spiel ohne Ergebnis gilt nicht als abgeschlossen und zählt für keinen KPI. |
| Sortierung | Spiele eines Teams aufsteigend nach `Date`, dann Uhrzeit aus `matchDate`, dann `id`. „Die letzten N Spiele“ sind die N neuesten nach dieser Sortierung. |
| Standard-Stichprobe | KPI 01: 5 Spiele · KPI 02–04: 10 Spiele. |
| Kleinere Stichprobe | Mit tatsächlicher Anzahl rechnen, Stichprobengrösse **immer anzeigen**, KPI als **„vorläufig“** kennzeichnen. |
| Team 1 / Team 2 | Team 1 = **Heimteam**, Team 2 = **Auswärtsteam**. Im Dashboard werden die Teamnamen angezeigt. |

### 1.1 Ligareferenz

- Basis: die **letzten 20 Spieltage vor dem Spieltag des analysierten Spiels**.
- Massgeblich ist die Spieltagsnummer in der Spalte **`Gameday`**, nicht das Spieldatum.
- Die Referenz reicht **über das Saisonende hinweg**:

| Analysiertes Spiel | Bundesliga | Premier League |
|---|---|---|
| 1. Spieltag 2026/27 | Spieltage 15–34 (2025/26) | Spieltage 19–38 (2025/26) |
| 3. Spieltag 2026/27 | Spieltage 1–2 (2026/27) + 17–34 (2025/26) | Spieltage 1–2 (2026/27) + 21–38 (2025/26) |

- Berücksichtigt werden nur **abgeschlossene** Spiele, also Spiele, die mit Ergebnis in der Datenbank stehen und vor dem Stichtag stattfanden.
- Ein **Nachholspiel** zählt zu seinem ursprünglichen Spieltag. Ist es zum Zeitpunkt der Analyse noch nicht gespielt, fehlt es in der Referenz und wird **nicht ersetzt**.
- Geteilt wird durch die **tatsächliche Anzahl** berücksichtigter Partien (im Normalfall 20 × Teams / 2, also 180 in der Bundesliga und 200 in der Premier League).
- Ist die Ligareferenz nicht vorhanden oder = 0 → **keine relative Abweichung, keine Anomalie-Einstufung**.

---

## 2. Anomalie-Einstufung (KPI 02–04)

### 2.1 Relative Abweichung

```
Relative Abweichung = (KPI-Wert der Begegnung − Referenzwert) / Referenzwert × 100
```

| KPI | Referenzwert |
|---|---|
| KPI 02 | Ligareferenz |
| KPI 03 | fester Wert 2,5 Tore pro Spiel |
| KPI 04 | Ligareferenz |

Negativ = unter dem Referenzwert, positiv = darüber.

### 2.2 Schwellenwerte (symmetrisch, nach Betrag)

| Gerundete Abweichung | Einstufung |
|---|---|
| −20,0 % bis +20,0 % (inkl.) | keine Anomalie |
| < −20,0 % bis −35,0 % (inkl.) / > +20,0 % bis +35,0 % (inkl.) | leichte Anomalie |
| < −35,0 % / > +35,0 % | starke Anomalie |

- Grenzfälle: genau ±20,0 % = keine Anomalie · genau ±35,0 % = leichte Anomalie.
- KPI 01 erhält **keine** Anomalie-Einstufung.
- Die Werte sind operative Startwerte und werden später anhand historischer Daten überprüft. Künftig sind auch KPI-spezifische Schwellenwerte möglich.

### 2.3 Rundung

- Gerechnet wird **immer mit ungerundeten Werten**.
- Erst das Endergebnis wird auf **eine Nachkommastelle** gerundet, kaufmännisch (ab ,5 aufrunden).
- Die Einstufung erfolgt anhand der **gerundeten** Abweichung. Beispiel: +20,04 % → +20,0 % → keine Anomalie.
- Technisch mit **Dezimalarithmetik** (Python `decimal`, `ROUND_HALF_UP`), **nicht** mit `round()`. Grund: `round()` rundet 4,35 auf 4,3 und 2,65 auf 2,6. Richtig ist 4,4 und 2,7.
- Weitergerechnet wird mit dem ungerundeten Wert. Beispiel KPI 03: gemeinsamer Teamdurchschnitt 4,35 → Anzeige 4,4, die Abweichung wird mit 4,35 berechnet (+74,0 %), nicht mit 4,4 (+76,0 %).

### 2.4 Vorzeichen

- **Frontend-Texte** mit „mehr / weniger / über / unter“: Abweichung **ohne Vorzeichen** („16,7 % über dem Liga-Durchschnitt“).
- **Kennzahlenfelder**: Vorzeichen **immer** anzeigen („−25,0 %“).
- **Frontend-Texte ohne „mehr / weniger / über / unter“** (Fall „Keine Anomalie“ bei KPI 02 und KPI 04): Vorzeichen **immer** anzeigen („Die Abweichung vom Liga-Durchschnitt beträgt +7,0 %.“ bzw. „… −8,9 %.“). Ohne Vorzeichen wäre die Richtung nicht erkennbar.
- Bei genau **0,0 %** steht nie ein Vorzeichen.
- Als Minuszeichen wird „−“ (U+2212) verwendet, nicht der Bindestrich „-“.

### 2.5 Einheitlicher Aufbau der KPI-Karten (ab KPI 02)

1. Hauptwert
2. Anomalie-Einstufung (keine / leicht / stark) und Richtung (positiv / negativ)
3. Relative Abweichung in Prozent
4. Referenzwert und beide Teamwerte
5. Datenbasis: Anzahl Spiele je Team, ggf. „vorläufig“
6. Überschrift und Erklärungssatz

Schwellenwerte, Rundung, Vorzeichen und die Regeln für fehlende Daten werden **zentral** umgesetzt und gelten für alle KPIs.

### 2.6 Auswahl der Top-Anomalien (ligaübergreifend)

**Zweck:** Legt fest, welche Begegnungen des aktuellen Spieltags im Bereich „Top Anomalien“ (`/dashboard`) und später auf der Startseite der öffentlichen Website erscheinen. Die Auswahl erfolgt **zentral in der Berechnungslogik**, nicht im Frontend.

**Grundlage:**
- Begegnungen des aktuellen Spieltags aller aktiven Ligen (aktueller Spieltag gemäss `04_Spielplan.md`, Abschnitt 4).
- Vorerst nur **KPI 02** und **KPI 04** mit leichter oder starker Anomalie.
- KPI 03 ist vorerst ausgeschlossen, weil seine Schwellenwerte noch überprüft werden. Aufnahme erst nach separater Prüfung und Freigabe.
- KPI 01 hat keine Anomalie-Einstufung und wird nicht berücksichtigt.

**Ausschlüsse:**
- Vorläufige KPI-Werte
- Begegnungen mit Status „verschoben“ oder „abgesagt“
- Begegnungen ohne Anomalie

**Rangfolge und Auswahl:**
1. Starke Anomalien vor leichten.
2. Innerhalb derselben Stufe: grösserer Betrag der (gerundeten) relativen Abweichung zuerst.
3. Bei Gleichstand: früheres Spieldatum (`Datum von`).
4. Danach: Reihenfolge der Begegnungen in der Spielplan-Datei.
5. Pro Begegnung höchstens ein Eintrag. Haben KPI 02 und KPI 04 derselben Begegnung eine Anomalie, zählt nur der KPI mit dem höheren Rang.
6. Höchstens vier Einträge. Gibt es weniger, werden nur diese angezeigt. Die Liste wird nicht aufgefüllt.

**Keine Anomalien:** Hinweis „Für den aktuellen Spieltag liegen keine Anomalien vor.“

**Gültigkeit:** gilt für das interne Dashboard und die spätere öffentliche Website.

---

## 3. KPI 01 – Formkurve (letzte 5 Spiele)

**Zweck:** Rein beschreibender Formindikator. Keine Ligareferenz, keine Anomalie.

**Berechnung:** Je Team die letzten 5 abgeschlossenen Ligaspiele, Ergebnis aus Sicht des Teams: S (Sieg), U (Unentschieden), N (Niederlage).

**Darstellung:**
- Je Team eine Reihe mit bis zu 5 Markierungen, sortiert **vom ältesten zum neuesten** Spiel.
- Farben: Sieg grün · Unentschieden grau · Niederlage rot.
- Fehlende Positionen als „–“ in neutraler Farbe, **nicht als Niederlage** werten.
- Tatsächlich verfügbare Anzahl anzeigen.

```
VfB Stuttgart        🟢 S · 🟢 S · ⚪ U · 🔴 N · 🟢 S
FC Bayern München    🟢 S · 🟢 S · 🟢 S · 🟢 S · ⚪ U
Aufsteiger           – · – · – · 🟢 S · 🔴 N   (2 von 5 Spielen)
```

**Sonderfälle:**
- 1–4 Spiele verfügbar: fehlende Positionen als „–“.
- Keine Ligaspiele verfügbar (z. B. Aufsteiger): 5 × „–“. Ergebnisse aus tieferen Ligen werden nicht übernommen.

---

## 4. KPI 02 – Erwartete Tore (Gesamtspiel)

**Stichprobe:** letzte 10 Ligaspiele je Team.

```
Teamdurchschnitt Team X = Summe aller Tore (beider Mannschaften) in den Spielen von Team X
                          / Anzahl berücksichtigter Spiele von Team X

Torindikator der Begegnung = (Teamdurchschnitt Team 1 + Teamdurchschnitt Team 2) / 2

Ligareferenz = Summe aller Tore in den Referenzpartien / Anzahl Referenzpartien

Relative Abweichung = (Torindikator − Ligareferenz) / Ligareferenz × 100
```

**Anomalie:** gemäss Abschnitt 2.2.

**Hinweis:** Kein xG-Modell und keine präzise Prognose der Torzahl. Angriffs-/Abwehrstärke und Chancenqualität werden nicht direkt berücksichtigt.

**Dashboard:**
- Hauptwert: Torindikator, beschriftet „Torpotenzial der Begegnung“
- Team 1 / Team 2: Ø Gesamttore pro Spiel des Heim- bzw. Auswärtsteams
- Ligareferenz: Ø Gesamttore pro Ligaspiel im Referenzzeitraum
- Abweichung in %, Datenbasis (Spiele je Team, ggf. „vorläufig“), Anomalie

**Frontend-Texte:**

| Fall | Überschrift | Beschreibung |
|---|---|---|
| Keine Anomalie | Keine statistische Besonderheit | In dieser Partie liegt der Torindikator bei durchschnittlich {Hauptwert} Toren. Die Abweichung vom Liga-Durchschnitt beträgt {Abweichung} %. *({Abweichung} mit Vorzeichen, siehe 2.4)* |
| Positiv | Viele Tore erwartet | In dieser Partie liegt der Torindikator bei durchschnittlich {Hauptwert} Toren. Das sind {Abweichung} % mehr als im Liga-Durchschnitt. |
| Negativ | Wenige Tore erwartet | In dieser Partie liegt der Torindikator bei durchschnittlich {Hauptwert} Toren. Das sind {Abweichung} % weniger als im Liga-Durchschnitt. |

Die Einstufung „leichte“ / „starke Anomalie“ wird zusätzlich separat angezeigt.

**Sonderfälle:**
- Weniger als 10 Spiele: alle verfügbaren nutzen → „vorläufig“.
- Ein Team ohne Ligaspiele: **kein Torindikator**. Der Wert des Gegners darf nicht allein ausgegeben werden.
- Ligareferenz fehlt oder = 0: keine Abweichung, keine Anomalie.

---

## 5. KPI 03 – Over 2.5 Goals

**Zweck:** Zeigt, wie stark der durchschnittliche Gesamttorwert beider Teams über oder unter der festen Marke von **2,5 Toren** liegt. Keine Wahrscheinlichkeit für „mehr als 2,5 Tore“.

**Stichprobe:** letzte 10 Ligaspiele je Team.

```
Teamdurchschnitt Team X  = Summe aller Tore in den Spielen von Team X / Anzahl Spiele
Teamabweichung Team X    = (Teamdurchschnitt Team X − 2,5) / 2,5 × 100

Gemeinsamer Teamdurchschnitt   = (Teamdurchschnitt Team 1 + Teamdurchschnitt Team 2) / 2
Gemeinsame Over-2.5-Abweichung = (Gemeinsamer Teamdurchschnitt − 2,5) / 2,5 × 100
```

**Beispiel:** Team 1 = 3,0 · Team 2 = 2,0 → Teamabweichungen +20 % / −20 % → gemeinsam 2,5 → Abweichung 0 %.

**Anomalie:** gemäss Abschnitt 2.2, auf Basis der gemeinsamen Over-2.5-Abweichung.

**Dashboard:**
- Hauptwert: gemeinsamer Teamdurchschnitt (Tore pro Spiel, z. B. 3,10)
- Referenzwert: 2,5 Tore pro Spiel
- Team 1 / Team 2: Teamdurchschnitt, in Klammern die Abweichung zur 2,5-Marke
- Relative Abweichung, Datenbasis, Anomalie
- Richtung und Stärke der Anomalie müssen getrennt erkennbar sein.

**Frontend-Texte:**

| Fall | Überschrift | Beschreibung |
|---|---|---|
| Keine Anomalie | Keine statistische Besonderheit | In den bisherigen Spielen erzielten die beiden Teams im Schnitt {Abweichung} % mehr/weniger Tore als die 2,5-Tore-Marke. |
| Positiv | Über 2,5 Goals erwartet | In den bisherigen Spielen beider Teams fielen im Schnitt {Abweichung} % mehr Tore als die 2,5-Tore-Marke. |
| Negativ | Unter 2,5 Goals erwartet | In den bisherigen Spielen beider Teams fielen im Schnitt {Abweichung} % weniger Tore als die 2,5-Tore-Marke. |

**Sonderfälle:**
- Weniger als 10 Spiele: alle verfügbaren nutzen → „vorläufig“.
- Ein Team ohne Ligaspiele: **kein gemeinsamer Over-2.5-Wert**.

**Abgrenzung zu KPI 02:** Gleiche Datenbasis (Ø Gesamttore beider Teams), aber unterschiedliche Referenz: KPI 02 vergleicht mit dem Ligadurchschnitt, KPI 03 mit der festen Marke 2,5.

---

## 6. KPI 04 – Gelbe Karten

**Stichprobe:** letzte 10 Ligaspiele je Team.

```
Teamdurchschnitt Team X  = Summe der gelben Karten, die Team X SELBST erhalten hat / Anzahl Spiele

Erwartete gelbe Karten   = Teamdurchschnitt Team 1 + Teamdurchschnitt Team 2   (Summe, nicht Durchschnitt!)

Ligareferenz             = Summe gelber Karten beider Teams in allen Referenzspielen / Anzahl Referenzspiele
                           (Referenzspiele gemäss Abschnitt 1.1, letzte 20 Spieltage laut `Gameday`)

Relative Abweichung      = (Erwartete gelbe Karten − Ligareferenz) / Ligareferenz × 100
```

**Zählregeln:**
- Nur **eigene** gelbe Karten des Teams, gegnerische Karten zählen nicht.
- Datenquelle: Spalte **AC „Home Yellow Cards Full Time“**, wenn das Team Heimteam ist, Spalte **AD „Away Yellow Cards Full Time“**, wenn es Auswärtsteam ist.
- Zählweise der Quelle wird **unverändert übernommen** (auch bei Gelb-Rot, Ersatzspielern, Offiziellen).
- **Rote Karten zählen nicht.**
- Neue Datenquellen müssen vorab auf gleiche Zählweise geprüft werden.

**Anomalie:** gemäss Abschnitt 2.2.

**Dashboard:**
- Hauptwert: erwartete gelbe Karten (Summe beider Teamdurchschnitte)
- Team 1 / Team 2: Ø eigene gelbe Karten pro Spiel
- Ligareferenz: Ø gelbe Karten pro Ligaspiel im Referenzzeitraum
- Abweichung in %, Anomalie (sofern berechenbar)
- Datenbasis: Spiele je Team **und** Anzahl Referenzspiele

**Beispiel (fiktiv):** Stuttgart 2,4 + Bayern 1,8 = 4,2 · Liga 3,6 → (4,2 − 3,6) / 3,6 × 100 = +16,7 % → keine Anomalie.

**Frontend-Texte:**

| Fall | Überschrift | Beschreibung |
|---|---|---|
| Keine Anomalie | Keine statistische Besonderheit | Der Kartenindikator dieser Begegnung liegt bei {Hauptwert} gelben Karten. Die Abweichung vom Liga-Durchschnitt beträgt {Abweichung} %. *({Abweichung} mit Vorzeichen, siehe 2.4)* |
| Positiv | Überdurchschnittlich viele gelbe Karten | In dieser Partie werden {Hauptwert} gelbe Karten erwartet. Das liegt {Abweichung} % über dem Liga-Durchschnitt. |
| Negativ | Unterdurchschnittlich viele gelbe Karten | In dieser Partie werden {Hauptwert} gelbe Karten erwartet. Das liegt {Abweichung} % unter dem Liga-Durchschnitt. |

**Sonderfälle:**
- Weniger als 10 Spiele: alle verfügbaren nutzen → „vorläufig“.
- Ein Team ohne Ligaspiele: Hauptwert, Abweichung und Anomalie **nicht verfügbar**.
- Aufsteiger ab 1 abgeschlossenem Ligaspiel: Berechnung mit verfügbaren Spielen → „vorläufig“.
- Fehlender Kartenwert in einem Spiel: Spiel auslassen, nicht nachziehen → „vorläufig“.
- Fehlender Kartenwert in einem Referenzspiel (z. B. Union Berlin – Bochum, 14.12.2024): Spiel wird für die Ligareferenz ausgelassen.
- Kein statistisches Prognosemodell, keine weiteren Einflussfaktoren.

---

## 7. Übersicht der KPI-Unterschiede

| | KPI 01 | KPI 02 | KPI 03 | KPI 04 |
|---|---|---|---|---|
| Stichprobe | 5 | 10 | 10 | 10 |
| Teamwert | S/U/N | Ø Gesamttore | Ø Gesamttore | Ø eigene Gelbe |
| Verknüpfung | – | Durchschnitt | Durchschnitt | **Summe** |
| Referenz | keine | Liga | 2,5 fix | Liga |
| Anomalie | nein | ja | ja | ja |

---

## 8. Offene Punkte / Unstimmigkeiten im Quelldokument

Diese Punkte sollten vor der Umsetzung im Code geklärt werden:

1. ~~**KPI 03 Frontend-Texte:** `{Hauptwert} %` statt `{Abweichung} %`.~~ **Erledigt am 30.10.2026:** `{Abweichung}` gilt. Im Word als Änderung markiert, mit deren Annahme abgeschlossen.
2. **KPI 03 „Keine Anomalie“ bei 0,0 %:** Der Satz „mehr/weniger“ passt nicht, wenn die Abweichung genau 0,0 % beträgt. Dafür fehlt ein eigener Text.
3. ~~**KPI 02 Fall A, Hinweis und Vorzeichen:** Hinweis stammte aus KPI 03; Vorzeichen im Text „Keine Anomalie“ ungeklärt.~~ **Erledigt am 30.10.2026:** Hinweis im Word ersetzt. Im Text „Keine Anomalie“ (KPI 02 und KPI 04) steht das Vorzeichen immer, bei 0,0 % keins (Abschnitt 2.4). Testfall KPI 02 PL-1 entsprechend auf „+7,0 %“ angepasst.
4. ~~**3-Tage-Regel:** Ligaspiele unter der Woche, Geltung für die Ligareferenz.~~ **Erledigt am 30.10.2026:** auf 2 Kalendertage reduziert (Spiele unter der Woche und dichte Spielpläne, z. B. Premier League über Weihnachten, zählen mit); gilt nur für Teamwerte, nicht für die Ligareferenz. Siehe Abschnitt 1.
5. ~~**Ligareferenz in KPI 04:** Definition der letzten 20 Spieltage.~~ **Erledigt am 28.10.2026:** einheitlich über Spalte `Gameday` geregelt, siehe Abschnitt 1.1.
6. **Rundung der Teamabweichungen (KPI 03):** Werden auch diese auf eine Nachkommastelle gerundet angezeigt? Vermutlich ja, sollte aber explizit stehen.
7. **Datenquelle KPI 04:** Der Name der Datenquelle (im Word-Archiv als Platzhalter „[Name der Quelle]“) ist noch nicht dokumentiert. Bei Bedarf in Abschnitt 6 ergänzen. Für die Berechnung nicht relevant.
8. ~~**Überschrift KPI 03 negativ:** „Unter 2.5 Goals“ statt „2,5“.~~ **Erledigt am 30.10.2026:** „2,5“ gilt, im Word als Änderung markiert.
9. **KPI 03 Nachkommastellen Hauptwert:** Das Beispiel „3,10“ hat zwei Nachkommastellen, die allgemeine Regel eine. Die Testfälle verwenden eine (z. B. 4,4). Bitte bestätigen. Abweichung und Einstufung ändern sich dadurch nicht.
10. **KPI-Karte bei Aufsteiger-Spielen (KPI 02–04):** Die Testfälle nehmen an: Teamwert des Gegners und Ligareferenz werden angezeigt, Hauptwert, Abweichung und Anomalie als „–“. Bitte bestätigen.

Für die Umsetzung blockierend ist keiner dieser Punkte: Die Testfälle legen für 2, 6, 9 und 10 jeweils eine Annahme fest. Wird eine Annahme geändert, sind die betroffenen Testfälle anzupassen.

**Umsetzung (Etappe C, 31.10.2026):** so wie in den Testfällen angenommen. Punkt 2: Bei genau 0,0 % zeigt KPI 03 nur die Überschrift „Keine statistische Besonderheit“, ohne Satz, bis ein Text festgelegt ist. Punkte 6 und 9: eine Nachkommastelle. Punkt 10: Gegnerwert und Ligareferenz sichtbar, Hauptwert, Abweichung und Anomalie „–“.
