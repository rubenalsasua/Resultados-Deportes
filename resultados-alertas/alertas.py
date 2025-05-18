import pika
import json

# Conexión a RabbitMQ
credentials = pika.PlainCredentials('user', 'bitnami')
parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)

# Criterios para detectar resultados inusuales
def es_resultado_inusual(result, sport):
    if sport == 'futbol':
        # Goleadas (diferencia de 4 o más goles)
        if abs(result['marcador_local'] - result['marcador_visitante']) >= 4:
            return f"ALERTA: Goleada en fútbol! {result['equipo_local']} {result['marcador_local']} - {result['marcador_visitante']} {result['equipo_visitante']}"
        # Muchos goles en total (7 o más)
        if (result['marcador_local'] + result['marcador_visitante']) >= 7:
            return f"ALERTA: Partido de fútbol con muchos goles! {result['equipo_local']} {result['marcador_local']} - {result['marcador_visitante']} {result['equipo_visitante']}"
    
    elif sport == 'baloncesto':
        # Diferencia muy amplia (30+ puntos)
        if abs(result['puntos_local'] - result['puntos_visitante']) >= 30:
            return f"ALERTA: Paliza en baloncesto! {result['equipo_local']} {result['puntos_local']} - {result['puntos_visitante']} {result['equipo_visitante']}"
        # Partidos de muy alta puntuación (220+ puntos totales)
        if (result['puntos_local'] + result['puntos_visitante']) >= 220:
            return f"ALERTA: Partido de baloncesto de alta puntuación! {result['equipo_local']} {result['puntos_local']} - {result['puntos_visitante']} {result['equipo_visitante']}"
        # Partidos de muy baja puntuación (130 o menos puntos totales)
        if (result['puntos_local'] + result['puntos_visitante']) <= 130:
            return f"ALERTA: Partido de baloncesto de baja puntuación! {result['equipo_local']} {result['puntos_local']} - {result['puntos_visitante']} {result['equipo_visitante']}"
    
    elif sport == 'tenis':
        # Victoria muy clara (todos los sets con gran diferencia)
        sets_claros = True
        for set_data in result['sets']:
            puntos = set_data['puntuacion'].split('-')
            if abs(int(puntos[0]) - int(puntos[1])) < 4:
                sets_claros = False
                break
        
        if sets_claros and len(result['sets']) >= 3:
            return f"ALERTA: Victoria aplastante en tenis! {result['ganador']} ha derrotado a {result['jugador1'] if result['ganador'] != result['jugador1'] else result['jugador2']}"
    
    elif sport == 'formula1':
        # Llegadas muy ajustadas entre los primeros puestos
        if len(result['resultados']) >= 2:
            # Simulamos una comparación de tiempos cercanos
            if random.random() < 0.3:  # 30% de probabilidad para simular finales ajustados
                return f"ALERTA: Final ajustado en F1 en {result['circuito']}! Diferencia de menos de 1 segundo entre {result['resultados'][0]['piloto']} y {result['resultados'][1]['piloto']}"
        
        # Circuito con incidentes
        if random.random() < 0.2:  # 20% de probabilidad
            return f"ALERTA: Múltiples incidentes en el circuito de {result['circuito']}!"
    
    return None

def callback(ch, method, properties, body):
    try:
        # Obtener el deporte desde la routing key
        sport = method.routing_key.split('.')[-1]
        result = json.loads(body)
        
        # Verificar si es un resultado inusual
        alerta = es_resultado_inusual(result, sport)
        
        if alerta:
            print(f"\033[1;31m{alerta}\033[0m")  # Imprimir en rojo para destacar
            # Aquí se podría enviar la alerta a otros sistemas (correo, SMS, etc.)
        else:
            print(f"[Alertas] Resultado normal de {sport} analizado")
            
    except Exception as e:
        print(f"[Alertas] Error al procesar el mensaje: {str(e)}")

try:
    # Importamos random aquí para evitar problemas si no se usa antes
    import random
    
    # Conexión a RabbitMQ
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Declarar exchange
    channel.exchange_declare(exchange='resultados', exchange_type='topic')
    
    # Crear cola exclusiva
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue
    
    # Vincular a todos los tipos de deportes
    routing_patterns = ['resultados.futbol', 'resultados.baloncesto', 
                        'resultados.tenis', 'resultados.formula1']
    
    for pattern in routing_patterns:
        channel.queue_bind(
            exchange='resultados',
            queue=queue_name,
            routing_key=pattern
        )
    
    # Configurar consumidor
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=True
    )
    
    print('[Alertas] Esperando resultados deportivos para analizar. Presiona CTRL+C para salir...')
    channel.start_consuming()
    
except Exception as e:
    print(f"[Alertas] Error de conexión: {str(e)}")