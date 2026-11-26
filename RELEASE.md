# Release: Version 0.29 – Englische Texte

**Stand:** 26.11.2026 · Version 0.29 · Release_14 des Design-Chats (Design 571), Entscheide Carsten 26.11.2026

**Commit:** Version 0.29: Englische Texte nach Release_14

## Was ändert sich?

- **Englisch:** «anomaly» heisst jetzt überall **«standout statistic(s)»** (Chips, Gruppen, Legenden, Box «Standout threshold», Startseite, Spieltag, Spielseite, Auswertung, Methodik, Glossar, Title/Description). «metric» im Fliesstext → «statistic»; die Gruppe «Metrics» bleibt.
- **Neue Standard-Sätze:** Signalqualität (S1), Footer «Statistical analysis, not betting advice. Not affiliated with any leagues or clubs.» (S2), Hinweis zu Wetten «… no betting advice or predictions of winnings.» (S3); dazu «when making your own predictions», «average for that league», «data-driven», «Both teams scoring expected more/less often», Methodik Ebene 3 (Erwartung, Unsicherheit, Mindestanforderungen, «overall rate»).
- **Deutsch, Methodik Ebene 3:** «letzte 10 Ligaspiele **jeder Mannschaft**» und neuer Satz zur Spanne (D1, D2). Alles andere im Deutschen unverändert.
- Keine Änderung an Layout, Daten, Berechnung oder Adressen.

## Einspielen

Pull Request zusammenführen („Squash and merge“, Tests grün), dann:

```bash
bash /docker/football-dashboard/tools/einspielen.sh github
```

## Erwartungswerte

- Tests rund **778 bestanden**, keine Fehler. Dashboard-Fusszeile: „Version 0.29 – Englische Texte“.
- Schritt 5 wie bisher (`/` = 301, `/de/` = 200, `/vorschau/` = 401), drei Testmails.

## Im Browser prüfen

1. `/en/` (Startseite): Legende Signalqualität mit dem neuen Satz, Footer «Statistical analysis, not betting advice. Not affiliated with any leagues or clubs.»
2. `/en/matchday/bundesliga/`: Legende «These are standout matches.», Kacheln ohne Auffälligkeit «No standout statistics».
3. Eine englische Spielseite: Gruppen «Standout statistics» / «No standout statistics», Box «Standout threshold»; auf dem Handy sauberer Umbruch.
4. `/en/methodology/` Ebene 3 und `/de/methodik/` Ebene 3 («jeder Mannschaft», Satz zur Spanne).
5. `/en/glossary/`: «Standout statistic», «Statistics».
