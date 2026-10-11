"""Orakel-Tests folk-theorem-demo: der Kern wird gegen UNABHÄNGIGE Rechenwege geprüft (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK §2).

Alle Orakel benutzen `scipy.optimize.linprog` und eine eigene, in dieser Datei aufgeschriebene Auszahlungstabelle; weder Polygonoperationen noch die
APS-Iteration des Kerns werden verwendet.

1. Trigger-Menge: Zugehörigkeit eines Paares als LP (Mischung nur über die Profile, deren Anreizbedingung mit v als Fortsetzung hält).
2. Volle Gleichgewichtsmenge W: die Fixpunkt-Bedingung W = B(W) als LP je Punkt, wobei W durch die Ecken des vom Kern gelieferten Polygons gegeben ist:
   (a) Ecken und innere Punkte liegen in B(W) (W ⊆ B(W): jeder Punkt ist tatsächlich ein Gleichgewicht, Selbsterzeugung),
   (b) Punkte knapp außerhalb liegen nicht in B(W) (B(W) ⊆ W: nichts Zusätzliches).
3. Abwechseln: Werte der Zwei-Zustands-Strategie aus dem linearen System, Schwelle 1/4."""

import itertools

import numpy as np
import pytest

import fkt_algorithm as A

linprog = pytest.importorskip("scipy.optimize").linprog

# Eigene Auszahlungstabelle: (Aktion A, Aktion B) -> (Auszahlung A, Auszahlung B); 0 = kooperieren, 1 = defektieren
U = {(0, 0): (3.0, 3.0), (0, 1): (0.0, 5.0), (1, 0): (5.0, 0.0), (1, 1): (1.0, 1.0)}
MINIMAX = 1.0


def gain(profile, i):
    """Gewinn des Spielers i aus einseitigem Abweichen, direkt aus der Tabelle."""
    a = list(profile)
    best = U[profile][i]
    for alt in (0, 1):
        b = a.copy()
        b[i] = alt
        best = max(best, U[tuple(b)][i])
    return best - U[profile][i]


def trigger_lp(v, delta):
    """Existiert eine Mischung λ über die Profile mit Σλ·u = v, die nur Profile mit v_i ≥ P + (1 − δ)/δ · Gewinn_i verwendet?"""
    profiles = list(U)
    bounds = []
    for p in profiles:
        ok = all(v[i] >= MINIMAX + (1 - delta) / delta * gain(p, i) - 1e-9 for i in (0, 1))
        bounds.append((0, None) if ok else (0, 0))
    a_eq = np.array([[U[p][0] for p in profiles], [U[p][1] for p in profiles], [1.0] * 4])
    b_eq = np.array([v[0], v[1], 1.0])
    res = linprog(c=np.zeros(4), A_eq=a_eq, b_eq=b_eq, bounds=bounds, method="highs")
    return res.status == 0


def in_b_of_w(v, delta, vertices):
    """Liegt v in B(W) für das Polygon W mit den Ecken `vertices`? LP über λ_a (Profilgewichte) und μ_{a,k} (Gewichte der Fortsetzung auf den Ecken)."""
    profiles = list(U)
    k = len(vertices)
    n = len(profiles) + len(profiles) * k                  # λ_a, dann μ_{a,k}
    a_eq, b_eq = [], []
    row = np.zeros(n)
    row[: len(profiles)] = 1.0
    a_eq.append(row)
    b_eq.append(1.0)
    for ai in range(len(profiles)):                         # Σ_k μ_{a,k} = λ_a
        row = np.zeros(n)
        row[ai] = -1.0
        row[len(profiles) + ai * k: len(profiles) + (ai + 1) * k] = 1.0
        a_eq.append(row)
        b_eq.append(0.0)
    for i in (0, 1):                                        # v_i = Σ_a λ_a (1 − δ) u_i(a) + δ Σ_{a,k} μ_{a,k} vertex_k,i
        row = np.zeros(n)
        for ai, p in enumerate(profiles):
            row[ai] = (1 - delta) * U[p][i]
            for kk in range(k):
                row[len(profiles) + ai * k + kk] = delta * vertices[kk][i]
        a_eq.append(row)
        b_eq.append(v[i])
    a_ub, b_ub = [], []
    for ai, p in enumerate(profiles):                       # Anreiz: δ Σ_k μ_{a,k} w_k,i ≥ (δ P + (1 − δ) g_i(a)) λ_a
        for i in (0, 1):
            row = np.zeros(n)
            row[ai] = delta * MINIMAX + (1 - delta) * gain(p, i)
            for kk in range(k):
                row[len(profiles) + ai * k + kk] = -delta * vertices[kk][i]
            a_ub.append(row)
            b_ub.append(0.0)
    res = linprog(c=np.zeros(n), A_eq=np.array(a_eq), b_eq=np.array(b_eq), A_ub=np.array(a_ub), b_ub=np.array(b_ub),
                  bounds=[(0, None)] * n, method="highs")
    return res.status == 0


@pytest.mark.parametrize("delta", [0.3, 0.45, 0.5, 0.55, 0.7, 0.9])
def test_trigger_membership_matches_the_lp_on_a_grid(delta):
    xs = np.arange(0.0, 5.01, 0.25)
    for x, y in itertools.product(xs, xs):
        assert A.trigger_contains((float(x), float(y)), delta) == trigger_lp((float(x), float(y)), delta), (x, y, delta)


def test_vectorised_trigger_mask_matches_the_lp():
    rng = np.random.default_rng(2)
    pts = rng.uniform(0.0, 5.0, size=(150, 2))
    for delta in (0.4, 0.6, 0.85):
        mask = A.trigger_mask(pts, delta)
        for p, m in zip(pts, mask):
            assert bool(m) == trigger_lp(tuple(p), delta)


@pytest.mark.parametrize("delta", [0.1, 0.3, 0.45, 0.5, 0.6, 0.8, 0.95])
def test_aps_set_is_a_fixed_point_of_the_generating_operator(delta):
    poly = A.aps_set(delta)
    verts = [tuple(float(c) for c in p) for p in poly]
    # (a) Selbsterzeugung: Ecken, Mittelpunkt und ein Punkt zwischen Ecke und Mittelpunkt sind in B(W)
    centre = tuple(np.mean(verts, axis=0))
    probes = list(verts) + [centre] + [tuple(0.5 * (np.array(v) + np.array(centre))) for v in verts]
    for p in probes:
        assert in_b_of_w(p, delta, verts), (delta, p)
    # (b) nichts Zusätzliches: Punkte knapp außerhalb (Normale nach außen von jeder Ecke und jeder Kantenmitte) sind nicht in B(W)
    outside = []
    if len(verts) >= 3:
        for i in range(len(verts)):
            a, b = np.array(verts[i]), np.array(verts[(i + 1) % len(verts)])
            mid = 0.5 * (a + b)
            edge = b - a
            normal = np.array([edge[1], -edge[0]])                 # nach außen bei Umlauf gegen den Uhrzeigersinn
            normal = normal / np.linalg.norm(normal)
            outside.append(tuple(mid + 1e-3 * normal))
    outside.append((1.0 - 1e-3, 1.0 - 1e-3))
    for p in outside:
        assert not in_b_of_w(p, delta, verts), (delta, p)


def test_the_alternating_strategy_by_a_linear_system_and_its_threshold():
    """Zwei Zustände: E1 = (A ausgebeutet), E2 = (B ausgebeutet); jeder geht in den anderen über. Werte aus V = u + δ P V, unabhängig von der Formel im Kern."""
    def values(delta):
        u = np.array([U[(0, 1)][0], U[(1, 0)][0]])        # Auszahlung für A in E1 (kooperiert gegen D) und in E2 (defektiert gegen C)
        p = np.array([[0.0, 1.0], [1.0, 0.0]])
        return np.linalg.solve(np.eye(2) - delta * p, u)

    for delta in (0.2, 0.25, 0.3, 0.5):
        v = (1 - delta) * values(delta)                   # normiert: mittlerer Wert je Runde
        assert v[0] == pytest.approx((0.0 + delta * 5.0) / (1 + delta)) and v[1] == pytest.approx((5.0 + delta * 0.0) / (1 + delta))
    # Anreiz: Wert des Ausgebeuteten ≥ 1 genau ab δ = 1/4
    holds = lambda d: (0.0 + d * 5.0) / (1 + d) >= 1.0 - 1e-12   # noqa: E731
    assert not holds(0.249) and holds(0.25) and holds(0.5)
    assert A.aps_contains((2.5, 2.5), 0.25 + 1e-6) and not A.aps_contains((2.5, 2.5), 0.25 - 1e-3)


def test_aps_sets_are_nested_in_delta_and_contain_the_trigger_points():
    deltas = [0.1, 0.25, 0.3, 0.45, 0.5, 0.6, 0.8, 0.95]
    polys = [A.aps_set(d) for d in deltas]
    for (d1, p1), (d2, p2) in zip(zip(deltas, polys), zip(deltas[1:], polys[1:])):
        for v in p1:
            assert A.polygon_contains(p2, tuple(v), tol=1e-7), (d1, d2, v)
    rng = np.random.default_rng(5)
    pts = rng.uniform(0, 5, size=(120, 2))
    for d, p in zip(deltas, polys):
        for q, m in zip(pts, A.trigger_mask(pts, d)):
            if m:
                assert A.polygon_contains(p, tuple(q), tol=1e-7), (d, q)
