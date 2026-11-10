# Release: Version 0.11 – Neue Datenbank 2018/19–2026/27

**Stand:** 10.11.2026 · Version 0.11 · Briefing „Neue Datenbank 2018/19–2026/27 einführen“ (Freigabe Carsten 10.11.2026)

**Commit:** Version 0.11: Neue Datenbank 2018/19–2026/27, Referenzsaison und neue Saisonauswahl

## Was ändert sich?

- **Referenzsaison:** Die älteste Saison der Datenbank liefert nur die Vorsaison und wird nie ausgewertet (bisher fest 2020/21). Alle anderen Saisons werden ausgewertet, auch die laufende. Neues Modul `app/core/seasons.py`; KPI-Regelwerk 1.2.
- **Simulation, Saisonauswahl:** Aktuelle Saison (vorläufig) · **Alle Saisons** (voreingestellt) · Alle Saisons plus aktuelle · Letzte 2 … 6 Saisons · jede Saison einzeln (neueste zuerst). Die Referenzsaison erscheint nie; neues ⓘ an „Saisons“.
- **Datenqualität:** je Liga „Referenzsaison: … (nur Vorsaison, nicht ausgewertet) · Ausgewertet: …“; neue Warnung „Saison fehlt“, wenn zwischen zwei Saisons eine fehlt.
- **Häufigkeit der Anomalien:** weiterhin die letzte abgeschlossene Saison, aber nie die Referenzsaison.
- **Unverändert:** KPI-Formeln, Rundung, `schwellen.toml`, Ligaseiten, Top Anomalien. Nachweis: Vollvergleich vorher/nachher (Prüfprotokoll `docs/tests/pruefprotokoll_datenbank_2018-2027.md`, Teil B) mit 0 Abweichungen.
- **Neue Excel-Datei** (`451348b6…`, Saisons 2018/19–2026/27): geprüft und korrigiert (Prüfprotokoll Teil A). Kopie in `tests/referenz/`. Wird **nach** dem Einspielen des Codes aufgespielt (Schritt 2 unten).
- Doku: KPI-Regelwerk v2.4, Dashboard-Briefing v4.9, `02_Datenbasis.md` (4d), `01` Abschnitt 0 und 6.2 (Saisonwechsel), CHANGELOG.

## Ablauf

1. Code einspielen: `bash /docker/football-dashboard/tools/einspielen.sh github`.
2. Danach die neue Excel-Datei `Database-Soccer-Intelligence.xlsx` (SHA-256 `451348b6…`) nach `01`, Abschnitt 6.2 aufspielen (zuerst als `data/upload.xlsx` prüfen, dann austauschen).

## Erwartungswerte

- Git-Stand vorher: `249641d`.
- Tests beim Einspielen: rund **376 bestanden, 12 übersprungen** (bisher 350/12; neu 26 Tests in `tests/test_seasons.py`). Laufzeit rund 1,5 Minuten länger als bisher (lokal 3:35 statt 2:04).
- Prüfung von `data/upload.xlsx` (Schritt 2): **Fehler: 0 | Warnungen: 24 | Hinweise: 64**. Warnungen: 23 × „Schüsse < aufs Tor + daneben“ (davon 18 in 2018/19), 1 × LaLiga 2026/27 Spieltag 8 mit 9 von 10 Spielen (Nachholspiel).
- SHA-256 der neuen Datei: `451348b6550b91f4df3a26450a26d205e76f69c13ac520d080d3a427ff084904`.
- Referenzsaison in allen vier Ligen: 2018/19; ausgewertet 2019/20–2026/27.
- Simulation, erster Aufruf nach dem Aufspielen: rund 50 Sekunden (bisher rund 30), danach sofort.
- Ligaseiten und Top Anomalien: für bereits vorhandene Spiele dieselben Werte wie vorher (Vollvergleich, Teil B).

## Im Browser prüfen

Nach Schritt 1 (Code) mit der **alten** Datei:

1. **Datenqualität:** 0 Fehler; je Liga „Referenzsaison: 2020/21 (nur Vorsaison, nicht ausgewertet) · Ausgewertet: 2021/22–2026/27“.
2. **Simulation:** Saisonauswahl voreingestellt auf „Alle Saisons (2021/22–2025/26)“; Tabellen gleich wie vorher mit „Alle abgeschlossenen“.

Nach Schritt 2 (neue Excel-Datei):

1. **Datenqualität:** 0 Fehler, SHA-256 beginnt mit `451348b6`, je Liga „Referenzsaison: 2018/19 (nur Vorsaison, nicht ausgewertet) · Ausgewertet: 2019/20–2026/27“; Spiele je Saison ab 2018/19.
2. **Simulation:**
   - Die Saisonauswahl zeigt in dieser Reihenfolge: Aktuelle Saison (2026/27, vorläufig) · Alle Saisons (2019/20–2025/26) · Alle Saisons plus aktuelle (2019/20–2026/27, inkl. vorläufig) · Letzte 2 bis Letzte 6 Saisons · Saison 2025/26 bis Saison 2019/20.
   - Voreingestellt ist „Alle Saisons (2019/20–2025/26)“.
   - 2018/19 erscheint nirgends.
3. **Simulation, „Saison 2019/20“ wählen:** Es erscheinen Werte (neu auswertbar).
4. **Ligaseiten und Top Anomalien:** aktueller Spieltag wie gewohnt, keine Fehlermeldung.
