"""Bereich Sensitivitätsanalyse (Version 0.12, Dashboard-Briefing 6.4, Designentwurf B vom 11.11.2026).

Links Liga und Saison, rechts eine Karte je KPI 02–09: vier Schwellen (leicht/stark, positiv/negativ) und daneben
Häufigkeit (leicht, stark) und Ergebnisqualität (Schwelle = leicht). Gerechnet wird in core/sensitivity.py mit den Fällen
aus core/simulation.py. Die Eingaben hier ändern nie die gültigen Schwellen (schwellen.toml).
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
PARTS = {"lp": POS, "sp": POS, "ln": NEG, "sn": NEG}
RATIO = [0.9, 1.05, 1.05, 12.0]               # Zeile: Richtung · leicht · stark · Zahlen
COLS = [6.5, 5, 7.5, 6, 5, 7.5, 6.5, 6.5, 7, 9, 7.5, 12.5, 13.5]    # Breiten der Zahlenspalten in % (Summe 100)
STAGE_CSS = dict(zip(RECOMMENDATIONS, ("zw", "ng", "ok", "lt", "nr", "uk")))

INFO = {
    "schnitt": "Anzahl Anomalien geteilt durch die Anzahl abgeschlossener Spieltage der Auswahl. Total = positiv + negativ.",
    "abdeckung": "Anteil der Spieltage, an denen die Schwelle mindestens einmal erreicht wird. 85,30 % heisst: an 85 von "
                 "100 Spieltagen gab es bei diesem KPI mindestens eine solche Anomalie. Total = positiv oder negativ.",
    "spiele": "Spiele, bei denen der KPI vor dem Spiel über der leichten Schwelle lag (die starken eingeschlossen) und "
              "deren Ergebnis bekannt ist. Vorläufige Werte (z. B. Aufsteiger) zählen nicht. Total = positiv + negativ.",
    "eingetroffen": "Davon die Spiele, in denen das Erwartete tatsächlich eintrat: positiv = mehr als der "
                    "Liga-Durchschnitt vor dem Spiel, negativ = weniger. Total = positiv + negativ.",
    "treffer": "Wie oft lag die Anomalie richtig? Eingetroffen geteilt durch Spiele mit Anomalie.",
    "grund": "Wie oft trat dasselbe in allen Spielen der Auswahl ein, mit und ohne Anomalie? Das ist der Normalfall, "
             "mit dem verglichen wird.",
    "mehrwert": "Trefferquote minus Grundquote, in Prozentpunkten. +8 heisst: Mit Anomalie trat das Erwartete in 8 von "
                "100 Spielen häufiger ein als im Normalfall.",
    "spanne": "Zeigt, wie stark der Mehrwert zufällig schwanken kann: Mit 95 % Sicherheit liegt der echte Mehrwert in "
              "diesem Bereich. Je weniger Spiele, desto breiter. Liegt der linke Wert über 0, ist der Vorteil gesichert.",
    "empfehlung": "Zu wenige Daten: unter 50 Spielen · Negativ: ganze Spanne unter 0 · Funktioniert: Mehrwert ≥ +5 Pp. "
                  "und linker Wert > 0 · Funktioniert leicht: Mehrwert ≥ +2 Pp. und linker Wert ≥ −5 · Keine relevante "
                  "Verbesserung: rechter Wert < +5 Pp. · Noch unklar: alles übrige. Beruht auf den gewählten Saisons.",
    "saisons": "„Alle Saisons“ sind alle abgeschlossenen Saisons; „Letzte 2, 3 …“ zählen nur abgeschlossene. Die "
               "älteste Saison der Datenbank (Referenzsaison) liefert nur die Vorsaison und fehlt immer.",
}

CSS = """<style>
[data-testid="stColumn"]:has(.st-key-sens_settings) {position:sticky; top:4.2rem; align-self:flex-start;}
.st-key-sens_settings {border:1px solid #c3ccd8; border-radius:.5rem; padding:.6rem .7rem; background:#e3e8ef;}
.si-sim-banner {background:#fff3cd; border:1px solid #f2c230; border-radius:.5rem; padding:.6rem .9rem; margin:.2rem 0 .8rem;
  color:#14213d;}
.si-warn {background:#fdf1e6; border:1px solid #f0a35a; border-radius:.5rem; padding:.45rem .8rem; margin:.2rem 0 .5rem;
  font-size:.85rem; color:#14213d;}
.si-meta {color:#5b6b84; font-size:.8rem; margin:0 0 .3rem;}
.si-note {color:#5b6b84; font-size:.8rem; margin:.3rem 0 0;}
[class*="st-key-sens_card_"] [data-testid="stVerticalBlock"] {gap:.2rem;}
[class*="st-key-sens_card_"] [data-testid="stHorizontalBlock"] {gap:.35rem; align-items:center;}
[class*="st-key-sens_card_"] input {padding:.15rem .35rem; font-size:.85rem; font-variant-numeric:tabular-nums;}
[class*="st-key-sens_card_"] [data-testid="stNumberInputContainer"] {height:1.9rem;}
[class*="st-key-sens_card_"] [data-testid="stMarkdownContainer"] p {margin:0;}
[class*="st-key-sens_card_"] .stMarkdown {margin-bottom:0;}
.si-kh {display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; font-size:1rem; color:#14213d;}
.si-kh .r {margin-left:auto; font-size:.82rem; color:#5b6b84;}
.si-lab {font-size:.82rem; color:#14213d; white-space:nowrap;} .si-lab.h {font-weight:700; text-align:center; font-size:.76rem;}
table.si-t {border-collapse:collapse; width:100%; table-layout:fixed; font-size:.82rem; color:#14213d;
  font-variant-numeric:tabular-nums;}
.si-t th {background:#eef2f7; border:1px solid #d8e0eb; padding:.2rem .25rem; font-size:.72rem; font-weight:700;
  text-align:center; line-height:1.15;}
.si-t th.g {background:#dfe6ef; font-size:.76rem;}
.si-t td {border:1px solid #e3e9f1; padding:.25rem .3rem; text-align:right; white-space:nowrap; overflow:hidden;
  text-overflow:ellipsis;}
.si-t td.c {text-align:center; white-space:normal;} .si-t td.s {color:#5b6b84; font-size:.76rem;}
.si-t td.q {border-left:2px solid #c3ccd8;}
.si-t th.q {border-left:2px solid #c3ccd8;}
.si-t tr.tot td {background:#f4f6f9; font-weight:700;} .si-t tr.grey td {color:#9aa6b8; background:#f7f8fa;}
.si-p {display:inline-block; border-radius:.25rem; padding:.02rem .35rem; font-size:.74rem; white-space:nowrap;}
.si-p.ok {background:#dcf3e5; color:#1f7a45; font-weight:700;} .si-p.lt {background:#fff1c2; color:#7a5a00;}
.si-p.nr {background:#eef0f3; color:#5b6b84;} .si-p.uk {background:#e3edfb; color:#1d5fb4;}
.si-p.ng {background:#fde8e8; color:#9b1c1c; font-weight:700;} .si-p.zw {background:#f1f3f6; color:#8a96a8;}
.si-i {position:relative; color:#4a90e2; cursor:help; font-weight:400;}
.si-i .tip {display:none; position:absolute; z-index:60; top:1.2rem; left:50%; transform:translateX(-50%); width:17rem;
  background:#fff; border:1px solid #c3ccd8; border-radius:.45rem; padding:.5rem .6rem; box-shadow:0 6px 18px rgba(20,33,61,.18);
  color:#14213d; font-weight:400; font-size:.78rem; line-height:1.35; text-align:left; white-space:normal;}
.si-i.r .tip {left:auto; right:-.3rem; transform:none;} .si-i:hover .tip {display:block;}
</style>"""


def info(key: str, right: bool = False) -> str:
    """ⓘ mit eigenem Fenster beim Darüberfahren (Browser-Tooltips erscheinen in Streamlit nicht)."""
    return f'<span class="si-i{" r" if right else ""}">ⓘ<span class="tip">{escape(INFO[key])}</span></span>'


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


def defaults(league: str) -> dict[str, Limits]:
    """Gültige Schwellen aus schwellen.toml; bei „Alle Ligen“ die Werte ohne Liga-Abweichung."""
    config = get_thresholds()
    return {kpi: Limits.from_thresholds(config.get(None if league == ALL else league, kpi)) for kpi in TOP_KPIS}


def _keep_order(kpi: str) -> None:
    """Bei jeder Eingabe: stark betragsmässig nie unter leicht – sonst wird stark auf den leichten Wert gesetzt."""
    state = st.session_state
    for light, strong, sign in (("lp", "sp", 1), ("ln", "sn", -1)):
        lk, sk = f"{KEY}{kpi}_{light}", f"{KEY}{kpi}_{strong}"
        if lk in state and sk in state and sign * state[sk] < sign * state[lk]:
            state[sk] = state[lk]


def threshold_input(kpi: str, part: str, base: Limits) -> float:
    """Ein Schwellenfeld: positiv 0 bis 999, negativ −999 bis 0, eine Nachkommastelle (Spezifikation R10)."""
    key = f"{KEY}{kpi}_{part}"
    default = float(getattr(base, {"lp": "light_pos", "ln": "light_neg", "sp": "strong_pos", "sn": "strong_neg"}[part]))
    lo, hi = (0.0, 999.0) if PARTS[part] == POS else (-999.0, 0.0)
    start = {} if key in st.session_state else {"value": default}       # Wert sonst aus der Sitzung
    return st.number_input(f"{kpi} {part}", min_value=lo, max_value=hi, step=0.1, format="%.1f", key=key,
                           label_visibility="collapsed", on_change=_keep_order, args=(kpi,), **start)


# --- Karte je KPI ----------------------------------------------------------------------------------------------

def head_html() -> str:
    h = (f'<table class="si-t">{colgroup()}<tr><th colspan=3 class=g>Häufigkeit leicht</th>'
         '<th colspan=3 class=g>Häufigkeit stark</th><th colspan=7 class="g q">Ergebnisqualität (Schwelle leicht)</th></tr><tr>'
         f'<th>Anzahl</th><th>Ø/ST {info("schnitt")}</th><th>Abdeckung {info("abdeckung")}</th>'
         f'<th>Anzahl</th><th>Ø/ST</th><th>Abdeckung</th>'
         f'<th class=q>Spiele {info("spiele")}</th><th>eingetr. {info("eingetroffen")}</th>'
         f'<th>Treffer {info("treffer")}</th><th>Grundquote {info("grund")}</th>'
         f'<th>Mehrwert Pp. {info("mehrwert", True)}</th><th>Spanne 95 % {info("spanne", True)}</th>'
         f'<th>Empfehlung {info("empfehlung", True)}</th></tr></table>')
    return h


def _freq(c: Count) -> str:
    per = pct(c.per_matchday) if c.per_matchday is not None else "–"
    cov = f"{pct(c.coverage)} %" if c.coverage is not None else "–"
    return f"<td>{num(c.count)}</td><td>{per}</td><td>{cov}</td>"


def _quality(q: Quality) -> str:
    if q.hit is None:
        rest = "<td class=c>–</td>" * 4
    else:
        rest = (f"<td>{pct(q.hit)} %</td><td>{pct(q.base)} %</td><td><b>{pct(q.gain, True)}</b></td>"
                f"<td class=s>{pct(q.low, True)} bis {pct(q.high, True)}</td>")
    return f"<td class=q>{num(q.cases)}</td><td>{num(q.hits)}</td>{rest}<td class=c>{pill(q.recommendation)}</td>"


def row_html(r: KpiSensitivity, direction: str) -> str:
    if direction == TOTAL:
        cells = (_freq(r.light[TOTAL]) + _freq(r.strong[TOTAL]) + f"<td class=q>{num(r.total_cases)}</td>"
                 f"<td>{num(r.total_hits)}</td>" + "<td class=c>–</td>" * 5)
        css = "tot"
    else:
        q = r.quality[direction]
        cells = _freq(r.light[direction]) + _freq(r.strong[direction]) + _quality(q)
        css = "grey" if q.recommendation == TOO_FEW else ""
    return f'<table class="si-t">{colgroup()}<tr class="{css}">{cells}</tr></table>'


def kpi_card(kpi: str, base: Limits, result_for) -> Limits:
    """Zeichnet die Karte; gibt die eingestellten Schwellen zurück. result_for(limits) rechnet den KPI aus."""
    number, _, title = TOP_KPIS[kpi].partition(" – ")
    with st.container(border=True, key=f"sens_card_{kpi}"):
        head = st.empty()
        c = st.columns(RATIO, vertical_alignment="bottom")
        c[1].markdown('<div class="si-lab h">Schwelle<br>leicht</div>', unsafe_allow_html=True)
        c[2].markdown('<div class="si-lab h">Schwelle<br>stark</div>', unsafe_allow_html=True)
        c[3].markdown(head_html(), unsafe_allow_html=True)
        values, rows = {}, []
        for direction, (lp, sp) in ((POS, ("lp", "sp")), (NEG, ("ln", "sn"))):
            c = st.columns(RATIO, vertical_alignment="center")
            c[0].markdown(f'<div class="si-lab">{"↗ Positiv" if direction == POS else "↘ Negativ"}</div>',
                          unsafe_allow_html=True)
            with c[1]:
                values[lp] = threshold_input(kpi, lp, base)
            with c[2]:
                values[sp] = threshold_input(kpi, sp, base)
            rows.append(c[3])
        total = st.columns(RATIO, vertical_alignment="center")
        total[0].markdown('<div class="si-lab"><b>Total</b></div>', unsafe_allow_html=True)
        total[1].markdown('<div class="si-lab h">–</div>', unsafe_allow_html=True)
        total[2].markdown('<div class="si-lab h">–</div>', unsafe_allow_html=True)
        limits = Limits(limit(values["lp"]), limit(values["ln"]), limit(values["sp"]), limit(values["sn"]))
        r = result_for(limits)
        rows[0].markdown(row_html(r, POS), unsafe_allow_html=True)
        rows[1].markdown(row_html(r, NEG), unsafe_allow_html=True)
        total[3].markdown(row_html(r, TOTAL), unsafe_allow_html=True)
        head.markdown(f'<div class="si-kh"><b>{escape(number)}</b> {escape(title)}<span class="r">positiv '
                      f'{pill(r.quality[POS].recommendation)} · negativ {pill(r.quality[NEG].recommendation)}</span></div>',
                      unsafe_allow_html=True)
    return limits


def own_values_css(chosen: dict[str, Limits], base: dict[str, Limits]) -> str:
    """Eigene Werte blau (abweichend von schwellen.toml)."""
    names = {"lp": "light_pos", "ln": "light_neg", "sp": "strong_pos", "sn": "strong_neg"}
    keys = [f".st-key-{KEY}{kpi}_{part} input" for kpi, lim in chosen.items() for part, attr in names.items()
            if getattr(lim, attr) != getattr(base[kpi], attr)]
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
        base = defaults(sel["league"])
        chosen_limits = {}
        for kpi in TOP_KPIS:
            chosen_limits[kpi] = kpi_card(kpi, base[kpi],
                                          lambda lim, k=kpi: evaluate(chosen, matchdays, {k: lim})[0])
        st.markdown(own_values_css(chosen_limits, base), unsafe_allow_html=True)
        st.markdown("<p class='si-note'>Gezählt wird, was <b>über</b> der Schwelle liegt: Bei 15 % zählt +15,00 % nicht, "
                    "+15,01 % schon. „Leicht“ enthält die starken Anomalien. Blau = abweichend von schwellen.toml.</p>"
                    "<p class='si-note'>Die Empfehlung beruht auf den gewählten Saisons (historisch). Bestätigen mit "
                    "einer einzelnen Saison, z. B. „Saison 2025/26“. Unter 50 Spielen ist die Zeile grau.</p>",
                    unsafe_allow_html=True)
        definitions()
    ui.footer()
