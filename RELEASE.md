# Release: Version 0.28 – Cookie-Hinweis und Google Analytics

**Stand:** 26.11.2026 · Version 0.28 · Entwürfe Cookie_Hinweis und Cookie_Einstellungen, Entscheide Carsten 25./26.11.2026

**Commit:** Version 0.28: Cookie-Hinweis und Google Analytics

## Was ändert sich?

- **Cookie-Hinweis** unten auf jeder Seite, bis eine Wahl getroffen ist: „Wir verwenden Webanalyse, um Soccer
  Intelligence zu verbessern. Die Nutzung erfolgt nur mit deiner Zustimmung.“ mit **Ablehnen** und **Zustimmen**
  (gleich gross, kein Link). Die Wahl gilt 6 Monate.
- **Cookie-Einstellungen** unter `/de/cookie-einstellungen/` bzw. `/en/cookie-settings/` (Link in der
  Datenschutzerklärung, Abschnitt Google Analytics): zeigt die Wahl und ändert sie jederzeit – auch ohne JavaScript.
- **Google Analytics 4** (`G-9XH0LGQLQ7`) wird **erst nach „Zustimmen“** geladen und nur auf der öffentlichen Website,
  nie in der Vorschau. Ablehnen oder Widerruf beendet die Messung sofort und löscht die Analyse-Cookies.
- Englische Datenschutzerklärung: überzähliges deutsches Wort entfernt.

## Einspielen

Pull Request zusammenführen („Squash and merge“, Tests grün), dann:

```bash
tmux new -s release028
```

```bash
bash /docker/football-dashboard/tools/einspielen.sh github
```

## Erwartungswerte

- Tests rund **790 bestanden**, keine Fehler (der Browser-Test E7 wird auf dem Server übersprungen, kein Node).
- Schritt 5: „Container laufen (Dashboard, Import, Vorschau, Website) · / = 301 · /de/ = 200 …“, `/vorschau/` = 401;
  drei Testmails. Dashboard-Fusszeile: „Version 0.28 – Cookie-Hinweis und Google Analytics“.
- Sicherheitsrichtlinie der Website mit den Google-Adressen (nur öffentlich):
  ```bash
  curl -sI https://soccer-intelligence.com/de/ | grep -i "content-security-policy" | grep -o "googletagmanager" | head -1
  ```
  Erwartet: `googletagmanager`.

## Im Browser prüfen

Am besten in einem **privaten Fenster** (dort ist noch keine Wahl gespeichert):

1. `https://soccer-intelligence.com/de/` → unten erscheint der **Cookie-Hinweis** (Handy: volle Breite; Computer:
   links unten, schmal). Die Seite ist trotzdem bedienbar.
2. **Vor der Wahl nichts an Google:** F12 → Netzwerk → Filter `google` → Seite neu laden (Strg+F5): **keine Einträge**.
3. **Zustimmen** klicken → Hinweis verschwindet; im Netzwerk erscheinen jetzt `gtag/js?id=G-9XH0LGQLQ7` und `collect`.
4. **GA4 → Berichte → Echtzeit:** innerhalb von 1–2 Minuten „1 Nutzer“.
5. Datenschutzerklärung → Abschnitt Google Analytics → Link **Cookie-Einstellungen**: zeigt „Zugestimmt: Google
   Analytics ist aktiv.“ → **Ablehnen** → „Abgelehnt: Google Analytics ist aus.“; F12 → Anwendung → Cookies: `_ga`
   und `_ga_…` sind weg.
6. Andere Seite öffnen: kein Hinweis mehr, keine Google-Anfragen.
7. Englisch: `/en/` im neuen privaten Fenster → „We use web analytics …“ mit **Decline** / **Accept**.
8. Vorschau `/vorschau/de/`: Hinweis erscheint auch dort, aber nach „Zustimmen“ **keine** Google-Anfragen.

Danach gehen wir gemeinsam die **Einstellungen in GA4** durch (Aufbewahrung 14 Monate, Google-Signale,
personalisierte Werbung, Datenfreigabe).
