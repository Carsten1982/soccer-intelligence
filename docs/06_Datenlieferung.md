# Soccer Intelligence – Datenlieferung (Konzept)

**Status: Entwurf, noch nicht freigegeben** · Stand 07.11.2026

Dieses Dokument hält fest, wie neue Spieldaten künftig regelmässig auf den Server kommen sollen.
Es ist noch nichts umgesetzt. Programmiert wird erst nach Klärung mit dem Datenlieferanten
und nach Freigabe durch Carsten (**Etappe G**, nach der Erweiterung auf vier Ligen in Etappe F).

---

## 1. Ausgangslage

- Heute: Carsten pflegt `data/Database-Soccer-Intelligence.xlsx` und `data/Spielplan.xlsx` von Hand und lädt sie mit WinSCP hoch.
- Ziel: weniger Handarbeit, regelmässige Aktualisierung, gleichzeitig keine unkontrollierte Änderung der Datenbank.

## 2. Datenlieferant Footiqo (Stand der Gespräche bis 06.11.2026)

Ansprechpartner: Javier (Footiqo). E-Mail-Verlauf bei Carsten, nicht in Git.

| Punkt | Inhalt |
|---|---|
| Format | **eine** Excel-Datei (.xlsx), ein Tabellenblatt je Liga, Spalten nach Carstens Beispieldatei |
| Zugriff | **fester Download-Link** auf der Plattform Footiqo; der Link bleibt dauerhaft gleich und liefert immer die aktuelle Fassung |
| Aktualisierung | zweimal pro Woche: **dienstags und donnerstags**; die Datei wird jeweils ersetzt |
| Umfang | **kumulativ**: alle abgeschlossenen Spiele ab Saison 2020/21, neue Spiele werden laufend ergänzt (keine Teillieferungen) |
| Spiel-ID | eindeutig und **dauerhaft**, auch bei Verlegungen |
| Abgesagte Spiele | nicht enthalten, solange sie nicht tatsächlich gespielt wurden |
| Korrekturen | selten; Footiqo informiert darüber |
| API | keine |
| Preis (Angebot) | 49.99 € (Historie + 4 Wochen Updates), danach 9.99 € je 4 Wochen oder 99.99 € für 12 Monate; keine Verlängerungspflicht |

**Gewünschte Ligen:** Bundesliga, Premier League, Serie A, LaLiga (Etappe F). Weitere Ligen ggf. später.

## 3. Noch offene Fragen an Footiqo

1. Werden fehlende Einzelstatistiken (z. B. Ecken, Gelbe Karten) in einer späteren Lieferung nachgeliefert?
2. Kann die Spalte **`Gameday`** (offizieller Spieltag) mitgeliefert werden? Sie würde die berechneten Spieltage von Serie A und LaLiga ersetzen (siehe `02_Datenbasis.md`, Abschnitt 4c).
3. **Nutzungsrechte:** Dürfen daraus berechnete Kennzahlen (nicht die Rohdaten) auf einer nicht-kommerziellen Website gezeigt werden, mit Footiqo als Quelle?
4. **Spielplan:** Kann Footiqo auch die angesetzten Spiele liefern? (Carsten klärt das ab, 07.11.2026.) Sonst bleibt der Spielplan Handarbeit, mit der Pflegeregel aus `04_Spielplan.md`.

Bewusst **nicht** nötig (lösen wir selbst): Dateiname, Uhrzeit des Updates, Aufbewahrung früherer Fassungen, Kennzeichnung von Korrekturen (unser Vergleich findet jede Änderung).

## 4. Grundsätze (Vorschlag)

- **Wir holen ab.** Der Server lädt die Datei selbst über den Download-Link. Kein Zugang für Dritte auf den Server.
- Der **Download-Link gilt als Geheimnis**: nur in `.env`, nie in Git oder in der Dokumentation.
- **Täglich nachsehen, nur bei Änderung verarbeiten:** Der Abholdienst lädt einmal täglich, vergleicht die Prüfsumme mit der letzten Fassung und arbeitet nur weiter, wenn sich etwas geändert hat. Damit ist die Uhrzeit des Updates egal.
- **Prüfschranke:** Eine Lieferung wird erst übernommen, wenn alle Prüfungen bestanden sind. Sonst bleibt die bisherige Datenbank gültig; lieber veraltete als falsche Daten.
- Alle gelieferten Dateien werden mit Datum aufbewahrt (`data/eingang/`), die ersetzte Datenbank kommt nach `backup/`.

## 5. Ablauf des Abholdienstes (Vorschlag)

```
täglich, z. B. 06:00
1. Abholen      Datei über den Download-Link laden
2. Vergleichen  Prüfsumme gleich wie zuletzt → Ende (nichts zu tun)
3. Ablegen      data/eingang/<Datum>_footiqo.xlsx
4. Prüfen       dieselben Prüfregeln wie im Bereich Datenqualität (02_Datenbasis.md)
5. Vergleichen  neu gegen aktuell (siehe 6)
6. Entscheiden  ok → alte Datenbank nach backup/, neue wird gültig (Dashboard liest automatisch neu ein)
                Problem → nichts ändern, Bericht ablegen
7. Melden       Kurzmeldung an Carsten; Anzeige „Letzter Import“ im Bereich Datenqualität
8. Ausbleiben   seit mehr als 5 Tagen keine neue Fassung → Warnung
```

## 6. Vergleich neu gegen bisher

Footiqo liefert immer den **ganzen Bestand**. Verglichen wird über die Spiel-`id`:

| Fall | Behandlung |
|---|---|
| neues Spiel | übernehmen |
| Spiel unverändert | nichts zu tun |
| Wert war leer, ist jetzt gefüllt (Nachlieferung) | übernehmen, im Bericht erwähnen |
| Wert war gefüllt, ist jetzt **anders** (Korrektur) | auflisten; Carsten entscheidet |
| Spiel fehlt in der neuen Datei | **nicht** übernehmen, Lieferung ablehnen und melden |

**Eigene Ergänzungen bleiben erhalten:** Spieltage (`Gameday`), Nachträge wie Union – Bochum oder Verona – Roma und die Löschungen aus `02_Datenbasis.md`, Abschnitt 4c, dürfen durch eine Lieferung nicht verloren gehen. Wie das genau geregelt wird (z. B. eigene Korrekturliste, die nach jedem Import angewendet wird), wird in der Spezifikation von Etappe G festgelegt.

**Teamnamen:** Weichen sie von unseren ab, braucht es eine Zuordnungstabelle. Das zeigt der erste Vergleich nach dem Testkauf.

## 7. Technik (Vorschlag)

- Eigener kleiner Container `soccer-import` im Projektordner, mit eigenem Zeitplan. Keine Änderung an der Server-Konfiguration.
- Nur der Abholdienst darf in `data/` schreiben; das Dashboard bleibt nur lesend.
- Wiederverwendung von Loader und Prüfregeln aus `app/core/`. Neu: Abholen, Vergleich, Übernahme, Meldung.

## 8. Vorgehen

1. Antworten von Footiqo auf Abschnitt 3.
2. Testkauf und **einmaliger Vergleich** der gelieferten Datei mit der heutigen Datenbank: Spalten, Teamnamen, IDs, Zählweise (v. a. Gelbe Karten, KPI 04), fehlende Werte, Spieltage.
3. Import-Regeln als Spezifikation, Freigabe durch Carsten.
4. Stufe 1: Abholdienst wird von Hand gestartet.
5. Stufe 2: täglicher Zeitplan und Meldung.

## 9. Alternativen (zur Einordnung)

- **Fussball-API:** sauber dokumentiertes Format, aber Zuordnungstabelle nötig, Abfrage-Grenzen, Detailstatistiken meist kostenpflichtig. Denkbar als Ergänzung nur für den **Spielplan**, falls Footiqo ihn nicht liefert. Vorher Anbieter und Kosten recherchieren.
- **Weiter von Hand:** möglich; die Prüfungen im Bereich Datenqualität bleiben in jedem Fall bestehen.
