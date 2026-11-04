# CSTR HMI Training Simulator v1.2.0

This is the updated version of the Continuous Stirred Tank Reactor (CSTR) Human-Machine Interface (HMI) training simulator with measurement noise for enhanced realism, and conversion tracking instead of outlet concentration.

## What's New in v1.1.0
- **Measurement Noise**: Realistic sensor inaccuracies added to conversion (X_A), T (reactor temperature), and Tj (jacket temperature) using Gaussian distributions
- **Conversion Tracking**: Trends now display conversion (X_A) instead of outlet concentration (C_A) for better visibility of reaction efficiency
- **Training Realism**: Operators must account for measurement uncertainty in control decisions
- **Improved Learning**: Better preparation for real-world process control scenarios with focus on safe conversion optimization

## New in v1.2.0: 3D view of the reactor

The HMI now includes an animated 3D model of reactor R-101 (`hmi/assets/cstr_3d.html`, built with three.js).
The simulation runs in Python (`hmi/cstr_model.py`) and every tick the state is sent to the 3D view, so the
animation always shows what the model is computing:

| 3D element | What it shows |
|---|---|
| Liquid and jacket colour | Reactor temperature T and jacket temperature T_j (blue → amber → red) |
| Agitator (Rushton turbine + pitched blade) and vortex | Agitator speed; speed also changes the heat-transfer coefficient UA |
| Blue / orange molecules inside the tank | Reactant A turning into product B with the same Arrhenius kinetics; the share of orange follows X_A |
| Spheres moving through the pipes and jacket | Feed flow F_in and coolant flow F_j, coloured by temperature |
| Control valves FV-101 / FV-102 | Hand-wheel and stem move with valve opening |
| Floating instrument tags | TI-101, TI-102, AI-101, FI-101, FI-102, SI-101 with measurement noise |
| Beacon, inner glow and vent vapour | Amber alarm above 320 K, flashing red and vapour above 330 K (runaway) |

Drag to rotate, scroll or pinch to zoom.

## Run from source

```bash
pip install -r requirements.txt
python hmi/app.py
```

The browser opens at `http://127.0.0.1:8050`. three.js is bundled in `hmi/assets/vendor/`, so the 3D view also works without internet.

The 3D page also runs on its own, with its own simulation and control panel: open `hmi/assets/cstr_3d.html` directly in a browser.

To build the Windows executable:

```bash
pyinstaller --onefile --name CSTR_v1.2.0 --add-data "hmi/assets;assets" hmi/app.py
```

### Code structure

- `hmi/cstr_model.py`: mass and energy balances, RK4 integrator, measurement noise, alarm limits.
- `hmi/app.py`: Dash HMI (controls, gauges, trends, disturbances) and the link to the 3D view (`postMessage`).
- `hmi/assets/cstr_3d.html`: 3D scene. With `?mode=hmi` it only shows the 3D view and takes its state from the HMI.
- `hmi/assets/hmi.css`: HMI styling (ISA-101 style: neutral grey, colour reserved for abnormal states).

### Model parameters used in v1.2.0

C_A,in = 4 mol/L, T_in = 308 K, V = 100 L, V_j = 20 L, ΔH_r = −60 kJ/mol, Ea = 83.14 kJ/mol.
k0 and UA are computed so that the base case (F_in = 10 L/min, F_j = 20 L/min, T_j,in = 290 K, 150 rpm)
is a stable steady state with T = 310 K and X_A = 0.15. With the +5 K preheater failure and no operator action
the reactor runs away to about 339 K; raising F_j to 40 L/min and lowering T_j,in to 285 K brings it back to about 316 K.

## How to Use

1. Download the `CSTR_v1.1.0.exe` file.
2. Double-click the executable to run it.
3. The application will automatically open your web browser to the HMI interface at `http://127.0.0.1:8050`.
4. Use the controls to simulate and train on CSTR operations:
   - Adjust manipulated variables (MV): Refrigerant flow (F_j), feed flow (F_in), coolant inlet temperature (T_j_in).
   - Monitor controlled variables (CV): Reactor temperature (T), conversion (X_A with noise).
   - View real-time trends: Temperature, conversion, heat generation/removal.
   - Apply perturbations (default 5 K increase in inlet temperature) for recommended operation scenarios.

## Features

- Dynamic CSTR simulation with real-time updates
- Measurement noise for realistic training
- Interactive controls for operator training
- Alarm system for critical conditions (T > 320 K warning, T > 330 K critical)
- Trend charts with legends and gauges for monitoring
- Perturbation tools for scenario training (recommended: increase conversion while keeping T < 320 K)

## Requirements

- Windows operating system
- No additional software installation required (all dependencies are included)

## Documentation

See `CSTR_Fundamentals.md` for detailed information about:
- CSTR operation principles
- Mass and energy balances
- Reaction kinetics
- Engineering concepts
- Recommended operation scenarios for safe conversion increase

## Notes

- The executable runs a local web server. Keep the console window open while using the application.
- Measurement noise is applied to displayed values but not to internal calculations for simulation accuracy.
- The initial state is the exact steady state of the base case (T = 310 K, X_A = 0.15, T_in = 308 K).
- For best experience, ensure no other applications are using port 8050.

## License

Important: NO license is required.

