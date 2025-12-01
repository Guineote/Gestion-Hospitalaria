from .estructuras import HashMap, Set, DoublyLinkedList
from .busqueda import Cadenas

class Medicamento:
    def __init__(self, id_medicamento, nombre, cantidad, tipo):
        self.id_medicamento = id_medicamento
        self.nombre = nombre
        self.cantidad = cantidad
        self.tipo = tipo

    def __str__(self):
        return f"Medicamento(ID: {self.id_medicamento}, Nombre: {self.nombre}, Cantidad: {self.cantidad}, Tipo: {self.tipo})"

class GestionFarmacia:
    def __init__(self):
        self.inventario = HashMap()  
        self.nombres_set = Set()    

    def registrar_nuevo(self, id_medicamento, nombre, cantidad, tipo):
        if id_medicamento in self.inventario or nombre in self.nombres_set:
            return False  
        medicamento = Medicamento(id_medicamento, nombre, cantidad, tipo)
        self.inventario.put(id_medicamento, medicamento)
        self.nombres_set.add(nombre)
        return True
    
    def eliminar_medicamento(self, id_medicamento):
        try:
            med = self.inventario.get(id_medicamento)
            self.nombres_set.discard(med.nombre)
            self.inventario.remove(id_medicamento)
            return True
        except KeyError:
            return False

    def buscar_por_id(self, id_medicamento):
        try:
            return self.inventario.get(id_medicamento)
        except KeyError:
            return None

    def buscar_por_nombre(self, termino):
        resultados = []
        termino_lower = termino.lower()
        modo = "fuzzy" if len(termino) <= 4 else "substring"

        for _, med in self.inventario:
            nombre_lower = med.nombre.lower()
            palabras = nombre_lower.split()

            coincidencia = False
            if modo == "substring":
                if Cadenas.kmp(nombre_lower, termino_lower) != -1:
                    coincidencia = True
            elif modo == "fuzzy":
                distancias = [Cadenas.levenshtein(termino_lower, palabra) for palabra in palabras]
                if min(distancias) <= 1:  # Estricto para evitar falsos positivos
                    coincidencia = True

            if coincidencia:
                resultados.append(med)

        return resultados

    def actualizar_cantidad(self, id_medicamento, delta):
        med = self.buscar_por_id(id_medicamento)
        if med:
            med.cantidad += delta
            if med.cantidad < 0:
                med.cantidad = 0  # No negativo
            return True
        return False

    def listar_todos(self):
        return [med for _, med in self.inventario]