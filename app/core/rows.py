"""Hilfsfunktionen, um Prüfergebnisse je Spielzeile zu erzeugen."""

import pandas as pd

from .issues import Issue

MAX_ROWS_PER_CHECK = 50  # Begrenzung der Einzelmeldungen je Prüfung


def valid_id(value) -> int | None:
    """Spiel-id als ganze Zahl, aber nur wenn sie endlich und ganzzahlig ist; sonst None.
    Nie abschneiden: 123,5 wird nicht zu 123. Text, leer, inf und NaN ergeben None (seit H.2)."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if number.is_integer() else None


def id_text(value) -> str:
    """id für Meldungstexte: als ganze Zahl, wenn möglich, sonst so, wie sie in der Datei steht."""
    mid = valid_id(value)
    return str(mid) if mid is not None else str(value)


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
        mid = valid_id(row.get("id"))
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
