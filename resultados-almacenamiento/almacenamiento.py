import pika, json
from pymongo import MongoClient

# Conexión a MongoDB
mongo_client = MongoClient('mongodb://mongodb:27017/')
db = mongo_client['resultados_deportes']

def callback(ch, method, properties, body):
    try:
        result = json.loads(body)
        sport = method.routing_key.split('.')[-1]
        collection = db[sport]
        collection.insert_one(result)
        print(f"[Almacenamiento] Resultado de {sport} guardado en MongoDB")
        print(f"[Almacenamiento] Datos: {json.dumps(result)[:100]}...")
    except Exception as e:
        print(f"[Almacenamiento] Error procesando mensaje: {str(e)}")

credentials = pika.PlainCredentials('user', 'bitnami')
parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)

try:
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange='resultados', exchange_type='topic')
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue
    routing_patterns = ['resultados.futbol', 'resultados.baloncesto', 
                       'resultados.tenis', 'resultados.formula1']
    
    for pattern in routing_patterns:
        channel.queue_bind(
            exchange='resultados',
            queue=queue_name,
            routing_key=pattern
        )

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=True
    )

    print('[Almacenamiento] Esperando resultados deportivos. Presiona CTRL+C para salir...')
    channel.start_consuming()
    
except Exception as e:
    print(f"[Almacenamiento] Error de conexión: {str(e)}")