"""Anmeldung am Dashboard (Version 0.15.2, Entscheidung Carsten 16.11.2026).

Ersetzt die Passwortabfrage des Browsers (Traefik BasicAuth), die auf manchen Arbeitsrechnern gesperrt ist, durch eine
Anmeldemaske im Dashboard: Benutzername und Passwort, danach ist das Dashboard 12 Stunden entsperrt („Abmelden“ jederzeit).

Sicherheit:
- Benutzername und Passwort stehen nur auf dem Server in `.env` (SI_LOGIN_USER, SI_LOGIN_HASH), nie im Code oder in Git.
  Vom Passwort wird nur ein Hash gespeichert: PBKDF2-SHA256 mit Zufallssalz und 600'000 Durchläufen, Schreibweise
  `pbkdf2:sha256:<Durchläufe>:<Salz hex>:<Hash hex>` (ohne „$“, damit docker compose nichts ersetzt).
- Fehlt die Einrichtung, bleibt das Dashboard gesperrt (nie offen).
- Nach der Anmeldung setzt die Seite ein Cookie mit Ablaufzeit (12 Stunden). Es ist mit einem Schlüssel signiert, der
  aus dem gespeicherten Hash abgeleitet wird: Ein neues Passwort macht alle alten Anmeldungen ungültig.
- Schutz vor Durchprobieren: je Besucher-Adresse (IP laut Traefik) nach 5 Fehlversuchen 15 Minuten Sperre, dazu
  wartet jede falsche Eingabe 1 Sekunde. Traefik begrenzt zusätzlich die Anfragen je Adresse (docker-compose.yml).
- Vergleiche mit hmac.compare_digest (keine Rückschlüsse über die Antwortzeit).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import threading
import time

import streamlit as st

COOKIE = "si_anmeldung"
HOURS = 12
MAX_FAILURES = 5
LOCK_SECONDS = 15 * 60
FAIL_DELAY = 1.0                                  # Sekunden Wartezeit nach jeder falschen Eingabe
SESSION_KEY = "si_angemeldet"
LOGGED_OUT = "si_abgemeldet"                      # nach „Abmelden“: Cookie in dieser Sitzung nicht mehr gelten lassen

_failures: dict[str, list[float]] = {}          # Adresse -> Zeitpunkte der Fehlversuche (im Dashboard-Prozess)
_lock = threading.Lock()


# --- Passwort und Token (ohne Streamlit, testbar) ------------------------------------------------------------------

def make_hash(password: str, iterations: int = 600_000, salt: bytes | None = None) -> str:
    """Hash für .env erzeugen (dieselbe Rechnung wie der Befehl in docs/01, Abschnitt 6.6)."""
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2:sha256:{iterations}:{salt.hex()}:{digest.hex()}"


def check_password(password: str, stored: str) -> bool:
    try:
        kind, algo, iterations, salt, digest = stored.strip().split(":")
        if kind != "pbkdf2" or algo != "sha256":
            return False
        test = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), int(iterations))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(test.hex(), digest)


def _key(stored: str) -> bytes:
    return hashlib.sha256(("soccer-intelligence-anmeldung|" + stored.strip()).encode("utf-8")).digest()


def make_token(user: str, stored: str, now: float | None = None, hours: int = HOURS) -> str:
    expires = int((now or time.time()) + hours * 3600)
    body = f"{user.strip().lower()}|{expires}"
    sig = hmac.new(_key(stored), body.encode("utf-8"), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{body}|{sig}".encode("utf-8")).decode("ascii")


def check_token(token: str | None, user: str, stored: str, now: float | None = None) -> bool:
    if not token or not isinstance(token, str):
        return False
    try:
        name, expires, sig = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8").rsplit("|", 2)
        body = f"{name}|{expires}"
        good = hmac.new(_key(stored), body.encode("utf-8"), hashlib.sha256).hexdigest()
        return (hmac.compare_digest(sig, good) and name == user.strip().lower()
                and int(expires) > (now or time.time()))
    except (ValueError, TypeError, UnicodeDecodeError):
        return False


def locked_for(address: str, now: float | None = None) -> int:
    """Sekunden, die diese Adresse noch gesperrt ist (0 = nicht gesperrt)."""
    now = now or time.time()
    with _lock:
        recent = [t for t in _failures.get(address, []) if now - t < LOCK_SECONDS]
        _failures[address] = recent
        if len(recent) < MAX_FAILURES:
            return 0
        return int(LOCK_SECONDS - (now - recent[-MAX_FAILURES]))


def note_failure(address: str, now: float | None = None) -> None:
    with _lock:
        _failures.setdefault(address, []).append(now or time.time())


def config() -> tuple[str, str] | None:
    user, stored = os.environ.get("SI_LOGIN_USER", "").strip(), os.environ.get("SI_LOGIN_HASH", "").strip()
    return (user, stored) if user and stored else None


# --- Streamlit ---------------------------------------------------------------------------------------------------

def _address() -> str:
    try:
        headers = st.context.headers or {}
        forwarded = headers.get("X-Forwarded-For") or headers.get("X-Real-Ip") or ""
        return str(forwarded).split(",")[0].strip() or "unbekannt"
    except Exception:                                  # z. B. ohne Browser (Tests)
        return "unbekannt"


def cookie_script(value: str, max_age: int) -> str:
    """Kleines Skript, das das Cookie im Browser setzt (Pfad /dashboard, nur über HTTPS)."""
    return (f"<script>window.parent.document.cookie = '{COOKIE}={value}; max-age={max_age}; path=/dashboard; "
            f"SameSite=Strict; Secure';</script>")


def _set_cookie(value: str, max_age: int) -> None:
    """Cookie im Browser setzen (Streamlit kann das nur über ein kleines Skript). Seit 0.19.1 mit st.iframe statt
    components.html (wird nach 2026-06-01 entfernt, Bereinigung B6); 1 Pixel hoch, weil 0 nicht erlaubt ist."""
    st.iframe(cookie_script(value, max_age), height=1)


def require_login() -> None:
    """Sperrt das Dashboard, bis die Anmeldung gültig ist. Aufruf ganz am Anfang von app.py."""
    cfg = config()
    if cfg is None:
        st.title("Soccer Intelligence")
        st.error("Die Anmeldung ist auf dem Server nicht eingerichtet (SI_LOGIN_USER und SI_LOGIN_HASH fehlen in .env). "
                 "Das Dashboard bleibt gesperrt.", icon="🔒")
        st.stop()
    user, stored = cfg
    cookie_ok = not st.session_state.get(LOGGED_OUT) and check_token(st.context.cookies.get(COOKIE), user, stored)
    if st.session_state.get(SESSION_KEY) or cookie_ok:
        st.session_state[SESSION_KEY] = True
        token = st.session_state.pop("si_neues_token", None)
        if token:
            _set_cookie(token, HOURS * 3600)
        return
    if st.session_state.get(LOGGED_OUT):
        _set_cookie("", 0)                            # Cookie im Browser löschen
    _login_form(user, stored)
    st.stop()


def _login_form(user: str, stored: str) -> None:
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("## Soccer Intelligence")
        st.caption("Internes Dashboard – bitte anmelden")
        address = _address()
        wait = locked_for(address)
        if wait:
            st.error(f"Zu viele Fehlversuche. Bitte in {wait // 60 + 1} Minuten erneut versuchen.", icon="⏳")
            return
        with st.form("anmeldung"):
            name = st.text_input("Benutzername", autocomplete="username")
            password = st.text_input("Passwort", type="password", autocomplete="current-password")
            sent = st.form_submit_button("Anmelden", type="primary", width="stretch")
        if sent:
            ok_user = hmac.compare_digest(name.strip().lower(), user.strip().lower())
            if ok_user and check_password(password, stored):
                st.session_state[SESSION_KEY] = True
                st.session_state.pop(LOGGED_OUT, None)
                st.session_state["si_neues_token"] = make_token(user, stored)
                st.rerun()
            note_failure(address)
            time.sleep(FAIL_DELAY)
            st.error("Benutzername oder Passwort falsch.")


def logout_button() -> None:
    """„Abmelden“ unten auf jeder Seite."""
    if st.button("Abmelden", key="si_abmelden"):
        st.session_state.pop(SESSION_KEY, None)
        st.session_state[LOGGED_OUT] = True
        st.rerun()
