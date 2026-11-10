"""Bereich Simulation – Spielwiese (Etappe I.1, Dashboard-Briefing 6.4, Design Variante B vom 08.11.2026).

Links die Einstellungen (Liga, Saisons, Schwellen für alle KPIs und je KPI, Stufe), rechts zwei Tabellen:
„Häufigkeit“ (wie viele Anomalien) und „Ergebnisqualität“ (treffen sie ein?). Gerechnet wird in core/simulation.py.
Die Einstellungen hier ändern nie die gültigen Schwellen (schwellen.toml).
"""

from __future__ import annotations

from decimal import Decimal
from html import escape

import streamlit as st

from core.kpis import Thresholds
from core.matchday import season_short
from core.simulation import (
    BETTER, DEFINITION_CHANGES, EVENT_TEXTS, MIN_CASES, SAME, TOO_FEW, WORSE, Setting, default_choice, frequency_rows,
    pct, quality_rows, quantize_threshold, running_seasons, season_choices,
)
from core.top import TOP_KPIS
from state import get_active_leagues, get_database, get_simulation_cases, get_thresholds
from views import components as ui
from views.registry import PAGES

ALL = "Alle Ligen"
STAGES = {"leicht + stark": "beide", "nur leicht": "leicht", "nur stark": "stark"}

INFO = {
    "faelle": "Anzahl Spiele, in denen dieser KPI eine Anomalie in dieser Richtung gezeigt hat (je nach Stufe leicht "
              "und stark zusammen). Gezählt werden nur Spiele mit bekanntem Ergebnis, ohne Aufsteiger und ohne "
              "„vorläufige“ Werte. Je mehr Fälle, desto verlässlicher sind die Quoten. Unter 100 Fällen ist die "
              "Zeile grau.",
    "treffer": "Anteil dieser Fälle, in denen das erwartete Ereignis im Spiel tatsächlich eingetreten ist. Beispiel "
               "KPI 02 positiv: Im Spiel fielen mehr Tore als der Liga-Durchschnitt, der vor dem Spiel galt. Diese "
               "Zahl allein sagt wenig, weil manche Ereignisse von Natur aus selten oder häufig sind. Darum steht "
               "daneben die Quote ohne Anomalie.",
    "ohne": "Wie oft dasselbe Ereignis in Spielen eintrat, in denen der KPI keine Anomalie zeigte (mit deinen "
            "Schwellen). Das ist der Normalfall, mit dem wir vergleichen. Liegt die Trefferquote nur knapp darüber, "
            "weiss die Anomalie kaum mehr als der Zufall.",
    "mehrwert": "Trefferquote minus Quote ohne Anomalie, in Prozentpunkten. +8 heisst: Bei einer Anomalie trat das "
                "Ereignis in 8 von 100 Spielen häufiger ein als sonst. Je höher, desto aussagekräftiger ist der KPI; "
                "Werte nahe 0 oder darunter bedeuten, dass die Anomalie nicht hilft. Die Zahl nach ± ist die "
                "zufällige Schwankung: Mit anderen Saisons könnte der Wert um so viel höher oder tiefer liegen.",
    "positiv": "Positive Anomalie: Der KPI erwartet mehr als üblich, zum Beispiel mehr Tore, Karten oder Ecken als im "
               "Liga-Durchschnitt. Sie gilt als eingetroffen, wenn der tatsächliche Wert im Spiel über der "
               "Ligareferenz lag, die vor dem Spiel galt. Bei KPI 03 zählen mindestens 3 Tore, bei KPI 08 „beide "
               "Teams treffen“. Fehlt der Wert im Spiel, zählt das Spiel nicht.",
    "negativ": "Negative Anomalie: Der KPI erwartet weniger als üblich, zum Beispiel weniger Tore, Karten oder Ecken "
               "als im Liga-Durchschnitt. Sie gilt als eingetroffen, wenn der tatsächliche Wert im Spiel unter der "
               "Ligareferenz lag, die vor dem Spiel galt. Bei KPI 03 zählen höchstens 2 Tore, bei KPI 08 „nicht "
               "beide Teams treffen“. Fehlt der Wert im Spiel, zählt das Spiel nicht.",
    "urteil": "Vergleicht den Mehrwert mit deinen Schwellen (nachher) mit dem Mehrwert der gültigen Schwellen "
              "(vorher). „Besser“ oder „schlechter“ erscheint nur, wenn der Unterschied grösser ist als die zufällige "
              "Schwankung. Sonst steht „kein klarer Unterschied“ – die Veränderung kann dann auch Zufall sein. Hat "
              "vorher oder nachher weniger als 100 Fälle, steht „zu wenige Fälle“.",
    "stufe": "Bestimmt, welche Anomalien in der Tabelle Ergebnisqualität zählen: leichte und starke zusammen, nur "
             "leichte oder nur starke. Starke Anomalien sind seltener, treffen aber oft häufiger ein. Mit „nur stark“ "
             "siehst du, ob sich die starke Stufe lohnt. Die Tabelle Häufigkeit zeigt immer beide Stufen getrennt.",
    "saisons": "Welche Saisons in die Tabellen einfliessen. „Alle Saisons“ sind alle abgeschlossenen Saisons, "
               "„Letzte 2, 3 …“ zählen ebenfalls nur abgeschlossene. Die aktuelle Saison ist noch nicht fertig und "
               "darum vorläufig. Die älteste Saison der Datenbank (Referenzsaison) fehlt immer: Sie liefert nur die "
               "Vorsaison für die Saison danach.",
    "schwellen": "Ab welcher Abweichung vom Liga-Durchschnitt (in %) eine Anomalie als leicht bzw. stark gilt. Die "
                 "zwei Felder oben gelten für alle KPIs; je KPI kannst du darunter einen eigenen Wert eintragen "
                 "(leer = Wert für alle). „Vorher“ sind die gültigen Schwellen aus schwellen.toml.",
}
CAP_FREQ = ("Wie viele Anomalien entstehen mit deinen Schwellen? Hier siehst du, wie Spiele zwischen keine, leicht "
            "und stark wandern, wenn du eine Schwelle veränderst.")
CAP_QUAL = ("Treffen die Anomalien im Spiel tatsächlich ein? Entscheidend ist der Mehrwert gegenüber Spielen ohne "
            "Anomalie, nicht die Trefferquote allein.")

CSS = """<style>
[data-testid="stColumn"]:has(.st-key-sim_settings) {position:sticky; top:4.2rem; align-self:flex-start;}
.st-key-sim_settings {border:1px solid #c3ccd8; border-radius:.5rem; padding:.6rem .7rem; background:#e3e8ef;}
.si-sim-banner {background:#fff3cd; border:1px solid #f2c230; border-radius:.5rem; padding:.6rem .9rem;
  margin:.2rem 0 1rem; color:#14213d;}
.si-sim h4 {margin:.6rem 0 .1rem; font-size:1.1rem; color:#14213d;}
.si-sim .cap {color:#5b6b84; font-size:.88rem; margin:0 0 .5rem;}
.si-sim .meta {color:#5b6b84; font-size:.8rem; margin:0 0 .4rem;}
.si-sim table {border-collapse:collapse; width:100%; font-size:.85rem; color:#14213d; font-variant-numeric:tabular-nums;}
.si-sim th {background:#eef2f7; font-weight:700; padding:.32rem .45rem; border:1px solid #d8e0eb; font-size:.76rem;
  text-align:center;}
.si-sim td {padding:.3rem .45rem; border:1px solid #e3e9f1; text-align:right; white-space:nowrap;}
.si-sim td.k {text-align:left; white-space:normal; width:8.5rem; line-height:1.2;}
.si-sim td.k small {display:block; font-size:.74rem;}
.si-sim td.c {text-align:center;} .si-sim td.c small {display:block; font-size:.72rem;}
.si-sim td.u {text-align:center; white-space:normal; width:6.6rem;}
.si-sim tr.sep td {border-top:2px solid #d8e0eb;}
.si-sim tr.grey td {color:#9aa6b8; background:#f7f8fa;}
.si-sim small {color:#5b6b84;} .si-sim .own {color:#1d5fb4; font-weight:700;}
.si-sim .up {color:#1f7a45; font-weight:700;} .si-sim .dn {color:#b42318; font-weight:700;}
.si-sim .i {position:relative; color:#4a90e2; cursor:help; margin-left:.15rem; font-weight:400;}
.si-sim .i .tip {display:none; position:absolute; z-index:50; top:1.25rem; left:50%; transform:translateX(-50%);
  width:19rem; background:#fff; border:1px solid #c3ccd8; border-radius:.45rem; padding:.55rem .65rem;
  box-shadow:0 6px 18px rgba(20,33,61,.18); color:#14213d; font-weight:400; font-size:.8rem; line-height:1.4;
  text-align:left; white-space:normal;}
.si-sim .i.r .tip {left:auto; right:-.4rem; transform:none;}
.si-sim .i:hover .tip {display:block;}
.si-sim .j {display:inline-block; line-height:1.2; padding:.08rem .4rem; border-radius:.3rem; background:#eef2f7;
  font-size:.78rem;}
.si-sim .j.good {background:#dcf3e5; color:#1f7a45; font-weight:700;}
.si-sim .j.bad {background:#fde8e8; color:#9b1c1c; font-weight:700;}
.si-sim .j.grey {background:#f1f3f6; color:#8a96a8;}
</style>"""


def info(key: str, right: bool = False) -> str:
    """ⓘ mit Erklärung, die beim Darüberfahren erscheint.
    Eigenes Fenster statt Browser-Tooltip, weil dieser in Streamlit nicht erscheint (Nachtrag 09.11.2026).
    right=True: Fenster öffnet nach links (für Spalten am rechten Rand)."""
    return f'<span class="i{" r" if right else ""}">ⓘ<span class="tip">{escape(INFO[key])}</span></span>'


def threshold_text(t: Thresholds) -> str:
    def num(d: Decimal) -> str:
        return format(d.normalize(), "f").replace(".", ",")
    return f"±{num(t.leicht)} / ±{num(t.stark)}"


# --- Einstellungen (links) -----------------------------------------------------------------------

def _reset() -> None:
    for key in list(st.session_state):
        if key.startswith("sim_th_"):
            del st.session_state[key]


def settings_panel(cases, standard: Thresholds) -> dict:
    """Linke Spalte. Gibt die Auswahl zurück; ungültige Schwellen ergeben einen Eintrag in 'errors'."""
    with st.container(key="sim_settings"):
        st.markdown("**Einstellungen**")
        leagues = [lg.name for lg in get_active_leagues()]
        league = st.selectbox("Liga", [ALL, *leagues], key="sim_liga")
        choices = season_choices(cases)          # ohne Referenzsaison, Voreinstellung „Alle Saisons“ (Version 0.11)
        labels = list(choices)
        default = default_choice(choices)
        season_label = st.selectbox("Saisons", labels, index=labels.index(default) if default else 0,
                                    key="sim_saisons", help=INFO["saisons"])

        st.markdown("**Schwellen für alle KPIs**", help=INFO["schwellen"])
        a, b = st.columns(2)
        g_light = a.number_input("leicht ± %", min_value=0.0, value=float(standard.leicht), step=1.0, format="%.2f",
                                 key="sim_th_all_l")
        g_strong = b.number_input("stark ± %", min_value=0.0, value=float(standard.stark), step=1.0, format="%.2f",
                                  key="sim_th_all_s")
        stage = st.selectbox("Stufe (Ergebnisqualität)", list(STAGES), key="sim_stufe", help=INFO["stufe"])
        st.markdown("**Je KPI** (leer = Wert für alle)")
        after, errors = {}, []
        for kpi, name in TOP_KPIS.items():
            label, cl, cs = st.columns([1.1, 1, 1], vertical_alignment="center")
            label.markdown(name.split(" – ")[0])
            own_l = cl.number_input(f"{name} leicht", min_value=0.0, value=None, step=1.0, format="%.2f",
                                    placeholder="alle", label_visibility="collapsed", key=f"sim_th_{kpi}_l")
            own_s = cs.number_input(f"{name} stark", min_value=0.0, value=None, step=1.0, format="%.2f",
                                    placeholder="alle", label_visibility="collapsed", key=f"sim_th_{kpi}_s")
            light = quantize_threshold(own_l if own_l is not None else g_light)
            strong = quantize_threshold(own_s if own_s is not None else g_strong)
            if not (0 < light < strong):
                errors.append(f"{name.split(' – ')[0]}: leicht muss grösser als 0 und kleiner als stark sein")
            after[kpi] = Thresholds(light, strong)
        st.button("Auf gültige Schwellen zurücksetzen", on_click=_reset, key="sim_reset")
    seasons = list(choices.get(season_label, []))
    return {"league": league, "seasons": seasons, "season_label": season_label,
            "running": bool(set(seasons) & set(running_seasons(cases))),
            "after": after, "errors": errors, "stage": STAGES[stage]}


# --- Tabellen (rechts) -------------------------------------------------------------------------------

def _before_text(cases, kpi: str, before) -> str:
    texts = {threshold_text(before(lg, kpi)) for lg in cases["league"].unique()}
    return texts.pop() if len(texts) == 1 else "je Liga"


def _share(n: int, total: int) -> str:
    return f'<small>({pct(n / total * 100) if total else "–"} %)</small>'


def kpi_cell(name: str, rowspan: int = 1) -> str:
    """KPI-Spalte zweizeilig und schmal: „KPI 02“ fett, darunter klein der Name (Nachtrag 09.11.2026)."""
    number, _, title = name.partition(" – ")
    span = f" rowspan='{rowspan}'" if rowspan > 1 else ""
    return f"<td class='k'{span}><b>{escape(number)}</b><small>{escape(title)}</small></td>"


def threshold_cell(cases, kpi: str, setting: Setting, rowspan: int = 1, show_before: bool = False) -> str:
    """Schwellen nachher; eigene Werte blau. show_before: darunter klein die gültigen Schwellen (vorher)."""
    changed = not all(setting.before(lg, kpi) == setting.after[kpi] for lg in cases["league"].unique())
    own = " class='own'" if changed else ""
    before = f"<small>vorher {_before_text(cases, kpi, setting.before)}</small>" if show_before and changed else ""
    span = f" rowspan='{rowspan}'" if rowspan > 1 else ""
    return f"<td class='c'{span}><span{own}>{threshold_text(setting.after[kpi])}</span>{before}</td>"


def frequency_table(cases, setting: Setting) -> str:
    head = ("<tr><th rowspan='2'>KPI</th><th colspan='2'>Schwellen " + info("schwellen") + "</th>"
            "<th colspan='2'>leicht</th><th colspan='2'>stark</th><th colspan='2'>Anomalien gesamt (Anteil der Spiele)</th>"
            "<th rowspan='2'>Veränderung</th></tr><tr>" + "<th>vorher</th><th>nachher</th>" * 4 + "</tr>")
    body = []
    for r in frequency_rows(cases, setting):
        kpi, total = r["kpi"], r["games"]
        b, a = r["total_before"], r["total_after"]
        change = "–" if not b else ("±0,00 %" if a == b else f"{pct((a - b) / b * 100, signed=True)} %")
        css = "up" if a > b else "dn" if a < b else ""
        body.append(
            f"<tr>{kpi_cell(r['name'])}<td class='c'>{_before_text(cases, kpi, setting.before)}</td>"
            f"{threshold_cell(cases, kpi, setting)}"
            f"<td>{r['light_before']}</td><td>{r['light_after']}</td>"
            f"<td>{r['strong_before']}</td><td>{r['strong_after']}</td>"
            f"<td>{b} {_share(b, total)}</td><td><b>{a}</b> {_share(a, total)}</td><td class='{css}'>{change}</td></tr>")
    return f"<table>{head}{''.join(body)}</table>"


JUDGE_CSS = {BETTER: "good", WORSE: "bad", TOO_FEW: "grey", SAME: ""}


def quality_table(cases, setting: Setting, stage: str) -> str:
    head = ("<tr><th rowspan='2'>KPI</th><th rowspan='2'>Schwellen " + info("schwellen") + "<br><small>leicht / stark"
            "</small></th><th rowspan='2'>Richtung</th><th colspan='2'>Fälle " + info("faelle") + "</th>"
            "<th colspan='2'>eingetroffen " + info("treffer") + "</th><th rowspan='2'>ohne Anomalie "
            + info("ohne") + "</th><th colspan='2'>Mehrwert " + info("mehrwert", right=True) + "</th>"
            "<th rowspan='2'>Urteil " + info("urteil", right=True) + "</th></tr><tr>"
            + "<th>vorher</th><th>nachher</th>" * 3 + "</tr>")
    body = []
    for i, r in enumerate(quality_rows(cases, setting, stage)):
        b, a = r["before"], r["after"]
        first = i % 2 == 0
        classes = " ".join(c for c in ("sep" if first else "", "grey" if a.cases < MIN_CASES else "") if c)
        lead = (kpi_cell(r["name"], 2) + threshold_cell(cases, r["kpi"], setting, 2, show_before=True)) if first else ""
        margin = f" <small>±{pct(a.margin)}</small>" if a.margin is not None else ""
        judge = f"<span class='j {JUDGE_CSS.get(r['judge'], '')}'>{r['judge']}</span>"
        hit_b = f"{pct(b.hit)} %" if b.hit is not None else "–"
        hit_a = f"{pct(a.hit)} %" if a.hit is not None else "–"
        ctrl = f"{pct(a.control)} %" if a.control is not None else "–"
        body.append(
            f"<tr class='{classes}'>{lead}<td>{r['direction']} {info(r['direction'])}</td><td>{b.cases}</td>"
            f"<td><b>{a.cases}</b></td><td>{hit_b}</td><td>{hit_a}</td><td>{ctrl}</td>"
            f"<td>{pct(b.gain, signed=True)}</td><td><b>{pct(a.gain, signed=True)}</b>{margin}</td>"
            f"<td class='u'>{judge}</td></tr>")
    return f"<table>{head}{''.join(body)}</table>"


def definitions() -> None:
    with st.expander("Definitionen und Änderungen"):
        st.markdown("**Wann gilt eine Anomalie als eingetroffen?** Verglichen wird der tatsächliche Wert im Spiel mit "
                    "der Ligareferenz, die vor dem Spiel galt (KPI-Regelwerk, Abschnitt 11). Gleichstand zählt in keiner "
                    "Richtung als eingetroffen.")
        st.markdown("\n".join(f"- **{TOP_KPIS[k]}:** {t}" for k, t in EVENT_TEXTS.items()))
        st.markdown("**Grundlage:** jedes Spiel so berechnet, als wäre es noch nicht gespielt (Stichtag = Spieldatum, "
                    "Spieltag = Gameday). Nicht verwendet: die Referenzsaison (älteste Saison der Datenbank, liefert nur "
                    "die Vorsaison), vorläufige Werte (z. B. Aufsteiger) und nicht berechenbare Werte.")
        st.markdown("**Änderungen an den Definitionen**\n\n" + "\n".join(f"- {d}: {t}" for d, t in DEFINITION_CHANGES))


# --- Seite --------------------------------------------------------------------------------------------

def render() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    ui.header()
    st.markdown("### Simulation – Spielwiese <small>(intern)</small>", unsafe_allow_html=True)
    st.caption("Wie gut funktionieren die Anomalien und ihre Schwellen? Berechnet mit allen historischen Spielen, "
               "jeweils so, als wären sie noch nicht gespielt.")
    st.markdown("<div class='si-sim-banner'><b>Spielwiese – nur zum Ausprobieren.</b> Hier veränderte Schwellen wirken "
                "nicht auf das Dashboard. Gültig bleiben die Werte in <code>schwellen.toml</code>; eine Übernahme "
                "erfolgt bewusst über die Datei.</div>", unsafe_allow_html=True)

    if get_database().has_errors:
        ui.blocked_notice(True, False, PAGES.get("datenqualitaet"))
        ui.footer()
        return
    cases = get_simulation_cases()
    if cases.empty:
        st.info("Keine Spiele für die Simulation vorhanden. Ausgewertet werden alle Saisons ausser der ältesten "
                "(Referenzsaison); enthält die Datenbank nur eine Saison, gibt es nichts auszuwerten.")
        ui.footer()
        return

    config = get_thresholds()
    left, right = st.columns([0.9, 3.7], gap="medium")   # links 10 % schmaler (Nachtrag 09.11.2026)
    with left:
        sel = settings_panel(cases, config.standard)
    with right:
        if sel["errors"]:
            st.error("Schwellen ungültig – bitte korrigieren:\n\n" + "\n".join(f"- {e}" for e in sel["errors"]))
            ui.footer()
            return
        chosen = cases[cases["season"].isin(sel["seasons"])]
        if sel["league"] != ALL:
            chosen = chosen[chosen["league"] == sel["league"]]
        setting = Setting(before=config.get, after=sel["after"])
        games = chosen[["league", "game"]].drop_duplicates().shape[0]
        seasons = ", ".join(season_short(s) for s in sel["seasons"])
        note = " · aktuelle Saison: vorläufig, noch nicht abgeschlossen" if sel["running"] else ""
        html = [
            "<div class='si-sim'>",
            f"<div class='meta'>Grundlage: {games:,} Spiele".replace(",", "'")
            + f" · {escape(sel['league'])} · Saisons {seasons}{note} · ohne Aufsteiger und vorläufige Werte</div>",
            f"<h4>Häufigkeit der Anomalien</h4><p class='cap'>{CAP_FREQ}</p>", frequency_table(chosen, setting),
            f"<h4>Ergebnisqualität</h4><p class='cap'>{CAP_QUAL}</p>", quality_table(chosen, setting, sel["stage"]),
            "</div>",
        ]
        st.markdown("".join(html), unsafe_allow_html=True)
        definitions()
    ui.footer()
