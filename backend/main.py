from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from models import get_db, crear_tablas, Usuario, RetoLectura, Reseña, Libro
from agents.vibe_agent import VibeAgent
from agents.recommender_agent import RecommenderAgent
from agents.librarian_agent import LibrarianAgent
from agents.supervisor_agent import SupervisorAgent

load_dotenv()
crear_tablas()

app = FastAPI(title="Novelia API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTH ---
SECRET_KEY = os.getenv("SECRET_KEY", "novelia_secret")
ALGORITHM = "HS256"
# Use pbkdf2_sha256 only to avoid bcrypt backend compatibility issues in the current environment
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

class UsuarioRegistro(BaseModel):
    username: str
    email: str
    password: str

class LibroData(BaseModel):
    id: str
    titulo: str
    autor: str
    genero: Optional[str] = ""
    descripcion: Optional[str] = ""
    portada_url: Optional[str] = ""
    tags: Optional[str] = ""

class AgregarBiblioteca(BaseModel):
    libro: LibroData
    estado: str

class ActualizarProgreso(BaseModel):
    libro_id: str
    progreso: int

class EscribirResena(BaseModel):
    libro_id: str
    calificacion: float
    texto: str

class VibeTexto(BaseModel):
    texto: str

class VibeCancion(BaseModel):
    nombre: str
    artista: Optional[str] = ""

class VibeVideo(BaseModel):
    url: str

class ChatLibros(BaseModel):
    mensaje: str

class RecuperarPassword(BaseModel):
    identificador: str
    nueva_password: str

class RetoLecturaBase(BaseModel):
    titulo: str
    descripcion: str
    progreso: int

class RetoLecturaCrear(RetoLecturaBase):
    pass

class RetoLecturaActualizar(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    progreso: Optional[int] = None


def crear_token(data: dict):
    datos = data.copy()
    datos["exp"] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)

def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        usuario = db.query(Usuario).filter(Usuario.username == username).first()
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return usuario
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# --- AUTH ---
@app.post("/registro")
def registro(datos: UsuarioRegistro, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.username == datos.username).first():
        raise HTTPException(status_code=400, detail="Username ya existe")
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    usuario = Usuario(
        username=datos.username,
        email=datos.email,
        password_hash=pwd_context.hash(datos.password)
    )
    db.add(usuario)
    db.commit()
    return {"mensaje": "Usuario registrado exitosamente"}

@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(
        (Usuario.username == form.username) | (Usuario.email == form.username)
    ).first()
    if not usuario or not pwd_context.verify(form.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = crear_token({"sub": usuario.username})
    return {"access_token": token, "token_type": "bearer", "username": usuario.username, "email": usuario.email}

@app.post("/recuperar-password")
def recuperar_password(datos: RecuperarPassword, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(
        (Usuario.username == datos.identificador) | (Usuario.email == datos.identificador)
    ).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.password_hash = pwd_context.hash(datos.nueva_password)
    db.commit()
    return {"mensaje": "Contraseña actualizada correctamente"}

# --- VIBE (Agente 1) ---
@app.post("/vibe/texto")
def vibe_texto(datos: VibeTexto, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        agente = VibeAgent()
        vibe_data = agente.detectar_desde_texto(datos.texto)
        supervisor = SupervisorAgent(db)
        supervisor.guardar_sesion_vibe(usuario.id, "texto", datos.texto, vibe_data)
        recommender = RecommenderAgent(db)
        resultado = recommender.recomendar(usuario.id, vibe_data)
        explicacion = supervisor.explicar_recomendacion(usuario.id, vibe_data, resultado["libros"], resultado["inferencias"])
        return {"vibe": vibe_data, "recomendaciones": resultado, "explicacion": explicacion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vibe/imagen")
async def vibe_imagen(imagen: UploadFile = File(...), usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        contenido = await imagen.read()
        agente = VibeAgent()
        vibe_data = agente.detectar_desde_imagen(contenido)
        supervisor = SupervisorAgent(db)
        supervisor.guardar_sesion_vibe(usuario.id, "imagen", imagen.filename, vibe_data)
        recommender = RecommenderAgent(db)
        resultado = recommender.recomendar(usuario.id, vibe_data)
        explicacion = supervisor.explicar_recomendacion(usuario.id, vibe_data, resultado["libros"], resultado["inferencias"])
        return {"vibe": vibe_data, "recomendaciones": resultado, "explicacion": explicacion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vibe/cancion")
def vibe_cancion(datos: VibeCancion, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        agente = VibeAgent()
        vibe_data = agente.detectar_desde_cancion(datos.nombre, datos.artista)
        supervisor = SupervisorAgent(db)
        supervisor.guardar_sesion_vibe(usuario.id, "cancion", f"{datos.nombre} - {datos.artista}", vibe_data)
        recommender = RecommenderAgent(db)
        resultado = recommender.recomendar(usuario.id, vibe_data)
        explicacion = supervisor.explicar_recomendacion(usuario.id, vibe_data, resultado["libros"], resultado["inferencias"])
        return {"vibe": vibe_data, "recomendaciones": resultado, "explicacion": explicacion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vibe/video")
def vibe_video(datos: VibeVideo, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        agente = VibeAgent()
        vibe_data = agente.detectar_desde_video(datos.url)
        supervisor = SupervisorAgent(db)
        supervisor.guardar_sesion_vibe(usuario.id, "video", datos.url, vibe_data)
        recommender = RecommenderAgent(db)
        resultado = recommender.recomendar(usuario.id, vibe_data)
        explicacion = supervisor.explicar_recomendacion(usuario.id, vibe_data, resultado["libros"], resultado["inferencias"])
        return {"vibe": vibe_data, "recomendaciones": resultado, "explicacion": explicacion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- BIBLIOTECA (Agente 3) ---
@app.post("/biblioteca/agregar")
def agregar_biblioteca(datos: AgregarBiblioteca, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        agente = LibrarianAgent(db)
        return agente.agregar_a_biblioteca(usuario.id, datos.libro.dict(), datos.estado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/biblioteca/progreso")
def actualizar_progreso(datos: ActualizarProgreso, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        agente = LibrarianAgent(db)
        return agente.actualizar_progreso(usuario.id, datos.libro_id, datos.progreso)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/biblioteca")
def obtener_biblioteca(usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        agente = LibrarianAgent(db)
        return agente.obtener_biblioteca(usuario.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resenas")
def escribir_resena(datos: EscribirResena, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        agente = LibrarianAgent(db)
        return agente.escribir_reseña(usuario.id, datos.libro_id, datos.calificacion, datos.texto)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/libros/populares")
def libros_populares(usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        agente = RecommenderAgent(db)
        return agente.libros_populares()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/libros/buscar")
def buscar_libros(q: str, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        agente = RecommenderAgent(db)
        libros = agente.buscar_libros_por_termino(q, max_results=8)
        if not libros:
            libros = agente._fallback_libros([], [q])
        return {"libros": libros, "query": q}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resenas")
def obtener_resenas(usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        reseñas = db.query(Reseña).filter(Reseña.usuario_id == usuario.id).all()
        resultado = []
        for reseña in reseñas:
            libro = db.query(Libro).filter(Libro.id == reseña.libro_id).first()
            resultado.append({
                "libro_id": reseña.libro_id,
                "titulo": libro.titulo if libro else "Título desconocido",
                "autor": libro.autor if libro else "Autor desconocido",
                "calificacion": reseña.calificacion,
                "texto": reseña.texto,
                "fecha": reseña.fecha.isoformat(),
                "portada_url": libro.portada_url if libro else ""
            })
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/retos")
def obtener_retos(usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    retos = db.query(RetoLectura).filter(RetoLectura.usuario_id == usuario.id).order_by(RetoLectura.fecha_creacion.desc()).all()
    return [
        {
            "id": reto.id,
            "titulo": reto.titulo,
            "descripcion": reto.descripcion,
            "progreso": reto.progreso,
            "objetivo": reto.objetivo,
            "es_sistema": bool(reto.es_sistema)
        }
        for reto in retos
    ]

@app.post("/retos")
def crear_reto(datos: RetoLecturaCrear, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    reto = RetoLectura(
        usuario_id=usuario.id,
        titulo=datos.titulo,
        descripcion=datos.descripcion,
        progreso=max(0, min(100, datos.progreso)),
        objetivo="Personalizado",
        es_sistema=0
    )
    db.add(reto)
    db.commit()
    return {"mensaje": "Reto agregado", "reto": {
        "id": reto.id,
        "titulo": reto.titulo,
        "descripcion": reto.descripcion,
        "progreso": reto.progreso,
        "objetivo": reto.objetivo,
        "es_sistema": False
    }}

@app.patch("/retos/{reto_id}")
def actualizar_reto(reto_id: int, datos: RetoLecturaActualizar, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    reto = db.query(RetoLectura).filter(RetoLectura.id == reto_id, RetoLectura.usuario_id == usuario.id).first()
    if not reto:
        raise HTTPException(status_code=404, detail="Reto no encontrado")
    if datos.titulo is not None:
        reto.titulo = datos.titulo
    if datos.descripcion is not None:
        reto.descripcion = datos.descripcion
    if datos.progreso is not None:
        reto.progreso = max(0, min(100, datos.progreso))
    db.commit()
    return {"mensaje": "Reto actualizado", "reto": {
        "id": reto.id,
        "titulo": reto.titulo,
        "descripcion": reto.descripcion,
        "progreso": reto.progreso,
        "objetivo": reto.objetivo,
        "es_sistema": bool(reto.es_sistema)
    }}

@app.delete("/retos/{reto_id}")
def eliminar_reto(reto_id: int, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    reto = db.query(RetoLectura).filter(RetoLectura.id == reto_id, RetoLectura.usuario_id == usuario.id).first()
    if not reto:
        raise HTTPException(status_code=404, detail="Reto no encontrado")
    db.delete(reto)
    db.commit()
    return {"mensaje": "Reto eliminado"}

# --- PERFIL (Agente 4) ---
@app.get("/perfil/resumen")
def resumen_perfil(usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        supervisor = SupervisorAgent(db)
        return supervisor.resumen_usuario(usuario.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/libros")
def chat_libros(datos: ChatLibros, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        supervisor = SupervisorAgent(db)
        return supervisor.responder_chat_libros(usuario.id, datos.mensaje)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/biblioteca/{libro_id}")
def eliminar_de_biblioteca(libro_id: str, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    try:
        from models import Biblioteca
        entrada = db.query(Biblioteca).filter(
            Biblioteca.usuario_id == usuario.id,
            Biblioteca.libro_id == libro_id
        ).first()
        if not entrada:
            raise HTTPException(status_code=404, detail="Libro no encontrado en tu biblioteca")
        db.delete(entrada)
        db.commit()
        return {"mensaje": "Libro eliminado de tu biblioteca"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"mensaje": "Novelia API funcionando 🎉"}