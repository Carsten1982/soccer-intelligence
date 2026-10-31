"""Datenqualität: alle Prüfergebnisse, Datenhinweise und Prüfregeln."""

import streamlit as st

from core.issues import FEHLER, HINWEIS, LEVEL_ORDER, WARNUNG
from state import fmt_dt, get_database, status_banner

st.title("🔎 Datenqualität")
db = get_database()
status_banner(db)
st.caption(f"Datei zuletzt geändert: {fmt_dt(db.file_modified)} · eingelesen: {fmt_dt(db.loaded_at)}")

a, b, c = st.columns(3)
a.metric("Fehler", db.count(FEHLER))
b.metric("Warnungen", db.count(WARNUNG))
c.metric("Hinweise", db.count(HINWEIS))

issues = db.issues_frame()
if issues.empty:
    st.success("Keine Auffälligkeiten.")
else:
    f1, f2 = st.columns(2)
    levels = f1.multiselect("Stufe", [FEHLER, WARNUNG, HINWEIS], default=[FEHLER, WARNUNG, HINWEIS])
    sheets = f2.multiselect("Blatt", sorted(issues["Blatt"].unique()), default=sorted(issues["Blatt"].unique()))
    view = issues[issues["Stufe"].isin(levels) & issues["Blatt"].isin(sheets)]
    view = view.sort_values("Stufe", key=lambda s: s.map(LEVEL_ORDER), kind="stable")
    st.dataframe(
        view, hide_index=True, width="stretch",
        column_config={"id": st.column_config.NumberColumn(format="%d"),
                       "Excel-Zeile": st.column_config.NumberColumn(format="%d")},
    )

if db.notes is not None and not db.notes.empty:
    with st.expander(f"Blatt »Datenhinweise« ({len(db.notes)} Einträge)"):
        st.dataframe(db.notes, hide_index=True, width="stretch")

with st.expander("Welche Prüfungen laufen?"):
    st.markdown(
        """
**Fehler** – Datenbank wird nicht verwendet, es werden keine Auswertungen angezeigt:
- Datei fehlt oder ist nicht lesbar (z. B. Upload unvollständig)
- Pflichtblatt *Bundesliga* oder *Premier League* fehlt oder ist leer
- Spaltenanzahl, Spaltennamen oder Reihenfolge weichen von den 58 erwarteten Spalten ab
- Pflichtfelder leer (Datum, Spieltag *Gameday*, id, Liga, Saison, Teams, Tore, Ergebnisse)
- Text statt Zahl, ungültiges Ergebnis (nur H/D/A), ungültiges Datum oder Saisonformat
- doppelte Spiel-id innerhalb eines Blatts

**Warnungen** – wahrscheinlich ein Datenfehler, die App läuft weiter:
- *FT* ≠ *Full-Time*, Halbzeiten ergeben nicht den Endstand, Ergebnisbuchstabe passt nicht
- Halbzeitwerte ergeben nicht den Gesamtwert (Ecken, Karten, Schüsse)
- Ballbesitz ergibt nicht 100 %, Schüsse gesamt kleiner als aufs Tor + daneben
- fehlende Statistikwerte, die nicht im Blatt *Datenhinweise* dokumentiert sind
- Saison unvollständig, doppelte Paarung, Datum passt nicht zu *matchDate*
- *Gameday* ausserhalb des möglichen Bereichs, Spieltag mit falscher Anzahl Spiele, Team mehrfach im selben Spieltag

**Hinweise** – kein Handlungsbedarf:
- mehr Tore als Schüsse aufs Tor (meist Eigentore)
- dokumentierte Sonderfälle mit leeren Statistikwerten (werden nie als 0 gerechnet)
- leere optionale Blätter (*Seria A*, *LaLiga*), neueste Saison noch laufend
        """
    )
