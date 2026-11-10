#!/usr/bin/env bash
# Soccer Intelligence – Release einspielen (seit 09.11.2026, ersetzt die sechs Einzelbefehle aus 01, Abschnitt 6.1).
#
# Zwei Wege (Aufruf auf dem Server):
#     bash /docker/football-dashboard/tools/einspielen.sh github   # Normalfall: den neuen Stand von GitHub holen
#     bash /docker/football-dashboard/tools/einspielen.sh          # Ersatz: release.zip (vorher mit WinSCP hochladen)
#
# Ablauf: 1 Vorprüfung · 2 Backup · 3 Übernehmen · 4 Tests · 5 Neubau und Prüfung · 6 Abschluss (fragt j/n).
# - GitHub ist die einzige Quelle. Weg "github" übernimmt nur Commits, die schon auf GitHub (Zweig main) sind,
#   und nur als "fast-forward": Der Server bekommt genau den Stand von GitHub, es entsteht kein eigener Commit.
# - Weg "Paket" committet am Schluss (nach j/n) und pusht nach GitHub. Er stoppt, wenn GitHub schon weiter ist.
# - Bei einem Fehler hält das Skript an, zeigt den Fehler und nennt den Rückweg (tools/zurueck.sh).
#   Es setzt nie selbst etwas zurück.
# - Es berührt nur unseren Container football-dashboard. Kein "docker compose down", keine anderen Container.
# - Die Excel-Dateien in data/ werden weder gelesen noch verändert (ausser lesend von den Tests).
# - Dateien löschen (nur Weg Paket): Enthält das Paket die Datei release_loeschen.txt (eine Datei je Zeile),
#   werden diese Dateien mit "git rm" entfernt. Erlaubt sind nur versionierte Dateien, nie data/, backup/, .env.
set -euo pipefail

# Alles steht in { … }: So liest bash das ganze Skript ein, bevor es startet. Wichtig, weil ein Paket
# dieses Skript selbst ersetzen kann (sonst liest bash mitten im Lauf in der neuen Fassung weiter).
{
PROJEKT="${SI_PROJEKT:-/docker/football-dashboard}"
WEG="${1:-paket}"
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

case "$WEG" in
  github|paket) ;;
  *) stopp "Unbekannter Weg \"$WEG\". Erlaubt: github (oder nichts für release.zip).";;
esac
cd "$PROJEKT" || stopp "Projektordner $PROJEKT nicht gefunden."

# ── 1 Vorprüfung ──────────────────────────────────────────────────────────────────────────────
schritt "1/6: Vorprüfung"
[ -d .git ] || stopp "Kein Git-Projekt in $PROJEKT."
if [ -n "$(git status --porcelain -- . ':(exclude)release*.zip')" ]; then   # das hochgeladene Paket zählt nicht
  git status --short -- . ':(exclude)release*.zip'
  stopp "Es gibt noch nicht committete Änderungen (oben). Erst klären, dann neu starten."
fi
[ "$(git rev-parse --abbrev-ref HEAD)" = main ] || stopp "Der Server steht nicht auf dem Zweig main."
ZIEL=$(git rev-parse --abbrev-ref '@{u}' 2>/dev/null) || stopp "Der Zweig main ist mit keinem GitHub-Zweig verbunden."
git fetch -q || stopp "GitHub ist nicht erreichbar (git fetch)."
VORHER=$(git rev-parse --short HEAD)

if [ "$WEG" = github ]; then
  if [ "$(git rev-parse HEAD)" = "$(git rev-parse "$ZIEL")" ]; then
    ok "Nichts Neues auf GitHub. Der Server ist schon auf dem Stand $VORHER."
    exit 0
  fi
  git merge-base --is-ancestor HEAD "$ZIEL" || stopp "Der Server hat Commits, die nicht auf GitHub sind. Nichts geändert."
  info "Neu auf GitHub (wird übernommen):"
  git log --oneline "HEAD..$ZIEL" | sed 's/^/     /'
  git diff --stat "HEAD" "$ZIEL" | sed 's/^/   /'
  ok "Git-Stand vorher: $VORHER · neuer Stand: $(git rev-parse --short "$ZIEL")"
else
  git merge-base --is-ancestor "$ZIEL" HEAD ||
    stopp "Auf GitHub gibt es neuere Commits als auf dem Server. Bitte so einspielen: bash $PROJEKT/tools/einspielen.sh github"
  # Das Paket darf auch release_2.zip oder "release (1).zip" heissen (der Browser hängt das an, wenn im
  # Download-Ordner schon eine release.zip liegt). Gesucht wird im Projektordner und in /root.
  KANDIDATEN=()
  for f in release.zip release_*.zip "release ("*").zip" /root/release.zip /root/release_*.zip "/root/release ("*").zip"; do
    [ -f "$f" ] && KANDIDATEN+=("$f")          # nur Dateien, die es wirklich gibt
  done
  [ "${#KANDIDATEN[@]}" -gt 0 ] || stopp "Kein Paket gefunden (release.zip, auch nicht release_2.zip o. ä.; weder in $PROJEKT noch in /root). Bitte zuerst mit WinSCP hochladen. Für den Stand von GitHub: bash $PROJEKT/tools/einspielen.sh github"
  if [ "${#KANDIDATEN[@]}" -gt 1 ]; then
    printf '   %s\n' "${KANDIDATEN[@]}"
    stopp "Mehrere Pakete gefunden (oben). Bitte die alten löschen, sodass nur das neue übrig bleibt."
  fi
  if [ "${KANDIDATEN[0]}" != "$PAKET" ]; then
    mv -- "${KANDIDATEN[0]}" "$PAKET"
    info "${KANDIDATEN[0]} als $PAKET übernommen."
  fi
  python3 -m zipfile -t "$PAKET" >/dev/null 2>&1 || stopp "$PAKET ist beschädigt oder unvollständig hochgeladen."
  ok "Git-Stand vorher: $VORHER · Paket gefunden"
fi

# ── 2 Backup ──────────────────────────────────────────────────────────────────────────────────
schritt "2/6: Backup"
BACKUP="backup/$(date +%F_%H%M)_vor_release"
mkdir -p "$BACKUP"
echo "$VORHER" > "$BACKUP/git_stand.txt"
tar czf "$BACKUP/code_docs.tgz" app tests docs tools ./*.md
if [ "$WEG" = github ]; then
  git diff --name-only --diff-filter=A HEAD "$ZIEL" > "$BACKUP/paket_dateien.txt"   # neue Dateien
else
  python3 -m zipfile -l "$PAKET" | awk 'NR>1 {print $1}' > "$BACKUP/paket_dateien.txt"
fi
echo "$BACKUP" > backup/LETZTES_RELEASE
ok "Backup in $BACKUP"

# ── 3 Übernehmen ──────────────────────────────────────────────────────────────────────────────
if [ "$WEG" = github ]; then
  schritt "3/6: Stand von GitHub übernehmen"
  git merge -q --ff-only "$ZIEL" || stopp "Übernahme von GitHub fehlgeschlagen."
  git log -1 --oneline | sed 's/^/   /'
else
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
fi
echo
if [ -f RELEASE.md ] && ! git diff --quiet "$VORHER" -- RELEASE.md; then   # nur wenn RELEASE.md neu ist
  info "Erwartungswerte aus RELEASE.md:"
  sed -n '/^## Erwartungswerte/,/^## /p' RELEASE.md | sed '1d;$d' | sed 's/^/   /'
fi
ok "Neuer Stand liegt bereit"

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

# ── 6 Abschluss ───────────────────────────────────────────────────────────────────────────────
schritt "6/6: Prüfung im Browser und Abschluss"
info "Bitte jetzt im Browser prüfen, was in RELEASE.md unter „Im Browser prüfen“ steht."
if [ "$WEG" = github ]; then
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
fi
TEXT=$(sed -n 's/^\*\*Commit:\*\* *//p' RELEASE.md 2>/dev/null | head -1)
[ -n "$TEXT" ] || TEXT="Release vom $(date +%d.%m.%Y)"
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
exit 0
}
