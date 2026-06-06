import os
import requests
import pandas as pd

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"
DATA_DIR = "data"


def get_cache_file_path(symbol, interval, limit):
    filename = f"{symbol}_{interval}_{limit}.csv"
    return os.path.join(DATA_DIR, filename)


def get_market_data(
    symbol="BTCUSDT",
    interval="1d",
    limit=100,
    use_cache=True
):

    os.makedirs(DATA_DIR, exist_ok=True)

    cache_file = get_cache_file_path(symbol, interval, limit)

    if use_cache and os.path.exists(cache_file):
        df = pd.read_csv(cache_file)
        return df.to_dict(orient="records")

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    response = requests.get(BINANCE_KLINES_URL, params=params)
    response.raise_for_status()

    raw_data = response.json()

    formatted_data = []

    for item in raw_data:
        formatted_data.append({
            "open_time": item[0],
            "open": float(item[1]),
            "high": float(item[2]),
            "low": float(item[3]),
            "close": float(item[4]),
            "volume": float(item[5]),
            "close_time": item[6]
        })

    df = pd.DataFrame(formatted_data)
    df.to_csv(cache_file, index=False)

    return formatted_data


def get_dataframe(symbol="BTCUSDT", interval="1d", limit=100, use_cache=True):
    data = get_market_data(symbol, interval, limit, use_cache)

    df = pd.DataFrame(data)

    return df