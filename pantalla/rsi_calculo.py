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

def calcular_rsi():
    # Cargar la configuración
    with open(config_file) as f:
        config = json.load(f)

    periodo = config["RSI"]["periodo"]
    temporalidad = config["RSI"]["temporalidad"]

    # Obtener datos históricos de Binance
    url = f'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={temporalidad}&limit={periodo}'
    response = requests.get(url)
    ohlcv = response.json()
    closes = [float(x[4]) for x in ohlcv]  # Precios de cierre

    # Calcular RSI
    rsi = calcular_rsi_func(closes)  # Implementa tu lógica de cálculo de RSI

    # Lógica de compra/venta
    if rsi < 30:
        print("Comprar: RSI bajo")
    elif rsi > 70:
        print("Vender: RSI alto")

def calcular_rsi_func(closes):
    # Calcular el cambio de precios
    cambios = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    
    # Calcular ganancias y pérdidas
    ganancias = [x if x > 0 else 0 for x in cambios]
    perdidas = [-x if x < 0 else 0 for x in cambios]

    # Calcular el promedio de ganancias y pérdidas
    promedio_ganancias = sum(ganancias) / len(ganancias)
    promedio_perdidas = sum(perdidas) / len(perdidas)

    # Calcular el índice de fuerza relativa (RS)
    if promedio_perdidas == 0:
        return 100  # RSI máximo si no hay pérdidas
    rs = promedio_ganancias / promedio_perdidas

    # Calcular el RSI
    rsi = 100 - (100 / (1 + rs))
    return rsi