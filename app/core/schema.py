"""Erwartete Struktur der Excel-Datenbank (Database-Soccer-Intelligence.xlsx).

Diese Datei beschreibt nur die Struktur. Sie enthält keine KPIs oder
fachlichen Analyse-Regeln.
"""

EXPECTED_COLUMNS: tuple[str, ...] = (
    'Date',
    'Gameday',
    'id',
    'matchDate',
    'Country',
    'League',
    'Season',
    'homeTeam',
    'awayTeam',
    'referee',
    'FT Home Goals',
    'FT Away Goals :',
    'FT Result :',
    'Full-Time Home Goals',
    'Full-Time Away Goals',
    'Full-Time Result',
    'First-Half Home Goals',
    'First-Half Away Goals',
    'First-Half Result',
    'Second-Half Home Goals',
    'Second-Half Away Goals',
    'Second-Half Result',
    'Home Corners Full Time',
    'Away Corners Full Time',
    'Home Corners First Half',
    'Away Corners First Half',
    'Home Corners Second Half',
    'Away Corners Second Half',
    'Home Yellow Cards Full Time',
    'Away Yellow Cards Full Time',
    'Home Yellow Cards First Half',
    'Away Yellow Cards First Half',
    'Home Yellow Cards Second Half',
    'Away Yellow Cards Second Half',
    'Home Ball Possession Full Time',
    'Away Ball Possession Full Time',
    'Home Ball Possession First Half',
    'Away Ball Possession First Half',
    'Home Ball Possession Second Half',
    'Away Ball Possession Second Half',
    'Home Team Shots Full Time',
    'Away Team Shots Full Time',
    'Home Team Shots First Half',
    'Away Team Shots First Half',
    'Home Team Shots Second Half',
    'Away Team Shots Second Half',
    'Home Shots on Target Full Time',
    'Away Shots on Target Full Time',
    'Home Shots on Target First Half',
    'Away Shots on Target First Half',
    'Home Shots on Target Second Half',
    'Away Shots on Target Second Half',
    'Home Shots off Target Full Time',
    'Away Shots off Target Full Time',
    'Home Shots off Target First Half',
    'Away Shots off Target First Half',
    'Home Shots off Target Second Half',
    'Away Shots off Target Second Half',
)

# --- Spaltengruppen -------------------------------------------------------

ID_COLUMNS = EXPECTED_COLUMNS[0:9]          # Date, Gameday ... awayTeam
REFEREE_COLUMN = EXPECTED_COLUMNS[9]        # referee
GOAL_BLOCK = EXPECTED_COLUMNS[10:22]        # FT, Full-Time, First-Half, Second-Half
STAT_COLUMNS = EXPECTED_COLUMNS[22:58]      # Ecken, Karten, Ballbesitz, Schüsse

RESULT_COLUMNS = tuple(c for c in GOAL_BLOCK if "Result" in c)
GOAL_COLUMNS = tuple(c for c in GOAL_BLOCK if "Result" not in c)

# Spalten, die nie leer sein dürfen (harter Fehler).
REQUIRED_COLUMNS = ID_COLUMNS + GOAL_BLOCK

# Spalten mit Zahlen. Statistikspalten dürfen leer sein (= keine Daten).
INTEGER_REQUIRED = ("Gameday", "id") + GOAL_COLUMNS
NUMERIC_OPTIONAL = STAT_COLUMNS

# Ganze Zahlen erwartet (seit H.1): alle Anzahlen. Nur der Ballbesitz (in %) darf Kommastellen haben.
POSSESSION_COLUMNS = tuple(c for c in STAT_COLUMNS if "Ball Possession" in c)
COUNT_COLUMNS = tuple(c for c in STAT_COLUMNS if c not in POSSESSION_COLUMNS)

VALID_RESULTS = frozenset({"H", "D", "A"})

# Zusammengehörige Tor-Spalten: (Heim, Auswärts, Ergebnis)
FT_SHORT = ("FT Home Goals", "FT Away Goals :", "FT Result :")
FULL_TIME = ("Full-Time Home Goals", "Full-Time Away Goals", "Full-Time Result")
FIRST_HALF = ("First-Half Home Goals", "First-Half Away Goals", "First-Half Result")
SECOND_HALF = ("Second-Half Home Goals", "Second-Half Away Goals", "Second-Half Result")

# Statistiken, bei denen 1. HZ + 2. HZ = Gesamt gelten muss.
# Format: (Anzeigename, Spaltenpräfix Heim, Spaltenpräfix Auswärts)
SUMMABLE_STATS = (
    ("Ecken", "Home Corners", "Away Corners"),
    ("Gelbe Karten", "Home Yellow Cards", "Away Yellow Cards"),
    ("Schüsse", "Home Team Shots", "Away Team Shots"),
    ("Schüsse aufs Tor", "Home Shots on Target", "Away Shots on Target"),
    ("Schüsse daneben", "Home Shots off Target", "Away Shots off Target"),
)
PERIODS = ("Full Time", "First Half", "Second Half")

POSSESSION = tuple(
    (p, f"Home Ball Possession {p}", f"Away Ball Possession {p}") for p in PERIODS
)

SEASON_PATTERN = r"^\d{4}/\d{4}$"
MATCHDATE_FORMAT = "%d-%m-%y %H:%M"

# Erwartete Spalten im Blatt "Datenhinweise"
NOTES_COLUMNS = ("Liga", "id", "Datum", "Begegnung", "Art", "Hinweis", "Geändert am", "Quelle")
