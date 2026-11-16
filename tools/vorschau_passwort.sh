#!/usr/bin/env bash
# Soccer Intelligence – Passwort der Website-Vorschau setzen oder ändern (seit 0.17, docs/08_Website.md).
#
# Aufruf auf dem Server:   bash /docker/football-dashboard/tools/vorschau_passwort.sh
#
# - Benutzername und Passwort werden abgefragt, das Passwort verdeckt und zweimal.
# - Gespeichert wird nur der bcrypt-Hash, in .env als SOCCER_VORSCHAU_AUTH (nicht in Git, nicht in der Doku).
#   Traefik fragt damit unter https://soccer-intelligence.com/vorschau nach (Passwortabfrage des Browsers).
# - Das Passwort erscheint weder auf dem Bildschirm noch im Befehlsverlauf; der Hash entsteht mit dem offiziellen
#   Apache-Werkzeug htpasswd in einem Wegwerf-Container.
# - Vorher wird .env nach backup/ gesichert. Andere Zeilen in .env bleiben unverändert.
# - Wirksam nach:   cd /docker/football-dashboard && docker compose up -d soccer-vorschau
set -euo pipefail
cd "${SI_PROJEKT:-/docker/football-dashboard}"

read -rp  "Benutzername: " U
read -rsp "Passwort: " P1; echo
read -rsp "Passwort wiederholen: " P2; echo

[ -n "$U" ]  || { echo "Abbruch: Benutzername ist leer. Nichts geändert."; exit 1; }
case "$U" in *:*|*[[:space:]]*|*\'*|*\"*|*\$*) echo "Abbruch: Der Benutzername darf keinen Doppelpunkt, keine Leerzeichen, Anführungszeichen oder \$ enthalten. Nichts geändert."; exit 1;; esac
[ -n "$P1" ] || { echo "Abbruch: Passwort ist leer. Nichts geändert."; exit 1; }
[ "${#P1}" -ge 10 ] || { echo "Abbruch: Das Passwort muss mindestens 10 Zeichen haben. Nichts geändert."; exit 1; }
[ "$P1" = "$P2" ] || { echo "Abbruch: Die beiden Eingaben sind verschieden. Nichts geändert."; exit 1; }

# Hash mit htpasswd (bcrypt) in einem Wegwerf-Container; das Passwort kommt über die Standardeingabe.
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
umask 077
{
  if [ -f .env ]; then grep -v '^SOCCER_VORSCHAU_AUTH=' .env || true; fi
  # Einfache Anführungszeichen: Docker Compose übernimmt die $-Zeichen des Hashs unverändert.
  echo "SOCCER_VORSCHAU_AUTH='$H'"
} > .env.neu
if [ -f .env ]; then cat .env.neu > .env; rm .env.neu; else mv .env.neu .env; fi

echo "Gespeichert in .env (Benutzer: $U, Passwort nur als Hash)."
echo "Wirksam nach: cd /docker/football-dashboard && docker compose up -d soccer-vorschau"
