import os
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"
DATA_DIR = "data"


def get_cache_file_path(symbol, interval, limit, start_date=None, end_date=None):
    if start_date and end_date:
        filename = f"{symbol}_{interval}_{start_date}_{end_date}.csv"
    else:
        filename = f"{symbol}_{interval}_{limit}.csv"

    return os.path.join(DATA_DIR, filename)


def date_to_milliseconds(date_value, end_of_day=False):
    date_time = datetime.strptime(date_value, "%Y-%m-%d").replace(
        tzinfo=timezone.utc
    )

    if end_of_day:
        date_time = date_time + timedelta(days=1) - timedelta(milliseconds=1)

    return int(date_time.timestamp() * 1000)


def format_kline(item):
    return {
        "open_time": item[0],
        "open": float(item[1]),
        "high": float(item[2]),
        "low": float(item[3]),
        "close": float(item[4]),
        "volume": float(item[5]),
        "close_time": item[6]
    }


def get_market_data(
    symbol="BTCUSDT",
    interval="1d",
    limit=100,
    use_cache=True,
    start_date=None,
    end_date=None
):

    os.makedirs(DATA_DIR, exist_ok=True)

    cache_file = get_cache_file_path(symbol, interval, limit, start_date, end_date)

    if use_cache and os.path.exists(cache_file):
        df = pd.read_csv(cache_file)
        return df.to_dict(orient="records")

    if start_date and end_date:
        start_time = date_to_milliseconds(start_date)
        end_time = date_to_milliseconds(end_date, end_of_day=True)
        formatted_data = []
        current_start_time = start_time

        while current_start_time <= end_time:
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": 1000,
                "startTime": current_start_time,
                "endTime": end_time
            }

            response = requests.get(BINANCE_KLINES_URL, params=params)
            response.raise_for_status()

            raw_data = response.json()

            if not raw_data:
                break

            formatted_data.extend(format_kline(item) for item in raw_data)

            last_close_time = raw_data[-1][6]
            current_start_time = last_close_time + 1

            if len(raw_data) < 1000:
                break

        df = pd.DataFrame(formatted_data)
        df.to_csv(cache_file, index=False)

        return formatted_data

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
        formatted_data.append(format_kline(item))

    df = pd.DataFrame(formatted_data)
    df.to_csv(cache_file, index=False)

    return formatted_data


def get_dataframe(
    symbol="BTCUSDT",
    interval="1d",
    limit=100,
    use_cache=True,
    start_date=None,
    end_date=None
):
    data = get_market_data(
        symbol,
        interval,
        limit,
        use_cache,
        start_date,
        end_date
    )

    df = pd.DataFrame(data)

    return df
