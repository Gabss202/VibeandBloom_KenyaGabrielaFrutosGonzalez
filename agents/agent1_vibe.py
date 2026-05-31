from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Inicializamos el cliente de Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Configuración del modo desarrollo (True para usar respuestas simuladas si no tienes cuota)
MODO_DESARROLLO = os.getenv("MODO_DESARROLLO", "false").lower() == "true"

VIBES_PREDEFINIDAS = {
    "cozy": ["romance suave", "amistad", "hogareño", "reconfortante", "slow life"],
    "nostalgica": ["melancolía", "recuerdos", "pérdida", "infancia", "tiempo pasado"],
    "romantica": ["amor intenso", "tensión sexual", "enemies to lovers", "slow burn"],
    "aventurera": ["viajes", "acción", "descubrimiento", "libertad", "riesgo"],
    "misteriosa": ["secretos", "thriller", "oscuridad", "suspenso", "giros"],
    "oscura": ["trauma", "antihéroe", "morally grey", "dark romance", "tragedia"],
    "magica": ["fantasía", "mundos alternativos", "magia", "profecías", "destino"]
}

def detectar_vibe(descripcion: str) -> dict:
    """
    Analiza el texto del usuario para extraer el mood y las vibes utilizando IA.
    Si MODO_DESARROLLO es True, simula la respuesta para ahorrar cuota de API.
    """
    # --- MODO SIMULADO / FALLBACK RÁPIDO ---
    if MODO_DESARROLLO:
        print("⚡ [MODO DESARROLLO] Usando respuesta simulada local...")
        return {
            "emociones": ["nostalgia", "rabia contenida", "tristeza"],
            "arquetipos": ["princesa atrapada", "bufón resentido"],
            "vibes": ["enemies to lovers", "traición", "romance oscuro"],
            "tono": "oscuro",
            "generos_sugeridos": ["fantasía oscura", "drama real"],
            "resumen_vibe": "Un silencio cargado de resentimiento y lazos rotos en el palacio."
        }

    # --- MODO REAL CON IA ---
    prompt = f"""
    Eres un agente experto en análisis literario y emocional llamado Vibe Reader.
    
    El usuario describió esto:
    "{descripcion}"
    
    Analiza el texto y llena la siguiente estructura JSON exacta:
    {{
        "emociones": ["emoción1", "emoción2"],
        "arquetipos": ["arquetipo1", "arquetipo2"],
        "vibes": ["vibe1", "vibe2"],
        "tono": "oscuro/suave/intenso/mágico/nostálgico/romántico/aventurero",
        "generos_sugeridos": ["género1", "género2"],
        "resumen_vibe": "Una frase poética que describe la vibe detectada"
    }}
    """

    try:
        # Forzamos a la API a devolver un JSON puro usando response_mime_type
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        
        # Al ser JSON nativo, no necesitamos limpiar comillas ni ```json, pasa directo
        return json.loads(response.text.strip())
        
    except Exception as e:
        print(f"⚠️ Error en API o JSON (usando fallback seguro): {e}")
        return {
            "emociones": ["indefinida"],
            "arquetipos": ["personaje complejo"],
            "vibes": ["misteriosa"],
            "tono": "intenso",
            "generos_sugeridos": ["ficción contemporánea"],
            "resumen_vibe": "Una historia que se siente entre sombras y luz"
        }

def vibe_mas_cercana(vibes_detectadas: list) -> str:
    """ Mapea las palabras clave detectadas con nuestro diccionario del sistema experto """
    for vibe_detectada in vibes_detectadas:
        for vibe_key, keywords in VIBES_PREDEFINIDAS.items():
            for keyword in keywords:
                if keyword.lower() in vibe_detectada.lower():
                    return vibe_key
    return "misteriosa"

if __name__ == "__main__":
    descripcion = """
    Estaba viendo TikTok y vi una animación de una princesa a la que van 
    a casar por el reino pero está triste, voltea a ver a su bufón que 
    la mira con rabia.
    """
    
    print("🌿 Analizando vibe...\n")
    resultado = detectar_vibe(descripcion)
    
    print("Emociones detectadas:", resultado.get("emociones"))
    print("Arquetipos:", resultado.get("arquetipos"))
    print("Vibes:", resultado.get("vibes"))
    print("Tono:", resultado.get("tono"))
    print("Géneros sugeridos:", resultado.get("generos_sugeridos"))
    print("\n✨ Resumen de tu vibe:")
    print(resultado.get("resumen_vibe"))
    
    vibe = vibe_mas_cercana(resultado.get("vibes", []))
    print(f"\n🎯 Vibe más cercana para la base de datos: {vibe}")