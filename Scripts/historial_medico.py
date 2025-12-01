from datetime import datetime
from .pacientes import GestionPacientes  
from .busqueda import Cadenas  
from .estructuras import DoublyLinkedList

class RegistroMedico:
    def __init__(self, fecha=None, tipo="Consulta", descripcion=""):
        self.fecha = fecha or datetime.now().strftime("%d/%m/%Y")
        self.tipo = tipo  # e.g., "Consulta", "Resultado", "Tratamiento"
        self.descripcion = descripcion

    def __str__(self):
        lineas = DoublyLinkedList()

        # Primera línea: la consulta
        lineas.append(f"- Consulta: {self.fecha}")

        # Especialidad (solo si no es la predeterminada)
        especialidad = self.tipo 
        if self.tipo != "Consulta":
            lineas.append(f"  - Especialidad: {especialidad}")

        # Procesamos la descripción línea por línea
        if self.descripcion.strip():
            lineas_desc = self.descripcion.strip().split('\n')
            for linea in lineas_desc:
                linea = linea.strip()
                if linea:
                    if ":" in linea:
                        clave, valor = linea.split(":", 1)
                        lineas.append(f"  - {clave.strip()}: {valor.strip()}")
                    else:
                        lineas.append(f"  - {linea}")

        # Convertimos a texto bonito
        resultado = ""
        actual = lineas._DoublyLinkedList__head 
        while actual:
            resultado += actual.get_data() + "\n"
            actual = actual.get_next()

        return resultado.rstrip()  # quita el último salto de línea

class GestionHistorial:
    def __init__(self, gestion_pacientes):
        self.gestion_pacientes = gestion_pacientes  # Referencia a GestionPacientes para integración

    def agregar_nuevo_registro(self, id_paciente, tipo="Consulta", descripcion=""):
        """
        Agrega un nuevo registro al historial de un paciente.
        
        :param id_paciente: str, ID del paciente
        :param tipo: str, tipo de registro (e.g., "Consulta", "Resultado", "Tratamiento")
        :param descripcion: str, detalles del registro
        :return: True si agregado, False si paciente no existe
        """
        try:
            registro = RegistroMedico(tipo=tipo, descripcion=descripcion)
            self.gestion_pacientes.agregar_registro_medico(id_paciente, registro)
            return True
        except ValueError:
            return False

    def ver_historial(self, id_paciente, formateado=False):
        """
        Ver el historial de un paciente.
        
        :param id_paciente: str, ID del paciente
        :param formateado: bool, si True, devuelve string como en el ejemplo; si False, lista de registros
        :return: str o list de RegistroMedico, o None si no encontrado
        """
        try:
            paciente = self.gestion_pacientes.buscar_por_id(id_paciente)
            if not paciente:
                return None

            historial = paciente.historial  # Ya es DoublyLinkedList

            if not formateado:
                return historial

            output = f"[ Historial de Paciente - {paciente.nombre} ]\n\n"

            if historial.is_empty():
                output += "    (No hay registros médicos aún)\n"
            else:
                actual = historial._DoublyLinkedList__head
                while actual:
                    output += str(actual.get_data()) + "\n\n"
                    actual = actual.get_next()

            return output.rstrip()
        except Exception:
            return None

    # Método adicional: buscar en historial por descripción (usando busqueda.py)
    def buscar_en_historial(self, id_paciente, patron, modo="substring"):
        historial = self.ver_historial(id_paciente)
        if not historial:
            return []
        resultados = []
        for reg in historial:
            if modo == "substring" and Cadenas.kmp(reg.descripcion.lower(), patron.lower()) != -1:
                resultados.append(reg)
            elif modo == "fuzzy":
                dist = Cadenas.levenshtein(reg.descripcion.lower(), patron.lower())
                if dist <= 3:  # Umbral ajustable
                    resultados.append(reg)
        return resultados