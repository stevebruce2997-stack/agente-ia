from util.reglas_util import clasificar_area_reglas, definir_prioridad_reglas


class EvaluacionService:
    """Compara lo que clasifica el sistema (reglas o IA) con la clasificacion
    manual del dataset (tickets con clasificado_por = "manual")."""

    def __init__(self, ticket_service, ia_service):
        self.ticket_service = ticket_service
        self.ia_service = ia_service

    def tickets_de_referencia(self):
        tickets = []
        for ticket in self.ticket_service.listar_tickets():
            if ticket.clasificado_por == "manual":
                tickets.append(ticket)
        return tickets

    def obtener_muestra(self, cantidad):
        """Toma 'cantidad' tickets repartidos en todo el dataset."""
        tickets = self.tickets_de_referencia()
        if cantidad >= len(tickets):
            return tickets
        paso = len(tickets) // cantidad
        return tickets[::paso][:cantidad]

    def _evaluar(self, tickets, clasificar):
        aciertos_area = 0
        aciertos_prioridad = 0
        alta_total = 0
        alta_detectadas = 0
        for ticket in tickets:
            area, prioridad = clasificar(ticket.descripcion)
            if area == ticket.area:
                aciertos_area += 1
            if prioridad == ticket.prioridad:
                aciertos_prioridad += 1
            if ticket.prioridad == "Alta":
                alta_total += 1
                if prioridad == "Alta":
                    alta_detectadas += 1
        total = len(tickets)
        return {
            "total": total,
            "acierto_area": aciertos_area / total * 100,
            "acierto_prioridad": aciertos_prioridad / total * 100,
            "alta_total": alta_total,
            "alta_detectadas": alta_detectadas,
        }

    def evaluar_reglas(self, tickets):
        def clasificar(descripcion):
            return clasificar_area_reglas(descripcion), definir_prioridad_reglas(descripcion)
        return self._evaluar(tickets, clasificar)

    def evaluar_ia(self, tickets):
        def clasificar(descripcion):
            area, confianza_area = self.ia_service.clasificar_area(descripcion)
            prioridad, confianza_prioridad = self.ia_service.clasificar_prioridad(descripcion)
            return area, prioridad
        return self._evaluar(tickets, clasificar)
