from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Usuario(Base):
    __tablename__ = "Usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String, unique=True, index=True, nullable=False)
    contrasena = Column(String, nullable=False)
    nombre_completo = Column(String)
    #especialidad = Column(String)
    fecha_creacion = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    pacientes = relationship("Paciente", back_populates="doctor")

class Paciente(Base):
    __tablename__ = "Pacientes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("Usuarios.id"))
    nombre = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    dni = Column(String, unique=True, index=True, nullable=False)
    sexo = Column(String, unique=False, index=True, nullable=False)
    correo = Column(String, unique=True, index=True, nullable=False)
    fecha_nacimiento = Column(Date)
    antecedentes_familiares = Column(Text)
    fecha_registro = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    doctor = relationship("Usuario", back_populates="pacientes")
    analisis = relationship("Analisis", back_populates="paciente", cascade="all, delete-orphan")

class Analisis(Base):
    __tablename__ = "Analisis"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("Pacientes.id"), nullable=False)
    fecha = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    ruta_imagen_mri = Column(String, nullable=False)
    resultado_tecnico = Column(Text)
    resultado_explicado = Column(Text)

    paciente = relationship("Paciente", back_populates="analisis")
