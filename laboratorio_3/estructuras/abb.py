# estructuras/abb.py

from typing import List, Optional
from estructuras.estudiante import Estudiante

class NodoABB:
    def __init__(self, estudiante: Estudiante):
        self.estudiante = estudiante
        self.izq: Optional['NodoABB'] = None
        self.der: Optional['NodoABB'] = None

class EstrategiaABB:
    def __init__(self):
        self.raiz: Optional[NodoABB] = None

    def insertar(self, estudiante: Estudiante) -> None:
        nuevo_nodo = NodoABB(estudiante)
        if self.raiz is None:
            self.raiz = nuevo_nodo
            return

        actual = self.raiz
        while True:
            if estudiante.id < actual.estudiante.id:
                if actual.izq is None:
                    actual.izq = nuevo_nodo
                    break
                actual = actual.izq
            elif estudiante.id > actual.estudiante.id:
                if actual.der is None:
                    actual.der = nuevo_nodo
                    break
                actual = actual.der
            else:
                # ID duplicado (se actualiza el registro)
                actual.estudiante = estudiante
                break

    def buscar(self, id_estudiante: int) -> Optional[Estudiante]:
        actual = self.raiz
        while actual:
            if id_estudiante == actual.estudiante.id:
                return actual.estudiante
            elif id_estudiante < actual.estudiante.id:
                actual = actual.izq
            else:
                actual = actual.der
        return None

    def obtener_ordenados(self) -> List[Estudiante]:
        resultado = []
        pila = []
        actual = self.raiz
        while pila or actual:
            while actual:
                pila.append(actual)
                actual = actual.izq
            actual = pila.pop()
            resultado.append(actual.estudiante)
            actual = actual.der
        return resultado

    def obtener_altura(self) -> int:
        if not self.raiz:
            return 0
        
        # Cálculo iterativo de la altura por niveles (BFS)
        altura = 0
        nivel_actual = [self.raiz]
        while nivel_actual:
            altura += 1
            siguiente_nivel = []
            for nodo in nivel_actual:
                if nodo.izq:
                    siguiente_nivel.append(nodo.izq)
                if nodo.der:
                    siguiente_nivel.append(nodo.der)
            nivel_actual = siguiente_nivel
        return altura