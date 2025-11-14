# ml_model.py

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Layer, Conv2D, Multiply
from tensorflow.keras import backend as K
import numpy as np
import cv2 as cv

# --- 1. Definición de la Capa Personalizada ---
# Copiamos la definición de tu script de entrenamiento
# para que TensorFlow sepa qué es "SpatialAttention" al cargar el modelo.
class SpatialAttention(Layer):
    def __init__(self, kernel_size=7, **kwargs):
        super(SpatialAttention, self).__init__(**kwargs)
        self.kernel_size = kernel_size
        self.conv = Conv2D(1, kernel_size=kernel_size, strides=1, padding='same', activation='sigmoid', use_bias=False)

    def call(self, inputs):
        original_dtype = inputs.dtype
        if original_dtype != tf.float32:
            inputs = tf.cast(inputs, tf.float32)

        avg_pool = K.mean(inputs, axis=-1, keepdims=True)
        max_pool = K.max(inputs, axis=-1, keepdims=True)
        concat = K.concatenate([avg_pool, max_pool], axis=-1)

        attention_map = self.conv(concat)

        if original_dtype != tf.float32:
             attention_map = tf.cast(attention_map, original_dtype)

        attended_feature = Multiply()([inputs, attention_map])
        return attended_feature

    def get_config(self):
        config = super(SpatialAttention, self).get_config()
        config.update({"kernel_size": self.kernel_size})
        return config


# --- 2. Variables Globales del Modelo ---
model = None
IMG_SIZE = (128, 128)
CLASS_NAMES = ['LevementeDemente', 'ModeradamenteDemente', 'NoDemente', 'MuyLevementeDemente']


# --- 3. Función para Cargar el Modelo ---
def load_ml_model():
    """Carga el modelo de IA en la memoria."""
    global model
    try:
        # Aquí le decimos a Keras que reconozca tu capa personalizada
        model = load_model(
            'alzheimer_model.h5', 
            custom_objects={'SpatialAttention': SpatialAttention}
        )
        print("Modelo de Alzheimer cargado exitosamente.")
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")


# --- 4. Función de Preprocesamiento ---
def preprocess_image(image_path: str):
    """Carga, redimensiona y normaliza una imagen desde una ruta."""
    img = cv.imread(image_path)
    if img is None:
        raise ValueError(f"No se pudo leer la imagen desde la ruta: {image_path}")
    
    img = cv.resize(img, IMG_SIZE)
    img_array = np.array(img).astype('float32') / 255.0
    
    # Añade la dimensión del "batch" (lote)
    img_batch = np.expand_dims(img_array, axis=0)
    return img_batch


# --- 5. Función de Predicción ---
def predict_image(image_path: str):
    """Realiza una predicción completa de la imagen."""
    global model
    if model is None:
        print("El modelo no está cargado.")
        return "Error", 0.0, None

    # Preprocesa la imagen
    try:
        image_batch = preprocess_image(image_path)
    except Exception as e:
        print(f"Error al preprocesar la imagen: {e}")
        return "Error Preprocesamiento", 0.0, None

    # Realiza la predicción
    prediction_scores = model.predict(image_batch)
    
    # Interpreta los resultados
    predicted_class_index = np.argmax(prediction_scores, axis=1)[0]
    predicted_label = CLASS_NAMES[predicted_class_index]
    confidence = float(np.max(prediction_scores[0]))
    
    # Devuelve el resultado y la confianza
    return predicted_label, confidence, prediction_scores[0]
