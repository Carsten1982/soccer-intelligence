# Soccer Intelligence – Öffentliche Website (Konzept und Protokoll)

**Version:** 1.1 · **Stand:** 17.11.2026 · **Umsetzung ab:** Version 0.17 (Grundgerüst, Spieltag), 0.18 (alle drei Seiten nach Entwurf)
**Grundlage:**
- Übergabe der Frontend-Entwürfe (Carsten, 16.11.2026, `Uebergabe_Frontend_Entwuerfe.md`)
- Entwürfe (Carsten, 17.11.2026, nochmals hochgeladen): Startseite „1d“ (`Main_P1`, ergänzend „1b“ `Main_C`), Spieltag „3d“ (`Spieltag_P1`), Matchdetail „2i“ (`Spiel_P1`, ergänzend „2c“ `Spiel_F`). Die älteren und neueren Entwürfe ergänzen sich (zeigen verschiedene Zustände)
- Entscheidungen Carsten vom 16.11.2026: T1–T5, F1–F8, Datenstand, Zeitreise; vom 17.11.2026: Q1–Q7

**Verlauf:** In 0.17 kamen die Entwürfe für Spieltag und Matchdetail nicht an (vom Upload entfernt); die Seite Spieltag entstand damals nach der Übergabe-Datei („Zu-Not-Weg“, Annahmen in Abschnitt 9). Seit **0.18** sind alle drei Seiten **genau nach den Entwürfen** gebaut; die damals nötigen Annahmen A1 und A2 sind damit ersetzt.

---

## 1. Ziel und Umfang

- Öffentliche, schnelle Website für Handy und Computer (Mobile first). Sie zeigt dieselben Auswertungen wie das Dashboard.
- **Das Dashboard ist der Datenlieferant (F6).** Die Website rechnet nichts Eigenes. Sie verwendet dieselben Funktionen wie das Dashboard: `core/anzeige.py` (welche Spiele wann erscheinen), `core/kpis.py` (Werte und Stufen), `core/top.py` (Ranking).
- **Umfang jetzt:** Startseite, Spieltag, Matchdetail. Methodik, Impressum, Datenschutz und Showcase folgen später.
- Bis zum Livegang nur als **Vorschau** unter `https://soccer-intelligence.com/vorschau`, mit Passwortabfrage (T3). Die Platzhalterseite unter `/` bleibt, bis Impressum und Datenschutz fertig und rechtlich geprüft sind.

## 2. Entscheidungen (Carsten, 16.11.2026)

| Nr. | Entscheidung |
|---|---|
| T1 | Kein Streamlit. Statische, schnelle Seiten (Mobile first, Ladezeit wichtig) |
| T2 | Seiten neu erzeugen nach jeder Übernahme und alle 15 Minuten. Angepfiffene und beendete Spiele bleiben auf der Spieltag-Seite sichtbar, bis der Spieltag zu Ende ist (in der Regel Sonntag auf Montag); Ergebnisse kommen mit der Übernahme dazu |
| T3 | Vorschau mit Passwortschutz |
| T4 | Umsetzung genau nach Designvorgabe. Schriften Outfit und Inter, **selbst gehostet** (schneller, kein Datenschutz-Thema mit Google) |
| T5 | Die Website schreibt mit **ß** („Fußball“, „weißt“). Das Dashboard bleibt bei ss (CLAUDE.md) |
| F1 | KPI 03 „Über 2,5 Tore“ mit der Abweichung wie im Rechenkern. Text und Vergleichswert seit 0.18 nach Q2 (2,5-Tore-Marke statt Ligaschnitt) |
| F2 | „Nicht gewertet“ = „vorläufig“ nach Regelwerk (weniger als 10 Spiele, z. B. Aufsteiger) |
| F3 | Keine Sonderbehandlung „Werte ab“ auf der Spieltag-Seite: Es stehen die Werte, die gerade berechenbar sind |
| F4 | Nachhol- und vorgezogene Spiele wie im Entwurf: im Spieltag, in dessen Zeitraum sie fallen, sonst im ersten; mit Chip |
| F5 | Verschobene, abgesagte, abgebrochene, ausgesetzte und gewertete Spiele als graue Status-Kachel wie im Entwurf |
| F6 | Ranking der Startseite = Top Anomalien des Dashboards (Regelwerk 2.6) |
| F7 | Pausen und Datenstand wie im Dashboard (Pause über 14 Tage, Spieltag ab 14 Tagen vorher, Warnung bei Datenstand über 3 Tage) |
| F8 | Adressen `/spieltag/<liga>`, Standard Bundesliga; nur der anstehende Spieltag (bei englischer Woche Tabs), kein Blättern; gespielte Spiele verlinken zum Matchdetail, verschobene nicht. Liganame „La Liga“ mit Abstand |
| D1 | **„Aktueller Datenstand“** (Startseite, Spieltag) und **„Stand“** (Fusszeile) = Datum bzw. Datum und Uhrzeit des **letzten erfolgreichen Importlaufs** über die API |
| Z1 | **Zeitreise** nur in der Vorschau: `?datum=…` auf jeder Seite (Abschnitt 6) |

**Entscheidungen Carsten vom 17.11.2026 (Fragerunde vor 0.18, alle Empfehlungen angenommen):**

| Nr. | Entscheidung |
|---|---|
| Q1 | Matchdetail, „Zahlen im Detail“: Erwartungswert = Hauptwert der Kennzahl. Die zweiteilige Leiste „Heim + Gast“ nur bei **Gelben Karten** (Summe der Teamwerte); alle anderen Kennzahlen zeigen „Je Mannschaft · Mittelwert beider Teams“ |
| Q2 | KPI 03 „Über 2,5 Tore“: Vergleichswert ist die **Marke 2,5** (nicht der Ligaschnitt), Erwartungswert in Toren; Texte „Mehr als 2,5 Tore erwartet“ / „Weniger als 2,5 Tore erwartet“ |
| Q3 | Die Website verwendet die kurzen Texte des Entwurfs (Übergabe 4.4), nicht die Texte des Dashboards |
| Q4 | Eine einzelne vorläufige Kennzahl erscheint ohne Stufe, schraffiert, unter „Im Normalbereich“ mit dem Vermerk „nicht gewertet“. Das ganze Spiel ist nur dann „nicht gewertet“, wenn alle Kennzahlen vorläufig sind (F2) |
| Q5 | Gespieltes Spiel: „Endstand 2 : 1“ bzw. „Ergebnis folgt“ statt des Anstosses, dazu der Hinweis „Die Werte wurden vor dem Spiel berechnet.“ |
| Q6 | Foto der Startseite: nur auf dem Server (`/docker/football-dashboard/website-bilder/portrait.jpg`), nie in Git; fehlt es, steht ein neutraler Platzhalter |
| Q7 | Startseite in einer Pause: Tage-Zähler bis zum nächsten Spieltag bzw. Saisonstart |

## 3. Technik

| Teil | Umsetzung |
|---|---|
| Programmteil | `app/website/` im bestehenden Projekt (gleiche Datenbank, gleicher Rechenkern) |
| Seiten | HTML-Vorlagen (Jinja2, gemeinsame Bausteine in `vorlagen/teile.html`) + eine CSS-Datei mit den Farben und Massen der Entwürfe; wenig JavaScript (`statisch/site.js`: Tabs der englischen Woche, „Zuklappen“ im Matchdetail), alles funktioniert auch ohne. Keine Inline-Stile (Content-Security-Policy), Balkenbreiten über Klassen `.w0`–`.w100`. Seit 0.19.1 hängt an CSS und JS eine Versionsnummer (`?v=` + Prüfsumme des Inhalts): Nach einem Release lädt der Browser geänderte Dateien neu, ohne Strg+F5 |
| Texte | Sprachdatei `app/website/texte/de.json` mit Schlüsseln (Übergabe 9.1); Mehrzahl als eigene Varianten; Fallback Deutsch |
| Formate | `app/website/format.py`: Datum „Sa 21.11.“, Prozent „+47,36 %“ mit echtem Minus „−“, Ergebnis „2 : 1“; je Sprache eine Tabelle (jetzt nur `de`) |
| Schriften | Outfit und Inter als variable WOFF2-Dateien (SIL Open Font License 1.1, Lizenzdateien liegen bei), nur lateinische Zeichen; erweiterte Zeichen lädt der Browser nur bei Bedarf |
| Daten | `app/website/daten.py` lädt Datenbank, Spielplan, Schwellen und den Importstand, mit Zwischenspeicher je Dateistand |
| Datenschnittstelle | Je Seite ein Datensatz mit **Codes statt Texten** (Abschnitt 5), als JSON abrufbar (`/vorschau/daten/…`). Daraus entsteht beim Livegang der statische Export |
| Vorschau | Container `soccer-vorschau` (gleiches Programm-Abbild wie das Dashboard), kleiner Python-Webserver, erzeugt die Seiten bei jedem Aufruf neu (nötig für die Zeitreise). Nur lesend auf `data/`, `import/` und (seit 0.18) `website-bilder/` (Foto, Q6). Beim Start rechnet er Startseite und Spieltage einmal vor, damit schon der erste Aufruf schnell ist |
| Zugang | Traefik-Router `Host(soccer-intelligence.com) && PathPrefix(/vorschau)` mit Passwortabfrage (BasicAuth, Hash in `.env` als `SOCCER_VORSCHAU_AUTH`), Anfragebremse, „noindex“ |
| Livegang (später) | statischer Export nach `site/`, ausgeliefert von nginx (wie der Platzhalter); Erzeugen im Container `soccer-import` nach jeder Übernahme und alle 15 Minuten |

## 4. Seiten und Adressen

| Adresse (Vorschau) | Seite | Version |
|---|---|---|
| `/vorschau/` | Startseite (in 0.17 Weiterleitung auf den Spieltag) | 0.18 |
| `/vorschau/spieltag` | Weiterleitung auf `/vorschau/spieltag/bundesliga` (F8) | 0.18 |
| `/vorschau/spieltag/<liga>` | Spieltag; `<liga>` = `bundesliga`, `la-liga`, `premier-league`, `serie-a` | 0.17 |
| `/vorschau/spiel/<id>` | Matchdetail, **eine Seite je Paarung** des Spielplans (laufende Saison und Vorsaison); `<id>` = Spiel-ID von API-Football; unbekannte ID: Seite „nicht gefunden“ (404) | 0.18 |
| `/vorschau/bilder/portrait.jpg` | Foto der Startseite aus `website-bilder/` (Q6); fehlt es: 404, die Startseite zeigt den Platzhalter | 0.18 |
| `/vorschau/methodik`, `/impressum`, `/datenschutz` | Hinweis „folgt später“ | später |
| `/vorschau/daten/start.json`, `/daten/spieltag/<liga>.json`, `/daten/spiel/<id>.json` | Datensätze der Seiten (Codes) | 0.17/0.18 |

Reihenfolge der Ligen auf der Website (Entwurf): Bundesliga, La Liga, Premier League, Serie A.

### 4.1 Adressschema ab 0.20 (Entscheidung Carsten 19.11.2026)

**Spiel-ID** = Fixture-ID von API-Football (z. B. `1550203`): bleibt bei Verschiebungen gleich und ist über alle Ligen und
Saisons eindeutig; Spiele des Altbestands (2018/19–2025/26) haben sie über `app/config/zuordnung_api.csv`. Bei einem
späteren Anbieterwechsel bleibt diese Nummer unsere feste ID (Zuordnung neuer Nummern).

| Adresse | Seite |
|---|---|
| `/de/` | Startseite |
| `/de/spieltag/<liga>/` | Spieltag (kommende Spiele) |
| `/de/spieltag/<liga>/<saison>/<nr>/` | Archivseite je Spieltag, `<saison>` z. B. `2025-26` |
| `/de/spiel/<liga>/<heim>-<gast>-<id>/` | Matchdetail, z. B. `/de/spiel/bundesliga/vfb-stuttgart-bayern-muenchen-1550203/` |
| `/de/methodik/`, `/de/glossar/`, `/de/impressum/`, `/de/datenschutz/`, `/de/kontakt/` | Inhaltsseiten |

Regeln:
- **Eindeutig ist nur die ID am Ende.** Liga und Teamnamen dienen der Lesbarkeit; Namen = **API-Namen** wie angezeigt
  (keine eigene Namensliste; Spielseiten sind kein SEO-Ziel).
- **Namen in Adressen:** Kleinschreibung, ä → ae, ö → oe, ü → ue, ß → ss, übrige Akzente entfernt (Atlético → atletico),
  alles andere als ein Zeichen ausser a–z und 0–9 → Bindestrich, keine doppelten Bindestriche.
- **Liga-Teil:** `bundesliga`, `premier-league`, `serie-a`, `la-liga`.
- **Weicht eine Adresse mit gültiger ID ab** (andere Liga, alter Vereinsname, fehlender Schrägstrich am Ende,
  Grossbuchstaben): dauerhafte Weiterleitung **301** auf die richtige Adresse. Unbekannte ID: 404.
- Jede Seite trägt ein `canonical`-Tag mit ihrer richtigen Adresse.
- **`/de/` gilt ab dem Livegang für alle Seiten**; `/` leitet auf `/de/` weiter. Alte Adressen der Vorschau
  (`/spiel/<id>`, `/spieltag/<liga>`) leiten dauerhaft auf die neuen weiter.
- Ein Vereinsname ändert sich → neue lesbare Adresse, alte leitet per 301 weiter; die ID bleibt.

**Englisch zum Livegang (Entscheidung Carsten 19.11.2026):** Die Website erscheint deutsch und englisch.

| Deutsch | Englisch |
|---|---|
| `/de/` | `/en/` |
| `/de/spieltag/<liga>/` | `/en/matchday/<liga>/` |
| `/de/spieltag/<liga>/<saison>/<nr>/` | `/en/matchday/<liga>/<saison>/<nr>/` |
| `/de/spiel/<liga>/<slug>-<id>/` | `/en/match/<liga>/<slug>-<id>/` |
| `/de/methodik/` | `/en/methodology/` |
| `/de/glossar/` | `/en/glossary/` |
| `/de/impressum/` | `/en/legal-notice/` |
| `/de/datenschutz/` | `/en/privacy-policy/` |
| `/de/kontakt/` | `/en/contact/` |
| `/de/cookie-einstellungen/` | `/en/cookie-settings/` |

- **Slug in beiden Sprachen gleich** (aus den API-Namen, z. B. `vfb-stuttgart-bayern-muenchen-1550203`); nur die
  Pfadwörter werden übersetzt. So ergibt sich die Adresse der anderen Sprache mit einer Regel.
- **Liga-Teil in beiden Sprachen gleich:** `bundesliga`, `premier-league`, `serie-a`, `la-liga`.
- Jede Seite verweist mit `hreflang` (de, en, x-default = de) auf beide Fassungen; Sprachwechsel führt auf dieselbe Seite.
- **Ohne Liga:** `/de/spieltag/` bzw. `/en/matchday/` leiten auf die Standardliga weiter (Bundesliga, F8; 302, weil
  die Standardliga sich ändern kann).
- **Sonderzeichen in Namen:** Apostrophe werden ersatzlos entfernt; „&“, Punkte, Leerzeichen und alle übrigen Zeichen
  ausser a–z und 0–9 werden zu einem Bindestrich; keine doppelten Bindestriche, keine am Anfang oder Ende.
  Beispiele: „1. FC Köln“ → `1-fc-koeln`, „Brighton & Hove Albion“ → `brighton-hove-albion`, „Atlético Madrid“ →
  `atletico-madrid`.
- **Cookie-Einstellungen:** `noindex`, nicht in der Sitemap.
- **404 je Sprachverzeichnis:** unbekannte Adresse unter `/de/` → deutsche Seite „nicht gefunden“, unter `/en/` → englische; sonst deutsch.
- **Neue Mannschaft:** Der Slug entsteht immer automatisch aus dem API-Namen. Fehlt im Namenverzeichnis ein deutscher oder englischer Anzeigename, zeigt die Seite bis dahin den API-Namen und meldet das intern (Datenimport/API); die Veröffentlichung wird nicht blockiert. Ein späterer Anzeigename ändert den Slug nicht.
- **Wiederholungsspiel mit neuer ID:** eigene Seite; die alte Seite bleibt erreichbar und wird nie gelöscht (mit ihrem Status, z. B. „Abgebrochen“).
- **Fehlende Übersetzung:** kommt nicht vor, solange alle Seiten in beiden Sprachen existieren. Falls künftig (z. B. dritte Sprache): kein `hreflang`-Eintrag für diese Seite, der Sprachwechsel führt auf die Startseite der Zielsprache. Fehlt nur ein einzelner Text, gilt der deutsche (Fallback der Sprachdatei).
- **Texte:** alle Website-Texte zusätzlich englisch (`texte/en.json`), Inhalte (Methodik, Glossar, rechtliche Seiten)
  aus dem finalen Content in beiden Sprachen; Teamnamen bleiben die API-Namen.



## 5. Seite Spieltag (Übergabe, Abschnitt 6)

### 5.1 Aufbau (seit 0.18 nach Entwurf 3d)
1. Kopf: Logo „Soccer Intelligence“, Navigation Spieltag · Methodik · Impressum.
2. Dunkler Kopfbereich: H1 „Alle Spiele im **Überblick**“ (Akzent), Text „Wähle deine Liga und sieh, bei welchen Partien die Zahlen aus der Reihe fallen.“, darunter die Liga-Auswahl: vier Kacheln mit „10. Spieltag“ bzw. Pausenname (A5); die gewählte in der Akzentfarbe. Darunter „Aktueller Datenstand: Mo 16.11.2026“ (D1).
3. Titel = Liganame, Zusammenfassung „10. Spieltag · 20.11. – 22.11.2026 · 9 Partien · 2 mit Auffälligkeit · plus 1 Nachholspiel“ (je Tab eine eigene Zeile).
4. Bei englischer Woche Tabs „10. Spieltag · ab 20.11.“ / „11. Spieltag · ab 24.11.“ (Standard: der frühere; ohne JavaScript stehen beide untereinander).
5. Legende Stark · Leicht · Ohne Auffälligkeit, „Wie lese ich das?“ (aufklappbar, Texte Übergabe 6.3).
6. Ohne jede Abweichung der Hinweis „Bei diesem Spieltag weicht kein Wert deutlich vom Ligaschnitt ab.“
7. Partien als Kacheln im Raster (Computer zwei Spalten, Handy eine), Fusszeile.

### 5.2 Welche Spiele (gleiche Regeln wie Dashboard, `07`, Abschnitt 4)
- Tabs = die Spieltage, die das Dashboard ohne Auswahl als Abschnitte zeigt (anstehender Spieltag, weitere Spieltage, die heute bis heute + 6 beginnen).
- Je Tab: alle Spiele des Spieltags (auch gespielte und solche mit Status, F5), dazu Nachhol- und vorgezogene Spiele der nächsten 7 Tage, die in den Zeitraum des Tabs fallen (sonst im ersten Tab, F4).
- Pausen (F7): Ist kein Spieltag in höchstens 14 Tagen, ersetzt eine Pausen-Karte die Liste (Spielpause, Winterpause, Sommerpause, Saisonstart). Datenstand über 3 Tage: gelbe Warnbox, Liste bleibt.

### 5.3 Einstufung je Partie (Codes in Klammern)
Reihenfolge der Prüfung: **Status > gespielt > nicht gewertet > Stufe** (Übergabe 6.4, letzter Absatz).

| Art | Wann |
|---|---|
| Status (`status`) | Spielplan-Status verschoben, abgesagt, abgebrochen, ausgesetzt, gewertet |
| Gespielt (`gespielt`) | Ergebnis in der Datenbank, oder Anstoss vorbei (dann „Ergebnis folgt“) |
| Nicht gewertet (`nicht_gewertet`) | alle 8 Kennzahlen vorläufig (F2) oder keine Werte |
| Hoch / Mittel / Gering (`hoch`, `mittel`, `gering`, seit 0.19) | mindestens eine nicht vorläufige Kennzahl ist auffällig; Art = höchster Prognosewert (Regelwerk 2.2). Bis 0.18: Stark (`stark`) / Leicht (`leicht`) |
| Ohne Auffälligkeit (`ohne`) | sonst |

Stufen kommen aus `schwellen.toml` über den Rechenkern (Übergabe 4.1, keine festen 20/35). Vorläufige Kennzahlen zählen für die Stufe nicht.

### 5.4 Sortierung und Zählung
- Seit 0.18 wie im Entwurf 3d (Skript `renderVals`): Stark (nach grösster Abweichung) → Leicht (nach grösster Abweichung) → Ohne Auffälligkeit → alle übrigen (Nicht gewertet, Status, Gespielt) als **eine** Gruppe nach Anstoss.
- Nachhol- und vorgezogene Spiele werden mitsortiert (wie im Entwurf); in 0.17 standen sie als Gruppe am Ende (Annahme A2, ersetzt).
- „Partien“ = Spiele des Spieltags ohne Sonderspiele; „mit Auffälligkeit“ = Stark + Leicht, Sonderspiele eingeschlossen; „plus n Nachholspiel(e)“ bzw. „plus n vorgezogene(s) Spiel(e)“.

### 5.5 Kachel
Heim, „gegen“, Gast, Termin („Sa 14.11. · 15:30“, „Sa 14.11. · Zeit offen“, „Wochenende 06./07.02. · Termin offen“, bei Status „Termin offen“ bzw. Datum), bei gespielten Spielen das Ergebnis. Chips (Stufe, Nachholspiel/vorgezogen, Status, Ergebnis folgt), runder Pfeil zur Seite des Spiels. Farben, Ränder und Masse nach Entwurf 3d. Verschobene und abgesagte Spiele sind nicht verlinkt (F8).

### 5.6 Datensatz (Codes, Auszug)
```json
{"seite": "spieltag", "liga": "bundesliga", "jetzt": "2026-11-16T14:00", "stand": "2026-11-16T04:05", "veraltet": false,
 "zustand": "liste", "pause": null,
 "ligen": [{"liga": "bundesliga", "spieltag": 10, "pause": null}],
 "tabs": [{"saison": "2026/2027", "spieltag": 10, "von": "2026-11-20", "bis": "2026-11-22", "partien": 9,
           "auffaellig": 2, "sonderspiele": {"nachholspiel": 1, "vorgezogen": 0},
           "spiele": [{"id": 1388512, "heim": "Bayern München", "gast": "1. FC Köln", "datum": "2026-11-20",
                       "anstoss": "20:30", "termin": "bestaetigt", "art": "hoch", "status": null,
                       "ergebnis": null, "sonderspiel": null, "link": true,
                       "staerkste": {"kpi": "kpi03", "abweichung": 44.0}}]}]}
```

## 6. Zeitreise (nur Vorschau)

- `?datum=2026-10-03` oder `?datum=2026-10-03T16:00` auf jeder Seite der Vorschau; ohne Uhrzeit gilt 08:00. Alle Links tragen das Datum weiter. Eine Leiste oben zeigt den Zeitpunkt und erlaubt die Eingabe.
- Annahmen (Carsten, 16.11.2026): Der Import ist an diesem Tag um 04:00 gelaufen (kein „veraltet“, Datenstand = dieser Tag, vor 04:00 der Vortag). Ergebnisse gelten nur für Spiele **vor** dem Importtag; die KPI-Werte werden mit genau diesem Datenstand berechnet.
- Grenzen: Spielplan = der heutige (spätere Verschiebungen sind schon eingetragen). Zeitraum = laufende Saison und Vorsaison.
- Auf der öffentlichen Seite gibt es keine Zeitreise.

## 7. Matchdetail und Startseite (seit 0.18)

**Seit 0.19 (Prognosewert, Regelwerk 2.2):** Website-Daten tragen statt „stark/leicht“ den Prognosewert `hoch`/`mittel`/`gering` (Kacheln, Karten, Ranking, Chips „Prognosewert hoch“ usw.). Gestaltung bis zum Designentwurf der Website unverändert: hoch wie bisher „stark“ (dunkel), mittel und gering wie bisher „leicht“ (hell). Neuer Entwurf und Release B folgen.

### 7.1 Matchdetail (Entwurf 2i, ergänzend 2c; Übergabe Abschnitt 7)
**Jede Paarung des Spielplans hat eine eigene Seite** unter `/spiel/<Spiel-ID von API-Football>` – auch gespielte, Nachhol- und vorgezogene Spiele. Verlinkt sind sie von der Spieltag-Seite und vom Ranking der Startseite. Verschobene und abgesagte Spiele haben ebenfalls eine Seite (über die Adresse erreichbar), werden aber nicht verlinkt (F8). Programm: `app/website/spiel.py` (Datensatz), `vorlagen/spiel.html`.

1. Kopf rechts „Zurück zum Spieltag“ (statt Navigation).
2. Scoreboard: Liga · Spieltag, Termin (bzw. „Endstand 2 : 1“ / „Ergebnis folgt“, Q5) mit Chips Nachholspiel/vorgezogen/Status, beide Teams mit Formkurve „Letzte 5 Spiele“ (S/U/N, „–“ = noch kein Spiel, KPI 01) und Legende.
3. Kernaussage: grösste Auffälligkeit („+44,00 % · Über 2,5 Tore · Mehr als 2,5 Tore erwartet“); ohne Auffälligkeit „Keine statistischen Auffälligkeiten – Alle 8 Kennzahlen liegen im Normalbereich. Die größte Abweichung: …“; nicht gewertet „Nicht gewertet“; Status „Für dieses Spiel gibt es keine Werte.“
4. Hinweise: Nachholspiel („… wird am So 22.11. um 17:30 Uhr nachgeholt“), vorgezogen, gespielt („Die Werte wurden vor dem Spiel berechnet.“, Q5).
5. „Auffälligkeiten“: Karten je Kennzahl mit Stufe, nach Betrag der Abweichung sortiert; Balken (Länge = Betrag/2 % der Breite, höchstens 50 %, über 100 % gekappt mit Streifen, Übergabe 4.2); aufklappbar „Zahlen im Detail“: Erwartungswert, „Je Mannschaft · Mittelwert beider Teams“ (bei Gelben Karten „Heim + Gast“ mit zweiteiliger Leiste, Q1), Ligaschnitt bzw. „Vergleichswert (Marke)“ 2,50 bei KPI 03 (Q2), Abweichung mit Stufe, „Zuklappen“.
6. „Im Normalbereich“: übrige Kennzahlen als aufklappbare Zeilen, nach Betrag; eine einzelne vorläufige Kennzahl dort schraffiert mit „· nicht gewertet“ (Q4). Ist das ganze Spiel nicht gewertet: Hinweisbox und Überschrift „Kennzahlen“ (ohne Werte: eigener Text „Für dieses Spiel liegen noch keine Werte vor …“).
7. Status-Spiele (verschoben, abgesagt …): nur Scoreboard und Kernaussage, keine Kennzahlen (wie die graue Kachel, F5).
8. Link „Wie entstehen diese Werte?“ (Methodik, folgt) und „Alle Spiele des Spieltags“.

Werte unverändert aus dem Rechenkern (F6): Erwartungswert = `hauptwert`, Teamwerte = `heim`/`auswaerts`, Ligaschnitt = `referenz`, Abweichung = `abweichung` (gerundet), Stufe aus `schwellen.toml`; KPI 08 in Prozent.

### 7.2 Startseite (Entwurf 1d, ergänzend 1b; Übergabe Abschnitt 5)
Programm: `app/website/start.py` (Datensatz), `vorlagen/start.html`.

1. Kopfbereich „Fußballspiele **durchleuchtet.**“ mit Knöpfen „Auffällige Spiele“ und „So funktioniert’s“.
2. **„Die auffälligsten Spiele“** = genau die Top Anomalien des Dashboards (F6): je Liga der zeitlich nächste Block (`core/anzeige.top_block`), nur Spiele vor dem Anpfiff und mit Werten (`values_gate`), Auswahl und Rangfolge nach Regelwerk 2.6 (`core/top.select_top`, seit 0.19: Prognosewert hoch vor mittel vor gering, dann grösster Betrag, früheres Datum, Ligareihenfolge; Liga-Mix höchstens 2 je Liga; höchstens 4, einer je Spiel; vorläufige Werte und verschobene Spiele nie). Je Zeile: Rang, „Bundesliga · Spieltag 10“, Paarung, Termin, Pfeil, Abweichung, Stufe, Kennzahl, Balken; Link zum Matchdetail.
3. Zustände statt der Liste (Pausenkarte): **Keine Abweichungen** (eine Liga spielt, aber ohne Auffälligkeit) · **Spielpause** / **Winterpause** (keine Liga in den nächsten 14 Tagen; Winterpause, wenn Weihnachten in der Lücke liegt) · **Saisonstart** (alle nächsten Spieltage gehören zu einer neuen Saison) · **Sommerpause** („Die Saison ist beendet“, kein angesetztes Spiel) · **Nächster Spieltag** ohne Pausennamen bei veraltetem Datenstand (S9). Massgebend ist der früheste nächste Spieltag aller Ligen; der Knopf führt zu dessen Liga. Tage-Zähler (Q7) bei Spiel-, Winterpause, Saisonstart und veraltetem Stand. Fehler in den Daten: Hinweis „Daten werden geprüft“.
4. Warnbox bei veraltetem Datenstand (über 3 Tage, F7); „Aktueller Datenstand: …“ (D1).
5. „Deine Liga. Dein Spieltag.“ (vier Liga-Knöpfe), „So funktioniert’s“ (drei Spalten), Band „Bereit für den Spieltag?“, Block „Von einem Fußballfan gebaut“ mit Foto (Q6) oder Platzhalter, SEO-Text „Was ist Soccer Intelligence?“.

**Foto (Q6):** Datei `portrait.jpg` im Ordner `/docker/football-dashboard/website-bilder/` auf dem Server (quadratisch, mindestens 230 × 230 Pixel, JPEG). Der Ordner ist nur lesend im Container `soccer-vorschau` eingebunden (`/bilder`), steht in `.gitignore` und kommt nie ins Programm-Abbild (Dockerfile kopiert nur `app/`). Ein neues Foto wirkt sofort (kein Neustart nötig; Browser-Zwischenspeicher bis 1 Stunde).

## 8. Testfälle (seit Version 0.17, `tests/test_website.py`)

| Nr. | Situation | Erwartet |
|---|---|---|
| W1 | Formate | „Sa 21.11.“, „+47,36 %“, „−22,07 %“ (U+2212), „0,00 %“ ohne Vorzeichen, „2 : 1“, Zeitraum über den Jahreswechsel |
| W2 | Einstufung | Status vor gespielt vor nicht gewertet vor Stufe; vorläufige Kennzahlen zählen nicht; seit 0.19 Prognosewert hoch vor mittel vor gering |
| W3 | Sortierung | seit 0.18: Stark → Leicht → Ohne → übrige (Nicht gewertet, Status, Gespielt) nach Anstoss; innerhalb Stark/Leicht nach Betrag; Sonderspiele mitsortiert |
| W4 | Zählung | Partien ohne Sonderspiele; „mit Auffälligkeit“ mit Sonderspielen; „keine mit Auffälligkeit“ |
| W5 | Nachholspiel | im Tab, in dessen Zeitraum es fällt, sonst im ersten; mitsortiert (seit 0.18); Chip |
| W6 | Englische Woche | zwei Tabs mit eigener Zählung; Standard der frühere |
| W7 | Pausen | Spielpause, Winterpause, Sommerpause, Saisonstart als Karte statt Liste; ab 14 Tagen Liste |
| W8 | Datenstand | Warnbox ab 4 Tagen, Liste bleibt; Datum = letzter erfolgreicher Lauf |
| W9 | Zeitreise | Datum aus der Adresse, Ergebnisse und Werte nur vor dem Importtag, Links tragen das Datum |
| W10 | Texte | jeder Schlüssel der Vorlagen in `de.json`; ß-Schreibweise; alle Texte maskiert |
| W11 | Vorschau-Dienst | Adressen (Startseite, Matchdetail, JSON), Weiterleitung, 404, ungültiges Datum, Dateien nur aus dem eigenen Ordner, Kopfzeilen; Foto nur aus `website-bilder/`, sonst Platzhalter; Vorladen bricht nie ab |
| W12 | Container | Router nur unter `/vorschau`, mit Passwortabfrage, noindex, Anfragebremse; nur lesend |
| W13 | Echte Daten | alle vier Ligen an mehreren Tagen (wie A27) ohne Fehler; mit echten Dateien auch Startseite und Matchdetail jeder verlinkten Paarung |
| W14 | Matchdetail | Q1 (Summe nur Gelbe Karten, sonst Mittelwert), Q2 (Marke 2,50), Q4 (einzelne vorläufige Kennzahl unter Normalbereich), Q5 (Endstand, Ergebnis folgt, Hinweis), nicht gewertet mit/ohne Werte, Status ohne Kennzahlen, Nachholspiel-Hinweis, Formkurve, Balken und Zahlen; **jede Paarung eines Spieltags und der ganzen Saison hat eine eigene Seite** (echte Saisonlisten) |
| W15 | Startseite | Ranking wie Dashboard (Prognosewert, Betrag, Liga-Mix, höchstens 4, einer je Spiel, ohne vorläufige und verschobene, nur vor dem Anpfiff); Zustände Spielpause, Winterpause, Sommerpause, Saisonstart, unbekannt (veraltet), keine, gesperrt; Tage-Zähler |
| W16 | Sicherheit | keine Inline-Stile und -Skripte (Content-Security-Policy), jede Balkenbreite hat eine CSS-Klasse |

## 9. Annahmen (bitte in der Vorschau prüfen)

| Nr. | Annahme | Grund |
|---|---|---|
| A1 | ~~Spieltag-Kachel und Liste im Stil der Startseite~~ – **erledigt mit 0.18**: genau nach Entwurf 3d | Entwurf `Spieltag_P1` war in 0.17 nicht angekommen |
| A2 | ~~Nachhol- und vorgezogene Spiele als eigene Gruppe am Ende~~ – **ersetzt mit 0.18**: mitsortiert wie im Entwurf 3d (Abschnitt 5.4) | Entwurf 3d sortiert alle Spiele gemeinsam |
| A3 | Status „gewertet“ (am grünen Tisch) bekommt den Chip „Am grünen Tisch gewertet“, damit er nicht mit „Nicht gewertet“ verwechselt wird | Begriffe sonst gleich |
| A4 | „Ergebnis folgt“ als Chip, solange das Ergebnis nach dem Anstoss noch nicht übernommen ist | Übergabe nennt nur „Ergebnis“ |
| A5 | Liga-Kachel zeigt in einer Pause den Pausennamen statt der Spieltagsnummer | Übergabe nennt nur „24. Spieltag“ |
| A6 | Bei veraltetem Datenstand ohne anstehenden Spieltag: Warnbox und Karte „Nächster Spieltag am …“ ohne Pausennamen | S9: keine Pausenhinweise bei veraltetem Stand |
| A7 | Die Pausen-Karte der Spieltag-Seite hat keinen Tage-Zähler (nur die Startseite, Q7) | Übergabe 6.4; Entwurf 3d bestätigt |
| A8 | Navigation zu Methodik und Impressum zeigt bis zur Umsetzung „Diese Seite folgt später.“ | Seiten noch nicht im Umfang |
| A9 | Vorschau-Leiste oben (Zeitpunkt, Eingabe) nur in der Vorschau, nicht Teil der Website | wie die Prototyp-Leiste des Entwurfs |

## 10. Offene Punkte

- **Für 0.20 beschlossen (Carsten 19.11.2026): Englisch zum Livegang** mit gleichem Slug in beiden Sprachen, übersetzten Pfadwörtern, `hreflang` und Regeln für Sonderzeichen (Abschnitt 4.1).
- **Für 0.20 beschlossen (Carsten 19.11.2026): Adressschema** nach Abschnitt 4.1 (ID am Ende, API-Namen, 301-Weiterleitungen, `/de/` für alle Seiten ab dem Livegang).
- **Für 0.20 beschlossen (Carsten 19.11.2026): kein Live-Status.** Ab dem Anpfiff gilt ein Spiel als gespielt: ausgegraut, markiert mit „Gespielt“, sobald importiert mit dem Endstand. Es bleibt an seinem Platz in den Top Anomalien (Startseite) und auf der Spieltag-Seite, bis der Spieltag endet; die Werte vor dem Spiel (Schnappschuss) bleiben sichtbar. Der Chip „Ergebnis folgt“ und der Glossar-Begriff entfallen, auch auf der Spielseite (`07`, 4.7). Präzisierung (Carsten 19.11.2026): **bis Anpfiff + 2 Stunden** normal ohne Beschriftung (während des Spiels nichts), **ab Anpfiff + 2 Stunden** ausgegraut mit „Gespielt“, **ab Import des Endstands** ausgegraut mit Endstand. Sichtbarkeit: reguläre Spiele bis zum Ende ihres Spieltags (Abend des letzten regulären Spiels), Sonderspiele bis zu ihrem eigenen Tagesende, Top Anomalien bis zum Ende des Blocks (4.2, 4.7).
- **Für 0.20 beschlossen (Carsten 19.11.2026): Datenstand 48 Stunden.** Daten bis 48 Stunden alt sind normal, die Website schlägt keinen Alarm. Erst wenn der letzte erfolgreiche Import mehr als 48 Stunden zurückliegt, erscheint der Hinweis „Spielplan zuletzt aktualisiert am …“ (bisher ab mehr als 3 Tagen; `07`, 4.3, S9). Intern meldet der E-Mail-Alarm (0.21) schon den ersten Ausfall.
- **Für 0.20 beschlossen (Carsten 19.11.2026): fehlender Schnappschuss.** Der Schnappschuss läuft stündlich als eigener Schritt (unabhängig von API und Freigabe) mit den Daten, die die Website gerade zeigt, für alle Spiele mit Anpfiff in der nächsten Stunde. Fehlt er trotzdem (Container-Ausfall), wird er beim nächsten Lauf aus den Daten vor dem Spiel nachträglich erstellt, gekennzeichnet („Werte nachträglich mit den Daten vor dem Spiel berechnet“) und in einer späteren Bilanz gesondert ausweisbar; Meldung im Reiter Datenimport/API, ab 0.21 per E-Mail.
- **Für 0.20 beschlossen (Carsten 19.11.2026): Werte eines Spiels einfrieren.** Bisher werden Kennzahlen und Einstufung bei jedem Laden neu berechnet. Die Regeln (Stichtag = Termin des Spiels, nur Daten davor) liefern dieselben Zahlen wie vor dem Spiel, ausser bei Korrekturen früherer Spiele, neuen Schwellen (einmal pro Saison) oder Regeländerungen. Neu: **Schnappschuss je Spiel** (Werte, Einstufung, Signalqualität, Stand der Schwellendatei), angelegt am Spieltag vor dem Anpfiff durch den Import-Container und danach nie mehr verändert; gespielte Spiele zeigen den Schnappschuss. Satz auf der Spielseite präzisiert: „Die Werte wurden mit den Daten vor dem Spiel berechnet.“
- **Für 0.20 beschlossen (Carsten 19.11.2026): Korrekturen.** Bei einer nachträglichen Änderung des **Ergebnisses** (Import, Korrekturfenster oder späte Korrektur) zeigt die Spielseite beim Endstand den Hinweis „Ergebnis nachträglich korrigiert“; bei Statistik-Korrekturen kein Hinweis. Der Schnappschuss eines Spiels wird **nie** geändert, auch nicht bei späteren Korrekturen früherer Spiele: Er zeigt, was vor dem Spiel bekannt war.
- **Später (Wunsch Carsten 19.11.2026): Rückblick für Fans.** Besucher sollen vergangene Spiele und deren Signale ansehen können (auf Basis der Schnappschüsse und Archivseiten), z. B. mit Bilanz „Was hat sich bestätigt?“.
- **Für 0.20 beschlossen (Carsten 19.11.2026): Links auf alte Spieltage.** „Zurück zum Spieltag“ und „Alle Spiele des Spieltags“ führen heute auf `/spieltag/<liga>`, also auf den **aktuellen** Spieltag, nicht auf den Spieltag des Spiels. Umsetzung: Archivseite je Spieltag (`/spieltag/<liga>/<saison>/<nr>`) mit allen Spielen, Ergebnissen und Schnappschüssen; „Zurück zum Spieltag“, „Alle Spiele des Spieltags“ und „Weitere Spiele dieses Spieltags“ zeigen bei gespielten Spielen dorthin, bei kommenden wie bisher auf den aktuellen Spieltag.
- **Für 0.20 beschlossen (Carsten 19.11.2026):** Fehlen für ein Spiel die Daten für eine Bewertung (zu wenig Spiele, z. B. Aufsteiger, oder technische Lücke), lautet der Text neutral **„Für dieses Spiel liegen nicht genug Daten für eine Bewertung vor.“** statt „Die statistische Datengrundlage ist zu schwach.“ Der Begriff „Nicht gewertet“ wird dabei durch einen eindeutigen Begriff ersetzt (Vorschlag „Zu wenig Daten“; Wortlaut mit dem finalen Content). Hero bei keiner Auffälligkeit mit dynamischer Zahl: „Keine der {n} Kennzahlen überschreitet ihre Schwelle.“ (n = gewertete Kennzahlen).
- Startseite: maximale Anzahl im Ranking (vorerst 4, wie Dashboard).
- Methodik-Seite mit den besprochenen Änderungen (Mehrwert = Trefferquote − Grundquote aller Spiele, Prozentpunkte statt Prozent).
- Methodik-Seite: eine oder zwei (Übergabe 10, Punkt 9).
- Livegang: Impressum, Datenschutz, rechtliche Prüfung „keine Wettberatung“, statischer Export und nginx, Weiterleitung `/` statt Platzhalter.
- Mehrsprachigkeit: Englisch zum Livegang (Abschnitt 4.1); IT und ES später.

## 11. Versionen

| Version | Inhalt |
|---|---|
| 0.17 | Grundgerüst (Design, Schriften, Texte, Formate, Daten, Vorschau-Container mit Passwort, Zeitreise) und Seite **Spieltag** |
| 0.18 | Alle drei Seiten **nach den Entwürfen**: Startseite (1d), Spieltag (3d), Matchdetail (2i) mit eigener Seite je Paarung; Entscheidungen Q1–Q7 |
| 0.19 | Prognosewert statt stark/leicht in den Daten und Texten (Gestaltung unverändert bis zum neuen Entwurf); Ranking mit Liga-Mix |
| 0.19.1 | CSS und JS mit Versionsnummer (`?v=`), damit nach einem Release kein Strg+F5 nötig ist |
| später | Methodik, Impressum, Datenschutz, Livegang |
