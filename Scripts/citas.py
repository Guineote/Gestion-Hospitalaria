from .estructuras import PQueue, HashMap, DoublyLinkedList
from .medicos import ESPECIALIDADES_VALIDAS
from datetime import datetime, timedelta
import random

class Cita:
    def __init__(self, id_cita, id_paciente, prioridad, nota, fecha, hora, especialidad):
        self.id_cita = id_cita
        self.id_paciente = id_paciente
        self.prioridad = prioridad  # "Alta", "Media", "Baja"
        self.nota = nota  # "Enfermedad grave", etc.
        self.fecha = fecha  # str "YYYY-MM-DD"
        self.hora = hora  # str "HH:MM"
        self.especialidad = especialidad
        self.gravedad = self.get_prioridad_num()

    def __str__(self):
        return f"Cita(ID: {self.id_cita}, Paciente: {self.id_paciente}, Prioridad: {self.prioridad}, Nota: {self.nota}, Fecha: {self.fecha} {self.hora}, Especialidad: {self.especialidad})"

    def get_prioridad_num(self):
        # Para cola de prioridad: Alta=3, Media=2, Baja=1
        if self.prioridad == "Alta":
            return 3
        elif self.prioridad == "Media":
            return 2
        else:
            return 1

class GestionCitas:
    def __init__(self, gestion_medicos, gestion_pacientes):
        self.citas = HashMap()  # Clave: id_cita, Valor: Cita
        self.gestion_medicos = gestion_medicos
        self.gestion_pacientes = gestion_pacientes
        self.contador_id = 1  # Para generar IDs automáticos

    def generar_id(self):
        id_cita = f"C{self.contador_id:03d}"
        self.contador_id += 1
        return id_cita

    def registrar_nueva(self, id_paciente, prioridad, nota, fecha, hora, especialidad):
        # Validar paciente existe
        paciente = self.gestion_pacientes.buscar_por_id(id_paciente)
        if not paciente:
            return False, "Paciente no encontrado."
        if paciente.estado == "Inactivo":
            paciente.estado = "Activo"
        # Validar especialidad
        if especialidad not in ESPECIALIDADES_VALIDAS:
            return False, "Especialidad no válida."
        # Buscar médicos con esa especialidad
        medicos_disponibles = []
        for medico in self.gestion_medicos.listar_todos():
            if medico.especialidad == especialidad:
                medicos_disponibles.append(medico)
        if not medicos_disponibles:
            return False, "No hay médicos disponibles para esta especialidad."
        # Elegir uno (ej: random, o el con menos pacientes)
        import random
        medico_asignado = random.choice(medicos_disponibles)
        # Asignar paciente al médico
        self.gestion_medicos.agregar_paciente_activo(medico_asignado.id_medico, id_paciente)
        # Validar hora disponible (simple: asumir todas disponibles por ahora)
        id_cita = self.generar_id()
        cita = Cita(id_cita, id_paciente, prioridad, nota, fecha, hora, especialidad)
        self.citas.put(id_cita, cita)
        return True, id_cita

    def cancelar_cita(self, id_cita):
        try:
            self.citas.remove(id_cita)
            return True
        except KeyError:
            return False

    def modificar_cita(self, id_cita, **kwargs):
        try:
            cita = self.citas.get(id_cita)
            for key, value in kwargs.items():
                if hasattr(cita, key):
                    setattr(cita, key, value)
            return True
        except KeyError:
            return False

    def listar_todas(self):
        citas_dll = DoublyLinkedList()
        for _, cita in self.citas:
            citas_dll.append(cita)
        # Ordenar usando tu nuevo método en DLL
        citas_dll.sort(key=lambda c: datetime.strptime(f"{c.fecha} {c.hora}", "%Y-%m-%d %H:%M"))
        return citas_dll  # Devuelve DLL

    def get_cola_urgentes(self):
        # Cola de prioridad: enqueue todas, dequeue en orden de prioridad
        cola = PQueue()
        for cita in self.listar_todas():
            # Key negativa para max-heap (mayor prioridad primero)
            cola.enqueue(cita)
        return cola