"""Abfragen bei API-Football (Spezifikation, Abschnitte 3, 11 und 12).

- Jede Antwort wird zuerst unverändert als .json.gz gespeichert, erst danach verarbeitet.
- Protokoll je Abfrage (CSV): Zeit, Endpunkt, Parameter, HTTP-Status, verbleibendes Kontingent – nie der Schlüssel.
- Eigene Obergrenze je Tag; höchstens 3 Versuche je Abfrage, danach Abbruch mit klarer Meldung (keine Endlosschleife).
"""

from __future__ import annotations

import csv
import gzip
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import requests

from . import einstellungen as E


class ImportFehler(Exception):
    """Lauf kann nicht weitergehen (Schlüssel fehlt, Obergrenze erreicht, API nicht erreichbar …)."""


@dataclass
class ApiClient:
    key: str | None
    raw_dir: Path
    limit: int = E.DAILY_LIMIT
    used_before: int = 0                      # heute schon verbrauchte Abfragen (aus dem Protokoll)
    pause: float = 0.3                        # Sekunden zwischen Abfragen (Minutenlimit)
    session: object = field(default_factory=requests.Session)
    sleep: object = time.sleep
    used: int = 0
    remaining: int | None = None              # Restkontingent laut API (Kopfzeile)

    def get(self, endpoint: str, params: dict) -> dict:
        if not self.key:
            raise ImportFehler(f"API-Schlüssel fehlt (Umgebungsvariable {E.KEY_ENV} in .env)")
        last = "unbekannt"
        for attempt in range(3):
            if self.used_before + self.used >= self.limit:
                raise ImportFehler(f"Eigene Obergrenze von {self.limit} Abfragen pro Tag erreicht – Lauf gestoppt")
            self.used += 1
            status, data = None, None
            try:
                r = self.session.get(E.BASE_URL + endpoint, params=params, headers={"x-apisports-key": self.key},
                                     timeout=60)
                status = r.status_code
                rem = r.headers.get("x-ratelimit-requests-remaining")
                self.remaining = int(rem) if rem and rem.isdigit() else self.remaining
                data = r.json() if r.ok else None
            except (requests.RequestException, ValueError) as exc:
                last = f"Netzfehler ({type(exc).__name__})"
            self._log(endpoint, params, status)
            if data is not None:
                errors = data.get("errors")
                if errors:                    # [] oder {} = keine Fehler
                    text = json.dumps(errors, ensure_ascii=False)
                    if "rateLimit" not in text:
                        raise ImportFehler(f"API meldet: {text}")
                    last = "Minutenlimit"
                else:
                    self._store(endpoint, params, data)
                    self.sleep(self.pause)
                    return data
            elif status is not None:
                last = f"HTTP {status}"
            self.sleep(5 * (attempt + 1))
        raise ImportFehler(f"API nicht erreichbar ({last}) – 3 Versuche: {endpoint}")

    def _store(self, endpoint: str, params: dict, data: dict) -> None:
        now = datetime.now()
        target = self.raw_dir / now.strftime("%Y-%m-%d")
        target.mkdir(parents=True, exist_ok=True)
        name = f"{now:%H%M%S}_{self.used_before + self.used:04d}_{endpoint.replace('/', '-')}.json.gz"
        payload = {"zeit": now.isoformat(timespec="seconds"), "endpunkt": endpoint, "parameter": params, "antwort": data}
        (target / name).write_bytes(gzip.compress(json.dumps(payload, ensure_ascii=False).encode()))

    def _log(self, endpoint: str, params: dict, status) -> None:
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        with open(self.raw_dir / "abfragen.csv", "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([datetime.now().isoformat(timespec="seconds"), endpoint,
                                    json.dumps(params, ensure_ascii=False), status if status is not None else "-",
                                    self.remaining if self.remaining is not None else "-"])


def used_today(raw_dir: Path, today: str) -> int:
    """Heute schon verbrauchte Abfragen laut Protokoll (für die eigene Obergrenze über mehrere Läufe)."""
    log = raw_dir / "abfragen.csv"
    if not log.exists():
        return 0
    with open(log, encoding="utf-8") as f:
        return sum(1 for row in csv.reader(f) if row and row[0].startswith(today))
