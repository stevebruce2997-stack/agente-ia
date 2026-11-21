from fastapi import FastAPI
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

app = FastAPI(title="Mesa de Ayuda IA")

@app.get("/")
def inicio():
    return {"mensaje": "¡El servidor web de la Mesa de Ayuda está encendido!"}

# Inicializamos los servicios una sola vez para que la web los pueda usar
ia_service = IAService()
agente = AgenteClasificador(ia_service)
ticket_service = TicketService(agente=agente)
estimador = EstimadorService(ticket_service)
evaluacion = EvaluacionService(ticket_service, ia_service)

# Reemplazamos las opciones del 'while True' y los 'input' por rutas Web (Endpoints)
@app.get("/usuario/{nombre}")
def ruta_usuario(nombre: str):
    # Lógica web para el usuario
    return {"mensaje": f"Bienvenido al sistema, usuario {nombre}. (Ruta web activada)"}

@app.get("/trabajador")
def ruta_trabajador():
    return {"mensaje": "Bienvenido al panel de Trabajador. (Ruta web activada)"}

@app.get("/lider")
def ruta_lider():
    return {"mensaje": "Bienvenido al panel de Líder de Equipo. (Ruta web activada)"}

@app.get("/superusuario")
def ruta_superusuario():
    return {"mensaje": "Bienvenido al panel de SuperUsuario. (Ruta web activada)"}