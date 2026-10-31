"""Hilfsfunktionen, um Prüfergebnisse je Spielzeile zu erzeugen."""

import pandas as pd

from .issues import Issue

MAX_ROWS_PER_CHECK = 50  # Begrenzung der Einzelmeldungen je Prüfung


def match_label(row) -> str:
    try:
        d = pd.Timestamp(row["Date"]).strftime("%d.%m.%Y")
    except Exception:  # noqa: BLE001 - Datum kann bei Fehlern ungültig sein
        d = "?"
    return f"{row.get('homeTeam', '?')} – {row.get('awayTeam', '?')} ({d})"


def row_issues(level, sheet, check, frame, message, original_index=True) -> list[Issue]:
    """Erzeugt je betroffener Zeile eine Meldung (max. MAX_ROWS_PER_CHECK)."""
    out: list[Issue] = []
    for idx, row in frame.head(MAX_ROWS_PER_CHECK).iterrows():
        try:
            mid = int(float(row.get("id")))
        except (TypeError, ValueError):
            mid = None
        out.append(
            Issue(
                level=level,
                sheet=sheet,
                check=check,
                message=message(row) if callable(message) else message,
                match_id=mid,
                match=match_label(row),
                excel_row=int(idx) + 2 if original_index else None,
            )
        )
    if len(frame) > MAX_ROWS_PER_CHECK:
        out.append(Issue(level, sheet, check, f"… und {len(frame) - MAX_ROWS_PER_CHECK} weitere Zeilen"))
    return out
