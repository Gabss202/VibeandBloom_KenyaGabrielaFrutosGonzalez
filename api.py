from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agents.agent2_recommender import recomendar_libros_por_vibe
from agents.agent3_librarian import (
    agregar_libro, agregar_resena,
    obtener_biblioteca, obtener_estadisticas, generar_insight_ia
)
from ui.styles import get_full_css
from ui.components.sidebar import get_nav_html, get_header_html
from ui.components.modal_vibe import get_modal_vibe_html
from ui.views.inicio import get_inicio_html
from ui.components.library import get_biblioteca_html, get_agregar_html, get_stats_html
from ui.components.main_phone import JS_CODE

app = FastAPI(title="Novelia API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class VibeRequest(BaseModel):
    descripcion: str

class LibroRequest(BaseModel):
    title: str
    author: str
    genre: str = ""
    status: str = "quiero_leer"
    total_pages: int = 0

class ResenaRequest(BaseModel):
    book_id: int
    rating: float
    review_text: str
    favorite_characters: str = ""
    music: str = ""
    vibes: str = ""

@app.get("/", response_class=HTMLResponse)
async def root():
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Novelia ✦</title>
<style>{get_full_css()}</style>
</head>
<body>
{get_header_html()}
{get_inicio_html()}
{get_biblioteca_html()}
{get_agregar_html()}
{get_stats_html()}
{get_modal_vibe_html()}
{get_nav_html()}
<script type="text/javascript">
{JS_CODE}
</script>
</body>
</html>"""
    return html

@app.post("/api/recomendar")
async def recomendar(req: VibeRequest):
    return recomendar_libros_por_vibe(req.descripcion)

@app.post("/api/agregar-libro")
async def add_libro(req: LibroRequest):
    return agregar_libro(req.title, req.author, req.genre, req.status, req.total_pages)

@app.post("/api/agregar-resena")
async def add_resena(req: ResenaRequest):
    return agregar_resena(req.book_id, req.rating, req.review_text,
                          req.favorite_characters, req.music, req.vibes)

@app.get("/api/biblioteca")
async def get_biblioteca(status: str = None):
    return obtener_biblioteca(status)

@app.get("/api/estadisticas")
async def get_estadisticas():
    stats = obtener_estadisticas()
    stats["insight"] = generar_insight_ia(stats, obtener_biblioteca())
    return stats