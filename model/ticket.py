from datetime import datetime

from model.constantes import FORMATO_FECHA


class Ticket:

    def __init__(self, id_ticket, usuario, area, descripcion, prioridad,
                 fecha_creacion, estado="Pendiente", solucion="",
                 fecha_cierre="", clasificado_por="reglas"):
        self.id_ticket = id_ticket
        self.usuario = usuario
        self.area = area
        self.descripcion = descripcion
        self.prioridad = prioridad
        self.fecha_creacion = fecha_creacion
        self.estado = estado
        self.solucion = solucion
        self.fecha_cierre = fecha_cierre
        self.clasificado_por = clasificado_por

    def calcular_duracion_horas(self):
        """Si el ticket esta resuelto: fecha_cierre - fecha_creacion.
        Si sigue abierto: ahora - fecha_creacion (tiempo ya consumido)."""
        inicio = datetime.strptime(self.fecha_creacion, FORMATO_FECHA)
        if self.fecha_cierre:
            fin = datetime.strptime(self.fecha_cierre, FORMATO_FECHA)
        else:
            fin = datetime.now()
        return max((fin - inicio).total_seconds() / 3600, 0.0)
