# Release: Version 0.21.2 – Entwürfe vom 20.11., zweite Lieferung

**Stand:** 20.11.2026 · Version 0.21.2 · Releasepaket vom 20.11.2026 (Entwürfe Main_P1, Spieltag_P1, Spiel_P1, Methodik_10; Template-Briefing; Entscheidungsprotokoll Beschluss 13)

**Commit:** Version 0.21.2: Entwürfe vom 20.11., zweite Lieferung

## Was ändert sich?

Nur die Website-Vorschau, am Dashboard und an den Berechnungen ändert sich nichts.

- **Spielseite:** Unten steht jetzt die grüne Schaltfläche „Alle Spiele des Spieltags“, darunter der unterstrichene Textlink „Wie entstehen diese Werte?“. Gegenüber 0.21.1 sind die Rollen also wieder getauscht. Der Hinweis zur Zeitzone entfällt auf der Spielseite.
- **Spieltag:** Im dunklen Kopfbereich fehlt die Zeile „Aktueller Datenstand: …“; der Datenstand steht in der Fusszeile. Der Kopfbereich ist dadurch niedriger.
- **Startseite:**
  - Die SEO-Box „Was ist Soccer Intelligence?“ ist ein eigener Block nach „Von einem Fußballfan gebaut“. Optisch ändert sich wenig.
  - In den Karten „Die auffälligsten Spiele“ bleibt der Signalqualität-Chip auf dem Handy immer neben der Kennzahl; ein langer Name bricht um.
- **Methodik:** Die Schaltfläche heisst „Weiter mit Zahlen: Ein Spiel durchgerechnet“, auf Englisch „Continue with numbers: a worked example“. Auf dem Computer steht sie in einer Zeile. Auf dem Handy ist sie höchstens 300 px breit und bricht fest nach dem Doppelpunkt um.

## Einspielen

Wie immer in `tmux`, mit neuem Sitzungsnamen:

```bash
tmux new -s release0212
```

```bash
bash /docker/football-dashboard/tools/einspielen.sh github
```

Später wieder verbinden mit `tmux attach -t release0212`. **Während der Tests keine Tasten drücken.** Am Ende `j`, danach `exit`.

## Erwartungswerte

- Git-Stand vorher: `273b969`.
- Schritt 4: rund **664 bestanden, 16 übersprungen, 18 ausgelassen**, keine Fehler.
- Schritt 5: alle Container laufen, `/` = 200, `/dashboard/` = 200, `/vorschau/` = 401.
- Dashboard-Fusszeile: „Version 0.21.2 – Entwürfe 20.11., zweite Lieferung“.

## Im Browser prüfen

1. **Spielseite** (eine beliebige Partie): unten zuerst die grüne Schaltfläche „Alle Spiele des Spieltags“ (führt zum Spieltag), darunter der Link „Wie entstehen diese Werte?“ (führt zur Methodik). Kein Satz zur Zeitzone mehr.
2. **Spieltag:** Im grünen Kopfbereich unter den vier Ligen steht kein „Aktueller Datenstand“ mehr. Der Hinweis zur Zeitzone steht weiterhin unter den Spielen.
3. **Startseite, Handy:** In den Karten „Die auffälligsten Spiele“ steht der Chip „Signalqualität …“ rechts neben dem Namen der Kennzahl, nicht darunter. Ganz unten nach „Von einem Fußballfan gebaut“ folgt „Was ist Soccer Intelligence?“.
4. **Methodik:** Auf dem Handy steht in der Schaltfläche unter Ebene 1 „Weiter mit Zahlen:“ in der ersten Zeile, „Ein Spiel durchgerechnet“ in der zweiten. Auf dem Computer steht alles in einer Zeile. Englisch: „Continue with numbers: / a worked example“.
5. **Für den Design-Chat** (nicht zu prüfen, nur weitergeben):
   - Das SEO-Briefing (3.1) und das Template-Briefing (3.3, 5) nennen noch 7 Tage Vorschau; umgesetzt sind 5 Tage.
   - Im README „Noch zu entscheiden“: Level-3-Chip DE („Für Statistik-Fans“ oder „Alles im Detail“), englischer Spieltitel („–“ oder „vs“, umgesetzt „vs“), Position des Glossar-Links (umgesetzt nach Methodik).
6. **Noch offen aus 0.21:** Glossar, Texte der Archivseite, Namen der 12 Aufsteiger, Frage „Auffällige Spiele je Spieltag“. Vor 0.22 dazu die Entscheidungen zum Abfrageplan (`06`, 10.2) und zu den E-Mail-Alarmen.
7. Sag mir, ob alles passt.
