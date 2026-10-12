from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd


def _segundos(valor: float) -> str:
    return f'{valor:.6f}'


def _entero(valor: int) -> str:
    return f'{int(valor):,}'.replace(',', '.')


def generar_informe(resumen: pd.DataFrame, metadatos: Dict[str, Any], ruta: str) -> None:
    n_max = int(resumen['N'].max())
    m_max = int(resumen.loc[resumen['Operacion'] == 'Busqueda', 'M'].max())
    k = int(resumen['Repeticiones'].min())
    caso_labels = {'aleatorio': 'Aleatorio', 'ordenado': 'Ordenado'}
    filas = resumen[
        (resumen['N'] == n_max)
        & (resumen['M'] == m_max)
        & (resumen['Operacion'] == 'Busqueda')
    ].sort_values(['Caso', 'Estructura'])

    tabla_busqueda = [
        '| Inserción | Estructura | Altura | Promedio (s) | Desv. estándar (s) | IC 95 % (s) | CV (%) |',
        '|---|---|---:|---:|---:|---:|---:|',
    ]
    for _, fila in filas.iterrows():
        tabla_busqueda.append(
            f"| {caso_labels[fila['Caso']]} | {fila['Estructura']} | "
            f"{fila['Altura_promedio']:.1f} | {_segundos(fila['Promedio_s'])} | "
            f"{_segundos(fila['Desviacion_estandar_s'])} | "
            f"[{_segundos(fila['IC95_inferior_s'])}, {_segundos(fila['IC95_superior_s'])}] | "
            f"{fila['CV_pct']:.1f} |"
        )

    maximo_abb = filas[filas['Estructura'] == 'ABB'].set_index('Caso')
    if {'aleatorio', 'ordenado'}.issubset(maximo_abb.index):
        altura_aleatoria = maximo_abb.loc['aleatorio', 'Altura_promedio']
        altura_ordenada = maximo_abb.loc['ordenado', 'Altura_promedio']
        razon_alturas = altura_ordenada / max(altura_aleatoria, 1)
        hallazgo_altura = (
            f"Con N={_entero(n_max)}, la altura media del ABB fue {altura_aleatoria:.1f} niveles "
            f"al insertar IDs aleatorios y {_entero(altura_ordenada)} al insertarlos ordenados "
            f"(aproximadamente {razon_alturas:.1f} veces mayor). Esto evidencia que este ABB "
            f"no balanceado puede degenerar; no es una propiedad de todos los árboles binarios."
        )
    else:
        hallazgo_altura = 'No fue posible calcular la comparación de altura del ABB.'

    busqueda_aleatoria = filas[
        (filas['Caso'] == 'aleatorio') & (filas['Operacion'] == 'Busqueda')
    ].set_index('Estructura')
    if {'Lista', 'ABB', 'BPlus'}.issubset(busqueda_aleatoria.index):
        lista_t = busqueda_aleatoria.loc['Lista', 'Promedio_s']
        abb_t = busqueda_aleatoria.loc['ABB', 'Promedio_s']
        bplus_t = busqueda_aleatoria.loc['BPlus', 'Promedio_s']
        hallazgo_busqueda = (
            f"Para IDs aleatorios, N={_entero(n_max)} y M={_entero(m_max)}, los promedios observados "
            f"fueron Lista {_segundos(lista_t)} s, ABB {_segundos(abb_t)} s y "
            f"B+ {_segundos(bplus_t)} s. Es una comparación descriptiva de estas "
            f"implementaciones y este equipo, no una garantía universal."
        )
    else:
        hallazgo_busqueda = 'No fue posible calcular la comparación de búsqueda.'

    busquedas_n = resumen[
        (resumen['Operacion'] == 'Busqueda')
        & (resumen['M'] == m_max)
        & (resumen['Caso'] == 'aleatorio')
        & (resumen['Estructura'] == 'Lista')
    ].sort_values('N')
    abb_n = resumen[
        (resumen['Operacion'] == 'Busqueda')
        & (resumen['M'] == m_max)
        & (resumen['Caso'] == 'aleatorio')
        & (resumen['Estructura'] == 'ABB')
    ].set_index('N')
    umbral = None
    for _, fila in busquedas_n.iterrows():
        n = int(fila['N'])
        if n in abb_n.index:
            abb_fila = abb_n.loc[n]
            if abb_fila['IC95_superior_s'] < fila['IC95_inferior_s']:
                umbral = n
                break
    if umbral is None:
        hallazgo_umbral = (
            'En los tamaños ensayados no apareció un punto donde los IC 95 % de Lista y ABB '
            'se separaran para búsqueda aleatoria. La ausencia de separación no demuestra '
            'que los rendimientos sean iguales.'
        )
    else:
        hallazgo_umbral = (
            f"Desde N={_entero(umbral)}, los IC 95 % observados de ABB y Lista para búsqueda "
            f"aleatoria dejaron de superponerse en este experimento. Este criterio es una "
            f"señal descriptiva, no sustituye una prueba pareada."
        )

    niveles_m = sorted(
        resumen.loc[resumen['Operacion'] == 'Busqueda', 'M'].unique().astype(int)
    )
    tabla_m = [
        '| Inserción | Estructura | Tiempo M mínimo (s) | Tiempo M máximo (s) | Razón máx./mín. | µs por búsqueda (mín. → máx.) |',
        '|---|---|---:|---:|---:|---:|',
    ]
    if len(niveles_m) >= 2:
        minimo_m, maximo_m = niveles_m[0], niveles_m[-1]
        for caso in ['aleatorio', 'ordenado']:
            for estructura in ['Lista', 'ABB', 'BPlus']:
                sub = resumen[
                    (resumen['Operacion'] == 'Busqueda')
                    & (resumen['N'] == n_max)
                    & (resumen['Caso'] == caso)
                    & (resumen['Estructura'] == estructura)
                ].set_index('M')
                tiempo_min = sub.loc[minimo_m, 'Promedio_s']
                tiempo_max = sub.loc[maximo_m, 'Promedio_s']
                por_busqueda_min = tiempo_min / minimo_m * 1_000_000
                por_busqueda_max = tiempo_max / maximo_m * 1_000_000
                tabla_m.append(
                    f"| {caso_labels[caso]} | {estructura} | {_segundos(tiempo_min)} | "
                    f"{_segundos(tiempo_max)} | {tiempo_max / tiempo_min:.2f}× | "
                    f"{por_busqueda_min:.2f} → {por_busqueda_max:.2f} |"
                )

    lineas = [
        '# Informe experimental: sistema de búsqueda',
        '',
        f"Prueba ejecutada: {metadatos['fecha']}.",
        '',
        '## Objetivo y variables',
        '',
        'Comparar búsqueda, inserción y listado ascendente en Lista, ABB no balanceado y '
        'B+ de orden 4. Se varían el tamaño de entrada N, la cantidad M de búsquedas y el '
        'orden de inserción (aleatorio u ordenado). Se mantiene fija la implementación y '
        'el orden del B+ para que el experimento quepa en el límite de ejecución.',
        '',
        f"- N: {metadatos['rangos_n']}.",
        f"- M: {metadatos['rangos_m']} IDs por medición de búsqueda.",
        f'- K: {k} corridas por combinación.',
        '- IDs buscados: 80 % existentes y 20 % ausentes; el mismo conjunto de búsquedas '
        'se entrega a las tres estructuras dentro de cada corrida y nivel M.',
        '- Los registros de estudiantes son sintéticos (nombres de ejemplo, edades y promedios '
        'aleatorios); no son datos reales de una institución. La variable usada por las '
        'estructuras es el ID.',
        f"- Semilla pseudoaleatoria: {metadatos['semilla']}; generación repetible de IDs y registros.",
        '',
        '## Equipo y software',
        '',
        f"- CPU: {metadatos['cpu']} ({metadatos['nucleos']} procesadores lógicos).",
        f"- Memoria instalada: {metadatos['memoria_gib']:.1f} GiB." if metadatos['memoria_gib'] else '- Memoria instalada: no disponible.',
        f"- Sistema: {metadatos['sistema']}.",
        f"- Python: {metadatos['python']}; NumPy: {metadatos['numpy']}; "
        f"pandas: {metadatos['pandas']}; Matplotlib: {metadatos['matplotlib']}.",
        f"- Duración total (benchmark, CSV y gráficas): {metadatos['duracion_s']:.2f} s "
        f"({metadatos['duracion_s'] / 60:.2f} min).",
        '',
        '## Medición y estadística',
        '',
        '- Cada operación se cronometra por separado con `time.perf_counter_ns()`; la '
        'generación de datos y la construcción de la estructura no forman parte del tiempo '
        'de búsqueda o listado. Inserción cronometra la construcción completa con N registros.',
        '- Se conservan todas las observaciones; no se eliminan valores atípicos. Se reportan '
        'promedio, desviación estándar muestral, mediana, mínimo, máximo y coeficiente de '
        'variación (CV = desviación / promedio × 100).',
        '- El IC del 95 % para el promedio usa la distribución t de Student con K−1 grados '
        'de libertad. Con K=5, el valor crítico es 2.776. Los intervalos son descriptivos; '
        'no se realizó una prueba de hipótesis pareada.',
        '- `resultados/datos_crudos.csv` contiene una fila por corrida, operación, estructura, '
        'N y M. En inserción/listado, M=0 indica que M no aplica. '
        '`resultados/resumen_estadistico.csv` contiene las estadísticas calculadas.',
        '',
        '## Resultados destacados',
        '',
        f"En el caso mayor (N={_entero(n_max)}, M={_entero(m_max)}), búsqueda: "
        + 'promedio ± desviación estándar e IC del 95 %:',
        '',
        *tabla_busqueda,
        '',
        f'- {hallazgo_altura}',
        f'- {hallazgo_busqueda}',
        f'- {hallazgo_umbral}',
        '',
        f'En N={_entero(n_max)}, esta fue la sensibilidad observada entre el menor y el mayor M '
        f'({ _entero(niveles_m[0]) } y { _entero(niveles_m[-1]) } búsquedas):',
        '',
        *tabla_m,
        '',
        'Una razón de tiempo total cercana a la razón entre M máximo y mínimo es compatible '
        'con crecimiento aproximadamente lineal en el número de consultas. El tiempo por '
        'búsqueda ayuda a distinguir ese crecimiento de variaciones por consulta.',
        '',
        '## Complejidad y límites',
        '',
        '- Lista: insertar al final es O(1) amortizado; buscar es O(N); ordenar al listar es '
        'O(N log N).',
        '- ABB sin balancear: búsqueda/inserción son O(h), donde h es la altura; en el peor '
        'caso h=N y el costo es O(N). Listar en orden es O(N).',
        '- B+: búsqueda/inserción siguen la altura del árbol; con orden fijo 4, la altura '
        'crece logarítmicamente. El listado recorre todas las hojas y cuesta O(N).',
        '- El máximo N es 10.000, se usa una sola máquina y cinco corridas. Los resultados '
        'no prueban complejidad asintótica ni se generalizan a otro hardware o lenguaje. '
        'La carga del sistema puede afectar las mediciones; repite el experimento en un '
        'entorno estable antes de defender diferencias pequeñas.',
        '',
        '## Gráficas para la sustentación',
        '',
        '1. `Busqueda_vs_N.png`: crecimiento de las búsquedas con N, para ambos órdenes.',
        '2. `Insercion_vs_N.png`: costo de construir cada estructura.',
        '3. `Listado_vs_N.png`: costo de listar en orden ascendente.',
        '4. `Busqueda_vs_M.png`: efecto de aumentar M con N fijo en su valor máximo.',
        '5. `Altura_vs_busqueda_ABB.png`: relación entre altura y búsquedas del ABB.',
        '6. `Variabilidad_busqueda.png`: compara el CV y la estabilidad observada entre corridas.',
        '',
        'Las barras en las gráficas representan una desviación estándar. Los CSV conservan '
        'el detalle suficiente para calcular otras estadísticas sin volver a correr el benchmark.',
        '',
    ]
    Path(ruta).write_text('\n'.join(lineas), encoding='utf-8')
