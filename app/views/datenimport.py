"""Bereich „Datenimport/API“ (Version 0.14, Designentwurf vom 15.11.2026, Dashboard-Briefing 6.5).

Zeigt den Stand des Datenimports aus /import (nur lesend): Statusleiste, die wartende neue Fassung mit Vollständigkeit
(Spielplan gegen Ergebnisse), Qualitätsbericht, Korrekturen, neuen Spielen und Spielplan-Änderungen sowie das
Protokoll der letzten 14 Tage. Die Buttons „Übernehmen“ und „Verwerfen“ legen nur eine Anfrage in /import/anfragen ab;
den Tausch macht der Container soccer-import (das Dashboard schreibt nie in die Excel-Dateien).
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from core import settings
from importer import einstellungen as E
from views import components as ui

CSS = """<style>
.di-st{display:grid;grid-template-columns:repeat(4,1fr);gap:.6rem;margin:.2rem 0 .9rem}
.di-st div{border:1px solid #d8e0eb;border-radius:.5rem;padding:.45rem .6rem;background:#fff}
.di-st small{display:block;color:#5b6b84;font-size:.75rem}.di-st b{font-size:1rem;color:#14213d}
.di-ok{color:#1f7a45 !important}.di-wn{color:#9a6200 !important}.di-bad{color:#9b1c1c !important}
.di-box{border:2px solid #f2c230;border-radius:.6rem;padding:.7rem .9rem;background:#fffdf3;margin:.3rem 0 .6rem}
.di-box.err{border-color:#d64545;background:#fff7f7}
.di-box h3{margin:0;font-size:1.1rem;color:#14213d}.di-sub{color:#5b6b84;font-size:.8rem;margin:.1rem 0 .5rem}
.di-kp{display:grid;grid-template-columns:repeat(5,1fr);gap:.5rem;margin:.3rem 0 .6rem}
.di-kp div{background:#fff;border:1px solid #d8e0eb;border-radius:.5rem;padding:.4rem;text-align:center}
.di-kp b{display:block;font-size:1.25rem;color:#14213d}.di-kp small{font-size:.75rem;color:#5b6b84}
table.di-t{border-collapse:collapse;width:100%;font-size:.82rem;color:#14213d;margin:.2rem 0 .4rem}
.di-t th{background:#eef2f7;border:1px solid #d8e0eb;padding:.25rem .4rem;font-size:.75rem;text-align:center}
.di-t td{border:1px solid #e3e9f1;padding:.25rem .4rem;text-align:right}.di-t td.l{text-align:left}
.di-t td.c{text-align:center}
.di-tag{display:inline-block;border-radius:.25rem;padding:.02rem .4rem;font-size:.74rem}
.t-ok{background:#dcf3e5;color:#1f7a45}.t-w{background:#fff1c2;color:#7a5a00}.t-b{background:#e3edfb;color:#1d5fb4}
.t-g{background:#eef0f3;color:#5b6b84}.t-r{background:#fde8e8;color:#9b1c1c}
.di-h{font-weight:700;font-size:.9rem;margin:.6rem 0 .1rem;color:#14213d}
.di-note{color:#5b6b84;font-size:.8rem;margin:.2rem 0}
@media (max-width:800px){.di-st,.di-kp{grid-template-columns:1fr 1fr}}
</style>"""
TAG = {"wartet": "t-w", "übernommen": "t-ok", "übernommen (automatisch)": "t-ok", "verworfen": "t-b", "ersetzt": "t-g",
       "fehlgeschlagen": "t-r", "Fehler – nicht übernehmbar": "t-r"}


def num(n) -> str:
    return "–" if n is None else f"{n:,}".replace(",", "'")


def _read(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reports(base: Path, days: int) -> list[dict]:
    """Berichte der letzten Tage, neueste zuerst."""
    cut = (datetime.now(ZoneInfo(E.TIMEZONE)) - timedelta(days=days)).strftime("%Y-%m-%d")
    out = []
    for p in sorted((base / "laeufe").glob("*/bericht.json"), reverse=True):
        if p.parent.name[:10] >= cut:
            rep = _read(p)
            if rep:
                out.append(rep)
    return out


def next_run(now: datetime, state: dict) -> datetime:
    day = now
    ran_today = state.get("letzter_lauf_tag") == now.strftime("%Y-%m-%d")
    if ran_today or now.weekday() >= 5:
        day = now + timedelta(days=1)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return day.replace(hour=E.RUN_HOUR, minute=0, second=0, microsecond=0)


def _when(iso: str | None) -> str:
    if not iso:
        return "–"
    d = datetime.fromisoformat(iso)
    return d.strftime("%a %d.%m.%Y, %H:%M").replace("Mon", "Mo").replace("Tue", "Di").replace("Wed", "Mi") \
        .replace("Thu", "Do").replace("Fri", "Fr").replace("Sat", "Sa").replace("Sun", "So")


def status_bar(state: dict, latest: dict | None, now: datetime) -> str:
    abo = (latest or {}).get("abo") or {}
    if abo.get("bis"):
        end = date.fromisoformat(abo["bis"])
        left = (end - now.date()).days
        css = "di-ok" if left > 21 else "di-wn" if left >= 0 else "di-bad"
        abo_txt = f'<small class="{css}">Abo gültig bis {end:%d.%m.%Y} (noch {left} Tage)</small>'
    else:
        abo_txt = "<small>Abo: noch kein Lauf</small>"
    rest = ((latest or {}).get("anfragen") or {}).get("rest")
    last = latest.get("start") if latest else None
    ok = latest and latest.get("status") != "fehlgeschlagen"
    last_css = "di-ok" if ok else "di-bad"
    auto = E.automatic_from()
    mode = ("automatisch" if auto and now.date() >= auto else "halbautomatisch")
    mode_txt = (f"Freigabe von Hand bis {auto - timedelta(days=1):%d.%m.%Y}" if auto and now.date() < auto
                else "fehlerfreie Fassungen werden sofort übernommen" if auto else "Freigabe von Hand")
    return (f'<div class="di-st"><div><small>Quelle</small><b>API-Football · {escape(abo.get("plan", "–"))}</b>{abo_txt}</div>'
            f'<div><small>Kontingent heute (Rest laut API)</small><b>{num(rest)}</b><small>eigene Obergrenze '
            f'{E.DAILY_LIMIT} je Tag</small></div>'
            f'<div><small>Letzter Lauf</small><b class="{last_css}">{_when(last)} {"✓" if ok else "✕"}</b>'
            f'<small>nächster: {_when(next_run(now, state).isoformat())}</small></div>'
            f'<div><small>Betriebsart</small><b>{mode}</b><small>{mode_txt}</small></div></div>')


def _table(head: list[str], rows: list[list], left: tuple[int, ...] = (0,)) -> str:
    h = "".join(f"<th>{escape(x)}</th>" for x in head)
    body = "".join("<tr>" + "".join(f'<td class="{"l" if i in left else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>"
                   for r in rows)
    return f'<table class="di-t"><tr>{h}</tr>{body}</table>'


def completeness(rep: dict) -> str:
    rows = []
    for league, mds in (rep.get("vollstaendigkeit") or {}).items():
        for m in mds:
            tag = ('<span class="di-tag t-ok">vollständig</span>' if m["fehlt"] == 0
                   else f'<span class="di-tag t-w">{m["fehlt"]} offen</span>')
            rows.append([escape(league), m["spieltag"], m["faellig"] + m["inaktiv"], m["geliefert"], m["inaktiv"],
                         m["fehlt"], tag])
    if not rows:
        return '<p class="di-note">Keine fälligen Spiele in den letzten 14 Tagen.</p>'
    return _table(["Liga", "Spieltag", "laut Spielplan fällig", "Ergebnis geliefert", "verschoben / abgesagt", "fehlt",
                   "Stand"], rows)


def quality(rep: dict) -> str:
    p = rep.get("pruefung") or {}
    db, fx = p.get("datenbank") or {}, p.get("spielplan") or {}
    g, n = db.get("gueltig") or {}, db.get("neu") or {}
    fg, fn = fx.get("gueltig") or {}, fx.get("neu") or {}
    new_msgs = db.get("neue_meldungen") or []
    rows = [
        ["Datenbank: Fehler", num(g.get("fehler")), f'<b class="{"di-ok" if not n.get("fehler") else "di-bad"}">{num(n.get("fehler"))}</b>',
         "Übernahme möglich" if not rep.get("fehler") else "Übernahme gesperrt"],
        ["Datenbank: Warnungen", num(g.get("warnungen")), num(n.get("warnungen")),
         f"{len(new_msgs)} neu (siehe unten)" if new_msgs else "keine neuen"],
        ["Datenbank: Hinweise", num(g.get("hinweise")), num(n.get("hinweise")), ""],
        ["Spielplan: Fehler / Warnungen", f'{num(fg.get("fehler"))} / {num(fg.get("warnungen"))}',
         f'{num(fn.get("fehler"))} / {num(fn.get("warnungen"))}', ""],
        ["Unbekannte Teams", "–", num(len(rep.get("unbekannte_teams") or [])), "werden mit dem Namen der API übernommen"],
        ["Korrekturen der API", "–", num(len(rep.get("korrekturen") or [])), "Einzelheiten unten"],
    ]
    return _table(["Prüfung", "gültige Fassung", "neue Fassung", "Bemerkung"], rows, left=(0, 3))


def write_request(base: Path, run_id: str, action: str) -> None:
    folder = base / "anfragen"
    folder.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo(E.TIMEZONE))
    payload = {"lauf": run_id, "aktion": action, "zeit": now.isoformat(timespec="seconds")}
    # Erst unter einem Namen schreiben, den der Dienst nicht liest, dann in einem Schritt umbenennen:
    # so findet er nie eine halb geschriebene Anfrage.
    name = f"{now:%Y%m%d_%H%M%S}_{action}.json"
    tmp = folder / f".{name}.tmp"
    tmp.write_text(json.dumps(payload), encoding="utf-8")
    tmp.replace(folder / name)


def pending_requests(base: Path, run_id: str) -> list[str]:
    out = []
    for p in (base / "anfragen").glob("*.json"):
        req = _read(p) or {}
        if req.get("lauf") == run_id:
            out.append(req.get("aktion", ""))
    return out


def pending_box(rep: dict, base: Path) -> None:
    run_id, err = rep["lauf"], rep.get("fehler", 0) > 0
    new_games = sum(len(v) for v in (rep.get("neue_spiele") or {}).values())
    fx = rep.get("spielplan_aenderungen") or {}
    fx_count = fx.get("neu", 0) + fx.get("entfallen", 0) + len(fx.get("geaendert") or [])
    db_new = (rep.get("pruefung") or {}).get("datenbank", {}).get("neu", {})
    warn_new = len((rep.get("pruefung") or {}).get("datenbank", {}).get("neue_meldungen") or [])
    saison = ", ".join(sorted(set((rep.get("saison") or {}).values())))
    st.markdown(
        f'<div class="di-box{" err" if err else ""}"><h3>{"Neue Daten bereit" if not err else "Neue Fassung mit Fehlern"}</h3>'
        f'<p class="di-sub">Lauf {_when(rep.get("start"))} · Saison {escape(saison)} · '
        f'{"alle Spiele der Saison neu geprüft" if rep.get("ganze_saison") else "letzte 2 Spieltage neu geprüft"} · '
        f'aufgebaut auf der gültigen Datenbank ({escape((rep.get("basis") or {}).get("datenbank", "")[:8])})</p>'
        f'<div class="di-kp"><div><b>{new_games}</b><small>neue Spiele mit Ergebnis</small></div>'
        f'<div><b>{len(rep.get("korrekturen") or [])}</b><small>korrigierte Werte</small></div>'
        f'<div><b>{fx_count}</b><small>Spielplan-Änderungen</small></div>'
        f'<div><b class="{"di-bad" if err else "di-ok"}">{num(db_new.get("fehler", rep.get("fehler")))}</b><small>Fehler</small></div>'
        f'<div><b class="{"di-wn" if warn_new else "di-ok"}">{warn_new}</b><small>neue Warnungen</small></div></div>'
        f'<div class="di-h">1. Vollständigkeit: Spielplan gegen gelieferte Ergebnisse (Spiele der letzten 14 Tage bis gestern)</div>'
        f'{completeness(rep)}'
        f'<div class="di-h">2. Qualitätsbericht der neuen Fassung (Prüfregeln wie unter Datenqualität)</div>{quality(rep)}</div>',
        unsafe_allow_html=True)
    details(rep)
    asked = pending_requests(base, run_id)
    if asked:
        st.info(f"Freigabe hinterlegt („{asked[0]}“). Der Import führt sie innerhalb einer Minute aus – Seite neu laden.")
        return
    c1, c2, c3 = st.columns([1, 1, 4])
    if c1.button("✓ Übernehmen", type="primary", disabled=err, key="di_ok"):
        write_request(base, run_id, "uebernehmen")
        st.rerun()
    if c2.button("✕ Verwerfen", key="di_no"):
        write_request(base, run_id, "verwerfen")
        st.rerun()
    c3.markdown('<p class="di-note">Datenbank und Spielplan werden gemeinsam übernommen; die bisherige Fassung kommt '
                'mit Datum ins Backup. Bei Fehlern ist „Übernehmen“ gesperrt.</p>', unsafe_allow_html=True)


def details(rep: dict) -> None:
    offen = rep.get("offen") or []
    missing = [(lg, m) for lg, mds in (rep.get("vollstaendigkeit") or {}).items() for m in mds if m["fehlende"] or m["inaktive"]]
    if offen or missing:
        with st.expander(f"Offen und verschoben ({len(offen) + sum(len(m['fehlende']) + len(m['inaktive']) for _, m in missing)})"):
            for o in offen:
                st.markdown(f"- **{escape(o['liga'])}**, {escape(o['heim'])} – {escape(o['gast'])} ({o['datum']}): {escape(o['grund'])}")
            for lg, m in missing:
                for x in m["fehlende"]:
                    st.markdown(f"- **{escape(lg)}**, Spieltag {m['spieltag']}: {escape(x)} – noch kein Ergebnis")
                for x in m["inaktive"]:
                    st.markdown(f"- **{escape(lg)}**, Spieltag {m['spieltag']}: {escape(x)}")
    if rep.get("umbenennungen"):
        with st.expander(f"Teamnamen umgestellt auf API-Football ({len(rep['umbenennungen'])} Teams) – einmalig"):
            st.dataframe(pd.DataFrame(rep["umbenennungen"]).rename(columns={"liga": "Liga", "alt": "bisher", "neu": "neu",
                                                                            "zeilen": "Zeilen"}),
                         hide_index=True, width="stretch")
    msgs = (rep.get("pruefung") or {}).get("datenbank", {}).get("neue_meldungen") or []
    msgs += (rep.get("pruefung") or {}).get("spielplan", {}).get("meldungen") or []
    if msgs:
        with st.expander(f"Neue Meldungen der Prüfung ({len(msgs)})"):
            st.dataframe(pd.DataFrame(msgs), hide_index=True, width="stretch")
    corr = rep.get("korrekturen") or []
    if corr:
        with st.expander(f"Korrekturen ({len(corr)})"):
            st.dataframe(pd.DataFrame(corr).astype(str), hide_index=True, width="stretch")
    games = rep.get("neue_spiele") or {}
    if any(games.values()):
        with st.expander(f"Neue Spiele ({sum(len(v) for v in games.values())})"):
            for league, rows in games.items():
                if rows:
                    st.markdown(f"**{escape(league)}**")
                    st.dataframe(pd.DataFrame(rows).drop(columns=["id"]), hide_index=True, width="stretch")
    fx = rep.get("spielplan_aenderungen") or {}
    if fx.get("neu") or fx.get("entfallen") or fx.get("geaendert"):
        with st.expander(f"Spielplan-Änderungen (neu {fx.get('neu', 0)} · entfallen {fx.get('entfallen', 0)} · "
                         f"geändert {len(fx.get('geaendert') or [])})"):
            for c in fx.get("geaendert") or []:
                st.markdown(f"- **{escape(c['liga'])}**, {escape(c['spiel'])}: "
                            + "; ".join(f"{escape(k)} {escape(str(c['vorher'][k]))} → {escape(str(c['neu'][k]))}" for k in c["neu"]))
    for key, title in (("unbekannte_teams", "Unbekannte Teams"), ("namensaenderungen_api", "Namensänderungen der API"),
                       ("wertungen", "Gewertete Spiele (von Hand entscheiden)")):
        if rep.get(key):
            with st.expander(f"{title} ({len(rep[key])})"):
                st.dataframe(pd.DataFrame(rep[key]), hide_index=True, width="stretch")


def history(reps: list[dict]) -> None:
    st.markdown("#### Protokoll der letzten 14 Tage")
    if not reps:
        st.caption("Noch keine Läufe.")
        return
    rows = []
    for r in reps:
        db = ((r.get("pruefung") or {}).get("datenbank") or {}).get("neu") or {}
        fx = r.get("spielplan_aenderungen") or {}
        st_txt = r.get("status", "–")
        note = r.get("meldung", "")
        tag = f'<span class="di-tag {TAG.get(st_txt, "t-g")}">{escape(st_txt)}{(": " + escape(note)) if note else ""}</span>'
        rows.append([_when(r.get("start")), num((r.get("anfragen") or {}).get("verbraucht")),
                     num(sum(len(v) for v in (r.get("neue_spiele") or {}).values())) if "neue_spiele" in r else "–",
                     num(len(r.get("korrekturen") or [])) if "korrekturen" in r else "–",
                     num(fx.get("neu", 0) + fx.get("entfallen", 0) + len(fx.get("geaendert") or [])) if fx else "–",
                     f'{num(db.get("fehler"))} Fehler · {num(db.get("warnungen"))} Warnungen' if db else "–", tag])
    st.markdown(_table(["Lauf", "Abfragen", "neue Spiele", "Korrekturen", "Spielplan", "Prüfung", "Status"], rows,
                       left=(0, 6)), unsafe_allow_html=True)
    st.markdown('<p class="di-note">Nach der Testphase verschwinden die Buttons; das Protokoll bleibt. Lieferungen mit '
                'Fehlern werden nie automatisch übernommen.</p>', unsafe_allow_html=True)


def render() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    ui.header(subtitle="Datenimport/API")
    base = E.IMPORT_DIR
    now = datetime.now(ZoneInfo(E.TIMEZONE))
    state = _read(base / "zustand.json") or {}
    reps = reports(base, E.HISTORY_DAYS)
    if not state and not reps:
        st.info("Noch kein Import gelaufen. Der Container soccer-import holt die Daten Montag bis Freitag um 04:00; "
                "ein erster Lauf lässt sich auf dem Server mit `docker exec soccer-import python -m importer.dienst "
                "--jetzt` starten.")
        ui.footer()
        return
    st.markdown(status_bar(state, reps[0] if reps else None, now), unsafe_allow_html=True)
    waiting = state.get("wartend")
    rep = next((r for r in reps if r.get("lauf") == waiting), None)
    if rep:
        pending_box(rep, base)
    else:
        st.success("Keine neuen Daten zur Freigabe. Die gültigen Dateien sind auf dem Stand des letzten übernommenen Laufs.")
    history(reps)
    st.caption(f"Gültige Datenbank: {settings.DATABASE_FILENAME} · Prüfregeln und Einzelheiten der Daten: Bereich Datenqualität")
    ui.footer()
