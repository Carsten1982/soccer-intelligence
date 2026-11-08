"""Auswahl der Top-Anomalien (KPI-Regelwerk, Abschnitt 2.6) mit ausgedachten Werten.

Die Auswahl verwendet von jedem KPI-Ergebnis nur Anomalie-Stufe, gerundete Abweichung und „vorläufig“.
Darum genügen hier schlanke Platzhalter statt vollständig berechneter KPIs.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from core.kpis import STRONG, classify
from core.top import MAX_ENTRIES, TOP_KPIS, Candidate, select_top


def res(deviation, vorlaeufig=False):
    if deviation is None:
        return SimpleNamespace(abweichung_rund=None, anomalie=None, vorlaeufig=vorlaeufig)
    d = Decimal(str(deviation))
    return SimpleNamespace(abweichung_rund=d, anomalie=classify(d)[0], vorlaeufig=vorlaeufig)


def cand(name, kpi02=0, kpi04=0, *, day=1, league_order=0, file_order=0, status="", vorl02=False, vorl04=False,
         kpi03=0, **more):
    """more: weitere KPIs, z. B. kpi06=40.0 (alle anderen ohne Anomalie)."""
    extra = {k: res(more.get(k, 0)) for k in ("kpi05", "kpi06", "kpi07", "kpi08", "kpi09")}
    kpis = SimpleNamespace(kpi02=res(kpi02, vorl02), kpi03=res(kpi03), kpi04=res(kpi04, vorl04), **extra)
    return Candidate(league="Liga", league_order=league_order, season="2026/2027", matchday=1,
                     datum_von=date(2026, 8, day), file_order=file_order, home=name, away="Gast",
                     status=status, kpis=kpis)


def names(entries):
    return [e.candidate.home for e in entries]


def test_strong_before_light_regardless_of_size():
    top = select_top([cand("leicht", kpi02=34.9), cand("stark", kpi04=-35.1)])
    assert names(top) == ["stark", "leicht"]
    assert [e.rank for e in top] == [1, 2]


def test_larger_absolute_deviation_first():
    top = select_top([cand("A", kpi02=22.0), cand("B", kpi04=-30.5), cand("C", kpi02=25.0)])
    assert names(top) == ["B", "C", "A"]


def test_tie_broken_by_date_then_league_then_file_order():
    top = select_top([
        cand("spaet", kpi02=25.0, day=3),
        cand("liga2", kpi02=-25.0, day=1, league_order=1, file_order=0),
        cand("liga1_b", kpi02=25.0, day=1, league_order=0, file_order=5),
        cand("liga1_a", kpi04=25.0, day=1, league_order=0, file_order=2),
    ])
    assert names(top) == ["liga1_a", "liga1_b", "liga2", "spaet"]


def test_at_most_one_entry_per_match_best_kpi_wins():
    top = select_top([cand("A", kpi02=24.0, kpi04=-40.0)])
    assert len(top) == 1
    assert top[0].kpi_key == "kpi04" and top[0].result.anomalie == STRONG


def test_same_deviation_in_both_kpis_prefers_kpi02():
    top = select_top([cand("A", kpi02=25.0, kpi04=-25.0)])
    assert top[0].kpi_key == "kpi02"


def test_at_most_four_entries():
    top = select_top([cand(f"T{i}", kpi02=21 + i) for i in range(7)])
    assert len(top) == MAX_ENTRIES == 4
    assert names(top) == ["T6", "T5", "T4", "T3"]


def test_no_filling_with_non_anomalies():
    top = select_top([cand("A", kpi02=25.0), cand("B", kpi02=10.0), cand("C", kpi02=-20.0)])
    assert names(top) == ["A"]


def test_all_kpis_02_to_09_count_since_stage_h():
    assert list(TOP_KPIS) == ["kpi02", "kpi03", "kpi04", "kpi05", "kpi06", "kpi07", "kpi08", "kpi09"]
    top = select_top([cand("drei", kpi03=80.0), cand("sechs", kpi06=-50.0), cand("acht", kpi08=25.0),
                      cand("neun", kpi09=-21.0)])
    assert names(top) == ["drei", "sechs", "acht", "neun"]
    assert [e.kpi_key for e in top] == ["kpi03", "kpi06", "kpi08", "kpi09"]
    assert top[0].kpi_name == "KPI 03 – Over 2.5 Goals"


def test_same_deviation_in_one_match_prefers_smaller_kpi_number():
    top = select_top([cand("A", kpi04=-25.0, kpi05=25.0, kpi07=-25.0)])
    assert top[0].kpi_key == "kpi04"
    top = select_top([cand("B", kpi05=30.0, kpi09=30.0)])
    assert top[0].kpi_key == "kpi05"


def test_two_decimals_decide_the_rank():
    top = select_top([cand("A", kpi02=25.01), cand("B", kpi05=25.02)])
    assert names(top) == ["B", "A"]


def test_provisional_values_excluded():
    top = select_top([cand("A", kpi02=40.0, vorl02=True, kpi04=22.0), cand("B", kpi04=50.0, vorl04=True)])
    assert names(top) == ["A"] and top[0].kpi_key == "kpi04"


def test_postponed_and_cancelled_excluded():
    top = select_top([cand("verschoben", kpi02=50.0, status="verschoben"),
                      cand("abgesagt", kpi02=50.0, status="abgesagt"),
                      cand("geplant", kpi02=21.0, status="geplant")])
    assert names(top) == ["geplant"]


def test_missing_values_and_missing_kpis_excluded():
    no_kpis = Candidate("Liga", 0, "2026/2027", 1, date(2026, 8, 1), 0, "ohne", "Gast", "", None)
    assert select_top([no_kpis, cand("leer", kpi02=None, kpi04=None)]) == []


def test_no_anomalies_gives_empty_list():
    assert select_top([cand("A"), cand("B", kpi02=-19.9)]) == []
    assert select_top([]) == []
