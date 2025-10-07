# CSTR HMI Training Simulator v1.1.0

This is the updated version of the Continuous Stirred Tank Reactor (CSTR) Human-Machine Interface (HMI) training simulator with measurement noise for enhanced realism.

## What's New in v1.1.0
- **Measurement Noise**: Realistic sensor inaccuracies added to CA (concentration), T (reactor temperature), and Tj (jacket temperature) using Gaussian distributions
- **Training Realism**: Operators must account for measurement uncertainty in control decisions
- **Improved Learning**: Better preparation for real-world process control scenarios

## How to Use

1. Download the `CSTR_HMI_v1.1.0_Training.exe` file.
2. Double-click the executable to run it.
3. The application will automatically open your web browser to the HMI interface at `http://127.0.0.1:8050`.
4. Use the controls to simulate and train on CSTR operations:
   - Adjust manipulated variables (MV): Refrigerant flow, feed flow, coolant temperature.
   - Monitor controlled variables (CV): Reactor temperature, product concentration (with noise).
   - View real-time trends and heat balances.
   - Apply perturbations for training scenarios.

## Features

- Dynamic CSTR simulation with real-time updates
- Measurement noise for realistic training
- Interactive controls for operator training
- Alarm system for critical conditions
- Trend charts and gauges for monitoring
- Perturbation tools for scenario training

## Requirements

- Windows operating system
- No additional software installation required (all dependencies are included)

## Documentation

See `CSTR_Fundamentals.md` for detailed information about:
- CSTR operation principles
- Mass and energy balances
- Reaction kinetics
- Engineering concepts
- Training perturbation scenarios

## Notes

- The executable runs a local web server. Keep the console window open while using the application.
- Measurement noise is applied to displayed values but not to internal calculations for simulation accuracy.
- For best experience, ensure no other applications are using port 8050.

## License

No License is requiered
