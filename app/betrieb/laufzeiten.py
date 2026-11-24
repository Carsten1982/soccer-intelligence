"""Laufzeiten gebuchter Dienste seit 0.23 (docs/09_Betrieb_EMail.md, Abschnitt 5).

Quelle: app/config/laufzeiten.toml (VPS, Domain, Postfach) und das Abo von API-Football aus dem letzten Bericht.
Ohne automatische Verlängerung: 30 Tage vorher Warnung, 7 Tage vorher kritisch. Mit automatischer Verlängerung:
14 Tage vorher Warnung „prüfen und nachtragen“ (die Datei kennt eine Verlängerung nicht von selbst).
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from core import settings

DATEI = settings.CONFIG_DIR / "laufzeiten.toml"


@dataclass
class Laufzeit:
    name: str
    bis: date
    automatisch: bool

    def rest(self, heute: date) -> int:
        return (self.bis - heute).days

    def stufe(self, heute: date) -> str | None:
        """None (in Ordnung), „warnung“ oder „kritisch“."""
        r = self.rest(heute)
        if self.automatisch:
            return "kritisch" if r < 0 else "warnung" if r <= 14 else None
        return "kritisch" if r <= 7 else "warnung" if r <= 30 else None

    def farbe(self, heute: date) -> str:
        return {None: "ok", "warnung": "wn", "kritisch": "bad"}[self.stufe(heute)]


def laden(datei: Path = DATEI, abo: dict | None = None) -> list[Laufzeit]:
    """Einträge der Datei, dazu das API-Abo aus dem Bericht ({"plan": …, "bis": "JJJJ-MM-TT"})."""
    out = []
    if Path(datei).exists():
        for d in tomllib.loads(Path(datei).read_text(encoding="utf-8")).get("dienst", []):
            out.append(Laufzeit(str(d["name"]), d["bis"], bool(d.get("automatisch", False))))
    if abo and abo.get("bis"):
        try:
            out.append(Laufzeit(f"API-Football ({abo.get('plan', 'Abo')})", date.fromisoformat(abo["bis"]), False))
        except ValueError:
            pass
    return sorted(out, key=lambda x: x.bis)
