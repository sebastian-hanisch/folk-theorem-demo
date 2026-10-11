"""Mini-Instanz-Tests je Einheit (DEMO-PLAYBOOK §1b): alles von Hand gerechnet, Auszahlungen 5/3/1/0."""

import numpy as np
import pytest

import fkt_algorithm as A
import fkt_constants as C
from fkt_scenario import deviation_gain, profile_payoff, stage_payoff

CC, CD, DC, DD = (0, 0), (0, 1), (1, 0), (1, 1)


def test_stage_and_profile_payoffs():
    assert stage_payoff(0, 0) == 3 and stage_payoff(0, 1) == 0 and stage_payoff(1, 0) == 5 and stage_payoff(1, 1) == 1
    assert profile_payoff(CC) == (3, 3) and profile_payoff(CD) == (0, 5) and profile_payoff(DC) == (5, 0) and profile_payoff(DD) == (1, 1)


def test_deviation_gains_by_hand():
    assert deviation_gain(CC, 0) == 2 and deviation_gain(CC, 1) == 2          # T − R
    assert deviation_gain(CD, 0) == 1                                         # A kooperiert gegen D: P − S
    assert deviation_gain(CD, 1) == 0                                         # B defektiert gegen C: kann nicht mehr bekommen
    assert deviation_gain(DC, 1) == 1 and deviation_gain(DC, 0) == 0
    assert deviation_gain(DD, 0) == 0 and deviation_gain(DD, 1) == 0


def test_punishment_threshold_by_hand():
    assert A.punishment_threshold(CC, 0, 0.5) == pytest.approx(3.0)           # 1 + (0,5 / 0,5) · 2
    assert A.punishment_threshold(CD, 0, 0.5) == pytest.approx(2.0)           # 1 + 1 · 1
    assert A.punishment_threshold(CD, 1, 0.5) == pytest.approx(1.0)           # kein Gewinn aus dem Abweichen
    assert A.punishment_threshold(CC, 0, 0.25) == pytest.approx(7.0)          # 1 + 3 · 2
    assert A.punishment_threshold(DD, 0, 0.1) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        A.punishment_threshold(CC, 0, 1.0)


def test_allowed_profiles():
    assert set(A.allowed_profiles((3.0, 3.0), 0.5)) == {CC, CD, DC, DD}
    assert CC not in A.allowed_profiles((3.0, 3.0), 0.49)
    assert A.allowed_profiles((1.0, 1.0), 0.1) == [DD]


def test_trigger_weights_by_hand():
    assert A.trigger_weights((3.0, 3.0), 0.6) == {CC: pytest.approx(1.0)}
    w = A.trigger_weights((4.0, 1.5), 0.8)
    assert w == {CC: pytest.approx(0.5), DC: pytest.approx(0.5)}              # 0,5 · (3,3) + 0,5 · (5,0)
    assert A.trigger_weights((4.0, 1.5), 0.7) is None                         # (C,C) wäre nötig, aber B bekäme zu wenig
    assert A.trigger_weights((1.0, 1.0), 0.1) == {DD: pytest.approx(1.0)}
    assert A.trigger_weights((4.9, 4.9), 0.99) is None                        # nicht zulässig


def test_convex_combination_rejects_points_outside_the_hull():
    assert A.convex_combination((4.0, 4.0), list(C.PROFILES)) is None
    assert A.convex_combination((2.5, 2.5), [CD, DC]) == {CD: pytest.approx(0.5), DC: pytest.approx(0.5)}


def test_polygon_area_and_clipping():
    square = [np.array(p, float) for p in ((0, 0), (2, 0), (2, 2), (0, 2))]
    assert A.polygon_area(square) == pytest.approx(4.0)
    half = A.clip_halfplane(square, np.array([1.0, 0.0]), 1.0)
    assert A.polygon_area(half) == pytest.approx(2.0)
    assert A.clip_halfplane(square, np.array([1.0, 0.0]), 3.0) == []


def test_polygon_contains_including_degenerate_polygons():
    tri = [np.array(p, float) for p in ((0, 0), (4, 0), (0, 4))]
    assert A.polygon_contains(tri, (1, 1)) and not A.polygon_contains(tri, (3, 3))
    seg = [np.array((1.0, 1.0)), np.array((3.0, 3.0))]
    assert A.polygon_contains(seg, (2, 2)) and not A.polygon_contains(seg, (2, 2.5))
    assert A.polygon_contains([np.array((1.0, 1.0))], (1, 1)) and not A.polygon_contains([np.array((1.0, 1.0))], (1, 1.1))
    assert not A.polygon_contains([], (1, 1))


def test_feasible_polygons():
    assert A.polygon_area(A.feasible_polygon()) == pytest.approx(20 / 3, abs=1e-6)           # (1,1), (13/3,1), (3,3), (1,13/3)
    full = A.feasible_polygon(individually_rational=False)
    assert A.polygon_contains(full, (3, 3)) and A.polygon_contains(full, (0, 5)) and not A.polygon_contains(full, (4.5, 4.5))


def test_aps_phases_by_hand():
    assert A.polygon_area(A.aps_set(0.1)) == 0.0 and A.polygon_contains(A.aps_set(0.1), (1, 1))
    assert not A.polygon_contains(A.aps_set(0.2), (2.5, 2.5))
    tri = A.aps_set(0.3)
    assert A.polygon_area(tri) == pytest.approx(4.5, abs=1e-6)
    assert A.polygon_contains(tri, (2.5, 2.5)) and A.polygon_contains(tri, (4.0, 1.0)) and not A.polygon_contains(tri, (3.0, 3.0))
    assert A.polygon_area(A.aps_set(0.5)) == pytest.approx(20 / 3, abs=1e-6)
    assert A.polygon_contains(A.aps_set(0.5), (3.0, 3.0))


def test_aps_set_validates_delta():
    with pytest.raises(ValueError):
        A.aps_set(1.0)
    with pytest.raises(ValueError):
        A.aps_set(0.0)


def test_threshold_delta_closed_forms():
    assert A.threshold_delta((3.0, 3.0), "trigger") == pytest.approx(0.5, abs=1e-6)       # (T − R)/(T − P)
    assert A.threshold_delta((3.0, 3.0), "aps") == pytest.approx(0.5, abs=1e-6)
    assert A.threshold_delta((2.5, 2.5), "aps") == pytest.approx(0.25, abs=1e-6)          # (P − S)/(T − P)
    assert A.threshold_delta((2.5, 2.5), "trigger") == pytest.approx(0.4, abs=1e-6)       # 1 + (1 − δ)/δ ≤ 2,5
    assert A.threshold_delta((4.0, 1.5), "trigger") == pytest.approx(0.8, abs=1e-6)       # (C,C) in der Mischung: 1 + 2 (1 − δ)/δ ≤ 1,5
    assert A.threshold_delta((4.0, 1.5), "aps") == pytest.approx(0.5, abs=1e-6)
    assert A.threshold_delta((1.0, 4.0), "trigger") is None
    assert A.threshold_delta((1.0, 4.0), "aps") == pytest.approx(0.25, abs=1e-6)


def test_trigger_area_is_zero_for_a_very_short_shadow_and_grows():
    assert A.trigger_area(0.2) < 0.01
    areas = [A.trigger_area(d) for d in (0.45, 0.5, 0.6, 0.8, 0.95)]
    assert areas == sorted(areas) and areas[-1] < A.polygon_area(A.feasible_polygon()) + 1e-9
