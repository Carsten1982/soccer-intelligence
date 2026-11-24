"""Plausibilitätsprüfungen für strukturell korrekte Ligablätter.

Alle Prüfungen ignorieren leere Werte: Eine leere Zelle bedeutet "keine Daten"
und ist kein Fehler. Es wird nie mit 0 aufgefüllt.
"""

from __future__ import annotations

import pandas as pd

from . import schema
from .issues import HINWEIS, WARNUNG, Issue
from .matchday import season_short
from .rows import row_issues
from .seasons import season_gaps


def _result_letter(home: pd.Series, away: pd.Series) -> pd.Series:
    out = pd.Series(pd.NA, index=home.index, dtype="string")
    out[home > away] = "H"
    out[home < away] = "A"
    out[home == away] = "D"
    return out


def _all_present(df: pd.DataFrame, cols) -> pd.Series:
    return df[list(cols)].notna().all(axis=1)


def check_goal_consistency(sheet: str, df: pd.DataFrame) -> list[Issue]:
    issues: list[Issue] = []

    # 1) "FT ..." muss identisch mit "Full-Time ..." sein
    ft, full = schema.FT_SHORT, schema.FULL_TIME
    diff = df[(df[ft[0]] != df[full[0]]) | (df[ft[1]] != df[full[1]]) | (df[ft[2]] != df[full[2]])]
    issues += row_issues(
        WARNUNG, sheet, "FT ≠ Full-Time", diff,
        lambda r: f"FT {r[ft[0]]}:{r[ft[1]]} {r[ft[2]]} vs. Full-Time {r[full[0]]}:{r[full[1]]} {r[full[2]]}",
    )

    # 2) 1. HZ + 2. HZ = Endstand
    h1, h2 = schema.FIRST_HALF, schema.SECOND_HALF
    bad = df[(df[h1[0]] + df[h2[0]] != df[full[0]]) | (df[h1[1]] + df[h2[1]] != df[full[1]])]
    issues += row_issues(
        WARNUNG, sheet, "Halbzeiten ≠ Endstand", bad,
        lambda r: f"HZ1 {r[h1[0]]}:{r[h1[1]]} + HZ2 {r[h2[0]]}:{r[h2[1]]} ≠ Endstand {r[full[0]]}:{r[full[1]]}",
    )

    # 3) Ergebnisbuchstabe passt zu den Toren
    for home, away, res in (ft, full, h1, h2):
        expected = _result_letter(df[home], df[away])
        bad = df[expected != df[res]]
        issues += row_issues(
            WARNUNG, sheet, "Ergebnisbuchstabe", bad,
            lambda r, h=home, a=away, x=res: f"{x} = {r[x]}, aber Tore {r[h]}:{r[a]}",
        )
    return issues


def check_stat_consistency(sheet: str, df: pd.DataFrame) -> list[Issue]:
    issues: list[Issue] = []

    # 1. HZ + 2. HZ = Gesamt (nur wenn alle drei Werte vorhanden)
    for label, home_prefix, away_prefix in schema.SUMMABLE_STATS:
        for prefix in (home_prefix, away_prefix):
            full, first, second = (f"{prefix} {p}" for p in schema.PERIODS)
            present = _all_present(df, (full, first, second))
            bad = df[present & (df[first] + df[second] != df[full])]
            issues += row_issues(
                WARNUNG, sheet, f"{label}: Halbzeiten ≠ Gesamt", bad,
                lambda r, f=full, a=first, b=second: f"{a} {r[a]:g} + {b} {r[b]:g} ≠ {f} {r[f]:g}",
            )

    # Ballbesitz Heim + Auswärts = 100 %
    for period, home, away in schema.POSSESSION:
        present = _all_present(df, (home, away))
        bad = df[present & ((df[home] + df[away]) != 100)]
        issues += row_issues(
            WARNUNG, sheet, "Ballbesitz ≠ 100 %", bad,
            lambda r, h=home, a=away, p=period: f"{p}: {r[h]:g} % + {r[a]:g} % = {r[h] + r[a]:g} %",
        )

    # Schüsse gesamt >= aufs Tor + daneben (geblockte Schüsse können die Differenz erklären). Seit 0.19.1 nur Hinweis
    # (Entscheidung Carsten 18.11.2026): kommt in der Quelle vor (z. B. id 11344), geht in keinen KPI ein.
    for side, total in (("Home", "Home Team Shots"), ("Away", "Away Team Shots")):
        for p in schema.PERIODS:
            t, on, off = f"{total} {p}", f"{side} Shots on Target {p}", f"{side} Shots off Target {p}"
            present = _all_present(df, (t, on, off))
            bad = df[present & (df[t] < df[on] + df[off])]
            issues += row_issues(
                HINWEIS, sheet, "Schüsse < aufs Tor + daneben", bad,
                lambda r, t=t, on=on, off=off: f"{t} {r[t]:g} < {r[on]:g} + {r[off]:g}",
            )

    # Mehr Tore als Schüsse aufs Tor: meist Eigentore -> nur Hinweis
    full = schema.FULL_TIME
    for goals, sot in ((full[0], "Home Shots on Target Full Time"), (full[1], "Away Shots on Target Full Time")):
        bad = df[df[sot].notna() & (df[goals] > df[sot])]
        issues += row_issues(
            HINWEIS, sheet, "Mehr Tore als Schüsse aufs Tor", bad,
            lambda r, g=goals, s=sot: f"{g} {r[g]} > {s} {r[s]:g} (meist Eigentore)",
        )
    return issues


def check_missing_stats(sheet: str, df: pd.DataFrame, noted_ids: set[tuple[str, int]]) -> list[Issue]:
    """Leere Statistikwerte: nicht dokumentiert -> Warnung, im Blatt Datenhinweise dokumentiert -> Hinweis.
    Je Stufe höchstens MAX_ROWS_PER_CHECK Einzelmeldungen, danach eine Sammelzeile (seit H.1)."""
    stats = list(schema.STAT_COLUMNS)
    missing_count = df[stats].isna().sum(axis=1)
    affected = df[missing_count > 0]
    documented = affected["id"].map(lambda i: (sheet, int(i)) in noted_ids).astype(bool)

    def msg(doc: str):
        def text(r):
            return (f"{int(missing_count[r.name])} von {len(stats)} Statistikwerten leer "
                    f"(= keine Daten, wird nicht als 0 gerechnet); {doc}")
        return text

    return (row_issues(WARNUNG, sheet, "Statistik fehlt", affected[~documented], msg("nicht dokumentiert"))
            + row_issues(HINWEIS, sheet, "Statistik fehlt", affected[documented],
                         msg("dokumentiert im Blatt Datenhinweise")))


def check_referee(sheet: str, df: pd.DataFrame) -> list[Issue]:
    bad = df[df["referee"].isna() | (df["referee"] == "")]
    return row_issues(HINWEIS, sheet, "Schiedsrichter fehlt", bad, "Spalte 'referee' ist leer")


def check_seasons(sheet: str, df: pd.DataFrame) -> list[Issue]:
    """Vollständigkeit je Saison: n Teams -> n*(n-1) Spiele, jede Paarung genau einmal."""
    issues: list[Issue] = []
    latest = df["Season"].max()
    for season, s in df.groupby("Season"):
        teams = pd.unique(pd.concat([s["homeTeam"], s["awayTeam"]]))
        n = len(teams)
        expected = n * (n - 1)
        if len(s) != expected:
            level = HINWEIS if (season == latest and len(s) < expected) else WARNUNG
            note = " (neueste Saison – evtl. noch laufend)" if level == HINWEIS else ""
            issues.append(Issue(level, sheet, "Saison unvollständig",
                                f"Saison {season}: {len(s)} von {expected} Spielen ({n} Teams){note}"))
        dup = s[s.duplicated(["homeTeam", "awayTeam"], keep=False)]
        issues += row_issues(WARNUNG, sheet, "Paarung doppelt", dup,
                             f"Paarung kommt in Saison {season} mehrfach vor")
        same = s[s["homeTeam"] == s["awayTeam"]]
        issues += row_issues(WARNUNG, sheet, "Heim = Auswärts", same, "Heim- und Auswärtsteam identisch")
    return issues


def check_season_gaps(sheet: str, df: pd.DataFrame) -> list[Issue]:
    """Fehlt zwischen zwei vorhandenen Saisons eine Saison, fehlen der Saison danach die Vorsaisonwerte
    (Teamwerte zu Saisonbeginn, Ligareferenz über das Saisonende). Sie wird trotzdem ausgewertet -> Warnung (0.11)."""
    return [Issue(WARNUNG, sheet, "Saison fehlt",
                  f"Saison {season_short(missing)} fehlt; {season_short(later)} wird ohne Vorsaison berechnet")
            for missing, later in season_gaps(df["Season"])]


def check_gamedays(sheet: str, df: pd.DataFrame) -> list[Issue]:
    """Spalte Gameday: Bereich 1 bis 2*(n-1), n/2 Spiele je Spieltag, jedes Team einmal je Spieltag.

    Gameday ist die Grundlage der Ligareferenz (KPI-Regelwerk, Abschnitt 1.1).
    """
    issues: list[Issue] = []
    for season, s in df.groupby("Season"):
        teams = pd.unique(pd.concat([s["homeTeam"], s["awayTeam"]]))
        n = len(teams)
        max_gd = 2 * (n - 1)
        gd = s["Gameday"]
        out = s[gd.notna() & ((gd < 1) | (gd > max_gd))]
        issues += row_issues(WARNUNG, sheet, "Gameday ausserhalb Bereich", out,
                             f"Gameday ausserhalb 1–{max_gd} (Saison {season}, {n} Teams)")
        counts = gd.value_counts()
        latest = season == df["Season"].max()
        for g, c in sorted(counts.items()):
            if c != n // 2:
                # Seit 0.23 (Carsten 24.11.2026): In der laufenden Saison nur ein Hinweis – der Spieltag läuft noch oder
                # ein Spiel ist verschoben. Ob nach dem Spieltag ein Ergebnis fehlt, prüft der Spielplan („Ergebnis
                # fehlt“, core/fixtures.py), weil nur er die Termine kennt.
                issues.append(Issue(HINWEIS if latest else WARNUNG, sheet, "Spieltag unvollständig",
                                    f"Saison {season}, Spieltag {int(g)}: {c} statt {n // 2} Spiele"
                                    + (" (läuft noch oder Spiel verschoben)" if latest else "")))
        long = pd.concat([s[["Gameday", "homeTeam"]].rename(columns={"homeTeam": "team"}),
                          s[["Gameday", "awayTeam"]].rename(columns={"awayTeam": "team"})])
        dup = long[long.duplicated(["Gameday", "team"])]
        for gameday, team in dup.drop_duplicates().itertuples(index=False):      # B4: Prüfung mit duplicated()
            issues.append(Issue(WARNUNG, sheet, "Team mehrfach im Spieltag",
                                f"Saison {season}, Spieltag {int(gameday)}: {team} mehrfach"))
    return issues


def run_plausibility_checks(sheet: str, df: pd.DataFrame, noted_ids: set[tuple[str, int]]) -> list[Issue]:
    return (
        check_goal_consistency(sheet, df)
        + check_stat_consistency(sheet, df)
        + check_missing_stats(sheet, df, noted_ids)
        + check_referee(sheet, df)
        + check_seasons(sheet, df)
        + check_season_gaps(sheet, df)
        + check_gamedays(sheet, df)
    )
