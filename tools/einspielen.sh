#!/usr/bin/env bash
# Soccer Intelligence – Release einspielen (seit 09.11.2026, ersetzt die sechs Einzelbefehle aus 01, Abschnitt 6.1).
#
# Aufruf auf dem Server (release.zip vorher mit WinSCP hochladen, nach /docker/football-dashboard oder /root):
#     bash /docker/football-dashboard/tools/einspielen.sh
#
# Ablauf: 1 Vorprüfung · 2 Backup · 3 Entpacken · 4 Tests · 5 Neubau und Prüfung · 6 Commit (fragt j/n).
# - Bei einem Fehler hält das Skript an, zeigt den Fehler und nennt den Rückweg (tools/zurueck.sh).
#   Es setzt nie selbst etwas zurück.
# - Es berührt nur unseren Container football-dashboard. Kein "docker compose down", keine anderen Container.
# - Die Excel-Dateien in data/ werden weder gelesen noch verändert (ausser lesend von den Tests).
# - Dateien löschen: Enthält das Paket die Datei release_loeschen.txt (eine Datei je Zeile), werden diese
#   Dateien mit "git rm" entfernt. Erlaubt sind nur versionierte Dateien, nie data/, backup/ oder .env.
set -euo pipefail

PROJEKT="${SI_PROJEKT:-/docker/football-dashboard}"
PAKET="release.zip"
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

cd "$PROJEKT" || stopp "Projektordner $PROJEKT nicht gefunden."

# ── 1 Vorprüfung ──────────────────────────────────────────────────────────────────────────────
schritt "1/6: Vorprüfung"
[ -d .git ] || stopp "Kein Git-Projekt in $PROJEKT."
if [ -n "$(git status --porcelain -- . ":(exclude)$PAKET")" ]; then     # das hochgeladene Paket selbst zählt nicht
  git status --short -- . ":(exclude)$PAKET"
  stopp "Es gibt noch nicht committete Änderungen (oben). Erst klären, dann neu starten."
fi
if [ ! -f "$PAKET" ]; then
  if [ -f "/root/$PAKET" ]; then mv "/root/$PAKET" .; info "$PAKET aus /root geholt."
  else stopp "$PAKET nicht gefunden (weder in $PROJEKT noch in /root). Bitte zuerst mit WinSCP hochladen."; fi
fi
python3 -m zipfile -t "$PAKET" >/dev/null 2>&1 || stopp "$PAKET ist beschädigt oder unvollständig hochgeladen."
VORHER=$(git rev-parse --short HEAD)
ok "Git-Stand vorher: $VORHER · Paket gefunden"

# ── 2 Backup ──────────────────────────────────────────────────────────────────────────────────
schritt "2/6: Backup"
BACKUP="backup/$(date +%F_%H%M)_vor_release"
mkdir -p "$BACKUP"
echo "$VORHER" > "$BACKUP/git_stand.txt"
tar czf "$BACKUP/code_docs.tgz" app tests docs ./*.md
python3 -m zipfile -l "$PAKET" | awk 'NR>1 {print $1}' > "$BACKUP/paket_dateien.txt"
echo "$BACKUP" > backup/LETZTES_RELEASE
ok "Backup in $BACKUP"

# ── 3 Entpacken ───────────────────────────────────────────────────────────────────────────────
schritt "3/6: Paket entpacken"
python3 -m zipfile -e "$PAKET" .
rm "$PAKET"
if [ -f release_loeschen.txt ]; then
  while IFS= read -r datei || [ -n "$datei" ]; do
    datei="${datei%$'\r'}"
    [ -z "$datei" ] && continue
    case "$datei" in
      /*|*..*|data/*|backup/*|.env*|.git/*) stopp "Unerlaubter Eintrag in release_loeschen.txt: $datei";;
    esac
    git ls-files --error-unmatch -- "$datei" >/dev/null 2>&1 || stopp "Zu löschende Datei ist nicht versioniert: $datei"
    git rm -q -- "$datei"
    info "gelöscht: $datei"
  done < release_loeschen.txt
  rm release_loeschen.txt
fi
git status --short
echo
if [ -f RELEASE.md ]; then
  info "Erwartungswerte aus RELEASE.md:"
  sed -n '/^## Erwartungswerte/,/^## /p' RELEASE.md | sed '1d;$d' | sed 's/^/   /'
fi
ok "Paket entpackt"

# ── 4 Tests ───────────────────────────────────────────────────────────────────────────────────
schritt "4/6: Tests (rund 4 Minuten, Wegwerf-Container)"
set +e
docker run --rm -v "$PWD":/src:ro -e SI_DATA_DIR=/src/data -e PYTHONDONTWRITEBYTECODE=1 -w /src python:3.12-slim \
  sh -c "pip install -q --root-user-action=ignore -r requirements-dev.txt && python -m pytest -q -p no:cacheprovider tests" \
  > "$BACKUP/tests.log" 2>&1
TESTS=$?
set -e
grep -v "notice\]" "$BACKUP/tests.log" | tail -6 | sed 's/^/   /'
[ "$TESTS" -eq 0 ] || stopp "Tests fehlgeschlagen (ganzes Protokoll: $BACKUP/tests.log)."
ok "Tests bestanden: $(grep -Eo '[0-9]+ passed(, [0-9]+ skipped)?' "$BACKUP/tests.log" | tail -1)"

# ── 5 Neubau und Prüfung ──────────────────────────────────────────────────────────────────────
schritt "5/6: Neubau (nur football-dashboard) und Prüfung"
docker compose up -d --build football-dashboard > "$BACKUP/neubau.log" 2>&1 || {
  tail -15 "$BACKUP/neubau.log" | sed 's/^/   /'; stopp "Neubau fehlgeschlagen."; }
PLATZHALTER="" DASHBOARD=""
for _ in $(seq 1 15); do
  sleep 2
  PLATZHALTER=$(curl -s -o /dev/null -w "%{http_code}" "$URL/" || true)
  DASHBOARD=$(curl -s -o /dev/null -w "%{http_code}" "$URL/dashboard/" || true)
  [ "$PLATZHALTER" = 200 ] && [ "$DASHBOARD" = 401 ] && break
done
docker ps --format "table {{.Names}}\t{{.Status}}" | sed 's/^/   /'
docker logs football-dashboard --tail 4 2>&1 | sed 's/^/   /'
LAEUFT=$(docker inspect -f '{{.State.Running}}' football-dashboard 2>/dev/null || echo false)
[ "$LAEUFT" = true ] || stopp "Container football-dashboard läuft nicht."
[ "$PLATZHALTER" = 200 ] || stopp "Platzhalterseite antwortet mit $PLATZHALTER statt 200."
[ "$DASHBOARD" = 401 ] || stopp "Dashboard antwortet mit $DASHBOARD statt 401 (Passwortschutz)."
ok "Container läuft · / = 200 · /dashboard/ = 401"

# ── 6 Commit ──────────────────────────────────────────────────────────────────────────────────
schritt "6/6: Prüfung im Browser und Commit"
TEXT=$(sed -n 's/^\*\*Commit:\*\* *//p' RELEASE.md 2>/dev/null | head -1)
[ -n "$TEXT" ] || TEXT="Release vom $(date +%d.%m.%Y)"
info "Bitte jetzt im Browser prüfen, was in RELEASE.md unter „Im Browser prüfen“ steht."
info "Commit-Text: $TEXT"
read -rp "   Alles in Ordnung? Commit und Push machen (j/n): " ANTWORT
case "$ANTWORT" in
  j|J|ja|Ja)
    git add -A
    git commit -q -m "$TEXT"
    git push -q
    ok "Eingespielt und gesichert: $(git log -1 --oneline)"
    info "Bitte die Git-Nummer an Claude schicken."
    ;;
  *)
    printf '\n\033[33m⏸  Nicht committet.\033[0m Das neue Release läuft, ist aber nicht gesichert.\n'
    info "Zurück zum Stand $VORHER:   bash $PROJEKT/tools/zurueck.sh"
    info "Oder später committen:      cd $PROJEKT && git add -A && git commit -m \"$TEXT\" && git push"
    ;;
esac
