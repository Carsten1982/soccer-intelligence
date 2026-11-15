# Release: Version 0.14.1 – Teamnamen mit Akzenten, Einspielen nach Abbruch

**Stand:** 15.11.2026 · Version 0.14.1 · Auftrag Carsten 15.11.2026 („Düsseldorf mit ü“, „Teams darfst Du umschreiben“)

**Commit:** Version 0.14.1: Teamnamen mit ü und Akzenten, Einspielen nach Abbruch

## Was ändert sich?

- **Teamnamen:** 10 Teams mit ü bzw. Akzent – Fortuna Düsseldorf, 1. FC Nürnberg, SpVgg Greuther Fürth, Alavés, Almería, Atlético Madrid, Cádiz, Deportivo La Coruña, Leganés, Málaga. Die Umbenennung macht der nächste Lauf des Imports; sie wird erst mit „Übernehmen“ gültig.
- **Einspielen:** Bricht ein Lauf nach dem Holen von GitHub ab, macht der nächste Aufruf mit Tests und Neubau weiter (statt „Nichts Neues“). Einspielen künftig immer in `tmux` (`01`, Abschnitt 6.1).
- **Protokoll im Reiter:** Status ohne Doppelung, z. B. „übernommen: 15.11.2026 14:37 (Dashboard)“.

## Erwartungswerte

- Git-Stand vorher: `8260056`.
- Tests beim Einspielen: rund **443 bestanden, 12 übersprungen** (Server zuletzt 441 / 12), keine Fehler.
- Schritt 5: „Container laufen (Dashboard und Import)“.
- Danach Lauf von Hand:
  ```bash
  docker exec soccer-import python -m importer.dienst --jetzt
  ```
  Erwartet: `Lauf … -> wartet`.

## Im Browser prüfen

1. **Datenimport/API → Neue Daten bereit:** 0 Fehler; aufklappbar „Teamnamen umgestellt auf API-Football“ mit den Teams oben, deren Spiele in der Datenbank stehen (bisher ohne Akzent → neu mit Akzent). Spielplan-Änderungen nur bei diesen Teams (Atlético Madrid, Alavés, Deportivo La Coruña, Málaga, Leganés usw. in LaLiga 2026/27), entfallen 0.
2. **Übernehmen**, nach einer Minute neu laden: Status „übernommen“.
3. **LaLiga, aktueller Spieltag:** „Atlético Madrid“, „Alavés“, „Deportivo La Coruña“, „Málaga“ mit Akzent; KPI-Werte unverändert.
4. **Fusszeile:** „Version 0.14.1 – Datenimport“.
