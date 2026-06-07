import requests
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class RecommenderAgent:
    def __init__(self, db):
        self.db = db
        self.model = client.models
        self.google_books_url = "https://www.googleapis.com/books/v1/volumes"

    # --- REGLAS DE INFERENCIA ---
    def aplicar_reglas(self, usuario_id: int, vibe_data: dict) -> dict:
        from models import Biblioteca, Reseña
        
        inferencias = []
        generos = vibe_data.get("generos", [])
        tags = vibe_data.get("tags", [])

        # Regla 1: historial del usuario
        libros_leidos = self.db.query(Biblioteca).filter(
            Biblioteca.usuario_id == usuario_id,
            Biblioteca.estado == "leido"
        ).count()

        if libros_leidos > 20:
            inferencias.append("Usuario experto → se priorizan libros menos conocidos")
            query_extra = "lesser known"
        else:
            query_extra = "popular"

        # Regla 2: vibe a género
        vibe = vibe_data.get("vibe", "")
        mapa_vibe = {
            "melancolico": ["drama", "ficcion literaria", "poesia"],
            "romantico": ["romance", "ficcion contemporanea"],
            "misterioso": ["thriller", "misterio", "suspenso"],
            "cozy": ["ficcion contemporanea", "humor", "slice of life"],
            "aventurero": ["fantasia", "aventura", "ciencia ficcion"],
            "oscuro": ["horror", "romance oscuro", "thriller psicologico"],
            "esperanzador": ["ficcion literaria", "inspiracional", "coming of age"]
        }
        if vibe in mapa_vibe:
            generos = mapa_vibe[vibe]
            inferencias.append(f"Vibe '{vibe}' → géneros recomendados: {', '.join(generos)}")

        # Regla 3: rating promedio del usuario
        reseñas = self.db.query(Reseña).filter(Reseña.usuario_id == usuario_id).all()
        if reseñas:
            promedio = sum(r.calificacion for r in reseñas) / len(reseñas)
            if promedio >= 4.5:
                inferencias.append("Lector exigente (rating promedio alto) → se filtran libros con rating > 4.0")

        return {
            "generos_finales": generos,
            "tags": tags,
            "query_extra": query_extra,
            "inferencias": inferencias
        }

    def buscar_libros_google(self, generos: list, tags: list, query_extra: str = "") -> list:
        libros = []
        query = f"{' '.join(tags[:2])} {generos[0] if generos else 'fiction'} {query_extra}"
        
        params = {
            "q": query,
            "maxResults": 10,
            "langRestrict": "es",
            "printType": "books"
        }
        
        try:
            response = requests.get(self.google_books_url, params=params)
            data = response.json()
            
            for item in data.get("items", []):
                info = item.get("volumeInfo", {})
                libros.append({
                    "id": item.get("id"),
                    "titulo": info.get("title", "Sin título"),
                    "autor": ", ".join(info.get("authors", ["Desconocido"])),
                    "descripcion": info.get("description", "")[:300],
                    "portada_url": info.get("imageLinks", {}).get("thumbnail", ""),
                    "genero": ", ".join(info.get("categories", generos[:1])),
                    "tags": ", ".join(tags)
                })
        except Exception as e:
            print(f"Error buscando libros: {e}")
        
        return libros

    def recomendar(self, usuario_id: int, vibe_data: dict) -> dict:
        from models import Biblioteca

        # Aplicar reglas
        reglas = self.aplicar_reglas(usuario_id, vibe_data)

        # Buscar libros
        libros = self.buscar_libros_google(
            reglas["generos_finales"],
            reglas["tags"],
            reglas["query_extra"]
        )

        # Filtrar libros ya en biblioteca
        ids_biblioteca = [
            b.libro_id for b in self.db.query(Biblioteca).filter(
                Biblioteca.usuario_id == usuario_id
            ).all()
        ]
        libros_filtrados = [l for l in libros if l["id"] not in ids_biblioteca]
        
        if ids_biblioteca:
            reglas["inferencias"].append(
                f"Se excluyeron {len(libros) - len(libros_filtrados)} libros ya en tu biblioteca"
            )

        return {
            "libros": libros_filtrados[:5],
            "inferencias": reglas["inferencias"],
            "generos_usados": reglas["generos_finales"]
        }