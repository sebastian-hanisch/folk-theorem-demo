"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import numpy as np
import plotly.graph_objects as go

import fkt_algorithm as A
import fkt_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=420, legend=True):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor="rgba(0,0,0,0)", showlegend=legend,
                      legend=dict(orientation="h", y=-0.2))
    return lock_axes(fig)


def _poly_trace(poly, name, color, line=None):
    pts = [tuple(p) for p in poly]
    if len(pts) >= 3:
        pts = pts + [pts[0]]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    mode = "lines" if len(pts) >= 2 else "markers"
    return go.Scatter(x=xs, y=ys, mode=mode, name=name, fill="toself" if len(pts) >= 4 else None, fillcolor=color,
                      line=dict(color=line or color, width=2), marker=dict(size=10, color=line or color),
                      hovertemplate=name + ": (%{x:.2f} / %{y:.2f})<extra></extra>")


def build_sets(delta, aps_poly, grid, v):
    """Die Ebene der Auszahlungspaare (A auf der x-Achse, B auf der y-Achse): zulässige Hülle, individuell rationale Menge, volle Gleichgewichtsmenge
    und die stationär tragbare Menge; der gewählte Punkt ist markiert."""
    fig = go.Figure()
    fig.add_trace(_poly_trace(A.feasible_polygon(individually_rational=False), "zulässig (Hülle der vier Stufenauszahlungen)", C.COLOR_FEASIBLE, "rgba(100,100,100,0.6)"))
    fig.add_trace(_poly_trace(A.feasible_polygon(), "zulässig und individuell rational (beide mindestens 1)", C.COLOR_IR, "rgba(80,80,80,0.9)"))
    if aps_poly:
        fig.add_trace(_poly_trace([np.array(p) for p in aps_poly], f"alle Gleichgewichte bei δ = {delta:.2f}".replace(".", ","), C.COLOR_APS, "#2f5d8a"))
    z = np.array(grid["z"], dtype=float)
    z[z == 0] = np.nan
    fig.add_trace(go.Heatmap(x=grid["x"], y=grid["x"], z=z, showscale=False, colorscale=[[0, C.COLOR_TRIGGER], [1, C.COLOR_TRIGGER]], zmin=0, zmax=1,
                             name="stationär tragbar (Trigger)", hoverinfo="skip", opacity=0.85))
    fig.add_trace(go.Scatter(x=[v[0]], y=[v[1]], mode="markers", name="gewähltes Paar", marker=dict(size=14, color=C.COLOR_POINT, symbol="x"),
                             hovertemplate="gewählt: (%{x:.2f} / %{y:.2f})<extra></extra>"))
    fig.update_xaxes(title_text="mittlere Auszahlung je Runde für A", range=[-0.2, 5.3])
    fig.update_yaxes(title_text="… für B", range=[-0.2, 5.3])
    return _base(fig, height=520)


def build_areas(curves):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=curves["delta"], y=curves["feasible"], mode="lines", name="zulässig und individuell rational",
                             line=dict(color="rgba(80,80,80,0.9)", width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=curves["delta"], y=curves["aps"], mode="lines+markers", name="alle Gleichgewichte", line=dict(color="#2f5d8a", width=4)))
    fig.add_trace(go.Scatter(x=curves["delta"], y=curves["trigger"], mode="lines+markers", name="stationär tragbar (Trigger)", line=dict(color=C.COLOR_TRIGGER, width=4)))
    fig.update_xaxes(title_text="Schatten der Zukunft δ")
    fig.update_yaxes(title_text="Fläche der tragbaren Paare")
    return _base(fig, height=380)


def build_alternation(curves):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=curves["delta"], y=curves["exploiter"], mode="lines", name="Wert für den Ausbeutenden", line=dict(color="#e08a2c", width=3)))
    fig.add_trace(go.Scatter(x=curves["delta"], y=curves["exploited"], mode="lines", name="Wert für den Ausgebeuteten", line=dict(color=C.COLOR_TRIGGER, width=4)))
    fig.add_hline(y=C.P, line=dict(color=C.COLOR_POINT, width=2, dash="dash"), annotation_text="Abweichen bringt P = 1", annotation_position="top left")
    fig.update_xaxes(title_text="Schatten der Zukunft δ")
    fig.update_yaxes(title_text="Wert je Runde im Wechsel")
    return _base(fig, height=360)
