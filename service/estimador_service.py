class EstimadorService:
    """Estima cuanto tardara un ticket usando el promedio de los tickets
    ya resueltos (mismo calculo fecha_cierre - fecha_creacion)."""

    def __init__(self, ticket_service):
        self.ticket_service = ticket_service

    def _horas_resueltas(self, area=None, prioridad=None):
        horas = []
        for ticket in self.ticket_service.listar_tickets():
            if ticket.estado == "Resuelto":
                if area is None or ticket.area == area:
                    if prioridad is None or ticket.prioridad == prioridad:
                        horas.append(ticket.calcular_duracion_horas())
        return horas

    def estimar_horas(self, area, prioridad):
        """Promedio de tickets con la misma area y prioridad.
        Si no hay, usa el promedio general. Devuelve None si no hay datos."""
        horas = self._horas_resueltas(area, prioridad)
        if len(horas) == 0:
            horas = self._horas_resueltas()
        if len(horas) == 0:
            return None
        return sum(horas) / len(horas)

    def estimar_restante(self, ticket):
        """Tiempo estimado menos el tiempo que ya paso (minimo cero)."""
        estimado = self.estimar_horas(ticket.area, ticket.prioridad)
        if estimado is None:
            return None
        restante = estimado - ticket.calcular_duracion_horas()
        if restante < 0:
            restante = 0
        return restante
