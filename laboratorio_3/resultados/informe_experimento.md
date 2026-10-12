# Informe experimental: sistema de búsqueda

Prueba ejecutada: 2026-10-06T10:21:14-05:00.

## Objetivo y variables

Comparar búsqueda, inserción y listado ascendente en Lista, ABB no balanceado y B+ de orden 4. Se varían el tamaño de entrada N, la cantidad M de búsquedas y el orden de inserción (aleatorio u ordenado). Se mantiene fija la implementación y el orden del B+ para que el experimento quepa en el límite de ejecución.

- N: [100, 500, 1000, 2500, 5000, 10000].
- M: [1000, 2500, 5000] IDs por medición de búsqueda.
- K: 5 corridas por combinación.
- IDs buscados: 80 % existentes y 20 % ausentes; el mismo conjunto de búsquedas se entrega a las tres estructuras dentro de cada corrida y nivel M.
- Los registros de estudiantes son sintéticos (nombres de ejemplo, edades y promedios aleatorios); no son datos reales de una institución. La variable usada por las estructuras es el ID.
- Semilla pseudoaleatoria: 2026; generación repetible de IDs y registros.

## Equipo y software

- CPU: AMD Ryzen 5 3450U with Radeon Vega Mobile Gfx (8 procesadores lógicos).
- Memoria instalada: 5.7 GiB.
- Sistema: Linux-7.0.0-38-generic-x86_64-with-glibc2.39.
- Python: 3.12.3; NumPy: 1.26.4; pandas: 2.1.4; Matplotlib: 3.6.3.
- Duración total (benchmark, CSV y gráficas): 108.52 s (1.81 min).

## Medición y estadística

- Cada operación se cronometra por separado con `time.perf_counter_ns()`; la generación de datos y la construcción de la estructura no forman parte del tiempo de búsqueda o listado. Inserción cronometra la construcción completa con N registros.
- Se conservan todas las observaciones; no se eliminan valores atípicos. Se reportan promedio, desviación estándar muestral, mediana, mínimo, máximo y coeficiente de variación (CV = desviación / promedio × 100).
- El IC del 95 % para el promedio usa la distribución t de Student con K−1 grados de libertad. Con K=5, el valor crítico es 2.776. Los intervalos son descriptivos; no se realizó una prueba de hipótesis pareada.
- `resultados/datos_crudos.csv` contiene una fila por corrida, operación, estructura, N y M. En inserción/listado, M=0 indica que M no aplica. `resultados/resumen_estadistico.csv` contiene las estadísticas calculadas.

## Resultados destacados

En el caso mayor (N=10.000, M=5.000), búsqueda: promedio ± desviación estándar e IC del 95 %:

| Inserción | Estructura | Altura | Promedio (s) | Desv. estándar (s) | IC 95 % (s) | CV (%) |
|---|---|---:|---:|---:|---:|---:|
| Aleatorio | ABB | 30.4 | 0.007219 | 0.001681 | [0.005133, 0.009306] | 23.3 |
| Aleatorio | BPlus | 11.0 | 0.015952 | 0.001063 | [0.014633, 0.017272] | 6.7 |
| Aleatorio | Lista | 10000.0 | 0.929210 | 0.063611 | [0.850239, 1.008181] | 6.8 |
| Ordenado | ABB | 10000.0 | 2.815609 | 0.206102 | [2.559740, 3.071477] | 7.3 |
| Ordenado | BPlus | 14.0 | 0.023220 | 0.001404 | [0.021478, 0.024963] | 6.0 |
| Ordenado | Lista | 10000.0 | 0.894351 | 0.079798 | [0.795285, 0.993418] | 8.9 |

- Con N=10.000, la altura media del ABB fue 30.4 niveles al insertar IDs aleatorios y 10.000 al insertarlos ordenados (aproximadamente 328.9 veces mayor). Esto evidencia que este ABB no balanceado puede degenerar; no es una propiedad de todos los árboles binarios.
- Para IDs aleatorios, N=10.000 y M=5.000, los promedios observados fueron Lista 0.929210 s, ABB 0.007219 s y B+ 0.015952 s. Es una comparación descriptiva de estas implementaciones y este equipo, no una garantía universal.
- Desde N=100, los IC 95 % observados de ABB y Lista para búsqueda aleatoria dejaron de superponerse en este experimento. Este criterio es una señal descriptiva, no sustituye una prueba pareada.

En N=10.000, esta fue la sensibilidad observada entre el menor y el mayor M (1.000 y 5.000 búsquedas):

| Inserción | Estructura | Tiempo M mínimo (s) | Tiempo M máximo (s) | Razón máx./mín. | µs por búsqueda (mín. → máx.) |
|---|---|---:|---:|---:|---:|
| Aleatorio | Lista | 0.188639 | 0.929210 | 4.93× | 188.64 → 185.84 |
| Aleatorio | ABB | 0.001912 | 0.007219 | 3.78× | 1.91 → 1.44 |
| Aleatorio | BPlus | 0.004522 | 0.015952 | 3.53× | 4.52 → 3.19 |
| Ordenado | Lista | 0.186311 | 0.894351 | 4.80× | 186.31 → 178.87 |
| Ordenado | ABB | 0.571990 | 2.815609 | 4.92× | 571.99 → 563.12 |
| Ordenado | BPlus | 0.005320 | 0.023220 | 4.36× | 5.32 → 4.64 |

Una razón de tiempo total cercana a la razón entre M máximo y mínimo es compatible con crecimiento aproximadamente lineal en el número de consultas. El tiempo por búsqueda ayuda a distinguir ese crecimiento de variaciones por consulta.

## Complejidad y límites

- Lista: insertar al final es O(1) amortizado; buscar es O(N); ordenar al listar es O(N log N).
- ABB sin balancear: búsqueda/inserción son O(h), donde h es la altura; en el peor caso h=N y el costo es O(N). Listar en orden es O(N).
- B+: búsqueda/inserción siguen la altura del árbol; con orden fijo 4, la altura crece logarítmicamente. El listado recorre todas las hojas y cuesta O(N).
- El máximo N es 10.000, se usa una sola máquina y cinco corridas. Los resultados no prueban complejidad asintótica ni se generalizan a otro hardware o lenguaje. La carga del sistema puede afectar las mediciones; repite el experimento en un entorno estable antes de defender diferencias pequeñas.

## Gráficas para la sustentación

1. `Busqueda_vs_N.png`: crecimiento de las búsquedas con N, para ambos órdenes.
2. `Insercion_vs_N.png`: costo de construir cada estructura.
3. `Listado_vs_N.png`: costo de listar en orden ascendente.
4. `Busqueda_vs_M.png`: efecto de aumentar M con N fijo en su valor máximo.
5. `Altura_vs_busqueda_ABB.png`: relación entre altura y búsquedas del ABB.
6. `Variabilidad_busqueda.png`: compara el CV y la estabilidad observada entre corridas.

Las barras en las gráficas representan una desviación estándar. Los CSV conservan el detalle suficiente para calcular otras estadísticas sin volver a correr el benchmark.
