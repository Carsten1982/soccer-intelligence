"""Laufplan seit 0.22: ein Lauf nach jedem Spiel, Wiederholung und gestaffelte Backups (Spezifikation `06`, 10.2).

- Je Anstosszeit ein Lauf bei Anpfiff + 2¼ Stunden (B1). Die Zeiten kommen aus dem gültigen Spielplan und werden bei
  jeder Prüfung neu berechnet; Verschiebungen wirken so von selbst. Läufe, die weniger als 30 Minuten auseinander-
  liegen, werden zum späteren zusammengelegt. Spiele ohne bestätigte Anstosszeit lösen keinen Lauf aus; ein Lauf in
  der Stunde des Kontrolllaufs (04:00) entfällt.
- Scheitert ein Lauf oder fehlen danach noch Werte eines frischen Spiels, folgt 1 Stunde später eine Wiederholung,
  höchstens zwei (B4).
- Backups: täglich 14 Tage, je Woche das letzte 8 Wochen, je Monat das letzte 12 Monate, je Saison das letzte vor dem
  1. Juli dauerhaft (B5, Regel 7).
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from pathlib import Path

import openpyxl

from . import einstellungen as E

NACH_ANPFIFF = timedelta(hours=2, minutes=15)
ZUSAMMENLEGEN = timedelta(minutes=30)
WIEDERHOLUNG_NACH = timedelta(hours=1)
WIEDERHOLUNGEN = 2
VERFALL = timedelta(hours=6)          # verpasste Läufe (z. B. Neustart) nur bis 6 Stunden nachholen, danach Kontrolllauf


def anstosszeiten(fx_path: Path, tage: set[date]) -> list[datetime]:
    """Anstosszeiten geplanter Spiele an diesen Tagen (ohne Status, mit bestätigter oder vorläufiger Uhrzeit)."""
    if not fx_path.exists():
        return []
    wb = openpyxl.load_workbook(fx_path, read_only=True)
    out = set()
    try:
        for ws in wb.worksheets:
            rows = ws.iter_rows(values_only=True)
            head = next(rows, None)
            if not head:
                continue
            col = {h: i for i, h in enumerate(head)}
            if not {"Datum von", "Status", "Anstoss", "Termin"} <= col.keys():
                continue
            for r in rows:
                tag, anstoss = r[col["Datum von"]], r[col["Anstoss"]]
                tag = tag.date() if isinstance(tag, datetime) else tag
                if tag not in tage or r[col["Status"]] or r[col["Termin"]] == "Zeit offen" or not anstoss:
                    continue
                try:
                    hh, mm = (int(x) for x in str(anstoss).split(":")[:2])
                except ValueError:
                    continue
                out.add(datetime.combine(tag, time(hh, mm)))
    finally:
        wb.close()
    return sorted(out)


def laufzeiten(anstoesse: list[datetime]) -> list[datetime]:
    """Anpfiff + 2¼ h, zusammengelegt (Abstand unter 30 Minuten → der spätere), ohne Läufe in der Stunde 04:00."""
    zeiten = sorted({a + NACH_ANPFIFF for a in anstoesse})
    out: list[datetime] = []
    for z in zeiten:
        if out and z - out[-1] < ZUSAMMENLEGEN:
            out[-1] = z
        else:
            out.append(z)
    return [z for z in out if z.hour != E.RUN_HOUR]


def plan(fx_path: Path, tag: date) -> list[datetime]:
    """Läufe, die an diesem Tag stattfinden (auch nach Spielen vom Vorabend, die nach Mitternacht enden)."""
    zeiten = laufzeiten(anstosszeiten(fx_path, {tag - timedelta(days=1), tag}))
    return [z for z in zeiten if z.date() == tag]


def faellig(state: dict, now: datetime, fx_path: Path) -> datetime | None:
    """Fälliger Lauf nach einem Spiel (der späteste verpasste, höchstens 6 Stunden alt), sonst None."""
    jetzt = now.replace(tzinfo=None, microsecond=0)
    erledigt = set(state.get("spiel_laeufe") or [])
    offen = [z for z in plan(fx_path, jetzt.date()) + plan(fx_path, jetzt.date() - timedelta(days=1))
             if z <= jetzt and jetzt - z <= VERFALL and z.isoformat(timespec="minutes") not in erledigt]
    return max(offen) if offen else None


def erledigt(state: dict, bis: datetime, fx_path: Path) -> None:
    """Alle Läufe bis zu diesem Zeitpunkt als erledigt vermerken (nur die letzten 2 Tage bleiben im Zustand)."""
    bis = bis.replace(tzinfo=None, microsecond=0)
    zeiten = [z for z in plan(fx_path, bis.date()) + plan(fx_path, bis.date() - timedelta(days=1)) if z <= bis]
    alt = [s for s in state.get("spiel_laeufe") or [] if s[:10] >= (bis.date() - timedelta(days=2)).isoformat()]
    state["spiel_laeufe"] = sorted(set(alt) | {z.isoformat(timespec="minutes") for z in zeiten})


def wiederholung_noetig(report: dict, now: datetime) -> bool:
    """Lauf gescheitert oder ein Spiel der letzten 2 Tage noch ohne vollständige Statistik."""
    if report.get("status") == "fehlgeschlagen":
        return True
    grenze = now.date() - timedelta(days=1)
    for o in report.get("offen") or []:
        try:
            tag = datetime.strptime(o["datum"], "%d.%m.%Y").date()
        except (KeyError, ValueError):
            continue
        if tag >= grenze:
            return True
    return False


def wiederholung_planen(state: dict, report: dict, now: datetime, anlass: str) -> None:
    """Nach einem Lauf nach dem Spiel: Wiederholung in 1 Stunde (höchstens zwei), sonst keine."""
    bisher = state.get("wiederholung") or {}
    nr = (bisher.get("nr", 0) if anlass == "wiederholung" else 0) + 1
    if wiederholung_noetig(report, now) and nr <= WIEDERHOLUNGEN:
        state["wiederholung"] = {"um": (now.replace(microsecond=0) + WIEDERHOLUNG_NACH).isoformat(), "nr": nr}
    else:
        state["wiederholung"] = None


def wiederholung_faellig(state: dict, now: datetime) -> bool:
    w = state.get("wiederholung")
    return bool(w) and now >= datetime.fromisoformat(w["um"])


# --- Backups (Regel 7) --------------------------------------------------------------------------------------------

def _stempel(path: Path, stem: str) -> datetime | None:
    """Zeit aus dem Namen <stem>_JJJJ-MM-TT_HHMMSS_…_vor_import.<endung>."""
    teil = path.name[len(stem) + 1:len(stem) + 18]
    try:
        return datetime.strptime(teil, "%Y-%m-%d_%H%M%S")
    except ValueError:
        return None


def behalten(stempel: list[datetime], heute: date) -> set[datetime]:
    """Welche Backups bleiben: alle der letzten 14 Tage; je Woche (Mo–So) das letzte, 8 Wochen; je Monat das letzte,
    12 Monate; je Saison (bis 30. Juni) das letzte, dauerhaft."""
    keep = {s for s in stempel if (heute - s.date()).days < 14}
    woche, monat, saison = {}, {}, {}
    for s in sorted(stempel):
        woche[s.isocalendar()[:2]] = s
        monat[(s.year, s.month)] = s
        saison[s.year if s.month < 7 else s.year + 1] = s
    keep |= {s for s in woche.values() if (heute - s.date()).days < 8 * 7}
    keep |= {s for s in monat.values() if (heute.year - s.year) * 12 + heute.month - s.month < 12}
    laufend = heute.year if heute.month < 7 else heute.year + 1
    keep |= {s for jahr, s in saison.items() if jahr < laufend}          # abgeschlossene Saisons dauerhaft
    return keep


def backups_aufraeumen(backup_dir: Path, stems: list[tuple[str, str]], heute: date) -> int:
    """Gestaffelt aufräumen; gibt die Zahl gelöschter Dateien zurück. Unbekannte Dateinamen bleiben unberührt."""
    weg = 0
    for stem, suffix in stems:
        dateien = {p: _stempel(p, stem) for p in backup_dir.glob(f"{stem}_*_vor_import{suffix}")}
        dateien = {p: s for p, s in dateien.items() if s is not None}
        keep = behalten(list(dateien.values()), heute)
        for p, s in dateien.items():
            if s not in keep:
                p.unlink()
                weg += 1
    return weg
