# schemas.py (COMPLETO Y CORREGIDO)

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

# Schemas para Analisis
class AnalisisBase(BaseModel):
    ruta_imagen_mri: str

class AnalisisCreate(AnalisisBase):
    pass

class Analisis(AnalisisBase):
    id: int
    paciente_id: int
    fecha: datetime
    resultado_tecnico: Optional[str] = None
    resultado_explicado: Optional[str] = None

    class Config:
        from_attributes = True # <--- CAMBIO AQUÍ

# Schemas para Paciente
class PacienteBase(BaseModel):
    nombre: str
    apellidos: str
    dni: str
    sexo: str
    correo: str
    fecha_nacimiento: Optional[date] = None
    antecedentes_familiares: Optional[str] = None

class PacienteCreate(PacienteBase):
    pass

class Paciente(PacienteBase):
    id: int
    usuario_id: Optional[int] = None
    analisis: List[Analisis] = []

    class Config:
        from_attributes = True # <--- CAMBIO AQUÍ

# Schemas para Usuario
class UsuarioBase(BaseModel):
    nombre_usuario: str
    nombre_completo: Optional[str] = None
    #especialidad: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(
        ...,
        min_length=8,
        max_length=72
    )

class Usuario(UsuarioBase):
    id: int
    pacientes: List[Paciente] = []

    class Config:
        from_attributes = True # <--- CAMBIO AQUÍ

# Schema para el Token
class Token(BaseModel):
    access_token: str
    token_type: str
