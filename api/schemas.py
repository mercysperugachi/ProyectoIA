from pydantic import BaseModel

# Lo que recibimos para Login/Registro
class UserSchema(BaseModel):
    email: str
    password: str

# Lo que recibimos para preguntar a la IA
class Consulta(BaseModel):
    texto: str
    usuario_email: str

# --- ESQUEMAS PARA MACHINE LEARNING ---

# Datos para entrenar el modelo (recibimos una lista de casos)
class DatosEntrenamiento(BaseModel):
    peso: list[float]  # Ej: [70, 80, 60]
    altura: list[float] # Ej: [1.70, 1.80, 1.65]
    calorias_reales: list[float] # Ej: [2000, 2500, 1800] 
    config: dict = {"test_size": 0.2, "random_state": 42} 

# Datos para pedir una predicción (un caso nuevo)
class DatosPrediccion(BaseModel):
    peso: float
    altura: float