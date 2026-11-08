"""Kleine Datei-Hilfen, die Datenbank, Spielplan und Zwischenspeicher gemeinsam nutzen."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class FileContent:
    """Der Inhalt einer Datei, einmal gelesen. Prüfsumme und eingelesene Daten gehören so sicher zum selben Stand,
    auch wenn die Datei während des Einlesens ersetzt wird (seit H.2)."""
    data: bytes
    sha256: str
    modified: datetime


def read_file(path: Path) -> FileContent:
    """Datei einmal ganz lesen (nur lesen, nie schreiben). Wirft OSError, z. B. wenn die Datei inzwischen fehlt."""
    with path.open("rb") as fh:
        modified = datetime.fromtimestamp(os.fstat(fh.fileno()).st_mtime, tz=timezone.utc)
        data = fh.read()
    return FileContent(data, hashlib.sha256(data).hexdigest(), modified)


def file_key(path: Path) -> tuple[int, int, int, int]:
    """Kennung des Dateistands für die Zwischenspeicher: Änderungszeit, Grösse, Zeitpunkt der letzten Änderung am
    Dateieintrag (ctime) und Dateinummer (inode).

    ctime und inode ändern sich bei jedem Ersetzen der Datei und lassen sich, anders als die Änderungszeit, nicht
    zurücksetzen. So wird auch eine ersetzte Datei mit gleicher Grösse und gleicher Änderungszeit erkannt (H.2).
    Fehlt die Datei, ist die Kennung (0, 0, 0, 0)."""
    try:
        st = path.stat()
    except OSError:
        return 0, 0, 0, 0
    return st.st_mtime_ns, st.st_size, st.st_ctime_ns, st.st_ino
