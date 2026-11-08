# Soccer Intelligence – KPI-Regelwerk

**Spezifikation v2.3** · Stand 08.11.2026 · KPI 01–09 gültig und umgesetzt (KPI 05–09, zwei Nachkommastellen und Top-Anomalien über KPI 02–09 seit Etappe H, eingespielt 08.11.2026) · KPI 10–13 Entwurf (Abschnitt 10)

> **Massgebliche Quelle seit 31.10.2026.** Änderungen werden nur noch in dieser Datei gemacht, mit Datum in der Änderungshistorie bzw. im `CHANGELOG.md`.
> Das Word-Dokument „Definition der Dashboard-KPIs (final)“ (Arbeitsstand 30.10.2026) liegt nur noch als Archiv im Ordner `word/` und wird nicht mehr gepflegt.

Abschnitt 8 sammelt offene Punkte.

**Dies ist die einzige gültige md-Fassung des KPI-Regelwerks.** Sie ersetzt `03_KPI_Grundregeln.md` und den Ordner `docs/kpis/` (beide gelöscht am 30.10.2026). Weitere KPIs werden als neue Abschnitte in dieser Datei ergänzt.

**Änderungshistorie**

| Datum | Änderung | Abschnitt |
|---|---|---|
| 27.10.2026 | Erstfassung KPIs 01–04 | alle |
| 08.11.2026 | **v2.3** (Etappe I.1): Ergebniskontrolle und Simulation festgelegt; offener Punkt 13 erledigt | 8, 11 |
| 08.11.2026 | **v2.2** (H.1): Ein Statistikwert mit Kommastellen (z. B. 4,5 Ecken) gilt als **fehlend** und wird nie abgeschnitten; die Datenprüfung meldet ihn als Warnung. Keine Änderung an Formeln oder Testfällen | 1 |
| 28.10.2026 | Ligareferenz über Spalte `Gameday` (letzte 20 Spieltage), Regel für Nachholspiele, fehlende Kartenwerte in Referenzspielen; offener Punkt 5 erledigt | 1.1, 6 |
| 30.10.2026 | Zeitlicher Abstand von 3 auf 2 Kalendertage reduziert, gilt nur für Teamwerte; offener Punkt 4 erledigt | 1 |
| 31.10.2026 | v1.2: Diese Datei ist die massgebliche Quelle, Word nur noch Archiv | Kopf |
| 08.11.2026 | v2.0 (Entwurf): neue Frontend-KPIs 05–09 (Ecken, Tore 1. HZ, Tore 2. HZ, Beide Teams treffen, Schüsse aufs Tor) und Simulations-KPIs 10–13 (nur Backend) nach Carstens Spezifikation „KPI05-13 Entwurf“ und den Entscheidungen vom 08.11.2026; Schwellen pro Liga und KPI einstellbar (Standard ±20/±35 %); Regel „−0,0 → 0,0“; Datenbasis mit Referenzspielen bei KPIs mit möglichen Lücken; neue offene Punkte 12–14 | 2.2, 2.4, 2.5, 2.6, 7, 8, 9, 10 |
| 08.11.2026 | **v2.1:** Testfälle KPI 05–09 bestätigt (Carsten). **Alle Werte mit zwei Nachkommastellen**, auch die Abweichung; Einstufung nach der auf zwei Stellen gerundeten Abweichung; Testfälle KPI 02–09 angepasst (keine Einstufung ändert sich). **Top-Anomalien über KPI 02–09** mit der bisherigen Rangfolge, Gewichtung später (Punkt 17). Offene Punkte 6 und 9 erledigt | 2.1–2.4, 2.6, 7, 8, 9 |
| 08.11.2026 | KPI 09 bleibt unverändert (Carsten, Rundgang); Gegenprobe eigene gegen eigene + gegnerische Schüsse festgehalten; Testfälle KPI 09 ergänzt um T23–T24 | 9.5 |
| 08.11.2026 | KPI 08 bleibt unverändert (Carsten, Rundgang); Variante „Angriff gegen Abwehr“ als offener Punkt 16 für Etappe I; Testfälle KPI 07 und 08 ergänzt um T18–T22 | 8 |
| 08.11.2026 | KPI 06 und 07: Hauptwert, Teamwerte und Ligareferenz mit zwei Nachkommastellen (Carsten, Rundgang); Abweichung weiter eine Nachkommastelle; Website offen (Punkt 15); Testfälle KPI 06 ergänzt um T15–T17 | 2.3, 8, 9.2, 9.3 |
| 08.11.2026 | KPI 05 und 09 nach dem gemeinsamen Rundgang umgestellt (Carsten): Teamwert zählt eigene **und** gegnerische Ecken bzw. Schüsse aufs Tor, Hauptwert = Mittelwert der Teamwerte (System wie KPI 02); Testfälle neu, ergänzt um T10–T14; Häufigkeit in Punkt 12 aktualisiert | 7, 8, 9.1, 9.5 |
| 07.11.2026 | v1.3: Regeln gelten unverändert für vier Ligen (Serie A, LaLiga ergänzt); Ligareferenz-Tabelle erweitert; Schwellen nach dem Einschalten pro Liga mit „Häufigkeit der Anomalien“ prüfen | 1.1, 8 |
| 30.10.2026 | v1.1: Stichtag = „Datum von“ aus dem Spielplan; Reihenfolge bei fehlenden Werten und Sortierung festgehalten; Rundung mit Dezimalarithmetik; Vorzeichen im Text „Keine Anomalie“; Auswahl der Top-Anomalien übernommen (bisher nur in `03_KPI_Grundregeln.md`); Spalten AC/AD für KPI 04; offene Punkte 1, 3 und 8 erledigt, neue Punkte 9 und 10 | 1, 2.3, 2.4, 2.6, 4, 5, 6, 8 |

Weitere KPIs werden im Projektverlauf ergänzt. Beispielrechnungen und Testfälle stehen in `docs/tests/test_kpi01_formkurve.md` bis `test_kpi04_gelbe_karten.md` (je zwei bestätigte Durchgänge: 1. Spieltag 2026/27 und 3. Spieltag 2025/26). Sie sind die verbindliche Referenz für die technische Umsetzung. Für KPI 05–09: `test_kpi05_ecken.md` bis `test_kpi09_schuesse_aufs_tor.md` (je 9 gemeinsame Testfälle T1–T9 und zusätzlich die Partien aus dem gemeinsamen Rundgang T10–T24, **bestätigt am 08.11.2026**).

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
| Fehlende Werte | Darstellung als „–“. **Niemals automatisch als 0** interpretieren. Ein Wert mit Kommastellen in einer Spalte mit Anzahlen (Ecken, Karten, Schüsse) gilt ebenfalls als fehlend: Er wird **nie abgeschnitten** (aus 4,5 wird nicht 4); die Datenprüfung meldet eine Warnung (seit H.1, 08.11.2026). Bei Toren, `Gameday` und `id` ist eine Kommazahl ein Fehler und sperrt die Datenbank. |
| Fehlender KPI-Wert in einem Spiel | Spiel wird für diesen KPI ausgelassen, **kein älteres Spiel nachgezogen**. Stichprobe sinkt (z. B. 9 statt 10) → „vorläufig“. Reihenfolge: **zuerst** die letzten 5 bzw. 10 Spiele bestimmen, **danach** Spiele ohne Wert entfernen. Ein Spiel ohne Ergebnis gilt nicht als abgeschlossen und zählt für keinen KPI. |
| Sortierung | Spiele eines Teams aufsteigend nach `Date`, dann Uhrzeit aus `matchDate`, dann `id`. „Die letzten N Spiele“ sind die N neuesten nach dieser Sortierung. |
| Standard-Stichprobe | KPI 01: 5 Spiele · KPI 02–04: 10 Spiele. |
| Kleinere Stichprobe | Mit tatsächlicher Anzahl rechnen, Stichprobengrösse **immer anzeigen**, KPI als **„vorläufig“** kennzeichnen. |
| Team 1 / Team 2 | Team 1 = **Heimteam**, Team 2 = **Auswärtsteam**. Im Dashboard werden die Teamnamen angezeigt. |

### 1.1 Ligareferenz

- Basis: die **letzten 20 Spieltage vor dem Spieltag des analysierten Spiels**.
- Massgeblich ist die Spieltagsnummer in der Spalte **`Gameday`**, nicht das Spieldatum.
- Die Referenz reicht **über das Saisonende hinweg**:

| Analysiertes Spiel | Bundesliga | Premier League, Serie A, LaLiga (je 38 Spieltage) |
|---|---|---|
| 1. Spieltag 2026/27 | Spieltage 15–34 (2025/26) | Spieltage 19–38 (2025/26) |
| 3. Spieltag 2026/27 | Spieltage 1–2 (2026/27) + 17–34 (2025/26) | Spieltage 1–2 (2026/27) + 21–38 (2025/26) |

- Berücksichtigt werden nur **abgeschlossene** Spiele, also Spiele, die mit Ergebnis in der Datenbank stehen und vor dem Stichtag stattfanden.
- Ein **Nachholspiel** zählt zu seinem ursprünglichen Spieltag. Ist es zum Zeitpunkt der Analyse noch nicht gespielt, fehlt es in der Referenz und wird **nicht ersetzt**.
- Geteilt wird durch die **tatsächliche Anzahl** berücksichtigter Partien (im Normalfall 20 × Teams / 2, also 180 in der Bundesliga und 200 in Premier League, Serie A und LaLiga).
- Ist die Ligareferenz nicht vorhanden oder = 0 → **keine relative Abweichung, keine Anomalie-Einstufung**.

---

## 2. Anomalie-Einstufung (KPI 02–09)

### 2.1 Relative Abweichung

```
Relative Abweichung = (KPI-Wert der Begegnung − Referenzwert) / Referenzwert × 100
```

| KPI | Referenzwert |
|---|---|
| KPI 02 | Ligareferenz |
| KPI 03 | fester Wert 2,5 Tore pro Spiel |
| KPI 04 | Ligareferenz |
| KPI 05–09 | Ligareferenz des jeweiligen KPI (Abschnitt 9) |

Negativ = unter dem Referenzwert, positiv = darüber.

### 2.2 Schwellenwerte (symmetrisch, nach Betrag)

| Gerundete Abweichung | Einstufung |
|---|---|
| −20,00 % bis +20,00 % (inkl.) | keine Anomalie |
| < −20,00 % bis −35,00 % (inkl.) / > +20,00 % bis +35,00 % (inkl.) | leichte Anomalie |
| < −35,00 % / > +35,00 % | starke Anomalie |

- Grenzfälle: genau ±20,00 % = keine Anomalie · genau ±35,00 % = leichte Anomalie. Massgeblich ist die auf **zwei** Nachkommastellen gerundete Abweichung (2.3).
- KPI 01 erhält **keine** Anomalie-Einstufung.
- Die Werte sind operative Startwerte und werden später anhand historischer Daten überprüft.
- **Einstellbar pro Liga und KPI (beschlossen 08.11.2026):** Die Schwellen stehen in der Konfigurationsdatei `app/config/schwellen.toml`: ein Standardwert (±20,00 % / ±35,00 %) und bei Bedarf Abweichungen je Liga, je KPI oder je Liga und KPI. Derzeit gilt überall der Standard. Änderungen nur bewusst über die Datei (mit Neubau, Git und CHANGELOG), nicht über das Dashboard. Die gültigen Schwellen werden im Bereich *Datenqualität* angezeigt. Der spätere Tab zur Schwellen-Analyse (Etappe I, nach Etappe H) darf andere Schwellen nur durchrechnen, nicht übernehmen. **Vorgehen (Carsten, 08.11.2026):** zuerst gelten überall dieselben Schwellen; mit dem Tab werden die Schwellen je KPI und Liga intern analysiert, danach folgt das Feintuning je KPI und Liga.

### 2.3 Rundung

- Gerechnet wird **immer mit ungerundeten Werten**.
- Erst das Endergebnis wird gerundet, kaufmännisch (ab 5 aufrunden), auf **zwei Nachkommastellen** – bei **allen** KPIs und allen angezeigten Werten: Teamwerte, Ligareferenz, Hauptwert, Abweichung, Teamabweichungen (KPI 03), BTTS-Quoten (KPI 08), auch in den Texten (**Entscheidung Carsten, 08.11.2026**, gilt ab Etappe H; vorher eine Nachkommastelle). Grund: Nachvollziehbarkeit. Mit einer Stelle wirkten kleine Werte widersprüchlich (Beispiel KPI 06 Newcastle – Liverpool: Anzeige 1,3 gegen 1,2, gerechnet 1,25 gegen 1,205 = +3,73 %). Darstellung auf der öffentlichen Website: offener Punkt 15.
- Die Einstufung erfolgt anhand der auf zwei Stellen **gerundeten** Abweichung. Beispiel: +20,004 % → +20,00 % → keine Anomalie; +20,04 % → leichte Anomalie (bis 08.11.2026 wäre +20,04 % auf +20,0 % gerundet worden → keine). In den Testfällen KPI 02–09 ändert sich dadurch keine Einstufung.
- Technisch mit **Dezimalarithmetik** (Python `decimal`, `ROUND_HALF_UP`), **nicht** mit `round()`. Grund: `round()` rundet z. B. 2,675 auf 2,67 (richtig 2,68) und rundete mit einer Stelle 4,35 auf 4,3 und 2,65 auf 2,6.
- Weitergerechnet wird mit dem ungerundeten Wert. Beispiel KPI 02 BL-1: Abweichung mit der Ligareferenz 3,2444… = +34,08 %; mit der angezeigten 3,24 ergäbe sich fälschlich +34,26 %.

### 2.4 Vorzeichen

- **Frontend-Texte** mit „mehr / weniger / über / unter“: Abweichung **ohne Vorzeichen** („16,67 % über dem Liga-Durchschnitt“).
- **Kennzahlenfelder**: Vorzeichen **immer** anzeigen („−25,00 %“).
- **Frontend-Texte ohne „mehr / weniger / über / unter“** (Fall „Keine Anomalie“ bei KPI 02, 04 und 05–09): Vorzeichen **immer** anzeigen („Die Abweichung vom Liga-Durchschnitt beträgt +7,01 %.“ bzw. „… −8,90 %.“). Ohne Vorzeichen wäre die Richtung nicht erkennbar.
- Bei genau **0,00 %** steht nie ein Vorzeichen. Das gilt auch, wenn ein kleiner negativer Wert auf „−0,00“ gerundet würde: Anzeige „0,00“, keine Richtung (*ergänzt 08.11.2026*). In den echten Daten kommt das nicht vor; der Code prüft die Regel mit einem eigenen Formattest.
- Als Minuszeichen wird „−“ (U+2212) verwendet, nicht der Bindestrich „-“.

### 2.5 Einheitlicher Aufbau der KPI-Karten (ab KPI 02)

1. Hauptwert
2. Anomalie-Einstufung (keine / leicht / stark) und Richtung (positiv / negativ)
3. Relative Abweichung in Prozent
4. Referenzwert und beide Teamwerte
5. Datenbasis: Anzahl Spiele je Team, ggf. „vorläufig“; bei KPIs mit möglichen fehlenden Statistikwerten (KPI 04, 05, 09) zusätzlich die Anzahl Referenzspiele
6. Überschrift und Erklärungssatz

Schwellenwerte, Rundung, Vorzeichen und die Regeln für fehlende Daten werden **zentral** umgesetzt und gelten für alle KPIs.

### 2.6 Auswahl der Top-Anomalien (ligaübergreifend)

**Zweck:** Legt fest, welche Begegnungen des aktuellen Spieltags im Bereich „Top Anomalien“ (`/dashboard`) und später auf der Startseite der öffentlichen Website erscheinen. Die Auswahl erfolgt **zentral in der Berechnungslogik**, nicht im Frontend.

**Grundlage:**
- Begegnungen des aktuellen Spieltags aller aktiven Ligen (aktueller Spieltag gemäss `04_Spielplan.md`, Abschnitt 4).
- **KPI 02–09** mit leichter oder starker Anomalie (**Entscheidung Carsten, 08.11.2026**, gilt ab Etappe H; bis dahin nur KPI 02 und 04). Damit ist auch KPI 03 wieder dabei.
- KPI 01 hat keine Anomalie-Einstufung und wird nicht berücksichtigt. KPI 10–13 sind nie Teil der Top-Anomalien.
- **Gewichtung vorerst unverändert:** Es gilt die bisherige Rangfolge nach Stufe und Prozent (unten). Probelauf mit allen Spieltagen 2025/26 über vier Ligen: Anteil an den Top-4-Einträgen KPI 03 39 %, KPI 08 27 %, KPI 06 18 %, KPI 04 10 %, KPI 07 7 %, KPI 02, 05 und 09 nie. Ziel ist ein ausgewogener Mix je Spieltag; die Gewichtung wird zusammen mit der Schwellen-Analyse erarbeitet (offener Punkt 17).

**Ausschlüsse:**
- Vorläufige KPI-Werte
- Begegnungen mit Status „verschoben“ oder „abgesagt“
- Begegnungen ohne Anomalie

**Rangfolge und Auswahl:**
1. Starke Anomalien vor leichten.
2. Innerhalb derselben Stufe: grösserer Betrag der (gerundeten) relativen Abweichung zuerst.
3. Bei Gleichstand: früheres Spieldatum (`Datum von`).
4. Danach: Reihenfolge der Begegnungen in der Spielplan-Datei.
5. Pro Begegnung höchstens ein Eintrag. Haben mehrere KPIs derselben Begegnung eine Anomalie, zählt nur der KPI mit dem höchsten Rang; bei Gleichstand der KPI mit der kleineren Nummer.
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

**Beispiel (fiktiv):** Stuttgart 2,4 + Bayern 1,8 = 4,2 · Liga 3,6 → (4,2 − 3,6) / 3,6 × 100 = +16,67 % → keine Anomalie.

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

| | KPI 01 | KPI 02 | KPI 03 | KPI 04 | KPI 05 | KPI 06 | KPI 07 | KPI 08 | KPI 09 |
|---|---|---|---|---|---|---|---|---|---|
| Name | Formkurve | Erwartete Tore | Over 2.5 | Gelbe Karten | Ecken | Tore 1. HZ | Tore 2. HZ | Beide Teams treffen | Schüsse aufs Tor |
| Stichprobe | 5 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 |
| Teamwert | S/U/N | Ø Gesamttore | Ø Gesamttore | Ø eigene Gelbe | Ø Ecken beider Teams | Ø Tore beider Teams HZ 1 | Ø Tore beider Teams HZ 2 | BTTS-Quote in % | Ø Schüsse aufs Tor beider Teams |
| Verknüpfung | – | Durchschnitt | Durchschnitt | **Summe** | Durchschnitt | Durchschnitt | Durchschnitt | Durchschnitt | Durchschnitt |
| Referenz | keine | Liga | 2,5 fix | Liga | Liga | Liga HZ 1 | Liga HZ 2 | Liga-BTTS-Quote | Liga |
| Anomalie | nein | ja | ja | ja | ja | ja | ja | ja | ja |
| Top-Anomalien | nein | ja | ja (ab H) | ja | ja (ab H) | ja (ab H) | ja (ab H) | ja (ab H) | ja (ab H) |
| Nachkommastellen | – | 2 (ab H) | 2 (ab H) | 2 (ab H) | 2 | 2 | 2 | 2 | 2 |

Simulations-KPIs 10–13 (nur Backend, keine Anomalie-Einstufung, nie Top-Anomalien): Abschnitt 10.

**Zusammenhang:** Hauptwert KPI 06 + Hauptwert KPI 07 = Torindikator KPI 02 (exakt, weil beide den Mittelwert der Teamwerte verwenden). Das ist gewollt.

---

## 8. Offene Punkte / Unstimmigkeiten im Quelldokument

Diese Punkte sollten vor der Umsetzung im Code geklärt werden:

1. ~~**KPI 03 Frontend-Texte:** `{Hauptwert} %` statt `{Abweichung} %`.~~ **Erledigt am 30.10.2026:** `{Abweichung}` gilt. Im Word als Änderung markiert, mit deren Annahme abgeschlossen.
2. **KPI 03 „Keine Anomalie“ bei 0,00 %:** Der Satz „mehr/weniger“ passt nicht, wenn die Abweichung genau 0,00 % beträgt. Dafür fehlt ein eigener Text.
3. ~~**KPI 02 Fall A, Hinweis und Vorzeichen:** Hinweis stammte aus KPI 03; Vorzeichen im Text „Keine Anomalie“ ungeklärt.~~ **Erledigt am 30.10.2026:** Hinweis im Word ersetzt. Im Text „Keine Anomalie“ (KPI 02 und KPI 04) steht das Vorzeichen immer, bei 0,0 % keins (Abschnitt 2.4). Testfall KPI 02 PL-1 entsprechend auf „+7,0 %“ angepasst.
4. ~~**3-Tage-Regel:** Ligaspiele unter der Woche, Geltung für die Ligareferenz.~~ **Erledigt am 30.10.2026:** auf 2 Kalendertage reduziert (Spiele unter der Woche und dichte Spielpläne, z. B. Premier League über Weihnachten, zählen mit); gilt nur für Teamwerte, nicht für die Ligareferenz. Siehe Abschnitt 1.
5. ~~**Ligareferenz in KPI 04:** Definition der letzten 20 Spieltage.~~ **Erledigt am 28.10.2026:** einheitlich über Spalte `Gameday` geregelt, siehe Abschnitt 1.1.
6. ~~**Rundung der Teamabweichungen (KPI 03):**~~ **Erledigt am 08.11.2026:** zwei Nachkommastellen wie alle Werte (2.3).
7. **Datenquelle KPI 04:** Der Name der Datenquelle (im Word-Archiv als Platzhalter „[Name der Quelle]“) ist noch nicht dokumentiert. Bei Bedarf in Abschnitt 6 ergänzen. Für die Berechnung nicht relevant. *(02.11.2026: Bei einem Wechsel des Lieferanten muss die Zählweise der Gelben Karten vorab verglichen werden, siehe `06_Datenlieferung.md`, Abschnitt 8.)*
8. ~~**Überschrift KPI 03 negativ:** „Unter 2.5 Goals“ statt „2,5“.~~ **Erledigt am 30.10.2026:** „2,5“ gilt, im Word als Änderung markiert.
9. ~~**KPI 03 Nachkommastellen Hauptwert:**~~ **Erledigt am 08.11.2026:** zwei Nachkommastellen für alle KPIs (2.3); das Beispiel „3,10“ passt damit.
10. **KPI-Karte bei Aufsteiger-Spielen (KPI 02–04):** Die Testfälle nehmen an: Teamwert des Gegners und Ligareferenz werden angezeigt, Hauptwert, Abweichung und Anomalie als „–“. Bitte bestätigen.
11. **Schwellenwerte für Serie A und LaLiga** (07.11.2026): Nach dem Einschalten (Etappe F) mit „Häufigkeit der Anomalien“ prüfen, ob die Schwellen ±20 % / ±35 % ähnlich oft anschlagen wie in Bundesliga und Premier League (v. a. KPI 03). **Ergebnis 07.11.2026 (Saison 2025/26):** KPI 02 und 04 schlagen ähnlich oft an wie in Bundesliga und Premier League (leicht 12–20 %, stark 0–6 %). KPI 03 seltener (Serie A 9,3 %, LaLiga 18,3 % Anomalien gesamt; Bundesliga 59,5 %, Premier League 19,9 %), weil beide Ligen nahe an der festen 2,5-Tore-Marke liegen. Die Schwellen bleiben unverändert; KPI 03 wird ohnehin zusammen mit Bundesliga und Premier League überprüft. Details: `docs/tests/pruefprotokoll_etappe_f.md`.
12. **Schwellen für KPI 05–09** (08.11.2026): Vorläufig gelten ±20 % / ±35 %. Probelauf mit der Saison 2025/26 (Anteil Spiele mit Anomalie, leicht + stark):

    | Liga | KPI 05 Ecken | KPI 06 Tore 1. HZ | KPI 07 Tore 2. HZ | KPI 08 BTTS | KPI 09 Schüsse aufs Tor | zum Vergleich KPI 02 |
    |---|---|---|---|---|---|---|
    | Bundesliga | 2 % | 28 % | 25 % | 23 % | 4 % | 14 % |
    | Premier League | 0,5 % | 29 % | 17 % | 32 % | 2 % | 9 % |
    | Serie A | 1 % | 25 % | 23 % | 34 % | 1 % | 12 % |
    | LaLiga | 1 % | 41 % | 23 % | 38 % | 2 % | 15 % |

    KPI 06–08 schlagen deutlich häufiger an als KPI 02; bei BTTS und den Halbzeit-Toren eher zu oft. **KPI 05 und 09 seit der Umstellung vom 08.11.2026 (eigene + gegnerische) dagegen sehr selten**, starke Anomalien praktisch nie (vorher mit nur eigenen Werten: KPI 05 14–27 %, KPI 09 22–32 %). Grund: Die Gesamtzahl der Ecken bzw. Schüsse aufs Tor pro Spiel schwankt viel weniger als die Tore, der Mittelwert zweier Teams glättet zusätzlich. Für eine ähnliche Häufigkeit wie KPI 02 lägen die Schwellen bei KPI 05 und 09 etwa bei ±12 % / ±18 %. **Entscheidung Carsten 08.11.2026:** Schwellen werden später bearbeitet; bis dahin gelten ±20 % / ±35 %. Klärung im Simulations-Tab (Etappe I), danach ggf. eigene Schwellen je KPI/Liga.
13. ~~**Ergebniskontrolle**~~ **erledigt 08.11.2026:** festgelegt in Abschnitt 11 (Entscheidungen Carsten).
14. **Schüsse aufs Tor (KPI 09, 12, 13):** Zählweise der Datenquelle (gehaltene, geblockte Schüsse, Tore) bei einem Lieferantenwechsel (Footiqo) vorab vergleichen, wie bei den Gelben Karten.
15. **Nachkommastellen auf der öffentlichen Website** (08.11.2026): Im Dashboard haben alle KPIs zwei Nachkommastellen (2.3). Für Frontend/Website entscheidet Carsten später (z. B. zwei Nachkommastellen oder eine einfachere Darstellung).
16. **KPI 08 „Angriff gegen Abwehr“ und Aussagekraft** (08.11.2026): Carsten fragt, ob KPI 08 einen Mehrwert für die Prognose bietet. Auswertung Claude (6'182 Spiele 2021/22–2025/26, vier Ligen, beide Teams mit 10 Spielen; BTTS im Schnitt 55 %): Im Fünftel mit dem niedrigsten KPI-08-Wert trafen beide in 48 % der Spiele, im höchsten Fünftel in 63 %. Varianten (Trefferquote des einen gegen Kassierquote des anderen Teams, Heim-/Auswärtsspiele getrennt, Tore statt ja/nein) trennen nicht besser. Teams mit 10 von 10 Spielen mit Tor treffen im nächsten Spiel zu 84 % (bei 5 oder weniger von 10: 66 %); gegen einen Gegner, der höchstens in 5 von 10 Spielen kassiert, nur zu 73 %. **Entscheidung Carsten:** KPI 08 bleibt wie definiert (Stimmungsbild, keine Prognose). „Heim trifft / Gast trifft“ und die Stärke des Gegners werden in Etappe I mit der Ergebniskontrolle (Punkt 13) geprüft; Ergebnisse sind zugleich Stoff für spätere Blog-Beiträge.
17. **Gewichtung der Top-Anomalien** (08.11.2026): Mit der bisherigen Rangfolge (Stufe, dann Prozent) kommen KPIs mit grossen relativen Ausschlägen (KPI 03, 06, 08) fast immer nach oben, KPI 02, 05 und 09 nie. Probelauf Claude (2025/26, vier Ligen, Anteil an den Top-4-Einträgen): bisherige Regel KPI 03 39 % · 08 27 % · 06 18 % · 04 10 % · 07 7 % · 02/05/09 0 %; mit „höchstens 1 Eintrag je KPI“ 03 24 % · 06 25 % · 08 24 % · 04 19 % · 07 7 % · 02/05/09 0 %; Rang nach **Seltenheit** (wie ungewöhnlich ist die Abweichung für diesen KPI in dieser Liga, verglichen mit der Vorsaison) plus höchstens 1 je KPI: 04 20 % · 08 18 % · 06 15 % · 07 13 % · 09 12 % · 02 11 % · 05 6 % · 03 4 %, im Schnitt 4 verschiedene KPIs je Spieltag. **Entscheidung Carsten:** vorerst bisherige Regel über KPI 02–09; die Gewichtung wird mit der Schwellen-Analyse (Etappe I) erarbeitet. Ziel: ein schöner Mix je Spieltag.

Für die Umsetzung blockierend ist keiner dieser Punkte: Die Testfälle legen für 2, 6, 9 und 10 jeweils eine Annahme fest. Wird eine Annahme geändert, sind die betroffenen Testfälle anzupassen.

**Umsetzung (Etappe C, 31.10.2026):** so wie in den Testfällen angenommen. Punkt 2: Bei genau 0,00 % zeigt KPI 03 nur die Überschrift „Keine statistische Besonderheit“, ohne Satz, bis ein Text festgelegt ist. Punkte 6 und 9: eine Nachkommastelle (ab Etappe H zwei, Entscheidung 08.11.2026). Punkt 10: Gegnerwert und Ligareferenz sichtbar, Hauptwert, Abweichung und Anomalie „–“.

---

## 9. Frontend-KPIs 05–09 (bestätigt 08.11.2026, Umsetzung Etappe H)

Quelle: Carstens Spezifikation „Soccer Intelligence – KPI-Regelwerk KPI 05–13, Entwurf“ (Word, 07.11.2026) mit den Entscheidungen vom 08.11.2026. Verbindlich seit der Bestätigung der Testfälle `docs/tests/test_kpi05_ecken.md` bis `test_kpi09_schuesse_aufs_tor.md` am 08.11.2026 (gemeinsamer Rundgang).

### 9.0 Gemeinsame Regeln für KPI 05–09

- Es gelten alle allgemeinen Regeln aus Abschnitt 1 (Saisonfenster, Stichtag „Datum von“, 2-Tage-Regel, Sortierung, keine Zukunftsdaten, fehlende Werte nie als 0) und die Anomalie-, Rundungs- und Vorzeichenregeln aus Abschnitt 2.
- **Stichprobe:** letzte 10 abgeschlossene Ligaspiele je Team. **Zuerst** die letzten 10 Spiele bestimmen, **danach** Spiele ohne Wert für diesen KPI auslassen; kein älteres Spiel nachziehen. Weniger als 10 gültige Spiele → tatsächliche Anzahl verwenden und „vorläufig“ anzeigen.
- **Ligareferenz:** letzte 20 Spieltage laut `Gameday` (Abschnitt 1.1), nur Spiele vor dem Stichtag; Spiele ohne vollständige Werte (beide Teams) werden für diesen KPI ausgelassen.
- Ist ein Teamwert nicht berechenbar (Team ohne Spiele): kein Hauptwert, keine Abweichung, keine Anomalie; Teamwert des Gegners und Ligareferenz werden trotzdem angezeigt (wie KPI 02–04, offener Punkt 10).
- Fehlt die Ligareferenz oder ist sie 0: Abweichung und Anomalie „–“.
- Überschrift bei „Keine Anomalie“ ist bei allen KPIs einheitlich **„Keine statistische Besonderheit“** (Entscheidung 08.11.2026).
- Textvariablen werden mit den gerundeten Anzeigewerten befüllt; Vorzeichen gemäss 2.4.
- **Datenbasis:** Anzahl Spiele je Team; bei KPI 05 und 09 zusätzlich die Anzahl Referenzspiele.
- KPI 05–09 fliessen ab Etappe H in die Top-Anomalien ein (2.6, Entscheidung 08.11.2026).
- **Darstellung im Dashboard** (Entscheidung 08.11.2026): kompakte Tabelle mit Hauptwert und Anomalie-Punkt je KPI 01–09; alle Details einer Begegnung (Teamwerte, Ligareferenz, Abweichung, Datenbasis, Texte) per Aufklappen. Einzelheiten im Dashboard-Briefing.

### 9.1 KPI 05 – Ecken

**Zweck:** schätzt das Gesamt-Eckballaufkommen der Begegnung anhand aller Ecken (eigene und gegnerische) in den bisherigen Spielen beider Teams.

```
Teamwert Team X        = Summe der Ecken BEIDER Mannschaften (W + X) in den Spielen von Team X / Anzahl gültiger Spiele
                         (eigene + gegnerische Ecken; Spiel nur gültig, wenn W und X gefüllt sind)
Erwartete Ecken        = (Teamwert Team 1 + Teamwert Team 2) / 2    (Mittelwert, wie KPI 02)
Ligareferenz           = Summe (W + X) in den Referenzspielen / Anzahl Referenzspiele mit W und X
Relative Abweichung    = (Erwartete Ecken − Ligareferenz) / Ligareferenz × 100
```

**Begründung (Änderung 08.11.2026, Carsten):** Nur die eigenen Ecken zu zählen misst vor allem die Stärke eines Teams. Ein Top-Team hat viele eigene Ecken, ein Abstiegskandidat viele gegen sich; treffen zwei starke Teams aufeinander, entstünde ein künstlich hoher Wert. Mit eigenen und gegnerischen Ecken ist Angriff gegen Abwehr automatisch verrechnet: (eigene Ecken Team 1 + zugelassene Ecken Team 2 + eigene Ecken Team 2 + zugelassene Ecken Team 1) / 2. Beispiel Bayern – Stuttgart, 1. Spieltag 2026/27: bisher 13,2 Ecken (+35,4 %, stark), neu 10,8 Ecken (+10,3 %, keine).

**Dashboard:** Hauptwert „Erwartete Ecken“ (zwei Nachkommastellen) · Team 1 / Team 2: Ø Ecken je Spiel (beide Mannschaften) · Ligareferenz · Abweichung · Anomalie · Datenbasis (Spiele je Team und Referenzspiele).

| Fall | Überschrift | Beschreibung |
|---|---|---|
| Keine Anomalie | Keine statistische Besonderheit | Der Eckballindikator liegt bei {Hauptwert} Ecken. Die Abweichung vom Liga-Durchschnitt beträgt {Abweichung} %. *(mit Vorzeichen)* |
| Positiv | Viele Ecken erwartet | Für diese Begegnung werden {Hauptwert} Ecken erwartet. Das liegt {Abweichung} % über dem Liga-Durchschnitt. |
| Negativ | Wenige Ecken erwartet | Für diese Begegnung werden {Hauptwert} Ecken erwartet. Das liegt {Abweichung} % unter dem Liga-Durchschnitt. |

### 9.2 KPI 06 – Tore 1. Halbzeit

**Zweck:** durchschnittliches gesamtes Toraufkommen in Halbzeit eins in den bisherigen Spielen beider Teams.

```
Teamwert Team X        = Summe der Tore BEIDER Mannschaften in Halbzeit 1 (Q + R) in den Spielen von Team X / Anzahl Spiele
Hauptwert              = (Teamwert Team 1 + Teamwert Team 2) / 2   (Mittelwert)
Ligareferenz           = Summe (Q + R) in den Referenzspielen / Anzahl Referenzspiele
Relative Abweichung    = (Hauptwert − Ligareferenz) / Ligareferenz × 100
```

**Dashboard:** Hauptwert „Tore 1. Halbzeit“ (Tore pro Spiel) · Team 1 / Team 2: Ø Tore beider Teams in Halbzeit 1 je Spiel · Ligareferenz · Abweichung · Anomalie · Datenbasis. Alle Werte mit zwei Nachkommastellen (2.3), auch in den Texten (z. B. „im Schnitt 1,25 Tore“).

| Fall | Überschrift | Beschreibung |
|---|---|---|
| Keine Anomalie | Keine statistische Besonderheit | In den bisherigen Spielen fielen in Halbzeit eins im Schnitt {Hauptwert} Tore. Die Abweichung vom Liga-Durchschnitt beträgt {Abweichung} %. *(mit Vorzeichen)* |
| Positiv | Viele Tore in Halbzeit 1 | In den bisherigen Spielen beider Teams fielen in Halbzeit eins durchschnittlich {Hauptwert} Tore. Das sind {Abweichung} % mehr als im Liga-Durchschnitt. |
| Negativ | Wenige Tore in Halbzeit 1 | In den bisherigen Spielen beider Teams fielen in Halbzeit eins durchschnittlich {Hauptwert} Tore. Das sind {Abweichung} % weniger als im Liga-Durchschnitt. |

### 9.3 KPI 07 – Tore 2. Halbzeit

Gleiche Logik und gleiche Darstellung wie KPI 06, ausschliesslich mit den Toren der **zweiten Halbzeit** (Spalten T + U), nicht mit dem Endstand.

| Fall | Überschrift | Beschreibung |
|---|---|---|
| Keine Anomalie | Keine statistische Besonderheit | In den bisherigen Spielen fielen in Halbzeit zwei im Schnitt {Hauptwert} Tore. Die Abweichung vom Liga-Durchschnitt beträgt {Abweichung} %. *(mit Vorzeichen)* |
| Positiv | Viele Tore in Halbzeit 2 | In den bisherigen Spielen beider Teams fielen in Halbzeit zwei durchschnittlich {Hauptwert} Tore. Das sind {Abweichung} % mehr als im Liga-Durchschnitt. |
| Negativ | Wenige Tore in Halbzeit 2 | In den bisherigen Spielen beider Teams fielen in Halbzeit zwei durchschnittlich {Hauptwert} Tore. Das sind {Abweichung} % weniger als im Liga-Durchschnitt. |

### 9.4 KPI 08 – Beide Teams treffen (BTTS)

**Zweck:** historische Häufigkeit, mit der in den Spielen eines Teams beide Mannschaften mindestens ein Tor erzielen. **Keine** Eintrittswahrscheinlichkeit des analysierten Spiels; nie als „Wahrscheinlichkeit“ bezeichnen.

```
BTTS in einem Spiel    = Heimtore ≥ 1 UND Auswärtstore ≥ 1 (Endstand, Spalten K und L)
Teamwert Team X        = Anzahl BTTS-Spiele von Team X / Anzahl Spiele × 100        (BTTS-Quote in %)
Hauptwert              = (BTTS-Quote Team 1 + BTTS-Quote Team 2) / 2               (BTTS-Indikator in %)
Ligareferenz           = BTTS-Spiele in den Referenzspielen / Anzahl Referenzspiele × 100
Relative Abweichung    = (Hauptwert − Ligareferenz) / Ligareferenz × 100            (relativ, nicht in Prozentpunkten)
```

**Dashboard:** Hauptwert „BTTS-Indikator“ in % (zwei Nachkommastellen) · Team 1 / Team 2: BTTS-Quote in % · Ligareferenz in % · Abweichung · Anomalie · Datenbasis. Feinschliff der Darstellung auf der späteren Website (Prozentwert je Team, darüber der Wert der Partie).

| Fall | Überschrift | Beschreibung |
|---|---|---|
| Keine Anomalie | Keine statistische Besonderheit | Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von {Hauptwert} % auf. Die Abweichung vom Liga-Durchschnitt von {Ligareferenz} % beträgt {Abweichung} %. *(mit Vorzeichen)* |
| Positiv | Beide Teams treffen häufig | Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von {Hauptwert} % auf. Das liegt {Abweichung} % über dem Liga-Durchschnitt von {Ligareferenz} %. |
| Negativ | Beide Teams treffen seltener | Die bisherigen Spiele beider Teams weisen einen gemeinsamen BTTS-Indikator von {Hauptwert} % auf. Das liegt {Abweichung} % unter dem Liga-Durchschnitt von {Ligareferenz} %. |

### 9.5 KPI 09 – Schüsse aufs Tor

**Zweck:** schätzt die Gesamtzahl der Schüsse aufs Tor in der Begegnung anhand aller Schüsse aufs Tor (abgegebene und zugelassene) in den bisherigen Spielen beider Teams.

```
Teamwert Team X        = Summe der Schüsse aufs Tor BEIDER Mannschaften (AU + AV) in den Spielen von Team X / Anzahl gültiger Spiele
                         (eigene + gegnerische; Spiel nur gültig, wenn AU und AV gefüllt sind)
Hauptwert              = (Teamwert Team 1 + Teamwert Team 2) / 2    (Mittelwert, wie KPI 02)
Ligareferenz           = Summe (AU + AV) in den Referenzspielen / Anzahl Referenzspiele mit AU und AV
Relative Abweichung    = (Hauptwert − Ligareferenz) / Ligareferenz × 100
```

**Begründung (Änderung 08.11.2026, Carsten):** wie KPI 05 – auch zugelassene Schüsse aufs Tor zählen, damit ein Team, das oft unter Beschuss steht, nicht als torungefährliche Partie erscheint.

**Gegenprobe (08.11.2026, Frage Carsten „Sind eigene Schüsse nicht aussagekräftiger?“):** 6'689 Spiele 2021/22–2025/26, vier Ligen. Zusammenhang mit den tatsächlichen Schüssen aufs Tor im Spiel: nur eigene (Summe) 0,19, eigene + gegnerische (Mittelwert) 0,22; mittlere Abweichung 2,6 bzw. 2,5. Auch für die Schüsse aufs Tor und Tore **eines** Teams sind eigene + vom Gegner zugelassene Schüsse besser (0,34 bzw. 0,29) als nur eigene (0,28 bzw. 0,25). **Entscheidung Carsten:** KPI 09 bleibt wie definiert; keine zusätzliche Aufteilung „eigene/zugelassene“ in der Detailansicht. Eigene Schüsse werden in KPI 12 und 13 (Simulation) verwendet.

**Dashboard:** Hauptwert „Erwartete Schüsse aufs Tor“ (zwei Nachkommastellen) · Team 1 / Team 2: Ø Schüsse aufs Tor je Spiel (beide Mannschaften) · Ligareferenz · Abweichung · Anomalie · Datenbasis (Spiele je Team und Referenzspiele).

| Fall | Überschrift | Beschreibung |
|---|---|---|
| Keine Anomalie | Keine statistische Besonderheit | Der Indikator liegt bei {Hauptwert} Schüssen aufs Tor. Die Abweichung vom Liga-Durchschnitt beträgt {Abweichung} %. *(mit Vorzeichen)* |
| Positiv | Viele Schüsse aufs Tor erwartet | Der Indikator liegt bei {Hauptwert} Schüssen aufs Tor. Das liegt {Abweichung} % über dem Liga-Durchschnitt. |
| Negativ | Wenige Schüsse aufs Tor erwartet | Der Indikator liegt bei {Hauptwert} Schüssen aufs Tor. Das liegt {Abweichung} % unter dem Liga-Durchschnitt. |

---

## 10. Simulations-KPIs 10–13 (Entwurf 08.11.2026, nur Backend)

**Status:** experimentelle Konzepte. **Nicht** im Frontend, **nie** in den Top-Anomalien, **keine** Anomalie-Einstufung, nicht als Prognose freigegeben. Berechnung nur offline bzw. im späteren Simulations-Tab (Etappe I) mit historischen Daten. Allgemeine Regeln aus Abschnitt 1 und 9.0 (Stichprobe, fehlende Werte, Ligareferenz) gelten sinngemäss. Ausgegeben werden immer auch die Einzelkomponenten und die Stichprobengrössen.

### 10.1 KPI 10 – Angriff gegen Abwehr, 1. Halbzeit

**Fragestellung:** Treffen Teams mit hohem Torertrag in Halbzeit eins auf Gegner, die in Halbzeit eins viele Gegentore zulassen?

```
Offensivwert Team X     = in Halbzeit 1 ERZIELTE Tore von Team X / Anzahl Spiele        (letzte 10 Spiele)
Defensivwert Team X     = in Halbzeit 1 KASSIERTE Tore von Team X / Anzahl Spiele
Richtung Heim           = (Offensivwert Heim + Defensivwert Auswärts) / 2   ≈ erwartete Tore des Heimteams
Richtung Auswärts       = (Offensivwert Auswärts + Defensivwert Heim) / 2   ≈ erwartete Tore des Auswärtsteams
Spielwert               = Richtung Heim + Richtung Auswärts                  ≈ erwartete Tore beider Teams in Halbzeit 1
Vergleich               = (Spielwert − Ligareferenz Tore HZ 1) / Ligareferenz Tore HZ 1 × 100   (beschreibend)
```

Entscheidung 08.11.2026: **Spielwert = Summe** beider Richtungen, damit er im gleichen Massstab wie die Ligareferenz (Tore beider Teams in Halbzeit 1, wie KPI 06) steht und direkt neben KPI 06 verglichen werden kann. Beide Richtungswerte werden zusätzlich ausgegeben, damit Asymmetrien sichtbar bleiben. Prüffrage: Liefert der Matchup-Wert gegenüber KPI 06 zusätzlichen Informationswert? Die Formel ist eine einfache Annahme, keine kalibrierte Torprognose.

### 10.2 KPI 11 – Angriff gegen Abwehr, 2. Halbzeit

Wie KPI 10, ausschliesslich mit den Toren der zweiten Halbzeit (Spalten T, U); Vergleich mit der Ligareferenz Tore HZ 2 (wie KPI 07). Prüffrage: Zusatznutzen gegenüber KPI 07?

### 10.3 KPI 12 – Offensivdruck

**Fragestellung:** Welche Teams zeigen in ihren bisherigen Spielen eine erhöhte offensive Aktivität? „Druck“ ist ein statistischer Proxy, keine Messung von Chancenqualität oder Spielkontrolle.

```
Schusswert Team X       = Ø EIGENE Gesamtschüsse je Spiel (Spalte AO bzw. AP, Gesamtspiel)
Eckenwert Team X        = Ø EIGENE Ecken je Spiel (Spalte W bzw. X, Gesamtspiel)
Liga-Schusswert         = Summe (AO + AP) in den Referenzspielen / (2 × Anzahl Referenzspiele)    (pro Team und Spiel)
Liga-Eckenwert          = Summe (W + X) in den Referenzspielen / (2 × Anzahl Referenzspiele)      (pro Team und Spiel)
Teamindex Team X        = (Schusswert / Liga-Schusswert + Eckenwert / Liga-Eckenwert) / 2
Begegnungsindex         = (Teamindex Team 1 + Teamindex Team 2) / 2        (1,00 = Ligadurchschnitt)
```

Entscheidung 08.11.2026: Liga-Durchschnitt **pro Team und Spiel**, Referenzzeitraum wie 1.1 (letzte 20 Spieltage). Nur berechnen, wenn beide Komponenten für beide Teams und beide Ligawerte vorhanden und grösser als 0 sind; keine Umgewichtung bei fehlender Komponente. Ausgabe: Index und beide Einzelkomponenten.

### 10.4 KPI 13 – Abschluss-Effizienz

**Fragestellung:** Wie häufig führen Schüsse aufs Tor bei einer Mannschaft zu einem Tor? Beschreibt historische Verwertung, nicht die Qualität einzelner Chancen; keine Gleichsetzung mit xG.

```
Teamquote Team X        = Summe EIGENE Tore / Summe EIGENE Schüsse aufs Tor × 100    (über die Stichprobe, nicht Ø der Spielquoten)
Begegnungswert          = (Teamquote Team 1 + Teamquote Team 2) / 2
Liga-Effizienz          = Summe aller Tore / Summe aller Schüsse aufs Tor × 100       (Referenzspiele mit AU und AV)
Vergleich               = (Begegnungswert − Liga-Effizienz) / Liga-Effizienz × 100   (beschreibend, nur wenn Liga-Effizienz > 0)
```

- Spiele ohne Wert für Schüsse aufs Tor werden für diesen KPI ausgelassen. Ist die Summe der Schüsse aufs Tor eines Teams 0, ist seine Teamquote nicht verfügbar.
- Entscheidung 08.11.2026: Tore zählen wie in der Datenbank, **einschliesslich Eigentore des Gegners**. Tore ohne registrierten Schuss aufs Tor (meist Eigentore) sind **kein** Datenkonflikt; über 10 Spiele glättet sich der Effekt. Sie stehen weiterhin als Hinweis im Bereich *Datenqualität*.
- Quote immer zusammen mit Anzahl Spiele und Anzahl Schüsse aufs Tor ausgeben (kleine Nenner schwanken stark).

### 10.5 Prüfung vor einer möglichen Produktivdefinition

| KPI | Zu testende Varianten | Prüffrage |
|---|---|---|
| 10/11 Angriff gegen Abwehr | Richtungswerte einzeln vs. Spielwert; HZ 1 vs. HZ 2 | Zusatznutzen gegenüber KPI 06/07? |
| 12 Offensivdruck | Komponenten einzeln vs. Index | Stabilität, Verständlichkeit, dominiert eine Komponente? |
| 13 Abschluss-Effizienz | Teamquoten, gemeinsame Quote, Nennergrössen | Schwankung, Datenfehler, zusätzliche Aussagekraft? |

Freigabekriterien: Berechnung auf historischen Begegnungen aller vier Ligen · Prüfung von Vollständigkeit, Ausreissern, Nullwerten und Nennern · Vergleich mit einer einfachen Baseline und den bestehenden KPIs · Verständlichkeit und Fan-Relevanz · Dokumentation von Beispielen und Grenzen · separate Freigabe von Formel, Anzeige, Schwellen und Top-Anomalie-Eignung.

---

## 11. Ergebniskontrolle und Simulation (Etappe I.1, Entscheidungen Carsten 08.11.2026)

Nur im internen Bereich „Simulation – Spielwiese“. Ändert keine Live-Werte und keine gültigen Schwellen.

### 11.1 Wann ist eine Anomalie eingetroffen?

Verglichen wird der **tatsächliche Wert im Spiel** mit der **Ligareferenz, die vor dem Spiel galt** (Abschnitt 1.1; nie mit dem Saisondurchschnitt, sonst flössen Zukunftsdaten ein). Positive Anomalie: eingetroffen, wenn der Wert **über** der Referenz liegt; negative: wenn er **darunter** liegt. Gleichstand zählt in keiner Richtung.

| KPI | Wert im Spiel | Vergleich |
|---|---|---|
| 02 | Tore beider Teams | Ligareferenz Tore |
| 03 | Tore beider Teams | feste Marke 2,5 (positiv: mindestens 3, negativ: höchstens 2) |
| 04 | gelbe Karten beider Teams | Ligareferenz Karten |
| 05 | Ecken beider Teams | Ligareferenz Ecken |
| 06 / 07 | Tore der 1. bzw. 2. Halbzeit | Ligareferenz der Halbzeit |
| 08 | beide treffen (100 %) oder nicht (0 %) | Ligareferenz BTTS-Quote, also: positiv = beide treffen, negativ = nicht beide |
| 09 | Schüsse aufs Tor beider Teams | Ligareferenz Schüsse aufs Tor |

Fehlt der Wert im Spiel oder ist er keine ganze Zahl, zählt das Spiel für diesen KPI nicht (Abschnitt 1). Hinweis: Weil die Werte ganze Zahlen sind, ist „über der Referenz“ unterschiedlich leicht zu erreichen (bei 3,07 Toren braucht es mindestens 4). Darum wird immer mit Spielen ohne Anomalie verglichen (11.2).

### 11.2 Kennzahlen

- **Grundlage:** alle Spiele der gewählten Saisons, je so berechnet, als wären sie noch nicht gespielt (Stichtag = Spieldatum, Spieltag = `Gameday`). Nicht verwendet: die erste Saison der Datenbank (ohne Vorsaison, d. h. 2020/21), vorläufige Werte (z. B. Aufsteiger) und nicht berechenbare Werte.
- **Fälle:** Spiele mit Anomalie in dieser Richtung und bekanntem Ergebnis. Positiv und negativ werden getrennt ausgewertet; leicht und stark wahlweise gemeinsam oder getrennt.
- **Trefferquote:** Anteil der Fälle, in denen die Anomalie eingetroffen ist (aus den aufsummierten Fällen, nicht als Durchschnitt von Saisonquoten).
- **Ohne Anomalie:** dasselbe Ereignis in den Spielen ohne Anomalie (mit den eingestellten Schwellen).
- **Mehrwert** (Hauptkennzahl): Trefferquote minus Quote ohne Anomalie, in Prozentpunkten.
- **Schwankung:** ±1,96 · √(p · (100 − p) / n) Prozentpunkte (95 %).
- Alle Zahlen mit zwei Nachkommastellen, kaufmännisch gerundet.

### 11.3 Urteil

Verglichen wird der Mehrwert nachher (eingestellte Schwellen) mit vorher (gültige Schwellen aus `schwellen.toml`):

- **unverändert:** gleiche Schwellen;
- **zu wenige Fälle:** vorher oder nachher weniger als 100 Fälle (Zeile grau, wenn nachher unter 100);
- **besser / schlechter:** der Mehrwert verändert sich um mehr als die Schwankung nachher;
- sonst **kein klarer Unterschied**.

### 11.4 Saisons

Auswahl (Wunsch Carsten 09.11.2026): alle abgeschlossenen Saisons (2021/22–2025/26), die letzten 4, 3 oder 2 Saisons, die letzte Saison und die aktuelle Saison (2026/27, vorläufig, noch nicht abgeschlossen). Ob eine Schwelle robust ist, zeigt der Vergleich „alle abgeschlossenen“ gegen „letzte 2 Saisons“: Hält der Mehrwert in beiden, ist die Schwelle nicht nur zufällig gut.

### 11.5 Änderungen an den Definitionen

Werden Anomalien später neu definiert, wird das hier mit Datum festgehalten und im Bereich „Definitionen und Änderungen“ des Tabs angezeigt (`app/core/simulation.py`, `DEFINITION_CHANGES`).

| Datum | Änderung |
|---|---|
| 08.11.2026 | Erste Fassung (Etappe I.1) |
