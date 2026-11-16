"""Probelauf der Einspiel-Skripte tools/einspielen.sh und tools/zurueck.sh (seit 09.11.2026).

Jeder Test baut in einem Wegwerf-Ordner ein kleines Projekt mit eigenem "GitHub" (ein lokales Git-Repository)
und ersetzt docker, curl und sleep durch Attrappen. So laufen die Skripte vollständig durch, ohne Server,
ohne Docker und ohne Netz. Geprüft wird, was danach in Git steht.

Braucht bash und git. Im Test-Container auf dem Server (python:3.12-slim, ohne git) werden die Tests
übersprungen; auf GitHub (automatische Tests) laufen sie.
"""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

pytestmark = pytest.mark.skipif(not (shutil.which("git") and shutil.which("bash")), reason="git oder bash fehlt")

ATTRAPPEN = {
    # Tests im Wegwerf-Container: bestanden, ausser TESTS_ROT ist gesetzt
    "docker": """#!/usr/bin/env bash
case "$1" in
  run) if [ -n "${TESTS_ROT:-}" ]; then echo "1 failed, 9 passed"; exit 1; fi; echo "10 passed, 1 skipped in 1s";;
  compose) echo "compose $*";;
  ps) printf 'NAMES STATUS\\nfootball-dashboard Up\\n';;
  logs) echo "gestartet";;
  inspect) echo true;;
esac
""",
    # Platzhalter 200, Dashboard 200 (Anmeldemaske seit 0.15.2; mit DASHBOARD_CODE=401 wie bis 0.15.1)
    "curl": """#!/usr/bin/env bash
for a in "$@"; do last="$a"; done
case "$last" in */dashboard/) printf "${DASHBOARD_CODE:-200}";; */vorschau/) printf "${VORSCHAU_CODE:-401}";; *) printf 200;; esac
""",
    "sleep": "#!/usr/bin/env bash\nexit 0\n",
}


class Umgebung:
    """Projektordner (Server), GitHub (bare repo) und ein zweiter Klon (Arbeit von Claude auf GitHub)."""

    def __init__(self, tmp: Path):
        self.tmp = tmp
        self.github = tmp / "github.git"
        self.server = tmp / "server"
        self.arbeit = tmp / "arbeit"
        attrappen = tmp / "bin"
        attrappen.mkdir()
        for name, inhalt in ATTRAPPEN.items():
            (attrappen / name).write_text(inhalt)
            (attrappen / name).chmod(0o755)
        self.env = {
            **os.environ,
            "PATH": f"{attrappen}{os.pathsep}{os.environ['PATH']}",
            "SI_PROJEKT": str(self.server),
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.invalid",
        }
        self.git(tmp, "init", "-q", "--bare", "-b", "main", str(self.github))
        self.git(tmp, "clone", "-q", str(self.github), str(self.server))
        for ordner in ("app", "tests", "docs", "tools"):
            (self.server / ordner).mkdir()
        (self.server / "app" / "app.py").write_text("print('v1')\n")
        (self.server / "tests" / "test_x.py").write_text("")
        (self.server / "docs" / "doku.md").write_text("Doku\n")
        (self.server / "RELEASE.md").write_text("# Release 1\n\n**Commit:** Erster Stand\n")
        (self.server / ".gitignore").write_text("data/\nbackup/\n.env\n")
        (self.server / "data").mkdir()
        (self.server / "data" / "db.xlsx").write_bytes(b"EXCEL")
        for skript in ("einspielen.sh", "zurueck.sh"):
            shutil.copy(TOOLS / skript, self.server / "tools" / skript)
        self.git(self.server, "add", "-A")
        self.git(self.server, "commit", "-q", "-m", "Start")
        self.git(self.server, "push", "-q", "-u", "origin", "main")
        self.git(tmp, "clone", "-q", str(self.github), str(self.arbeit))

    def git(self, cwd: Path, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=cwd, env=getattr(self, "env", None), check=True,
                              capture_output=True, text=True).stdout.strip()

    def kopf(self, wo: Path, ref: str = "HEAD") -> str:
        return self.git(wo, "rev-parse", ref)

    def lauf(self, skript: str, *args: str, antwort: str = "j", **extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(["bash", str(self.server / "tools" / skript), *args], input=antwort + "\n",
                              cwd=self.tmp, env={**self.env, **extra}, capture_output=True, text=True, timeout=60)

    def neu_auf_github(self, datei: str, inhalt: str, *, mit_merge: bool = False) -> None:
        """Claude arbeitet auf GitHub: neuer Commit (auf Wunsch über einen Zweig mit Merge-Commit)."""
        if mit_merge:
            self.git(self.arbeit, "checkout", "-q", "-b", "claude/aenderung")
        pfad = self.arbeit / datei
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_text(inhalt)
        self.git(self.arbeit, "add", "-A")
        self.git(self.arbeit, "commit", "-q", "-m", f"Neu: {datei}")
        if mit_merge:
            self.git(self.arbeit, "checkout", "-q", "main")
            self.git(self.arbeit, "merge", "-q", "--no-ff", "-m", "Merge pull request", "claude/aenderung")
        self.git(self.arbeit, "push", "-q", "origin", "main")


@pytest.fixture
def u(tmp_path):
    return Umgebung(tmp_path)


def test_github_weg_uebernimmt_genau_den_stand_von_github(u):
    u.neu_auf_github("app/app.py", "print('v2')\n", mit_merge=True)
    r = u.lauf("einspielen.sh", "github")
    assert r.returncode == 0, r.stdout + r.stderr
    assert u.kopf(u.server) == u.kopf(u.github, "main")              # kein eigener Commit auf dem Server
    assert (u.server / "app" / "app.py").read_text() == "print('v2')\n"
    assert (u.server / "data" / "db.xlsx").read_bytes() == b"EXCEL"   # Excel unberührt
    assert "Server und GitHub sind gleich" in r.stdout


def test_github_weg_ohne_neues_aendert_nichts(u):
    vorher = u.kopf(u.server)
    r = u.lauf("einspielen.sh", "github")
    assert r.returncode == 0 and "Nichts Neues auf GitHub" in r.stdout
    assert u.kopf(u.server) == vorher and not (u.server / "backup").exists()


def test_github_weg_macht_nach_abbruch_weiter(u):
    """15.11.2026: Verbindung nach Schritt 3 weg -> beim nächsten Aufruf nicht „Nichts Neues“, sondern Tests und Neubau."""
    vorher = u.kopf(u.server)
    u.neu_auf_github("app/app.py", "print('v2')\n")
    r = u.lauf("einspielen.sh", "github", TESTS_ROT="1")               # bricht in Schritt 4 ab
    assert r.returncode == 1 and (u.server / "backup" / "EINSPIELEN_OFFEN").exists()
    r = u.lauf("einspielen.sh", "github")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "noch nicht fertig eingespielt" in r.stdout and "Nichts Neues" not in r.stdout
    assert "Tests bestanden" in r.stdout and "Container laufen" in r.stdout
    assert not (u.server / "backup" / "EINSPIELEN_OFFEN").exists()
    assert f"Stand davor: {vorher[:7]}" in r.stdout                   # Rückweg zeigt den Stand vor dem Abbruch
    r = u.lauf("einspielen.sh", "github")                               # danach wirklich nichts mehr zu tun
    assert "Nichts Neues auf GitHub" in r.stdout


def test_github_weg_stoppt_bei_eigenen_commits_auf_dem_server(u):
    u.neu_auf_github("docs/neu.md", "x\n")
    (u.server / "docs" / "lokal.md").write_text("lokal\n")
    u.git(u.server, "add", "-A")
    u.git(u.server, "commit", "-q", "-m", "nur auf dem Server")
    vorher = u.kopf(u.server)
    r = u.lauf("einspielen.sh", "github")
    assert r.returncode == 1 and "nicht auf GitHub" in r.stdout
    assert u.kopf(u.server) == vorher


def test_stoppt_bei_nicht_committeten_aenderungen(u):
    u.neu_auf_github("docs/neu.md", "x\n")
    (u.server / "docs" / "doku.md").write_text("von Hand geändert\n")
    r = u.lauf("einspielen.sh", "github")
    assert r.returncode == 1 and "nicht committete" in r.stdout
    assert not (u.server / "docs" / "neu.md").exists()


def test_rote_tests_stoppen_und_nennen_den_rueckweg(u):
    u.neu_auf_github("app/app.py", "kaputt\n")
    r = u.lauf("einspielen.sh", "github", TESTS_ROT="1")
    assert r.returncode == 1 and "Tests fehlgeschlagen" in r.stdout and "zurueck.sh" in r.stdout
    assert "compose" not in r.stdout                                    # kein Neubau mit roten Tests


def test_rueckweg_nach_github_weg_auch_mit_merge_commit(u):
    vorher = u.kopf(u.server)
    u.neu_auf_github("app/neu.py", "neu\n", mit_merge=True)
    assert u.lauf("einspielen.sh", "github").returncode == 0
    r = u.lauf("zurueck.sh")
    assert r.returncode == 0, r.stdout + r.stderr
    assert u.git(u.server, "rev-parse", "HEAD^{tree}") == u.git(u.server, "rev-parse", f"{vorher}^{{tree}}")
    assert u.kopf(u.server) == u.kopf(u.github, "main")              # Gegen-Commit ist auf GitHub
    assert not (u.server / "app" / "neu.py").exists()
    assert u.git(u.server, "rev-list", "--count", "HEAD") == "4"      # nichts verloren: Start, Änderung, Merge, Rückweg


def test_rueckweg_auf_version_mit_browser_passwort(u):
    """0.15.2: Der Rückweg auf eine Version vor der Anmeldemaske (Dashboard antwortet mit 401) gilt als gelungen."""
    u.neu_auf_github("app/neu.py", "neu\n")
    assert u.lauf("einspielen.sh", "github").returncode == 0
    r = u.lauf("zurueck.sh", DASHBOARD_CODE="401")
    assert r.returncode == 0 and "/dashboard/ = 401" in r.stdout, r.stdout + r.stderr


def test_einspielen_stoppt_ohne_anmeldemaske(u):
    """0.15.2: Antwortet das Dashboard nach dem Neubau nicht mit der Anmeldemaske (200), stoppt das Skript."""
    u.neu_auf_github("app/neu.py", "neu\n")
    r = u.lauf("einspielen.sh", "github", DASHBOARD_CODE="502")
    assert r.returncode == 1 and "statt 200 (Anmeldemaske" in r.stdout


def test_rueckweg_fragt_vorher(u):
    u.neu_auf_github("app/neu.py", "neu\n")
    assert u.lauf("einspielen.sh", "github").returncode == 0
    jetzt = u.kopf(u.server)
    r = u.lauf("zurueck.sh", antwort="n")
    assert r.returncode == 0 and "nichts geändert" in r.stdout and u.kopf(u.server) == jetzt


def _paket(u: Umgebung, name: str = "release.zip") -> None:
    with zipfile.ZipFile(u.server / name, "w") as z:
        z.writestr("app/app.py", "print('paket')\n")
        z.writestr("RELEASE.md", "# Release 2\n\n**Commit:** Paket zwei\n\n## Erwartungswerte\n\n- eins\n\n## Ende\n")


def test_paket_weg_mit_umbenanntem_paket_committet_und_pusht(u):
    _paket(u, "release_2.zip")
    r = u.lauf("einspielen.sh")
    assert r.returncode == 0, r.stdout + r.stderr
    assert u.git(u.server, "log", "-1", "--format=%s") == "Paket zwei"
    assert u.kopf(u.server) == u.kopf(u.github, "main")
    assert not list(u.server.glob("release*.zip"))


def test_paket_weg_stoppt_wenn_github_weiter_ist(u):
    u.neu_auf_github("docs/neu.md", "x\n")
    _paket(u)
    vorher = u.kopf(u.server)
    r = u.lauf("einspielen.sh")
    assert r.returncode == 1 and "einspielen.sh github" in r.stdout
    assert u.kopf(u.server) == vorher and (u.server / "release.zip").exists()   # Paket bleibt liegen


def test_paket_weg_antwort_n_und_rueckweg(u):
    vorher = u.kopf(u.server)
    _paket(u)
    r = u.lauf("einspielen.sh", antwort="n")
    assert r.returncode == 0 and "Nicht committet" in r.stdout
    assert u.lauf("zurueck.sh").returncode == 0
    assert u.kopf(u.server) == vorher
    assert (u.server / "app" / "app.py").read_text() == "print('v1')\n"
    assert u.git(u.server, "status", "--porcelain") == ""


def test_paket_darf_das_skript_selbst_ersetzen(u):
    # Ein Paket mit neuer Fassung von einspielen.sh: bash muss mit der alten Fassung sauber zu Ende laufen.
    neu = "#!/usr/bin/env bash\n" + "# neue Zeile, verschiebt alles\n" * 40 + (TOOLS / "einspielen.sh").read_text()
    _paket(u)
    with zipfile.ZipFile(u.server / "release.zip", "a") as z:
        z.writestr("tools/einspielen.sh", neu)
    r = u.lauf("einspielen.sh")
    assert r.returncode == 0, r.stdout + r.stderr
    assert u.git(u.server, "log", "-1", "--format=%s") == "Paket zwei"
    assert (u.server / "tools" / "einspielen.sh").read_text() == neu
