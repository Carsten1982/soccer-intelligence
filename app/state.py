"""Laden der Datenbank mit Cache.

Der Cache-Schlüssel enthält Änderungszeit und Grösse der Datei. Wird die Excel-Datei
auf dem Server ersetzt, liest die App sie beim nächsten Seitenaufruf automatisch neu ein –
ohne Neustart des Containers.
"""

from __future__ import annotations

from zoneinfo import ZoneInfo

import streamlit as st

from core import settings
from core.issues import FEHLER, HINWEIS, WARNUNG
from core.loader import DatabaseLoad, load_database

TZ = ZoneInfo(settings.TIMEZONE)


@st.cache_data(show_spinner="Datenbank wird eingelesen …", max_entries=2)
def _cached_load(path: str, mtime_ns: int, size: int) -> DatabaseLoad:  # noqa: ARG001 - Teil des Cache-Schlüssels
    return load_database(path)


def get_database() -> DatabaseLoad:
    path = settings.DATABASE_FILE
    try:
        stat = path.stat()
        key = (stat.st_mtime_ns, stat.st_size)
    except OSError:
        key = (0, 0)
    return _cached_load(str(path), *key)


def fmt_dt(dt) -> str:
    return dt.astimezone(TZ).strftime("%d.%m.%Y, %H:%M Uhr") if dt else "-"


def status_banner(db: DatabaseLoad) -> None:
    e, w, h = db.count(FEHLER), db.count(WARNUNG), db.count(HINWEIS)
    if e:
        st.error(f"**Datenbank nicht verwendbar:** {e} Fehler gefunden. Details unter *Datenqualität*.", icon="⛔")
    elif w:
        st.warning(f"Datenbank geladen mit {w} Warnung(en) und {h} Hinweis(en). Details unter *Datenqualität*.", icon="⚠️")
    else:
        st.success(f"Datenbank geprüft: keine Fehler, keine Warnungen ({h} Hinweis(e)).", icon="✅")
