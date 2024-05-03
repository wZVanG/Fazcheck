import redis
import json

# Conectar a la base de datos Redis
r = redis.Redis(host='localhost', port=6379, db=0)

data = {}  # Diccionario para almacenar los datos

for key in r.keys():
    value = r.get(key)
    # Convertir el valor binario a una lista de números
    value_list = list(value)  
    data[key.decode()] = value_list

# Guardar el diccionario como JSON
with open("datos_redis.json", "w") as f:
    json.dump(data, f, indent=4)  # indent para mejor legibilidad

print("Datos guardados en datos_redis.json")