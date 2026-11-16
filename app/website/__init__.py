"""Öffentliche Website von Soccer Intelligence (seit Version 0.17, Konzept docs/08_Website.md).

Die Website rechnet nichts Eigenes: Welche Spiele erscheinen, entscheidet core/anzeige.py, die Werte und Stufen
kommen aus core/kpis.py – genau wie im Dashboard (Entscheidung F6: das Dashboard ist der Datenlieferant).

- einstellungen.py  Ligen, Adressen, Pfade
- format.py         Datum, Prozent, Ergebnis je Sprache (jetzt nur Deutsch)
- texte.py          Sprachdatei texte/de.json mit Schlüsseln
- daten.py          Laden von Datenbank, Spielplan, Schwellen und Importstand (mit Zwischenspeicher), Zeitreise
- spieltag.py       Datensatz der Seite Spieltag (Codes, keine Texte)
- seiten.py         HTML aus den Vorlagen (vorlagen/) erzeugen
- vorschau.py       kleiner Webserver für die Vorschau unter /vorschau (mit ?datum=…)
"""
