from google import genai
import os
from dotenv import load_dotenv
from models import Biblioteca, Reseña, SesionVibe

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class SupervisorAgent:
    def __init__(self, db):
        self.db = db
        self.model = client.models

    def explicar_recomendacion(self, usuario_id: int, vibe_data: dict, libros: list, inferencias: list) -> dict:
        # Construir contexto para Gemini
        libros_texto = "\n".join([
            f"- {l['titulo']} de {l['autor']} (género: {l['genero']})"
            for l in libros[:5]
        ])

        inferencias_texto = "\n".join([f"• {i}" for i in inferencias])

        prompt = f"""
        Eres el supervisor de un sistema de recomendación de libros llamado Novelia.
        
        El usuario tiene un vibe: {vibe_data.get('vibe', 'desconocido')}
        Tags detectados: {', '.join(vibe_data.get('tags', []))}
        
        Se aplicaron estas inferencias:
        {inferencias_texto}
        
        Se recomendaron estos libros:
        {libros_texto}
        
        Genera un resumen explicando:
        1. Por qué se detectó ese vibe
        2. Por qué se recomendaron esos libros
        3. Qué reglas se aplicaron
        
        Sé amigable, claro y usa máximo 4 oraciones. Habla directamente al usuario (usa "tú").
        """

        response = self.model.generate_content(prompt)

        return {
            "vibe_detectado": vibe_data.get("vibe"),
            "tags": vibe_data.get("tags", []),
            "inferencias": inferencias,
            "explicacion": response.text.strip(),
            "total_recomendaciones": len(libros)
        }

    def resumen_usuario(self, usuario_id: int) -> dict:
        # Estadísticas del usuario
        biblioteca = self.db.query(Biblioteca).filter(
            Biblioteca.usuario_id == usuario_id
        ).all()

        reseñas = self.db.query(Reseña).filter(
            Reseña.usuario_id == usuario_id
        ).all()

        leidos = [b for b in biblioteca if b.estado == "leido"]
        leyendo = [b for b in biblioteca if b.estado == "leyendo"]
        quiero_leer = [b for b in biblioteca if b.estado == "quiero_leer"]

        rating_promedio = 0
        if reseñas:
            rating_promedio = sum(r.calificacion for r in reseñas) / len(reseñas)

        # Inferencias sobre el perfil
        inferencias_perfil = []

        if len(leidos) > 20:
            inferencias_perfil.append("Lector experto: más de 20 libros leídos")
        elif len(leidos) > 5:
            inferencias_perfil.append("Lector activo: entre 5 y 20 libros leídos")
        else:
            inferencias_perfil.append("Lector nuevo: menos de 5 libros leídos")

        if rating_promedio >= 4.5:
            inferencias_perfil.append("Lector exigente: rating promedio alto")
        elif rating_promedio >= 3.0:
            inferencias_perfil.append("Lector moderado: rating promedio normal")

        if len(quiero_leer) > 10:
            inferencias_perfil.append("Lista de deseos grande: más de 10 libros pendientes")

        # Vibes más usados
        sesiones = self.db.query(SesionVibe).filter(
            SesionVibe.usuario_id == usuario_id
        ).all()

        vibes_conteo = {}
        for s in sesiones:
            v = s.vibe_detectado
            vibes_conteo[v] = vibes_conteo.get(v, 0) + 1

        vibe_favorito = max(vibes_conteo, key=vibes_conteo.get) if vibes_conteo else "sin datos"

        return {
            "estadisticas": {
                "libros_leidos": len(leidos),
                "leyendo_ahora": len(leyendo),
                "quiero_leer": len(quiero_leer),
                "total_reseñas": len(reseñas),
                "rating_promedio": round(rating_promedio, 1)
            },
            "vibe_favorito": vibe_favorito,
            "inferencias_perfil": inferencias_perfil
        }

    def guardar_sesion_vibe(self, usuario_id: int, tipo: str, entrada: str, vibe_data: dict):
        sesion = SesionVibe(
            usuario_id=usuario_id,
            tipo_entrada=tipo,
            entrada_raw=entrada,
            vibe_detectado=vibe_data.get("vibe", ""),
            tags_generados=",".join(vibe_data.get("tags", []))
        )
        self.db.add(sesion)
        self.db.commit()