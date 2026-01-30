# NutriApp API - Backend de Nutrición Inteligente

![Estado](https://img.shields.io/badge/Estado-Finalizado-green?style=for-the-badge)
![Python Version](https://img.shields.io/badge/python-3.13-blue?style=for-the-badge&logo=python&logoColor=white)
![Framework](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![AI](https://img.shields.io/badge/AI-Google_Gemini-orange?style=for-the-badge&logo=google&logoColor=white)
![Database](https://img.shields.io/badge/Database-PostgreSQL_Supabase-336791?style=for-the-badge&logo=postgresql&logoColor=white)

> *Institución:* Escuela Politécnica Nacional (EPN)
> *Carrera:* Tecnología Superior en Desarrollo de Software
> *Asignatura:* Fundamentos de Inteligencia Artificial
> *Semestre:* 2025-B

El presente proyecto implementa una *API REST* moderna y escalable, desarrollada bajo el ecosistema de *Python* y *FastAPI. El sistema está diseñado para actuar como el motor de una plataforma de salud ("NutriApp"), integrando capacidades de **Inteligencia Artificial Generativa* (Gemini) para asistencia conversacional y *Machine Learning* (Scikit-Learn) para predicciones calóricas personalizadas.

La arquitectura sigue los estándares de desarrollo moderno, garantizando validación de datos con Pydantic, manejo de sesiones, y persistencia eficiente en la nube mediante *PostgreSQL (Supabase)* y *SQLAlchemy*.

## 1. Demostración Funcional (Evidencia)
A continuación, se presenta la demostración operativa del backend consumido mediante la interfaz Swagger UI y las pruebas de los modelos de IA y ML.

### Video Explicativo del Proyecto
[(https://youtu.be/60bg9Hq-gcQ)]

---

## 2. Estructura del Proyecto
El código sigue una arquitectura modular para asegurar la escalabilidad y el mantenimiento del servicio. A continuación se detalla la organización de los directorios y archivos principales:

text
PROYECTOIA
├──   api
│   ├── index.py               # Controlador principal: Define rutas (Endpoints) y lógica de IA/ML.
│   ├── database.py            # Configuración de conexión a PostgreSQL (SQLAlchemy).
│   ├── models.py              # Entidades ORM que mapean las tablas (Usuarios, Historial).
│   └── schemas.py             # Modelos Pydantic para validación de datos (Request/Response).
├──    __pycache__             # Archivos compilados de Python.
├── .env                       # Variables de entorno (API Keys, Credenciales DB).
├── .gitignore                 # Exclusiones de Git.
├── requirements.txt           # Lista de dependencias y librerías.
└── vercel.json                # Configuración para despliegue Serverless.
 
## 3. Stack Tecnológico

| Componente | Tecnología Seleccionada | Detalle / Versión |

| *Lenguaje Core* | Python | Versión 3.13 |
| *Framework Web* | Spring Boot | 3.2.1 |
| *Inteligencia Artificial* | Google Gemini | Modelo 2.5 Flash (Generativo) |
| *Machine Learning* | Scikit-Learn | Regresión Lineal & Métricas |
| *Base de Datos* | PostgreSQL (Supabase) | Relacional en la Nube |
| *ORM* | SQLAlchemy | Gestión de consultas SQL |
| *Servidor* | Uvicorn | Servidor ASGI |


## 4. Guía de Instalación y Despliegue
   
### 4.1. Requisitos del Entorno
Para garantizar la correcta ejecución del servicio, asegúrese de cumplir con:

1.  *Python:* Versión 3.10 o superior.
2.  *Clave API:* Google AI Studio (Gemini).
3.  *Base de Datos:* URL de conexión a PostgreSQL (Supabase).

### 4.2. Ejecución desde Código Fuente
1.  Clone el repositorio o descargue el código fuente.
2.  Cree un entorno virtual e instale las dependencias:
   
http
Bash
pip install -r requirements.txt
Configure el archivo .env con sus credenciales.

Ejecute la aplicación:

http
Bash
python -m uvicorn api.index:app --reload

### 4.3. URL Base
Una vez iniciada la aplicación, la API estará escuchando en:

http
[http://127.0.0.1:8000](http://127.0.0.1:8000)


## 5. Documentación Interactiva (Swagger UI)
El proyecto utiliza Swagger UI generado automáticamente por FastAPI para probar los endpoints en tiempo real.

### ¿Para qué sirve esta URL?
La dirección:

http
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

proporciona una interfaz gráfica web que permite:

### 5.1. Verificar Endpoints de IA:
Probar el chat con Gemini (/preguntar) y ver cómo se mantiene el contexto de la conversación.

### 5.2. Entrenar Modelo ML:
Enviar datasets JSON al endpoint /ml/train y observar cómo el sistema recalcula el error cuadrático medio (MSE) y la precisión ($R^2$).

### 5.3. Gestión de Usuarios:
Registrar usuarios y simular el inicio de sesión contra la base de datos real en Supabase.

## 6. Endpoints Principales 

| Método | Endpoint | Descripción |

| *POST* | /registro | Registrar un nuevo usuario en la base de datos. |
| *POST* | /login | Autenticar credenciales de usuario. |
| *POST* | /preguntar | Enviar consulta al Asistente Nutricional (Gemini). |
| *POST* | /ml/train | Re-entrenar el modelo de predicción calórica. |
| *POST* | /ml/predict | Predecir calorías para un caso específico (Peso/Altura). |
| *GET* | /ml/metrics | Consultar la precisión actual del modelo de ML. |
