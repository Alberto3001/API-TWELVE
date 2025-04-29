from flask import Flask, jsonify, request
import requests
import logging

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(_name_)

# Lista de API keys actualizadas
api_keys = [
    "feabf983cf074d359445956929a55d85",
    "0e7c0dc8a0e945498c0c4e48ecbc4903",
    "1a633df7fa13469682df09947a790f44",
    "ddf91394e0d249de950824b784f787a0",
    "e02c4efdc3994bcea6d15a6758f0ca6d",
    "bcedf25a07df483c84a4d3225afefdbc",
    "9ac3fd76279d4ba8ba9d6064379c0822",
    "a489561e00d54c0882b2e304623cd0f1",
    "34a2f10cbcc24e288822fe640b9da234",
    "236945029bb741a9a80f058f4654de2b"
]

current_key_index = 0  # Índice de la API key actual
url_time_series = "https://api.twelvedata.com/time_series"
url_price = "https://api.twelvedata.com/price"

def fetch_data(symbol="AAPL", interval="1min", is_crypto=False):
    global current_key_index
    api_key = api_keys[current_key_index]

    # Si es una crypto, se fuerza el par con USD
    if is_crypto:
        symbol = f"{symbol}/USD"

    params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": api_key
    }
    
    try:
        response = requests.get(url_time_series, params=params)
        data = response.json()

        # Si recibimos un error 429 (límite de peticiones), cambiamos de API key
        if data.get("code") == 429:
            logging.warning(f"Límite alcanzado con la API key {api_key}. Cambiando a la siguiente API key.")
            current_key_index = (current_key_index + 1) % len(api_keys)
            return fetch_data(symbol, interval, is_crypto)  # Reintentamos con la nueva API key
        
        return data  # Devolvemos la respuesta de Twelve Data

    except requests.exceptions.RequestException as e:
        logging.error(f"Error en la petición: {e}")
        return {"error": "No se pudo obtener la información"}

def fetch_current_price(symbol="AAPL", is_crypto=False):
    global current_key_index
    api_key = api_keys[current_key_index]

    if is_crypto:
        symbol = f"{symbol}/USD"

    params = {
        "symbol": symbol,
        "apikey": api_key
    }
    
    try:
        response = requests.get(url_price, params=params)
        data = response.json()

        if data.get("code") == 429:
            logging.warning(f"Límite alcanzado con la API key {api_key}. Cambiando a la siguiente API key.")
            current_key_index = (current_key_index + 1) % len(api_keys)
            return fetch_current_price(symbol, is_crypto)  # Reintentamos con la nueva API key
        
        return data  # Devolvemos la respuesta de Twelve Data

    except requests.exceptions.RequestException as e:
        logging.error(f"Error en la petición: {e}")
        return {"error": "No se pudo obtener la información"}

# Endpoint para llamar a Twelve Data
@app.route("/get_market_data", methods=["GET"])
def get_market_data():
    symbol = request.args.get("symbol", "AAPL")  # Permite cambiar el símbolo
    interval = request.args.get("interval", "1min")  # Permite cambiar el intervalo
    is_crypto = request.args.get("crypto", "false").lower() == "true"  # Define si es una crypto

    data = fetch_data(symbol, interval, is_crypto)
    return jsonify(data)

# Nuevo endpoint para obtener solo el precio actual
@app.route("/get_current_price", methods=["GET"])
def get_current_price():
    symbol = request.args.get("symbol", "AAPL")
    is_crypto = request.args.get("crypto", "false").lower() == "true"
    
    data = fetch_current_price(symbol, is_crypto)
    
    if "price" in data:
        return jsonify({"symbol": symbol, "current_price": data["price"]})
    else:
        return jsonify({"error": "No se pudo obtener el precio actual"})
    
@app.route('/status', methods=['GET'])
def status():
    """Endpoint para verificar si el servicio está funcionando correctamente."""
    return jsonify({"status": "OK"}), 200
  

if _name_ == "__main__":
    app.run(debug=True)

    #Hola