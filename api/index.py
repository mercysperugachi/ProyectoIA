import os
import sys
import numpy as np
import joblib
from fastapi import FastAPI, Depends, HTTPException
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# LIBRERÍAS DE MACHINE LEARNING 
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# MODULOS DE DATOS (Con imports relativos correctos)
from .database import engine, get_db
from . import models
from . import schemas

# CARGAR CONFIGURACIÓN
load_dotenv()

try:
    models.Base.metadata.create_all(bind=engine)
    print("Base de datos conectada y tablas verificadas.")
except Exception as e:
    print(f"Error conectando a la BD: {e}")

app = FastAPI(title="NutriApp API")

# Configuración CORS
origins = [
    "http://localhost:3000", # frontend local
    "http://127.0.0.1:3000",
    "https://tu-frontend-en-vercel.vercel.app", 
    "*" # Permitir todos para evitar errores por ahora
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permitir todos para evitar errores por ahora
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODELO_ML = None
METRICAS_ML = {
    "estado": "no entrenado",
    "mse": None,
    "r2": None
}

# --- CONFIGURACIÓN DE GEMINI (VERSIÓN ESTÁNDAR) ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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

def obtener_chat_usuario(email: str):
    if email not in HISTORIAL_SESIONES:
        # 1. Definimos el modelo aquí (usando gemini-1.5-flash que es estable)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=instrucciones_nutriapp
        )
        # 2. Iniciamos el chat correctamente
        HISTORIAL_SESIONES[email] = model.start_chat(history=[])
    
    return HISTORIAL_SESIONES[email]


# ENDPOINTS (RUTAS)

@app.get("/")
def estado():
    return {"mensaje": "Servidor de NutriApp corriendo correctamente."}

# RUTAS DE MACHINE LEARNING
@app.post("/ml/train")
def entrenar_modelo(datos: schemas.DatosEntrenamiento):
    """
    Recibe datos históricos y entrena un modelo de Regresión Lineal.
    INCLUYE PROTECCIÓN CONTRA ERRORES MATEMÁTICOS (NaN).
    """
    global MODELO_ML, METRICAS_ML
    try:
        # 1. Preparación de datos
        X = np.column_stack((datos.peso, datos.altura))
        y = np.array(datos.calorias_reales)

        # Validación: Necesitamos al menos 2 filas de datos
        if len(X) < 2:
            return {"error": "Por favor envía al menos 2 ejemplos de datos para entrenar."}

        # 2. Configuración (con seguridad por si config viene vacío)
        cfg = datos.config if datos.config else {}
        test_size = cfg.get("test_size", 0.2)
        random_state = cfg.get("random_state", 42)

        # 3. División del Dataset
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # 4. Entrenamiento
        model = LinearRegression()
        model.fit(X_train, y_train)

        # 5. Evaluación (Protegida)
        if len(X_test) < 2:
            # Si el set de prueba es muy chico, no calculamos métricas complejas
            mse = 0.0
            r2 = 0.0
        else:
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

        # --- AQUÍ ESTÁ EL TRUCO PARA EVITAR EL ERROR 500 ---
        # Si el cálculo matemático da "NaN" (Not a Number), lo cambiamos a 0.0
        safe_mse = 0.0 if np.isnan(mse) else mse
        safe_r2 = 0.0 if np.isnan(r2) else r2

        # 6. Guardar en memoria
        MODELO_ML = model
        METRICAS_ML = {
            "estado": "Entrenado", 
            "mse": safe_mse, 
            "r2": safe_r2, 
            "configuracion_usada": cfg
        }

        return {"mensaje": "Modelo entrenado exitosamente", "metricas": METRICAS_ML}

    except Exception as e:
        print(f"Error en entrenamiento: {e}") # Ver error en consola
        return {"error": f"Fallo durante el entrenamiento: {str(e)}"}
    
# --- MOSTRAR MÉTRICAS ---
@app.get("/ml/metrics")
def obtener_metricas():
    """ Devuelve el rendimiento del último entrenamiento realizado. """
    return METRICAS_ML

# --- RECIBIR UN NUEVO CASO (PREDICCIÓN) ---
@app.post("/ml/predict")
def predecir_calorias(caso: schemas.DatosPrediccion):
    """ Usa el modelo entrenado para predecir calorías de un nuevo usuario. """
    global MODELO_ML
    
    # Validación: No podemos predecir si no hemos entrenado
    if MODELO_ML is None:
        raise HTTPException(status_code=400, detail="El modelo no ha sido entrenado. Usa /ml/train primero.")
    
    # Inferencia
    datos_entrada = np.array([[caso.peso, caso.altura]])
    prediccion = MODELO_ML.predict(datos_entrada)[0]
    
    return {
        "input": caso,
        "prediccion_calorias": round(prediccion, 2),
        "fuente": "Modelo de Machine Learning (Regresión Lineal)"
    }

# Ruta de registro
@app.post("/registro")
def registrar_usuario(datos: schemas.UserSchema, db: Session = Depends(get_db)):
    # Buscamos si el email ya existe
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

# RUTA PREGUNTAR
@app.post("/preguntar")
def preguntar(consulta: schemas.Consulta, db: Session = Depends(get_db)):
    try:
        # Obtener el chat del usuario
        chat = obtener_chat_usuario(consulta.usuario_email)
        
        # Enviar mensaje a Gemini
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
        # Si falla la sesión, intentamos resetearla para la próxima
        if consulta.usuario_email in HISTORIAL_SESIONES:
            del HISTORIAL_SESIONES[consulta.usuario_email]
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