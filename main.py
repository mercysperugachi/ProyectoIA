import os
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# CARGAR CONFIGURACIÓN
load_dotenv()

app = FastAPI(title="NutriApp API")

# CONFIGURACIÓN DE CORS (Para permitir solicitudes desde cualquier origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos
class Login(BaseModel):
    usuario: str
    password: str

class Consulta(BaseModel):
    texto: str
    usuario_email: str

# Usuarios simulados
USUARIOS_DB = {
    "admin@nutriapp.com": "nutria123",
    "estudiante@epn.edu.ec": "nutria123"
}

# CONFIGURACIÓN DE GEMINI
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# DICCIONARIO PARA GUARDAR LA SESIÓN DE CADA USUARIO
HISTORIAL_SESIONES = {}

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

# funcion para crear una nueva sesión de chat
def obtener_chat_usuario(email: str):
    if email not in HISTORIAL_SESIONES:
        HISTORIAL_SESIONES[email] = client.chats.create(
            model="gemini-2.5-flash", # Modelo de Gemini
            config={"system_instruction": instrucciones_nutriapp}
        )
    return HISTORIAL_SESIONES[email]


# ENDPOINTS (RUTAS)

@app.get("/")
def estado():
    return {"mensaje": "Servidor de NutriApp activo con memoria"}

# Ruta de login
@app.post("/login")
async def login(datos: Login):
    # Verificamos credenciales
    if datos.usuario in USUARIOS_DB and USUARIOS_DB[datos.usuario] == datos.password:
        return {
            "estado": "exitoso",
            "mensaje": f"Bienvenido a NutriApp, {datos.usuario}",
            "token_simulado": "nutria" 
        }
    else:
        return {
            "estado": "error",
            "mensaje": "Credenciales incorrectas"
        }

# RUTA PARA PREGUNTAR (Usa la memoria)
@app.post("/preguntar")
async def preguntar(consulta: Consulta):
    try:
        # Usamos send_message para que Gemini use el historial acumulado
        chat=obtener_chat_usuario(consulta.usuario_email)
        response = chat.send_message(consulta.texto)
        return {"respuesta": response.text}
    except Exception as e:
        return {"error": f"Error al procesar: {str(e)}"}

# RUTA PARA BORRAR LA MEMORIA
@app.post("/reset")
async def reset_chat(usuario_email: str):
    try:
        if usuario_email in HISTORIAL_SESIONES:
            del HISTORIAL_SESIONES[usuario_email]
            return {"mensaje": f"Historial de {usuario_email} reiniciado."}
        else:
            return {"mensaje": "No se encontró historial para este usuario."}
    except Exception as e:
        return {"error": f"Error al reiniciar: {str(e)}"}
    
# RUTA PARA CERRAR SESIÓN
@app.post("/logout")
async def logout():
    return {
        "estado": "exitoso",
        "mensaje": "Sesión cerrada. Tu historial se ha conservado para tu próxima entrada."
    }