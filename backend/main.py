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

from models import get_db, crear_tablas, Usuario
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTH ---
SECRET_KEY = os.getenv("SECRET_KEY", "novelia_secret")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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
    estado: str  # "leyendo", "quiero_leer", "leido"

class ActualizarProgreso(BaseModel):
    libro_id: str
    progreso: int

class EscribirReseña(BaseModel):
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

def crear_token(data: dict):
    datos = data.copy()
    datos["exp"] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)

def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        usuario = db.query(Usuario).filter(Usuario.username == username).first()
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return usuario
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# --- RUTAS AUTH ---
@app.post("/registro")
def registro(datos: UsuarioRegistro, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.username == datos.username).first():
        raise HTTPException(status_code=400, detail="Username ya existe")
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
    usuario = db.query(Usuario).filter(Usuario.username == form.username).first()
    if not usuario or not pwd_context.verify(form.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = crear_token({"sub": usuario.username})
    return {"access_token": token, "token_type": "bearer"}

# --- RUTAS VIBE (Agente 1) ---
@app.post("/vibe/texto")
def vibe_texto(datos: VibeTexto, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    agente = VibeAgent()
    vibe_data = agente.detectar_desde_texto(datos.texto)
    supervisor = SupervisorAgent(db)
    supervisor.guardar_sesion_vibe(usuario.id, "texto", datos.texto, vibe_data)
    recommender = RecommenderAgent(db)
    resultado = recommender.recomendar(usuario.id, vibe_data)
    explicacion = supervisor.explicar_recomendacion(usuario.id, vibe_data, resultado["libros"], resultado["inferencias"])
    return {"vibe": vibe_data, "recomendaciones": resultado, "explicacion": explicacion}

@app.post("/vibe/imagen")
async def vibe_imagen(imagen: UploadFile = File(...), usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    contenido = await imagen.read()
    agente = VibeAgent()
    vibe_data = agente.detectar_desde_imagen(contenido)
    supervisor = SupervisorAgent(db)
    supervisor.guardar_sesion_vibe(usuario.id, "imagen", imagen.filename, vibe_data)
    recommender = RecommenderAgent(db)
    resultado = recommender.recomendar(usuario.id, vibe_data)
    explicacion = supervisor.explicar_recomendacion(usuario.id, vibe_data, resultado["libros"], resultado["inferencias"])
    return {"vibe": vibe_data, "recomendaciones": resultado, "explicacion": explicacion}

@app.post("/vibe/cancion")
def vibe_cancion(datos: VibeCancion, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    agente = VibeAgent()
    vibe_data = agente.detectar_desde_cancion(datos.nombre, datos.artista)
    supervisor = SupervisorAgent(db)
    supervisor.guardar_sesion_vibe(usuario.id, "cancion", f"{datos.nombre} - {datos.artista}", vibe_data)
    recommender = RecommenderAgent(db)
    resultado = recommender.recomendar(usuario.id, vibe_data)
    explicacion = supervisor.explicar_recomendacion(usuario.id, vibe_data, resultado["libros"], resultado["inferencias"])
    return {"vibe": vibe_data, "recomendaciones": resultado, "explicacion": explicacion}

@app.post("/vibe/video")
def vibe_video(datos: VibeVideo, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    agente = VibeAgent()
    vibe_data = agente.detectar_desde_video(datos.url)
    supervisor = SupervisorAgent(db)
    supervisor.guardar_sesion_vibe(usuario.id, "video", datos.url, vibe_data)
    recommender = RecommenderAgent(db)
    resultado = recommender.recomendar(usuario.id, vibe_data)
    explicacion = supervisor.explicar_recomendacion(usuario.id, vibe_data, resultado["libros"], resultado["inferencias"])
    return {"vibe": vibe_data, "recomendaciones": resultado, "explicacion": explicacion}

# --- RUTAS BIBLIOTECA (Agente 3) ---
@app.post("/biblioteca/agregar")
def agregar_biblioteca(datos: AgregarBiblioteca, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    agente = LibrarianAgent(db)
    return agente.agregar_a_biblioteca(usuario.id, datos.libro.dict(), datos.estado)

@app.post("/biblioteca/progreso")
def actualizar_progreso(datos: ActualizarProgreso, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    agente = LibrarianAgent(db)
    return agente.actualizar_progreso(usuario.id, datos.libro_id, datos.progreso)

@app.get("/biblioteca")
def obtener_biblioteca(usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    agente = LibrarianAgent(db)
    return agente.obtener_biblioteca(usuario.id)

@app.post("/resenas")
def escribir_reseña(datos: EscribirReseña, usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    agente = LibrarianAgent(db)
    return agente.escribir_reseña(usuario.id, datos.libro_id, datos.calificacion, datos.texto)

# --- RUTAS PERFIL (Agente 4) ---
@app.get("/perfil/resumen")
def resumen_perfil(usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    supervisor = SupervisorAgent(db)
    return supervisor.resumen_usuario(usuario.id)

@app.get("/")
def root():
    return {"mensaje": "Novelia API funcionando 🎉"}