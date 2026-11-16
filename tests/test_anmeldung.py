"""Version 0.15.2: Anmeldemaske statt Passwortabfrage des Browsers (Entscheidung Carsten 16.11.2026).

Geprüft ohne echte Zugangsdaten (Testpasswort): Hash, signiertes Cookie mit Ablauf, Sperre nach Fehlversuchen,
gesperrtes Dashboard ohne Einrichtung und die Maske selbst (falsches Passwort, richtiges Passwort, Abmelden).
"""

from __future__ import annotations

import pytest

pytest.importorskip("streamlit")
import anmeldung  # noqa: E402

try:
    from streamlit.testing.v1 import AppTest
except ImportError:  # pragma: no cover
    AppTest = None

PASSWORD = "Test-Passwort-123"
USER = "Tester@Example.org"
STORED = anmeldung.make_hash(PASSWORD, iterations=1_000, salt=b"0123456789abcdef")


def test_hash_has_no_dollar_and_checks():
    stored = anmeldung.make_hash(PASSWORD, iterations=1_000)
    assert stored.startswith("pbkdf2:sha256:1000:") and "$" not in stored
    assert anmeldung.check_password(PASSWORD, stored)
    assert not anmeldung.check_password("falsch", stored)
    assert not anmeldung.check_password(PASSWORD, "kaputt") and not anmeldung.check_password(PASSWORD, "")


def test_token_valid_12_hours_and_signed():
    now = 1_800_000_000
    token = anmeldung.make_token(USER, STORED, now=now)
    assert anmeldung.check_token(token, USER.lower(), STORED, now=now + 11 * 3600)
    assert not anmeldung.check_token(token, USER, STORED, now=now + 12 * 3600 + 1)        # abgelaufen
    assert not anmeldung.check_token(token, "anderer@example.org", STORED, now=now)
    new_stored = anmeldung.make_hash("neues Passwort", iterations=1_000)
    assert not anmeldung.check_token(token, USER, new_stored, now=now)                     # neues Passwort
    forged = token[:-4] + ("AAAA" if not token.endswith("AAAA") else "BBBB")
    assert not anmeldung.check_token(forged, USER, STORED, now=now) and not anmeldung.check_token("", USER, STORED)


def test_lock_after_five_failures():
    addr, t = "198.51.100.7", 1_800_000_000
    for i in range(4):
        anmeldung.note_failure(addr, now=t + i)
    assert anmeldung.locked_for(addr, now=t + 5) == 0
    anmeldung.note_failure(addr, now=t + 5)
    assert anmeldung.locked_for(addr, now=t + 6) > 14 * 60
    assert anmeldung.locked_for(addr, now=t + 16 * 60) == 0                                # nach 15 Minuten frei


def _gate():
    import streamlit as st

    import anmeldung as a
    a.require_login()
    st.write("geheimer Inhalt")
    a.logout_button()


@pytest.mark.skipif(AppTest is None, reason="Streamlit-Testwerkzeug nicht vorhanden")
def test_login_form_wrong_and_right_password(monkeypatch):
    monkeypatch.setenv("SI_LOGIN_USER", USER)
    monkeypatch.setenv("SI_LOGIN_HASH", STORED)
    monkeypatch.setattr(anmeldung, "FAIL_DELAY", 0)
    at = AppTest.from_function(_gate, default_timeout=30).run()
    text = "\n".join(str(m.value) for m in at.markdown)
    assert "geheimer Inhalt" not in text and len(at.text_input) == 2
    at.text_input[0].input("tester@example.org")                          # Gross-/Kleinschreibung egal
    at.text_input[1].input("falsch")
    at.button[0].click().run()
    assert any("falsch" in str(e.value) for e in at.error)
    assert "geheimer Inhalt" not in "\n".join(str(m.value) for m in at.markdown)
    at.text_input[0].input(USER)
    at.text_input[1].input(PASSWORD)
    at.button[0].click().run()
    assert "geheimer Inhalt" in "\n".join(str(m.value) for m in at.markdown)
    at.button(key="si_abmelden").click().run()                              # Abmelden -> Maske
    assert "geheimer Inhalt" not in "\n".join(str(m.value) for m in at.markdown)


@pytest.mark.skipif(AppTest is None, reason="Streamlit-Testwerkzeug nicht vorhanden")
def test_dashboard_stays_locked_without_setup(monkeypatch):
    monkeypatch.delenv("SI_LOGIN_USER", raising=False)
    monkeypatch.delenv("SI_LOGIN_HASH", raising=False)
    at = AppTest.from_function(_gate, default_timeout=30).run()
    assert any("nicht eingerichtet" in str(e.value) for e in at.error)
    assert "geheimer Inhalt" not in "\n".join(str(m.value) for m in at.markdown)
