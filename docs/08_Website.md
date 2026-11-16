# Soccer Intelligence – Öffentliche Website (Konzept und Protokoll)

**Version:** 1.0 · **Stand:** 16.11.2026 · **Umsetzung ab:** Version 0.17
**Grundlage:**
- Übergabe der Frontend-Entwürfe (Carsten, 16.11.2026, `Uebergabe_Frontend_Entwuerfe.md`)
- Entwurf „1d · Startseite mit Pausen A“ (`Main_P1`)
- Entscheidungen Carsten vom 16.11.2026: T1–T5, F1–F8, Datenstand, Zeitreise

**Wichtig:** Die Entwürfe für Spieltag (`Spieltag_P1`) und Matchdetail (`Spiel_P1`) kamen nicht an (vom Upload entfernt). Carsten hat den „Zu-Not-Weg“ gewählt: Spieltag und Matchdetail werden **nach der Übergabe-Datei** gebaut, im Stil der Startseite. Jede Stelle, an der ich dabei etwas annehmen musste, steht in **Abschnitt 9 (Annahmen)** und wird in der Vorschau geprüft.

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
| F1 | KPI 03 „Über 2,5 Tore“ vorerst mit der Abweichung wie im Rechenkern. **Offener Punkt:** Text und Vergleichswert (2,5-Tore-Marke statt Ligaschnitt) im Nachgang anpassen |
| F2 | „Nicht gewertet“ = „vorläufig“ nach Regelwerk (weniger als 10 Spiele, z. B. Aufsteiger) |
| F3 | Keine Sonderbehandlung „Werte ab“ auf der Spieltag-Seite: Es stehen die Werte, die gerade berechenbar sind |
| F4 | Nachhol- und vorgezogene Spiele wie im Entwurf: im Spieltag, in dessen Zeitraum sie fallen, sonst im ersten; mit Chip |
| F5 | Verschobene, abgesagte, abgebrochene, ausgesetzte und gewertete Spiele als graue Status-Kachel wie im Entwurf |
| F6 | Ranking der Startseite = Top Anomalien des Dashboards (Regelwerk 2.6) |
| F7 | Pausen und Datenstand wie im Dashboard (Pause über 14 Tage, Spieltag ab 14 Tagen vorher, Warnung bei Datenstand über 3 Tage) |
| F8 | Adressen `/spieltag/<liga>`, Standard Bundesliga; nur der anstehende Spieltag (bei englischer Woche Tabs), kein Blättern; gespielte Spiele verlinken zum Matchdetail, verschobene nicht. Liganame „La Liga“ mit Abstand |
| D1 | **„Aktueller Datenstand“** (Startseite, Spieltag) und **„Stand“** (Fusszeile) = Datum bzw. Datum und Uhrzeit des **letzten erfolgreichen Importlaufs** über die API |
| Z1 | **Zeitreise** nur in der Vorschau: `?datum=…` auf jeder Seite (Abschnitt 6) |

## 3. Technik

| Teil | Umsetzung |
|---|---|
| Programmteil | `app/website/` im bestehenden Projekt (gleiche Datenbank, gleicher Rechenkern) |
| Seiten | HTML-Vorlagen (Jinja2) + eine CSS-Datei mit den Farben und Massen des Entwurfs; wenig JavaScript (nur Tabs), alles funktioniert auch ohne |
| Texte | Sprachdatei `app/website/texte/de.json` mit Schlüsseln (Übergabe 9.1); Mehrzahl als eigene Varianten; Fallback Deutsch |
| Formate | `app/website/format.py`: Datum „Sa 21.11.“, Prozent „+47,36 %“ mit echtem Minus „−“, Ergebnis „2 : 1“; je Sprache eine Tabelle (jetzt nur `de`) |
| Schriften | Outfit und Inter als variable WOFF2-Dateien (SIL Open Font License 1.1, Lizenzdateien liegen bei), nur lateinische Zeichen; erweiterte Zeichen lädt der Browser nur bei Bedarf |
| Daten | `app/website/daten.py` lädt Datenbank, Spielplan, Schwellen und den Importstand, mit Zwischenspeicher je Dateistand |
| Datenschnittstelle | Je Seite ein Datensatz mit **Codes statt Texten** (Abschnitt 5), als JSON abrufbar (`/vorschau/daten/…`). Daraus entsteht beim Livegang der statische Export |
| Vorschau | Container `soccer-vorschau` (gleiches Programm-Abbild wie das Dashboard), kleiner Python-Webserver, erzeugt die Seiten bei jedem Aufruf neu (nötig für die Zeitreise). Nur lesend auf `data/` und `import/` |
| Zugang | Traefik-Router `Host(soccer-intelligence.com) && PathPrefix(/vorschau)` mit Passwortabfrage (BasicAuth, Hash in `.env` als `SOCCER_VORSCHAU_AUTH`), Anfragebremse, „noindex“ |
| Livegang (später) | statischer Export nach `site/`, ausgeliefert von nginx (wie der Platzhalter); Erzeugen im Container `soccer-import` nach jeder Übernahme und alle 15 Minuten |

## 4. Seiten und Adressen

| Adresse (Vorschau) | Seite | Version |
|---|---|---|
| `/vorschau/` | Startseite (bis 0.19: Weiterleitung auf den Spieltag) | 0.19 |
| `/vorschau/spieltag/<liga>` | Spieltag; `<liga>` = `bundesliga`, `la-liga`, `premier-league`, `serie-a` | 0.17 |
| `/vorschau/spiel/<id>` | Matchdetail; `<id>` = Spiel-ID von API-Football | 0.18 |
| `/vorschau/methodik`, `/impressum`, `/datenschutz` | Hinweis „folgt später“ | später |
| `/vorschau/daten/spieltag/<liga>.json` | Datensatz der Seite (Codes) | 0.17 |

Reihenfolge der Ligen auf der Website (Entwurf): Bundesliga, La Liga, Premier League, Serie A.

## 5. Seite Spieltag (Übergabe, Abschnitt 6)

### 5.1 Aufbau
1. Kopf: Logo „Soccer Intelligence“, Navigation Spieltag · Methodik · Impressum.
2. Link „Startseite“, H1 „Alle Spiele im Überblick“, Text „Wähle deine Liga und sieh, bei welchen Partien die Zahlen aus der Reihe fallen.“
3. Liga-Auswahl: vier Kacheln, je „10. Spieltag“ (anstehender Spieltag); die gewählte in der Akzentfarbe. Darunter „Aktueller Datenstand: Mo 16.11.2026“ (D1).
4. Titel = Liganame, Zusammenfassung „10. Spieltag · 20.11. – 22.11.2026 · 9 Partien · 2 mit Auffälligkeit · plus 1 Nachholspiel“.
5. Legende Stark · Leicht · Ohne Auffälligkeit, „Wie lese ich das?“ (aufklappbar, Texte Übergabe 6.3).
6. Bei englischer Woche Tabs „10. Spieltag · ab 20.11.“ / „11. Spieltag · ab 24.11.“ (Standard: der frühere).
7. Liste der Partien als Kacheln, Fusszeile.

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
| Stark (`stark`) | mindestens eine nicht vorläufige Kennzahl mit starker Abweichung |
| Leicht (`leicht`) | sonst mindestens eine mit leichter Abweichung |
| Ohne Auffälligkeit (`ohne`) | sonst |

Stufen kommen aus `schwellen.toml` über den Rechenkern (Übergabe 4.1, keine festen 20/35). Vorläufige Kennzahlen zählen für die Stufe nicht.

### 5.4 Sortierung und Zählung
- Stark (nach grösster Abweichung) → Leicht (nach grösster Abweichung) → Ohne → Nicht gewertet → Status → Gespielt; sonst nach Anstoss.
- Nachhol- und vorgezogene Spiele stehen danach, am Ende der Liste (Übergabe 6.4), unter sich gleich sortiert.
- „Partien“ = Spiele des Spieltags ohne Sonderspiele; „mit Auffälligkeit“ = Stark + Leicht, Sonderspiele eingeschlossen; „plus n Nachholspiel(e)“ bzw. „plus n vorgezogene(s) Spiel(e)“.

### 5.5 Kachel
Heim, „gegen“, Gast, Termin („Sa 14.11. · 15:30“, „Sa 14.11. · Zeit offen“, „Wochenende 06./07.02. · Termin offen“, bei Status „Termin offen“ bzw. Datum). Chips rechts, runder Pfeil. Farben und Ränder nach Übergabe 6.2.

### 5.6 Datensatz (Codes, Auszug)
```json
{"seite": "spieltag", "liga": "bundesliga", "jetzt": "2026-11-16T14:00", "stand": "2026-11-16T04:05", "veraltet": false,
 "zustand": "liste", "pause": null,
 "ligen": [{"liga": "bundesliga", "spieltag": 10, "pause": null}],
 "tabs": [{"saison": "2026/2027", "spieltag": 10, "von": "2026-11-20", "bis": "2026-11-22", "partien": 9,
           "auffaellig": 2, "sonderspiele": {"nachholspiel": 1, "vorgezogen": 0},
           "spiele": [{"id": 1388512, "heim": "Bayern München", "gast": "1. FC Köln", "datum": "2026-11-20",
                       "anstoss": "20:30", "termin": "bestaetigt", "art": "stark", "status": null,
                       "ergebnis": null, "sonderspiel": null, "link": true,
                       "staerkste": {"kpi": "kpi03", "abweichung": 44.0}}]}]}
```

## 6. Zeitreise (nur Vorschau)

- `?datum=2026-10-03` oder `?datum=2026-10-03T16:00` auf jeder Seite der Vorschau; ohne Uhrzeit gilt 08:00. Alle Links tragen das Datum weiter. Eine Leiste oben zeigt den Zeitpunkt und erlaubt die Eingabe.
- Annahmen (Carsten, 16.11.2026): Der Import ist an diesem Tag um 04:00 gelaufen (kein „veraltet“, Datenstand = dieser Tag, vor 04:00 der Vortag). Ergebnisse gelten nur für Spiele **vor** dem Importtag; die KPI-Werte werden mit genau diesem Datenstand berechnet.
- Grenzen: Spielplan = der heutige (spätere Verschiebungen sind schon eingetragen). Zeitraum = laufende Saison und Vorsaison.
- Auf der öffentlichen Seite gibt es keine Zeitreise.

## 7. Matchdetail und Startseite

Folgen in 0.18 und 0.19, Regeln aus der Übergabe (Abschnitte 5 und 7) mit den Entscheidungen F1, F2, F6, F7, F8. Werden vor der Umsetzung hier ergänzt.

## 8. Testfälle (Version 0.17)

| Nr. | Situation | Erwartet |
|---|---|---|
| W1 | Formate | „Sa 21.11.“, „+47,36 %“, „−22,07 %“ (U+2212), „0,00 %“ ohne Vorzeichen, „2 : 1“, Zeitraum über den Jahreswechsel |
| W2 | Einstufung | Status vor gespielt vor nicht gewertet vor Stufe; vorläufige Kennzahlen zählen nicht; stark vor leicht |
| W3 | Sortierung | Stark → Leicht → Ohne → Nicht gewertet → Status → Gespielt; innerhalb Stark/Leicht nach Betrag |
| W4 | Zählung | Partien ohne Sonderspiele; „mit Auffälligkeit“ mit Sonderspielen; „keine mit Auffälligkeit“ |
| W5 | Nachholspiel | im Tab, in dessen Zeitraum es fällt, sonst im ersten; am Ende der Liste; Chip |
| W6 | Englische Woche | zwei Tabs mit eigener Zählung; Standard der frühere |
| W7 | Pausen | Spielpause, Winterpause, Sommerpause, Saisonstart als Karte statt Liste; ab 14 Tagen Liste |
| W8 | Datenstand | Warnbox ab 4 Tagen, Liste bleibt; Datum = letzter erfolgreicher Lauf |
| W9 | Zeitreise | Datum aus der Adresse, Ergebnisse und Werte nur vor dem Importtag, Links tragen das Datum |
| W10 | Texte | jeder Schlüssel der Vorlagen in `de.json`; ß-Schreibweise; alle Texte maskiert |
| W11 | Vorschau-Dienst | Adressen, Weiterleitung, 404, ungültiges Datum, Dateien nur aus dem eigenen Ordner, Kopfzeilen |
| W12 | Container | Router nur unter `/vorschau`, mit Passwortabfrage, noindex, Anfragebremse; nur lesend |
| W13 | Echte Daten | alle vier Ligen an mehreren Tagen (wie A27) ohne Fehler |

## 9. Annahmen (bitte in der Vorschau prüfen)

| Nr. | Annahme | Grund |
|---|---|---|
| A1 | Spieltag-Kachel und Liste im Stil der Startseite (Karten, Radius, Schrift), Masse aus der Übergabe 6.2 | Entwurf `Spieltag_P1` nicht angekommen |
| A2 | Nachhol- und vorgezogene Spiele stehen als eigene Gruppe am Ende der Liste | Übergabe 6.4 „am Ende der Liste“ zusammen mit 6.3 „Sortierung nach Stufe“ |
| A3 | Status „gewertet“ (am grünen Tisch) bekommt den Chip „Am grünen Tisch gewertet“, damit er nicht mit „Nicht gewertet“ verwechselt wird | Begriffe sonst gleich |
| A4 | „Ergebnis folgt“ als Chip, solange das Ergebnis nach dem Anstoss noch nicht übernommen ist | Übergabe nennt nur „Ergebnis“ |
| A5 | Liga-Kachel zeigt in einer Pause den Pausennamen statt der Spieltagsnummer | Übergabe nennt nur „24. Spieltag“ |
| A6 | Bei veraltetem Datenstand ohne anstehenden Spieltag: Warnbox und Karte „Nächster Spieltag am …“ ohne Pausennamen | S9: keine Pausenhinweise bei veraltetem Stand |
| A7 | Die Pausen-Karte der Spieltag-Seite hat keinen Tage-Zähler (nur die Startseite) | Übergabe 6.4 |
| A8 | Navigation zu Methodik und Impressum zeigt bis zur Umsetzung „Diese Seite folgt später.“ | Seiten noch nicht im Umfang |
| A9 | Vorschau-Leiste oben (Zeitpunkt, Eingabe) nur in der Vorschau, nicht Teil der Website | wie die Prototyp-Leiste des Entwurfs |

## 10. Offene Punkte

- F1: KPI 03 Text und Vergleichswert (2,5-Tore-Marke) anpassen.
- Startseite: maximale Anzahl im Ranking (vorerst 4, wie Dashboard).
- Methodik-Seite: eine oder zwei (Übergabe 10, Punkt 9).
- Livegang: Impressum, Datenschutz, rechtliche Prüfung „keine Wettberatung“, statischer Export und nginx, Weiterleitung `/` statt Platzhalter.
- Mehrsprachigkeit (EN, IT, ES): Übersetzungen, Namenstabellen, Adressen je Sprache (später).

## 11. Versionen

| Version | Inhalt |
|---|---|
| 0.17 | Grundgerüst (Design, Schriften, Texte, Formate, Daten, Vorschau-Container mit Passwort, Zeitreise) und Seite **Spieltag** |
| 0.18 | Seite **Matchdetail** |
| 0.19 | **Startseite** |
| später | Methodik, Impressum, Datenschutz, Livegang |
