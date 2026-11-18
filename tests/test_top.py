"""Auswahl der Top Anomalien (KPI-Regelwerk 2.6, seit Version 0.19 nach Prognosewert mit Liga-Mix).

Die Auswahl verwendet von jedem KPI-Ergebnis nur Einstufung (Prognosewert), gerundete Abweichung und „vorläufig“.
Darum genügen hier schlanke Platzhalter statt vollständig berechneter KPIs. Testfälle P17–P20 und P23–P25 der
Spezifikation vom 18.11.2026.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from core.kpis import HIGH, LOW, MEDIUM, NONE
from core.top import MAX_ENTRIES, MAX_PER_LEAGUE, TOP_KPIS, Candidate, has_low, select_top

KEYS = ("kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08", "kpi09")


def res(deviation=0, level=NONE, vorlaeufig=False):
    if deviation is None:
        return SimpleNamespace(abweichung_rund=None, anomalie=None, vorlaeufig=vorlaeufig)
    return SimpleNamespace(abweichung_rund=Decimal(str(deviation)), anomalie=level, vorlaeufig=vorlaeufig)


def cand(name, league="Liga", *, day=1, league_order=0, file_order=0, status="", **kpis):
    """kpis: z. B. kpi02=(25.0, HIGH) oder kpi04=(−40.0, MEDIUM, True) für vorläufig; alle anderen nicht auffällig."""
    values = {k: res(*kpis[k]) if k in kpis else res() for k in KEYS}
    return Candidate(league=league, league_order=league_order, season="2026/2027", matchday=1,
                     datum_von=date(2026, 8, day), file_order=file_order, home=name, away="Gast",
                     status=status, kpis=SimpleNamespace(**values))


def names(entries):
    return [e.candidate.home for e in entries]


def test_p17_high_before_medium_before_low_then_largest_deviation():
    top = select_top([cand("A", "L1", kpi02=(22.0, HIGH)), cand("B", "L2", kpi02=(35.0, HIGH)),
                      cand("C", "L3", kpi04=(60.0, MEDIUM)), cand("D", "L4", kpi04=(-40.0, MEDIUM)),
                      cand("E", "L5", kpi05=(90.0, LOW))])
    assert names(top) == ["B", "A", "C", "D"] and [e.rank for e in top] == [1, 2, 3, 4]


def test_p18_fill_with_low_and_hint():
    top = select_top([cand("A", "L1", kpi02=(22.0, HIGH)), cand("C", "L2", kpi04=(30.0, MEDIUM)),
                      cand("E", "L3", kpi05=(40.0, LOW)), cand("F", "L4", kpi05=(-55.0, LOW))])
    assert names(top) == ["A", "C", "F", "E"] and has_low(top)
    assert not has_low(select_top([cand("A", kpi02=(22.0, HIGH))]))


def test_p19_same_level_in_one_match_larger_deviation_wins():
    top = select_top([cand("A", kpi09=(-12.0, HIGH), kpi03=(40.0, HIGH))])
    assert len(top) == 1 and top[0].kpi_key == "kpi03"


def test_p20_higher_level_beats_larger_deviation_in_one_match():
    top = select_top([cand("A", kpi04=(60.0, MEDIUM), kpi05=(-11.0, HIGH))])
    assert top[0].kpi_key == "kpi05" and top[0].result.anomalie == HIGH


def test_p23_league_mix_at_most_two_per_league():
    top = select_top([cand("SA1", "Serie A", kpi02=(50.0, HIGH)), cand("SA2", "Serie A", kpi02=(45.0, HIGH)),
                      cand("SA3", "Serie A", kpi02=(40.0, HIGH)), cand("LL", "LaLiga", kpi02=(30.0, HIGH)),
                      cand("BL", "Bundesliga", kpi04=(60.0, MEDIUM))])
    assert MAX_PER_LEAGUE == 2
    assert names(top) == ["SA1", "SA2", "LL", "BL"]                       # dritter Serie-A-Kandidat übersprungen


def test_p24_fill_with_same_league_when_others_lack():
    top = select_top([cand(f"SA{i}", "Serie A", kpi02=(50.0 - i, HIGH)) for i in range(5)])
    assert names(top) == ["SA0", "SA1", "SA2", "SA3"]


def test_p25_fewer_than_four_are_shown_as_they_are():
    top = select_top([cand("A", kpi02=(25.0, HIGH)), cand("B", kpi02=(10.0, NONE)), cand("C", kpi03=(30.0, LOW))])
    assert names(top) == ["A", "C"] and len(top) < MAX_ENTRIES


def test_tie_broken_by_date_then_league_then_file_order():
    top = select_top([
        cand("spaet", "L1", kpi02=(25.0, HIGH), day=3),
        cand("liga2", "L2", kpi02=(-25.0, HIGH), day=1, league_order=1, file_order=0),
        cand("liga1_b", "L3", kpi02=(25.0, HIGH), day=1, league_order=0, file_order=5),
        cand("liga1_a", "L4", kpi04=(25.0, HIGH), day=1, league_order=0, file_order=2),
    ])
    assert names(top) == ["liga1_a", "liga1_b", "liga2", "spaet"]


def test_same_deviation_in_one_match_prefers_smaller_kpi_number():
    assert select_top([cand("A", kpi04=(-25.0, HIGH), kpi05=(25.0, HIGH))])[0].kpi_key == "kpi04"


def test_two_decimals_decide_the_rank():
    top = select_top([cand("A", "L1", kpi02=(25.01, HIGH)), cand("B", "L2", kpi05=(25.02, HIGH))])
    assert names(top) == ["B", "A"]


def test_at_most_four_entries():
    top = select_top([cand(f"T{i}", f"L{i}", kpi02=(21 + i, HIGH)) for i in range(7)])
    assert len(top) == MAX_ENTRIES == 4 and names(top) == ["T6", "T5", "T4", "T3"]


def test_all_kpis_02_to_09_count():
    assert list(TOP_KPIS) == list(KEYS)
    top = select_top([cand("drei", "L1", kpi03=(80.0, HIGH)), cand("sechs", "L2", kpi06=(-50.0, HIGH))])
    assert [e.kpi_key for e in top] == ["kpi03", "kpi06"] and top[0].kpi_name == "KPI 03 – Over 2.5 Goals"


def test_provisional_values_excluded():
    top = select_top([cand("A", "L1", kpi02=(40.0, HIGH, True), kpi04=(22.0, MEDIUM)),
                      cand("B", "L2", kpi04=(50.0, HIGH, True))])
    assert names(top) == ["A"] and top[0].kpi_key == "kpi04"


def test_postponed_and_cancelled_excluded():
    top = select_top([cand("verschoben", kpi02=(50.0, HIGH), status="verschoben"),
                      cand("abgesagt", kpi02=(50.0, HIGH), status="abgesagt"),
                      cand("geplant", kpi02=(21.0, HIGH), status="geplant")])
    assert names(top) == ["geplant"]


def test_missing_values_and_missing_kpis_excluded():
    no_kpis = Candidate("Liga", 0, "2026/2027", 1, date(2026, 8, 1), 0, "ohne", "Gast", "", None)
    assert select_top([no_kpis, cand("leer", kpi02=(None,), kpi04=(None,))]) == []


def test_no_anomalies_gives_empty_list():
    assert select_top([cand("A"), cand("B", kpi02=(-19.9, NONE))]) == [] and select_top([]) == []
