import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Ahora la función pide obligatoriamente el parámetro 'tipo_usuario'
def iniciar_soporte(tipo_usuario):
    print(f"\n[Sistema] Asignando especialista para perfil: {tipo_usuario}...")
    
    cliente = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # EL ARMARIO DE MÁSCARAS (Diccionario de libretos)
    libretos = {
        "Usuario": (
            "Eres un técnico de Nivel 1. Sé muy paciente, usa analogías de la vida diaria "
            "y no uses jerga técnica. Guía al usuario paso a paso como si fuera un principiante absoluto."
        ),
        "Trabajador": (
            "Eres un ingeniero de soporte técnico senior. Habla de colega a colega, sé directo, "
            "técnico y al grano. Asume que el usuario sabe usar la terminal y comandos avanzados."
        ),
        "Lider": (
            "Eres un analista de soporte corporativo. Enfócate en el impacto al negocio. "
            "Ofrece soluciones temporales rápidas para que el equipo no pierda productividad "
            "y mantén un tono de profundo respeto corporativo."
        ),
        "SuperUsuario": (
            "Eres un conserje tecnológico VIP. Hablas con el CEO/Dueño de la empresa. "
            "Tono de extrema cortesía y guante blanco. Resuelve el problema asumiendo tú la "
            "carga técnica, sin pedirle al usuario que haga tareas manuales tediosas."
        )
    }
    
    # Extraemos el libreto exacto. Si por error llega otro nombre, usa "Usuario" por defecto.
    instruccion_asignada = libretos.get(tipo_usuario, libretos["Usuario"])
    
    try:
        # Inyectamos la máscara al motor 3.8
        chat = cliente.chats.create(
            model="gemini-3.5-flash-lite",
            config={"system_instruction": instruccion_asignada}
        )
        
        print("\n=== SOPORTE TÉCNICO EN LÍNEA ===")
        print("Escribe 'salir' en cualquier momento para terminar el chat.\n")
        
        while True:
            # Agregamos un \n al inicio para separar tu mensaje del texto anterior
            mensaje = input("\n👤 Tú: ")
            
            if mensaje.lower() == 'salir':
                print("\n🤖 Agente: Ha sido un placer ayudarte. ¡Hasta pronto!\n")
                break
                
            if mensaje.strip() == "":
                continue
                
            respuesta = chat.send_message(mensaje)
            # Damos espacio antes de que hable el agente, y dibujamos una línea separadora al final
            print(f"\n🤖 Agente: {respuesta.text}")
            print("—" * 50)
            
    except Exception as e:
        print(f"\n[ERROR DE CONEXIÓN]: {e}")