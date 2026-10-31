"""Etappe E: Prüfungen der Zugangs-Konfiguration (docker-compose.yml, Platzhalterseite).

Reine Textprüfungen, keine Verbindung zu Docker oder Traefik. Sie stellen sicher, dass
- das Dashboard nur unter /dashboard und nur mit Passwortabfrage erreichbar ist,
- Suchmaschinen den Hinweis „noindex“ erhalten,
- keine Zugangsdaten (Passwort oder Hash) in der versionierten Datei stehen,
- die Platzhalterseite vorhanden ist.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "docker-compose.yml"
PLACEHOLDER = ROOT / "placeholder"

pytestmark = pytest.mark.skipif(not COMPOSE.exists(), reason="docker-compose.yml nicht im Projektordner")


@pytest.fixture(scope="module")
def compose() -> str:
    return COMPOSE.read_text(encoding="utf-8")


def _service_block(text: str, name: str) -> str:
    match = re.search(rf"^  {re.escape(name)}:\n(.*?)(?=^  \S|\Z)", text, re.S | re.M)
    assert match, f"Service {name} fehlt"
    return match.group(1)


def test_dashboard_only_under_dashboard_path(compose):
    block = _service_block(compose, "football-dashboard")
    assert "STREAMLIT_SERVER_BASE_URL_PATH=dashboard" in block
    assert "Host(`soccer-intelligence.com`) && PathPrefix(`/dashboard`)" in block


def test_dashboard_router_uses_password_and_noindex(compose):
    block = _service_block(compose, "football-dashboard")
    assert "routers.soccer.middlewares=soccerintel-auth,soccerintel-noindex" in block
    assert "middlewares.soccerintel-auth.basicauth.users=${SOCCER_DASHBOARD_AUTH:?" in block
    assert "X-Robots-Tag=noindex, nofollow" in block


def test_no_credentials_in_compose(compose):
    # Hash-Formate, die Traefik versteht: bcrypt ($2y$/$2a$/$2b$), Apache-MD5 ($apr1$), SHA1 ({SHA})
    for pattern in (r"\$2[aby]\$", r"\$apr1\$", r"\{SHA\}"):
        assert not re.search(pattern, compose), "Zugangsdaten gehören nur in .env"
    assert "@" not in compose, "Benutzername gehört nur in .env"


def test_env_is_ignored_by_git():
    lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in lines


def test_data_stays_read_only(compose):
    assert "./data:/data:ro" in _service_block(compose, "football-dashboard")


def test_placeholder_service_and_files(compose):
    block = _service_block(compose, "soccer-placeholder")
    assert "./placeholder:/usr/share/nginx/html:ro" in block
    assert "routers.soccer-placeholder.rule=Host(`soccer-intelligence.com`)" in block
    assert "middlewares" not in block                      # Platzhalter bleibt öffentlich
    html = (PLACEHOLDER / "index.html").read_text(encoding="utf-8")
    assert "Soccer Intelligence" in html
    assert "<script" not in html and "http" not in html.split("</head>")[0].lower()  # nichts Externes
    assert "Disallow: /dashboard" in (PLACEHOLDER / "robots.txt").read_text(encoding="utf-8")


def test_password_script_stores_only_hash():
    script = (ROOT / "tools" / "dashboard_passwort.sh").read_text(encoding="utf-8")
    assert "read -rsp" in script                         # Passwort verdeckt eingeben
    assert "htpasswd -niB" in script                     # bcrypt-Hash
    assert "SOCCER_DASHBOARD_AUTH='$H'" in script        # nur der Hash landet in .env
    assert "set -euo pipefail" in script                 # bei Fehlern sofort abbrechen
