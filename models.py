from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

# Tabla de Usuarios
class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

# Tabla deHistorial de Chats
class HistorialDB(Base):
    __tablename__ = "historial_chats"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_email = Column(String, index=True)
    mensaje_usuario = Column(Text) # Pregunta
    respuesta_ia = Column(Text)    # Respuesta
    fecha = Column(DateTime(timezone=True), server_default=func.now())