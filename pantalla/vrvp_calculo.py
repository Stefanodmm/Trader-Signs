import json
import os
import requests

# Ruta del archivo de configuración
config_file = 'config.json'

# Verificar si el archivo de configuración existe
if not os.path.exists(config_file):
    # Crear un archivo de configuración con valores predeterminados
    default_config = {
        "RSI": {"periodo": 14, "temporalidad": "1d", "tiempo_espera": 5},
        "MACD": {"rapido": 12, "lento": 26, "signal": 9, "temporalidad": "1d", "tiempo_espera": 5},
        "B.Bolinger": {"periodo": 20, "desviacion": 2, "temporalidad": "1d", "tiempo_espera": 5},
        "VRVP": {"periodo": 14, "temporalidad": "1d", "tiempo_espera": 5}
    }
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=4)
    print(f"Archivo de configuración '{config_file}' creado con valores predeterminados.")

def calcular_vrvp():
    # Cargar la configuración
    with open(config_file) as f:
        config = json.load(f)

    periodo = config["VRVP"]["periodo"]
    temporalidad = config["VRVP"]["temporalidad"]

    # Obtener datos históricos de Binance
    url = f'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={temporalidad}&limit={periodo}'
    response = requests.get(url)
    ohlcv = response.json()
    closes = [float(x[4]) for x in ohlcv]  # Precios de cierre

    # Calcular VRVP
    # Implementa aquí la lógica para calcular el VRVP
    # Lógica de compra/venta basada en el VRVP
    pass
