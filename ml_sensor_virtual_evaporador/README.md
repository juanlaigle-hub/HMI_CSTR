# Sensor virtual de °Brix, HMF y color con machine learning · evaporador de jugo de manzana

Un **sensor virtual** (*soft sensor*) para la juguera, que estima cada minuto tres variables con los instrumentos que
la planta ya tiene (temperaturas, presiones y caudales):
- el **°Brix del concentrado**, como respaldo del refractómetro en línea y para seguir controlando si este falla;
- el **HMF** y el **color**, que hoy se miden en laboratorio cada pocas horas.

Este ejercicio es independiente: no modifica el simulador de `evaporador_jugo/`. Usa una **copia de su núcleo
físico** para generar los datos (`datos/simulador_evaporador.js`).

**Video de la demo:** [`demo_sensor_virtual.mp4`](demo_sensor_virtual.mp4).
**Notebook ejecutado:** [`notebook/entrenamiento_sensor_virtual.ipynb`](notebook/entrenamiento_sensor_virtual.ipynb).

## Resultados

### °Brix del concentrado
Errores medidos contra el valor real, que solo se conoce porque los datos son simulados.

| Modelo | MAE en campañas de prueba | MAE en el ensayo B (escalones, no visto) |
|---|---|---|
| Ingenuo (°Brix = consigna 70) | 1,36 | 14,30 |
| Físico (EPE del 5º efecto + balance de masa) | 1,02 | 1,73 |
| Ridge (sensores + rasgos físicos) | 0,65 | 2,08 |
| **Gradient boosting con restricciones de monotonía** (desplegado) | **0,54** | **1,05** |

### HMF y color
Con solo **120 análisis de laboratorio** para entrenar:

| Variable | Modelo | MAE | R² |
|---|---|---|---|
| HMF | Gradient boosting sobre sensores crudos | 0,82 mg/kg | 0,57 |
| HMF | Ridge sobre sensores crudos | 0,72 mg/kg | 0,55 |
| HMF | Arrhenius por efecto (6 coeficientes libres) | 0,44 mg/kg | 0,87 |
| HMF | **Caja gris (2 constantes cinéticas)** (desplegado) | **0,50 mg/kg** | **0,89** |
| Color | Gradient boosting sobre sensores crudos | 0,0071 | 0,47 |
| Color | **Caja gris** (desplegado) | **0,0029** | **0,94** |

**Curva de aprendizaje:** con solo 20 análisis, la caja gris ya tiene un MAE de 0,52 mg/kg, mientras que el gradient
boosting necesita más de 120 y aun así no la alcanza (0,82 mg/kg). En planta, eso significa semanas menos de
recolección de datos.

![Curva de aprendizaje](figuras/04_curva_aprendizaje.png)

## Fenomenología: cómo se verificó que todo respete la física

1. **Datos.** Antes de modelar se verifican tres correlaciones:
   - el HMF sube con la temperatura del vapor (Arrhenius, r = +0,72);
   - en los ensayos, más alimentación da menos °Brix (balance de masa, r = −0,65);
   - la elevación del punto de ebullición del 5º efecto crece con el °Brix (r = +0,76).
2. **Rasgos con física.**
   - **°Brix por EPE:** se invierte $\text{EPE} = 2{,}5\,B/(100-B)$ usando $T_5 - T_{\text{sat}}(p_5)$.
   - **°Brix por balance de masa:** $F B_f/(F - E\dot m_s)$.
   - **HMF por Arrhenius:** la velocidad de reacción por el tiempo de residencia de los sólidos en cada efecto,
     con las masas retenidas de diseño.
3. **Restricciones de monotonía.** En el gradient boosting de °Brix se impone que el °Brix solo puede subir con los
   rasgos físicos y con el vapor, y solo puede bajar con la alimentación.
4. **Constantes con sentido físico.** El modelo de caja gris del HMF calibra la constante cinética con el
   laboratorio y obtiene 0,161 (evaporador) y 0,188 (tanque), contra 0,18 del simulador. En el color obtiene
   0,00097 y 0,00114, contra 0,0011. El modelo con un coeficiente libre por efecto, en cambio, da valores sin sentido
   (0 y 163) por la colinealidad entre las temperaturas de los efectos.
5. **Pruebas de sensibilidad sobre los datos de prueba.**

   | Prueba | Modelo | Filas en el sentido correcto |
   |---|---|---|
   | +10 °C en todas las temperaturas → el HMF sube | Caja gris | 100 % |
   | +10 °C en todas las temperaturas → el HMF sube | Gradient boosting sobre sensores crudos | 98,2 % (los árboles no extrapolan) |
   | +10 % de alimentación → el °Brix baja | Gradient boosting monótono | 100 % |

6. **Monitoreo.** El residuo laboratorio − predicción se vigila con un límite de ±3σ (σ = 0,88 mg/kg). En las campañas
   de prueba queda dentro del límite aunque los tubos se ensucien.

## Paso a paso: cómo se hace esto en una juguera real

| Paso | En una planta real | En este ejercicio |
|---|---|---|
| **1. Definir el problema y el KPI** | Qué variable falta medir, con qué precisión y qué decisión se toma con ella (seguir controlando sin refractómetro, retener lotes, ajustar el vapor) | °Brix ± 1 como respaldo del control; HMF con error menor al del laboratorio entre análisis |
| **2. Extraer el historiador** | Exportar de PI, el historiador del SCADA o el DCS meses de datos cada minuto, con las etiquetas de los instrumentos | `datos/generar_campanas.js`: 14 campañas de 24 h con ruido de instrumentos |
| **3. Juntar el laboratorio** | Análisis de HMF y color con su hora de muestreo exacta (¡no la hora en que se cargó el resultado!) | 176 análisis cada 2 h, con 5 % de error |
| **4. Planificar ensayos en planta** | En lazo cerrado el °Brix casi no varía y los datos no enseñan la relación causa-efecto. Se hacen escalones de alimentación en manual, coordinados con producción | 2 campañas de ensayo de 8 h; sin ellas, el sensor de °Brix no le ganaba a "°Brix = consigna" |
| **5. Limpiar y alinear** | Filtrar ruido (promedios móviles), descartar paradas, CIP y arranques, y alinear el laboratorio con el proceso según el tiempo de residencia | Promedios de 5 min (°Brix) y 15 min (calidad) |
| **6. Diseñar rasgos con física** | EPE, balances, Arrhenius y tiempos de residencia con los datos de diseño del equipo | Ver la sección de fenomenología |
| **7. Dividir por tiempo** | Entrenar con el pasado y probar con el futuro. Partir al azar mezcla minutos vecinos y da métricas engañosas | Entrenamiento: campañas 1–10 + ensayo A. Prueba: campañas 11–14 + ensayo B |
| **8. Línea base y modelos** | Empezar por lo simple (física, PLS, Ridge) y sumar complejidad solo si mejora | Ingenuo → físico → Ridge → gradient boosting monótono; caja gris para la calidad |
| **9. Validar la física** | Pruebas de sensibilidad con los ingenieros de proceso: si una predicción va contra la física, el modelo no se usa | Sensibilidades, monotonía y constantes cinéticas |
| **10. Desplegar en el DCS o SCADA** | Exportar el modelo (ONNX, código en el controlador o un servidor de inferencia) y verificar que dé lo mismo que en Python | `modelo/sensor_virtual.json`, verificado con diferencia 0, y ejecutado en `sensor_virtual.html` |
| **11. Operación con respaldo** | Alarma de discrepancia entre refractómetro y sensor virtual; opción de controlar con el sensor virtual si el refractómetro falla | Botones "Simular falla del refractómetro" y "Controlar con el sensor virtual" |
| **12. Monitorear y recalibrar** | Cada análisis de laboratorio se compara con el sensor virtual; si el residuo sale de ±3σ, se recalibra | Límite de ±3σ en la página |

## Cómo usarlo

```bash
cd ml_sensor_virtual_evaporador/datos
node generar_campanas.js 14 24 11 2     # 14 campañas de 24 h + 2 ensayos de 8 h (≈ 1 min)
cd ../notebook
pip install -r ../requirements.txt
python construir_notebook.py entrenamiento_sensor_virtual.py
```

Después se abre `sensor_virtual.html`: es el evaporador con el panel "Sensor virtual · machine learning". El panel
muestra, en vivo:
- °Brix, HMF y color virtuales;
- la lectura del refractómetro;
- los análisis de laboratorio cada 2 h de planta;
- el valor real, que en una planta no existe y aquí se muestra solo para evaluar.

Con los botones se puede simular la falla del refractómetro y pasar el control al sensor virtual.

## Archivos

| Archivo | Contenido |
|---|---|
| `datos/simulador_evaporador.js` | Copia del núcleo físico del evaporador |
| `datos/generar_campanas.js` | Generador del historiador y del laboratorio |
| `datos/historico.csv`, `laboratorio.csv` | 21 136 minutos de proceso y 176 análisis |
| `notebook/entrenamiento_sensor_virtual.py` / `.ipynb` | Entrenamiento, comparación, fenomenología y exportación |
| `modelo/sensor_virtual.json` | Modelo desplegable |
| `modelo/*.csv` | Tablas de resultados, constantes cinéticas y chequeos de fenomenología |
| `figuras/` | Gráficos del notebook |
| `sensor_virtual.html` | Evaporador con el sensor virtual en vivo |
| `demo_sensor_virtual.mp4` | Video de la demo guiada |

## Limitaciones

- Los datos son simulados. En una planta, el modelo se reentrena con su historiador y su laboratorio. Lo que se
  transfiere es la **metodología**: rasgos físicos, ensayos, partición temporal, restricciones de monotonía y
  chequeos de fenomenología.
- El °Brix por EPE depende de medir bien la presión del 5º efecto: a 6 kPa, un error de 0,3 kPa equivale a casi
  0,6 °C de temperatura de saturación.
- El sensor virtual no reemplaza al laboratorio: lo complementa entre análisis, y cada análisis sirve para controlarlo.
