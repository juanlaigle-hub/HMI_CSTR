# Robot balancín B-2 · péndulo invertido sobre dos ruedas con control LQR

Simulador interactivo de un robot autoequilibrado de dos ruedas con patas de altura variable. La física es no lineal, el control es óptimo (LQR) y se calcula en el propio navegador. La escena 3D (three.js) muestra el robot, la vertical, el ángulo θ, el centro de masa, el par de cada rueda y la huella en el suelo. El panel **"∑ Ver la matemática"** muestra las ecuaciones de este documento con sus valores en vivo, incluidos los **polos del sistema en el plano complejo**. Al mover un control, se resaltan en rosa la ecuación y el término que cambia.

<p><img src="../assets/robot-1.jpg" width="49%" alt=""> <img src="../assets/robot-2.jpg" width="49%" alt=""></p>

## Cómo abrirlo

Abre `robot.html` en el navegador con doble clic. three.js y MathJax están incluidos en `vendor/`, así que funciona sin internet. El botón **"▶ Demo guiada"** reproduce una secuencia guiada, con subtítulos.

| Pestaña | Qué se puede mover |
|---|---|
| **Mando** | Quedarse quieto, avanzar 1,5 m, ir y volver, ocho, conducción libre (velocidad y giro); empujón normal y fuerte; levantar el robot |
| **Robot** | Altura de las patas $h$, masa del cuerpo $M$, par máximo por rueda; opción de no recalcular el LQR |
| **LQR** | Pesos $q_x, q_v, q_\theta, q_\omega$ y $R$ (escala logarítmica); muestra la ganancia $K$ |

Experimentos sugeridos:

1. **Fase no mínima:** pon cámara lenta ×¼ y "Avanzar 1,5 m". Las ruedas retroceden unos 3 cm antes de avanzar.
2. **Altura y estabilidad:** al subir las patas, el polo inestable se acerca al origen. Un péndulo más alto cae más lento y es más fácil de equilibrar.
3. **LQR sin recalcular:** desactiva "Recalcular el LQR", sube las patas al máximo y da un empujón. La K vieja ya no es la óptima para ese robot.
4. **R grande:** con $R$ = 100 el controlador ahorra par. Los polos se acercan al eje imaginario y la respuesta se vuelve lenta y amplia.
5. **Saturación:** con 1,2 N·m por rueda el "empujón fuerte" lo tira. Con 3 N·m se recupera.

---

## 1. Modelo

Coordenadas generalizadas:
- $x$: avance de las ruedas, con $x = r\,\varphi$ (rueda sin deslizar).
- $\theta$: inclinación del cuerpo respecto de la vertical, positiva hacia adelante.

El cuerpo, de masa $M$, tiene su centro de masa a una distancia $\ell = h + 0{,}05$ m del eje de las ruedas. Cada rueda tiene masa $m_w$, radio $r$ e inercia $I_w = \tfrac12 m_w r^2$.

El motor aplica un par $\tau$ **entre el cuerpo y las ruedas**. Sobre las ruedas genera una fuerza de avance $\tau/r$, y sobre el cuerpo una reacción $-\tau$.

### Ecuaciones de Lagrange

Energía cinética y potencial:

$$
\mathcal T = \tfrac12 a\,\dot x^2 + b\cos\theta\,\dot x\,\dot\theta + \tfrac12 c\,\dot\theta^2,
\qquad
\mathcal V = M g \ell \cos\theta
$$

con

$$
a = M + 2m_w + \frac{2I_w}{r^2}, \qquad b = M\ell, \qquad c = I_b + M\ell^2, \qquad I_b = 0{,}25\,M\ell^2
$$

De $\frac{d}{dt}\frac{\partial\mathcal L}{\partial\dot q} - \frac{\partial\mathcal L}{\partial q} = Q_q$ sale el modelo no lineal:

$$
\begin{bmatrix} a & b\cos\theta \\ b\cos\theta & c \end{bmatrix}
\begin{bmatrix}\ddot x\\ \ddot\theta\end{bmatrix} =
\begin{bmatrix} \tau/r - b_x\dot x + b\sin\theta\,\dot\theta^2 \\ M g \ell\sin\theta - \tau \end{bmatrix}
$$

El simulador resuelve este sistema de 2×2 en cada paso (sin linealizar). $b_x$ es la fricción de rodadura.

## 2. Linealización y espacio de estados

Con $\sin\theta \approx \theta$, $\cos\theta \approx 1$ y $\dot\theta^2 \approx 0$, y llamando $\Delta = ac - b^2$:

$$
\mathbf s = \begin{bmatrix} x & \dot x & \theta & \dot\theta \end{bmatrix}^{\mathsf T},
\qquad \dot{\mathbf s} = A\,\mathbf s + B\,\tau
$$

$$
A = \begin{bmatrix}
0 & 1 & 0 & 0 \\
0 & -\dfrac{c\,b_x}{\Delta} & -\dfrac{b\,Mg\ell}{\Delta} & 0 \\
0 & 0 & 0 & 1 \\
0 & \dfrac{b\,b_x}{\Delta} & \dfrac{a\,Mg\ell}{\Delta} & 0
\end{bmatrix},
\qquad
B = \begin{bmatrix} 0 \\ \dfrac{c/r + b}{\Delta} \\ 0 \\ -\dfrac{a + b/r}{\Delta} \end{bmatrix}
$$

Sin control, los polos son las raíces de $\det(sI - A) = 0$. Con los valores por defecto ($M$ = 3 kg, $h$ = 0,25 m) dan aproximadamente $\{-8{,}03;\; -0{,}02;\; 0;\; +8{,}00\}$. El polo en $+8$ rad/s es el del péndulo invertido: sin control el robot se cae en menos de un segundo.

## 3. Control óptimo LQR

Se busca el par que minimiza

$$
J = \int_0^\infty \left( \mathbf s^{\mathsf T} Q\, \mathbf s + R\,\tau^2 \right) dt,
\qquad Q = \operatorname{diag}(q_x, q_v, q_\theta, q_\omega)
$$

La solución es una realimentación lineal del estado:

$$
\tau = -K\,(\mathbf s - \mathbf s_{\text{ref}}), \qquad K = R^{-1} B^{\mathsf T} P
$$

donde $P$ es la solución simétrica definida positiva de la **ecuación algebraica de Riccati**:

$$
A^{\mathsf T}P + PA - PB\,R^{-1}B^{\mathsf T}P + Q = 0
$$

### Cómo se resuelve en el navegador

1. Se discretiza con un paso pequeño, $\Delta t$ = 2 ms: $A_d \approx I + A\Delta t + \tfrac12 A^2\Delta t^2$, $B_d \approx B\Delta t + \tfrac12 AB\,\Delta t^2$, $Q_d = Q\,\Delta t$, $R_d = R\,\Delta t$. Así la Riccati discreta tiende a la continua.
2. La Riccati discreta se resuelve con el **algoritmo de doblamiento (SDA)**, que converge cuadráticamente en unas 20–30 iteraciones:

$$
\begin{aligned}
W_k &= (I + G_k H_k)^{-1} \\
A_{k+1} &= A_k W_k A_k \\
G_{k+1} &= G_k + A_k W_k G_k A_k^{\mathsf T} \\
H_{k+1} &= H_k + A_k^{\mathsf T} H_k W_k A_k
\end{aligned}
\qquad A_0 = A_d,\; G_0 = B_d R_d^{-1} B_d^{\mathsf T},\; H_0 = Q_d
$$

3. Con $P = H_\infty$: $K = (R_d + B_d^{\mathsf T} P B_d)^{-1} B_d^{\mathsf T} P A_d$.

La iteración simple de Riccati tarda miles de pasos en converger para el modo lento de la posición. Con SDA, en cambio, el cálculo toma alrededor de 1 ms y se rehace cada vez que cambian $Q$, $R$, la altura o la masa.

Con los pesos por defecto ($Q$ = diag(2, 1, 40, 1), $R$ = 2):

$$
K \approx \begin{bmatrix} -0{,}97 & -1{,}59 & -9{,}92 & -1{,}64 \end{bmatrix}
$$

Los polos con control, $\det(sI - (A - BK)) = 0$, quedan en aproximadamente $\{-21{,}1;\; -6{,}4;\; -0{,}97 \pm 0{,}65i\}$, todos en el semiplano izquierdo.

**Detalles prácticos:**
- El error de posición $x - x_{\text{ref}}$ se limita a ±1 m. Así, una referencia lejana no pide una inclinación exagerada.
- En las misiones con velocidad (ocho y conducción libre), $\mathbf s_{\text{ref}} = (x_{\text{ref}}, v_{\text{ref}}, 0, 0)$, con $x_{\text{ref}}$ integrando $v_{\text{ref}}$.

## 4. Fase no mínima

Transformando por Laplace las ecuaciones linealizadas (sin fricción), la transferencia del par al avance es

$$
\frac{X(s)}{T(s)} = \frac{(c/r + b)\,s^2 - Mg\ell/r}{s^2\left[(ac - b^2)\,s^2 - a\,Mg\ell\right]}
$$

Tiene ceros en

$$
z = \pm\sqrt{\frac{M g \ell}{c + b\,r}}
$$

El cero positivo, de unos 4,6 s⁻¹ con los valores por defecto, hace que el sistema sea **de fase no mínima**. Para avanzar, el robot primero tiene que inclinarse hacia adelante, y para eso mueve las ruedas un poco **hacia atrás**. En la simulación, al pedir un escalón de 1,5 m las ruedas retroceden unos 3 cm antes de avanzar.

## 5. Giro y reparto entre ruedas

La diferencia de par entre las ruedas genera una diferencia de fuerzas en el suelo, separadas por la trocha $d$:

$$
J_\psi\,\ddot\psi = \frac{d}{2r}\,(\tau_R - \tau_L) - b_\psi\,\dot\psi
$$

$$
J_\psi = \frac{M\,(0{,}18^2 + 0{,}12^2)}{12} + 2 m_w \left(\frac d2\right)^2 + 2\cdot\tfrac14 m_w r^2
$$

El rumbo se controla con un PD:

$$
\tau_\psi = K_{p\psi}\,(\psi_{\text{ref}} - \psi) + K_{d\psi}\,(\dot\psi_{\text{ref}} - \dot\psi), \qquad K_{p\psi} = 1{,}2,\; K_{d\psi} = 0{,}25
$$

El par de cada rueda combina equilibrio y giro, y se satura al límite del motor:

$$
\tau_{R,L} = \operatorname{sat}_{\tau_{\max}}\!\left(\frac{\tau}{2} \pm \frac{\tau_\psi}{2}\right)
$$

Cuando un motor satura, el par total ya no es el que pide el LQR. Si el empujón es grande, el robot no alcanza a ponerse debajo del centro de masa y se cae. Esto se detecta cuando $|\theta| > 66°$; entonces el robot queda apoyado a unos 81°.

La posición en el plano se obtiene integrando:

$$
\dot X = \dot x\cos\psi, \qquad \dot Y = \dot x\sin\psi
$$

## 6. Parámetros

| Símbolo | Valor | Descripción |
|---|---|---|
| $r$ | 0,085 m | radio de rueda |
| $m_w$ | 0,35 kg | masa de cada rueda |
| $d$ | 0,34 m | distancia entre ruedas |
| $M$ | 3,0 kg (1,5–6) | masa del cuerpo |
| $h$ | 0,25 m (0,12–0,38) | altura de las patas (cadera–eje); $\ell = h + 0{,}05$ m |
| $I_b$ | $0{,}25\,M\ell^2$ | inercia del cuerpo respecto de su centro de masa |
| $b_x$ | 0,08 N·s/m | fricción de rodadura |
| $b_\psi$ | 0,05 N·m·s | amortiguamiento de giro |
| $\tau_{\max}$ | 1,2 N·m por rueda (0,4–3) | par máximo del motor |
| $g$ | 9,81 m/s² | gravedad |

## 7. Integración numérica

Euler semi-implícito con paso fijo de 2 ms: primero se actualizan las velocidades y después las posiciones con esas velocidades nuevas. Los polos del panel se calculan con el polinomio característico (método de Faddeev–LeVerrier) y sus raíces con el método de Durand–Kerner.

## Archivos

- `robot.html`: el simulador completo (modelo, LQR, escena 3D, panel de ecuaciones y demo guiada).
- `vendor/`: three.js r128 (MIT) y MathJax 3.2.2 (Apache 2.0).
