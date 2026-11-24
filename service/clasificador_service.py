import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class AgenteClasificador:
    """Agente de IA generativa que razona el contexto para clasificar tickets."""

    def __init__(self, ia_service=None, usar_ia=True):
        # Conectamos directamente el nuevo motor de Google
        self.cliente = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def clasificar(self, descripcion):
        """Lee el problema, razona el nivel de urgencia y devuelve (area, prioridad, metodo)."""
        print("\n[IA Analizando gravedad del ticket...]")
        
        # INGENIERÍA DE PROMPTS: Le enseñamos a razonar a la IA
        libreto = (
            "Eres un experto en soporte técnico clasificando tickets. "
            "Lee el problema del usuario y devuelve SOLO DOS PALABRAS separadas por una coma. "
            "Primera palabra (el área): Hardware, Software o Redes. "
            "Segunda palabra (la prioridad): Baja, Media, Alta o Critica. "
            "REGLAS DE RAZONAMIENTO: "
            "- Si el usuario describe daños físicos, humo, llamas, fuego, chispas, o riesgo a la integridad física -> Critica. "
            "- Si el problema le impide trabajar por completo (pantalla azul, apagón) -> Alta. "
            "- Si es un problema molesto pero puede seguir trabajando (lentitud, error de programa) -> Media. "
            "- Si es una consulta, instalación o duda general -> Baja. "
            "Ejemplo de tu respuesta exacta: Hardware, Critica"
        )

        try:
            # Usamos el modelo ultra-rápido que no se satura
            respuesta = self.cliente.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=descripcion,
                config={"system_instruction": libreto}
            )
            
            # La IA nos devuelve algo como "Hardware, Critica". Lo separamos.
            resultado = respuesta.text.strip().split(',')
            area = resultado[0].strip()
            prioridad = resultado[1].strip()
            
            return area, prioridad, "IA-Gemini"
            
        except Exception as e:
            print(f"[Aviso]: Saturación de red ({e}). Usando clasificación manual.")
            return "Soporte General", "Media", "Reglas-Emergencia"