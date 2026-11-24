class EstimadorService:
    """Estima cuánto tardará un ticket basándose en SLAs (Acuerdos de Nivel de Servicio)
    para garantizar tiempos de respuesta profesionales, incluso sin historial."""

    def __init__(self, ticket_service):
        self.ticket_service = ticket_service
        
        # DEFINICIÓN DE SLAs (En horas estimadas de resolución máxima)
        self.sla = {
            "Critica": 1.0,  # 1 hora
            "Alta": 4.0,     # 4 horas
            "Media": 24.0,   # 24 horas
            "Baja": 48.0     # 48 horas
        }

    def estimar_horas(self, area, prioridad):
        """Devuelve el SLA garantizado según la prioridad del ticket."""
        # Si la prioridad existe en nuestro diccionario de SLA, devolvemos el valor.
        # Si por alguna razón llega un dato extraño, garantizamos 24 horas (Media) por defecto.
        return self.sla.get(prioridad, 24.0)

    def estimar_restante(self, ticket):
        """Tiempo del SLA menos el tiempo que ya pasó (mínimo cero)."""
        estimado = self.estimar_horas(ticket.area, ticket.prioridad)
        
        # Calculamos cuánto tiempo ha pasado desde que se creó el ticket
        horas_pasadas = ticket.calcular_duracion_horas()
        
        restante = estimado - horas_pasadas
        if restante < 0:
            restante = 0
        return restante