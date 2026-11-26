# Release: Version 0.30 – Showcase (mit 0.29 Englische Texte)

**Stand:** 26.11.2026 · Version 0.30 · Release_15 des Design-Chats (Design 575), Entscheide Carsten 26.11.2026.
Enthält auch **0.29** (englische Texte nach Release_14), das noch nicht eingespielt war.

**Commit:** Version 0.30: Showcase

## Was ändert sich?

- **Showcase** (nur für deine Bewerbungen, nie im Index, nicht von der Plattform verlinkt):
  - `/showcase` – Einstieg mit Foto und drei Kacheln
  - `/showcase/project` – Projekt mit Zahlen (Version und Spiele live)
  - `/showcase/ki-automation` – Monitoring und KI-Agenten (nur das Datenmonitoring „Im Betrieb“)
  - `/showcase/ki-automation/data` – Dashboard „Datenmonitoring“ mit **echten Werten aus dem Backend**
- **Backend:** täglicher Verlauf der Datenprüfung und Backups (`import/kennzahlen.json`), Verfügbarkeit je Tag im
  Prüfskript, Testfälle beim Einspielen (`import/release.json`, ab dem nächsten Einspielen).
- **0.29:** englische Texte mit „standout statistic(s)“ statt „anomaly“, neue Standard-Sätze, Methodik DE (D1, D2).

## Vorher: zwei Bilder auf den Server legen

Die Bilder hast du im Chat bekommen (`showcase-portrait.webp`, `showcase-vorschau.jpg`). Sie gehören nach
`/docker/football-dashboard/website-bilder/` (wie das Foto der Startseite; nie in Git). Zum Beispiel vom Laptop aus
(PowerShell oder Terminal, im Ordner mit den beiden Dateien):

```bash
scp showcase-portrait.webp showcase-vorschau.jpg root@72.60.132.157:/docker/football-dashboard/website-bilder/
```

Ohne die Bilder funktioniert alles; dann steht im Hero ein neutraler Platzhalter und die Linkvorschau ohne Bild.

## Einspielen

Pull Request zusammenführen („Squash and merge“, Tests grün), dann:

```bash
tmux new -s release030
```

```bash
bash /docker/football-dashboard/tools/einspielen.sh github
```

## Erwartungswerte

- Tests rund **810 bestanden**, keine Fehler (hier: 824 bestanden, 18 übersprungen; der Browser-Test E7 wird auf dem
  Server übersprungen). Dashboard-Fusszeile: „Version 0.30 – Showcase“.
- Schritt 5 wie bisher (`/` = 301, `/de/` = 200, `/vorschau/` = 401), drei Testmails.
- Danach (nur lesend):
  ```bash
  for u in /showcase /showcase/project /showcase/ki-automation /showcase/ki-automation/data /en/showcase; do printf "%-34s %s %s\n" "$u" "$(curl -s -o /dev/null -w "%{http_code}" "https://soccer-intelligence.com$u")" "$(curl -sI "https://soccer-intelligence.com$u" | grep -i '^x-robots-tag' | tr -d '\r')"; done
  ```
  Erwartet: vier Mal `200 x-robots-tag: noindex, nofollow`, `/en/showcase` = `404`.
- Nach dem nächsten Kontrolllauf (04:00) liegt `import/kennzahlen.json` vor; „Hinweise im Verlauf“ zeigt ab dem zweiten
  Tag eine Linie. „Automatische Tests“ zeigt bis zum nächsten Einspielen „Wird beim nächsten Release erfasst“ (beim
  Einspielen von 0.30 läuft noch das alte Einspiel-Skript).

## Im Browser prüfen (am Computer)

1. `https://soccer-intelligence.com/showcase`: Foto, Tablet, drei Kacheln; Reiter „Showcase“ aktiv.
2. Kachel „Das Projekt“ → Projekt-Seite: **Version 0.30**, Spiele wie im Dashboard, **23**, **7’524 / 4’621**,
   **> 800 Testfälle**, Chip „In Entwicklung“ beim Wettbewerbsmonitoring. „Plattform live erleben“ → Startseite.
3. Reiter „KI & Automatisierung“: Karte 01 „Im Betrieb“ führt zum Dashboard; Karten 02–04 „In Entwicklung“ ohne Link.
4. Dashboard: Systemstatus, Spiele je Liga, letzte Importe, Datenprüfung, Website & Server mit echten Werten, kein
   gelbes Band „Entwurf“.
5. Plattform (`/de/`): nirgends ein Link zum Showcase.
6. Linkvorschau: den Link `https://soccer-intelligence.com/showcase` dir selbst per E-Mail oder in LinkedIn senden →
   Titel, Text und Bild erscheinen (das Bild nur, wenn es auf dem Server liegt).
7. 0.29: `/en/` Footer „Statistical analysis, not betting advice. Not affiliated with any leagues or clubs.“
