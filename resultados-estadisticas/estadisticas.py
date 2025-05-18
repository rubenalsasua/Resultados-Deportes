import pika
import json
import time
from collections import defaultdict

# Conexión a RabbitMQ
credentials = pika.PlainCredentials('user', 'bitnami')
parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)

# Diccionarios para almacenar estadísticas
estadisticas = {
    'futbol': {
        'goleadores': defaultdict(int),      # Equipos con más goles marcados
        'victorias': defaultdict(int),       # Equipos con más victorias
        'total_partidos': 0,                 # Total de partidos procesados
        'promedio_goles': 0                  # Promedio de goles por partido
    },
    'baloncesto': {
        'puntuaciones': defaultdict(list),   # Lista de puntos por equipo 
        'victorias': defaultdict(int),       # Equipos con más victorias
        'total_partidos': 0                  # Total de partidos procesados
    },
    'tenis': {
        'victorias': defaultdict(int),       # Jugadores con más victorias
        'total_partidos': 0                  # Total de partidos procesados
    },
    'formula1': {
        'podios': defaultdict(lambda: defaultdict(int)),  # Pilotos con más podios por circuito
        'victorias_piloto': defaultdict(int),             # Pilotos con más victorias
        'total_carreras': 0                               # Total de carreras procesadas
    }
}

# Función para actualizar estadísticas de fútbol
def actualizar_futbol(result):
    # Contar goles
    estadisticas['futbol']['goleadores'][result['equipo_local']] += result['marcador_local']
    estadisticas['futbol']['goleadores'][result['equipo_visitante']] += result['marcador_visitante']
    
    # Contar victorias
    if result['marcador_local'] > result['marcador_visitante']:
        estadisticas['futbol']['victorias'][result['equipo_local']] += 1
    elif result['marcador_local'] < result['marcador_visitante']:
        estadisticas['futbol']['victorias'][result['equipo_visitante']] += 1
    
    # Actualizar total partidos y promedio goles
    estadisticas['futbol']['total_partidos'] += 1
    total_goles = sum(estadisticas['futbol']['goleadores'].values())
    if estadisticas['futbol']['total_partidos'] > 0:
        estadisticas['futbol']['promedio_goles'] = total_goles / (estadisticas['futbol']['total_partidos'] * 2)  # Dividido por partidos * 2 equipos

# Función para actualizar estadísticas de baloncesto
def actualizar_baloncesto(result):
    # Registrar puntos
    estadisticas['baloncesto']['puntuaciones'][result['equipo_local']].append(result['puntos_local'])
    estadisticas['baloncesto']['puntuaciones'][result['equipo_visitante']].append(result['puntos_visitante'])
    
    # Contar victorias
    if result['puntos_local'] > result['puntos_visitante']:
        estadisticas['baloncesto']['victorias'][result['equipo_local']] += 1
    elif result['puntos_local'] < result['puntos_visitante']:
        estadisticas['baloncesto']['victorias'][result['equipo_visitante']] += 1
    
    # Actualizar total partidos
    estadisticas['baloncesto']['total_partidos'] += 1

# Función para actualizar estadísticas de tenis
def actualizar_tenis(result):
    # Contar victorias
    estadisticas['tenis']['victorias'][result['ganador']] += 1
    
    # Actualizar total partidos
    estadisticas['tenis']['total_partidos'] += 1

# Función para actualizar estadísticas de Formula 1
def actualizar_formula1(result):
    circuito = result['circuito']
    
    # Registrar podios (posiciones 1-3)
    for posicion in result['resultados'][:3]:  # Primeras 3 posiciones
        piloto = posicion['piloto']
        puesto = posicion['posición']
        estadisticas['formula1']['podios'][circuito][piloto] += 1
        
        # Contar victoria si es posición 1
        if puesto == 1:
            estadisticas['formula1']['victorias_piloto'][piloto] += 1
    
    # Actualizar total carreras
    estadisticas['formula1']['total_carreras'] += 1

# Función para mostrar las estadísticas acumuladas
def mostrar_estadisticas():
    print("\n\n================ ESTADÍSTICAS DEPORTIVAS ================")
    
    # Estadísticas de fútbol
    print("\n🥅 FÚTBOL:")
    if estadisticas['futbol']['total_partidos'] > 0:
        print(f"  Partidos procesados: {estadisticas['futbol']['total_partidos']}")
        print(f"  Promedio de goles por partido: {estadisticas['futbol']['promedio_goles']:.2f}")
        
        print("  Equipos más goleadores:")
        equipos_goleadores = sorted(estadisticas['futbol']['goleadores'].items(), key=lambda x: x[1], reverse=True)
        for i, (equipo, goles) in enumerate(equipos_goleadores[:5]):
            print(f"    {i+1}. {equipo}: {goles} goles")
        
        print("  Equipos con más victorias:")
        equipos_ganadores = sorted(estadisticas['futbol']['victorias'].items(), key=lambda x: x[1], reverse=True)
        for i, (equipo, victorias) in enumerate(equipos_ganadores[:5]):
            print(f"    {i+1}. {equipo}: {victorias} victorias")
    else:
        print("  No hay datos suficientes")
    
    # Estadísticas de baloncesto
    print("\n🏀 BALONCESTO:")
    if estadisticas['baloncesto']['total_partidos'] > 0:
        print(f"  Partidos procesados: {estadisticas['baloncesto']['total_partidos']}")
        
        # Calcular promedio de puntos por equipo
        promedio_puntos = {}
        for equipo, puntos in estadisticas['baloncesto']['puntuaciones'].items():
            if puntos:
                promedio_puntos[equipo] = sum(puntos) / len(puntos)
        
        print("  Equipos con mayor promedio de puntos:")
        mejores_ofensivas = sorted(promedio_puntos.items(), key=lambda x: x[1], reverse=True)
        for i, (equipo, promedio) in enumerate(mejores_ofensivas[:5]):
            print(f"    {i+1}. {equipo}: {promedio:.1f} puntos por partido")
        
        print("  Equipos con más victorias:")
        equipos_ganadores = sorted(estadisticas['baloncesto']['victorias'].items(), key=lambda x: x[1], reverse=True)
        for i, (equipo, victorias) in enumerate(equipos_ganadores[:5]):
            print(f"    {i+1}. {equipo}: {victorias} victorias")
    else:
        print("  No hay datos suficientes")
    
    # Estadísticas de tenis
    print("\n🎾 TENIS:")
    if estadisticas['tenis']['total_partidos'] > 0:
        print(f"  Partidos procesados: {estadisticas['tenis']['total_partidos']}")
        
        print("  Jugadores con más victorias:")
        jugadores_ganadores = sorted(estadisticas['tenis']['victorias'].items(), key=lambda x: x[1], reverse=True)
        for i, (jugador, victorias) in enumerate(jugadores_ganadores[:5]):
            print(f"    {i+1}. {jugador}: {victorias} victorias")
    else:
        print("  No hay datos suficientes")
    
    # Estadísticas de Formula 1
    print("\n🏎️ FORMULA 1:")
    if estadisticas['formula1']['total_carreras'] > 0:
        print(f"  Carreras procesadas: {estadisticas['formula1']['total_carreras']}")
        
        print("  Pilotos con más victorias:")
        pilotos_ganadores = sorted(estadisticas['formula1']['victorias_piloto'].items(), key=lambda x: x[1], reverse=True)
        for i, (piloto, victorias) in enumerate(pilotos_ganadores[:5]):
            print(f"    {i+1}. {piloto}: {victorias} victorias")
        
        print("  Circuitos más dominados:")
        for circuito, pilotos in estadisticas['formula1']['podios'].items():
            if pilotos:
                mejor_piloto = max(pilotos.items(), key=lambda x: x[1])
                print(f"    {circuito}: {mejor_piloto[0]} ({mejor_piloto[1]} podios)")
    else:
        print("  No hay datos suficientes")
    
    print("\n=======================================================\n")

# Función de callback para procesar mensajes
def callback(ch, method, properties, body):
    try:
        # Obtener el deporte desde la routing key
        sport = method.routing_key.split('.')[-1]
        result = json.loads(body)
        
        # Actualizar estadísticas según el tipo de deporte
        if sport == 'futbol':
            actualizar_futbol(result)
        elif sport == 'baloncesto':
            actualizar_baloncesto(result)
        elif sport == 'tenis':
            actualizar_tenis(result)
        elif sport == 'formula1':
            actualizar_formula1(result)
        
        print(f"[Estadísticas] Procesado resultado de {sport}")
        
    except Exception as e:
        print(f"[Estadísticas] Error al procesar el mensaje: {str(e)}")

# Hilo principal
try:
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
    
    print('[Estadísticas] Iniciando servicio de estadísticas deportivas...')
    
    # Mostrar estadísticas cada 30 segundos
    last_report_time = time.time()
    
    def process_data_events():
        channel.connection.process_data_events(time_limit=1)  # Procesar eventos por 1 segundo
    
    # Bucle principal
    while True:
        process_data_events()
        
        # Mostrar estadísticas periódicamente
        current_time = time.time()
        if current_time - last_report_time >= 30:  # Cada 30 segundos
            mostrar_estadisticas()
            last_report_time = current_time
    
except KeyboardInterrupt:
    print("[Estadísticas] Servicio detenido por el usuario")
    mostrar_estadisticas()  # Mostrar estadísticas finales
except Exception as e:
    print(f"[Estadísticas] Error en el servicio: {str(e)}")