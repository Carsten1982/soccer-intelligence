# Soccer Intelligence – E-Mail, Alarme und Überwachung (Spezifikation)

**Version 0.4** · Stand 20.11.2026 (v0.4: umgesetzt mit 0.23, Abschnitt 10; v0.3: F5 und F6 bestätigt, Testmails nach jedem Release M9; v0.2: Entscheide F1–F7) · **Status: freigegeben von Carsten am 20.11.2026** · Umsetzung mit Version 0.23

Diese Datei ist die einzige Stelle für den Mailversand, die Alarme, die wöchentliche Statusmail, die
Server-Überwachung, die Laufzeiten (Abos, Domain, Postfach) und den Versand des Kontaktformulars. Grundlage: Entscheide
Carsten vom 20.11.2026 (Zuschnitt 0.22/0.23/0.24, Postfächer, Alarmliste, Statusmail, Spamschutz).

---

## 1. Entscheide (Carsten 20.11.2026)

| Nr. | Thema | Entscheid |
|---|---|---|
| M1 | Postfächer | Bei Hostinger: **ein Postfach** `info@soccer-intelligence.com` (allgemeine Mails, Kontaktformular, Impressum) und `alert@soccer-intelligence.com` als **Alias** darauf (Alarme). Postfach gültig bis 20.11.2028 (Carsten 20.11.2026). |
| M2 | Was kommt per Mail | **Nur Alarme** und **eine Statusmail pro Woche** (Beweis, dass alles läuft). Keine tägliche Sammelmail. |
| M3 | Daten-Alarme (sofort) | Import fehlgeschlagen · API-Kontingent fast aufgebraucht · Schnappschuss fehlt · Datei-Prüfung gescheitert (Website zeigt „Daten werden geprüft“). |
| M4 | Server-Alarme (Warnung / Kritisch) | Festplatte über 85 % / über 95 % · Arbeitsspeicher über 90 % für 15 Minuten / über 95 % für 5 Minuten · CPU über 90 % für 30 Minuten / – · Docker-Container mehr als 3 Neustarts in 10 Minuten / länger als 5 Minuten nicht verfügbar. |
| M5 | Häufigkeit | Je Alarmart höchstens eine Mail pro Stunde; ist das Problem behoben, eine Mail „Behoben“. |
| M6 | Kontaktformular | Versand per Mail, keine Speicherung (Beschluss 8, 19.11.2026). Spamschutz: Rechenaufgabe, verstecktes Feld, höchstens 3 Nachrichten pro Stunde je Absender – reicht für den Anfang. |
| M7 | Laufzeiten | Im Dashboard verfolgen: API-Football-Abo (aus der API), Domain (bis 23.10.2027, automatische Verlängerung an), Postfach (bis 20.11.2028). |
| M9 | Testmails nach jedem Release | Wunsch Carsten 20.11.2026: Nach jedem Einspielen geht über **jeden** Versandweg eine Testmail (Abschnitt 2.1). |
| M8 | Weiterleitung | Das Postfach leitet an die private Adresse von Carsten weiter, also auch alles, was an den Alias `alert@` geht (eingerichtet bei Hostinger; die Adresse steht nur dort, nie im Programm oder in `.env`). |

## 2. Mailversand (Technik)

- **Eine Anmeldung:** Versand immer über das Postfach `info@` (SMTP von Hostinger mit SSL, `smtp.hostinger.com`,
  Port 465). Ein Alias hat kein eigenes Login; ob Hostinger einen Alias als Absender erlaubt, ist nicht sicher –
  darum ist der Absender immer `info@`, mit eigenem Namen je Zweck: „Soccer Intelligence Alarm“ bzw. „Soccer
  Intelligence Kontakt“ (Rückfrage Carsten 20.11.2026).
- **Empfänger:** Alarme und Statusmail **an den Alias `alert@`**, Kontaktformular an `info@`; beides landet im Postfach,
  das an die private Adresse weiterleitet (M8). Alarme bleiben am Empfänger `alert@` und am Absendernamen erkennbar und
  lassen sich filtern. Die private Adresse steht nirgends im Programm, auch nicht in `.env`.
- **Zugangsdaten nur in `.env`** auf dem Server (nie in Git, Code, Logs oder Chat):
  `SI_SMTP_HOST`, `SI_SMTP_PORT`, `SI_SMTP_USER`, `SI_SMTP_PASSWORT`, dazu die Empfänger `SI_ALARM_AN` und
  `SI_KONTAKT_AN` (Standard `alert@` bzw. `info@`). Eintragen
  mit dem Skript `tools/mail_einrichten.sh` (Passwort wird nicht angezeigt, vorher Kopie von `.env` nach `backup/`;
  Ablauf in `01`, Abschnitt 6.6).
- **Fehlt die Konfiguration**, wird nichts versendet; das Dashboard zeigt „Mailversand nicht eingerichtet“, die Website
  zeigt beim Kontaktformular den heutigen Hinweis (Versand gesperrt).
- **Scheitert der Versand** (Server nicht erreichbar, Passwort falsch): Eintrag im Ereignisprotokoll, Hinweis im
  Dashboard, neuer Versuch beim nächsten Anlass. Eine fehlende Statusmail am Montag ist das Zeichen, dass der Versand
  selbst gestört ist.
- **Testmail von Hand:** `docker exec soccer-import python -m betrieb.mail --test alert` (bzw. `info` im Container
  `soccer-vorschau`, `python3 tools/ueberwachen.py --test` auf dem Server).

### 2.1 Integrierter Test nach jedem Release (M9)

Das Einspiel-Skript schickt nach dem Neustart (Schritt 5) über **alle drei Versandwege** je eine Testmail und meldet
das Ergebnis; in Schritt 6 fragt es, ob alle drei angekommen sind:

| Weg | Empfänger | Prüft |
|---|---|---|
| Container `soccer-import` | an `alert@` | Alarme und Statusmail (Zugangsdaten im Container) |
| Container `soccer-vorschau` | an `info@` | Kontaktformular (Zugangsdaten im Container) |
| Prüfskript auf dem Server | an `alert@` | Server-Alarme (Zugangsdaten aus `.env`, ohne Container) |

Betreff: `[Soccer Intelligence] Test nach Release <Version> (<Git>) – <Weg>`. Eine gescheiterte Testmail stoppt das
Einspielen nicht (die Website läuft trotzdem), wird aber deutlich gemeldet und ins Ereignisprotokoll geschrieben. Ist
der Mailversand noch nicht eingerichtet, sagt das Skript das und schickt nichts.
- Mails sind einfacher Text, Deutsch (Schweizer Schreibweise wie das Dashboard), Betreff mit Stufe:
  `[Soccer Intelligence] KRITISCH: …`, `WARNUNG: …`, `BEHOBEN: …`, `Wochenstatus KW 48`.
  Jede Alarm-Mail nennt: was, seit wann, betroffene Werte, was zu tun ist (Reiter im Dashboard oder Befehl).

## 3. Alarme

### 3.1 Daten-Alarme (Container `soccer-import`)

| Alarm | Auslöser | Stufe |
|---|---|---|
| Import fehlgeschlagen | Kontrolllauf fehlgeschlagen, oder ein Lauf nach dem Spiel ist auch nach den 2 Wiederholungen fehlgeschlagen | Kritisch |
| API-Kontingent | 80 % der eigenen Tagesgrenze (400 von 500) verbraucht → Warnung; Grenze erreicht oder Rest laut API unter 10 % → Kritisch | Warnung / Kritisch |
| Schnappschuss fehlt | Schnappschuss-Lauf mit Fehler oder seit über 2 Stunden nicht gelaufen, oder ein Spiel hat angepfiffen, ohne dass sein Schnappschuss besteht (`07`, 4.9) | Kritisch |
| Datei-Prüfung gescheitert | Die gültigen Dateien in `data/` haben Fehler der Prüfregeln (dieselbe Prüfung, nach der die Website „Daten werden geprüft“ zeigt). Geprüft beim stündlichen Schnappschuss-Lauf und nach jedem Tausch | Kritisch |
| Fassung wartet auf Freigabe *(Frage F4)* | Eine Fassung mit Fehlern oder neuen Warnungen wartet im Reiter (`06`, 10.2, Regel 3) | Warnung |
| Entscheid offen *(Frage F4)* | Ein Spiel wird zurückgehalten und wartet auf den Entscheid (`06`, 10.2, Regel 4) | Warnung |
| Statistik fehlt dauerhaft | Ein Spiel hat 7 Tage nach dem Spiel noch fehlende Werte (`06`, Abschnitt 10) | Warnung |
| Laufzeit endet | Ohne automatische Verlängerung (API-Abo): 30 Tage vorher Warnung, 7 Tage vorher Kritisch. Mit automatischer Verlängerung (VPS, Domain, Postfach): 14 Tage vorher Warnung „Bitte prüfen, ob verlängert wurde, und das neue Datum in `laufzeiten.toml` nachtragen“ (die Datei kennt eine Verlängerung nicht von selbst) | Warnung / Kritisch |

### 3.2 Server-Alarme (Prüfskript auf dem Server)

| Alarm | Warnung | Kritisch | Gemessen |
|---|---|---|---|
| Festplatte | über 85 % belegt | über 95 % belegt | Partition mit `/docker/football-dashboard/` |
| Arbeitsspeicher | über 90 % während 15 Minuten | über 95 % während 5 Minuten | verfügbarer Speicher (`MemAvailable`) |
| CPU | über 90 % während 30 Minuten | – | Auslastung aller Kerne |
| Container | mehr als 3 Neustarts in 10 Minuten | länger als 5 Minuten nicht verfügbar (gestoppt oder „unhealthy“) | `football-dashboard`, `soccer-import`, `soccer-vorschau`, `soccer-placeholder` |
| Website erreichbar | – | länger als 5 Minuten nicht erreichbar: `/` nicht 200, `/dashboard/` nicht 200, `/vorschau/` nicht 401 | Abruf von aussen über Traefik (deckt auch einen Ausfall von Traefik ab, ohne ihn anzufassen) |
| Import-Dienst lebt | – | `soccer-import` meldet sich seit über 30 Minuten nicht (Lebenszeichen-Datei; 30 statt 15, weil ein langer Kontrolllauf es nicht erneuert) | Datei `import/lebenszeichen` |

- **Technik:** Skript `tools/ueberwachen.sh` im Projektordner, läuft **jede Minute** über den Zeitplan des Servers
  (`cron`, einmaliger Eintrag – Frage F1). Es liest nur: `/proc`, `df`, `docker inspect` unserer vier Container, einen
  Abruf der eigenen Adressen. Es startet, stoppt oder ändert nichts (Schutzregeln `01`, Abschnitt 5).
- Das Skript verschickt seine Alarme **selbst** (mit `curl` über SMTP, Zugangsdaten aus `.env`), damit eine Meldung
  auch dann kommt, wenn gerade der Container `soccer-import` ausgefallen ist.
- Es schreibt seine letzten Messwerte nach `import/server.json` (Dashboard und Statusmail lesen sie) und seinen Zustand
  (seit wann über der Schwelle, letzte Mail je Alarm) nach `import/ueberwachung.json`.

### 3.3 Häufigkeit und „Behoben“ (M5)

- Je Alarmart (z. B. „Festplatte“, „Container soccer-vorschau“) **höchstens eine Mail pro Stunde**.
- Steigt die Stufe (Warnung → Kritisch), geht sofort eine Mail, auch innerhalb der Stunde.
- **Erinnerung** alle 24 Stunden, solange ein Alarm besteht.
- **Höchstens 3 Mails je Alarm, egal was sonst passiert** (F5, Carsten 20.11.2026): Meldung, höhere Stufe,
  Erinnerung und „Behoben“ zählen zusammen. Danach steht der Alarm nur noch im Dashboard und in der Statusmail.
  Endet ein Alarm und tritt später neu auf, ist das ein neuer Alarm.
- Ist das Problem behoben, eine Mail **„BEHOBEN: …“** mit Dauer (sofern die 3 Mails nicht aufgebraucht sind).
- Alle Alarme und Mails stehen im Ereignisprotokoll (`import/ereignisse.jsonl`) und im Reiter Datenimport/API
  (Block „Alarme“: offene Alarme, letzte 14 Tage).

## 4. Wöchentliche Statusmail (M2)

**Jeden Montag um 06:00** (F7) von `soccer-import` an `alert@`, Betreff `[Soccer Intelligence] Wochenstatus KW 48`.

1. **Gesamturteil** in der ersten Zeile: „Alles in Ordnung“ oder „n offene Alarme“.
2. **Läufe der Woche:** Anzahl je Anlass (Kontrolllauf, nach dem Spiel, Wiederholung), davon übernommen, wartend,
   fehlgeschlagen; geschriebene Spiele, Korrekturen, offene Spiele mit fehlenden Werten.
3. **Alarme der Woche:** je Alarm Stufe, Beginn, Ende bzw. „offen“.
4. **Server:** Festplatte, Arbeitsspeicher, CPU (aktuell und Höchstwert der Woche), Neustarts der Container.
5. **Backups:** Anzahl und Grösse, ältestes und neuestes, letzte Monatssicherung.
6. **Laufzeiten:** API-Abo, Domain, Postfach mit Datum und Resttagen.
7. **Hinweise:** Vereine ohne Anzeigenamen der Website, offene Entscheide.
8. **Am ersten Montag im Monat:** Erinnerung, die Monatssicherung auf den Laptop zu laden (Befehl aus `01`, 6.5).

## 5. Laufzeiten (M7)

- Datei `app/config/laufzeiten.toml` (keine Geheimnisse, Änderung über Git): je Eintrag Name, Ablaufdatum,
  automatische Verlängerung ja/nein. Einträge (Carsten 20.11.2026, alle mit automatischer Verlängerung): **VPS KVM 1
  bis 22.06.2027** (frühester Ablauf, auf ihm läuft alles), Domain `soccer-intelligence.com` bis 23.10.2027,
  E-Mail-Postfach bis 20.11.2028. Das API-Abo kommt wie heute aus der API.
- Dashboard, Reiter Datenimport/API: Block **„Laufzeiten“** neben der Statusleiste: Datum, Resttage, Farbe (grün,
  ab 30 Tagen gelb, ab 7 Tagen oder abgelaufen rot).
- Alarme nach 3.1, Zeile in der Statusmail.

## 6. Kontaktformular (Website, M6)

- Das Formular besteht seit 0.21 (`vorlagen/inhalt/kontakt.*.html`): Name (optional), E-Mail, Nachricht, Einwilligung
  Datenschutz, Sicherheitsfrage, verstecktes Feld. Ab 0.23 ist der Knopf „Senden“ aktiv, sobald die Zugangsdaten
  für `info@` in `.env` stehen.
- **Prüfung auf dem Server** (ohne JavaScript nutzbar): Pflichtfelder, gültige E-Mail-Adresse, Nachricht 10 bis 5'000
  Zeichen, Name höchstens 100 Zeichen, Einwilligung gesetzt, Sicherheitsfrage richtig, verstecktes Feld leer. Bei
  Fehlern bleibt die Eingabe stehen, die Fehler stehen je Feld (Texte Abschnitt 6.1).
- **Sicherheitsfrage:** zufällig aus 10 einfachen Rechenaufgaben (z. B. „Was ergibt 4 + 3?“); welche gestellt wurde,
  steht in einem versteckten Feld mit Prüfsumme (das Geheimnis entsteht beim Start des Dienstes, die Aufgabe gilt
  2 Stunden – keine Konfiguration nötig), damit niemand die Antwort mitschicken kann.
- **Anfragebremse:** höchstens 3 gesendete Nachrichten pro Stunde je Absender-Adresse (IP), danach Hinweis
  „Bitte später noch einmal versuchen“. Die Zählung liegt nur im Arbeitsspeicher, nichts wird gespeichert.
- **Versand:** von `info@` an `info@`, „Antwort an“ = Adresse des Absenders; Betreff
  `Kontaktformular: <erste 60 Zeichen der Nachricht>`; Inhalt: Name, E-Mail, Sprache der Seite, Zeitpunkt, Nachricht.
  Keine Speicherung, kein Protokoll des Inhalts (nur „Nachricht gesendet“ / „Versand fehlgeschlagen“ ohne Inhalt).
- **Nach dem Senden:** Weiterleitung auf die Seite mit „Danke, deine Nachricht ist angekommen.“ (kein doppeltes Senden
  beim Neuladen). Scheitert der Versand: „Die Nachricht konnte gerade nicht gesendet werden. Bitte versuche es später
  noch einmal oder schreib an info@soccer-intelligence.com.“ und ein Daten-Alarm „Kontaktformular: Versand gescheitert“.
- Die Datenschutzerklärung hat den Abschnitt „Kontakt per E-Mail und Kontaktformular“ bereits; die juristische
  Prüfung steht vor dem Livegang an (`01`, Abschnitt 0, 1.0).
- Die Website schreibt mit „ß“ (Entscheid 16.11.2026); alle Texte Deutsch und Englisch.

### 6.1 Texte der Feldfehler (Deutsch / Englisch)

| Fall | Deutsch | Englisch |
|---|---|---|
| E-Mail fehlt | Bitte gib deine E-Mail-Adresse ein. | Please enter your email address. |
| E-Mail ungültig | Diese E-Mail-Adresse sieht nicht vollständig aus. | This email address doesn't look complete. |
| Nachricht fehlt | Bitte schreib eine Nachricht. | Please write a message. |
| Nachricht zu kurz | Deine Nachricht ist etwas kurz – bitte mindestens 10 Zeichen. | Your message is a little short – please use at least 10 characters. |
| Nachricht zu lang | Deine Nachricht ist zu lang – bitte höchstens 5.000 Zeichen. | Your message is too long – please use no more than 5,000 characters. |
| Name zu lang | Bitte höchstens 100 Zeichen. | Please use no more than 100 characters. |
| Einwilligung fehlt | Bitte bestätige, dass du die Datenschutzerklärung gelesen hast. | Please confirm that you have read the privacy policy. |
| Sicherheitsfrage falsch | Das Ergebnis stimmt leider nicht. Bitte versuch es noch einmal. | That answer isn't right. Please try again. |
| Zu viele Nachrichten | Du hast gerade mehrere Nachrichten gesendet. Bitte versuch es in einer Stunde noch einmal. | You have just sent several messages. Please try again in an hour. |

## 7. Ereignisprotokoll und Dashboard

- `import/ereignisse.jsonl` (seit 0.22) bekommt zusätzlich: Alarm ausgelöst / erinnert / behoben, Mail gesendet /
  gescheitert, Statusmail gesendet, Kontaktformular gesendet / gescheitert (ohne Inhalt).
- Reiter Datenimport/API: neue Blöcke **„Alarme“** (offene Alarme mit Stufe und Beginn, letzte 14 Tage),
  **„Server“** (letzte Messwerte aus `server.json`, Zeit der Messung) und **„Laufzeiten“**; in der Statusleiste
  „Mailversand: eingerichtet ✓ / nicht eingerichtet / gestört“.
- Dazu der Wunsch vom 20.11.2026: „Läufe heute“ nennt die Partien (schon umgesetzt, kommt mit 0.23).

## 8. Tests (0.23)

Alarmregeln je Auslöser (Schwelle knapp darunter und darüber, Dauer), Drosselung (eine Mail pro Stunde, Stufe steigt,
Erinnerung, „Behoben“), Statusmail (Inhalt aus einem Beispiel-Protokoll, erster Montag im Monat), Laufzeiten (Farben,
30/7 Tage, automatische Verlängerung), Kontaktformular (jeder Feldfehler DE/EN, Sicherheitsfrage mit falscher
Prüfsumme, Anfragebremse, ohne Konfiguration gesperrt, keine Speicherung), Mailversand mit nachgebildetem
SMTP-Server (keine echte Mail), Prüfskript mit Beispielwerten aus `/proc` und `docker inspect` (ohne echten Server),
keine Zugangsdaten in Logs oder Protokoll.

## 9. Entscheide Carsten 20.11.2026 (Fragen F1–F7)

| Nr. | Frage | Entscheid |
|---|---|---|
| F1 | Eintrag im Zeitplan (`cron`) des Servers für das Prüfskript | **Ja** (einmaliger Eintrag, nur diese Zeile; Befehl in `01`, Abschnitt 6, nach der Umsetzung) |
| F2 | Welche Container | **Nur unsere vier**; Traefik über „Website erreichbar“ |
| F3 | Kontaktformular | An `info@`; **beide Postfächer leiten an die private Adresse weiter** (M8) |
| F4 | „Fassung wartet auf Freigabe“ und „Entscheid offen“ als Alarm | **Ja** (Warnung) |
| F5 | Erinnerung | **Höchstens 3 Mails je Alarm, egal was sonst passiert** (bestätigt) |
| F6 | Laufzeiten | VPS KVM 1 bis 22.06.2027, Domain bis 23.10.2027, Postfach bis 20.11.2028; alle mit automatischer Verlängerung |
| F7 | Statusmail | **Montag 06:00** |

## 10. Umsetzung (Version 0.23)

| Teil | Datei |
|---|---|
| Mailversand, Testmail | `app/betrieb/mail.py` (nur Standardbibliothek) |
| Alarm-Zustand, Drosselung, höchstens 3 Mails | `app/betrieb/alarme.py` (nur Standardbibliothek) |
| Daten-Alarme | `app/betrieb/pruefungen.py`, aufgerufen jede Minute vom Dienst `soccer-import` (`importer/dienst.py`) |
| Statusmail | `app/betrieb/status.py` (Montag 06:00) |
| Laufzeiten | `app/config/laufzeiten.toml`, `app/betrieb/laufzeiten.py` |
| Server-Prüfskript | `tools/ueberwachen.py` (cron jede Minute; schreibt `import/server.json`, `import/ueberwachung.json`) |
| Einrichten auf dem Server | `tools/mail_einrichten.sh` (`01`, Abschnitt 6.6) |
| Testmails nach jedem Release | `tools/einspielen.sh`, Schritt 5 |
| Kontaktformular | `app/website/kontakt.py`, `vorschau.py` (POST), `vorlagen/inhalt/kontakt.*.html`, Texte `formular.*` |
| Dashboard | Reiter Datenimport/API: Blöcke Alarme, Server, Laufzeiten |
| Tests | `tests/test_betrieb_023.py` (B1–B8) |
