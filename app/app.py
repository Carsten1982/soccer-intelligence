"""Soccer Intelligence – Einstiegspunkt und Navigation (Dashboard-Briefing, Kapitel 2 und 3).

Bereiche (Tabs oben):
  Top Anomalien (Startbereich)  ·  je aktive Liga ein Bereich  ·  Datenqualität  ·  Sensitivitätsanalyse (intern)  ·
  Datenimport/API (intern, ganz rechts, seit Version 0.14)

Zugang (seit 0.15.2): Anmeldemaske mit Benutzername und Passwort (anmeldung.py) statt der Passwortabfrage des Browsers.

Welche Ligen aktiv sind, steht in config/ligen.toml, nicht im Programmcode. Ist eine der Konfigurationsdateien
(ligen.toml, teams.toml, schwellen.toml) ungültig, zeigt die App nur eine klare Meldung.
"""

import streamlit as st

from core.config import ConfigError
from state import get_active_leagues, get_teams, get_thresholds
from views import components as ui
from views import datenimport, datenqualitaet, liga, simulation, top_anomalien
from views.registry import PAGES

import anmeldung
import vorladen

st.set_page_config(page_title="Soccer Intelligence", page_icon="⚽", layout="wide")
ui.inject_css()
vorladen.start()                       # Hintergrund-Helfer: rechnet nach jeder Datenänderung alles vor (0.15.1, F4)
anmeldung.require_login()              # Anmeldemaske; ohne gültige Anmeldung endet die Seite hier (0.15.2)

try:                                   # alle drei Konfigurationsdateien vorab prüfen (H.1)
    leagues = get_active_leagues()     # ligen.toml
    get_teams()                        # teams.toml
    get_thresholds()                   # schwellen.toml
except ConfigError as exc:
    ui.header()
    st.error(f"**Konfiguration ungültig:** {exc}", icon="⛔")
    st.stop()


def _league_page(league):
    """Erzeugt die Seitenfunktion für eine Liga (eigener Funktionsname je Liga)."""
    def page():
        liga.render(league)
    page.__name__ = f"liga_{league.url.replace('-', '_')}"
    return page


PAGES["top"] = st.Page(top_anomalien.render, title="Top Anomalien", url_path="top-anomalien", default=True)
league_pages = [st.Page(_league_page(lg), title=lg.name, url_path=lg.url) for lg in leagues]
for lg, page in zip(leagues, league_pages):
    PAGES[f"liga_{lg.url}"] = page
PAGES["datenqualitaet"] = st.Page(datenqualitaet.render, title="Datenqualität", url_path="datenqualitaet")
PAGES["simulation"] = st.Page(simulation.render, title="Sensitivitätsanalyse",
                              url_path="simulation")   # intern; Name seit 0.12, Adresse unverändert

PAGES["datenimport"] = st.Page(datenimport.render, title="Datenimport/API", url_path="datenimport")   # seit 0.14

nav = st.navigation([PAGES["top"], *league_pages, PAGES["simulation"], PAGES["datenqualitaet"], PAGES["datenimport"]],
                    position="top")             # seit 0.19.1: Sensitivitätsanalyse vor Datenqualität (Carsten)
nav.run()
anmeldung.logout_button()              # „Abmelden“ unten auf jeder Seite (0.15.2)
