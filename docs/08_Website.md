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
| D1 | **„Aktueller Datenstand“** (Startseite bis 0.21.2; Spieltag bis 0.21.1) und **„Stand“** (Fusszeile) = Datum bzw. Datum und Uhrzeit des **letzten erfolgreichen Importlaufs** über die API |
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
| Seiten | HTML-Vorlagen (Jinja2, gemeinsame Bausteine in `vorlagen/teile.html`, Kachel in `kachel.html`, Methodik-Bausteine in `methodik_teile.html`, lange Texte je Sprache in `vorlagen/inhalt/<seite>.<sprache>.html`) + eine CSS-Datei mit den Farben und Massen der Entwürfe P1 (seit 0.21); wenig JavaScript (`statisch/site.js`: Tabs der englischen Woche und der Methodik-Tabellen, „Zuklappen“ auf der Spielseite, Sprachmenü schliesst mit Escape und Klick daneben), alles funktioniert auch ohne. Keine Inline-Stile (Content-Security-Policy), Balkenbreiten über Klassen `.w0`–`.w100`. Seit 0.19.1 hängt an CSS und JS eine Versionsnummer (`?v=` + Prüfsumme des Inhalts): Nach einem Release lädt der Browser geänderte Dateien neu, ohne Strg+F5 |
| Texte | Sprachdateien `app/website/texte/de.json` und (seit 0.21) `en.json` mit denselben Schlüsseln (Übergabe 9.1); Mehrzahl als eigene Varianten; Fallback Deutsch; ein Test prüft gleiche Schlüssel und Platzhalter in beiden Sprachen |
| Formate | `app/website/format.py`: Datum „Sa 21.11.“ / „Sat 21 Nov“, Prozent „+47,36 %“ / „+47.36%“ mit echtem Minus „−“, Ergebnis „2 : 1“ (Spielseite) bzw. „2:1“ (Chips), Zeitraum „20.11. – 22.11.2026“ / „20–22 Nov 2026“; je Sprache eine Tabelle |
| Adressen | `app/website/adressen.py` (seit 0.21): Pfadwörter je Sprache, Slugs, Erkennen einer Adresse mit 301/302/404 (Abschnitt 4.1) |
| Suchmaschinen | `app/website/seo.py` (Index-Regeln für Seite und Sitemap, Title, Description, JSON-LD), `sitemap.py` (robots.txt, Sitemap-Index mit Teilen je Liga und Saison), Konfiguration `app/config/website.toml` (`index_ab`, `seiten_ab_saison`) – Abschnitt 4.2 |
| Anzeigenamen | `app/website/namen.py` mit `app/config/teamnamen_anzeige.csv` (Liga; Name der Datenquelle; Deutsch; Englisch; Glossar Abschnitt 11). Fehlende Vereine zeigen den Namen der Datenquelle und stehen im Reiter Datenimport/API |
| Methodik | `app/website/methodik.py` (seit 0.21): Zahlen und Tabellen aus `schwellen.toml`, Excel-Download beim Aufruf erzeugt |
| Icons | `statisch/wurzel/`: `favicon.ico`, `favicon.svg`, `favicon-64.png`, `apple-touch-icon.png`, `og-image.png` (1200 × 630, sprachneutral), im Livebetrieb im Hauptverzeichnis der Domain |
| Schriften | Outfit und Inter als variable WOFF2-Dateien (SIL Open Font License 1.1, Lizenzdateien liegen bei), nur lateinische Zeichen; erweiterte Zeichen lädt der Browser nur bei Bedarf |
| Daten | `app/website/daten.py` lädt Datenbank, Spielplan, Schwellen und den Importstand, mit Zwischenspeicher je Dateistand |
| Datenschnittstelle | Je Seite ein Datensatz mit **Codes statt Texten** (Abschnitt 5), als JSON abrufbar (`/vorschau/daten/…`). Daraus entsteht beim Livegang der statische Export |
| Vorschau | Container `soccer-vorschau` (gleiches Programm-Abbild wie das Dashboard), kleiner Python-Webserver, erzeugt die Seiten bei jedem Aufruf neu (nötig für die Zeitreise). Nur lesend auf `data/`, `import/` und (seit 0.18) `website-bilder/` (Foto, Q6). Beim Start rechnet er Startseite und Spieltage einmal vor, damit schon der erste Aufruf schnell ist |
| Zugang | Traefik-Router `Host(soccer-intelligence.com) && PathPrefix(/vorschau)` mit Passwortabfrage (BasicAuth, Hash in `.env` als `SOCCER_VORSCHAU_AUTH`), Anfragebremse, „noindex“ |
| Livegang (1.0) | derselbe Dienst unter der Domain (Beschluss 19.11.2026: kein statischer Export; HTML bei jedem Aufruf, Browser-Zwischenspeicher 5 Minuten, Abschnitt 4.2) |

## 4. Seiten und Adressen

Seit 0.21 gelten die Adressen aus Abschnitt 4.1 in beiden Sprachen; in der Vorschau steht `/vorschau` davor
(z. B. `/vorschau/de/spieltag/bundesliga/`). Alte Vorschau-Adressen (`/vorschau/spieltag/<liga>`, `/vorschau/spiel/<id>`,
`/vorschau/impressum` …) leiten dauerhaft (301) auf die neuen weiter.

| Adresse (ohne `/vorschau`) | Seite | Version |
|---|---|---|
| `/` | 301 auf `/de/` | 0.21 |
| `/de/`, `/en/` | Startseite | 0.18 / 0.21 |
| `/de/spieltag/`, `/en/matchday/` | 302 auf die Standardliga (Bundesliga, F8) | 0.21 |
| `/de/spieltag/<liga>/`, `/en/matchday/<liga>/` | Spieltag | 0.17 / 0.21 |
| `/de/spieltag/<liga>/<2025-26>/<nr>/` | Archivseite je Spieltag (nur begonnene Spieltage, ab `seiten_ab_saison`) | 0.21 |
| `/de/spiel/<liga>/<heim>-<gast>-<id>/`, `/en/match/…` | Spielseite, **eine je Paarung**; unbekannte ID oder Saison vor `seiten_ab_saison`: 404; abweichender Slug, andere Liga, fehlender Schrägstrich: 301 | 0.18 / 0.21 |
| `/de/methodik/`, `/de/glossar/`, `/de/kontakt/`, `/de/impressum/`, `/de/datenschutz/` (englisch Abschnitt 4.1) | Inhaltsseiten (Abschnitt 7.3) | 0.21 |
| `/de/cookie-einstellungen/`, `/en/cookie-settings/` | Hinweis „folgt“ bis 0.22 | 0.21 |
| `/de/methodik/soccer-intelligence-schwellen.xlsx`, `/en/methodology/soccer-intelligence-thresholds.xlsx` | Excel-Datei der Methodik | 0.21 |
| `/robots.txt`, `/sitemap.xml`, `/sitemaps/<teil>.xml` | Abschnitt 4.2 | 0.21 |
| `/favicon.ico`, `/favicon.svg`, `/apple-touch-icon.png`, `/og-image.png` | Icons, Vorschaubild für soziale Netzwerke | 0.21 |
| `/bilder/portrait.jpg` | Foto der Startseite aus `website-bilder/` (Q6); fehlt es: 404, die Startseite zeigt den Platzhalter | 0.18 |
| `/daten/start.json`, `/daten/spieltag/<liga>.json`, `/daten/spiel/<id>.json` | Datensätze der Seiten (Codes) | 0.17/0.18 |
| alles andere unter `/de/` bzw. `/en/` | „Seite nicht gefunden“ (404) in dieser Sprache, sonst deutsch | 0.21 |

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
- **Eindeutig ist nur die ID am Ende.** Liga und Teamnamen dienen der Lesbarkeit; der Slug entsteht aus den **API-Namen**.
  Angezeigt werden seit 0.21 die Anzeigenamen je Sprache (`teamnamen_anzeige.csv`, Glossar Abschnitt 11); sie ändern
  den Slug nie.
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



### 4.2 Indexierung, Kopfbereich, Sitemap, Caching (seit 0.21, SEO-Briefing)

- **Index-Regeln** (`seo.py`, eine Funktion je Seitenart für Seite und Sitemap): Spielseite indexierbar, wenn `index_ab`
  gesetzt ist, der Anstoss ab `index_ab` liegt, das Spiel in einem Tab der Spieltag-Seite steht oder gespielt ist, kein
  ausschliessender Status und kein „Werte ab“ vorliegt und **mindestens 6 der 8 Kennzahlen** bewertet sind (seit 0.24,
  `index_min_kennzahlen` in `website.toml`, Entscheid Carsten 24.11.2026 nach dem Frontend-Review; bis 0.23 eine). Archivseite
  indexierbar, wenn der Spieltag ab dem Tag von `index_ab` begonnen hat. Inhaltsseiten, Startseite und Spieltag immer;
  Cookie-Einstellungen und 404 nie. Nicht indexierbar = `noindex,follow`.
- **Vor dem Livegang** ist `index_ab` in `app/config/website.toml` leer: nichts aus den Spiel- und Archivseiten ist
  indexierbar, die Teile der Sitemap je Liga und Saison sind leer. Die Vorschau sendet immer `noindex, nofollow`; die
  Vorschau-Leiste zeigt, ob die Seite nach dem Livegang in den Index käme.
- **Kopfbereich:** Title und Description je Seite (Spielseite je Zustand, Description höchstens 155 Zeichen: zuerst auf
  eine Kennzahl, dann ohne Signalqualität kürzen, notfalls am Wortende), `canonical`, `hreflang` de/en/x-default (= de),
  Open Graph (`og:locale` de_CH/en_GB, Bild `og-image.png`), Twitter-Karte, JSON-LD: Startseite Organization + WebSite,
  sonst BreadcrumbList + WebPage bzw. ContactPage; **seit 0.24 kein `SportsEvent` mehr** (ohne Ort für Google ungültig,
  kein Nutzen; Entscheid Carsten 24.11.2026; bis 0.23 auf indexierbaren Spielseiten). 404: ohne canonical und hreflang.
- **robots.txt:** alles erlaubt (noindex-Seiten werden nicht gesperrt, sonst sähe Google das noindex nicht), Verweis auf
  die Sitemap. **Sitemap:** `/sitemap.xml` ist ein Index mit `/sitemaps/seiten.xml` (Startseite, Spieltag je Liga,
  Methodik, Glossar, Kontakt, Impressum, Datenschutz) und je Liga und Saison `/sitemaps/<liga>-<2026-27>.xml`; jeder
  Eintrag mit beiden Sprachfassungen und x-default.
- **Caching:** HTML `Cache-Control: public, max-age=300` (Vorschau und Fehlerseiten `no-store`); CSS, JS, Schriften und
  Icons 30 Tage; Excel 1 Tag; Weiterleitungen `no-store`. **Dateifehler:** Start-, Spieltag-, Archiv- und Spielseiten
  antworten mit **503**, `Retry-After: 600` und `no-store`; Inhaltsseiten bleiben mit 200 erreichbar.
- **Seitenspeicher (seit 0.24, Frontend- und Backend-Review):** Der Dienst speichert jede fertige Seite (nur Status 200,
  nicht das Kontaktformular) je Adresse, Datenstand der Dateien, Importstand und **Minute**. Ein Statuswechsel (z. B.
  „Gespielt“ nach Anpfiff + 2 h) erscheint dadurch höchstens eine Minute später. Gleichzeitige Aufrufe derselben neuen
  Seite rechnen nur einmal. Startseite: 0,37 s → 0,001 s; 10 gleichzeitige 7,6 s → 0,01 s (lokal gemessen). Während des
  Datentauschs (`import/uebergabe.json`) bleibt der bisherige Datenstand. Zusätzlich: `Permissions-Policy`, Zeitlimit 20 s
  je Verbindung, strenge Prüfung von `Content-Length`; Komprimierung und HSTS per Traefik-Label.
- **Web-App-Manifest und Browserfarbe (seit 0.24, Entscheide Carsten 24.11.2026):** `/manifest.webmanifest` mit Name
  „Soccer Intelligence“, Kurzname „Soccer Intel“, `display: browser` (Zurück-Knopf des Browsers bleibt), Start `/`,
  Icons 192 und 512 px sowie „maskable“ 512 px (aus `favicon.svg` abgeleitet); `<meta name="theme-color" content="#0B3D2E">`.
  „Zahlen im Detail“ auf der Spielseite mindestens 44 px hoch (Touch-Ziel).
- **Barrierefreiheit:** Sprunglink „Zum Inhalt springen“, sichtbarer Fokus (dunkelgrün mit weissem Abstand, auf dunklen
  Flächen in Akzentfarbe), Tabs und Aufklapper ohne JavaScript, Tabellen mit `caption` und `scope`, Kontraste nach
  WCAG AA (Statuskachel #5B6B61, Formkreis „U“ #487560, Eingabefelder #7A8A81). Geprüft mit axe-core (WCAG 2.1 AA und
  Best Practice) auf allen Seitenarten in beiden Sprachen, Desktop und Handy.

## 5. Seite Spieltag (Übergabe, Abschnitt 6)

### 5.1 Aufbau (seit 0.18 nach Entwurf 3d)
1. Kopf: Logo „Soccer Intelligence“, Navigation Spieltag · Methodik · Impressum.
2. Dunkler Kopfbereich: H1 „Alle Spiele im **Überblick**“ (Akzent), Text „Wähle deine Liga und sieh, bei welchen Partien die Zahlen aus der Reihe fallen.“, darunter die Liga-Auswahl: vier Kacheln mit „10. Spieltag“ bzw. Pausenname (A5); die gewählte in der Akzentfarbe. Seit 0.21.2 ohne „Aktueller Datenstand“ (steht in der Fusszeile) und mit niedrigerem Kopfbereich (bis 0.21.1: „Aktueller Datenstand: Mo 16.11.2026“, D1).
3. Titel = Liganame, Zusammenfassung „10. Spieltag · 20.11. – 22.11.2026 · 9 Partien · 2 mit Auffälligkeit · plus 1 Nachholspiel“ (je Tab eine eigene Zeile).
4. Bei englischer Woche Tabs „10. Spieltag · ab 20.11.“ / „11. Spieltag · ab 24.11.“ (Standard: der frühere; ohne JavaScript stehen beide untereinander).
5. Legende Stark · Leicht · Ohne Auffälligkeit, „Wie lese ich das?“ (aufklappbar, Texte Übergabe 6.3).
6. Ohne jede Abweichung der Hinweis „Bei diesem Spieltag weicht kein Wert deutlich vom Ligaschnitt ab.“
7. Partien als Kacheln im Raster (Computer zwei Spalten, Handy eine), Fusszeile.

### 5.2 Welche Spiele (gleiche Regeln wie Dashboard, `07`, Abschnitt 4)
- Tabs = die Spieltage, die das Dashboard ohne Auswahl als Abschnitte zeigt (anstehender Spieltag, weitere Spieltage, die heute bis heute + 5 beginnen; bis 0.21 heute + 6).
- Je Tab: alle Spiele des Spieltags (auch gespielte und solche mit Status, F5), dazu Nachhol- und vorgezogene Spiele der nächsten 7 Tage, die in den Zeitraum des Tabs fallen (sonst im ersten Tab, F4).
- Pausen (F7): Ist kein Spieltag in höchstens 14 Tagen, ersetzt eine Pausen-Karte die Liste (Spielpause, Winterpause, Sommerpause, Saisonstart). Datenstand über 48 Stunden (seit 0.20; bis 0.19.1: 3 Tage): gelbe Warnbox, Liste bleibt.

### 5.3 Einstufung je Partie (Codes in Klammern)
Reihenfolge der Prüfung (seit 0.20, Entscheidungsprotokoll 19.11.2026 Nr. 1): **Status > gespielt > Werte ab > zu wenig Daten > Stufe** (bis 0.19.1: Status > gespielt > nicht gewertet > Stufe).

| Art | Wann |
|---|---|
| Status (`status`) | Spielplan-Status verschoben, abgesagt, abgebrochen, ausgesetzt, gewertet (gewertet nur für nie gespielte Spiele, `07`, 4.9) |
| Gespielt (`gespielt`) | Ergebnis in der Datenbank, oder ab Anpfiff + 2 Stunden (ohne Anstosszeit ab Mitternacht) mit Chip „Gespielt“ (seit 0.20; bis 0.19.1 ab dem Anstoss „Ergebnis folgt“) |
| Werte ab (`werte_ab`, seit 0.20) | vor dem Anstoss, ein Team hat sein vorheriges Ligaspiel noch nicht gespielt bzw. das Ergebnis fehlt: Chip „Werte ab 5.12.“ bzw. „Werte folgen“ |
| Zu wenig Daten (`zu_wenig_daten`, bis 0.19.1 `nicht_gewertet`) | alle 8 Kennzahlen vorläufig (F2) oder keine Werte |
| Stark / Mittel / Gering (`stark`, `mittel`, `gering`, seit 0.20; 0.19: `hoch`/`mittel`/`gering`) | mindestens eine nicht vorläufige Kennzahl ist auffällig; Art = höchste Signalqualität (Regelwerk 2.2). Bis 0.18: Stark (`stark`) / Leicht (`leicht`) als Grösse der Abweichung |
| Ohne Auffälligkeit (`ohne`) | sonst |

Stufen kommen aus `schwellen.toml` über den Rechenkern (Übergabe 4.1, keine festen 20/35). Vorläufige Kennzahlen zählen für die Stufe nicht.

### 5.4 Sortierung und Zählung
- Seit 0.18 wie im Entwurf 3d (Skript `renderVals`): Stark (nach grösster Abweichung) → Leicht (nach grösster Abweichung) → Ohne Auffälligkeit → alle übrigen (Nicht gewertet, Status, Gespielt) als **eine** Gruppe nach Anstoss.
- Nachhol- und vorgezogene Spiele werden mitsortiert (wie im Entwurf); in 0.17 standen sie als Gruppe am Ende (Annahme A2, ersetzt).
- Zählform seit 0.20 (Template-Briefing 3.3): „9 Spiele“, „9 Spiele + 1 Nachholspiel“, „8 Spiele + 2 Nachholspiele“, nur Sonderspiele „1 Nachholspiel“ bzw. „1 Spiel vorgezogen“, danach „· 4 auffällige Spiele“ (Sonderspiele eingeschlossen). Chips der Sonderspiele mit Nummer: „Nachholspiel · Spieltag 13“, „Vorgezogen · Spieltag 23“ (auch im Scoreboard und in der Kopfzeile des Rankings). Bis 0.19.1: „Partien“, „mit Auffälligkeit“, „plus n Nachholspiel(e)“.

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

**Seit 0.20 Signalqualität `stark`/`mittel`/`gering`** (Chips „Signalqualität stark“ usw.; Werte unverändert). **Seit 0.19 (Prognosewert, Regelwerk 2.2):** Website-Daten tragen statt „stark/leicht“ den Prognosewert `hoch`/`mittel`/`gering` (Kacheln, Karten, Ranking, Chips „Prognosewert hoch“ usw.). Gestaltung bis zum Designentwurf der Website unverändert: hoch wie bisher „stark“ (dunkel), mittel und gering wie bisher „leicht“ (hell). Neuer Entwurf und Release B folgen.

### 7.1 Matchdetail (Entwurf 2i, ergänzend 2c; Übergabe Abschnitt 7)
**Jede Paarung des Spielplans hat eine eigene Seite** unter `/spiel/<Spiel-ID von API-Football>` – auch gespielte, Nachhol- und vorgezogene Spiele. Verlinkt sind sie von der Spieltag-Seite und vom Ranking der Startseite. Verschobene und abgesagte Spiele haben ebenfalls eine Seite (über die Adresse erreichbar), werden aber nicht verlinkt (F8). Programm: `app/website/spiel.py` (Datensatz), `vorlagen/spiel.html`.

1. Kopf rechts „Zurück zum Spieltag“ (statt Navigation).
2. Scoreboard: Liga · Spieltag, Termin (bzw. „Endstand 2 : 1“ / „Ergebnis folgt“, Q5) mit Chips Nachholspiel/vorgezogen/Status, beide Teams mit Formkurve „Letzte 5 Spiele“ (S/U/N, „–“ = noch kein Spiel, KPI 01) und Legende.
3. Kernaussage: grösste Auffälligkeit („+44,00 % · Über 2,5 Tore · Mehr als 2,5 Tore erwartet“); ohne Auffälligkeit „Keine statistischen Auffälligkeiten – Alle 8 Kennzahlen liegen im Normalbereich. Die größte Abweichung: …“; nicht gewertet „Nicht gewertet“; Status „Für dieses Spiel gibt es keine Werte.“
4. Hinweise: Nachholspiel („… wird am So 22.11. um 17:30 Uhr nachgeholt“), vorgezogen, gespielt („Die Werte wurden mit den Daten vor dem Spiel berechnet.“, Q5). Seit 0.20 mit dem Schnappschuss (`07`, 4.9): gespielte Spiele zeigen seine Werte; fehlt er „Werte nachträglich mit den Daten vor dem Spiel berechnet.“; weicht das Ergebnis vom zuerst übernommenen ab „Endstand: Ergebnis nachträglich korrigiert“. Bis Anpfiff + 2 Stunden steht der Termin (kein Live-Status), danach „Gespielt“ bzw. „Endstand 2 : 1“. Vor dem Anstoss ohne Werte: Scoreboard bleibt, statt der Kennzahlen „Werte ab Sa 05.12. – sobald beide Teams ihr vorheriges Ligaspiel gespielt haben.“ bzw. „Werte folgen, sobald das Ergebnis vom 28.11. übernommen ist.“ Ohne Auffälligkeit „Keine der {n} Kennzahlen überschreitet ihre Schwelle.“ mit n = bewertete Kennzahlen (n = 1: „Die einzige gewertete Kennzahl …“).
5. „Auffälligkeiten“: Karten je Kennzahl mit Stufe, nach Betrag der Abweichung sortiert; Balken (Länge = Betrag/2 % der Breite, höchstens 50 %, über 100 % gekappt mit Streifen, Übergabe 4.2); aufklappbar „Zahlen im Detail“: Erwartungswert, „Je Mannschaft · Mittelwert beider Teams“ (bei Gelben Karten „Heim + Gast“ mit zweiteiliger Leiste, Q1), Ligaschnitt bzw. „Vergleichswert (Marke)“ 2,50 bei KPI 03 (Q2), Abweichung mit Stufe, „Zuklappen“.
6. „Im Normalbereich“: übrige Kennzahlen als aufklappbare Zeilen, nach Betrag; eine einzelne vorläufige Kennzahl dort schraffiert mit „· nicht gewertet“ (Q4). Ist das ganze Spiel nicht gewertet: Hinweisbox und Überschrift „Kennzahlen“ (ohne Werte: eigener Text „Für dieses Spiel liegen noch keine Werte vor …“).
7. Status-Spiele (verschoben, abgesagt …): nur Scoreboard und Kernaussage, keine Kennzahlen (wie die graue Kachel, F5).
8. Seit 0.21.2: grüne Schaltfläche „Alle Spiele des Spieltags“, darunter der unterstrichene Textlink „Wie entstehen diese Werte?“ (Methodik); kein Zeitzonen-Hinweis auf der Spielseite.

**Seit 0.23 (Entwurf Spiel_P1 „2k final“, Beschlüsse Carsten 24.11.2026):** einheitliche Karten in vier Fällen –
**A** auffällig (Chip Signalqualität), **B** „Keine Auffälligkeit“, **C** „Nicht eingestuft ⓘ“ (Schaltfläche klappt
eine kurze Erklärung auf, ohne JavaScript immer sichtbar), **D** „Zu wenig Daten“ mit „Keine Bewertung möglich.“.
Gruppen „Auffälligkeiten“ und „Ohne Auffälligkeit“ (bei zu wenig Daten „Kennzahlen“; der Hinweis nennt die neue
Mannschaft). „Zahlen im Detail“ in vier Blöcken: letzte 10 Ligaspiele je Team (Gelbe Karten: Summe beider Teams, sonst
Mittelwert), Ligadurchschnitt pro Spiel bzw. Marke 2,5, Abweichung, **Grenzwert** = Vergleichswert × (1 ± Schwelle/100),
exakt gerechnet und kaufmännisch auf zwei Stellen, in der Richtung der Abweichung; ohne Schwelle in dieser Richtung
„in dieser Richtung keine Schwelle in der Liga“. Satz zur Schwelle mit ganzer Zahl („mehr als 35 % unter dem
Ligadurchschnitt“). Kurzaussagen je Kennzahl „Mehr/Weniger … erwartet“. Bei „Beide Teams treffen“ steht „(in %)“ in der
Kernaussage, bis 520 px ausgeblendet. Rechenlogik unverändert (Regelwerk, Abschnitt 8).

**Seit 0.25 – Auswertung nach dem Spiel** (Entwurf `Auswertung_D`, Design-Spezifikation Release_08 vom 25.11.2026,
Beschlüsse 35–52, Entscheide Carsten 25.11.2026): Sobald der **Endstand** vorliegt, zeigt dieselbe Adresse die Auswertung
statt der Erwartungsansicht. Scoreboard mit grossem Spielstand und „Halbzeit 1 : 0“ (ohne Formkurve und Kernaussage),
ein Hinweisfeld (gespielt, nachträglich berechnet, korrigiert, Statistik fehlt, ohne Erwartungswerte, zu wenig Daten,
Nachholspiel), Tabelle „Erwartet und tatsächlich“ (echte `<table>` mit Rollen; Gruppen „Auffälligkeiten“ und „Ohne
Auffälligkeit“ bzw. „Kennzahlen“; Spalten Ligadurchschnitt · Erwartungswert · Tatsächlich; ab 700 px Chips, darunter
Symbol + Text und graue Zeile; bis 360 px kleinere Spaltenköpfe), Box „Statistisch auffällig ab“ (Knopf mit
`aria-expanded`, geschlossen; Grenzwert in Richtung der Abweichung, „nicht definiert“, bei „Über 2,5 Tore“ ohne Schwelle
„keine Schwelle“). **Bestätigt** nach Regelwerk 11.1 (Vergleich mit dem Ligadurchschnitt vor dem Spiel, strikt;
„Über 2,5 Tore“ mindestens 3 / höchstens 2; „Beide Teams treffen“ Ja/Nein; fehlt der Wert: „Bewertung folgt“), nur Fall A.
Erwartungswerte aus dem Schnappschuss, tatsächliche Werte immer aktuell; der Import hält die zuerst bekannten Ist-Werte
fest (`<API-ID>.ist.json`), weicht ein Wert später ab, steht „Ergebnis oder Statistik nachträglich korrigiert“.
Description „{Heim} – {Gast} ({Liga}, {Spieltag}, {Datum}): Endstand 2 : 1. Unsere Erwartungswerte im Vergleich …“.
Spielseite vor dem Spiel (Release_08, Abschnitt 9): „Statistisch auffällig ab“, „nicht definiert“, graue Regelzeile statt
Erklärsätzen, Fall C ohne ⓘ mit Satz „Diese Abweichung ist in der {Liga} kein verlässlicher Hinweis …“ (Liga als Feld je
Liga und Sprache, DE „in der La Liga“), Legende „Keine Auffälligkeit / Nicht eingestuft“, „Erwarteter Anteil“,
„Beide Teams treffen“ ohne Nachkommastellen (Grenzwert weiter zwei Stellen). **Spieltag-Seite** (Release_08, 16): gespielte
Kachel mit Meta-Zeile, Toren je Team, Bilanz („2 von 3 bestätigt“, alle bestätigt grün mit ✓, „Keine Auffälligkeiten“,
fehlt ein Wert „Bewertung folgt“, ohne Endstand „Endstand folgt“), gespielte Spiele am Ende; die Kopfzeile zählt alle Spiele
mit Auffälligkeit, auch gespielte; Legende „Gespielte Spiele“. Archiv unverändert (nächstes Release).

**Seit 0.26 (Design 550, Beschlüsse 53–58, Entscheide Carsten 25.11.2026):** Spieltag-Seite mit Link „Frühere Spieltage
ansehen“ zur Archivseite des Spieltags vor dem ersten Tab (am 1. Spieltag kein Link); Archivseiten zeigen gespielte Spiele
mit der neuen Kachel (Tore, Bilanz), nur Pfeile zum Blättern. Auswertung: Hinweisfeld nur bei Ausnahmen („Hinweis:“,
„Nachholspiel:“), zwei getrennte Tabellen, Zeile „Kein Ligadurchschnitt – feste Marke 2,5.“, Regelzeile „… über der Marke
2,5“. Spielseite: „kein verlässlicher Hinweis für kommende Spiele“, Chips immer rechtsbündig, lange Teamnamen umbrechen
nur zwischen Wörtern bzw. mit Trennstrich. Betreiberangaben mit `tools/impressum_einrichten.sh` (nur `.env`).

Werte unverändert aus dem Rechenkern (F6): Erwartungswert = `hauptwert`, Teamwerte = `heim`/`auswaerts`, Ligaschnitt = `referenz`, Abweichung = `abweichung` (gerundet), Stufe aus `schwellen.toml`; KPI 08 in Prozent.

### 7.2 Startseite (Entwurf 1d, ergänzend 1b; Übergabe Abschnitt 5)
Programm: `app/website/start.py` (Datensatz), `vorlagen/start.html`.

1. Kopfbereich „Fußballspiele **durchleuchtet.**“ mit Knöpfen „Auffällige Spiele“ und „So funktioniert’s“.
2. **„Die auffälligsten Spiele“** = genau die Top Anomalien des Dashboards (F6): je Liga der zeitlich nächste Block (`core/anzeige.top_block`), nur Spiele mit Werten (`values_from`, nie „Werte ab“); seit 0.20 bleiben gespielte Spiele mit den Werten ihres Schnappschusses auf ihrem Platz, ausgegraut mit „Gespielt“ bzw. „Endstand 2 : 1“, es rückt keines nach (bis 0.19.1: nur Spiele vor dem Anpfiff); Auswahl und Rangfolge nach Regelwerk 2.6 (`core/top.select_top`, seit 0.19: Prognosewert hoch vor mittel vor gering, dann grösster Betrag, früheres Datum, Ligareihenfolge; Liga-Mix höchstens 2 je Liga; höchstens 4, einer je Spiel; vorläufige Werte und verschobene Spiele nie). Je Zeile: Rang, „Bundesliga · Spieltag 10“, Paarung, Termin, Pfeil, Abweichung, Stufe, Kennzahl, Balken; Link zum Matchdetail.
3. Zustände statt der Liste (Pausenkarte): **Keine Abweichungen** (eine Liga spielt, aber ohne Auffälligkeit) · **Spielpause** / **Winterpause** (keine Liga in den nächsten 14 Tagen; Winterpause, wenn Weihnachten in der Lücke liegt) · **Saisonstart** (alle nächsten Spieltage gehören zu einer neuen Saison) · **Sommerpause** („Die Saison ist beendet“, kein angesetztes Spiel) · **Nächster Spieltag** ohne Pausennamen bei veraltetem Datenstand (S9). Massgebend ist der früheste nächste Spieltag aller Ligen; der Knopf führt zu dessen Liga. Tage-Zähler (Q7) bei Spiel-, Winterpause, Saisonstart und veraltetem Stand. Fehler in den Daten: Hinweis „Daten werden geprüft“.
4. Warnbox bei veraltetem Datenstand (über 48 Stunden seit 0.20, bis 0.19.1 über 3 Tage, F7); bis 0.21.2 darunter „Aktueller Datenstand: …“ (D1), seit 0.22 nur noch in der Fusszeile (Wunsch Carsten 20.11.2026).
5. „Deine Liga. Dein Spieltag.“ (vier Liga-Knöpfe), „So funktioniert’s“ (drei Spalten), Band „Bereit für den Spieltag?“, Block „Von einem Fußballfan gebaut“ mit Foto (Q6) oder Platzhalter, SEO-Text „Was ist Soccer Intelligence?“.

**Foto (Q6):** Datei `portrait.jpg` im Ordner `/docker/football-dashboard/website-bilder/` auf dem Server (quadratisch, mindestens 230 × 230 Pixel, JPEG). Der Ordner ist nur lesend im Container `soccer-vorschau` eingebunden (`/bilder`), steht in `.gitignore` und kommt nie ins Programm-Abbild (Dockerfile kopiert nur `app/`). Ein neues Foto wirkt sofort (kein Neustart nötig; Browser-Zwischenspeicher bis 1 Stunde).

### 7.3 Inhaltsseiten, Archiv und Fehlerseite (seit 0.21)

**Seit 0.21.1 (Entwurfsrunde 20.11.2026, Entwürfe vom 20.11.):** Signalqualität in kräftigeren Grüntönen (Chip stark
#C8DECE/#2F4A3C/#8FB59D, Balken #3E6B53/#A3BFAD; mittel #DAEADF/#3E5247/#A9C8B3, #5F8C72/#B5CFBE; gering
#EAF2EC/#5B6B61/#BFD5C6, #7BA38A/#C8DACE; Kacheln stark #D6E8DB mit Streifen #4F8268, mittel #E5F0E7/#7BA38A,
gering #F3F8F4/#A3BFAD). Spielseite ohne „Weitere Spiele dieses Spieltags“; „Alle Spiele des Spieltags“ ist Textlink,
„Wie entstehen diese Werte?“ die Schaltfläche. Spieltag: SEO-Satz „Wir bieten transparente …“ entfällt. Methodik:
Einstieg als drei Karten (Ebene, Titel, eine Zeile); mit Skript blendet die Wahl tiefere Ebenen aus (Start: Ebene aus
der Adresse, sonst 1), ohne Skript ist alles sichtbar; Weiter-Schaltflächen je Ebene (höchstens 300 px, Rundung 28 px);
Ligen-Tabellen bis 520 px ohne Mindestbreite (kein Scrollbalken von 320 bis 412 px, bis 340 px ohne Balkensymbol).
Mobil bis 520 px: Navigation und Sprachmenü einzeilig, bis 440 px Sprachknopf „DE“/„EN“; Footer bis 640 px mit 14 px
Abstand; SEO-Box der Startseite höchstens 816 px breit.

**Seit 0.21.2 (zweite Lieferung der Entwürfe vom 20.11., Entscheidungsprotokoll Beschluss 13):** Spielseite mit
grüner Schaltfläche „Alle Spiele des Spieltags“ und darunter dem Textlink „Wie entstehen diese Werte?“ (Rollen
gegenüber 0.21.1 wieder getauscht), ohne Zeitzonen-Hinweis. Spieltag: Kopfbereich ohne „Aktueller Datenstand“ und
niedriger (oben 12–24 px, unten 18–28 px). Startseite: SEO-Box als eigener Block nach „Von einem Fußballfan gebaut“;
in der Ranking-Karte bleibt der Signalqualität-Chip neben der Kennzahl, ein langer Name bricht um. Methodik:
Schaltfläche „Weiter mit Zahlen: Ein Spiel durchgerechnet“ (EN „Continue with numbers: a worked example“) auf dem
Computer einzeilig, bis 520 px höchstens 300 px breit mit festem Umbruch nach dem Doppelpunkt.

- **Startseite, Spieltag, Spielseite** nach den Entwürfen P1 vom 19.11.2026 (Main_P1, Spieltag_P1, Spiel_P1): Ranking als
  Karten mit Signalqualität (drei Balken), Kacheln je Stufe (stark/mittel/gering mit farbigem Streifen), Legende mit
  „Wie lese ich das?“, Zeitzonen-Hinweis, „Weitere Spiele dieses Spieltags“ auf der Spielseite; Endstand auf Kacheln und
  im Ranking kompakt „Gespielt · 2:1“, auf der Spielseite „Endstand 2 : 1“. Seit 0.23 im Ranking der Startseite „Endstand“ mit weisser Marke „2 : 1“ (vor dem Ergebnis weiter „Gespielt“), Karte hellgrau; auf der Spieltag-Seite steht die Legende in jedem Reiter nach der Zusammenfassung, vor den Kacheln; Methodik-Spalte „Schwelle (vom Ligadurchschnitt)“; Kopf bis 520 px mit der Sprachwahl rechts (Entscheide Carsten 24.11.2026).
- **Methodik** (Entwurf Methodik_10): drei Ebenen mit Sprungmarken (`#ebene1` bis `#ebene3`), ohne JavaScript alle
  sichtbar. Zahlen aus `schwellen.toml`: Saisons, bewährte Kombinationen (von 8 Kennzahlen × 4 Ligen × 2 Richtungen),
  Aufteilung stark/mittel/gering, Tabelle je Liga (Kennzahl, Richtung, Schwelle, Signalqualität) und Übersicht. Das
  Rechenbeispiel (Bayern – Stuttgart, 30. Spieltag 2025/26) ist fester Text; ein Test prüft seine Zahlen gegen die
  Schwellendatei. Excel-Datei mit allen Zahlen je Liga, Kennzahl und Richtung (Spiele, Trefferquote, Vergleichswert,
  Mehrwert, Spanne, Saisons mit Vorteil) und einem Blatt „Grundlage“, beim Aufruf aus der Schwellendatei erzeugt.
- **Glossar** (ohne Entwurf, im Stil der Methodik): Grundbegriffe, Kennzahlen, Spielstatus, Datenstand und Zeiten;
  Begriffe nach dem Glossar (Release-Fassung 19.11.2026). Text freigegeben von Carsten am 20.11.2026.
- **Kontakt** (Entwurf Kontakt): Formular mit Pflichtfeldern, Sicherheitsfrage und verstecktem Feld. **Seit 0.23 aktiv** (Versand über `info@`, Prüfung auf dem Server mit Fehlern je Feld, wechselnde Rechenaufgabe mit Prüfsumme, höchstens 3 Nachrichten pro Stunde, keine Speicherung; Spezifikation `09_Betrieb_EMail.md`, Abschnitt 6). Ohne eingerichteten Versand bleibt die Schaltfläche gesperrt.
- **Impressum, Datenschutz** (Entwürfe): Betreiberangaben nur aus `.env` auf dem Server (`SI_IMPRESSUM_NAME`,
  `SI_IMPRESSUM_ADRESSE` mit „|“ getrennt, `SI_KONTAKT_EMAIL`); fehlen sie, steht ein Platzhalter. Juristische Prüfung
  vor dem Livegang offen.
- **Archivseite je Spieltag** (ohne Entwurf, aus der Spieltag-Seite abgeleitet): Kopf „<Liga> · Spieltag <nr> · Saison
  <saison>“, Pfeile zum vorherigen und nächsten Spieltag (der aktuelle führt auf die Spieltag-Seite), Kacheln mit
  Endstand und Signalqualität der Werte vor dem Spiel; „Zurück“ der Spielseite führt bei gespielten Spielen hierher.
- **Seite nicht gefunden** (Entwurf Fehler_404): drei Schaltflächen (Startseite, Spieltag, Methodik), 404, noindex.

## 8. Testfälle (seit Version 0.17, `tests/test_website.py`)

| Nr. | Situation | Erwartet |
|---|---|---|
| W1 | Formate | „Sa 21.11.“, „+47,36 %“, „−22,07 %“ (U+2212), „0,00 %“ ohne Vorzeichen, „2 : 1“, Zeitraum über den Jahreswechsel |
| W2 | Einstufung | Status vor gespielt vor nicht gewertet vor Stufe; vorläufige Kennzahlen zählen nicht; seit 0.19 Prognosewert hoch vor mittel vor gering; seit 0.20 Status vor gespielt (ab Anpfiff + 2 h) vor Werte ab vor zu wenig Daten vor Signalqualität stark/mittel/gering |
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
| W14 | Matchdetail | Q1 (Summe nur Gelbe Karten, sonst Mittelwert), Q2 (Marke 2,50), Q4 (einzelne vorläufige Kennzahl unter Normalbereich), Q5 (Endstand, Ergebnis folgt, Hinweis), nicht gewertet mit/ohne Werte, Status ohne Kennzahlen, Nachholspiel-Hinweis, Formkurve, Balken und Zahlen; **jede Paarung eines Spieltags und der ganzen Saison hat eine eigene Seite** (echte Saisonlisten); seit 0.20: Schnappschuss, nachträglich, korrigiert, „Werte ab“ auf der Seite, bis Anpfiff + 2 h normal |
| W15 | Startseite | Ranking wie Dashboard (Prognosewert, Betrag, Liga-Mix, höchstens 4, einer je Spiel, ohne vorläufige und verschobene, nur vor dem Anpfiff); Zustände Spielpause, Winterpause, Sommerpause, Saisonstart, unbekannt (veraltet), keine, gesperrt; Tage-Zähler; seit 0.20 gespielte bleiben ausgegraut (kein Nachrücken), Endstand |
| W16 | Sicherheit | keine Inline-Stile und -Skripte (Content-Security-Policy; JSON-LD ist Daten), jede Balkenbreite hat eine CSS-Klasse |
| W17 | Adressen (0.21, `tests/test_website_021.py`) | Slugs, Pfade je Sprache, Erkennen mit 200/301/302/404, Sprachwechsel auf dieselbe Seite, alte Saisons 404 |
| W18 | Archiv | Kopf, Endstand „Gespielt · 2:1“, Pfeile, nicht begonnener Spieltag 404, „Zurück“ der Spielseite ins Archiv |
| W19 | Indexierung, Sitemap | Index-Regeln (Livegang, Fenster, Status, Werte ab, bewertete Kennzahl, Saison), robots.txt, Sitemap-Index, hreflang je Eintrag, vor dem Livegang leer |
| W20 | Kopfbereich | canonical, hreflang, og:locale, Title; JSON-LD lesbar; 404 ohne canonical; Description höchstens 155 Zeichen ohne Wett-Wörter (Fehler gefunden: „Zu wenig Daten“ und Status wurden nicht gekürzt) |
| W21 | Englisch | gleiche Schlüssel und Platzhalter in `de.json` und `en.json`, Formate, Anzeigenamen mit Rückfall auf die Datenquelle |
| W22 | Caching, 503 | Kopfzeilen je Antwort, Icons, 503 mit Retry-After, Vorschaubild 1200 × 630 |
| W23 | Ohne JavaScript | Sprungliste, Tab-Überschriften, Tab-Leiste versteckt; Kachelklassen und Signalqualität-Chips |
| W24 | Methodik | Zahlen aus der Schwellendatei, Rechenbeispiel passt zur Schwellendatei, Excel-Download (Spalten, Zeilen, Zahlen) |
| W25 | Inhaltsseiten | je Seite ein H1, Sprache, keine Inline-Stile, eindeutige IDs, Sprungmarken vorhanden; Betreiberangaben nur aus der Server-Konfiguration; keine privaten E-Mail-Adressen im Code |
| W26 | Endstand | kompakt auf Kacheln, lang auf der Spielseite |
| W27 | Entwurfsrunde 20.11. (0.21.1) | Spielseite ohne „Weitere Spiele“, Spieltag ohne SEO-Satz, Methodik mit drei Karten und Ebenen, Farben, Sprachknopf mobil |
| W28 | Entwürfe 20.11., zweite Lieferung (0.21.2) | Spielseite Schaltfläche/Textlink und kein Zeitzonen-Hinweis; Spieltag-Kopf ohne Datenstand; SEO-Box eigener Block; Chip neben Kennzahl; Weiter-Schaltfläche mit Umbruch nur mobil |
| W29 | Wünsche 20.11. (0.22) | Startseite ohne „Aktueller Datenstand“; Athletic Club heisst „Athletic Bilbao“ (DE/EN), Adresse bleibt `athletic-club` |
| – | Browser (vor dem Release, nicht automatisch) | axe-core 4.10 auf allen Seitenarten DE/EN, 1280 und 390 px: keine Verstösse; 360 px ohne Querscrollen; Sprachmenü (Escape, Klick daneben), Tabs mit und ohne JavaScript, Download |

## 9. Annahmen (bitte in der Vorschau prüfen)

| Nr. | Annahme | Grund |
|---|---|---|
| A1 | ~~Spieltag-Kachel und Liste im Stil der Startseite~~ – **erledigt mit 0.18**: genau nach Entwurf 3d | Entwurf `Spieltag_P1` war in 0.17 nicht angekommen |
| A2 | ~~Nachhol- und vorgezogene Spiele als eigene Gruppe am Ende~~ – **ersetzt mit 0.18**: mitsortiert wie im Entwurf 3d (Abschnitt 5.4) | Entwurf 3d sortiert alle Spiele gemeinsam |
| A3 | Status „gewertet“ (am grünen Tisch) bekommt den Chip „Am grünen Tisch gewertet“, damit er nicht mit „Nicht gewertet“ verwechselt wird | Begriffe sonst gleich |
| A4 | ~~„Ergebnis folgt“ als Chip, solange das Ergebnis nach dem Anstoss noch nicht übernommen ist~~ – entfällt seit 0.20 (Entscheidung Carsten 19.11.2026): ab Anpfiff + 2 Stunden „Gespielt“ | Übergabe nennt nur „Ergebnis“ |
| A5 | Liga-Kachel zeigt in einer Pause den Pausennamen statt der Spieltagsnummer | Übergabe nennt nur „24. Spieltag“ |
| A6 | Bei veraltetem Datenstand ohne anstehenden Spieltag: Warnbox und Karte „Nächster Spieltag am …“ ohne Pausennamen | S9: keine Pausenhinweise bei veraltetem Stand |
| A7 | Die Pausen-Karte der Spieltag-Seite hat keinen Tage-Zähler (nur die Startseite, Q7) | Übergabe 6.4; Entwurf 3d bestätigt |
| A8 | Navigation zu Methodik und Impressum zeigt bis zur Umsetzung „Diese Seite folgt später.“ | Seiten noch nicht im Umfang |
| A9 | Vorschau-Leiste oben (Zeitpunkt, Eingabe, seit 0.21 Index-Status) nur in der Vorschau, nicht Teil der Website | wie die Prototyp-Leiste des Entwurfs |
| A10 | Methodik: Die Angabe „Auffällige Spiele je Spieltag“ (Entwurf: z. B. Bundesliga stark 1,4 · mittel 1,9 · gering 1,4) fehlt vorerst; die Übersicht zeigt Anzahl der Schwellen je Stufe | Zahlen stehen nicht in `schwellen.toml`; **Entscheid Carsten 20.11.2026: weglassen** |
| A11 | Methodik: Ebenen als Sprungmarken, alle Ebenen immer sichtbar (der Entwurf blendet tiefere Ebenen erst nach Wahl ein) | alles im HTML (Beschluss Thema 4), ohne JavaScript nutzbar |
| A12 | Vorschaubild `og-image.png` sprachneutral: Logo, „Soccer Intelligence“ und die vier Ligen | ein Bild für beide Sprachen |
| A13 | Glossar und Archivseite: Texte von Claude vorgeschlagen, **freigegeben von Carsten am 20.11.2026** | Beschluss 19.11.2026: ohne Entwurf |
| A14 | Ranking der Startseite: gespieltes Spiel zeigt „Gespielt · 2:1“ wie die Kachel | Glossar Abschnitt 19 |
| A15 | Methodik Ebene 3: Chip DE „Ebene 3 · Für Statistik-Fans“ (EN „Level 3 · Full details“); Auswahlkarte „Alles im Detail“ | Beschluss Carsten 20.11.2026 |
| A16 | Glossar-Link im Footer als fünfter Link nach „Methodik“ | Beschluss Carsten 20.11.2026 |

## 10. Offene Punkte

- **Beschluss Carsten 19.11.2026, bestätigt 20.11.2026: Englischer Match-Title mit „vs“** (Glossar): „{Home} vs {Away} · {League}, Matchday {n} {Season} | Soccer Intelligence“; Deutsch mit Gedankenstrich. Anzeigenamen je Sprache aus einer Namenstabelle (Glossar Abschnitt 11), Slug weiter aus dem Namen der Datenquelle (0.21). **Releaseplan** 0.20 / 0.21 / 0.22 / 1.0 freigegeben (`01`, Abschnitt 0); Spezifikation der E-Mail-Alarme offen, vor Beginn von 0.22.
- **SEO-Check, Beschlüsse Carsten 19.11.2026:**
  - *0.21* Kein `eventStatus` (z. B. verschoben): solche Seiten sind `noindex` und haben kein `SportsEvent`; Nachholspiele
    mit Werten tragen nur das neue `startDate`.
  - *0.21* Keine Event-Rich-Results angestrebt: `SportsEvent` als reine Auszeichnung, ohne Ort.
  - *0.20* Impressum und Datenschutz `index` und in der Sitemap (Cookie-Einstellungen bleiben `noindex`).
  - *0.20* H1 der Spielseite visuell versteckt („nur für Screenreader und Suchmaschinen“, gleicher Text wie das
    Scoreboard; CSS-Klasse für Screenreader, nicht `display:none`).
  - *0.20* Benannte Stufen in SEO-Texten gross wie im Glossar („High signal quality“ bzw. „Signalqualität stark“).
  - *0.20* Startseiten-Text „Die interessantesten Abweichungen und Prognosen des kommenden Spieltags.“ bleibt (Carsten).
  - *0.20* **Title der Spielseite mit Spieltag und Saison** (eindeutig auch über Saisons und Wiederholungsspiele):
    „{Heim} – {Gast} · {Liga}, {n}. Spieltag {Saison} | Soccer Intelligence“ bzw. „{Home} – {Away} · {League}, Matchday {n}
    {Season} | Soccer Intelligence“, z. B. „VfB Stuttgart – Bayern München · Bundesliga, 13. Spieltag 2025/26 | Soccer
    Intelligence“.
- **Beschlüsse Carsten 19.11.2026 (Themen 1–7, neun Fragen):**
  - *0.20* **Kachel Sonderspiel:** „Nachholspiel · Spieltag 13“ / „Rescheduled · Matchday 13“, „Vorgezogen · Spieltag 23“ /
    „Brought forward · Matchday 23“.
  - *0.20* **Zählform** im Tab nur mit Sonderspielen: „1 Nachholspiel“ / „1 rescheduled match“ (Mehrzahl entsprechend).
  - *0.20* **Am grünen Tisch:** Status nur bei nie gespielten Spielen; gespielte, später umgewertete Spiele bleiben normal
    gespielt mit Ergebnis auf dem Platz. Absicherung: Meldet die API für ein Spiel mit Ergebnis in der Datenbank `AWD`,
    wird „gewertet“ für die Anzeige ignoriert und intern gemeldet.
  - *0.20* **Tabs ohne JavaScript:** alle Tabs untereinander mit Überschrift und Sprungliste (Anker); das Skript schaltet
    die Tab-Ansicht erst ein, wenn es läuft. Aufklapper mit `<details>`.
  - *0.20* **Caching:** Daten und Berechnungen im Speicher bis zur nächsten Dateiänderung; HTML bei jedem Aufruf gebaut, mit
    `Cache-Control: max-age=300`; 503 mit `no-store`; CSS, JS, Schriften 30 Tage (Versionsnummer `?v=`). Kein statischer
    Export.
  - *bereits umgesetzt (0.17)* **Schriften** selbst gehostet (Outfit, Inter, variable WOFF2, `font-display: swap`, OFL);
    keine Google-Fonts-Links aus den Entwürfen.
  - *0.21* **Kontaktformular:** Versand per E-Mail über das Hostinger-Postfach (Zugang in `.env`), `Reply-To` = Absender,
    keine Speicherung; Pflichtfelder E-Mail, Nachricht, Einverständnis, Sicherheitsfrage; Prüfung auf dem Server;
    verstecktes Feld; höchstens 3 Nachrichten pro Stunde und Besucher (IP nur kurz im Speicher); Inhalt nie in Protokollen;
    funktioniert ohne JavaScript; Fehlertext „Deine Nachricht konnte nicht gesendet werden. Bitte versuche es in ein paar
    Minuten noch einmal.“ / „Your message could not be sent. Please try again in a few minutes.“ plus Feldfehler;
    Abschnitt Kontaktformular in der Datenschutzerklärung.
  - *0.21* **Cookie-Wahl:** eigenes Cookie `cookie_wahl` (`zugestimmt`/`abgelehnt`), 6 Monate, `SameSite=Lax`, `Secure`;
    vor Zustimmung nichts von Google (auch kein Tag Manager); Cookie-Einstellungen funktionieren ohne JavaScript;
    automatischer Browser-Test: keine Anfrage an Google vor der Zustimmung.
  - *0.20* **Barrierefreiheit:** WCAG AA auch für ausgegraute Kacheln (Text mindestens 4,5:1, „Gespielt“ als Text);
    Kontrast-Check der Entwurfsfarben im Design-Chat; automatische Prüfung mit axe-core; Lighthouse vor 1.0.
  - *Entwicklung:* Frist veralteter Spielplan 48 Stunden ab letztem erfolgreichem Lauf (0.20); Prüfung fehlender
    englischer Schlüssel vor jedem Release als Warnung (0.20); Anstosszeiten bereits in Europe/Zurich (seit 0.14),
    Zeitzonenangabe in strukturierten Daten (0.21); Wiederholungsspiel wie beschlossen (0.20).
- **Lücke gefunden (19.11.2026), Behebung in 0.20: „Werte ab …“ auf der Website.** Das Dashboard zeigt Werte erst,
  wenn beide Teams ihr vorheriges Ligaspiel gespielt haben und das Ergebnis übernommen ist (`core/anzeige.values_gate`,
  `07`, 4.5); vorher steht „Werte ab …“. Die Website wendet diese Regel bisher nur im Ranking der Startseite an: Kacheln
  der Spieltag-Seite und Matchdetail zeigen auch für weit entfernte Spiele Werte und Auffälligkeiten (geprüft:
  Dortmund – Gladbach am 20.03.2027 zeigte am 21.11.2026 „auffällig · gering“). Ab 0.20 gilt die Regel auf allen Seiten:
  Scoreboard und „Zurück zum Spieltag“ bleiben, statt der Kennzahlen steht der „Werte ab“-Hinweis (Wortlaut DE/EN nach
  Freigabe Carsten), keine Bewertung, damit `noindex` (0.21).
  Wortlaut (Freigabe Carsten 19.11.2026): Vorspiel steht aus – „Werte ab Sa 05.12. – sobald beide Teams ihr vorheriges
  Ligaspiel gespielt haben.“ / „Values from Sat 5 Dec – once both teams have played their previous league match.“;
  Ergebnis noch nicht übernommen – „Werte folgen, sobald das Ergebnis vom 28.11. übernommen ist.“ / „Values will follow
  once the result from 28 Nov has been processed.“; Kachel – „Werte ab 5.12.“ / „Values from 5 Dec“.
  Regeln: vorheriges Spiel = zeitlich letztes angesetztes Ligaspiel vor dem Anpfiff (über die Saisongrenze; verschobene
  usw. zählen nicht, Nachholspiele schon); Aufsteiger ohne vorheriges Spiel: keine Sperre („Zu wenig Daten“); „Werte ab“ =
  Tag nach dem späteren ausstehenden Vorspiel (erwartetes Datum), „Ergebnis vom“ = späteres fehlendes Vorspiel.
  **Anpfiff ohne Werte:** Der Schnappschuss wartet, bis die Vorspiel-Ergebnisse übernommen sind, und rechnet dann mit den
  Daten vor dem Spiel (Vermerk „Werte nachträglich mit den Daten vor dem Spiel berechnet.“); bis dahin ab Anpfiff + 2 h
  ausgegraut mit „Gespielt“, ohne Werte; „Werte ab …“ erscheint nach dem Anpfiff nie.
  SEO/Social: Description „{Heimteam} – {Auswärtsteam} ({Liga}, {n}. Spieltag, {Datum}): Die Werte folgen, sobald beide
  Teams ihr vorheriges Ligaspiel gespielt haben.“ / „{Home} – {Away} ({League}, Matchday {n}, {date}): Values will follow
  once both teams have played their previous league match.“; og:title „{Heimteam} – {Auswärtsteam}“; kein SportsEvent.
- **Für 0.20 beschlossen (Carsten 19.11.2026): Archivseite und Glossar ohne eigenen Entwurf.** Archivseite aus der
  Spieltag-Seite abgeleitet (gleiche Kacheln mit Endstand, Kopf „<Liga> · Spieltag <nr> · Saison <saison>“, Pfeile zum
  vorherigen und nächsten Spieltag, keine Tabs, nicht in der Navigation). Glossar als Textseite im Stil der Methodik,
  verlinkt im Footer und von der Methodik. Texte DE/EN sowie SEO-Title und -Description liefert Carsten
  (Vorschlag von Claude für die Archivseite).
- **Für 0.21 beschlossen (Carsten 19.11.2026):**
  - **Zeitzone:** alle Anstosszeiten in mitteleuropäischer Zeit; Hinweis „Alle Anstoßzeiten in mitteleuropäischer Zeit
    (MEZ/MESZ).“ bzw. „All kick-off times in Central European Time (CET/CEST).“
  - **Archivseiten im Index:** indexierbar, wenn der Spieltag nach dem Livegang begonnen hat (Index-Fenster),
    unabhängig vom Status einzelner Spiele; davor begonnene Spieltage `noindex,follow`; nur indexierbare Archivseiten in
    der Sitemap; Spielseiten folgen ihrer eigenen Regel.
  - **Navigation:** verlinkt direkt auf `/de/spieltag/bundesliga/` bzw. `/en/matchday/bundesliga/`; die Weiterleitung
    `/de/spieltag/` (302) bleibt für eingetippte Adressen, ohne `hreflang` und Canonical.
  - **Index-Fenster kommender Spiele:** indexierbar, sobald das Spiel in einem Tab der Spieltag-Seite erscheint
    (anstehender Spieltag und Spieltage mit erstem Spiel bis heute + 6; Sonderspiele ab 7 Tagen vorher). *Seit 0.21.1 (Carsten 20.11.2026): heute + 5, Sonderspiele ab 5 Tagen vorher.*
  - **Strukturierte Daten:** `SportsEvent` (mit `startDate` inkl. Zeitzone) nur auf indexierbaren Spielseiten; auf
    `noindex`-Seiten nur `BreadcrumbList`. *Seit 0.24 entfällt `SportsEvent` (Entscheid Carsten 24.11.2026).*
- **Für 0.21 beschlossen (Carsten 19.11.2026): Spielseiten ohne Werte.** Eine Spielseite ist indexierbar und in der
  Sitemap, wenn sie im Index-Fenster liegt (Thema 4), keinen der fünf ausschliessenden Status hat und **mindestens eine
  bewertete Kennzahl** zeigt; sonst `noindex,follow` und nicht in der Sitemap (Seite bleibt erreichbar). Eine Funktion
  entscheidet für Seite und Sitemap. Teilweise vorläufige Spiele sind indexierbar; gespielte Spiele behalten den Stand
  ihres Schnappschusses; abgebrochene oder ausgesetzte Spiele sind `noindex`, bis sie als beendet Werte zeigen; ein
  verschobenes Spiel wird mit neuem Termin und Werten indexierbar (Adresse unverändert).
- **Release-Zuschnitt (Carsten 19.11.2026):** Der Umfang von 0.20 ist mit den bis hier beschlossenen Punkten abgeschlossen. Weitere Beschlüsse aus der Abstimmung mit dem Design- und Content-Chat kommen in **0.21** (zusammen mit E-Mail, Cookie-Banner, GA4, Search Console, robots.txt und Sitemap); danach 1.0 (Qualität und Livegang).
- **Für 0.20 beschlossen (Carsten 19.11.2026): Technik, SEO und Indexierung (Thema 4).**
  - Alle Texte, Zahlen und Zustände stehen im ausgelieferten HTML, auch alle Tabs der Spieltag-Seite und alle Ebenen
    und Tabellen der Methodik; JavaScript blendet nur ein und aus.
  - Bei Dateifehlern („Die Daten werden gerade geprüft.“) Status **503 mit `Retry-After`**; Impressum, Datenschutz,
    Kontakt und Cookie-Einstellungen bleiben mit 200 erreichbar.
  - **Indexierung:** kommende Spiele und Spiele ab dem Livegang (mit Schnappschuss) indexierbar und in der Sitemap;
    laufende Saison vor dem Livegang und Vorsaison 2025/26 erreichbar, aber `noindex` und nicht in der Sitemap;
    Saisons 2018/19–2024/25 zunächst ohne Seiten (404).
  - **Nichts verbauen für den Rückblick (Version 2/3):** Adressschema gilt für alle Saisons, einmal veröffentlichte
    Adressen werden nie gelöscht (sonst 301); Schnappschüsse ab 0.20 vor jedem Anpfiff und einmalig nachträglich für
    laufende Saison und Vorsaison (gekennzeichnet); Schnappschuss-Format mit Versionsnummer; Indexierung zentral in der
    Konfiguration (`index_ab`, `seiten_ab_saison`); Sitemap als Index mit Teilen je Liga und Saison; Archivseiten je
    Spieltag ohne Eintrag in der Navigation (nur von Spielseiten verlinkt); Ergebnis und Schnappschuss je Spiel als
    Grundlage der späteren Bilanz.
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
| 0.20 | Nur nötige Textanpassungen im heutigen Aussehen: Signalqualität stark/mittel/gering; Statusmodell (gespielt ab Anpfiff + 2 h, „Werte ab …“ auf Spieltag-Seite und Matchdetail, „Zu wenig Daten“); Werte gespielter Spiele aus dem Schnappschuss mit Hinweisen; Ranking ohne Nachrücken; Sonderspiele mit Nummer, neue Zählform; 48-Stunden-Grenze |
| 0.21 | **Neue Website** nach den Entwürfen P1: Deutsch und Englisch mit Adressen `/de/` und `/en/`, 301/302/404, Archiv je Spieltag; Methodik mit Excel-Download, Glossar, Kontakt (ohne Versand), Impressum, Datenschutz, Seite nicht gefunden; Index-Regeln, robots.txt, Sitemap, Title/Description/Open Graph/JSON-LD; Caching und 503; Tabs ohne JavaScript, Fokus, Kontraste, axe-core; Anzeigenamen je Sprache |
| 0.21.1 | Entwürfe 20.11. (Farben, Spielseite, Methodik-Karten, Handy) und Vorschau 5 Tage |
| 0.21.2 | Zweite Lieferung der Entwürfe 20.11.: Spielseite, Spieltag-Kopf, Startseite (SEO-Box, Ranking-Karte), Methodik-Schaltfläche |
| 0.22 | Startseite ohne Datenstand-Zeile; Anzeigenamen der 12 Aufsteiger und Athletic Bilbao; Glossar und Archivtexte freigegeben |
| 0.23 | Kontaktformular aktiv; Spielseite nach Entwurf 2k final (Karten A–D, Grenzwert im Detail), Endstand-Marke im Ranking, Legende je Reiter, Glossartexte zu den Läufen nach jedem Spiel freigegeben |
| später | 0.24 Cookie-Wahl, GA4; 1.0 Qualität und Livegang |
