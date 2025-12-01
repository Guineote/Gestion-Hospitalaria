from .estructuras import HashMap, Set
from .busqueda import Cadenas 

ESPECIALIDADES_VALIDAS = Set()
for esp in [
    "Medicina Familiar",
    "Medicina interna",
    "Ginecología",
    "Cardiología",
    "Pediatría",
    "Neurología",
    "Ortopedía",
    "Medicina de emergencias",
    "Cirugía general"
]:
    ESPECIALIDADES_VALIDAS.add(esp)

class Medico:
    def __init__(self, id_medico, nombre, especialidad, cedula, horario=None, pacientes_activos=None):
        self.id_medico = id_medico
        self.nombre = nombre
        self.especialidad = especialidad
        self.cedula = cedula
        self.horario = HashMap()  
        if horario:
            for dia, hora in horario:
                self.horario.put(dia, hora)
        self.pacientes_activos = Set() 
        if pacientes_activos:
            for pa in pacientes_activos:
                self.pacientes_activos.add(pa)

    def agregar_horario(self, dia, hora):
        self.horario.put(dia, hora)

    def agregar_paciente_activo(self, id_paciente):
        self.pacientes_activos.add(id_paciente)

    def remover_paciente_activo(self, id_paciente):
        self.pacientes_activos.discard(id_paciente)

    def __str__(self):
        horarios_str = ", ".join(f"{dia}: {hora}" for dia, hora in self.horario.items())
        pacientes_str = ", ".join(str(pa) for pa in self.pacientes_activos)
        return (f"Medico(ID: {self.id_medico}, Nombre: {self.nombre}, Especialidad: {self.especialidad}, "
                f"Cedula: {self.cedula}, Horario: {{{horarios_str}}}, Pacientes Activos: {{{pacientes_str}}}")

class GestionMedicos:
    def __init__(self):
        self.medicos = HashMap()  
        self.especialidades = Set()  

    def registrar_nuevo(self, id_medico, nombre, especialidad, cedula, horario=None):
        """
        Registra un nuevo médico. Horario como lista de tuplas (dia, hora) para convertir a HashMap.
        Valida especialidad y evita duplicados por ID.
        Actualiza el Set de especialidades.
        
        :param id_medico: str o int, ID único
        :param nombre: str
        :param especialidad: str
        :param cedula: str
        :param horario: list of tuples (dia, hora), e.g., [("lunes", "09:00-17:00")]
        :return: True si se registró, False si ya existe o especialidad inválida
        """
        if id_medico in self.medicos:
            return False  # Duplicado
        if especialidad not in ESPECIALIDADES_VALIDAS:
            return False  # Especialidad no válida
        
        medico = Medico(id_medico, nombre, especialidad, cedula, horario)
        self.medicos.put(id_medico, medico)
        self.especialidades.add(especialidad)
        return True

    def buscar_por_id(self, id_medico):
        try:
            return self.medicos.get(id_medico)
        except KeyError:
            return None

    def buscar_por_nombre(self, nombre, modo="exacto"):
        resultados = []
        nombre_lower = nombre.lower()
        for _, medico in self.medicos:
            nombre_med_lower = medico.nombre.lower()
            if modo == "exacto":
                if nombre_med_lower == nombre_lower:
                    resultados.append(medico)
            elif modo == "substring":
                if Cadenas.kmp(nombre_med_lower, nombre_lower) != -1:
                    resultados.append(medico)
            elif modo == "fuzzy":
                dist = Cadenas.levenshtein(nombre_med_lower, nombre_lower)
                if dist <= 2: 
                    resultados.append(medico)
            else:
                raise ValueError("Modo de búsqueda inválido.")
        return resultados

    def eliminar_medico(self, id_medico):
        try:
            medico = self.medicos.get(id_medico)
            if len(medico.pacientes_activos) > 0:
                return False  # No eliminar si tiene pacientes activos
            self.medicos.remove(id_medico)
            # Actualizar Set de especialidades si ya no hay médicos con esa
            especialidad = medico.especialidad
            if not any(m.especialidad == especialidad for _, m in self.medicos):
                self.especialidades.discard(especialidad)
            return True
        except KeyError:
            return False

    def listar_todos(self):
        return [medico for _, medico in self.medicos]

    def agregar_paciente_activo(self, id_medico, id_paciente):
        medico = self.buscar_por_id(id_medico)
        if medico:
            medico.agregar_paciente_activo(id_paciente)
            return True
        return False

    def remover_paciente_activo(self, id_medico, id_paciente):
        medico = self.buscar_por_id(id_medico)
        if medico:
            medico.remover_paciente_activo(id_paciente)
            return True
        return False