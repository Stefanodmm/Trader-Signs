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

def calcular_bollinger():
    # Cargar la configuración
    with open(config_file) as f:
        config = json.load(f)

    periodo = config["B.Bolinger"]["periodo"]
    desviacion = config["B.Bolinger"]["desviacion"]
    temporalidad = config["B.Bolinger"]["temporalidad"]

    # Obtener datos históricos de Binance
    url = f'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={temporalidad}&limit={periodo}'
    response = requests.get(url)
    ohlcv = response.json()
    closes = [float(x[4]) for x in ohlcv]  # Precios de cierre

    # Calcular Bandas de Bollinger
    media_movil, upper_band, lower_band = calcular_bollinger_func(closes, periodo, desviacion)  # Implementa tu lógica de cálculo

    # Lógica de compra/venta
    if closes[-1] < lower_band:
        print("Comprar: Precio por debajo de la banda inferior")
    elif closes[-1] > upper_band:
        print("Vender: Precio por encima de la banda superior")

def calcular_bollinger_func(closes, periodo, desviacion):
    # Calcular la media móvil simple
    media_movil = sum(closes[-periodo:]) / periodo

    # Calcular la desviación estándar
    desviaciones = [(x - media_movil) ** 2 for x in closes[-periodo:]]
    desviacion_estandar = (sum(desviaciones) / periodo) ** 0.5

    # Calcular las bandas de Bollinger
    upper_band = media_movil + (desviacion * desviacion_estandar)
    lower_band = media_movil - (desviacion * desviacion_estandar)

    return media_movil, upper_band, lower_band  # Devolver los valores calculados
