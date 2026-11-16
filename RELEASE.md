# Release: Version 0.15.2 (Nachtrag) – Seitentest mit Anmeldung

**Stand:** 16.11.2026 · Version 0.15.2 · Nachtrag nach dem gestoppten ersten Einspielversuch

**Commit:** Version 0.15.2, Nachtrag: Seitentest der Startseite meldet sich an

## Was ändert sich?

- **Grund:** Der erste Einspielversuch von 0.15.2 (16.11.2026) stoppte in Schritt 4 an einem einzigen Test (`test_app_start_page_top_anomalien`, 477 bestanden, 1 Fehler). Der Test startet das ganze Dashboard mit den echten Excel-Dateien und stand seit 0.15.2 vor der Anmeldemaske. Er läuft nur auf dem Server (die Excel-Dateien fehlen auf GitHub), darum fiel er vorher nicht auf. Das Dashboard selbst war in Ordnung; in Betrieb genommen wurde nichts.
- **Korrektur:** Der Test meldet sich mit einem Test-Zugang an (nur im Test, nicht der echte). Ein neuer Test prüft auch ohne Excel-Dateien – also lokal und auf GitHub –, dass diese Anmeldung an der Maske vorbeikommt.
- **Warum liefen alle Tests (20 Minuten)?** Ein laufender Aufruf von `einspielen.sh` arbeitet mit der Fassung zu Ende, mit der er gestartet wurde. Die neue Fassung (nur schnelle Tests) lag nach Schritt 3 bereit und gilt ab jetzt.
- Die Angaben zu 0.15.2 (Anmeldemaske, 12 Stunden, „Abmelden“, Sperre nach 5 Fehlversuchen) gelten unverändert. Der Zugang ist bereits in `.env` gesetzt (16.11.2026); nicht erneut nötig.

## Erwartungswerte

- Git-Stand vorher: `9a3d0ff` (geholt, aber nicht in Betrieb; in Betrieb ist noch 0.15.1).
- Schritt 4: „Tests (rund 5 Minuten, Wegwerf-Container)“ und „Bitte warten und nichts drücken“ (Anzeige noch aus der Fassung `9a3d0ff`; tatsächlich rund 8 Minuten). Ergebnis rund **463 bestanden, 15 übersprungen, 16 ausgelassen** (langsame Tests), keine Fehler.
- Schritt 5 meldet: „Container laufen (Dashboard und Import) · / = 200 · /dashboard/ = 200 (Anmeldemaske)“.

## Im Browser prüfen

1. `https://soccer-intelligence.com/dashboard` öffnen: **keine** Passwortabfrage des Browsers mehr, sondern die Maske „Soccer Intelligence – Internes Dashboard – bitte anmelden“.
2. Mit falschem Passwort: „Benutzername oder Passwort falsch.“
3. Mit richtigem Benutzernamen und Passwort: Top Anomalien erscheinen; unten auf der Seite „Abmelden“.
4. Seite neu laden: Sie bleiben angemeldet.
5. „Abmelden“ klicken: wieder die Maske.
6. Fusszeile: „Version 0.15.2 – Anmeldung“.
7. Wenn möglich auf dem Bank-Arbeitsrechner ausprobieren.
