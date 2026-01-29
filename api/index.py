import os
from fastapi import FastAPI, Depends, HTTPException
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# MODULOS DE DATOS
from .database import engine, get_db
import models
import schemas

# CARGAR CONFIGURACIÓN
load_dotenv()


app = FastAPI(title="NutriApp API")

origins = [
    "http://localhost:3000", # frontend
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],   # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],   # Permitir todos los headers
)


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
    return {"mensaje": "Servidor de NutriApp corriendo correctamente."}

# Ruta de registro
@app.post("/registro")
def registrar_usuario(datos: schemas.UserSchema, db: Session = Depends(get_db)):
    # Buscamos si el email ya existe en Supabase
    usuario_existe = db.query(models.UsuarioDB).filter(models.UsuarioDB.email == datos.email).first()
    if usuario_existe:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    # Si no existe, lo creamos
    nuevo_usuario = models.UsuarioDB(email=datos.email, password=datos.password)
    db.add(nuevo_usuario)
    db.commit()
    return {"mensaje": f"Usuario {datos.email} guardado en la nube correctamente."} 

# Ruta de login
@app.post("/login")
def login(datos: schemas.UserSchema, db: Session = Depends(get_db)):
    # Buscamos el usuario en la base de datos 
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.email == datos.email).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no registrado")
    
    if usuario.password != datos.password:
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    return {
        "estado": "exitoso",
        "mensaje": f"Bienvenido de nuevo, {usuario.email}",
        "token": "token_supabase_real"
    }

# RUTA PREGUNTAR (guarda en Supabase)
@app.post("/preguntar")
def preguntar(consulta: schemas.Consulta, db: Session = Depends(get_db)):
    try:
        # Obtener respuesta de Gemini (usando memoria RAM para contexto inmediato)
        chat = obtener_chat_usuario(consulta.usuario_email)
        response = chat.send_message(consulta.texto)
        respuesta_texto = response.text

        # GUARDAR EN SUPABASE (Base de Datos)
        nuevo_chat = models.HistorialDB(
            usuario_email=consulta.usuario_email,
            mensaje_usuario=consulta.texto,
            respuesta_ia=respuesta_texto
        )
        db.add(nuevo_chat)
        db.commit()

        # Retornar respuesta al usuario
        return {"respuesta": respuesta_texto}

    except Exception as e:
        return {"error": f"Error IA: {str(e)}"}
    
# RUTA PARA REINICIAR LA SESIÓN DE CHAT
@app.post("/resetear_sesion")
def resetear_chat(usuario_email: str):
    if usuario_email in HISTORIAL_SESIONES:
        del HISTORIAL_SESIONES[usuario_email]
        return {"mensaje": "Memoria reiniciada"}
    return {"mensaje": "No hay memoria activa"}
    
# RUTA PARA CERRAR SESIÓN
@app.post("/logout")
async def logout():
    return {
        "estado": "exitoso",
        "mensaje": "Sesión cerrada. Tu historial se ha conservado para tu próxima entrada."
    }