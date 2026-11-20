from util.consola_util import (pedir_area, pedir_numero, pedir_prioridad,
                               pedir_texto, mostrar_ticket)
from util.tiempo_util import formatear_horas
from model.constantes import AREAS, ESTADOS, PRIORIDADES


def ver_todos(ticket_service):
    tickets = ticket_service.listar_tickets()
    if len(tickets) == 0:
        print("No hay tickets registrados.")
    for ticket in tickets:
        mostrar_ticket(ticket)


def ver_estadisticas(ticket_service, estimador):
    datos = ticket_service.estadisticas()
    print("Total de tickets:", datos["total"])
    print("Tickets por estado:")
    for estado in datos["por_estado"]:
        print("-", estado, ":", datos["por_estado"][estado])
    print("Tickets por area:")
    for area in datos["por_area"]:
        info = datos["por_area"][area]
        print("-", area, ":", info["recibidos"], "| promedio de resolucion:",
              formatear_horas(info["promedio_horas"]))
    print("Promedio general de resolucion:", formatear_horas(datos["promedio_horas"]))
    print()
    print("Tiempo estimado de resolucion (agente estimador):")
    for area in AREAS:
        for prioridad in PRIORIDADES:
            horas = estimador.estimar_horas(area, prioridad)
            if horas is not None:
                print("-", area, "/", prioridad, ": ~" + formatear_horas(horas))


def modificar(ticket_service):
    id_ticket = pedir_numero("Numero de ticket a modificar: ")
    ticket = ticket_service.buscar_ticket(id_ticket)
    if ticket is None:
        print("No se encontro el ticket.")
        return
    mostrar_ticket(ticket)
    usuario = pedir_texto("Nuevo usuario: ")
    area = pedir_area()
    descripcion = pedir_texto("Nueva descripcion: ")
    prioridad = pedir_prioridad()
    print("Estados:", ", ".join(ESTADOS))
    estado = pedir_texto("Nuevo estado: ")
    try:
        ticket_service.modificar_ticket(id_ticket, usuario, area, descripcion, prioridad, estado)
        print("Ticket modificado.")
    except ValueError as error:
        print("Error:", error)


def eliminar(ticket_service):
    id_ticket = pedir_numero("Numero de ticket a eliminar: ")
    try:
        ticket_service.eliminar_ticket(id_ticket)
        print("Ticket eliminado.")
    except ValueError as error:
        print("Error:", error)


def estimar_tiempo(estimador):
    area = pedir_area()
    prioridad = pedir_prioridad()
    horas = estimador.estimar_horas(area, prioridad)
    if horas is None:
        print("Aun no hay tickets resueltos para estimar.")
    else:
        print("Tiempo promedio esperado: ~" + formatear_horas(horas))


def consultar_ia(ticket_service, ia_service):
    print("Ejemplos:")
    print("- Resume la situacion de los tickets.")
    print("- Que area tiene mas tickets?")
    print("- Cuantos tickets pendientes de prioridad alta hay?")
    pregunta = pedir_texto("Pregunta: ")
    try:
        respuesta = ia_service.consultar(pregunta, ticket_service.listar_tickets())
        print()
        print("Respuesta de la IA:")
        print(respuesta)
    except Exception as error:
        print("Error al consultar la IA:", error)


def mostrar_resultado(nombre, resultado):
    print(nombre + ":")
    print("   Acierto en area:", round(resultado["acierto_area"], 1), "%")
    print("   Acierto en prioridad:", round(resultado["acierto_prioridad"], 1), "%")
    print("   Tickets de prioridad Alta detectados:", resultado["alta_detectadas"],
          "de", resultado["alta_total"])


def evaluar_clasificadores(evaluacion):
    print("=== EVALUAR CLASIFICADORES (reglas vs IA) ===")
    total = len(evaluacion.tickets_de_referencia())
    if total == 0:
        print("No hay tickets de referencia (clasificado_por = manual).")
        return
    print("Tickets de referencia en el dataset:", total)
    cantidad = pedir_numero("Cuantos tickets evaluar? (la IA es lenta, por ejemplo 30): ")
    if cantidad <= 0:
        print("La cantidad debe ser mayor a cero.")
        return
    muestra = evaluacion.obtener_muestra(cantidad)
    print("Evaluando", len(muestra), "tickets...")
    print()
    mostrar_resultado("REGLAS", evaluacion.evaluar_reglas(muestra))
    try:
        mostrar_resultado("IA", evaluacion.evaluar_ia(muestra))
    except Exception as error:
        print("No se pudo evaluar la IA:", error)


def cambiar_modo_ia(agente):
    agente.usar_ia = not agente.usar_ia
    if agente.usar_ia:
        print("Clasificacion con IA ACTIVADA (la primera vez descarga los modelos).")
    else:
        print("Clasificacion con IA DESACTIVADA (se usan las reglas).")


def menu_superusuario(ticket_service, estimador, ia_service, agente, evaluacion):
    while True:
        modo = "IA" if agente.usar_ia else "reglas"
        print("\n--- Menu SuperUsuario (clasificacion actual: " + modo + ") ---")
        print("1. Ver todos los tickets")
        print("2. Ver estadisticas")
        print("3. Modificar un ticket")
        print("4. Eliminar un ticket")
        print("5. Estimar tiempo de resolucion")
        print("6. Consultar datos con IA")
        print("7. Activar/desactivar IA en la clasificacion")
        print("8. Evaluar clasificadores (reglas vs IA)")
        print("9. Salir")
        opcion = input("Elige una opcion: ")
        if opcion == "1":
            ver_todos(ticket_service)
        elif opcion == "2":
            ver_estadisticas(ticket_service, estimador)
        elif opcion == "3":
            modificar(ticket_service)
        elif opcion == "4":
            eliminar(ticket_service)
        elif opcion == "5":
            estimar_tiempo(estimador)
        elif opcion == "6":
            consultar_ia(ticket_service, ia_service)
        elif opcion == "7":
            cambiar_modo_ia(agente)
        elif opcion == "8":
            evaluar_clasificadores(evaluacion)
        elif opcion == "9":
            break
        else:
            print("Opcion no valida")
