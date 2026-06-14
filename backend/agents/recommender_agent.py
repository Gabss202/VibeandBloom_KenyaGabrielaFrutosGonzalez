import os
import re
import requests
from dotenv import load_dotenv

try:
    from google import genai
except Exception:
    genai = None

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if genai and GEMINI_API_KEY else None


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
            inferencias.append("Usuario experto -> se priorizan libros menos conocidos")

        vibe = vibe_data.get("vibe", "")
        mapa_vibe = {
            "melancolico": ["drama", "literary fiction", "poetry"],
            "romantico": ["romance", "love story", "contemporary romance"],
            "misterioso": ["thriller", "mystery", "suspense"],
            "cozy": ["contemporary fiction", "cozy mystery", "slice of life"],
            "aventurero": ["fantasy", "adventure", "science fiction"],
            "oscuro": ["dark romance", "horror", "psychological thriller"],
            "esperanzador": ["coming of age", "inspirational", "literary fiction"],
        }
        if vibe in mapa_vibe:
            generos = mapa_vibe[vibe]
            inferencias.append(f"Vibe '{vibe}' -> géneros recomendados: {', '.join(generos)}")

        reseñas = self.db.query(Reseña).filter(Reseña.usuario_id == usuario_id).all()
        if reseñas:
            promedio = sum(r.calificacion for r in reseñas) / len(reseñas)
            if promedio >= 4.5:
                inferencias.append("Lector exigente -> se priorizan libros mejor valorados")

        return {
            "generos_finales": generos,
            "tags": tags,
            "inferencias": inferencias,
        }

    def obtener_libros_con_gemini(self, generos: list, tags: list) -> list:
        if not client:
            return self._fallback_libros(generos, tags)

        prompt = f"""
        Recomienda 5 libros modernos, populares y conversados en BookTok/Bookstagram publicados después del 2015.
        Géneros: {', '.join(generos[:2])}
        Tags/mood: {', '.join(tags[:3])}

        Responde SOLO con este formato JSON exacto, sin texto extra:
        [
          {{"titulo": "Título del libro", "autor": "Nombre Autor", "descripcion": "Sinopsis breve de 2 oraciones.", "genero": "género"}},
          {{"titulo": "...", "autor": "...", "descripcion": "...", "genero": "..."}}
        ]
        """

        import json

        try:
            response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
            text = response.text.strip()
            text = re.sub(r"```json|```", "", text).strip()
            libros_raw = json.loads(text)
        except Exception:
            return self._fallback_libros(generos, tags)

        libros = []
        for i, libro in enumerate(libros_raw):
            titulo = libro.get("titulo", "")
            autor = libro.get("autor", "")
            portada = self.buscar_portada(titulo, autor)
            libros.append({
                "id": f"gemini_{i}_{titulo.replace(' ', '_')}",
                "titulo": titulo,
                "autor": autor,
                "descripcion": libro.get("descripcion", ""),
                "portada_url": portada,
                "genero": libro.get("genero", ""),
                "tags": ", ".join(tags)
            })
        return libros

    def buscar_portada(self, titulo: str, autor: str) -> str:
        try:
            params = {"q": f"{titulo} {autor}", "limit": 1, "fields": "cover_i"}
            response = requests.get(self.open_library_url, params=params, timeout=20)
            data = response.json()
            docs = data.get("docs", [])
            if docs and docs[0].get("cover_i"):
                cover_id = docs[0]["cover_i"]
                return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
        except Exception:
            pass
        return ""

    def _fallback_libros(self, generos: list, tags: list) -> list:
        base = [
            {"titulo": "Fourth Wing", "autor": "Rebecca Yarros", "descripcion": "Fantasía de ritmo ágil, tensión romántica y mucha conversación en comunidades lectoras modernas.", "genero": "fantasy"},
            {"titulo": "Happy Place", "autor": "Emily Henry", "descripcion": "Romance contemporáneo con humor, emoción y química natural entre personajes.", "genero": "romance"},
            {"titulo": "The Seven Husbands of Evelyn Hugo", "autor": "Taylor Jenkins Reid", "descripcion": "Drama moderno, glamour y una protagonista inolvidable con gran impacto social.", "genero": "literary fiction"},
            {"titulo": "A Good Girl's Guide to Murder", "autor": "Holly Jackson", "descripcion": "Misterio juvenil con pistas claras, ritmo alto y una investigación que engancha.", "genero": "mystery"},
            {"titulo": "Book Lovers", "autor": "Emily Henry", "descripcion": "Romance inteligente sobre libros, editoriales y segundas oportunidades.", "genero": "contemporary romance"},
        ]

        libros = []
        for i, libro in enumerate(base):
            portada = self.buscar_portada(libro["titulo"], libro["autor"])
            libros.append({
                "id": f"fallback_{i}_{libro['titulo'].replace(' ', '_')}",
                "titulo": libro["titulo"],
                "autor": libro["autor"],
                "descripcion": libro["descripcion"],
                "portada_url": portada,
                "genero": libro["genero"],
                "tags": ", ".join(tags)
            })
        return libros

    def libros_populares(self) -> list:
        recomendados = [
            {"titulo": "It Ends With Us", "autor": "Colleen Hoover", "descripcion": "Romance contemporáneo muy popular en BookTok con una historia intensa y emotiva.", "genero": "romance"},
            {"titulo": "The Atlas Six", "autor": "Olivie Blake", "descripcion": "Fantasía oscura y sofisticada que ha sido tendencia en comunidades lectora.", "genero": "fantasy"},
            {"titulo": "People We Meet on Vacation", "autor": "Emily Henry", "descripcion": "Romance ligero con humor y química que sigue siendo un favorito actual.", "genero": "romance"},
            {"titulo": "The Maid", "autor": "Nita Prose", "descripcion": "Misterio accesible con gran atractivo social y un personaje principal inolvidable.", "genero": "mystery"},
            {"titulo": "Tomorrow, and Tomorrow, and Tomorrow", "autor": "Gabrielle Zevin", "descripcion": "Novela moderna sobre amistad, amor y creación de videojuegos.", "genero": "literary fiction"},
        ]
        libros = []
        for i, libro in enumerate(recomendados):
            portada = self.buscar_portada(libro["titulo"], libro["autor"])
            libros.append({
                "id": f"popular_{i}_{libro['titulo'].replace(' ', '_')}",
                "titulo": libro["titulo"],
                "autor": libro["autor"],
                "descripcion": libro["descripcion"],
                "portada_url": portada,
                "genero": libro["genero"],
                "tags": libro["genero"]
            })
        return libros

    def recomendar(self, usuario_id: int, vibe_data: dict) -> dict:
        from models import Biblioteca

        reglas = self.aplicar_reglas(usuario_id, vibe_data)
        libros = self.obtener_libros_con_gemini(reglas["generos_finales"], reglas["tags"])

        ids_biblioteca = [
            b.libro_id for b in self.db.query(Biblioteca).filter(
                Biblioteca.usuario_id == usuario_id
            ).all()
        ]
        libros_filtrados = [libro for libro in libros if libro["id"] not in ids_biblioteca]

        return {
            "libros": libros_filtrados[:5],
            "inferencias": reglas["inferencias"],
            "generos_usados": reglas["generos_finales"],
        }