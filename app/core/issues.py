"""Einheitliches Format für Prüfergebnisse."""

from dataclasses import dataclass

FEHLER = "Fehler"      # Daten nicht verwendbar -> App zeigt keine Auswertungen
WARNUNG = "Warnung"    # Daten verwendbar, aber wahrscheinlich ein Datenfehler
HINWEIS = "Hinweis"    # Auffälligkeit ohne Handlungsbedarf (z. B. Eigentore, leere Statistik)

LEVEL_ORDER = {FEHLER: 0, WARNUNG: 1, HINWEIS: 2}


@dataclass(frozen=True)
class Issue:
    level: str
    sheet: str
    check: str
    message: str
    match_id: int | None = None
    match: str | None = None
    excel_row: int | None = None

    def as_dict(self) -> dict:
        return {
            "Stufe": self.level,
            "Blatt": self.sheet,
            "Prüfung": self.check,
            "Details": self.message,
            "id": self.match_id,
            "Begegnung": self.match,
            "Excel-Zeile": self.excel_row,
        }
