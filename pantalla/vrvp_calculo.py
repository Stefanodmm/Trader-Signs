# Archivo vrvp_calculo.py

import json
import os
import requests
import numpy as np

# Ruta del archivo de configuración
config_file = 'config.json'  # Asegúrate de que este archivo esté en la misma carpeta que este script

def crear_configuracion():
    # Crear un archivo de configuración con valores predeterminados
    default_config = {
        "RSI": {"periodo": 14, "temporalidad": "1d", "tiempo_espera": 5},
        "MACD": {"rapido": 12, "lento": 26, "signal": 9, "temporalidad": "1d", "tiempo_espera": 5},
        "B.Bolinger": {"periodo": 20, "desviacion": 2, "temporalidad": "1d", "tiempo_espera": 5},
        "VRVP": {  # Cambiar la estructura para que coincida con el uso de bb_calculo
            "num_niveles": 24,
            "va_porcentaje": 70,
            "temporalidad": "1h",  # Añadir temporalidad
            "lookback_period": 100  # Número de velas hacia atrás a analizar
        }
    }
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=4)
    print(f"Archivo de configuración '{config_file}' creado con valores predeterminados.")

# Verificar si el archivo de configuración existe, si no, crearlo
if not os.path.exists(config_file):
    crear_configuracion()

def calcular_vrvp():
    # Cargar la configuración
    with open(config_file) as f:
        config = json.load(f)

    # Verificar que la configuración de VRVP tenga las claves necesarias
    if "VRVP" not in config:
        raise KeyError("La configuración de VRVP no contiene las claves necesarias.")

    # Obtener valores de configuración
    num_niveles = config["VRVP"]["num_niveles"]
    va_porcentaje = config["VRVP"]["va_porcentaje"]
    lookback_period = config["VRVP"]["lookback_period"]
    temporalidad = config["VRVP"]["temporalidad"]

    # Usar un símbolo por defecto si no se encuentra en la configuración
    symbol = config.get("trading", {}).get("symbol", "BTCUSDT")

    # Obtener datos históricos de Binance
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={temporalidad}&limit={lookback_period}'
    response = requests.get(url)
    ohlcv = response.json()

    # Verificar si la respuesta es válida
    if not ohlcv or 'code' in ohlcv:
        raise ValueError("Error al obtener datos de Binance: " + str(ohlcv))

    # Convertir datos a un array de numpy
    precios = np.array([[float(data[0]), float(data[1]), float(data[2]), float(data[3]), float(data[4]), float(data[5])] for data in ohlcv])
    high_prices = precios[:, 2]
    low_prices = precios[:, 3]
    volumes = precios[:, 5]

    # Calcular el rango de precios
    precio_max = high_prices.max()
    precio_min = low_prices.min()

    # Crear niveles de precio
    niveles = np.linspace(precio_min, precio_max, num_niveles)
    volumen_por_nivel = np.zeros(num_niveles - 1)

    # Calcular volumen por nivel
    for i in range(len(precios)):
        for j in range(len(niveles) - 1):
            if (low_prices[i] <= niveles[j + 1] and high_prices[i] >= niveles[j]):
                volumen_por_nivel[j] += volumes[i]

    # Encontrar el Point of Control (POC)
    poc_index = np.argmax(volumen_por_nivel)
    poc_precio = (niveles[poc_index] + niveles[poc_index + 1]) / 2

    # Calcular Value Area (70% del volumen total)
    total_volumen = np.sum(volumen_por_nivel)
    volumen_objetivo = total_volumen * (va_porcentaje / 100)

    # Expandir desde el POC hasta alcanzar el volumen objetivo
    volumen_acumulado = volumen_por_nivel[poc_index]
    superior_idx = poc_index
    inferior_idx = poc_index

    while volumen_acumulado < volumen_objetivo and (superior_idx < len(volumen_por_nivel) - 1 or inferior_idx > 0):
        vol_superior = volumen_por_nivel[superior_idx + 1] if superior_idx < len(volumen_por_nivel) - 1 else 0
        vol_inferior = volumen_por_nivel[inferior_idx - 1] if inferior_idx > 0 else 0

        if vol_superior > vol_inferior and superior_idx < len(volumen_por_nivel) - 1:
            superior_idx += 1
            volumen_acumulado += vol_superior
        elif inferior_idx > 0:
            inferior_idx -= 1
            volumen_acumulado += vol_inferior

    va_superior = niveles[superior_idx + 1] if superior_idx < len(niveles) - 1 else niveles[-1]
    va_inferior = niveles[inferior_idx] if inferior_idx > 0 else niveles[0]

    return {
        'niveles': niveles,
        'volumen_por_nivel': volumen_por_nivel,
        'poc_precio': poc_precio,
        'va_superior': va_superior,
        'va_inferior': va_inferior,
        'volumen_total': total_volumen,
        'volumen_va': volumen_acumulado
    }  # Retornar los valores calculados

# Ejemplo de uso
if __name__ == "__main__":
    try:
        resultado = calcular_vrvp()
        print("Resultados del cálculo de VRVP:", resultado)
    except Exception as e:
        print("Error:", str(e))
