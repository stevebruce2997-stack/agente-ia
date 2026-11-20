import csv
import os


def leer_csv(ruta_archivo):
    registros = []
    if not os.path.exists(ruta_archivo):
        return registros
    with open(ruta_archivo, mode="r", newline="", encoding="utf-8-sig") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            registros.append(fila)
    return registros


def escribir_csv(ruta_archivo, columnas, registros):
    with open(ruta_archivo, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        for registro in registros:
            escritor.writerow(registro)
