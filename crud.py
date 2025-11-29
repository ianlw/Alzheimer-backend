from sqlalchemy.orm import Session
import models
import schemas
import auth
import ml_model
import llm_service

# --- CRUD para Usuarios ---
def get_usuario_by_nombre_usuario(db: Session, nombre_usuario: str):
    return db.query(models.Usuario).filter(models.Usuario.nombre_usuario == nombre_usuario).first()

def create_usuario(db: Session, usuario: schemas.UsuarioCreate):
    hashed_password = auth.get_password_hash(usuario.contrasena)
    db_usuario = models.Usuario(
        nombre_usuario=usuario.nombre_usuario,
        contrasena=hashed_password,
        nombre_completo=usuario.nombre_completo,
        #especialidad=usuario.especialidad  # <-- Esta línea fue descomentada
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    # --- SECCIÓN DE DATOS DE EJEMPLO ELIMINADA ---
    # Ya no se crean pacientes ni análisis al registrarse.
    # --- FIN DE LA SECCIÓN ELIMINADA ---

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
def create_analisis_for_paciente(db: Session, paciente_id: int, ruta_imagen_mri: str, is_example: bool = False):
    
    # 2. OBTENER EL PACIENTE PRIMERO
    # Necesitamos sus datos (nombre, edad, etc.) para pasárselos a Gemini
    paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_id).first()
    
    if not paciente:
        # Manejo de error básico si el paciente no existe (aunque la FK lo previene)
        print(f"Paciente {paciente_id} no encontrado.")
        return None

    if is_example:
        # ... (lógica de ejemplo sin cambios) ...
        resultado_tecnico = "Simulación..."
        resultado_explicado = "Simulación..."
    else:
        print(f"Iniciando análisis de ML para la imagen: {ruta_imagen_mri}")
        
        # A. Predicción de la IMAGEN (Tu CNN)
        label, confidence, scores = ml_model.predict_image(ruta_imagen_mri)
        
        if scores is None:
            # Si falla la imagen
            resultado_tecnico = f"Error visual: {label}"
            resultado_explicado = "Error al procesar la imagen."
        else:
            # B. Generación de TEXTO (Gemini LLM)
            print("Consultando a Gemini para generar reporte...")
            
            # Llamamos a la función que creamos en el paso 3
            res_tecnico, res_explicado = llm_service.generar_reporte_medico(
                paciente=paciente,
                diagnostico_cnn=label,
                confianza=confidence,
                scores=scores
            )
            
            resultado_tecnico = res_tecnico
            resultado_explicado = res_explicado

    # Guardado en Base de Datos (Igual que antes)
    db_analisis = models.Analisis(
        paciente_id=paciente_id,
        ruta_imagen_mri=ruta_imagen_mri,
        resultado_tecnico=resultado_tecnico,
        resultado_explicado=resultado_explicado
    )
    
    db.add(db_analisis)
    db.commit()
    db.refresh(db_analisis)
    
    print("Análisis Completo (CNN + LLM) guardado.")
    return db_analisis

# --- FUNCIÓN PARA LEER ANÁLISIS ---
def get_analisis_for_paciente(db: Session, paciente_id: int):
    """
    Devuelve una lista de todos los análisis para un paciente específico.
    """
    return db.query(models.Analisis).filter(models.Analisis.paciente_id == paciente_id).all()
