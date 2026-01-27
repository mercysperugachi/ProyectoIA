from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión a la base de datos PostgreSQL (Supabase)  
DATABASE_URL = "postgresql://postgres:Osaodis2479207%40@db.rtgyzuyhvggyuzkfwleh.supabase.co:5432/postgres"

# Configuración del motor
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependencia para usar en las rutas (para abrir y cerrar conexión)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()