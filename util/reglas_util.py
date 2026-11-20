from model.constantes import AREAS

# Si la descripcion contiene alguna de estas palabras, entonces va a esa area
REGLAS_AREA = {
    "Redes": ["internet", "wifi", "vpn", "conexion", "router", "servidor", "la red"],
    "Software": ["sistema", "programa", "aplicacion", "contrasena", "clave",
                 "acceso", "usuario", "correo", "instalar", "excel", "word"],
    "Soporte Tecnico": ["pantalla", "teclado", "mouse", "impresora", "computadora",
                        "laptop", "no enciende", "cable", "monitor"],
}

# Si la descripcion contiene alguna de estas palabras, entonces tiene esa prioridad
REGLAS_PRIORIDAD = {
    "Alta": ["urgente", "no puedo trabajar", "caid", "no funciona", "no enciende",
             "sin internet", "bloqueado"],
    "Media": ["lento", "error", "falla", "intermitente", "no carga"],
}

# Preguntas repetitivas que ya tienen una respuesta conocida
RESPUESTAS_FRECUENTES = {
    "olvide mi contrasena": "Usa la opcion 'Olvide mi contrasena' en la pagina de inicio de sesion.",
    "reiniciar": "Reinicia el equipo y vuelve a intentar. Si persiste, espera al agente.",
    "wifi": "Verifica que estes conectado a la red corporativa y reinicia el WiFi.",
}


def limpiar(texto):
    """Pasa a minusculas y quita tildes para poder comparar palabras."""
    texto = texto.lower()
    texto = texto.replace("á", "a").replace("é", "e").replace("í", "i")
    texto = texto.replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    return texto


def clasificar_area_reglas(descripcion):
    """Regla: gana el area con mas palabras clave encontradas."""
    texto = limpiar(descripcion)
    mejor_area = "Soporte Tecnico"   # area por defecto
    mejor_puntaje = 0
    for area in AREAS:
        puntaje = 0
        for palabra in REGLAS_AREA[area]:
            if palabra in texto:
                puntaje += 1
        if puntaje > mejor_puntaje:
            mejor_puntaje = puntaje
            mejor_area = area
    return mejor_area


def definir_prioridad_reglas(descripcion):
    texto = limpiar(descripcion)
    for palabra in REGLAS_PRIORIDAD["Alta"]:
        if palabra in texto:
            return "Alta"
    for palabra in REGLAS_PRIORIDAD["Media"]:
        if palabra in texto:
            return "Media"
    return "Baja"


def buscar_respuesta_frecuente(descripcion):
    texto = limpiar(descripcion)
    for pregunta in RESPUESTAS_FRECUENTES:
        if pregunta in texto:
            return RESPUESTAS_FRECUENTES[pregunta]
    return None
