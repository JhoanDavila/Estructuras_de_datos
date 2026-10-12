# estructuras/bplus.py

from typing import List, Optional
from estructuras.estudiante import Estudiante

class NodoBPlus:
    def __init__(self, es_hoja: bool = False):
        self.es_hoja = es_hoja
        self.llaves: List[int] = []
        self.hijos: List['NodoBPlus'] = []       # En hojas no se usa
        self.valores: List[Estudiante] = []       # Solo para hojas
        self.siguiente: Optional['NodoBPlus'] = None # Enlace entre hojas

class EstrategiaBPlus:
    def __init__(self, orden: int = 4):
        self.orden = orden
        self.raiz = NodoBPlus(es_hoja=True)

    def buscar(self, id_estudiante: int) -> Optional[Estudiante]:
        actual = self.raiz
        while not actual.es_hoja:
            i = 0
            while i < len(actual.llaves) and id_estudiante >= actual.llaves[i]:
                i += 1
            actual = actual.hijos[i]

        for i, llave in enumerate(actual.llaves):
            if llave == id_estudiante:
                return actual.valores[i]
        return None

    def insertar(self, estudiante: Estudiante) -> None:
        raiz = self.raiz
        if len(raiz.llaves) == self.orden - 1:
            nueva_raiz = NodoBPlus(es_hoja=False)
            nueva_raiz.hijos.append(self.raiz)
            self._dividir_hijo(nueva_raiz, 0, self.raiz)
            self.raiz = nueva_raiz
        self._insertar_no_lleno(self.raiz, estudiante)

    def _dividir_hijo(self, padre: NodoBPlus, i: int, hijo: NodoBPlus) -> None:
        medio = len(hijo.llaves) // 2
        nuevo = NodoBPlus(es_hoja=hijo.es_hoja)

        if hijo.es_hoja:
            nuevo.llaves = hijo.llaves[medio:]
            nuevo.valores = hijo.valores[medio:]
            hijo.llaves = hijo.llaves[:medio]
            hijo.valores = hijo.valores[:medio]
            
            nuevo.siguiente = hijo.siguiente
            hijo.siguiente = nuevo
            
            padre.llaves.insert(i, nuevo.llaves[0])
            padre.hijos.insert(i + 1, nuevo)
        else:
            promocionar = hijo.llaves[medio]
            nuevo.llaves = hijo.llaves[medio + 1:]
            nuevo.hijos = hijo.hijos[medio + 1:]
            
            hijo.llaves = hijo.llaves[:medio]
            hijo.hijos = hijo.hijos[:medio + 1]
            
            padre.llaves.insert(i, promocionar)
            padre.hijos.insert(i + 1, nuevo)

    def _insertar_no_lleno(self, nodo: NodoBPlus, estudiante: Estudiante) -> None:
        if nodo.es_hoja:
            i = 0
            while i < len(nodo.llaves) and nodo.llaves[i] < estudiante.id:
                i += 1
            if i < len(nodo.llaves) and nodo.llaves[i] == estudiante.id:
                nodo.valores[i] = estudiante
            else:
                nodo.llaves.insert(i, estudiante.id)
                nodo.valores.insert(i, estudiante)
        else:
            i = len(nodo.llaves) - 1
            while i >= 0 and estudiante.id < nodo.llaves[i]:
                i -= 1
            i += 1
            if len(nodo.hijos[i].llaves) == self.orden - 1:
                self._dividir_hijo(nodo, i, nodo.hijos[i])
                if estudiante.id >= nodo.llaves[i]:
                    i += 1
            self._insertar_no_lleno(nodo.hijos[i], estudiante)

    def obtener_ordenados(self) -> List[Estudiante]:
        resultado = []
        actual = self.raiz
        while not actual.es_hoja:
            actual = actual.hijos[0]
        
        while actual:
            resultado.extend(actual.valores)
            actual = actual.siguiente
        return resultado

    def obtener_altura(self) -> int:
        altura = 0
        actual = self.raiz
        while actual:
            altura += 1
            if actual.es_hoja:
                break
            actual = actual.hijos[0]
        return altura