from fastapi import FastAPI
import models
from database import engine
from routers import usuarios, pacientes
from fastapi.middleware.cors import CORSMiddleware # <--- 1. Importa el middleware
from fastapi.staticfiles import StaticFiles
import os
import ml_model  # <--- 1. IMPORTA TU NUEVO MÓDULO

# Crea las tablas en la base de datos (si no existen)
# Esta línea es crucial para que SQLAlchemy cree tu archivo .db y las tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API para Detección de Alzheimer",
    description="Backend para gestionar médicos, pacientes y análisis de MRI.",
    version="1.0.0"
)

# 2. CONFIGURA LOS ARCHIVOS ESTÁTICOS
# Crea la carpeta si no existe (para evitar errores al iniciar)
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Monta la carpeta: Esto hace la magia.
# Le dice: "Cuando alguien pida /uploads/algo.jpg, busca en la carpeta 'uploads' del disco".
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
async def startup_event():
    """Carga el modelo de ML al iniciar el servidor."""
    print("Iniciando servidor y cargando modelo de ML...")
    ml_model.load_ml_model()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todos los encabezados
)

# Incluir los routers desde la carpeta 'routers'
app.include_router(usuarios.router, tags=["Usuarios y Autenticación"])
app.include_router(pacientes.router, tags=["Pacientes y Análisis"])

@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a la API de Detección de Alzheimer"}
