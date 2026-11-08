"""Kleine Datei-Hilfen, die Datenbank und Spielplan gemeinsam nutzen."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_of(path: Path) -> str:
    """Prüfsumme der Datei (SHA-256), in Blöcken von 1 MB gelesen."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
