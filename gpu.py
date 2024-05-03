import tensorflow as tf

# Verificar que la GPU está disponible
if tf.config.list_physical_devices('GPU'):
    print("GPU disponible")

    # Configurar el contexto de ejecución para usar la GPU
    with tf.device('/GPU:0'):
        # ... (Tu código de identificación de rostros usando insightface) ...
        print("OK GPU")
else:
    print("GPU no disponible")