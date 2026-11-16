# Release: Version 0.15.2 – Anmeldemaske und kürzeres Einspielen

**Stand:** 16.11.2026 · Version 0.15.2 · Entscheidungen Carsten 16.11.2026 (L1–L4, kürzeres Einspielen)

**Commit:** Version 0.15.2: Anmeldemaske statt Browser-Passwortabfrage, Einspielen mit schnellen Tests

## Was ändert sich?

- **Anmeldemaske:** Statt der Passwortabfrage des Browsers zeigt das Dashboard eine eigene Maske mit **Benutzername** und **Passwort**. Danach bleiben Sie **12 Stunden** angemeldet; unten auf jeder Seite gibt es **„Abmelden“**. Nach 5 falschen Versuchen ist die Anmeldung 15 Minuten gesperrt.
- **Zugangsdaten** stehen nur in `.env` auf dem Server (Benutzername und Passwort-Hash), nie im Code oder auf GitHub.
- **Einspielen kürzer:** Auf dem Server laufen nur noch die schnellen Tests (rund 5 statt 25 Minuten). Die langsamen laufen weiterhin bei jedem Pull Request auf GitHub.

## Vor dem Einspielen (einmalig): Zugang setzen

Nach dem Zusammenführen auf GitHub, **vor** dem Einspielen: Befehl aus `01`, Abschnitt 6.3 („Vor dem ersten Einspielen von 0.15.2“). Er fragt Benutzername und Passwort (verdeckt, zweimal, mindestens 10 Zeichen). Erwartet: „Gespeichert in .env (Benutzer: …, Passwort nur als Hash).“ Ohne diesen Schritt bleibt das Dashboard nach dem Einspielen gesperrt (Hinweis „Anmeldung nicht eingerichtet“) – dann den Schritt nachholen und `docker compose up -d football-dashboard`.

## Erwartungswerte

- Git-Stand vorher: `88a3066`.
- Tests beim Einspielen: **nur die schnellen**, rund **464 bestanden, 13 übersprungen, 16 ausgelassen** (langsame Tests), keine Fehler; Dauer rund 5 Minuten.
- Schritt 5 meldet: „Container laufen (Dashboard und Import) · / = 200 · /dashboard/ = 200 (Anmeldemaske)“.

## Im Browser prüfen

1. `https://soccer-intelligence.com/dashboard` öffnen: **keine** Passwortabfrage des Browsers mehr, sondern die Maske „Soccer Intelligence – Internes Dashboard – bitte anmelden“.
2. Mit falschem Passwort: „Benutzername oder Passwort falsch.“
3. Mit richtigem Benutzernamen und Passwort: Top Anomalien erscheinen; unten auf der Seite „Abmelden“.
4. Seite neu laden: Sie bleiben angemeldet.
5. „Abmelden“ klicken: wieder die Maske.
6. Fusszeile: „Version 0.15.2 – Anmeldung“.
7. Wenn möglich auf dem Bank-Arbeitsrechner ausprobieren.
