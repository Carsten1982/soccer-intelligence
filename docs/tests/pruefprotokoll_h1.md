# Prüfprotokoll H.1 – Aufräumen und Tempo (Version 0.9.1)

**Datum:** 08.11.2026 · **Geprüft von:** Claude · **Datenbank:** SHA-256 `f37e36d3…` · **Spielplan:** Stand 07.11.2026

Ziel: Die Funde der Code-Prüfung beheben, **ohne dass sich ein einziges Ergebnis ändert**. Carsten muss danach nur noch kurz im Browser schauen, ob alles wie bisher aussieht.

---

## 1. Vorher/Nachher-Vergleich (alle Begegnungen)

Gleicher Ablauf wie im Vollvergleich von Etappe H: jedes Spiel der Datenbank als analysiertes Spiel (Stichtag = Spieldatum, Spieltag = `Gameday`) plus alle Begegnungen des Spielplans. Einmal mit dem Code von Etappe H (Git `51e595b`), einmal mit H.1. Verglichen wurde das **vollständige Ergebnis** je Begegnung: Formkurve, alle Teamwerte, Ligareferenzen, Hauptwerte, Abweichungen, Einstufungen, „vorläufig“, Überschriften, Texte und die verwendeten Spiel-ids.

| Liga | Begegnungen | Abweichungen |
|---|---|---|
| Bundesliga | 1'863 | 0 |
| Premier League | 2'310 | 0 |
| Serie A | 2'310 | 0 |
| LaLiga | 2'325 | 0 |
| **Gesamt** | **8'808** | **0** |

Ebenfalls identisch: die Häufigkeit der Anomalien aller vier Ligen (alle Zahlen und Anteile) und die 60 Prüfmeldungen der Datenbank.

## 2. Gegenrechnung und Seiten

| Prüfung | Ergebnis |
|---|---|
| App gegen unabhängige Gegenrechnung (`tests/gegenrechnung.py`), alle 8'808 Begegnungen | 0 Abweichungen |
| Alle Seiten (Top Anomalien, vier Ligen, Datenqualität) erzeugt und das HTML verglichen | Inhalt identisch; nur das CSS der alten Tabelle fehlt (rund 1'900 Zeichen weniger) |
| Ungültige `schwellen.toml` bzw. `teams.toml` beim Start | Meldung „Konfiguration ungültig: …“, kein Absturz |
| KPI-Ergebnisse eines Spieltags im Zwischenspeicher (pickle, wie Streamlit) | 124 kB für 39 Begegnungen, Laden 2 ms, Inhalt identisch |

## 3. Tests

| Bereich | Neu |
|---|---|
| Kommazahl bei Toren, `Gameday`, `id` → Fehler; bei Ecken → Warnung und Wert fehlt; Ballbesitz mit Kommastellen erlaubt | 5 Tests |
| KPI-Berechnung und Gegenrechnung: Kommazahl gilt als fehlend (z. B. Spiel mit 4,5 Ecken fällt weg) | 12 Tests |
| Kaputtes XML in Datenbank und Spielplan → „Datei nicht lesbar“ | 2 Tests |
| Datenhinweise ohne Spalte `Liga` → kein Absturz | 1 Test |
| „Statistik fehlt“ höchstens 50 Meldungen je Stufe | 1 Test |
| Geteilte Ligareferenzen liefern dieselben Ergebnisse (Mini-Daten und echte Spieltage 17/18 der Bundesliga 2025/26) | 2 Tests |
| Anteile kaufmännisch gerundet (0,125 % → 0,13 %) | 6 Tests |
| Spieltags-KPIs aus `core/results.py`, Spieltage je Liga | 2 Tests |

Entfernt: 2 Tests der alten Tabelle, 2 doppelte Tests. Lokal: **279 bestanden**, 9 übersprungen (8 Seitentests brauchen Streamlit, 1 Spielplan-Test gilt nur für den alten Stand). Auf dem Server laufen die 8 Seitentests mit: erwartet **rund 287 bestanden, 1 übersprungen**.

## 4. Zeitmessung (lokal, gleiche Daten)

| Vorgang | Etappe H | H.1 |
|---|---|---|
| Häufigkeit der Anomalien, vier Ligen (1'446 Spiele) | 28,7 s | 5,8 s |
| Aktueller Spieltag, vier Ligen (39 Begegnungen) | 0,76 s | 0,18 s, danach aus dem Zwischenspeicher |
| Alle 8'808 Begegnungen | 178,6 s | 50,5 s |

## 5. Bewusst nicht umgesetzt

- **R9** (`except Exception` um `st.page_link` enger fassen): lässt sich ohne echtes Streamlit nicht prüfen. Bleibt, wie es ist.
- **A6** (nur ein Rechenweg für KPI 02–04) und **L5** (Zeilen einmal je Liga): grösserer Umbau, sinnvoll mit Etappe I.

## 6. Was Carsten noch prüfen sollte

Nur kurz im Browser: Startseite, eine Liga (Zeile aufklappen), Datenqualität → Häufigkeit (sollte jetzt nach wenigen Sekunden erscheinen). Rechnerisch ist nichts offen.
