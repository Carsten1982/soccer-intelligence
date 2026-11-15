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


def test_import_service(compose):
    """Version 0.14: nur der Import schreibt in data/; kein Zugang von aussen; Schlüssel nur aus .env."""
    block = _service_block(compose, "soccer-import")
    assert "- ./data:/data " in block and "./data:/data:ro" not in block and "traefik" not in block and "ports" not in block
    assert "API_FOOTBALL_KEY=${API_FOOTBALL_KEY:-}" in block and 'command: ["python", "-m", "importer.dienst"]' in block
    dash = _service_block(compose, "football-dashboard")
    assert "./import:/import:ro" in dash and "./import/anfragen:/import/anfragen" in dash


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


# --- Einspiel-Skripte (seit 09.11.2026): nur unser Container, nie data/ ---------------------------------------

SCRIPTS = [ROOT / "tools" / "einspielen.sh", ROOT / "tools" / "zurueck.sh"]


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.name)
def test_release_scripts_touch_only_our_container(script):
    text = script.read_text(encoding="utf-8")
    code = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
    for forbidden in ("compose down", "docker stop", "docker rm", "docker system", "prune", "rm -rf", "restart",
                      "git push -f", "--force", "git clean"):
        assert forbidden not in code, f"{script.name}: verboten: {forbidden}"
    assert "set -euo pipefail" in code                               # bricht bei jedem Fehler ab
    for line in code.splitlines():
        if "docker compose" in line:
            assert "up -d --build football-dashboard" in line, line     # nur unsere Services (seit 0.14 auch Import)
            assert set(line.split("--build", 1)[1].split(">")[0].split()) <= {"football-dashboard", "soccer-import"}, line
        if "docker " in line and "inspect" in line or "docker logs" in line:
            assert "football-dashboard" in line or "soccer-import" in line, line
    assert "data/" not in code.replace("data/*|", "")                # data/ nur in der Sperrliste für Löschungen


def test_release_script_asks_before_commit():
    code = SCRIPTS[0].read_text(encoding="utf-8")
    assert code.index("read -rp") < code.index("git commit")          # Commit erst nach j/n
    assert "zurueck.sh" in code                                       # nennt den Rückweg


def test_github_weg_holt_nur_von_github():
    code = SCRIPTS[0].read_text(encoding="utf-8")
    assert "merge -q --ff-only" in code                               # Server bekommt genau den Stand von GitHub
    assert code.index('if [ "$WEG" = github ]; then\n  read -rp') < code.index("git commit")  # kein Commit im Weg github


def test_automatische_tests_auf_github():
    wf = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
    assert 'python-version: "3.12"' in wf
    assert "pip install -r requirements-dev.txt" in wf
    assert "python -m pytest -q -p no:cacheprovider tests" in wf
    assert "permissions:\n  contents: read" in wf                     # nur lesen
    assert "secrets." not in wf and "ssh" not in wf.lower()           # kein Zugang zum Server
