from util.consola_util import pedir_texto, mostrar_ticket, mostrar_estimacion_restante
from util.reglas_util import buscar_respuesta_frecuente


def crear_ticket(ticket_service, estimador, usuario):
    print("=== CREAR TICKET ===")
    descripcion = pedir_texto("Describe tu problema: ")
    try:
        ticket = ticket_service.crear_ticket(usuario, descripcion)
        print()
        print("Ticket creado con el numero", ticket.id_ticket)
        print("Derivado al area:", ticket.area, "| Prioridad:", ticket.prioridad)
        mostrar_estimacion_restante(estimador, ticket)
        respuesta = buscar_respuesta_frecuente(descripcion)
        if respuesta is not None:
            print("Sugerencia automatica:", respuesta)
    except ValueError as error:
        print("Error:", error)


def ver_mis_tickets(ticket_service, estimador, usuario):
    print("=== MIS TICKETS ===")
    mis_tickets = ticket_service.tickets_de_usuario(usuario)
    if len(mis_tickets) == 0:
        print("No has creado tickets.")
        return
    for ticket in mis_tickets:
        mostrar_ticket(ticket)
        if ticket.estado == "Pendiente":
            print("   Posicion en la cola de", ticket.area, ":",
                  ticket_service.posicion_en_cola(ticket))
        if ticket.estado != "Resuelto":
            mostrar_estimacion_restante(estimador, ticket)


def menu_usuario(ticket_service, estimador, usuario):
    while True:
        print("\n--- Menu Usuario ---")
        print("1. Crear ticket")
        print("2. Ver mis tickets")
        print("3. Salir")
        opcion = input("Elige una opcion: ")
        if opcion == "1":
            crear_ticket(ticket_service, estimador, usuario)
        elif opcion == "2":
            ver_mis_tickets(ticket_service, estimador, usuario)
        elif opcion == "3":
            break
        else:
            print("Opcion no valida")
