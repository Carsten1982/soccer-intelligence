"""Zahlen der Methodik-Seite und Excel-Download (seit 0.21; Entwurf „Methodik_10“, Template-Briefing T6).

Alles, was sich mit den Schwellen ändert, kommt aus app/config/schwellen.toml (eine Stelle, keine Handarbeit):
- Ebene 1: Zahl der Saisons, Zahl der bewährten Kombinationen (von 8 Kennzahlen × 4 Ligen × 2 Richtungen) und ihre
  Aufteilung auf stark / mittel / gering.
- Ebene 3: Tabellen je Liga (Kennzahl, Richtung, Schwelle, Signalqualität) und die Übersicht der Ligen.
- Excel-Datei: alle Zahlen je Liga, Kennzahl und Richtung (Spiele, Trefferquote, Vergleichswert, Mehrwert, Spanne,
  Saisons mit Vorteil), dazu ein Blatt mit der Grundlage. Erzeugt beim Aufruf, nie von Hand hochgeladen
  (Beschluss 19.11.2026).

Das Rechenbeispiel (Ebene 2) ist fester Text aus dem Entwurf; ein Test prüft, dass seine Zahlen zur Schwellendatei
passen (tests/test_website_021.py).
"""

from __future__ import annotations

import io
import re
from datetime import datetime
from decimal import Decimal

from core import settings
from core.kpis import HIGH, KPI_KEYS, LEVELS, LOW, MEDIUM
from core.thresholds import ThresholdConfig, load_thresholds

from . import einstellungen as W
from . import format as F
from . import texte as T

# Reihenfolge der Ligen auf der Methodik-Seite (Entwurf Methodik_10): Bundesliga, Premier League, Serie A, La Liga
REIHENFOLGE = ("Bundesliga", "Premier League", "Serie A", "LaLiga")
KENNZAHLEN = tuple(k for k in KPI_KEYS if k != "kpi01")       # KPI 02–09 haben Schwellen
RICHTUNGEN = ("mehr", "weniger")
DATEI = {"de": "soccer-intelligence-schwellen.xlsx", "en": "soccer-intelligence-thresholds.xlsx"}
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
ZAHLWORT = {"de": ("null", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf"),
            "en": ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve")}


def download_pfad(lang: str) -> str:
    """Adresse der Excel-Datei im Verzeichnis der Methodik: /de/methodik/soccer-intelligence-schwellen.xlsx"""
    return f"/{lang}/{W.PFADE['methodik'][lang]}/{DATEI[lang]}"


def download_sprache(pfad: str) -> str | None:
    """Sprache, wenn pfad die Adresse der Excel-Datei ist, sonst None."""
    return next((lang for lang in W.SPRACHEN if pfad == download_pfad(lang)), None)


def _konfig(cfg: ThresholdConfig | None) -> ThresholdConfig:
    return cfg if cfg is not None else load_thresholds(settings.THRESHOLDS_FILE)


def saisons(text: str) -> tuple[int, str, str]:
    """„2019/2020-2025/2026“ → (7, „2019/20“, „2025/26“). Unlesbar → (0, „–“, „–“)."""
    m = re.fullmatch(r"\s*(\d{4})/(\d{4})\s*-\s*(\d{4})/(\d{4})\s*", text or "")
    if not m:
        return 0, F.STRICH, F.STRICH
    von, bis = int(m.group(1)), int(m.group(3))
    return bis - von + 1, f"{von}/{str(von + 1)[-2:]}", f"{bis}/{str(bis + 1)[-2:]}"


def schwelle_text(wert: Decimal, lang: str) -> str:
    """„10 %“ / „10%“ (ganze Zahl ohne Nachkommastellen, sonst zwei)."""
    zahl = f"{wert:.0f}" if wert == wert.to_integral_value() else f"{wert:.2f}".replace(".", F.FORMATE[lang]["komma"])
    return F.FORMATE[lang]["prozent"].format(zahl=zahl)


def daten(lang: str = W.SPRACHE, cfg: ThresholdConfig | None = None) -> dict:
    """Werte für die Vorlage methodik.<sprache>.html."""
    cfg = _konfig(cfg)
    namen = {lg.name: lg for lg in W.LIGEN}
    ligen = []
    for name in REIHENFOLGE:
        web = namen.get(name)
        if web is None:
            continue
        zeilen = []
        for kpi in KENNZAHLEN:
            t = cfg.get(name, kpi)
            for richtung, signal in (("mehr", t.positiv), ("weniger", t.negativ)):
                if signal is not None:
                    zeilen.append({"kpi": kpi, "richtung": richtung, "schwelle": schwelle_text(signal.schwelle, lang),
                                   "stufe": signal.signalqualitaet})
        zahl = {st: sum(1 for z in zeilen if z["stufe"] == st) for st in LEVELS}
        ligen.append({"key": web.key, "slug": web.slug, "zeilen": zeilen, "anzahl": len(zeilen), **zahl})
    n, von, bis = saisons(cfg.saisons)
    alle = [z for lg in ligen for z in lg["zeilen"]]
    return {
        "ligen": ligen,
        "saisons": n, "saison_von": von, "saison_bis": bis,
        "saisons_wort": ZAHLWORT[lang][n] if 1 < n < len(ZAHLWORT[lang]) else str(n),
        "kennzahlen": len(KENNZAHLEN), "ligen_zahl": len(ligen),
        "moeglich": len(KENNZAHLEN) * len(ligen) * len(RICHTUNGEN),
        "kombinationen": len(alle),
        "stark": sum(1 for z in alle if z["stufe"] == HIGH),
        "mittel": sum(1 for z in alle if z["stufe"] == MEDIUM),
        "gering": sum(1 for z in alle if z["stufe"] == LOW),
        "download": DATEI[lang],
    }


def _zahl(wert):
    return float(wert) if isinstance(wert, Decimal) else wert


def excel(lang: str = W.SPRACHE, cfg: ThresholdConfig | None = None) -> bytes:
    """Excel-Datei mit allen Zahlen je Liga, Kennzahl und Richtung (Blatt 1) und der Grundlage (Blatt 2)."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    cfg = _konfig(cfg)
    tx = lambda k, **w: T.t(f"methodik_excel.{k}", lang, **w)          # noqa: E731
    wb = Workbook()
    ws = wb.active
    ws.title = tx("blatt_schwellen")
    kopf = [tx(f"spalte.{s}") for s in ("liga", "kennzahl", "richtung", "schwelle", "signalqualitaet", "spiele",
                                        "trefferquote", "vergleichswert", "mehrwert", "spanne_links",
                                        "spanne_rechts", "saisons_positiv")]
    ws.append(kopf)
    fett, grau = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="0B3D2E")
    for zelle in ws[1]:
        zelle.font, zelle.fill = fett, grau
        zelle.alignment = Alignment(vertical="center", wrap_text=True)
    namen = {lg.name: lg for lg in W.LIGEN}
    for name in REIHENFOLGE:
        if name not in namen:
            continue
        for kpi in KENNZAHLEN:
            t = cfg.get(name, kpi)
            for richtung, s in (("mehr", t.positiv), ("weniger", t.negativ)):
                if s is None:
                    continue
                ws.append([T.t(f"liga.{namen[name].key}", lang), T.t(f"kennzahl.{kpi}.name", lang),
                           tx(f"richtung.{richtung}"), _zahl(s.schwelle), T.t(f"stufe_kurz.{s.signalqualitaet}", lang),
                           s.spiele, _zahl(s.trefferquote), _zahl(s.vergleichsgruppe), _zahl(s.mehrwert),
                           _zahl(s.spanne_links), _zahl(s.spanne_rechts), s.saisons_positiv])
    for zeile in ws.iter_rows(min_row=2):
        for zelle in zeile[3:4] + zeile[6:11]:
            zelle.number_format = "0.00"
    for spalte, breite in zip("ABCDEFGHIJKL", (16, 34, 16, 12, 16, 10, 14, 16, 14, 14, 14, 14)):
        ws.column_dimensions[spalte].width = breite
    ws.freeze_panes = "A2"

    g = wb.create_sheet(tx("blatt_grundlage"))
    n, von, bis = saisons(cfg.saisons)
    zeilen = [
        (tx("titel"), ""),
        ("", ""),
        (tx("saisons"), f"{von} – {bis} ({n})"),
        (tx("berechnet"), cfg.berechnet),
        (tx("freigabe"), cfg.freigabe),
        ("", ""),
        (tx("regeln"), ""),
        *[(T.t(f"stufe_kurz.{st}", lang), tx(f"regel.{st}")) for st in LEVELS],
        (tx("regel.mindest_titel"), tx("regel.mindest")),
        (tx("regel.schwelle_titel"), tx("regel.schwelle")),
        ("", ""),
        (tx("spalten"), ""),
        *[(tx(f"spalte.{s}"), tx(f"erklaerung.{s}")) for s in ("trefferquote", "vergleichswert", "mehrwert",
                                                                "spanne_links", "saisons_positiv")],
        ("", ""),
        (tx("hinweis"), ""),
    ]
    for a, b in zeilen:
        g.append([a, b])
    g["A1"].font = Font(bold=True, size=14)
    for zelle in ("A7", "A14"):
        g[zelle].font = Font(bold=True)
    g.column_dimensions["A"].width = 30
    g.column_dimensions["B"].width = 100
    for zeile in g.iter_rows():
        for zelle in zeile:
            zelle.alignment = Alignment(vertical="top", wrap_text=True)

    zeit = datetime.fromisoformat(cfg.berechnet) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", cfg.berechnet or "") \
        else datetime(2026, 1, 1)
    wb.properties.creator = "Soccer Intelligence"
    wb.properties.created = wb.properties.modified = zeit
    puffer = io.BytesIO()
    wb.save(puffer)
    return puffer.getvalue()
