from util.reglas_util import clasificar_area_reglas, definir_prioridad_reglas

UMBRAL_CONFIANZA = 0.5


class AgenteClasificador:
    """Decide el area y la prioridad de un ticket.
    Si la IA esta activada y esta segura, usa la IA; si no, usa las reglas."""

    def __init__(self, ia_service=None, usar_ia=False):
        self.ia_service = ia_service
        self.usar_ia = usar_ia

    def clasificar(self, descripcion):
        """Devuelve (area, prioridad, metodo)."""
        if self.usar_ia:
            try:
                area, confianza_area = self.ia_service.clasificar_area(descripcion)
                prioridad, confianza_prioridad = self.ia_service.clasificar_prioridad(descripcion)
                if confianza_area >= UMBRAL_CONFIANZA and confianza_prioridad >= UMBRAL_CONFIANZA:
                    return area, prioridad, "ia"
            except Exception as error:
                print("Aviso: no se pudo usar la IA (" + str(error) + "). Se usan las reglas.")
                self.usar_ia = False

        area = clasificar_area_reglas(descripcion)
        prioridad = definir_prioridad_reglas(descripcion)
        return area, prioridad, "reglas"