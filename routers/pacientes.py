# routers/pacientes.py

# Importa UploadFile y File para manejar la subida de archivos
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
import auth
from database import get_db
import shutil # Usaremos shutil para guardar el archivo

router = APIRouter()

@router.post("/pacientes/", response_model=schemas.Paciente)
def create_paciente(paciente: schemas.PacienteCreate, db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    # Esta función se queda igual
    return crud.create_paciente(db=db, paciente=paciente, usuario_id=1)

@router.get("/pacientes/", response_model=List[schemas.Paciente])
def read_pacientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    # Esta función se queda igual
    pacientes = crud.get_pacientes(db, skip=skip, limit=limit)
    return pacientes

# --- CAMBIOS IMPORTANTES AQUÍ ---
@router.post("/pacientes/{paciente_id}/analisis/", response_model=schemas.Analisis)
# 1. Ya no pedimos 'analisis: schemas.AnalisisCreate'
# 2. Añadimos un nuevo parámetro 'file: UploadFile = File(...)'
async def create_analisis(
    paciente_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(auth.oauth2_scheme),
    file: UploadFile = File(...)
):
    # 3. Define la ruta donde se guardará el archivo
    file_path = f"uploads/{file.filename}"

    # 4. Guarda el archivo en el disco
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 5. Llama a la función CRUD, pasándole la ruta del archivo guardado
    return crud.create_analisis_for_paciente(
        db=db,
        paciente_id=paciente_id,
        ruta_imagen_mri=file_path  # Pasamos la ruta real
    )


@router.get("/pacientes/{paciente_id}/analisis/", response_model=List[schemas.Analisis])
def read_analisis_for_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(auth.oauth2_scheme)
):
    """
    Obtiene el historial de análisis para un paciente específico.
    """
    analisis_list = crud.get_analisis_for_paciente(db=db, paciente_id=paciente_id)
    return analisis_list

