"""Kern der Demo (numpy): welche Auszahlungspaare trägt das unendlich wiederholte Gefangenendilemma als Gleichgewicht?

Einheiten (DEMO-PLAYBOOK §1b):

- `punishment_threshold`  was die Fortsetzung mindestens wert sein muss, damit niemand in diesem Profil abweicht
- `allowed_profiles`      Profile, die ein Paar v stationär tragen kann
- `trigger_weights`       Mischung der Profile (öffentliche Zufallsvorrichtung), die v erzeugt, nur aus tragbaren Profilen
- `convex_hull`, `clip_halfplane`, `polygon_area`, `polygon_contains`   Polygonoperationen
- `feasible_polygon`      zulässige, individuell rationale Menge
- `aps_set`               volle Menge der Gleichgewichtsauszahlungen (Abreu, Pearce, Stacchetti) als Polygon
- `threshold_delta`       kleinstes δ, ab dem ein Paar tragbar ist (Bisektion)

Mit öffentlicher Zufallsvorrichtung (beide sehen denselben Münzwurf). Strafe bei Abweichen: dauerhaft gegenseitige Defektion, die schärfste
mögliche Strafe, weil sie sowohl Minimax als auch Gleichgewicht des Stufenspiels ist."""

import itertools
from functools import lru_cache

import numpy as np

import fkt_constants as C
from fkt_scenario import STAGE_POINTS, deviation_gain, profile_payoff

PUNISH = C.P   # Minimaxwert jedes Spielers: beide defektieren


def punishment_threshold(profile: tuple[int, int], player: int, delta: float) -> float:
    """Mindestwert der Fortsetzung für `player`, damit er im Profil nicht abweicht:
    (1 − δ) · Gewinn ≤ δ · (Fortsetzung − P), also Fortsetzung ≥ P + (1 − δ)/δ · Gewinn."""
    if not 0.0 < delta < 1.0:
        raise ValueError("δ muss in (0, 1) liegen")
    return PUNISH + (1.0 - delta) / delta * deviation_gain(profile, player)


def allowed_profiles(v: tuple[float, float], delta: float) -> list[tuple[int, int]]:
    """Profile, in denen beide Spieler mit der stationären Fortsetzung v nicht abweichen wollen."""
    return [p for p in C.PROFILES
            if all(v[i] >= punishment_threshold(p, i, delta) - C.TOL for i in (0, 1))]


def _barycentric(point, a, b, c):
    m = np.array([[b[0] - a[0], c[0] - a[0]], [b[1] - a[1], c[1] - a[1]]])
    det = np.linalg.det(m)
    if abs(det) < 1e-12:
        return None
    s, t = np.linalg.solve(m, np.array(point) - np.array(a))
    return 1.0 - s - t, s, t


def convex_combination(point, profiles) -> dict | None:
    """Gewichte über `profiles` (nichtnegativ, Summe 1) mit Σ w · Auszahlung = point; None, wenn der Punkt nicht in der Hülle liegt.
    Probiert Einzelpunkt, Strecken und Dreiecke (Carathéodory in der Ebene)."""
    pts = [np.array(profile_payoff(p)) for p in profiles]
    point = np.array(point, dtype=float)
    for p, prof in zip(pts, profiles):
        if np.allclose(p, point, atol=C.TOL):
            return {prof: 1.0}
    for (i, p), (j, q) in itertools.combinations(list(enumerate(pts)), 2):
        d = q - p
        cross = d[0] * (point - p)[1] - d[1] * (point - p)[0]
        if abs(cross) < 1e-9:
            t = float(np.dot(point - p, d) / np.dot(d, d))
            if -C.TOL <= t <= 1 + C.TOL:
                return {profiles[i]: 1.0 - t, profiles[j]: t}
    for (i, p), (j, q), (k, r) in itertools.combinations(list(enumerate(pts)), 3):
        bary = _barycentric(point, p, q, r)
        if bary is not None and all(w >= -C.TOL for w in bary):
            return {profiles[i]: bary[0], profiles[j]: bary[1], profiles[k]: bary[2]}
    return None


def trigger_weights(v: tuple[float, float], delta: float) -> dict | None:
    """Mischung der tragbaren Profile, die v als stationäres Gleichgewichtspaar erzeugt (Grim-Trigger-Strafe), sonst None."""
    return convex_combination(v, allowed_profiles(v, delta))


def trigger_contains(v: tuple[float, float], delta: float) -> bool:
    return trigger_weights(v, delta) is not None


# --- Polygone ------------------------------------------------------------------------------------------------------------------------------

def convex_hull(points) -> list[np.ndarray]:
    """Konvexe Hülle (Andrew), gegen den Uhrzeigersinn; Zwei- und Einpunktfälle bleiben erhalten."""
    pts = sorted({(round(float(p[0]), 9), round(float(p[1]), 9)) for p in points})
    if len(pts) <= 2:
        return [np.array(p) for p in pts]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 1e-14:
            lower.pop()
        lower.append(p)
    upper: list = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 1e-14:
            upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    if not hull:
        return [np.array(pts[0])]
    arr = [np.array(p) for p in hull]
    if len(arr) >= 3 and polygon_area(arr) < 1e-9:            # numerisch eine Strecke: auf die beiden äußersten Punkte zurückführen
        far = max(itertools.combinations(arr, 2), key=lambda pq: float(np.linalg.norm(pq[0] - pq[1])))
        return [far[0], far[1]] if float(np.linalg.norm(far[0] - far[1])) > 1e-9 else [far[0]]
    return arr


def clip_halfplane(poly, normal, offset) -> list[np.ndarray]:
    """Schnitt mit der Halbebene normal · x ≥ offset (Sutherland-Hodgman)."""
    if not poly:
        return []
    if len(poly) == 1:
        return poly if float(np.dot(normal, poly[0])) >= offset - 1e-12 else []
    out = []
    n = len(poly)
    for i in range(n):
        cur, nxt = poly[i], poly[(i + 1) % n]
        dc, dn = float(np.dot(normal, cur)) - offset, float(np.dot(normal, nxt)) - offset
        if dc >= -1e-12:
            out.append(cur)
        if (dc >= -1e-12) != (dn >= -1e-12):
            out.append(cur + dc / (dc - dn) * (nxt - cur))
    return convex_hull(out) if out else []


def polygon_area(poly) -> float:
    if len(poly) < 3:
        return 0.0
    x = np.array([p[0] for p in poly])
    y = np.array([p[1] for p in poly])
    return float(0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def polygon_contains(poly, point, tol: float = 1e-9) -> bool:
    """Liegt `point` im (auch entarteten) konvexen Polygon `poly`?"""
    if not poly:
        return False
    point = np.array(point, dtype=float)
    if len(poly) == 1:
        return bool(np.allclose(poly[0], point, atol=tol))
    if len(poly) == 2:
        p, q = poly
        d = q - p
        if abs(d[0] * (point - p)[1] - d[1] * (point - p)[0]) > tol:
            return False
        t = float(np.dot(point - p, d) / np.dot(d, d))
        return -tol <= t <= 1 + tol
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        if (b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0]) < -tol:
            return False
    return True


def feasible_polygon(individually_rational: bool = True) -> list[np.ndarray]:
    """Hülle der vier Stufenauszahlungen; mit `individually_rational` auf v_i ≥ P beschnitten (Folk-Theorem-Region)."""
    poly = convex_hull(STAGE_POINTS)
    if individually_rational:
        poly = clip_halfplane(poly, np.array([1.0, 0.0]), PUNISH)
        poly = clip_halfplane(poly, np.array([0.0, 1.0]), PUNISH)
    return poly


@lru_cache(maxsize=1024)
def _aps_cached(delta: float) -> tuple:
    return tuple(_aps_compute(delta))


def aps_set(delta: float) -> list[np.ndarray]:
    """Wie `_aps_compute`, aber zwischengespeichert (reine Funktion von δ)."""
    return list(_aps_cached(round(float(delta), 12)))


def _aps_compute(delta: float) -> list[np.ndarray]:
    """Menge aller Gleichgewichtsauszahlungen (normiert, mit öffentlicher Zufallsvorrichtung) als konvexes Polygon.

    Iteration W ← B(W) von der zulässigen, individuell rationalen Menge aus: B(W) ist die Hülle aller (1 − δ)·u(a) + δ·w mit w in W, die in a
    für beide Spieler anreizverträglich sind (w_i ≥ P + (1 − δ)/δ · Gewinn_i(a)). Die Folge fällt monoton gegen die größte selbsterzeugende Menge."""
    if not 0.0 < delta < 1.0:
        raise ValueError("δ muss in (0, 1) liegen")
    w = feasible_polygon()
    for _ in range(C.APS_MAX_ITERATIONS):
        new_points = []
        for a in C.PROFILES:
            wa = w
            for i, normal in ((0, np.array([1.0, 0.0])), (1, np.array([0.0, 1.0]))):
                wa = clip_halfplane(wa, normal, punishment_threshold(a, i, delta))
                if not wa:
                    break
            u = np.array(profile_payoff(a))
            new_points.extend((1.0 - delta) * u + delta * q for q in wa)
        nxt = convex_hull(new_points)
        if not nxt:
            return []
        same = len(nxt) == len(w) and all(np.allclose(p, q, rtol=0.0, atol=1e-11) for p, q in zip(nxt, w))
        w = nxt
        if same:
            break
    return w


def aps_contains(v: tuple[float, float], delta: float) -> bool:
    return polygon_contains(aps_set(delta), v)


def threshold_delta(v: tuple[float, float], kind: str = "aps", lo: float = 0.001, hi: float = 0.999, steps: int = 40) -> float | None:
    """Kleinstes δ, ab dem `v` tragbar ist (`kind` = "aps" oder "trigger"); None, wenn selbst bei δ = hi nicht. Beide Mengen wachsen mit δ."""
    contains = aps_contains if kind == "aps" else trigger_contains
    if not contains(v, hi):
        return None
    if contains(v, lo):
        return lo
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        if contains(v, mid):
            hi = mid
        else:
            lo = mid
    return hi


# --- Vektorisierte Trigger-Menge (für Flächen und Karten) ---------------------------------------------------------------------------------

def _hull_contains_vec(poly, pts: np.ndarray, tol: float = 1e-9) -> np.ndarray:
    """Für viele Punkte (n, 2): liegen sie im (möglicherweise entarteten) konvexen Polygon?"""
    n = pts.shape[0]
    if not poly:
        return np.zeros(n, dtype=bool)
    if len(poly) == 1:
        return np.all(np.abs(pts - poly[0]) <= tol, axis=1)
    if len(poly) == 2:
        p, q = poly
        d = q - p
        cross = d[0] * (pts[:, 1] - p[1]) - d[1] * (pts[:, 0] - p[0])
        t = ((pts[:, 0] - p[0]) * d[0] + (pts[:, 1] - p[1]) * d[1]) / float(np.dot(d, d))
        return (np.abs(cross) <= tol) & (t >= -tol) & (t <= 1 + tol)
    inside = np.ones(n, dtype=bool)
    m = len(poly)
    for i in range(m):
        a, b = poly[i], poly[(i + 1) % m]
        inside &= (b[0] - a[0]) * (pts[:, 1] - a[1]) - (b[1] - a[1]) * (pts[:, 0] - a[0]) >= -tol
    return inside


def trigger_mask(pts: np.ndarray, delta: float) -> np.ndarray:
    """Für viele Punkte (n, 2): ist das Paar stationär tragbar? Punkte werden nach der Menge ihrer tragbaren Profile gruppiert (höchstens 16 Gruppen)."""
    if not 0.0 < delta < 1.0:
        raise ValueError("δ muss in (0, 1) liegen")
    n = pts.shape[0]
    allowed = np.zeros((n, len(C.PROFILES)), dtype=bool)
    for k, prof in enumerate(C.PROFILES):
        ok = np.ones(n, dtype=bool)
        for i in (0, 1):
            ok &= pts[:, i] >= punishment_threshold(prof, i, delta) - C.TOL
        allowed[:, k] = ok
    out = np.zeros(n, dtype=bool)
    keys = allowed @ (1 << np.arange(len(C.PROFILES)))
    for key in np.unique(keys):
        sel = keys == key
        profiles = [p for k, p in enumerate(C.PROFILES) if key & (1 << k)]
        if not profiles:
            continue
        hull = convex_hull([profile_payoff(p) for p in profiles])
        out[sel] = _hull_contains_vec(hull, pts[sel])
    return out


@lru_cache(maxsize=256)
def trigger_area(delta: float, step: float = 0.025) -> float:
    """Fläche der stationär tragbaren Menge (Raster über [0, 5]²; Fehler etwa die Rasterfläche mal Randlänge)."""
    xs = np.arange(0.0, 5.0 + 1e-9, step)
    gx, gy = np.meshgrid(xs, xs)
    pts = np.column_stack([gx.ravel(), gy.ravel()])
    return float(trigger_mask(pts, delta).sum()) * step * step
