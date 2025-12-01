# Gestión-Hospitalaria

> Un sistema completo de administración clínica desarrollado en Python, enfocado en la implementación **desde cero** de estructuras de datos y algoritmos de optimización.

## 📋 Descripción

Este proyecto es una aplicación de escritorio para la gestión integral de un hospital. A diferencia de las aplicaciones estándar que dependen de librerías de alto nivel para el manejo de datos, este sistema implementa sus propias estructuras (HashMaps, Heaps, Listas Enlazadas) para gestionar la memoria y la lógica de negocio, demostrando un entendimiento profundo de la eficiencia algorítmica.

El sistema permite gestionar pacientes, médicos, citas con triaje automático, inventario de farmacia y notificaciones.

## 🚀 Características Principales

### 🧠 Estructuras de Datos Propias
El núcleo del proyecto reside en `scripts/estructuras.py`. No se utilizan listas o diccionarios de Python para la lógica crítica:
* **Colas de Prioridad (Min-Heap):** Utilizadas para el sistema de priorizacipon de citas según su nivel. Los pacientes se atienden según su gravedad, no solo por orden de llegada. (triaje)
* **Tablas Hash (con encadenamiento):** Para la búsqueda $O(1)$ de Pacientes, Médicos y Medicamentos.
* **Listas Doblemente Enlazadas:** Manejo del historial médico cronológico, permitiendo navegación eficiente en ambos sentidos.
* **Colas (FIFO):** Gestión de notificaciones y recordatorios.
* **Árboles de Huffman:** (Implementado en backend) Para compresión y codificación de textos médicos.

### 🔍 Algoritmos de Búsqueda Avanzada
Implementación de lógica difusa y exacta en `scripts/busqueda.py`:
* **Algoritmo KMP (Knuth-Morris-Pratt):** Para búsquedas exactas de subcadenas sin retroceso.
* **Distancia de Levenshtein:** Para búsquedas difusas ("Fuzzy Search"). Permite encontrar pacientes o medicamentos incluso con errores tipográficos (ej: buscar "paracatamol" encuentra "Paracetamol").

### 🖥️ Interfaz Gráfica (GUI)
* Diseño moderno basado en **Tkinter** y **ttkbootstrap**.
* Navegación por pestañas y paneles colapsables.
* Actualización en tiempo real basada en eventos.

## 🛠️ Instalación y uso
Instalar la dependencia ttkinter y ttkbootstrap meidante pip.
Alternativa: Se puede ejecutar el ambiente virtual hosp ubicado en la raíz del proyecto sin embargo se requiere tener instalado Anaconda.
Pasos para ejecutar mediante ambiente virtual:
* conda activate hosp.
* cd "Ruta donde se almacene el proyecto"
* python hospital.py

En caso de que no se encunetre el ambiente hosp:
* conda env create -f hosp.yml
* conda activate hosp


## 📂 Estructura del Proyecto

```text
Gestion-Hospitalaria/
├── Assets/                 # Recursos gráficos
├── Scripts/
│   ├── busqueda.py         # KMP, Levenshtein, Hamming, Huffman
│   ├── citas.py            # Lógica de triaje y PQueue
│   ├── estructuras.py      # Implementación de Nodos, Listas, Heaps, HashMaps
│   ├── farmacia.py         # Gestión de inventario
│   ├── historial_medico.py # Registros clínicos
│   ├── medicos.py          # Gestión de personal
│   ├── notificaciones.py   # Cola de mensajes
│   └── pacientes.py        # Gestión de usuarios
├── hospital.py             # Punto de entrada (Main) y GUI
└── datos/                  # Persistencia en archivos de texto plano (.txt)
```


