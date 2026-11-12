"""Gemeinsame Bausteine der Oberfläche: Stil, Kopfbereich, Fusszeile, Sperrhinweis.

Die Liga-Tabelle selbst steht seit Etappe H in views/kpi_table.py.
Die HTML-Funktionen (…_html) sind reine Funktionen ohne Streamlit und werden getestet.
Alle Texte aus Excel-Dateien werden mit html.escape maskiert.
"""

from __future__ import annotations

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
NAV_ACTIVE = "#4a90e2"  # Balken unter dem aktiven Tab

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
/* Kopfbereich Top Anomalien mit mehreren Ligen (Etappe F): kompakt in zwei Spalten */
.si-matchday .si-box.si-grid {{display:inline-grid; grid-template-columns:auto auto; column-gap:1.4rem; row-gap:.1rem;
  text-align:left; font-size:.92rem;}}
.si-grid .si-grid-item {{white-space:nowrap;}}
@media (max-width: 640px) {{ .si-matchday .si-box.si-grid {{grid-template-columns:auto;}} }}
.si-badge {{display:inline-block; margin-top:.2rem; padding:0 .4rem; border-radius:.3rem; font-size:.75rem;
  background:#fde8e8; color:#9b1c1c;}}
.si-footer {{color:{SLATE}; font-size:.75rem; margin-top:2rem;}}
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
.si-matchday-nav .si-box {{white-space:nowrap;}}
[class*="st-key-prev_"] button p, [class*="st-key-next_"] button p {{font-size:1.5rem !important; line-height:1 !important;}}
[class*="st-key-prev_"] button, [class*="st-key-next_"] button {{min-height:2.6rem; padding:0 .7rem;}}

/* Kompakte Liga-Tabelle (Etappe H, Briefing 4.1): Raster statt Tabelle, jede Begegnung aufklappbar (<details>).
   Die Spalten # und Spiel bleiben beim seitlichen Schieben stehen. */
.si-cwrap {{overflow-x:auto; border:1px solid {LINE}; border-radius:.5rem; margin-bottom:.5rem;
  scrollbar-width:auto; scrollbar-color:#9aa6b8 {HEAD_BG};}}
.si-cgrid {{min-width:1060px; color:{NAVY};}}
.si-crow {{display:grid; grid-template-columns:2.4rem 12.5rem 5.6rem repeat(8, minmax(5.9rem, 1fr)) 1.8rem;
  align-items:center; border-bottom:1px solid {LINE}; font-size:.9rem; background:#fff;}}
.si-crow.si-alt {{background:{ROW_ALT};}}
.si-chead {{background:{HEAD_BG}; font-weight:700; font-size:.82rem; line-height:1.15;}}
.si-chead small {{display:block; font-weight:500; color:{SLATE}; font-size:.7rem;}}
details.si-cdet {{margin:0;}}
details.si-cdet > summary {{list-style:none; cursor:pointer;}}
details.si-cdet > summary::-webkit-details-marker {{display:none;}}
details.si-cdet > summary:hover, details.si-cdet[open] > summary {{background:#e8f0fb;}}
.si-cc {{padding:.42rem .5rem;}}
.si-cn {{text-align:center; color:{SLATE};}}
.si-cg .si-team {{display:block; line-height:1.3; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}}
.si-cg .si-badge {{margin-top:.15rem;}}
.si-cs1 {{position:sticky; left:0; z-index:2; background:inherit;}}
.si-cs2 {{position:sticky; left:2.4rem; z-index:2; background:inherit; border-right:2px solid {LINE};}}
.si-cf .si-fline {{display:block; line-height:1.45; white-space:nowrap;}}
.si-cf .si-dot, .si-kc .si-formrow .si-dot {{width:.68rem; height:.68rem;}}
.si-cf .si-form {{width:.68rem; font-size:.75rem;}}
.si-ckv {{text-align:right; white-space:nowrap; font-variant-numeric:tabular-nums;}}
.si-num {{margin-right:.35rem;}}
.si-ckv .si-v {{margin-left:.25rem;}}
.si-chev {{display:inline-block; color:{SLATE}; font-size:1.2rem; transition:transform .15s;}}
details.si-cdet[open] .si-chev {{transform:rotate(90deg);}}
.si-cdetail {{border-bottom:2px solid {LINE}; background:#fafbfd;}}
.si-cdetail-in {{position:sticky; left:0; width:min(100%, calc(100vw - 3rem)); box-sizing:border-box; display:grid;
  grid-template-columns:repeat(3, minmax(0, 1fr)); gap:.6rem; padding:.7rem;}}
.si-kc {{border:1px solid {LINE}; border-radius:.5rem; background:#fff; padding:.55rem .65rem; font-size:.82rem;
  color:{NAVY}; min-width:0;}}
.si-kc-h {{display:flex; align-items:center; gap:.35rem; font-size:.85rem; margin-bottom:.35rem;}}
.si-kc-a {{margin-left:auto; color:{SLATE}; font-size:.75rem; white-space:nowrap;}}
.si-kc-m {{display:grid; grid-template-columns:repeat(3, 1fr); gap:.3rem; margin-bottom:.35rem;}}
.si-kc-m span {{display:block; color:{SLATE}; font-size:.7rem;}}
.si-kc-m b {{font-size:.98rem;}}
.si-kc-t {{display:grid; grid-template-columns:minmax(0, 1fr) auto; gap:.05rem .5rem; margin-bottom:.3rem;}}
.si-kc-t span {{color:{SLATE}; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;}}
.si-kc-t b {{text-align:right; white-space:nowrap;}}
.si-kc-b {{color:{SLATE}; font-size:.72rem; margin-bottom:.3rem;}}
.si-kc-x {{line-height:1.35;}}
@media (max-width: 700px) {{
  .si-cgrid {{min-width:0; width:max-content;}}
  .si-crow {{grid-template-columns:2rem 9.2rem 5rem repeat(8, 5.6rem) 1.4rem; font-size:.84rem;}}
  .si-cs2 {{left:2rem;}}
  .si-cdetail-in {{grid-template-columns:1fr;}}
}}

/* Top Anomalien (Briefing 5.2) */
.si-card {{border:1px solid {LINE}; border-radius:.6rem; padding:.9rem 1rem; background:#fff; color:{NAVY};}}
.si-card-top {{display:flex; align-items:center; gap:.6rem; margin-bottom:.35rem;}}
.si-rank {{display:inline-flex; align-items:center; justify-content:center; width:1.8rem; height:1.8rem; border-radius:50%;
  background:{NAVY}; color:#fff; font-weight:700;}}
.si-card-meta {{color:{SLATE}; font-size:.85rem;}}
.si-card-match {{font-size:1.15rem; font-weight:700; margin:.1rem 0 .3rem 0;}}
.si-card-kpi {{color:{SLATE}; font-size:.85rem;}}
.si-card-value {{font-size:1rem; margin:.3rem 0 .5rem 0;}}
.si-card .si-desc {{font-size:.85rem; line-height:1.35;}}

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


def header_html(right_label: str, right_value: str | list[str], subtitle: str = SUBTITLE) -> str:
    """Kopfbereich. right_value: ein Text (Liga-Bereich) oder eine Liste (Top Anomalien: eine Zeile je Liga,
    kompakt in zwei Spalten, damit der Kopf bei vier Ligen nicht zu breit wird)."""
    right = ""
    if isinstance(right_value, list) and right_value:
        items = "".join(f'<div class="si-grid-item">{escape(v)}</div>' for v in right_value)
        right = (f'<div class="si-matchday"><div class="si-label">{escape(right_label)}</div>'
                 f'<div class="si-box si-grid">{items}</div></div>')
    elif right_value:
        right = (f'<div class="si-matchday"><div class="si-label">{escape(right_label)}</div>'
                 f'<div class="si-box">{escape(right_value)}</div></div>')
    return (f'<div class="si-header"><div><h1>{TITLE}</h1><div class="si-sub">{escape(subtitle)}</div></div>'
            f"{right}</div>")


def title_html() -> str:
    return f'<div class="si-header"><div><h1>{TITLE}</h1><div class="si-sub">{escape(SUBTITLE)}</div></div></div>'


def matchday_box_html(label: str, value: str) -> str:
    return (f'<div class="si-matchday si-matchday-nav"><div class="si-label">{escape(label)}</div>'
            f'<div class="si-box">{escape(value)}</div></div>')


def header(right_label: str = "", right_value: str | list[str] = "", subtitle: str = SUBTITLE) -> None:
    st.markdown(header_html(right_label, right_value, subtitle), unsafe_allow_html=True)


def footer() -> None:
    st.markdown(f'<div class="si-footer">Soccer Intelligence · Version {escape(settings.APP_VERSION)}</div>',
                unsafe_allow_html=True)


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
