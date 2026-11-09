#!/usr/bin/env bash
# Soccer Intelligence – Rückweg zum Stand vor dem letzten Release (seit 09.11.2026).
#
# Aufruf auf dem Server:   bash /docker/football-dashboard/tools/zurueck.sh
#
# - Liest den Stand vor dem letzten Release aus backup/LETZTES_RELEASE (geschrieben von tools/einspielen.sh).
# - Fragt vor jeder Änderung nach (j/n).
# - Noch nicht committet: Code auf den alten Stand setzen, neue Dateien aus dem Paket entfernen.
# - Schon committet: Der Release-Commit wird mit "git revert" rückgängig gemacht (neuer Commit, nichts geht
#   verloren) und gepusht. So bleiben Server und GitHub gleich.
# - Danach Neubau nur von football-dashboard und Prüfung. Die Excel-Dateien in data/ bleiben unberührt.
set -euo pipefail

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
  MODUS=revert
  info "Das Release ist schon committet. Es wird mit einem Gegen-Commit rückgängig gemacht und gepusht:"
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
  git revert --no-edit "$VORHER..HEAD" || stopp "git revert ist auf einen Konflikt gestossen."
  git push -q
fi
ok "Code auf dem Stand vor dem Release ($(git log -1 --oneline))"

docker compose up -d --build football-dashboard > "$BACKUP/zurueck_neubau.log" 2>&1 || stopp "Neubau fehlgeschlagen ($BACKUP/zurueck_neubau.log)."
P="" D=""
for _ in $(seq 1 15); do
  sleep 2
  P=$(curl -s -o /dev/null -w "%{http_code}" "$URL/" || true)
  D=$(curl -s -o /dev/null -w "%{http_code}" "$URL/dashboard/" || true)
  [ "$P" = 200 ] && [ "$D" = 401 ] && break
done
[ "$P" = 200 ] && [ "$D" = 401 ] || stopp "Nach dem Rückweg: / = $P, /dashboard/ = $D (erwartet 200 und 401)."
ok "Alter Stand läuft · / = 200 · /dashboard/ = 401"
