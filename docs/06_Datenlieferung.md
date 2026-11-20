# Soccer Intelligence – Datenlieferung über API-Football (Spezifikation)

**Version 0.9** · Stand 20.11.2026 (v0.9: Spezifikation Lauf nach jedem Spiel und Übernahme ohne Freigabe, 10.2, zur Freigabe; v0.8: Entwurf Abfrageplan ab 0.22, 10.2; v0.7: stündlicher Schnappschuss-Lauf, Version 0.20) · **Status: freigegeben von Carsten am 15.11.2026; v0.4: Ergebnis des Vollvergleichs; v0.5: Tagesbetrieb umgesetzt (Version 0.14); v0.6: Ergebnis-Import v1.1 nach Review (R1–R9, Abschnitt 10.1) und Spielplan nach `07_Spielplan_Anzeige.md` (Version 0.15)** · Grundlage: Entwurf v0.1 (ChatGPT,
15.11.2026), kritisch geprüft und ergänzt von Claude (v0.2); Entscheidungen E1–E12 von Carsten am 15.11.2026 (v0.3).

Diese Datei ist die einzige Stelle für die Datenlieferung: Datenquelle, Feldzuordnung, Abläufe, Abfragebudget und
offene Entscheidungen. Der Prüfbericht des Vollvergleichs kommt später nach `docs/tests/pruefprotokoll_api.md`.
Programmiert wird erst nach Freigabe dieser Spezifikation (Arbeitsweise: Vorschlag → Freigabe → Umsetzung).

---

## 0. Kurzfassung

- **Quelle:** API-Football (API v3, `v3.football.api-sports.io`). **Tarif:** Pro, 3 Monate für 43,20 $ (Entscheidung
  Carsten). Der Gratis-Plan enthält nur die Saisons 2022–2024 und reicht nicht für den Tagesbetrieb (Test 15.11.2026).
- **Phase 1 – Datenquelle wechseln:** gleiche Datenbank mit 58 Spalten, KPI-Regelwerk unverändert. Der **Vollvergleich**
  aller Saisons 2018/19–2025/26 (15.11.2026) erfüllte die 99 % bei Gelben Karten und Schüssen aufs Tor nicht. Darum
  (Entscheidung Carsten 15.11.2026): **Altbestand bleibt die Grundlage** und wurde **mit zwei Quellen bereinigt**
  (API-Football und football-data.co.uk einig, Altbestand abweichend → korrigiert); **ab dem Stichtag kommen neue Spiele
  nur von der API** (2025/26 stimmen alle drei Quellen zu 99–100 % überein). Abschnitt 9.
- **Danach Tagesbetrieb:** täglich um 04:00 (Europe/Zurich; bis 0.14 Montag bis Freitag) neue Spiele, Statistiken und Spielplan holen;
  daraus eine **neue Fassung** der Excel-Dateien erzeugen, prüfen und tauschen. Die bestehende Datei wird nie
  verändert.
- **Teamnamen:** künftig die Namen von API-Football (E6), je Team-ID fest hinterlegt.
- **Rohdaten:** Jede API-Antwort wird unverändert gespeichert. Damit sind spätere Auswertungen ohne neue Abfragen
  möglich. Wettquoten und Verletzungen folgen in Phase 2, rückwirkend (E10, geändert 15.11.2026).
- **Phase 2 – Anreicherung (später):** weitere Statistiken, Tabellenstände (selbst berechnet), Wettquoten,
  Verletzungen, Datensatz für Machine Learning.

## 1. Ausgangslage

- Heute pflegt Carsten `data/Database-Soccer-Intelligence.xlsx` (58 Spalten, Aufbau `02_Datenbasis.md`) und
  `data/Spielplan.xlsx` (`04_Spielplan.md`) von Hand und lädt sie hoch (`01`, Abschnitt 6.2).
- **Footiqo** (Excel-Lieferung, Gespräche bis 06.11.2026) wurde verworfen: Lieferung nur dienstags und freitags um die
  Mittagszeit, also zu spät für die Analyse der kommenden Spieltage; neues Angebot 19 € statt 9 € je 4 Wochen.
- **API-Football** liefert Ergebnisse und Statistiken in der Regel am Morgen nach dem Spiel und den Spielplan
  der ganzen Saison. Gewählt am 15.11.2026.

## 2. Ziel und Abgrenzung

**Ziel Phase 1:** Wechsel der Datenquelle, **keine** Neuentwicklung des KPI-Modells.

- Alle 58 Spalten bleiben erhalten (Namen, Reihenfolge, Bedeutung, Format). Keine Spalte kommt dazu.
- Das KPI-Regelwerk (`03_KPI_Regelwerk.md`) gilt unverändert: letzte 5/10 Spiele, Ligareferenz über 20 Spieltage,
  2-Tage-Regel, fehlende Werte nie als 0, gerundete Abweichung, gültige Schwellen.
- Die bestätigten Testfälle (`docs/tests/`) laufen weiter mit ihren Referenzkopien in `tests/referenz/`.
- Fehlende API-Werte bleiben **leer**; `null` wird nie zu 0; eine echte 0 bleibt 0.

**Nicht Teil von Phase 1:** neue KPIs, neue Spalten, Tabellenstände, Verarbeitung von Wettquoten und Verletzungen
(nur Sammeln, E10), Machine Learning (siehe Abschnitt 13), KPI-Freigabe je Liga (geparkt, Diskussionspapier vom 14.11.2026).

## 3. Tarif, Kontingent und Grundsätze der Abfrage

| Punkt | Festlegung |
|---|---|
| Gratis-Plan | 100 Abfragen pro Tag, nur Saisons 2022–2024. Test 15.11.2026: `fixtures?league=78&season=2026` → „Free plans do not have access to this season, try from 2022 to 2024.“ |
| Betrieb | **Pro**, 3 Monate (43,20 $), laut Anbieter 7'500 Abfragen pro Tag. Vor Abschluss im Dashboard prüfen: automatische Verlängerung, und bei Überschreitung **sperren statt Zusatzkosten**. |
| Eigene Obergrenze | **500 Abfragen pro Tag** im Tagesbetrieb (Schutz gegen Fehler im Skript; für den einmaligen Vollvergleich 4'000, Abschnitt 12). Bei Erreichen stoppen alle nicht zwingenden Abrufe, und es erscheint eine Meldung. |
| Zählung | Jede HTTP-Anfrage zählt als eine Abfrage, unabhängig von der Anzahl Spiele in der Antwort (laut Anbieter, im Test zu bestätigen). Das verbleibende Kontingent steht in den Antwort-Kopfzeilen (`x-ratelimit-requests-remaining`, zu bestätigen); `status` zählt nicht. |
| Minutenlimit | Abfragen gedrosselt (höchstens eine pro Sekunde, im Test anpassen). |
| Fehler | Höchstens 3 Wiederholungen mit wachsender Wartezeit, danach Abbruch mit Meldung; nie eine Endlosschleife. |
| Schlüssel | API-Schlüssel nur in `.env` auf dem Server (wie der Passwort-Hash), nie in Code, Logs, Rohdaten, Excel oder Git. Für Tests von Claude über das sichere Formular der Arbeitsumgebung, nie im Chat. **Der am 15.11.2026 auf einem Screenshot sichtbare Schlüssel wird vor dem Betrieb ersetzt.** |
| Daten zuerst sichern | Jede Antwort wird zuerst als Rohdatei gespeichert (Abschnitt 11), erst danach verarbeitet. |

## 4. API-Grundlagen

| Punkt | Inhalt | Geprüft? |
|---|---|---|
| Ligen | Bundesliga **78**, Premier League **39**, Serie A **135**, LaLiga **140** | ja (Bundesliga 78, Saison 2026 „Current“) |
| Saison | API-Saison = Startjahr: `2025` ↔ `2025/2026` | ja |
| Zeitzone | `timezone=Europe/Zurich`; unsere Spalte `matchDate` steht schon in mitteleuropäischer Zeit (Beispiel Bundesliga 08.11.2026, 19:30) | zu bestätigen im Vergleich |
| Spielliste | `fixtures?league=…&season=…` liefert die ganze Saison (alle Runden, Status, Ergebnisse) in **einer** Abfrage | zu testen |
| Mehrfachabfrage | `fixtures?ids=ID1-ID2-…` (bis 20 Spiele) liefert je Spiel zusätzlich `events`, `lineups`, `statistics`, `players` | zu testen (wichtigste offene Frage) |
| Halbzeit-Statistik | `fixtures/statistics?fixture=…&half=true`, laut Anbieter erst ab Saison 2024; eine Abfrage je Spiel | zu testen |
| Status | `status` zeigt Plan und Verbrauch, zählt nicht zum Kontingent | zu testen |

## 5. Feldzuordnung der 58 Spalten

Status: **D** = direkt übernehmbar · **T** = mit Umwandlung · **E** = aus Ereignissen gezählt · **H** = nur ab 2024
(Halbzeit-Statistik) · **A** = Altbestand behalten, falls die API nichts liefert. Alle Zuordnungen werden im Vollvergleich
geprüft; vorher gelten sie als „noch nicht geprüft“.

| Spalte(n) | Inhalt | API-Quelle | Umwandlung | Status |
|---|---|---|---|---|
| A `Date` | Spieldatum | `fixture.date` | Datum ohne Uhrzeit, Europe/Zurich | T |
| B `Gameday` | Spieltag | `league.round` „Regular Season – 12“ | Zahl aus dem Text; Nachholspiel muss die ursprüngliche Runde behalten (Regel `02`) | T, zu prüfen |
| C `id` | Spiel-ID | bestehende Spiele: unverändert · neue: `fixture.id` | Entscheidung E2 | T |
| D `matchDate` | Datum und Uhrzeit | `fixture.date` | Text `TT-MM-JJ HH:MM`, Europe/Zurich | T |
| E `Country` | Land | `league.country` | Germany, England, Italy, Spain wie bisher | T |
| F `League` | Liga | `league.name` | unsere Namen (Bundesliga, Premier League, Serie A, LaLiga) | T |
| G `Season` | Saison | `league.season` | `2025` → `2025/2026` | T |
| H, I `homeTeam`, `awayTeam` | Teams | `teams.home/away.id` | Name von API-Football, je Team-ID fest hinterlegt (E6) | T |
| J `referee` | Schiedsrichter | `fixture.referee` | „Name, Land“ → „Name“; Schreibweise kann abweichen (nur Anzeige) | T |
| K–M `FT …` | Endstand und Ergebnis | `score.fulltime` | H/D/A berechnen; Wertungsspiele siehe 6.3 | T |
| N–P `Full-Time …` | Endstand (doppelt, beabsichtigt) | wie K–M | identisch zu K–M | T |
| Q–S `First-Half …` | Halbzeitstand | `score.halftime` | H/D/A berechnen | T |
| T–V `Second-Half …` | Tore 2. Halbzeit | `score.fulltime − score.halftime` | getrennt, nicht kumuliert | T |
| W, X Ecken gesamt | Corner Kicks | `statistics` „Corner Kicks“ | Zahl; `null` bleibt leer | D |
| Y–AB Ecken je Halbzeit | Corner Kicks | `half=true` | ab 2024; vorher Altbestand | H, A |
| AC, AD Gelbe Karten gesamt | Yellow Cards (KPI 04) | `statistics` „Yellow Cards“ | Zählweise Gelb-Rot prüfen (6.2) | D, zu prüfen |
| AE–AH Gelbe Karten je Halbzeit | Karten-Ereignisse | `events` (type Card, Minute) | zählen nach Minute ≤ 45+ / > 45; alle Saisons möglich | E |
| AI, AJ Ballbesitz gesamt | Ball Possession | `statistics` | „55%“ → 55 | T |
| AK–AN Ballbesitz je Halbzeit | Ball Possession | `half=true` | ab 2024; vorher Altbestand | H, A |
| AO, AP Schüsse gesamt | Total Shots | `statistics` | Zahl; Zählweise Altbestand uneinheitlich (6.1) | D, zu prüfen |
| AQ–AT Schüsse je Halbzeit | Total Shots | `half=true` | ab 2024; vorher Altbestand | H, A |
| AU, AV Schüsse aufs Tor gesamt | Shots on Goal (KPI 09) | `statistics` | Zahl | D |
| AW–AZ Schüsse aufs Tor je Halbzeit | Shots on Goal | `half=true` | ab 2024; vorher Altbestand | H, A |
| BA, BB Schüsse daneben gesamt | Shots off Goal | `statistics` | Zahl; ohne geblockte (6.1) | D, zu prüfen |
| BC–BF Schüsse daneben je Halbzeit | Shots off Goal | `half=true` | ab 2024; vorher Altbestand | H, A |
| Blatt *Datenhinweise* | eigene Hinweise | – | bleibt unverändert, wird nie aus der API erzeugt | – |

**Für KPIs massgeblich** (Abnahme mit 99 %): Tore Endstand und Halbzeit (K, L, Q, R, T, U), Ecken gesamt (W, X), Gelbe
Karten gesamt (AC, AD), Schüsse aufs Tor gesamt (AU, AV), dazu Datum, Teams und Spieltag.

## 6. Bekannte Unterschiede und Risiken

### 6.1 Schüsse: Altbestand zählt uneinheitlich

Im Altbestand gilt meist „Schüsse gesamt > aufs Tor + daneben“: Geblockte Schüsse zählen zu „gesamt“, aber nicht zu
„daneben“. In einigen Saisons sind beide Werte gleich, dort fehlen die geblockten Schüsse in „gesamt“:

| Liga | Saisons mit gesamt = aufs Tor + daneben |
|---|---|
| Bundesliga | 2020/21–2023/24 (fast alle Spiele) |
| Premier League | 2023/24 |
| Serie A | 2018/19–2019/20, 2020/21 teilweise |
| LaLiga | keine |

Der Vergleich wertet die Schüsse darum **je Saison** aus. KPI 09 (aufs Tor) ist nicht betroffen; der Versuchs-KPI 12
(Offensivdruck) würde einheitlichere Werte erhalten.

### 6.2 Zählweisen, die der Vergleich klären muss

- **Gelb-Rot:** Zählt die zweite Gelbe als Gelbe Karte (Altbestand und API)? Wirkt direkt auf KPI 04.
- **Karten für Trainer oder Ersatzspieler auf der Bank:** zählen sie mit?
- **Eigentore:** gehen in den Endstand ein (unverändert); nur bei Torminuten aus Ereignissen relevant.
- **Nachspielzeit:** Ereignisse in der Nachspielzeit der 1. Halbzeit gehören zur 1. Halbzeit (`time.elapsed` 45 plus `time.extra`).
- **Fehlende Statistik:** kommt sie als `null`, als fehlender Eintrag oder als 0? Nur eine ausdrücklich gelieferte 0 ist eine 0.

### 6.3 Wertungsspiele und eigene Korrekturen

- Die Datenbank führt das **Ergebnis auf dem Platz**, nicht die Wertung (Union Berlin – Bochum 2024/25, Verona – Roma
  2020/21; `02_Datenbasis.md`). Die API liefert bei Wertungen vermutlich das gewertete Ergebnis (Status `AWD`/`WO`).
  Solche Spiele werden **nie automatisch** übernommen, sondern gemeldet.
- **Eigene Korrekturliste:** Nachträge, Löschungen (z. B. Serie A 2019/20, Entscheidungsspiel Spezia – Verona) und
  Korrekturen aus `02` stehen in einer Liste, die bei jeder Erzeugung der Datenbank angewendet wird. Sie gehen durch
  den Wechsel der Quelle nicht verloren.

### 6.4 Halbzeit-Statistiken vor 2024

Ecken, Ballbesitz und Schüsse je Halbzeit liefert die API erst ab 2024. Vor 2024 bleiben die Werte des Altbestands
(Entscheidung Carsten 15.11.2026), sofern der Vollvergleich die übrigen Felder bestätigt. Keine dieser Spalten wird
heute von einem KPI genutzt.

## 7. Spiel-ID, Teamnamen und Stichtag

- **Bestehende Spiele** behalten ihre `id`; es gibt keine Umnummerierung.
- **Neue Spiele** (ab Stichtag, E4) erhalten als `id` die API-Fixture-ID (E2). Kollisionen sind ausgeschlossen: unsere IDs
  liegen heute unter 160'000, die API-IDs über 1 Million. So bleiben es 58 Spalten.
- **Zuordnung alter Spiele zu API-Spielen** (für Vergleich und Erzeugung): über Liga, Saison, Heimteam, Gastteam und
  Datum. Die Zuordnungstabelle (unsere `id` ↔ API-ID) wird als eigene Datei gespeichert und ist danach fest.
- **Teamnamen (E6, Carsten 15.11.2026): die Namen von API-Football** (z. B. statt `FC Koln` der Name der API). Sie
  werden je Team-ID **einmal festgehalten** (`app/config/teams.toml`, Felder `api_team_id` und `team_name`), damit eine
  spätere Namensänderung bei der API (z. B. Sponsor) nicht still alle Spiele umbenennt; eine Änderung wird gemeldet.
  Mit dem automatischen Spielplan (Phase 4, E14) erhalten **alle** Spiele, auch die historischen, die neuen Namen; ebenso der Spielplan.
  Die Testfälle in `docs/tests/` und `tests/referenz/` behalten ihre bisherigen Namen (eigene Referenzkopien).
  Neue Teams (Aufsteiger) werden gemeldet, nie geraten.
- **Doppelte Spiele** sind ausgeschlossen: Ein Spiel wird über seine Fixture-ID erkannt, auch nach einer Verlegung.

## 8. Spielplan

Der Spielplan wird aus den Spiellisten der API erzeugt (laufende Saison und Vorsaison, je eine Abfrage je Liga).
Zielformat: `Spielplan.xlsx` nach `04_Spielplan.md`. **Regeln seit Version 0.15:** `07_Spielplan_Anzeige.md`,
Abschnitt 3 (Status nur aus der API mit Originalcode, Datum = Termin laut API, Vermerk Nachholspiel/vorgezogen,
Termin bestätigt/Zeit offen/vorläufig, feste Zuordnung eigene ID ↔ API-ID). Die frühere Regel „mehr als 3 Tage
ausserhalb = verschoben“ (v0.3–v0.5) ist damit ersetzt.

## 9. Phase A: Vollvergleich (Skript A)

**Zweck:** Prüfen, ob die API-Daten unseren Altbestand ersetzen können. Keine Änderung an produktiven Dateien.

- **Umfang:** alle Spiele 2018/19–2025/26 der vier Ligen (rund 11'000), dazu Halbzeit-Statistiken 2024/25 und
  2025/26. Statt der 200 Stichproben aus v0.1, weil das Kontingent von Pro das erlaubt und kleine Stichproben
  Zählweisen übersehen können.
- **Ablauf:** Spielliste je Liga und Saison → Zuordnung zu unseren Spielen → Mehrfachabfrage (20 Spiele je Abfrage) →
  Rohdaten speichern → Umwandlung nach Abschnitt 5 → Vergleich Feld für Feld.
- **Bericht** (`docs/tests/pruefprotokoll_api.md`) je Liga, Saison und Feld: Anzahl verglichen, gleich, abweichend,
  fehlend (API oder Altbestand), mit Beispielen. Jede Abweichung wird eingeordnet als technische Abweichung (Format),
  echte Datenabweichung, andere Zählweise oder fehlender Wert. Dazu: nicht zuordenbare Spiele, Wirkung auf die KPIs
  (KPI-Werte mit beiden Quellen gerechnet, Anzahl geänderter Anomalien).
- **Abnahmeregel (Carsten 15.11.2026):** Sind die für KPIs massgeblichen Felder (Abschnitt 5) zu **mindestens 99 %**
  identisch, wird umgestellt. Bei geringerer Übereinstimmung entscheidet Carsten anhand des Berichts.
- **Danach** läuft die Sensitivitätsanalyse einmal mit den neuen Daten, um zu bestätigen, dass die gültigen
  Schwellen weiter passen.

**Ergebnis 15.11.2026** (`docs/tests/pruefprotokoll_api.md`): Zuordnung 100 %; Tore, Datum, Spieltag und Ecken über
99 %; Gelbe Karten 97,2 %, Schüsse aufs Tor 89,6 % → Abnahmeregel nicht erfüllt. Dreifachvergleich mit
football-data.co.uk: Bei Gelben Karten weicht meist der Altbestand ab, bei Schüssen aufs Tor (Serie A 2018/19–2020/21,
Bundesliga 2019/20–2023/24) meist die API. **Entscheidung Carsten:** keine vollständige Umstellung, sondern
**Bereinigung des Altbestands mit zwei Quellen** (1'932 Zellen, 76 Spieltage; `02_Datenbasis.md`, Abschnitt 4e).
Sensitivitätsanalyse danach: unverändert ausser KPI 04 stark (Mehrwert positiv +10,37 → +6,45, negativ +6,70 → +5,00).

## 10. Phase B: Tagesbetrieb (Skript B)

**Rhythmus:** täglich um 04:00 Europe/Zurich (E8, geändert 15.11.2026: auch am Wochenende, synchron zu den Spieltagen). Geprüft mit der 2-Tage-Regel: Wochenendspiele sind am
Montag da, Montagsspiele am Dienstag, Spiele unter der Woche am Folgetag, also immer vor dem nächsten Spieltag.

**Seit 0.20 zusätzlich stündlich:** der Schnappschuss-Lauf im selben Container (`importer/schnappschuss.py`): Werte jedes
Spiels ab einer Stunde vor dem Anpfiff einfrieren, fehlende nachholen, erstes Ergebnis festhalten; nach jeder Übernahme
sofort ein weiterer Lauf. Er liest nur `data/` und schreibt nur nach `/import/schnappschuesse/` (Regeln: `07`, 4.9).
Keine Abfragen bei API-Football.

**Ablauf je Lauf:**

```
1. Kontingent prüfen (status)
2. Spielliste je Liga holen (4 Abfragen): Ergebnisse, Status, Spielplan der ganzen Saison
3. Spiele bestimmen (Entscheidung Carsten 15.11.2026, ersetzt „seit dem letzten Lauf plus 3 Tage“):
   - jedes beendete Spiel der Saison, das noch nicht in der Datenbank steht (auch Nachholspiele, egal wie spät)
   - Spiele mit API-ID der letzten 2 Spieltage je Liga neu holen; montags alle Spiele der Saison mit API-ID
   - Spiele mit API-ID, deren Statistik noch unvollständig ist
4. Details dieser Spiele per Mehrfachabfrage holen (20 Spiele je Abfrage), ab 2024 Halbzeit-Statistik je Spiel
   (für neue Spiele und die letzten 2 Spieltage)
5. Rohdaten speichern
6. Neue Fassung erzeugen: Altbestand + neue Spiele (+ geänderte Werte) + eigene Korrekturliste
   → import/laeufe/<Lauf>/Database-Soccer-Intelligence.xlsx und Spielplan.xlsx, dazu bericht.json
7. Prüfen mit den bestehenden Prüfregeln (02, 04) und Vergleich mit der gültigen Fassung
8. Tauschen nach Freigabe im Reiter „Datenimport/API“ (E3, E15) oder bei Problemen nichts ändern und melden
9. Protokoll: Abfragen, neue Spiele, Korrekturen, fehlende Werte, Meldungen
```

**Regeln:**
- **Prüfschranke:** Eine neue Fassung wird nur gültig, wenn alle Prüfungen bestanden sind. Lieber veraltete als falsche
  Daten.
- **Vergleich neu gegen bisher:** neues Spiel → übernehmen · leerer Wert jetzt gefüllt → übernehmen und melden ·
  gefüllter Wert jetzt anders → melden, Carsten entscheidet · Spiel fehlt plötzlich → Fassung ablehnen.
- Spiele **ohne Statistik** am Morgen nach dem Spiel werden mit leeren Werten übernommen und bei den nächsten Läufen
  nachgefüllt (höchstens 7 Tage lang, danach Meldung). Sie gelten als „offen“ und sperren die Übernahme nicht; gesperrt
  wird nur bei Fehlern (E16).
- **Verschiebungen** brauchen kein Vormerken: Jeder Lauf holt die ganze Spielliste der Saison (4 Abfragen); Status und
  neuer Termin stehen darin, und ein spät gespieltes Spiel wird automatisch aufgenommen. Im Spielplan wird es
  automatisch „verschoben“ (E17).
- **Korrekturen** der API an Spielen mit API-ID erscheinen mit altem und neuem Wert im Reiter und werden nur mit der
  Freigabe übernommen; ein leerer API-Wert überschreibt nie einen vorhandenen.
- Es wartet immer höchstens **eine** Fassung; ein neuer Lauf ersetzt die wartende und baut auf der gültigen auf.
  Übernommen wird nur, wenn die gültigen Dateien seit dem Lauf unverändert sind (sonst baut der nächste Lauf neu auf).
- Spiele vor dem Stichtag werden im Tagesbetrieb **nie** verändert.
- Die ersetzte Fassung kommt nach `backup/`. Das Dashboard liest die neue Datei beim nächsten Aufruf automatisch.

**Technik (umgesetzt in Version 0.14):** eigener kleiner Container `soccer-import` (gleiches Image, Befehl
`python -m importer.dienst`, Code in `app/importer/`); er legt jede neue Fassung mit Bericht unter
`import/laeufe/<lauf>/` ab und tauscht nach Freigabe (Backup `backup/*_vor_import.xlsx`, die letzten 30, Tausch in
einem Schritt). Das Dashboard liest `import/` nur und schreibt ausschliesslich Freigabe-Anfragen nach `import/anfragen/`. Wiederverwendung von Loader
und Prüfregeln aus `app/core/`. Kein Eingriff in Traefik oder andere Container; Einrichtung nur mit Freigabe Carsten
(Schutzregeln `01`, Abschnitt 5).

### 10.1 Regeln seit Version 0.15 (Spezifikation Ergebnis-Import v1.1, Review ChatGPT, Entscheidungen Carsten 15.11.2026)

| Nr. | Thema | Regel |
|---|---|---|
| R1 | Korrekturen der API | **Korrekturfenster 7 Tage:** Ändert die API bis 7 Tage nach dem Spiel einen Wert, übernimmt der Import ihn selbst (auch im Automatikbetrieb). Danach ist das Spiel **eingefroren**: Eine Änderung erscheint im Reiter als „späte Korrektur“ mit zwei Buttons (übernehmen / bisherigen Wert behalten). Ein leerer Wert, der gefüllt wird, ist keine Korrektur und wird immer übernommen. Niemand schreibt von Hand in eine Datei: Die Entscheide hält der Dienst in `import/entscheidungen.json` fest (Backup mit jeder Übernahme), jeder Lauf wendet sie an, ein entschiedener Punkt wird nie wieder gefragt. |
| R2 | Gewertete Spiele | Die Datenbank führt das **Ergebnis auf dem Platz** (`02`). Nie ausgetragene Spiele (AWD/WO) kommen nicht in die Datenbank, stehen im Spielplan als `gewertet` und zählen bei der Vollständigkeit nicht als „fehlt“; ein Forfait-Ergebnis zählt **nicht** zur Formkurve. Die API meldet Wertungen auch als FT mit dem gewerteten Ergebnis (Verona – Roma 2020/21: FT 3:0, auf dem Platz 0:0). Darum: **Endstand muss zu den Tor-Ereignissen passen**, sonst wartet das Spiel (bzw. die Tor-Korrektur) auf einen Entscheid im Reiter: „Ergebnis auf dem Platz“ (Tore aus den Ereignissen) oder „Endstand der API“. Vollvergleich: 11'963 von 11'978 Spielen stimmen überein. |
| R3 | Gelbe Karten | Zählweise (geprüft an 24'000 Teamwerten): **Gelb-Rot = 2 Gelbe Karten**, direkte Rote zählt nie als Gelbe; so zählen API-Statistik, Altbestand und football-data.co.uk. Ersatz aus den Ereignissen bei leerem API-Wert (E13) nur noch, wenn die Tor-Ereignisse zum Endstand passen (Ereignisse wirken vollständig). Festgehalten im KPI-Regelwerk, KPI 04. |
| R4 | Fehlende Statistik | KPI-Regel unverändert (letzte 10 Spiele, Spiele ohne Wert fallen weg, Datenbasis und „vorläufig“). Der Bericht nennt bei offenen Spielen die fehlenden KPI-Felder. Die Variante „letzte 10 Spiele **mit** Wert“ ist für die KPI-Überarbeitung vorgemerkt (Regelwerk, Abschnitt 8). |
| R5 | Automatikbetrieb | Automatisch übernommen wird nur eine **unkritische** Fassung: keine Fehler, keine kritischen Punkte (Endstand ≠ Tor-Ereignisse, Spiel verschwindet aus der API-Liste, Widerspruch in der Zuordnung, „noch nicht gespielt“ mit vergangenem Termin), keine Plausibilitätswarnung, keine **neue** Warnung der Prüfregeln. Bekannte Warnungen blockieren nicht. |
| R6 | Plausibilität neuer/geänderter Spiele | **Fehler:** negative Werte, Halbzeit-Tore grösser als Endstand, Schüsse aufs Tor grösser als Schüsse gesamt, doppelte id. **Warnung:** je Team mehr als 30 Ecken, 10 Gelbe, 25 Schüsse aufs Tor, 9 Tore (Grenzen Carsten). **Hinweis:** fehlende Statistik. Gilt nur für neue und geänderte Spiele; der Altbestand behält seine bekannten Meldungen. |
| R7 | Zwei Quellen | Nachweis 2025/26 im Prüfprotokoll (`docs/tests/pruefprotokoll_api.md`, Abschnitt 7). Keine rückwirkende Bereinigung mehr. |
| R8 | IDs | Keine neue Spalte. Jede id nur einmal **über alle Ligen** (Fehler), feste Zuordnung eigene ID ↔ API-ID in `app/config/zuordnung_api.csv` (11'978 Spiele, geprüft über Datum und Endstand). |
| R9 | Rohdaten | 12 Monate aufbewahren, ältere Tagesordner löscht der Dienst. |

### 10.2 Lauf nach jedem Spiel und Übernahme ohne Freigabe (seit Version 0.22) – freigegeben von Carsten am 20.11.2026

**Beschlüsse Carsten 20.11.2026:**

| Nr. | Thema | Beschluss |
|---|---|---|
| B1 | Lauf nach jedem Spiel | Je Anstosszeit ein Lauf bei **Anpfiff + 2¼ Stunden**. Er holt **Endstand, Status und alle Statistiken** der beendeten Spiele und schreibt sie in die Datenbank und den Spielplan. |
| B2 | Keine Freigabe mehr | Jede fehlerfreie Fassung wird **sofort übernommen**, auch die des Laufs um 04:00. Der Knopf „Übernehmen“ im Reiter Datenimport/API entfällt. |
| B3 | Kontrolllauf | Der tägliche Lauf um **04:00** bleibt (Abschnitt 10, montags die ganze Saison) und gleicht alles nochmals ab. Kein zusätzlicher Lauf um 01:00. |
| B4 | Wiederholung | Scheitert ein Lauf, läuft ein Spiel noch (Verlängerung, Unterbrechung) bzw. hat es trotz Anstosszeit vor über 2 Stunden nicht begonnen, oder fehlen nach ihm noch Werte eines Spiels, folgt **1 Stunde später** eine Wiederholung, höchstens zwei. Danach übernimmt der Kontrolllauf; ab 0.23 kommt eine Alarm-Mail. |
| B5 | Backups | Vor jedem Tausch ein Backup, gestaffelt aufbewahrt (Regel 7). |

**Regeln:**

1. **Laufplan:** Die Laufzeiten entstehen aus dem gültigen Spielplan (Europe/Zurich) und werden nach jedem Lauf neu
   berechnet; Verschiebungen und neue Termine wirken so automatisch. Gleiche Anstosszeiten ergeben einen Lauf; Läufe,
   die weniger als 30 Minuten auseinanderliegen, werden zum späteren zusammengelegt. Spiele ohne Anstosszeit lösen
   keinen Lauf aus (sie kommen mit dem Kontrolllauf). Beispiel Samstag 21.11.2026 (Anstösse 13:30 bis 21:00 in vier
   Ligen): Läufe um 15:45, 16:15, 17:15, 17:45, 18:30, 20:15, 20:45 und 23:15, zusammen 8.
2. **Ablauf:** Jeder Lauf ist ein normaler Lauf nach Abschnitt 10 (Spielliste je Liga, neue Fassung, alle Prüfungen
   10.1), nur die Auswahl der Spiele ist kleiner: die Spiele seiner Anstosszeit(en) und alle Spiele der letzten
   7 Tage mit fehlenden Werten. Liegt ein Lauf in der Stunde des Kontrolllaufs, entfällt er.
3. **Übernahme:** Übernommen wird wie im Automatikbetrieb (R5), jetzt für jeden Lauf und ohne Testphase
   (`automatisch_ab` = Datum des Einspielens). Die Prüfschranke bleibt: Fehler → nichts wird geschrieben, die gültigen
   Dateien bleiben, Meldung im Reiter (ab 0.23 per Mail).
4. **Kritische Spiele** (R5: Endstand passt nicht zu den Tor-Ereignissen, späte Korrektur nach 7 Tagen, Widerspruch
   in der Zuordnung, Spiel verschwindet aus der API-Liste): Heute sperren sie die ganze Fassung. **Vorschlag:** Nur das
   betroffene Spiel bzw. der betroffene Wert wird zurückgehalten und wartet im Reiter auf deinen Entscheid; alles
   andere wird übernommen. So blockiert ein einzelnes Spiel nicht den ganzen Spieltag. *(Frage F1)*
5. **Fehlende Statistik:** Liefert die API kurz nach dem Spiel nur Endstand und Status, wird das Spiel mit leeren
   Werten geschrieben (wie heute, Abschnitt 10) und von der Wiederholung bzw. dem Kontrolllauf nachgefüllt. Fehlende
   Werte zählen nie als 0. Korrekturen der API bis 7 Tage nach dem Spiel übernimmt jeder Lauf selbst (R1). Die
   Warnungen „Statistik fehlt“ und „Spieltag unvollständig“ sind direkt nach dem Spiel normal und **sperren die
   Übernahme nicht** (Nachprüfung 20.11.2026); sie bleiben im Bericht und im Bereich Datenqualität.
6. **Schreiben:** Vor dem Tausch ein Backup; der Tausch geschieht in einem Schritt (neue Datei fertig geschrieben und
   geprüft, dann ersetzt), Dashboard und Website sehen nie eine halbe Datei (umgesetzt seit 0.15.1). Übernommen wird
   nur, wenn die gültigen Dateien seit Beginn des Laufs unverändert sind; sonst baut der nächste Lauf neu auf.
   Werte vor dem Anpfiff ändern sich dadurch nicht: Sie sind im Schnappschuss eingefroren (`07`, 4.9).
7. **Backups** in `backup/` (ersetzt „die letzten 30“):

   | Stufe | Was bleibt | Wie lange |
   |---|---|---|
   | Täglich | jedes Backup vor einem Tausch | 14 Tage |
   | Wöchentlich | das letzte Backup jeder Woche (Montag bis Sonntag) | 8 Wochen |
   | Monatlich | das letzte Backup jedes Monats | 12 Monate |
   | Saisonende | das Backup nach dem letzten Spieltag jeder Saison (ab 1. Juli: Saison der Vorsaison) | dauerhaft |

   Das Aufräumen macht der Dienst nach jedem Tausch. Die Entscheide (`import/entscheidungen.json`) werden gleich
   gesichert. Zusätzlich einmal im Monat eine Kopie ausserhalb des Servers (Anleitung `01`, Abschnitt 6; Erinnerung in
   der Statusmail ab 0.23).
8. **Reiter Datenimport/API:** statt Freigabe ein Protokoll: heutige und geplante Läufe (Zeit, Anlass, Status:
   geplant / übernommen / ohne Änderung / wiederholt / fehlgeschlagen), je Lauf geschriebene Spiele und gefüllte
   Werte, zurückgehaltene Spiele mit Entscheid-Knöpfen (R1, R2), nächster Lauf, Backups (Anzahl, Grösse).
9. **Ereignisprotokoll** `import/ereignisse.jsonl` (eine Zeile je Lauf und Ereignis): Grundlage für Alarme und die
   wöchentliche Statusmail in 0.23.
10. **Kontingent:** Ein Lauf braucht 4 Abfragen für die Spielliste plus wenige Mehrfachabfragen; ein voller
    Wochenend-Spieltag rund 50–100 zusätzlich. Eigene Obergrenze 500 pro Tag, Tarif Pro 7'500 pro Tag. Ist die eigene
    Obergrenze erreicht, entfallen weitere Läufe des Tages bis auf den Kontrolllauf.
11. **Schutzregel:** `01`, Abschnitt 5 wird angepasst: Der Import-Dienst schreibt nach bestandenen Prüfungen ohne
    Freigabe nach `data/`; alle anderen Regeln (nur eigener Ordner, Backup vor Änderungen, Excel nur durch den Dienst)
    bleiben.

**Tests (0.22):** Laufplan aus Spielplan (Zusammenlegen, ohne Anstosszeit, Verschiebung, Kollision mit 04:00),
Wiederholung (höchstens zwei, nur bei Fehler oder fehlenden Werten), Übernahme ohne Freigabe, kritisches Spiel
zurückgehalten (nach F1), leere Werte nie 0, Backup-Staffel (Stichtage über Jahreswechsel und Saisonende), Tausch nur
bei unveränderter Datei, Kontingent-Grenze; Probelauf mit Aufzeichnungen echter API-Antworten eines Samstags.

**Entscheide Carsten 20.11.2026:**
- **F1** Kritische Spiele werden einzeln zurückgehalten, der Rest übernommen (Regel 4): **ja**.
- **F2** Gefragt wird nur bei den kritischen Fällen aus Regel 4 sowie bei Fassungen mit Fehlern oder neuen Warnungen
  (Prüfschranke): **ja**.
- **F3** Ohne E-Mail in 0.22, Meldungen bis 0.23 nur im Reiter: **ja**.

**Umsetzung (0.22):** `importer/laufplan.py` (Laufzeiten, Fälligkeit, Wiederholung, Backup-Staffel), `importer/dienst.py`
(Anlass je Lauf: `kontrolle`, `spiel`, `wiederholung`; Ereignisprotokoll `import/ereignisse.jsonl`),
`importer/erzeugen.py` (`recheck=False` für Läufe nach dem Spiel; kritische Punkte sperren nicht mehr),
`app/config/import.toml` (`automatisch_ab = 2026-11-20`), Reiter Datenimport/API (Läufe heute, Anlass im Protokoll,
Entscheide auch ohne wartende Fassung). Tests L1–L5 (`tests/test_import_022.py`).

## 11. Rohdatenspeicher

- Jede API-Antwort unverändert als komprimierte Datei (`data/api_roh/<Jahr>/<Datum>/<Endpunkt>_<Parameter>.json.gz`).
- Dazu je Abfrage: Abrufzeit, Endpunkt, Parameter (ohne Schlüssel), Liga, Saison, Fixture-IDs, HTTP-Status,
  verbleibendes Kontingent, Verarbeitungsstatus.
- Nie in Git; im Backup enthalten. Geschätzt wenige hundert MB für alle Saisons.
- Die Excel-Fassung lässt sich jederzeit aus den Rohdaten neu erzeugen, ohne neue Abfragen.

## 12. Abfragebudget (Schätzung, im Test zu bestätigen)

| Vorgang | Abfragen |
|---|---|
| Vollvergleich: Spielliste je Liga und Saison (4 × 8) | 32 |
| Vollvergleich: Mehrfachabfrage, rund 11'000 Spiele ÷ 20 | ≈ 560 |
| Vollvergleich: Halbzeit-Statistik 2024/25 und 2025/26 (je Spiel) | ≈ 2'900 |
| **Vollvergleich gesamt** | **≈ 3'500**, einmalig, an einem Tag möglich (Pro). Für diesen Lauf gilt eine eigene Obergrenze von 4'000, die beim Start ausdrücklich gesetzt wird. |
| Tagesbetrieb: Status + Spielliste | 5 |
| Tagesbetrieb: Mehrfachabfrage (bis 38 Spiele) | 2–3 |
| Tagesbetrieb: Halbzeit-Statistik je Spiel | bis 38 |
| **Tagesbetrieb je Lauf** | **≈ 10–50**, weit unter 500 |

Mit Pro bleibt viel Reserve; die Planung „höchstens 80 pro Tag“ aus v0.1 ist damit nicht mehr nötig.

## 13. Phase 2: Anreicherung (später, eigene Spezifikation)

Nach dem Wechsel der Quelle, als eigener Schritt (Entscheidung Carsten 15.11.2026):

- **Weitere Statistiken** aus den Rohdaten, ohne neue Abfragen: Fouls, Abseits, geblockte Schüsse, Schüsse im und
  ausserhalb des Strafraums, Pässe, Paraden, xG (falls vorhanden), Torminuten, Aufstellungen.
- **Tabellenstände vor jedem Spieltag** selbst aus den Ergebnissen berechnet. Die API liefert nur die aktuelle Tabelle;
  für die Vergangenheit führte sie zu Wissen aus der Zukunft.
- **Wettquoten vor dem Spiel** und **Verletzungen/Sperren:** lassen sich vermutlich nicht nachträglich für vergangene
  Spiele abfragen (zu prüfen). Entscheidung 15.11.2026 (E10): beides in Phase 2, rückwirkend; historische Wettquoten
  gibt es für alle Saisons bei football-data.co.uk.
- **Datensatz für Machine Learning** als eigene Datei aus den Rohdaten; jedes Merkmal nur mit dem Wissen vor dem Spiel.

## 14. Tests und Abnahme

- **Datenstruktur:** 58 Spalten, Namen, Reihenfolge, Formate; Blatt *Datenhinweise* unverändert; erzeugte Datei besteht
  die Prüfregeln aus `02` und `04`.
- **Umwandlung:** je Feld ein Test mit gespeicherten Beispiel-Antworten der API (ohne Netz): Endstand, Halbzeit, 2.
  Halbzeit, Ecken, Karten (inkl. Gelb-Rot und Nachspielzeit), Ballbesitz „55%“, fehlender Wert bleibt leer, echte 0
  bleibt 0, Saison, Zeitzone, Spieltag aus der Runde.
- **Zuordnung:** neues Spiel wird angelegt; vorhandenes nicht verdoppelt; gleiche Teams an verschiedenen Terminen
  getrennt; verschobenes Spiel über die Fixture-ID aktualisiert; abweichende Teamnamen korrekt zugeordnet; unbekanntes
  Team gemeldet.
- **Spielplan:** neue Spiele ergänzt, mindestens 14 Tage, Verschiebungen und Absagen gekennzeichnet, Spieltag und
  Hauptzeitraum richtig.
- **Kontingent:** Zählung, Stopp bei der Obergrenze, keine Endlosschleife bei Fehlern.
- **Sicherheit:** kein Schlüssel in Code, Rohdaten oder Logs (Test sucht danach); bei Fehlern bleibt die gültige Fassung
  unverändert.
- **KPIs:** bestätigte Testfälle grün; Vollvergleich der Dashboard-Werte alte gegen neue Datenquelle mit Bericht.

## 15. Arbeitsphasen und Freigaben

| Phase | Inhalt | Ergebnis | Freigabe |
|---|---|---|---|
| 0 | Spezifikation (diese Datei) | v0.3, freigegeben 15.11.2026 | Carsten |
| 1 | Zugang: Pro-Abo; Schlüssel und Netzfreigabe für Claudes Arbeitsumgebung; Test der offenen API-Fragen (Abschnitt 4) | kurzer Testbericht | – |
| 2 | Skript A und Vollvergleich, nur in der Arbeitsumgebung, keine produktiven Dateien | `pruefprotokoll_api.md` | Carsten: Umstellung ja/nein |
| 3 | ~~Erzeugung der Datenbank aus API-Daten~~ → Bereinigung des Altbestands mit zwei Quellen; Vollvergleich der Dashboard-Werte; Sensitivitätsanalyse neu (**erledigt 15.11.2026**) | bereinigte Datenbank `3a258961…`, Prüfprotokoll | Carsten |
| 4 | Skript B und Container `soccer-import`, Reiter „Datenimport/API“, zuerst halbautomatisch (**umgesetzt in Version 0.14**) | Release mit Tests | Carsten |
| 5 | Abnahme nach 2 Wochen Betrieb; Entscheid über vollautomatischen Tausch | Eintrag CHANGELOG | Carsten |
| später | Phase 2: Anreicherung | eigene Spezifikation | Carsten |

## 16. Entscheidungen

| # | Frage | Stand |
|---|---|---|
| E1 | Tarif | **Entschieden:** Pro, 3 Monate (43,20 $). Gratis-Plan nur für erste Versuche (Saisons 2022–2024). |
| E2 | ID neuer Spiele | **Entschieden:** API-Fixture-ID als `id`; keine neue Spalte. |
| E3 | Automatisierung | **Entschieden:** 2 Wochen halbautomatisch (Carsten bestätigt den Tausch mit einem Befehl), danach automatisch. |
| E4 | Stichtag für API-IDs | **Entschieden:** erster Spieltag nach der Abnahme von Phase 3. |
| E5 | Halbzeit-Statistik ab 2024 | **Entschieden:** holen (rund 38 Abfragen je Spieltag). |
| E6 | Teamnamen | **Entschieden:** Namen von API-Football, je Team-ID fest hinterlegt (Abschnitt 7). |
| E7 | Umfang Vergleich | **Entschieden:** Vollvergleich aller Saisons statt 200 Stichproben; Abnahme bei mindestens 99 %. |
| E8 | Rhythmus | **Entschieden:** Montag bis Freitag 04:00 Europe/Zurich, je Lauf „seit letztem Lauf plus 3 Tage“. **Geändert 15.11.2026:** täglich 04:00 (Spielplan v2.1). |
| E9 | Abgebrochene Spiele (`ABD`) | **Entschieden:** neuer Status `abgebrochen` im Spielplan (Ergänzung `04`, Prüfregel und Anzeige wie `abgesagt`). |
| E10 | Wettquoten und Verletzungen | **Geändert 15.11.2026:** erst in Phase 2, dann rückwirkend ergänzt (vorher: ab Phase 1 sammeln). |
| E11 | Altwerte, die die API nicht liefert | **Entschieden:** behalten, sofern der Vergleich die übrigen Daten bestätigt. |
| E12 | Umstellung der ganzen Datenbank auf API-Daten | **Entschieden:** ja, wenn die KPI-Felder zu mindestens 99 % identisch sind. **Ergebnis:** nicht erfüllt; stattdessen Bereinigung mit zwei Quellen (Entscheidung 15.11.2026). |
| E13 | Gelbe Karten bei leerem API-Wert | **Entschieden 15.11.2026:** aus den Spielereignissen zählen (keine Karte = sichere 0). |
| E14 | Teamnamen-Umstellung | **Entschieden 15.11.2026:** erst mit dem automatischen Spielplan (Phase 4), weil Datenbank und Spielplan gleich geschrieben sein müssen. |
| E15 | Freigabe | **Entschieden 15.11.2026:** eigener Reiter „Datenimport/API“ mit „Übernehmen“ und „Verwerfen“, Vollständigkeit (Spielplan gegen Ergebnisse), Qualitätsbericht, Protokoll der letzten 14 Tage; Datenbank und Spielplan nur gemeinsam. |
| E16 | Fehlende Ergebnisse | **Entschieden 15.11.2026:** gelten als „offen“, sperren die Übernahme nicht; gesperrt wird nur bei Fehlern. |
| E17 | Verschiebungen | **Entschieden 15.11.2026:** im Spielplan automatisch eingetragen und unter „Spielplan-Änderungen“ gezeigt. |
| E18 | Erste Übernahme | **Entschieden 15.11.2026:** stellt die Teamnamen um und zeigt die vollständige Liste alt → neu. |
| E19 | Neu holen | **Entschieden 15.11.2026:** je Lauf die letzten 2 Spieltage, montags die ganze Saison (Spiele mit API-ID). |
| E20 | E-Mail-Benachrichtigung | **Später**, wenn alles läuft (Wunsch Carsten). |
| E21 | Review Ergebnis-Import (R1–R9) | **Entschieden 15.11.2026:** Abschnitt 10.1 (Korrekturfenster 7 Tage und Entscheide per Button statt Handarbeit, Ergebnis auf dem Platz, Gelb-Rot = 2 Gelbe, Automatik nur unkritisch, Plausibilität mit Grenzen 30/10/25/9, Zuordnungsdatei, Rohdaten 12 Monate). |
| E22 | Spielplan v2.1 (S1–S10, O1, O2) | **Entschieden 15.11.2026:** `07_Spielplan_Anzeige.md`. Import umgesetzt in 0.15, Anzeige folgt in 0.16 nach Designentwurf. |

Alle Entscheidungen von Carsten am 15.11.2026.

## Anhang: Vorgeschichte Footiqo (bis 07.11.2026)

Footiqo bot eine kumulative Excel-Datei (Historie ab 2020/21) über einen festen Download-Link an, zweimal pro Woche
aktualisiert, ohne API und ohne Spielplan. Preis: 49,99 € (Historie + 4 Wochen), danach 9,99 € je 4 Wochen; später
19 €. Verworfen wegen der Lieferzeiten (dienstags und freitags mittags). Die damals festgelegten Grundsätze
(Prüfschranke, Eingangsordner, eigene Korrekturen bleiben erhalten, Dashboard nur lesend) gelten weiter und sind oben
eingearbeitet.
