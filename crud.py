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

    # Después de crear el nuevo usuario, le asignamos pacientes de ejemplo.
    print(f"Creando pacientes de ejemplo para el Dr. {db_usuario.nombre_completo}...")
    pacientes_ejemplo = [
            schemas.PacienteCreate(
                nombre="Juan", 
                apellidos="Pérez", 
                dni=f"111111_{db_usuario.id}", 
                sexo="Masculino", 
                correo=f"juan.perez_{db_usuario.id}@example.com",
                antecedentes_familiares="Hipertensión paterna."
            ),
            schemas.PacienteCreate(
                nombre="Ana", 
                apellidos="García", 
                dni=f"222222_{db_usuario.id}", 
                sexo="Femenino", 
                correo=f"ana.garcia_{db_usuario.id}@example.com",
                antecedentes_familiares="Diabetes materna."
            ),
            schemas.PacienteCreate(
                nombre="Luis", 
                apellidos="Martínez", 
                dni=f"333333_{db_usuario.id}", 
                sexo="Masculino", 
                correo=f"luis.martinez_{db_usuario.id}@example.com",
                antecedentes_familiares="Sin antecedentes relevantes."
            )
        ]

    for paciente_data in pacientes_ejemplo:
        # Crea el paciente
        db_paciente = create_paciente(db, paciente_data, usuario_id=db_usuario.id)

# Ahora creamos una lista con varios análisis de ejemplo
        print(f"Creando múltiples análisis de ejemplo para {db_paciente.nombre}...")
        analisis_multiples = [
            f"/imagenes_ejemplo/{db_paciente.dni}/resonancia_año_1.nii.gz",
            f"/imagenes_ejemplo/{db_paciente.dni}/resonancia_año_2.nii.gz"
        ]

        # Recorremos la lista y creamos un análisis por cada elemento
        for ruta in analisis_multiples:
            create_analisis_for_paciente(
                db=db,
                paciente_id=db_paciente.id,
                ruta_imagen_mri=ruta
            )

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

# crud.py

# ... (mantén todas tus otras funciones CRUD como están)

# --- FUNCIÓN NUEVA AQUÍ ---
def get_analisis_for_paciente(db: Session, paciente_id: int):
    """
    Devuelve una lista de todos los análisis para un paciente específico.
    """
    return db.query(models.Analisis).filter(models.Analisis.paciente_id == paciente_id).all()
