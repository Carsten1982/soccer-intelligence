#!/usr/bin/env bash
# Soccer Intelligence – Mailversand und Server-Überwachung einrichten (seit 0.23, docs/09_Betrieb_EMail.md).
#
# Aufruf auf dem Server (einmalig nach dem Einspielen von 0.23, später zum Ändern eines Passworts):
#   bash /docker/football-dashboard/tools/mail_einrichten.sh
#
# 1. Trägt in .env ein: SI_SMTP_HOST, SI_SMTP_PORT, SI_SMTP_USER (das Postfach info@), SI_ALARM_AN (alert@, ein Alias
#    auf dasselbe Postfach), SI_KONTAKT_AN, SI_KONTAKT_EMAIL (Impressum zeigt die Projektadresse) und – verdeckt
#    abgefragt – SI_SMTP_PASSWORT. Leere Eingabe = bisheriges Passwort behalten. Vorher Kopie von .env nach backup/.
#    Andere Zeilen bleiben unverändert.
# 2. Startet nur unsere zwei betroffenen Container neu (soccer-import, soccer-vorschau), damit sie die Werte lesen.
# 3. Fragt, ob das Prüfskript in den Zeitplan des Servers (cron) eingetragen werden soll (Entscheid Carsten
#    20.11.2026, F1): genau eine Zeile, alle anderen Einträge bleiben unverändert; erneutes Ausführen schadet nicht.
# 4. Schickt über alle drei Versandwege eine Testmail.
# Passwörter erscheinen weder auf dem Bildschirm noch im Befehlsverlauf, in Git oder in Logs.
set -euo pipefail
cd "${SI_PROJEKT:-/docker/football-dashboard}"

ALERT=alert@soccer-intelligence.com
INFO=info@soccer-intelligence.com
CRON_ZEILE="* * * * * /usr/bin/env python3 $PWD/tools/ueberwachen.py >/dev/null 2>&1"

command -v python3 >/dev/null || { echo "Abbruch: python3 fehlt auf dem Server (für das Prüfskript). Nichts geändert."; exit 1; }

echo "Passwort des Postfachs $INFO (wie bei Hostinger festgelegt; $ALERT ist ein Alias und braucht keins)."
read -rsp "Passwort für $INFO (leer = bisheriges behalten): " PW; echo
case "$PW" in *\'*) echo "Abbruch: Das Passwort darf kein einfaches Anführungszeichen (') enthalten. Nichts geändert."; exit 1;; esac
alt() { [ -f .env ] && sed -n "s/^$1='\{0,1\}\([^']*\)'\{0,1\}\$/\1/p" .env | tail -1 || true; }
[ -n "$PW" ] || PW=$(alt SI_SMTP_PASSWORT)
[ -n "$PW" ] || { echo "Abbruch: Kein Passwort eingegeben und keins gespeichert. Nichts geändert."; exit 1; }

mkdir -p backup import/meldungen
[ -f .env ] && cp -a .env "backup/env_$(date +%Y%m%d_%H%M%S)"
umask 077
{
  if [ -f .env ]; then
    grep -Ev '^(SI_SMTP_HOST|SI_SMTP_PORT|SI_SMTP_USER|SI_SMTP_PASSWORT|SI_ALARM_AN|SI_KONTAKT_AN|SI_KONTAKT_EMAIL)=' .env || true
  fi
  echo "SI_SMTP_HOST=smtp.hostinger.com"
  echo "SI_SMTP_PORT=465"
  echo "SI_SMTP_USER=$INFO"
  echo "SI_SMTP_PASSWORT='$PW'"
  echo "SI_ALARM_AN=$ALERT"
  echo "SI_KONTAKT_AN=$INFO"
  echo "SI_KONTAKT_EMAIL=$INFO"
} > .env.neu
unset PW
if [ -f .env ]; then cat .env.neu > .env; rm .env.neu; else mv .env.neu .env; fi
echo "✅ Gespeichert in .env (Passwort nur dort)."

echo "Container soccer-import und soccer-vorschau übernehmen die Werte (nur diese zwei werden neu gestartet) …"
docker compose up -d soccer-import soccer-vorschau >/dev/null 2>&1 && echo "✅ Neu gestartet."

if crontab -l 2>/dev/null | grep -qF "tools/ueberwachen.py"; then
  echo "✅ Prüfskript steht schon im Zeitplan des Servers."
else
  read -rp "Prüfskript jede Minute im Zeitplan des Servers eintragen? (j/n): " J
  case "$J" in
    j|J|ja|Ja)
      ( crontab -l 2>/dev/null || true; echo "$CRON_ZEILE" ) | crontab -
      echo "✅ Eingetragen: $CRON_ZEILE";;
    *) echo "Nicht eingetragen. Später: dieses Skript nochmals ausführen.";;
  esac
fi

sleep 5
echo "Testmails über alle drei Versandwege:"
docker exec soccer-import python -m betrieb.mail --test alert --weg "Container soccer-import (an alert@)" || true
docker exec soccer-vorschau python -m betrieb.mail --test info --weg "Container soccer-vorschau (an info@)" || true
python3 tools/ueberwachen.py --test || true
echo "Bitte im Posteingang prüfen: drei Mails mit „Testmail – …“ im Betreff."
