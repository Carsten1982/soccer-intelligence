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


def test_dashboard_router_login_ratelimit_noindex(compose):
    """Seit 0.15.2: keine Passwortabfrage des Browsers mehr (BasicAuth), dafür Anmeldemaske im Dashboard mit
    Zugangsdaten aus .env und eine Anfragebremse je Adresse; „noindex“ bleibt."""
    block = _service_block(compose, "football-dashboard")
    assert "routers.soccer.middlewares=soccerintel-ratelimit,soccerintel-noindex" in block
    assert "basicauth" not in block
    assert "soccerintel-ratelimit.ratelimit.average=30" in block and "ratelimit.burst=100" in block
    assert "SI_LOGIN_USER=${SI_LOGIN_USER:-}" in block and "SI_LOGIN_HASH=${SI_LOGIN_HASH:-}" in block
    assert "X-Robots-Tag=noindex, nofollow" in block


def test_app_requires_login_before_navigation():
    app = (ROOT / "app" / "app.py").read_text(encoding="utf-8")
    assert app.index("anmeldung.require_login()") < app.index("st.navigation(")


def test_server_runs_fast_tests_github_all():
    """0.15.2: Beim Einspielen nur die schnellen Tests; GitHub prüft bei jedem Pull Request alle."""
    script = (ROOT / "tools" / "einspielen.sh").read_text(encoding="utf-8")
    assert "-m 'not langsam' tests" in script
    wf = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
    assert "python -m pytest -q -p no:cacheprovider tests" in wf and "langsam" not in wf


def test_no_credentials_in_compose(compose):
    # Hash-Formate, die Traefik versteht: bcrypt ($2y$/$2a$/$2b$), Apache-MD5 ($apr1$), SHA1 ({SHA})
    for pattern in (r"\$2[aby]\$", r"\$apr1\$", r"\{SHA\}"):
        assert not re.search(pattern, compose), "Zugangsdaten gehören nur in .env"
    assert "@" not in compose, "Benutzername gehört nur in .env"
    assert "pbkdf2:" not in compose, "Passwort-Hash gehört nur in .env"


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


def test_preview_service_only_under_vorschau_with_password(compose):
    """Seit 0.17: Vorschau der Website nur unter /vorschau, mit Passwortabfrage (Hash nur in .env), Anfragebremse und
    noindex; liest data/ und import/ nur; kein Port nach aussen."""
    block = _service_block(compose, "soccer-vorschau")
    assert 'command: ["python", "-m", "website.vorschau"]' in block
    assert "Host(`soccer-intelligence.com`) && PathPrefix(`/vorschau`)" in block
    assert "routers.soccervorschau.middlewares=soccervorschau-auth,soccerintel-ratelimit,soccerintel-noindex" in block
    assert "soccervorschau-auth.basicauth.users=${SOCCER_VORSCHAU_AUTH:-}" in block
    assert "./data:/data:ro" in block and "./import:/import:ro" in block and "ports" not in block
    assert "loadbalancer.server.port=8080" in block and "SI_VORSCHAU_PORT=8080" in block


def test_preview_photo_only_on_server():
    """Seit 0.18 (Q6): Das Foto der Startseite liegt nur auf dem Server in website-bilder/ (nur lesend eingebunden),
    nie in Git und nie im Image (Dockerfile kopiert nur app/)."""
    block = _service_block((ROOT / "docker-compose.yml").read_text(encoding="utf-8"), "soccer-vorschau")
    assert "./website-bilder:/bilder:ro" in block
    assert "website-bilder/" in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    kopien = [z for z in (ROOT / "Dockerfile").read_text(encoding="utf-8").splitlines() if z.startswith(("COPY", "ADD"))]
    assert kopien == ["COPY requirements.txt .", "COPY app/ /app/"]      # (auf dem Server liegt das Foto im Ordner)


def test_preview_password_script_stores_only_hash():
    script = (ROOT / "tools" / "vorschau_passwort.sh").read_text(encoding="utf-8")
    assert "read -rsp" in script and "htpasswd -niB" in script
    assert 'echo "SOCCER_VORSCHAU_AUTH=\'$H\'"' in script and "grep -v '^SOCCER_VORSCHAU_AUTH='" in script
    assert "unset P1 P2" in script and "$P1" not in script.split("unset P1 P2")[1]
    assert "set -euo pipefail" in script and "backup/env_" in script


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
    """Seit 0.15.2: Benutzername und PBKDF2-Hash für die Anmeldemaske; das Passwort selbst landet nirgends."""
    script = (ROOT / "tools" / "dashboard_passwort.sh").read_text(encoding="utf-8")
    assert "read -rsp" in script                         # Passwort verdeckt eingeben
    assert 'echo "SI_LOGIN_HASH=$H"' in script and 'echo "SI_LOGIN_USER=$U"' in script
    assert "pbkdf2_hmac" in script and "600000" in script
    assert "-e '^SI_LOGIN_USER=' -e '^SI_LOGIN_HASH='" in script   # andere Zeilen in .env bleiben
    assert "unset P1 P2" in script and "$P1" not in script.split("unset P1 P2")[1]
    assert "set -euo pipefail" in script                 # bei Fehlern sofort abbrechen


def test_password_script_hash_matches_app():
    """Das Skript rechnet gleich wie app/anmeldung.py: ein dort erzeugter Hash wird von der App erkannt."""
    import hashlib

    import anmeldung
    salt, n = bytes(range(16)), 600000
    stored = "pbkdf2:sha256:%d:%s:%s" % (n, salt.hex(), hashlib.pbkdf2_hmac("sha256", b"Ein-Passwort-123", salt, n).hex())
    assert anmeldung.check_password("Ein-Passwort-123", stored) and not anmeldung.check_password("x", stored)


# --- Einspiel-Skripte (seit 09.11.2026): nur unser Container, nie data/ ---------------------------------------

SCRIPTS = [ROOT / "tools" / "einspielen.sh", ROOT / "tools" / "zurueck.sh"]
OUR_SERVICES = {"football-dashboard", "soccer-import", "soccer-vorschau", "soccer-website"}   # seit 0.27 die Website


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.name)
def test_release_scripts_touch_only_our_container(script):
    text = script.read_text(encoding="utf-8")
    code = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
    for forbidden in ("compose down", "docker stop", "docker rm", "docker system", "prune", "rm -rf", "restart",
                      "git push -f", "--force", "git clean"):
        assert forbidden not in code, f"{script.name}: verboten: {forbidden}"
    assert "set -euo pipefail" in code                               # bricht bei jedem Fehler ab
    for line in code.splitlines():
        if "docker compose stop" in line:                          # seit 0.27: Rückweg stoppt nur die eigene Website
            assert set(line.split("docker compose stop", 1)[1].split(">")[0].split()) <= OUR_SERVICES, line
        elif "docker compose" in line:
            assert "up -d --build football-dashboard" in line, line     # nur unsere Services (seit 0.14 auch Import)
            assert set(line.split("--build", 1)[1].split(">")[0].split()) <= OUR_SERVICES, line
        if "docker " in line and "inspect" in line or "docker logs" in line:
            assert any(name in line for name in OUR_SERVICES), line
    assert "data/" not in code.replace("data/*|", "")                # data/ nur in der Sperrliste für Löschungen


def test_release_script_asks_and_never_commits():
    code = SCRIPTS[0].read_text(encoding="utf-8")
    assert "read -rp" in code                                         # fragt am Schluss j/n
    assert "zurueck.sh" in code                                       # nennt den Rückweg
    assert "git commit" not in code and "git push" not in code        # seit 0.24 nur noch Weg github: nie eigener Commit


def test_github_weg_holt_nur_von_github():
    code = SCRIPTS[0].read_text(encoding="utf-8")
    assert "merge -q --ff-only" in code                               # Server bekommt genau den Stand von GitHub
    assert "zipfile" not in code and "release.zip\"" not in code      # seit 0.24 kein ZIP-Weg mehr


def test_automatische_tests_auf_github():
    wf = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
    assert 'python-version: "3.12"' in wf
    assert "pip install -r requirements-dev.txt" in wf
    assert "python -m pytest -q -p no:cacheprovider tests" in wf
    assert "permissions:\n  contents: read" in wf                     # nur lesen
    assert "secrets." not in wf and "ssh" not in wf.lower()           # kein Zugang zum Server


def test_skripte_erwarten_die_weiterleitung_der_website(monkeypatch):
    """Fehler gefunden in 0.27 vor dem Einspielen: zurueck.sh erwartete für / den Code 302, die Website leitet aber
    dauerhaft (301) auf /de/ weiter – der Rückweg wäre fälschlich gestoppt. Skripte und Website müssen übereinstimmen."""
    import sys
    sys.path.insert(0, str(ROOT / "app"))
    from website import einstellungen as W
    from website import vorschau
    monkeypatch.setattr(W, "PREFIX", "")
    monkeypatch.setattr(W, "VORSCHAU", False)
    code = str(vorschau.beantworten("/", "").status)
    assert code == "301"
    assert f'[ "$P" = {code} ]' in (ROOT / "tools" / "zurueck.sh").read_text(encoding="utf-8")
    assert f"200|{code})" in (ROOT / "tools" / "einspielen.sh").read_text(encoding="utf-8")


def test_website_container_livegang():
    """0.27: Website als eigener Container unter / – ohne Passwort, ohne noindex, eigene Middlewares (hängt nicht an den
    Labels von Dashboard oder Vorschau), Vorrang vor der Platzhalterseite, Daten nur lesend."""
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    block = compose.split("\n  soccer-website:\n", 1)[1].split("\n  soccer-placeholder:\n", 1)[0]
    zeilen = [z.strip() for z in block.splitlines() if not z.strip().startswith("#")]
    assert "- SI_VORSCHAU_PREFIX=" in zeilen and "container_name: soccer-website" in zeilen
    assert '- "traefik.http.routers.soccerweb.rule=Host(`soccer-intelligence.com`)"' in zeilen   # ganze Domain
    assert '- "traefik.http.routers.soccerweb.priority=40"' in zeilen
    mw = next(z for z in zeilen if "routers.soccerweb.middlewares=" in z).split("=", 1)[1].strip('"').split(",")
    assert mw == ["soccerweb-ratelimit", "soccerweb-compress", "soccerweb-hsts"]
    for name in mw:                                                  # in diesem Container selbst definiert
        assert any(f"traefik.http.middlewares.{name}." in z for z in zeilen), name
    assert "noindex" not in block and "basicauth" not in block and "SOCCER_VORSCHAU_AUTH" not in block
    assert "- ./data:/data:ro" in zeilen and "- ./import:/import:ro" in zeilen and "ports:" not in block
    # gleiche Werte wie die gemeinsamen Middlewares von Dashboard und Vorschau
    for alt, neu in (("soccerintel-ratelimit.ratelimit.average=30", "soccerweb-ratelimit.ratelimit.average=30"),
                     ("soccerintel-ratelimit.ratelimit.burst=100", "soccerweb-ratelimit.ratelimit.burst=100"),
                     ("soccerintel-hsts.headers.stsSeconds=31536000", "soccerweb-hsts.headers.stsSeconds=31536000")):
        assert alt in compose and neu in block
    # Priorität 40 schlägt die Platzhalterseite (Traefik: Länge der Regel), aber nicht /dashboard und /vorschau
    regel = lambda router: re.search(rf"routers\.{re.escape(router)}\.rule=([^\"]+)\"", compose).group(1)
    assert len(regel("soccer-placeholder")) < 40 < min(len(regel("soccer")), len(regel("soccervorschau")))
