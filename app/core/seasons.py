"""Referenzsaison und ausgewertete Saisons (Version 0.11, Briefing „Neue Datenbank“, KPI-Regelwerk Abschnitt 1.2).

Regel (Entscheidung Carsten 10.11.2026):
- Die älteste Saison eines Ligablatts ist die Referenzsaison. Sie liefert nur Daten für die folgende Saison
  (Teamwerte der Vorsaison, Ligareferenz über das Saisonende hinweg) und wird selbst nicht ausgewertet.
- Alle anderen Saisons werden ausgewertet, auch die laufende (als „vorläufig“ gekennzeichnet).
- Beim Saisonwechsel entfernt Carsten die älteste Saison aus der Excel-Datei; die nächste wird automatisch
  Referenzsaison. Darum steht hier keine feste Jahreszahl.

Alle Funktionen nehmen beliebige Saisonbezeichnungen „JJJJ/JJJJ“ entgegen (z. B. die Spalte `season` der aufbereiteten
Liga oder `Season` des Ligablatts); leere Werte werden ignoriert.
"""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from .fixtures import previous_season


def season_list(seasons: Iterable) -> list[str]:
    """Alle vorhandenen Saisons, ohne Doppelte, aufsteigend sortiert."""
    return sorted({str(s) for s in seasons if not pd.isna(s)})


def reference_season(seasons: Iterable) -> str | None:
    """Die älteste Saison (Referenzsaison) oder None, wenn keine Saison vorhanden ist."""
    present = season_list(seasons)
    return present[0] if present else None


def analysed_seasons(seasons: Iterable) -> list[str]:
    """Alle Saisons ausser der Referenzsaison, aufsteigend. Bei nur einer Saison: leer (nichts auswertbar)."""
    return season_list(seasons)[1:]


def season_gaps(seasons: Iterable) -> list[tuple[str, str]]:
    """Lücken zwischen Saisons: (fehlende Saison, Saison danach, die ohne Vorsaison berechnet wird).

    Beispiel: 2020/21, 2022/23 -> [("2021/2022", "2022/2023")]. Fehlt mehr als eine Saison, wird jede fehlende
    einzeln gemeldet; die Saison danach ist dann jeweils die nächste vorhandene."""
    present = season_list(seasons)
    gaps = []
    for earlier, later in zip(present, present[1:]):
        missing = []
        season = later
        while previous_season(season) != earlier:
            season = previous_season(season)
            missing.append(season)
            if len(missing) > 50:          # Schutz gegen unsinnige Bezeichnungen
                break
        gaps += [(m, later) for m in reversed(missing)]
    return gaps
