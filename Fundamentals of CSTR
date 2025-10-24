# CSTR (Continuous Stirred Tank Reactor) Fundamentals

## General Description
A Continuous Stirred Tank Reactor (CSTR) is a type of chemical reactor where reactants enter continuously and products exit continuously, maintaining constant volume. The stirrer ensures perfect mixing, resulting in uniform concentrations and temperatures throughout the reactor.

## Chemical Reaction
The simulated reaction is first-order irreversible: **A → B**

- **Type**: Exothermic reaction (releases heat)
- **Kinetics**: r_A = k * C_A, where k follows Arrhenius law: k = k0 * exp(-Ea/RT)
- **Reaction enthalpy**: ΔH_r = -60,000 J/mol (negative = exothermic)

## Fundamental Balances

### Mass Balance
For component A:
```
dC_A/dt = (F/V) * (C_A_in - C_A) - r_A
```
Where:
- F: Inlet volumetric flow [L/min]
- V: Reactor volume [L]
- C_A_in: Inlet concentration of A [mol/L]
- C_A: Concentration in the reactor [mol/L]
- r_A: Reaction rate [mol/(L·min)]

### Energy Balance
For the reactor:
```
ρ·Cp·V · dT/dt = F·ρ·Cp·(T_in - T) + r_A·(-ΔH_r)·V - U·A·(T - T_j)
```

For the cooling jacket:
```
ρ_j·Cp_j·V_j · dT_j/dt = F_j·ρ_j·Cp_j·(T_j_in - T_j) + U·A·(T - T_j)
```

Where:
- T: Reactor temperature [K]
- T_j: Jacket temperature [K]
- U: Overall heat transfer coefficient [J/(min·L·K)]
- A: Heat transfer area [m²]

## Engineering Concepts

### Reynolds Number (Re)
Indicates the flow regime:
- Re < 10: Laminar
- 10 < Re < 10,000: Transition
- Re > 10,000: Turbulent

### Damköhler Number (Da)
Relationship between reaction time and residence time:
```
Da = τ · k
```
Where τ = V/F is the residence time.

### Conversion and Yield
- Conversion of A: X_A = (C_A_in - C_A_out)/C_A_in
- Yield: Depends on selectivity and conversion

## Trainer Disturbance Case

### Scenario: Sudden Increase in Inlet Temperature (T_in)
**Description**: The feed temperature suddenly increases by 10 K due to a preheater failure.

**Expected behavior**:
1. The reactor temperature (T) begins to increase
2. The reaction rate (k) increases exponentially
3. The outlet concentration (C_A) decreases
4. The generated heat increases, potentially causing thermal runaway

**Operator actions**:
1. **Monitoring**: Observe the increase in T and decrease in C_A
2. **Immediate response**: Increase coolant flow (F_j) to maximum
3. **Fine adjustment**: Reduce coolant temperature (T_j_in) if necessary
4. **Preventive control**: If T > 320 K, activate alarms and consider reducing inlet flow (F_in)
5. **Stabilization**: Keep T below 330 K to avoid critical conditions

**Learning objectives**:
- Recognize thermal disturbances
- Apply cascade control (temperature → coolant flow)
- Understand the balance between production and safety
- Practice response to thermal runaway scenarios

## System Parameters
- Reactor volume: 100 L
- Density: 1000 g/L
- Heat capacity: 4.187 J/(g·K)
- U·A coefficient: 800 J/(min·K)
- Activation energy: 83,140 J/mol
- Pre-exponential factor: 7.2 × 10^10 min⁻¹

This simulation allows training operators in chemical reactor control under realistic conditions with measurement noise.

---

## Operational Interest Scenarios

### Scenario 1: Operating Point Optimization for Maximum Conversion

**Objective**: Find the optimal operating conditions that maximize the conversion of A (X_A) while maintaining the reactor temperature in a safe range.

**Scenario Description**:
The operator must adjust the manipulated variables (F_in, F_j, T_j_in) to achieve the maximum possible conversion of reactant A while maintaining the reactor temperature between 310-320 K. This is a typical optimization scenario where the balance between productivity and operational safety is sought.

**Associated Phenomenology**:

1. **Cinética de Reacción y Temperatura**: La velocidad de reacción sigue la ley de Arrhenius (k = k0 × exp(-Ea/RT)), lo que significa que la velocidad aumenta exponencialmente con la temperatura. Un aumento de temperatura de 10 K puede duplicar o triplicar la velocidad de reacción.

2. **Balance Térmico**: El reactor opera en un balance delicado entre:
   - **Calor generado**: Q_gen = r_A × (-ΔH_r) × V (la reacción exotérmica genera calor)
   - **Calor removido**: Q_rem = U × A × (T - T_j) (la camisa de refrigeración remueve calor)
   - **Calor de alimentación**: F × ρ × Cp × (T_in - T)

3. **Tiempo de Residencia**: τ = V/F_in determina cuánto tiempo los reactivos permanecen en el reactor. Un tiempo de residencia mayor permite mayor conversión, pero reduce la capacidad de producción.

4. **Número de Damköhler (Da)**: Da = τ × k relaciona el tiempo de reacción con el tiempo de residencia:
   - Da << 1: Conversión baja (flujo muy rápido o reacción lenta)
   - Da >> 1: Conversión alta (flujo lento o reacción rápida)
   - Da ≈ 1: Zona óptima de operación

**Recommended Control Strategy**:

1. **Phase 1 - Initial Exploration** (t = 0-10 min):
   - Start from baseline conditions: F_in = 10 L/min, F_j = 20 L/min, T_j_in = 290 K
   - Observe initial steady state: T ≈ 310 K, X_A ≈ 0.15

2. **Phase 2 - Feed Flow Reduction** (t = 10-20 min):
   - Gradually reduce F_in from 10 to 7 L/min
   - Increase residence time (τ = V/F_in increases from 10 to 14.3 min)
   - Observe: T increases due to higher conversion → more heat generated
   - Monitor: X_A increases significantly

3. **Phase 3 - Fine Tuning of Cooling System** (t = 20-30 min):
   - If T > 320 K: Increase F_j to 25-30 L/min or reduce T_j_in to 285 K
   - If T < 315 K: Reduce F_j to 15 L/min to allow T to rise
   - Objective: Maintain T ≈ 318 K (high conversion zone without risk)

4. **Phase 4 - Stabilization** (t = 30-40 min):
   - Finely adjust F_j to maintain stable T
   - Verify that X_A remains at the maximum achievable (typically 0.25-0.30)
   - Confirm that Q_generated ≈ Q_removed (stable thermal balance)

**Success Indicators**:
- X_A > 0.25 (conversion > 25%)
- 315 K < T < 320 K (safe and productive temperature range)
- Stable T for at least 10 minutes
- No temperature alarms

**Key Learnings**:
- Understand the trade-off between residence time and production capacity
- Recognize the strong exponential dependence of reaction rate on temperature
- Master thermal control through cooling system manipulation
- Identify optimal operating point through trend observation

---

### Scenario 2: Handling Multiple Simultaneous Disturbances (Advanced Scenario)

**Objective**: Maintain the reactor under safe operating conditions in the face of simultaneous disturbances in the feed and cooling system.

**Scenario Description**:
The operator faces a complex situation where two simultaneous disturbances occur:
1. **Disturbance in T_in**: Feed temperature increases from 300 K to 310 K (upstream heat exchanger failure)
2. **Cooling system degradation**: The U×A coefficient decreases by 20% (simulating jacket fouling)

This scenario represents a real operational emergency situation requiring fast and coordinated response.

**Associated Phenomenology**:

1. **Cascade Effect of Thermal Disturbances**:
   - The increase in T_in directly raises the reactor temperature
   - Higher temperature increases k exponentially (Arrhenius effect)
   - Higher k → higher r_A → more Q_generated
   - Additional Q_generated further increases T
   - **Positive feedback**: Can lead to "thermal runaway" if not controlled

2. **Cooling System Degradation**:
   - Reduction of U×A means: Q_removed = U×A×(T - T_j) decreases
   - Lower heat removal capacity worsens the thermal problem
   - The system has less safety margin to absorb disturbances

3. **System Response Dynamics**:
   - **Fast response** (seconds to minutes): Flow term F/V×(T_in - T) changes immediately
   - **Intermediate response** (minutes): Kinetics adjust to new temperature
   - **Slow response** (10-20 minutes): System seeks new steady state

4. **Multiple Possible Steady States**:
   - In exothermic reactors, multiple steady states can exist:
     - **Low stable state**: Low T, low conversion (initial desired state)
     - **High stable state**: High T, high conversion (may be unstable)
     - **Extinction state**: Reaction shuts down (very low T)
   - Disturbances can force an unwanted transition between states

5. **Physical Actuator Limitations**:
   - F_j has a maximum limit (50 L/min)
   - T_j_in has a minimum limit (≈ 280 K, cooling tower water temperature)
   - If disturbances are very severe, the system may not have sufficient control capacity

**Recommended Control Strategy**:

**Time t=0: Disturbance Detection**
- **Symptom**: T begins to increase rapidly (> 1 K/min)
- **Confirmation**: Verify that T_in increased in the process diagram
- **Early alarm**: Activate intensive monitoring

**Phase 1 - Immediate Response** (t = 0-2 min):
- **Action 1**: Increase F_j to maximum available (50 L/min)
  - Rationale: Maximize Q_removed = U×A×(T - T_j) by increasing coolant flow
- **Action 2**: Reduce T_j_in to minimum available (280 K)
  - Rationale: Reduce T_j to increase the gradient (T - T_j)
- **Objective**: Buy time to assess the situation

**Phase 2 - Assessment and Adjustment** (t = 2-5 min):
- **Monitor**: If T stabilizes or begins to decrease → partial success
- **If T continues rising**: Consider reducing F_in to decrease sensible heat input
- **Mental calculation**: Estimate if Q_removed is sufficient by observing trends of Q_generated and Q_removed

**Phase 3 - Critical Decision** (t = 5-10 min):

**Option A - If T < 325 K**: Maintain control with maximum cooling
- Continue with F_j = 50 L/min and T_j_in = 280 K
- Wait for system to reach new steady state
- Accept temporarily reduced conversion if necessary

**Option B - If 325 K < T < 330 K**: Reduce reactor load
- Reduce F_in from 10 to 6-7 L/min (decreases heat input and reaction load)
- Warning: This also reduces residence time initially
- Net effect: Lower incoming heat flow allows cooling to be more effective

**Option C - If T > 330 K**: Emergency - Consider emergency shutdown
- **Critical action**: Drastically reduce F_in to 5 L/min (minimum) to "cool" the reactor
- Consider adding "quench" (in real systems: cold water injection, bypass opening)
- In this simulation: Observe if T begins to decrease with minimum F_in and maximum cooling

**Phase 4 - Stabilization and Recovery** (t = 10-30 min):
- Once T < 320 K and dT/dt ≈ 0: System is under control
- Gradually restore F_in to normal value
- Adjust F_j and T_j_in to maintain T in target range (310-320 K)
- Document the event and actions taken

**Phenomenological Analysis During the Scenario**:

1. **Observe Q_generated vs Q_removed**:
   - Beginning: Q_generated > Q_removed → T increases
   - After intervention: Q_removed increases
   - Stabilization: Q_generated ≈ Q_removed

2. **Behavior of C_A (or X_A)**:
   - High T → high k → high r_A → low C_A (high X_A)
   - If F_in is reduced: τ increases → X_A increases further
   - Observe if X_A reaches values > 0.30 (indicative of extreme conditions)

3. **Jacket Response (T_j)**:
   - With maximum F_j: T_j responds quickly to T_j_in
   - Observe gradient (T - T_j): must increase to compensate for U×A degradation
   - If (T - T_j) > 20 K: System is working at its limit

**Success Indicators**:
- Maintain T < 330 K at all times (avoid critical state)
- Recover stable control with T < 320 K in less than 20 minutes
- Avoid reactor emergency shutdown
- Understand the interaction between multiple disturbances

**Failure Indicators**:
- T > 330 K at any time (safety failure)
- T oscillations > 5 K (unstable control)
- Inability to stabilize the system within 30 minutes

**Key Learnings**:
- Recognize thermal emergency situations and act quickly
- Understand positive feedback in exothermic reactors
- Master coordinated use of multiple manipulated variables (F_j, T_j_in, F_in)
- Develop decision criteria under pressure
- Understand physical limits of actuators and consequences of operating near those limits
- Appreciate the importance of thermal balance in process safety

**Connection with Process Safety**:
This scenario illustrates fundamental process safety concepts:
- **Layers of protection**: Basic control (cooling) → advanced control (load reduction) → emergency shutdown
- **Thermal runaway**: Critical phenomenon in exothermic reactors that must be avoided
- **Response time**: Speed of operator action is critical
- **"What-if" analysis**: What happens if cooling fails AND T_in increases simultaneously?

---

## Training Recommendations

### Difficulty Progression:
1. **Basic Level**: Scenario 1 (optimization) - System familiarization
2. **Intermediate Level**: Single T_in disturbance (original case in document)
3. **Advanced Level**: Scenario 2 (multiple disturbances) - Emergency handling

### Operator Evaluation Metrics:
- **Response time**: How long does it take to detect and respond to the disturbance?
- **Effectiveness**: Does it keep variables within safe limits?
- **Efficiency**: Does it minimize production losses?
- **Understanding**: Can they explain the observed phenomenology?

### Complementary Exercises:
1. Manually calculate the Damköhler number under different conditions
2. Estimate optimal residence time for different conversion objectives
3. Plot curves of Q_generated vs T and Q_removed vs T to identify stable operating points
4. Simulate instrumentation failures (what to do if the T sensor is faulty?)
