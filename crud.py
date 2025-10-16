from sqlalchemy.orm import Session
import models
import schemas
import auth

# --- CRUD para Usuarios ---
def get_usuario_by_nombre_usuario(db: Session, nombre_usuario: str):
    return db.query(models.Usuario).filter(models.Usuario.nombre_usuario == nombre_usuario).first()

def create_usuario(db: Session, usuario: schemas.UsuarioCreate):
    hashed_password = auth.get_password_hash(usuario.contrasena)
    db_usuario = models.Usuario(
        nombre_usuario=usuario.nombre_usuario,
        contrasena=hashed_password,
        nombre_completo=usuario.nombre_completo,
        #especialidad=usuario.especialidad
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

# --- CRUD para Pacientes ---
def get_pacientes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Paciente).offset(skip).limit(limit).all()

def create_paciente(db: Session, paciente: schemas.PacienteCreate, usuario_id: int):
    db_paciente = models.Paciente(**paciente.dict(), usuario_id=usuario_id)
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    return db_paciente

# --- CRUD para Analisis ---
# La función ahora recibe 'ruta_imagen_mri' como un string, no como un objeto schema
def create_analisis_for_paciente(db: Session, paciente_id: int, ruta_imagen_mri: str):
    # Simulación del análisis de Deep Learning
    resultado_tecnico = "Simulación: El análisis hipocampal muestra una ligera atrofia cortical."
    resultado_explicado = "Simulación: Se han encontrado algunos marcadores tempranos que podrían ser indicativos de Alzheimer. Se recomienda seguimiento."

    db_analisis = models.Analisis(
        paciente_id=paciente_id,
        ruta_imagen_mri=ruta_imagen_mri, # Usamos la ruta que recibimos
        resultado_tecnico=resultado_tecnico,
        resultado_explicado=resultado_explicado
    )
    db.add(db_analisis)
    db.commit()
    db.refresh(db_analisis)
    return db_analisis
