# Este archivo ha sido limpiado para que no retorne nada

import requests
import pandas as pd

def calcular_macd(symbol, timeframe='1m', limit=100, short_window=12, long_window=26, signal_window=9):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={timeframe}&limit={limit}'
    response = requests.get(url)
    data = response.json()
    
    # Convertir a DataFrame
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = df['close'].astype(float)  # Convertir a float

    # Calcular la EMA rápida y lenta
    df['EMA_short'] = df['close'].ewm(span=short_window, adjust=False).mean()
    df['EMA_long'] = df['close'].ewm(span=long_window, adjust=False).mean()
    
    # Calcular el MACD
    df['MACD'] = df['EMA_short'] - df['EMA_long']
    df['Signal'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()
    
    # Retornar el último valor de MACD y Signal
    return df['MACD'].iloc[-1], df['Signal'].iloc[-1]

# Puedes agregar aquí cualquier importación necesaria si es requerido por el resto del programa
