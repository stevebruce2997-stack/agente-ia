from util.consola_util import pedir_area, mostrar_ticket
from util.tiempo_util import formatear_horas


def informe_general(ticket_service):
    datos = ticket_service.estadisticas()
    print("Total de tickets:", datos["total"])
    print("Tickets recibidos por area:")
    for area in datos["por_area"]:
        info = datos["por_area"][area]
        print("-", area, ":", info["recibidos"], "recibidos |", info["resueltos"],
              "resueltos | promedio de resolucion:", formatear_horas(info["promedio_horas"]))
    print("Promedio general de resolucion:", formatear_horas(datos["promedio_horas"]))


def tickets_del_equipo(ticket_service):
    area = pedir_area()
    tickets = ticket_service.tickets_por_area(area)
    if len(tickets) == 0:
        print("No hay tickets en esta area.")
    for ticket in tickets:
        mostrar_ticket(ticket)


def cola_por_area(ticket_service):
    area = pedir_area()
    cola = ticket_service.cola_atencion(area)
    if len(cola) == 0:
        print("No hay tickets pendientes en esta area.")
    for ticket in cola:
        mostrar_ticket(ticket)


def historial_por_area(ticket_service):
    area = pedir_area()
    resueltos = ticket_service.historial_resueltos(area)
    if len(resueltos) == 0:
        print("No hay tickets resueltos en esta area.")
    for ticket in resueltos:
        mostrar_ticket(ticket)


def menu_lider(ticket_service):
    while True:
        print("\n--- Menu Lider de Equipo ---")
        print("1. Ver informe general")
        print("2. Ver todos los tickets de un area")
        print("3. Ver cola de atencion por area")
        print("4. Ver historial de resueltos por area")
        print("5. Salir")
        opcion = input("Elige una opcion: ")
        if opcion == "1":
            informe_general(ticket_service)
        elif opcion == "2":
            tickets_del_equipo(ticket_service)
        elif opcion == "3":
            cola_por_area(ticket_service)
        elif opcion == "4":
            historial_por_area(ticket_service)
        elif opcion == "5":
            break
        else:
            print("Opcion no valida")
