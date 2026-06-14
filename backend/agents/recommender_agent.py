import os
import re
import random
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
            libros = self.buscar_libros_openlibrary(generos, tags, max_results=5)
            return libros if libros else self._fallback_libros(generos, tags)

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
            libros = self.buscar_libros_openlibrary(generos, tags, max_results=5)
            return libros if libros else self._fallback_libros(generos, tags)

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

    def buscar_libros_openlibrary(self, generos: list, tags: list, max_results: int = 8) -> list:
        query_parts = []
        if generos:
            query_parts.append(" ".join(generos[:3]))
        if tags:
            query_parts.append(" ".join(tags[:5]))
        query = " ".join(query_parts).strip() or "popular books"

        params = {
            "q": query,
            "fields": "title,author_name,cover_i,subject,first_publish_year,edition_key",
            "limit": max_results * 2,
        }
        try:
            response = requests.get(self.open_library_url, params=params, timeout=20)
            data = response.json()
            docs = data.get("docs", [])
            libros = []
            for doc in docs:
                titulo = doc.get("title") or "Título desconocido"
                autores = doc.get("author_name") or ["Autor desconocido"]
                autor = autores[0]
                genero = ", ".join([g for g in doc.get("subject", [])[:2]]) if doc.get("subject") else generos[0] if generos else "Ficción"
                portada = ""
                if doc.get("cover_i"):
                    portada = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
                libro_id = doc.get("edition_key", [None])[0] or f"ol_{titulo.replace(' ', '_')}_{autor.replace(' ', '_')}"
                libros.append({
                    "id": libro_id,
                    "titulo": titulo,
                    "autor": autor,
                    "descripcion": f"Lectura recomendada basada en {', '.join(generos[:2])} y el mood detectado.",
                    "portada_url": portada,
                    "genero": genero,
                    "tags": ", ".join(tags)
                })
                if len(libros) >= max_results:
                    break
            if libros:
                return libros
        except Exception:
            pass
        return []

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

    def normalizar_query(self, termino: str) -> str:
        termino = termino.strip().lower()
        termino = termino.replace('&', ' ').replace('/', ' ').replace('-', ' ')
        termino = termino.replace('darkromance', 'dark romance')
        termino = termino.replace('romántico', 'romantico').replace('misterioso', 'misterioso')
        termino = re.sub(r'\s+', ' ', termino)
        return termino

    def _query_param_for_termino(self, termino: str) -> dict:
        termino = termino.lower()
        if any(word in termino for word in ["dark romance", "darkromance", "oscuro", "oscura", "gótico", "gotico", "gothic"]):
            return {"subject": "dark romance"}
        if any(word in termino for word in ["cozy", "acogedor", "acogedora", "cálido", "calido", "hogareño", "hogareno", "comfortable"]):
            return {"subject": "cozy"}
        if any(word in termino for word in ["misterioso", "misterio", "thriller", "suspense"]):
            return {"subject": "mystery"}
        if any(word in termino for word in ["romántico", "romantico", "amor", "romance"]):
            return {"subject": "romance"}
        if any(word in termino for word in ["aventura", "aventurero", "aventurera", "fantasía", "fantasia", "fantasy"]):
            return {"q": "fantasy adventure"}
        return {"q": termino}

    def buscar_libros_por_termino(self, termino: str, max_results: int = 8) -> list:
        termino_normalizado = self.normalizar_query(termino)
        search_params = self._query_param_for_termino(termino_normalizado)
        params = {
            **search_params,
            "fields": "title,author_name,cover_i,subject,edition_key",
            "limit": max_results * 2,
        }
        try:
            response = requests.get(self.open_library_url, params=params, timeout=20)
            data = response.json()
            docs = data.get("docs", [])
            libros = []
            vistos = set()
            for doc in docs:
                titulo = doc.get("title") or termino
                autores = doc.get("author_name") or ["Autor desconocido"]
                autor = autores[0]
                genero = ", ".join([g for g in doc.get("subject", [])[:2]]) if doc.get("subject") else "Ficción"
                portada = ""
                if doc.get("cover_i"):
                    portada = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
                libro_id = (doc.get("edition_key", [None])[0] or f"ol_{titulo.replace(' ', '_')}_{autor.replace(' ', '_')}")
                if libro_id in vistos:
                    continue
                vistos.add(libro_id)
                libros.append({
                    "id": libro_id,
                    "titulo": titulo,
                    "autor": autor,
                    "descripcion": f"Lectura recomendada basada en '{termino_normalizado}'.",
                    "portada_url": portada,
                    "genero": genero,
                    "tags": search_params.get("subject") or search_params.get("q")
                })
                if len(libros) >= max_results:
                    break
            if libros:
                return libros

            if search_params.get("subject"):
                fallback_params = {
                    "q": termino_normalizado,
                    "fields": "title,author_name,cover_i,subject,edition_key",
                    "limit": max_results * 2,
                }
                response = requests.get(self.open_library_url, params=fallback_params, timeout=20)
                data = response.json()
                docs = data.get("docs", [])
                for doc in docs:
                    titulo = doc.get("title") or termino
                    autores = doc.get("author_name") or ["Autor desconocido"]
                    autor = autores[0]
                    genero = ", ".join([g for g in doc.get("subject", [])[:2]]) if doc.get("subject") else "Ficción"
                    portada = ""
                    if doc.get("cover_i"):
                        portada = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
                    libro_id = (doc.get("edition_key", [None])[0] or f"ol_{titulo.replace(' ', '_')}_{autor.replace(' ', '_')}")
                    if libro_id in vistos:
                        continue
                    vistos.add(libro_id)
                    libros.append({
                        "id": libro_id,
                        "titulo": titulo,
                        "autor": autor,
                        "descripcion": f"Lectura recomendada basada en '{termino_normalizado}'.",
                        "portada_url": portada,
                        "genero": genero,
                        "tags": termino_normalizado
                    })
                    if len(libros) >= max_results:
                        break
                if libros:
                    return libros

            if (search_params.get("q") or termino_normalizado) != termino_normalizado:
                return self.buscar_libros_por_termino(termino_normalizado, max_results=max_results)
            return []
        except Exception:
            return []

    def buscar_libro_por_texto(self, termino: str) -> dict:
        libros = self.buscar_libros_por_termino(termino, max_results=1)
        return libros[0] if libros else {}

    def _fallback_libros(self, generos: list, tags: list) -> list:
        base = [
            {"titulo": "Fourth Wing", "autor": "Rebecca Yarros", "descripcion": "Fantasía de ritmo ágil, tensión romántica y mucha conversación en comunidades lectoras modernas.", "genero": "fantasy"},
            {"titulo": "Happy Place", "autor": "Emily Henry", "descripcion": "Romance contemporáneo con humor, emoción y química natural entre personajes.", "genero": "romance"},
            {"titulo": "The Seven Husbands of Evelyn Hugo", "autor": "Taylor Jenkins Reid", "descripcion": "Drama moderno, glamour y una protagonista inolvidable con gran impacto social.", "genero": "literary fiction"},
            {"titulo": "A Good Girl's Guide to Murder", "autor": "Holly Jackson", "descripcion": "Misterio juvenil con pistas claras, ritmo alto y una investigación que engancha.", "genero": "mystery"},
            {"titulo": "Book Lovers", "autor": "Emily Henry", "descripcion": "Romance inteligente sobre libros, editoriales y segundas oportunidades.", "genero": "contemporary romance"},
            {"titulo": "Tomorrow, and Tomorrow, and Tomorrow", "autor": "Gabrielle Zevin", "descripcion": "Una novela moderna sobre amistad, creatividad y el impacto emocional de los juegos.", "genero": "literary fiction"},
            {"titulo": "The Atlas Six", "autor": "Olivie Blake", "descripcion": "Fantasía oscura con magia, traición y un grupo de personajes muy comentado en redes.", "genero": "fantasy"},
            {"titulo": "The Maidens", "autor": "Alex Michaelides", "descripcion": "Thriller psicológico con misterio académico y giros intensos.", "genero": "mystery"},
            {"titulo": "The House in the Cerulean Sea", "autor": "TJ Klune", "descripcion": "Fantasía contemporánea y cálida sobre familia encontrada y magia amable.", "genero": "fantasy"},
            {"titulo": "The Light Between Oceans", "autor": "M.L. Stedman", "descripcion": "Drama evocador sobre amor, responsabilidad y decisiones difíciles en una isla solitaria.", "genero": "literary fiction"},
        ]

        random.shuffle(base)
        libros = []
        for i, libro in enumerate(base[:7]):
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
            {"titulo": "Book Lovers", "autor": "Emily Henry", "descripcion": "Romance actual con humor y química, tendencia en comunidades de lectura modernas.", "genero": "romance"},
            {"titulo": "Tomorrow, and Tomorrow, and Tomorrow", "autor": "Gabrielle Zevin", "descripcion": "Novela sobre amistad, creatividad y la cultura gamer, muy comentada en BookTok.", "genero": "literary fiction"},
            {"titulo": "The Atlas Six", "autor": "Olivie Blake", "descripcion": "Fantasía oscura con magia y tensión, uno de los títulos más buscados por lectores jóvenes.", "genero": "fantasy"},
            {"titulo": "The Maidens", "autor": "Alex Michaelides", "descripcion": "Thriller psicológico con un misterio académico muy comentado.", "genero": "mystery"},
            {"titulo": "The House in the Cerulean Sea", "autor": "TJ Klune", "descripcion": "Fantasía contemporánea y cálida sobre familia encontrada y magia amable.", "genero": "fantasy"},
            {"titulo": "Crying in H Mart", "autor": "Michelle Zauner", "descripcion": "Memorias modernas y emotivas sobre identidad, familia y música.", "genero": "memoir"},
        ]
        random.shuffle(recomendados)
        libros = []
        for i, libro in enumerate(recomendados[:6]):
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