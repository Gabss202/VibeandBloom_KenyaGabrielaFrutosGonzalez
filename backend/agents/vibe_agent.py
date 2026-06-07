from google import genai
import os
from dotenv import load_dotenv
import base64

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class VibeAgent:
    def __init__(self):
        self.model = client.models

    def detectar_desde_texto(self, texto: str) -> dict:
        prompt = f"""
        Eres un experto en emociones y literatura. Analiza este texto y detecta el vibe emocional.
        Texto: "{texto}"
        
        Responde EXACTAMENTE en este formato:
        VIBE: [una palabra: melancolico/romantico/misterioso/cozy/aventurero/oscuro/esperanzador]
        TAGS: [5 palabras separadas por comas]
        GENEROS: [3 géneros literarios separados por comas]
        EXPLICACION: [una oración explicando por qué]
        """
        response = self.model.generate_content(prompt)
        return self._parsear_respuesta(response.text, "texto")

    def detectar_desde_imagen(self, imagen_bytes: bytes) -> dict:
        imagen_base64 = base64.b64encode(imagen_bytes).decode("utf-8")
        prompt = """
        Analiza esta imagen y detecta el vibe emocional para recomendar libros.
        
        Responde EXACTAMENTE en este formato:
        VIBE: [una palabra: melancolico/romantico/misterioso/cozy/aventurero/oscuro/esperanzador]
        TAGS: [5 palabras separadas por comas]
        GENEROS: [3 géneros literarios separados por comas]
        EXPLICACION: [una oración explicando por qué]
        """
        response = self.model.generate_content([
            {"mime_type": "image/jpeg", "data": imagen_base64},
            prompt
        ])
        return self._parsear_respuesta(response.text, "imagen")

    def detectar_desde_cancion(self, nombre_cancion: str, artista: str = "") -> dict:
        prompt = f"""
        Analiza la canción "{nombre_cancion}" {f"de {artista}" if artista else ""}.
        Basándote en el género musical, letra típica y mood de esta canción,
        detecta el vibe emocional para recomendar libros.
        
        Responde EXACTAMENTE en este formato:
        VIBE: [una palabra: melancolico/romantico/misterioso/cozy/aventurero/oscuro/esperanzador]
        TAGS: [5 palabras separadas por comas]
        GENEROS: [3 géneros literarios separados por comas]
        EXPLICACION: [una oración explicando por qué]
        """
        response = self.model.generate_content(prompt)
        return self._parsear_respuesta(response.text, "cancion")

    def detectar_desde_video(self, url_youtube: str) -> dict:
        prompt = f"""
        Analiza este video de YouTube: {url_youtube}
        Basándote en el título y contexto de la URL, detecta el vibe emocional
        para recomendar libros.
        
        Responde EXACTAMENTE en este formato:
        VIBE: [una palabra: melancolico/romantico/misterioso/cozy/aventurero/oscuro/esperanzador]
        TAGS: [5 palabras separadas por comas]
        GENEROS: [3 géneros literarios separados por comas]
        EXPLICACION: [una oración explicando por qué]
        """
        response = self.model.generate_content(prompt)
        return self._parsear_respuesta(response.text, "video")

    def _parsear_respuesta(self, texto: str, tipo: str) -> dict:
        lineas = texto.strip().split("\n")
        resultado = {"tipo": tipo, "vibe": "", "tags": [], "generos": [], "explicacion": ""}
        for linea in lineas:
            if linea.startswith("VIBE:"):
                resultado["vibe"] = linea.replace("VIBE:", "").strip().lower()
            elif linea.startswith("TAGS:"):
                resultado["tags"] = [t.strip() for t in linea.replace("TAGS:", "").split(",")]
            elif linea.startswith("GENEROS:"):
                resultado["generos"] = [g.strip() for g in linea.replace("GENEROS:", "").split(",")]
            elif linea.startswith("EXPLICACION:"):
                resultado["explicacion"] = linea.replace("EXPLICACION:", "").strip()
        return resultado