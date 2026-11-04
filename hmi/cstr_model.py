"""Dynamic model of the jacketed CSTR (A -> B, first order, exothermic).

The same equations drive the Dash HMI and the 3D viewer
(``assets/cstr_3d.html``), so both always show the same process state.

Mass balance     dC_A/dt = F/V (C_A,in - C_A) - k C_A
Reactor energy   rho Cp V dT/dt   = F rho Cp (T_in - T) + (-dH) k C_A V - UA (T - T_j)
Jacket energy    rho Cp V_j dT_j/dt = F_j rho Cp (T_j,in - T_j) + UA (T - T_j)

with k = k0 exp(-Ea / (R T)). Units: L, min, mol, J, K.

k0 and UA are not free inputs: they are computed so that the base case
(F = 10 L/min, F_j = 20 L/min, T_j,in = 290 K, T_in = 308 K, 150 rpm)
is an exact, stable steady state with T = 310 K and X_A = 0.15.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field, asdict

# --- Physical parameters -------------------------------------------------
V = 100.0          # reactor volume [L]
VJ = 20.0          # jacket volume [L]
RHO = 1000.0       # density [g/L]
CP = 4.187         # heat capacity [J/(g K)]
DH = -60000.0      # reaction enthalpy [J/mol]
EA = 83140.0       # activation energy [J/mol]
RGAS = 8.314       # gas constant [J/(mol K)]
CA_IN = 4.0        # inlet concentration of A [mol/L]

# --- Base operating point ------------------------------------------------
F0, FJ0, TJIN0, TIN0, N0 = 10.0, 20.0, 290.0, 308.0, 150.0
T0, X0 = 310.0, 0.15

_k_base = (F0 / V) * X0 / (1 - X0)
K0 = _k_base / math.exp(-EA / (RGAS * T0))                     # [1/min]
CA0 = CA_IN * (1 - X0)
_q_gen0 = _k_base * CA0 * (-DH) * V
_q_rem0 = _q_gen0 + F0 * RHO * CP * (TIN0 - T0)
TJ0 = TJIN0 + _q_rem0 / (FJ0 * RHO * CP)
UA0 = _q_rem0 / (T0 - TJ0)                                      # [J/(min K)]

# --- Alarm limits and actuator ranges -------------------------------------
T_WARN, T_CRIT = 320.0, 330.0
LIMITS = {"F": (2.0, 20.0), "Fj": (0.0, 50.0), "Tjin": (280.0, 300.0), "N": (0.0, 300.0)}

# --- Measurement noise (standard deviations) ------------------------------
NOISE = {"T": 0.3, "Tj": 0.3, "X": 0.004}


def rate_constant(T: float) -> float:
    return K0 * math.exp(-EA / (RGAS * T))


def agitation_factor(N: float) -> float:
    """Film coefficient grows with agitator speed (h ~ N^(2/3)); 1.0 at 150 rpm."""
    return (max(N, 30.0) / N0) ** (2.0 / 3.0)


@dataclass
class Inputs:
    F: float = F0          # feed flow [L/min]
    Fj: float = FJ0        # coolant flow [L/min]
    Tjin: float = TJIN0    # coolant inlet temperature [K]
    N: float = N0          # agitator speed [rpm]
    dTin: float = 0.0      # feed temperature disturbance [K]
    fouling: float = 1.0   # UA multiplier (0.8 = 20 % fouling)

    @property
    def Tin(self) -> float:
        return TIN0 + self.dTin

    @property
    def UA(self) -> float:
        return UA0 * self.fouling * agitation_factor(self.N)


@dataclass
class State:
    CA: float = CA0
    T: float = T0
    Tj: float = TJ0
    t: float = 0.0


def derivatives(s: State, u: Inputs) -> dict:
    k = rate_constant(s.T)
    r = k * s.CA
    q_gen = r * (-DH) * V
    q_rem = u.UA * (s.T - s.Tj)
    return {
        "CA": u.F / V * (CA_IN - s.CA) - r,
        "T": (u.F * (u.Tin - s.T) + (q_gen - q_rem) / (RHO * CP)) / V,
        "Tj": (u.Fj * (u.Tjin - s.Tj) + q_rem / (RHO * CP)) / VJ,
        "k": k,
        "Qgen": q_gen,
        "Qrem": q_rem,
    }


def integrate(s: State, u: Inputs, dt_min: float, h: float = 0.01) -> State:
    """Advance the state by dt_min minutes with classic RK4 sub-steps."""
    n = max(1, math.ceil(dt_min / h))
    h = dt_min / n
    ca, T, tj = s.CA, s.T, s.Tj
    for _ in range(n):
        def f(c, x, y):
            d = derivatives(State(c, x, y), u)
            return d["CA"], d["T"], d["Tj"]
        k1 = f(ca, T, tj)
        k2 = f(ca + h / 2 * k1[0], T + h / 2 * k1[1], tj + h / 2 * k1[2])
        k3 = f(ca + h / 2 * k2[0], T + h / 2 * k2[1], tj + h / 2 * k2[2])
        k4 = f(ca + h * k3[0], T + h * k3[1], tj + h * k3[2])
        ca += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        T += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        tj += h / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        ca = max(ca, 0.0)
    return State(ca, T, tj, s.t + dt_min)


def conversion(s: State) -> float:
    return 1.0 - s.CA / CA_IN


def alarm_level(T: float) -> int:
    """0 = normal, 1 = high (T > 320 K), 2 = critical (T > 330 K)."""
    return 2 if T > T_CRIT else 1 if T > T_WARN else 0


def measure(s: State, rng: random.Random | None = None) -> dict:
    """Noisy sensor readings, as seen by the operator."""
    g = (rng or random).gauss
    return {
        "T": s.T + g(0, NOISE["T"]),
        "Tj": s.Tj + g(0, NOISE["Tj"]),
        "X": min(1.0, max(0.0, conversion(s) + g(0, NOISE["X"]))),
    }


def snapshot(s: State, u: Inputs) -> dict:
    """Everything the HMI and the 3D viewer need for one instant."""
    d = derivatives(s, u)
    m = measure(s)
    return {
        **asdict(s),
        "X": conversion(s),
        "k": d["k"],
        "Qgen": d["Qgen"],
        "Qrem": d["Qrem"],
        "UA": u.UA,
        "tau": V / u.F,
        "Da": V / u.F * d["k"],
        "Tm": m["T"],
        "Tjm": m["Tj"],
        "Xm": m["X"],
        "level": alarm_level(s.T),
        **{key: getattr(u, key) for key in ("F", "Fj", "Tjin", "N", "dTin", "fouling")},
        "Tin": u.Tin,
    }
