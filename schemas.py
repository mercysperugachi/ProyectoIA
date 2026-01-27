from pydantic import BaseModel

# Lo que recibimos para Login/Registro
class UserSchema(BaseModel):
    email: str
    password: str

# Lo que recibimos para preguntar a la IA
class Consulta(BaseModel):
    texto: str
    usuario_email: str