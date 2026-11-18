"""Auswahl der Top Anomalien (KPI-Regelwerk, Abschnitt 2.6; seit Version 0.19 nach Prognosewert).

- Grundlage: je aktiver Liga der zeitlich nächste Block (anstehender Spieltag samt Sonderspielen an seinen Tagen bzw.
  Sonderspiele davor, höchstens 14 Tage entfernt), nur Spiele vor dem Anpfiff und mit Werten (core/anzeige.py).
- Auffällig ist eine Kennzahl KPI 02–09, wenn ihre Abweichung über der Schwelle ihrer Liga liegt (schwellen.toml);
  sie trägt den Prognosewert hoch / mittel / gering. Ausgeschlossen: vorläufige Werte, verschobene/abgesagte Spiele.
- Pro Begegnung ein Eintrag: die Kennzahl mit dem höchsten Prognosewert, dann der grössten Abweichung (gerundet),
  bei Gleichstand die kleinere KPI-Nummer.
- Rangfolge: hoch vor mittel vor gering; innerhalb einer Stufe grösste Abweichung; dann früheres „Datum von“,
  Reihenfolge der Ligen in der Konfiguration und im Spielplan.
- Liga-Mix: höchstens zwei Einträge je Liga; nur wenn danach weniger als vier gewählt sind, wird mit den
  übersprungenen Begegnungen in derselben Rangfolge aufgefüllt. Höchstens vier Einträge; gibt es weniger
  Auffälligkeiten, werden weniger angezeigt.

Die Auswahl ist reine Logik ohne Oberfläche und gilt auch für die Website (Startseite).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .fixtures import INACTIVE_STATUS
from .kpis import LEVELS, LOW, RANK, KpiResult, MatchKpis

# KPIs, die in die Auswahl einfliessen (Schlüssel = Attribut in MatchKpis), in der Reihenfolge der KPI-Nummer.
TOP_KPIS = {
    "kpi02": "KPI 02 – Erwartete Tore", "kpi03": "KPI 03 – Over 2.5 Goals", "kpi04": "KPI 04 – Gelbe Karten",
    "kpi05": "KPI 05 – Ecken", "kpi06": "KPI 06 – Tore 1. Halbzeit", "kpi07": "KPI 07 – Tore 2. Halbzeit",
    "kpi08": "KPI 08 – Beide Teams treffen", "kpi09": "KPI 09 – Schüsse aufs Tor",
}
MAX_ENTRIES = 4
MAX_PER_LEAGUE = 2           # Liga-Mix (Entscheidung Carsten 18.11.2026)
NO_ANOMALIES_TEXT = "Für die anstehenden Spiele liegen keine Auffälligkeiten vor."
LOW_HINT = "Ergänzt mit Spielen geringer Verlässlichkeit."


@dataclass(frozen=True)
class Candidate:
    """Eine Begegnung des aktuellen Spieltags mit ihren KPI-Ergebnissen."""
    league: str
    league_order: int        # Reihenfolge der Liga in der Konfiguration
    season: str
    matchday: int
    datum_von: date
    file_order: int          # Reihenfolge der Begegnung im Spielplan-Blatt
    home: str
    away: str
    status: str
    kpis: MatchKpis | None   # None bei verschobenen/abgesagten Spielen
    when: str = ""           # Datum und Anstoss für die Karte („Sa 21.11. · 18:30“, seit 0.16)


@dataclass(frozen=True)
class TopEntry:
    rank: int
    candidate: Candidate
    kpi_key: str
    kpi_name: str
    result: KpiResult


def _eligible(result: KpiResult) -> bool:
    return result.anomalie in LEVELS and not result.vorlaeufig and result.abweichung_rund is not None


def _sort_key(c: Candidate, result: KpiResult, kpi_order: int) -> tuple:
    return (
        -RANK[result.anomalie],                     # 1. hoch vor mittel vor gering
        -abs(result.abweichung_rund),               # 2. grösster Betrag zuerst
        c.datum_von,                                # 3. früheres Spieldatum
        c.league_order, c.file_order,               # 4. Reihenfolge im Spielplan
        kpi_order,                                  # bei Gleichstand in einer Begegnung: kleinere KPI-Nummer
    )


def select_top(candidates: list[Candidate], max_entries: int = MAX_ENTRIES,
               max_per_league: int = MAX_PER_LEAGUE) -> list[TopEntry]:
    best_per_match: list[tuple[tuple, Candidate, str]] = []
    for c in candidates:
        if c.kpis is None or c.status in INACTIVE_STATUS:
            continue
        options = []
        for order, key in enumerate(TOP_KPIS):
            result = getattr(c.kpis, key)
            if _eligible(result):
                options.append((_sort_key(c, result, order), c, key))
        if options:
            best_per_match.append(min(options, key=lambda o: o[0]))   # höchstens ein Eintrag je Begegnung
    best_per_match.sort(key=lambda o: o[0])
    chosen, skipped, per_league = [], [], {}
    for item in best_per_match:                                        # Liga-Mix: höchstens zwei je Liga …
        league = item[1].league
        if len(chosen) < max_entries and per_league.get(league, 0) < max_per_league:
            chosen.append(item)
            per_league[league] = per_league.get(league, 0) + 1
        else:
            skipped.append(item)
    for item in skipped:                                               # … sonst mit derselben Liga auffüllen
        if len(chosen) >= max_entries:
            break
        chosen.append(item)
    chosen.sort(key=lambda o: o[0])
    return [
        TopEntry(rank=i, candidate=c, kpi_key=key, kpi_name=TOP_KPIS[key], result=getattr(c.kpis, key))
        for i, (_, c, key) in enumerate(chosen, start=1)
    ]


def has_low(entries: list[TopEntry]) -> bool:
    """Enthält die Auswahl Einträge mit Prognosewert „gering“ (Hinweis über der Liste)?"""
    return any(e.result.anomalie == LOW for e in entries)
