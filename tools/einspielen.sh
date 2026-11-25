#!/usr/bin/env bash
# Soccer Intelligence – Release einspielen (seit 09.11.2026, ersetzt die sechs Einzelbefehle aus 01, Abschnitt 6.1).
#
# Aufruf auf dem Server:
#     bash /docker/football-dashboard/tools/einspielen.sh github   # den neuen Stand von GitHub holen
# Seit 0.24 gibt es nur noch diesen Weg (Backend-Review B, Entscheid Carsten 24.11.2026): der frühere Ersatzweg über
# ein hochgeladenes release.zip ist entfernt – er wurde seit dem 09.11.2026 nicht mehr gebraucht.
#
# Ablauf: 1 Vorprüfung · 2 Backup · 3 Übernehmen · 4 Tests · 5 Neubau und Prüfung · 6 Abschluss (fragt j/n).
# - GitHub ist die einzige Quelle. Weg "github" übernimmt nur Commits, die schon auf GitHub (Zweig main) sind,
#   und nur als "fast-forward": Der Server bekommt genau den Stand von GitHub, es entsteht kein eigener Commit.
# - Bei einem Fehler hält das Skript an, zeigt den Fehler und nennt den Rückweg (tools/zurueck.sh).
#   Es setzt nie selbst etwas zurück.
# - Bricht ein Lauf nach Schritt 3 ab (z. B. Verbindung weg), merkt sich das Skript den geholten Stand in
#   backup/EINSPIELEN_OFFEN. Der nächste Aufruf "github" macht dann mit Tests und Neubau weiter (seit 15.11.2026).
# - Es berührt nur unsere Container football-dashboard und soccer-import (seit 0.14). Kein "docker compose down",
#   keine anderen Container.
# - Die Excel-Dateien in data/ werden weder gelesen noch verändert (ausser lesend von den Tests).
set -euo pipefail

# Alles steht in { … }: So liest bash das ganze Skript ein, bevor es startet. Wichtig, weil ein neuer Stand
# dieses Skript selbst ersetzen kann (sonst liest bash mitten im Lauf in der neuen Fassung weiter).
{
PROJEKT="${SI_PROJEKT:-/docker/football-dashboard}"
WEG="${1:-github}"
URL="https://soccer-intelligence.com"

ok()     { printf '\033[32m✅ %s\033[0m\n' "$*"; }
info()   { printf '   %s\n' "$*"; }
schritt(){ printf '\n\033[1m── Schritt %s ──────────────────────────────────────\033[0m\n' "$*"; }
stopp() {
  printf '\n\033[31m⛔ STOPP: %s\033[0m\n' "$*"
  if [ -n "${BACKUP:-}" ]; then
    printf '   Der laufende Stand ist unverändert, solange Schritt 5 nicht begonnen hat.\n'
    printf '   Rückweg:   bash %s/tools/zurueck.sh\n' "$PROJEKT"
  fi
  printf '   Bitte die Ausgabe an Claude schicken.\n'
  exit 1
}

case "$WEG" in
  github) ;;
  *) stopp "Unbekannter Weg \"$WEG\". Erlaubt ist nur: github (seit 0.24 gibt es keinen ZIP-Weg mehr).";;
esac
cd "$PROJEKT" || stopp "Projektordner $PROJEKT nicht gefunden."

# ── 1 Vorprüfung ──────────────────────────────────────────────────────────────────────────────
schritt "1/6: Vorprüfung"
[ -d .git ] || stopp "Kein Git-Projekt in $PROJEKT."
if [ -n "$(git status --porcelain)" ]; then
  git status --short
  stopp "Es gibt noch nicht committete Änderungen (oben). Erst klären, dann neu starten."
fi
[ "$(git rev-parse --abbrev-ref HEAD)" = main ] || stopp "Der Server steht nicht auf dem Zweig main."
ZIEL=$(git rev-parse --abbrev-ref '@{u}' 2>/dev/null) || stopp "Der Zweig main ist mit keinem GitHub-Zweig verbunden."
git fetch -q || stopp "GitHub ist nicht erreichbar (git fetch)."
VORHER=$(git rev-parse --short HEAD)
OFFEN="backup/EINSPIELEN_OFFEN"   # geholter, aber noch nicht fertig eingespielter Stand
NACHHOLEN=""

if [ "$(git rev-parse HEAD)" = "$(git rev-parse "$ZIEL")" ]; then
  if [ -f "$OFFEN" ] && [ "$(cat "$OFFEN")" = "$(git rev-parse HEAD)" ]; then
    NACHHOLEN=1
    ok "Stand $VORHER ist schon geholt, aber noch nicht fertig eingespielt (letzter Lauf abgebrochen)."
    info "Es geht mit den Tests und dem Neubau weiter (Schritte 4 bis 6)."
  else
    ok "Nichts Neues auf GitHub. Der Server ist schon auf dem Stand $VORHER."
    exit 0
  fi
else
  git merge-base --is-ancestor HEAD "$ZIEL" || stopp "Der Server hat Commits, die nicht auf GitHub sind. Nichts geändert."
  info "Neu auf GitHub (wird übernommen):"
  git log --oneline "HEAD..$ZIEL" | sed 's/^/     /'
  git diff --stat "HEAD" "$ZIEL" | sed 's/^/   /'
  ok "Git-Stand vorher: $VORHER · neuer Stand: $(git rev-parse --short "$ZIEL")"
fi

if [ -n "$NACHHOLEN" ]; then
  BACKUP=$(cat backup/LETZTES_RELEASE 2>/dev/null || echo "backup/$(date +%F_%H%M)_nachgeholt")
  mkdir -p "$BACKUP"
  VORHER=$(cat "$BACKUP/git_stand.txt" 2>/dev/null || echo "$VORHER")   # Stand vor dem abgebrochenen Lauf
  info "Backup vom abgebrochenen Lauf: $BACKUP (Stand davor: $VORHER)"
else
# ── 2 Backup ──────────────────────────────────────────────────────────────────────────────────
schritt "2/6: Backup"
BACKUP="backup/$(date +%F_%H%M)_vor_release"
mkdir -p "$BACKUP"
echo "$VORHER" > "$BACKUP/git_stand.txt"
tar czf "$BACKUP/code_docs.tgz" app tests docs tools ./*.md
git diff --name-only --diff-filter=A HEAD "$ZIEL" > "$BACKUP/paket_dateien.txt"   # neue Dateien (für zurueck.sh)
echo "$BACKUP" > backup/LETZTES_RELEASE
ok "Backup in $BACKUP"

# ── 3 Übernehmen ──────────────────────────────────────────────────────────────────────────────
schritt "3/6: Stand von GitHub übernehmen"
git merge -q --ff-only "$ZIEL" || stopp "Übernahme von GitHub fehlgeschlagen."
git log -1 --oneline | sed 's/^/   /'
echo
if [ -f RELEASE.md ] && ! git diff --quiet "$VORHER" -- RELEASE.md; then   # nur wenn RELEASE.md neu ist
  info "Erwartungswerte aus RELEASE.md:"
  sed -n '/^## Erwartungswerte/,/^## /p' RELEASE.md | sed '1d;$d' | sed 's/^/   /'
fi
git rev-parse HEAD > "$OFFEN"   # bis Schritt 5 fertig ist
ok "Neuer Stand liegt bereit"
fi

# ── 4 Tests ───────────────────────────────────────────────────────────────────────────────────
# Seit 0.15.2 nur die schnellen Tests: Die langsamen Ende-zu-Ende-Tests (Marker „langsam“) laufen bei jedem Pull Request
# vollständig auf GitHub; ohne grünen Haken wird nicht zusammengeführt (Entscheidung Carsten 16.11.2026).
schritt "4/6: Tests (rund 8 Minuten, Wegwerf-Container)"
info "Bitte warten und nichts drücken (Ctrl+C bricht die Tests ab)."
set +e
docker run --rm -v "$PWD":/src:ro -e SI_DATA_DIR=/src/data -e PYTHONDONTWRITEBYTECODE=1 -w /src python:3.12-slim \
  sh -c "pip install -q --root-user-action=ignore -r requirements-dev.txt && python -m pytest -q -p no:cacheprovider -m 'not langsam' tests" \
  > "$BACKUP/tests.log" 2>&1
TESTS=$?
set -e
grep -v "notice\]" "$BACKUP/tests.log" | tail -6 | sed 's/^/   /'
[ "$TESTS" -eq 0 ] || stopp "Tests fehlgeschlagen (ganzes Protokoll: $BACKUP/tests.log)."
ok "Tests bestanden: $(grep -Eo '[0-9]+ passed(, [0-9]+ skipped)?' "$BACKUP/tests.log" | tail -1)"

# ── 5 Neubau und Prüfung ──────────────────────────────────────────────────────────────────────
schritt "5/6: Neubau (football-dashboard, soccer-import, soccer-vorschau, soccer-website) und Prüfung"
docker compose up -d --build football-dashboard soccer-import soccer-vorschau soccer-website > "$BACKUP/neubau.log" 2>&1 || {
  tail -15 "$BACKUP/neubau.log" | sed 's/^/   /'; stopp "Neubau fehlgeschlagen."; }
# Seit 0.27 (Livegang): / leitet dauerhaft auf /de/ weiter (301), /de/ ist die Startseite der Website
START="" SEITE="" DASHBOARD="" VORSCHAU=""
for _ in $(seq 1 15); do
  sleep 2
  START=$(curl -s -o /dev/null -w "%{http_code}" "$URL/" || true)
  SEITE=$(curl -s -o /dev/null -w "%{http_code}" "$URL/de/" || true)
  DASHBOARD=$(curl -s -o /dev/null -w "%{http_code}" "$URL/dashboard/" || true)
  VORSCHAU=$(curl -s -o /dev/null -w "%{http_code}" "$URL/vorschau/" || true)
  [ "$SEITE" = 200 ] && [ "$DASHBOARD" = 200 ] && break
done
docker ps --format "table {{.Names}}\t{{.Status}}" | sed 's/^/   /'
docker logs football-dashboard --tail 4 2>&1 | sed 's/^/   /'
LAEUFT=$(docker inspect -f '{{.State.Running}}' football-dashboard 2>/dev/null || echo false)
[ "$LAEUFT" = true ] || stopp "Container football-dashboard läuft nicht."
IMPORT=$(docker inspect -f '{{.State.Running}}' soccer-import 2>/dev/null || echo false)
[ "$IMPORT" = true ] || stopp "Container soccer-import läuft nicht (Datenimport)."
WEBSEITE=$(docker inspect -f '{{.State.Running}}' soccer-vorschau 2>/dev/null || echo false)
[ "$WEBSEITE" = true ] || stopp "Container soccer-vorschau läuft nicht (Vorschau der Website, seit 0.17)."
OEFFENTLICH=$(docker inspect -f '{{.State.Running}}' soccer-website 2>/dev/null || echo false)
[ "$OEFFENTLICH" = true ] || stopp "Container soccer-website läuft nicht (öffentliche Website, seit 0.27)."
case "$START" in 200|301) ;; *) stopp "Die Startadresse / antwortet mit $START statt 301 (Weiterleitung auf /de/).";; esac
[ "$SEITE" = 200 ] || stopp "Die Website /de/ antwortet mit $SEITE statt 200."
[ "$DASHBOARD" = 200 ] || stopp "Dashboard antwortet mit $DASHBOARD statt 200 (Anmeldemaske, seit 0.15.2)."
ok "Container laufen (Dashboard, Import, Vorschau, Website) · / = $START · /de/ = 200 · /dashboard/ = 200 (Anmeldemaske)"
if [ "$VORSCHAU" = 401 ]; then
  ok "/vorschau/ = 401 (Passwortabfrage der Vorschau)"
else
  info "Hinweis: /vorschau/ antwortet mit $VORSCHAU statt 401. Passwort der Vorschau setzen (01, Abschnitt 6.3)."
fi
rm -f "$OFFEN"

# Testmails über alle drei Versandwege (seit 0.23, Wunsch Carsten 20.11.2026, docs/09, Abschnitt 2.1).
# Eine gescheiterte Testmail stoppt das Einspielen nicht, wird aber gemeldet.
RELEASE_TEXT="$(sed -n 's/^APP_VERSION = "\(.*\)"/\1/p' app/core/settings.py | head -1) ($(git rev-parse --short HEAD))"
MAILS=0
info "Testmails über alle drei Versandwege:"
set +e
docker exec soccer-import python -m betrieb.mail --test alert --release "$RELEASE_TEXT" --weg "Container soccer-import (an alert@)" 2>&1 | sed 's/^/   /'
[ "${PIPESTATUS[0]}" -eq 0 ] && MAILS=$((MAILS + 1))
docker exec soccer-vorschau python -m betrieb.mail --test info --release "$RELEASE_TEXT" --weg "Container soccer-vorschau (an info@)" 2>&1 | sed 's/^/   /'
[ "${PIPESTATUS[0]}" -eq 0 ] && MAILS=$((MAILS + 1))
python3 tools/ueberwachen.py --test --release "$RELEASE_TEXT" 2>&1 | sed 's/^/   /'
[ "${PIPESTATUS[0]}" -eq 0 ] && MAILS=$((MAILS + 1))
set -e
if [ "$MAILS" -eq 3 ]; then
  ok "3 Testmails gesendet – bitte gleich im Posteingang prüfen."
else
  info "Hinweis: nur $MAILS von 3 Testmails gesendet (Mailversand eingerichtet? 01, Abschnitt 6.6). Der neue Stand läuft trotzdem."
fi

# ── 6 Abschluss ───────────────────────────────────────────────────────────────────────────────
schritt "6/6: Prüfung im Browser und Abschluss"
info "Bitte jetzt im Browser prüfen, was in RELEASE.md unter „Im Browser prüfen“ steht."
[ "$MAILS" -gt 0 ] && info "Und: Sind die $MAILS Testmails angekommen (Betreff „Test nach Release …“)?"
read -rp "   Alles in Ordnung? (j/n): " ANTWORT
case "$ANTWORT" in
  j|J|ja|Ja)
    ok "Eingespielt: $(git log -1 --oneline) · Server und GitHub sind gleich."
    info "Bitte die Git-Nummer an Claude schicken."
    ;;
  *)
    printf '\n\033[33m⏸  Nicht bestätigt.\033[0m Der neue Stand läuft.\n'
    info "Zurück zum Stand $VORHER (auch auf GitHub):   bash $PROJEKT/tools/zurueck.sh"
    ;;
esac
exit 0
}
