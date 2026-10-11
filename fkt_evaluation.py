"""Kennzahlen, Verdikt-Logik und Auswertungen über den Kern (die Komposition der Einheiten aus fkt_algorithm)."""

from dataclasses import dataclass

import numpy as np

import fkt_algorithm as A
import fkt_constants as C


def fmt(x: float, digits: int = 2) -> str:
    """Zahl mit deutschem Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


@dataclass(frozen=True)
class Settings:
    delta: float = C.DEFAULT_DELTA
    v1: float = C.DEFAULT_V1
    v2: float = C.DEFAULT_V2


@dataclass(frozen=True)
class Analysis:
    feasible: bool                                   # in der Hülle der vier Stufenauszahlungen
    rational: bool                                   # beide mindestens P
    trigger: bool                                    # stationär tragbar (Grim-Trigger-Strafe, öffentliche Zufallsvorrichtung)
    aps: bool                                        # irgendwie als Gleichgewicht tragbar
    weights: dict | None                             # Profilmischung der Trigger-Konstruktion
    threshold_trigger: float | None
    threshold_aps: float | None
    aps_polygon: tuple
    area_feasible: float
    area_aps: float
    area_trigger: float


def analyse(settings: Settings) -> Analysis:
    v = (settings.v1, settings.v2)
    hull = A.feasible_polygon(individually_rational=False)
    poly = A.aps_set(settings.delta)
    return Analysis(
        feasible=A.polygon_contains(hull, v),
        rational=bool(v[0] >= C.P - C.TOL and v[1] >= C.P - C.TOL),
        trigger=A.trigger_contains(v, settings.delta),
        aps=A.polygon_contains(poly, v),
        weights=A.trigger_weights(v, settings.delta),
        threshold_trigger=A.threshold_delta(v, "trigger", steps=30),
        threshold_aps=A.threshold_delta(v, "aps", steps=30),
        aps_polygon=tuple(tuple(float(c) for c in p) for p in poly),
        area_feasible=A.polygon_area(A.feasible_polygon()),
        area_aps=A.polygon_area(poly),
        area_trigger=A.trigger_area(settings.delta),
    )


def area_curves(deltas=C.AREA_DELTAS) -> dict:
    """Fläche der zulässigen, individuell rationalen Menge, der vollen Gleichgewichtsmenge und der stationär tragbaren Menge je δ."""
    full = A.polygon_area(A.feasible_polygon())
    return {
        "delta": list(deltas),
        "feasible": [full] * len(deltas),
        "aps": [A.polygon_area(A.aps_set(d)) for d in deltas],
        "trigger": [A.trigger_area(d) for d in deltas],
    }


def alternation(delta: float) -> dict:
    """Abwechselndes Ausbeuten: A wird in einer Runde ausgebeutet (C gegen D), in der nächsten B, und so weiter.

    Wert für den gerade Ausgebeuteten: (S + δ·T)/(1 + δ); für den gerade Ausbeutenden: (T + δ·S)/(1 + δ). Abweichen bringt dem Ausgebeuteten P
    (er defektiert, dann defektieren beide für immer). Anreizverträglich genau dann, wenn (S + δ·T)/(1 + δ) ≥ P."""
    exploited = (C.S + delta * C.T) / (1.0 + delta)
    exploiter = (C.T + delta * C.S) / (1.0 + delta)
    return {"exploited": exploited, "exploiter": exploiter, "deviation": C.P, "holds": exploited >= C.P - C.TOL,
            "threshold": (C.P - C.S) / (C.T - C.P)}


def alternation_curves(deltas=C.AREA_DELTAS) -> dict:
    rows = [alternation(d) for d in deltas]
    return {"delta": list(deltas), "exploited": [r["exploited"] for r in rows], "exploiter": [r["exploiter"] for r in rows]}


def trigger_grid(delta: float, step: float = 0.1) -> dict:
    xs = np.arange(0.0, 5.0 + 1e-9, step)
    gx, gy = np.meshgrid(xs, xs)
    pts = np.column_stack([gx.ravel(), gy.ravel()])
    return {"x": xs.tolist(), "z": A.trigger_mask(pts, delta).reshape(gx.shape).astype(int).tolist()}


def verdict(an: Analysis, settings: Settings) -> tuple[str, str]:
    """(Stufe, Satz): ist das Paar (v1, v2) bei diesem δ als Gleichgewicht tragbar, und womit?"""
    v1, v2 = fmt(settings.v1, 1), fmt(settings.v2, 1)
    d = fmt(settings.delta)
    if not an.feasible:
        return "error", f"({v1} / {v2}) ist **nicht zulässig**: es liegt außerhalb der Hülle der vier Stufenauszahlungen, kein Spiel erzeugt es im Mittel."
    if not an.rational:
        return "error", f"({v1} / {v2}) ist **nicht individuell rational**: ein Spieler bekäme weniger als 1, das er durch ständiges Defektieren immer sichern kann."
    if an.trigger:
        names = ", ".join(f"{w * 100:.0f} % {name}" for name, w in _named(an.weights))
        return "success", (f"({v1} / {v2}) ist bei δ = {d} **tragbar, schon mit einer einfachen Trigger-Strategie**: Mischung {names}; wer abweicht, löst dauerhafte "
                           f"gegenseitige Defektion aus. Ab δ = {fmt(an.threshold_trigger)} gilt das.")
    if an.aps:
        return "info", (f"({v1} / {v2}) ist bei δ = {d} **tragbar, aber nicht mit einer stationären Trigger-Strategie**: es braucht Strategien, deren Fortsetzung "
                        f"sich über die Zeit ändert (etwa Wechsel der Rollen). Die Trigger-Variante trägt es erst ab δ = {fmt(an.threshold_trigger) if an.threshold_trigger else 'nie'}, "
                        f"die allgemeine ab δ = {fmt(an.threshold_aps)}.")
    need = fmt(an.threshold_aps) if an.threshold_aps is not None else None
    if need is None:
        return "warning", f"({v1} / {v2}) ist bei **keinem** δ < 1 tragbar."
    return "warning", f"({v1} / {v2}) ist bei δ = {d} **nicht tragbar**: die Beziehung ist zu kurz. Ab δ = {need} wäre es möglich."


def _named(weights: dict | None):
    from fkt_constants import PROFILE_NAMES
    return [(PROFILE_NAMES[p], w) for p, w in (weights or {}).items()]
