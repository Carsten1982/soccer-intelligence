# Soccer Intelligence – Spielplan, Import und Anzeige kommender Spieltage (Spezifikation)

**Version:** 2.2 · **Stand:** 19.11.2026 (2.2: Statusmodell und Schnappschuss, umgesetzt in 0.20)
**Grundlage:**
- v2.0 und die Rückmeldung von ChatGPT („Prüfpunkte v2.0“)
- Entscheidungen Carsten vom 15.11.2026: S1–S10, O1, O2
- Prüfung von Code und echten API-Daten durch Claude

**Geplante Versionen:** 0.15 (Import) und 0.16 (Anzeige)
**Status:** freigegeben von Carsten am 15.11.2026. **Abschnitt 3 (Import) umgesetzt in Version 0.15; Abschnitte 4 und 5 (Anzeige) umgesetzt in Version 0.16** nach dem Designentwurf vom 16.11.2026 (Festlegungen bei der Umsetzung: Abschnitt 4.8). Gewertete Spiele: `06_Datenlieferung.md`, Abschnitt 10.1 (R2).

**Änderungen gegenüber v2.0:**
- Originalstatus der API (S1)
- drei Terminfälle (S2)
- zeitliche Sortierung (S3)
- Top-Anomalien-Block mit Nachholspielen (S4)
- kein künstlicher Hauptzeitraum (S5)
- feste Zuordnungsdatei (S6)
- Top Anomalien nur vor Anpfiff (S7)
- „Werte ab“ präzisiert (S8)
- Datenstand höchstens 3 Tage alt (S9; seit 0.20: 48 Stunden)
- Saisonwechsel (S10)
- „Spielpause“ statt „Länderspielpause“ und einheitlich 14 Tage (O1)
- Abschnitte innerhalb von heute bis heute + 6 (O2)
- Zeitzone ausdrücklich geregelt
- zwei Container
- Testfälle ergänzt (Z1–Z12)

---

## 1. Ziel

Das Dashboard zeigt je Liga die **tatsächlich anstehenden Spiele**, getrennt nach **offiziellen Spieltagen**.
- Nachholspiele und vorgezogene Spiele bleiben ihrem Spieltag zugeordnet.
- Pausen und Saisonende werden richtig erkannt, aber nie aus fehlenden oder veralteten Daten abgeleitet.
- Dieselbe Logik verwendet später die öffentliche Website.

---

## 2. Ausgangslage (Befunde aus Code und echten API-Daten 2026/27)

| Befund | Beispiel | Folge im heutigen Code |
|---|---|---|
| Nachholspiele haben bei der API **keinen Sonderstatus** | LaLiga Spieltag 1: vier Spiele am 25.–27.08. gespielt (Hauptzeitraum 15.–17.08.) | Unsere 3-Tage-Regel macht daraus „verschoben“, und **diese Spiele bekommen keine KPIs** (Fehler) |
| Vorgezogene Spiele | LaLiga Spieltag 23: zwei Spiele am 02.12.2026, der Rest im Februar | ebenfalls „verschoben“, ohne KPIs |
| Die API liefert **immer** Datum und Uhrzeit. TBD kommt selten vor; ferne Spieltage haben **einen einheitlichen Platzhalter-Termin** | Bundesliga ab Spieltag 19: alle Spiele „Sa 15:30“ | Wir zeigen eine Uhrzeit, die es noch nicht gibt |
| Am letzten Spieltag spielen alle tatsächlich gleichzeitig | Bundesliga Spieltag 34, Premier League, LaLiga | Eine reine „alle gleich“-Regel wäre falsch (S2) |
| Pausen 2026/27 | Bundesliga Winterpause 18 Tage; Serie A 12, LaLiga 13; Premier League ohne Pause; im September und März auch 18–20 Tage ohne Spiel | keine Pausenerkennung |
| Statusarten in 8 Saisons Rohdaten | fast nur FT und NS; einmal ABD (Rayo – Athletic, 10.10.2026) | – |
| **Gewertete Spiele kommen auch als FT** | Verona – Roma 2020/21: API meldet FT 3:0 (Wertung), auf dem Platz 0:0 | Der Status AWD/WO allein ist **nicht verlässlich** (siehe Spezifikation Ergebnis-Import) |

Die Saisonliste der API liefert alles Nötige. Zusätzlich braucht es nur die Spielliste der Vorsaison (Abschnitt 3.6).

---

## 3. Import (Container `soccer-import`, `app/importer/spielplan.py`)

### 3.1 Status: Original speichern, Anzeige und KPI ableiten (S1)

Neue Spalte **`API-Status`** im Spielplan, mit dem Kurzcode der API unverändert. Daraus werden abgeleitet:

| API | Bedeutung | Spielplan-Status (bisherige Spalte) | Anzeige | KPI-Werte für das Spiel |
|---|---|---|---|---|
| NS | angesetzt | geplant (leer) | geplant | ja |
| TBD | Datum bekannt, Zeit offen | geplant | „Zeit offen“ | ja |
| 1H, HT, 2H, ET, BT, P, LIVE | läuft | geplant | „läuft“ | ja (vor dem Spiel berechnet) |
| INT | kurz unterbrochen | geplant | „unterbrochen“ | ja |
| SUSP | ausgesetzt, Fortsetzung an anderem Tag | **ausgesetzt** (neu) | „ausgesetzt“ | ja, bis zur Fortsetzung |
| FT, AET, PEN | beendet | geplant | gespielt mit Ergebnis | – |
| PST | verschoben, ohne neuen Termin | verschoben | „verschoben“ | nein |
| CANC | abgesagt | abgesagt | „abgesagt“ | nein |
| ABD | abgebrochen | abgebrochen | „abgebrochen“ | nein |
| AWD, WO | gewertet | **gewertet** (neu) | „gewertet“ | nein |
| NS, Termin liegt mehr als 1 Tag zurück (Datenfehler) | unklar | geplant | „Status offen“ | nein; **Warnung** im Bericht |

- Die **3-Tage-Regel** („mehr als 3 Tage ausserhalb = verschoben“) **entfällt**.
- Neue Werte in der Spalte Status: `ausgesetzt`, `gewertet`. Beide zählen nicht für „Spieltag beendet“.

### 3.2 Datum

- **Datum von = Datum bis = Termin laut API**, für alle Spiele, auch Nachholspiele, vorgezogene und verschobene Spiele.
- PST-Spiele behalten das Datum, das die API weiter liefert, also den ursprünglichen Termin (S5).
- Der KPI-Stichtag (`Datum von`) ist damit immer der echte bzw. letzte bekannte Termin.

### 3.3 Spalte `Hinweis` (nur Anzeige, ohne Wirkung auf die KPIs)

- **Hauptzeitraum** eines Spieltags: das Fenster von höchstens 4 Kalendertagen mit den meisten regulären Spielen (Status NS/TBD/FT …, ohne PST/CANC/ABD/SUSP/AWD/WO).
  - Bei Gleichstand gewinnt das **frühere Fenster** (so schon heute im Code).
  - **Ohne reguläre Spiele gibt es keinen Hauptzeitraum** und damit keine Vermerke (S5).
- **„Nachholspiel“**: Termin mehr als 3 Tage nach dem Hauptzeitraum. **„vorgezogen“**: mehr als 3 Tage davor.
- Bis 3 Tage ausserhalb gehört ein Spiel regulär zum Spieltag, z. B. LaLiga Freitag bis Montag oder Dienstag.

### 3.4 Spalte `Termin` (S2)

| Wert | Erkennung | Anzeige |
|---|---|---|
| `bestätigt` | Normalfall | „Fr 20.11. · 20:30“ |
| `Zeit offen` | API-Status TBD (je Spiel) | „Sa 06.12. · Zeit offen“ |
| `vorläufig` | **alle** Spiele des Spieltags haben denselben Termin **und** dieser liegt **mehr als 14 Tage** in der Zukunft | „Wochenende 06./07.02. · Termin offen“ |

- Die 14-Tage-Grenze verhindert, dass der echte letzte Spieltag mit gleichzeitigen Anstössen als Platzhalter gilt. Die Ligen legen die Zeiten 3–10 Wochen im Voraus fest (Daten 2026/27).
- Gemischte Spieltage: Jedes Spiel wird einzeln eingestuft (TBD je Spiel). Die Platzhalterregel gilt nur, wenn **alle** Spiele denselben Termin haben.
- Was die API liefert: Datum, Uhrzeit, Status. „vorläufig“ ist eine eigene Ableitung und wird so dokumentiert.

### 3.5 Zuordnung Spielplan ↔ Datenbank (S6)

| Spiele | Verknüpfung |
|---|---|
| ab 15.11.2026 neu importiert | `id` in der Datenbank **ist** die API-Spiel-ID |
| bis 15.11.2026 (Altbestand, eigene IDs) | **feste, einmal geprüfte Zuordnungsdatei** eigene ID ↔ API-ID (aus dem Vollvergleich: alle 11'568 Spiele 2018/19–2025/26, geprüft über Datum, Teams und Ergebnis; dazu einmalig die Spiele 2026/27 bis zum Umstieg). Sie liegt versioniert im Projekt (rund 12'000 Zeilen, keine geheimen Daten) |
| Gegenprüfung | Saison + Heim + Gast muss zur ID passen. Widerspruch, doppelte ID oder ein Spiel ohne Zuordnung → **Fehler** im Bericht |

- Die Verknüpfung bleibt bei Terminänderungen stabil, weil die API-ID bei Verschiebungen gleich bleibt.
- Ein Wiederholungsspiel mit neuer API-ID fällt als „Paarung doppelt“ auf und wird von Hand entschieden.

### 3.6 Zwei Saisons im Spielplan

- Der Spielplan enthält die **aktuelle Saison und die Vorsaison**. Das sind 4 Abfragen mehr pro Lauf.
- Beide Saisons durchlaufen dieselben Regeln und Prüfungen.

### 3.7 Laufplan

- **Täglich um 04:00** (Europe/Zurich). Montags alle API-Spiele der Saison neu prüfen, sonst die letzten 2 Spieltage.
- Ein neuer Lauf ersetzt die wartende Fassung. Eine Freigabe am Wochenende ist nicht nötig.
- Folge in der Testphase: Ein am Samstag verschobenes Spiel erscheint erst nach der Freigabe am Montag (akzeptiert).

### 3.8 Zeitzone

- Die API wird mit `timezone=Europe/Zurich` abgefragt und liefert die Zeit mit Schweizer Versatz (Sommer- und Winterzeit).
- Alle Datumsvergleiche und Tagesgrenzen gelten in Europe/Zurich.
- „Heute“ und „jetzt“ werden immer in Europe/Zurich bestimmt.

### 3.9 Freigabe

- **Eine Freigabe für Ergebnisse und Spielplan gemeinsam.**
- Im Reiter werden beide Teile getrennt dargestellt (Abschnitt 5).

### 3.10 Prüfregeln (`app/core/fixtures.py`)

- Die neuen Spalten `API-Status`, `Hinweis` und `Termin` sind optional; ein alter Spielplan bleibt lesbar.
- Ungültige Werte sind Fehler.
- Neue Warnung: „NS mit vergangenem Termin“.
- Alle bisherigen Prüfungen bleiben.

### 3.11 Einmaliger Effekt

- Rund 10–15 Spiele wechseln von „verschoben“ zu „geplant“ mit Vermerk und bekommen erstmals KPIs.
- Ein Vollvergleich vorher/nachher belegt, dass sich sonst nichts ändert.

---

## 4. Anzeige (Ligaseiten, Top Anomalien, später öffentliche Website)

Die ganze Logik steht als reine Funktionen in `app/core/anzeige.py` (anstehender Spieltag auch in `app/core/matchday.py`), mit „jetzt“ und dem Tag des letzten erfolgreichen Importlaufs als Parameter. Dashboard und Website verwenden **dieselben Funktionen**.

### 4.1 Begriffe

- **Reguläres Spiel:** Spielplan-Status geplant, ohne Hinweis.
- **Sonderspiel:** Nachholspiel oder vorgezogenes Spiel.
- **Ende eines Spieltags:** Tagesende (23:59 Europe/Zurich) des letzten Tages mit einem regulären Spiel. Sonderspiele und Spiele mit anderem Status zählen nicht.
- **Anstehender Spieltag:** der Spieltag mit dem frühesten Termin, dessen Ende noch nicht erreicht ist.

### 4.2 Sichtbarkeit auf der Ligaseite

1. Der **anstehende Spieltag** bleibt sichtbar **bis zum Tagesende seines letzten regulären Spieltags**:
   - Freitag bis Sonntag: bis Sonntagabend.
   - LaLiga Freitag bis Montag oder Dienstag: bis Montag- bzw. Dienstagabend.
   - Englische Woche: bis Mittwochabend.
2. **Gespielte Spiele** bleiben bis dahin im Abschnitt, mit Ergebnis.
3. **Weitere Spieltage**, deren erstes reguläres Spiel **heute bis heute + 6** stattfindet, erscheinen als eigene Abschnitte (O2). Bei drei Spieltagen sind es drei Abschnitte.
4. **Sonderspiele** erscheinen ab 7 Tagen vor ihrem Termin als eigener Abschnitt unter ihrer **ursprünglichen Spieltagsnummer**, mit Vermerk. Sie verschwinden nach ihrem Tagesende.
5. **Verschoben (ohne Termin), abgesagt, abgebrochen, gewertet:** Diese Spiele erscheinen nicht als kommend. Beim Blättern stehen sie in ihrem Spieltag mit Vermerk.
6. **Reihenfolge der Abschnitte: zeitlich** nach dem frühesten Spiel. Bei gleichem Termin entscheidet die Spieltagsnummer, die immer die offizielle bleibt (S3).
   - Beispiel LaLiga am 01.12.: zuerst „Spieltag 23 · vorgezogen · Mi 02.12.“, dann „Spieltag 15 · So 06.12.“.
7. Innerhalb eines Abschnitts: nach Datum, dann Anstoss.

### 4.3 Pausen und Saisonende (O1, S9, S10)

| Situation | Anzeige |
|---|---|
| Nächster Spieltag in **höchstens 14 Tagen** (genau 14 eingeschlossen) | der nächste Spieltag, ohne Pausenhinweis |
| Nächster Spieltag **mehr als 14 Tage** entfernt, die Pause schliesst den **25.12.** ein | „**Winterpause** – nächster Spieltag am …“; ab 14 Tagen vorher zusätzlich der Spieltag |
| Nächster Spieltag mehr als 14 Tage entfernt, sonst | „**Spielpause** – nächster Spieltag am …“ (keine unbelegte Bezeichnung als Länderspielpause); ab 14 Tagen vorher zusätzlich der Spieltag |
| Letzter Spieltag beendet, aber ein Spiel der Saison noch offen oder angesetzt | **keine** Sommerpause; das offene Spiel wird normal gezeigt |
| Alle Spiele der Saison gespielt, neue Saison ohne angesetztes Spiel | „**Sommerpause**“ + letzter Spieltag der alten Saison mit Ergebnissen |
| Neue Saison mit angesetzten Spielen, Start in mehr als 14 Tagen | „**Sommerpause – Saisonstart am …**“ + letzter Spieltag der alten Saison |
| Neue Saison, 1. Spieltag in höchstens 14 Tagen | 1. Spieltag; die neue Saison ist jetzt Standard |

- **Datenstand (S9):** Pausen- und Sommerpausenhinweise erscheinen nur, wenn der **letzte erfolgreiche Importlauf höchstens 3 Tage** zurückliegt. Sonst steht stattdessen „Spielplan zuletzt aktualisiert am …“, auch während der Saison.
  - **Ab 0.20 (Entscheidung Carsten 19.11.2026): Grenze 48 Stunden statt 3 Tage.** Daten bis 48 Stunden alt gelten als aktuell (ein ausgefallener Tag löst keinen Hinweis aus). Liegt der letzte erfolgreiche Importlauf **mehr als 48 Stunden** zurück, erscheint auf Website und Dashboard der Hinweis „Spielplan zuletzt aktualisiert am …“, und Pausenhinweise entfallen. Intern meldet der E-Mail-Alarm (0.21) schon den ersten fehlgeschlagenen Lauf.
- **Saisonwechsel (S10):** Die neue Saison wird Standard, sobald sie mindestens ein angesetztes Spiel hat. Die Vorsaison bleibt über die Pfeile erreichbar.
- Erwartung 2026/27:
  - Die Bundesliga zeigt ab 21.12. den Hinweis „Winterpause – nächster Spieltag am Fr 08.01.“ und ab 25.12. zusätzlich Spieltag 15.
  - Serie A und LaLiga zeigen direkt den nächsten Spieltag; die Premier League hat keine Pause.

### 4.4 Navigation

- **Zurück:** alle Spieltage der aktuellen Saison und der Vorsaison.
- **Vorwärts:** höchstens 2 Spieltage über den anstehenden hinaus.

### 4.5 „Werte ab …“ (S8)

- KPI-Werte erscheinen erst, wenn **beide Teams ihr vorheriges Ligaspiel gespielt haben** und das Ergebnis in der gültigen Datenbank steht.
- **Vorheriges Spiel** = das zeitlich letzte Ligaspiel vor dem Anstoss, nach echtem Termin, nicht nach Spieltagsnummer.
- **„Werte ab <Datum>“** = der Tag nach dem späteren der beiden vorherigen Spiele (Import um 04:00). Im halbautomatischen Betrieb nach der Freigabe.
- **Beispiel:** Spieltag 12 am Sa 05.12., Spieltag 13 am Di 08.12. Am Fr 04.12. zeigt Bayern – Köln (Sp. 13) „Werte ab So 06.12.“.
- **Aufsteiger und fehlende Werte:** wie bisher. Die Datenbasis (Spiele je Team) wird gezeigt, bei unter 10 Spielen mit „vorläufig“. Es entstehen keine künstlichen Werte.
- Die Rechenregeln (KPI-Regelwerk) bleiben unverändert. Entschieden wird nur, **wann** Werte angezeigt werden.

### 4.6 Spalte „Datum“ in der Spieltagsübersicht

| Fall | Anzeige |
|---|---|
| kommend, bestätigt | „Fr 20.11. · 20:30“ |
| Zeit offen | „Sa 06.12. · Zeit offen“ |
| vorläufig | „Wochenende 06./07.02. · Termin offen“ |
| angepfiffen, bis Anpfiff + 2 Stunden (seit 0.20) | wie kommend („Fr 20.11. · 20:30“), nichts Zusätzliches |
| gespielt | „Fr 20.11. · 2:1“ (Ergebnis aus der Datenbank) |
| ab Anpfiff + 2 Stunden, Ergebnis noch nicht übernommen | „Fr 20.11. · Gespielt“ (seit 0.20; bis 0.19.1 ab dem Anstoss „Ergebnis folgt“); ohne Anstosszeit ab Mitternacht nach dem Spieltag |
| verschoben / abgesagt / abgebrochen / ausgesetzt / gewertet | der jeweilige Status |

Dazu kommen die Vermerke „Nachholspiel“ und „vorgezogen“ am Spiel.

### 4.7 Top Anomalien (S4, S7)

- **Je Liga ein Block: der zeitlich nächste.**
  - Normal ist das der anstehende Spieltag; in einer englischen Woche unter der Woche nur dieser.
  - **Sonderspiele, die in die Tage dieses Spieltags fallen, gehören zum Block.** Beispiel: Spieltag 15 Fr–So plus ein Nachholspiel von Spieltag 1 am Sonntag ergibt einen Block mit 11 Spielen. Auf der Ligaseite sind es dagegen zwei Abschnitte (Sp. 15 und Sp. 1).
  - Sonderspiele **vor** dem nächsten Spieltag bilden einen eigenen Block bis zu ihrem Tagesende. Beispiel LaLiga: am 01./02.12. die zwei vorgezogenen Spiele von Spieltag 23, ab 03.12. Spieltag 15.
- ~~**Nur Spiele vor dem Anpfiff:** Ein Spiel verschwindet zur geplanten Anstosszeit aus den Top Anomalien.~~ Bis 0.19.1; seit 0.20 siehe unten. Es gibt keine Live-Daten. Auf der Ligaseite bleibt es mit Ergebnis.
- Eine Liga nimmt teil, wenn ihr Block **höchstens 14 Tage** entfernt ist. Sonst steht in der Kopfzeile z. B. „Bundesliga: Winterpause bis 07.01.“.
- Spiele ohne Werte (4.5) nehmen nicht teil. Jedes Spiel kommt genau einmal vor.

**Ab 0.20 (Entscheidung Carsten 19.11.2026): Gespielte Spiele bleiben stehen.** Die Top-Anomalien-Liste eines Blocks wird vor dem ersten Anpfiff festgelegt und bleibt, bis der Block endet. Gespielte Spiele bleiben auf ihrem Platz, **ausgegraut** und mit **„Gespielt“** markiert, nach dem Import mit dem **Endstand**; es rückt kein anderes Spiel nach. Kein Live-Status, kein „Ergebnis folgt“. Gilt gleich für Dashboard und Website (Startseite, Spieltag-Seite, Matchdetail). Ersetzt die Regel „nur Spiele vor dem Anpfiff“ und Testfall A23. Präzisierung (Carsten 19.11.2026): **bis Anpfiff + 2 Stunden** normal ohne Beschriftung (während des Spiels nichts), **ab Anpfiff + 2 Stunden** ausgegraut mit „Gespielt“, **ab Import des Endstands** ausgegraut mit Endstand. Sichtbarkeit: reguläre Spiele bis zum Ende ihres Spieltags (Abend des letzten regulären Spiels), Sonderspiele bis zu ihrem eigenen Tagesende, Top Anomalien bis zum Ende des Blocks (4.2, 4.7).

### 4.8 Festlegungen bei der Umsetzung (Version 0.16)

Wo die Abschnitte 4.1–4.7 offen liessen, wie etwas genau gilt, ist es so umgesetzt (Tests `tests/test_anzeige.py`):

| Punkt | Umsetzung |
|---|---|
| Pause | Abstand zwischen dem Ende des letzten beendeten Spieltags und dem ersten Tag des nächsten **mehr als 14 Tage**. Die Box steht während der ganzen Pause, ab 14 Tagen vor dem Spieltag zusammen mit ihm (Entwurf C) |
| Sonderspiele | erscheinen im selben Fenster wie weitere Spieltage: Termin heute bis heute + 6. Ohne weiteren regulären Spieltag der Saison (4.3, „ein Spiel noch offen“) erscheinen sie unabhängig vom Abstand |
| „Gespielt“ | seit 0.20 ab Anpfiff + 2 Stunden, ohne bekannte Uhrzeit (Zeit offen, alter Spielplan) ab Mitternacht nach dem Spieltag (bis 0.19.1: ab dem Anstoss bzw. Tagesende, „Ergebnis folgt“). Mit Ergebnis in der Datenbank immer „gespielt“. „Status offen“ (3.1) erscheint nur im Bericht des Imports |
| „Werte ab“ | genannt werden nur Teams, deren Vorspiel heute oder später ist; beide im selben Spieltag: „beide Teams spielen vorher noch (Spieltag N)“. Lag das fehlende Vorspiel an einem früheren Tag: „Werte folgen, sobald das Ergebnis vom … übernommen ist“. Verschobene, abgesagte, abgebrochene, ausgesetzte und gewertete Spiele zählen nicht als Vorspiel. Ergebnis gesucht über Saison + Heim + Gast |
| Letzter erfolgreicher Importlauf (S9) | neuester Lauf in `/import/laeufe/`, dessen Status nicht „fehlgeschlagen“ oder „Fehler – nicht übernehmbar“ ist; massgebend ist seit 0.20 sein **Beginn mit Uhrzeit** (`core/importstand.py`, für Dashboard und Website), veraltet nach mehr als 48 Stunden. Ohne Lauf: Box „Spielplan zuletzt aktualisiert am unbekannt“ |
| „Ein Spiel der Saison noch offen“ (4.3) | angesetzt heute oder später, oder verschoben bzw. ausgesetzt |
| Pfeile ohne Auswahl | ◀ zum Spieltag vor dem anstehenden; ▶ zum anstehenden, wenn er (noch) nicht als Abschnitt erscheint, sonst zum nächsten. Schaltfläche „Zu den kommenden Spielen“ zurück |
| Top Anomalien, Sonderspiele davor | Block = die Sonderspiele des frühesten Tages; Kopfzeile bis Tagesende, nach dem letzten Anpfiff „alle Spiele angepfiffen“ (ebenso beim Spieltag) |
| Kopfzeile in der Pause | „Winterpause bis 07.01.“ bzw. „Spielpause bis …“, „Sommerpause“; bei altem Datenstand „nächster Spieltag am …“ |
| Termin „vorläufig“ | „Wochenende 06./07.02. · Termin offen“ für Samstag/Sonntag, sonst „Di 12.01. · Termin offen“ |
| Abschnitt mit nicht gezeigten Spielen | Hinweis in der Kopfzeile, z. B. „(1 Spiel verschoben – beim Blättern sichtbar)“ |

---

### 4.9 Statusmodell und Schnappschuss (seit 0.20, Entscheidungsprotokoll 19.11.2026 Nr. 1–2a, 4a)

**Prüfreihenfolge je Spiel:** Status → gespielt → „Werte ab …“ → zu wenig Daten → Signalqualität.

| Zustand | Regel | Umsetzung |
|---|---|---|
| Ausschliessender Status | verschoben, abgesagt, abgebrochen, ausgesetzt, gewertet: keine Werte, nie ein Endstand | wie bisher |
| **Absicherung „gewertet“** | „Am grünen Tisch gewertet“ nur für nie gespielte Spiele. Meldet die API AWD/WO für ein Spiel, dessen Ergebnis vom Platz in der Datenbank steht, bleibt es gespielt mit diesem Ergebnis (Status „geplant“, Hinweis „Gewertet, aber gespielt“ in der Datenqualität) | `core/fixtures._awarded_but_played` beim Einlesen; die Datei bleibt unverändert |
| Gespielt | ab Anpfiff + 2 Stunden bzw. ohne Anstosszeit ab Mitternacht nach dem Spieltag ausgegraut mit „Gespielt“, nach dem Import mit Endstand; bis dahin normal, kein Live-Status | `anzeige.played_from`, `is_played`, `date_cell` |
| „Werte ab …“ | wie 4.5; nach dem Anstoss nie | `anzeige.values_from` (Datum für die Website, Text für das Dashboard), `missing_previous` |
| Zu wenig Daten | alle 8 Kennzahlen vorläufig oder keine Werte (bis 0.19.1 „nicht gewertet“) | Website |
| Top Anomalien | der Block enthält alle Spiele; die Liste steht vor dem ersten Anpfiff fest, gespielte bleiben ausgegraut, keines rückt nach (4.7) | `anzeige.top_block`, `core/top.Candidate.played` |

**Schnappschuss je Spiel** (`core/schnappschuss.py`, Lauf `importer/schnappschuss.py`):

- **Wann:** Der Container `soccer-import` prüft einmal je volle Stunde (und sofort nach jeder Übernahme) alle angesetzten Spiele der laufenden Saison und der Vorsaison mit API-ID, deren Anpfiff höchstens eine Stunde entfernt oder schon vorbei ist. Ohne Anstosszeit gilt der Anstoss wie überall als 23:59.
- **Was:** alle KPI-Ergebnisse, wie Dashboard und Website sie zeigen (Teamwerte, Ligareferenz, Formkurve, Einstufung mit Schwellen und Signalqualität), verlustfrei (Brüche als Text), mit Formatnummer, App-Version, Prüfsummen von Datenbank und Schwellen.
- **Unveränderlich:** eine Datei je Spiel, `/import/schnappschuesse/<liga>/<saison>/<API-ID>.json`; sie wird einmal angelegt und nie überschrieben.
- **Wartet** auf die Ergebnisse der vorherigen Spiele beider Teams (4.5). Fehlt der Schnappschuss beim Anstoss, wird er nachgeholt, sobald es geht, und als **nachträglich** markiert. So entstehen beim ersten Lauf auch die Schnappschüsse aller gespielten Spiele beider Saisons.
- **Anzeige:** vor dem Anstoss die aktuell berechneten Werte; ab dem Anstoss die des Schnappschusses („Die Werte wurden mit den Daten vor dem Spiel berechnet.“). Fehlt er: nachträglich mit den Daten vor dem Spiel berechnet, mit Hinweis; fehlt dazu noch ein Vorspiel-Ergebnis, keine Werte, bis er nachgeholt ist.
- **Korrekturen:** Das erste Ergebnis eines Spiels wird einmal festgehalten (`<API-ID>.ergebnis.json`). Weicht die Datenbank später ab (Korrekturen der Quelle bis 7 Tage), zeigt die Seite den neuen Endstand und „Ergebnis nachträglich korrigiert“; die Werte bleiben.
- **Überwachung:** Stand des letzten Laufs in `/import/schnappschuesse/stand.json` und im Reiter Datenimport/API (neu, nachträglich, wartend, Fehler; rot nach einem Fehler oder wenn der letzte Lauf älter als 2 Stunden ist). E-Mail-Alarm ab 0.22.
- **Bekannte Einschränkungen:** Ein Spiel, das nach dem ersten Anpfiff des Blocks noch verschoben wird, fällt aus den Top Anomalien (es hat keine Werte mehr); ein abgebrochenes oder abgesagtes Spiel zeigt bis zum nächsten Import „Gespielt“.

## 5. Reiter „Datenimport/API“ (Entwurf 2 vom 15.11.2026)

- **Statusleiste:** „nächster Lauf … · täglich“.
- **Kasten „Neue Daten bereit“** mit zwei Blöcken:
  - **A · Ergebnisse (Datenbank):** Vollständigkeit, Korrekturen alt → neu, neue Spiele, Qualität.
  - **B · Spielplan**, gruppiert: verschoben · Nachholspiel (neuer Termin) · vorgezogen · Termin geändert · ausgesetzt/abgesagt/abgebrochen/gewertet · neu oder entfallen · Anstosszeit geändert · **Anstosszeiten festgelegt** (eingeklappt, zählt nicht als wichtige Änderung).
- **„So sieht das Dashboard nach der Übernahme aus“:** je Liga der angezeigte Spieltag, Spiele, Block für Top Anomalien, sichtbar bis (seit 0.16; berechnet mit dem neuen Spielplan und denselben Funktionen wie die Ligaseite).
- **Ein Button „Übernehmen (Ergebnisse und Spielplan)“** und „Verwerfen“.
- **Protokoll:** Spielplan als „wichtig · Anstosszeiten“. Das Datum des letzten erfolgreichen Laufs ist die Grundlage für S9.

---

## 6. Unverändert und abgegrenzt

- KPI-Formeln, Schwellen, Regelwerk, Stichtag-Regel (`Datum von`), 2-Tage-Regel.
- **Architektur:** zwei Container. `football-dashboard` liest nur; `soccer-import` holt, erzeugt, prüft und tauscht nach Freigabe. Es gibt eine wartende Fassung, Backup und Tausch in einem Schritt. Daran ändert sich nichts.
- Keine neuen API-Abfragen ausser der Spielliste der Vorsaison.
- Historische Daten werden nicht verändert.
- Kein neues Dashboard-Design. Neu sind Abschnitte, die Datumsspalte, Vermerke und Hinweise; dazu kommt vorher ein Designentwurf.
- Alle bestehenden Tests bestehen weiter.

---

## 7. Testfälle (automatisch, ohne Netz, mit festen Daten und Ausschnitten echter API-Antworten)

### 7.1 Import

| Nr. | Situation | Erwartet |
|---|---|---|
| I1 | PST | verschoben, API-Status PST, Datum = Termin laut API, keine KPIs |
| I2 | Nachholspiel: NS, 10 Tage nach dem Hauptzeitraum | geplant, Hinweis „Nachholspiel“, Spieltagsnummer unverändert |
| I3 | Vorgezogen (echt: LaLiga Sp. 23, 02.12.2026) | geplant, Hinweis „vorgezogen“ |
| I4 | Gespieltes Nachholspiel (echt: LaLiga Sp. 1, FT 27.08.) | **nicht** verschoben, bekommt KPIs (Regressionstest) |
| I5 | Platzhalter: alle Spiele „Sa 15:30“, mehr als 14 Tage entfernt | Termin `vorläufig` |
| I6 | **Letzter Spieltag**: alle gleichzeitig, in 5 Tagen (Z3) | Termin `bestätigt` |
| I7 | Gemischt: ein Spiel TBD, Rest bestätigt (Z4) | je Spiel richtig eingestuft |
| I8 | SUSP und INT (Z1) | ausgesetzt bzw. geplant mit Anzeige „unterbrochen“ |
| I9 | AWD und WO (Z2) | Status gewertet, keine KPI-Werte |
| I10 | CANC, ABD | abgesagt bzw. abgebrochen |
| I11 | NS mit Termin vor 3 Tagen (Z5) | Warnung, Anzeige „Status offen“ |
| I12 | Zwei gleich grosse Fenster (Z6) | früheres Fenster ist Hauptzeitraum |
| I13 | Spieltag ohne reguläre Spiele | kein Hauptzeitraum, keine Vermerke |
| I14 | LaLiga Fr–Mo bzw. Fr–Di | alle regulär |
| I15 | Nur die Anstosszeit ändert sich | Gruppe „Anstosszeit geändert“, keine Warnung |
| I16 | Platzhalter wird zu echter Zeit | „Anstosszeiten festgelegt“ |
| I17 | Zuordnung Vorsaison über die Zuordnungsdatei (Z9) | jedes Spiel genau einem Datensatz zugeordnet; Widerspruch → Fehler |
| I18 | Terminänderung eines bekannten Spiels (Z11) | Zuordnung über die API-ID stabil; Änderung im Bericht |
| I19 | Zeitstempel UTC 23:30 = Schweiz 00:30 Folgetag (Z10) | Schweizer Datum |
| I20 | Neue Spalten mit ungültigem Wert; alter Spielplan ohne Spalten | Fehler bzw. weiterhin lesbar |
| I21 | Zwei Saisons im Spielplan; Saisonwechsel der API | beide geprüft; kein Datenverlust |
| I22 | Vollvergleich der KPIs vorher/nachher | alle bisherigen Werte gleich; neue nur bei früher „verschobenen“ Sonderspielen |

### 7.2 Anzeige

| Nr. | Situation (heute = …) | Erwartet |
|---|---|---|
| A1 | Spieltag Fr–So; heute Fr, Sa, So, Mo | Fr–So dieser Spieltag; Mo der nächste |
| A2 | Sonntag, Freitagsspiel gespielt | bleibt mit Ergebnis im Abschnitt |
| A3 | LaLiga Fr–Mo; heute Mo bzw. Di | Mo sichtbar; Di der nächste |
| A4 | Englische Woche Sa Sp. 12 / Di Sp. 13 | Sa zwei Abschnitte (13 mit „Werte ab …“); Mo nur 13 mit Werten; bis Mi abends |
| A5 | Drei Spieltage beginnen heute bis heute + 6 (echt: Bundesliga 08.–17.01.2027; Z12) | drei Abschnitte |
| A6 | Spiel an Tag heute + 6 bzw. heute + 7 | Abschnitt bzw. noch nicht |
| A7 | Nachholspiel in 5 bzw. 10 Tagen | Abschnitt unter dem ursprünglichen Spieltag bzw. noch nicht |
| A8 | Vorgezogen (echt: LaLiga 02.12.), heute 01.12. | Reihenfolge: zuerst Sp. 23, dann Sp. 15 |
| A9 | Zwei Spieltage am selben Tag | zwei Abschnitte, nach Spieltagsnummer |
| A10 | Zeit offen bzw. vorläufig | Anzeige wie 4.6, nicht verschoben |
| A11 | PST, ABD, SUSP, gewertet | nicht unter „kommend“; beim Blättern mit Vermerk |
| A12 | Pause 12 Tage (echt: 08.11. → 20.11.) | nächster Spieltag, kein Hinweis |
| A13 | Bundesliga-Winterpause (20.12. → 08.01.) | 21.–24.12. nur Hinweis; ab 25.12. Hinweis und Spieltag 15 |
| A14 | Lange Pause im September (18 Tage) | „Spielpause – nächster Spieltag am …“; ab 14 Tagen vorher mit Spieltag |
| A15 | Genau 14 Tage bis zum nächsten Spieltag | Spieltag wird gezeigt |
| A16 | Letzter Spieltag vorbei, ein Nachholspiel offen | keine Sommerpause |
| A17 | Alle Spiele gespielt, neue Saison ohne angesetztes Spiel | „Sommerpause“ + letzter Spieltag |
| A18 | Neue Saison, Start in 30 bzw. 14 Tagen | „Sommerpause – Saisonstart am …“ bzw. 1. Spieltag als Standard |
| A19 | Letzter erfolgreicher Lauf vor 4 Tagen (Z8) | keine Pausen- oder Sommerpausenmeldung, stattdessen „Spielplan zuletzt aktualisiert am …“ |
| A20 | Navigation | zurück alle Spieltage beider Saisons; vorwärts genau 2 |
| A21 | Team hat sein vorheriges Spiel noch nicht gespielt | keine Werte, „Werte ab <Tag nach dem späteren Spiel>“ |
| A22 | Vorheriges Spiel ist ein Nachholspiel mit höherer Spieltagsnummer-Reihenfolge | massgebend ist der echte Termin |
| A23 | Top Anomalien: Freitagsspiel beendet, Samstag offen (Z7) | seit 0.20: Freitagsspiel bleibt im Block (ausgegraut), „noch 2 Spiele“; bis 0.19.1 nur noch auf der Ligaseite |
| A24 | Top Anomalien: Spieltag 15 + Nachholspiel Sp. 1 am selben Wochenende | ein Block mit 11 Spielen; Ligaseite zwei Abschnitte |
| A25 | Top Anomalien: Block in 20 bzw. 14 Tagen | ausgeschlossen mit Hinweis bzw. dabei |
| A26 | Tagesgrenze: Spiel So 21:00 | bis So 23:59 sichtbar, Mo nicht mehr |
| A27 | Echte Saisonlisten aller vier Ligen 2026/27, mehrere Stichtage | erwartete Abschnitte und Hinweise |
| A28 | Letzter erfolgreicher Lauf vor genau 48 Stunden bzw. 48 Stunden und 1 Minute (0.20) | aktuell bzw. veraltet |
| A29 | Anstoss 15:30: 15:29, 15:30, 17:29, 17:30 (0.20) | bis 17:29 Termin, ab 17:30 „Gespielt“; mit Ergebnis der Endstand |
| A30 | Ohne Anstosszeit (Zeit offen bzw. leer) (0.20) | „Gespielt“ ab Mitternacht nach dem Spieltag |
| A31 | Verschobenes Spiel; Ergebnis vor Anpfiff + 2 h (Zeitreise) (0.20) | nie gespielt; mit Ergebnis sofort gespielt |
| A32 | „Werte ab“ als Datum und nach dem Anstoss (0.20) | Datum bzw. „Ergebnis vom“; ab dem Anstoss nie |
| A33 | API meldet „gewertet“ für ein gespieltes Spiel (0.20) | bleibt gespielt mit Ergebnis vom Platz, Hinweis in der Datenqualität |
| SN1–SN10 | Schnappschuss (`tests/test_schnappschuss.py`, 0.20) | genau gespeichert, nie überschrieben, Lauf je Stunde, Warten, nachträglich, Korrektur, Anzeige vor/nach dem Anstoss |

---

## 8. Umsetzung in Schritten

| Schritt | Inhalt | Prüfung |
|---|---|---|
| 1. Import (0.15) | Status, Spalten `API-Status`/`Hinweis`/`Termin`, Zuordnungsdatei, Vorsaison, täglicher Lauf, gruppierter Bericht, Prüfregeln; dazu die Punkte aus der Spezifikation Ergebnis-Import | I1–I22, Vollvergleich, Probelauf mit echter API, Freigabe im Reiter |
| 2. Designentwurf | Ligaseite (Abschnitte, Datumsspalte, Hinweise), Top Anomalien | Freigabe Carsten |
| 3. Rechenkern Anzeige | Sichtbarkeit, Abschnitte, Pausen, Datenstand, Navigation, „Werte ab“, Top-Anomalien-Block | A1–A27 |
| 4. Oberfläche (0.16) | Ligaseiten, Top Anomalien, Reiter (Blöcke A/B) | Seitentests, Browser |
| 5. Doku | `04` (Abschnitt 6 und 3-Tage-Regel ersetzt), `05`, `06`, CHANGELOG, RELEASE | – |

---

## 9. Entscheidungen (Carsten, 15.11.2026)

| Nr. | Entscheidung |
|---|---|
| S1 | Original-Status speichern; Anzeige und KPI-Berechtigung nach Tabelle 3.1 |
| S2 | drei Terminfälle; „vorläufig“ nur bei gleichem Termin **und** mehr als 14 Tagen |
| S3 | Abschnitte zeitlich, bei Gleichstand nach Spieltagsnummer |
| S4 | Ligaseite nach ursprünglichem Spieltag; Top Anomalien nach zeitlichem Block |
| S5 | Gleichstand → früheres Fenster; ohne reguläre Spiele kein Hauptzeitraum |
| S6 | feste, geprüfte Zuordnungsdatei eigene ID ↔ API-ID |
| S7 | Top Anomalien nur vor dem Anpfiff (seit 0.20: Liste steht vor dem ersten Anpfiff fest, gespielte bleiben ausgegraut, 4.7) |
| S8 | „Werte ab“ = Tag nach dem späteren der beiden vorherigen Spiele (nach echtem Termin) |
| S9 | Pausen- und Sommerpausenhinweise nur bei Lauf höchstens 3 Tage alt (ab 0.20: höchstens 48 Stunden) |
| S10 | neue Saison wird Standard ab dem ersten angesetzten Spiel; in der Sommerpause Hinweis und letzter Spieltag |
| O1 | einheitlich mehr als 14 Tage; „Winterpause“ (inkl. 25.12.) oder „Spielpause“ |
| O2 | weitere Spieltage heute bis heute + 6 automatisch als Abschnitt |
| früher | eine Freigabe; täglicher Lauf; Navigation vorwärts 2; Datumsspalte mit Ergebnis; Sichtbarkeit bis Tagesende des letzten regulären Spieltags |

**Gewertete Spiele** (entschieden 15.11.2026, R2): nicht in die Datenbank, nicht in die Formkurve; Spielplan-Status `gewertet` (`06`, Abschnitt 10.1).
