# Release: Version 0.19 – Auffälligkeit und Prognosewert (statt leicht/stark)

**Stand:** 18.11.2026 · Version 0.19 · Spezifikation und Freigabe Carsten 18.11.2026 · Regeln: KPI-Regelwerk v2.7 (2.2, 2.6, 11), Dashboard-Briefing v5.6, Prüfprotokoll `docs/tests/pruefprotokoll_prognosewert.md`

**Commit:** Version 0.19: Auffälligkeit und Prognosewert statt leicht/stark – Schwellen je Liga, KPI und Richtung

## Was ändert sich?

- **Ein Spiel ist auffällig oder nicht.** Statt „leicht“ und „stark“ gibt es je Liga, Kennzahl und Richtung (mehr/weniger) höchstens **eine Schwelle**, und jede Auffälligkeit trägt einen **Prognosewert**: hoch, mittel oder gering. Kombinationen ohne Schwelle werden nie ausgezeichnet.
- **Neue `app/config/schwellen.toml`** mit den freigegebenen **23 Schwellen** (16 hoch, 6 mittel, 1 gering; Saisons 2019/20–2025/26) samt Herleitung je Zeile. Die alte Datei liegt in `app/config/archiv/schwellen_2026-11-14.toml`; das alte Format wird abgelehnt.
- **Top Anomalien** (Dashboard und Startseite der Vorschau): zuerst „hoch“, dann „mittel“, dann „gering“, jeweils nach der grössten Abweichung; **höchstens zwei Spiele je Liga** (Liga-Mix, aufgefüllt, wenn die anderen Ligen nicht genug haben); weniger als vier, wenn nicht genug auffällig sind. Hinweise „Aktuell nur x auffällige Spiele.“ und „Ergänzt mit Spielen geringer Verlässlichkeit.“
- **Ligaseiten und Top-Karten:** Kreise in drei Grüntönen (hoch dunkel, mittel, gering hell), Legende „Prognosewert: hoch, mittel, gering, nicht auffällig“, in den Details eine Zeile zur Herleitung (Schwelle, Trefferquote, Vergleichsgruppe).
- **Sensitivitätsanalyse:** zwei Zeilen je Kennzahl (mehr, weniger) mit je einer Schwelle, neue Spalte **Prognosewert**, kürzere Kurzhilfen, neues **Erklärfeld** unter der Tabelle (Beispiel Bundesliga Schüsse aufs Tor weniger, aufklappbare Felder) und Knopf **„Schwellenvorschlag berechnen“** mit Download als `schwellen.toml` (nur Anzeige, nichts wird gespeichert).
- **Datenqualität:** Reiter „Schwellen und Häufigkeit“ mit der Tabelle „Gültige Schwellen und Prognosewerte“ (23 Zeilen) und der Häufigkeit nach hoch/mittel/gering.
- **Vorschau der Website:** Daten und Texte mit Prognosewert („Prognosewert hoch“ usw.); **Gestaltung unverändert** (hoch wie bisher „stark“, mittel und gering wie bisher „leicht“) bis zum eigenen Design (Release B).
- **KPI-Berechnung unverändert:** alle Werte, Referenzen und Texte wie in 0.18 (Vollvergleich, Prüfprotokoll Abschnitt 4).
- Die Darstellung im Dashboard ist ein Zwischenstand bis zu deinem Designentwurf (Design-Briefing vom 18.11.2026).

## Einspielen

Wie immer in `tmux`: `bash /docker/football-dashboard/tools/einspielen.sh github`, mit `j` abschliessen, wenn alles passt. Keine Zusatzschritte. Die Schwellendatei kommt mit GitHub; am Server ist nichts von Hand zu ändern.

## Erwartungswerte

- Git-Stand vorher: `fbdd5d9`.
- Schritt 4 des Einspielens: rund **587 bestanden, 15 übersprungen, 17 ausgelassen** (langsame Tests), keine Fehler; Dauer rund 9 Minuten.
- Schritt 5: „Container laufen (Dashboard, Import, Vorschau) · / = 200 · /dashboard/ = 200 (Anmeldemaske)“ und „/vorschau/ = 401 (Passwortabfrage der Vorschau)“.
- Dashboard-Fusszeile: „Version 0.19 – Prognosewert (Auffälligkeit statt leicht/stark)“.
- **Datenqualität → Schwellen und Häufigkeit:** 23 Zeilen, z. B. Bundesliga · Schüsse aufs Tor · weniger · −10,00 % · hoch · 227 Spiele · 63,44 % · 51,57 % · +11,87.
- **Sensitivitätsanalyse → „Schwellenvorschlag berechnen“** mit „Alle Saisons“ (2019/20–2025/26): genau dieselben 23 Kombinationen wie die gültige Datei (lokal mit der echten Datenbank des Probelaufs geprüft).
- Häufigkeit (Mittel je Liga-Spieltag, Saisons 2019/20–2025/26): Spiele mit „hoch“ Bundesliga 1,4 · Premier League 2,6 · Serie A 4,8 · La Liga 3,6.
- Lokal mit den echten Dateien des Probelaufs (Stand 15.11.) am Sa 21.11. 10:00: Startseite 1. Barcelona – Villarreal (Über 2,5 Tore +56,00 %), 2. Racing Santander – Real Sociedad (+54,00 %), 3. Monza – Fiorentina (+50,00 %), 4. AC Milan – Frosinone (+42,00 %), alle „Prognosewert hoch“, je zwei aus La Liga und Serie A. Mit den neueren Daten auf dem Server können die Spiele abweichen.

## Im Browser prüfen

Falls eine Seite alt aussieht: einmal **Strg+F5** (Zwischenspeicher des Browsers).

1. **Top Anomalien:** bis zu 4 Karten, je Karte „Auffällig · Prognosewert hoch“ (bzw. mittel/gering) und eine Zeile zur Herleitung; höchstens zwei Spiele aus derselben Liga (ausser die anderen Ligen haben zu wenig).
2. **Eine Ligaseite** (z. B. Bundesliga): Legende „Prognosewert: hoch, mittel, gering, nicht auffällig“; Kreise in drei Grüntönen, nicht auffällige mit hellem Ring. Details einer Kennzahl aufklappen: Herleitungszeile. In der Bundesliga gibt es „gering“ nur bei Gelben Karten (mehr).
3. **Datenqualität → Schwellen und Häufigkeit:** Tabelle mit 23 Zeilen (siehe Erwartungswerte), Häufigkeit mit den Spalten hoch, mittel, gering.
4. **Sensitivitätsanalyse:** je Kennzahl zwei Zeilen (mehr, weniger), Spalte Prognosewert (farbige Kennzeichnung bzw. grauer Grund), Kurzhilfen ⓘ kurz mit „Mehr Details findest du unter der Tabelle.“ Darunter das Erklärfeld mit dem Beispiel Bundesliga Schüsse aufs Tor weniger (227 Spiele, 63,44 %, 51,57 %, +11,87 Pp.) und die aufklappbaren Felder. Eine einzelne Saison wählen: Prognosewert „–“, grau, „nur bei mehreren Saisons“. „↺ Auf gültige Schwellen zurücksetzen“ stellt die Vorbelegung wieder her.
5. **„Schwellenvorschlag berechnen“** (Saison „Alle Saisons“): Tabelle mit 23 Zeilen = Datenqualität; Download „Vorschlag als schwellen.toml herunterladen“ funktioniert.
6. **Vorschau** (`/vorschau`): Startseite-Ranking mit „Prognosewert hoch“; Spieltag mit Legende und Kacheln wie bisher gestaltet; Matchdetail eines ausgezeichneten Spiels mit „Prognosewert …“.
7. Sag mir, ob die Texte der Sensitivitätsanalyse verständlich sind und was im Designentwurf anders werden soll.
