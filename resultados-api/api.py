from flask import Flask, jsonify
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# Helper functions to generate random results
def generate_football_result():
    teams = ["Barcelona", "Real Madrid", "Manchester United", "Liverpool", 
             "Bayern Munich", "PSG", "Juventus", "Inter Milan", "Alaves", "Porto"]
    home_team = random.choice(teams)
    away_team = random.choice([t for t in teams if t != home_team])
    home_score = random.randint(0, 5)
    away_score = random.randint(0, 5)
    
    return {
        "deporte": "Futbol",
        "equipo_local": home_team,
        "equipo_visitante": away_team,
        "marcador_local": home_score,
        "marcador_visitante": away_score,
        "fecha": (datetime.now() - timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d")
    }

def generate_basketball_result():
    teams = ["LA Lakers", "Boston Celtics", "Chicago Bulls", "Baskonia",
             "Miami Heat", "Toronto Raptors", "Dallas Mavericks", "Brooklyn Nets"]
    home_team = random.choice(teams)
    away_team = random.choice([t for t in teams if t != home_team])
    home_score = random.randint(70, 120)
    away_score = random.randint(70, 120)
    
    return {
        "deporte": "Baloncesto",
        "equipo_local": home_team,
        "equipo_visitante": away_team,
        "puntos_local": home_score,
        "puntos_visitante": away_score,
        "fecha": (datetime.now() - timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d")
    }

def generate_tennis_result():
    players = ["Rafael Nadal", "Novak Djokovic", "Roger Federer", "Carlos Alcaraz",
               "Serena Williams", "Naomi Osaka", "Iga Swiatek", "Paula Badosa"]
    player1 = random.choice(players)
    player2 = random.choice([p for p in players if p != player1])
    
    sets = []
    winner = random.choice([player1, player2])
    
    # Generate plausible set results
    if random.random() > 0.3:  # Most matches are not 5 sets
        num_sets = 3
    else:
        num_sets = 5
        
    sets_won = {player1: 0, player2: 0}
    needed_to_win = (num_sets // 2) + 1
    
    while max(sets_won.values()) < needed_to_win:
        set_winner = player1 if sets_won[player2] >= needed_to_win else (
                     player2 if sets_won[player1] >= needed_to_win else 
                     random.choice([player1, player2]))
        
        if set_winner == player1:
            score = f"{random.randint(6, 7)}-{random.randint(0, 5)}"
            sets_won[player1] += 1
        else:
            score = f"{random.randint(0, 5)}-{random.randint(6, 7)}"
            sets_won[player2] += 1
            
        sets.append({"puntuacion": score})
    
    winner = player1 if sets_won[player1] > sets_won[player2] else player2
    
    return {
        "deporte": "Tenis",
        "jugador1": player1,
        "jugador2": player2,
        "ganador": winner,
        "sets": sets,
        "fecha": (datetime.now() - timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d")
    }

def generate_f1_result():
    drivers = ["Lewis Hamilton", "Max Verstappen", "Fernando Alonso", "Charles Leclerc",
               "Carlos Sainz", "Sergio Pérez", "Lando Norris", "George Russell"]
    
    # Shuffle drivers for random positions
    random.shuffle(drivers)
    
    results = []
    for i, driver in enumerate(drivers[:10]):  # Top 10 finishers
        results.append({
            "posición": i + 1,
            "piloto": driver,
            "tiempo": f"1:{random.randint(30, 35)}:{random.randint(10, 59)}.{random.randint(100, 999)}"
        })
    
    return {
        "deporte": "Formula 1",
        "circuito": random.choice(["Mónaco", "Silverstone", "Monza", "Spa", "Barcelona", "Austin"]),
        "resultados": results,
        "fecha": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
    }

# API endpoints
@app.route('/api/resultados/futbol', methods=['GET'])
def football_result():
    return jsonify([generate_football_result() for _ in range(10)])

@app.route('/api/resultados/baloncesto', methods=['GET'])
def basketball_result():
    return jsonify([generate_basketball_result() for _ in range(10)])

@app.route('/api/resultados/tenis', methods=['GET'])
def tennis_result():
    return jsonify([generate_tennis_result() for _ in range(10)])

@app.route('/api/resultados/formula1', methods=['GET'])
def f1_result():
    return jsonify([generate_f1_result() for _ in range(10)])

@app.route('/api/resultados/aleatorio', methods=['GET'])
def random_result():
    generators = [
        generate_football_result,
        generate_basketball_result,
        generate_tennis_result,
        generate_f1_result
    ]
    selected_generator = random.choice(generators)
    return jsonify([selected_generator() for _ in range(10)])

@app.route('/api/resultados/todos', methods=['GET'])
def all_results():
    results = {
        "futbol": [generate_football_result() for _ in range(10)],
        "baloncesto": [generate_basketball_result() for _ in range(10)],
        "tenis": [generate_tennis_result() for _ in range(10)],
        "formula1": [generate_f1_result() for _ in range(10)]
    }
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)