from google import genai
from dotenv import load_dotenv
import os
import json
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import get_connection

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODO_DESARROLLO = os.getenv("MODO_DESARROLLO", "false").lower() == "true"

# ============================================
# GESTIÓN DE BIBLIOTECA PERSONAL
# ============================================

def agregar_libro(title: str, author: str, genre: str, status: str = "quiero_leer", total_pages: int = 0, cover_url: str = "") -> dict:
    """Agrega un libro a la biblioteca personal."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Regla: verificar si el libro ya existe
    cursor.execute("SELECT id FROM books WHERE title = ? AND author = ?", (title, author))
    existente = cursor.fetchone()
    
    if existente:
        conn.close()
        return {"exito": False, "mensaje": f"'{title}' ya está en tu biblioteca 📚"}
    
    cursor.execute("""
        INSERT INTO books (title, author, genre, status, cover_url, total_pages, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, author, genre, status, cover_url, total_pages, datetime.now().isoformat()))
    
    conn.commit()
    book_id = cursor.lastrowid
    conn.close()
    
    return {"exito": True, "mensaje": f"'{title}' agregado a tu biblioteca 🌸", "book_id": book_id}

def actualizar_estado(book_id: int, nuevo_estado: str) -> dict:
    """
    Regla de inferencia: cambia el estado del libro.
    Estados válidos: quiero_leer, leyendo, leido
    """
    estados_validos = ["quiero_leer", "leyendo", "leido"]
    
    # IF estado no válido THEN rechazar
    if nuevo_estado not in estados_validos:
        return {"exito": False, "mensaje": "Estado no válido"}
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE books SET status = ? WHERE id = ?", (nuevo_estado, book_id))
    conn.commit()
    conn.close()
    
    emojis = {"quiero_leer": "🔖", "leyendo": "📖", "leido": "✅"}
    return {"exito": True, "mensaje": f"Estado actualizado a {emojis[nuevo_estado]} {nuevo_estado}"}

def agregar_resena(book_id: int, rating: float, review_text: str, 
                   favorite_characters: str = "", music: str = "", vibes: str = "") -> dict:
    """Agrega o actualiza la reseña de un libro."""
    
    # Regla: calificación debe ser entre 0.5 y 5
    if not (0.5 <= rating <= 5):
        return {"exito": False, "mensaje": "La calificación debe ser entre 0.5 y 5 ⭐"}
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar si ya existe reseña
    cursor.execute("SELECT id FROM reviews WHERE book_id = ?", (book_id,))
    existente = cursor.fetchone()
    
    if existente:
        cursor.execute("""
            UPDATE reviews SET rating=?, review_text=?, favorite_characters=?, 
            music=?, vibes=?, date_reviewed=?
            WHERE book_id=?
        """, (rating, review_text, favorite_characters, music, vibes, 
              datetime.now().isoformat(), book_id))
    else:
        cursor.execute("""
            INSERT INTO reviews (book_id, rating, review_text, favorite_characters, music, vibes, date_reviewed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (book_id, rating, review_text, favorite_characters, music, vibes, datetime.now().isoformat()))
    
    # Regla: si agregó reseña, actualizar estado a leido automáticamente
    cursor.execute("UPDATE books SET status = 'leido' WHERE id = ?", (book_id,))
    
    conn.commit()
    conn.close()
    
    estrellas = "⭐" * int(rating)
    return {"exito": True, "mensaje": f"Reseña guardada {estrellas}", "rating": rating}

def obtener_biblioteca(status: str = None) -> list:
    """Obtiene todos los libros, opcionalmente filtrados por estado."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if status:
        cursor.execute("""
            SELECT b.id, b.title, b.author, b.genre, b.status, b.cover_url, b.total_pages,
                   r.rating, r.review_text, r.favorite_characters, r.music, r.vibes
            FROM books b
            LEFT JOIN reviews r ON b.id = r.book_id
            WHERE b.status = ?
            ORDER BY b.date_added DESC
        """, (status,))
    else:
        cursor.execute("""
            SELECT b.id, b.title, b.author, b.genre, b.status, b.cover_url, b.total_pages,
                   r.rating, r.review_text, r.favorite_characters, r.music, r.vibes
            FROM books b
            LEFT JOIN reviews r ON b.id = r.book_id
            ORDER BY b.date_added DESC
        """)
    
    libros = []
    for row in cursor.fetchall():
        libros.append({
            "id": row[0], "title": row[1], "author": row[2],
            "genre": row[3], "status": row[4], "cover_url": row[5],
            "total_pages": row[6], "rating": row[7], "review_text": row[8],
            "favorite_characters": row[9], "music": row[10], "vibes": row[11]
        })
    
    conn.close()
    return libros

def obtener_estadisticas() -> dict:
    """
    Agente 3: analiza la biblioteca y genera estadísticas
    para el dashboard de la app.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total por estado
    cursor.execute("SELECT status, COUNT(*) FROM books GROUP BY status")
    conteos = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Promedio de calificaciones
    cursor.execute("SELECT AVG(rating) FROM reviews WHERE rating IS NOT NULL")
    promedio = cursor.fetchone()[0] or 0
    
    # Género más leído
    cursor.execute("""
        SELECT genre, COUNT(*) as total FROM books 
        WHERE status = 'leido' AND genre IS NOT NULL
        GROUP BY genre ORDER BY total DESC LIMIT 1
    """)
    genero_fav = cursor.fetchone()
    
    # Libros por mes
    cursor.execute("""
        SELECT strftime('%Y-%m', date_added) as mes, COUNT(*) 
        FROM books WHERE status = 'leido'
        GROUP BY mes ORDER BY mes
    """)
    por_mes = [{"mes": row[0], "cantidad": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "total_leidos": conteos.get("leido", 0),
        "total_leyendo": conteos.get("leyendo", 0),
        "total_quiero_leer": conteos.get("quiero_leer", 0),
        "promedio_calificacion": round(promedio, 2),
        "genero_favorito": genero_fav[0] if genero_fav else "Sin datos",
        "libros_por_mes": por_mes
    }

def generar_insight_ia(estadisticas: dict, libros: list) -> str:
    """Genera un insight personalizado basado en los hábitos de lectura."""
    if MODO_DESARROLLO:
        return "📊 Llevas 3 libros leídos este mes. Tu género favorito es el dark romance — tienes un gusto exquisito 🌹"
    
    prompt = f"""
    Eres Bloom, la bibliotecaria de Novelia. Analiza estos hábitos de lectura:
    
    Estadísticas: {json.dumps(estadisticas, ensure_ascii=False)}
    Últimos libros: {json.dumps([{"title": l["title"], "rating": l["rating"]} for l in libros[:5]], ensure_ascii=False)}
    
    Genera un mensaje corto (2-3 oraciones) cálido y personalizado que:
    1. Celebre sus logros de lectura
    2. Note un patrón interesante en sus gustos
    3. Lo motive a seguir leyendo
    
    Tono: como una amiga booktoker apasionada. En español.
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text

if __name__ == "__main__":
    print("🌿 Probando Agente 3 — La Bibliotecaria\n")
    
    # Prueba: agregar libros
    print("📚 Agregando libros de prueba...")
    r1 = agregar_libro("A Court of Thorns and Roses", "Sarah J. Maas", "dark romance", "leido", 419)
    r2 = agregar_libro("The Midnight Library", "Matt Haig", "ficción contemporánea", "leyendo", 304)
    r3 = agregar_libro("Six of Crows", "Leigh Bardugo", "fantasía", "quiero_leer", 465)
    print(r1["mensaje"])
    print(r2["mensaje"])
    print(r3["mensaje"])
    
    # Prueba: agregar reseña
    print("\n⭐ Agregando reseña...")
    if r1["exito"]:
        resena = agregar_resena(
            book_id=r1["book_id"],
            rating=4.5,
            review_text="Me hizo sentir cosas muy intensas. Feyre y Tamlin tienen una dinámica fascinante.",
            favorite_characters="Rhysand, Feyre",
            music="Cruel Summer - Taylor Swift",
            vibes="enemies to lovers, dark romance"
        )
        print(resena["mensaje"])
    
    # Prueba: estadísticas
    print("\n📊 Estadísticas de tu biblioteca:")
    stats = obtener_estadisticas()
    print(f"  Leídos: {stats['total_leidos']}")
    print(f"  Leyendo: {stats['total_leyendo']}")
    print(f"  Quiero leer: {stats['total_quiero_leer']}")
    print(f"  Promedio calificación: {stats['promedio_calificacion']} ⭐")
    print(f"  Género favorito: {stats['genero_favorito']}")
    
    # Prueba: insight
    print("\n✨ Insight de Bloom:")
    libros = obtener_biblioteca()
    insight = generar_insight_ia(stats, libros)
    print(insight)