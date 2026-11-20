from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google.adk.agents import Agent

# Carga la clave del archivo .env (esta en esta misma carpeta)
load_dotenv(Path(__file__).parent / ".env")

# Gemini lee la clave GEMINI_API_KEY que cargo load_dotenv
modelo = "gemini-flash-lite-latest"

# Dataset: el CSV esta en la carpeta datos, junto a este archivo
carpeta = Path(__file__).parent / "datos"
tickets = pd.read_csv(carpeta / "tickets.csv", dtype=str, keep_default_na=False)
tickets["id_ticket"] = tickets["id_ticket"].astype(int)
tickets["fecha_creacion"] = pd.to_datetime(tickets["fecha_creacion"], format="%Y-%m-%d %H:%M")
tickets["fecha_cierre"] = pd.to_datetime(tickets["fecha_cierre"], format="%Y-%m-%d %H:%M",
                                         errors="coerce")

# Tiempo de resolucion = fecha_cierre - fecha_creacion (igual que en el ejemplo del scooter)
tickets["horas_resolucion"] = (tickets["fecha_cierre"] - tickets["fecha_creacion"]).dt.total_seconds() / 3600

# "Ahora" sirve para calcular cuanto tiempo lleva abierto un ticket.
# Para la demo se puede fijar a la fecha de referencia del dataset:
AHORA = pd.Timestamp("2026-10-03 08:00")
#AHORA = pd.Timestamp.now()

ORDEN_PRIORIDAD = {"Alta": 1, "Media": 2, "Baja": 3}
PALABRAS_VACIAS = ["para", "como", "esta", "estoy", "tengo", "desde", "porque", "pero", "favor",
                   "ayuda", "hola", "buenos", "dias", "tardes", "cuando", "donde", "tiene",
                   "hace", "hoy", "ayer", "mucho", "puedo", "puede", "quiero", "necesito"]


# Funciones auxiliares (no son herramientas del agente)
def limpiar(texto):
    """Minusculas y sin tildes, para comparar nombres y palabras."""
    texto = str(texto).lower()
    texto = texto.replace("á", "a").replace("é", "e").replace("í", "i")
    texto = texto.replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    return texto


def palabras_clave(texto):
    """Palabras de mas de 3 letras, sin signos ni palabras vacias."""
    texto = limpiar(texto)
    for signo in ".,;:!?¿¡()\"":
        texto = texto.replace(signo, " ")
    palabras = set()
    for palabra in texto.split():
        if len(palabra) > 3 and palabra not in PALABRAS_VACIAS:
            palabras.add(palabra)
    return palabras


def a_lista(tabla):
    """Convierte las filas en diccionarios simples (con las fechas como texto)."""
    lista = []
    for _, fila in tabla.iterrows():
        ticket = {
            "id_ticket": int(fila["id_ticket"]),
            "usuario": fila["usuario"],
            "area": fila["area"],
            "prioridad": fila["prioridad"],
            "estado": fila["estado"],
            "descripcion": fila["descripcion"],
            "fecha_creacion": fila["fecha_creacion"].strftime("%Y-%m-%d %H:%M"),
        }
        if fila["estado"] == "Resuelto":
            ticket["solucion"] = fila["solucion"]
            ticket["horas_resolucion"] = round(float(fila["horas_resolucion"]), 1)
        else:
            ticket["horas_abierto"] = round((AHORA - fila["fecha_creacion"]).total_seconds() / 3600, 1)
        lista.append(ticket)
    return lista


# Herramientas: funciones normales de Python que consultan el dataset
def buscar_tickets_de_usuario(nombre: str) -> dict:
    """Busca los tickets de una persona por su nombre o parte del nombre. Ejemplo: 'Carmen'."""
    nombres = tickets["usuario"].map(limpiar)
    encontrados = tickets[nombres.str.contains(limpiar(nombre), regex=False)]
    recientes = encontrados.sort_values("fecha_creacion", ascending=False).head(15)
    return {
        "usuarios_encontrados": sorted(encontrados["usuario"].unique().tolist()),
        "total_tickets": len(encontrados),
        "tickets_mas_recientes": a_lista(recientes),
    }


def ver_ticket(id_ticket: int) -> dict:
    """Muestra el estado y los datos de un ticket por su numero. Ejemplo: 25."""
    encontrado = tickets[tickets["id_ticket"] == id_ticket]
    if len(encontrado) == 0:
        return {"error": "No existe un ticket con ese numero."}
    return {"ticket": a_lista(encontrado)[0]}


def cola_de_atencion(area: str = "", limite: int = 5) -> dict:
    """Lista los tickets pendientes en el orden en que deben atenderse: primero la prioridad
    (Alta, Media, Baja) y luego el mas antiguo. El area es opcional:
    'Soporte Tecnico', 'Redes' o 'Software'."""
    cola = tickets[tickets["estado"] == "Pendiente"].copy()
    if area != "":
        cola = cola[cola["area"].map(limpiar) == limpiar(area)]
    cola["orden"] = cola["prioridad"].map(ORDEN_PRIORIDAD)
    cola = cola.sort_values(["orden", "fecha_creacion"]).head(limite)
    return {"tickets_en_cola": a_lista(cola)}


def contar_tickets(area: str = "", prioridad: str = "", estado: str = "") -> dict:
    """Cuenta tickets. Todos los filtros son opcionales: area ('Soporte Tecnico', 'Redes',
    'Software'), prioridad ('Alta', 'Media', 'Baja') y estado ('Pendiente', 'En proceso',
    'Resuelto')."""
    filtrados = tickets
    if area != "":
        filtrados = filtrados[filtrados["area"].map(limpiar) == limpiar(area)]
    if prioridad != "":
        filtrados = filtrados[filtrados["prioridad"].map(limpiar) == limpiar(prioridad)]
    if estado != "":
        filtrados = filtrados[filtrados["estado"].map(limpiar) == limpiar(estado)]
    return {"cantidad": len(filtrados)}


def resumen_por_area() -> dict:
    """Reporte: tickets recibidos, resueltos y sin resolver por area, y el tiempo promedio
    de resolucion en horas."""
    resumen = {}
    for area in sorted(tickets["area"].unique()):
        del_area = tickets[tickets["area"] == area]
        resueltos = del_area[del_area["estado"] == "Resuelto"]
        resumen[area] = {
            "recibidos": len(del_area),
            "resueltos": len(resueltos),
            "sin_resolver": len(del_area) - len(resueltos),
            "promedio_horas_resolucion": round(float(resueltos["horas_resolucion"].mean()), 1),
        }
    general = tickets["horas_resolucion"].mean()
    return {"por_area": resumen, "promedio_general_horas": round(float(general), 1)}


def tiempo_estimado(area: str, prioridad: str) -> dict:
    """Estima en horas cuanto tardara un ticket nuevo, usando el promedio de los tickets ya
    resueltos con la misma area y prioridad. Ejemplo: area 'Redes', prioridad 'Alta'."""
    resueltos = tickets[tickets["estado"] == "Resuelto"]
    parecidos = resueltos[(resueltos["area"].map(limpiar) == limpiar(area))
                          & (resueltos["prioridad"].map(limpiar) == limpiar(prioridad))]
    if len(parecidos) == 0:
        return {"horas_estimadas": round(float(resueltos["horas_resolucion"].mean()), 1),
                "tickets_usados": len(resueltos), "nota": "Promedio general: no hay casos iguales."}
    return {"horas_estimadas": round(float(parecidos["horas_resolucion"].mean()), 1),
            "tickets_usados": len(parecidos)}


def buscar_casos_similares(problema: str, limite: int = 3) -> dict:
    """Busca tickets ya resueltos parecidos al problema descrito. Devuelve su area, prioridad
    y la solucion que funciono. Sirve para clasificar un problema nuevo y sugerir una solucion."""
    buscadas = palabras_clave(problema)
    resueltos = tickets[tickets["estado"] == "Resuelto"]
    casos = []
    for _, fila in resueltos.iterrows():
        coincidencias = len(buscadas & palabras_clave(fila["descripcion"]))
        if coincidencias > 0:
            casos.append((coincidencias, fila["id_ticket"]))
    casos.sort(reverse=True)
    mejores = [id_ticket for _, id_ticket in casos[:limite]]
    elegidos = resueltos[resueltos["id_ticket"].isin(mejores)]
    return {"casos_similares": a_lista(elegidos)}


root_agent = Agent(
    model=modelo,  # el modelo de lenguaje
    name="asistente_mesa_ayuda",
    instruction=(
        "Eres un asistente de la mesa de ayuda de soporte tecnico de una empresa. "
        "Responde en español y de forma breve. "
        "Usa las herramientas para consultar los datos y no inventes informacion. "
        "Si te piden los tickets de una persona por su nombre, usa buscar_tickets_de_usuario. "
        "Si alguien describe un problema nuevo, no crees tickets: primero usa "
        "buscar_casos_similares y luego sugiere el area y la prioridad, la solucion que funciono "
        "y el tiempo_estimado. "
        "Areas: Soporte Tecnico (computadoras, pantallas, impresoras, teclados), "
        "Redes (internet, wifi, VPN, servidores), "
        "Software (sistemas, correo, cuentas, contraseñas, accesos). "
        "Prioridades: Alta (bloquea el trabajo), Media (molesta pero se puede trabajar), "
        "Baja (consulta o solicitud sin urgencia). "
        "Aclara siempre que tu clasificacion es una sugerencia que un agente humano debe confirmar. "
        "Si te preguntan algo que no tiene que ver con la mesa de ayuda, "
        "explica que solo ayudas con tickets de soporte."
    ),
    tools=[buscar_tickets_de_usuario, ver_ticket, cola_de_atencion, contar_tickets,
           resumen_por_area, tiempo_estimado, buscar_casos_similares],  # las funciones
)
