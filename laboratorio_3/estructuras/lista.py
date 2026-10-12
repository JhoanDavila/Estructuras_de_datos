# estructuras/lista.py

from typing import List, Optional
from estructuras.estudiante import Estudiante

class EstrategiaLista:
    def __init__(self):
        self.estudiantes: List[Estudiante] = []

    def insertar(self, estudiante: Estudiante) -> None:
        self.estudiantes.append(estudiante)

    def buscar(self, id_estudiante: int) -> Optional[Estudiante]:
        for est in self.estudiantes:
            if est.id == id_estudiante:
                return est
        return None

    def obtener_ordenados(self) -> List[Estudiante]:
        return sorted(self.estudiantes, key=lambda x: x.id)

    def obtener_altura(self) -> int:
        # En una lista la altura o profundidad equivalente es N
        return len(self.estudiantes)