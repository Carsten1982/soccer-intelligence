"""Zellen der Liga-Tabelle für KPI 01–04 (Dashboard-Briefing, Kapitel 7–9).

Reine Funktionen (kein Streamlit): aus den Rechenergebnissen werden HTML-Zellen.
Alle Texte werden maskiert. Fehlende Werte erscheinen als „–“.
"""

from __future__ import annotations

from html import escape

from core.kpis import (
    LIGHT, NONE, PLACEHOLDER, SAMPLE, STRONG, FormTeam, KpiResult, MatchKpis, de, de_signed, round1,
)
from views.components import ColumnGroup

FORM_TITLES = {"S": "Sieg", "U": "Unentschieden", "N": "Niederlage"}
ANOMALY_LABEL = {NONE: "Keine Anomalie", LIGHT: "Leichte Anomalie", STRONG: "Starke Anomalie"}
VORLAEUFIG_HINT = "Vorläufig: weniger Spiele als im KPI-Regelwerk vorgesehen"

GROUPS = [
    ColumnGroup("KPI 01", ["Heim", "Gast"], "Formkurve (letzte 5 Spiele)"),
    ColumnGroup("KPI 02", ["Team 1", "Team 2", "Hauptwert", "Ligareferenz", "Abweichung", "Anomalie",
                           "Datenbasis", "Beschreibung"], "Erwartete Tore"),
    ColumnGroup("KPI 03", ["Team 1", "Team 2", "Hauptwert", "Referenzwert", "Abweichung", "Anomalie",
                           "Datenbasis", "Beschreibung"], "Over 2.5 Goals"),
    ColumnGroup("KPI 04", ["Team 1", "Team 2", "Hauptwert", "Ligareferenz", "Abweichung", "Anomalie",
                           "Datenbasis", "Beschreibung"], "Gelbe Karten"),
]
N_CELLS = sum(len(g.columns) for g in GROUPS)


def form_cell(ft: FormTeam) -> str:
    marks = []
    for f in ft.form:
        if f == PLACEHOLDER:
            marks.append('<span class="si-form si-form-none" title="kein Spiel">–</span>')
        else:
            marks.append(f'<span class="si-dot si-form-{f}" title="{FORM_TITLES[f]}"></span>')
    return f'<span class="si-formrow" title="{ft.anzahl} von 5 Spielen">{"".join(marks)}</span>'


def anomaly_cell(anomaly: str | None) -> str:
    if anomaly is None:
        return PLACEHOLDER
    return f'<span class="si-dot si-anom-{anomaly}" title="{ANOMALY_LABEL[anomaly]}"></span>'


def data_basis_cell(r: KpiResult, reference_games: int | None = None) -> str:
    h, a = r.heim.spiele, r.auswaerts.spiele
    text = str(h) if h == a else f"{h} / {a}"
    title = f"Heim {h} · Gast {a} Spiele"
    if reference_games is not None:
        title += f" · Referenzspiele der Liga: {reference_games}"
    badge = f' <span class="si-v" title="{VORLAEUFIG_HINT}">V</span>' if r.vorlaeufig else ""
    return f'<span title="{escape(title)}">{text}</span>{badge}'


def description_cell(r: KpiResult) -> str:
    if r.ueberschrift is None:
        return PLACEHOLDER
    text = f"<br>{escape(r.text)}" if r.text else ""
    return f'<div class="si-desc"><strong>{escape(r.ueberschrift)}</strong>{text}</div>'


def pct(value) -> str:
    return PLACEHOLDER if value is None else f"{de_signed(value)} %"


def kpi_cells(r: KpiResult, reference: str) -> list[str]:
    """8 Zellen: Team 1, Team 2, Hauptwert, Referenz, Abweichung, Anomalie, Datenbasis, Beschreibung."""
    if r.kpi == "KPI03":
        dev_h, dev_a = r.teamabweichung
        team1 = de(r.heim.wert_rund) + (f" ({pct(round1(dev_h))})" if dev_h is not None else "")
        team2 = de(r.auswaerts.wert_rund) + (f" ({pct(round1(dev_a))})" if dev_a is not None else "")
        ref_games = None
    else:
        team1, team2 = de(r.heim.wert_rund), de(r.auswaerts.wert_rund)
        ref_games = r.referenz.spiele if r.referenz is not None else None
    return [
        team1, team2,
        f"<strong>{de(r.hauptwert_rund)}</strong>",
        reference,
        pct(r.abweichung_rund),
        anomaly_cell(r.anomalie),
        data_basis_cell(r, ref_games if r.kpi == "KPI04" else None),
        description_cell(r),
    ]


def match_cells(k: MatchKpis) -> list[str]:
    ref02 = de(k.kpi02.referenz.wert_rund) if k.kpi02.referenz else PLACEHOLDER
    ref04 = de(k.kpi04.referenz.wert_rund) if k.kpi04.referenz else PLACEHOLDER
    return ([form_cell(k.form_home), form_cell(k.form_away)]
            + kpi_cells(k.kpi02, ref02)
            + kpi_cells(k.kpi03, "2,5")
            + kpi_cells(k.kpi04, ref04))


def empty_cells() -> list[str]:
    """Verschobene/abgesagte Spiele: Status wird angezeigt, KPI-Werte nicht (Briefing 4.4, Regel 4)."""
    return [PLACEHOLDER] * N_CELLS


LEGEND_HTML = (
    '<div class="si-legend">Anomalie: '
    '<span class="si-dot si-anom-keine"></span> Keine Anomalie '
    '<span class="si-dot si-anom-leicht"></span> Leichte Anomalie '
    '<span class="si-dot si-anom-stark"></span> Starke Anomalie'
    ' &nbsp;·&nbsp; Formkurve: <span class="si-dot si-form-S"></span> Sieg '
    '<span class="si-dot si-form-U"></span> Unentschieden <span class="si-dot si-form-N"></span> Niederlage'
    f' &nbsp;·&nbsp; <span class="si-v">V</span> {VORLAEUFIG_HINT} (unter {SAMPLE} Spielen)'
    "</div>"
)
