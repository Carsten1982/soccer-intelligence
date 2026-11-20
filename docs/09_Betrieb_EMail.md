# Soccer Intelligence – E-Mail, Alarme und Überwachung (Spezifikation)

**Version 0.1** · Stand 20.11.2026 · **Status: Entwurf zur Freigabe durch Carsten** · Umsetzung mit Version 0.23

Diese Datei ist die einzige Stelle für den Mailversand, die Alarme, die wöchentliche Statusmail, die
Server-Überwachung, die Laufzeiten (Abos, Domain, Postfach) und den Versand des Kontaktformulars. Grundlage: Entscheide
Carsten vom 20.11.2026 (Zuschnitt 0.22/0.23/0.24, Postfächer, Alarmliste, Statusmail, Spamschutz).

---

## 1. Entscheide (Carsten 20.11.2026)

| Nr. | Thema | Entscheid |
|---|---|---|
| M1 | Postfächer | Bei Hostinger eingerichtet: `info@soccer-intelligence.com` (allgemeine Mails, Kontaktformular, Impressum) und `alert@soccer-intelligence.com` (Alarme, Weiterleitung an die private Adresse). Postfach gültig bis 20.11.2028. |
| M2 | Was kommt per Mail | **Nur Alarme** und **eine Statusmail pro Woche** (Beweis, dass alles läuft). Keine tägliche Sammelmail. |
| M3 | Daten-Alarme (sofort) | Import fehlgeschlagen · API-Kontingent fast aufgebraucht · Schnappschuss fehlt · Datei-Prüfung gescheitert (Website zeigt „Daten werden geprüft“). |
| M4 | Server-Alarme (Warnung / Kritisch) | Festplatte über 85 % / über 95 % · Arbeitsspeicher über 90 % für 15 Minuten / über 95 % für 5 Minuten · CPU über 90 % für 30 Minuten / – · Docker-Container mehr als 3 Neustarts in 10 Minuten / länger als 5 Minuten nicht verfügbar. |
| M5 | Häufigkeit | Je Alarmart höchstens eine Mail pro Stunde; ist das Problem behoben, eine Mail „Behoben“. |
| M6 | Kontaktformular | Versand per Mail, keine Speicherung (Beschluss 8, 19.11.2026). Spamschutz: Rechenaufgabe, verstecktes Feld, höchstens 3 Nachrichten pro Stunde je Absender – reicht für den Anfang. |
| M7 | Laufzeiten | Im Dashboard verfolgen: API-Football-Abo (aus der API), Domain (bis 23.10.2027, automatische Verlängerung an), Postfach (bis 20.11.2028). |

## 2. Mailversand (Technik)

- **Ein Absender je Zweck:** Alarme und Statusmail von `alert@`, Kontaktformular von `info@`. Versand über SMTP von
  Hostinger mit SSL (`smtp.hostinger.com`, Port 465 – beim Einrichten zu bestätigen).
- **Empfänger:** Alarme und Statusmail an `alert@` selbst; das Postfach leitet an die private Adresse weiter (M1).
  So steht die private Adresse nirgends im Programm, auch nicht in `.env`. Kontaktformular an `info@` (Frage F3).
- **Zugangsdaten nur in `.env`** auf dem Server (nie in Git, Code, Logs oder Chat):
  `SI_SMTP_HOST`, `SI_SMTP_PORT`, `SI_ALERT_USER`, `SI_ALERT_PASSWORT`, `SI_INFO_USER`, `SI_INFO_PASSWORT`. Eintragen
  mit einem Befehl wie beim API-Schlüssel (Passwort wird nicht angezeigt, vorher Kopie von `.env` nach `backup/`).
  Die Befehle stehen nach der Umsetzung in `01`, Abschnitt 6.
- **Fehlt die Konfiguration**, wird nichts versendet; das Dashboard zeigt „Mailversand nicht eingerichtet“, die Website
  zeigt beim Kontaktformular den heutigen Hinweis (Versand gesperrt).
- **Scheitert der Versand** (Server nicht erreichbar, Passwort falsch): Eintrag im Ereignisprotokoll, Hinweis im
  Dashboard, neuer Versuch beim nächsten Anlass. Eine fehlende Statusmail am Montag ist das Zeichen, dass der Versand
  selbst gestört ist.
- **Testmail:** `docker exec soccer-import python -m betrieb.mail --test` schickt eine Testmail an `alert@`. Das
  Einspiel-Skript bietet sie nach dem Einspielen von 0.23 an.
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
| Laufzeit endet | API-Abo, Domain oder Postfach: 30 Tage vorher Warnung, 7 Tage vorher Kritisch; bei automatischer Verlängerung nur ein Hinweis in der Statusmail | Warnung / Kritisch |

### 3.2 Server-Alarme (Prüfskript auf dem Server)

| Alarm | Warnung | Kritisch | Gemessen |
|---|---|---|---|
| Festplatte | über 85 % belegt | über 95 % belegt | Partition mit `/docker/football-dashboard/` |
| Arbeitsspeicher | über 90 % während 15 Minuten | über 95 % während 5 Minuten | verfügbarer Speicher (`MemAvailable`) |
| CPU | über 90 % während 30 Minuten | – | Auslastung aller Kerne |
| Container | mehr als 3 Neustarts in 10 Minuten | länger als 5 Minuten nicht verfügbar (gestoppt oder „unhealthy“) | `football-dashboard`, `soccer-import`, `soccer-vorschau`, `soccer-placeholder` |
| Website erreichbar | – | länger als 5 Minuten nicht erreichbar: `/` nicht 200, `/dashboard/` nicht 200, `/vorschau/` nicht 401 | Abruf von aussen über Traefik (deckt auch einen Ausfall von Traefik ab, ohne ihn anzufassen) |
| Import-Dienst lebt | – | `soccer-import` meldet sich seit über 15 Minuten nicht (Lebenszeichen-Datei) | Datei `import/lebenszeichen` |

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
- **Erinnerung** alle 24 Stunden, solange ein Alarm besteht *(Frage F5)*.
- Ist das Problem behoben, eine Mail **„BEHOBEN: …“** mit Dauer.
- Alle Alarme und Mails stehen im Ereignisprotokoll (`import/ereignisse.jsonl`) und im Reiter Datenimport/API
  (Block „Alarme“: offene Alarme, letzte 14 Tage).

## 4. Wöchentliche Statusmail (M2)

**Jeden Montag um 08:00** von `soccer-import` an `alert@`, Betreff `[Soccer Intelligence] Wochenstatus KW 48`.

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
  automatische Verlängerung ja/nein. Erste Einträge: Domain `soccer-intelligence.com` 23.10.2027 (automatisch),
  E-Mail-Postfach 20.11.2028 (*Verlängerung: Frage F6*), VPS (*Frage F6*). Das API-Abo kommt wie heute aus der API.
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
  steht in einem versteckten Feld mit Prüfsumme (Geheimnis `SI_FORMULAR_GEHEIMNIS` in `.env`), damit niemand die
  Antwort mitschicken kann.
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

## 9. Fragen an Carsten vor der Umsetzung

- **F1 Zeitplan des Servers:** Das Prüfskript braucht einen einmaligen Eintrag im Zeitplan (`cron`) des Servers –
  das ist eine Änderung ausserhalb unseres Ordners (Schutzregel 1). Den Befehl gebe ich dir; er fügt nur diese eine
  Zeile hinzu und lässt alle anderen Einträge unverändert. Einverstanden? *Vorschlag: ja.* (Alternative ohne Eintrag
  ausserhalb des Ordners gibt es nicht ohne Zugriff des Containers auf Docker selbst – das wäre praktisch Vollzugriff
  auf den Server, das will ich nicht.)
- **F2 Welche Container überwachen?** *Vorschlag:* nur unsere vier; andere (Traefik, n8n, article-generator) nicht,
  ein Ausfall von Traefik fällt über „Website erreichbar“ auf.
- **F3 Kontaktformular an `info@`:** Leitet `info@` ebenfalls an deine private Adresse weiter (in deiner Tabelle steht
  die Weiterleitung nur bei `alert@`)? *Vorschlag:* Weiterleitung auch für `info@` einrichten, sonst liest du
  Kontaktnachrichten nur im Webmail von Hostinger.
- **F4** Sollen „Fassung wartet auf Freigabe“ und „Entscheid offen“ ebenfalls als Alarm (Warnung) kommen? Beide brauchen
  dich. *Vorschlag: ja.*
- **F5 Erinnerung** alle 24 Stunden, solange ein Alarm besteht? *Vorschlag: ja.*
- **F6 Laufzeiten:** Verlängert sich das Postfach automatisch? Soll der VPS aufgenommen werden (Ablaufdatum)?
- **F7 Statusmail** Montag 08:00 – passt die Zeit?
