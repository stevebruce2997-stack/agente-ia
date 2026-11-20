"""Valida el CSV generado por otro LLM antes de usarlo en el proyecto.

Uso (desde la raiz del proyecto, junto a main.py):
    python validar_dataset.py                 -> valida tickets.csv
    python validar_dataset.py otra_ruta.csv   -> valida otro archivo
"""
import csv
import sys
from collections import Counter
from datetime import datetime

from model.constantes import AREAS, ESTADOS, PRIORIDADES, FORMATO_FECHA
from repository.ticket_repository import COLUMNAS, RUTA_POR_DEFECTO
from util.archivo_util import leer_csv
from util.reglas_util import clasificar_area_reglas, definir_prioridad_reglas
from util.tiempo_util import formatear_horas

MINIMO_FILAS = 200
MINIMO_POR_COMBINACION = 15


def leer_encabezado(ruta):
    with open(ruta, mode="r", newline="", encoding="utf-8-sig") as archivo:
        return next(csv.reader(archivo), [])


def parsear(texto):
    try:
        return datetime.strptime(texto, FORMATO_FECHA)
    except (ValueError, TypeError):
        return None


def mediana(lista):
    lista = sorted(lista)
    medio = len(lista) // 2
    if len(lista) % 2 == 1:
        return lista[medio]
    return (lista[medio - 1] + lista[medio]) / 2


def validar(ruta):
    errores = []
    avisos = []

    if leer_encabezado(ruta) != COLUMNAS:
        print("ERROR: el encabezado no coincide.")
        print("  Esperado:", ",".join(COLUMNAS))
        print("  Recibido:", ",".join(leer_encabezado(ruta)))
        return

    filas = leer_csv(ruta)
    print("Filas leidas:", len(filas))
    ids = []
    duraciones = {"Alta": [], "Media": [], "Baja": []}
    combinaciones = Counter()
    estados = Counter()
    descripciones = Counter()
    coincide_area = 0
    coincide_prioridad = 0

    for numero, fila in enumerate(filas, start=2):   # la fila 1 es el encabezado
        linea = "Linea " + str(numero) + ": "
        try:
            ids.append(int(fila["id_ticket"]))
        except ValueError:
            errores.append(linea + "id_ticket no es un numero")
        if not fila["usuario"].strip():
            errores.append(linea + "usuario vacio")
        if not fila["descripcion"].strip():
            errores.append(linea + "descripcion vacia")
        if fila["area"] not in AREAS:
            errores.append(linea + "area no valida: " + fila["area"])
        if fila["prioridad"] not in PRIORIDADES:
            errores.append(linea + "prioridad no valida: " + fila["prioridad"])
        if fila["estado"] not in ESTADOS:
            errores.append(linea + "estado no valido: " + fila["estado"])
        if not fila["clasificado_por"].strip():
            errores.append(linea + "clasificado_por vacio")

        creacion = parsear(fila["fecha_creacion"])
        if creacion is None:
            errores.append(linea + "fecha_creacion con formato invalido")

        if fila["estado"] == "Resuelto":
            cierre = parsear(fila["fecha_cierre"])
            if cierre is None:
                errores.append(linea + "Resuelto sin fecha_cierre valida")
            elif creacion is not None:
                if cierre < creacion:
                    errores.append(linea + "fecha_cierre anterior a fecha_creacion")
                elif fila["prioridad"] in duraciones:
                    horas = (cierre - creacion).total_seconds() / 3600
                    duraciones[fila["prioridad"]].append(horas)
            if not fila["solucion"].strip():
                errores.append(linea + "Resuelto sin solucion")
        else:
            if fila["fecha_cierre"].strip():
                errores.append(linea + "tiene fecha_cierre pero no esta Resuelto")
            if fila["solucion"].strip():
                errores.append(linea + "tiene solucion pero no esta Resuelto")

        estados[fila["estado"]] += 1
        combinaciones[(fila["area"], fila["prioridad"])] += 1
        descripciones[fila["descripcion"].strip().lower()] += 1
        if clasificar_area_reglas(fila["descripcion"]) == fila["area"]:
            coincide_area += 1
        if definir_prioridad_reglas(fila["descripcion"]) == fila["prioridad"]:
            coincide_prioridad += 1

    total = len(filas)
    if total == 0:
        print("ERROR: el archivo no tiene filas.")
        return

    # ---------- avisos de calidad ----------
    if len(set(ids)) != len(ids):
        errores.append("Hay id_ticket repetidos")
    elif ids != list(range(1, len(ids) + 1)):
        avisos.append("Los id_ticket no son consecutivos desde 1")
    if total < MINIMO_FILAS:
        avisos.append("Pocas filas (" + str(total) + "); se recomiendan al menos " + str(MINIMO_FILAS))
    for area in AREAS:
        for prioridad in PRIORIDADES:
            if combinaciones[(area, prioridad)] < MINIMO_POR_COMBINACION:
                avisos.append("Pocos tickets en " + area + " / " + prioridad + ": "
                              + str(combinaciones[(area, prioridad)]))
    repetidas = sum(c - 1 for c in descripciones.values() if c > 1)
    if repetidas / total > 0.25:
        avisos.append("Mas del 25% de las descripciones estan repetidas (" + str(repetidas) + ")")
    resueltos = estados["Resuelto"] / total
    if not 0.75 <= resueltos <= 0.92:
        avisos.append("Porcentaje de resueltos fuera de lo esperado: " + str(round(resueltos * 100)) + "%")
    if all(len(duraciones[p]) > 0 for p in PRIORIDADES):
        m = {p: mediana(duraciones[p]) for p in PRIORIDADES}
        if not m["Alta"] < m["Media"] < m["Baja"]:
            avisos.append("Las medianas de resolucion no crecen de Alta a Baja")
    acuerdo_area = coincide_area / total * 100
    if acuerdo_area > 95:
        avisos.append("Las reglas aciertan el area en " + str(round(acuerdo_area)) +
                      "%: las descripciones usan demasiado nuestras palabras clave (sesgo)")

    # ---------- resumen ----------
    print("\nPor estado:", dict(estados))
    print("Por area:", dict(Counter(f["area"] for f in filas)))
    print("Por prioridad:", dict(Counter(f["prioridad"] for f in filas)))
    print("Descripciones unicas:", len(descripciones), "de", total)
    print("\nMediana de resolucion por prioridad:")
    for prioridad in PRIORIDADES:
        if duraciones[prioridad]:
            print("-", prioridad, ":", formatear_horas(mediana(duraciones[prioridad])),
                  "(" + str(len(duraciones[prioridad])) + " tickets)")
    print("\nAcierto de las reglas actuales sobre este dataset:")
    print("- Area:", round(acuerdo_area, 1), "%")
    print("- Prioridad:", round(coincide_prioridad / total * 100, 1), "%")

    print("\n=== RESULTADO ===")
    if errores:
        print("ERRORES (" + str(len(errores)) + "), corregir antes de usar:")
        for e in errores[:15]:
            print(" -", e)
        if len(errores) > 15:
            print(" ... y", len(errores) - 15, "mas")
    else:
        print("Sin errores de formato.")
    if avisos:
        print("AVISOS:")
        for a in avisos:
            print(" -", a)


if __name__ == "__main__":
    ruta_archivo = sys.argv[1] if len(sys.argv) > 1 else RUTA_POR_DEFECTO
    validar(ruta_archivo)
