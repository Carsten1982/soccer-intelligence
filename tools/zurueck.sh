#!/usr/bin/env bash
# Soccer Intelligence – Rückweg zum Stand vor dem letzten Release (seit 09.11.2026).
#
# Aufruf auf dem Server:   bash /docker/football-dashboard/tools/zurueck.sh
#
# - Liest den Stand vor dem letzten Release aus backup/LETZTES_RELEASE (geschrieben von tools/einspielen.sh).
# - Fragt vor jeder Änderung nach (j/n).
# - Noch nicht committet (Weg Paket, Antwort n): Code auf den alten Stand setzen, neue Dateien aus dem Paket entfernen.
# - Schon committet oder von GitHub geholt: Ein Gegen-Commit stellt genau den alten Stand wieder her (nichts geht
#   verloren, auch Merge-Commits von GitHub sind kein Problem) und wird gepusht. So bleiben Server und GitHub gleich.
# - Danach Neubau nur von football-dashboard und Prüfung. Die Excel-Dateien in data/ bleiben unberührt.
set -euo pipefail

# Alles steht in { … }: So liest bash das ganze Skript ein, bevor es startet (der Rückweg ersetzt Dateien).
{
PROJEKT="${SI_PROJEKT:-/docker/football-dashboard}"
URL="https://soccer-intelligence.com"
ok()   { printf '\033[32m✅ %s\033[0m\n' "$*"; }
info() { printf '   %s\n' "$*"; }
stopp(){ printf '\n\033[31m⛔ STOPP: %s\033[0m\n   Bitte die Ausgabe an Claude schicken.\n' "$*"; exit 1; }

cd "$PROJEKT" || stopp "Projektordner $PROJEKT nicht gefunden."
[ -f backup/LETZTES_RELEASE ] || stopp "Kein Release von tools/einspielen.sh gefunden (backup/LETZTES_RELEASE fehlt)."
BACKUP=$(cat backup/LETZTES_RELEASE)
VORHER=$(cat "$BACKUP/git_stand.txt")
JETZT=$(git rev-parse --short HEAD)
git cat-file -e "$VORHER^{commit}" 2>/dev/null || stopp "Git-Stand $VORHER aus $BACKUP nicht gefunden."

echo "Rückweg zum Stand vor dem Release vom $(basename "$BACKUP" | cut -c1-15)"
info "Stand vor dem Release: $VORHER · aktueller Stand: $JETZT"
if [ "$(git rev-parse "$VORHER")" = "$(git rev-parse HEAD)" ]; then
  MODUS=zuruecksetzen
  info "Das Release ist noch nicht committet. Geänderte Dateien werden auf $VORHER zurückgesetzt,"
  info "neue Dateien aus dem Paket entfernt."
else
  MODUS=gegencommit
  [ -z "$(git status --porcelain)" ] || { git status --short; stopp "Es gibt nicht committete Änderungen (oben)."; }
  info "Das Release ist schon committet. Ein Gegen-Commit stellt den Stand $VORHER wieder her und wird gepusht."
  info "Rückgängig gemacht werden:"
  git log --oneline "$VORHER..HEAD" | sed 's/^/     /'
fi
read -rp "   Wirklich zurück? (j/n): " ANTWORT
case "$ANTWORT" in j|J|ja|Ja) ;; *) echo "Abgebrochen, nichts geändert."; exit 0;; esac

if [ "$MODUS" = zuruecksetzen ]; then
  git reset -q --hard "$VORHER"
  while IFS= read -r datei || [ -n "$datei" ]; do
    [ -n "$datei" ] || continue
    if [ -f "$datei" ] && ! git ls-files --error-unmatch -- "$datei" >/dev/null 2>&1; then
      rm -f -- "$datei"; info "entfernt: $datei"
    fi
  done < "$BACKUP/paket_dateien.txt"
else
  # Neuer Commit auf dem aktuellen Stand, dessen Inhalt genau der alte Stand ist. Danach "fast-forward" dorthin.
  GEGEN=$(git commit-tree "$VORHER^{tree}" -p HEAD -m "Rückweg auf Stand $VORHER (macht $JETZT rückgängig)")
  git merge -q --ff-only "$GEGEN" || stopp "Gegen-Commit konnte nicht übernommen werden."
  git push -q || stopp "Push nach GitHub fehlgeschlagen. Der Server ist zurück, GitHub noch nicht."
fi
ok "Code auf dem Stand vor dem Release ($(git log -1 --oneline))"

# Datenimport (seit 0.14) mitbauen, wenn der alte Stand ihn schon kennt; sonst nur ein Hinweis (er läuft weiter)
if grep -q "^  soccer-import:" docker-compose.yml; then
  docker compose up -d --build football-dashboard soccer-import > "$BACKUP/zurueck_neubau.log" 2>&1 || stopp "Neubau fehlgeschlagen ($BACKUP/zurueck_neubau.log)."
else
  docker compose up -d --build football-dashboard > "$BACKUP/zurueck_neubau.log" 2>&1 || stopp "Neubau fehlgeschlagen ($BACKUP/zurueck_neubau.log)."
  info "Hinweis: Der alte Stand kennt den Datenimport noch nicht. Der Container soccer-import läuft weiter;"
  info "neue Daten im Bereich Datenimport/API bis zur Klärung nicht übernehmen (01, Abschnitt 6.3)."
fi
P="" D=""
for _ in $(seq 1 15); do
  sleep 2
  P=$(curl -s -o /dev/null -w "%{http_code}" "$URL/" || true)
  D=$(curl -s -o /dev/null -w "%{http_code}" "$URL/dashboard/" || true)
  [ "$P" = 200 ] && { [ "$D" = 200 ] || [ "$D" = 401 ]; } && break
done
# /dashboard/: 200 = Anmeldemaske (ab 0.15.2), 401 = Passwortabfrage des Browsers (bis 0.15.1)
[ "$P" = 200 ] && { [ "$D" = 200 ] || [ "$D" = 401 ]; } || stopp "Nach dem Rückweg: / = $P, /dashboard/ = $D (erwartet 200 und 200 bzw. 401)."
ok "Alter Stand läuft · / = 200 · /dashboard/ = $D"
exit 0
}
