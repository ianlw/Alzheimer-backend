# llm_service.py
import google.generativeai as genai
import os
import json
from datetime import date

# Configura la API Key desde las variables de entorno
# Si estás probando en local y no tienes variables de entorno, puedes pegarla aquí temporalmente,
# pero en producción (Render) debes usar la variable de entorno.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Usamos gemini-1.5-flash porque es rápido y barato, ideal para esta tarea
model = genai.GenerativeModel('gemini-2.5-flash')

def calcular_edad(fecha_nacimiento):
    if not fecha_nacimiento:
        return "Desconocida"
    today = date.today()
    return today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

def generar_reporte_medico(paciente, diagnostico_cnn, confianza, scores):
    """
    Usa Gemini para generar un reporte médico basado en la predicción de la imagen y los datos del paciente.
    """
    
    edad = calcular_edad(paciente.fecha_nacimiento)
    
    # Prompt (Instrucción) para el LLM
    prompt = f"""
    Actúa como un Neurólogo experto especializado en la enfermedad de Alzheimer.
    Tu tarea es generar un reporte médico basado en los datos de un paciente y el análisis de una resonancia magnética (MRI) realizado por un modelo de Inteligencia Artificial.

    DATOS DEL PACIENTE:
    - Nombre: {paciente.nombre} {paciente.apellidos}
    - Edad: {edad} años
    - Sexo: {paciente.sexo}
    - Antecedentes Familiares: {paciente.antecedentes_familiares}

    RESULTADO DEL ANÁLISIS DE IMAGEN (IA):
    - Predicción del Modelo: {diagnostico_cnn}
    - Nivel de Confianza: {confianza * 100:.2f}%
    - Scores brutos: {scores}

    INSTRUCCIONES DE SALIDA:
    Debes generar una respuesta estrictamente en formato JSON con dos campos:
    1. "resultado_tecnico": Un párrafo con terminología médica dirigido a otros doctores. Describe el hallazgo de la imagen, correlaciónalo con la edad y antecedentes, y menciona el nivel de certeza.
    2. "resultado_explicado": Un párrafo empático y claro dirigido al paciente o sus familiares. Explica qué significa el resultado sin usar jerga compleja y sugiere el siguiente paso lógico (ej. más pruebas, seguimiento, hábitos saludables).

    IMPORTANTE:
    - Si la predicción es "NonDemented", sé tranquilizador.
    - Si es "VeryMildDemented" o superior, sé cauto y recomienda confirmación clínica.
    - Responde en Español.
    - NO uses Markdown (```json). Devuelve solo el texto JSON plano.
    """

    try:
        response = model.generate_content(prompt)
        
        # Limpieza básica por si el modelo devuelve markdown
        texto_limpio = response.text.replace("```json", "").replace("```", "").strip()
        
        # Convertir el texto a un diccionario Python
        datos = json.loads(texto_limpio)
        return datos.get("resultado_tecnico"), datos.get("resultado_explicado")

    except Exception as e:
        print(f"Error al generar reporte con Gemini: {e}")
        # Fallback en caso de error
        return (
            f"Análisis IA: {diagnostico_cnn} (Confianza: {confianza:.2%}).",
            "No se pudo generar la explicación detallada en este momento."
        )
