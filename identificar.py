import cv2
import insightface
import redis
import numpy as np
from insightface.data import get_image as ins_get_image
import time


# Inicializar el modelo de reconocimiento facial
model = insightface.app.FaceAnalysis(name='buffalo_l',root='insightface_model')

# use GPU

model.prepare(ctx_id=0)


nombres_personas = {
    "77346499": "Mercy Ipanaque",
    "45897437": "Walter Chapilliquen",
    "00000001": "Messi",
    "00000002": "Nazario",
    "00000003": "Ronaldo"
}

# Conectar a la base de datos Redis
r = redis.Redis(host='localhost', port=6379, db=0)

MAX_DISTANCE = 20

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
            print("distancia -->", distancia)
            if distancia < min_distancia and distancia <= MAX_DISTANCE:
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
        imagen_valores = nombre.split(":")
        if len(imagen_valores) == 2:
            persona_valores = imagen_valores[1].split("_")

            if len(persona_valores) == 2:

                part_tipo_documento, part_numero_documento = persona_valores

                if part_numero_documento in nombres_personas:
                    nombre_persona = nombres_personas[part_numero_documento]
                    #print("El nombre de la persona es:", nombre_persona)
                else:
                    nombre_persona = 'Desconocido'
                    #print("El número de documento no está en el diccionario.", part_numero_documento)

            else:

                nombre_persona = 'Desconocido'
                #print("El número de documento no tiene el formato esperado.")

        else:
            nombre_persona = 'Desconocido'
            #print("El nombre de la persona no tiene el formato esperado.")

        cv2.putText(imagen, nombre_persona, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        
    return imagen

# Función para capturar video desde la cámara
def capturar_video():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo capturar el video desde la cámara")
            break

        #Calcular tiempo de procesamiento
        start_time = time.time()
        
        nombres, coordenadas = identificar_rostro(frame)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Tiempo de procesamiento identificación: {elapsed_time} segundos")

        frame = dibujar_cara_y_nombre(frame, nombres, coordenadas)

        cv2.imshow('Video', frame)


        # time.sleep(0.1)

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