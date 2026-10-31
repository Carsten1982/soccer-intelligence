#!/usr/bin/env bash
# Soccer Intelligence – Zugang zum Dashboard setzen oder ändern (Etappe E).
#
# Aufruf auf dem Server:   cd /docker/football-dashboard && bash tools/dashboard_passwort.sh
#
# - Benutzername und Passwort werden abgefragt, das Passwort verdeckt und zweimal.
# - Gespeichert wird nur der bcrypt-Hash, in .env als SOCCER_DASHBOARD_AUTH (nicht in Git).
# - Das Passwort erscheint weder auf dem Bildschirm noch im Befehlsverlauf.
# - Vorher wird .env nach backup/ gesichert. Andere Zeilen in .env bleiben unverändert.
# - Wirksam erst nach:   docker compose up -d football-dashboard
set -euo pipefail
cd "$(dirname "$0")/.."

read -rp  "Benutzername: " U
read -rsp "Passwort: " P1; echo
read -rsp "Passwort wiederholen: " P2; echo

[ -n "$U" ]  || { echo "Abbruch: Benutzername ist leer. Nichts geändert."; exit 1; }
case "$U" in *:*) echo "Abbruch: Der Benutzername darf keinen Doppelpunkt enthalten. Nichts geändert."; exit 1;; esac
[ -n "$P1" ] || { echo "Abbruch: Passwort ist leer. Nichts geändert."; exit 1; }
[ "$P1" = "$P2" ] || { echo "Abbruch: Die beiden Eingaben sind verschieden. Nichts geändert."; exit 1; }

# Hash erzeugen mit dem offiziellen Apache-Werkzeug htpasswd (bcrypt), in einem Wegwerf-Container.
H=$(printf '%s\n' "$P1" | docker run --rm -i httpd:2.4-alpine htpasswd -niB "$U")
unset P1 P2
case "$H" in
  "$U:\$2y\$"*) ;;
  *) echo "Abbruch: Der Hash konnte nicht erzeugt werden. Nichts geändert."; exit 1;;
esac

mkdir -p backup
if [ -f .env ]; then
  cp -a .env "backup/env_$(date +%Y%m%d_%H%M%S)"
fi
{
  if [ -f .env ]; then grep -v '^SOCCER_DASHBOARD_AUTH=' .env || true; fi
  # Einfache Anführungszeichen: Docker Compose übernimmt die $-Zeichen des Hashs unverändert.
  echo "SOCCER_DASHBOARD_AUTH='$H'"
} > .env.neu
chmod 600 .env.neu
mv .env.neu .env

echo "Gespeichert in .env (Benutzer: $U, Passwort nur als Hash)."
echo "Wirksam nach: docker compose up -d football-dashboard"
