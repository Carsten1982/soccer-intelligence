"""Datenimport über API-Football (Version 0.14, Spezifikation docs/06_Datenlieferung.md).

Bausteine:
- client:     Abfragen mit Obergrenze, Wiederholungen, Rohdatenspeicher und Protokoll (ohne Schlüssel)
- convert:    Spiel der API -> Zeile mit den 58 Spalten der Datenbank (Abschnitt 5 der Spezifikation)
- spielplan:  Spielliste der API -> Spielplan im Format von 04_Spielplan.md
- teams:      feste Teamnamen je API-Team-ID (app/config/teamnamen.toml)
- erzeugen:   neue Fassung von Datenbank und Spielplan mit Bericht (Vollständigkeit, Qualität, Korrekturen)
- dienst:     Zeitplan (Montag bis Freitag 04:00), Freigabe aus dem Dashboard, Tausch mit Backup

Die gültigen Excel-Dateien werden nie bearbeitet: Es entsteht immer eine neue Fassung, die erst nach Freigabe (bzw.
später automatisch, wenn fehlerfrei) die gültige ersetzt.
"""
