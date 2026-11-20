from collections import Counter

# Modelo 1: clasificador zero-shot multilingue (area y prioridad)
MODELO_CLASIFICADOR = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
# Modelo 2: modelo generativo local (respuestas sugeridas y analisis)
MODELO_GENERADOR = "Qwen/Qwen2.5-0.5B-Instruct"

# El modelo zero-shot compara el ticket con estas descripciones
ETIQUETAS_AREA = {
    "Redes": "problemas de internet, wifi, VPN o conexion de red",
    "Software": "problemas con programas, sistemas, correo, contrasenas o accesos",
    "Soporte Tecnico": "fallas fisicas de computadoras, pantallas, impresoras o teclados",
}
ETIQUETAS_PRIORIDAD = {
    "Alta": "es urgente y impide trabajar",
    "Media": "es molesto pero se puede seguir trabajando",
    "Baja": "es una consulta o duda sencilla",
}


class IAService:

    def __init__(self):
        self.clasificador = None
        self.generador = None

    # ---------- carga de modelos (solo cuando se necesitan) ----------
    def cargar_clasificador(self):
        if self.clasificador is None:
            from transformers import pipeline
            print("Cargando modelo clasificador (la primera vez descarga el modelo)...")
            self.clasificador = pipeline("zero-shot-classification",
                                         model=MODELO_CLASIFICADOR)

    def cargar_generador(self):
        if self.generador is None:
            from transformers import pipeline
            print("Cargando modelo generativo local...")
            self.generador = pipeline("text-generation", model=MODELO_GENERADOR)

    def _clasificar(self, texto, etiquetas, plantilla):
        self.cargar_clasificador()
        resultado = self.clasificador(
            texto,
            list(etiquetas.values()),
            hypothesis_template=plantilla
        )
        mejor_etiqueta = resultado["labels"][0]
        confianza = resultado["scores"][0]
        for clave in etiquetas:
            if etiquetas[clave] == mejor_etiqueta:
                return clave, confianza
        return None, 0.0
    def clasificar_area(self, descripcion):
        return self._clasificar(descripcion, ETIQUETAS_AREA, "Este ticket trata sobre {}.")

    def clasificar_prioridad(self, descripcion):
        return self._clasificar(descripcion, ETIQUETAS_PRIORIDAD, "Este problema {}.")

    # ---------- generacion de texto ----------
    def _generar(self, mensaje_sistema, mensaje_usuario, max_tokens):
        self.cargar_generador()
        mensajes = [
            {"role": "system", "content": mensaje_sistema},
            {"role": "user", "content": mensaje_usuario},
        ]
        resultado = self.generador(
            mensajes,
            max_new_tokens=max_tokens,
            temperature=0.3,
        )
        return resultado[0]["generated_text"][-1]["content"].strip()

    def sugerir_respuesta(self, descripcion, area):
        sistema = ("Eres un agente de soporte tecnico de una empresa. "
                   "Responde siempre en espanol, con maximo 3 pasos cortos. "
                   "No inventes datos ni pidas informacion personal.")
        usuario = "Area: " + area + "\nProblema del usuario: " + descripcion
        return self._generar(sistema, usuario, 120)

    def crear_contexto(self, tickets):
        por_estado = Counter(t.estado for t in tickets)
        por_area = Counter(t.area for t in tickets)
        pendientes = Counter(t.prioridad for t in tickets if t.estado == "Pendiente")
        horas = [t.calcular_duracion_horas() for t in tickets if t.estado == "Resuelto"]
        promedio = sum(horas) / len(horas) if horas else 0.0

        lineas = ["DATOS CALCULADOS POR EL SISTEMA", "",
                  "Total de tickets: " + str(len(tickets)),
                  "Promedio de horas de resolucion: " + str(round(promedio, 2)), "",
                  "TICKETS POR ESTADO"]
        for estado in por_estado:
            lineas.append(estado + ": " + str(por_estado[estado]))
        lineas.append("")
        lineas.append("TICKETS POR AREA")
        for area in por_area:
            lineas.append(area + ": " + str(por_area[area]))
        lineas.append("")
        lineas.append("PENDIENTES POR PRIORIDAD")
        for prioridad in pendientes:
            lineas.append(prioridad + ": " + str(pendientes[prioridad]))
        return "\n".join(lineas)

    def consultar(self, pregunta, tickets):
        if not pregunta.strip():
            raise ValueError("La pregunta no puede estar vacia.")
        if not tickets:
            return "No existen tickets registrados."
        contexto = self.crear_contexto(tickets)
        sistema = ("Eres un asistente que analiza tickets de una mesa de ayuda. "
                   "Responde siempre en espanol, de forma breve y directa. "
                   "Usa exclusivamente los datos proporcionados por el sistema. "
                   "No inventes informacion.")
        usuario = contexto + "\n\nPREGUNTA DEL USUARIO:\n" + pregunta
        return self._generar(sistema, usuario, 80)
