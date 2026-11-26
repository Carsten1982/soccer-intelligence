# Release: Version 0.31 – Showcase Englisch

**Stand:** 26.11.2026 · Version 0.31 · Paket Release_20 des Design-Chats (Design 582), Entscheide Carsten 26.11.2026

**Commit:** Version 0.31: Showcase Englisch mit Sprachauswahl, kompakter Hero, Archiv, Wie lese ich das?

## Was ändert sich?

- **Showcase auf Englisch:** `/en/showcase`, `/en/showcase/project`, `/en/showcase/ai-automation`,
  `/en/showcase/ai-automation/data`. Wie die deutschen Seiten noindex, nicht in der Sitemap und nicht von der
  Plattform verlinkt. Die Texte folgen Release_16 (Spalte Englisch) mit den Entscheiden aus Release_18.
- **Sprachauswahl** im Kopf aller acht Seiten (Globus, „Deutsch / English“, zwischen „KI & Automatisierung“ und
  „Kontakt“). Der Wechsel bleibt auf derselben Seite.
- **Kompakter Hero** nach den Vorlagen des Design-Chats: Auf der Startseite stehen Kopf, Hero und die drei Kacheln
  ohne Scrollen auf einem Full-HD-Bildschirm. Projekt- und KI-Seite haben denselben Hero, das Dashboard bleibt gleich.
- **Englisches Linkvorschau-Bild** `showcase-vorschau-en.jpg`. Es liegt wie das deutsche nur auf dem Server, nicht in Git.
- **Archiv-Spieltag:** Sind alle Partien gespielt, entfallen die Legende, „Wie lese ich das?“ und „· n auffällig“.
  Die aktuelle Spieltag-Seite bleibt unverändert.
- **Spielseite nach dem Spiel:** „Wie lese ich das?“ hat fünf Einträge (Ligadurchschnitt / Vergleichswert,
  Erwartungswert, Tatsächlich, Signalqualität, Bestätigt) und einen Schlusssatz, auf Deutsch und Englisch. Die Regel
  „Bestätigt“ ändert sich nicht.

## Vor dem Einspielen: englisches Vorschaubild hochladen

Die Datei `showcase-vorschau-en.jpg` (1200 × 630) bekommst du von Claude zum Download. Lade sie wie das deutsche Bild
nach `/docker/football-dashboard/website-bilder/`. Fehlt sie, haben die englischen Seiten kein Vorschaubild; sonst
funktioniert alles.

## Einspielen

```bash
bash /docker/football-dashboard/tools/einspielen.sh github
```

## Erwartungswerte

- Rund **872 Tests bestanden** (18 übersprungen), keine Fehler. Dashboard-Fusszeile: „Version 0.31 – Showcase Englisch“.
- `https://soccer-intelligence.com/en/showcase` liefert 200, mit Kopfzeile `X-Robots-Tag: noindex, nofollow`.
- Die Sitemap enthält weiterhin keine Showcase-Adresse.

## Im Browser prüfen

1. `https://soccer-intelligence.com/showcase`: kompakter Hero; Kopf, Hero und die drei Kacheln ohne Scrollen sichtbar.
2. Sprachauswahl öffnen und „English“ wählen: `/en/showcase`, alle Texte auf Englisch, Navigation „Project · Platform
   · AI & Automation“. Auf jeder der vier Seiten zurück auf „Deutsch“ wechseln: Es bleibt dieselbe Seite.
3. `/en/showcase/ai-automation/data`: „System status: all systems operational“, in der Tabelle „Control run“ bzw.
   „After the match“ und „Imported“, „Next scheduled run: today at …“.
4. Ein abgeschlossener Spieltag im Archiv, z. B. `https://soccer-intelligence.com/de/spieltag/bundesliga/2026-27/10/`:
   ohne Legende, ohne „Wie lese ich das?“, die Zeile darunter ohne „· n auffällig“. Die aktuelle Spieltag-Seite zeigt
   beides weiterhin.
5. Eine Spielseite nach dem Spiel: „Wie lese ich das?“ öffnen. Es erscheinen fünf Einträge und der Schlusssatz zu
   „Über 2,5 Tore“ und „Beide Teams treffen“; auf Englisch unter `/en/match/…` ebenso.
