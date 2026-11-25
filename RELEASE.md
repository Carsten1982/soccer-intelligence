# Release: Version 0.27 – Livegang

**Stand:** 25.11.2026 · Version 0.27 · Livegang am 26.11.2026 · Entscheide Carsten 25.11.2026

**Commit:** Version 0.27: Livegang

## Was ändert sich?

- **Die Website geht live** unter `https://soccer-intelligence.com/` (leitet auf `/de/` weiter), ohne Passwort, im
  neuen Container `soccer-website`. Die Vorschau bleibt mit Passwort unter `/vorschau` (mit Zeitreise, nie im Index).
  Das Dashboard bleibt unter `/dashboard`.
- **Suchmaschinen:** `index_ab` = 26.11.2026. Archivseiten der **laufenden Saison** sind je Liga im Index und in der
  Sitemap, auch Spieltage vor dem Livegang; frühere Saisons nicht. Spielseiten ab dem 26.11. nach ihrer Regel.
- **Platzhalterseite** läuft vorerst ungenutzt weiter (Rückweg: Website-Container stoppen, `01`, Abschnitt 6.7).
- **Statusmail** (Montag) mit neuer Zeile „Website und Sitemap erreichbar: … Seiten in … Teil-Sitemaps“.
- **Überwachung** prüft jetzt `/de/`, die Sitemap und den Container `soccer-website`.
- **Texte „bestätigt“** präzisiert: Methodik, Startseite, Glossar mit neuem Begriff „Bestätigt / Nicht bestätigt“ (DE/EN).
- Fehler vor dem Einspielen gefunden und behoben: Der Rückweg (`zurueck.sh`) hätte für `/` den falschen Code erwartet.

## Einspielen

**Schritt 1 – Impressum** (falls noch nicht gemacht oder ohne Ort; fragt Name, Strasse, **PLZ und Ort**, Land und zeigt alles vor dem Speichern):

```bash
bash /docker/football-dashboard/tools/impressum_einrichten.sh
```

**Schritt 2 – Release einspielen** wie immer. Dabei läuft noch das Einspiel-Skript von 0.26. Es kennt den neuen
Container noch nicht: Nach diesem Schritt ist die Website **noch nicht live**, `/` zeigt weiter die Platzhalterseite.

```bash
tmux new -s release027
```

```bash
bash /docker/football-dashboard/tools/einspielen.sh github
```

**Schritt 3 – Livegang-Befehl** (einmalig; ab dem nächsten Release baut `einspielen.sh` die Website selbst mit):

```bash
cd /docker/football-dashboard && docker compose up -d --build soccer-website
```

Nach rund 1 Minute prüfen (nur lesend):

```bash
for u in / /de/ /sitemap.xml /dashboard/ /vorschau/; do printf "%-14s %s\n" "$u" "$(curl -s -o /dev/null -w "%{http_code}" "https://soccer-intelligence.com$u")"; done
```

**Rückweg, falls etwas nicht stimmt** (die Platzhalterseite antwortet nach wenigen Sekunden wieder):

```bash
cd /docker/football-dashboard && docker compose stop soccer-website
```

## Erwartungswerte

- Schritt 1: „✅ Gespeichert in .env.“ und „✅ Vorschau übernimmt die Angaben …“ (noch die Fassung von 0.26; die
  Website liest die Angaben in Schritt 3 beim Start). Prüfen unter `/vorschau/de/impressum/`.
- Schritt 2: Git-Stand vorher `a4a1d40` (oder neuer). Tests rund **757 bestanden**, keine Fehler (hier ohne echte
  Daten: 757 bestanden, 18 übersprungen). Container laufen, `/` = 200 (noch Platzhalterseite), `/dashboard/` = 200;
  drei Testmails. Dashboard-Fusszeile: „Version 0.27 – Livegang“.
- Schritt 3: `docker compose` meldet `Container soccer-website Started`. Prüfbefehl:
  `/` = **301**, `/de/` = **200**, `/sitemap.xml` = **200**, `/dashboard/` = **200**, `/vorschau/` = **401**.
- Bis Schritt 3 läuft, kommen **keine** Alarm-Mails (die Überwachung prüft wie bisher, solange der Container fehlt).

## Im Browser prüfen

1. **Startseite** `https://soccer-intelligence.com/` (privates Fenster, ohne Passwort): leitet auf `/de/`; keine
   graue Vorschau-Leiste oben. Sprachwechsel auf Englisch → `/en/`.
2. **Spieltag, Spielseite, Archiv:** je Liga einmal durchklicken; „Frühere Spieltage ansehen“ führt ins Archiv.
3. **Impressum** `/de/impressum/` und `/en/legal-notice/`: deine Angaben statt Platzhalter.
4. **Quelltext** (Strg+U) der Startseite: kein `noindex`. Bei einer Archivseite der laufenden Saison ebenfalls kein
   `noindex`; bei einer Archivseite der Saison 2025/26 `noindex,follow`.
5. **Sitemap** `/sitemap.xml`: Verweise auf `seiten.xml` und je Liga `…-2026-27.xml`; einen Teil öffnen – Einträge
   mit den Archivseiten der laufenden Saison. **robots.txt** `/robots.txt`: „Allow: /“ und die Sitemap-Adresse.
6. **Kontaktformular** auf der Live-Seite einmal absenden → Mail kommt bei `info@` an.
7. **Komprimierung und HSTS** (aus 0.24 offen, jetzt ohne Passwort prüfbar):
   ```bash
   curl -s -D - -o /dev/null --compressed https://soccer-intelligence.com/statisch/site.css | grep -iE "^HTTP|content-encoding|content-length|strict-transport"
   ```
   Erwartet: `content-encoding: gzip` (oder `br`) und `strict-transport-security`.
8. **Dashboard** `/dashboard/` mit Anmeldemaske und **Vorschau** `/vorschau/` mit Passwort: unverändert.
9. **Handy:** Startseite und Spieltag mit gutem Netz (Tempo-Frage aus 0.24).
10. Danach: **Google Search Console** einrichten (Anleitung von Claude) und die Sitemap einreichen.
