# Laboratorio 3:

**Estudiante:** Jhoan Sebastian Davila Hernandez
## 1. Descripción del Problema

Una institución educativa requiere un sistema de información para gestionar los registros académicos de sus estudiantes. Cada registro contiene un **ID único de matrícula**, **Nombre**, **Edad** y **Promedio académico**. 

El sistema debe soportar de manera eficiente tres operaciones fundamentales:
1. **Buscar:** Consultar la información de un estudiante dado su ID.
2. **Insertar:** Registrar un nuevo estudiante en el sistema.
3. **Listar:** Mostrar la lista completa de estudiantes ordenados de forma ascendente por su ID.

### Pregunta Central del Estudio
El objetivo principal de este proyecto es estudiar experimentalmente cómo escalan los tiempos de ejecución de estas operaciones al variar el tamaño de entrada $N$ (hasta 10.000 estudiantes) y la cantidad de consultas $M$, evaluando tres estrategias de almacenamiento:
- **Lista sin ordenar:** Inserción simple, búsqueda lineal $\mathcal{O}(N)$ y ordenamiento previo al listar.
- **Árbol Binario de Búsqueda (ABB):** Estructura jerárquica no balanceada sensible al orden de inserción.
- **Árbol B+ (Orden 4):** Estructura m-vías balanceada con índices internos y hojas enlazadas.

Asimismo, se analiza el impacto drástico que tiene el orden de llegada de los datos (IDs aleatorios vs. IDs ordenados) sobre las estructuras de árbol no balanceadas.

## 2. Diseño Experimental

Para evaluar la eficiencia y la capacidad de escalamiento de las estructuras, se construyó un benchmark en Python bajo las siguientes condiciones controladas:

### Estructuras de Datos Evaluadas
1. **Lista:** Almacena los registros en un arreglo dinámico simple. Inserta elementos al final en $\mathcal{O}(1)$ amortizado, realiza búsquedas secuenciales en $\mathcal{O}(N)$ y requiere ordenar una copia del arreglo para el listado ascendente en $\mathcal{O}(N \log N)$.
2. **Árbol Binario de Búsqueda (ABB):** Implementación jerárquica no balanceada. Presenta una complejidad de $\mathcal{O}(h)$ para inserción y búsqueda (donde $h$ es la altura del árbol). Un recorrido *inorder* permite generar el listado ordenado en $\mathcal{O}(N)$.
3. **Árbol B+ (Orden 4):** Estructura m-vías balanceada. Los nodos internos funcionan como índice y las hojas guardan los registros enlazados entre sí. Ofrece búsquedas e inserciones en $\mathcal{O}(\log N)$ y recorre las hojas en $\mathcal{O}(N)$ para el listado ascendente.

### Parámetros y Factores de Entrada
- **Tamaños de entrada ($N$):** Se evaluaron 6 niveles: 100, 500, 1.000, 2.500, 5.000 y 10.000 registros de estudiantes.
- **Volumen de búsquedas ($M$):** Se probaron 1.000, 2.500 y 5.000 consultas por cada corrida de evaluación.
- **Número de repeticiones ($K$):** Cada combinación de parámetros se ejecutó 5 veces ($K=5$) para calcular métricas de dispersión e intervalos de confianza.
- **Semilla fija:** Se utilizó la semilla `2026` para garantizar la generación idéntica y reproducible de datos sintéticos y conjuntos de búsqueda.

### Patrones de Inserción
Se compararon dos escenarios de llegada para los datos:
- **IDs Aleatorios:** Los estudiantes se insertan con claves distribuidas al azar uniformemente entre 1 y $N$.
- **IDs Ordenados:** Los estudiantes se insertan siguiendo un orden estrictamente creciente de ID. Este escenario busca evaluar el caso peor del ABB no balanceado.

### Generación de Consultas
Cada conjunto de $M$ búsquedas está compuesto por un **80% de IDs existentes** en la estructura y un **20% de IDs ausentes** (fuera del rango de inserción). Las 3 estructuras evaluadas reciben exactamente el mismo conjunto de consultas dentro de cada corrida.

### Medición de Tiempos y Tratamiento de Datos
- **Aislamiento de la medición:** Los tiempos de inserción, búsqueda y listado se cronometran por separado utilizando `time.perf_counter_ns()`. La generación de datos sintéticos y la inicialización de memoria quedan totalmente excluidas de las mediciones.
- **Tratamiento de valores atípicos:** Se conservan el 100% de las observaciones registradas; no se elimina ningún valor atípico para reflejar la variabilidad real de la máquina y la gestión de memoria del entorno.

## 3. Explicación de las Estructuras y Complejidad Teórica vs. Resultados

A continuación se contrasta el comportamiento teórico de cada estructura de datos frente a las mediciones reales obtenidas en el benchmark para el caso máximo ($N = 10.000$ estudiantes, $M = 5.000$ búsquedas).

### Resumen de Complejidad Teórica

| Estructura | Inserción | Búsqueda (Mejor / Promedio) | Búsqueda (Peor Caso) | Listado Ascendente |
|---|---|---|---|---|
| **Lista** | $\mathcal{O}(1)$ amortizado | $\mathcal{O}(N)$ | $\mathcal{O}(N)$ | $\mathcal{O}(N \log N)$ |
| **ABB (no balanceado)** | $\mathcal{O}(h)$ | $\mathcal{O}(\log N)$ | $\mathcal{O}(N)$ (si $h = N$) | $\mathcal{O}(N)$ |
| **Árbol B+ (Orden 4)** | $\mathcal{O}(\log N)$ | $\mathcal{O}(\log_b N)$ | $\mathcal{O}(\log_b N)$ | $\mathcal{O}(N)$ |

---

### Análisis de Resultados Experimentales (N = 10.000, M = 5.000)

#### 1. Lista sin ordenar
- **Teoría:** Insertar al final es un proceso eficiente $\mathcal{O}(1)$. Sin embargo, al no mantener un orden, la búsqueda requiere un recorrido secuencial $\mathcal{O}(N)$. Para listar, debe ordenar una copia de la lista en $\mathcal{O}(N \log N)$.
- **Resultados:** 
  - **Búsqueda:** Fue la estructura más lenta en ambos patrones de inserción, tomando alrededor de **0.929 s** (aleatorio) y **0.894 s** (ordenado) para completar las 5.000 consultas.
  - **Inserción:** Mantuvo los tiempos más bajos de construcción (~0.001 s)].

#### 2. Árbol Binario de Búsqueda (ABB)
- **Teoría:** Su complejidad depende directamente de la altura $h$ del árbol. Si los datos ingresan al azar, el árbol se mantiene razonablemente balanceado con $h \approx \mathcal{O}(\log N)$. Si los datos ingresan de forma estrictamente ordenada, la estructura degenera en una lista enlazada, donde $h = N$ y la búsqueda se degrada a $\mathcal{O}(N)$.
- **Resultados:**
  - **Caso Aleatorio ($h \approx 30.4$ niveles):** En $N = 10.000$, logró el mejor tiempo de búsqueda entre todas las estructuras con tan solo **0.0072 s**.
  - **Caso Ordenado ($h = 10.000$ niveles):** Al degenerar completamente la estructura, el tiempo de búsqueda se disparó a **2.815 s** (~390 veces más lento que el caso aleatorio), superando incluso el tiempo de búsqueda de la Lista.

#### 3. Árbol B+ (Orden 4)
- **Teoría:** Estructura multicamino balanceada que garantiza una altura logarítmica baja de forma uniforme. La búsqueda e inserción toman $\mathcal{O}(\log N)$ independientemente del orden de llegada de los datos. El listado ordenado recorre la secuencia enlazada de las hojas en $\mathcal{O}(N)$.
- **Resultados:**
  - **Inmunidad al orden de llegada:** En $N = 10.000$, el tiempo de búsqueda se mantuvo extremadamente estable y rápido tanto con IDs aleatorios (**0.0159 s**, $h = 11.0$) como con IDs ordenados (**0.0232 s**, $h = 14.0$).
  - **Costo de Inserción:** Debido a las operaciones de división de nodos (*splits*) y ajuste de claves de índice durante la inserción, la construcción tomó más tiempo (~0.076 s) que en la Lista o el ABB aleatorio, pero garantizó predictibilidad y escalabilidad en las búsquedas.

---

### Conclusión sobre la Complejidad

1. **Lista sin ordenar:** Es ideal si la prioridad exclusiva es la ingesta rápida de datos ($\mathcal{O}(1)$ amortizado), pero resulta inviable para volúmenes altos de consulta debido a la penalización lineal $\mathcal{O}(N)$ en cada búsqueda.
2. **ABB no balanceado:** Muestra un rendimiento excelente con entradas aleatorias ($h \approx 30.4$), pero es extremadamente vulnerable al orden de llegada: cuando los datos entran ordenados, se degrada a una lista enlazada ($h = 10.000$), elevando el tiempo de búsqueda en más de dos órdenes de magnitud.
3. **Árbol B+ (Orden 4):** Ofrece la solución más consistente, sólida y escalable para un sistema de almacenamiento y búsqueda. Aunque su costo de inserción es ligeramente superior por el mantenimiento de índices y divisiones de nodos, garantiza búsquedas logarítmicas estables ($\approx 0.015 - 0.023\text{ s}$) independientemente de cómo ingresen los datos.

## 4. Guía de Visualización de Gráficas

Las gráficas generadas se encuentran almacenadas en el directorio `resultados/graficas/`. Para la presentación y defensa del estudio, se recomienda seguir este orden explicativo:

1. **`Busqueda_vs_N.png` — Escalabilidad de la Búsqueda según $N$**
   - **Qué representa:** Muestra el tiempo promedio de búsqueda a medida que crece el número de estudiantes ($N$) de 100 a 10.000, fijando $M = 5.000$ consultas. Los dos paneles dividen la inserción aleatoria de la ordenada.
   - **Hallazgo clave:** Evidencia la búsqueda lineal $\mathcal{O}(N)$ de la Lista y la severa degeneración del ABB a $\mathcal{O}(N)$ cuando entra ordenado, contrastando con el comportamiento logarítmico e inmune del Árbol B+.

2. **`Altura_vs_busqueda_ABB.png` — Relación entre Altura y Tiempo en el ABB**
   - **Qué representa:** Correlaciona la altura promedio observada en el ABB con el tiempo consumido por las búsquedas.
   - **Hallazgo clave:** Muestra de forma directa cómo pasar de $h \approx 30.4$ niveles (aleatorio) a $h = 10.000$ niveles (ordenado) incrementa el tiempo de búsqueda en casi 390 veces, demostrando el impacto práctico de la falta de balanceo.

3. **`Insercion_vs_N.png` — Costo de Construcción e Inserción**
   - **Qué representa:** Compara el tiempo que tarda cada estructura en construir la base de datos con $N$ registros.
   - **Hallazgo clave:** La Lista presenta los menores tiempos de inserción ($\mathcal{O}(1)$ amortizado). El B+ requiere mayor tiempo inicial por las divisiones de nodos y mantenimiento de índices, un costo que se compensa posteriormente en la fase de consultas.

4. **`Listado_vs_N.png` — Rendimiento del Listado Ascendente**
   - **Qué representa:** Evalúa el tiempo necesario para entregar la totalidad de los estudiantes ordenados por ID de menor a mayor.
   - **Hallazgo clave:** Compara el costo de ordenar una copia en la Lista ($\mathcal{O}(N \log N)$) frente al recorrido *inorder* en el ABB y el recorrido de la secuencia de hojas en el Árbol B+ ($\mathcal{O}(N)$).

5. **`Busqueda_vs_M.png` — Sensibilidad al Número de Consultas ($M$)**
   - **Qué representa:** Mantiene $N = 10.000$ fijo y evalúa la respuesta al incrementar el volumen de búsquedas ($M = 1.000, 2.500, 5.000$).
   - **Hallazgo clave:** La tendencia directamente proporcional (lineal con respecto a $M$) confirma que el tiempo unitario por consulta permanece constante y predecible al escalar el número de usuarios o peticiones.

6. **`Variabilidad_busqueda.png` — Estabilidad y Dispersión de las Mediciones**
   - **Qué representa:** Compara el Coeficiente de Variación ($CV = \frac{\text{Desviación}}{\text{Promedio}} \times 100$) en el caso mayor ($N=10.000, M=5.000$).
   - **Hallazgo clave:** Un menor $CV$ refleja mediciones más estables entre ejecuciones. El Árbol B+ demuestra ser la estructura más estable y predecible ($CV \approx 6.0\% - 6.7\%$).

> **Nota de lectura:** En las figuras con rangos de tiempo muy amplios, el eje de ordenadas (eje Y) utiliza escala logarítmica. Las barras verticales en cada punto representan una desviación estándar entre las $K=5$ corridas de prueba.

## Instructivo para replicar el laboratorio:
Para ejecutar el laboratorio se requiere minimo tener python y las librerias: `numpy`, `pandas` y `matplotlib`
teniendo esto solo es ejecutar el orquestador main.py, desde donde se manejan los atributos que se van a usar durante el experimento, ademas de donde se llaman todos los scripts para crear los datos dentro de las estructuras y ejecutar los experimentos.