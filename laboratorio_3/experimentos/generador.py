# experimentos/generador.py

import random
from typing import List, Tuple
from estructuras.estudiante import Estudiante

NOMBRES_EJEMPLO = ["Ana", "Carlos", "María", "Juan", "Laura", "Pedro", "Sofia", "Diego", "Elena", "Lucas"]

class GeneradorDatos:
    """
    Genera conjuntos de estudiantes y listas de IDs para pruebas de rendimiento.
    """

    @staticmethod
    def generar_estudiantes(n: int, ordenados: bool = False) -> List[Estudiante]:
        """
        Genera N estudiantes.
        Si ordenados=True, los IDs se generan en orden estrictamente creciente (1, 2, ..., N).
        Si ordenados=False, los IDs se entregan desordenados (aleatorios).
        """
        ids = list(range(1, n + 1))
        
        if not ordenados:
            random.shuffle(ids)

        estudiantes = []
        for id_est in ids:
            nombre = random.choice(NOMBRES_EJEMPLO)
            edad = random.randint(17, 28)
            promedio = round(random.uniform(2.5, 5.0), 2)
            estudiantes.append(Estudiante(id_est, nombre, edad, promedio))

        return estudiantes

    @staticmethod
    def generar_ids_busqueda(m: int, n_max: int, proporcion_existentes: float = 0.8) -> List[int]:
        """
        Genera M IDs para evaluar la operación de búsqueda.
        Una proporción estará dentro del rango [1, n_max] (existentes) y otra fuera (no existentes).
        """
        cant_existentes = int(m * proporcion_existentes)
        cant_no_existentes = m - cant_existentes

        existentes = [random.randint(1, n_max) for _ in range(cant_existentes)]
        no_existentes = [random.randint(n_max + 1, n_max + 2 * m) for _ in range(cant_no_existentes)]

        ids_busqueda = existentes + no_existentes
        random.shuffle(ids_busqueda)
        return ids_busqueda