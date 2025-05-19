from flask import Flask, jsonify, render_template
from pymongo import MongoClient
import requests

app = Flask(__name__)

# Conexión a MongoDB (nombre de servicio y base de datos correctos)
mongo_client = MongoClient("mongodb://mongodb:27017/")
db = mongo_client['resultados_deportes']

# Colecciones por deporte
colecciones = ['futbol', 'baloncesto', 'tenis', 'formula1']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/datos')
def get_datos():
    datos = []
    for col in colecciones:
        for doc in db[col].find({}, {'_id': 0}).limit(25):
            doc['deporte'] = col
            datos.append(doc)
    return jsonify(datos)

@app.route('/api/alertas')
def get_alertas():
    # Si tienes una colección específica de alertas, cámbiala aquí.
    # Si no, puedes dejarlo vacío o simular alertas.
    return jsonify([])

@app.route('/api/rabbitmq')
def get_rabbitmq_status():
    RABBITMQ_API = "http://rabbitmq:15672/api/queues"
    RABBITMQ_USER = "user"
    RABBITMQ_PASS = "bitnami"
    try:
        response = requests.get(RABBITMQ_API, auth=(RABBITMQ_USER, RABBITMQ_PASS))
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)