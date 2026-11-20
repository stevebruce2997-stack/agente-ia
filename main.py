from menu.menu_lider import menu_lider
from menu.menu_superusuario import menu_superusuario
from menu.menu_trabajador import menu_trabajador
from menu.menu_usuario import menu_usuario
from service.clasificador_service import AgenteClasificador
from service.estimador_service import EstimadorService
from service.evaluacion_service import EvaluacionService
from service.ia_service import IAService
from service.ticket_service import TicketService
from util.consola_util import pedir_texto


def mostrar_menu():
    print("\n=== Sistema de Mesa de Ayuda ===")
    print("1. Ingresar como Usuario")
    print("2. Ingresar como Trabajador")
    print("3. Ingresar como Lider de Equipo")
    print("4. Ingresar como SuperUsuario")
    print("5. Salir")


def main():
    ia_service = IAService()
    agente = AgenteClasificador(ia_service)      # por defecto usa reglas
    ticket_service = TicketService(agente=agente)
    estimador = EstimadorService(ticket_service)
    evaluacion = EvaluacionService(ticket_service, ia_service)

    while True:
        mostrar_menu()
        opcion = input("Elige una opcion: ")
        if opcion == "1":
            usuario = pedir_texto("Ingresa tu nombre: ")
            menu_usuario(ticket_service, estimador, usuario)
        elif opcion == "2":
            menu_trabajador(ticket_service, ia_service)
        elif opcion == "3":
            menu_lider(ticket_service)
        elif opcion == "4":
            menu_superusuario(ticket_service, estimador, ia_service, agente, evaluacion)
        elif opcion == "5":
            print("Saliendo del sistema")
            break
        else:
            print("Opcion no valida")


if __name__ == "__main__":
    main()
