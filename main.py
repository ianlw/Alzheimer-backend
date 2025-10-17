from fastapi import FastAPI
import models
from database import engine
from routers import usuarios, pacientes
from fastapi.middleware.cors import CORSMiddleware # <--- 1. Importa el middleware

# Crea las tablas en la base de datos (si no existen)
# Esta línea es crucial para que SQLAlchemy cree tu archivo .db y las tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API para Detección de Alzheimer",
    description="Backend para gestionar médicos, pacientes y análisis de MRI.",
    version="1.0.0"
)

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
