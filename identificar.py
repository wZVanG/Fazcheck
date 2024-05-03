import cv2
import insightface
import redis
import numpy as np
from insightface.data import get_image as ins_get_image

# Inicializar el modelo de reconocimiento facial
model = insightface.app.FaceAnalysis(name='buffalo_l',root='insightface_model')
model.prepare(ctx_id=0)  # Remove the nms parameter

# Conectar a la base de datos Redis
r = redis.Redis(host='localhost', port=6379, db=0)

def identificar_rostro(ruta_imagen):
    # Obtener caras detectadas y sus embeddings
    faces = model.get(ruta_imagen)

    nombres_identificados = []
    coordenadas_caras = []

    for face in faces:
        embedding = face.embedding

        # Buscar el vector más cercano en Redis
        min_distancia = float('inf')
        nombre_identificado = None

        for clave in r.keys():
            face_embedding_bytes = r.get(clave)
            vector_almacenado = np.frombuffer(face_embedding_bytes, dtype=np.float32)
            distancia = np.linalg.norm(embedding - vector_almacenado)
            if distancia < min_distancia:
                min_distancia = distancia
                nombre_identificado = clave.decode()

        if nombre_identificado:
            nombres_identificados.append(nombre_identificado)
            coordenadas_caras.append(face.bbox.astype(int))

    return nombres_identificados, coordenadas_caras

def dibujar_cara_y_nombre(imagen, nombres, coordenadas):
    for nombre, (x, y, w, h) in zip(nombres, coordenadas):
        # Dibujar rectángulo alrededor de la cara
        cv2.rectangle(imagen, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # Mostrar nombre debajo del rectángulo
        cv2.putText(imagen, nombre, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
    return imagen

# Función para capturar video desde la cámara
def capturar_video():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo capturar el video desde la cámara")
            break

        nombres, coordenadas = identificar_rostro(frame)
        frame = dibujar_cara_y_nombre(frame, nombres, coordenadas)

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Ejecutar la función para capturar video
capturar_video()

# Para obtener de una foto cambiar por esto:

# get_img = ins_get_image(ruta_imagen)
# img = model.get(get_img)
# identificar_rostro("/var/www/Enterfast/desconocido6")