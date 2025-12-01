from .estructuras import HashMap, Set, DoublyLinkedList
from .busqueda import Cadenas 

class Paciente:
    def __init__(self, id_paciente, nombre, edad, alergias=None, estado="Activo"):
        self.id_paciente = id_paciente
        self.nombre = nombre
        self.edad = edad
        self.alergias = Set()
        if alergias:
            for alergia in alergias:
                self.alergias.add(alergia)
        self.estado = estado
        self.historial = DoublyLinkedList()  

    def agregar_alergia(self, alergia):
        self.alergias.add(alergia)

    def __str__(self):
        return (f"Paciente(ID: {self.id_paciente}, Nombre: {self.nombre}, Edad: {self.edad}, "
                f"Alergias: {self.alergias}, Estado: {self.estado})")

class GestionPacientes:
    def __init__(self):
        self.pacientes = HashMap()  

    def registrar_nuevo(self, id_paciente, nombre, edad, alergias=None, estado="Activo"):
        if id_paciente in self.pacientes:
            raise ValueError(f"Paciente con ID {id_paciente} ya existe.")
        paciente = Paciente(id_paciente, nombre, edad, alergias, estado)
        self.pacientes.put(id_paciente, paciente)

    def buscar_por_id(self, id_paciente):
        try:
            return self.pacientes.get(id_paciente)
        except KeyError:
            return None

    def buscar_por_nombre(self, nombre, modo="exacto"):
        resultados = []
        nombre_lower = nombre.lower()
        for _, paciente in self.pacientes:
            nombre_pac_lower = paciente.nombre.lower()
            if modo == "exacto":
                if nombre_pac_lower == nombre_lower:
                    resultados.append(paciente)
            elif modo == "substring":
                if Cadenas.kmp(nombre_pac_lower, nombre_lower) != -1:
                    resultados.append(paciente)
            elif modo == "fuzzy":
                dist = Cadenas.levenshtein(nombre_pac_lower, nombre_lower)
                if dist <= 2: 
                    resultados.append(paciente)
            else:
                raise ValueError("Modo de búsqueda inválido.")
        return resultados

    def eliminar_paciente(self, id_paciente):
        try:
            self.pacientes.remove(id_paciente)
        except KeyError:
            raise ValueError(f"Paciente con ID {id_paciente} no encontrado.")

    def listar_todos(self):
        return [paciente for _, paciente in self.pacientes]


    def agregar_registro_medico(self, id_paciente, registro):
        paciente = self.buscar_por_id(id_paciente)
        if paciente:
            paciente.historial.append(registro)
        else:
            raise ValueError(f"Paciente con ID {id_paciente} no encontrado.")

    def ver_historial(self, id_paciente):
        paciente = self.buscar_por_id(id_paciente)
        if paciente:
            return list(paciente.historial)  
        else:
            raise ValueError(f"Paciente con ID {id_paciente} no encontrado.")