import pika, json, time, random
import requests

credentials = pika.PlainCredentials('user', 'bitnami')
parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declare an exchange for topic-based routing
channel.exchange_declare(exchange='resultados', exchange_type='topic')

# API endpoints available
endpoints = {
    'futbol': 'http://localhost:5000/api/resultados/futbol',
    'baloncesto': 'http://localhost:5000/api/resultados/baloncesto',
    'tenis': 'http://localhost:5000/api/resultados/tenis',
    'formula1': 'http://localhost:5000/api/resultados/formula1',
    'aleatorio': 'http://localhost:5000/api/resultados/aleatorio'
}

while True:
    try:
        # Select a random sport
        sport = random.choice(list(endpoints.keys()))
        
        # Call the API
        response = requests.get(endpoints[sport])
        
        if response.status_code == 200:
            results = response.json()
            
            # If it's a random result, determine the sport type from the first result
            if sport == 'aleatorio' and results:
                if 'deporte' in results[0]:
                    # Map API sport name to routing key
                    sport_mapping = {
                        'Fútbol': 'futbol',
                        'Baloncesto': 'baloncesto', 
                        'Tenis': 'tenis',
                        'Fórmula 1': 'formula1'
                    }
                    sport = sport_mapping.get(results[0]['deporte'], 'otros')
            
            # Publish each result to RabbitMQ
            for result in results:
                # Convert result to JSON string
                message = json.dumps(result)
                
                # Send message with topic routing key (e.g. 'resultados.futbol')
                routing_key = f"resultados.{sport}"
                channel.basic_publish(
                    exchange='resultados',
                    routing_key=routing_key,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    )
                )
                
                print(f"[Producer] Resultado enviado: {routing_key}")
                print(f"[Producer] Datos: {message[:100]}...")  # Show beginning of the message
        else:
            print(f"[Producer] Error al obtener resultados de {sport}: {response.status_code}")
            
    except Exception as e:
        print(f"[Producer] Error: {str(e)}")
    
    # Wait before next request
    time.sleep(3)