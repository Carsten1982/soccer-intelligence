# Soccer Intelligence – Dashboard-Briefing

**Version 5.10** · Stand 20.11.2026 (Version 0.21.1: Vorschau heute + 5 statt + 6, 4; Version 0.21: Vereine ohne Anzeigenamen der Website im Reiter Datenimport/API, 6.5; Version 0.20: Signalqualität stark/mittel/gering statt Prognosewert, gespielt ab Anpfiff + 2 Stunden, Top Anomalien ohne Nachrücken, Schnappschüsse im Reiter Datenimport/API, 48-Stunden-Grenze, 4, 5, 6.5; Version 0.19.1: Reiter-Reihenfolge, Text Top Anomalien, Schwellen je Liga in der Sensitivitätsanalyse; Version 0.19: Auffälligkeit und Prognosewert statt leicht/stark, 4.1, 5, 6.3, 6.4, 8; Version 0.14: Bereich Datenimport/API, 6.5; Version 0.15: Entwurf 2 mit Blöcken A/B und Entscheiden; Version 0.15.2: Anmeldemaske, 2.4; Version 0.16: kommende Spieltage, 4, 4.4, 5)

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

- **Seit 0.15.2 (Entscheidung Carsten 16.11.2026): Anmeldemaske im Dashboard** statt der Passwortabfrage des Browsers (Traefik BasicAuth, auf manchen Arbeitsrechnern gesperrt). Die Maske zeigt „Soccer Intelligence“, „Internes Dashboard – bitte anmelden“, die Felder **Benutzername** und **Passwort** und den Button **„Anmelden“**; bei falscher Eingabe „Benutzername oder Passwort falsch.“, nach 5 Fehlversuchen 15 Minuten Sperre. Wer nicht angemeldet ist, sieht auf jeder Adresse unter /dashboard nur die Maske, keine Seiten, keine Daten und keine Buttons.
- Angemeldet bleibt man **12 Stunden** (signiertes Cookie); unten auf jeder Seite **„Abmelden“**. Ein neues Passwort meldet alle Browser ab.

- Das Ausblenden von Menüpunkten oder nicht verlinkte Adressen gelten nicht als Schutz.

- Die Zugangsdaten werden ausschliesslich als Passwort-Hash in einer Konfigurationsdatei auf dem Server hinterlegt (z. B. .env). Das Klartextpasswort darf weder im Programmcode noch in Git oder in der Dokumentation gespeichert werden.

- Zu Beginn gibt es einen gemeinsamen Zugang. Weitere Benutzer können später ergänzt werden.

- Die Verbindung erfolgt ausschliesslich über HTTPS.

- Die Änderung betrifft nur den eigenen Container football-dashboard und eine neue, kleine Komponente für die Platzhalterseite. Traefik selbst, n8n und alle anderen Anwendungen bleiben unverändert. Die Umsetzung erfolgt erst nach separater Freigabe gemäss den Schutzregeln.

- Suchmaschinen: Alle Antworten unter /dashboard tragen zusätzlich den Hinweis „noindex, nofollow“.

*Umgesetzt in Etappe E (31.10.2026), Anmeldemaske seit Version 0.15.2 (16.11.2026), freigegeben von Carsten. Technische Details: `docs/01_Technisches_Setup.md`, Abschnitte 3 und 4.*

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

Weitere aktivierte Ligen erhalten automatisch einen eigenen Tab. Dieser wird vor dem Tab Datenqualität eingefügt. Seit Etappe F (Änderung 07.11.2026): Top Anomalien · Bundesliga · Premier League · Serie A · LaLiga · Datenqualität. Seit 0.19.1 (Carsten 18.11.2026) mit den internen Bereichen: Top Anomalien · Bundesliga · Premier League · Serie A · LaLiga · Sensitivitätsanalyse · Datenqualität · Datenimport/API.

Der aktive Tab muss visuell klar erkennbar sein.

Die Tabs müssen mit der oben definierten URL-Struktur verknüpft sein.

## 4. Liga-Bereiche (Bundesliga, Premier League, Serie A, LaLiga)

Die Liga-Bereiche zeigen jeweils die **kommenden Spiele nach Spieltag** (seit 0.16, siehe 4.4; bis 0.15.2: alle Begegnungen des aktuellen Spieltags).

Die Darstellung erfolgt in einer breiten Tabelle, je Spieltag ein Abschnitt.

*Änderung 16.11.2026 (Version 0.16, Designentwurf freigegeben):* Die Spalte **„Datum“** zwischen „Spiel“ und „Form“ zeigt Wochentag, Datum und Anstosszeit bzw. das Ergebnis (Spielplan-Spezifikation `07`, Abschnitt 4.6). Stadioninformationen werden weiterhin nicht angezeigt.

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

- Je Begegnung eine Zeile mit Laufnummer, Spielpaarung, Formkurve (KPI 01) und je KPI 02–09 **Hauptwert und Punkt nach Signalqualität** (seit 0.19, Kapitel 8), Kennzeichnung „V“ bei vorläufigen Werten (nie auffällig). Die aufgeklappte KPI-Karte zeigt rechts oben „Auffällig · Signalqualität stark“ bzw. „Keine Auffälligkeit“ und darunter die Herleitung (Schwelle, Trefferquote, alle Spiele, Mehrwert, Spiele).
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

### 4.4 Spielplan und kommende Spieltage

Welche Begegnungen angezeigt werden, steht ausschliesslich in der Datei data/Spielplan.xlsx (ein Tabellenblatt pro Liga, Blattname = Liganame). Die historische Datenbank wird dafür nicht verwendet, ausser für das Ergebnis gespielter Spiele und für „Werte ab“. Der Aufbau der Datei ist in 04_Spielplan.md beschrieben.

*Änderung 16.11.2026 (Version 0.16):* Was die Ligaseite zeigt, regelt die Spielplan-Spezifikation `07_Spielplan_Anzeige.md`, **Abschnitt 4** (Sichtbarkeit, Abschnitte, Pausen, Navigation, „Werte ab“, Spalte Datum; Festlegungen 4.8). Kurz:

1.  Ein Spieltag ist beendet am Tagesende seines letzten regulären Spiels (Zeitzone Europe/Zurich). **Anstehend** ist der nicht beendete Spieltag mit dem frühesten Termin.

2.  Ohne Auswahl („Kommende Spiele“) erscheinen als **Abschnitte**: der anstehende Spieltag (höchstens 14 Tage entfernt), weitere Spieltage, die heute bis heute + 5 beginnen (seit 0.21.1; bis 0.21 heute + 6), und Nachhol- oder vorgezogene Spiele unter ihrer offiziellen Nummer. Gespielte Spiele bleiben grau mit Ergebnis stehen (seit 0.20: ab Anpfiff + 2 Stunden grau mit „Gespielt“, nach dem Import mit Ergebnis; bis dahin normal; Werte des Schnappschusses, `07`, 4.9).

3.  Pausen über 14 Tage zeigen eine Box („Winterpause“, „Spielpause“, „Sommerpause“), nur wenn der letzte erfolgreiche Importlauf höchstens 48 Stunden zurückliegt (seit 0.20; bis 0.19.1: 3 Tage); sonst „Spielplan zuletzt aktualisiert am …“.

4.  Spiele mit Status (verschoben, abgesagt, abgebrochen, ausgesetzt, gewertet) erscheinen nicht unter den kommenden Spielen. Beim Blättern stehen sie in ihrem Spieltag mit dem Status in der Spalte Datum, ohne KPI-Werte. Die 3-Tage-Pflegeregel von 07.11.2026 ist seit 0.15 ersetzt (`04_Spielplan.md`, Abschnitt 6).

*Pfeile:* zurück alle Spieltage der Saison und der Vorsaison, vorwärts höchstens 2 über den anstehenden hinaus (bis 0.15.2 nur bis zum aktuellen). KPI-Werte erscheinen erst, wenn beide Teams ihr vorheriges Spiel gespielt haben („Werte ab …“).

5.  Die KPIs jeder Begegnung werden immer so berechnet, als wäre das Spiel noch nicht gespielt. Stichtag ist „Datum von“ der Begegnung im Spielplan (KPI-Regelwerk, Abschnitt 1). Das gilt auch, wenn der angezeigte Spieltag bereits gespielt ist.

6.  Teams ohne Ligadaten (z. B. Aufsteiger) werden angezeigt. Ihre KPI-Werte erscheinen gemäss KPI-Regelwerk als „--“.

7.  Fehler im Spielplan werden auf der Seite Datenqualität angezeigt: fehlende Pflichtfelder, ungültiges Datum, unbekannter Teamname, Team doppelt im selben Spieltag, weniger Spiele als erwartet (Anzahl Teams / 2).

8.  Die Begegnungen werden nach „Datum von“ sortiert, bei gleichem Datum in der Reihenfolge der Spielplan-Datei.

9.  Enthält die Datenbank oder der Spielplan einen Fehler (gemäss 02_Datenbasis.md bzw. 04_Spielplan.md), zeigen die Liga-Bereiche und der Bereich Top Anomalien statt der Tabelle einen Hinweis mit Link zum Bereich Datenqualität.

## 5. Bereich Top Anomalien

Der Bereich Top Anomalien (/dashboard) zeigt die auffälligsten Anomalien der anstehenden Spiele aller aktiven Ligen (seit 0.16 je Liga der zeitlich nächste Block, `07`, Abschnitt 4.7; bis 0.15.2 der aktuelle Spieltag). Er ist die Grundlage für die spätere Startseite der öffentlichen Website. Die Auswahl erfolgt deshalb zentral in der Berechnungslogik und nicht in der Oberfläche.

### 5.1 Auswahl-Logik

1.  Grundlage ist je aktiver Liga der zeitlich nächste Block (*Änderung 16.11.2026, Version 0.16*): der anstehende Spieltag samt Nachhol- und vorgezogenen Spielen an seinen Tagen; Sonderspiele davor bilden einen eigenen Block. Eine Liga nimmt teil, wenn ihr Block höchstens 14 Tage entfernt ist. Nur Spiele **mit Werten** („Werte ab“, 4.4). *Änderung 19.11.2026 (Version 0.20):* Die Liste steht vor dem ersten Anpfiff fest; angepfiffene Spiele bleiben mit den Werten ihres Schnappschusses stehen, ab Anpfiff + 2 Stunden ausgegraut mit „Gespielt“ bzw. dem Ergebnis; es rückt kein anderes Spiel nach (bis 0.19.1: nur Spiele vor dem Anpfiff).

2.  Berücksichtigt werden **KPI02 bis KPI09**, die **auffällig** sind (seit 0.19: Abweichung über der Schwelle ihrer Liga, KPI und Richtung; KPI-Regelwerk 2.2).

3.  Vorläufige Werte sowie Spiele mit Status (verschoben, abgesagt, abgebrochen, ausgesetzt, gewertet) werden nicht berücksichtigt.

4.  Rangfolge (seit 0.19, Entscheidungen Carsten 17./18.11.2026): Signalqualität **stark** vor **mittel** vor **gering**; innerhalb einer Stufe der grösste Betrag der Abweichung; bei Gleichstand das frühere Spieldatum, danach die Reihenfolge im Spielplan. Keine Mischformel.

5.  Pro Begegnung wird höchstens ein Eintrag angezeigt: der KPI mit der höchsten Signalqualität, dann der grössten Abweichung (bei Gleichstand der KPI mit der kleineren Nummer).

6.  **Liga-Mix:** höchstens zwei Einträge je Liga; nur wenn die anderen Ligen nicht genug Auffälligkeiten haben, wird mit weiteren Spielen derselben Liga aufgefüllt.

7.  Angezeigt werden höchstens vier Einträge; mit „gering“ wird aufgefüllt. Gibt es weniger Auffälligkeiten, werden nur diese angezeigt mit dem Hinweis «Aktuell nur x auffällige Spiele.». Ist ein Eintrag „gering“ dabei: «Ergänzt mit Spielen geringer Verlässlichkeit.»

8.  Gibt es keine Auffälligkeit, erscheint der Hinweis «Für die anstehenden Spiele liegen keine Auffälligkeiten vor.»

9.  Text unter der Liste (Wortlaut Carsten 18.11.2026, seit 0.19.1) mit drei Zwischentiteln: **Berücksichtigte Spiele** (anstehende Spieltage aller Ligen samt Nachhol- und vorgezogenen Spielen, je Liga der nächste Spieltag, wenn er innerhalb der nächsten 14 Tage beginnt, Sonderspiele separat; nur Spiele mit vollständigen, nicht vorläufigen Werten; seit 0.20 Satz „Die Liste steht vor dem ersten Anpfiff fest: Gespielte Spiele bleiben ausgegraut an ihrem Platz, es rückt kein anderes Spiel nach.“) · **Auswahl der Auffälligkeiten** (über der Schwelle der Liga; nach Signalqualität stark, mittel, gering, innerhalb der Stufe grösste Abweichung) · **Verteilung der Spiele** (eine Auffälligkeit je Begegnung, in der Regel höchstens zwei Spiele je Liga mit Auffüllen, maximal 4 Spiele). Wortlaut in `app/views/top_anomalien.py` (`selection_text`). Die Karten zeigen den Signalqualität und die Herleitung.

Die Auswahl-Logik wird zusätzlich im KPI-Regelwerk festgehalten (Abschnitt 2.6), da sie später auch für die öffentliche Startseite gilt.

### 5.2 Darstellung

Jeder Eintrag zeigt:

- Rang (1 bis 4)

- Liga und Spieltag, seit 0.16 mit Datum und Anstoss

- Begegnung (Heim – Gast)

- KPI-Name

- Hauptwert und relative Abweichung mit Vorzeichen

- Anomalie-Einstufung gemäss Kapitel 8

- Überschrift und Beschreibung exakt gemäss KPI-Regelwerk

Ein Klick auf einen Eintrag öffnet den Bereich der jeweiligen Liga. Im Kopfbereich steht je Liga ein Kästchen, z. B. „Bundesliga: Spieltag 10 · noch 4 Spiele“ bzw. „Bundesliga: Winterpause bis 07.01.“ (seit 0.16; vorher der Spieltag pro Liga, siehe 3.2).

*Umgesetzt in Etappe D (31.10.2026): Karten in zwei Spalten, darunter der Link „Zur Liga“ (`app/views/top_anomalien.py`); die Auswahl selbst steht in `app/core/top.py`, die Blöcke seit 0.16 in `app/core/anzeige.py`. Die Spieltag-Pfeile der Liga-Bereiche wirken hier nicht.*

## 6. Bereich Datenqualität

Der Bereich Datenqualität (/dashboard/datenqualitaet) ist ein internes Kontrollblatt. Er wird als letzter Tab ganz rechts angezeigt und ist wie alle Bereiche passwortgeschützt. Er dient ausschliesslich der Anzeige. Daten können hier nicht bearbeitet werden.

### 6.1 Datenbank

- Datenstand: Dateiname, Datum der letzten Änderung, Anzahl Spiele je Liga und Saison

- **Änderung 10.11.2026 (Version 0.11):** je Liga die **Referenzsaison** (älteste Saison, nur Vorsaison, nicht ausgewertet) und die ausgewerteten Saisons, z. B. „Referenzsaison: 2018/19 (nur Vorsaison, nicht ausgewertet) · Ausgewertet: 2019/20–2026/27“ (KPI-Regelwerk 1.2). Fehlt zwischen zwei Saisons eine Saison, erscheint eine Warnung „Saison fehlt“.

- Prüfergebnisse gemäss 02_Datenbasis.md, gegliedert in Fehler, Warnungen und Hinweise

- Inhalt des Tabellenblatts «Datenhinweise»

### 6.2 Spielplan und Spieltage

- Übersicht pro Liga über alle Spieltage der Datei Spielplan.xlsx mit Saison, Spieltag, erstem und letztem Spieldatum, Anzahl Spiele und Status «beendet», «aktuell» oder «kommend».

- Der gemäss 4.4 aktuelle Spieltag ist hervorgehoben. So lässt sich prüfen, welcher Spieltag im Dashboard angezeigt wird und welcher als nächster folgt.

- Aufgeklappt zeigt jeder Spieltag seine Begegnungen mit Datum, Status und Hinweisen, z. B. Aufsteiger ohne Ligadaten.

- Prüfergebnisse des Spielplans gemäss 04_Spielplan.md.

- KPI-Werte werden hier nicht angezeigt. Sie erscheinen nur in den Liga-Bereichen.

### 6.3 Schwellen und Häufigkeit (Tab „Schwellen und Häufigkeit“, seit 0.19)

**Gültige Schwellen und Signalqualität:** Tabelle je Liga, KPI und Richtung mit Schwelle, Signalqualität, Spielen, Trefferquote, Vergleichsgruppe und Mehrwert aus `schwellen.toml`, dazu Saisons und Freigabedatum der Datei. Kombinationen, die fehlen, werden nie ausgezeichnet. Nur Anzeige, Änderung einmal pro Saison über die Datei.

**Häufigkeit je Liga und KPI:** Wie oft ist jeder KPI (ausser KPI01) auffällig, und mit welchem Signalqualität (stark, mittel, gering; nicht auffällig; vorläufig; nicht berechenbar; Anteil auffällig, Anteil hoch)? Grundlage sind alle Spiele der letzten abgeschlossenen Saison (nie der Referenzsaison), jeweils so berechnet, als wären sie noch nicht gespielt. Anteile mit zwei Nachkommastellen, kaufmännisch gerundet. Bis 0.18: Spalten „leicht/stark“.

### 6.4 Sensitivitätsanalyse (Version 0.12; Entwurf C seit 0.13; seit 0.19 eine Schwelle je Richtung und Signalqualität)

Siebter Bereich (ganz rechts, nur intern), Tab-Name **„Sensitivitätsanalyse“**, Adresse `/dashboard/simulation`. Frage: Wie oft schlagen die Auffälligkeiten mit bestimmten Schwellen an, und wie verlässlich sind sie? Rechenregeln: KPI-Regelwerk, Abschnitt 11. Die Darstellung ist ein Zwischenstand bis zum Designentwurf (Design-Briefing vom 18.11.2026).

- **Kopf:** „Soccer Intelligence“, darunter **„Sensitivitätsanalyse“**. Gelber Hinweis: „Die hier angepassten Schwellen dienen der Simulation und haben keinen Einfluss auf die anderen Dashboard-Tabs. Es gelten weiterhin die Werte in der Datei schwellen.toml.“ Darunter 1 cm Abstand.
- **Links Einstellungen** (bleiben beim Scrollen stehen): **Liga** (Alle Ligen oder eine Liga) und **Saison** (Regelwerk 11.4, voreingestellt „Alle Saisons“, mit ⓘ).
- **Rechts:** Grundlage (Spiele, Liga, Saisons, abgeschlossene Spieltage); bei „Alle Ligen“ ein orangefarbener Hinweis mit den Spieltagen je Liga; Knopf **„Auf gültige Schwellen zurücksetzen“**.
- **Eine Tabelle für alle KPIs 02–09.** Kopfzeile (bleibt oben): **KPI** · **Schwelle:** Richtung (ⓘ), Abweichung in % (ⓘ) · **Betroffene Spiele:** Anzahl Spiele, Ø/ST, Spieltagsabdeckung · **Ergebnisqualität und Signalqualität:** Anzahl eingetroffen, Trefferquote, Vergleichsgruppe (alle Spiele), Mehrwert in Pp., Spanne (Wilson 95 %), Empfehlung, **Signalqualität** (jede Spalte mit ⓘ-Kurzhilfe, Verweis „Mehr Details findest du unter der Tabelle.“).
  - Je KPI **zwei Zeilen: ↗ mehr, ↘ weniger**; Nummer und Name links; KPIs durch eine Linie getrennt.
  - In jeder Zeile ein **Eingabefeld** (Betrag, eine Nachkommastelle). Vorbelegt mit der gültigen Schwelle; leer mit grauem Text **„keine“** (keine gültige Schwelle) bzw. bei „Alle Ligen“ **„je Liga“** (unterschiedliche Schwellen; jede Liga zählt mit ihrer gültigen). Seit 0.19.1 stehen bei „je Liga“ die gültigen Schwellen klein und grau unter dem Feld (z. B. „PL 10 · SA 15“), und beim Wechsel auf eine Liga zeigt das Feld deren Schwelle (Fehler 0.19 behoben). Eigene Werte blau. Ohne Schwelle steht in der Zeile nur die Vergleichsgruppe und „keine Schwelle“; das Feld bleibt leer (Entscheidung Carsten 18.11.2026, keine Vorbelegung mit 0 %).
  - Empfehlung als farbige Marke wie bisher (Funktioniert grün, Funktioniert leicht gelb, Keine relevante Verbesserung grau, Noch unklar blau, Negativ rot, Zu wenige Daten grau). Unter 50 Spielen ist die Zeile grau.
  - **Signalqualität:** Marke stark (dunkel), mittel, gering (hell) in einer Farbe; „–“ mit grauem Grund (z. B. „Empfehlung: Funktioniert leicht“, „nicht stabil (4 von 7 Saisons)“). Bei einer einzelnen Saison ist die Spalte ausgegraut: „–“, „nur bei mehreren Saisons“.
  - Kein „Total“ mehr (bis 0.18).
- **Anmerkung** unter der Tabelle: über der Schwelle zählt, blaue Werte, graue Zeilen, leere Felder.
- **Erklärfeld** (ersetzt „Definitionen und Änderungen“): Rahmen „Wie kommen die Werte in dieser Tabelle zustande?“ und **Beispiel** in sechs Schritten (Bundesliga, Schüsse aufs Tor, weniger; Werte aus der gültigen Datei mit Stand der Saisons) immer sichtbar; aufklappbar: Abweichung in % und Schwelle · Anzahl Spiele, Ø pro Spieltag, Spieltagsabdeckung · Anzahl eingetroffen und Trefferquote · Vergleichsgruppe und Mehrwert in Pp. · Spanne (Wilson 95 %) · Empfehlung (sechs Stufen) · Signalqualität (Voraussetzungen, vier Stufen, Hinweis auf zu optimistische Werte) · Grundlage der Berechnung. Verständlich für einen 16-Jährigen (Wunsch Carsten). Texte: Spezifikation 18.11.2026, Abschnitt 4. Die Änderungshistorie steht nur im Regelwerk (11.5).
- **Schwellenvorschlag:** Knopf „Schwellenvorschlag berechnen“ rechnet mit den gewählten Saisons für alle Ligen, KPIs und Richtungen die Schwelle nach Regelwerk 2.2 und zeigt sie als Tabelle; „Vorschlag als schwellen.toml herunterladen“. Nichts wird gespeichert; Übernahme nach Freigabe über GitHub (einmal pro Saison nach Saisonende).
- Die Fälle aller Spiele werden einmal je Datenbankstand berechnet (beim ersten Aufruf rund 50 Sekunden); jede Änderung der Schwellen wirkt danach sofort.

### 6.5 Datenimport/API (Version 0.14; seit 0.15 Entwurf 2, freigegeben 15.11.2026)

Achter Bereich (ganz rechts, nur intern), Tab-Name **„Datenimport/API“**, Adresse `/dashboard/datenimport`. Regeln des
Imports: `06_Datenlieferung.md` (Ergebnisse, Abschnitt 10 und 10.1) und `07_Spielplan_Anzeige.md` (Spielplan, Abschnitt 3
und 5). Das Dashboard schreibt nie in die Excel-Dateien; alle Buttons legen nur eine Anfrage ab, den Tausch und das
Festhalten der Entscheide macht der Container `soccer-import`.

- **Kopf:** „Soccer Intelligence“, darunter „Datenimport/API“.
- **Statusleiste** (vier Kacheln): Quelle mit Plan und **Abo gültig bis** (rot, wenn abgelaufen; gelb unter 3 Wochen) ·
  Kontingent heute (Rest laut API) und eigene Obergrenze · letzter Lauf (✓/✕) und nächster Lauf („täglich“) ·
  Betriebsart (halbautomatisch bis …, oder automatisch).
- **Kasten „Neue Daten bereit“** (gelb; rot „Neue Fassung mit Fehlern“), nur wenn eine Fassung wartet: Lauf, Saison,
  „letzte 2 Spieltage“ bzw. montags „alle Spiele der Saison neu geprüft“, Basis der gültigen Datenbank.
  Kennzahlen: neue Spiele, korrigierte Werte, Spielplan: wichtige Änderungen (+ Anstosszeiten), Fehler, kritische Punkte /
  neue Warnungen.
- **„Ihre Entscheidung“** (nur wenn nötig): späte Korrekturen der API (Spiel älter als 7 Tage) mit den Buttons
  „API-Wert übernehmen“ / „bisherigen Wert behalten“; Endstand passt nicht zu den Tor-Ereignissen mit „Ergebnis auf dem
  Platz (Tor-Ereignisse)“ / „Endstand der API“. Ein Entscheid wird festgehalten und wirkt ab dem nächsten Lauf.
  Weitere kritische Punkte (Spiel verschwunden, Zuordnung, „noch nicht gespielt“ mit vergangenem Termin) als Warnung.
- **Block A · Ergebnisse (Datenbank)** (links): Vollständigkeit je Liga und Spieltag der letzten 14 Tage (fällig,
  geliefert, verschoben/abgesagt/gewertet, fehlt, Stand), Qualitätsbericht (Prüfregeln gültig gegen neu, Plausibilität
  neuer/geänderter Spiele, Zuordnung und doppelte IDs, unbekannte Teams); aufklappbar: offene Spiele mit fehlenden
  KPI-Feldern, Korrekturen (davon KPI-relevant), neue Spiele, Meldungen der Prüfung, Teamnamen-Umstellungen, unbekannte
  Teams, Namensänderungen der API, gewertete Spiele.
- **Block B · Spielplan** (rechts): Spiele neu/entfallen und Änderungen nach Gruppen: verschoben · Nachholspiel (neuer
  Termin) · vorgezogen · Termin geändert · ausgesetzt/abgesagt/abgebrochen/gewertet · Anstosszeit geändert ·
  Anstosszeiten festgelegt · Vermerk geändert (die wichtigen Gruppen aufgeklappt).
- **„So sieht das Dashboard nach der Übernahme aus“** (seit 0.16): je Liga, was die Ligaseite (Abschnitte bzw. Hinweis),
  die Spiele, der Block der Top Anomalien und „sichtbar bis“ mit dem neuen Spielplan zeigen würden.
- Zeile „Im Automatikbetrieb: würde ohne Rückfrage übernommen“ bzw. „würde auf Ihre Freigabe warten – Gründe“.
- Buttons **„✓ Übernehmen (Ergebnisse und Spielplan)“** (gesperrt bei Fehlern) und **„✕ Verwerfen“**; danach Hinweis
  „Freigabe hinterlegt“. A und B werden immer gemeinsam übernommen.
- **Protokoll der letzten 14 Tage:** je Lauf Zeit, Abfragen, neue Spiele, Korrekturen, Spielplan (wichtig ·
  Anstosszeiten), Prüfung, Status (wartet, übernommen, verworfen, ersetzt, fehlgeschlagen mit Meldung).
- **Schnappschüsse (Werte vor dem Anpfiff)** (seit 0.20, `07`, 4.9): letzter Lauf (✓, rot ✕ bei einem Fehler oder wenn
  er älter als 2 Stunden ist), neu (davon nachträglich), erste Ergebnisse, Dauer; je Liga neu, vorhanden und „wartet
  auf Vorspiel-Ergebnis“; die wartenden Spiele mit Datum. E-Mail-Alarm ab 0.22.
- **Anzeigenamen der Website (Deutsch/Englisch)** (seit 0.21, `08`, 4.1): Vereine der jeweils neuesten Saison im
  Spielplan ohne Eintrag in `app/config/teamnamen_anzeige.csv`, mit Liga und Name der Datenquelle (sonst ✓). Die Website
  zeigt dort bis zum Nachtrag (über GitHub) den Namen der Datenquelle; die Veröffentlichung wird nicht blockiert.
- Nach der Testphase (Datum `automatisch_ab`) verschwinden die Buttons; das Protokoll bleibt. Fassungen mit Fehlern,
  kritischen Punkten oder neuen Warnungen werden nie automatisch übernommen.

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
| 6       | Einstufung   | Nicht auffällig oder auffällig mit Signalqualität (seit 0.19) |
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
| 6       | Einstufung   | Nicht auffällig oder auffällig mit Signalqualität (seit 0.19) |
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
| 6       | Einstufung   | Nicht auffällig oder auffällig mit Signalqualität (seit 0.19) |
| 7       | Datenbasis   | Anzahl verwendeter Spiele                               |
| 8       | Beschreibung | Überschrift und Beschreibung exakt gemäss KPI-Regelwerk |

Die Anzahl der verwendeten Referenzspiele der Liga soll ebenfalls nachvollziehbar sein.

Diese Information kann kompakt in der Spalte «Datenbasis» oder über einen Tooltip dargestellt werden. Dafür soll keine zusätzliche Hauptspalte entstehen.

## 8. Darstellung der Auffälligkeiten (seit Version 0.19)

Die Auffälligkeiten sollen in der Tabelle schnell und eindeutig erkennbar sein. Seit 0.19 zeigt der Punkt den **Signalqualität** (Zwischenstand bis zum Designentwurf, Design-Briefing 18.11.2026): eine Farbe in drei Stufen, damit er nicht mit der Richtung (mehr/weniger) verwechselt wird.

| **Status**                         | **Darstellung**                 |
|------------------------------------|---------------------------------|
| Nicht auffällig (oder vorläufig)   | heller, umrandeter Punkt        |
| Auffällig · Signalqualität gering    | hell-türkiser Punkt mit Rand    |
| Auffällig · Signalqualität mittel    | türkiser Punkt                  |
| Auffällig · Signalqualität stark      | dunkel-türkiser Punkt           |

Bis 0.18: grau = keine, gelb = leichte, rot = starke Anomalie.

Die Richtung der Abweichung wird über den Prozentwert mit Vorzeichen dargestellt (z. B. +24,50 %, −18,20 %). Die genauen Schwellen und Signalqualität stehen im KPI-Regelwerk (2.2) und in `schwellen.toml`; sie dürfen nicht im Frontend neu definiert werden.

KPI01 Formkurve erhält keine Einstufung.

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

15. Der Bereich Top Anomalien zeigt höchstens vier Einträge gemäss der Auswahl-Logik in Kapitel 5 (seit 0.19 nach Signalqualität mit Liga-Mix).

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
