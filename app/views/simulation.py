"""Bereich Sensitivitätsanalyse (seit 0.12; Version 0.19: eine Schwelle je Richtung und Prognosewert; Dashboard-Briefing
6.4, KPI-Regelwerk 11).

Links Liga und Saison, rechts je KPI 02–09 zwei Zeilen (mehr / weniger), jede mit eigener Schwelle, Häufigkeit
(betroffene Spiele), Ergebnisqualität, Empfehlung und Prognosewert. Gerechnet wird in core/sensitivity.py mit den Fällen
aus core/simulation.py. Die Eingaben hier ändern nie die gültigen Schwellen (schwellen.toml). Haben die Ligen
unterschiedliche Schwellen, bleibt das Feld bei „Alle Ligen“ leer („je Liga“); eine eingetragene Zahl gilt dann für alle
Ligen. Darunter das Erklärfeld (Rahmen, Beispiel, aufklappbare Erklärungen) und der Schwellenvorschlag.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from html import escape

import streamlit as st

from core.kpis import de, de_signed
from core.matchday import season_short
from core.sensitivity import (
    DIRECTIONS, MEHR, RECOMMENDATIONS, RULES, TOO_FEW, Count, Limits, Quality, evaluate, limit, matchday_summary,
    proposal, proposal_toml,
)
from core.simulation import EVENT_TEXTS, default_choice, pct, running_seasons, season_choices
from core.top import TOP_KPIS
from state import get_active_leagues, get_closed_matchdays, get_database, get_simulation_cases, get_thresholds
from views import components as ui
from views.registry import PAGES

ALL = "Alle Ligen"
KEY = "sth_"                                  # Präfix der Schwellenfelder (Zurücksetzen löscht alle)
PARTS = DIRECTIONS                            # Zeilenfolge: mehr, weniger
LABEL = {"mehr": "↗ mehr", "weniger": "↘ weniger"}
RATIO = [1.15, 1.2, 1.2, 11.1]               # Zeile: KPI · Richtung · Abweichung in % · Zahlen
COLS = [7, 5.5, 8.5, 7.5, 7.5, 9, 7.5, 13, 16, 18.5]   # Breiten der Zahlenspalten in % (Summe 100)
STAGE_CSS = dict(zip(RECOMMENDATIONS, ("zw", "ng", "ok", "lt", "nr", "uk")))
R = RULES
MORE = "Mehr Details findest du unter der Tabelle."


def _n(x) -> str:
    """Zahl der Regeln für Texte: 5 statt 5.0, 10 bleibt 10, Komma statt Punkt.
    Nullen nur nach dem Komma streichen (Fehler beim Testen 0.19: aus 10 wurde 1, aus 60 wurde 6)."""
    if not isinstance(x, Decimal):
        return str(x)
    text = f"{x:f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text.replace(".", ",")


INFO = {
    "richtung": f"Mehr = mehr als im Ligaschnitt erwartet, weniger = weniger. Je Kennzahl gibt es zwei Zeilen. {MORE}",
    "schwelle": "Die Schwelle dieser Zeile: Auffällig ist ein Spiel, wenn die Erwartung um mehr als diesen Wert vom "
                "Ligaschnitt abweicht. Vorbelegt mit der gültigen Schwelle; eigene Werte sind blau. Leer = keine Schwelle "
                f"bzw. bei „Alle Ligen“ je Liga die eigene. {MORE}",
    "spiele": f"So viele frühere Spiele lagen über der Schwelle (ohne vorläufige Werte). {MORE}",
    "schnitt": f"So viele solche Spiele gab es im Schnitt je Spieltag. {MORE}",
    "abdeckung": f"An wie vielen von 100 Spieltagen es mindestens ein solches Spiel gab. {MORE}",
    "eingetroffen": "In so vielen dieser Spiele trat das Erwartete wirklich ein (mehr bzw. weniger als der Ligaschnitt "
                    f"vor dem Spiel). {MORE}",
    "treffer": f"Eingetroffen geteilt durch Anzahl Spiele: Wie oft lag die Auffälligkeit richtig? {MORE}",
    "vergleich": f"Wie oft dasselbe bei allen Spielen eintrat – der Normalfall. {MORE}",
    "mehrwert": f"Trefferquote minus Vergleichsgruppe: So viele Treffer mehr pro 100 Spiele. {MORE}",
    "spanne": "In diesem Bereich liegt der echte Mehrwert mit 95 % Sicherheit. Links der ungünstigste, rechts der "
              f"günstigste Fall. {MORE}",
    "empfehlung": "Urteil aus Anzahl, Mehrwert und Spanne: Zu wenige Daten, Negativ, Funktioniert, Funktioniert leicht, "
                  f"Keine relevante Verbesserung oder Noch unklar. {MORE}",
    "prognosewert": "Wie stark wir uns auf die Auffälligkeit verlassen können: hoch, mittel, gering oder „–“ (mit Grund). "
                    f"Nur bei „Funktioniert“ und stabil über die Saisons. {MORE}",
    "saisons": "Welche Saisons ausgewertet werden. Den Prognosewert gibt es nur bei mehreren Saisons. Die älteste Saison "
               "der Datenbank (Referenzsaison) liefert nur die Vorsaison und fehlt immer.",
}

CSS = """<style>
[data-testid="stColumn"]:has(.st-key-sens_settings) {position:sticky; top:4.2rem; align-self:flex-start;}
.st-key-sens_settings {border:1px solid #c3ccd8; border-radius:.5rem; padding:.6rem .7rem; background:#e3e8ef;}
.si-sim-banner {background:#fff3cd; border:1px solid #f2c230; border-radius:.5rem; padding:.6rem .9rem;
  margin:.2rem 0 1cm; color:#14213d;}
.si-warn {background:#fdf1e6; border:1px solid #f0a35a; border-radius:.5rem; padding:.45rem .8rem; margin:.2rem 0 .5rem;
  font-size:.85rem; color:#14213d;}
.si-meta {color:#5b6b84; font-size:.8rem; margin:0 0 .3rem;}
.si-note {color:#5b6b84; font-size:.8rem; margin:.3rem 0 0;}
.st-key-sens_head {position:sticky; top:3.75rem; z-index:30; background:#fff; padding-bottom:.15rem;}
.st-key-sens_head [data-testid="stHorizontalBlock"], [class*="st-key-sens_kpi_"] [data-testid="stHorizontalBlock"]
  {gap:.35rem; align-items:center;}
.st-key-sens_head [data-testid="stHorizontalBlock"] {align-items:stretch;}
.st-key-sens_head [data-testid="stColumn"] {overflow:visible;}
[class*="st-key-sens_kpi_"] {border-top:2px solid #c3ccd8; padding-top:.25rem;}
[class*="st-key-sens_kpi_"], [class*="st-key-sens_kpi_"] [data-testid="stVerticalBlock"] {gap:.15rem !important;}
[class*="st-key-sens_kpi_"] [data-testid="stMarkdownContainer"], .st-key-sens_head [data-testid="stMarkdownContainer"]
  {margin-bottom:0;}
[class*="st-key-sens_kpi_"] input {padding:.15rem .35rem; font-size:.85rem; font-variant-numeric:tabular-nums;}
[class*="st-key-sens_kpi_"] [data-testid="stNumberInputContainer"] {height:1.9rem;}
[class*="st-key-sens_kpi_"] [data-testid="stMarkdownContainer"] p, .st-key-sens_head [data-testid="stMarkdownContainer"] p
  {margin:0;}
[class*="st-key-sens_kpi_"] .stMarkdown, .st-key-sens_head .stMarkdown {margin-bottom:0;}
.si-kpi {font-size:.85rem; color:#14213d; line-height:1.2;} .si-kpi small {display:block; color:#5b6b84; font-size:.74rem;}
.si-lab {font-size:.8rem; color:#14213d; white-space:nowrap;} .si-lab.s {padding-left:.55rem;}
.si-lab.t {font-weight:700;} .si-lab.c {text-align:center;}
.si-perliga {font-size:.68rem; color:#5b6b84; line-height:1.15; margin:-.15rem 0 0 .2rem; white-space:nowrap; letter-spacing:-.01em;}
.si-h {background:#eef2f7; border:1px solid #d8e0eb; font-size:.72rem; font-weight:700; color:#14213d; text-align:center;
  line-height:1.15; display:flex; align-items:center; justify-content:center; padding:.15rem .2rem; box-sizing:border-box;}
.si-h.g {background:#dfe6ef; font-size:.76rem; height:1.6rem;} .si-h.l {height:2.7rem;} .si-h.full {height:4.35rem;}
.si-h.span {position:relative; z-index:2; width:calc(100% * 2.65 / 1.45 + .35rem);}
.si-h.blank {background:#dfe6ef; border-left:none;}
table.si-t {border-collapse:collapse; width:100%; margin:0 !important; table-layout:fixed; font-size:.82rem; color:#14213d;
  font-variant-numeric:tabular-nums;}
.si-t th {background:#eef2f7; border:1px solid #d8e0eb; padding:.15rem .25rem; font-size:.72rem; font-weight:700;
  text-align:center; line-height:1.15;}
.si-t th.g {background:#dfe6ef; font-size:.76rem; height:1.6rem;} .si-t tr.l th {height:2.7rem;}
.si-t td {border:1px solid #e3e9f1; padding:.25rem .3rem; text-align:right; white-space:nowrap; overflow:hidden;
  text-overflow:ellipsis;}
.si-t td.c {text-align:center; white-space:normal;} .si-t td.s {color:#5b6b84; font-size:.76rem;}
.si-t td.q, .si-t th.q {border-left:2px solid #c3ccd8;}
.si-t tr.str td {background:#fafbfd;}
.si-t tr.tot td {background:#f4f6f9; font-weight:700;} .si-t tr.grey td {color:#9aa6b8; background:#f7f8fa;}
.si-p {display:inline-block; border-radius:.25rem; padding:.02rem .35rem; font-size:.74rem; white-space:nowrap;}
.si-p.ok {background:#dcf3e5; color:#1f7a45; font-weight:700;} .si-p.lt {background:#fff1c2; color:#7a5a00;}
.si-p.nr {background:#eef0f3; color:#5b6b84;} .si-p.uk {background:#e3edfb; color:#1d5fb4;}
.si-p.ng {background:#fde8e8; color:#9b1c1c; font-weight:700;} .si-p.zw {background:#f1f3f6; color:#8a96a8;}
.si-i {position:relative; color:#4a90e2; cursor:help; font-weight:400;}
.si-i .tip {display:none; position:absolute; z-index:60; top:1.2rem; left:50%; transform:translateX(-50%); width:17rem;
  background:#fff; border:1px solid #c3ccd8; border-radius:.45rem; padding:.5rem .6rem; box-shadow:0 6px 18px rgba(20,33,61,.18);
  color:#14213d; font-weight:400; font-size:.78rem; line-height:1.35; text-align:left; white-space:normal;}
.si-i.r .tip {left:auto; right:-.3rem; transform:none;} .si-i.l .tip {left:-.3rem; transform:none;}
.si-i:hover .tip {display:block;}
.si-pw {display:inline-block; border-radius:.25rem; padding:.02rem .4rem; font-size:.74rem; font-weight:700; white-space:nowrap;}
.si-pw.hoch {background:#0f766e; color:#fff;} .si-pw.mittel {background:#8fd3cb; color:#0b4f4a;}
.si-pw.gering {background:#e3f4f2; color:#0b4f4a; border:1px solid #8fd3cb;}
.si-why {color:#8a96a8; font-size:.7rem; white-space:normal; line-height:1.15;}
.si-t td.off {background:#f1f3f6; color:#9aa6b8;}
.si-box {border:1px solid #c3ccd8; border-radius:.5rem; padding:.7rem .9rem; background:#f8fafc; margin:.6rem 0 .4rem;
  color:#14213d; font-size:.9rem;}
.si-box h4 {margin:0 0 .3rem; font-size:1rem;} .si-box ol {margin:.3rem 0 0 1.1rem; padding:0;} .si-box li {margin:.25rem 0;}
</style>"""


def info(key: str, side: str = "") -> str:
    """ⓘ mit eigenem Fenster beim Darüberfahren (Browser-Tooltips erscheinen in Streamlit nicht)."""
    return f'<span class="si-i {side}">ⓘ<span class="tip">{escape(INFO[key])}</span></span>'


def pill(stage: str) -> str:
    return f'<span class="si-p {STAGE_CSS[stage]}">{escape(stage)}</span>'


def num(n: int) -> str:
    return f"{n:,}".replace(",", "'")


def colgroup() -> str:
    return "<colgroup>" + "".join(f'<col style="width:{w}%">' for w in COLS) + "</colgroup>"


# --- Einstellungen (links) -----------------------------------------------------------------------------------

def settings_panel(cases) -> dict:
    with st.container(key="sens_settings"):
        st.markdown("**Einstellungen**")
        league = st.selectbox("Liga", [ALL, *[lg.name for lg in get_active_leagues()]], key="sens_liga")
        choices = season_choices(cases)
        labels = list(choices)
        default = default_choice(choices)
        label = st.selectbox("Saison", labels, index=labels.index(default) if default else 0, key="sens_saison",
                             help=INFO["saisons"])
    seasons = list(choices.get(label, []))
    return {"league": league, "seasons": seasons, "running": bool(set(seasons) & set(running_seasons(cases)))}


def _reset() -> None:
    for key in [k for k in st.session_state if str(k).startswith(KEY)]:
        del st.session_state[key]


# --- Schwellen: gültige Werte, Eingaben, wirksame Werte je Liga ----------------------------------------------

def valid_limits(league: str) -> dict[str, dict[str, Limits]]:
    """Gültige Schwellen aus schwellen.toml je KPI und Liga der Auswahl (bei „Alle Ligen“ alle aktiven Ligen)."""
    config = get_thresholds()
    leagues = [lg.name for lg in get_active_leagues()] if league == ALL else [league]
    return {kpi: {lg: Limits.from_thresholds(config.get(lg, kpi)) for lg in leagues} for kpi in TOP_KPIS}


def defaults(per_league: dict[str, Limits]) -> dict[str, float | None]:
    """Vorbelegung je Feld: der gültige Wert, wenn er in allen Ligen gleich ist, sonst leer („je Liga“)."""
    out = {}
    for part in PARTS:
        values = {x.get(part) for x in per_league.values()}
        value = values.pop() if len(values) == 1 else None
        out[part] = float(value) if value is not None else None
    return out


def placeholder(per_league: dict[str, Limits], part: str) -> str:
    values = {x.get(part) for x in per_league.values()}
    return "keine" if values == {None} else "je Liga"


SHORT = {"Bundesliga": "BL", "Premier League": "PL", "Serie A": "SA", "LaLiga": "LL"}


def per_league_hint(per_league: dict[str, Limits], part: str) -> str:
    """Bei „Alle Ligen“ mit verschiedenen Schwellen: die gültigen Werte je Liga, z. B. „PL 10 · SA 15“ (0.19.1)."""
    values = {lg: x.get(part) for lg, x in per_league.items()}
    if len(set(values.values())) < 2:
        return ""
    return " · ".join(f"{SHORT.get(lg, lg[:3])} {_n(v)}" for lg, v in values.items() if v is not None)


def follow_league(league: str) -> None:
    """Beim Wechsel der Liga: unveränderte Felder (noch der gültige Wert der bisherigen Auswahl) zeigen den gültigen Wert
    der neuen Auswahl. Eigene Eingaben bleiben stehen."""
    state, before = st.session_state, st.session_state.get("sens_prev_liga")
    state["sens_prev_liga"] = league
    if before is None or before == league:
        return
    old, new = valid_limits(before), valid_limits(league)
    for kpi in TOP_KPIS:
        was, now = defaults(old[kpi]), defaults(new[kpi])
        for part in PARTS:
            key = f"{KEY}{kpi}_{part}"
            if key in state and was[part] != now[part] and state[key] == was[part]:
                state[key] = now[part]      # zuweisen statt löschen: sonst behält der Browser das leere Feld (0.19.1)


def threshold_input(kpi: str, part: str, default: float | None, hint: str) -> float | None:
    """Ein Schwellenfeld (Betrag 0 bis 999, eine Nachkommastelle); leer = keine Schwelle bzw. je Liga."""
    key = f"{KEY}{kpi}_{part}"
    start = {} if key in st.session_state else {"value": default}       # Wert sonst aus der Sitzung
    return st.number_input(f"{kpi} {part}", min_value=0.0, max_value=999.0, step=0.1, format="%.1f", key=key,
                           placeholder=hint, label_visibility="collapsed", **start)


def effective(values: dict[str, float | None], per_league: dict[str, Limits]) -> Limits | dict[str, Limits]:
    """Wirksame Schwellen: eingetragene Zahl für alle Ligen, leeres Feld = gültiger Wert der Liga (auch „keine“).
    Gleich in allen Ligen -> ein Limits, sonst je Liga."""
    out = {}
    for lg, valid in per_league.items():
        v = {p: limit(values[p]) if values[p] is not None else valid.get(p) for p in PARTS}
        out[lg] = Limits(v[MEHR], v["weniger"])
    distinct = set(out.values())
    return distinct.pop() if len(distinct) == 1 else out


# --- Tabelle ---------------------------------------------------------------------------------------------------

def head() -> None:
    """Kopfzeile über allen KPIs (bleibt beim Blättern oben stehen)."""
    with st.container(key="sens_head"):
        c = st.columns(RATIO, vertical_alignment="top")
        c[0].markdown('<div class="si-h full">KPI</div>', unsafe_allow_html=True)
        c[1].markdown('<div class="si-h g span">Schwelle</div>'
                      f'<div class="si-h l">Richtung&nbsp;{info("richtung", "l")}</div>', unsafe_allow_html=True)
        c[2].markdown('<div class="si-h g blank"></div>'
                      f'<div class="si-h l">Abweichung in %&nbsp;{info("schwelle", "l")}</div>', unsafe_allow_html=True)
        c[3].markdown(
            f'<table class="si-t">{colgroup()}<tr><th colspan=3 class=g>Betroffene Spiele</th>'
            '<th colspan=7 class="g q">Ergebnisqualität und Prognosewert</th></tr><tr class=l>'
            f'<th>Anzahl Spiele {info("spiele")}</th><th>Ø/ST {info("schnitt")}</th>'
            f'<th>Spieltags&shy;abdeckung {info("abdeckung")}</th><th class=q>Anzahl eingetroffen {info("eingetroffen")}</th>'
            f'<th>Treffer&shy;quote {info("treffer")}</th><th>Vergleichs&shy;gruppe (alle Spiele) {info("vergleich")}</th>'
            f'<th>Mehrwert in Pp. {info("mehrwert", "r")}</th><th>Spanne (Wilson 95 %) {info("spanne", "r")}</th>'
            f'<th>Empfehlung {info("empfehlung", "r")}</th><th>Prognose&shy;wert {info("prognosewert", "r")}</th></tr>'
            '</table>', unsafe_allow_html=True)


def _count_cells(c: Count) -> str:
    per = pct(c.per_matchday) if c.per_matchday is not None else "–"
    cov = f"{pct(c.coverage)} %" if c.coverage is not None else "–"
    return f"<td>{num(c.count)}</td><td>{per}</td><td>{cov}</td>"


def prognosis_cell(q: Quality, one_season: bool) -> str:
    if one_season:
        return '<td class="c off">–<div class="si-why">nur bei mehreren Saisons</div></td>'
    if q.prognosewert:
        return f'<td class=c><span class="si-pw {q.prognosewert}">{q.prognosewert}</span></td>'
    return f'<td class=c>–<div class="si-why">{escape(q.reason)}</div></td>'


def line_html(c: Count, q: Quality, one_season: bool, no_threshold: bool) -> str:
    """Eine Zeile: betroffene Spiele, Ergebnisqualität, Empfehlung und Prognosewert mit derselben Schwelle."""
    if no_threshold:
        cells = ("<td>–</td><td>–</td><td>–</td><td class=q>–</td><td>–</td>"
                 + (f"<td>{pct(q.base)} %</td>" if q.base is not None else "<td>–</td>")
                 + '<td>–</td><td class=s>–</td><td class=c colspan=2><span class="si-why">keine Schwelle</span></td>')
        return f'<table class="si-t">{colgroup()}<tr class="grey">{cells}</tr></table>'
    if q.rate is None:                                     # niemand über der Schwelle: nur die Vergleichsgruppe
        base = f"{pct(q.base)} %" if q.base is not None else "–"
        rest = f"<td>–</td><td>{base}</td><td>–</td><td class=s>–</td>"
    else:
        rest = (f"<td>{pct(q.rate)} %</td><td>{pct(q.base)} %</td><td><b>{pct(q.gain, True)}</b></td>"
                f"<td class=s>{pct(q.low, True)} bis {pct(q.high, True)}</td>")
    css = "grey" if q.recommendation == TOO_FEW else ""
    cells = (_count_cells(c) + f"<td class=q>{num(q.hits)}</td>" + rest
             + f"<td class=c>{pill(q.recommendation)}</td>" + prognosis_cell(q, one_season))
    return f'<table class="si-t">{colgroup()}<tr class="{css}">{cells}</tr></table>'


def kpi_block(kpi: str, per_league: dict[str, Limits], result_for, one_season: bool) -> dict[str, float | None]:
    """Zwei Zeilen (mehr, weniger) für einen KPI; gibt die Eingaben zurück. result_for(limits) rechnet den KPI aus."""
    number, _, title = TOP_KPIS[kpi].partition(" – ")
    start = defaults(per_league)
    with st.container(key=f"sens_kpi_{kpi}"):
        values, slots = {}, {}
        for part in PARTS:
            c = st.columns(RATIO, vertical_alignment="center")
            if part == MEHR:
                c[0].markdown(f'<div class="si-kpi"><b>{escape(number)}</b><small>{escape(title)}</small></div>',
                              unsafe_allow_html=True)
            c[1].markdown(f'<div class="si-lab">{LABEL[part]}</div>', unsafe_allow_html=True)
            with c[2]:
                values[part] = threshold_input(kpi, part, start[part], placeholder(per_league, part))
                hint = per_league_hint(per_league, part) if values[part] is None else ""
                if hint:
                    st.markdown(f'<div class="si-perliga">{escape(hint)}</div>', unsafe_allow_html=True)
            slots[part] = c[3]
        lim = effective(values, per_league)
        r = result_for(lim)
        for part in PARTS:
            none = (lim.get(part) is None) if isinstance(lim, Limits) else all(x.get(part) is None for x in lim.values())
            slots[part].markdown(line_html(r.counts[part], r.quality[part], one_season, none), unsafe_allow_html=True)
    return values


def own_values_css(chosen: dict[str, dict[str, float | None]], starts: dict[str, dict[str, float | None]]) -> str:
    """Eigene Werte blau (abweichend von schwellen.toml; bei „je Liga“ jede eingetragene Zahl)."""
    keys = [f".st-key-{KEY}{kpi}_{part} input" for kpi, values in chosen.items() for part, v in values.items()
            if v is not None and (starts[kpi][part] is None or limit(v) != limit(starts[kpi][part]))]
    return f"<style>{', '.join(keys)} {{color:#1d5fb4; font-weight:700;}}</style>" if keys else ""


# --- Erklärfeld (Spezifikation 18.11.2026, Abschnitt 4.2) -------------------------------------------------------------

def _example() -> dict | None:
    """Beispiel aus der gültigen Schwellendatei: Bundesliga, Schüsse aufs Tor, weniger. Werte mit zwei Nachkommastellen
    wie in der Tabelle, damit die Rechnung aufgeht (0.19.1: vorher 63 − 52 = +12 mit gerundeten Werten)."""
    config = get_thresholds()
    s = config.get("Bundesliga", "kpi09").negativ
    if s is None or s.spiele is None or s.trefferquote is None or s.vergleichsgruppe is None or s.mehrwert is None \
            or s.spanne_links is None or s.spanne_rechts is None:
        return None
    hits = round(s.spiele * float(s.trefferquote) / 100)
    seasons = config.saisons.replace("/20", "/").replace("-", "–") if config.saisons else ""
    return {"t": _n(s.schwelle), "n": s.spiele, "h": hits, "q": de(s.trefferquote), "b": de(s.vergleichsgruppe),
            "g": de_signed(s.mehrwert), "g0": round(float(s.mehrwert)), "lo": de_signed(s.spanne_links),
            "lo0": round(float(s.spanne_links)), "hi": de_signed(s.spanne_rechts), "st": s.saisons_positiv or "",
            "pw": s.prognosewert, "seasons": seasons}


def explanation() -> None:
    """Rahmen und Einstieg (immer sichtbar), danach aufklappbare Erklärungen je Spalte (Wortlaut Carsten 18.11.2026 mit
    Korrekturen, Version 0.19.1)."""
    st.markdown(
        "<div class='si-box'><h4>Wie kommen die Werte in dieser Tabelle zustande?</h4>Wir schauen in die Vergangenheit: "
        "Wie oft ist eingetroffen, was eine Auffälligkeit angekündigt hat? Die Tabelle zeigt das Spalte für Spalte. Am "
        "Ende steht der <b>Prognosewert</b>. Er zeigt, wie zuverlässig sich eine Auffälligkeit in der Vergangenheit "
        "bestätigt hat. Die folgenden Erklärungen beschreiben, wie die einzelnen Werte berechnet werden und welche "
        "Aussagekraft sie haben.</div>", unsafe_allow_html=True)
    e = _example()
    if e:
        st.markdown(f"""<div class='si-box'><h4>Beispiel: Bundesliga, Schüsse aufs Tor, „weniger“</h4>
<small>Stand Saisons {escape(e["seasons"])}</small><ol>
<li><b>Abweichung in %:</b> Für jedes Spiel berechnen wir vor dem Anpfiff, wie viele Schüsse aufs Tor zu erwarten sind.
Grundlage dafür sind die letzten 10 Spiele beider Teams. Diesen Wert vergleichen wir mit dem Ligaschnitt der letzten 20
Spieltage. Liegt die Erwartung mehr als <b>{e["t"]} %</b> darunter (die <b>Schwelle</b> dieser Zeile), zählt das Spiel als
auffällig. Jede Liga hat für jede Kennzahl und Richtung eine eigene Schwelle.</li>
<li><b>Trefferquote:</b> In {e["n"]} früheren Spielen lag die Erwartung mehr als {e["t"]} % unter dem Ligaschnitt.
Anschliessend haben wir geprüft, was im Spiel tatsächlich passiert ist: In {e["h"]} dieser {e["n"]} Spiele fielen weniger
Schüsse aufs Tor als im Ligaschnitt. Die Auffälligkeit hat sich somit in <b>{e["q"]} %</b> der Fälle bestätigt.</li>
<li><b>Vergleichsgruppe und Mehrwert in Pp.:</b> Bei <i>allen</i> Spielen – auch denen ohne Auffälligkeit – fielen in
{e["b"]} % der Fälle weniger Schüsse aufs Tor als im Ligaschnitt. Der <b>Mehrwert in Pp.</b> ergibt sich aus der
Differenz: {e["q"]} − {e["b"]} = <b>{e["g"]} Prozentpunkte</b>. Die Auffälligkeit hat sich damit in rund {e["g0"]} von 100
Spielen häufiger bestätigt als im Durchschnitt aller Spiele.</li>
<li><b>Spanne (Wilson 95 %):</b> Auch ein guter Wert kann durch Zufall zustande kommen. Die Spanne zeigt, wie stark der
berechnete Mehrwert statistisch schwanken kann. Hier liegt er mit 95 % Sicherheit zwischen <b>{e["lo"]} und {e["hi"]}
Pp.</b> Selbst am unteren Ende der Spanne bleiben rund {e["lo0"]} Treffer mehr pro 100 Spiele.</li>
<li><b>Empfehlung:</b> Dieses Feld fasst Anzahl Spiele, Mehrwert und Spanne zu einem Urteil zusammen. Es beantwortet die
Frage: Gibt es einen statistisch relevanten Vorteil? Die möglichen Urteile sind <i>Zu wenige Daten, Negativ,
Funktioniert, Funktioniert leicht, Keine relevante Verbesserung</i> und <i>Noch unklar</i>. Hier lautet das Ergebnis:
<b>Funktioniert</b>. Wie die einzelnen Urteile berechnet werden, steht weiter unten unter „Empfehlung“.</li>
<li><b>Prognosewert:</b> Er zeigt, wie zuverlässig sich eine Auffälligkeit in der Vergangenheit bestätigt hat:
<b>hoch</b>, <b>mittel</b>, <b>gering</b> oder <b>–</b> (nicht verlässlich genug). Ein Prognosewert wird nur vergeben, wenn
die Empfehlung „Funktioniert“ lautet und der Mehrwert auch über mehrere Saisons hinweg stabil positiv war (hier in
{escape(e["st"]).replace("/", " von ")} Saisons). Im Beispiel ergeben {e["q"]} % Trefferquote und {e["g"]} Pp. den
Prognosewert <b>{e["pw"]}</b>. Die genauen Regeln stehen weiter unten unter „Prognosewert“.</li></ol></div>""",
                    unsafe_allow_html=True)
    with st.expander("Abweichung in % und Schwelle"):
        st.markdown(f"""**Abweichung in %:** Wie stark weicht die Erwartung für ein Spiel vom Ligaschnitt ab? Die Erwartung wird anhand der letzten 10 Spiele beider Teams berechnet (Datenstand höchstens zwei Tage vor dem Anpfiff). Als Vergleich dient der Ligaschnitt der 20 vorherigen Spieltage. Beispiel: Erwartung 7,8 Schüsse, Ligaschnitt 9,0 Schüsse → −13,3 %.

**Schwelle:** Sie legt fest, ab welcher Abweichung ein Spiel als auffällig gilt. Entscheidend ist, dass die Abweichung die Schwelle überschreitet. Bei einer Schwelle von 10 % zählt deshalb −10,01 %, −10,00 % hingegen nicht.

**Es gibt keine einheitliche Schwelle.** Jede Liga hat je Kennzahl und Richtung (*mehr* / *weniger*) höchstens eine eigene Schwelle. Diese wird nach einem festen Verfahren bestimmt:
1. Wir probieren {", ".join(_n(c) for c in R.candidates[:-1])} und {_n(R.candidates[-1])} % aus.
2. In Frage kommen nur Schwellen mit der Empfehlung **Funktioniert**, deren Vorteil zudem **stabil** ist (siehe „Prognosewert“).
3. Davon nehmen wir die mit dem **besten Prognosewert**; bei Gleichstand die mit **mehr Spielen**, damit Auffälligkeiten nicht zu selten werden.
4. Gibt es keine passende Schwelle, wird diese Kennzahl in der jeweiligen Liga und Richtung nicht als Auffälligkeit ausgewiesen.

Die gültigen Schwellen werden einmal pro Saison nach Saisonende neu bestimmt und freigegeben (Knopf „Schwellenvorschlag berechnen“ unten). In der Tabelle kannst du andere Werte ausprobieren; was von der gültigen Schwelle abweicht, ist blau. Bei „Alle Ligen“ zählt jede Liga mit ihrer eigenen Schwelle, solange das Feld leer ist; die Schwellen der Ligen stehen klein darunter.""")
    with st.expander("Anzahl Spiele, Ø pro Spieltag, Spieltagsabdeckung"):
        st.markdown("**Anzahl Spiele:** So viele Spiele lagen über der festgelegten Schwelle. Vorläufige Werte (z. B. bei "
                    "Aufsteigern) werden nicht berücksichtigt.\n\n"
                    "**Ø pro Spieltag:** So viele auffällige Spiele gab es durchschnittlich pro Spieltag. Ein Wert von "
                    "0,50 bedeutet beispielsweise, dass es im Schnitt an jedem zweiten Spieltag ein auffälliges Spiel "
                    "gab.\n\n"
                    "**Spieltagsabdeckung:** An wie vielen von 100 Spieltagen es mindestens ein auffälliges Spiel gab.")
    with st.expander("Anzahl eingetroffen und Trefferquote"):
        st.markdown("**Eingetroffen** bedeutet: Der tatsächliche Wert im Spiel lag über (*mehr*) bzw. unter (*weniger*) "
                    "dem Ligaschnitt, der bereits **vor** dem Spiel galt. Lag der Wert genau auf dem Ligaschnitt, zählt "
                    "das nicht als Treffer.\n\n"
                    + "\n".join(f"- {TOP_KPIS[k].partition(' – ')[2]}: {t}" for k, t in EVENT_TEXTS.items())
                    + "\n\n**Trefferquote** = eingetroffen ÷ Spiele mit bekanntem Ergebnis.")
    with st.expander("Vergleichsgruppe (alle Spiele) und Mehrwert in Pp."):
        st.markdown("**Vergleichsgruppe:** Sie zeigt, wie oft dasselbe Ergebnis bei **allen** Spielen eintrat – "
                    "unabhängig davon, ob eine Auffälligkeit vorlag oder nicht. Dieser Vergleich ist wichtig, weil manche "
                    "Ergebnisse ohnehin häufig vorkommen: Eine Trefferquote von 60 % ist wenig aussagekräftig, wenn das "
                    "Ergebnis auch bei 60 % aller Spiele eintritt.\n\n"
                    "**Mehrwert in Pp.** = Trefferquote − Vergleichsgruppe, angegeben in Prozentpunkten. +12 Pp. "
                    "bedeutet: Das erwartete Ergebnis trat bei Spielen mit Auffälligkeit 12 Prozentpunkte häufiger ein "
                    "als bei allen Spielen.")
    with st.expander("Spanne (Wilson 95 %)"):
        st.markdown("Wirfst du eine Münze zehnmal und es kommt siebenmal Kopf, bedeutet das noch nicht, dass die Münze "
                    "gezinkt ist. Sieben Treffer können auch durch Zufall entstehen. Genauso kann ein hoher Mehrwert bei "
                    "wenigen Spielen Zufall sein.\n\n"
                    "Die **Spanne** (berechnet mit dem Wilson-Verfahren) zeigt, wie genau sich der Mehrwert anhand der "
                    "vorhandenen Daten einschätzen lässt: Mit 95 % Sicherheit liegt der echte Mehrwert in diesem "
                    "Bereich. Je mehr Spiele ausgewertet werden, desto genauer wird die Einschätzung und desto enger "
                    "wird die Spanne.\n"
                    "- **Gutes Beispiel:** Mehrwert +12 Pp., Spanne **+5 bis +18 Pp.** (227 Spiele). Selbst im "
                    "ungünstigsten Fall bleiben +5 Pp. – der Vorteil ist kaum Zufall.\n"
                    "- **Schwaches Beispiel:** Mehrwert +12 Pp., Spanne **−4 bis +30 Pp.** (nur 35 Spiele). Der Mehrwert "
                    "sieht gleich gut aus, aber im ungünstigsten Fall wäre die Auffälligkeit sogar schlechter als der "
                    "Normalfall – das kann reines Glück sein.\n\n"
                    "**Linker (unterer) Wert** = ungünstigster Fall, **rechter (oberer) Wert** = günstigster Fall. Für "
                    "unsere Urteile zählt vor allem der linke Wert. (Fachlich: Newcombe-Methode aus zwei "
                    "Wilson-Intervallen.)")
    with st.expander("Empfehlung"):
        st.markdown(f"""Die Empfehlung fasst Anzahl Spiele, Mehrwert und Spanne zu einem Urteil zusammen. Die sechs möglichen Stufen werden von oben nach unten geprüft. Sobald eine Stufe zutrifft, wird dieses Urteil vergeben:
1. **Zu wenige Daten:** Weniger als {R.min_cases} Spiele. Die Datenbasis ist zu klein, um eine verlässliche Aussage zu treffen – ähnlich wie fünf Münzwürfe noch keinen belastbaren Schluss zulassen.
2. **Negativ:** Mindestens {R.min_cases} Spiele, und selbst der rechte (obere) Wert der Spanne liegt unter 0. Die Auffälligkeit schneidet damit schlechter ab als die Vergleichsgruppe.
3. **Funktioniert:** Mindestens {R.min_cases} Spiele, Mehrwert mindestens +{_n(R.works_gain)} Pp. **und** der linke Wert der Spanne liegt über +{_n(R.works_low)} Pp. Auch am unteren Ende der Spanne bleibt somit ein Mehrwert von mehr als {_n(R.works_low)} Prozentpunkten.
4. **Funktioniert leicht:** Mindestens {R.min_cases} Spiele, Mehrwert mindestens +{_n(R.light_gain)} Pp. und der linke Wert liegt nicht unter −{_n(-R.light_floor)} Pp. Es gibt Hinweise auf einen positiven Mehrwert, dieser ist statistisch aber weniger eindeutig.
5. **Keine relevante Verbesserung:** Mindestens {R.min_cases} Spiele, und selbst der rechte (obere) Wert der Spanne liegt unter +{_n(R.relevant_high)} Pp. Ein relevanter Mehrwert ist damit nicht erkennbar.
6. **Noch unklar:** Mindestens {R.min_cases} Spiele, aber keine der anderen Stufen trifft zu. Die Daten reichen noch nicht für eine eindeutige Bewertung; häufig ist die Spanne noch zu gross.

Für den Prognosewert zählt nur „Funktioniert“. Die anderen Stufen zeigen, warum eine Zeile nicht reicht.""")
    with st.expander("Prognosewert"):
        a, b = R.stable_share
        share = "zwei Dritteln" if (a, b) == (2, 3) else f"{a}/{b}"
        st.markdown(f"""Der Prognosewert zeigt, wie zuverlässig sich eine Auffälligkeit in früheren Spielen bestätigt hat. Er bestimmt auch die Reihenfolge der **Top Anomalien**: zuerst hoch, dann mittel, dann gering. Innerhalb jeder Stufe entscheidet die Grösse der Abweichung. Pro Liga werden in der Regel höchstens zwei Spiele berücksichtigt.

**Voraussetzungen:**
1. Die Empfehlung lautet **Funktioniert**.
2. **Stabil:** Der Mehrwert war in mindestens **{share} der ausgewerteten Saisons** jeweils positiv (bei 7 Saisons also in mindestens {R.stable_needed(7)}). Dadurch werden Auffälligkeiten ausgeschlossen, deren positiver Gesamtwert hauptsächlich durch einzelne besonders gute Saisons zustande kommt.

**Die vier Stufen:**
- **hoch:** Trefferquote **ab {_n(R.high_rate)} %** und Mehrwert **ab +{_n(R.high_gain)} Pp.** Das Ergebnis trat also in mindestens 6 von 10 Fällen ein und lag gleichzeitig deutlich über dem Vergleichswert. Der zusätzliche Mindestwert von +{_n(R.high_gain)} Pp. verhindert, dass eine Kennzahl allein aufgrund einer ohnehin hohen Grundhäufigkeit als „hoch“ eingestuft wird (z. B. „wenig Tore in der 1. Halbzeit“: schon bei allen Spielen rund 64 %).
- **mittel:** Trefferquote **ab {_n(R.medium_rate)} %** (oder ab {_n(R.high_rate)} %, wenn der Mehrwert unter +{_n(R.high_gain)} Pp. liegt).
- **gering:** Trefferquote **ab {_n(R.low_rate)} %**. Die Auffälligkeit bestätigt sich mindestens in jedem zweiten Fall. Der Vorteil gegenüber dem Vergleichswert ist aber geringer.
- **–:** Die Voraussetzungen sind nicht erfüllt oder die Trefferquote liegt unter {_n(R.low_rate)} %. Der Grund wird grau daneben angezeigt. Mit einer solchen Schwelle wird die Kennzahl nirgends als auffällig ausgewiesen – weder in den Top Anomalien noch auf den Ligaseiten.

Bei einer **einzelnen Saison** lässt sich die Stabilität nicht prüfen: Die Spalte ist dann ausgegraut mit „–“ und dem Hinweis „nur bei mehreren Saisons“.

**Wichtig:** Der Prognosewert ist **keine Wahrscheinlichkeit für das nächste Spiel**, sondern zeigt die Ergebnisse vergleichbarer Auffälligkeiten aus der Vergangenheit. Da wir aus mehreren möglichen Schwellen die jeweils beste auswählen, können die historischen Werte etwas zu positiv ausfallen. In einer neuen Saison kann die Trefferquote deshalb einige Prozentpunkte tiefer liegen. Prüfen kannst du das, indem du oben nur die letzte Saison auswählst und die Trefferquote vergleichst.""")
    with st.expander("Grundlage der Berechnung"):
        st.markdown("Jedes frühere Spiel wird so berechnet, als wäre es noch nicht gespielt – nur mit Daten, die vor dem "
                    "Anpfiff bekannt waren. Ausgewertet werden die gewählten Saisons, nur abgeschlossene Spieltage. Nicht "
                    "verwendet werden die älteste Saison der Datenbank (sie liefert nur die Vorsaison-Werte) und "
                    "vorläufige Werte (Teams mit weniger als 10 Spielen, z. B. Aufsteiger).")


# --- Schwellenvorschlag ----------------------------------------------------------------------------------------------

def proposal_section(cases, matchdays_all, seasons: list[str]) -> None:
    """Vorschlag aller Kombinationen Liga × KPI × Richtung mit den gewählten Saisons (nur Anzeige und Download)."""
    st.markdown("#### Schwellenvorschlag")
    st.markdown("<p class='si-note'>Rechnet für alle Ligen, Kennzahlen und Richtungen die Schwelle nach der festen Regel "
                "(siehe „Abweichung in % und Schwelle“) mit den links gewählten Saisons. Für die gültige Datei: einmal "
                "pro Saison nach Saisonende mit „Alle Saisons“. Nichts wird gespeichert – die Übernahme erfolgt nach "
                "Freigabe über GitHub.</p>", unsafe_allow_html=True)
    if not st.button("Schwellenvorschlag berechnen", key="sens_proposal"):
        return
    leagues = [lg.name for lg in get_active_leagues()]
    with st.spinner("Rechne alle Kombinationen …"):
        df = proposal(cases[cases["season"].isin(seasons)], matchdays_all[matchdays_all["season"].isin(seasons)],
                      leagues, list(TOP_KPIS))
    if df.empty:
        st.info("Keine Kombination erfüllt die Bedingungen.")
        return
    show = df.assign(KPI=df["kpi"].map(TOP_KPIS), Stabil=df["saisons_positiv"].astype(str) + "/" + df["saisons"].astype(str))
    show = show[["liga", "KPI", "richtung", "schwelle", "prognosewert", "spiele", "trefferquote", "vergleichsgruppe",
                 "mehrwert", "spanne_links", "Stabil"]]
    st.dataframe(show.round(2), hide_index=True, use_container_width=True)
    span = f"{seasons[0]}-{seasons[-1]}" if seasons else ""
    st.download_button("Vorschlag als schwellen.toml herunterladen", proposal_toml(df, span, date.today().isoformat()),
                       file_name="schwellen_vorschlag.toml", mime="text/plain", key="sens_proposal_dl")


# --- Seite ---------------------------------------------------------------------------------------------------------

def render() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    ui.header(subtitle="Sensitivitätsanalyse")
    st.markdown("<div class='si-sim-banner'>Die hier angepassten Schwellen dienen der Simulation und haben keinen Einfluss "
                "auf die anderen Dashboard-Tabs. Es gelten weiterhin die Werte in der Datei <code>schwellen.toml</code>."
                "</div>", unsafe_allow_html=True)
    if get_database().has_errors:
        ui.blocked_notice(True, False, PAGES.get("datenqualitaet"))
        ui.footer()
        return
    cases = get_simulation_cases()
    if cases.empty:
        st.info("Keine Spiele für die Sensitivitätsanalyse vorhanden. Ausgewertet werden alle Saisons ausser der ältesten "
                "(Referenzsaison); enthält die Datenbank nur eine Saison, gibt es nichts auszuwerten.")
        ui.footer()
        return

    left, right = st.columns([0.9, 3.7], gap="medium")
    with left:
        sel = settings_panel(cases)
    with right:
        chosen = cases[cases["season"].isin(sel["seasons"])]
        all_matchdays = get_closed_matchdays()
        matchdays = all_matchdays[all_matchdays["season"].isin(sel["seasons"])]
        if sel["league"] != ALL:
            chosen = chosen[chosen["league"] == sel["league"]]
            matchdays = matchdays[matchdays["league"] == sel["league"]]
        per_league = matchday_summary(matchdays)
        games = chosen[["league", "game"]].drop_duplicates().shape[0]
        seasons = ", ".join(season_short(s) for s in sel["seasons"])
        st.markdown(f"<p class='si-meta'>Grundlage: {num(games)} Spiele · {escape(sel['league'])} · Saisons {seasons} · "
                    f"{num(len(matchdays))} abgeschlossene Spieltage · ohne vorläufige Werte</p>", unsafe_allow_html=True)
        if sel["league"] == ALL:
            detail = ", ".join(f"{escape(lg)} {num(n)}" for lg, n in per_league.items())
            st.markdown(f"<div class='si-warn'>⚠ Alle Ligen: Die Ligen haben unterschiedlich viele Spieltage (Bundesliga "
                        f"34, andere 38 je Saison; in der laufenden Saison unterschiedlich weit). Gezählt wird je Liga: "
                        f"{num(len(matchdays))} abgeschlossene Spieltage ({detail}).</div>", unsafe_allow_html=True)
        st.button("↺ Auf gültige Schwellen zurücksetzen", on_click=_reset, key="sens_reset")
        follow_league(sel["league"])
        valid = valid_limits(sel["league"])
        one_season = len(sel["seasons"]) < 2
        head()
        chosen_values = {}
        for kpi in TOP_KPIS:
            chosen_values[kpi] = kpi_block(kpi, valid[kpi],
                                           lambda lim, k=kpi: evaluate(chosen, matchdays, {k: lim})[0], one_season)
        st.markdown(own_values_css(chosen_values, {k: defaults(v) for k, v in valid.items()}), unsafe_allow_html=True)
        st.markdown("<p class='si-note'>Gezählt wird, was <b>über</b> der Schwelle liegt: Bei 15 % zählt +15,00 % nicht, "
                    "+15,01 % schon. Blau = abweichend von schwellen.toml. Unter 50 Spielen ist die Zeile grau. "
                    "Leeres Feld: keine Schwelle („keine“) bzw. bei „Alle Ligen“ je Liga die gültige („je Liga“).</p>",
                    unsafe_allow_html=True)
        explanation()
        proposal_section(cases, all_matchdays, sel["seasons"])
    ui.footer()
