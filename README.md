# CSTR HMI Training Simulator v1.1.0

This is the updated version of the Continuous Stirred Tank Reactor (CSTR) Human-Machine Interface (HMI) training simulator with measurement noise for enhanced realism, and conversion tracking instead of outlet concentration.

## What's New in v1.1.0
- **Measurement Noise**: Realistic sensor inaccuracies added to conversion (X_A), T (reactor temperature), and Tj (jacket temperature) using Gaussian distributions
- **Conversion Tracking**: Trends now display conversion (X_A) instead of outlet concentration (C_A) for better visibility of reaction efficiency
- **Training Realism**: Operators must account for measurement uncertainty in control decisions
- **Improved Learning**: Better preparation for real-world process control scenarios with focus on safe conversion optimization

## How to Use

1. Download the `CSTR_HMI_v1.1.0.exe` file.
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
- Initial state approximates steady state with T_in = 300 K for consistent starting point.
- For best experience, ensure no other applications are using port 8050.

## License

Important: NO license is required.
