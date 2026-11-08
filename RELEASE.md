# Release: Dokumentation zusammengeführt

**Stand:** 09.11.2026 · Version bleibt 0.10.1 · Nur Dokumentation, **kein Code** · Auftrag Carsten 09.11.2026

## Was ändert sich?

- **Eine Stelle für den Projektstand.** `docs/01_Technisches_Setup.md`, Abschnitt 0, enthält jetzt alles zum Stand:
  - was in Betrieb ist,
  - was als Nächstes kommt,
  - eine Versionstabelle mit Datum, Git-Nummer und Testzahl. Sie dient auch als Rückweg zu jeder Version.
- **Ein Ablauf für jedes Release:** `01`, Abschnitt 6.1, mit allen Befehlen. Jedes künftige Paket heisst `release.zip` und bringt eine neue `RELEASE.md` mit, nur noch mit dem, was sich ändert, und den Erwartungswerten.
- **Die 12 alten Anleitungen** (`ANLEITUNG_*.md`) werden gelöscht. Ihr Inhalt steht in der Versionstabelle, im CHANGELOG und im Git-Verlauf.
- **`CLAUDE.md` gestrafft:** 108 → 62 Zeilen. Es bleiben Einstieg, Quellen, Arbeitsweise und Regeln. Der Stand steht nur noch in `01`.
- **`01_Technisches_Setup.md` gestrafft:** 439 → 345 Zeilen.
  - Die Kopie von `docker-compose.yml` ist durch eine Kurzbeschreibung ersetzt.
  - Veraltete Teile sind entfernt, zum Beispiel „bis Schritt 1“.
  - Die Entscheidungen sind nach Datum sortiert.
  - Erledigte offene Punkte sind entfernt; sie stehen im CHANGELOG.

**Nicht geändert:** Code, Tests, Regelwerk, Dashboard-Briefing, Datenbasis, Spielplan, Prüfprotokolle, Testfälle.

## Erwartungswerte

- **Voraussetzung:** Der Nachtrag 0.10.1 ist committet, `git status` ist also leer.
- **Nach dem Entpacken und Löschen:** `M` für 3 Dateien (`CHANGELOG.md`, `CLAUDE.md`, `docs/01_Technisches_Setup.md`), `D` für 12 Anleitungen, `??` für `RELEASE.md`.
- **Tests und Neubau sind nicht nötig,** weil kein Code geändert wird.

## Befehle (Sonderfall: nur Doku, mit Löschen)

1. **Backup** (wie `01`, Abschnitt 6.1, Schritt 1):
   ```bash
   cd /docker/football-dashboard && git status --short && B=backup/$(date +%F_%H%M)_vor_doku && mkdir -p "$B" && git rev-parse --short HEAD > "$B/git_stand.txt" && tar czf "$B/code_docs.tgz" app tests docs *.md && ls -la "$B" && cat "$B/git_stand.txt"
   ```
2. **Entpacken und alte Anleitungen löschen:**
   ```bash
   cd /docker/football-dashboard && { [ -f release.zip ] || mv /root/release.zip . ; } && python3 -m zipfile -e release.zip . && rm release.zip && git rm -q ANLEITUNG_*.md && git status --short
   ```
3. **Commit:**
   ```bash
   cd /docker/football-dashboard && git add -A && git commit -m "Doku zusammengeführt: Stand in 01, RELEASE.md statt Anleitungen" && git push && git log -1 --oneline
   ```

**Rückweg:** `git reset --hard <Git-Stand aus Schritt 1>`
