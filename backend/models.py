from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./novelia.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- TABLAS ---

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    biblioteca = relationship("Biblioteca", back_populates="usuario")
    reseñas = relationship("Reseña", back_populates="usuario")

class Libro(Base):
    __tablename__ = "libros"
    id = Column(String, primary_key=True)  # ID de Google Books
    titulo = Column(String)
    autor = Column(String)
    genero = Column(String)
    descripcion = Column(Text)
    portada_url = Column(String)
    rating_promedio = Column(Float, default=0.0)
    total_reseñas = Column(Integer, default=0)
    tags = Column(String)  # guardados como "tag1,tag2,tag3"

class Biblioteca(Base):
    __tablename__ = "biblioteca"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    libro_id = Column(String, ForeignKey("libros.id"))
    estado = Column(String)  # "leyendo", "quiero_leer", "leido"
    progreso = Column(Integer, default=0)  # porcentaje 0-100
    fecha_agregado = Column(DateTime, default=datetime.utcnow)
    usuario = relationship("Usuario", back_populates="biblioteca")

class Reseña(Base):
    __tablename__ = "reseñas"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    libro_id = Column(String, ForeignKey("libros.id"))
    calificacion = Column(Float)  # 1.0 a 5.0
    texto = Column(Text)
    fecha = Column(DateTime, default=datetime.utcnow)
    usuario = relationship("Usuario", back_populates="reseñas")

class SesionVibe(Base):
    __tablename__ = "sesiones_vibe"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    tipo_entrada = Column(String)  # "texto", "imagen", "cancion", "video"
    entrada_raw = Column(Text)     # lo que escribió/subió el usuario
    vibe_detectado = Column(String)  # "melancolico", "romantico", etc
    tags_generados = Column(String)  # "nostalgia,lluvia,amor"
    fecha = Column(DateTime, default=datetime.utcnow)

def crear_tablas():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()