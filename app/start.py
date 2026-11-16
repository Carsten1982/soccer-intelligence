"""Startet das Dashboard (Version 0.15.1, Code-Prüfung F4).

Wie bisher `streamlit run app.py …`, zusätzlich startet sofort der Vorlade-Helfer (vorladen.py). So sind nach einem
Neustart des Containers – z. B. nach dem Einspielen – alle Seiten vorbereitet, auch bevor jemand das Dashboard öffnet.
Aufruf (Dockerfile): python start.py --server.address=0.0.0.0 --server.port=8501
"""

import sys

from streamlit.web import cli

import vorladen

if __name__ == "__main__":
    vorladen.start()
    sys.argv = ["streamlit", "run", "app.py", *sys.argv[1:]]
    sys.exit(cli.main())
