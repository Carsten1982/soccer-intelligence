"""Version 0.23: Mailversand, Alarme, Statusmail, Laufzeiten, Server-Prüfskript, Kontaktformular.

Spezifikation docs/09_Betrieb_EMail.md (Entscheide Carsten 20.11.2026: M1–M9, F1–F7). Keine echte Mail: Der
SMTP-Server ist nachgebildet.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from betrieb import alarme, laufzeiten, mail, pruefungen, status
from betrieb.alarme import Befund

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ueberwachen as U  # noqa: E402

ENV = {"SI_SMTP_USER": "info@soccer-intelligence.com", "SI_SMTP_PASSWORT": "pw-geheim-123"}   # ein Postfach, alert@ = Alias


class FakeSMTP:
    gesendet: list = []
    fehler: Exception | None = None

    def __init__(self, host, port, timeout=None):
        self.host, self.port = host, port

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def login(self, user, pw):
        if FakeSMTP.fehler:
            raise FakeSMTP.fehler
        self.user = user

    def send_message(self, msg):
        FakeSMTP.gesendet.append(msg)


@pytest.fixture(autouse=True)
def _smtp_leeren():
    FakeSMTP.gesendet, FakeSMTP.fehler = [], None


# --- B1 Mailversand ----------------------------------------------------------------------------------------------------

def test_b1_not_configured_sends_nothing():
    assert mail.konfig("alert", {}) is None and not mail.eingerichtet("info", {"SI_SMTP_USER": "x"})
    assert mail.senden("alert", "x", "y", env={}) == (False, mail.NICHT_EINGERICHTET)


def test_b1_send_to_own_mailbox_with_reply_to_and_no_header_injection():
    ok, meldung = mail.senden("info", "Kontakt\r\nBcc: boese@example.com", "Text", antwort_an="a@b.ch\nX: y",
                              env=ENV, smtp_klasse=FakeSMTP)
    msg = FakeSMTP.gesendet[0]
    assert ok and meldung == "gesendet"
    assert msg["To"] == "info@soccer-intelligence.com" and msg["From"] == "Soccer Intelligence Kontakt <info@soccer-intelligence.com>"
    assert msg["Subject"] == "[Soccer Intelligence] Kontakt Bcc: boese@example.com" and msg["Bcc"] is None
    assert "\n" not in str(msg["Reply-To"]) and msg["X"] is None                     # kein eingeschleuster Kopf
    cfg = mail.konfig("alert", ENV)
    assert (cfg["host"], cfg["port"], cfg["an"]) == ("smtp.hostinger.com", 465, "alert@soccer-intelligence.com")


def test_b1_alerts_go_to_alias_and_are_sent_from_the_mailbox():
    """Ein Postfach (info@), alert@ ist ein Alias (Carsten 20.11.2026): Anmeldung und Absender immer das Postfach,
    Alarme an den Alias, damit sie erkennbar und filterbar bleiben."""
    ok, _ = mail.senden("alert", "KRITISCH: Test", "…", env=ENV, smtp_klasse=FakeSMTP)
    msg = FakeSMTP.gesendet[0]
    assert ok and msg["To"] == "alert@soccer-intelligence.com"
    assert msg["From"] == "Soccer Intelligence Alarm <info@soccer-intelligence.com>"
    assert mail.konfig("alert", {**ENV, "SI_ALARM_AN": "test@example.com"})["an"] == "test@example.com"


def test_b1_error_message_never_contains_password():
    FakeSMTP.fehler = RuntimeError("Login mit pw-geheim-123 abgelehnt")
    ok, meldung = mail.senden("alert", "x", "y", env=ENV, smtp_klasse=FakeSMTP)
    assert not ok and "pw-geheim-123" not in meldung and "***" in meldung


def test_b1_release_testmail_subject(monkeypatch):
    ok, _ = mail.testmail("alert", "0.23 – Betrieb (abc1234)", "Container soccer-import (an alert@)", env=ENV,
                          smtp_klasse=FakeSMTP)
    assert ok and FakeSMTP.gesendet[0]["Subject"] == ("[Soccer Intelligence] Test nach Release 0.23 – Betrieb (abc1234) – "
                                                      "Container soccer-import (an alert@)")
    monkeypatch.setattr(mail, "testmail", lambda *a, **k: (False, mail.NICHT_EINGERICHTET))
    assert mail.main(["--test", "alert"]) == 3 and mail.main(["--test", "x"]) == 2


# --- B2 Alarme: Drosselung, Stufe, Erinnerung, höchstens 3 Mails -------------------------------------------------------

T0 = datetime(2026, 11, 21, 10, 0)


def _lauf(pfad, befunde, now, mails):
    return alarme.verarbeiten(pfad, befunde, now, lambda b, t: mails.append(b) or (True, "gesendet"))


def test_b2_new_escalate_remind_resolve(tmp_path):
    p, mails = tmp_path / "alarme.json", []
    w, k = Befund("festplatte", "warnung", "Festplatte zu 86 % belegt", "…"), Befund("festplatte", "kritisch", "Festplatte zu 96 % belegt", "…")
    _lauf(p, [w], T0, mails)
    _lauf(p, [w], T0 + timedelta(minutes=1), mails)                                   # keine zweite Mail
    assert mails == ["WARNUNG: Festplatte zu 86 % belegt"]
    _lauf(p, [k], T0 + timedelta(minutes=2), mails)                                   # Stufe steigt: sofort
    assert mails[-1] == "KRITISCH: Festplatte zu 96 % belegt (Stufe gestiegen)"
    _lauf(p, [k], T0 + timedelta(hours=26), mails)                                    # Erinnerung nach 24 h
    assert mails[-1].endswith("(Erinnerung)") and len(mails) == 3
    _lauf(p, [k], T0 + timedelta(hours=60), mails)                                    # höchstens 3 Mails
    _lauf(p, [], T0 + timedelta(hours=61), mails)                                     # auch kein „Behoben“
    assert len(mails) == 3
    z = alarme.laden(p)
    assert z["aktiv"] == {} and z["verlauf"][-1]["stufe"] == "kritisch" and z["verlauf"][-1]["mails"] == 3


def test_b2_resolved_mail_and_hourly_throttle(tmp_path):
    p, mails = tmp_path / "alarme.json", []
    b = Befund("import", "kritisch", "Import fehlgeschlagen", "…")
    _lauf(p, [b], T0, mails)
    _lauf(p, [], T0 + timedelta(minutes=10), mails)
    assert mails == ["KRITISCH: Import fehlgeschlagen", "BEHOBEN: Import fehlgeschlagen"]
    _lauf(p, [b], T0 + timedelta(minutes=20), mails)                                  # gleiche Art < 1 h: wartet
    assert len(mails) == 2
    _lauf(p, [b], T0 + timedelta(minutes=71), mails)                                  # Stunde um: nachgeholt
    assert mails[-1] == "KRITISCH: Import fehlgeschlagen" and len(mails) == 3


def test_b2_failed_sending_pauses_15_minutes_and_is_logged(tmp_path):
    p, versuche, log = tmp_path / "alarme.json", [], []
    senden = lambda b, t: versuche.append(b) or (False, "SMTPAuthenticationError")   # noqa: E731
    b = Befund("kontingent", "warnung", "API-Kontingent fast aufgebraucht", "…")
    alarme.verarbeiten(p, [b], T0, senden, log.append)
    alarme.verarbeiten(p, [b], T0 + timedelta(minutes=5), senden, log.append)
    alarme.verarbeiten(p, [b], T0 + timedelta(minutes=16), senden, log.append)
    assert len(versuche) == 2 and alarme.laden(p)["versand"]["ok"] is False
    assert any(e["art"] == "alarm" for e in log) and any(e["art"] == "alarm_mail" and not e["ok"] for e in log)


# --- B3 Daten-Alarme ---------------------------------------------------------------------------------------------------

def _bericht(base, lauf, **werte):
    d = base / "laeufe" / lauf
    d.mkdir(parents=True, exist_ok=True)
    (d / "bericht.json").write_text(json.dumps({"lauf": lauf, "start": f"{lauf[:10]}T04:00:00", **werte}), encoding="utf-8")


def _snap(base, lauf, fehler=None):
    from importer.schnappschuss import save_status
    save_status(base, {"lauf": lauf, "fehler": fehler})


def _keys(base, now=T0):
    return {b.schluessel: b.stufe for b in pruefungen.befunde(base, base / "data", now)}


def test_b3_import_quota_snapshot_files(tmp_path, monkeypatch):
    monkeypatch.setattr(pruefungen.laufzeiten, "laden", lambda **k: [])
    base = tmp_path
    _bericht(base, "2026-11-21_040000", status="fehlgeschlagen", anlass="kontrolle", meldung="Timeout")
    _snap(base, "2026-11-21T09:00:00")
    (base / "roh").mkdir()
    (base / "roh" / "abfragen.csv").write_text("".join(f"2026-11-21T09:00,{i}\n" for i in range(410)), encoding="utf-8")
    assert _keys(base) == {"import": "kritisch", "kontingent": "warnung"}
    _snap(base, "2026-11-21T07:30:00")                                                # älter als 2 h
    assert _keys(base)["schnappschuss"] == "kritisch"
    _snap(base, "2026-11-21T09:50:00", "RuntimeError: Datenbank oder Spielplan mit Fehlern – keine Schnappschüsse")
    k = _keys(base)
    assert k["dateien"] == "kritisch" and "schnappschuss" not in k
    _bericht(base, "2026-11-21_174500", status="fehlgeschlagen", anlass="spiel", meldung="x")
    (base / "zustand.json").write_text(json.dumps({"wiederholung": {"um": "2026-11-21T18:45:00", "nr": 1}}), encoding="utf-8")
    assert "import" not in _keys(base)                                                # Wiederholung folgt noch


def test_b3_approval_decision_statistics_contact(tmp_path, monkeypatch):
    monkeypatch.setattr(pruefungen.laufzeiten, "laden", lambda **k: [])
    base = tmp_path
    _bericht(base, "2026-11-21_040000", status="übernommen (automatisch)", anlass="kontrolle",
             kritisch=[{"art": "endstand", "id": 77, "liga": "Bundesliga", "spiel": "A - B", "api": "3:0", "ereignisse": "2:0"}],
             spaete_korrekturen=[], offen=[{"liga": "LaLiga", "heim": "C", "gast": "D", "datum": "10.11.2026",
                                            "fehlt": ["Ecken"], "grund": "Statistik fehlt seit 11 Tagen"}])
    _bericht(base, "2026-11-21_174500", status="wartet", anlass="spiel", automatik={"gruende": ["1 Fehler"]},
             kritisch=[{"art": "endstand", "id": 77, "liga": "Bundesliga", "spiel": "A - B", "api": "3:0", "ereignisse": "2:0"}])
    (base / "zustand.json").write_text(json.dumps({"wartend": "2026-11-21_174500"}), encoding="utf-8")
    (base / "meldungen").mkdir()
    (base / "meldungen" / "kontakt_20261121_090000.json").write_text(
        json.dumps({"zeit": "2026-11-21T09:00:00", "meldung": "SMTPAuthenticationError"}), encoding="utf-8")
    k = _keys(base)
    assert k == {"freigabe": "warnung", "entscheid": "warnung", "statistik": "warnung", "kontakt": "warnung"}
    (base / "entscheidungen.json").write_text(json.dumps([{"art": "endstand", "id": 77, "spalte": None}]), encoding="utf-8")
    assert "entscheid" not in _keys(base)
    assert "kontakt" not in _keys(base, T0 + timedelta(hours=25))                     # nach 24 h vorbei


# --- B4 Laufzeiten -----------------------------------------------------------------------------------------------------

def test_b4_runtimes_file_and_levels():
    lz = {x.name: x for x in laufzeiten.laden(abo={"plan": "Pro", "bis": "2027-02-15"})}
    assert lz["VPS KVM 1 (Server)"].bis == date(2027, 6, 22) and lz["VPS KVM 1 (Server)"].automatisch
    assert lz["Domain soccer-intelligence.com"].bis == date(2027, 10, 23)
    assert lz["E-Mail-Postfach soccer-intelligence.com"].bis == date(2028, 11, 20)
    api = lz["API-Football (Pro)"]
    assert not api.automatisch and api.stufe(date(2027, 1, 15)) is None and api.stufe(date(2027, 1, 16)) == "warnung"
    assert api.stufe(date(2027, 2, 8)) == "kritisch" and api.farbe(date(2027, 2, 8)) == "bad"
    vps = lz["VPS KVM 1 (Server)"]
    assert vps.stufe(date(2027, 6, 7)) is None and vps.stufe(date(2027, 6, 8)) == "warnung"
    assert vps.stufe(date(2027, 6, 23)) == "kritisch"


# --- B5 Statusmail ----------------------------------------------------------------------------------------------------

def test_b5_status_mail_monday_6_once_per_week(tmp_path):
    mo = datetime(2026, 11, 23, 6, 0)
    assert status.faellig({}, mo) and not status.faellig({}, mo.replace(hour=5, minute=59))
    assert not status.faellig({"letzte_statusmail": "2026-48"}, mo) and not status.faellig({}, mo + timedelta(days=1))
    alarme.ereignis(tmp_path / "ereignisse.jsonl", {"zeit": "2026-11-21T22:45:00", "lauf": "x", "anlass": "spiel",
                                                    "status": "übernommen (automatisch)", "neue_spiele": 2,
                                                    "korrekturen": 0, "abfragen": 20})
    betreff, text = status.text(tmp_path, tmp_path, tmp_path / "backup", mo)
    assert betreff == "Wochenstatus KW 48" and text.startswith("Alles in Ordnung.")
    for teil in ("LÄUFE DER WOCHE", "1 nach dem Spiel", "Neue Spiele: 2", "ALARME", "SERVER", "BACKUPS", "LAUFZEITEN",
                 "VPS KVM 1 (Server): bis 22.06.2027"):
        assert teil in text, teil
    assert "Monatssicherung" not in text
    assert "Monatssicherung" in status.text(tmp_path, tmp_path, tmp_path, datetime(2026, 12, 7, 6, 0))[1]


def test_b5_service_sends_status_mail_once(tmp_path, monkeypatch):
    from importer import dienst
    monkeypatch.setattr(pruefungen, "befunde", lambda *a: [])
    monkeypatch.setattr(dienst, "fehlende_namen", lambda d: [])
    mails = []
    tz = dienst.ZoneInfo("Europe/Zurich")
    for minute in (0, 1):
        dienst.betrieb_pruefen(tmp_path, tmp_path, datetime(2026, 11, 23, 6, minute, tzinfo=tz),
                               senden=lambda b, t: mails.append(b) or (True, "gesendet"))
    assert mails == ["Wochenstatus KW 48"] and dienst.load_state(tmp_path)["letzte_statusmail"] == "2026-48"


# --- B6 Prüfskript des Servers ------------------------------------------------------------------------------------------

def _m(**werte):
    m = {"festplatte": 50.0, "speicher": 40.0, "cpu": 10.0, "lebenszeichen_min": 1.0,
         "container": {n: {"status": "running", "neustarts": 0, "health": ""} for n in U.CONTAINER},
         "website": {"/": 200, "/dashboard/": 200, "/vorschau/": 401}}
    m.update(werte)
    return m


def test_b6_thresholds_with_durations():
    z = {}
    assert U.auswerten(_m(), z, T0) == []
    assert [(b.schluessel, b.stufe) for b in U.auswerten(_m(festplatte=86.0), {}, T0)] == [("festplatte", "warnung")]
    assert U.auswerten(_m(festplatte=95.5), {}, T0)[0].stufe == "kritisch"
    z = {}
    for minute in range(0, 16):                                                       # RAM 92 %: nach 15 Min. Warnung
        b = U.auswerten(_m(speicher=92.0), z, T0 + timedelta(minutes=minute))
    assert [(x.schluessel, x.stufe) for x in b] == [("speicher", "warnung")]
    z = {}
    for minute in range(0, 6):                                                        # RAM 96 %: nach 5 Min. kritisch
        b = U.auswerten(_m(speicher=96.0), z, T0 + timedelta(minutes=minute))
    assert b[0].stufe == "kritisch"
    z = {}
    assert U.auswerten(_m(cpu=95.0), z, T0) == []
    assert U.auswerten(_m(cpu=95.0), z, T0 + timedelta(minutes=30))[0].schluessel == "cpu"
    assert U.auswerten(_m(cpu=50.0), z, T0 + timedelta(minutes=31)) == []             # Dauer beginnt neu


def test_b6_containers_website_heartbeat():
    z, weg = {}, _m()
    weg["container"]["soccer-vorschau"] = {"status": "exited", "neustarts": 0, "health": ""}
    assert U.auswerten(weg, z, T0) == []
    assert U.auswerten(weg, z, T0 + timedelta(minutes=5))[0].schluessel == "container:soccer-vorschau"
    z = {}
    for i, n in enumerate((0, 1, 2, 3, 4)):
        m = _m()
        m["container"]["soccer-import"]["neustarts"] = n
        b = U.auswerten(m, z, T0 + timedelta(minutes=i * 2))
    assert [(x.schluessel, x.stufe) for x in b] == [("container:soccer-import", "warnung")]
    z = {}
    aus = _m(website={"/": None, "/dashboard/": 502, "/vorschau/": 401})
    assert U.auswerten(aus, z, T0) == []
    assert U.auswerten(aus, z, T0 + timedelta(minutes=5))[0].schluessel == "website"
    assert U.auswerten(_m(website={"/": 200, "/dashboard/": 200, "/vorschau/": 200}), {}, T0) == []   # nach dem Livegang
    assert U.auswerten(_m(lebenszeichen_min=29.0), {}, T0) == []
    assert U.auswerten(_m(lebenszeichen_min=31.0), {}, T0)[0].schluessel == "lebenszeichen"


def test_b6_proc_values_and_env_reads_only_mail_keys(tmp_path):
    (tmp_path / "meminfo").write_text("MemTotal: 1000 kB\nMemFree: 100 kB\nMemAvailable: 250 kB\n")
    (tmp_path / "stat").write_text("cpu  100 0 100 700 100 0 0 0\ncpu0 1 2 3\n")
    assert U.speicher(tmp_path) == 75.0 and U.cpu_zaehler(tmp_path) == (1000, 800)
    assert U.cpu_prozent([0, 0], (1000, 800)) == 20.0 and U.cpu_prozent(None, (1, 1)) is None
    (tmp_path / ".env").write_text("API_FOOTBALL_KEY=geheim\nSI_SMTP_USER=info@soccer-intelligence.com\n"
                                   "SI_SMTP_PASSWORT='a$b'\n# SI_SMTP_HOST=x\nSI_LOGIN_HASH=$2b$xyz\nSI_ALARM_AN=alert@soccer-intelligence.com\n")
    assert U.env_lesen(tmp_path / ".env") == {"SI_SMTP_USER": "info@soccer-intelligence.com", "SI_SMTP_PASSWORT": "a$b",
                                              "SI_ALARM_AN": "alert@soccer-intelligence.com"}


def test_b6_week_maxima(tmp_path):
    U.server_json(tmp_path / "server.json", _m(zeit="x", festplatte=60.0, cpu=None), T0)
    U.server_json(tmp_path / "server.json", _m(zeit="x", festplatte=55.0, cpu=70.0), T0)
    w = json.loads((tmp_path / "server.json").read_text())["woche"]
    assert (w["festplatte"], w["cpu"], w["kw"]) == (60.0, 70.0, "2026-47")


# --- B7 Kontaktformular -----------------------------------------------------------------------------------------------

def test_b7_security_question_token():
    from website import kontakt as KT
    frage, token = KT.neue_aufgabe(1000.0)
    idx = KT.aufgabe_aus(token, 1000.0 + 60)
    assert KT.AUFGABEN[idx][0] == frage
    assert KT.aufgabe_aus(token, 1000.0 + 2 * 3600 + 1) is None                       # abgelaufen
    i, ts, sig = token.split(".")
    assert KT.aufgabe_aus(f"{(int(i) + 1) % 10}.{ts}.{sig}", 1000.0) is None          # verändert
    assert KT.aufgabe_aus("kaputt", 1000.0) is None


def _form(KT, ts=None, **werte):
    frage, token = KT.neue_aufgabe(ts)
    ans = KT.AUFGABEN[KT.aufgabe_aus(token, ts)][1]
    f = {"name": ["Max"], "email": ["max@example.com"], "nachricht": ["Hallo, eine Frage zur Methodik."],
         "einverstanden": ["ja"], "antwort": [str(ans)], "aufgabe": [token], "website": [""]}
    f.update({k: [v] for k, v in werte.items()})
    return f


@pytest.mark.parametrize("feld,wert,fehler", [
    ("email", "", "email_fehlt"), ("email", "max@", "email_ungueltig"), ("nachricht", "", "nachricht_fehlt"),
    ("nachricht", "kurz", "nachricht_kurz"), ("nachricht", "x" * 5001, "nachricht_lang"), ("name", "n" * 101, "name_lang"),
    ("einverstanden", "", "einwilligung"), ("antwort", "99", "antwort")])
def test_b7_field_errors(feld, wert, fehler):
    from website import kontakt as KT
    werte, f = KT.pruefen(_form(KT, **{feld: wert}))
    assert f == {"email" if feld == "email" else "einverstanden" if feld == "einverstanden" else feld: fehler} or \
        list(f.values()) == [fehler]


def test_b7_send_rate_limit_honeypot_not_configured(monkeypatch):
    from website import kontakt as KT
    monkeypatch.setattr(KT, "BREMSE", KT.Bremse())
    gesendet = []
    senden = lambda b, t, a: gesendet.append((b, t, a)) or (True, "gesendet")       # noqa: E731
    assert KT.bearbeiten(_form(KT, 1000.0), "9.9.9.9", "de", env=ENV, senden=senden, jetzt=1000.0) is None
    b, t, a = gesendet[0]
    assert b == "Kontaktformular: Hallo, eine Frage zur Methodik." and a == "max@example.com" and "Sprache der Seite: de" in t
    for _ in range(2):
        KT.bearbeiten(_form(KT, 1000.0), "9.9.9.9", "de", env=ENV, senden=senden, jetzt=1000.0)
    f = KT.bearbeiten(_form(KT, 1000.0), "9.9.9.9", "de", env=ENV, senden=senden, jetzt=1000.0)
    assert f.status == "zu_viele" and len(gesendet) == 3                               # höchstens 3 je Stunde
    assert KT.bearbeiten(_form(KT, 1000.0), "9.9.9.9", "de", env=ENV, senden=senden, jetzt=1000.0 + 3601) is None
    assert KT.bearbeiten(_form(KT, website="http://spam"), "8.8.8.8", "de", env=ENV, senden=senden) is None
    assert len(gesendet) == 4                                                          # Bot: nichts gesendet
    f = KT.bearbeiten(_form(KT), "7.7.7.7", "de", env={}, senden=senden)
    assert f is not None and not f.aktiv and len(gesendet) == 4                        # nicht eingerichtet


def test_b7_page_post_and_redirect(monkeypatch, tmp_path):
    from website import kontakt as KT
    from website import vorschau as V
    monkeypatch.setattr(KT, "BREMSE", KT.Bremse())
    monkeypatch.setattr(KT, "MELDUNGEN", tmp_path)
    seite = V.beantworten("/vorschau/en/contact/", "")
    html = seite.inhalt.decode()
    assert seite.kopf["Cache-Control"] == "no-store" and "Security question: What is" in html
    assert 'name="aufgabe" value="' in html and "<button type=\"submit\" class=\"knopf-voll\" disabled>" in html
    falsch = V.beantworten_post("/vorschau/en/contact/", b"email=x&nachricht=kurz", "1.1.1.1").inhalt.decode()
    for text in ("Please check the highlighted fields.", "This email address doesn't look complete.",
                 "Your message is a little short", 'aria-invalid="true"', 'value="x"'):
        assert text.replace("'", "&#39;") in falsch, text
    monkeypatch.setenv("SI_SMTP_USER", ENV["SI_SMTP_USER"])
    monkeypatch.setenv("SI_SMTP_PASSWORT", ENV["SI_SMTP_PASSWORT"])
    form = _form(KT)
    from urllib.parse import urlencode
    body = urlencode({k: v[0] for k, v in form.items()}).encode()
    ok = V.beantworten_post("/vorschau/de/kontakt/", body, "1.1.1.1", senden=lambda b, t, a: (True, "gesendet"))
    assert ok.status == 303 and ok.kopf["Location"] == "/vorschau/de/kontakt/?gesendet=1"
    assert "Danke, deine Nachricht ist angekommen." in V.beantworten("/vorschau/de/kontakt/", "gesendet=1").inhalt.decode()
    kaputt = V.beantworten_post("/vorschau/de/kontakt/", body, "2.2.2.2", senden=lambda b, t, a: (False, "SMTPException: x"))
    assert "konnte gerade nicht gesendet werden" in kaputt.inhalt.decode()
    meldung = json.loads(next(tmp_path.glob("kontakt_*.json")).read_text())
    assert set(meldung) == {"zeit", "meldung"} and "Hallo" not in json.dumps(meldung)   # nie der Inhalt
    assert V.beantworten_post("/vorschau/de/spieltag/bundesliga/", b"", "1.1.1.1").status == 405
    assert V.beantworten_post("/vorschau/de/kontakt/", b"x" * 20_001, "1.1.1.1").status == 413


# --- B8 Konfiguration und Einspielen ------------------------------------------------------------------------------------

def test_b8_compose_and_release_script():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    for var in ("SI_SMTP_USER=${SI_SMTP_USER:-}", "SI_SMTP_PASSWORT=${SI_SMTP_PASSWORT:-}", "SI_ALARM_AN=${SI_ALARM_AN:-}",
                "SI_KONTAKT_AN=${SI_KONTAKT_AN:-}", "./import/meldungen:/meldungen"):
        assert var in compose, var
    assert not re.search(r"@yahoo|PASSWORT=[^$]", compose)
    skript = (ROOT / "tools" / "einspielen.sh").read_text(encoding="utf-8")
    assert "docker exec soccer-import python -m betrieb.mail --test alert" in skript
    assert "docker exec soccer-vorschau python -m betrieb.mail --test info" in skript
    assert "python3 tools/ueberwachen.py --test" in skript


def test_b8_host_modules_use_standard_library_only():
    """mail.py, alarme.py und tools/ueberwachen.py laufen auf dem Server ohne Container (nur Standardbibliothek)."""
    erlaubt = {"__future__", "json", "os", "smtplib", "ssl", "sys", "email", "dataclasses", "datetime", "pathlib",
               "shutil", "subprocess", "urllib", "betrieb"}
    for datei in (ROOT / "app" / "betrieb" / "mail.py", ROOT / "app" / "betrieb" / "alarme.py", ROOT / "tools" / "ueberwachen.py"):
        for mod in re.findall(r"^(?:from|import) ([\w.]+)", datei.read_text(encoding="utf-8"), re.M):
            assert mod.split(".")[0] in erlaubt, (datei.name, mod)


def test_b8_setup_script_touches_only_mail_keys_and_one_cron_line():
    """tools/mail_einrichten.sh: Passwörter verdeckt, nur die Mail-Einträge in .env ersetzt (vorher Backup), genau eine
    Zeile im Zeitplan, keine private Adresse."""
    s = (ROOT / "tools" / "mail_einrichten.sh").read_text(encoding="utf-8")
    assert s.count("read -rsp") == 1 and 'read -rsp "Passwort für $INFO' in s                # ein Postfach
    assert "cp -a .env \"backup/env_$(date" in s
    assert "grep -Ev '^(SI_SMTP_HOST|SI_SMTP_PORT|SI_SMTP_USER|SI_SMTP_PASSWORT|SI_ALARM_AN|SI_KONTAKT_AN|SI_KONTAKT_EMAIL)='" in s
    assert 'grep -qF "tools/ueberwachen.py"' in s and "docker compose up -d soccer-import soccer-vorschau" in s
    assert "docker compose down" not in s and "yahoo" not in s.lower()
    assert set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", s)) == {"alert@soccer-intelligence.com", "info@soccer-intelligence.com"}
