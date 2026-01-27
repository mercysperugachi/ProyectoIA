from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Sin clave API")
else:
    print(f"Clave: {api_key[:10]}...")
    client = genai.Client(api_key=api_key)
    
    print("\Modelos disponibles:")
    try:
        # Versión a prueba de fallos: Solo imprime el nombre
        for m in client.models.list():
            print(f" -> {m.name}")
    except Exception as e:
        print(f"Error: {e}")