# Release: Version 0.23 – E-Mail, Alarme und Überwachung

**Stand:** 20.11.2026 · Version 0.23 · Spezifikation `docs/09_Betrieb_EMail.md` (Entscheide Carsten 20.11.2026: M1–M9, F1–F7)

**Commit:** Version 0.23: E-Mail, Alarme und Überwachung

## Was ändert sich?

- **Alarme per Mail** an `alert@` (Alias auf das Postfach `info@`, Absender „Soccer Intelligence Alarm“), über die Weiterleitung bei dir:
  - Import fehlgeschlagen
  - API-Kontingent
  - Schnappschuss
  - Datei-Prüfung („Daten werden geprüft“)
  - neue Daten warten auf Freigabe
  - Entscheid offen
  - Statistik fehlt dauerhaft
  - Laufzeit endet
  - Kontaktformular gescheitert

  Höchstens eine Mail pro Stunde je Alarmart, höchstens 3 Mails je Alarm, dazu „Behoben“, solange die 3 nicht aufgebraucht sind.
- **Server-Überwachung:** Ein Prüfskript läuft jede Minute auf dem Server und prüft:
  - Festplatte, Arbeitsspeicher, CPU
  - unsere vier Container
  - ob die Website erreichbar ist
  - ob der Import-Dienst lebt

  Die Schwellen sind deine (Warnung / Kritisch).
- **Statusmail jeden Montag um 06:00:** Läufe, Alarme, Server, Backups, Laufzeiten; am ersten Montag im Monat die Erinnerung an die Monatssicherung.
- **Laufzeiten im Dashboard:** VPS bis 22.06.2027, Domain bis 23.10.2027, Postfach bis 20.11.2028, API-Abo aus der API. Die Farbe zeigt, wie viel Zeit bleibt.
- **Kontaktformular aktiv:**
  - Versand über `info@`.
  - Fehler werden je Feld angezeigt.
  - Die Rechenaufgabe wechselt.
  - Höchstens 3 Nachrichten pro Stunde je Absender.
  - Nichts wird gespeichert.
- **Impressum** zeigt die Projektadresse `info@soccer-intelligence.com` (nach dem Einrichten).
- **Nach jedem Release** schickt das Einspiel-Skript über alle drei Wege eine Testmail (dein Wunsch).
- **Reiter Datenimport/API:**
  - neue Blöcke „Alarme“, „Server“ und „Laufzeiten“
  - in „Läufe heute“ stehen die Partien hinter „nach dem Spiel“ (dein Wunsch)

## Einspielen

Zuerst wie immer:

```bash
tmux new -s release023
```

```bash
bash /docker/football-dashboard/tools/einspielen.sh github
```

Beim ersten Mal meldet Schritt 5 „nur 0 von 3 Testmails gesendet“. Das ist richtig, der Versand ist noch nicht eingerichtet. Danach **einmalig** den Mailversand einrichten:

```bash
bash /docker/football-dashboard/tools/mail_einrichten.sh
```

Das Skript fragt das Passwort des Postfachs `info@` verdeckt ab (wie bei Hostinger festgelegt; `alert@` ist ein Alias und braucht keins), trägt alles in `.env` ein und startet die zwei betroffenen Container neu. Dann fragt es, ob das Prüfskript in den Zeitplan des Servers kommt: mit `j` bestätigen. Zum Schluss schickt es drei Testmails.

## Erwartungswerte

- Git-Stand vorher: `1701bc6`.
- Schritt 4: rund **715 bestanden, 16 übersprungen, 18 ausgelassen**, keine Fehler.
- Schritt 5: alle Container laufen, `/` = 200, `/dashboard/` = 200, `/vorschau/` = 401; Hinweis „nur 0 von 3 Testmails“ (beim ersten Mal).
- Dashboard-Fusszeile: „Version 0.23 – E-Mail, Alarme und Überwachung“.
- `mail_einrichten.sh`: „✅ Gespeichert in .env“, „✅ Neu gestartet“, „✅ Eingetragen: * * * * * …“ und drei Zeilen „✅ Testmail …: gesendet“.

## Im Browser prüfen

1. **Posteingang (Yahoo):** drei Mails „[Soccer Intelligence] Testmail – …“ (Container soccer-import an alert@, Container soccer-vorschau an info@, Prüfskript auf dem Server an alert@). Bitte auch im Spam-Ordner nachsehen.
2. **Dashboard, Reiter Datenimport/API:**
   - Block „Alarme“: „Mailversand: funktioniert“. Das erscheint erst, wenn eine Alarm-Mail verschickt wurde; vorher steht „noch keine Mail“.
   - Block „Server“: Messwerte, nach einer Minute ohne roten Hinweis.
   - Block „Laufzeiten“: VPS, Domain, Postfach, API-Abo.
   - „Läufe heute“ mit Partien.
3. **Kontaktformular** (`/vorschau/de/kontakt/`):
   - Absenden ohne Angaben: rote Fehler je Feld.
   - Dann richtig ausfüllen und senden: „Danke, deine Nachricht ist angekommen.“ und eine Mail „Kontaktformular: …“ im Posteingang. Mit „Antworten“ geht die Antwort an die eingegebene Adresse.
4. **Impressum:** zeigt `info@soccer-intelligence.com`.
5. **Am Montag um 06:00** kommt die erste Statusmail „Wochenstatus KW …“.
6. Sag mir, ob alles passt.
