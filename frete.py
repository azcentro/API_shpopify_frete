from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import dotenv
import os

dotenv.load_dotenv()

app = Flask(__name__)

# Ativar CORS para todas as rotas..
CORS(app)

CORS(app, resources={r"/*": {"origins": "*"}})  # Permitir todos os domínios

# Configurações
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ENDERECO_ORIGEM = "Avenida Dr. Lauro Dornelles, 719, Centro, Alegrete, RS, 97541151"
CUSTO_POR_KM = 2.50  # Exemplo: R$2,50 por km
TARIFA_FIXA = 3.00

# Função para calcular a distância usando Google Maps
def calcular_distancia(endereco_destino):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": ENDERECO_ORIGEM,
        "destinations": endereco_destino,
        "key": GOOGLE_API_KEY,
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] == "OK":
        distancia_metros = data["rows"][0]["elements"][0]["distance"]["value"]
        distancia_km = distancia_metros / 1000  # Convertendo para km
        return distancia_km
    else:
        raise Exception(f"Erro na API do Google: {data['status']}")

# Endpoint para calcular o frete
@app.route("/calcular-frete", methods=["POST"])
def calcular_frete():
    try:
        # Recebe o endereço do cliente
        dados = request.json
        endereco_cliente = dados.get("endereco")

        if not endereco_cliente:
            return jsonify({"erro": "Endereço do cliente não informado"}), 400

        # Calcula a distância
        distancia_km = calcular_distancia(endereco_cliente)

        custo_ajuste = CUSTO_POR_KM

        if distancia_km > 80.00:
            custo_ajuste = 0.5
        elif distancia_km > 40.00:
            custo_ajuste = 0.7

        # Calcula o custo do frete
        custo_frete = (distancia_km * custo_ajuste) + TARIFA_FIXA

        # Retorna o resultado
        return jsonify({
            "distancia_km": round(distancia_km, 2),
            "custo_frete": round(custo_frete, 2),
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
