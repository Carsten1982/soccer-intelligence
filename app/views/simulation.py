"""Bereich Sensitivitätsanalyse (Version 0.12; seit 0.13 Designentwurf C vom 14.11.2026, Dashboard-Briefing 6.4).

Links Liga und Saison, rechts eine Tabelle mit vier Zeilen je KPI 02–09: leicht positiv, stark positiv, leicht
negativ, stark negativ, jede mit eigener Schwelle, Häufigkeit (betroffene Spiele) und Ergebnisqualität (Prognosewert),
dazu eine Zeile Total. Gerechnet wird in core/sensitivity.py mit den Fällen aus core/simulation.py. Die Eingaben hier
ändern nie die gültigen Schwellen (schwellen.toml). Hat ein KPI je Liga eigene Schwellen (KPI 03), bleibt das Feld bei
„Alle Ligen“ leer („je Liga“); eine eingetragene Zahl gilt dann für alle Ligen.
"""

from __future__ import annotations

from html import escape

import streamlit as st

from core.matchday import season_short
from core.sensitivity import (
    NEG, POS, RECOMMENDATIONS, TOO_FEW, TOTAL, Count, KpiSensitivity, Limits, Quality, evaluate, limit, matchday_summary,
)
from core.simulation import DEFINITION_CHANGES, EVENT_TEXTS, default_choice, pct, running_seasons, season_choices
from core.top import TOP_KPIS
from state import get_active_leagues, get_closed_matchdays, get_database, get_simulation_cases, get_thresholds
from views import components as ui
from views.registry import PAGES

ALL = "Alle Ligen"
KEY = "sth_"                                  # Präfix der Schwellenfelder (Zurücksetzen löscht alle)
PARTS = ("lp", "sp", "ln", "sn")              # Zeilenfolge: leicht positiv, stark positiv, leicht negativ, stark negativ
ATTR = {"lp": "light_pos", "sp": "strong_pos", "ln": "light_neg", "sn": "strong_neg"}
LABEL = {"lp": "↗ Leicht positiv", "sp": "⇈ Stark positiv", "ln": "↘ Leicht negativ", "sn": "⇊ Stark negativ"}
RATIO = [1.15, 1.45, 1.2, 10.9]              # Zeile: KPI · Eigenschaft · Abweichung in % · Zahlen
COLS = [8, 6.5, 9.5, 9, 9, 10, 8.5, 17, 22.5]  # Breiten der Zahlenspalten in % (Summe 100)
STAGE_CSS = dict(zip(RECOMMENDATIONS, ("zw", "ng", "ok", "lt", "nr", "uk")))

INFO = {
    "eigenschaft": "Leicht: alle Spiele über der leichten Schwelle (die starken eingeschlossen). Stark: nur die Spiele "
                   "über der starken Schwelle. Positiv = mehr als üblich erwartet, negativ = weniger.",
    "schwelle": "Positiv zählt, was über der Schwelle liegt, negativ, was darunter liegt. Vorbelegt mit den gültigen "
                "Werten aus schwellen.toml; eigene Werte erscheinen blau. KPI 03 bei „Alle Ligen“: leeres Feld = je Liga "
                "die eigene gültige Schwelle; eine eingetragene Zahl gilt für alle Ligen.",
    "spiele": "Spiele, bei denen der KPI vor dem Spiel über (positiv) bzw. unter (negativ) der Schwelle lag. Vorläufige "
              "Werte (z. B. Aufsteiger) zählen nicht. Total = leicht positiv + leicht negativ.",
    "schnitt": "Durchschnitt pro Spieltag: Anzahl Spiele geteilt durch die abgeschlossenen Spieltage der Auswahl. 0,50 "
               "heisst: im Schnitt an jedem zweiten Spieltag ein solches Spiel.",
    "abdeckung": "Anteil der Spieltage mit mindestens einem solchen Spiel. 85,30 % heisst: an 85 von 100 Spieltagen gab "
                 "es bei diesem KPI mindestens eine solche Anomalie. Total = leicht positiv oder leicht negativ.",
    "eingetroffen": "Davon die Spiele, in denen das Erwartete tatsächlich eintrat: positiv = mehr als der "
                    "Liga-Durchschnitt vor dem Spiel, negativ = weniger. Total = leicht positiv + leicht negativ.",
    "treffer": "Wie oft lag die Anomalie richtig? Anzahl eingetroffen geteilt durch die Spiele mit bekanntem Ergebnis "
               "(fehlt der Wert im Spiel, z. B. keine Ecken erfasst, zählt das Spiel hier nicht).",
    "vergleich": "Wie oft trat dasselbe in allen Spielen der Auswahl ein, mit und ohne Anomalie? Das ist der Normalfall. "
                 "Er hängt nicht von der Schwelle ab und ist darum für leicht und stark gleich.",
    "mehrwert": "Trefferquote minus Vergleichsgruppe, in Prozentpunkten. +8 heisst: Mit Anomalie trat das Erwartete in "
                "8 von 100 Spielen häufiger ein als im Normalfall.",
    "spanne": "Zeigt, wie stark der Mehrwert zufällig schwanken kann: Mit 95 % Sicherheit liegt der echte Mehrwert in "
              "diesem Bereich. Je weniger Spiele, desto breiter. Liegt der linke Wert über 0, ist der Vorteil gesichert.",
    "empfehlung": "Fasst Mehrwert und Spanne zusammen; die erste passende Stufe gilt. Zu wenige Daten: unter 50 Spielen. "
                  "Negativ: die ganze Spanne liegt unter 0. Funktioniert: Mehrwert mindestens +5 Pp. und linker Wert "
                  "über 0. Funktioniert leicht: Mehrwert mindestens +2 Pp. und linker Wert nicht unter −5. Keine "
                  "relevante Verbesserung: auch der rechte Wert liegt unter +5 Pp. Noch unklar: alles übrige. Beruht "
                  "auf den gewählten Saisons (historisch); Erklärung unten unter „Definitionen und Änderungen“.",
    "saisons": "„Alle Saisons“ sind alle abgeschlossenen Saisons; „Letzte 2, 3 …“ zählen nur abgeschlossene. Die "
               "älteste Saison der Datenbank (Referenzsaison) liefert nur die Vorsaison und fehlt immer.",
}

STAGES_TEXT = """**Wie entsteht die Empfehlung?** Für jede Zeile schauen wir auf zwei Dinge. Der **Mehrwert** sagt, wie viel \
öfter das Erwartete eintrat, wenn eine Anomalie angezeigt wurde, verglichen mit allen Spielen: +5 Pp. heisst, in 5 von \
100 Spielen öfter. Weil im Fussball auch viel Zufall steckt, zeigt die **Spanne**, in welchem Bereich der echte Mehrwert \
mit 95 % Sicherheit liegt; je mehr Spiele, desto enger wird sie. Geprüft wird in dieser Reihenfolge, die erste passende \
Stufe gilt:

- **Zu wenige Daten:** Es gibt weniger als 50 Spiele. Das reicht für kein Urteil, so wie man aus fünf Münzwürfen nicht \
ablesen kann, ob eine Münze gezinkt ist.
- **Negativ:** Sogar der beste Wert der Spanne liegt unter 0. Die Anomalie liegt also öfter daneben als der Normalfall.
- **Funktioniert:** Der Mehrwert beträgt mindestens +5 Pp., und selbst der schlechteste Wert der Spanne liegt noch \
über 0. Die Anomalie hilft also mit grosser Sicherheit.
- **Funktioniert leicht:** Der Mehrwert beträgt mindestens +2 Pp., und im ungünstigsten Fall verliert man höchstens \
5 Pp. Ein kleiner, aber wahrscheinlicher Vorteil.
- **Keine relevante Verbesserung:** Sogar der beste Wert der Spanne liegt unter +5 Pp. Die Anomalie schadet nicht, \
hilft aber kaum.
- **Noch unklar:** Keine der Stufen oben passt, meist weil die Spanne sehr breit ist. Mehr Spiele würden helfen."""

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
    for part, attr in ATTR.items():
        values = {getattr(x, attr) for x in per_league.values()}
        out[part] = float(values.pop()) if len(values) == 1 else None
    return out


def follow_league(league: str) -> None:
    """Beim Wechsel der Liga: unveränderte Felder (noch der gültige Wert der bisherigen Auswahl) zeigen den gültigen Wert
    der neuen Auswahl, z. B. KPI 03 „je Liga“ -> Bundesliga 35. Eigene Eingaben bleiben stehen."""
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
                del state[key]


def _keep_order(kpi: str) -> None:
    """Bei jeder Eingabe: stark betragsmässig nie unter leicht – sonst wird stark auf den leichten Wert gesetzt."""
    state = st.session_state
    for light, strong, sign in (("lp", "sp", 1), ("ln", "sn", -1)):
        lk, sk = f"{KEY}{kpi}_{light}", f"{KEY}{kpi}_{strong}"
        if state.get(lk) is not None and state.get(sk) is not None and sign * state[sk] < sign * state[lk]:
            state[sk] = state[lk]


def threshold_input(kpi: str, part: str, default: float | None) -> float | None:
    """Ein Schwellenfeld: positiv 0 bis 999, negativ −999 bis 0, eine Nachkommastelle; leer = je Liga."""
    key = f"{KEY}{kpi}_{part}"
    lo, hi = (0.0, 999.0) if part in ("lp", "sp") else (-999.0, 0.0)
    start = {} if key in st.session_state else {"value": default}       # Wert sonst aus der Sitzung
    return st.number_input(f"{kpi} {part}", min_value=lo, max_value=hi, step=0.1, format="%.1f", key=key,
                           placeholder="je Liga", label_visibility="collapsed", on_change=_keep_order, args=(kpi,),
                           **start)


def effective(values: dict[str, float | None], per_league: dict[str, Limits]) -> Limits | dict[str, Limits]:
    """Wirksame Schwellen: eingetragene Zahl für alle Ligen, leeres Feld = gültiger Wert der Liga. Liegt stark dadurch
    unter leicht, gilt stark = leicht (wie bei der Eingabe). Gleich in allen Ligen -> ein Limits, sonst je Liga."""
    out = {}
    for lg, valid in per_league.items():
        v = {p: limit(values[p]) if values[p] is not None else getattr(valid, ATTR[p]) for p in PARTS}
        out[lg] = Limits(v["lp"], v["ln"], max(v["sp"], v["lp"]), min(v["sn"], v["ln"]))
    distinct = set(out.values())
    return distinct.pop() if len(distinct) == 1 else out


# --- Tabelle ---------------------------------------------------------------------------------------------------

def head() -> None:
    """Kopfzeile über allen KPIs (bleibt beim Blättern oben stehen)."""
    with st.container(key="sens_head"):
        c = st.columns(RATIO, vertical_alignment="top")
        c[0].markdown('<div class="si-h full">KPI</div>', unsafe_allow_html=True)
        c[1].markdown('<div class="si-h g span">Schwellen</div>'
                      f'<div class="si-h l">Eigenschaft&nbsp;{info("eigenschaft", "l")}</div>', unsafe_allow_html=True)
        c[2].markdown('<div class="si-h g blank"></div>'
                      f'<div class="si-h l">Abweichung in %&nbsp;{info("schwelle", "l")}</div>', unsafe_allow_html=True)
        c[3].markdown(
            f'<table class="si-t">{colgroup()}<tr><th colspan=3 class=g>Betroffene Spiele</th>'
            '<th colspan=6 class="g q">Prognosewert</th></tr><tr class=l>'
            f'<th>Anzahl Spiele {info("spiele")}</th><th>Ø/ST {info("schnitt")}</th>'
            f'<th>Spieltags&shy;abdeckung {info("abdeckung")}</th><th class=q>Anzahl eingetroffen {info("eingetroffen")}</th>'
            f'<th>Treffer&shy;quote {info("treffer")}</th><th>Vergleichs&shy;gruppe (alle Spiele) {info("vergleich")}</th>'
            f'<th>Mehrwert in Pp. {info("mehrwert", "r")}</th><th>Spanne (Wilson 95 %) {info("spanne", "r")}</th>'
            f'<th>Empfehlung {info("empfehlung", "r")}</th></tr></table>', unsafe_allow_html=True)


def _count_cells(c: Count) -> str:
    per = pct(c.per_matchday) if c.per_matchday is not None else "–"
    cov = f"{pct(c.coverage)} %" if c.coverage is not None else "–"
    return f"<td>{num(c.count)}</td><td>{per}</td><td>{cov}</td>"


def line_html(c: Count, q: Quality, css: str) -> str:
    """Eine Zeile: betroffene Spiele und Prognosewert mit derselben Schwelle."""
    if q.hit is None:                                      # keine Anomalie: nur die Vergleichsgruppe
        base = f"{pct(q.base)} %" if q.base is not None else "–"
        rest = f"<td>–</td><td>{base}</td><td>–</td><td class=c>–</td>"
    else:
        rest = (f"<td>{pct(q.hit)} %</td><td>{pct(q.base)} %</td><td><b>{pct(q.gain, True)}</b></td>"
                f"<td class=s>{pct(q.low, True)} bis {pct(q.high, True)}</td>")
    css = (css + " grey") if q.recommendation == TOO_FEW else css
    cells = _count_cells(c) + f"<td class=q>{num(q.hits)}</td>" + rest + f"<td class=c>{pill(q.recommendation)}</td>"
    return f'<table class="si-t">{colgroup()}<tr class="{css}">{cells}</tr></table>'


def total_html(r: KpiSensitivity) -> str:
    rate = f"{pct(r.total_hits / r.total_cases * 100)} %" if r.total_cases else "–"
    cells = (_count_cells(r.light[TOTAL]) + f"<td class=q>{num(r.total_hits)}</td><td>{rate}</td>"
             + "<td class=c>–</td>" * 4)
    return f'<table class="si-t">{colgroup()}<tr class="tot">{cells}</tr></table>'


def kpi_block(kpi: str, per_league: dict[str, Limits], result_for) -> dict[str, float | None]:
    """Vier Zeilen und Total für einen KPI; gibt die Eingaben zurück. result_for(limits) rechnet den KPI aus."""
    number, _, title = TOP_KPIS[kpi].partition(" – ")
    start = defaults(per_league)
    with st.container(key=f"sens_kpi_{kpi}"):
        values, slots = {}, {}
        for part in (*PARTS, TOTAL):
            c = st.columns(RATIO, vertical_alignment="center")
            if part == "ln":                                   # KPI-Name in der Mitte der fünf Zeilen
                c[0].markdown(f'<div class="si-kpi"><b>{escape(number)}</b><small>{escape(title)}</small></div>',
                              unsafe_allow_html=True)
            if part == TOTAL:
                c[1].markdown('<div class="si-lab t">Total</div>', unsafe_allow_html=True)
                c[2].markdown('<div class="si-lab c">–</div>', unsafe_allow_html=True)
            else:
                c[1].markdown(f'<div class="si-lab{" s" if part[0] == "s" else ""}">{LABEL[part]}</div>',
                              unsafe_allow_html=True)
                with c[2]:
                    values[part] = threshold_input(kpi, part, start[part])
            slots[part] = c[3]
        r = result_for(effective(values, per_league))
        for part, count, quality in (("lp", r.light[POS], r.quality[POS]), ("sp", r.strong[POS], r.strong_quality[POS]),
                                     ("ln", r.light[NEG], r.quality[NEG]), ("sn", r.strong[NEG], r.strong_quality[NEG])):
            slots[part].markdown(line_html(count, quality, "str" if part[0] == "s" else ""), unsafe_allow_html=True)
        slots[TOTAL].markdown(total_html(r), unsafe_allow_html=True)
    return values


def own_values_css(chosen: dict[str, dict[str, float | None]], starts: dict[str, dict[str, float | None]]) -> str:
    """Eigene Werte blau (abweichend von schwellen.toml; bei „je Liga“ jede eingetragene Zahl)."""
    keys = [f".st-key-{KEY}{kpi}_{part} input" for kpi, values in chosen.items() for part, v in values.items()
            if v is not None and (starts[kpi][part] is None or limit(v) != limit(starts[kpi][part]))]
    return f"<style>{', '.join(keys)} {{color:#1d5fb4; font-weight:700;}}</style>" if keys else ""


def definitions() -> None:
    with st.expander("Definitionen und Änderungen"):
        st.markdown("**Wann gilt eine Anomalie als eingetroffen?** Verglichen wird der tatsächliche Wert im Spiel mit "
                    "der Ligareferenz, die vor dem Spiel galt (KPI-Regelwerk, Abschnitt 11). Gleichstand zählt in keiner "
                    "Richtung als eingetroffen.")
        st.markdown("\n".join(f"- **{TOP_KPIS[k]}:** {t}" for k, t in EVENT_TEXTS.items()))
        st.markdown("**Grundlage:** jedes Spiel so berechnet, als wäre es noch nicht gespielt (Stichtag = Spieldatum, "
                    "Spieltag = Gameday); nur abgeschlossene Spieltage. Nicht verwendet: die Referenzsaison (älteste "
                    "Saison der Datenbank), vorläufige Werte (z. B. Aufsteiger) und nicht berechenbare Werte.")
        st.markdown(STAGES_TEXT)
        st.markdown("**Änderungen an den Definitionen**\n\n" + "\n".join(f"- {d}: {t}" for d, t in DEFINITION_CHANGES))


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
        matchdays = get_closed_matchdays()
        matchdays = matchdays[matchdays["season"].isin(sel["seasons"])]
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
        head()
        chosen_values = {}
        for kpi in TOP_KPIS:
            chosen_values[kpi] = kpi_block(kpi, valid[kpi],
                                           lambda lim, k=kpi: evaluate(chosen, matchdays, {k: lim})[0])
        st.markdown(own_values_css(chosen_values, {k: defaults(v) for k, v in valid.items()}), unsafe_allow_html=True)
        st.markdown("<p class='si-note'>Gezählt wird, was <b>über</b> der Schwelle liegt: Bei 15 % zählt +15,00 % nicht, "
                    "+15,01 % schon. „Leicht“ enthält die starken Spiele. <b>Total</b> = leicht positiv + leicht negativ "
                    "(die starken sind darin enthalten und werden nicht nochmals gezählt). Blau = abweichend von "
                    "schwellen.toml. Unter 50 Spielen ist die Zeile grau.</p>"
                    "<p class='si-note'>Leeres Feld „je Liga“ (KPI 03 bei „Alle Ligen“): Jede Liga zählt mit ihrer "
                    "gültigen Schwelle. Eine eingetragene Zahl gilt für alle Ligen; liegt stark dadurch unter leicht, "
                    "gilt stark = leicht.</p>"
                    "<p class='si-note'>Die Empfehlung beruht auf den gewählten Saisons (historisch). Bestätigen mit "
                    "einer einzelnen Saison, z. B. „Saison 2025/26“.</p>",
                    unsafe_allow_html=True)
        definitions()
    ui.footer()
