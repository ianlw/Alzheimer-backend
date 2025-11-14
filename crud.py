from sqlalchemy.orm import Session
import models
import schemas
import auth
import ml_model

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
    
    # Esta lógica ahora solo se ejecutará para subidas reales,
    # ya que 'is_example=True' nunca será llamado.
    if is_example:
        print("Creando análisis de SIMULACIÓN (ejemplo).")
        resultado_tecnico = "Simulación: El análisis hipocampal muestra una ligera atrofia cortical."
        resultado_explicado = "Simulación: Se han encontrado algunos marcadores tempranos que podrían ser indicativos de Alzheimer. Se recomienda seguimiento."
    else:
        print(f"Iniciando análisis de ML para la imagen: {ruta_imagen_mri}")
        label, confidence, scores = ml_model.predict_image(ruta_imagen_mri)
        
        if scores is None:
            resultado_tecnico = f"Error en la predicción para: {ruta_imagen_mri}. Diagnóstico: {label}"
            resultado_explicado = "El modelo no pudo procesar la imagen. Verifique el formato o la integridad del archivo."
        else:
            resultado_tecnico = (
                f"Diagnóstico Predicho: {label} (Confianza: {confidence*100:.2f}%). "
                f"Scores: [NoDemente: {scores[2]:.3f}, "
                f"MuyLeve: {scores[3]:.3f}, "
                f"Leve: {scores[0]:.3f}, "
                f"Moderado: {scores[1]:.3f}]"
            )
            resultado_explicado = (
                f"El análisis de la imagen de resonancia magnética sugiere un diagnóstico "
                f"de '{label}' con una confianza del {confidence*100:.2f}%. "
            )
            if label == "NoDemente":
                resultado_explicado += "No se observan signos significativos de demencia."
            else:
                resultado_explicado += "Se recomienda una evaluación clínica más detallada para confirmar el diagnóstico."

    db_analisis = models.Analisis(
        paciente_id=paciente_id,
        ruta_imagen_mri=ruta_imagen_mri,
        resultado_tecnico=resultado_tecnico,
        resultado_explicado=resultado_explicado
    )
    
    db.add(db_analisis)
    db.commit()
    db.refresh(db_analisis)
    
    if not is_example:
        print("Análisis de ML completado y guardado.")
    
    return db_analisis

# --- FUNCIÓN PARA LEER ANÁLISIS ---
def get_analisis_for_paciente(db: Session, paciente_id: int):
    """
    Devuelve una lista de todos los análisis para un paciente específico.
    """
    return db.query(models.Analisis).filter(models.Analisis.paciente_id == paciente_id).all()
