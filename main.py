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
# Importamos tu nuevo agente inteligente
from service.soporte_interactivo import iniciar_soporte

def mostrar_menu():
    print("\n=== Sistema de Mesa de Ayuda ===")
    print("1. Ingresar como Usuario")
    print("2. Ingresar como Trabajador")
    print("3. Ingresar como Lider de Equipo")
    print("4. Ingresar como SuperUsuario")
    print("5. Salir") # La opción 5 vuelve a ser Salir (eliminamos el chat suelto)

def inicio():
    # Inicialización de la arquitectura de tu compañero
    ia_service = IAService()
    agente = AgenteClasificador(ia_service)
    ticket_service = TicketService(agente=agente)
    estimador = EstimadorService(ticket_service)
    evaluacion = EvaluacionService(ticket_service, ia_service)

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            nombre = pedir_texto("Ingrese su nombre: ")
            menu_usuario(ticket_service, estimador, nombre) # Crea su ticket aquí
            # ENRUTAMIENTO DINÁMICO: Al terminar su ticket, le ofrecemos soporte
            if input("\n[Sistema] ¿Desea hablar con el Agente de Soporte Asignado? (s/n): ").lower() == 's':
                iniciar_soporte("Usuario")

        elif opcion == '2':
            menu_trabajador(ticket_service, ia_service)
            if input("\n[Sistema] ¿Desea abrir el canal con el Ingeniero de Soporte Nivel 2? (s/n): ").lower() == 's':
                iniciar_soporte("Trabajador")

        elif opcion == '3':
            menu_lider(ticket_service)
            if input("\n[Sistema] ¿Desea asistencia con el Analista Corporativo? (s/n): ").lower() == 's':
                iniciar_soporte("Lider")

        elif opcion == '4':
            menu_superusuario(ticket_service, estimador, ia_service, agente, evaluacion)
            # El CEO recibe un trato VIP inmediato
            if input("\n[Sistema] ¿Desea asistencia VIP en vivo (Atención Inmediata)? (s/n): ").lower() == 's':
                iniciar_soporte("SuperUsuario")

        elif opcion == '5':
            print("Saliendo del sistema...")
            break
        else:
            print("Opción inválida. Intente nuevamente.")


if __name__ == "__main__":
    inicio()