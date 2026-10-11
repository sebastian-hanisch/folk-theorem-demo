"""Jede Zahl aus README und App wird hier über die echten Auswertungsfunktionen nachgerechnet (DEMO-PLAYBOOK §4)."""

import pytest

import fkt_algorithm as A
import fkt_constants as C
import fkt_evaluation as E

FULL = 20 / 3


def test_three_phases_of_the_full_equilibrium_set():
    assert A.polygon_area(A.aps_set(0.24)) == 0.0                                   # nur (1 / 1)
    assert A.polygon_area(A.aps_set(0.26)) == pytest.approx(4.5, abs=1e-6)          # Dreieck mit Summe höchstens 5
    assert A.polygon_area(A.aps_set(0.49)) == pytest.approx(4.5, abs=1e-6)
    for d in (0.5, 0.6, 0.8, 0.95):
        assert A.polygon_area(A.aps_set(d)) == pytest.approx(FULL, abs=1e-6)        # die ganze zulässige, individuell rationale Region


def test_thresholds_one_quarter_and_one_half():
    assert (C.P - C.S) / (C.T - C.P) == pytest.approx(0.25)
    assert (C.T - C.R) / (C.T - C.P) == pytest.approx(0.5)
    assert A.threshold_delta((3.0, 3.0), "aps") == pytest.approx(0.5, abs=1e-6)
    assert A.threshold_delta((2.5, 2.5), "aps") == pytest.approx(0.25, abs=1e-6)


def test_threshold_table_for_four_pairs():
    expected = {(3.0, 3.0): (0.5, 0.5), (2.5, 2.5): (0.4, 0.25), (4.0, 1.5): (0.8, 0.5), (1.0, 4.0): (None, 0.25)}
    for v, (trig, aps) in expected.items():
        got_t, got_a = A.threshold_delta(v, "trigger"), A.threshold_delta(v, "aps")
        assert got_a == pytest.approx(aps, abs=1e-6), v
        if trig is None:
            assert got_t is None
        else:
            assert got_t == pytest.approx(trig, abs=1e-6), v


def test_trigger_areas():
    full = A.polygon_area(A.feasible_polygon())
    expect = {0.45: 0.173, 0.5: 0.539, 0.6: 2.104, 0.8: 4.97, 0.95: 6.238}
    for d, area in expect.items():
        assert A.trigger_area(d) == pytest.approx(area, abs=0.05), d
    assert A.trigger_area(0.6) / full == pytest.approx(0.316, abs=0.01)
    assert A.trigger_area(0.8) / full == pytest.approx(0.745, abs=0.01)
    assert A.trigger_area(0.95) / full == pytest.approx(0.936, abs=0.01)


def test_the_trigger_region_never_exceeds_the_full_set_and_never_contains_pairs_above_the_sum_bound_below_one_half():
    for d in (0.3, 0.45):
        assert A.trigger_area(d) <= A.polygon_area(A.aps_set(d)) + 1e-9
    assert not A.trigger_contains((3.0, 3.0), 0.45)
    assert not A.aps_contains((3.0, 3.0), 0.45)


def test_alternating_values_by_hand():
    a = E.alternation(0.5)
    assert a["exploited"] == pytest.approx(5 * 0.5 / 1.5) and a["exploiter"] == pytest.approx(5 / 1.5)
    assert a["holds"] and a["threshold"] == pytest.approx(0.25)
    assert not E.alternation(0.2)["holds"] and E.alternation(0.25)["holds"]


def test_preset_stories():
    def run(name):
        p = C.PRESETS[name]
        return E.analyse(E.Settings(p["delta"], p["v1"], p["v2"]))

    a = run("Gegenseitige Kooperation (3 / 3) bei δ = 0,60")
    assert a.trigger and a.aps
    b = run("Knapp unter der Schwelle (3 / 3 bei δ = 0,45)")
    assert not b.trigger and not b.aps and b.threshold_aps == pytest.approx(0.5, abs=1e-6)
    c = run("Einseitig vorteilhaft (4 / 1,5) bei δ = 0,60")
    assert c.aps and not c.trigger
    d = run("Abwechselnd ausbeuten (2,5 / 2,5) bei δ = 0,30")
    assert d.aps and not d.trigger
    e = run("Sehr kurzer Schatten (δ = 0,15)")
    assert not e.aps and e.area_aps == 0.0


def test_verdict_levels_and_texts():
    base = E.Settings(0.6, 3.0, 3.0)
    assert E.verdict(E.analyse(base), base)[0] == "success"
    off = E.Settings(0.6, 4.8, 4.8)
    level, text = E.verdict(E.analyse(off), off)
    assert level == "error" and "nicht zulässig" in text
    low = E.Settings(0.6, 0.5, 4.5)
    level, text = E.verdict(E.analyse(low), low)
    assert level == "error" and "individuell rational" in text
    only_full = E.Settings(0.6, 4.0, 1.5)
    level, text = E.verdict(E.analyse(only_full), only_full)
    assert level == "info" and "nicht mit einer stationären Trigger-Strategie" in text
    short = E.Settings(0.45, 3.0, 3.0)
    level, text = E.verdict(E.analyse(short), short)
    assert level == "warning" and "0,50" in text


def test_area_curves_have_the_right_shape():
    curves = E.area_curves(deltas=(0.2, 0.3, 0.5, 0.9))
    assert curves["aps"] == pytest.approx([0.0, 4.5, FULL, FULL], abs=1e-6)
    assert curves["trigger"][0] < 0.01 and curves["trigger"][3] > curves["trigger"][2] > curves["trigger"][1]
