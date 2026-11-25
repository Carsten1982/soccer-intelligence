#!/usr/bin/env bash
# Soccer Intelligence – Betreiberangaben für Impressum und Datenschutz einrichten (seit 0.26).
#
# Aufruf auf dem Server (einmalig, später zum Ändern):
#   bash /docker/football-dashboard/tools/impressum_einrichten.sh
#
# Fragt Name und Adresse ab und trägt sie in .env ein (SI_IMPRESSUM_NAME, SI_IMPRESSUM_ADRESSE; die Adresszeilen mit „|“
# getrennt, z. B. „Strasse 1|1234 Ort|Schweiz“). Die Angaben stehen nur in .env auf dem Server, nie im Programm oder in
# Git (CLAUDE.md, Regeln). Vorher Kopie von .env nach backup/. Andere Zeilen bleiben unverändert. Danach werden nur die
# Website-Container soccer-vorschau und (seit 0.27, Livegang) soccer-website neu erstellt (sie lesen die Werte beim Start).
set -euo pipefail
cd "${SI_PROJEKT:-/docker/football-dashboard}"

echo "Betreiberangaben für Impressum und Datenschutz (erscheinen öffentlich auf der Website)."
read -rp "Name: " NAME
read -rp "Strasse und Hausnummer: " STRASSE
read -rp "PLZ und Ort (z. B. 1234 Musterort): " ORT
read -rp "Land: " LAND
for wert in "$NAME" "$STRASSE" "$ORT" "$LAND"; do
  [ -n "$wert" ] || { echo "Abbruch: Alle vier Angaben sind nötig. Nichts geändert."; exit 1; }
  case "$wert" in *\'*|*\|*) echo "Abbruch: Bitte kein einfaches Anführungszeichen (') und kein „|“ verwenden. Nichts geändert."; exit 1;; esac
done

echo
echo "So erscheint es im Impressum:"
printf '   %s\n   %s\n   %s\n   %s\n' "$NAME" "$STRASSE" "$ORT" "$LAND"
read -rp "Stimmt das? (j/n): " J
case "$J" in j|J|ja|Ja) ;; *) echo "Nichts geändert."; exit 0;; esac

mkdir -p backup
[ -f .env ] && cp -a .env "backup/env_$(date +%Y%m%d_%H%M%S)"
umask 077
{
  if [ -f .env ]; then grep -Ev '^(SI_IMPRESSUM_NAME|SI_IMPRESSUM_ADRESSE)=' .env || true; fi
  echo "SI_IMPRESSUM_NAME='$NAME'"
  echo "SI_IMPRESSUM_ADRESSE='$STRASSE|$ORT|$LAND'"
} > .env.neu
if [ -f .env ]; then cat .env.neu > .env; rm .env.neu; else mv .env.neu .env; fi
echo "✅ Gespeichert in .env."

DIENSTE="soccer-vorschau"
docker compose config --services 2>/dev/null | grep -qx soccer-website && DIENSTE="$DIENSTE soccer-website"
# shellcheck disable=SC2086
docker compose up -d $DIENSTE >/dev/null 2>&1 && echo "✅ Website übernimmt die Angaben (neu erstellt: $DIENSTE)."
echo "Bitte prüfen: https://soccer-intelligence.com/de/impressum/ (vor dem Livegang: /vorschau/de/impressum/)"
