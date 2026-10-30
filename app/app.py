import streamlit as st

st.set_page_config(
    page_title="Fussball Analyse",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Fussball Analyse")
st.subheader("Bundesliga – Statistik und Auffälligkeiten")

st.info(
    "Die technische Grundlage steht. "
    "Im nächsten Schritt integrieren wir die Bundesliga-Daten."
)

st.markdown("### Geplante Funktionen")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Spiele", "Noch keine Daten")

with col2:
    st.metric("Statistiken", "In Vorbereitung")

with col3:
    st.metric("Auffälligkeiten", "In Vorbereitung")

st.divider()
st.caption("Version 0.1 – Erste Testversion")
