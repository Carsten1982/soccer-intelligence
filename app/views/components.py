"""Gemeinsame Bausteine der Oberfläche: Stil, Kopfbereich, Spieltabelle, Sperrhinweis.

Die HTML-Funktionen (…_html) sind reine Funktionen ohne Streamlit und werden getestet.
Alle Texte aus Excel-Dateien werden mit html.escape maskiert.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape

import streamlit as st

from core import settings

# --- Stil (Dashboard-Briefing, Kapitel 3.1) ------------------------------------

NAVY = "#14213d"       # Überschriften, zentrale Informationen
SLATE = "#5b6b84"      # Untertitel, Beschriftungen
LINE = "#d8e0eb"       # feine Trennlinien
ROW_ALT = "#f3f6fa"    # dezente Zeilenfläche
HEAD_BG = "#eef2f7"    # Kopfzeile der Tabelle
NAV_BG = "#343a40"     # Navigationsleiste (dunkelgrau)
NAV_ACTIVE = "#4a90e2" # Balken unter dem aktiven Tab

CSS = f"""
<style>
.si-header {{display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; flex-wrap:wrap;
  margin:0 0 1rem 0;}}
.si-header h1 {{color:{NAVY}; font-size:2rem; font-weight:800; margin:0; padding:0; line-height:1.2;}}
.si-header .si-sub {{color:{SLATE}; font-size:1rem; margin-top:.15rem;}}
.si-matchday {{text-align:right; min-width:12rem;}}
.si-matchday .si-label {{color:{SLATE}; font-size:.8rem;}}
.si-matchday .si-box {{border:1px solid {LINE}; border-radius:.5rem; padding:.35rem .8rem; color:{NAVY};
  font-weight:600; background:#fff; display:inline-block; margin-top:.2rem;}}
/* Tabelle scrollt in einem eigenen Rahmen: max. 72 % der Fensterhöhe, damit die horizontale Scrollbar
   immer sichtbar ist (Briefing 4.3). Kopfzeilen bleiben oben, # und Spiel links stehen. */
.si-tablewrap {{overflow:auto; max-height:72vh; border:1px solid {LINE}; border-radius:.5rem; margin-bottom:.5rem;
  scrollbar-width:auto; scrollbar-color:#9aa6b8 {HEAD_BG};}}
.si-tablewrap::-webkit-scrollbar {{height:14px; width:12px;}}
.si-tablewrap::-webkit-scrollbar-track {{background:{HEAD_BG};}}
.si-tablewrap::-webkit-scrollbar-thumb {{background:#9aa6b8; border-radius:7px; border:3px solid {HEAD_BG};}}
.si-table {{border-collapse:separate; border-spacing:0; width:100%; font-size:.9rem; color:{NAVY};}}
.si-table th, .si-table td {{padding:.45rem .6rem; border-bottom:1px solid {LINE}; background:#fff;
  vertical-align:middle; white-space:nowrap;}}
.si-table thead th {{background:{HEAD_BG}; font-weight:700; text-align:left;}}
.si-table thead th.si-sub {{font-weight:500; font-size:.75rem; color:{SLATE};}}
.si-table thead th.si-group {{border-left:2px solid {LINE};}}
.si-table td.si-groupstart, .si-table th.si-groupstart {{border-left:2px solid {LINE};}}
.si-table tbody tr:nth-child(even) td {{background:{ROW_ALT};}}
.si-table .si-sticky {{position:sticky; z-index:2;}}
.si-table .si-c1 {{left:0; width:3rem; min-width:3rem; max-width:3rem; text-align:center;}}
.si-table .si-c2 {{left:3rem; min-width:13rem; border-right:2px solid {LINE};}}
.si-table thead th {{position:sticky; top:0; z-index:3;}}
.si-table thead tr:first-child th {{height:3.6rem; box-sizing:border-box;}}
.si-table thead tr:nth-child(2) th {{top:3.6rem;}}
.si-table thead th.si-sticky {{z-index:4;}}
.si-table .si-team {{display:block; line-height:1.35;}}
.si-badge {{display:inline-block; margin-top:.2rem; padding:0 .4rem; border-radius:.3rem; font-size:.75rem;
  background:#fde8e8; color:#9b1c1c;}}
.si-footer {{color:{SLATE}; font-size:.75rem; margin-top:2rem;}}
.si-groupsub {{font-weight:500; font-size:.8rem; color:{SLATE};}}
.si-table td.si-desccol {{white-space:normal; min-width:17rem; max-width:20rem; font-size:.8rem; line-height:1.3;}}
.si-desc strong {{color:{NAVY};}}
.si-dot {{display:inline-block; width:.8rem; height:.8rem; border-radius:50%; vertical-align:middle; margin:0 .08rem;}}
.si-formrow {{white-space:nowrap;}}
.si-form {{display:inline-block; width:.8rem; text-align:center; color:#9aa6b8; margin:0 .08rem;}}
.si-form-S {{background:#2e9e5b;}} .si-form-U {{background:#9aa6b8;}} .si-form-N {{background:#d64545;}}
.si-anom-keine {{background:#9aa6b8;}} .si-anom-leicht {{background:#f2c230;}} .si-anom-stark {{background:#d64545;}}
.si-v {{display:inline-block; padding:0 .3rem; border-radius:.25rem; background:#fff3cd; color:#7a5b00;
  font-size:.7rem; font-weight:700; cursor:help;}}
.si-legend {{color:{SLATE}; font-size:.8rem; margin:.25rem 0 1rem 0;}}
.si-legend .si-dot {{margin-left:.6rem;}}
.si-matchday-nav {{text-align:center; min-width:0;}}

/* Abstand oben verkleinert (Navigation -> Überschrift, Änderung 31.10.2026) */
[data-testid="stMainBlockContainer"] {{padding-top:61px !important;}}

/* Navigation: dunkelgraue Leiste, weisse Schrift, aktiver Tab fett mit blauem Balken */
[data-testid="stHeader"] {{background:{NAV_BG} !important;}}
[data-testid="stHeader"] [data-testid="stToolbar"] * {{color:#e9ecef !important;}}
[data-testid="stTopNavLink"] {{color:#c3c9d1 !important; background:transparent !important; border-radius:0 !important;
  border-bottom:3px solid transparent;}}
[data-testid="stTopNavLink"] * {{color:inherit !important; font-weight:inherit !important;}}
[data-testid="stTopNavLink"]:hover {{color:#ffffff !important; background:rgba(255,255,255,.08) !important;}}
[data-testid="stTopNavLink"][aria-current="page"] {{color:#ffffff !important; font-weight:700 !important;
  border-bottom:3px solid {NAV_ACTIVE} !important;}}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


# --- Kopfbereich (Kapitel 3.2) ---------------------------------------------------

TITLE = "Soccer Intelligence"
SUBTITLE = "KPI-Übersicht pro Spiel – alle Begegnungen eines Spieltags"


def header_html(right_label: str, right_value: str) -> str:
    right = ""
    if right_value:
        right = (f'<div class="si-matchday"><div class="si-label">{escape(right_label)}</div>'
                 f'<div class="si-box">{escape(right_value)}</div></div>')
    return (f'<div class="si-header"><div><h1>{TITLE}</h1><div class="si-sub">{escape(SUBTITLE)}</div></div>'
            f"{right}</div>")


def title_html() -> str:
    return f'<div class="si-header"><div><h1>{TITLE}</h1><div class="si-sub">{escape(SUBTITLE)}</div></div></div>'


def matchday_box_html(label: str, value: str) -> str:
    return (f'<div class="si-matchday si-matchday-nav"><div class="si-label">{escape(label)}</div>'
            f'<div class="si-box">{escape(value)}</div></div>')


def header(right_label: str = "", right_value: str = "") -> None:
    st.markdown(header_html(right_label, right_value), unsafe_allow_html=True)


def footer() -> None:
    st.markdown(f'<div class="si-footer">Soccer Intelligence · Version {escape(settings.APP_VERSION)}</div>',
                unsafe_allow_html=True)


# --- Spieltabelle (Kapitel 4.1–4.3) ----------------------------------------------

@dataclass
class ColumnGroup:
    """Eine KPI-Gruppe, z. B. „KPI 02“ / „Erwartete Tore“ mit ihren Spalten."""
    title: str
    columns: list[str] = field(default_factory=list)
    subtitle: str = ""


@dataclass
class MatchRow:
    home: str
    away: str
    status: str = ""                      # leer/„geplant“ oder „verschoben“/„abgesagt“
    cells: list[str] = field(default_factory=list)   # bereits fertiges HTML je KPI-Spalte


def match_table_html(rows: list[MatchRow], groups: list[ColumnGroup] | None = None) -> str:
    """Tabelle mit fixierten Spalten # und Spiel und horizontal scrollbaren KPI-Gruppen."""
    groups = groups or []
    two_rows = bool(groups)
    rs = ' rowspan="2"' if two_rows else ""
    head1 = [f'<th class="si-sticky si-c1"{rs}>#</th>', f'<th class="si-sticky si-c2"{rs}>Spiel</th>']
    head2: list[str] = []
    for g in groups:
        sub = f'<div class="si-groupsub">{escape(g.subtitle)}</div>' if g.subtitle else ""
        head1.append(f'<th class="si-group" colspan="{max(len(g.columns), 1)}">{escape(g.title)}{sub}</th>')
        for i, c in enumerate(g.columns):
            cls = "si-sub si-groupstart" if i == 0 else "si-sub"
            head2.append(f'<th class="{cls}">{escape(c)}</th>')
    thead = "<tr>" + "".join(head1) + "</tr>" + ("<tr>" + "".join(head2) + "</tr>" if two_rows else "")

    body = []
    for n, r in enumerate(rows, start=1):
        badge = ""
        if r.status and r.status != "geplant":
            badge = f'<span class="si-badge">{escape(r.status)}</span>'
        tds = [
            f'<td class="si-sticky si-c1">{n}</td>',
            f'<td class="si-sticky si-c2"><span class="si-team">{escape(r.home)}</span>'
            f'<span class="si-team">{escape(r.away)}</span>{badge}</td>',
        ]
        pos = 0
        for g in groups:
            for i, col in enumerate(g.columns):
                cell = r.cells[pos] if pos < len(r.cells) else "–"
                classes = (["si-groupstart"] if i == 0 else []) + (["si-desccol"] if col == "Beschreibung" else [])
                cls = f' class="{" ".join(classes)}"' if classes else ""
                tds.append(f"<td{cls}>{cell}</td>")
                pos += 1
        body.append("<tr>" + "".join(tds) + "</tr>")
    return (f'<div class="si-tablewrap"><table class="si-table"><thead>{thead}</thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def match_table(rows: list[MatchRow], groups: list[ColumnGroup] | None = None) -> None:
    st.markdown(match_table_html(rows, groups), unsafe_allow_html=True)


# --- Sperrhinweis (Kapitel 4.4, Regel 9) ------------------------------------------

def blocked_notice(db_errors: bool, fx_errors: bool, dq_page=None) -> None:
    parts = []
    if db_errors:
        parts.append("die **Datenbank**")
    if fx_errors:
        parts.append("der **Spielplan**")
    verb = "enthalten" if len(parts) > 1 else "enthält"
    st.error(f"Die Tabelle kann nicht angezeigt werden, weil {' und '.join(parts)} Fehler {verb}.", icon="⛔")
    if dq_page is not None:
        try:
            st.page_link(dq_page, label="Zum Bereich Datenqualität", icon="🔎")
            return
        except Exception:  # noqa: BLE001 - z. B. ausserhalb der Navigation (Tests)
            pass
    st.markdown("Details im Bereich **Datenqualität**.")
