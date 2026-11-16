#!/usr/bin/env bash
# Soccer Intelligence – Zugang zum Dashboard setzen oder ändern (seit 0.15.2 für die Anmeldemaske; bis 0.15.1 BasicAuth).
#
# Aufruf auf dem Server:   bash /docker/football-dashboard/tools/dashboard_passwort.sh
#
# - Benutzername und Passwort werden abgefragt, das Passwort verdeckt und zweimal.
# - Gespeichert werden in .env nur der Benutzername (SI_LOGIN_USER) und der Hash des Passworts (SI_LOGIN_HASH,
#   PBKDF2-SHA256, 600'000 Durchläufe, Zufallssalz) – nicht in Git, nicht in der Doku.
# - Das Passwort erscheint weder auf dem Bildschirm noch im Befehlsverlauf; es geht nur über die Standardeingabe in
#   einen Wegwerf-Container, der den Hash berechnet (gleiche Rechnung wie app/anmeldung.py).
# - Vorher wird .env nach backup/ gesichert. Andere Zeilen (z. B. SOCCER_DASHBOARD_AUTH für einen Rückweg auf 0.15.1,
#   API_FOOTBALL_KEY) bleiben unverändert.
# - Wirksam nach:   cd /docker/football-dashboard && docker compose up -d football-dashboard
#   (beim Einspielen eines Releases geschieht das automatisch). Ein neues Passwort meldet alle Browser ab.
set -euo pipefail
cd "${SI_PROJEKT:-/docker/football-dashboard}"

read -rp  "Benutzername: " U
read -rsp "Passwort: " P1; echo
read -rsp "Passwort wiederholen: " P2; echo

[ -n "$U" ]  || { echo "Abbruch: Benutzername ist leer. Nichts geändert."; exit 1; }
case "$U" in *[[:space:]]*|*\'*|*\"*|*\$*) echo "Abbruch: Der Benutzername darf keine Leerzeichen, Anführungszeichen oder \$ enthalten. Nichts geändert."; exit 1;; esac
[ -n "$P1" ] || { echo "Abbruch: Passwort ist leer. Nichts geändert."; exit 1; }
[ "${#P1}" -ge 10 ] || { echo "Abbruch: Das Passwort muss mindestens 10 Zeichen haben. Nichts geändert."; exit 1; }
[ "$P1" = "$P2" ] || { echo "Abbruch: Die beiden Eingaben sind verschieden. Nichts geändert."; exit 1; }

# Hash berechnen (PBKDF2-SHA256) in einem Wegwerf-Container; das Passwort kommt über die Standardeingabe.
H=$(printf '%s' "$P1" | docker run --rm -i python:3.12-slim python -c '
import hashlib, os, sys
p = sys.stdin.read().encode("utf-8"); s = os.urandom(16); n = 600000
print("pbkdf2:sha256:%d:%s:%s" % (n, s.hex(), hashlib.pbkdf2_hmac("sha256", p, s, n).hex()))')
unset P1 P2
case "$H" in
  pbkdf2:sha256:600000:*) ;;
  *) echo "Abbruch: Der Hash konnte nicht erzeugt werden. Nichts geändert."; exit 1;;
esac

mkdir -p backup
if [ -f .env ]; then
  cp -a .env "backup/env_$(date +%Y%m%d_%H%M%S)"
fi
umask 077
{
  if [ -f .env ]; then grep -v -e '^SI_LOGIN_USER=' -e '^SI_LOGIN_HASH=' .env || true; fi
  echo "SI_LOGIN_USER=$U"
  echo "SI_LOGIN_HASH=$H"
} > .env.neu
if [ -f .env ]; then cat .env.neu > .env; rm .env.neu; else mv .env.neu .env; fi

echo "Gespeichert in .env (Benutzer: $U, Passwort nur als Hash)."
echo "Wirksam nach: cd /docker/football-dashboard && docker compose up -d football-dashboard"
