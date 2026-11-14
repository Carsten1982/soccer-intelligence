"""Bereich Datenqualität (Dashboard-Briefing, Kapitel 6): internes Kontrollblatt, nur Anzeige."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.issues import FEHLER, HINWEIS, LEVEL_ORDER, WARNUNG
from core.matchday import CURRENT, date_range, matchday_games, matchday_overview, season_short
from core.overview import games_per_season, league_summary, seasons_text
from state import (
    fixtures_banner, fmt_dt, get_active_leagues, get_database, get_fixtures, get_frequency, get_thresholds,
    status_banner, today,
)
from views import components as ui

DB_RULES = """
**Fehler** – Datenbank wird nicht verwendet, es werden keine Auswertungen angezeigt:
- Datei fehlt oder ist nicht lesbar (z. B. Upload unvollständig)
- Pflichtblatt *Bundesliga*, *Premier League*, *Serie A* oder *LaLiga* fehlt oder ist leer
- Spaltenanzahl, Spaltennamen oder Reihenfolge weichen von den 58 erwarteten Spalten ab
- Pflichtfelder leer (Datum, Spieltag *Gameday*, id, Liga, Saison, Teams, Tore, Ergebnisse)
- Text statt Zahl, ungültiges Ergebnis (nur H/D/A), ungültiges Datum (auch eine Zahl statt eines Datums) oder Saisonformat
- Kommazahl bei Toren, Spieltag *Gameday* oder id (dort sind nur ganze Zahlen erlaubt)
- doppelte Spiel-id innerhalb eines Blatts

**Warnungen** – wahrscheinlich ein Datenfehler, die App läuft weiter:
- *FT* ≠ *Full-Time*, Halbzeiten ergeben nicht den Endstand, Ergebnisbuchstabe passt nicht
- Halbzeitwerte ergeben nicht den Gesamtwert (Ecken, Karten, Schüsse)
- Ballbesitz ergibt nicht 100 %, Schüsse gesamt kleiner als aufs Tor + daneben
- Kommazahl bei Ecken, Karten oder Schüssen: Der Wert gilt als fehlend (nie abgeschnitten, nie 0); Ballbesitz darf
  Kommastellen haben
- fehlende Statistikwerte, die nicht im Blatt *Datenhinweise* dokumentiert sind (höchstens 50 Einzelzeilen je Stufe,
  danach eine Sammelzeile)
- Saison unvollständig, doppelte Paarung, Datum passt nicht zu *matchDate*
- Saison fehlt zwischen zwei vorhandenen Saisons (die Saison danach wird dann ohne Vorsaison berechnet)
- *Gameday* ausserhalb des möglichen Bereichs, Spieltag mit falscher Anzahl Spiele, Team mehrfach im selben Spieltag

**Hinweise** – kein Handlungsbedarf:
- mehr Tore als Schüsse aufs Tor (meist Eigentore)
- dokumentierte Sonderfälle mit leeren Statistikwerten (werden nie als 0 gerechnet)
- unbekannte zusätzliche Blätter (werden ignoriert), neueste Saison noch laufend
"""

FIXTURE_RULES = """
**Fehler** – Spielplan wird nicht verwendet, das Dashboard zeigt einen Hinweis statt der Tabelle:
- Datei fehlt oder ist nicht lesbar
- Tabellenblatt einer aktiven Liga fehlt
- Pflichtspalte fehlt oder ist falsch geschrieben (*Saison, Spieltag, Datum von, Datum bis, Heimmannschaft, Gastmannschaft*)
- Pflichtfeld leer
- *Datum von* oder *Datum bis* ist kein Excel-Datum (z. B. Zeitraum als Text), *Datum bis* liegt vor *Datum von*
- *Spieltag* ist keine ganze Zahl ab 1, *Saison* nicht im Format JJJJ/JJJJ
- *Status* enthält einen nicht erlaubten Wert (erlaubt: leer, geplant, verschoben, abgesagt)

**Warnungen** – Spielplan wird verwendet, sollte aber geprüft werden:
- Teamname unbekannt (weder in der Datenbank noch in der Teamliste): Aufsteiger oder Schreibfehler?
- Team kommt im selben Spieltag mehrfach vor, Heim- und Gastmannschaft identisch
- weniger Spiele in einem Spieltag als erwartet (Anzahl Teams / 2 laut Konfiguration)
- dieselbe Paarung kommt in einer Saison mehrfach vor
- Tabellenblatt einer aktiven Liga ist leer

**Hinweise** – kein Handlungsbedarf:
- bekannter Aufsteiger (Teamliste) ohne Daten in der Datenbank
- Team ohne Ligaspiele in Saison und Vorsaison (KPIs erscheinen als „–“)
- Begegnung steht bereits als gespieltes Spiel in der Datenbank
- leeres Tabellenblatt einer noch nicht aktiven Liga
"""


def _issue_table(issues: pd.DataFrame, key: str) -> None:
    if issues.empty:
        st.success("Keine Auffälligkeiten.")
        return
    f1, f2 = st.columns(2)
    levels = f1.multiselect("Stufe", [FEHLER, WARNUNG, HINWEIS], default=[FEHLER, WARNUNG, HINWEIS], key=f"{key}_lvl")
    sheets = sorted(issues["Blatt"].unique())
    chosen = f2.multiselect("Blatt", sheets, default=sheets, key=f"{key}_sheet")
    view = issues[issues["Stufe"].isin(levels) & issues["Blatt"].isin(chosen)]
    view = view.sort_values("Stufe", key=lambda s: s.map(LEVEL_ORDER), kind="stable")
    config = {c: st.column_config.NumberColumn(format="%d") for c in ("id", "Excel-Zeile") if c in view.columns}
    st.dataframe(view, hide_index=True, width="stretch", column_config=config)


def _database_section() -> None:
    db = get_database()
    status_banner(db)

    st.markdown("#### Datenstand")
    st.markdown(
        f"- **Datei:** `{db.path.name}`\n"
        f"- **Zuletzt geändert:** {fmt_dt(db.file_modified)} · **eingelesen:** {fmt_dt(db.loaded_at)}\n"
        f"- **SHA-256:** `{(db.sha256 or '-')[:16]}…`"
    )
    if db.leagues:
        cols = st.columns(len(db.leagues))
        for col, (name, df) in zip(cols, db.leagues.items()):
            s = league_summary(df)
            with col, st.container(border=True):
                st.markdown(f"**{name}**")
                a, b = st.columns(2)
                a.metric("Spiele", f"{s['Spiele']:,}".replace(",", "."))
                b.metric("Teams", s["Teams"])
                st.caption(f"{s['Saisons']} Saisons ({s['Erste Saison']} – {s['Letzte Saison']}) · "
                           f"{s['Erstes Spiel']:%d.%m.%Y} bis {s['Letztes Spiel']:%d.%m.%Y}")
                st.caption(seasons_text(s))
        st.markdown("**Spiele je Saison**")
        st.dataframe(games_per_season(db.leagues), width="stretch")

    st.markdown("#### Prüfergebnisse")
    a, b, c = st.columns(3)
    a.metric("Fehler", db.count(FEHLER))
    b.metric("Warnungen", db.count(WARNUNG))
    c.metric("Hinweise", db.count(HINWEIS))
    _issue_table(db.issues_frame(), "db")

    if db.notes is not None and not db.notes.empty:
        with st.expander(f"Blatt »Datenhinweise« ({len(db.notes)} {'Eintrag' if len(db.notes) == 1 else 'Einträge'})"):
            st.dataframe(db.notes, hide_index=True, width="stretch")
    with st.expander("Welche Prüfungen laufen? (Datenbank)"):
        st.markdown(DB_RULES)


def _overview_frame(overview) -> pd.DataFrame:
    return pd.DataFrame([{
        "Saison": season_short(m.saison),
        "Spieltag": m.spieltag,
        "Erstes Datum": f"{m.erstes_datum:%d.%m.%Y}",
        "Letztes Datum": f"{m.letztes_datum:%d.%m.%Y}",
        "Spiele": m.anzahl,
        "Status": m.status,
    } for m in overview])


def _highlight_current(row: pd.Series) -> list[str]:
    style = "background-color:#e3ecf8; font-weight:700" if row["Status"] == CURRENT else ""
    return [style] * len(row)


def _fixtures_section() -> None:
    fx = get_fixtures()
    fixtures_banner(fx)
    heute = today()

    st.markdown("#### Datenstand")
    st.markdown(
        f"- **Datei:** `{fx.path.name}`\n"
        f"- **Zuletzt geändert:** {fmt_dt(fx.file_modified)} · **eingelesen:** {fmt_dt(fx.loaded_at)}\n"
        f"- **Heute (Europe/Zurich):** {heute:%d.%m.%Y}"
    )

    st.markdown("#### Spieltage")
    if fx.has_errors:
        st.info("Die Spieltagsübersicht erscheint, sobald die Fehler im Spielplan behoben sind.")
    else:
        st.caption("aktuell = wird im Dashboard angezeigt · beendet = spätestes „Datum bis“ liegt vor heute · "
                   "kommend = noch nicht beendet")
        for league in get_active_leagues():
            fixtures = fx.leagues.get(league.name)
            overview = matchday_overview(fixtures, heute) if fixtures is not None else []
            st.markdown(f"**{league.name}**")
            if not overview:
                st.caption("Keine Spieltage im Spielplan.")
                continue
            frame = _overview_frame(overview)
            st.dataframe(frame.style.apply(_highlight_current, axis=1), hide_index=True, width="stretch")
            for m in overview:
                title = (f"Saison {season_short(m.saison)} · Spieltag {m.spieltag} · "
                         f"{date_range(m.erstes_datum, m.letztes_datum)} · {m.status}")
                with st.expander(title, expanded=False):
                    games = matchday_games(fixtures, m.saison, m.spieltag)
                    table = pd.DataFrame([{
                        "Begegnung": f"{g.heim} – {g.gast}",
                        "Datum": date_range(g.datum_von, g.datum_bis),
                        "Status": g.status,
                        "Hinweise": "; ".join(
                            f"{t}: {fx.team_notes[(league.name, g.saison, t)]}"
                            for t in (g.heim, g.gast) if (league.name, g.saison, t) in fx.team_notes
                        ),
                    } for g in games.itertuples()])
                    st.dataframe(table, hide_index=True, width="stretch")

    st.markdown("#### Prüfergebnisse")
    a, b, c = st.columns(3)
    a.metric("Fehler", fx.count(FEHLER))
    b.metric("Warnungen", fx.count(WARNUNG))
    c.metric("Hinweise", fx.count(HINWEIS))
    _issue_table(fx.issues_frame(), "fx")
    with st.expander("Welche Prüfungen laufen? (Spielplan)"):
        st.markdown(FIXTURE_RULES)


def _thresholds_section() -> None:
    """Gültige Schwellenwerte (Briefing 6.3, Etappe H): nur Anzeige, Änderung bewusst über die Datei."""
    from core.thresholds import describe
    st.markdown("#### Gültige Schwellenwerte")
    st.caption("Aus `app/config/schwellen.toml` · eingestuft wird die auf zwei Nachkommastellen gerundete "
               "Abweichung: Anomalie, wenn sie über der positiven bzw. unter der negativen Schwelle liegt (genau auf "
               "der Schwelle zählt zur schwächeren Stufe) · KPI 03 je Liga · Änderungen nur über die Datei (Neubau, "
               "Git, CHANGELOG), nicht hier.")
    rows = describe(get_thresholds())
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=(len(rows) + 1) * 35 + 3)   # ohne Scrollen


def _frequency_section() -> None:
    _thresholds_section()
    st.markdown("#### Häufigkeit je Liga und KPI")
    st.caption("Wie oft zeigen KPI 02–09 keine, leichte oder starke Anomalien? Grundlage: alle Spiele der letzten "
               "abgeschlossenen Saison, jeweils so berechnet, als wären sie noch nicht gespielt. Dient der Überprüfung "
               "der Schwellenwerte je Liga und KPI.")
    db = get_database()
    if db.has_errors:
        st.info("Wird angezeigt, sobald die Datenbank fehlerfrei ist.")
        return
    for league in get_active_leagues():
        season, table = get_frequency(league)
        st.markdown(f"**{league.name}**" + (f" · Saison {season_short(season)}" if season else ""))
        if season is None:
            st.caption("Keine vollständige Saison in der Datenbank (ausser der Referenzsaison, "
                       "die nie ausgewertet wird).")
            continue
        st.dataframe(table, hide_index=True, width="stretch")


def render() -> None:
    ui.header()
    st.markdown("### Datenqualität")
    st.caption("Internes Kontrollblatt. Daten werden hier nur angezeigt, nicht bearbeitet.")
    tab_db, tab_fx, tab_freq = st.tabs(["Datenbank", "Spielplan und Spieltage", "Häufigkeit der Anomalien"])
    with tab_db:
        _database_section()
    with tab_fx:
        _fixtures_section()
    with tab_freq:
        _frequency_section()
    ui.footer()
