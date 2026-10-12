# experimentos/benchmark.py

import time
import random
import numpy as np
import pandas as pd
from typing import List, Optional
from estructuras.lista import EstrategiaLista
from estructuras.abb import EstrategiaABB
from estructuras.bplus import EstrategiaBPlus
from experimentos.generador import GeneradorDatos

ESTRUCTURAS = {
    'Lista': EstrategiaLista,
    'ABB': EstrategiaABB,
    'BPlus': EstrategiaBPlus
}

class Benchmark:
    def __init__(self, k_repeticiones: int = 5, m_busquedas: int = 5000, semilla: int = 2026):
        self.k = k_repeticiones
        self.m = m_busquedas
        self.semilla = semilla

    def ejecutar_experimentos(
        self, rangos_n: List[int], rangos_m: Optional[List[int]] = None
    ) -> pd.DataFrame:
        if self.k < 2:
            raise ValueError('Se requieren al menos dos corridas para calcular desviación estándar.')

        rangos_m = sorted(set(rangos_m or [self.m]))
        if not rangos_m or rangos_m[0] < 1:
            raise ValueError('Cada cantidad M de búsquedas debe ser positiva.')

        random.seed(self.semilla)
        resultados = []

        for n in rangos_n:
            for caso in ['aleatorio', 'ordenado']:
                ordenado_flag = (caso == 'ordenado')
                for corrida in range(1, self.k + 1):
                    estudiantes = GeneradorDatos.generar_estudiantes(n, ordenados=ordenado_flag)
                    ids_por_m = {
                        m: GeneradorDatos.generar_ids_busqueda(m, n)
                        for m in rangos_m
                    }

                    for nombre_est, ClaseEstructura in ESTRUCTURAS.items():
                        est = ClaseEstructura()
                        t0 = time.perf_counter_ns()
                        for e in estudiantes:
                            est.insertar(e)
                        tiempo_insercion = (time.perf_counter_ns() - t0) / 1_000_000_000
                        altura = est.obtener_altura()
                        resultados.append({
                            'N': n, 'M': 0, 'Corrida': corrida, 'Semilla': self.semilla,
                            'Caso': caso, 'Estructura': nombre_est,
                            'Operacion': 'Insercion', 'Tiempo_s': tiempo_insercion,
                            'Altura': altura,
                        })

                        t0 = time.perf_counter_ns()
                        _ = est.obtener_ordenados()
                        tiempo_listado = (time.perf_counter_ns() - t0) / 1_000_000_000
                        resultados.append({
                            'N': n, 'M': 0, 'Corrida': corrida, 'Semilla': self.semilla,
                            'Caso': caso, 'Estructura': nombre_est,
                            'Operacion': 'Listado', 'Tiempo_s': tiempo_listado,
                            'Altura': altura,
                        })

                        for m, ids_buscar in ids_por_m.items():
                            t0 = time.perf_counter_ns()
                            for id_b in ids_buscar:
                                est.buscar(id_b)
                            tiempo_busqueda = (time.perf_counter_ns() - t0) / 1_000_000_000
                            resultados.append({
                                'N': n, 'M': m, 'Corrida': corrida, 'Semilla': self.semilla,
                                'Caso': caso, 'Estructura': nombre_est,
                                'Operacion': 'Busqueda', 'Tiempo_s': tiempo_busqueda,
                                'Altura': altura,
                            })

        return pd.DataFrame(resultados)

    @staticmethod
    def calcular_resumen(datos_crudos: pd.DataFrame) -> pd.DataFrame:
        columnas = ['N', 'M', 'Caso', 'Estructura', 'Operacion']
        resumen = datos_crudos.groupby(columnas)['Tiempo_s'].agg(
            Promedio_s='mean',
            Desviacion_estandar_s='std',
            Mediana_s='median',
            Minimo_s='min',
            Maximo_s='max',
            Repeticiones='count',
        ).reset_index()
        resumen['CV_pct'] = (
            resumen['Desviacion_estandar_s'] / resumen['Promedio_s'] * 100
        )

        t_critico_95 = {
            1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
            6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
            11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
            16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
            21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
            26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
        }
        resumen['IC95_margen_s'] = resumen.apply(
            lambda fila: t_critico_95.get(int(fila['Repeticiones']) - 1, 1.96)
            * fila['Desviacion_estandar_s'] / np.sqrt(fila['Repeticiones']),
            axis=1,
        )
        resumen['IC95_inferior_s'] = (
            resumen['Promedio_s'] - resumen['IC95_margen_s']
        ).clip(lower=0)
        resumen['IC95_superior_s'] = (
            resumen['Promedio_s'] + resumen['IC95_margen_s']
        )
        resumen['Tiempo_por_busqueda_us'] = np.where(
            (resumen['Operacion'] == 'Busqueda') & (resumen['M'] > 0),
            resumen['Promedio_s'] / resumen['M'] * 1_000_000,
            np.nan,
        )

        alturas = datos_crudos.drop_duplicates(
            ['N', 'Caso', 'Estructura', 'Corrida']
        ).groupby(['N', 'Caso', 'Estructura'])['Altura'].agg(
            Altura_promedio='mean', Altura_desviacion='std'
        ).reset_index()
        return resumen.merge(alturas, on=['N', 'Caso', 'Estructura'], how='left')