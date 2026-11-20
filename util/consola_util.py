from model.constantes import AREAS, PRIORIDADES
from util.tiempo_util import formatear_horas


def pedir_numero(mensaje):
    """Pide un numero y no se cae si el usuario escribe letras."""
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("Debes ingresar un numero.")


def pedir_texto(mensaje):
    while True:
        texto = input(mensaje).strip()
        if texto:
            return texto
        print("Este campo no puede estar vacio.")


def _pedir_de_lista(titulo, opciones):
    print(titulo)
    for i in range(len(opciones)):
        print(i + 1, ".", opciones[i])
    while True:
        numero = pedir_numero("Elige una opcion: ")
        if 1 <= numero <= len(opciones):
            return opciones[numero - 1]
        print("Opcion no valida.")


def pedir_area():
    return _pedir_de_lista("Areas disponibles:", AREAS)


def pedir_prioridad():
    return _pedir_de_lista("Prioridades disponibles:", PRIORIDADES)


def mostrar_ticket(ticket):
    print("Ticket", ticket.id_ticket, "|", ticket.usuario, "|", ticket.area, "|",
          "Prioridad:", ticket.prioridad, "|", ticket.estado)
    print("   Creado:", ticket.fecha_creacion, "| Clasificado por:", ticket.clasificado_por)
    tiempo = formatear_horas(ticket.calcular_duracion_horas())
    if ticket.estado == "Resuelto":
        print("   Tiempo de resolucion:", tiempo)
    else:
        print("   Tiempo transcurrido:", tiempo)
    print("   Problema:", ticket.descripcion)
    if ticket.solucion != "":
        print("   Solucion:", ticket.solucion)


def mostrar_estimacion_restante(estimador, ticket):
    restante = estimador.estimar_restante(ticket)
    if restante is None:
        print("   Tiempo restante estimado: sin datos suficientes")
    elif restante == 0:
        print("   Tiempo estimado superado: ya lleva mas tiempo del habitual")
    else:
        print("   Tiempo restante estimado: ~" + formatear_horas(restante))
