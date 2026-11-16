"""Vorladen im Hintergrund (Version 0.15.1, Code-Prüfung F4, Entscheidung Carsten 16.11.2026).

Das Dashboard speichert Rechenergebnisse zwischen (st.cache_data in state.py). Ändern sich die Daten, rechnet sonst der
erste Besucher einer Seite neu – seit dem täglichen Import also jeden Morgen, bei der Sensitivitätsanalyse rund
40 Sekunden. Darum prüft ein kleiner Hintergrund-Helfer jede Minute, ob sich Datenbank, Spielplan, Konfiguration oder
das Datum geändert haben, und berechnet dann alles vor: Datenbank und Spielplan, Häufigkeit der Anomalien
(Datenqualität), die KPIs der angezeigten Spieltage je Liga (Abschnitte der Ligaseiten, seit 0.16) und die Sensitivitätsanalyse.
Beim Start des Containers (z. B. nach dem Einspielen) läuft das Vorladen sofort.

Der Zwischenspeicher gehört dem ganzen Dashboard-Prozess; was der Helfer berechnet, sehen alle Besucher sofort.
Der Helfer rechnet nur über dieselben Funktionen wie die Seiten – er ändert keine Daten und keine Ergebnisse.
In den Tests ist er ausgeschaltet (Umgebungsvariable SI_VORLADEN=0).
"""

from __future__ import annotations

import logging
import os
import threading
import time
import traceback

import state
from core import settings
from core.files import file_key
from core.anzeige import upcoming

INTERVAL = 60          # Sekunden zwischen zwei Prüfungen


def _data_key() -> tuple:
    files = (settings.DATABASE_FILE, settings.FIXTURES_FILE, settings.THRESHOLDS_FILE, settings.LEAGUES_FILE,
             settings.TEAMS_FILE)
    return tuple(file_key(f) for f in files) + (state.today(),)   # neuer Tag: Abschnitte können wechseln


def warm_up() -> float:
    """Alles vorberechnen, was die Seiten brauchen. Gibt die Dauer in Sekunden zurück."""
    start = time.monotonic()
    db, fx = state.get_database(), state.get_fixtures()
    if db.has_errors or fx.has_errors:             # gesperrte Daten: die Seiten zeigen nur einen Hinweis
        return time.monotonic() - start
    state.get_prepared()
    state.get_thresholds()
    at, last_import = state.now(), state.last_import_day()
    for league in state.get_active_leagues():
        state.get_frequency(league)
        state.get_results(league)
        fixtures = fx.leagues.get(league.name)
        if fixtures is None:
            continue
        view = upcoming(fixtures, at, last_import)            # Abschnitte der Ligaseite (seit 0.16)
        for saison, spieltag in dict.fromkeys(s.key for s in view.sections):
            state.get_matchday_kpis(league, saison, spieltag)
    state.get_closed_matchdays()
    state.get_simulation_cases()
    return time.monotonic() - start


def _loop() -> None:
    # Streamlit warnt ausserhalb einer Seite bei jedem Zwischenspeicher-Aufruf („missing ScriptRunContext“) – harmlos
    logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context").setLevel(logging.ERROR)
    logging.getLogger("streamlit.runtime.caching.cache_data_api").setLevel(logging.ERROR)
    last = None
    while True:
        try:
            key = _data_key()
            if key != last:
                print(f"Vorladen: {warm_up():.0f} Sekunden", flush=True)
                last = key
        except Exception:                                  # nie das Dashboard stören; nächster Versuch in 1 Minute
            traceback.print_exc()
        time.sleep(INTERVAL)


_lock = threading.Lock()
_thread: threading.Thread | None = None


def _wait_for_runtime() -> None:
    """Beim Start über start.py läuft der Helfer, bevor Streamlit bereit ist: kurz warten."""
    from streamlit.runtime import Runtime
    for _ in range(120):
        if Runtime.exists():
            return
        time.sleep(1)


def start() -> threading.Thread | None:
    """Startet den Helfer genau einmal je Dashboard-Prozess – aus start.py beim Containerstart und zur Sicherheit
    auch aus app.py (falls das Dashboard ohne start.py läuft). Ein zweiter Aufruf tut nichts."""
    global _thread
    if os.environ.get("SI_VORLADEN", "1") == "0":
        return None
    with _lock:
        if _thread is None or not _thread.is_alive():
            _thread = threading.Thread(target=lambda: (_wait_for_runtime(), _loop()), name="vorladen", daemon=True)
            _thread.start()
    return _thread
