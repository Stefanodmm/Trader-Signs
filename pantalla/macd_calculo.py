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

def calcular_macd():
    # Cargar la configuración
    with open(config_file) as f:
        config = json.load(f)

    rapido = config["MACD"]["rapido"]
    lento = config["MACD"]["lento"]
    signal = config["MACD"]["signal"]
    temporalidad = config["MACD"]["temporalidad"]

    # Obtener datos históricos de Binance
    url = f'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={temporalidad}&limit={lento}'
    response = requests.get(url)
    ohlcv = response.json()
    closes = [float(x[4]) for x in ohlcv]  # Precios de cierre

    # Calcular MACD
    macd, signal_line = calcular_macd_func(closes, rapido, lento, signal)  # Implementa tu lógica de cálculo de MACD

    # Lógica de compra/venta
    if macd > signal_line:
        print("Comprar: MACD cruzó hacia arriba")
    elif macd < signal_line:
        print("Vender: MACD cruzó hacia abajo")

def calcular_macd_func(closes, rapido, lento, signal):
    # Calcular la media móvil exponencial (EMA) rápida y lenta
    def ema(prices, period):
        k = 2 / (period + 1)
        ema_values = [sum(prices[:period]) / period]  # Inicializar con la media simple
        for price in prices[period:]:
            ema_values.append((price - ema_values[-1]) * k + ema_values[-1])
        return ema_values

    ema_rapido = ema(closes, rapido)
    ema_lento = ema(closes, lento)

    # Calcular el MACD
    macd = [ema_rapido[i] - ema_lento[i] for i in range(len(ema_lento))]
    
    # Calcular la línea de señal
    signal_line = ema(macd, signal)

    return macd[-1], signal_line[-1]  # Devolver el último valor de MACD y la línea de señal
