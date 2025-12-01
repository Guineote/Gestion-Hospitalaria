# Scripts/notificaciones.py
from .estructuras import Queue
from datetime import datetime

class Notificacion:
    def __init__(self, mensaje):
        self.mensaje = mensaje
        self.fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

    def __str__(self):
        return f"[{self.fecha_hora}] {self.mensaje}"

class GestionNotificaciones:
    def __init__(self):
        self.cola = Queue()  # Tu Queue personalizada (FIFO)

    def agregar(self, mensaje):
        notif = Notificacion(mensaje)
        self.cola.enqueue(notif)

    def obtener_todas(self):
        # Devuelve una DoublyLinkedList para iterar fácilmente
        from .estructuras import DoublyLinkedList
        lista = DoublyLinkedList()
        temp_queue = Queue()
        while not self.cola.is_empty():
            notif = self.cola.dequeue()
            lista.append(notif)
            temp_queue.enqueue(notif)
        # Restaurar cola original
        while not temp_queue.is_empty():
            self.cola.enqueue(temp_queue.dequeue())
        return lista

    def contar(self):
        return self.cola.length()

    def limpiar(self):
        while not self.cola.is_empty():
            self.cola.dequeue()