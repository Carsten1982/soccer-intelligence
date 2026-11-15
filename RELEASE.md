# Release: Version 0.14 – Datenimport über API-Football

**Stand:** 15.11.2026 · Version 0.14 · Spezifikation `06_Datenlieferung.md` v0.5 und Designentwurf „Datenimport/API“ (Freigabe Carsten 15.11.2026)

**Commit:** Version 0.14: Datenimport über API-Football (Container soccer-import, Reiter Datenimport/API)

## Was ändert sich?

- **Neuer Container `soccer-import`:** holt Montag bis Freitag um 04:00 die Spiele und den Spielplan von API-Football und legt eine **neue Fassung** von Datenbank und Spielplan bereit. Die gültigen Dateien ändern sich erst nach Ihrer Freigabe.
- **Neuer Reiter „Datenimport/API“** (ganz rechts): Statusleiste (Abo, Kontingent, letzter/nächster Lauf, Betriebsart), Kasten „Neue Daten bereit“ mit Vollständigkeit, Qualitätsbericht, Korrekturen, neuen Spielen, Spielplan-Änderungen, Buttons **Übernehmen** und **Verwerfen**, Protokoll der letzten 14 Tage.
- **Erste Übernahme:** stellt Datenbank und Spielplan auf die **Teamnamen von API-Football** um (z. B. „Bayern München“, „1. FC Köln“) und erzeugt den Spielplan der ganzen Saison aus der API.
- Spielplan kennt den Status **„abgebrochen“**.
- `einspielen.sh` baut jetzt beide Container (`football-dashboard` und `soccer-import`).

## Vor dem Einspielen (einmalig): API-Schlüssel in `.env`

Befehl in `01`, Abschnitt 6.5 („Schlüssel eintragen“). Erwartet: `1`; der Schlüssel erscheint nicht auf dem Bildschirm.

## Erwartungswerte

- Git-Stand vorher: `3f44fa1`. Der Pull Request enthält auch die Doku „bereinigte Datenbank aktiv“.
- Tests beim Einspielen: **438 bestanden, 15 übersprungen** (bisher 428 / 12).
- Schritt 5 meldet: „Container laufen (Dashboard und Import)“; `docker ps` zeigt zusätzlich `soccer-import`.
- **Erster Lauf von Hand** (sonst Montag 04:00):
  ```bash
  docker exec soccer-import python -m importer.dienst --jetzt
  ```
  Erwartet nach rund 30–60 Sekunden: `Lauf <Datum> -> wartet`.

## Im Browser prüfen

1. **Reiter „Datenimport/API“:** Statusleiste „API-Football · Pro, Abo gültig bis 15.02.2027“, Betriebsart „halbautomatisch“.
2. **Kasten „Neue Daten bereit“:** 0 Fehler; aufklappbar „Teamnamen umgestellt auf API-Football (rund 30 Teams) – einmalig“; Spielplan-Änderungen (beim ersten Lauf viele, weil der Spielplan jetzt die ganze Saison aus der API enthält); Vollständigkeit je Liga „vollständig“.
3. **Übernehmen** klicken → Hinweis „Freigabe hinterlegt“. Nach einer Minute Seite neu laden: „Keine neuen Daten zur Freigabe“, im Protokoll Status „übernommen“.
4. **Ligaseite Bundesliga:** neue Teamnamen (z. B. „Bayern München“, „1. FC Köln“), aktueller Spieltag aus dem neuen Spielplan, KPIs wie gewohnt.
5. **Datenqualität:** Datenbank 0 Fehler; Spielplan 0 Fehler.
6. Falls etwas nicht stimmt: **Verwerfen** statt Übernehmen; nach einer Übernahme Rückweg mit `backup/*_vor_import.xlsx` (`01`, Abschnitt 6.5).
