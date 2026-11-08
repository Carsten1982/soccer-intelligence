# Soccer Intelligence – Dashboard-Briefing

**Version 4.7** · Stand 08.11.2026 (H.1: Anteile kaufmännisch gerundet, Architektur-Hinweis)

> **Massgebliche Quelle seit 31.10.2026.** Änderungen werden nur noch in dieser Datei gemacht, mit Datum in der Änderungshistorie bzw. im `CHANGELOG.md`.
> Das Word-Dokument *Dashboard-Briefing v4.2* liegt nur noch als Archiv im Ordner `word/` und wird nicht mehr gepflegt. Änderungen seit 31.10.2026 sind im Text als „Änderung“ mit Datum gekennzeichnet.
>
> Zusammenspiel der Dokumente: Berechnungen → `03_KPI_Regelwerk.md` · Spielplan → `04_Spielplan.md` · Aufbau, Navigation und Darstellung des Dashboards → diese Datei.

## 1. Projektziel

Wir entwickeln das interne Dashboard von Soccer Intelligence weiter.

Das Dashboard dient dazu, Fussballspiele anhand definierter KPIs statistisch zu analysieren und mögliche Auffälligkeiten (Anomalien) zu erkennen.

Im ersten Schritt steht die interne Analyse- und Qualitätssicherungsumgebung im Vordergrund. Die Berechnungen und Datenstrukturen sollen jedoch bereits so aufgebaut sein, dass später eine öffentliche Website darauf aufbauen kann.

**Wichtig:** Die KPI-Berechnungen und deren fachliche Regeln sind ausschliesslich im KPI-Regelwerk definiert. Das KPI-Regelwerk ist die Datei docs/03_KPI_Regelwerk.md. Es ist die verbindliche fachliche Grundlage. Die Berechnungslogik darf nicht eigenständig interpretiert, verändert oder durch alternative Formeln ersetzt werden.

Das Dashboard-Briefing definiert primär die technische Umsetzung, Navigation und Darstellung.

## 2. Architektur und URL-Struktur

Wir unterscheiden zwischen dem öffentlichen Bereich und dem internen Dashboard.

### 2.1 Öffentliche Website

Die öffentliche Website wird später unter folgender Domain erreichbar sein:

https://soccer-intelligence.com

Sie soll ausgewählte Analysen und statistische Auffälligkeiten für Besucher zugänglich machen.

Die geplante öffentliche Navigation umfasst drei Bereiche:

1.  Top Anomalien

2.  Bundesliga

3.  Premier League

Die öffentliche Website wird zu einem späteren Zeitpunkt separat gestaltet und umgesetzt.

### 2.2 Internes Dashboard

Das interne Dashboard ist unter folgender Adresse erreichbar:

<https://soccer-intelligence.com/dashboard>

Die Startseite <https://soccer-intelligence.com> zeigt bis zum Start der öffentlichen Website weiterhin die bestehende Platzhalterseite.

Das Dashboard ist eine einzige Anwendung mit mehreren Bereichen. Jeder Bereich hat eine eigene URL:

| **Bereich**                  | **URL**                   |
|------------------------------|---------------------------|
| Top Anomalien (Startbereich) | /dashboard                |
| Bundesliga                   | /dashboard/bundesliga     |
| Premier League               | /dashboard/premier-league |
| Serie A *(seit Etappe F)*    | /dashboard/serie-a        |
| LaLiga *(seit Etappe F)*     | /dashboard/laliga         |
| Datenqualität                | /dashboard/datenqualitaet |

Beim Aufruf von /dashboard wird direkt der Bereich Top Anomalien angezeigt. Eine eigene Adresse /dashboard/top und eine Weiterleitung sind nicht erforderlich.

Zu Beginn gab es vier Bereiche. **Änderung 07.11.2026 (Carsten):** Mit Etappe F kommen Serie A und LaLiga dazu, insgesamt also sechs Bereiche. Jede weitere Liga erhält nach demselben Muster einen eigenen Bereich. Welche Ligen aktiv sind, wird in der Konfiguration festgelegt und nicht im Programmcode.

### 2.3 Verhalten der Navigation

Die Navigation zeigt einen Tab pro Bereich, zu Beginn: Top Anomalien, Bundesliga, Premier League, Datenqualität.

- Ein Klick auf einen Tab öffnet den Bereich und aktualisiert die URL.

- Jeder Bereich ist direkt über seine URL aufrufbar.

- Beim Aktualisieren der Seite bleibt der aufgerufene Bereich erhalten.

- Die Browsernavigation (Zurück/Vorwärts) funktioniert korrekt.

- Der aktive Tab ist anhand der URL klar erkennbar.

- Eine unbekannte Adresse (z. B. /dashboard/xyz) zeigt den Hinweis „Seite nicht gefunden“ mit einem Link zu den Top Anomalien.

### 2.4 Sicherheit und Zugriffsschutz

Das gesamte Dashboard, also alle Adressen unter /dashboard, ist passwortgeschützt. Die Platzhalterseite unter soccer-intelligence.com bleibt öffentlich.

- Der Schutz erfolgt serverseitig vor der Anwendung (Passwortschutz über Traefik). Wer nicht angemeldet ist, erreicht weder die Seiten noch die Daten, auch nicht über den direkten Aufruf einer URL.

- Das Ausblenden von Menüpunkten oder nicht verlinkte Adressen gelten nicht als Schutz.

- Die Zugangsdaten werden ausschliesslich als Passwort-Hash in einer Konfigurationsdatei auf dem Server hinterlegt (z. B. .env). Das Klartextpasswort darf weder im Programmcode noch in Git oder in der Dokumentation gespeichert werden.

- Zu Beginn gibt es einen gemeinsamen Zugang. Weitere Benutzer können später ergänzt werden.

- Die Verbindung erfolgt ausschliesslich über HTTPS.

- Die Änderung betrifft nur den eigenen Container football-dashboard und eine neue, kleine Komponente für die Platzhalterseite. Traefik selbst, n8n und alle anderen Anwendungen bleiben unverändert. Die Umsetzung erfolgt erst nach separater Freigabe gemäss den Schutzregeln.

- Suchmaschinen: Alle Antworten unter /dashboard tragen zusätzlich den Hinweis „noindex, nofollow“.

*Umgesetzt in Etappe E (31.10.2026), freigegeben von Carsten. Technische Details: `docs/01_Technisches_Setup.md`, Abschnitte 3 und 4.*

## 3. Dashboard-Navigation und Design

Das Dashboard soll sich an den bereitgestellten Design-Screenshots orientieren.

Die Screenshots gelten nur für Layout und Design. Zahlen, Texte und Anomalie-Einstufungen darin sind Beispiele und nicht verbindlich. Massgeblich ist ausschliesslich das KPI-Regelwerk.

### 3.1 Grunddesign

- Heller, weisser Hintergrund

- Dunkelblaue Schrift für Überschriften und zentrale Informationen

- Dezente hellblaue bzw. graublaue Flächen für Tabellenzeilen

- Feine graublaue Trennlinien

- Klare Gruppierung der KPI-Bereiche

- Sachliches, übersichtliches und professionelles Erscheinungsbild

Das Dashboard ist ein Analysewerkzeug. Die Daten und deren Lesbarkeit stehen im Vordergrund.

### 3.2 Kopfbereich

Im oberen Bereich soll Folgendes angezeigt werden:

**Titel:** Soccer Intelligence

**Untertitel:** KPI-Übersicht pro Spiel – alle Begegnungen eines Spieltags

Rechts im Kopfbereich werden in den Liga-Bereichen Saison und aktueller Spieltag der jeweiligen Liga angezeigt (Regeln siehe 4.4), beispielsweise: «Saison 2026/27 · Spieltag 1». Im Bereich Top Anomalien wird der Spieltag pro Liga angezeigt, beispielsweise: «Bundesliga: Spieltag 1 · Premier League: Spieltag 1». Mit vier Ligen (Etappe F) steht diese Anzeige kompakt in zwei Spalten («Bundesliga: Spieltag 2» · «Premier League: Spieltag 2» / «Serie A: Spieltag 2» · «LaLiga: Spieltag 2»), auf schmalen Bildschirmen untereinander.

~~Es soll in der ersten Version keine zusätzliche Spieltagsnavigation mit Pfeilen oder weiteren Bedienelementen geben.~~

**Änderung 31.10.2026 (Carsten):** In den Liga-Bereichen lässt sich der Spieltag mit Pfeilen ◀ ▶ neben dem Spieltagsfeld wählen:

- Auswählbar sind alle Spieltage der Spielplan-Datei bis einschliesslich des aktuellen Spieltags (gemäss 4.4). Nicht in die Zukunft.
- Die Auswahl gilt je Liga getrennt.
- Der gewählte Spieltag steht in der Adresse, z. B. `/bundesliga?spieltag=1` (bei einer früheren Saison zusätzlich `&saison=2025-26`). Ohne Angabe oder bei ungültiger Angabe wird der aktuelle Spieltag angezeigt.
- Ist nicht der aktuelle Spieltag gewählt, heisst das Feld „Ausgewählter Spieltag“, und es gibt eine Schaltfläche „Zum aktuellen Spieltag“.
- Die KPIs werden wie immer so berechnet, als wäre der gewählte Spieltag noch nicht gespielt (Stichtag „Datum von“). Spätere Spiele fliessen nicht ein.
- Der Bereich Top Anomalien zeigt immer den aktuellen Spieltag und reagiert nicht auf die Pfeile.

**Änderung 31.10.2026 (Carsten):** Navigation als dunkelgraue Leiste mit weisser Schrift; aktiver Tab fett mit blauem Balken darunter, die übrigen Tabs in hellgrauer Schrift. Abstand zwischen Navigation und Überschrift deutlich verkleinert.

### 3.3 Hauptnavigation

Die Navigation besteht aus einem Tab pro Bereich. Zu Beginn sind das vier Tabs:

- Top Anomalien

- Bundesliga

- Premier League

- Datenqualität (ganz rechts)

Weitere aktivierte Ligen erhalten automatisch einen eigenen Tab. Dieser wird vor dem Tab Datenqualität eingefügt. Seit Etappe F (Änderung 07.11.2026): Top Anomalien · Bundesliga · Premier League · Serie A · LaLiga · Datenqualität.

Der aktive Tab muss visuell klar erkennbar sein.

Die Tabs müssen mit der oben definierten URL-Struktur verknüpft sein.

## 4. Liga-Bereiche (Bundesliga, Premier League, Serie A, LaLiga)

Die Liga-Bereiche zeigen jeweils alle Begegnungen des **aktuellen** Spieltags (siehe 4.4).

Die Darstellung erfolgt in einer breiten Tabelle.

Es sollen keine Anstosszeiten und keine Stadioninformationen angezeigt werden.

### 4.1 Tabellenstruktur

Die Tabelle enthält folgende Bereiche:

- Laufende Nummer

- Spielpaarung

- KPI01 Formkurve

- KPI02 Erwartete Tore

- KPI03 Over 2.5 Goals

- KPI04 Gelbe Karten

- Weitere KPIs gemäss späterer Erweiterung

Die KPI-Bereiche sollen visuell voneinander getrennt sein.

**Änderung 08.11.2026 (Carsten, beschlossen – gilt ab Etappe H):** Ziel ist eine **kompaktere Tabelle mit besserer Übersicht**. Mit KPI 05–09 (Ecken, Tore 1. HZ, Tore 2. HZ, Beide Teams treffen, Schüsse aufs Tor; Definitionen im KPI-Regelwerk, Abschnitt 9) wird die Tabelle **kompakt**:

- Je Begegnung eine Zeile mit Laufnummer, Spielpaarung, Formkurve (KPI 01) und je KPI 02–09 **Hauptwert und Anomalie-Punkt** (grau/gelb/rot), Kennzeichnung „V“ bei vorläufigen Werten.
- Alle Details einer Begegnung (je KPI: Teamwerte, Ligareferenz, Abweichung, Datenbasis inkl. Referenzspiele, Überschrift und Text) erscheinen **per Aufklappen** der Begegnung.
- Fixierte Spalten (# und Spiel), Legende und die übrigen Regeln aus 4.2–4.4 bleiben.
- Alle Zahlen mit **zwei Nachkommastellen** (KPI-Regelwerk 2.3, Entscheidung 08.11.2026).
- Ein Design-Vorschlag (Desktop und Handy) wird **vor** der Umsetzung vorgelegt und von Carsten abgenommen. Er dient zugleich als Vorlage für die spätere Website.

### 4.2 Fixierte Spalten

Die ersten beiden Spalten müssen beim horizontalen Scrollen dauerhaft sichtbar bleiben:

1.  \#

2.  Spiel

Das bedeutet:

- Die laufende Nummer bleibt links fixiert.

- Die Spielpaarung mit Heim- und Gastmannschaft bleibt ebenfalls links fixiert.

- Nur die nachfolgenden KPI-Spalten werden horizontal gescrollt.

Diese Funktion muss sowohl technisch als auch visuell sauber umgesetzt werden.

### 4.3 Horizontales Scrollen

Das Dashboard wird perspektivisch 8 bis 10 KPIs enthalten.

Deshalb sollen nicht alle KPI-Spalten auf eine Bildschirmbreite komprimiert werden.

Stattdessen:

- Die Tabelle erhält eine ausreichende Mindestbreite.

- Die KPI-Spalten behalten eine gut lesbare Breite.

- Horizontales Scrollen muss möglich sein.

- Eine sichtbare Scrollbar am unteren Tabellenrand soll die Navigation erleichtern.

- Das Scrollen soll mit Maus, Trackpad und Touch funktionieren.

Die ersten beiden Spalten bleiben dabei fixiert.

### 4.4 Spielplan und aktueller Spieltag

Welche Begegnungen angezeigt werden, steht ausschliesslich in der Datei data/Spielplan.xlsx (ein Tabellenblatt pro Liga, Blattname = Liganame). Die historische Datenbank wird dafür nicht verwendet. Der Aufbau der Datei ist in 04_Spielplan.md beschrieben.

Der aktuelle Spieltag wird **für jede Liga separat** bestimmt:

1.  Ein Spieltag gilt als beendet, sobald das späteste „Datum bis“ seiner Spiele vor dem heutigen Datum liegt (Zeitzone Europe/Zurich). Die Anzeige wechselt am Tag nach dem letzten Spiel.

2.  Angezeigt wird der Spieltag mit der niedrigsten Nummer, der noch nicht beendet ist.

3.  Sind alle Spieltage der Datei beendet, wird der letzte Spieltag der Datei angezeigt.

4.  Spiele mit Status „verschoben“ oder „abgesagt“ zählen nicht für die Frage, ob ein Spieltag beendet ist. Sie werden mit ihrem Status, aber ohne KPI-Werte angezeigt. Nachholspiele werden in Version 1 nicht separat angezeigt. *Ergänzt 07.11.2026:* Spiele, die mehr als 3 Tage ausserhalb des Hauptzeitraums ihres Spieltags liegen, werden im Spielplan bewusst als „verschoben“ gepflegt (Pflegeregel in `04_Spielplan.md`, Abschnitt 6). Die bestehende Logik bleibt unverändert.

5.  Die KPIs jeder Begegnung werden immer so berechnet, als wäre das Spiel noch nicht gespielt. Stichtag ist „Datum von“ der Begegnung im Spielplan (KPI-Regelwerk, Abschnitt 1). Das gilt auch, wenn der angezeigte Spieltag bereits gespielt ist.

6.  Teams ohne Ligadaten (z. B. Aufsteiger) werden angezeigt. Ihre KPI-Werte erscheinen gemäss KPI-Regelwerk als „--“.

7.  Fehler im Spielplan werden auf der Seite Datenqualität angezeigt: fehlende Pflichtfelder, ungültiges Datum, unbekannter Teamname, Team doppelt im selben Spieltag, weniger Spiele als erwartet (Anzahl Teams / 2).

8.  Die Begegnungen werden nach „Datum von“ sortiert, bei gleichem Datum in der Reihenfolge der Spielplan-Datei.

9.  Enthält die Datenbank oder der Spielplan einen Fehler (gemäss 02_Datenbasis.md bzw. 04_Spielplan.md), zeigen die Liga-Bereiche und der Bereich Top Anomalien statt der Tabelle einen Hinweis mit Link zum Bereich Datenqualität.

## 5. Bereich Top Anomalien

Der Bereich Top Anomalien (/dashboard) zeigt die auffälligsten Anomalien des aktuellen Spieltags aller aktiven Ligen. Er ist die Grundlage für die spätere Startseite der öffentlichen Website. Die Auswahl erfolgt deshalb zentral in der Berechnungslogik und nicht in der Oberfläche.

### 5.1 Auswahl-Logik

1.  Grundlage sind die Begegnungen des aktuellen Spieltags jeder aktiven Liga gemäss 4.4.

2.  Berücksichtigt werden **KPI02 bis KPI09** mit leichter oder starker Anomalie (**Änderung 08.11.2026, Carsten – gilt ab Etappe H**; bis dahin nur KPI02 und KPI04).

3.  Die Rangfolge bleibt vorerst wie bisher (Punkt 5). Weil damit KPIs mit grossen relativen Ausschlägen (v. a. KPI03, 06, 08) bevorzugt werden, wird die Gewichtung zusammen mit der Schwellen-Analyse überarbeitet. Ziel: ein ausgewogener Mix je Spieltag (KPI-Regelwerk, offener Punkt 17).

4.  Vorläufige Werte sowie Spiele mit Status «verschoben» oder «abgesagt» werden nicht berücksichtigt.

5.  Rangfolge: Starke Anomalien kommen vor leichten. Bei gleicher Stärke entscheidet der Betrag der relativen Abweichung, der grösste zuerst. Bei Gleichstand entscheidet das frühere Spieldatum, danach die Reihenfolge im Spielplan.

6.  Pro Begegnung wird höchstens ein Eintrag angezeigt, nämlich der KPI mit dem höchsten Rang (bei Gleichstand der KPI mit der kleineren Nummer).

7.  Angezeigt werden höchstens vier Einträge. Gibt es weniger Anomalien, werden nur diese angezeigt. Es wird nicht aufgefüllt.

8.  Gibt es keine Anomalie, erscheint der Hinweis «Für den aktuellen Spieltag liegen keine Anomalien vor.»

Die Auswahl-Logik wird zusätzlich im KPI-Regelwerk festgehalten (Abschnitt 2.6), da sie später auch für die öffentliche Startseite gilt.

### 5.2 Darstellung

Jeder Eintrag zeigt:

- Rang (1 bis 4)

- Liga und Spieltag

- Begegnung (Heim – Gast)

- KPI-Name

- Hauptwert und relative Abweichung mit Vorzeichen

- Anomalie-Einstufung gemäss Kapitel 8

- Überschrift und Beschreibung exakt gemäss KPI-Regelwerk

Ein Klick auf einen Eintrag öffnet den Bereich der jeweiligen Liga. Im Kopfbereich wird der Spieltag pro Liga angezeigt (siehe 3.2).

*Umgesetzt in Etappe D (31.10.2026): Karten in zwei Spalten, darunter der Link „Zur Liga“ (`app/views/top_anomalien.py`); die Auswahl selbst steht in `app/core/top.py`. Die Spieltag-Pfeile der Liga-Bereiche wirken hier nicht: Top Anomalien zeigt immer den aktuellen Spieltag.*

## 6. Bereich Datenqualität

Der Bereich Datenqualität (/dashboard/datenqualitaet) ist ein internes Kontrollblatt. Er wird als letzter Tab ganz rechts angezeigt und ist wie alle Bereiche passwortgeschützt. Er dient ausschliesslich der Anzeige. Daten können hier nicht bearbeitet werden.

### 6.1 Datenbank

- Datenstand: Dateiname, Datum der letzten Änderung, Anzahl Spiele je Liga und Saison

- Prüfergebnisse gemäss 02_Datenbasis.md, gegliedert in Fehler, Warnungen und Hinweise

- Inhalt des Tabellenblatts «Datenhinweise»

### 6.2 Spielplan und Spieltage

- Übersicht pro Liga über alle Spieltage der Datei Spielplan.xlsx mit Saison, Spieltag, erstem und letztem Spieldatum, Anzahl Spiele und Status «beendet», «aktuell» oder «kommend».

- Der gemäss 4.4 aktuelle Spieltag ist hervorgehoben. So lässt sich prüfen, welcher Spieltag im Dashboard angezeigt wird und welcher als nächster folgt.

- Aufgeklappt zeigt jeder Spieltag seine Begegnungen mit Datum, Status und Hinweisen, z. B. Aufsteiger ohne Ligadaten.

- Prüfergebnisse des Spielplans gemäss 04_Spielplan.md.

- KPI-Werte werden hier nicht angezeigt. Sie erscheinen nur in den Liga-Bereichen.

### 6.3 Häufigkeit der Anomalien

Für jede Liga und jeden KPI (ausser KPI01) wird angezeigt, wie oft keine, leichte und starke Anomalien auftreten. Grundlage sind alle Spiele der letzten abgeschlossenen Saison, jeweils so berechnet, als wären sie noch nicht gespielt. Die Übersicht dient der Überprüfung der Schwellenwerte, insbesondere bei KPI03.

**Ergänzung 08.11.2026 (ab Etappe H):** Unter der Häufigkeit werden die **gültigen Schwellenwerte** angezeigt (Standard ±20 % / ±35 % und allfällige Abweichungen je Liga und KPI aus `app/config/schwellen.toml`, KPI-Regelwerk 2.2). Nur Anzeige, keine Bearbeitung.

**Ergänzung 08.11.2026 (H.1):** Die Anteile „leicht“ und „stark“ werden wie alle Werte im Dashboard mit zwei Nachkommastellen **kaufmännisch** gerundet (0,125 % → 0,13 %). Die Berechnung für alle vier Ligen dauert beim ersten Aufruf je Datenbankstand rund 6 Sekunden (vorher rund 30).

### 6.4 Simulation (geplant, Etappe I)

Ein zusätzlicher Bereich „Simulation“ (nur intern) rechnet mit historischen Spielen: Simulations-KPIs 10–13 (KPI-Regelwerk, Abschnitt 10), Ergebniskontrolle (wie oft eine Anomalie im Spiel eingetroffen ist) und alternative Schwellen je Liga und KPI. Die Simulation verändert keine Live-Werte; übernommene Schwellen werden bewusst in `schwellen.toml` eingetragen. Spezifikation folgt vor Etappe I.

**Vorgehen (Carsten, 08.11.2026):** Nach Etappe H wird zuerst dieser interne Tab zur **Analyse der Schwellen je KPI und Liga** gebaut, danach folgt das Feintuning je KPI und Liga. Im selben Schritt wird die **Gewichtung der Top Anomalien** erarbeitet (5.1, Punkt 3).

## 7. Verbindliche KPI-Spaltenstruktur

Die folgenden Spalten sind für die ersten vier KPIs verbindlich.

**Änderung 08.11.2026 (ab Etappe H):** In der Tabelle stehen nur noch Hauptwert und Anomalie-Punkt je KPI (4.1). Die hier beschriebenen Detailspalten erscheinen in der aufgeklappten Ansicht einer Begegnung, für KPI 05–09 sinngemäss gemäss KPI-Regelwerk, Abschnitt 9. Alle Zahlen mit zwei Nachkommastellen.

Die Reihenfolge der Spalten in der Tabelle legt dieses Briefing fest. Der Kartenaufbau in Abschnitt 2.5 des KPI-Regelwerks gilt für spätere Detail- und Website-Ansichten.

Die fachlichen Berechnungen und Regeln sind vollständig im KPI-Regelwerk beschrieben. Es ist die alleinige Grundlage für die Berechnungen.

### 7.1 KPI01 – Formkurve

Die Formkurve wird als kompakte visuelle Darstellung abgebildet.

| **Spalte** | **Inhalt**                   |
|------------|------------------------------|
| Heim       | Formkurve der Heimmannschaft |
| Gast       | Formkurve der Gastmannschaft |

Darstellung:

- Bis zu fünf Marker pro Mannschaft.

- Chronologische Reihenfolge: ältestes Spiel links, neuestes Spiel rechts.

- Sieg = grüner Marker.

- Unentschieden = grauer Marker.

- Niederlage = roter Marker.

- Fehlende Spiele werden neutral mit «–» dargestellt.

Es gibt bei KPI01 keine Anomalieklassifizierung.

Die Anzahl tatsächlich verfügbarer Spiele muss berücksichtigt werden. Die Details dazu stehen im KPI-Regelwerk.

### 7.2 KPI02 – Erwartete Tore

Für KPI02 sind folgende acht Spalten vorgesehen:

| **Nr.** | **Spalte**   | **Inhalt**                                              |
|---------|--------------|---------------------------------------------------------|
| 1       | Team 1       | Wert der Heimmannschaft                                 |
| 2       | Team 2       | Wert der Gastmannschaft                                 |
| 3       | Hauptwert    | Gemeinsamer Torindikator der Begegnung                  |
| 4       | Ligareferenz | Durchschnitt der Liga                                   |
| 5       | Abweichung   | Prozentuale Abweichung von der Ligareferenz             |
| 6       | Anomalie     | Keine, leichte oder starke Anomalie                     |
| 7       | Datenbasis   | Anzahl verwendeter Spiele                               |
| 8       | Beschreibung | Überschrift und Beschreibung exakt gemäss KPI-Regelwerk |

Die Bezeichnung «Team 1» entspricht der Heimmannschaft, «Team 2» der Gastmannschaft.

Die Spalte «Beschreibung» zeigt Überschrift und Beschreibung exakt gemäss den Frontend-Texten im KPI-Regelwerk. Eigene Formulierungen sind nicht zulässig.

### 7.3 KPI03 – Over 2.5 Goals

Für KPI03 sind folgende acht Spalten vorgesehen:

| **Nr.** | **Spalte**   | **Inhalt**                                              |
|---------|--------------|---------------------------------------------------------|
| 1       | Team 1       | Wert der Heimmannschaft                                 |
| 2       | Team 2       | Wert der Gastmannschaft                                 |
| 3       | Hauptwert    | Gemeinsamer Teamdurchschnitt                            |
| 4       | Referenzwert | Fixer Referenzwert von 2,5                              |
| 5       | Abweichung   | Prozentuale Abweichung vom Referenzwert                 |
| 6       | Anomalie     | Keine, leichte oder starke Anomalie                     |
| 7       | Datenbasis   | Anzahl verwendeter Spiele                               |
| 8       | Beschreibung | Überschrift und Beschreibung exakt gemäss KPI-Regelwerk |

Wichtig: Der KPI zeigt die statistische Abweichung des gemeinsamen Teamdurchschnitts vom Referenzwert 2,5.

Er ist keine direkte Wahrscheinlichkeit dafür, dass in der Begegnung mehr als 2,5 Tore fallen.

Die Berechnung erfolgt ausschliesslich gemäss KPI-Regelwerk.

### 7.4 KPI04 – Gelbe Karten

Für KPI04 sind folgende acht Spalten vorgesehen:

| **Nr.** | **Spalte**   | **Inhalt**                                              |
|---------|--------------|---------------------------------------------------------|
| 1       | Team 1       | Durchschnitt der gelben Karten der Heimmannschaft       |
| 2       | Team 2       | Durchschnitt der gelben Karten der Gastmannschaft       |
| 3       | Hauptwert    | Erwartete gelbe Karten der Begegnung                    |
| 4       | Ligareferenz | Durchschnitt der Liga                                   |
| 5       | Abweichung   | Prozentuale Abweichung von der Ligareferenz             |
| 6       | Anomalie     | Keine, leichte oder starke Anomalie                     |
| 7       | Datenbasis   | Anzahl verwendeter Spiele                               |
| 8       | Beschreibung | Überschrift und Beschreibung exakt gemäss KPI-Regelwerk |

Die Anzahl der verwendeten Referenzspiele der Liga soll ebenfalls nachvollziehbar sein.

Diese Information kann kompakt in der Spalte «Datenbasis» oder über einen Tooltip dargestellt werden. Dafür soll keine zusätzliche Hauptspalte entstehen.

## 8. Darstellung der Anomalien

Die Anomalien sollen in der Tabelle schnell und eindeutig erkennbar sein.

Folgende Farbgebung ist vorgesehen:

| **Status**       | **Darstellung** |
|------------------|-----------------|
| Keine Anomalie   | Grauer Punkt    |
| Leichte Anomalie | Gelber Punkt    |
| Starke Anomalie  | Roter Punkt     |

Die Richtung der Abweichung wird separat dargestellt, beispielsweise über den Prozentwert mit Vorzeichen.

Beispiele:

- +24,50 %

- −18,20 %

Die Farbcodierung zeigt die Stärke der Auffälligkeit. Die Richtung wird durch den Zahlenwert und die Beschreibung vermittelt.

Die genauen Schwellenwerte und Klassifizierungsregeln sind im KPI-Regelwerk festgelegt. Diese dürfen nicht im Frontend neu definiert werden.

KPI01 Formkurve erhält keine Anomaliefarbe.

## 9. Datenbasis und vorläufige Werte

Die Datenbasis muss für jeden KPI nachvollziehbar sein.

Die Anzahl verwendeter Spiele ist dynamisch und darf nicht fest im Frontend hinterlegt werden.

Beispiele:

- 10 = beide Teams haben jeweils zehn Spiele in der Datenbasis.

- 9 / 10 = Heimmannschaft hat neun, Gastmannschaft zehn verwendbare Spiele.

Bei weniger verfügbaren Spielen als im KPI-Regelwerk vorgesehen, muss der Wert als «Vorläufig» gekennzeichnet werden.

Darstellung: Die Spalte «Datenbasis» zeigt die Anzahl Spiele (z. B. «7 / 10») und bei vorläufigen Werten zusätzlich ein hervorgehobenes «V». Beim Darüberfahren erscheint der Hinweis «Vorläufig: weniger Spiele als im KPI-Regelwerk vorgesehen». Eine zusätzliche Spalte ist nicht vorgesehen. Bei KPI01 ist die Anzahl verfügbarer Spiele an den Platzhaltern «–» erkennbar.

Es dürfen keine fehlenden Daten künstlich mit Nullwerten aufgefüllt werden.

Die Behandlung fehlender Daten und die Berechnung mit kleineren Stichproben erfolgen gemäss KPI-Regelwerk.

## 10. Vereinsdaten

Vereinslogos werden aus rechtlichen Gründen weder im Dashboard noch auf der öffentlichen Website verwendet.

Für die Vereinsdaten ist eine zentrale Struktur vorzusehen, beispielsweise mit:

- team_id

- team_name (Schreibweise wie in Datenbank und Spielplan)

- display_name (Anzeigename, z. B. «1. FC Köln»)

Die Ligazugehörigkeit wird nicht fest beim Verein gespeichert, da Vereine auf- und absteigen. Sie ergibt sich pro Saison aus Datenbank und Spielplan.

In Version 1 werden die Teamnamen so angezeigt, wie sie in Datenbank und Spielplan stehen (z. B. «Bayern Munich», «FC Koln»). Deutsche Anzeigenamen werden später über display_name ergänzt.

## 11. Technische Architektur

Die Anwendung soll modular aufgebaut sein.

Folgende Bereiche sind voneinander zu trennen:

1.  Datenbeschaffung

2.  Datenaufbereitung

3.  KPI-Berechnungen

4.  Anomalieklassifizierung

5.  Datenqualitätsprüfung

6.  Darstellung und Benutzeroberfläche

Die KPI-Berechnungen dürfen nicht direkt in den UI-Komponenten implementiert werden.

Die gleiche Daten- und Berechnungslogik soll später sowohl für das interne Dashboard als auch für die öffentliche Website verwendet werden können.

Das öffentliche Frontend und das interne Dashboard dürfen unterschiedliche Oberflächen haben, sollen aber auf derselben fachlichen Berechnungsgrundlage aufbauen.

Die URL-Navigation muss ebenfalls sauber in die bestehende Architektur integriert werden.

**Umsetzung (H.1, 08.11.2026):** Die KPI-Ergebnisse eines Spieltags berechnet `app/core/results.py` (ohne Oberfläche). Der Liga-Bereich und die Top Anomalien nutzen dieselbe Funktion und denselben Zwischenspeicher (`state.get_matchday_kpis`); ein Bereich ruft den anderen nicht mehr auf. Der Zwischenspeicher wird neu berechnet, sobald sich Datenbank, Spielplan, Schwellen, Ligen oder Teamliste ändern.

## 12. Responsive Darstellung

Das Dashboard soll primär für die Nutzung auf Desktop-Geräten optimiert sein.

Die breite Tabelle mit den KPI-Gruppen ist ein zentrales Element. Deshalb soll sie nicht auf Kosten der Lesbarkeit vollständig auf schmale Bildschirme angepasst werden.

Auf kleineren Bildschirmen muss das horizontale Scrollen zuverlässig funktionieren.

Die beiden fixierten Spalten \# und Spiel sollen auch auf kleineren Bildschirmen sichtbar bleiben, sofern technisch sinnvoll umsetzbar.

## 13. Qualitätssicherung

Vor der Umsetzung sind die bestehende Projektstruktur, Datenbank und bereits vorhandenen Berechnungsmodule zu prüfen.

Bitte nicht sofort mit umfangreichen Codeänderungen beginnen.

**Vorgehensweise:**

1.  Bestehende Projektstruktur analysieren.

2.  Vorhandene Datenbank und Datenmodelle prüfen.

3.  Bestehende KPI-Berechnungen untersuchen.

4.  Vorhandene Routing- und Authentifizierungslogik prüfen.

5.  Abweichungen zwischen bestehender Implementierung und KPI-Regelwerk identifizieren.

6.  Einen kurzen Umsetzungsvorschlag mit den notwendigen Anpassungen erstellen.

7.  Erst nach dieser Analyse mit der Implementierung beginnen.

Bestehende funktionierende Funktionen sollen erhalten bleiben. Keine unnötigen Neuentwicklungen oder vollständigen Umstrukturierungen ohne sachlichen Grund.

### 13.1 KPI-Validierung

Die KPI-Berechnungen müssen anhand der Testfälle in `docs/tests/` überprüft werden. Die Testfälle sind erstellt und abgenommen (28./29.10.2026) und liegen als folgende Dateien vor:

- docs/tests/test_kpi01_formkurve.md

- docs/tests/test_kpi02_erwartete_tore.md

- docs/tests/test_kpi03_over25.md

- docs/tests/test_kpi04_gelbe_karten.md

Die Berechnungen müssen mit dem KPI-Regelwerk übereinstimmen. Die JSON-Blöcke in den Testfällen werden als automatische Tests umgesetzt und müssen exakt erfüllt sein. Grundlage ist die Datenbank mit dem in den Testfällen genannten SHA-256-Wert.

### 13.2 Routing- und Sicherheitstests

Zusätzlich müssen folgende Punkte getestet werden:

- /dashboard zeigt den Bereich Top Anomalien.

- /dashboard/bundesliga zeigt die Bundesliga.

- /dashboard/premier-league zeigt die Premier League.

- /dashboard/datenqualitaet zeigt den Bereich Datenqualität.

- Beim Wechsel zwischen den Tabs wird die URL aktualisiert.

- Ein Seiten-Reload erhält den ausgewählten Bereich.

- Browser Zurück/Vorwärts funktioniert.

- Alle Adressen unter /dashboard sind serverseitig passwortgeschützt.

- Nicht angemeldete Benutzer erhalten auch bei direktem URL-Aufruf keinen Zugriff.

- Die Startseite soccer-intelligence.com zeigt weiterhin öffentlich die Platzhalterseite

- Eine unbekannte Adresse unter /dashboard zeigt den Hinweis „Seite nicht gefunden“.

## 14. Nicht Bestandteil dieser Umsetzungsphase

Folgende Themen sind in dieser Phase nicht umzusetzen:

- Vollständiges öffentliches Frontend

- Öffentliche Benutzerregistrierung

- Deutsche Anzeigenamen der Vereine (display_name)

- Weitere KPIs, die noch nicht fachlich definiert sind

- ~~Zusätzliche Spieltagsnavigation~~ (umgesetzt am 31.10.2026, siehe 3.2)

- Erweiterte Filter- und Sortierfunktionen, sofern sie nicht bereits vorhanden sind

Die Architektur soll spätere Erweiterungen jedoch ermöglichen.

## 15. Abnahmekriterien

Die Umsetzung gilt als erfolgreich, wenn folgende Punkte erfüllt sind:

1.  Das Dashboard besitzt die Bereiche Top Anomalien, Bundesliga, Premier League und Datenqualität, seit Etappe F zusätzlich Serie A und LaLiga. Weitere Ligen lassen sich über die Konfiguration ergänzen.

2.  Alle Bereiche sind über die definierten URLs direkt erreichbar.

3.  /dashboard zeigt direkt den Bereich Top Anomalien.

4.  Die Navigation und die URL bleiben synchron.

5.  Alle Adressen unter /dashboard sind serverseitig passwortgeschützt. Die Startseite / bleibt öffentlich.

6.  Die Liga-Ansichten zeigen alle Begegnungen des **aktuellen** Spieltags gemäss 4.4.

7.  Die ersten beiden Tabellenspalten bleiben beim horizontalen Scrollen fixiert.

8.  Die KPI-Gruppen sind klar voneinander getrennt.

9.  Die KPI-Spalten entsprechen exakt der definierten Struktur.

10. Die Darstellung der Anomalien entspricht den Vorgaben.

11. Die Datenbasis ist dynamisch und vorläufige Werte werden gekennzeichnet.

12. Die KPI-Berechnungen stimmen mit dem KPI-Regelwerk überein.

13. Die bestehende Funktionalität bleibt erhalten.

14. Die technische Grundlage ermöglicht eine spätere öffentliche Website mit derselben Berechnungslogik.

15. Der Bereich Top Anomalien zeigt höchstens vier Einträge gemäss der Auswahl-Logik in Kapitel 5.

16. Der Bereich Datenqualität zeigt die Prüfergebnisse von Datenbank und Spielplan, die Spieltagsübersicht mit dem aktuellen Spieltag und die Häufigkeit der Anomalien.

17. **Ab Etappe H:** Die Liga-Bereiche zeigen KPI 01–09 in der kompakten Tabelle mit Details per Aufklappen; alle Zahlen mit zwei Nachkommastellen; Top Anomalien über KPI 02–09; der Bereich Datenqualität zeigt die Häufigkeit für KPI 02–09 und die gültigen Schwellenwerte.

## 16. Abschliessende Anweisung

Bitte analysiere zunächst den bestehenden Projektstand und erstelle einen kurzen Vorschlag zur Umsetzung.

Achte besonders darauf, dass:

- die bestehende Architektur berücksichtigt wird,

- die neue URL-Struktur sauber integriert wird,

- die Authentifizierung für alle Dashboard-Unterseiten gilt,

- die KPI-Berechnungen ausschliesslich dem KPI-Regelwerk folgen,

- die Tabellenstruktur exakt wie beschrieben umgesetzt wird,

- bestehende funktionierende Funktionen nicht unnötig verändert werden.

Wenn fachliche oder technische Unklarheiten auftreten, stelle Rückfragen, bevor du eigenständige Annahmen triffst.

**Ziel ist eine stabile, modulare interne Analyseplattform, die später als technische Grundlage für die öffentliche Website von Soccer Intelligence dient.**
