from datetime import datetime
from models import Biblioteca, Libro, Reseña
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class LibrarianAgent:
    def __init__(self, db):
        self.db = db
        # model set

    def guardar_libro(self, libro_data: dict) -> Libro:
        # Verificar si el libro ya existe en BD
        libro = self.db.query(Libro).filter(Libro.id == libro_data["id"]).first()
        if not libro:
            libro = Libro(
                id=libro_data["id"],
                titulo=libro_data["titulo"],
                autor=libro_data["autor"],
                genero=libro_data.get("genero", ""),
                descripcion=libro_data.get("descripcion", ""),
                portada_url=libro_data.get("portada_url", ""),
                tags=libro_data.get("tags", "")
            )
            self.db.add(libro)
            self.db.commit()
        return libro

    def agregar_a_biblioteca(self, usuario_id: int, libro_data: dict, estado: str) -> dict:
        # Primero guardar el libro si no existe
        self.guardar_libro(libro_data)

        # Verificar si ya está en la biblioteca del usuario
        existente = self.db.query(Biblioteca).filter(
            Biblioteca.usuario_id == usuario_id,
            Biblioteca.libro_id == libro_data["id"]
        ).first()

        if existente:
            # Actualizar estado
            existente.estado = estado
            self.db.commit()
            accion = "actualizado"
        else:
            # Agregar nuevo
            entrada = Biblioteca(
                usuario_id=usuario_id,
                libro_id=libro_data["id"],
                estado=estado,
                progreso=0,
                fecha_agregado=datetime.utcnow()
            )
            self.db.add(entrada)
            self.db.commit()
            accion = "agregado"

        # Inferencia: sugerir reseña si estado es "leido"
        sugerencia = None
        if estado == "leido":
            sugerencia = "¡Terminaste este libro! ¿Te gustaría dejar una reseña?"

        return {
            "mensaje": f"Libro '{libro_data['titulo']}' {accion} como '{estado}'",
            "accion": accion,
            "sugerencia": sugerencia
        }

    def actualizar_progreso(self, usuario_id: int, libro_id: str, progreso: int) -> dict:
        entrada = self.db.query(Biblioteca).filter(
            Biblioteca.usuario_id == usuario_id,
            Biblioteca.libro_id == libro_id
        ).first()

        if not entrada:
            return {"error": "Libro no encontrado en tu biblioteca"}

        entrada.progreso = progreso

        # Inferencia: si progreso >= 80% sugerir libros similares
        inferencia = None
        if progreso >= 80 and entrada.estado == "leyendo":
            inferencia = "Estás casi terminando, pronto te recomendaremos libros similares"

        # Inferencia: marcar como leído automáticamente si llega a 100%
        if progreso == 100:
            entrada.estado = "leido"
            inferencia = "¡Libro completado! Marcado como leído automáticamente"

        self.db.commit()
        return {
            "mensaje": f"Progreso actualizado a {progreso}%",
            "inferencia": inferencia
        }

    def escribir_reseña(self, usuario_id: int, libro_id: str, calificacion: float, texto: str) -> dict:
        # Verificar si ya existe reseña
        existente = self.db.query(Reseña).filter(
            Reseña.usuario_id == usuario_id,
            Reseña.libro_id == libro_id
        ).first()

        if existente:
            existente.calificacion = calificacion
            existente.texto = texto
            existente.fecha = datetime.utcnow()
            self.db.commit()
            accion = "actualizada"
        else:
            reseña = Reseña(
                usuario_id=usuario_id,
                libro_id=libro_id,
                calificacion=calificacion,
                texto=texto,
                fecha=datetime.utcnow()
            )
            self.db.add(reseña)
            self.db.commit()
            accion = "publicada"

        # Actualizar rating promedio del libro
        self._actualizar_rating(libro_id)

        # Gemini genera respuesta emotiva a la reseña
        prompt = f"""
        Un lector escribió esta reseña de un libro con {calificacion} estrellas:
        "{texto}"
        
        Responde con UN mensaje corto (máximo 2 oraciones) celebrando su reseña
        y animándolo a seguir leyendo. Sé cálido y entusiasta.
        """
        response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)

        return {
            "mensaje": f"Reseña {accion} exitosamente",
            "respuesta_ia": response.text.strip()
        }

    def _actualizar_rating(self, libro_id: str):
        reseñas = self.db.query(Reseña).filter(Reseña.libro_id == libro_id).all()
        if reseñas:
            libro = self.db.query(Libro).filter(Libro.id == libro_id).first()
            if libro:
                libro.rating_promedio = sum(r.calificacion for r in reseñas) / len(reseñas)
                libro.total_reseñas = len(reseñas)
                self.db.commit()

    def obtener_biblioteca(self, usuario_id: int) -> dict:
        entradas = self.db.query(Biblioteca).filter(
            Biblioteca.usuario_id == usuario_id
        ).all()

        leyendo, quiero_leer, leidos = [], [], []

        for entrada in entradas:
            libro = self.db.query(Libro).filter(Libro.id == entrada.libro_id).first()
            if not libro:
                continue
            datos = {
                "id": libro.id,
                "titulo": libro.titulo,
                "autor": libro.autor,
                "portada_url": libro.portada_url,
                "progreso": entrada.progreso,
                "fecha_agregado": entrada.fecha_agregado.isoformat()
            }
            if entrada.estado == "leyendo":
                leyendo.append(datos)
            elif entrada.estado == "quiero_leer":
                quiero_leer.append(datos)
            elif entrada.estado == "leido":
                leidos.append(datos)

        return {
            "leyendo": leyendo,
            "quiero_leer": quiero_leer,
            "leidos": leidos
        }