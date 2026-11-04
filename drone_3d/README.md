# Cuadricóptero Q-450 · simulador 3D con la matemática a la vista

Simulador interactivo de un cuadricóptero de 450 mm. Usa dinámica de cuerpo rígido en 6 grados de libertad, control PID en cascada y motores con su propia dinámica. La escena 3D (three.js) muestra el dron, las fuerzas sobre cada motor, la referencia, la estela y el viento. Un panel opcional, **"∑ Ver la matemática"**, muestra las ecuaciones de este documento con sus valores en vivo. Al mover cualquier control, ese panel resalta en rosa la ecuación y el término que cambia.

## Cómo abrirlo

Abre `cuadricoptero.html` en el navegador con doble clic. No necesita servidor ni instalación. three.js y MathJax están incluidos en `vendor/`, así que funciona sin internet. Si falta algún archivo local, se cargan desde un CDN.

| Pestaña | Qué se puede mover |
|---|---|
| **Misión** | Punto fijo (x, y, altura, rumbo) o trayectorias: círculo, ocho, cuadrado, espiral; aterrizar y despegar |
| **Entorno** | Viento (velocidad, dirección, ráfagas), carga útil que el controlador no conoce, eficiencia del motor M3, empujón |
| **Control** | Las 8 ganancias del PID; muestra $\omega_n$ y $\zeta$ del lazo de actitud |

Experimentos sugeridos:

1. **Acción integral:** con 0,8 kg de carga el dron baja al principio y el término $K_i\int e\,dt$ recupera la altura en unos segundos. Con $K_i = 0$ queda un error permanente.
2. **Amortiguamiento:** si $K_{d,\eta}$ baja de 8, entonces $\zeta < 0{,}3$ y el dron oscila. Si sube mucho, responde lento.
3. **Separación de lazos:** con $K_{p,\eta}$ bajo y $K_p$ horizontal alto, el lazo interno deja de ser más rápido que el externo y la posición se vuelve inestable.
4. **Avería de motor:** con M3 al 60 %, el mezclador pide más a M3 hasta saturarlo y los demás motores compensan. Las barras de los motores lo muestran.
5. **Viento con ráfagas:** con 10 m/s y 60 % de turbulencia, el dron se inclina contra el viento y el integral horizontal compensa el arrastre medio.

---

## 1. Sistemas de referencia

- **Mundo (ENU):** $x$ al este, $y$ al norte, $z$ hacia arriba.
- **Cuerpo (FLU):** $x_b$ hacia el frente, $y_b$ hacia la izquierda, $z_b$ hacia arriba del dron.
- **Actitud:** ángulos de Euler $\boldsymbol\eta = (\phi, \theta, \psi)$: alabeo, cabeceo y guiñada, en secuencia Z-Y-X.

La matriz de rotación del cuerpo al mundo es

$$
R = R_z(\psi)\,R_y(\theta)\,R_x(\phi) =
\begin{bmatrix}
c_\psi c_\theta & c_\psi s_\theta s_\phi - s_\psi c_\phi & c_\psi s_\theta c_\phi + s_\psi s_\phi \\
s_\psi c_\theta & s_\psi s_\theta s_\phi + c_\psi c_\phi & s_\psi s_\theta c_\phi - c_\psi s_\phi \\
-s_\theta & c_\theta s_\phi & c_\theta c_\phi
\end{bmatrix}
$$

con $c = \cos$ y $s = \sin$. La tercera columna es la dirección del empuje en el mundo. Con $\theta > 0$ la nariz baja y el dron acelera hacia adelante. Con $\phi > 0$ se inclina hacia la derecha y acelera en $-y_b$.

## 2. Motores y hélices

Cada motor $i$ gira a $\Omega_i$ [rad/s] y produce un empuje y un par de reacción:

$$
T_i = h_i\,k_T\,\Omega_i^2 \qquad Q_i = k_Q\,\Omega_i^2
$$

$h_i$ es la eficiencia del motor (1 si está sano). El motor responde como un sistema de primer orden y tiene saturación:

$$
\tau_m\,\dot\Omega_i = \Omega_i^{\text{cmd}} - \Omega_i, \qquad 0 \le \Omega_i \le \Omega_{\max}
$$

## 3. Mezclador (configuración X)

Los motores están a $\pm d$ en los dos ejes del cuerpo, con $d = \ell/\sqrt{2}$:

| Motor | Posición | Giro (visto desde arriba) |
|---|---|---|
| M1 | frente-derecha $(d, -d)$ | antihorario |
| M2 | atrás-izquierda $(-d, d)$ | antihorario |
| M3 | frente-izquierda $(d, d)$ | horario |
| M4 | atrás-derecha $(-d, -d)$ | horario |

El empuje total y los pares sobre el cuerpo salen de $\boldsymbol\tau = \sum \mathbf r_i \times \mathbf F_i$ más los pares de reacción:

$$
\begin{bmatrix} T \\ \tau_\phi \\ \tau_\theta \\ \tau_\psi \end{bmatrix} =
\begin{bmatrix} 1 & 1 & 1 & 1 \\ -d & d & d & -d \\ -d & d & -d & d \\ -c & -c & c & c \end{bmatrix}
\begin{bmatrix} T_1 \\ T_2 \\ T_3 \\ T_4 \end{bmatrix},
\qquad c = \frac{k_Q}{k_T}
$$

Las filas de la matriz son ortogonales, así que la inversa es directa. El controlador la usa para pasar de $(T, \boldsymbol\tau)$ al empuje de cada motor:

$$
T_i^{\text{cmd}} = \frac{T}{4} + \frac{a_{2i}}{4d^2}\,\tau_\phi + \frac{a_{3i}}{4d^2}\,\tau_\theta + \frac{a_{4i}}{4c^2}\,\tau_\psi,
\qquad \Omega_i^{\text{cmd}} = \sqrt{T_i^{\text{cmd}}/k_T}
$$

donde $a_{ji}$ son los elementos de la matriz. Cada $T_i^{\text{cmd}}$ se limita al rango $[0, T_{\max}]$. Si alguno llega al tope, el estado pasa a "Motores saturados".

## 4. Dinámica traslacional (Newton)

$$
m\,\ddot{\mathbf p} = R\begin{bmatrix}0\\0\\T\end{bmatrix} - m\,g\,\mathbf e_z - k_d\,(\dot{\mathbf p} - \mathbf w)
$$

$\mathbf w$ es la velocidad del viento: un valor medio más ráfagas generadas con un proceso de Ornstein–Uhlenbeck:

$$
\dot{\mathbf w}_g = -\frac{\mathbf w_g}{\tau_g} + \sigma\sqrt{\frac{2}{\tau_g}}\;\boldsymbol\xi(t)
$$

$\boldsymbol\xi(t)$ es ruido blanco y $\tau_g$ = 1,2 s.

## 5. Dinámica rotacional (Euler)

$$
I\,\dot{\boldsymbol\omega} = \boldsymbol\tau - \boldsymbol\omega \times I\boldsymbol\omega - k_r\,\boldsymbol\omega,
\qquad I = \operatorname{diag}(I_x, I_y, I_z)
$$

$\boldsymbol\omega = (p, q, r)$ son las velocidades angulares en el cuerpo, las que mediría un giróscopo. Los ángulos de Euler evolucionan según

$$
\begin{bmatrix}\dot\phi\\ \dot\theta\\ \dot\psi\end{bmatrix} =
\begin{bmatrix} 1 & s_\phi t_\theta & c_\phi t_\theta \\ 0 & c_\phi & -s_\phi \\ 0 & s_\phi / c_\theta & c_\phi / c_\theta \end{bmatrix}
\begin{bmatrix} p\\ q\\ r\end{bmatrix}
$$

con $t = \tan$. La matriz es singular en $\theta = \pm 90°$. El controlador limita la inclinación a 35°, así que nunca se llega ahí.

## 6. Control en cascada

```
p_ref ──► PID posición ──► (T, φ_d, θ_d) ──► PD actitud ──► τ ──► Mezclador ──► Ω_i ──► Dinámica ──┐
  ▲                                                                                               │
  └──────────────────────────────── p, ṗ, η, ω (realimentación) ──────────────────────────────────┘
```

### 6.1 Lazo externo: posición (PID)

$$
\mathbf e = \mathbf p_{\text{ref}} - \mathbf p
$$

$$
\mathbf a_{\text{des}} = K_p\,\mathbf e + K_i\int \mathbf e\,dt - K_d\,(\dot{\mathbf p} - \dot{\mathbf p}_{\text{ref}})
$$

Se usan ganancias distintas para el plano horizontal y para la altura. La derivada actúa sobre la velocidad medida y no sobre el error, así un cambio brusco de referencia no produce un golpe derivativo. El integral tiene límites (anti-windup) y se congela cuando el dron está apoyado en el suelo.

La aceleración deseada se convierte en empuje y ángulos. Primero se rota al marco de rumbo del dron:

$$
a_f = a_x\cos\psi + a_y\sin\psi, \qquad a_l = -a_x\sin\psi + a_y\cos\psi
$$

y después:

$$
T_{\text{cmd}} = \frac{\hat m\,(g + a_z)}{\cos\phi\,\cos\theta},
\qquad \theta_d = \arctan\frac{a_f}{g + a_z},
\qquad \phi_d = -\arctan\frac{a_l}{g + a_z}
$$

$\hat m$ = 1,5 kg es la masa que **cree** el controlador. Si se agrega carga útil, la diferencia $m - \hat m$ la corrige el término integral de altura.

### 6.2 Lazo interno: actitud (PD)

$$
\boldsymbol\tau_{\text{cmd}} = I\left[K_{p,\eta}\,(\boldsymbol\eta_d - \boldsymbol\eta) - K_{d,\eta}\,\boldsymbol\omega\right]
$$

Para ángulos chicos ($\boldsymbol\omega \approx \dot{\boldsymbol\eta}$), cada eje se comporta como un sistema de segundo orden:

$$
\ddot e + K_{d,\eta}\,\dot e + K_{p,\eta}\,e = 0
\quad\Rightarrow\quad
\omega_n = \sqrt{K_{p,\eta}}, \qquad \zeta = \frac{K_{d,\eta}}{2\sqrt{K_{p,\eta}}}
$$

Con los valores por defecto ($K_{p,\eta}$ = 180, $K_{d,\eta}$ = 22) queda $\omega_n \approx$ 13,4 rad/s y $\zeta \approx$ 0,82. El lazo de posición horizontal tiene $\omega_n \approx \sqrt{1{,}8} \approx$ 1,3 rad/s. El lazo interno es unas 10 veces más rápido, que es lo que hace funcionar la cascada.

### 6.3 Rumbo

$$
\tau_\psi = I_z\left[K_{p,\psi}\,\operatorname{wrap}(\psi_d - \psi) - K_{d,\psi}\,r\right], \qquad K_{p,\psi} = 6,\; K_{d,\psi} = 3
$$

$\operatorname{wrap}$ lleva el error al intervalo $(-\pi, \pi]$, así el dron gira por el camino más corto.

## 7. Trayectorias

Cada misión genera $\mathbf p_{\text{ref}}(t)$ y su derivada $\dot{\mathbf p}_{\text{ref}}(t)$, que el PID usa como prealimentación:

| Misión | $\mathbf p_{\text{ref}}(t)$ |
|---|---|
| Círculo | $(3\cos\omega t,\; 3\sin\omega t,\; 3)$, $\omega$ = 0,35 rad/s, con la nariz tangente al recorrido |
| Ocho | $(3{,}5\sin\omega t,\; 1{,}75\sin 2\omega t,\; 3 + 0{,}5\sin\omega t)$, $\omega$ = 0,3 rad/s |
| Espiral | círculo de 2,5 m que sube de 1 a 5 m y vuelve a bajar |
| Cuadrado | lados de 6 m a 1,6 m/s, mirando en la dirección de avance |

Para que el dron no salte al cambiar de misión, la referencia se acerca al punto objetivo a 3 m/s como máximo.

## 8. Parámetros

| Símbolo | Valor | Descripción |
|---|---|---|
| $\hat m$ | 1,5 kg | masa nominal (la que conoce el controlador) |
| $\ell$ | 0,225 m | largo del brazo (centro a motor) |
| $I_x, I_y, I_z$ | 0,0123; 0,0123; 0,0224 kg·m² | momentos de inercia |
| $k_T$ | 1,0·10⁻⁵ N·s² | coeficiente de empuje |
| $k_Q$ | 1,6·10⁻⁷ N·m·s² | coeficiente de par |
| $\tau_m$ | 35 ms | constante de tiempo del motor |
| $\Omega_{\max}$ | 1100 rad/s | velocidad máxima ($T_{\max}$ ≈ 12,1 N por motor; relación empuje/peso ≈ 3,3) |
| $k_d$ | 0,3 N·s/m | arrastre aerodinámico lineal |
| $k_r$ | 0,002 N·m·s | amortiguamiento rotacional |
| $g$ | 9,81 m/s² | gravedad |

En vuelo estacionario cada motor gira a $\Omega_h = \sqrt{\hat m g / 4k_T} \approx$ 606 rad/s (unas 5800 rpm).

## 9. Integración numérica

Euler semi-implícito con paso fijo de 2 ms (500 pasos por segundo de simulación). Primero se actualizan las velocidades y después las posiciones con esas velocidades nuevas. Cuando la simulación se pausa o va en cámara lenta, también se pausa o se frena el giro visible de las hélices.

## Archivos

- `cuadricoptero.html`: el simulador completo (modelo, control, escena 3D y panel de ecuaciones).
- `vendor/three.min.js`, `vendor/OrbitControls.js`: three.js r128 (licencia MIT).
- `vendor/mathjax/`: MathJax 3.2.2 con salida SVG, más las extensiones `html` y `boldsymbol` (licencia Apache 2.0).
