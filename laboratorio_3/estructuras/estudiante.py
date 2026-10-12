# estructuras/estudiante.py

class Estudiante:
    """
    Representa un registro individual de un estudiante.
    """
    __slots__ = ('id', 'nombre', 'edad', 'promedio')

    def __init__(self, id_estudiante: int, nombre: str, edad: int, promedio: float):
        self.id = id_estudiante
        self.nombre = nombre
        self.edad = edad
        self.promedio = promedio

    def __eq__(self, other):
        if isinstance(other, Estudiante):
            return self.id == other.id
        return self.id == other

    def __lt__(self, other):
        if isinstance(other, Estudiante):
            return self.id < other.id
        return self.id < other

    def __gt__(self, other):
        if isinstance(other, Estudiante):
            return self.id > other.id
        return self.id > other

    def __repr__(self):
        return f"Estudiante(id={self.id}, nombre='{self.nombre}', edad={self.edad}, promedio={self.promedio})"