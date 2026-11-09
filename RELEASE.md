# Release: Einspiel-Skript

**Stand:** 09.11.2026 · Version bleibt 0.10.1 · Kein Code der App geändert · Freigabe Carsten 09.11.2026

**Commit:** Einspiel-Skript tools/einspielen.sh und Rückweg tools/zurueck.sh

## Was ändert sich?

- **`tools/einspielen.sh`:** Ein Befehl statt sechs.
  - Ablauf: Vorprüfung → Backup → Entpacken (inkl. Löschliste) → Tests → Neubau nur von `football-dashboard` → Prüfung `200`/`401`.
  - Am Schluss fragt es: „Commit und Push machen (j/n)“.
  - Bei einem Fehler hält es an und nennt den Rückweg.
- **`tools/zurueck.sh`:** Rückweg zum Stand vor dem letzten Release. Es fragt vorher nach.
  - Noch nicht committet: Dateien werden zurückgesetzt.
  - Schon committet: Gegen-Commit, damit nichts verloren geht.
- **3 neue Schutztests** (`tests/test_deploy.py`): Die Skripte dürfen nur unseren Container anfassen. Verboten sind unter anderem `compose down`, `prune`, `rm -rf` und Force-Push. Der Commit kommt erst nach j/n.
- **Doku:** `01`, Abschnitt 6.1 (Skript als Normalfall, Einzelbefehle als Ersatz), CHANGELOG.

**Dieses eine Mal** wird noch von Hand eingespielt, weil das Skript selbst neu ist. Ab dem nächsten Release gilt nur noch `bash /docker/football-dashboard/tools/einspielen.sh`.

## Erwartungswerte

- Git-Stand vorher: `0d4d856`.
- Nach dem Entpacken:
  - `M` für 4 Dateien: `CHANGELOG.md`, `RELEASE.md`, `docs/01_Technisches_Setup.md`, `tests/test_deploy.py`,
  - `??` für `tools/` mit den zwei neuen Skripten.
- Tests: **348 bestanden, 1 übersprungen**.
- Ein Neubau ist nicht nötig, weil sich die App nicht ändert.

## Im Browser prüfen

Nichts: Am Dashboard ändert sich nichts.
