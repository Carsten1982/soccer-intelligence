"""Kompakte Liga-Tabelle mit KPI 01–09 (Dashboard-Briefing 4.1, Design abgenommen am 08.11.2026).

Je Begegnung eine Zeile: Nummer, Spiel, Formkurve und je KPI 02–09 der Hauptwert mit Anomalie-Punkt
(KPI 03: Abweichung zur 2,5-Tore-Marke, weil sein Hauptwert dem von KPI 02 entspricht). Ein Klick auf die
Zeile klappt alle Details auf (HTML <details>, ohne JavaScript): je KPI Einstufung, Hauptwert, Abweichung,
Ligareferenz, Teamwerte, Datenbasis, Überschrift und Text.

Reine Funktionen (kein Streamlit). Alle Texte werden maskiert. Fehlende Werte erscheinen als „–“.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape

from core.kpis import (
    FORM_SAMPLE, LIGHT, NONE, PLACEHOLDER, SAMPLE, STRONG, FormTeam, KpiResult, MatchKpis, de, de_signed, round_display,
)
from core.top import TOP_KPIS

FORM_TITLES = {"S": "Sieg", "U": "Unentschieden", "N": "Niederlage"}
ANOMALY_LABEL = {NONE: "Keine Anomalie", LIGHT: "Leichte Anomalie", STRONG: "Starke Anomalie"}
VORLAEUFIG_HINT = "Vorläufig: weniger Spiele als im KPI-Regelwerk vorgesehen"


@dataclass(frozen=True)
class KpiColumn:
    key: str        # Attribut in MatchKpis
    number: str     # „KPI 02“
    short: str      # Spaltenkopf
    name: str       # voller Name (Details, Tooltip)


COLUMNS = [
    KpiColumn("kpi02", "KPI 02", "Tore", "Erwartete Tore"),
    KpiColumn("kpi03", "KPI 03", "Über 2,5", "Over 2.5 Goals"),
    KpiColumn("kpi04", "KPI 04", "Gelbe K.", "Gelbe Karten"),
    KpiColumn("kpi05", "KPI 05", "Ecken", "Ecken"),
    KpiColumn("kpi06", "KPI 06", "Tore HZ 1", "Tore 1. Halbzeit"),
    KpiColumn("kpi07", "KPI 07", "Tore HZ 2", "Tore 2. Halbzeit"),
    KpiColumn("kpi08", "KPI 08", "BTTS", "Beide Teams treffen"),
    KpiColumn("kpi09", "KPI 09", "Aufs Tor", "Schüsse aufs Tor"),
]
assert [c.key for c in COLUMNS] == list(TOP_KPIS)


# --- kleine Bausteine -----------------------------------------------------------------

def form_marks(ft: FormTeam) -> str:
    marks = []
    for f in ft.form:
        if f == PLACEHOLDER:
            marks.append('<span class="si-form si-form-none" title="kein Spiel">–</span>')
        else:
            marks.append(f'<span class="si-dot si-form-{f}" title="{FORM_TITLES[f]}"></span>')
    return f'<span class="si-formrow" title="{ft.anzahl} von {FORM_SAMPLE} Spielen">{"".join(marks)}</span>'


def anomaly_cell(anomaly: str | None) -> str:
    if anomaly is None:
        return PLACEHOLDER
    return f'<span class="si-dot si-anom-{anomaly}" title="{ANOMALY_LABEL[anomaly]}"></span>'


def v_badge(r: KpiResult) -> str:
    return f'<span class="si-v" title="{VORLAEUFIG_HINT}">V</span>' if r.vorlaeufig else ""


def pct(value) -> str:
    """Prozentwert mit Vorzeichen: +23,21 % / −8,90 % / 0,00 %."""
    return PLACEHOLDER if value is None else f"{de_signed(value)} %"


def value_text(r: KpiResult, value) -> str:
    """Zahl mit zwei Nachkommastellen, bei KPI 08 mit „%“."""
    if value is None:
        return PLACEHOLDER
    return f"{de(value)} %" if r.prozent else de(value)


def compact_value(col: KpiColumn, r: KpiResult) -> str:
    """Wert in der kompakten Zeile. KPI 03 zeigt die Abweichung zur 2,5-Marke (Entscheidung 08.11.2026)."""
    if col.key == "kpi03":
        return pct(r.abweichung_rund)
    return value_text(r, r.hauptwert_rund)


def compact_cell(col: KpiColumn, r: KpiResult) -> str:
    label = ANOMALY_LABEL.get(r.anomalie, "nicht berechenbar")
    title = escape(f"{col.number} – {col.name}: {label}" + (" (vorläufig)" if r.vorlaeufig else ""))
    return (f'<div class="si-cc si-ckv" title="{title}"><span class="si-num">{compact_value(col, r)}</span>'
            f'{anomaly_cell(r.anomalie)}{v_badge(r)}</div>')


# --- Detail-Kärtchen ----------------------------------------------------------------

def _team_lines(k: MatchKpis, left: str, right: str) -> str:
    return (f'<div class="si-kc-t"><span>{escape(k.match.home)}</span><b>{left}</b>'
            f'<span>{escape(k.match.away)}</span><b>{right}</b></div>')


def form_card(k: MatchKpis) -> str:
    return (f'<div class="si-kc"><div class="si-kc-h"><b>KPI 01</b>&nbsp;Formkurve (letzte {FORM_SAMPLE} Spiele)</div>'
            + _team_lines(k, form_marks(k.form_home), form_marks(k.form_away)) + "</div>")


def detail_card(col: KpiColumn, r: KpiResult, k: MatchKpis) -> str:
    if r.kpi == "KPI03":
        dev_h, dev_a = r.teamabweichung
        team1 = f"{de(r.heim.wert_rund)} ({pct(round_display(dev_h))})" if r.heim.wert is not None else PLACEHOLDER
        team2 = f"{de(r.auswaerts.wert_rund)} ({pct(round_display(dev_a))})" if r.auswaerts.wert is not None else PLACEHOLDER
        ref_label, ref_value = "Referenz", "2,50 (fest)"
        basis = f"{r.heim.spiele} / {r.auswaerts.spiele} Spiele"
    else:
        team1, team2 = value_text(r, r.heim.wert_rund), value_text(r, r.auswaerts.wert_rund)
        ref_label, ref_value = "Liga", value_text(r, r.referenz.wert_rund if r.referenz else None)
        basis = f"{r.heim.spiele} / {r.auswaerts.spiele} Spiele"
        if r.referenz is not None:
            basis += f" · Liga {r.referenz.spiele} Spiele"
    label = ANOMALY_LABEL.get(r.anomalie, "nicht berechenbar")
    text = ""
    if r.ueberschrift:
        text = f"<b>{escape(r.ueberschrift)}</b>" + (f" {escape(r.text)}" if r.text else "")
    return (
        f'<div class="si-kc"><div class="si-kc-h">{anomaly_cell(r.anomalie)}<b>{col.number}</b>&nbsp;{escape(col.name)}'
        f'<span class="si-kc-a">{label}</span></div>'
        f'<div class="si-kc-m"><div><span>Hauptwert</span><b>{value_text(r, r.hauptwert_rund)}</b></div>'
        f'<div><span>Abweichung</span><b>{pct(r.abweichung_rund)}</b></div>'
        f'<div><span>{ref_label}</span><b>{ref_value}</b></div></div>'
        + _team_lines(k, team1, team2)
        + f'<div class="si-kc-b">Datenbasis: {basis} {v_badge(r)}</div>'
        + (f'<div class="si-kc-x">{text}</div>' if text else "")
        + "</div>"
    )


# --- Tabelle --------------------------------------------------------------------------

def _head() -> str:
    cells = "".join(f'<div class="si-cc si-ckv" title="{c.number} – {escape(c.name)}"><small>{c.number}</small>'
                    f'{escape(c.short)}</div>' for c in COLUMNS)
    return ('<div class="si-crow si-chead"><div class="si-cc si-cn si-cs1">#</div>'
            '<div class="si-cc si-cg si-cs2">Spiel</div><div class="si-cc si-cf">Form</div>'
            f'{cells}<div class="si-cc si-cx"></div></div>')


def _names(home: str, away: str, status: str) -> str:
    badge = f'<span class="si-badge">{escape(status)}</span>' if status and status != "geplant" else ""
    return (f'<div class="si-cc si-cg si-cs2"><span class="si-team">{escape(home)}</span>'
            f'<span class="si-team">{escape(away)}</span>{badge}</div>')


def match_row(n: int, home: str, away: str, status: str, k: MatchKpis | None) -> str:
    """Eine Begegnung. Ohne KPIs (verschoben/abgesagt): Zeile ohne Werte und ohne Details (Briefing 4.4, Regel 4)."""
    alt = " si-alt" if n % 2 == 0 else ""
    number = f'<div class="si-cc si-cn si-cs1">{n}</div>'
    if k is None:
        empty = "".join(f'<div class="si-cc si-ckv">{PLACEHOLDER}</div>' for _ in COLUMNS)
        return (f'<div class="si-crow si-cplain{alt}">{number}{_names(home, away, status)}'
                f'<div class="si-cc si-cf">{PLACEHOLDER}</div>{empty}<div class="si-cc si-cx"></div></div>')
    form = (f'<div class="si-cc si-cf"><span class="si-fline">{form_marks(k.form_home)}</span>'
            f'<span class="si-fline">{form_marks(k.form_away)}</span></div>')
    cells = "".join(compact_cell(c, getattr(k, c.key)) for c in COLUMNS)
    summary = (f'<summary class="si-crow{alt}">{number}{_names(home, away, status)}{form}{cells}'
               '<div class="si-cc si-cx"><span class="si-chev">›</span></div></summary>')
    cards = form_card(k) + "".join(detail_card(c, getattr(k, c.key), k) for c in COLUMNS)
    detail = f'<div class="si-cdetail"><div class="si-cdetail-in">{cards}</div></div>'
    return f'<details class="si-cdet">{summary}{detail}</details>'


def compact_table_html(rows: list[tuple[str, str, str, MatchKpis | None]]) -> str:
    """rows: (Heim, Gast, Status, KPIs oder None) in der Reihenfolge des Spielplans."""
    body = "".join(match_row(i, h, a, s, k) for i, (h, a, s, k) in enumerate(rows, start=1))
    return f'<div class="si-cwrap"><div class="si-cgrid">{_head()}{body}</div></div>'


LEGEND_HTML = (
    '<div class="si-legend">Anomalie: '
    '<span class="si-dot si-anom-keine"></span> keine '
    '<span class="si-dot si-anom-leicht"></span> leicht '
    '<span class="si-dot si-anom-stark"></span> stark'
    ' &nbsp;·&nbsp; Form: <span class="si-dot si-form-S"></span> Sieg '
    '<span class="si-dot si-form-U"></span> Unentschieden <span class="si-dot si-form-N"></span> Niederlage'
    f' &nbsp;·&nbsp; <span class="si-v">V</span> vorläufig (unter {SAMPLE} Spielen)'
    ' &nbsp;·&nbsp; KPI 03 zeigt die Abweichung zur 2,5-Tore-Marke (sein Hauptwert entspricht KPI 02)'
    ' &nbsp;·&nbsp; Alle Werte mit zwei Nachkommastellen'
    "</div>"
)
