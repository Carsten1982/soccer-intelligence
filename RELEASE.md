# Release: GitHub als einzige Quelle

**Stand:** 09.11.2026 · Version bleibt 0.10.1 · Kein Code der App geändert · Auftrag Carsten 09.11.2026

**Commit:** GitHub als einzige Quelle: einspielen.sh github, automatische Tests, robuster Rückweg

## Was ändert sich?

- **Neuer Normalfall:** Änderungen entstehen auf GitHub, der Server holt sie mit einem Befehl ab:
  `bash /docker/football-dashboard/tools/einspielen.sh github`
  (Backup → genau den Stand von GitHub übernehmen → Tests → Neubau → Prüfung `200`/`401` → j/n).
- **Automatische Tests auf GitHub** (`.github/workflows/tests.yml`): laufen bei jedem Push und jedem Pull Request.
- **`tools/zurueck.sh`:** stellt den alten Stand mit einem Gegen-Commit wieder her (klappt auch nach einem Merge auf GitHub).
- **Beide Skripte** lesen sich jetzt vollständig ein, bevor sie starten. Ein Paket darf das Skript also selbst ersetzen.
- **11 Probeläufe** der Skripte (`tests/test_einspielen.py`, laufen auf GitHub) und 2 neue Prüfungen in `tests/test_deploy.py`.
- **Doku:** `01` (Entscheidung, Abschnitt 6.1), `CLAUDE.md` v1.9, CHANGELOG.

**Dieses eine Mal** läuft das Einspielen über eine Kopie des alten Skripts, weil das Paket das Skript selbst ersetzt (das alte Skript würde sonst mitten im Lauf abbrechen).

## Erwartungswerte

- Git-Stand vorher: `0dafea3`.
- Nach dem Entpacken:
  - `M` für 7 Dateien: `CHANGELOG.md`, `CLAUDE.md`, `RELEASE.md`, `docs/01_Technisches_Setup.md`, `tests/test_deploy.py`, `tools/einspielen.sh`, `tools/zurueck.sh`,
  - `??` für `.github/` und `tests/test_einspielen.py`.
- Tests: **350 bestanden, 12 übersprungen** (die 11 Probeläufe brauchen git, das im Test-Container fehlt).

## Im Browser prüfen

- Dashboard: nichts geändert.
- GitHub, Reiter **Actions**: Lauf „Tests“ zum neuen Commit mit grünem Haken.
