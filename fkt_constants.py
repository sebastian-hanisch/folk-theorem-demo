"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

COOPERATE, DEFECT = 0, 1

# Auszahlungen je Runde (Axelrod), fest.
T, R, P, S = 5.0, 3.0, 1.0, 0.0

DELTA_MIN, DELTA_MAX, DEFAULT_DELTA, DELTA_STEP = 0.05, 0.95, 0.60, 0.01
V_MIN, V_MAX, V_STEP = 0.0, 5.0, 0.1
DEFAULT_V1, DEFAULT_V2 = 3.0, 3.0

PROFILES = ((COOPERATE, COOPERATE), (COOPERATE, DEFECT), (DEFECT, COOPERATE), (DEFECT, DEFECT))
PROFILE_NAMES = {(0, 0): "beide kooperieren", (0, 1): "A kooperiert, B defektiert", (1, 0): "A defektiert, B kooperiert", (1, 1): "beide defektieren"}

TOL = 1e-9
APS_MAX_ITERATIONS = 4000
AREA_DELTAS = tuple(round(0.05 * i, 2) for i in range(1, 20))     # 0,05 bis 0,95
GRID_N = 60                                                     # Auflösung der Trigger-Karte

COLOR_FEASIBLE = "rgba(150,150,150,0.25)"
COLOR_IR = "rgba(150,150,150,0.55)"
COLOR_APS = "rgba(76,120,168,0.45)"
COLOR_TRIGGER = "rgba(47,107,101,0.75)"
COLOR_POINT = "#B5483A"

PRESETS = {
    "Gegenseitige Kooperation (3 / 3) bei δ = 0,60": {"delta": 0.60, "v1": 3.0, "v2": 3.0},
    "Knapp unter der Schwelle (3 / 3 bei δ = 0,45)": {"delta": 0.45, "v1": 3.0, "v2": 3.0},
    "Einseitig vorteilhaft (4 / 1,5) bei δ = 0,60": {"delta": 0.60, "v1": 4.0, "v2": 1.5},
    "Abwechselnd ausbeuten (2,5 / 2,5) bei δ = 0,30": {"delta": 0.30, "v1": 2.5, "v2": 2.5},
    "Sehr kurzer Schatten (δ = 0,15)": {"delta": 0.15, "v1": 3.0, "v2": 3.0},
}
PRESET_HELP = {
    "Gegenseitige Kooperation (3 / 3) bei δ = 0,60": "Ab δ = 1/2 trägt gegenseitige Kooperation, schon mit einfacher Trigger-Strategie.",
    "Knapp unter der Schwelle (3 / 3 bei δ = 0,45)": "Unter 1/2 ist (3 / 3) kein Gleichgewichtspaar mehr, auch nicht mit komplizierteren Strategien.",
    "Einseitig vorteilhaft (4 / 1,5) bei δ = 0,60": "Das Folk-Theorem trägt auch sehr ungleiche Paare, solange jeder mehr als das Minimum 1 bekommt.",
    "Abwechselnd ausbeuten (2,5 / 2,5) bei δ = 0,30": "Bei δ = 0,30 trägt keine Kooperation, aber ein Wechsel: erst wird A ausgebeutet, dann B. Nur nicht-stationär.",
    "Sehr kurzer Schatten (δ = 0,15)": "Ganz kurze Beziehungen tragen nur gegenseitige Defektion (1 / 1).",
}
