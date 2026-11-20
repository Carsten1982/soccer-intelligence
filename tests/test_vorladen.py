"""Version 0.15.1 (Code-Prüfung F4): Vorladen im Hintergrund nach jeder Datenänderung und beim Containerstart."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

pytest.importorskip("streamlit")
import vorladen  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def test_switched_off_in_tests():
    assert vorladen.start() is None                    # SI_VORLADEN=0 (conftest)


def test_warm_up_prepares_all_pages(monkeypatch):
    """Vorgeladen wird genau das, was die Seiten brauchen: Datenbank, Spielplan, Häufigkeit, Ergebnisse, KPIs der
    Abschnitte je Liga (seit 0.16; ein Spieltag mit zwei Abschnitten nur einmal), Sensitivitätsanalyse."""
    calls = []
    league = SimpleNamespace(name="Bundesliga")
    fx = SimpleNamespace(has_errors=False, leagues={"Bundesliga": "plan"})
    db = SimpleNamespace(has_errors=False)
    st = vorladen.state
    monkeypatch.setattr(st, "get_database", lambda: calls.append("db") or db)
    monkeypatch.setattr(st, "get_fixtures", lambda: calls.append("fx") or fx)
    for name in ("get_prepared", "get_thresholds", "get_closed_matchdays", "get_simulation_cases"):
        monkeypatch.setattr(st, name, lambda n=name: calls.append(n))
    monkeypatch.setattr(st, "get_active_leagues", lambda: [league])
    monkeypatch.setattr(st, "get_frequency", lambda lg: calls.append("frequency"))
    monkeypatch.setattr(st, "get_matchday_kpis", lambda lg, s, m: calls.append(("kpis", s, m)))
    monkeypatch.setattr(st, "get_results", lambda lg: calls.append("results"))
    monkeypatch.setattr(st, "last_import", lambda: None)
    sections = [SimpleNamespace(key=("2026/2027", 11)), SimpleNamespace(key=("2026/2027", 23)),
                SimpleNamespace(key=("2026/2027", 11))]
    monkeypatch.setattr(vorladen, "upcoming", lambda f, at, imp: SimpleNamespace(sections=sections))
    vorladen.warm_up()
    assert calls == ["db", "fx", "get_prepared", "get_thresholds", "frequency", "results", ("kpis", "2026/2027", 11),
                     ("kpis", "2026/2027", 23), "get_closed_matchdays", "get_simulation_cases"]


def test_blocked_data_is_not_computed(monkeypatch):
    st = vorladen.state
    monkeypatch.setattr(st, "get_database", lambda: SimpleNamespace(has_errors=True))
    monkeypatch.setattr(st, "get_fixtures", lambda: SimpleNamespace(has_errors=False))
    monkeypatch.setattr(st, "get_simulation_cases", lambda: pytest.fail("darf nicht rechnen"))
    vorladen.warm_up()


def test_dockerfile_starts_with_warm_up():
    assert 'CMD ["python", "start.py"' in (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "vorladen.start()" in (ROOT / "app" / "start.py").read_text(encoding="utf-8")
