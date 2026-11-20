# Soccer Intelligence – Technisches Setup und Betrieb

**Stand:** 20.11.2026 · **Verantwortlich:** Carsten Thiele · **Mitwirkende:** ChatGPT (Server-Setup, Review), Claude (Daten, Architektur, Code)

Diese Datei ist die **einzige Stelle** für Projektstand, Versionen, Server, Abläufe und Architektur. Fachliche Regeln stehen in `02`–`06`, Änderungen im `CHANGELOG.md`, das aktuelle Release in `RELEASE.md`.

---

## 0. Stand und Versionen

**In Betrieb:** Version 0.21.1 (seit 20.11.2026) – Dashboard mit vier Ligen (Bundesliga, Premier League, Serie A, LaLiga), KPI 01–09 mit Auffälligkeit und Signalqualität stark / mittel / gering (23 Schwellen), Top Anomalien, Datenqualität, Sensitivitätsanalyse, Datenimport über API-Football mit Schnappschuss je Spiel; Vorschau weiterer Spieltage ab heute + 5; Website-Vorschau unter `/vorschau` nach den Entwürfen vom 20.11. in Deutsch und Englisch (Archiv je Spieltag, Methodik mit Excel-Download, Glossar, Kontakt ohne Versand, Impressum, Datenschutz), vorbereitet für Suchmaschinen (noch nichts im Index, `index_ab` leer).

**Als Nächstes:** Version 0.21.2 einspielen (zweite Lieferung der Entwürfe vom 20.11.). Offen beim Design-Chat: Briefings nennen noch 7 statt 5 Tage Vorschau; Level-3-Chip DE („Für Statistik-Fans“ oder „Alles im Detail“), englischer Spieltitel („–“ oder „vs“, umgesetzt „vs“), Position des Glossar-Links (umgesetzt nach Methodik). Danach Version 0.22 – vorher Spezifikation E-Mail-Alarme und Entscheidungen zum Abfrageplan (`06`, 10.2: Läufe bei Anpfiff + 2¼ h); Freigaben aus `RELEASE.md` 0.21 (Glossar, Archivtexte, Namen der 12 Aufsteiger, „Auffällige Spiele je Spieltag“).

**Als Nächstes – Releaseplan bis zum Livegang (Freigabe Carsten 19.11.2026):**

| Release | Schwerpunkt | Inhalt (Details: `08_Website.md`, Abschnitt 10; Briefings des Design-Chats) | Voraussetzungen |
|---|---|---|---|
| **0.20 Fundament** | Rechenlogik, Datenregeln, Dashboard | Umbenennung Signalqualität stark/mittel/gering; Schnappschuss je Spiel (stündlich, versioniert, nachträglich für laufende Saison und Vorsaison); Statusmodell (Zu wenig Daten, AWD-Absicherung, Gespielt nach Anpfiff + 2 h, kein Nachrücken in den Top Anomalien, „Werte ab …“ auf allen Seiten, Sonderspiel-Nummer und Zählform); 48-Stunden-Grenze; Dashboard angepasst | keine |
| **0.21 Neue Website** | Templates, Sprachen, Adressen, SEO | Templates T1–T7, T9–T11 nach den Entwürfen; DE/EN mit Anzeigenamen je Sprache; Adressen `/de/`, `/en/`, 301, Canonical, hreflang, 404, 503; Indexierungsregeln, robots.txt, Sitemap; Titles/Descriptions/Social/JSON-LD; Tabs ohne JS, Fokus, Kontraste, axe-core; Caching; Excel-Download Methodik | Texte Archiv/Glossar, offene Glossar-Vorschläge |
| **0.22 Betrieb & Einwilligung** | E-Mail, Kontakt, Cookies, Analytics | **Spezifikation E-Mail-Alarme (offen, vor Beginn von 0.22)**; E-Mail über Hostinger-Postfach; Kontaktformular-Versand; Alarme (API, Import, Freigabe, Schnappschuss); Cookie-Hinweis und Cookie-Einstellungen; Tag Manager und GA4 nach Zustimmung; Search Console | Postfach, GA4-/GTM-IDs |
| **1.0 Qualität & Livegang** | Prüfung, Korrekturen, Umschalten | Qualitätschecks (Compound Engineering, Web Quality Skills, Lighthouse, axe mit echten Daten); Befunde beheben; Domain umschalten, `/` → `/de/`, Vorschau-Passwort weg, `index_ab` setzen, Sitemap einreichen | Impressum mit Projektadresse, juristische Prüfung DE/EN, Nutzungsrechte API-Football, Hosting-Angabe |

Danach: **Prognose gegen Ergebnis** auf der Spielseite (je Kennzahl Wert vor dem Spiel aus dem Schnappschuss und tatsächlicher Wert, „bestätigt / nicht bestätigt“; Wunsch Carsten 20.11.2026, nach Abschluss der Releases bis 1.0) · Rückblick für Fans (Version 2/3) · E-Mail-Benachrichtigung über den Alarm hinaus · Phase 2: Wettquoten, Verletzungen, Tabellenstände · Phase 3: primäre Auffälligkeit je Spiel, neue KPIs · Rundum-Prüfung des Codes.

| Version | Etappe | Inhalt | Eingespielt | Git | Tests |
|---|---|---|---|---|---|
| 0.21.2 | Entwürfe 20.11., zweite Lieferung | Spielseite: grüne Schaltfläche „Alle Spiele des Spieltags“, Textlink zur Methodik, ohne Zeitzonen-Hinweis; Spieltag-Kopf ohne „Aktueller Datenstand“ und niedriger; Startseite: SEO-Box eigener Block, Chip neben der Kennzahl; Methodik-Schaltfläche mit Umbruch nur mobil | – | – | – |
| 0.21.1 | Entwürfe 20.11. | Kräftigere Grüntöne, Spielseite ohne „Weitere Spiele“, Methodik-Einstieg als Karten, mobil einzeilige Navigation und Tabellen ohne Scrollbalken; Vorschau weiterer Spieltage heute + 5 statt + 6; Entwurf Abfrageplan (`06`, 10.2) | 20.11.2026 | `273b969` | 697 |
| 0.21 | Neue Website | Website-Vorschau nach den Entwürfen P1, Deutsch/Englisch, Adressen `/de/` `/en/` mit 301/302/404, Archiv je Spieltag, Methodik mit Excel-Download, Glossar, Kontakt, Impressum, Datenschutz, 404; Index-Regeln, Sitemap, robots.txt, JSON-LD; Caching, 503; axe-core ohne Befund; Anzeigenamen je Sprache | 20.11.2026 | `006a150` | 696 |
| 0.20 | Fundament | Signalqualität stark/mittel/gering; Schnappschuss je Spiel; Statusmodell (gespielt ab Anpfiff + 2 h, kein Nachrücken, „Werte ab“ auf allen Seiten, Zu wenig Daten, AWD-Absicherung, Sonderspiel-Nummer, Zählform); 48-Stunden-Grenze; ein Importstand für Dashboard und Website | 20.11.2026 | `10fa028` | 645 |
| 0.19.1 | Nach Abnahme 0.19 | Texte Top Anomalien und Sensitivitätsanalyse, Reiter getauscht, Schwellen je Liga sichtbar, KPI 03 bei 0,00 %, Schusssumme als Hinweis, Cache-Versionsnummer der Website, Bereinigungen B1, B3–B6, Gegenrechnung Prognosewert | 19.11.2026 | `537b4a4` | 627 |
| 0.19 | Prognosewert | Auffälligkeit und Prognosewert statt leicht/stark: Schwellen je Liga, KPI und Richtung (23), Top Anomalien mit Liga-Mix, Sensitivitätsanalyse mit Prognosewert, Erklärfeld und Schwellenvorschlag | 18.11.2026 | `cd45076` | 619 |
| 0.18 | Website: drei Seiten | Startseite (1d), Spieltag (3d) und Matchdetail je Paarung (2i) genau nach den Entwürfen; Entscheidungen Q1–Q7; Foto nur auf dem Server (`website-bilder/`); Vorladen beim Start | 17.11.2026 | `fbdd5d9` | 617 |
| 0.17 | Website: Spieltag | Öffentliche Website als Vorschau unter `/vorschau` (Container `soccer-vorschau`, Passwortabfrage): Design-Grundlagen, Schriften selbst gehostet, Sprachdatei mit ß, Seite Spieltag mit Tabs, Kacheln, Pausen, Datenstand, Zeitreise | 17.11.2026 | `49c2056` | 600 |
| 0.16 | Kommende Spieltage | Ligaseiten mit Abschnitten je Spieltag, Spalte Datum, gespielte Spiele grau, „Werte ab“, Pausen-Boxen, Datenstand, Pfeile vorwärts 2; Top Anomalien je Liga der nächste Block vor dem Anpfiff; Vorschau im Reiter Datenimport/API | 16.11.2026 | `5b1e949` | 563 |
| 0.15.2 | Anmeldemaske | Anmeldemaske statt Browser-Passwortabfrage (Benutzername, Passwort-Hash in .env, 12 h, Sperre nach Fehlversuchen, Anfragebremse), Einspielen mit schnellen Tests; Nachtrag: Seitentest mit Anmeldung | 16.11.2026 | `47d54ca` | 479 |
| 0.15.1 | Code-Prüfung | Übergabe-Protokoll und Prüfsummen bei der Übernahme, eindeutige Backups, negative Werte, Vorladen im Hintergrund, schneller Testlauf, Bereinigungsliste | 16.11.2026 | `88a3066` | 470 |
| 0.15 | Datenimport nach Reviews | Spielplan v2.1 (Status nur aus der API, Nachholspiele mit KPIs, Termin, Vorsaison), Ergebnis-Import R1–R9 (Korrekturfenster, Entscheide, Endstand gegen Tor-Ereignisse, Plausibilität, Zuordnungsdatei), täglich, Reiter Blöcke A/B | 16.11.2026 | `a4367eb` | 459 |
| 0.14.1 | Datenimport, Nachtrag | Teamnamen mit ü und Akzenten (10 Teams), Einspiel-Skript macht nach Abbruch weiter, Statustext | 15.11.2026 | `1408c50` | 442 |
| 0.14 | Datenimport | Datenimport über API-Football: Container soccer-import, Reiter Datenimport/API mit Freigabe, Spielplan aus der API, Teamnamen der API, Status „abgebrochen“ | 15.11.2026 | `8260056` | 441 |
| 0.13 | Neue Schwellen | Gültige Schwellen positiv/negativ getrennt, KPI 03 je Liga; Sensitivitätsanalyse nach Entwurf C (vier Zeilen je KPI, Bewertung auch für stark) | 14.11.2026 | `89128e5` | 428 |
| 0.12 | Sensitivitätsanalyse | Spielwiese ersetzt: vier Schwellen je KPI, Häufigkeit mit Spieltagsabdeckung, Ergebnisqualität gegen Grundquote mit Wilson-Spanne und Empfehlung | 12.11.2026 | `1482bc3` | 398 |
| 0.11 | Neue Datenbank | Datenbank 2018/19–2026/27, Referenzsaison, neue Saisonauswahl, Warnung „Saison fehlt“ | 10.11.2026 | `034e57a` | 376 |
| 0.10.1 | GitHub | GitHub als einzige Quelle: einspielen.sh github, automatische Tests, robuster Rückweg | 10.11.2026 | `20275e9` | 350 |
| 0.10.1 | Skript | Einspiel-Skript `tools/einspielen.sh`, Rückweg `tools/zurueck.sh` | 09.11.2026 | `0dafea3` | 348 |
| 0.10.1 | Doku | Dokumentation zusammengeführt (nur Doku, kein Code) | 08.11.2026 | `0d4d856` | – |
| 0.10.1 | I.1 Nachtrag | Simulation: Info-Fenster, Schwellen in der Ergebnisqualität, neue Saisonauswahl | 08.11.2026 | `9684edb` | 345 |
| 0.10 | I.1 | Simulation – Spielwiese: Häufigkeit und Ergebnisqualität je KPI mit eigenen Schwellen (Regelwerk 11) | 08.11.2026 | `dbd90c5` | 345 |
| 0.9.2 | H.2 | Stabilität (zweite Code-Prüfung, S1–S6) | 08.11.2026 | `291eeac` | 319 |
| 0.9.1 | H.1 | Aufräumen und Tempo (erste Code-Prüfung) | 08.11.2026 | `b5a7ea8` | 287 |
| 0.9 | H | KPI 05–09, zwei Nachkommastellen, Top Anomalien über KPI 02–09, Schwellen-Datei | 08.11.2026 | `51e595b` | 260 |
| 0.8 | F | Vier Ligen (Serie A, LaLiga), unabhängige Gegenrechnung | 07.11.2026 | `cc00dd9` | 171 |
| 0.7 | E | Dashboard unter `/dashboard` mit Passwort, Platzhalter unter `/` | 31.10.2026 | `64a684b` | 152 |
| 0.6 | D | Top Anomalien | 31.10.2026 | `1a1c527` | 145 |
| – | C, Anpassungen | Spieltag-Pfeile, Navigation, Referenz-Datenbank für Tests | 31.10.2026 | `4c3be5c` | 140 |
| – | C | KPI 01–04, Häufigkeit der Anomalien | 31.10.2026 | `8cb5f0f` | 126 |
| – | B | Spielplan, aktueller Spieltag, Datenqualität | 31.10.2026 | `ff4fbe8` | 72 |
| – | A | Datenbank einlesen und prüfen (Schritt 1) | 31.10.2026 | `ffec276` | 26 |

- **Rückweg** zu einer Version: Abschnitt 6.1.
- **Prüfprotokolle** grösserer Etappen: `docs/tests/pruefprotokoll_*.md`.
- **Frühere Anleitungen** (`ANLEITUNG_*.md`): seit 09.11.2026 durch `RELEASE.md` und Abschnitt 6.1 ersetzt. Sie bleiben im Git-Verlauf erhalten.
- **Daten:** Datenbank SHA-256 `3a258961…` (2018/19–2026/27, bereinigt mit API-Football und football-data.co.uk, aktiv seit 15.11.2026; vorher `451348b6…`), `02_Datenbasis.md` Abschnitt 4e; Prüfprotokolle `docs/tests/pruefprotokoll_api.md` und `pruefprotokoll_datenbank_2018-2027.md`. Spielplan mit vier Blättern (`04_Spielplan.md`).

---

## 1. Projektziel

Fussball-Analyseplattform auf Basis historischer Spieldaten (Bundesliga, Premier League, Serie A, LaLiga). Auffälligkeiten („Anomalien“) anstehender Partien werden erkannt und angezeigt. Lernprojekt, nicht kommerziell.

Ausbaustufen:
1. Excel-Datenbank, von Carsten gepflegt.
2. Internes Dashboard mit allen anstehenden Partien und Analysen.
3. Öffentliche Website (Mobile First), als eigenes Projekt, das einen Datenexport des Rechenkerns anzeigt.

---

## 2. Grundsatzentscheidungen

| Datum | Entscheidung |
|---|---|
| 18.11.2026 | **Begriff „Prognosewert“ wird „Signalqualität“** (Carsten): Stufen **stark / mittel / gering** statt hoch / mittel / gering, im Dashboard und auf der Website, in Code, Schwellendatei, Doku und Designs. Umgesetzt in 0.20 (Vollvergleich: Werte gleich, nur „hoch“ → „stark“). Achtung: „stark“ meinte bis 0.18 die Grösse der Abweichung (leicht/stark); ab der Umsetzung nur noch die Signalqualität. |
| 18.11.2026 | **Nach Abnahme 0.19 (Carsten):** Text unter den Top Anomalien mit Zwischentiteln (Wortlaut Carsten mit zwei Präzisierungen), Reiter Sensitivitätsanalyse vor Datenqualität, Erklärtexte der Sensitivitätsanalyse überarbeitet, Schwellen je Liga unter dem Feld, Zeilen ohne Schwelle bleiben leer (keine Vorbelegung), KPI 03 bei genau 0,00 % mit eigenem Satz, Aufsteiger-Anzeige bestätigt, „Schüsse < aufs Tor + daneben“ nur noch Hinweis, Cache-Versionsnummer der Website, Bereinigungen B1, B3–B6 in 0.19.1. |
| 18.11.2026 | **Auffälligkeit und Prognosewert** statt leicht/stark (Carsten, nach Gegenprüfung durch ChatGPT und Prüfrunde): Schwellen je Liga, KPI und Richtung nach fester Regel aus der Sensitivitätsanalyse (Funktioniert mit Rand > +2 Pp., stabil in zwei Dritteln der Saisons, Prognosewert hoch/mittel/gering), keine Handanpassung, Top Anomalien nach Prognosewert mit Liga-Mix, Neuberechnung einmal pro Saison mit Freigabe über GitHub. Details: KPI-Regelwerk 2.2, 2.6, 11; `docs/tests/pruefprotokoll_prognosewert.md`. |
| 09.11.2026 | **GitHub ist die einzige Quelle** (Carsten): Änderungen entstehen nur noch auf GitHub (Claude Code mit dem Repository verbunden, Pull Request mit automatischen Tests, Freigabe durch Carsten mit „Squash and merge“). Der Server holt mit `tools/einspielen.sh github` ab und ändert selbst nichts mehr. Das Paket `release.zip` bleibt als Ersatz (Abschnitt 6.1). |
| 08.11.2026 | **Neue KPIs:** 5 Frontend-KPIs (05 Ecken, 06 Tore 1. HZ, 07 Tore 2. HZ, 08 Beide Teams treffen, 09 Schüsse aufs Tor) und 4 Simulations-KPIs nur im Backend (10/11 Angriff gegen Abwehr HZ 1/2, 12 Offensivdruck, 13 Abschluss-Effizienz). Schwellen pro Liga und KPI einstellbar (Datei `app/config/schwellen.toml`, Standard ±20/±35 %, kein eigener Tab). Kompakte Liga-Tabelle mit Details per Aufklappen. Reihenfolge: Spezifikation + Testfälle → Etappe H (KPI 05–09) → Etappe I (Simulations-Tab). Details: KPI-Regelwerk v2.0, CHANGELOG. |
| 08.11.2026 | **Etappe H freigegeben (Carsten):** Testfälle KPI 05–09 bestätigt; **alle KPIs mit zwei Nachkommastellen** (auch Abweichung, Einstufung nach gerundetem Wert); **Top Anomalien über KPI 02–09** (bisherige Rangfolge, Gewichtung später); kompaktere Liga-Tabelle mit Aufklappen, Design-Vorschlag vor der Umsetzung. Danach Etappe I: interner Tab zur Schwellen-Analyse je KPI und Liga, Feintuning, Gewichtung der Top Anomalien. Ablauf: md-Dateien → Backup → Design-Vorschlag → Programmieren und Einspielen. |
| 07.11.2026 | **Spieltage mit verlegten Spielen:** Die bestehende Logik für den aktuellen Spieltag bleibt. Spiele, die mehr als 3 Tage ausserhalb des Hauptzeitraums ihres Spieltags liegen, werden im Spielplan als `verschoben` gepflegt (keine KPIs, keine Top Anomalie). Keine Pflege auf Tagesebene, keine Mehrheitsregel. Grundlage: Auswertung 2022/23–2025/26, betroffen unter 2 % der Spiele (`04_Spielplan.md`, Abschnitt 6). |
| 07.11.2026 | Blatt für Italien heisst in Datenbank und Spielplan **`Serie A`** (bisher `Seria A`); der Code wird in Etappe F angepasst. Blattnamen ohne Leerzeichen: `LaLiga`. |
| 06.11.2026 | **Erweiterung auf vier Ligen** (Serie A, LaLiga) als nächster Schritt (Etappe F), vor der Datenlieferung (Etappe G). Reihenfolge: Daten auf den Server → Sicherung in GitHub → Etappe F → Etappe G → neue KPIs → öffentliche Website. |
| 02.11.2026 | **Reihenfolge nach Phase 1:** zuerst die Datenquelle klären, die neuen KPIs können parallel laufen, danach die öffentliche Website. Grund: Teamnamen, IDs, Nutzungsrechte und Spielplan-Pflege beeinflussen die Website. *(Präzisiert am 06.11.2026, siehe oben.)* |
| 31.10.2026 | **Die md-Dateien in `docs/` sind die einzige massgebliche Quelle.** Die Word-Dokumente (`word/`) sind Archiv und werden nicht mehr gepflegt. Änderungen nur noch in den md-Dateien, mit Eintrag im CHANGELOG. |
| 31.10.2026 | **Etappe E:** öffentliche Platzhalterseite unter `/` (Variante b), ein gemeinsamer Zugang zum Dashboard (Benutzername und Passwort nur in `.env`), Hinweis `noindex` für Suchmaschinen. |
| 31.10.2026 | Spieltag-Pfeile in den Liga-Bereichen (je Liga, nicht in die Zukunft, Auswahl in der Adresse); Top Anomalien immer aktueller Spieltag. |
| 30.10.2026 | **Dashboard mit Passwortschutz** unter `https://soccer-intelligence.com/dashboard`. Schutz serverseitig über Traefik für alle Adressen unter `/dashboard`. Zugangsdaten nur als Hash in einer Konfigurationsdatei auf dem Server. Ersetzt die Entscheidung vom 25.10.2026. |
| 30.10.2026 | Startseite `https://soccer-intelligence.com` zeigt bis zur öffentlichen Website weiterhin die **Platzhalterseite** (öffentlich). |
| 30.10.2026 | Bereiche des Dashboards: `/dashboard` = Top Anomalien, `/dashboard/bundesliga`, `/dashboard/premier-league`. Jede weitere aktivierte Liga erhält automatisch einen eigenen Bereich nach demselben Muster (z. B. `/dashboard/laliga`). |
| 30.10.2026 | Das Dashboard bleibt ein reines Ansichts-Werkzeug: keine Funktionen zum Importieren, Bearbeiten oder Verwalten in der App. |
| 30.10.2026 | **Keine Vereinslogos**, weder im Dashboard noch auf der öffentlichen Website (rechtliche Gründe). |
| 30.10.2026 | **Ein KPI-Regelwerk:** gültig ist nur `docs/03_KPI_Regelwerk.md`. `03_KPI_Grundregeln.md` und `docs/kpis/` sind gelöscht. ~~Massgebliche Quelle bleibt das Word-Dokument „Definition der Dashboard-KPIs“.~~ (ersetzt am 31.10.2026, siehe oben) |
| 30.10.2026 | Im Text „Keine Anomalie“ (KPI 02 und 04) steht die Abweichung immer mit Vorzeichen, bei 0,0 % ohne. |
| 28.10.2026 | Ligareferenz über die Spalte `Gameday` (letzte 20 Spieltage). Spalte in der Datenbank ergänzt. |
| 25.10.2026 | Daten werden **nur über die Datei auf dem Server** geändert, nie über die App. |
| 25.10.2026 | **Einzige gültige Datenquelle:** `data/Database-Soccer-Intelligence.xlsx` |
| 25.10.2026 | Spielplan (anstehende Partien) kommt als **eigene Datei** `data/Spielplan.xlsx`, getrennt von den historischen Daten. Aufbau: `04_Spielplan.md` (Datum von / Datum bis, beschlossen 30.10.2026). |
| 25.10.2026 | Start mit abgeschlossenen Saisons 2020/21–2025/26. Die laufende Saison 2026/27 wird nach dem Prototyp ergänzt. |
| 25.10.2026 | Keine externe Fussball-API vorerst. *(Stand 02.11.2026: Eine regelmässige Datenlieferung wird geprüft, siehe `06_Datenlieferung.md`. Noch keine Entscheidung.)* |
| 25.10.2026 | KPIs werden von Carsten definiert, bevor Analysen gebaut werden. Keine KPIs ohne Abstimmung. |

---

## 3. Server

| | |
|---|---|
| Anbieter / Host | Hostinger VPS, `srv1774622.hstgr.cloud` |
| IP | 72.60.132.157 |
| Betriebssystem | Ubuntu 24.04.4 LTS |
| Ressourcen | 48 GB Speicher (16 % belegt), 3,8 GB RAM |
| Domain | https://soccer-intelligence.com |

### Container auf dem Server

| Container | Zweck | Gehört zu uns? |
|---|---|---|
| `football-dashboard` | Soccer Intelligence (Streamlit), unter `/dashboard` | **ja** |
| `soccer-placeholder` | Platzhalterseite unter `/` (nginx, statisch), seit Etappe E | **ja** |
| `soccer-import` | Datenimport über API-Football (täglich 04:00, bis 0.14 Montag bis Freitag), seit Version 0.14; kein Zugang von aussen | **ja** |
| `soccer-vorschau` | Vorschau der öffentlichen Website unter `/vorschau` mit Passwortabfrage, seit Version 0.17 (`08_Website.md`) | **ja** |
| `article-generator` | Artikeltext-Generator | nein – nicht anfassen |
| `n8n-wxit-n8n-1` | n8n Automatisierung | nein – nicht anfassen |
| `traefik-traefik-1` | Webserver / HTTPS für alle Anwendungen | nein – nicht anfassen |
| Chatbot | Ort unklar (kein eigener Container gefunden) | nein – offen |

### So kommt die Website ins Internet

```
Besucher → https://soccer-intelligence.com/            → Traefik → soccer-placeholder (nginx, öffentlich)
Besucher → https://soccer-intelligence.com/dashboard…  → Traefik (Anfragebremse je Adresse)
                                                                  → football-dashboard (Streamlit, Port 8501, Anmeldemaske)
Besucher → https://soccer-intelligence.com/vorschau…   → Traefik (Passwortabfrage, Anfragebremse, seit 0.17)
                                                                  → soccer-vorschau (Python, Port 8080, nur intern)
```

- Traefik läuft im Host-Netzwerk, erledigt HTTPS/Zertifikat und findet beide Container automatisch über ihre Docker-Labels.
- Bei gleicher Domain gewinnt die längere Regel: Alles unter `/dashboard` geht zum Dashboard, alles andere zur Platzhalterseite.
- Antworten des Dashboards und der Vorschau tragen den Hinweis `X-Robots-Tag: noindex, nofollow` (Suchmaschinen sollen nichts aufnehmen). `robots.txt` der Platzhalterseite sperrt `/dashboard` und `/vorschau` zusätzlich.
- Die Vorschau (seit 0.17) ist nur mit der Passwortabfrage des Browsers erreichbar (Traefik BasicAuth, bcrypt-Hash in `.env` als `SOCCER_VORSCHAU_AUTH`, setzen: Abschnitt 6.3). Fehlt der Eintrag, ist `/vorschau` nicht erreichbar.

- Port 8501 ist nur lokal gebunden (`127.0.0.1`), also von aussen nicht direkt erreichbar.
- Traefik liest die Container-Adresse selbständig aus Docker. Ein Neubau des Containers bricht das Routing nicht.

### Zugang (seit Version 0.15.2, 16.11.2026; vorher Etappe E)

- Streamlit läuft unter dem Pfad `/dashboard` (Umgebungsvariable `STREAMLIT_SERVER_BASE_URL_PATH=dashboard` in `docker-compose.yml`).
- **Anmeldemaske im Dashboard** (`app/anmeldung.py`) statt der Passwortabfrage des Browsers (Traefik BasicAuth bis
  0.15.1; auf manchen Arbeitsrechnern gesperrt). Ohne gültige Anmeldung zeigt jede Adresse unter `/dashboard` nur die
  Maske; Navigation, Seiten und die Buttons im Reiter Datenimport/API erscheinen erst danach.
- Ein Zugang (Benutzername und Passwort). Beides steht nur in `.env` auf dem Server: `SI_LOGIN_USER` im Klartext,
  `SI_LOGIN_HASH` als PBKDF2-SHA256-Hash (600'000 Durchläufe, Zufallssalz). Nicht in Git, nicht in der Dokumentation.
  Setzen oder ändern: Abschnitt 6.3. Fehlen die Zeilen, bleibt das Dashboard gesperrt (Hinweis statt Inhalt).
- Nach der Anmeldung bleibt man **12 Stunden** angemeldet (signiertes Cookie, nur über HTTPS, Pfad `/dashboard`).
  „Abmelden“ unten auf jeder Seite. Ein neues Passwort meldet alle Browser ab.
- Schutz vor Durchprobieren: je Adresse nach 5 Fehlversuchen 15 Minuten Sperre, jede falsche Eingabe wartet 1 Sekunde;
  dazu begrenzt Traefik die Anfragen je Adresse (Label `soccerintel-ratelimit` des eigenen Containers).
- Betroffen sind nur die Labels des eigenen Containers `football-dashboard`. Die Traefik-Grundkonfiguration, n8n und alle
  anderen Anwendungen bleiben unverändert. `SOCCER_DASHBOARD_AUTH` bleibt in `.env`, damit ein Rückweg auf 0.15.1 geht.

---

## 4. Projektordner `/docker/football-dashboard/`

```
/docker/football-dashboard/
├── .github/workflows/tests.yml automatische Tests auf GitHub (bei Push und Pull Request)
├── Dockerfile                  Bauplan des Containers (Python 3.12, Streamlit)
├── docker-compose.yml          Container-Konfiguration inkl. Traefik-Labels (Dashboard + Platzhalter + Import)
├── .env                        Zugang zum Dashboard (Benutzername + Passwort-Hash), zur Vorschau (SOCCER_VORSCHAU_AUTH), API-Schlüssel (API_FOOTBALL_KEY) und seit 0.21 Betreiberangaben für Impressum/Kontakt (SI_IMPRESSUM_NAME, SI_IMPRESSUM_ADRESSE, SI_KONTAKT_EMAIL), nicht in Git
├── requirements.txt            Python-Pakete (Versionen fest); requirements-dev.txt zusätzlich pytest
├── app/                        Anwendung (Aufbau Abschnitt 7)
├── tests/                      automatische Tests; tests/referenz/ = feste Datenbank-Stände für die Testfälle
├── placeholder/                Platzhalterseite unter / (index.html, robots.txt)
├── tools/                      einspielen.sh (Release), zurueck.sh (Rückweg), dashboard_passwort.sh (Zugang), vorschau_passwort.sh (Vorschau, seit 0.17)
├── data/                       nicht in Git: Database-Soccer-Intelligence.xlsx, Spielplan.xlsx (GÜLTIG)
├── import/                     nicht in Git: Datenimport (laeufe/ mit Berichten und neuen Fassungen, roh/ mit API-Antworten, anfragen/, zustand.json)
├── website-bilder/             nicht in Git: Foto der Startseite portrait.jpg (seit 0.18, nur lesend in soccer-vorschau)
├── backup/                     Sicherungen, nicht in Git (auch die vor einem Import ersetzten Fassungen, die letzten 30)
├── docs/                       Dokumentation, massgebliche Quelle (md)
├── word/                       Archiv der Word-Dokumente (nicht mehr gepflegt)
├── CLAUDE.md                   Einstieg und Regeln für Claude
├── CHANGELOG.md                Änderungsprotokoll
└── RELEASE.md                  das aktuelle Release (wird mit jeder Änderung ersetzt)
```

**docker-compose.yml:** Die Datei selbst ist massgeblich und wird hier nicht kopiert. Sie enthält vier eigene Container:
- **`football-dashboard`:**
  - `./data:/data:ro`: Die Excel-Dateien sind nur lesbar.
  - Port nur lokal (`127.0.0.1:8501`), Pfad `/dashboard` (`STREAMLIT_SERVER_BASE_URL_PATH`).
  - Traefik-Labels: Anfragebremse und `noindex` (seit 0.15.2 ohne BasicAuth); Anmeldedaten `SI_LOGIN_USER`, `SI_LOGIN_HASH` aus `.env`.
  - Kopfzeile `X-Robots-Tag: noindex, nofollow`.
  - `./import:/import:ro` und `./import/anfragen` (schreibbar, nur für Freigabe-Anfragen) seit Version 0.14.
- **`soccer-placeholder`:** nginx 1.27, nur lesend.
- **`soccer-import`** (seit 0.14): gleiches Image, Befehl `python -m importer.dienst`; schreibt `./data` (nur beim Tausch nach Freigabe), `./import`, `./backup`; keine Labels, kein Port; Schlüssel aus `.env` (`API_FOOTBALL_KEY`, fehlt er, meldet der Reiter „API-Schlüssel fehlt“).
- **`soccer-vorschau`** (seit 0.17): gleiches Image, Befehl `python -m website.vorschau`; liest `./data`, `./import` und `./website-bilder` (Foto, seit 0.18) nur; kein Port nach aussen (Traefik intern auf 8080); Traefik-Labels: Pfad `/vorschau`, Passwortabfrage (`SOCCER_VORSCHAU_AUTH` aus `.env`), Anfragebremse, `noindex`; seit 0.21 Betreiberangaben aus `.env` (`SI_IMPRESSUM_NAME`, `SI_IMPRESSUM_ADRESSE` mit „|“ zwischen Strasse, PLZ Ort und Land, `SI_KONTAKT_EMAIL`; fehlen sie, zeigen Impressum und Datenschutz einen Platzhalter).

Die Tests in `tests/test_deploy.py` prüfen diese Punkte automatisch.

### Installierte Versionen im Container

| Paket | Version |
|---|---|
| Python | 3.12.15 |
| streamlit | 1.66.1 |
| pandas | 3.1.0 |
| openpyxl | 3.1.5 |

Seit Etappe A (31.10.2026) legt `requirements.txt` genau diese Versionen fest (`streamlit==1.66.1`, `pandas==3.1.0`, `openpyxl==3.1.5`).

Kontrolle nach jedem Neubau:

```bash
docker exec football-dashboard pip freeze | grep -iE "^(streamlit|pandas|openpyxl)=="
```

Erwartet: genau die drei Versionen oben. Weicht etwas ab → Ursache klären, bevor weitergearbeitet wird.

---

## 5. Schutzregeln (verbindlich)

1. Nur im Ordner `/docker/football-dashboard/` arbeiten.
2. `article-generator`, Chatbot, n8n und Traefik nicht verändern oder neu starten.
3. Kein `docker compose down`, keine globalen Docker-Befehle, keine Änderungen an gemeinsamen Netzwerken.
4. Traefik-Labels und Ports nicht ändern (nur mit eigener Freigabe). Letzte Freigabe: Etappe E, 31.10.2026.
5. Vor jeder Änderung: Backup der betroffenen Dateien.
6. Neu bauen nur die eigenen Services: `docker compose up -d --build football-dashboard soccer-import` (seit 0.14 mit dem Datenimport; die Platzhalterseite `soccer-placeholder` gehört ebenfalls zu uns und muss bei Code-Änderungen nicht neu gestartet werden)
7. Danach immer prüfen: `docker ps` → alle Container laufen weiter.
8. Keine Passwörter, Tokens oder Schlüssel in Code oder Dokumentation. Die Zugangsdaten für den Dashboard-Passwortschutz liegen nur als Hash in einer Konfigurationsdatei auf dem Server (z. B. `.env`, nicht in Git); ebenso der API-Schlüssel von API-Football (`API_FOOTBALL_KEY` in `.env`).
9. Fehlende Statistikwerte nie durch 0 oder Schätzungen ersetzen.
10. Änderungen erst nach Freigabe durch Carsten.

---

## 6. Abläufe

### 6.1 Release einspielen

**GitHub ist die einzige Quelle** (seit 09.11.2026). Jede Änderung entsteht auf GitHub, der Server holt nur ab.

1. **Claude arbeitet auf GitHub.** In einer Sitzung von Claude Code (claude.ai/code, mit dem Repository `Carsten1982/soccer-intelligence` verbunden). Claude legt die Änderung auf einem eigenen Zweig ab (`claude/…`), mit neuer `RELEASE.md` (Inhalt, Erwartungswerte, was im Browser zu prüfen ist).
2. **Carsten prüft auf GitHub.** „Create PR“ (Pull Request) öffnen. Dort stehen alle Änderungen Zeile für Zeile, und die **automatischen Tests** laufen (`.github/workflows/tests.yml`, rund 3 Minuten). Erst bei grünem Haken: „Squash and merge“ (ein Commit je Änderung, gut lesbarer Verlauf).
3. **Server holt ab** – immer in einer `tmux`-Sitzung, damit ein Verbindungsabbruch der Browser-Konsole den Lauf nicht stoppt (seit 15.11.2026):
   ```bash
   tmux new -s einspielen
   ```
   ```bash
   bash /docker/football-dashboard/tools/einspielen.sh github
   ```
   Nach einem Verbindungsabbruch: neu anmelden und `tmux attach -t einspielen` (der Lauf geht dort weiter); fertig: `exit`.
   Wurde der Lauf trotzdem nach dem Holen abgebrochen, merkt sich das Skript das (`backup/EINSPIELEN_OFFEN`) und macht beim nächsten Aufruf mit Tests und Neubau weiter, statt „Nichts Neues“ zu melden.
   Bringt ein Release eine neue Fassung von `einspielen.sh` selbst mit, gilt sie erst ab dem **nächsten** Aufruf: Der laufende Aufruf arbeitet mit der Fassung zu Ende, mit der er gestartet wurde (so liefen beim ersten Einspielen von 0.15.2 noch alle Tests).
   Das Skript zeigt, was neu ist, macht ein Backup, übernimmt genau den Stand von GitHub (nur „fast-forward“, kein eigener Commit), testet mit den echten Excel-Dateien (seit 0.15.2 nur die schnellen Tests, rund 8 Minuten; die langsamen laufen bei jedem Pull Request auf GitHub), baut nur `football-dashboard` und `soccer-import` neu und prüft `200`/`200` (Platzhalter, Anmeldemaske). Danach im Browser prüfen, was in `RELEASE.md` steht, und mit `j` bestätigen.

Das Skript stoppt, wenn auf dem Server etwas geändert wurde, das nicht auf GitHub ist (`git status` nicht leer oder eigene Commits). Bei einem Fehler hält es an, setzt nichts selbst zurück und nennt den Rückweg. Protokolle (Tests, Neubau) liegen im Backup-Ordner. Die automatischen Tests auf GitHub laufen ohne die Excel-Dateien aus `data/` (die liegen nur auf dem Server); dafür prüfen sie auch die Einspiel-Skripte in einem Probelauf (`tests/test_einspielen.py`, im Test-Container auf dem Server übersprungen, weil dort `git` fehlt).

**Rückweg zum Stand vor dem letzten Release:**

```bash
bash /docker/football-dashboard/tools/zurueck.sh
```

Fragt vorher nach. Schon übernommen oder committet: Ein Gegen-Commit stellt genau den alten Stand wieder her und wird gepusht (nichts geht verloren, Server und GitHub bleiben gleich). Noch nicht committet (Weg Paket, Antwort `n`): Dateien zurücksetzen, neue Dateien aus dem Paket entfernen. Danach Neubau und Prüfung. Die Excel-Dateien bleiben unberührt.

**Ersatz: Paket `release.zip`** (wenn GitHub nicht geht). Das Paket enthält `RELEASE.md` mit dem Commit-Text (Zeile `**Commit:** …`); sollen Dateien gelöscht werden, liegt `release_loeschen.txt` bei (eine Datei je Zeile). Mit WinSCP hochladen (Projektordner oder `/root`, auch als `release_2.zip`), dann `bash /docker/football-dashboard/tools/einspielen.sh` (ohne `github`). Am Schluss fragt es „Commit und Push machen (j/n)“. Das Skript stoppt, wenn GitHub schon weiter ist als der Server.

**Ohne Skript** (Notfall) – die Schritte für ein Paket einzeln:

1. **Backup.** `git status` muss leer sein. Am Schluss steht der Git-Stand vorher.
   ```bash
   cd /docker/football-dashboard && git status --short && B=backup/$(date +%F_%H%M)_vor_release && mkdir -p "$B" && git rev-parse --short HEAD > "$B/git_stand.txt" && tar czf "$B/code_docs.tgz" app tests docs *.md && ls -la "$B" && cat "$B/git_stand.txt"
   ```
2. **Paket** `release.zip` mit WinSCP hochladen und entpacken. Der Befehl holt die Datei auch aus `/root`:
   ```bash
   cd /docker/football-dashboard && { [ -f release.zip ] || mv /root/release.zip . ; } && python3 -m zipfile -e release.zip . && rm release.zip && git status --short
   ```
3. **Tests** im Wegwerf-Container (Projekt nur lesend eingebunden).
   - `tests` am Ende ist wichtig, sonst sammelt pytest auch `backup/`.
   - `SI_DATA_DIR=/src/data` ist wichtig, sonst finden die Seitentests die Excel-Dateien nicht.
   - Bei Fehlern: **Stopp**, Ausgabe an Claude.
   - Auf GitHub laufen immer **alle** Tests. Beim Einspielen mit dem Skript (seit 0.15.2) und für die Arbeit
     zwischendurch genügt der schnelle Lauf ohne die Ende-zu-Ende-Tests (Marker `langsam`): `-m "not langsam"`.
     Der Befehl unten macht den vollständigen Lauf (rund 20 Minuten).
   ```bash
   cd /docker/football-dashboard && docker run --rm -v "$PWD":/src:ro -e SI_DATA_DIR=/src/data -e PYTHONDONTWRITEBYTECODE=1 -w /src python:3.12-slim sh -c "pip install -q --root-user-action=ignore -r requirements-dev.txt && python -m pytest -q -p no:cacheprovider tests" 2>&1 | tail -15
   ```
4. **Aktivieren** (nur unser Container) und **prüfen**. Erwartet: `200` und `200` (seit 0.15.2 Anmeldemaske; bis 0.15.1 `401`).
   ```bash
   cd /docker/football-dashboard && docker compose up -d --build football-dashboard && sleep 5 && docker ps --format "table {{.Names}}\t{{.Status}}" && docker logs football-dashboard --tail 8 && curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/ ; curl -s -o /dev/null -w "%{http_code}\n" https://soccer-intelligence.com/dashboard/
   ```
5. **Im Browser** prüfen, was in `RELEASE.md` steht.
6. **Commit und Push** mit dem Text aus `RELEASE.md`. Die Git-Nummer der letzten Zeile an Claude schicken.
   ```bash
   cd /docker/football-dashboard && git add -A && git commit -m "<Text aus RELEASE.md>" && git push && git log -1 --oneline
   ```

Rückweg ohne Skript (noch nicht committet): `cd /docker/football-dashboard && git reset --hard <Git-Stand vorher> && docker compose up -d --build football-dashboard`

### 6.2 Neue Excel-Datei aufspielen

Grundsatz: Die neue Datei wird **erst geprüft und dann** zur gültigen Datenquelle. Die App liest nur `Database-Soccer-Intelligence.xlsx`. Eine Datei mit anderem Namen in `data/` wird ignoriert.

1. **Hochladen unter Zwischennamen:** `data/upload.xlsx` (WinSCP).
2. **Prüfen** mit allen Prüfregeln aus `02_Datenbasis.md`:
   ```bash
   docker exec football-dashboard python -c "
   from pathlib import Path
   from core.loader import load_database
   db = load_database(Path('/data/upload.xlsx'))
   print('Fehler:', db.count('Fehler'), '| Warnungen:', db.count('Warnung'), '| Hinweise:', db.count('Hinweis'))
   for i in db.issues:
       if i.level != 'Hinweis': print(i.level, i.sheet, i.check, i.match_id, i.message)
   "
   ```
   Erwartet: `Fehler: 0`. Neue Warnungen vor dem Austausch klären. **Bei Fehlern: Stopp**, Datei korrigieren und erneut hochladen.
3. **Sichern und austauschen.** `mv` im selben Ordner ist sofort komplett, die App liest nie eine halbe Datei.
   ```bash
   cd /docker/football-dashboard && cp -p data/Database-Soccer-Intelligence.xlsx backup/Database-Soccer-Intelligence_$(date +%F_%H%M).xlsx && mv data/upload.xlsx data/Database-Soccer-Intelligence.xlsx && sha256sum data/Database-Soccer-Intelligence.xlsx
   ```
4. **Kontrolle:** Die App liest die neue Datei beim nächsten Seitenaufruf automatisch, ohne Neustart. Bereich Datenqualität ansehen und die Prüfsumme in `02_Datenbasis.md` und im CHANGELOG eintragen.
5. **Rückweg:** letzte Sicherung zurückkopieren.
   ```bash
   cd /docker/football-dashboard && ls -t backup/Database-Soccer-Intelligence_*.xlsx | head -3
   cp -p backup/Database-Soccer-Intelligence_<DATUM_ZEIT>.xlsx data/restore.xlsx && mv data/restore.xlsx data/Database-Soccer-Intelligence.xlsx
   ```

Für `Spielplan.xlsx` gilt derselbe Ablauf. Die Prüfregeln stehen in `04_Spielplan.md`.

**Saisonwechsel (seit Version 0.11, KPI-Regelwerk 1.2):** Die älteste Saison der Datenbank ist die Referenzsaison: Sie liefert nur die Vorsaison und wird nie ausgewertet. Beginnt eine neue Saison (z. B. 2027/28):

1. In der Excel-Datei in allen vier Ligablättern die Zeilen der ältesten Saison löschen (z. B. 2018/19). Nur ganze Zeilen löschen, nie einzelne Zellen, sonst verrutschen die Spalten (Fehler vom 10.11.2026, `02_Datenbasis.md`, Abschnitt 4d). Einträge im Blatt *Datenhinweise* zu gelöschten Spielen ebenfalls löschen.
2. Die neue Saison wie gewohnt ergänzen und die Datei nach den Schritten 1–4 oben aufspielen.
3. Kontrolle im Bereich Datenqualität: je Liga „Referenzsaison: 2019/20 (nur Vorsaison, nicht ausgewertet)“, keine Warnung „Saison fehlt“. Im Code ist nichts zu ändern.

### 6.3 Dashboard-Zugang setzen oder Passwort ändern (seit 0.15.2: Anmeldemaske)

```bash
bash /docker/football-dashboard/tools/dashboard_passwort.sh
```
```bash
cd /docker/football-dashboard && docker compose up -d football-dashboard
```

- Fragt Benutzername und Passwort (verdeckt, zweimal, mindestens 10 Zeichen). Gespeichert werden nur `SI_LOGIN_USER`
  und der Hash `SI_LOGIN_HASH` in `.env`. Das Passwort erscheint weder auf dem Bildschirm noch im Befehlsverlauf.
- Die alte `.env` wird vorher nach `backup/env_<Datum>` gesichert. Andere Zeilen in `.env` bleiben unverändert.
- Bei verschiedenen Eingaben oder einem Fehler bricht das Skript ab und ändert nichts.
- **Vor dem ersten Einspielen von 0.15.2** (das Skript liegt dann erst auf GitHub, noch nicht auf dem Server):
  ```bash
  cd /docker/football-dashboard && git fetch -q && bash <(git show origin/main:tools/dashboard_passwort.sh)
  ```

**Passwort der Website-Vorschau** (seit 0.17, Passwortabfrage des Browsers unter `/vorschau`):

```bash
bash /docker/football-dashboard/tools/vorschau_passwort.sh
```
```bash
cd /docker/football-dashboard && docker compose up -d --build soccer-vorschau
```

- Gleiche Bedienung wie oben (Benutzername, Passwort verdeckt und zweimal, mindestens 10 Zeichen, Sicherung von `.env`).
  Gespeichert wird nur der bcrypt-Hash als `SOCCER_VORSCHAU_AUTH`. Benutzername und Passwort dürfen andere sein als
  beim Dashboard.

**Foto der Startseite** (seit 0.18, Entscheidung Q6 in `08_Website.md`): nur auf dem Server, nie in Git.

1. Foto vorbereiten: JPEG, quadratisch, mindestens 230 × 230 Pixel (angezeigt 115 × 115, doppelt für scharfe
   Handy-Bildschirme), Dateiname genau `portrait.jpg`.
2. Mit WinSCP nach `/docker/football-dashboard/website-bilder/` hochladen (Ordner entsteht beim Einspielen von 0.18;
   fehlt er: `mkdir -p /docker/football-dashboard/website-bilder`). Den Ordner selbst nicht löschen oder umbenennen,
   sonst sieht der Container ihn erst nach einem Neustart wieder.
3. Prüfen (erwartet `-rw-r--r--` und die Grösse in Bytes):
   ```bash
   ls -l /docker/football-dashboard/website-bilder/portrait.jpg
   ```
4. Die Startseite der Vorschau neu laden: Das Foto erscheint sofort (kein Neustart nötig; der Browser behält ein altes
   Foto bis zu einer Stunde, dann Strg+F5). Ohne Datei steht ein neutraler Platzhalter.

### 6.4 Zustand prüfen (nur lesend)

```bash
cd /docker/football-dashboard && git log -1 --oneline && docker ps --format "table {{.Names}}\t{{.Status}}" && docker logs football-dashboard --tail 20 && docker logs soccer-import --tail 10 && docker logs soccer-vorschau --tail 5 && sha256sum data/*.xlsx
```

### 6.5 Datenimport über API-Football (seit Version 0.14)

Regeln und Ablauf: `06_Datenlieferung.md`; Bereich im Dashboard: Dashboard-Briefing 6.5.

**Schlüssel eintragen** (einmalig, vor dem ersten Einspielen von 0.14; der Schlüssel steht nur in `.env`):
```bash
( umask 077 && cd /docker/football-dashboard && cp -p .env backup/env_$(date +%F_%H%M) && read -rsp "API-Schlüssel: " K && echo && [ -n "$K" ] && { grep -v "^API_FOOTBALL_KEY=" .env || true; } > .env.neu && printf 'API_FOOTBALL_KEY=%s\n' "$K" >> .env.neu && cat .env.neu > .env && rm .env.neu && grep -c "^API_FOOTBALL_KEY=" .env )
```
Erwartet: `1` (der Schlüssel erscheint nicht auf dem Bildschirm; vorher kommt eine Kopie von `.env` nach `backup/`). Ein vorhandener Eintrag wird ersetzt, eine leere Eingabe ändert nichts. Neuer Schlüssel: denselben Befehl ausführen, danach `cd /docker/football-dashboard && docker compose up -d soccer-import`.

**Täglich:** Jeden Tag um 04:00 (seit 0.15 auch am Wochenende) holt `soccer-import` die Daten und legt eine neue
Fassung bereit. Im Reiter „Datenimport/API“ prüfen und **Übernehmen** oder **Verwerfen**; eine Freigabe am Wochenende
ist nicht nötig (der nächste Lauf ersetzt die wartende Fassung). Der Tausch geschieht innerhalb einer Minute; die
bisherigen Dateien kommen nach `backup/` (`…_vor_import.xlsx`, dazu `entscheidungen_…json`). Erscheint „Ihre
Entscheidung“, im Reiter einen der beiden Buttons wählen; der Entscheid wirkt ab dem nächsten Lauf (`06`, Abschnitt
10.1). Ab dem Datum `automatisch_ab` in `app/config/import.toml` wird eine **unkritische** Fassung sofort übernommen.

**Lauf sofort starten** (z. B. nach dem Einspielen oder wenn ein Lauf fehlgeschlagen ist):
```bash
docker exec soccer-import python -m importer.dienst --jetzt
```

**Import anhalten und wieder starten** (nur unser Container):
```bash
cd /docker/football-dashboard && docker compose stop soccer-import
```
```bash
cd /docker/football-dashboard && docker compose up -d soccer-import
```

**Rückweg nach einer übernommenen Fassung:** wie Abschnitt 6.2, Schritt 5, mit den Dateien `backup/*_vor_import.xlsx`
(Datenbank und Spielplan gemeinsam zurückkopieren).

---

## 7. Architektur

Grundsatz (freigegeben 25.10.2026): Die Rechenlogik steht in `app/core`, ohne Oberfläche und testbar. `app/views` zeigt nur an. Dieselbe Logik soll später die öffentliche Website über einen Datenexport bedienen.

```
app/
├── app.py                Navigation; prüft beim Start ligen.toml, teams.toml und schwellen.toml
├── state.py              Laden mit Cache (neu laden bei geänderter Datei), KPI-Ergebnisse je Spieltag (H.1)
├── config/               Konfiguration, mit dem Code versioniert (Änderung -> Container neu bauen)
│   ├── ligen.toml        aktive Ligen, Adresse, Anzahl Teams (Etappe B)
│   ├── teams.toml        Teamliste: bekannte Teams ohne Datenbankeinträge, z. B. Aufsteiger (Etappe B)
│   ├── teamnamen.toml    Teamnamen von API-Football je Team-ID, mit bisheriger Schreibweise (0.14)
│   ├── zuordnung_api.csv feste Zuordnung eigene Spiel-ID ↔ API-ID, 11'978 Spiele (0.15)
│   ├── import.toml       Datenimport: Datum für den automatischen Tausch (0.14)
│   ├── schwellen.toml    Schwellen und Signalqualität je Liga, KPI und Richtung (seit 0.19, Feld `signalqualitaet` seit 0.20)
│   ├── teamnamen_anzeige.csv  Anzeigenamen der Vereine Deutsch/Englisch für die Website (0.21; Slug bleibt API-Name)
│   ├── website.toml      Website: `index_ab` (Livegang, leer = nichts indexierbar), `seiten_ab_saison` (0.21)
│   └── archiv/           frühere Fassungen, z. B. schwellen_2026-11-14.toml (leicht/stark bis 0.18)
├── core/                 Kernlogik ohne Oberfläche (testbar)
│   ├── settings.py       Pfade, Pflichtblätter, Version
│   ├── schema.py         erwartete Struktur der Excel-Datei
│   ├── files.py          Prüfsumme einer Datei (H.1)
│   ├── loader.py         Einlesen + Strukturprüfung
│   ├── validation.py     Plausibilitätsprüfungen
│   ├── rows.py, issues.py  Prüfmeldungen (Fehler, Warnung, Hinweis)
│   ├── config.py         Einlesen der Konfiguration (Etappe B)
│   ├── fixtures.py       Spielplan einlesen und prüfen (Etappe B)
│   ├── matchday.py       aktueller Spieltag, Spieltagsübersicht (Etappe B)
│   ├── anzeige.py        kommende Spieltage: Abschnitte, Pausen, Navigation, „Werte ab“, Top-Block, Vorschau (0.16);
│   │                     seit 0.20 gespielt ab Anpfiff + 2 h, 48-Stunden-Grenze, values_from
│   ├── schnappschuss.py  Schnappschuss je Spiel: genau speichern/lesen, nie überschreiben, was die Seiten zeigen (0.20)
│   ├── importstand.py    Beginn des letzten erfolgreichen Importlaufs, für Dashboard und Website (0.20)
│   ├── overview.py       Übersicht der Datenbank (Spiele je Saison)
│   ├── kpis.py           KPI 01–09 gemäss Regelwerk (Etappen C und H)
│   ├── thresholds.py     Schwellen und Signalqualität aus schwellen.toml (seit 0.19 je Liga, KPI und Richtung)
│   ├── results.py        KPI-Ergebnisse aller Begegnungen eines Spieltags (H.1)
│   ├── top.py            Auswahl der Top Anomalien (seit 0.19 nach Signalqualität mit Liga-Mix)
│   ├── simulation.py     Ergebniskontrolle und Simulation der Schwellen (Etappe I.1)
│   └── frequency.py      Häufigkeit der Anomalien (Etappe C)
├── website/              öffentliche Website (0.17, 08_Website.md): daten (Laden, Zeitreise), start, spieltag, spiel
│                         (Datensätze mit Codes, 0.18), seiten + vorlagen/ (HTML, teile.html = Bausteine, inhalt/ = lange
│                         Texte je Sprache), texte/de.json + en.json (Sprachdateien), format (DE/EN), statisch/ (CSS,
│                         Schriften, site.js, wurzel/ = Icons), vorschau (Webserver unter /vorschau); seit 0.21 adressen
│                         (Pfade, 301/302/404), seo (Index-Regeln, Title, JSON-LD), sitemap (robots.txt, Sitemap), namen
│                         (Anzeigenamen je Sprache), methodik (Zahlen aus schwellen.toml, Excel-Download)
├── importer/             Datenimport über API-Football (0.14): client (Abfragen, Obergrenze, Rohdaten), convert (58
│                         Spalten, Tor-Ereignisse), spielplan, teams, erzeugen (neue Fassung + Bericht), dienst (Zeitplan,
│                         Freigabe), entscheide (Entscheide aus dem Reiter, 0.15), schnappschuss (stündlicher Lauf, 0.20);
│                         core/zuordnung.py = eigene ID ↔ API-ID
└── views/                Bereiche: Top Anomalien, je Liga, Datenqualität, Datenimport/API (datenimport.py, 0.14); components.py = Stil, Kopfbereich,
                          Sperrhinweis; kpi_table.py = kompakte Liga-Tabelle mit Aufklappen (Etappe H);
                          simulation.py = Bereich Simulation – Spielwiese (Etappe I.1)
tests/                    automatische Tests; gegenrechnung.py = unabhängige zweite KPI-Berechnung (Etappe F)
data/Spielplan.xlsx       anstehende Partien
docs/                     Dokumentation (01–06, tests/)
CLAUDE.md                 Projektübersicht für Claude Code
CHANGELOG.md              Änderungsprotokoll
```

---

## 8. Offene Punkte

- [ ] Ablauf: Knopf „Run workflow“ auf GitHub zum Einspielen (GitHub als einzige Quelle und automatische Tests erledigt 09.11.2026)
- [ ] Spielplan Premier League, Spieltag 1 (16.–20.08. statt gespielt 21.–24.08.): prüft Carsten
- [ ] Name des bisherigen Datenanbieters dokumentieren (`02_Datenbasis.md`, Regelwerk Abschnitt 8, Punkt 7)
- [ ] Öffentliche Website: Impressum und Datenschutz – Texte seit 0.21 auf der Vorschau (Betreiberangaben aus `.env`); juristische Prüfung DE/EN vor dem Livegang offen
- [ ] Server: Meldung „1 updates could not be installed automatically“ (unattended-upgrades) prüfen. Kein Upgrade auf Ubuntu 26.04 vorerst.
- [ ] Wo läuft der Chatbot? (nur zur Dokumentation)
- [ ] Aufräumen in `backup/` nach einigen Wochen stabilen Betriebs
- [ ] Offene KPI-Punkte im Regelwerk, Abschnitt 8 (nicht blockierend)

Erledigte Punkte stehen im CHANGELOG.

### 8.1 Offene Bereinigungen im Code (seit 16.11.2026)

Regel (CLAUDE.md, Arbeitsweise): Vor jeder Änderung diese Liste prüfen. Betrifft ein Punkt eine Datei, die ohnehin
geändert wird, die Bereinigung mit erledigen und hier abhaken (mit Version). Spätestens bei der Rundum-Prüfung des Codes
werden alle offenen Punkte abgearbeitet. Bedingung jeder Bereinigung: KPI-Ergebnisse und Meldungen bleiben gleich
(Vollvergleich bzw. bestehende Tests).

| Nr. | Datei, Stelle | Bereinigung | Herkunft | Status |
|---|---|---|---|---|
| B1 | `app/core/simulation.py` `build_cases()`, `app/core/kpis.py` `team_games()`/`reference_games()` | Sensitivitätsanalyse beschleunigen: Teamspiele und Referenzspiele über vorbereitete Indizes statt wiederholter Filter über die ganze Liga. Vorher Benchmark aller vier Ligen, nachher Vollvergleich aller Fälle | Code-Prüfung 16.11.2026, P2 | **erledigt 0.19.1:** Index je vorbereiteter Liga (`league_index`, `team_rows`, `reference_rows`); Fälle aller vier Ligen 52,8 s → 5,2 s, alle 77'354 Fälle und alle 95'824 KPI-Werte identisch (Vollvergleich, `tests/test_kpis.py`) |
| B2 | `app/core/loader.py` `_read_notes()` | IDs je Liga einmal als Menge bilden statt für jeden Datenhinweis neu zu suchen | Code-Prüfung 16.11.2026, P3a | **erledigt 0.15.1** |
| B3 | `app/importer/spielplan.py` `main_period()` | Gleitendes Fenster statt Neufiltern je Starttag; Regel „früheres Fenster gewinnt“ ist durch Tests abgesichert | Code-Prüfung 16.11.2026, P3b | **erledigt 0.19.1:** gleitendes Fenster, Vergleich mit der bisherigen Umsetzung an 3'000 Zufallsfällen |
| B4 | `app/core/validation.py`, Prüfung „Team mehrfach im Spieltag“ | `groupby`/`duplicated` statt zeilenweiser Prüfung, Meldungen unverändert | Code-Prüfung 16.11.2026, P3c | **erledigt 0.19.1:** war bereits mit `duplicated()` umgesetzt; letzte Zeilenschleife durch `itertuples()` ersetzt |
| B5 | `app/core/fixtures.py` `_parse_sheet()`, `_plausibility()` | `itertuples()` statt `iterrows()` (nur mit Messung) | Code-Prüfung 16.11.2026, P3d | **erledigt 0.19.1:** Zeilen als `dict` statt `iterrows()`; Spielplan einlesen 0,75 s → 0,53 s, Ergebnis und alle 156 Meldungen identisch |
| B6 | `app/anmeldung.py` `_set_cookie()` | `st.components.v1.html` durch `st.iframe` ersetzen (Streamlit meldet im Protokoll: „will be removed after 2026-06-01“). Mit streamlit 1.66.1 noch lauffähig; spätestens vor einem Streamlit-Update, mit Browser-Test der Anmeldung | Umsetzung 0.16 (Protokoll der Probe) | **erledigt 0.19.1:** `st.iframe` statt `components.html`; im Browser geprüft (Cookie gesetzt, 12 Stunden, zweiter Tab angemeldet); auf dem Server mit HTTPS prüfen |
| B7 | `app/state.py` `last_import_day()`, `app/website/daten.py` `letzter_import()` | Gleiche Funktion doppelt (Liste der Fehlstatus zweimal) – eine Fassung für Dashboard und Website, mit Uhrzeit | Umsetzung 0.20 (48-Stunden-Grenze) | **erledigt 0.20:** `core/importstand.last_successful_run` |

---

## 9. Ideen für später (erst nach stabiler erster Version)

| Idee | Notiz |
|---|---|
| ~~Spieltage im Dashboard vor- und zurückblättern~~ | umgesetzt am 31.10.2026 (Briefing 3.2) |
| Mehrheitsregel für den aktuellen Spieltag (07.11.2026 zurückgestellt) | Aktuell = Spieltag mit den meisten Spielen der nächsten 7 Tage; offene Spiele früherer Spieltage in einem Bereich „Nachholspiele“ mit KPIs. Nur nötig, falls verzerrte Spieltage deutlich häufiger werden als heute. |
| Internes Test-Datum (`testdatum` in der Konfiguration) | Dashboard verhält sich wie an einem anderen Tag; praktisch zum Durchspielen vergangener Spieltage |

