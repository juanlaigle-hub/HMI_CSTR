"""CSTR HMI Training Simulator — Dash app with live 3D view.

Run:  python hmi/app.py   → opens http://127.0.0.1:8050

The process is simulated here (cstr_model.py). Each tick the state is sent
with postMessage to the 3D viewer (assets/cstr_3d.html?mode=hmi), which is
embedded in an iframe and only animates what the model computes.
"""
from __future__ import annotations

import os
import sys
import threading
import webbrowser
from dataclasses import asdict

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State, ctx, no_update

import cstr_model as m

TICK_MS = 500                       # wall-clock period of the simulation loop
HISTORY_MIN = 60                    # minutes kept in the trends


def resource_path(rel: str) -> str:
    """Path that also works inside a PyInstaller one-file executable."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


app = Dash(
    __name__,
    title="CSTR HMI Training Simulator",
    assets_folder=resource_path("assets"),
    assets_ignore=r"^(three\.min|OrbitControls)\.js$",  # loaded only by the 3D iframe
    update_title=None,
)
server = app.server

# ----------------------------------------------------------------- layout --
COLORS = {"T": "#2c6a8a", "Tj": "#7656a3", "X": "#4d7a22", "warn": "#b97f00", "crit": "#c42b2b",
          "grid": "#c9cfd2", "muted": "#59646b", "gen": "#c42b2b", "rem": "#2c6a8a"}


def slider(id_, label, lo, hi, step, value, unit, marks_step):
    marks = {v: f"{v:g}" for v in [lo + i * marks_step for i in range(int((hi - lo) / marks_step) + 1)]}
    return html.Div(className="ctl", children=[
        html.Label([html.Span(label), html.Output(id=f"{id_}-val", children=f"{value:g} {unit}")], htmlFor=id_),
        dcc.Slider(id=id_, min=lo, max=hi, step=step, value=value, marks=marks, updatemode="drag"),
    ])


def readout(id_, tag, label):
    return html.Div(className="cell", id=f"cell-{id_}", children=[
        html.Small([html.B(tag), f" · {label}"]),
        html.Output(id=id_, children="—"),
    ])


app.layout = html.Div(className="hmi", children=[
    dcc.Store(id="sim", data=None),
    dcc.Store(id="sink"),
    dcc.Interval(id="tick", interval=TICK_MS),

    html.Header(className="bar", children=[
        html.Div(className="brand", children=[
            html.H1("R-101 · CSTR HMI Training Simulator"),
            html.P("A → B exotérmica · reactor encamisado · v1.2.0 con vista 3D"),
        ]),
        html.Div(className="spacer"),
        html.Span(id="status", className="pill", children=[html.I(), html.Span("Operación normal", id="status-txt")]),
        html.Span(id="clock", className="clock", children="t = 0.0 min"),
        dcc.RadioItems(id="speed", className="seg", value=1, inline=True,
                       options=[{"label": "Pausa", "value": 0}, {"label": "0.5 min/s", "value": 0.5},
                                {"label": "1 min/s", "value": 1}, {"label": "4 min/s", "value": 4}]),
    ]),

    html.Main(className="grid", children=[
        html.Section(className="left", children=[
            html.Div(className="view", children=[
                html.Iframe(id="viz3d", src="/assets/cstr_3d.html?mode=hmi", title="Vista 3D del reactor R-101"),
            ]),
            html.Div(className="grp", children=[
                html.H2(f"Tendencias · últimos {HISTORY_MIN} min"),
                dcc.Graph(id="trends", config={"displayModeBar": False}, style={"height": "330px"}),
            ]),
        ]),
        html.Aside(className="panel", children=[
            html.Div(className="grp", children=[
                html.H2("Variables controladas"),
                dcc.Graph(id="gauges", config={"displayModeBar": False}, style={"height": "200px"}),
                html.Div(className="ro", children=[
                    readout("o-T", "TI-101", "T reactor"),
                    readout("o-Tj", "TI-102", "T camisa"),
                    readout("o-X", "AI-101", "Conversión X_A"),
                    readout("o-Tin", "TI-100", "T alimentación"),
                ]),
            ]),
            html.Div(className="grp", children=[
                html.H2("Balance térmico"),
                html.Div(id="balance", className="kv"),
            ]),
            html.Div(className="grp", children=[
                html.H2("Variables manipuladas"),
                slider("F", "FV-101 · Caudal de alimentación F_in", *m.LIMITS["F"], 0.5, m.F0, "L/min", 6),
                slider("Fj", "FV-102 · Caudal de refrigerante F_j", *m.LIMITS["Fj"], 1, m.FJ0, "L/min", 10),
                slider("Tjin", "T entrada refrigerante T_j,in", *m.LIMITS["Tjin"], 0.5, m.TJIN0, "K", 5),
                slider("N", "M-101 · Velocidad del agitador", *m.LIMITS["N"], 5, m.N0, "rpm", 100),
            ]),
            html.Div(className="grp", children=[
                html.H2("Perturbaciones"),
                dcc.Checklist(id="dist", className="dist", value=[], options=[
                    {"label": "Fallo del precalentador (T_in +5 K)", "value": "tin"},
                    {"label": "Ensuciamiento de camisa (UA −20 %)", "value": "foul"},
                ]),
                html.Button("Restablecer estado inicial", id="reset", className="btn"),
                html.P(className="note", children=(
                    "Escenario recomendado: activa el fallo del precalentador y lleva el reactor de vuelta "
                    "por debajo de 320 K maximizando la conversión. Las medidas incluyen ruido gaussiano.")),
            ]),
        ]),
    ]),
])


# -------------------------------------------------------------- callbacks --
def inputs_from(F, Fj, Tjin, N, dist) -> m.Inputs:
    dist = dist or []
    return m.Inputs(F=float(F), Fj=float(Fj), Tjin=float(Tjin), N=float(N),
                    dTin=5.0 if "tin" in dist else 0.0, fouling=0.8 if "foul" in dist else 1.0)


@app.callback(
    Output("sim", "data"),
    Input("tick", "n_intervals"), Input("reset", "n_clicks"),
    State("sim", "data"), State("speed", "value"),
    State("F", "value"), State("Fj", "value"), State("Tjin", "value"), State("N", "value"), State("dist", "value"),
)
def step(_, __, data, speed, F, Fj, Tjin, N, dist):
    """Advance the simulation one tick; the state lives in the browser session."""
    u = inputs_from(F, Fj, Tjin, N, dist)
    if data is None or ctx.triggered_id == "reset":
        s = m.State()
        hist = []
    else:
        s = m.State(**data["state"])
        hist = data["hist"]
        dt = (speed or 0) * TICK_MS / 1000.0
        if dt > 0:
            s = m.integrate(s, u, dt)
    snap = m.snapshot(s, u)
    if not hist or snap["t"] > hist[-1]["t"]:
        hist.append({k: round(snap[k], 4) for k in ("t", "T", "Tj", "Tm", "Xm", "Qgen", "Qrem")})
    hist = [h for h in hist if h["t"] >= snap["t"] - HISTORY_MIN]
    return {"state": asdict(s), "snap": snap, "hist": hist}


@app.callback(
    Output("F", "value"), Output("Fj", "value"), Output("Tjin", "value"), Output("N", "value"), Output("dist", "value"),
    Input("reset", "n_clicks"), prevent_initial_call=True,
)
def reset_controls(_):
    return m.F0, m.FJ0, m.TJIN0, m.N0, []


for sid, unit, fmt in (("F", "L/min", "{:.1f}"), ("Fj", "L/min", "{:.0f}"), ("Tjin", "K", "{:.1f}"), ("N", "rpm", "{:.0f}")):
    app.callback(Output(f"{sid}-val", "children"), Input(sid, "value"))(
        lambda v, unit=unit, fmt=fmt: f"{fmt.format(v)} {unit}" if v is not None else no_update)


LEVEL_TXT = {0: ("ok", "Operación normal"), 1: ("warn", "Alarma alta · T > 320 K"), 2: ("crit", "Crítico · T > 330 K")}


@app.callback(
    Output("o-T", "children"), Output("o-Tj", "children"), Output("o-X", "children"), Output("o-Tin", "children"),
    Output("cell-o-T", "className"), Output("status", "className"), Output("status-txt", "children"),
    Output("clock", "children"), Output("balance", "children"), Output("gauges", "figure"), Output("trends", "figure"),
    Input("sim", "data"),
)
def render(data):
    if not data:
        return (no_update,) * 11
    s, hist = data["snap"], data["hist"]
    lvl, txt = LEVEL_TXT[s["level"]]
    cell_cls = "cell" + ("" if lvl == "ok" else f" {lvl}")
    balance = [
        html.Span(["Q generado ", html.B(f"{s['Qgen'] / 60000:.1f} kW")]),
        html.Span(["Q removido ", html.B(f"{s['Qrem'] / 60000:.1f} kW")]),
        html.Span(["k ", html.B(f"{s['k']:.2e} min⁻¹")]),
        html.Span(["τ ", html.B(f"{s['tau']:.1f} min")]),
        html.Span(["Da ", html.B(f"{s['Da']:.3f}")]),
        html.Span(["UA ", html.B(f"{s['UA'] / 1000:.1f} kJ/(min·K)")]),
    ]
    return (
        f"{s['Tm']:.1f} K", f"{s['Tjm']:.1f} K", f"{s['Xm'] * 100:.1f} %", f"{s['Tin']:.1f} K",
        cell_cls, f"pill {lvl}", txt, f"t = {s['t']:.1f} min", balance,
        gauges_figure(s), trends_figure(hist, s["t"]),
    )


def gauges_figure(s):
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="gauge+number", value=s["Tm"], number={"suffix": " K", "valueformat": ".1f", "font": {"size": 18}},
        title={"text": "T reactor", "font": {"size": 12}}, domain={"x": [0, 0.48], "y": [0, 1]},
        gauge={"axis": {"range": [280, 370], "tickfont": {"size": 9}}, "bar": {"color": COLORS["T"], "thickness": 0.3},
               "steps": [{"range": [320, 330], "color": "rgba(185,127,0,.35)"},
                         {"range": [330, 370], "color": "rgba(196,43,43,.35)"}],
               "threshold": {"line": {"color": COLORS["crit"], "width": 2}, "value": m.T_CRIT}}))
    fig.add_trace(go.Indicator(
        mode="gauge+number", value=s["Xm"] * 100, number={"suffix": " %", "valueformat": ".1f", "font": {"size": 18}},
        title={"text": "Conversión X_A", "font": {"size": 12}}, domain={"x": [0.52, 1], "y": [0, 1]},
        gauge={"axis": {"range": [0, 100], "tickfont": {"size": 9}}, "bar": {"color": COLORS["X"], "thickness": 0.3}}))
    fig.update_layout(margin=dict(l=24, r=24, t=36, b=8), paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="IBM Plex Mono, monospace", color=COLORS["muted"]))
    return fig


def trends_figure(hist, t_now):
    t = [h["t"] for h in hist]
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.45, 0.28, 0.27])
    fig.add_trace(go.Scatter(x=t, y=[h["Tm"] for h in hist], name="T (TI-101)", line=dict(color=COLORS["T"], width=2)), 1, 1)
    fig.add_trace(go.Scatter(x=t, y=[h["Tj"] for h in hist], name="T_j (TI-102)", line=dict(color=COLORS["Tj"], width=2)), 1, 1)
    for y, c in ((m.T_WARN, COLORS["warn"]), (m.T_CRIT, COLORS["crit"])):
        fig.add_hline(y=y, line=dict(color=c, dash="dash", width=1), row=1, col=1)
    fig.add_trace(go.Scatter(x=t, y=[h["Xm"] * 100 for h in hist], name="X_A (AI-101)", line=dict(color=COLORS["X"], width=2)), 2, 1)
    fig.add_trace(go.Scatter(x=t, y=[h["Qgen"] / 60000 for h in hist], name="Q generado", line=dict(color=COLORS["gen"], width=2)), 3, 1)
    fig.add_trace(go.Scatter(x=t, y=[h["Qrem"] / 60000 for h in hist], name="Q removido", line=dict(color=COLORS["rem"], width=2, dash="dot")), 3, 1)
    x0 = max(0.0, t_now - HISTORY_MIN)
    fig.update_xaxes(range=[x0, max(x0 + HISTORY_MIN, t_now)], gridcolor=COLORS["grid"], zeroline=False)
    fig.update_xaxes(title_text="tiempo [min]", row=3, col=1)
    fig.update_yaxes(gridcolor=COLORS["grid"], zeroline=False)
    fig.update_yaxes(title_text="K", row=1, col=1)
    fig.update_yaxes(title_text="X_A %", row=2, col=1)
    fig.update_yaxes(title_text="kW", row=3, col=1)
    fig.update_layout(margin=dict(l=50, r=10, t=10, b=36), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      legend=dict(orientation="h", y=1.08, x=0, font=dict(size=11)), uirevision="trends",
                      font=dict(family="Barlow, sans-serif", size=11, color=COLORS["muted"]))
    return fig


# Send each new state to the 3D iframe (runs in the browser, no round-trip).
app.clientside_callback(
    """
    function(data) {
        const f = document.getElementById('viz3d');
        if (data && f && f.contentWindow) {
            f.contentWindow.postMessage(Object.assign({type: 'cstr-state'}, data.snap), '*');
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("sink", "data"),
    Input("sim", "data"),
)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    if os.environ.get("CSTR_NO_BROWSER") != "1":
        threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    app.run(host="127.0.0.1", port=port, debug=False)
