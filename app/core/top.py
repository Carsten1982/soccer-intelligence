"""Auswahl der Top-Anomalien (KPI-Regelwerk, Abschnitt 2.6; Dashboard-Briefing, Kapitel 5.1).

- Grundlage: Begegnungen des aktuellen Spieltags aller aktiven Ligen.
- Vorerst nur KPI 02 und KPI 04 mit leichter oder starker Anomalie (KPI 03 erst nach Freigabe).
- Ausgeschlossen: vorläufige Werte, Begegnungen mit Status „verschoben“ oder „abgesagt“.
- Rangfolge: stark vor leicht · grösserer Betrag der gerundeten Abweichung · früheres „Datum von“ ·
  Reihenfolge im Spielplan (Ligen in der Reihenfolge der Konfiguration, darin Reihenfolge der Datei).
- Pro Begegnung höchstens ein Eintrag (der KPI mit dem höheren Rang), insgesamt höchstens vier, kein Auffüllen.

Die Auswahl ist reine Logik ohne Oberfläche und gilt auch für die spätere öffentliche Website.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .fixtures import INACTIVE_STATUS
from .kpis import LIGHT, STRONG, KpiResult, MatchKpis

# KPIs, die in die Auswahl einfliessen (Schlüssel = Attribut in MatchKpis). KPI 03 erst nach Freigabe.
TOP_KPIS = {"kpi02": "KPI 02 – Erwartete Tore", "kpi04": "KPI 04 – Gelbe Karten"}
MAX_ENTRIES = 4
NO_ANOMALIES_TEXT = "Für den aktuellen Spieltag liegen keine Anomalien vor."


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


@dataclass(frozen=True)
class TopEntry:
    rank: int
    candidate: Candidate
    kpi_key: str
    kpi_name: str
    result: KpiResult


def _eligible(result: KpiResult) -> bool:
    return result.anomalie in (LIGHT, STRONG) and not result.vorlaeufig and result.abweichung_rund is not None


def _sort_key(c: Candidate, result: KpiResult, kpi_order: int) -> tuple:
    return (
        0 if result.anomalie == STRONG else 1,     # 1. stark vor leicht
        -abs(result.abweichung_rund),               # 2. grösster Betrag zuerst
        c.datum_von,                                # 3. früheres Spieldatum
        c.league_order, c.file_order,               # 4. Reihenfolge im Spielplan
        kpi_order,                                  # stabile Reihenfolge bei völligem Gleichstand
    )


def select_top(candidates: list[Candidate], max_entries: int = MAX_ENTRIES) -> list[TopEntry]:
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
            best_per_match.append(min(options, key=lambda o: o[0]))   # 5. höchstens ein Eintrag je Begegnung
    best_per_match.sort(key=lambda o: o[0])
    return [
        TopEntry(rank=i, candidate=c, kpi_key=key, kpi_name=TOP_KPIS[key], result=getattr(c.kpis, key))
        for i, (_, c, key) in enumerate(best_per_match[:max_entries], start=1)   # 6. höchstens vier
    ]
