# Librerías necesarias
import os
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# 1. CARGAR CONFIGURACIÓN
# Carga la API Key desde el archivo .env para mayor seguridad
load_dotenv()

app = FastAPI(title="NutriApp Backend API")

# 2. CONFIGURACIÓN DE CORS
# Esto permite que el frontend de tu compañero (en otro puerto o PC) se comunique con tu API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las conexiones. En producción se limita.
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. CONFIGURACIÓN DE GEMINI
client = genai.Client(api_key="GEMINI_API_KEY")

# Instrucciones de sistema detalladas para darle personalidad a tu app
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

# 4. MODELO DE DATOS
class Consulta(BaseModel):
    texto: str

# 5. ENDPOINTS (RUTAS)
@app.get("/")
def home():
    return {"mensaje": "Servidor de NutriApp activo y listo"}

@app.post("/preguntar")
async def chat_api(consulta: Consulta):
    try:
        # Llamada a la API de Gemini con las instrucciones de sistema
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=consulta.texto,
            config={"system_instruction": instrucciones_nutriapp}
        )
        return {"respuesta": response.text}
    
    except Exception as e:
        return {"error": f"Ocurrió un error en el servidor: {str(e)}"}