import cv2
import numpy as np
import insightface
import redis
from insightface.data import get_image as ins_get_image

model = insightface.app.FaceAnalysis(name='buffalo_l',root='insightface_model')
model.prepare(ctx_id=0)
r = redis.Redis(host='localhost', port=6379, db=0)

def guardar_persona(tipo_documento, numero_documento, face_embedding_bytes):
    # Clave optimizada para el Hash
    clave = f"p:{tipo_documento}_{numero_documento}"

    r.set(clave, face_embedding_bytes)

    print(f"Vector de rostro de {numero_documento} guardado correctamente.")

def guardar_rostro(ruta_imagen):

    # Extraer tipo y número de documento del nombre de archivo
    nombre_archivo = ruta_imagen.split("/")[-1]
    tipo_documento, numero_documento = nombre_archivo.split("_")[0], nombre_archivo.split("_")[1].split(".")[0]
    tipo_documento = int(tipo_documento)
    
    get_img = ins_get_image(ruta_imagen)
    img = model.get(get_img)
    
    if len(img) == 0:
        print(f"No se detectó ninguna cara en {ruta_imagen}")
        return
    embedding = img[0].embedding

    guardar_persona(tipo_documento, numero_documento, embedding.tobytes())
    
    # Guardar la imagen de cara detectada en un archivo
    rimg = model.draw_on(get_img, [img[0]])
    nombre_archivo_sin_carpeta = ruta_imagen.split("/")[-1]
    nuevo_nombre_archivo = nombre_archivo_sin_carpeta.split(".")[0]
    cv2.imwrite(f"caras_detectadas/{nuevo_nombre_archivo}.jpg", rimg)
    print(f"Imagen de {numero_documento} guardada correctamente.")


# Ejemplo de uso

# Obtener ruta de la carpeta del archivo 1_45897437 usando la ubicacion del archivo que ejecuta el script

ruta_carpeta = "/".join(__file__.split("/")[:-1])

guardar_rostro(f"{ruta_carpeta}/caras/1_77346499")

# Cerrar la conexión a Redis
r.close()
