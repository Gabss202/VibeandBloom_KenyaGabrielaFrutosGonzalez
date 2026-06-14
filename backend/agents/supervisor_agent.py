from google import genai
import os
from datetime import date, datetime
from dotenv import load_dotenv
from models import ActividadLectura, Biblioteca, Reseña, SesionVibe, RetoLectura

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

class SupervisorAgent:
    def __init__(self, db):
        self.db = db

    def _detectar_intencion(self, mensaje: str) -> str:
        texto = mensaje.lower()
        reglas = [
            ("recomendacion", ["recomienda", "sugiere", "booktok", "qué leo", "que leo", "similar a", "parecido a"]),
            ("perfil", ["racha", "perfil", "estadísticas", "estadisticas", "nivel", "reto", "progreso"]),
            ("explicacion", ["por qué", "porque", "explica", "explicación", "regla", "inferencia"]),
            ("biblioteca", ["agrega", "añade", "marcar", "quiero leer", "leyendo", "leído", "leido"]),
            ("reseña", ["reseña", "review", "opinas", "calificación", "calificacion"]),
        ]
        for intencion, palabras in reglas:
            if any(palabra in texto for palabra in palabras):
                return intencion
        return "conversacion"

    def _registrar_actividad(self, usuario_id: int, tipo: str, detalle: str, puntos: int = 1):
        actividad = ActividadLectura(
            usuario_id=usuario_id,
            tipo=tipo,
            detalle=detalle,
            puntos=puntos,
            fecha=datetime.utcnow()
        )
        self.db.add(actividad)
        self.db.commit()

    def _dias_actividad(self, usuario_id: int):
        fechas = []

        for actividad in self.db.query(ActividadLectura).filter(ActividadLectura.usuario_id == usuario_id).all():
            fechas.append(actividad.fecha.date())
        for biblioteca in self.db.query(Biblioteca).filter(Biblioteca.usuario_id == usuario_id).all():
            fechas.append(biblioteca.fecha_agregado.date())
        for resena in self.db.query(Reseña).filter(Reseña.usuario_id == usuario_id).all():
            fechas.append(resena.fecha.date())
        for sesion in self.db.query(SesionVibe).filter(SesionVibe.usuario_id == usuario_id).all():
            fechas.append(sesion.fecha.date())

        return sorted(set(fechas))

    def _racha_desde_fechas(self, fechas: list[date]) -> int:
        if not fechas:
            return 0

        fechas_ordenadas = sorted(set(fechas), reverse=True)
        racha = 1
        fecha_actual = fechas_ordenadas[0]

        for fecha in fechas_ordenadas[1:]:
            if (fecha_actual - fecha).days == 1:
                racha += 1
                fecha_actual = fecha
            elif (fecha_actual - fecha).days > 1:
                break

        return racha

    def explicar_recomendacion(self, usuario_id: int, vibe_data: dict, libros: list, inferencias: list) -> dict:
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
        Genera un resumen explicando por qué se detectó ese vibe, por qué se recomendaron esos libros y qué reglas se aplicaron.
        Sé amigable, claro y usa máximo 4 oraciones. Habla directamente al usuario (usa "tú").
        """
        if client:
            try:
                response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
                explicacion = response.text.strip()
            except Exception:
                explicacion = f"Detecté el vibe {vibe_data.get('vibe', 'desconocido')} y prioricé libros acordes con tus señales y hábitos."
        else:
            explicacion = f"Detecté el vibe {vibe_data.get('vibe', 'desconocido')} y prioricé libros acordes con tus señales y hábitos."
        return {
            "vibe_detectado": vibe_data.get("vibe"),
            "tags": vibe_data.get("tags", []),
            "inferencias": inferencias,
            "explicacion": explicacion,
            "total_recomendaciones": len(libros)
        }

    def resumen_usuario(self, usuario_id: int) -> dict:
        biblioteca = self.db.query(Biblioteca).filter(Biblioteca.usuario_id == usuario_id).all()
        reseñas = self.db.query(Reseña).filter(Reseña.usuario_id == usuario_id).all()
        actividades = self.db.query(ActividadLectura).filter(ActividadLectura.usuario_id == usuario_id).all()
        leidos = [b for b in biblioteca if b.estado == "leido"]
        leyendo = [b for b in biblioteca if b.estado == "leyendo"]
        quiero_leer = [b for b in biblioteca if b.estado == "quiero_leer"]
        rating_promedio = 0
        if reseñas:
            rating_promedio = sum(r.calificacion for r in reseñas) / len(reseñas)
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
        sesiones = self.db.query(SesionVibe).filter(SesionVibe.usuario_id == usuario_id).all()
        vibes_conteo = {}
        for s in sesiones:
            v = s.vibe_detectado
            vibes_conteo[v] = vibes_conteo.get(v, 0) + 1
        vibe_favorito = max(vibes_conteo, key=vibes_conteo.get) if vibes_conteo else "sin datos"

        dias_actividad = self._dias_actividad(usuario_id)
        racha_lectura = self._racha_desde_fechas(dias_actividad)
        actividad_30_dias = len([d for d in dias_actividad if (datetime.utcnow().date() - d).days <= 30])
        actividad_7_dias = len([d for d in dias_actividad if (datetime.utcnow().date() - d).days <= 7])
        if len(leidos) >= 20:
            nivel_lector = "Experto"
        elif len(leidos) >= 10:
            nivel_lector = "Avanzado"
        elif len(leidos) >= 5:
            nivel_lector = "Intermedio"
        else:
            nivel_lector = "Inicial"
        retos = [
            {
                "titulo": "Racha de 7 días",
                "descripcion": "Mantén actividad lectora durante una semana seguida.",
                "progreso": min(100, round((racha_lectura / 7) * 100)),
            },
            {
                "titulo": "5 libros completados",
                "descripcion": "Alcanza cinco libros terminados para desbloquear el nivel lector.",
                "progreso": min(100, round((len(leidos) / 5) * 100)),
            },
            {
                "titulo": "3 reseñas útiles",
                "descripcion": "Escribe tres reseñas con criterio para afinar tus recomendaciones.",
                "progreso": min(100, round((len(reseñas) / 3) * 100)),
            },
        ]

        if not dias_actividad:
            inferencias_perfil.append("Aún no hay actividad suficiente para calcular racha de lectura")

        retos_usuario = [
            {
                "id": reto.id,
                "titulo": reto.titulo,
                "descripcion": reto.descripcion,
                "progreso": reto.progreso,
                "objetivo": reto.objetivo,
                "es_sistema": bool(reto.es_sistema)
            }
            for reto in self.db.query(RetoLectura).filter(RetoLectura.usuario_id == usuario_id).order_by(RetoLectura.fecha_creacion.desc()).all()
        ]

        if retos_usuario:
            retos.extend(retos_usuario)

        return {
            "estadisticas": {
                "libros_leidos": len(leidos),
                "leyendo_ahora": len(leyendo),
                "quiero_leer": len(quiero_leer),
                "total_reseñas": len(reseñas),
                "rating_promedio": round(rating_promedio, 1),
                "racha_lectura": racha_lectura,
                "dias_activos_30": actividad_30_dias,
                "progreso_semanal": min(100, round((actividad_7_dias / 7) * 100)),
                "actividad_total": len(actividades)
            },
            "nivel_lector": nivel_lector,
            "vibe_favorito": vibe_favorito,
            "inferencias_perfil": inferencias_perfil,
            "retos": retos,
            "ultima_actividad": dias_actividad[0].isoformat() if dias_actividad else None,
            "actividad_reciente": [
                {
                    "tipo": a.tipo,
                    "detalle": a.detalle,
                    "fecha": a.fecha.isoformat()
                }
                for a in sorted(actividades, key=lambda item: item.fecha, reverse=True)[:5]
            ]
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
        self._registrar_actividad(usuario_id, "vibe", f"Analizó entrada de tipo {tipo}", 1)

    def responder_chat_libros(self, usuario_id: int, mensaje: str) -> dict:
        resumen = self.resumen_usuario(usuario_id)
        intencion = self._detectar_intencion(mensaje)
        contexto = f"""
        Usuario lector con estas estadísticas:
        - Libros leídos: {resumen['estadisticas']['libros_leidos']}
        - Leyendo ahora: {resumen['estadisticas']['leyendo_ahora']}
        - Por leer: {resumen['estadisticas']['quiero_leer']}
        - Racha actual: {resumen['estadisticas']['racha_lectura']}
        - Vibe favorito: {resumen['vibe_favorito']}
        Inferencias: {', '.join(resumen['inferencias_perfil'])}
        """

        prompt = f"""
        Eres un chatbot experto en libros modernos, recomendaciones de BookTok y sistema experto explicable.
        Responde al usuario con tono natural, cercano y útil.
        Debes incluir:
        - una respuesta directa a su pregunta;
        - una inferencia breve sobre su perfil lector si aplica;
        - una sugerencia práctica siguiente si aplica;
        - máximo 5 oraciones.

        Contexto del usuario:
        {contexto}

        Mensaje del usuario:
        {mensaje}
        """

        if client:
            try:
                response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
                respuesta = response.text.strip()
            except Exception:
                respuesta = f"Puedo ayudarte con libros, inferencias y hábitos de lectura. Veo una racha de {resumen['estadisticas']['racha_lectura']} días y te sugeriría seguir con una recomendación que encaje con tu vibe {resumen['vibe_favorito']}."
        else:
            respuesta = f"Puedo ayudarte con libros, inferencias y hábitos de lectura. Veo una racha de {resumen['estadisticas']['racha_lectura']} días y te sugeriría seguir con una recomendación que encaje con tu vibe {resumen['vibe_favorito']}."

        self._registrar_actividad(usuario_id, "chat", mensaje[:250], 1)
        return {
            "respuesta": respuesta,
            "resumen": resumen,
            "intencion": intencion
        }
