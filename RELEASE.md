# Release: Doku und bereinigte Datenbank (Vollvergleich API-Football)

**Stand:** 15.11.2026 · Version bleibt 0.13 · Kein Code geändert · Neue Datenbank zum Aufspielen · Auftrag Carsten 15.11.2026

**Commit:** Doku: Vollvergleich API-Football und bereinigte Datenbank (3a258961)

## Was ändert sich?

- **Doku:** Prüfprotokoll `docs/tests/pruefprotokoll_api.md` (neu), `02_Datenbasis.md` Abschnitt 4e, Spezifikation `06_Datenlieferung.md` v0.4, `01` Abschnitt 0, CHANGELOG.
- **Datenbank** (nicht in Git, separat von Claude geliefert): `Database-Soccer-Intelligence.xlsx`, bereinigt mit zwei Quellen: 453 Gelbe Karten, 147 Schüsse gesamt, 83 Schüsse aufs Tor, 35 Ecken, Tore LaLiga 2025/26 Spieltag 37, 76 offizielle Spieltage; 146 neue Einträge im Blatt *Datenhinweise*. Änderungsprotokoll `Aenderungsprotokoll.csv`.
- KPI-Werte ändern sich leicht, am meisten bei KPI 04 (Gelbe Karten): 950 von 11'978 Einstufungen.

## Erwartungswerte

- Git-Stand vorher: `7b23f81`. Nur Doku: auf dem Server ist für den Pull Request nichts einzuspielen.
- **Neue Datenbank:** SHA-256 `3a2589616b2b0625d3a9150484bd0ce24e6340b334756b115d0d4582925822a8`.
- **Prüfung der hochgeladenen Datei** (`01`, Abschnitt 6.2, Schritt 2): **Fehler 0 · Warnungen 35 · Hinweise 201** (bisher 0 / 24 / 64). Neu sind 11 Warnungen „Schüsse < aufs Tor + daneben“ (bekannt, `02` Abschnitt 4e).

## Im Browser prüfen

1. **Datenqualität → Datenbank:** Prüfsumme beginnt mit `3a258961`; 0 Fehler, 35 Warnungen, 201 Hinweise.
2. **Datenqualität → Häufigkeit der Anomalien, Bundesliga 2025/26:** KPI 04 leicht **69**, stark **13** (bisher 82 / 14).
3. **Sensitivitätsanalyse** (Alle Ligen, Alle Saisons): KPI 04 stark positiv **214** Spiele, Mehrwert **+6,45**, „Funktioniert leicht“; KPI 02 leicht positiv **683** Spiele, Mehrwert **+8,05**.
4. **LaLiga, Saison 2025/26, Spieltag 37** (falls aufrufbar): z. B. Real Sociedad – Valencia 3:4.
