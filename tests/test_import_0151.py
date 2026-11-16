"""Version 0.15.1: Absicherung der Übernahme nach der Code-Prüfung vom 16.11.2026 (F1, F2).

F1: Datenbank und Spielplan werden mit Übergabe-Protokoll getauscht. Bricht der Tausch mitten drin ab, führt recover()
    ihn zu Ende – nie bleibt ein Mischstand aus alter und neuer Datei.
F2: Vor dem Tausch werden beide Dateien der Fassung gegen die Prüfsummen im Bericht geprüft; Backups haben eindeutige
    Namen und werden nie überschrieben.
"""

from __future__ import annotations

import os
from datetime import datetime

import pytest
from test_import import TZ, FakeApi, details, halves, season_list  # noqa: F401 (Fixtures)
from test_import_015 import base_db, env, run  # noqa: F401 (Fixtures)

from importer import dienst
from importer.erzeugen import sha256

DB, FX = "Database-Soccer-Intelligence.xlsx", "Spielplan.xlsx"
WHEN = datetime(2026, 11, 10, 4, 0, tzinfo=TZ)
LATER = datetime(2026, 11, 10, 8, 0, tzinfo=TZ)


@pytest.mark.langsam
def test_interrupted_swap_is_completed(base_db, season_list, details, halves, tmp_path, monkeypatch):
    """Abbruch zwischen den beiden Dateien: neue Datenbank, alter Spielplan -> recover() führt den Tausch zu Ende."""
    e = env(tmp_path, base_db)
    rep = run(e, WHEN, FakeApi(season_list, details, halves))
    old_fx = sha256(e["data"] / FX)
    real, calls = os.replace, []

    def failing(src, dst):                    # 1. Protokoll, 2. Datenbank, 3. Spielplan -> bricht ab
        calls.append(dst)
        if len(calls) == 3:
            raise OSError("Abbruch (Test)")
        real(src, dst)
    monkeypatch.setattr(dienst.os, "replace", failing)
    with pytest.raises(OSError):
        dienst.apply(e["base"], e["data"], e["backup"], rep["lauf"], "uebernehmen", "Test", LATER)
    monkeypatch.setattr(dienst.os, "replace", real)
    assert sha256(e["data"] / DB) == rep["dateien"]["datenbank"] and sha256(e["data"] / FX) == old_fx   # Mischstand
    assert (e["base"] / dienst.HANDOVER).exists()
    assert "zu Ende geführt" in dienst.recover(e["base"], e["data"], LATER)
    assert sha256(e["data"] / FX) == rep["dateien"]["spielplan"] and sha256(e["data"] / DB) == rep["dateien"]["datenbank"]
    assert dienst.load_report(e["base"], rep["lauf"])["status"] == "übernommen"
    assert dienst.load_state(e["base"])["wartend"] is None and not (e["base"] / dienst.HANDOVER).exists()
    assert dienst.recover(e["base"], e["data"], LATER) is None          # nichts mehr zu tun


@pytest.mark.langsam
def test_changed_or_missing_staged_file_is_refused(base_db, season_list, details, halves, tmp_path):
    """F2: Fassung verändert oder unvollständig -> keine Übernahme, gültige Dateien und Backups unverändert."""
    e = env(tmp_path, base_db)
    before = {n: sha256(e["data"] / n) for n in (DB, FX)}
    rep = run(e, WHEN, FakeApi(season_list, details, halves))
    staged = e["base"] / "laeufe" / rep["lauf"]
    with (staged / FX).open("ab") as fh:
        fh.write(b"x")
    msg = dienst.apply(e["base"], e["data"], e["backup"], rep["lauf"], "uebernehmen", "Test", LATER)
    assert "beschädigt oder verändert" in msg and "Spielplan" in msg
    assert {n: sha256(e["data"] / n) for n in (DB, FX)} == before and not e["backup"].exists()
    assert dienst.load_report(e["base"], rep["lauf"])["status"] == "Fehler – nicht übernehmbar"
    rep2 = run(e, WHEN.replace(hour=5), FakeApi(season_list, details, halves))
    (e["base"] / "laeufe" / rep2["lauf"] / DB).unlink()
    msg = dienst.apply(e["base"], e["data"], e["backup"], rep2["lauf"], "uebernehmen", "Test", LATER)
    assert "Database" in msg and {n: sha256(e["data"] / n) for n in (DB, FX)} == before


def test_backup_names_are_unique(tmp_path):
    """F2: Zwei Backups in derselben Sekunde überschreiben sich nicht."""
    data, base, backup = tmp_path / "data", tmp_path / "import", tmp_path / "backup"
    data.mkdir()
    base.mkdir()
    for n in (DB, FX):
        (data / n).write_bytes(b"alt")
    dienst._backup(base, data, backup, "2026-11-16_040000", LATER)
    for n in (DB, FX):
        (data / n).write_bytes(b"neu")
    dienst._backup(base, data, backup, "2026-11-16_040000", LATER)
    files = sorted(p.name for p in backup.iterdir())
    assert len(files) == 4 and sum(f.endswith("_2_vor_import.xlsx") for f in files) == 2
    contents = sorted(p.read_bytes() for p in backup.glob("Database-*"))
    assert contents == [b"alt", b"neu"]                                  # nichts überschrieben
