from util.consola_util import pedir_area, pedir_numero, pedir_texto, mostrar_ticket


def ver_cola(ticket_service, area):
    cola = ticket_service.cola_atencion(area)
    if len(cola) == 0:
        print("No hay tickets pendientes.")
        return
    print("Cola de atencion (primero el mas prioritario):")
    for i in range(len(cola)):
        print("Posicion", i + 1)
        mostrar_ticket(cola[i])


def atender_siguiente(ticket_service, area):
    ticket = ticket_service.atender_siguiente(area)
    if ticket is None:
        print("No hay tickets pendientes.")
    else:
        print("Ahora atiendes:")
        mostrar_ticket(ticket)


def resolver(ticket_service, area):
    id_ticket = pedir_numero("Numero de ticket a resolver: ")
    solucion = pedir_texto("Describe la solucion aplicada: ")
    try:
        ticket_service.resolver_ticket(id_ticket, solucion, area)
        print("Ticket resuelto.")
    except ValueError as error:
        print("Error:", error)


def historial(ticket_service, area):
    resueltos = ticket_service.historial_resueltos(area)
    if len(resueltos) == 0:
        print("Aun no hay tickets resueltos en tu area.")
    for ticket in resueltos:
        mostrar_ticket(ticket)


def sugerencia_ia(ticket_service, ia_service, area):
    id_ticket = pedir_numero("Numero de ticket: ")
    ticket = ticket_service.buscar_ticket(id_ticket)
    if ticket is None or ticket.area != area:
        print("No se encontro ese ticket en tu area.")
        return
    try:
        print("Sugerencia de la IA (revisala antes de aplicarla):")
        print(ia_service.sugerir_respuesta(ticket.descripcion, ticket.area))
    except Exception as error:
        print("No se pudo usar la IA:", error)


def menu_trabajador(ticket_service, ia_service):
    print("\nIdentifica tu area de trabajo")
    area = pedir_area()
    while True:
        print("\n--- Menu Trabajador (" + area + ") ---")
        print("1. Ver cola de atencion de mi area")
        print("2. Atender siguiente ticket")
        print("3. Resolver un ticket")
        print("4. Ver historial de resueltos")
        print("5. Pedir sugerencia de IA para un ticket")
        print("6. Salir")
        opcion = input("Elige una opcion: ")
        if opcion == "1":
            ver_cola(ticket_service, area)
        elif opcion == "2":
            atender_siguiente(ticket_service, area)
        elif opcion == "3":
            resolver(ticket_service, area)
        elif opcion == "4":
            historial(ticket_service, area)
        elif opcion == "5":
            sugerencia_ia(ticket_service, ia_service, area)
        elif opcion == "6":
            break
        else:
            print("Opcion no valida")
