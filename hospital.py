from Scripts.pacientes import GestionPacientes, Paciente
from Scripts.medicos import GestionMedicos, Medico, ESPECIALIDADES_VALIDAS
from Scripts.historial_medico import GestionHistorial, RegistroMedico
from Scripts.busqueda import Cadenas
from Scripts.estructuras import DoublyLinkedList, Set
from Scripts.farmacia import GestionFarmacia, Medicamento
from Scripts.citas import GestionCitas, Cita
from Scripts.notificaciones import GestionNotificaciones
from Scripts.estructuras import HashMap, Set, PQueue
from datetime import datetime, timedelta
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import Toplevel, Label, Entry, Button
import random
import os
import ttkbootstrap as ttk


class HospitalGUI(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gestion_pacientes = GestionPacientes()
        self.gestion_medicos = GestionMedicos()
        self.gestion_historial = GestionHistorial(self.gestion_pacientes)
        self.gestion_farmacia = GestionFarmacia()
        self.gestion_citas = GestionCitas(self.gestion_medicos, self.gestion_pacientes)
        self.gestion_notificaciones = GestionNotificaciones()
        self.load_from_txt()
        self.pack(fill=BOTH, expand=YES)
        self.crear_interfaz()
        
        if len(self.gestion_pacientes.listar_todos()) == 0:
            self.generar_datos_iniciales()
            self.save_to_txt()
        self.actualizar_vistas()

    def crear_interfaz(self):
        buttonbar = ttk.Frame(self, bootstyle='primary')
        buttonbar.pack(fill=X, pady=1)
        ttk.Button(buttonbar, text="➕ Nuevo Paciente", bootstyle="success-outline", command=self.nuevo_paciente).pack(side=LEFT, padx=2, pady=2)
        ttk.Button(buttonbar, text="👨‍⚕️ Nuevo Médico", bootstyle="info-outline", command=self.nuevo_medico).pack(side=LEFT, padx=2, pady=2)
        ttk.Button(buttonbar, text="💊 Farmacia", bootstyle="success-outline", command=self.farmacia).pack(side=LEFT, padx=2, pady=2)
        ttk.Button(buttonbar, text="📅 Citas Médicas", bootstyle="Warning-outline", command=self.citas_medicas).pack(side=LEFT, padx=2, pady=2)
        ttk.Button(buttonbar, text="📓 Historial Médico", bootstyle="Warning-outline", command=self.mostrar_historial).pack(side=LEFT, padx=2, pady=2)
        ttk.Button(buttonbar, text="🔄 Actualizar", bootstyle="dark-outline", command=self.actualizar_vistas).pack(side=LEFT, padx=2, pady=2)
        ttk.Button(buttonbar, text="🗑️ Eliminar", bootstyle="danger-outline", command=self.eliminar_seleccionado).pack(side=LEFT, padx=2, pady=2)
        ttk.Button(buttonbar, text="🏨 Nuevo registro", bootstyle="success-outline", command=self.nuevo_registro).pack(side=LEFT, padx=2, pady=2) 

        left_panel = ttk.Frame(self, width=300,)
        left_panel.pack(side=LEFT, fill=Y, padx=5, pady=5)
        left_panel.pack_propagate(False)

        notif_cf = CollapsingFrame(left_panel)
        notif_cf.pack(fill=X, pady=4)
        notif_frame = ttk.Labelframe(notif_cf, text="Notificaciones", bootstyle=SECONDARY)
        notif_cf.add(notif_frame, title="🔔 Notificaciones")
        self.lbl_total_notif = ttk.Label(notif_frame, text="Total Notificaciones: 0")
        self.lbl_total_notif.grid(row=0, column=0, sticky=W, pady=2, padx=5)
        # ScrolledText para mostrar notificaciones
        self.text_notif = ScrolledText(notif_frame, height=12, font=("Consolas", 9), state="disabled")
        self.text_notif.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        notif_frame.grid_rowconfigure(1, weight=1)
        notif_frame.grid_columnconfigure(0, weight=1)
        ttk.Separator(notif_frame, orient=HORIZONTAL).grid(row=3, columnspan=2, sticky=EW, pady=10, padx=5)
        ttk.Button(notif_frame, text="Limpiar", bootstyle="danger-outline", command=self.limpiar_notificaciones).grid(row=4, column=0, pady=5)
        
        
        stats_cf = CollapsingFrame(left_panel)
        stats_cf.pack(fill=X, pady=4)
        stats_frm = ttk.Labelframe(stats_cf, text="Estadísticas", bootstyle=SECONDARY)
        stats_cf.add(stats_frm, title="📊 Estadísticas")
        self.lbl_total_pacientes = ttk.Label(stats_frm, text="Total Pacientes: 0")
        self.lbl_total_pacientes.grid(row=0, column=0, sticky=W, pady=2, padx=5)
        self.lbl_total_medicos = ttk.Label(stats_frm, text="Total Médicos: 0")
        self.lbl_total_medicos.grid(row=1, column=0, sticky=W, pady=2, padx=5)
        self.lbl_pacientes_activos = ttk.Label(stats_frm, text="Pacientes Activos: 0")
        self.lbl_pacientes_activos.grid(row=2, column=0, sticky=W, pady=2, padx=5)
        ttk.Separator(stats_frm, orient=HORIZONTAL).grid(row=3, columnspan=2, sticky=EW, pady=10, padx=5)
        ttk.Button(stats_frm, text="Exportar Datos", bootstyle=LINK, command=self.exportar_datos).grid(row=5, columnspan=2, sticky=W, padx=5)

        medicos_cf = CollapsingFrame(left_panel)
        medicos_cf.pack(fill=BOTH, pady=4, expand=True)
        medicos_frm = ttk.Labelframe(medicos_cf, text="Médicos", bootstyle=SECONDARY)
        medicos_cf.add(medicos_frm, title="👨‍⚕️ Médicos Disponibles")
        self.listbox_medicos = ttk.Treeview(medicos_frm, columns=('especialidad',), 
                                            show='tree headings', height=8)
        self.listbox_medicos.heading('#0', text='Nombre')
        self.listbox_medicos.heading('especialidad', text='Especialidad')
        self.listbox_medicos.column('#0', width=150)
        self.listbox_medicos.column('especialidad', width=120)
        self.listbox_medicos.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        medicos_frm.rowconfigure(0, weight=1)  # Para que el Treeview se expanda
        medicos_frm.columnconfigure(0, weight=1)
        right_panel = ttk.Frame(self, padding=5)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=YES)

        # Pestañas para Pacientes y Búsqueda
        self.notebook = ttk.Notebook(right_panel)  # Guardamos referencia para detectar pestaña activa
        self.notebook.pack(fill=BOTH, expand=YES)

        # --- Pestaña Pacientes ---
        tab_pacientes = ttk.Frame(self.notebook)
        self.notebook.add(tab_pacientes, text="👥 Pacientes")

        # Barra de búsqueda
        search_frm = ttk.Frame(tab_pacientes)
        search_frm.pack(fill=X, pady=5)
        ttk.Label(search_frm, text="🔍 Buscar:").pack(side=LEFT, padx=5)
        self.search_entry_pac = ttk.Entry(search_frm)  # Separado por pestaña
        self.search_entry_pac.pack(side=LEFT, fill=X, expand=YES, padx=5)
        ttk.Button(search_frm, text="Buscar", bootstyle=OUTLINE, command=self.buscar_paciente).pack(side=RIGHT)

        pane = ttk.Panedwindow(tab_pacientes, orient=VERTICAL)
        pane.pack(fill=BOTH, expand=YES, padx=5, pady=5)

        top_frame = ttk.Frame(pane)
        pane.add(top_frame, weight=3)
        columns = ('id', 'nombre', 'edad', 'alergias', 'medico', 'estado')
        self.tv_pacientes = ttk.Treeview(top_frame, columns=columns, show='headings', height=12)
        for col in columns:
            self.tv_pacientes.heading(col, text=col.capitalize() if col != 'id' else 'ID')
            if col == 'id': self.tv_pacientes.column(col, width=60, anchor=CENTER)
            elif col == 'nombre': self.tv_pacientes.column(col, width=180)
            elif col == 'edad': self.tv_pacientes.column(col, width=70, anchor=CENTER)
            elif col == 'alergias': self.tv_pacientes.column(col, width=220)
            elif col == 'medico': self.tv_pacientes.column(col, width=160)
            elif col == 'estado': self.tv_pacientes.column(col, width=90, anchor=CENTER)
        self.tv_pacientes.pack(fill=BOTH, expand=YES, pady=5)

        bottom_frame = ttk.Frame(pane)
        pane.add(bottom_frame, weight=2)

        self.historial_text = ScrolledText(bottom_frame, font=("Consolas", 10), wrap="word")
        self.historial_text.pack(fill=BOTH, expand=YES, padx=5, pady=5)

        # --- Pestaña Médicos ---
        tab_medicos = ttk.Frame(self.notebook)
        self.notebook.add(tab_medicos, text="🩺 Médicos")

        # Barra de búsqueda
        search_frm2 = ttk.Frame(tab_medicos)
        search_frm2.pack(fill=X, pady=5)
        ttk.Label(search_frm2, text="🔍 Buscar:").pack(side=LEFT, padx=5)
        self.search_entry_med = ttk.Entry(search_frm2)  # Separado por pestaña
        self.search_entry_med.pack(side=LEFT, fill=X, expand=YES, padx=5)
        ttk.Button(search_frm2, text="Buscar", bootstyle=OUTLINE, command=self.buscar_medico).pack(side=RIGHT)

        # Treeview de médicos
        columns = ('id', 'nombre', 'especialidad', 'cedula', 'pacientes activos')
        self.tv_medicos = ttk.Treeview(tab_medicos, columns=columns, show='headings', height=12)
        
        self.tv_medicos.heading('id', text='ID')
        self.tv_medicos.heading('nombre', text='Nombre')
        self.tv_medicos.heading('especialidad', text='Especialidad')
        self.tv_medicos.heading('cedula', text='Cédula')
        self.tv_medicos.heading('pacientes activos', text='Pacientes Activos')

        self.tv_medicos.column('id', width=50, anchor=CENTER)
        self.tv_medicos.column('nombre', width=150)
        self.tv_medicos.column('especialidad', width=60, anchor=CENTER)
        self.tv_medicos.column('cedula', width=60, anchor=CENTER)
        self.tv_medicos.column('pacientes activos', width=200, anchor=CENTER)

        self.tv_medicos.pack(fill=BOTH, expand=YES, pady=5)


        # --- Pestaña Consultas e Historial de pacientes--- modificar
        tab_historial = ttk.Frame(self.notebook)
        self.notebook.add(tab_historial, text="📋 Consultas e Historial de pacientes")
        
        search_frm_hist = ttk.Frame(tab_historial)
        search_frm_hist.pack(fill=X, pady=5)
        ttk.Label(search_frm_hist, text="🔍 ID Paciente:").pack(side=LEFT, padx=5)
        self.search_entry_hist = ttk.Entry(search_frm_hist)
        self.search_entry_hist.pack(side=LEFT, fill=X, expand=YES, padx=5)
        ttk.Button(search_frm_hist, text="Buscar Historial", bootstyle=OUTLINE, command=self.mostrar_historial_paciente).pack(side=RIGHT)
        
        self.historial_display = ScrolledText(tab_historial, font=("Consolas", 10), wrap="word", height=20)
        self.historial_display.pack(fill=BOTH, expand=YES, padx=5, pady=5)

        log_cf = CollapsingFrame(tab_historial)
        log_cf.pack(fill=BOTH, expand=YES, pady=5)
        log_container = ttk.Frame(log_cf)
        self.log_text = ScrolledText(log_container, height=20, font=("Consolas", 9))
        self.log_text.pack(fill=BOTH, expand=YES)
        log_cf.add(log_container, title="📝 Registro de Actividades")

    def generar_datos_iniciales(self):
        # Listas hardcoded para nombres comunes españoles (pacientes y médicos)
        nombres_pacientes = [
            "Juan García", "María Fernández", "Antonio González", "Jose Rodríguez", "Carmen López",
            "Francisco Martínez", "Ana Sánchez", "Luis Pérez", "Dolores Martín", "Manuel Gómez",
            "Teresa Ruiz", "Pedro Hernández", "Isabel Jiménez", "Miguel Díaz", "Pilar Moreno",
            "Rafael Álvarez", "Concepción Muñoz", "Carlos Romero", "Rosa Alonso", "Javier Gutiérrez"
        ]
        nombres_medicos = [
            "Dr. Ana Gómez", "Dra. Sofia Martínez", "Dr. Carlos Ruiz", "Dra. Elena Sánchez",
            "Dr. Javier López", "Dra. Laura Pérez", "Dr. Miguel Fernández", "Dra. Isabel García",
            "Dr. Pedro Alonso", "Dra. Carmen Díaz"
        ]
        alergias_posibles = [[], ["Penicilina"], ["Lactosa"], ["Polen"], ["Frutos secos"], ["Mariscos"], ["Huevos"]]
        dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes"]
        especialidades_lista = list(ESPECIALIDADES_VALIDAS) 
        tipos_registro = ["Consulta", "Resultado", "Tratamiento"]
        desc_registro = ["Cardiología", "Análisis de Sangre (Normales)", "Antihipertensivos", "Chequeo general", "Vacuna", "Radiografía"]
        nombres_meds = ["Aspirina", "Paracetamol", "Ibuprofeno", "Amoxicilina", "Omeprazol", "Loratadina", "Vitamina C", "Insulina", "Atorvastatina", "Metformina"]
        tipos_meds = ["Tabletas", "Ampolletas", "Solución", "Jarabe", "Cápsulas"]
        prioridades = ["Alta", "Media", "Baja"]
        notas = ["Enfermedad grave", "Requiere cirugía de emergencia", "Visita de control", "Visita normal"]
        
        for i in range(10):
            id_p_random = f"P{random.randint(1,20):03d}"
            prioridad = random.choice(prioridades)
            nota = random.choice(notas)
            # Fecha próxima: hoy + 1-7 días
            fecha = (datetime.now() + timedelta(days=random.randint(1,7))).strftime("%Y-%m-%d")
            # Hora: 8:00 a 18:00, en intervalos de 30 min
            horas_posibles = [f"{h:02d}:{m:02d}" for h in range(8,19) for m in [0,30]]
            hora = random.choice(horas_posibles)
            especialidad = random.choice(especialidades_lista)
            self.gestion_citas.registrar_nueva(id_p_random, prioridad, nota, fecha, hora, especialidad)
            
        for i in range(20):
            id_p = f"P{i+1:03d}"
            nombre = nombres_pacientes[i]
            edad = random.randint(18, 80)
            alergias = random.choice(alergias_posibles)
            #estado = random.choice(["Activo", "Inactivo"])
            estado = "Activo" if random.random() < 0.5 else "Inactivo"
            self.gestion_pacientes.registrar_nuevo(id_p, nombre, edad, alergias, estado)
            
            # Agregar 1-3 registros de historial random
            for _ in range(random.randint(1, 3)):
                tipo = random.choice(tipos_registro)
                desc = random.choice(desc_registro)
                self.gestion_historial.agregar_nuevo_registro(id_p, tipo, desc)        
        
        pacientes_activos = []
        for i in range(1, 21):
            id_p = f"P{i:03d}"
            paciente = self.gestion_pacientes.pacientes.get(id_p)
            if paciente and paciente.estado == "Activo":
                pacientes_activos.append(id_p)
            
        # Generar 10 médicos
        for i in range(10):
            id_m = f"M{i+1:03d}"
            nombre = nombres_medicos[i]
            especialidad = random.choice(especialidades_lista)
            cedula = f"CED{random.randint(100, 999)}"
            # Horario random: 1-3 días
            horario = []
            for dia in random.sample(dias_semana, random.randint(1, 3)):
                horario.append((dia, f"{random.randint(8,10):02d}:00-{random.randint(16,18):02d}:00"))
            self.gestion_medicos.registrar_nuevo(id_m, nombre, especialidad, cedula, horario)
                    
        idx = 0
        medicos_ids = [f"M{i+1:03d}" for i in range(10)]

        for id_p in pacientes_activos:
            id_m = medicos_ids[idx % len(medicos_ids)]
            self.gestion_medicos.agregar_paciente_activo(id_m, id_p)
            idx += 1
        
        for i in range(10):
            id_med = f"MED{i+1:03d}"    
            nombre = nombres_meds[i]
            cantidad = random.randint(50, 200)
            tipo = random.choice(tipos_meds)
            self.gestion_farmacia.registrar_nuevo(id_med, nombre, cantidad, tipo)

    def actualizar_vistas(self):
        #self.lbl_total_notif.config(text="Total Notificaciones: 0")
        self.lbl_total_pacientes.config(text=f"Total Pacientes: {len(self.gestion_pacientes.pacientes)}")
        self.lbl_total_medicos.config(text=f"Total Médicos: {len(self.gestion_medicos.medicos)}")
        pacientes_activos = sum(1 for p in self.gestion_pacientes.listar_todos() if p.estado == "Activo")
        self.lbl_pacientes_activos.config(text=f"Pacientes Activos: {pacientes_activos}")

        # Treeview pacientes
        self.tv_pacientes.delete(*self.tv_pacientes.get_children())
        for p in self.gestion_pacientes.listar_todos():
            alergias_str = ", ".join(str(a) for a in p.alergias)
            # Médico asignado: Buscar si está en algún médico (simple iteración)
            medico_asignado = "N/A"
            for m in self.gestion_medicos.listar_todos():
                if p.id_paciente in m.pacientes_activos:
                    medico_asignado = m.nombre
                    break
            self.tv_pacientes.insert("", "end", values=(p.id_paciente, p.nombre, p.edad, alergias_str, medico_asignado, p.estado))

        # Treeview médicos
        self.tv_medicos.delete(*self.tv_medicos.get_children())
        for m in self.gestion_medicos.listar_todos():
            pacientes_str = len(m.pacientes_activos)
            self.tv_medicos.insert("", "end", values=(m.id_medico, m.nombre, m.especialidad, m.cedula, pacientes_str))

        # Listbox médicos (panel izquierdo)
        self.listbox_medicos.delete(*self.listbox_medicos.get_children())
        for m in self.gestion_medicos.listar_todos():
            iid = self.listbox_medicos.insert("", "end", text=m.nombre)
            self.listbox_medicos.set(iid, "especialidad", m.especialidad)

        if self.notebook.select() == str(self.notebook.tabs()[2]):  # Asumiendo que tab_historial es la tercera pestaña (índice 2)
            self.mostrar_historial_paciente()
        
        self.actualizar_notificaciones()
        # Log (agrega mensaje)
        self.log_text.insert("end", f"Vistas actualizadas a las {datetime.now().strftime('%H:%M:%S')}.\n")

    def nuevo_paciente(self):
        modal = Toplevel(self)
        modal.title("Nuevo Paciente")
        modal.geometry("520x520")
        modal.resizable(False, False)

        # Campos
        ttk.Label(modal, text="ID del Paciente:", font=("Helvetica", 10, "bold")).pack(pady=(15,5), anchor="w", padx=30)
        id_entry = ttk.Entry(modal, width=35)
        id_entry.pack(pady=5)

        ttk.Label(modal, text="Nombre Completo:", font=("Helvetica", 10, "bold")).pack(pady=(10,5), anchor="w", padx=30)
        nombre_entry = ttk.Entry(modal, width=35)
        nombre_entry.pack(pady=5)

        ttk.Label(modal, text="Edad:", font=("Helvetica", 10, "bold")).pack(pady=(10,5), anchor="w", padx=30)
        edad_entry = ttk.Entry(modal, width=35)
        edad_entry.pack(pady=5)

        ttk.Label(modal, text="Alergias (separadas por coma):", font=("Helvetica", 10, "bold")).pack(pady=(10,5), anchor="w", padx=30)
        alergias_entry = ttk.Entry(modal, width=35)
        alergias_entry.pack(pady=5)

        ttk.Label(modal, text="Estado:", font=("Helvetica", 10, "bold")).pack(pady=(10,5), anchor="w", padx=30)
        estado_combo = ttk.Combobox(modal, values=["Activo", "Inactivo"], state="readonly", width=32)
        estado_combo.set("Activo")
        estado_combo.pack(pady=5)

        def guardar_paciente():
            id_p = id_entry.get().strip()
            nombre = nombre_entry.get().strip()
            edad_str = edad_entry.get().strip()

            if not id_p:
                Messagebox.show_error("El ID es obligatorio.", title="Campo requerido")
                return
            if not nombre:
                Messagebox.show_error("El nombre es obligatorio.", title="Campo requerido")
                return
            if not edad_str:
                Messagebox.show_error("La edad es obligatoria.", title="Campo requerido")
                return
            if not edad_str.isdigit():
                Messagebox.show_error("La edad debe ser un número.", title="Formato inválido")
                return

            alergias = [a.strip() for a in alergias_entry.get().split(",") if a.strip()]
            estado = estado_combo.get()

            try:
                self.gestion_pacientes.registrar_nuevo(id_p, nombre, int(edad_str), alergias, estado)
                self.notificar(f"Nuevo paciente registrado: {nombre}")
                Messagebox.show_info("Paciente registrado correctamente.", title="Éxito")
                modal.destroy()
                self.actualizar_vistas()
            except ValueError as e:
                Messagebox.show_error(f"Error: {e}", title="Error de registro")

        ttk.Button(modal, text="Registrar Paciente", bootstyle=SUCCESS, command=guardar_paciente).pack(pady=20)

    def nuevo_medico(self):
        modal = Toplevel(self)
        modal.title("Nuevo Médico")
        modal.geometry("550x520")
        modal.resizable(False, False)
        
        especialidades_lista = list(ESPECIALIDADES_VALIDAS)  

        ttk.Label(modal, text="ID del Médico:", font=("Helvetica", 10, "bold")).pack(pady=(15,5), anchor="w", padx=30)
        id_entry = ttk.Entry(modal, width=35)
        id_entry.pack(pady=5)

        ttk.Label(modal, text="Nombre Completo:", font=("Helvetica", 10, "bold")).pack(pady=(10,5), anchor="w", padx=30)
        nombre_entry = ttk.Entry(modal, width=35)
        nombre_entry.pack(pady=5)

        ttk.Label(modal, text="Especialidad:", font=("Helvetica", 10, "bold")).pack(pady=(10,5), anchor="w", padx=40)
        esp_combo = ttk.Combobox(modal, values=especialidades_lista, state="readonly", width=37)
        esp_combo.pack(pady=5)
        esp_combo.set("Medicina interna")

        ttk.Label(modal, text="Cédula:", font=("Helvetica", 10, "bold")).pack(pady=(10,5), anchor="w", padx=30)
        cedula_entry = ttk.Entry(modal, width=35)
        cedula_entry.pack(pady=5)

        ttk.Label(modal, text="Horario (opcional - ej: lunes:09:00-17:00,martes:10:00-18:00):", font=("Helvetica", 10, "bold")).pack(pady=(10,5) ,anchor="w", padx=30)
        horario_entry = ttk.Entry(modal, width=35)
        horario_entry.pack(pady=5)

        def guardar_medico():
            id_m = id_entry.get().strip()
            nombre = nombre_entry.get().strip()
            especialidad = esp_combo.get().strip()
            cedula = cedula_entry.get().strip()
            texto_horario = horario_entry.get().strip()

            if not all([id_m, nombre, especialidad, cedula]):
                Messagebox.show_error("Todos los campos son obligatorios (excepto horario).", title="Error")
                return

            horario = []
            if texto_horario:
                try:
                    pares = texto_horario.split(",")
                    for par in pares:
                        par = par.strip()
                        if not par: 
                            continue
                        if ":" not in par:
                            raise ValueError("Falta ':'")
                        dia, hora = par.split(":", 1)  # split solo en el primer ':'
                        dia = dia.strip().lower().capitalize()  # lunes → Lunes
                        hora = hora.strip()
                        horario.append((dia, hora))
                except Exception as e:
                    Messagebox.show_error(
                        "Formato de horario inválido.\n"
                        "Usa: lunes:09:00-17:00, martes:10:00-18:00",
                        title="Error de formato"
                    )
                    return

            if self.gestion_medicos.registrar_nuevo(id_m, nombre, especialidad, cedula, horario):
                self.notificar(f"Nuevo médico registrado: {nombre}")
                Messagebox.show_info("Médico registrado correctamente.", title="Éxito")
                modal.destroy()
                self.actualizar_vistas()
            else:
                Messagebox.show_error("ID duplicado o especialidad no válida.", title="Error")
            

        ttk.Button(modal, text="Registrar Médico", bootstyle=INFO, command=guardar_medico).pack(pady=20)

    def eliminar_seleccionado(self):
        tab_id = self.notebook.select()
        tab_name = self.notebook.tab(tab_id, "text")
        
        if "Pacientes" in tab_name:
            selected = self.tv_pacientes.selection()
            if selected:
                id_p = self.tv_pacientes.item(selected[0])['values'][0]
                try:
                    self.gestion_pacientes.eliminar_paciente(id_p)
                    self.notificar(f"Paciente eliminado: ID {id_p}")
                    Messagebox.ok("Paciente eliminado.")
                    self.actualizar_vistas()
                except ValueError as e:
                    Messagebox.show_error(str(e))
        elif "Médicos" in tab_name:
            selected = self.tv_medicos.selection()
            if selected:
                id_m = self.tv_medicos.item(selected[0])['values'][0]
                if self.gestion_medicos.eliminar_medico(id_m):
                    self.notificar(f"Médico eliminado: ID {id_m}")
                    Messagebox.ok("Médico eliminado.")
                    self.actualizar_vistas()
                else:
                    Messagebox.show_error("No se puede eliminar (no existe o tiene pacientes activos).")
        else:
            Messagebox.show_error("Seleccione una pestaña válida.")

    def buscar_paciente(self):
        termino = self.search_entry_pac.get().strip()
        if not termino:
            self.actualizar_vistas()
            return

        resultados = []
        termino_lower = termino.lower()
        is_numeric = termino.isdigit()

        for paciente in self.gestion_pacientes.listar_todos():
            coincidencia = False

            # 1. Búsqueda por ID (exacta o parcial, siempre, independientemente de numeric)
            id_lower = str(paciente.id_paciente).lower()
            if termino_lower == id_lower or termino_lower in id_lower:
                coincidencia = True

            # 2. Búsqueda por nombre (palabra por palabra, priorizando startswith, luego fuzzy estricto)
            if not coincidencia:
                nombre_lower = paciente.nombre.lower()
                palabras_nombre = nombre_lower.split()
                
                for palabra in palabras_nombre:
                    if palabra.startswith(termino_lower):
                        coincidencia = True
                        break
                    
                    # Fuzzy más estricto: <=1 para short, <=2 para long
                    dist = Cadenas.levenshtein(termino_lower, palabra)
                    max_dist = 1 if len(termino_lower) <= 4 else 2
                    if dist <= max_dist:
                        coincidencia = True
                        break
                
                # Substring en nombre completo como fallback
                if not coincidencia and Cadenas.kmp(nombre_lower, termino_lower) != -1:
                    coincidencia = True

            # 3. Búsqueda por edad (solo si numeric)
            if not coincidencia and is_numeric:
                if str(paciente.edad) == termino:
                    coincidencia = True

            # 4. Búsqueda por estado o alergias
            if not coincidencia:
                estado_lower = paciente.estado.lower()
                alergias_str = " ".join(str(a).lower() for a in paciente.alergias)
                
                if termino_lower in estado_lower or Cadenas.kmp(alergias_str, termino_lower) != -1:
                    coincidencia = True

            if coincidencia:
                resultados.append(paciente)

        # Actualizar tabla
        self.tv_pacientes.delete(*self.tv_pacientes.get_children())
        for p in resultados:
            alergias_str = ", ".join(str(a) for a in p.alergias)
            medico_asignado = "N/A"
            for m in self.gestion_medicos.listar_todos():
                if p.id_paciente in m.pacientes_activos:
                    medico_asignado = m.nombre
                    break
            self.tv_pacientes.insert("", "end", values=(
                p.id_paciente, p.nombre, p.edad, alergias_str, medico_asignado, p.estado
            ))

        if not resultados:
            self.tv_pacientes.insert("", "end", values=("Sin resultados", "", "", "", "", ""))

    def buscar_medico(self):
        termino = self.search_entry_med.get().strip()
        if not termino:
            self.actualizar_vistas()
            return

        resultados = []
        termino_lower = termino.lower()
        is_numeric = termino.isdigit()

        for medico in self.gestion_medicos.listar_todos():
            coincidencia = False

            # 1. Búsqueda por ID (exacta o parcial, siempre)
            id_lower = str(medico.id_medico).lower()
            if termino_lower == id_lower or termino_lower in id_lower:
                coincidencia = True

            # 2. Búsqueda por nombre (palabra por palabra, startswith + fuzzy estricto)
            if not coincidencia:
                nombre_lower = medico.nombre.lower()
                palabras_nombre = nombre_lower.split()
                
                for palabra in palabras_nombre:
                    if palabra.startswith(termino_lower):
                        coincidencia = True
                        break
                    
                    dist = Cadenas.levenshtein(termino_lower, palabra)
                    max_dist = 1 if len(termino_lower) <= 4 else 2
                    if dist <= max_dist:
                        coincidencia = True
                        break
                
                if not coincidencia and Cadenas.kmp(nombre_lower, termino_lower) != -1:
                    coincidencia = True

            # 3. Búsqueda por especialidad
            if not coincidencia:
                especialidad_lower = medico.especialidad.lower()
                if termino_lower in especialidad_lower or Cadenas.kmp(especialidad_lower, termino_lower) != -1:
                    coincidencia = True

            # 4. Búsqueda por cédula (parcial si numeric)
            if not coincidencia:
                cedula_lower = str(medico.cedula).lower()
                if termino_lower == cedula_lower or termino_lower in cedula_lower:
                    coincidencia = True

            if coincidencia:
                resultados.append(medico)

        # Actualizar tabla
        self.tv_medicos.delete(*self.tv_medicos.get_children())
        for m in resultados:
            pacientes_str = len(m.pacientes_activos)
            self.tv_medicos.insert("", "end", values=(
                m.id_medico, m.nombre, m.especialidad, m.cedula, pacientes_str
            ))

        if not resultados:
            self.tv_medicos.insert("", "end", values=("Sin resultados", "", "", "", ""))

    def farmacia(self):
        modal = Toplevel(self)
        modal.title("💊 Módulo de Farmacia")
        modal.geometry("800x700")
        modal.resizable(False, False)

        # Notebook para pestañas
        notebook = ttk.Notebook(modal)
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Pestaña 1: Mostrar Inventario
        tab_inventario = ttk.Frame(notebook)
        notebook.add(tab_inventario, text="📦 Inventario")

        columns = ('id', 'nombre', 'cantidad', 'tipo')  # Añadido 'tipo'
        tv_inventario = ttk.Treeview(tab_inventario, columns=columns, show='headings', height=15)
        tv_inventario.heading('id', text='ID')
        tv_inventario.heading('nombre', text='Nombre')
        tv_inventario.heading('cantidad', text='Cantidad')
        tv_inventario.heading('tipo', text='Tipo')
        tv_inventario.column('id', width=100)
        tv_inventario.column('nombre', width=200)
        tv_inventario.column('cantidad', width=100, anchor=CENTER)
        tv_inventario.column('tipo', width=150)
        tv_inventario.pack(fill=BOTH, expand=YES, pady=5)

        def actualizar_inventario():
            tv_inventario.delete(*tv_inventario.get_children())
            for med in self.gestion_farmacia.listar_todos():
                tv_inventario.insert("", "end", values=(med.id_medicamento, med.nombre, med.cantidad, med.tipo))

        # Nuevo botón: Eliminar inventario (elimina medicamento seleccionado)
        def eliminar_inventario():
            selected = tv_inventario.selection()
            if selected:
                id_med = tv_inventario.item(selected[0])['values'][0]
                if self.gestion_farmacia.eliminar_medicamento(id_med):
                    self.notificar(f"Medicamento eliminado: ID {id_med}")
                    Messagebox.show_info("Medicamento eliminado.")
                    actualizar_inventario()
                else:
                    Messagebox.show_error("No encontrado.")
                
        ttk.Button(tab_inventario, text="Actualizar Inventario", bootstyle=INFO, command=actualizar_inventario).pack(side=LEFT, pady=10)
        ttk.Button(tab_inventario, text="Eliminar Seleccionado", bootstyle=DANGER, command=eliminar_inventario).pack(side=LEFT, pady=10, padx=10)
        actualizar_inventario()  # Inicial

        # Pestaña 2: Buscar Medicamento
        tab_buscar = ttk.Frame(notebook)
        notebook.add(tab_buscar, text="🔍 Buscar")

        search_frm = ttk.Frame(tab_buscar)
        search_frm.pack(fill=X, pady=5)
        ttk.Label(search_frm, text="Buscar por ID o Nombre:").pack(side=LEFT, padx=5)
        search_entry = ttk.Entry(search_frm)
        search_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)

        def buscar_med():
            termino = search_entry.get().strip().upper()  # Upper para IDs (case-insensitive)
            if not termino:
                return
            resultados = []
            # Búsqueda por ID (exacta o parcial, case-insensitive)
            for _, med in self.gestion_farmacia.inventario:
                if termino in med.id_medicamento.upper():
                    resultados.append(med)
            if not resultados:
                # Si no es ID, buscar por nombre
                resultados = self.gestion_farmacia.buscar_por_nombre(termino.lower())  # Lower para nombres
            
            tv_buscar.delete(*tv_buscar.get_children())
            for med in resultados:
                tv_buscar.insert("", "end", values=(med.id_medicamento, med.nombre, med.cantidad, med.tipo))
            if not resultados:
                tv_buscar.insert("", "end", values=("Sin resultados", "", "", ""))

        ttk.Button(search_frm, text="Buscar", bootstyle=OUTLINE, command=buscar_med).pack(side=RIGHT)

        tv_buscar = ttk.Treeview(tab_buscar, columns=columns, show='headings', height=15)
        tv_buscar.heading('id', text='ID')
        tv_buscar.heading('nombre', text='Nombre')
        tv_buscar.heading('cantidad', text='Cantidad')
        tv_buscar.heading('tipo', text='Tipo')
        tv_buscar.column('id', width=100)
        tv_buscar.column('nombre', width=200)
        tv_buscar.column('cantidad', width=100, anchor=CENTER)
        tv_buscar.column('tipo', width=150)
        tv_buscar.pack(fill=BOTH, expand=YES, pady=5)

        # Pestaña 3: Registrar Nuevo
        tab_registrar = ttk.Frame(notebook)
        notebook.add(tab_registrar, text="➕ Registrar Nuevo")

        ttk.Label(tab_registrar, text="ID Medicamento:").pack(pady=5)
        id_entry = ttk.Entry(tab_registrar)
        id_entry.pack()

        ttk.Label(tab_registrar, text="Nombre:").pack(pady=5)
        nombre_entry = ttk.Entry(tab_registrar)
        nombre_entry.pack()

        ttk.Label(tab_registrar, text="Cantidad Inicial:").pack(pady=5)
        cantidad_entry = ttk.Entry(tab_registrar)
        cantidad_entry.pack()

        ttk.Label(tab_registrar, text="Tipo:").pack(pady=5)  # Nuevo campo para tipo
        tipo_combo = ttk.Combobox(tab_registrar, values=["Tabletas", "Ampolletas", "Solución", "Jarabe", "Cápsulas"], state="readonly")
        tipo_combo.set("Tabletas")
        tipo_combo.pack()

        def guardar_med():
            id_med = id_entry.get().strip().upper()
            nombre = nombre_entry.get().strip()
            cantidad_str = cantidad_entry.get().strip()
            tipo = tipo_combo.get()
            if not all([id_med, nombre, cantidad_str.isdigit(), tipo]):
                Messagebox.show_error("Campos inválidos.")
                return
            if self.gestion_farmacia.registrar_nuevo(id_med, nombre, int(cantidad_str), tipo):
                self.notificar(f"Nuevo medicamento agregado: {nombre} ({cantidad_str} unidades)")
                Messagebox.show_info("Registrado correctamente.")
                actualizar_inventario()  # Actualiza la otra pestaña si abierta
            else:
                Messagebox.show_error("Duplicado.")

        ttk.Button(tab_registrar, text="Registrar", bootstyle=SUCCESS, command=guardar_med).pack(pady=20)

        # Pestaña 4: Surtir Receta
        tab_surtir = ttk.Frame(notebook)
        notebook.add(tab_surtir, text="📝 Surtir Receta")

        ttk.Label(tab_surtir, text="Cédula del Médico:").pack(pady=5)
        cedula_entry = ttk.Entry(tab_surtir)
        cedula_entry.pack()

        cesta = DoublyLinkedList()

        ttk.Label(tab_surtir, text="ID Medicamento:").pack(pady=5)
        id_med_entry = ttk.Entry(tab_surtir)
        id_med_entry.pack()

        ttk.Label(tab_surtir, text="Cantidad:").pack(pady=5)
        cant_entry = ttk.Entry(tab_surtir)
        cant_entry.pack()
        
        tv_cesta = ttk.Treeview(tab_surtir, columns=('id', 'cantidad', 'nombre'), show='headings', height=5)
        tv_cesta.heading('id', text='ID')
        tv_cesta.heading('cantidad', text='Cantidad')
        tv_cesta.heading('nombre', text='Nombre')
        tv_cesta.pack(fill=X, pady=5)        

        def agregar_a_cesta():
            id_med = id_med_entry.get().strip().upper()
            cant_str = cant_entry.get().strip()
            if not cant_str.isdigit():
                Messagebox.show_error("Cantidad inválida.")
                return
            cant = int(cant_str)
            med = self.gestion_farmacia.buscar_por_id(id_med)
            if med and med.cantidad >= cant:
                cesta.append((id_med, med.nombre, cant))  # id, nombre, cant (int)
                actualizar_cesta()
            else:
                Messagebox.show_error("No disponible o insuficiente.")

        ttk.Button(tab_surtir, text="Agregar a Receta", bootstyle=INFO, command=agregar_a_cesta).pack(pady=10)

        def actualizar_cesta():
            tv_cesta.delete(*tv_cesta.get_children())
            for item in cesta:
                id_med, nombre, cant = item
                tv_cesta.insert("", "end", values=(id_med, nombre, str(cant)))

        # Nuevo botón: Eliminar item seleccionado del carrito
        def eliminar_de_cesta():
            selected = tv_cesta.selection()
            if selected:
                values = tv_cesta.item(selected[0])['values']
                if len(values) != 3:
                    Messagebox.show_error("Error en selección.")
                    return
                id_med = values[0]
                nombre = values[1]
                try:
                    cant = int(values[2])  # Cast from str
                except ValueError:
                    Messagebox.show_error("Error en cantidad: no es numérica.")
                    return
                try:
                    cesta.remove(value=(id_med, nombre, cant))
                    actualizar_cesta()
                    Messagebox.show_info("Item eliminado del carrito.")
                except ValueError:
                    Messagebox.show_error("No encontrado.")

        ttk.Button(tab_surtir, text="Eliminar Seleccionado", bootstyle=DANGER, command=eliminar_de_cesta).pack(pady=5)

        def surtir_receta():
            if cesta.is_empty():
                Messagebox.show_error("Carrito vacío. Agregue medicamentos antes de surtir.")
                return
            cedula = cedula_entry.get().strip().upper()
            medico_encontrado = False
            for m in self.gestion_medicos.listar_todos():
                if str(m.cedula).upper() == cedula:
                    medico_encontrado = True
                    break
            if not medico_encontrado:
                Messagebox.show_error("Cédula no válida. Verifica el formato (ej: CED123).")
                return
            # Opcional: Mensaje de confirmación con lista de medicamentos
            meds_lista = "\n".join(f"- {nombre} (x{cant})" for id_med, nombre, cant in cesta)
            confirm = Messagebox.yesno(f"¿Surtir los siguientes medicamentos?\n{meds_lista}", title="Confirmar Receta")
            if confirm == "No":
                return
            for item in cesta:
                id_med, nombre, cant = item
                self.gestion_farmacia.actualizar_cantidad(id_med, -int(cant))
            cesta.clear()
            actualizar_cesta()
            actualizar_inventario()
            self.notificar("Receta surtida, inventario de farmacia actualizado.")
            Messagebox.show_info("Receta surtida correctamente.")
            

        ttk.Button(tab_surtir, text="Surtir Receta", bootstyle=SUCCESS, command=surtir_receta).pack(pady=10)

        # Botón Salir
        ttk.Button(modal, text="Salir", bootstyle=DANGER, command=modal.destroy).pack(pady=10)

    def mostrar_historial(self):
        selected = self.tv_pacientes.selection()
        if not selected:
            self.historial_text.delete(1.0, "end")
            self.historial_text.insert("end", "Seleccione un paciente para ver su historial.")
            return
        
        id_p = self.tv_pacientes.item(selected[0])['values'][0]
        historial =self.gestion_historial.ver_historial(id_p, formateado=True)
        self.historial_text.delete(1.0, "end")
        self.historial_text.insert("end", historial or "Este paciente no tiene historial aún.")

    def mostrar_historial_paciente(self):
        id_pac = self.search_entry_hist.get().strip()
        self.historial_display.delete(1.0, "end")
        if id_pac:
        # Búsqueda por ID: solo un paciente
            paciente = self.gestion_pacientes.buscar_por_id(id_pac)
            if not paciente:
                Messagebox.show_error("Paciente no encontrado.")
                return
            pacientes = [paciente]
        else:
            # Todos los pacientes
            pacientes = self.gestion_pacientes.listar_todos()
            if not pacientes:
                self.historial_display.insert("end", "No hay pacientes registrados.\n")
                return
            
        # Obtener historial como DoublyLinkedList (ya es Deque-like)
        for paciente in pacientes:    
            historial = paciente.historial  # DoublyLinkedList
        
            if historial.is_empty():
                continue
        
            # Mostrar en formato ASCII bonito, últimas primero (recorre desde tail)
            output = f"\n Paciente ID: {paciente.id_paciente} | Nombre: {paciente.nombre} \n \n Historial de Visitas (últimas primero):\n\n"
            
            # Recorrer desde el final (última visita primero)
            current = historial._DoublyLinkedList__tail  # Acceso a tail
            is_first = True
            while current:
                reg = current.get_data()
                diag = reg.descripcion.split('\n')[0] if '\n' in reg.descripcion else reg.descripcion  # Simplificado, ajusta si necesitas
                if reg.descripcion:
                    desc_lines = reg.descripcion.split('\n')
                    for line in desc_lines:
                        if line.strip().startswith("Resultado:"):
                            diag = line.split(":", 1)[1].strip()
                            break
                label = "Última Visita" if is_first else "Visita Previa"
                output += f"Deque - Historial \n {label}: {reg.fecha} - Diagnóstico: {diag}\n\n"
                is_first = False
                current = current.get_prev()
            
            output += "\n\n"
            
            self.historial_display.insert("end", output)
    
    def citas_medicas(self):
        modal = Toplevel(self)
        modal.title("📅 Módulo de Citas Médicas")
        modal.geometry("800x600")
        modal.resizable(True, True)

        # Notebook para pestañas
        notebook = ttk.Notebook(modal)
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Pestaña 1: Programar Nueva Cita
        tab_nueva = ttk.Frame(notebook)
        notebook.add(tab_nueva, text="➕ Nueva Cita")

        ttk.Label(tab_nueva, text="ID Paciente:").pack(pady=5)
        id_pac_entry = ttk.Entry(tab_nueva)
        id_pac_entry.pack()

        ttk.Label(tab_nueva, text="Prioridad:").pack(pady=5)
        prioridad_combo = ttk.Combobox(tab_nueva, values=["Alta", "Media", "Baja"], state="readonly")
        prioridad_combo.set("Baja")
        prioridad_combo.pack()

        ttk.Label(tab_nueva, text="Nota de Control:").pack(pady=5)
        nota_combo = ttk.Combobox(tab_nueva, values=["Enfermedad grave", "Requiere cirugía de emergencia", "Visita de control", "Visita normal"], state="readonly")
        nota_combo.set("Visita normal")
        nota_combo.pack()

        # Días: Próximos 30 días
        dias_posibles = [(datetime.now() + timedelta(days=d)).strftime("%Y-%m-%d") for d in range(1,31)]
        ttk.Label(tab_nueva, text="Fecha:").pack(pady=5)
        fecha_combo = ttk.Combobox(tab_nueva, values=dias_posibles, state="readonly")
        fecha_combo.set(dias_posibles[0])
        fecha_combo.pack()

        # Horas: 00:00 a 23:30, intervalos de 30 min
        horas_posibles = [f"{h:02d}:{m:02d}" for h in range(24) for m in [0,30]]
        ttk.Label(tab_nueva, text="Hora:").pack(pady=5)
        hora_combo = ttk.Combobox(tab_nueva, values=horas_posibles, state="readonly")
        hora_combo.set("08:00")
        hora_combo.pack()

        ttk.Label(tab_nueva, text="Especialidad:").pack(pady=5)
        esp_combo = ttk.Combobox(tab_nueva, values=list(ESPECIALIDADES_VALIDAS), state="readonly")
        esp_combo.set("Medicina interna")
        esp_combo.pack()

        def programar_cita():
            id_pac = id_pac_entry.get().strip()
            prioridad = prioridad_combo.get()
            nota = nota_combo.get()
            fecha = fecha_combo.get()
            hora = hora_combo.get()
            especialidad = esp_combo.get()
            if not id_pac:
                Messagebox.show_error("ID Paciente requerido.")
                return
            exito, msg = self.gestion_citas.registrar_nueva(id_pac, prioridad, nota, fecha, hora, especialidad)
            if exito:
                pac_nombre = self.gestion_pacientes.buscar_por_id(id_pac).nombre
                self.notificar(f"Nueva cita programada para {pac_nombre} - {fecha}/{hora}")
                Messagebox.show_info(f"Cita programada: ID {msg}")
            else:
                Messagebox.show_error(msg)

        ttk.Button(tab_nueva, text="Programar Cita", bootstyle=SUCCESS, command=programar_cita).pack(pady=20)

        # Pestaña 2: Ver Lista de Citas
        tab_lista = ttk.Frame(notebook)
        notebook.add(tab_lista, text="📋 Lista de Citas")

        columns = ('id', 'paciente', 'prioridad', 'nota', 'fecha_hora', 'especialidad')
        tv_citas = ttk.Treeview(tab_lista, columns=columns, show='headings', height=15)
        tv_citas.heading('id', text='ID')
        tv_citas.heading('paciente', text='Paciente')
        tv_citas.heading('prioridad', text='Prioridad')
        tv_citas.heading('nota', text='Nota')
        tv_citas.heading('fecha_hora', text='Fecha/Hora')
        tv_citas.heading('especialidad', text='Especialidad')
        tv_citas.pack(fill=BOTH, expand=YES, pady=5)

        def actualizar_lista():
            tv_citas.delete(*tv_citas.get_children())
            for cita in self.gestion_citas.listar_todas():
                paciente = self.gestion_pacientes.buscar_por_id(cita.id_paciente)
                pac_nombre = paciente.nombre if paciente else "Desconocido"
                tv_citas.insert("", "end", values=(cita.id_cita, pac_nombre, cita.prioridad, cita.nota, f"{cita.fecha} {cita.hora}", cita.especialidad))

        def cancelar_seleccionada():
            selected = tv_citas.selection()
            if selected:
                id_cita = tv_citas.item(selected[0])['values'][0]
                if self.gestion_citas.cancelar_cita(id_cita):
                    Messagebox.show_info("Cita cancelada.")
                    actualizar_lista()

        def modificar_seleccionada():
            selected = tv_citas.selection()
            if selected:
                id_cita = tv_citas.item(selected[0])['values'][0]
                # Para modificar, abre un modal simple (ejemplo: cambiar fecha)
                mod_modal = Toplevel(modal)
                mod_modal.title("Modificar Cita")
                ttk.Label(mod_modal, text="Nueva Fecha:").pack()
                new_fecha = ttk.Entry(mod_modal)
                new_fecha.pack()
                ttk.Label(mod_modal, text="Nueva Hora:").pack()
                new_hora = ttk.Entry(mod_modal)
                new_hora.pack()
                def guardar_mod():
                    if self.gestion_citas.modificar_cita(id_cita, fecha=new_fecha.get(), hora=new_hora.get()):
                        Messagebox.show_info("Cita modificada.")
                        mod_modal.destroy()
                        actualizar_lista()
                ttk.Button(mod_modal, text="Guardar", command=guardar_mod).pack()

        ttk.Button(tab_lista, text="Actualizar Lista", bootstyle=INFO, command=actualizar_lista).pack(side=LEFT, pady=10)
        ttk.Button(tab_lista, text="Cancelar Seleccionada", bootstyle=DANGER, command=cancelar_seleccionada).pack(side=LEFT, pady=10, padx=10)
        ttk.Button(tab_lista, text="Modificar Seleccionada", bootstyle=WARNING, command=modificar_seleccionada).pack(side=LEFT, pady=10, padx=10)
        actualizar_lista()  # Inicial

        # Pestaña 3: Priorizar Urgentes
        tab_urgentes = ttk.Frame(notebook)
        notebook.add(tab_urgentes, text="🚑 Urgentes")

        urg_text = ScrolledText(tab_urgentes, height=20, font=("Consolas", 10))
        urg_text.pack(fill=BOTH, expand=YES, pady=5)

        def mostrar_urgentes():
            urg_text.delete(1.0, "end")
            cola = self.gestion_citas.get_cola_urgentes()
            
            urg_text.insert("end", " Cola de Prioridad - Citas Urgentes\n")
            urg_text.insert("end", "──────────────────────────────────────────────\n")
            
            if cola.is_empty():
                urg_text.insert("end", "   (No hay citas urgentes pendientes)\n")
                return
            
            i = 1
            while not cola.is_empty():
                cita = cola.dequeue()
                paciente = self.gestion_pacientes.buscar_por_id(cita.id_paciente)
                pac_nombre = paciente.nombre if paciente else "Desconocido"
                linea = f"   {i}. {pac_nombre} - Prioridad: {cita.prioridad} ({cita.nota})\n"
                urg_text.insert("end", linea)
                i += 1

        ttk.Button(tab_urgentes, text="Actualizar Cola", bootstyle=INFO, command=mostrar_urgentes).pack(pady=10)
        mostrar_urgentes()  # Inicial

        # Botón Salir
        ttk.Button(modal, text="Salir", bootstyle=DANGER, command=modal.destroy).pack(pady=10)
    
    def actualizar_notificaciones(self):
            self.lbl_total_notif.config(text=f"Total Notificaciones: {self.gestion_notificaciones.contar()}")
            self.text_notif.config(state="normal")
            self.text_notif.delete(1.0, "end")
            for notif in self.gestion_notificaciones.obtener_todas():
                self.text_notif.insert("end", str(notif) + "\n")
            self.text_notif.config(state="disabled")
            self.text_notif.see("end")

    def limpiar_notificaciones(self):
        self.gestion_notificaciones.limpiar()
        self.actualizar_notificaciones()

    def notificar(self, mensaje):
        self.gestion_notificaciones.agregar(mensaje)
        self.actualizar_notificaciones()
    
    def nuevo_registro(self):
        modal = Toplevel(self)
        modal.title("Agregar Nuevo Registro Médico")
        modal.geometry("600x600")

        # Seleccionar Paciente
        ttk.Label(modal, text="Seleccionar Paciente:").pack(pady=5)
        pacientes = self.gestion_pacientes.listar_todos()
        pac_values = [f"{p.id_paciente} - {p.nombre}" for p in pacientes]
        pac_combo = ttk.Combobox(modal, values=pac_values, state="readonly")
        pac_combo.pack(pady=5)

        # Fecha de Consulta
        ttk.Label(modal, text="Fecha de Consulta (DD/MM/YYYY):").pack(pady=5)
        fecha_entry = ttk.Entry(modal)
        fecha_entry.pack(pady=5)

        # Especialidad
        ttk.Label(modal, text="Especialidad:").pack(pady=5)
        esp_combo = ttk.Combobox(modal, values=list(ESPECIALIDADES_VALIDAS), state="readonly")
        esp_combo.pack(pady=5)

        # Resultado
        ttk.Label(modal, text="Resultado:").pack(pady=5)
        resultado_entry = ttk.Entry(modal)
        resultado_entry.pack(pady=5)

        # Tratamiento Actual
        ttk.Label(modal, text="Tratamiento Actual:").pack(pady=5)
        tratamiento_entry = ttk.Entry(modal)
        tratamiento_entry.pack(pady=5)

        def guardar_registro():
            selected_pac = pac_combo.get()
            if not selected_pac:
                Messagebox.show_error("Seleccione un paciente.")
                return
            id_paciente = selected_pac.split(" - ")[0]
            fecha = fecha_entry.get().strip()
            especialidad = esp_combo.get()
            resultado = resultado_entry.get().strip()
            tratamiento = tratamiento_entry.get().strip()

            if not all([fecha, especialidad, resultado, tratamiento]):
                Messagebox.show_error("Todos los campos son requeridos.")
                return

            # Formatear descripción
            descripcion = f"Especialidad: {especialidad}\nResultado: {resultado}\nTratamiento: {tratamiento}"

            # Agregar registro
            registro = RegistroMedico(fecha=fecha, tipo="Consulta", descripcion=descripcion)
            try:
                self.gestion_pacientes.agregar_registro_medico(id_paciente, registro)
                self.notificar(f"Nuevo registro agregado para paciente {id_paciente}")
                Messagebox.show_info("Registro agregado exitosamente.")
                modal.destroy()
                self.actualizar_vistas()
            except ValueError as e:
                Messagebox.show_error(str(e))

        ttk.Button(modal, text="Guardar", bootstyle=SUCCESS, command=guardar_registro).pack(pady=20)
        ttk.Button(modal, text="Cancelar", bootstyle=DANGER, command=modal.destroy).pack(pady=5)

    
    def load_from_txt(self):
        print("--- Iniciando carga de datos ---")
        def procesar_linea_entidad(linea, inicio_etiqueta):
            idx = Cadenas.find(linea, inicio_etiqueta)
            if idx == -1: return None
            
            raw = linea[idx + len(inicio_etiqueta):]
            raw = raw.strip()
            if raw.endswith(")"): raw = raw[:-1]
            
            chars = []
            depth = 0
            i = 0
            while i < len(raw):
                c = raw[i]
                if c == '{': depth += 1
                elif c == '}': depth -= 1
                
                if c == ',' and depth > 0: chars.append('|')
                else: chars.append(c)
                i += 1
            
            contenido_sano = "".join(chars)
            try: campos_raw = Cadenas.parse_campos(contenido_sano)
            except: return None

            datos_map = HashMap()
            for k, v in campos_raw.items():
                if "|" in v: v = v.replace("|", ",") 
                datos_map.put(k, v)
            return datos_map

        mapa_paciente_nombre_id = HashMap(capacity=100)
        if os.path.exists("pacientes.txt"):
            try:
                with open("pacientes.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        datos = procesar_linea_entidad(line, "Paciente(")
                        if not datos: continue
                        try:
                            mis_alergias = Set()
                            al_str = datos.get("Alergias")
                            if al_str and len(al_str) > 2:
                                clean = al_str.replace("{", "").replace("}", "")
                                for al in clean.split(","):
                                    if al.strip(): mis_alergias.add(al.strip())

                            self.gestion_pacientes.registrar_nuevo(
                                datos.get("ID"), datos.get("Nombre"), 
                                int(datos.get("Edad")), mis_alergias, datos.get("Estado")
                            )
                            mapa_paciente_nombre_id.put(datos.get("Nombre"), datos.get("ID"))
                        except: pass
                print("Pacientes cargados.")
            except Exception as e: print(f"Error Pacientes: {e}")

        if os.path.exists("medicos.txt"):
            try:
                conteo = 0
                with open("medicos.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        if "edico(" not in line: continue
                        datos = procesar_linea_entidad(line, "edico(")
                        if not datos: continue

                        try:
                            # 1. Registro Básico
                            id_med = datos.get("ID")
                            self.gestion_medicos.registrar_nuevo(
                                id_med,
                                datos.get("Nombre"),
                                datos.get("Especialidad"),
                                datos.get("Cedula")
                            )
                            medico_obj = None
                            try:
                                medico_obj = self.gestion_medicos.medicos.get(id_med)
                            except: pass

                            if medico_obj:
                                pac_str = datos.get("Pacientes Activos")
                                if pac_str and len(pac_str) > 2:
                                    clean_pac = pac_str.replace("{", "").replace("}", "")
                                    for pid in clean_pac.split(","):
                                        pid = pid.strip()
                                        if pid:
                                            medico_obj.agregar_paciente_activo(pid)
                                hor_str = datos.get("Horario")
                                if hor_str and len(hor_str) > 2:
                                    clean_hor = hor_str.replace("{", "").replace("}", "")
                                    # Separamos por comas (días)
                                    for entry in clean_hor.split(","):
                                        # entry: "lunes: 09:00-17:00"
                                        if ":" in entry:
                                            parts = entry.split(":", 1)
                                            dia = parts[0].strip()
                                            horas = parts[1].strip()
                                            medico_obj.agregar_horario(dia, horas)
                            
                            conteo += 1
                        except Exception as e:
                            print(f"Error médico {datos.get('Nombre')}: {e}")
                print(f"Médicos cargados: {conteo} (Con pacientes y horarios)")
            except Exception as e: print(f"Error Medicos: {e}")

        if os.path.exists("historiales.txt"):
            try:
                current_id = None
                with open("historiales.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if "[ Historial de Paciente" in line:
                            parts = line.split(" - ")
                            if len(parts) > 1:
                                nombre = parts[1].replace(" ]", "").strip()
                                try: current_id = mapa_paciente_nombre_id.get(nombre)
                                except: current_id = None
                            continue
                        
                        if current_id and line.startswith("- ") and "Consulta" not in line:
                            texto = line[2:]
                            tipo = "General"
                            desc = texto
                            if "Especialidad:" in texto:
                                tipo = "Especialidad"
                                desc = texto.split(": ")[1]
                            self.gestion_historial.agregar_nuevo_registro(current_id, tipo, desc)
                print("Historiales cargados.")
            except: pass

        if os.path.exists("farmacia.txt"):
            try:
                with open("farmacia.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        if "Medicamento(" not in line: continue
                        
                        datos = procesar_linea_entidad(line, "Medicamento(")
                        if datos:
                            nm = Medicamento(
                                datos.get("ID"),        
                                datos.get("Nombre"), 
                                int(datos.get("Cantidad")), 
                                datos.get("Tipo")
                            )
                            
                            if hasattr(self.gestion_farmacia, 'inventario'):
                                self.gestion_farmacia.inventario.put(nm.id_medicamento, nm)
                                if hasattr(self.gestion_farmacia, 'nombres_set'):
                                    self.gestion_farmacia.nombres_set.add(nm.nombre)
                                    
                print("Farmacia cargada (Indexada por ID).")
            except Exception as e: 
                print(f"Error cargando farmacia: {e}")

        if os.path.exists("citas.txt"):
            try:
                with open("citas.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        if "Cita(" not in line: continue
                        datos = procesar_linea_entidad(line, "Cita(")
                        if datos:
                            raw_fecha = datos.get("Fecha")
                            fecha = raw_fecha.split(" ")[0] if " " in raw_fecha else raw_fecha
                            hora = raw_fecha.split(" ")[1] if " " in raw_fecha else "00:00"
                            c = Cita(datos.get("ID"), datos.get("Paciente"), datos.get("Prioridad"), datos.get("Nota"), fecha, hora, datos.get("Especialidad"))
                            self.gestion_citas.citas.put(c.id_cita, c)
                print("Citas cargadas.")
            except: pass

        if os.path.exists("notificaciones.txt"):
            try:
                cola_ref = getattr(self.gestion_notificaciones, 'cola', None) or \
                            getattr(self.gestion_notificaciones, 'notificaciones', None)
                with open("notificaciones.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip() and cola_ref: cola_ref.enqueue(line.strip())
                print("Notificaciones cargadas.")
            except: pass
    
            
    def save_pacientes_to_txt(self):
        try:
            with open("pacientes.txt", "w", encoding="utf-8") as f:
                f.write("Historial de Pacientes:\n")
                for p in self.gestion_pacientes.listar_todos():
                    f.write(str(p) + "\n")
                    f.write("-" * 50 + "\n")
        except Exception as e:
            print(f"Error guardando pacientes: {e}")

    def save_medicos_to_txt(self):
        try:
            with open("medicos.txt", "w", encoding="utf-8") as f:
                f.write("Historial de Médicos:\n")
                for m in self.gestion_medicos.listar_todos():
                    f.write(str(m) + "\n")
                    f.write("-" * 50 + "\n")
        except Exception as e:
            print(f"Error guardando médicos: {e}")

    def save_historiales_to_txt(self):
        try:
            with open("historiales.txt", "w", encoding="utf-8") as f:
                f.write("Historiales Médicos:\n")
                for p in self.gestion_pacientes.listar_todos():
                    # Obtenemos historial formateado
                    historial = self.gestion_historial.ver_historial(p.id_paciente, formateado=True)
                    if historial: # Solo escribir si hay historial
                        f.write(historial + "\n")
                        f.write("-" * 50 + "\n")
        except Exception as e:
            print(f"Error guardando historiales: {e}")
    
    def save_to_txt(self):
        print("--- Guardando datos en TXT... ---")
        
        self.save_pacientes_to_txt()
        self.save_medicos_to_txt()
        self.save_historiales_to_txt()
        
        try:
            with open("citas.txt", "w", encoding="utf-8") as f:
                for cita in self.gestion_citas.listar_todas():
                    f.write(str(cita) + "\n")
        except Exception as e:
            print(f"Error guardando citas: {e}")

        try:
            with open("farmacia.txt", "w", encoding="utf-8") as f:
                # Tu HashMap itera devolviendo (clave, valor)
                # self.gestion_farmacia.inventario es un HashMap
                for id_med, obj_med in self.gestion_farmacia.inventario:
                    f.write(str(obj_med) + "\n")
        except Exception as e:
            print(f"Error guardando farmacia: {e}")

        try:
            with open("notificaciones.txt", "w", encoding="utf-8") as f:
                cola_ref = None
                if hasattr(self.gestion_notificaciones, 'cola'):
                    cola_ref = self.gestion_notificaciones.cola
                elif hasattr(self.gestion_notificaciones, 'notificaciones'):
                    cola_ref = self.gestion_notificaciones.notificaciones
                
                if cola_ref:
                    for notif in cola_ref:
                        f.write(str(notif) + "\n")
        except Exception as e:
            print(f"Error guardando notificaciones: {e}")
            
        print("--- Guardado completado ---")
    
    def exportar_datos(self):
        self.save_to_txt()
        try:
            from tkinter import messagebox # Importación local segura
            messagebox.showinfo("Exportar", "Datos guardados correctamente en los archivos TXT.")
        except:
            print("Datos exportados correctamente.")
    

    
        
class CollapsingFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.row = 0

    def add(self, child, title="Section"):
        header = ttk.Frame(self, bootstyle=PRIMARY)
        header.grid(row=self.row, column=0, sticky=EW, pady=1)
        ttk.Label(header, text=title, font=("Helvetica", 10, "bold")).pack(side=LEFT, padx=10)
        btn = ttk.Button(header, text="▼", width=3, bootstyle="primary-outline",
                        command=lambda c=child: self.toggle(c, btn))
        btn.pack(side=RIGHT, padx=5)
        child.btn = btn
        child.grid(row=self.row + 1, column=0, sticky=EW)
        self.row += 2

    def toggle(self, child, btn):
        if child.winfo_viewable():
            child.grid_remove()
            btn.configure(text="▶")
        else:
            child.grid()
            btn.configure(text="▼")


def on_closing():
    try:
        gui.save_to_txt() 
    except Exception as e:
        print(f"Error crítico al guardar en salida: {e}")
    finally:
        app.destroy()
        
if __name__ == '__main__':
    app = ttk.Window(title="Sistema de Gestión Hospitalaria", themename="cosmo")
    gui = HospitalGUI(app)
    app.protocol("WM_DELETE_WINDOW", lambda: [gui.save_to_txt(), app.destroy()])
    app.mainloop()