"""Bereich „Datenimport/API“ (Version 0.14, Designentwurf vom 15.11.2026, Dashboard-Briefing 6.5; seit 0.15 Entwurf 2).

Zeigt den Stand des Datenimports aus /import (nur lesend): Statusleiste, die wartende neue Fassung mit
- „Ihre Entscheidung“: späte Korrekturen der API und Endstände, die nicht zu den Tor-Ereignissen passen (je zwei Buttons),
- Block A · Ergebnisse (Vollständigkeit, Qualität, Korrekturen, neue Spiele) und
- Block B · Spielplan (Änderungen nach Gruppen),
sowie das Protokoll der letzten 14 Tage und seit 0.20 den Stand der Schnappschüsse (Überwachung; E-Mail-Alarm ab
0.22). Alle Buttons legen nur eine Anfrage in /import/anfragen ab; den Tausch und das
Festhalten der Entscheide macht der Container soccer-import (das Dashboard schreibt nie in die Excel-Dateien).
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from core import anzeige, settings
from core.files import file_key
from core.fixtures import load_fixtures
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
    """Nächster Kontrolllauf: täglich um 04:00 (seit 0.15 auch am Wochenende)."""
    ran_today = state.get("letzter_lauf_tag") == now.strftime("%Y-%m-%d")
    day = now + timedelta(days=1) if ran_today else now
    return day.replace(hour=E.RUN_HOUR, minute=0, second=0, microsecond=0)


def next_any(now: datetime, state: dict) -> tuple[datetime, str]:
    """Nächster Lauf überhaupt (seit 0.22): Kontrolllauf, Lauf nach dem Spiel oder Wiederholung."""
    from importer import laufplan
    fx = settings.DATA_DIR / settings.FIXTURES_FILENAME
    local = now.replace(tzinfo=None, microsecond=0)
    done = set(state.get("spiel_laeufe") or [])
    kandidaten = [(next_run(now, state).replace(tzinfo=None), "Kontrolllauf")]
    for tag in (local.date(), local.date() + timedelta(days=1)):
        kandidaten += [(z, "nach dem Spiel") for z in laufplan.plan(fx, tag)
                       if z > local and z.isoformat(timespec="minutes") not in done]
    w = state.get("wiederholung")
    if w:
        kandidaten.append((datetime.fromisoformat(w["um"]), f"Wiederholung {w['nr']}"))
    z, art = min(kandidaten)
    return z.replace(tzinfo=now.tzinfo), art


ANLASS = {"kontrolle": "Kontrolllauf", "spiel": "nach dem Spiel", "wiederholung": "Wiederholung"}


def plan_box(now: datetime, state: dict, reps: list[dict]) -> str:
    """„Läufe heute“ (seit 0.22): geplante Läufe nach dem Spiel und die schon gelaufenen des Tages."""
    from importer import laufplan
    fx = settings.DATA_DIR / settings.FIXTURES_FILENAME
    local = now.replace(tzinfo=None)
    heute = local.strftime("%Y-%m-%d")
    rows = [[_when(r.get("start")), escape(ANLASS.get(r.get("anlass", "kontrolle"), "–")),
             f'<span class="di-tag {TAG.get(r.get("status", ""), "t-g")}">{escape(r.get("status", "–"))}</span>']
            for r in reversed(reps) if (r.get("start") or "")[:10] == heute]
    done = set(state.get("spiel_laeufe") or [])
    rows += [[_when(z.isoformat()), "nach dem Spiel" + (": " + escape(", ".join(partien)) if partien else ""),
              '<span class="di-tag t-g">geplant</span>']
             for z, partien in laufplan.plan_mit_partien(fx, local.date())
             if z > local and z.isoformat(timespec="minutes") not in done]
    w = state.get("wiederholung")
    if w:
        rows.append([_when(w["um"]), f"Wiederholung {w['nr']}", '<span class="di-tag t-g">geplant</span>'])
    if not rows:
        return '<p class="di-note">Heute keine Läufe nach dem Spiel; nächster Kontrolllauf um 04:00.</p>'
    return ("<h4>Läufe heute</h4>" + _table(["Zeit", "Anlass", "Status"], rows, left=(0, 1, 2))
            + '<p class="di-note">Je Anstosszeit ein Lauf bei Anpfiff + 2¼ Stunden; fehlen danach Werte, folgt nach '
              '1 Stunde eine Wiederholung (höchstens zwei). Fehlerfreie Fassungen werden sofort übernommen.</p>')


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
                else "nach jedem Spiel und um 04:00, ohne Freigabe" if auto else "Freigabe von Hand")
    return (f'<div class="di-st"><div><small>Quelle</small><b>API-Football · {escape(abo.get("plan", "–"))}</b>{abo_txt}</div>'
            f'<div><small>Kontingent heute (Rest laut API)</small><b>{num(rest)}</b><small>eigene Obergrenze '
            f'{E.DAILY_LIMIT} je Tag</small></div>'
            f'<div><small>Letzter Lauf</small><b class="{last_css}">{_when(last)} {"✓" if ok else "✕"}</b>'
            f'<small>nächster: {_when(next_any(now, state)[0].isoformat())} · {next_any(now, state)[1]}</small></div>'
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
    return _table(["Liga", "Spieltag", "fällig", "geliefert", "verschoben / abgesagt / gewertet", "fehlt", "Stand"], rows)


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
        ["Plausibilität neuer/geänderter Spiele: Fehler / Warnungen", "–",
         f'{num(len((rep.get("plausibilitaet") or {}).get("fehler") or []))} / '
         f'{num(len((rep.get("plausibilitaet") or {}).get("warnungen") or []))}', "Grenzen: Ecken 30, Gelbe 10, aufs Tor 25, Tore 9 je Team"],
        ["Zuordnung Spielplan ↔ Datenbank, doppelte IDs", "–",
         num(len(rep.get("zuordnung") or []) + len(rep.get("doppelte_ids") or [])), "über die API-ID"],
        ["Unbekannte Teams", "–", num(len(rep.get("unbekannte_teams") or [])), "werden mit dem Namen der API übernommen"],
    ]
    return _table(["Prüfung", "gültige Fassung", "neue Fassung", "Bemerkung"], rows, left=(0, 3))


def write_request(base: Path, run_id: str | None, action: str, **extra) -> None:
    folder = base / "anfragen"
    folder.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo(E.TIMEZONE))
    payload = {"lauf": run_id, "aktion": action, "zeit": now.isoformat(timespec="seconds"), **extra}
    # Erst unter einem Namen schreiben, den der Dienst nicht liest, dann in einem Schritt umbenennen:
    # so findet er nie eine halb geschriebene Anfrage.
    name = f"{now:%Y%m%d_%H%M%S_%f}_{action}.json"
    tmp = folder / f".{name}.tmp"
    tmp.write_text(json.dumps(payload, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(folder / name)


def pending_requests(base: Path, run_id: str) -> list[str]:
    out = []
    for p in (base / "anfragen").glob("*.json"):
        req = _read(p) or {}
        if req.get("lauf") == run_id and req.get("aktion") in ("uebernehmen", "verwerfen"):
            out.append(req.get("aktion", ""))
    return out


def _decided(base: Path) -> set[tuple]:
    """Entscheide, die schon festgehalten sind oder als Anfrage warten: (Art, id, Spalte)."""
    keys = set()
    for e in _read(base / E.DECISIONS_FILE) or []:
        keys.add((e.get("art"), int(e.get("id", -1)), e.get("spalte")))
    for p in (base / "anfragen").glob("*.json"):
        req = _read(p) or {}
        if req.get("aktion") == "entscheid":
            keys.add((req.get("art"), int(req.get("id", -1)), req.get("spalte")))
    return keys


LABELS = {"uebernehmen": "API-Wert übernehmen", "ablehnen": "bisherigen Wert behalten",
          "platz": "Ergebnis auf dem Platz (Tor-Ereignisse)", "api": "Endstand der API"}


def decisions(rep: dict, base: Path) -> None:
    """„Ihre Entscheidung“: späte Korrekturen und Endstand gegen Tor-Ereignisse, je zwei Buttons (R1, R2)."""
    done = _decided(base)
    score = [k for k in rep.get("kritisch") or [] if k["art"] == "endstand"]
    late = rep.get("spaete_korrekturen") or []
    open_items = [("endstand", k, None) for k in score if ("endstand", int(k["id"]), None) not in done]
    open_items += [("korrektur", k, k["spalte"]) for k in late if ("korrektur", int(k["id"]), k["spalte"]) not in done]
    if not (score or late):
        return
    st.markdown('<div class="di-h">Ihre Entscheidung</div>', unsafe_allow_html=True)
    if not open_items:
        st.info("Alle Entscheide sind festgehalten. Sie wirken ab dem nächsten Lauf.")
        return
    for i, (art, k, col) in enumerate(open_items):
        if art == "endstand":
            text = (f"**{escape(k['liga'])}**, {escape(k['spiel'])} ({k.get('datum', '')}): Endstand der API "
                    f"**{k['api']}**, laut Tor-Ereignissen **{k['ereignisse']}** – Wertung oder Datenfehler? "
                    "Das Spiel wird bis zum Entscheid nicht aufgenommen bzw. nicht geändert.")
            options = ("platz", "api")
        else:
            text = (f"**{escape(k['liga'])}**, {escape(k['spiel'])} ({k['datum']}): späte Änderung der API "
                    f"(Spiel älter als {E.CORRECTION_DAYS} Tage) – {escape(k['spalte'])} "
                    f"**{escape(str(k['alt']))} → {escape(str(k['neu']))}**" + (" · KPI-relevant" if k.get("kpi") else ""))
            options = ("uebernehmen", "ablehnen")
        c0, c1, c2 = st.columns([5, 2, 2], vertical_alignment="center")
        c0.markdown(text)
        for c, opt in zip((c1, c2), options):
            if c.button(LABELS[opt], key=f"dec_{art}_{k['id']}_{col}_{opt}_{i}"):
                write_request(base, rep["lauf"], "entscheid", art=art, id=k["id"], liga=k["liga"], spiel=k["spiel"],
                              spalte=col, api_wert=k.get("neu") if art == "korrektur" else k.get("api"),
                              alt_wert=k.get("alt"), entscheid=opt)
                st.rerun()
    st.caption("Ein Entscheid wird festgehalten, mit der nächsten Übernahme gesichert und nie wieder gefragt. "
               "Er wirkt ab dem nächsten Lauf.")


def _fx_counts(fx: dict) -> tuple[int, int]:
    """(wichtige Änderungen, Anstosszeiten) – ältere Berichte ohne Gruppen zählen alles als wichtig."""
    if "gruppen" in fx:
        g = fx["gruppen"]
        return fx.get("wichtig", 0), len(g.get("anstoss", [])) + len(g.get("festgelegt", []))
    return fx.get("neu", 0) + fx.get("entfallen", 0) + len(fx.get("geaendert") or []), 0


GROUP_TITLES = {"verschoben": ("t-r", "verschoben, ohne neuen Termin"), "nachholspiel": ("t-b", "Nachholspiel (neuer Termin)"),
                "vorgezogen": ("t-w", "vorgezogen"), "termin": ("t-g", "Termin geändert"),
                "status": ("t-r", "ausgesetzt / abgesagt / abgebrochen / gewertet"),
                "anstoss": ("t-g", "Anstosszeit geändert"), "festgelegt": ("t-ok", "Anstosszeiten festgelegt (bisher offen)"),
                "vermerk": ("t-g", "Vermerk geändert")}


def _v(field: str, value) -> str:
    """Wert einer Spielplan-Änderung zum Anzeigen: leerer Status = geplant, sonst leer = „–“."""
    if value in (None, ""):
        return "geplant" if field == "Status" else "–"
    return escape(str(value))


def block_fixtures(rep: dict) -> None:
    fx = rep.get("spielplan_aenderungen") or {}
    st.markdown('<div class="di-h">B · Spielplan</div><p class="di-note">Wann gespielt wird. Bestimmt, was das '
                'Dashboard zeigt, und den Stichtag der KPIs.</p>', unsafe_allow_html=True)
    groups = fx.get("gruppen")
    if groups is None:                                   # Bericht aus 0.14
        st.markdown(f"Änderungen: neu {fx.get('neu', 0)} · entfallen {fx.get('entfallen', 0)} · "
                    f"geändert {len(fx.get('geaendert') or [])}")
        return
    if fx.get("neu") or fx.get("entfallen"):
        st.markdown(f"Spiele neu im Spielplan: **{fx.get('neu', 0)}** · entfallen: **{fx.get('entfallen', 0)}**")
    shown = False
    for key, (css, title) in GROUP_TITLES.items():
        items = groups.get(key) or []
        if not items:
            continue
        shown = True
        with st.expander(f"{title} ({len(items)})", expanded=key in ("verschoben", "nachholspiel", "vorgezogen", "status")):
            for c in items:
                st.markdown(f"- **{escape(c['liga'])}**, Sp. {c.get('spieltag', '')} · {escape(c['spiel'])}: "
                            + "; ".join(f"{escape(k)} {_v(k, c['vorher'][k])} → {_v(k, c['neu'][k])}" for k in c["neu"]))
    if not shown:
        st.markdown('<p class="di-note">Keine Änderungen an bestehenden Spielen.</p>', unsafe_allow_html=True)
    msgs = (rep.get("pruefung") or {}).get("spielplan", {}).get("meldungen") or []
    if msgs:
        with st.expander(f"Meldungen der Spielplan-Prüfung ({len(msgs)})"):
            st.dataframe(pd.DataFrame(msgs), hide_index=True, width="stretch")


def block_results(rep: dict) -> None:
    st.markdown('<div class="di-h">A · Ergebnisse (Datenbank)</div><p class="di-note">Was gespielt wurde. Grundlage '
                'aller KPI-Werte.</p>', unsafe_allow_html=True)
    st.markdown(completeness(rep), unsafe_allow_html=True)
    st.markdown(quality(rep), unsafe_allow_html=True)
    offen = rep.get("offen") or []
    missing = [(lg, m) for lg, mds in (rep.get("vollstaendigkeit") or {}).items() for m in mds if m["fehlende"] or m["inaktive"]]
    if offen or missing:
        with st.expander(f"Offen und verschoben ({len(offen) + sum(len(m['fehlende']) + len(m['inaktive']) for _, m in missing)})"):
            for o in offen:
                fields = ", ".join(o.get("fehlt") or [])
                st.markdown(f"- **{escape(o['liga'])}**, {escape(o['heim'])} – {escape(o['gast'])} ({o['datum']}): "
                            f"{escape(o['grund'])}" + (f" – fehlt: {escape(fields)}" if fields else ""))
            for lg, m in missing:
                for x in m["fehlende"]:
                    st.markdown(f"- **{escape(lg)}**, Spieltag {m['spieltag']}: {escape(x)} – noch kein Ergebnis")
                for x in m["inaktive"]:
                    st.markdown(f"- **{escape(lg)}**, Spieltag {m['spieltag']}: {escape(x)}")
    corr = rep.get("korrekturen") or []
    if corr:
        kpi = sum(1 for c in corr if c.get("kpi"))
        with st.expander(f"Korrekturen ({len(corr)}, davon {kpi} KPI-relevant)"):
            st.dataframe(pd.DataFrame(corr).astype(str), hide_index=True, width="stretch")
    games = rep.get("neue_spiele") or {}
    if any(games.values()):
        with st.expander(f"Neue Spiele ({sum(len(v) for v in games.values())})"):
            for league, rows in games.items():
                if rows:
                    st.markdown(f"**{escape(league)}**")
                    st.dataframe(pd.DataFrame(rows).drop(columns=["id"]), hide_index=True, width="stretch")
    plaus = rep.get("plausibilitaet") or {}
    msgs = (plaus.get("fehler") or []) + (plaus.get("warnungen") or [])
    msgs += [{"liga": z["liga"], "id": z.get("id"), "spiel": "", "meldung": z["meldung"]} for z in rep.get("zuordnung") or []]
    msgs += [{"liga": d["ligen"], "id": d["id"], "spiel": "", "meldung": "id doppelt"} for d in rep.get("doppelte_ids") or []]
    msgs += (rep.get("pruefung") or {}).get("datenbank", {}).get("neue_meldungen") or []
    if msgs:
        with st.expander(f"Meldungen der Prüfung ({len(msgs)})"):
            st.dataframe(pd.DataFrame(msgs).astype(str), hide_index=True, width="stretch")
    if rep.get("umbenennungen"):
        with st.expander(f"Teamnamen umgestellt ({len(rep['umbenennungen'])} Teams)"):
            st.dataframe(pd.DataFrame(rep["umbenennungen"]).rename(columns={"liga": "Liga", "alt": "bisher", "neu": "neu",
                                                                            "zeilen": "Zeilen"}),
                         hide_index=True, width="stretch")
    for key, title in (("unbekannte_teams", "Unbekannte Teams"), ("namensaenderungen_api", "Namensänderungen der API"),
                       ("wertungen", "Gewertete Spiele (nicht in der Datenbank)")):
        if rep.get(key):
            with st.expander(f"{title} ({len(rep[key])})"):
                st.dataframe(pd.DataFrame(rep[key]), hide_index=True, width="stretch")


@st.cache_data(show_spinner=False, max_entries=2)
def _staged_fixtures(path: str, key: tuple):  # noqa: ARG001 - key ist Teil des Cache-Schlüssels
    from state import get_database, get_leagues, get_teams
    return load_fixtures(path, get_leagues(), get_database().leagues, get_teams())


def preview(rep: dict, base: Path, now: datetime) -> None:
    """„So sieht das Dashboard nach der Übernahme aus“ (Entwurf 2, seit 0.16): je Liga, was Ligaseite und Top
    Anomalien mit dem neuen Spielplan zeigen würden."""
    path = base / "laeufe" / rep["lauf"] / settings.FIXTURES_FILENAME
    if not path.exists():
        return
    fx = _staged_fixtures(str(path), file_key(path))
    st.markdown(f"##### So sieht das Dashboard nach der Übernahme aus (heute {anzeige.day_text_year(now.date())})")
    if fx.has_errors:
        st.markdown('<p class="di-note">Der neue Spielplan enthält Fehler – keine Vorschau.</p>', unsafe_allow_html=True)
        return
    from state import get_active_leagues
    at = now.replace(tzinfo=None)
    rows = []
    for league in get_active_leagues():
        fixtures = fx.leagues.get(league.name)
        if fixtures is None or fixtures.empty:
            continue
        pv = anzeige.preview(fixtures, at)
        rows.append([escape(league.name), escape(pv.shown), escape(pv.games), escape(pv.top), escape(pv.until)])
    st.markdown(_table(["Liga", "Angezeigt (Kommende Spiele)", "Spiele", "Top Anomalien", "sichtbar bis"], rows,
                       left=(0, 1, 3, 4)), unsafe_allow_html=True)


def pending_box(rep: dict, base: Path) -> None:
    run_id, err = rep["lauf"], rep.get("fehler", 0) > 0
    new_games = sum(len(v) for v in (rep.get("neue_spiele") or {}).values())
    important, kickoff = _fx_counts(rep.get("spielplan_aenderungen") or {})
    critical = rep.get("kritisch") or []
    warn_new = len((rep.get("pruefung") or {}).get("datenbank", {}).get("neue_meldungen") or [])
    saison = ", ".join(sorted(set((rep.get("saison") or {}).values())))
    st.markdown(
        f'<div class="di-box{" err" if err else ""}"><h3>{"Neue Daten bereit" if not err else "Neue Fassung mit Fehlern"}</h3>'
        f'<p class="di-sub">Lauf {_when(rep.get("start"))} · Saison {escape(saison)} · '
        f'{"alle Spiele der Saison neu geprüft" if rep.get("ganze_saison") else "letzte 2 Spieltage neu geprüft"} · '
        f'aufgebaut auf der gültigen Datenbank ({escape((rep.get("basis") or {}).get("datenbank", "")[:8])})</p>'
        f'<div class="di-kp"><div><b>{new_games}</b><small>neue Spiele mit Ergebnis</small></div>'
        f'<div><b>{len(rep.get("korrekturen") or [])}</b><small>korrigierte Werte</small></div>'
        f'<div><b>{important}</b><small>Spielplan: wichtige Änderungen'
        f'{f" (+{kickoff} Anstosszeiten)" if kickoff else ""}</small></div>'
        f'<div><b class="{"di-bad" if err else "di-ok"}">{num(rep.get("fehler"))}</b><small>Fehler</small></div>'
        f'<div><b class="{"di-wn" if (critical or warn_new) else "di-ok"}">{len(critical) + warn_new}</b>'
        f'<small>kritische Punkte / neue Warnungen</small></div></div></div>',
        unsafe_allow_html=True)
    decisions(rep, base)
    others = [k for k in critical if k["art"] != "endstand"]
    for k in others:
        st.warning(f"**{escape(k['liga'])}**, {escape(k['spiel'])}: {escape(k['text'])}")
    a, b = st.columns(2, gap="medium")
    with a:
        block_results(rep)
    with b:
        block_fixtures(rep)
    preview(rep, base, datetime.now(ZoneInfo(E.TIMEZONE)))
    auto = rep.get("automatik") or {}
    if auto:
        st.caption("Im Automatikbetrieb: " + ("würde ohne Rückfrage übernommen" if auto.get("ok")
                                              else "würde auf Ihre Freigabe warten – " + "; ".join(auto.get("gruende") or [])))
    asked = pending_requests(base, run_id)
    if asked:
        st.info(f"Freigabe hinterlegt („{asked[0]}“). Der Import führt sie innerhalb einer Minute aus – Seite neu laden.")
        return
    c1, c2, c3 = st.columns([2, 1, 4])
    if c1.button("✓ Übernehmen (Ergebnisse und Spielplan)", type="primary", disabled=err, key="di_ok"):
        write_request(base, run_id, "uebernehmen")
        st.rerun()
    if c2.button("✕ Verwerfen", key="di_no"):
        write_request(base, run_id, "verwerfen")
        st.rerun()
    c3.markdown('<p class="di-note">A und B stammen aus derselben Abfrage und werden gemeinsam übernommen; die bisherige '
                'Fassung kommt mit Datum ins Backup. Bei Fehlern ist „Übernehmen“ gesperrt.</p>', unsafe_allow_html=True)


def history(reps: list[dict]) -> None:
    st.markdown("#### Protokoll der letzten 14 Tage")
    if not reps:
        st.caption("Noch keine Läufe.")
        return
    rows = []
    for r in reps:
        db = ((r.get("pruefung") or {}).get("datenbank") or {}).get("neu") or {}
        fx = r.get("spielplan_aenderungen") or {}
        important, kickoff = _fx_counts(fx)
        st_txt = r.get("status", "–")
        note = r.get("meldung", "")
        tag = f'<span class="di-tag {TAG.get(st_txt, "t-g")}">{escape(st_txt)}{(": " + escape(note)) if note else ""}</span>'
        rows.append([_when(r.get("start")), escape(ANLASS.get(r.get("anlass", "kontrolle"), "–")),
                     num((r.get("anfragen") or {}).get("verbraucht")),
                     num(sum(len(v) for v in (r.get("neue_spiele") or {}).values())) if "neue_spiele" in r else "–",
                     num(len(r.get("korrekturen") or [])) if "korrekturen" in r else "–",
                     f"{num(important)} · {num(kickoff)}" if fx else "–",
                     f'{num(db.get("fehler"))} Fehler · {num(db.get("warnungen"))} Warnungen' if db else "–", tag])
    st.markdown(_table(["Lauf", "Anlass", "Abfragen", "neue Spiele", "Korrekturen", "Spielplan (wichtig · Anstosszeiten)",
                        "Prüfung", "Status"], rows, left=(0, 1, 7)), unsafe_allow_html=True)
    st.markdown('<p class="di-note">Seit 0.22 ohne Freigabe: Fehlerfreie Fassungen werden sofort übernommen. Fassungen '
                'mit Fehlern oder neuen Warnungen warten auf Ihre Freigabe; kritische Spiele werden zurückgehalten und '
                'warten oben auf Ihren Entscheid.</p>', unsafe_allow_html=True)


def snapshot_box(stand: dict | None, now: datetime) -> str:
    """Stand des stündlichen Schnappschuss-Laufs (seit 0.20, core/schnappschuss.py): Werte je Spiel vor dem Anpfiff."""
    if not stand:
        return ('<div class="di-h">Schnappschüsse (Werte vor dem Anpfiff)</div><p class="di-note">Noch kein Lauf. Der '
                'Container soccer-import legt sie stündlich an; sofort: <code>docker exec soccer-import python -m '
                'importer.schnappschuss</code>.</p>')
    run = datetime.fromisoformat(stand["lauf"])
    age = now.replace(tzinfo=None) - run
    css = "di-bad" if stand.get("fehler") or age > timedelta(hours=2) else "di-ok"
    sign = "✕" if css == "di-bad" else "✓"
    waiting = stand.get("wartend") or []
    rows = [[escape(league), num(c.get("neu")), num(c.get("vorhanden")), num(c.get("wartend"))]
            for league, c in (stand.get("ligen") or {}).items()]
    text = (f'<div class="di-h">Schnappschüsse (Werte vor dem Anpfiff)</div>'
            f'<p class="di-note">Letzter Lauf <b class="{css}">{_when(stand["lauf"])} {sign}</b> · neu '
            f'{num(stand.get("neu"))} (davon nachträglich {num(stand.get("neu_nachtraeglich"))}) · erste Ergebnisse '
            f'{num(stand.get("ergebnisse_neu"))} · Dauer {stand.get("dauer_s", "–")} s · stündlich, nach jeder '
            f'Übernahme sofort</p>')
    if stand.get("fehler"):
        text += f'<p class="di-note di-bad">Fehler: {escape(stand["fehler"])}</p>'
    if rows:
        text += _table(["Liga", "neu", "vorhanden", "wartet auf Vorspiel-Ergebnis"], rows)
    if waiting:
        text += ('<p class="di-note">Wartet (Anpfiff nah oder vorbei, Ergebnis des vorherigen Spiels fehlt): '
                 + escape("; ".join(waiting)) + "</p>")
    return text


def names_box(paare: list[tuple[str, str]]) -> str:
    """Anzeigenamen der Website (seit 0.21, app/config/teamnamen_anzeige.csv): Vereine der laufenden Saison ohne
    Eintrag. Sie erscheinen auf der Website mit dem Namen der Datenquelle; die Veröffentlichung wird nicht blockiert."""
    from website.namen import fehlende
    fehlt = fehlende(paare)
    kopf = '<div class="di-h">Anzeigenamen der Website (Deutsch/Englisch)</div>'
    if not fehlt:
        return kopf + '<p class="di-note"><b class="di-ok">✓</b> Alle Vereine der laufenden Saison haben einen Anzeigenamen.</p>'
    return (kopf + f'<p class="di-note"><b class="di-wn">{num(len(fehlt))} Vereine ohne Anzeigenamen</b> – die Website '
            'zeigt dort den Namen der Datenquelle. Nachtragen in <code>app/config/teamnamen_anzeige.csv</code> '
            '(über GitHub).</p>' + _table(["Liga", "Name der Datenquelle"], [[escape(a), escape(b)] for a, b in fehlt], (0, 1)))


def _paare_laufende_saison() -> list[tuple[str, str]]:
    """(Liga, Verein) aller Spiele der jeweils neuesten Saison im Spielplan."""
    from state import get_fixtures
    paare = []
    for liga, plan in (get_fixtures().leagues or {}).items():
        if plan is None or plan.empty:
            continue
        neu = plan[plan["saison"] == max(plan["saison"])]
        paare += [(liga, n) for n in set(neu["heim"]) | set(neu["gast"])]
    return paare


def render() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    ui.header(subtitle="Datenimport/API")
    base = E.IMPORT_DIR
    now = datetime.now(ZoneInfo(E.TIMEZONE))
    state = _read(base / "zustand.json") or {}
    reps = reports(base, E.HISTORY_DAYS)
    if not state and not reps:
        st.info("Noch kein Import gelaufen. Der Container soccer-import holt die Daten täglich um 04:00; "
                "ein erster Lauf lässt sich auf dem Server mit `docker exec soccer-import python -m importer.dienst "
                "--jetzt` starten.")
        ui.footer()
        return
    st.markdown(status_bar(state, reps[0] if reps else None, now), unsafe_allow_html=True)
    if (base / "uebergabe.json").exists():               # Übergabe-Protokoll (0.15.1, F1)
        st.warning("Eine Übernahme läuft gerade oder wurde unterbrochen. Der Import führt sie selbst zu Ende "
                   "(spätestens beim nächsten Start bzw. Lauf); die bisherigen Dateien liegen im Backup.")
    waiting = state.get("wartend")
    rep = next((r for r in reps if r.get("lauf") == waiting), None)
    if rep:
        pending_box(rep, base)
    else:
        st.success("Alles übernommen. Die gültigen Dateien sind auf dem Stand des letzten übernommenen Laufs.")
        last = next((r for r in reps if str(r.get("status", "")).startswith("übernommen")), None)
        if last:                                       # zurückgehaltene Spiele warten auf den Entscheid (F1, 0.22)
            # Späte Korrekturen erkennt nur der Kontrolllauf: sie kommen aus dem letzten übernommenen Kontrolllauf,
            # alles andere aus dem letzten übernommenen Lauf.
            ctrl = next((r for r in reps if str(r.get("status", "")).startswith("übernommen")
                         and r.get("anlass", "kontrolle") == "kontrolle"), None)
            if ctrl is not None and ctrl is not last:
                last = {**last, "spaete_korrekturen": ctrl.get("spaete_korrekturen") or []}
            decisions(last, base)
            for k in [k for k in last.get("kritisch") or [] if k["art"] != "endstand"]:
                st.warning(f"**{escape(k['liga'])}**, {escape(k['spiel'])}: {escape(k['text'])}")
    st.markdown(plan_box(now, state, reps), unsafe_allow_html=True)
    history(reps)
    from importer.schnappschuss import load_status
    st.markdown(snapshot_box(load_status(base), now), unsafe_allow_html=True)
    try:
        st.markdown(names_box(_paare_laufende_saison()), unsafe_allow_html=True)
    except Exception as exc:                               # Spielplan nicht lesbar: Hinweis statt Abbruch
        st.caption(f"Anzeigenamen nicht geprüft: {exc}")
    st.caption(f"Gültige Datenbank: {settings.DATABASE_FILENAME} · Prüfregeln und Einzelheiten der Daten: Bereich Datenqualität")
    ui.footer()
