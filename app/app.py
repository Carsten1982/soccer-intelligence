"""Soccer Intelligence – Einstiegspunkt und Navigation."""

import streamlit as st

from core import settings

st.set_page_config(page_title="Soccer Intelligence", page_icon="⚽", layout="wide")

pages = [
    st.Page("views/uebersicht.py", title="Übersicht", icon="🏠", default=True),
    st.Page("views/datenqualitaet.py", title="Datenqualität", icon="🔎"),
]

nav = st.navigation(pages)
st.sidebar.caption(f"Version {settings.APP_VERSION}")
nav.run()
