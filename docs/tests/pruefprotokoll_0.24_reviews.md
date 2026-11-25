# Prüfprotokoll 0.24 – Frontend- und Backend-Review (ChatGPT), Bewertung durch Claude

**Stand:** 24.11.2026 · Grundlage: Reviews von ChatGPT zu Version 0.23 (Pakete vom 24.11.2026) · Entscheide Carsten 24.11.2026

Grundsatz: so viel verbessern wie nötig, so wenig verändern wie möglich. Jeder Punkt wurde am Code geprüft; Messungen
lokal (4 Kerne, Testdaten). **Rechenkern (`app/core/`) unverändert** – KPI-Ergebnisse können sich nicht ändern.

## 1. Messungen

| Was | vorher (0.23) | nachher (0.24) |
|---|---|---|
| Startseite, 1 Aufruf | 0,37 s | 0,001 s (aus dem Seitenspeicher) |
| Startseite, 10 gleichzeitig (langsamster) | 7,6 s | 0,01 s |
| Startseite, 50 gleichzeitig | – | Median 0,01 s; langsamster ≈ 1 s einmal je Minute (Neuberechnung) |
| Ursache (Profiler) | `start_daten` rechnet bei jedem Aufruf Ranking, „Werte ab“ und Top-Block aller vier Ligen mit vielen kleinen pandas-Abfragen; Python rechnet in einem Prozess nicht parallel | – |
| Touch-Ziele (iPhone-Profil) | ≥ 44 px ausser „Zahlen im Detail“ (36 px) und Chip ⓘ (28 px) | „Zahlen im Detail“ 44 px; ⓘ Trefferfläche 44 px (unsichtbar) |
| HTTP-Protokoll Browser ↔ Traefik | HTTP/2 (Test Carsten) | unverändert |
| HSTS | fehlt (Test Carsten) | per Label |

## 2. Backend-Review

| Nr. | Befund (Review) | Prüfung am Code | Entscheid |
|---|---|---|---|
| A1/A2 | Slowloris, keine Socket-Timeouts | bestätigt: `Handler` ohne `timeout` | **umgesetzt:** `timeout = 20` |
| A3 | keine Begrenzung gleichzeitiger Anfragen | bestätigt, aber Traefik-Rate-Limit (30/s je Adresse) davor; eigentliche Ursache war die Rechenzeit | **umgesetzt über den Seitenspeicher** (gleiche Seite nur einmal je Minute gerechnet); keine eigene Sperre |
| A4 | `Content-Length` negativ/ungültig | **bestätigt:** `-5` führte zu `read(-5)` = Lesen bis Verbindungsende | **umgesetzt:** 400 bei ungültig/negativ, 413 bei zu gross, vor dem Lesen (Test R1) |
| A5 | IP im Dashboard anders als im Kontaktformular | **bestätigt:** Dashboard nahm den **ersten** `X-Forwarded-For`-Eintrag (vom Besucher fälschbar → Sperre nach Fehlversuchen umgehbar) | **umgesetzt:** letzter Eintrag (von Traefik), Funktion `adresse_aus` (Test R2) |
| A6 | IP hängt an Traefik-Konfiguration | zutreffend, aber gewollt: Traefik hängt die echte Adresse an | keine Änderung |
| A7 | Bremse nicht atomar | bestätigt (Prüfen und Merken getrennt) | **umgesetzt:** `reservieren()` in einem Schritt, `freigeben()` bei gescheitertem Versand (Test R3) |
| A8 | IP-Einträge unbegrenzt | teilweise: Aufräumen fand nur leere Einträge | **umgesetzt:** abgelaufene Adressen werden entfernt |
| A9 | Einwilligung zu grosszügig geprüft | jeder nicht leere Wert zählt; Formular sendet nur „ja“ | keine Änderung (kein Risiko) |
| A10 | Rechenaufgabe wiederverwendbar (2 h) | bestätigt | keine Änderung: Schutz ist die Bremse (3/h je Adresse), die Aufgabe nur eine Hürde |
| A11 | Dashboard-Cookie nicht HttpOnly | bestätigt; Streamlit kann Cookies nur per Skript setzen | keine Änderung: signiert, 12 h, `Secure`, `SameSite=Strict`; internes Werkzeug |
| A12 | Login-Sperre nur im Prozess | zutreffend; Streamlit läuft als ein Prozess, Sperre mit Lock | keine Änderung |
| B | ZIP-Weg kann `.env` überschreiben | **bestätigt:** Python macht aus `../.env` ein `.env` im Projektordner | **umgesetzt:** ZIP-Weg ganz entfernt (Entscheid Carsten 24.11.2026); nur noch `github` |
| B | Rechte von `.env` und Kopien | Skripte schreiben mit `umask 077`; Kopien in `backup/` | keine Änderung |
| C | Container als root | bestätigt | **nach dem Livegang** (Entscheid Carsten, `01` Abschnitt 8): braucht Besitzerwechsel von `data/`, `import/`, `backup/` auf dem Server – zu riskant kurz vor dem Livegang |
| C | `no-new-privileges` fehlt | bestätigt | **umgesetzt** für unsere drei Container (Platzhalter unverändert, entfällt beim Livegang) |
| C | keine CPU-/RAM-Grenzen | bestätigt | **umgesetzt** nach Messung (Ruhezustand 108–168 MiB): `mem_limit` 1 GB / 1,5 GB (Import) / 1 GB; CPU-Grenzen nicht nötig (1 vCPU) |
| C | Root-Dateisystem schreibbar | bestätigt | später (Streamlit schreibt Zwischendateien) |
| D | Datenbank und Spielplan nicht gemeinsam getauscht | bestätigt; Website lädt neu, sobald sich eine Datei ändert → kurz gemischter Stand möglich (selbstheilend) | **umgesetzt:** Website behält den bisherigen Stand, solange `import/uebergabe.json` steht (höchstens 10 Min.; Test R5). Dashboard (intern) unverändert |
| E1–E4 | Startseite rechnet jedes Mal neu, gleichzeitige Misses | bestätigt (Messung oben) | **umgesetzt:** Seitenspeicher je Adresse, Datenstand, Minute (Test R4) |
| E5 | Speicherbedarf der Container | gemessen (Carsten 24.11.2026): Dashboard 168 MiB, Import 108 MiB, Vorschau 111 MiB von 3,8 GiB | unkritisch; Grenzen gesetzt |
| E6 | Sensitivitätsanalyse, Testdauer | zutreffend (≈ 13 Min.) | keine Änderung vor dem Livegang |
| F | `requests==2.32.3` | bekannte Schwachstelle (.netrc, behoben in 2.32.4) | **umgesetzt:** 2.32.5 |

## 3. Frontend-Review

| Nr. | Empfehlung | Entscheid |
|---|---|---|
| 1 | Komprimierung | **umgesetzt** per Label (`soccerintel-compress`); Prüfung nach dem Livegang (`01`, Abschnitt 8) |
| 2 | HTTP-Protokoll | erledigt: HTTP/2 zwischen Browser und Traefik |
| 3 | Schriften | Preload beider Schriften nötig; Ersatzschriften mit `size-adjust`: später |
| 4, 6 | Critical CSS, DOM | nicht umsetzen |
| 5 | Server-Performance | **umgesetzt** (Seitenspeicher) |
| 7 | Touch-Ziele | „Zahlen im Detail“ 44 px **umgesetzt** (Entscheid Carsten); ⓘ: grössere Trefferfläche ohne sichtbare Änderung **umgesetzt** |
| 8 | `:active` | später |
| 9 | `theme-color` | **umgesetzt** |
| 10 | Manifest | **umgesetzt** (`display: browser`, Icons aus dem Favicon; Entscheid Carsten) |
| 11–13 | Prefetch, View Transitions, Service Worker | später bzw. nicht |
| 14 | Index Spielseiten | **umgesetzt:** mindestens 6 von 8 Kennzahlen (Entscheid Carsten) |
| 15, 16, 18, 20 | Archiv, SEO-Grundstruktur, lastmod, Fehlerseiten | bereits gut bzw. nicht umsetzen |
| 17 | SportsEvent | **entfernt** (Entscheid Carsten) |
| 19 | HSTS, Permissions-Policy | **umgesetzt** |
| 21, 22 | Manuelle A11y, Fokus im Formular | später (nach dem Livegang) |
| 23, 24 | Cookie, GTM, GA4 | 0.25 |

## 4. Tests

Neu: `tests/test_review_024.py` (R1–R5), W32 (Manifest, theme-color, ohne SportsEvent, 44 px), W19 angepasst.
Vollständige Testreihe: siehe RELEASE.md (Erwartungswerte).
