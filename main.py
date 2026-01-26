import os
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# 1. CARGAR CONFIGURACIÓN
load_dotenv()

app = FastAPI(title="NutriApp API con Memoria y Reset")

# 2. CONFIGURACIÓN DE CORS (Para permitir solicitudes desde cualquier origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. CONFIGURACIÓN DE GEMINI
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

instrucciones_nutriapp = """
CONTEXTO:
Eres el asistente virtual experto de 'NutriApp', una plataforma para mejorar la salud alimenticia.

PERSONALIDAD Y TONO:
- Eres motivador, profesional y amable.
- Tus respuestas deben ser claras y directas, ideales para leerse en una app móvil.

REGLAS ESPECÍFICAS:
1. Especialización: Solo hablas de nutrición, recetas, ejercicio y salud. 
2. Restricción: Si preguntan de otros temas, declina amablemente diciendo que eres un experto en nutrición.
3. Formato: Si das una lista de ingredientes o pasos, usa viñetas para que se vea ordenado.
4. Seguridad: Siempre termina recomendaciones de dietas con la frase: 'Recuerda consultar con un profesional de la salud'.
"""

# 4. VARIABLE GLOBAL DE SESIÓN (La memoria)
# Esta función crea la sesión de chat con tus instrucciones
def crear_nueva_sesion():
    return client.chats.create(
        model="gemini-2.0-flash",
        config={"system_instruction": instrucciones_nutriapp}
    )

# Inicializamos la primera sesión
chat_session = crear_nueva_sesion()

# 5. MODELO DE DATOS
class Consulta(BaseModel):
    texto: str

# 6. ENDPOINTS (RUTAS)

@app.get("/")
def estado():
    return {"mensaje": "Servidor de NutriApp activo con memoria"}

# RUTA PARA PREGUNTAR (Usa la memoria)
@app.post("/preguntar")
async def preguntar(consulta: Consulta):
    try:
        # Usamos send_message para que Gemini use el historial acumulado
        response = chat_session.send_message(consulta.texto)
        return {"respuesta": response.text}
    except Exception as e:
        return {"error": f"Error al procesar: {str(e)}"}

# RUTA PARA BORRAR LA MEMORIA
@app.post("/reset")
async def reset_chat():
    global chat_session
    try:
        # Reemplazamos la sesión actual por una nueva y vacía
        chat_session = crear_nueva_sesion()
        return {"mensaje": "Historial de NutriApp borrado con éxito. ¡Chat reiniciado!"}
    except Exception as e:
        return {"error": f"No se pudo resetear: {str(e)}"}