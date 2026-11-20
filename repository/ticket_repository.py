import os

from model.ticket import Ticket
from util.archivo_util import leer_csv, escribir_csv

COLUMNAS = ["id_ticket", "usuario", "area", "descripcion", "prioridad", "estado",
            "solucion", "fecha_creacion", "fecha_cierre", "clasificado_por"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_POR_DEFECTO = os.path.join(os.path.dirname(BASE_DIR), "tickets.csv")


class TicketRepository:

    def __init__(self, ruta_archivo=RUTA_POR_DEFECTO):
        self.ruta_archivo = ruta_archivo

    def guardar_todos(self, tickets):
        registros = []
        for ticket in tickets:
            registro = {
                "id_ticket": ticket.id_ticket,
                "usuario": ticket.usuario,
                "area": ticket.area,
                "descripcion": ticket.descripcion,
                "prioridad": ticket.prioridad,
                "estado": ticket.estado,
                "solucion": ticket.solucion,
                "fecha_creacion": ticket.fecha_creacion,
                "fecha_cierre": ticket.fecha_cierre,
                "clasificado_por": ticket.clasificado_por,
            }
            registros.append(registro)
        escribir_csv(self.ruta_archivo, COLUMNAS, registros)

    def obtener_todos(self):
        filas = leer_csv(self.ruta_archivo)
        tickets = []
        for fila in filas:
            ticket = Ticket(
                id_ticket=int(fila["id_ticket"]),
                usuario=fila["usuario"],
                area=fila["area"],
                descripcion=fila["descripcion"],
                prioridad=fila["prioridad"],
                fecha_creacion=fila["fecha_creacion"],
                estado=fila["estado"],
                solucion=fila["solucion"],
                fecha_cierre=fila["fecha_cierre"],
                clasificado_por=fila["clasificado_por"],
            )
            tickets.append(ticket)
        return tickets
