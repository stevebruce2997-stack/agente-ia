def formatear_horas(horas):
    """Convierte horas decimales a un texto como '2 h 15 min' o '1 d 3 h'."""
    minutos_totales = int(round(horas * 60))
    dias = minutos_totales // 1440
    horas_resto = (minutos_totales % 1440) // 60
    minutos = minutos_totales % 60
    if dias > 0:
        return str(dias) + " d " + str(horas_resto) + " h"
    if horas_resto > 0:
        return str(horas_resto) + " h " + str(minutos) + " min"
    return str(minutos) + " min"


def promedio(lista):
    if len(lista) == 0:
        return 0.0
    return sum(lista) / len(lista)
