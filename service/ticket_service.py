from datetime import datetime

from model.constantes import AREAS, ESTADOS, PRIORIDADES, ORDEN_PRIORIDAD, FORMATO_FECHA
from model.ticket import Ticket
from repository.ticket_repository import TicketRepository
from service.clasificador_service import AgenteClasificador
from util.tiempo_util import promedio


class TicketService:

    def __init__(self, repositorio=None, agente=None):
        self.repositorio = repositorio if repositorio else TicketRepository()
        self.agente = agente if agente else AgenteClasificador()

    # ---------- consultas ----------
    def listar_tickets(self):
        return self.repositorio.obtener_todos()

    def buscar_ticket(self, id_ticket):
        for ticket in self.listar_tickets():
            if ticket.id_ticket == id_ticket:
                return ticket
        return None

    def tickets_de_usuario(self, usuario):
        return [t for t in self.listar_tickets() if t.usuario == usuario]

    def tickets_por_area(self, area):
        return [t for t in self.listar_tickets() if t.area == area]

    def historial_resueltos(self, area):
        return [t for t in self.listar_tickets()
                if t.area == area and t.estado == "Resuelto"]

    # ---------- cola de atencion ----------
    def _ordenar_cola(self, tickets, area=None):
        cola = []
        for ticket in tickets:
            if ticket.estado == "Pendiente":
                if area is None or ticket.area == area:
                    cola.append(ticket)
        # primero la prioridad (Alta, Media, Baja) y luego el mas antiguo
        cola.sort(key=lambda t: (ORDEN_PRIORIDAD[t.prioridad], t.fecha_creacion))
        return cola

    def cola_atencion(self, area=None):
        return self._ordenar_cola(self.listar_tickets(), area)

    def posicion_en_cola(self, ticket):
        cola = self.cola_atencion(ticket.area)
        for i in range(len(cola)):
            if cola[i].id_ticket == ticket.id_ticket:
                return i + 1
        return None

    # ---------- operaciones ----------
    def crear_ticket(self, usuario, descripcion):
        usuario = usuario.strip()
        descripcion = descripcion.strip()
        if not usuario or not descripcion:
            raise ValueError("El usuario y la descripcion son obligatorios.")

        tickets = self.listar_tickets()
        nuevo_id = 1
        if tickets:
            nuevo_id = max(t.id_ticket for t in tickets) + 1

        area, prioridad, metodo = self.agente.clasificar(descripcion)
        ticket = Ticket(nuevo_id, usuario, area, descripcion, prioridad,
                        datetime.now().strftime(FORMATO_FECHA), clasificado_por=metodo)
        tickets.append(ticket)
        self.repositorio.guardar_todos(tickets)
        return ticket

    def atender_siguiente(self, area):
        tickets = self.listar_tickets()
        cola = self._ordenar_cola(tickets, area)
        if len(cola) == 0:
            return None
        ticket = cola[0]
        ticket.estado = "En proceso"
        self.repositorio.guardar_todos(tickets)
        return ticket

    def resolver_ticket(self, id_ticket, solucion, area):
        if not solucion.strip():
            raise ValueError("Debes registrar la solucion aplicada.")
        tickets = self.listar_tickets()
        ticket = self._buscar_en(tickets, id_ticket)
        if ticket.area != area:
            raise ValueError("Ese ticket pertenece a otra area.")
        if ticket.estado != "En proceso":
            raise ValueError("Solo se puede resolver un ticket que esta En proceso.")
        ticket.estado = "Resuelto"
        ticket.solucion = solucion.strip()
        ticket.fecha_cierre = datetime.now().strftime(FORMATO_FECHA)
        self.repositorio.guardar_todos(tickets)
        return ticket

    def modificar_ticket(self, id_ticket, usuario, area, descripcion, prioridad, estado):
        if area not in AREAS or estado not in ESTADOS or prioridad not in PRIORIDADES:
            raise ValueError("Area, prioridad o estado no validos.")
        tickets = self.listar_tickets()
        ticket = self._buscar_en(tickets, id_ticket)
        ticket.usuario = usuario
        ticket.area = area
        ticket.descripcion = descripcion
        ticket.prioridad = prioridad
        ticket.estado = estado
        ticket.clasificado_por = "manual"
        if estado == "Resuelto":
            if not ticket.fecha_cierre:
                ticket.fecha_cierre = datetime.now().strftime(FORMATO_FECHA)
        else:
            ticket.fecha_cierre = ""
        self.repositorio.guardar_todos(tickets)
        return ticket

    def eliminar_ticket(self, id_ticket):
        tickets = self.listar_tickets()
        ticket = self._buscar_en(tickets, id_ticket)
        tickets.remove(ticket)
        self.repositorio.guardar_todos(tickets)

    def _buscar_en(self, tickets, id_ticket):
        for ticket in tickets:
            if ticket.id_ticket == id_ticket:
                return ticket
        raise ValueError("No existe un ticket con id " + str(id_ticket) + ".")

    # ---------- reportes ----------
    def estadisticas(self):
        tickets = self.listar_tickets()
        por_estado = {}
        por_area = {}
        horas_totales = []
        for ticket in tickets:
            por_estado[ticket.estado] = por_estado.get(ticket.estado, 0) + 1
            if ticket.area not in por_area:
                por_area[ticket.area] = {"recibidos": 0, "resueltos": 0, "horas": []}
            datos = por_area[ticket.area]
            datos["recibidos"] += 1
            if ticket.estado == "Resuelto":
                horas = ticket.calcular_duracion_horas()
                datos["resueltos"] += 1
                datos["horas"].append(horas)
                horas_totales.append(horas)
        for area in por_area:
            por_area[area]["promedio_horas"] = promedio(por_area[area]["horas"])
        return {
            "total": len(tickets),
            "por_estado": por_estado,
            "por_area": por_area,
            "promedio_horas": promedio(horas_totales),
        }