import requests
import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class RecommenderAgent:
    def __init__(self, db):
        self.db = db
        self.open_library_url = "https://openlibrary.org/search.json"

    def aplicar_reglas(self, usuario_id: int, vibe_data: dict) -> dict:
        from models import Biblioteca, Reseña
        inferencias = []
        generos = vibe_data.get("generos", [])
        tags = vibe_data.get("tags", [])

        libros_leidos = self.db.query(Biblioteca).filter(
            Biblioteca.usuario_id == usuario_id,
            Biblioteca.estado == "leido"
        ).count()

        if libros_leidos > 20:
            inferencias.append("Usuario experto → se priorizan libros menos conocidos")

        vibe = vibe_data.get("vibe", "")
        mapa_vibe = {
            "melancolico": ["drama", "literary fiction", "poetry"],
            "romantico": ["romance", "love story", "contemporary romance"],
            "misterioso": ["thriller", "mystery", "suspense"],
            "cozy": ["contemporary fiction", "cozy mystery", "slice of life"],
            "aventurero": ["fantasy", "adventure", "science fiction"],
            "oscuro": ["dark romance", "horror", "psychological thriller"],
            "esperanzador": ["coming of age", "inspirational", "literary fiction"]
        }
        if vibe in mapa_vibe:
            generos = mapa_vibe[vibe]
            inferencias.append(f"Vibe '{vibe}' → géneros recomendados: {', '.join(generos)}")

        reseñas = self.db.query(Reseña).filter(Reseña.usuario_id == usuario_id).all()
        if reseñas:
            promedio = sum(r.calificacion for r in reseñas) / len(reseñas)
            if promedio >= 4.5:
                inferencias.append("Lector exigente → se priorizan libros mejor valorados")

        return {
            "generos_finales": generos,
            "tags": tags,
            "inferencias": inferencias
        }

    def obtener_libros_con_gemini(self, generos: list, tags: list) -> list:
        prompt = f"""
        Recomienda 5 libros modernos y populares de BookTok/Bookstagram publicados después del 2010.
        Géneros: {', '.join(generos[:2])}
        Tags/mood: {', '.join(tags[:3])}
        
        Responde SOLO con este formato JSON exacto, sin texto extra:
        [
          {{"titulo": "Título del libro", "autor": "Nombre Autor", "descripcion": "Sinopsis breve de 2 oraciones.", "genero": "género"}},
          {{"titulo": "...", "autor": "...", "descripcion": "...", "genero": "..."}}
        ]
        """
        response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
        
        import json
        import re
        text = response.text.strip()
        text = re.sub(r'```json|```', '', text).strip()
        libros_raw = json.loads(text)
        
        libros = []
        for i, libro in enumerate(libros_raw):
            titulo_query = libro['titulo'].replace(' ', '+')
            portada = self.buscar_portada(libro['titulo'], libro['autor'])
            libros.append({
                "id": f"gemini_{i}_{titulo_query}",
                "titulo": libro.get("titulo", ""),
                "autor": libro.get("autor", ""),
                "descripcion": libro.get("descripcion", ""),
                "portada_url": portada,
                "genero": libro.get("genero", ""),
                "tags": ", ".join(tags)
            })
        return libros

    def buscar_portada(self, titulo: str, autor: str) -> str:
        try:
            params = {"q": f"{titulo} {autor}", "limit": 1, "fields": "cover_i"}
            r = requests.get(self.open_library_url, params=params, timeout=30)
            data = r.json()
            docs = data.get("docs", [])
            if docs and docs[0].get("cover_i"):
                cover_id = docs[0]["cover_i"]
                return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
        except:
            pass
        return ""

    def recomendar(self, usuario_id: int, vibe_data: dict) -> dict:
        from models import Biblioteca
        reglas = self.aplicar_reglas(usuario_id, vibe_data)
        libros = self.obtener_libros_con_gemini(reglas["generos_finales"], reglas["tags"])

        ids_biblioteca = [
            b.libro_id for b in self.db.query(Biblioteca).filter(
                Biblioteca.usuario_id == usuario_id
            ).all()
        ]
        libros_filtrados = [l for l in libros if l["id"] not in ids_biblioteca]

        return {
            "libros": libros_filtrados[:5],
            "inferencias": reglas["inferencias"],
            "generos_usados": reglas["generos_finales"]
        }
