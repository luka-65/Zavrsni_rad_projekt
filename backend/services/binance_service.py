import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from utils.errors import ExternalServiceError
from utils.validation import ValidationError, validate_market_inputs

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"
DATA_DIR = "data"
MAX_KLINES_PER_REQUEST = 1000

REQUEST_TIMEOUT = 10

CACHE_TTL_SECONDS = 300


def binance_get(url, params=None):
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    except requests.Timeout:
        raise ExternalServiceError(
            "Binance nije odgovorio na vrijeme. Pokušajte ponovno za nekoliko trenutaka.", 504
        ) from None
    except requests.RequestException:
        raise ExternalServiceError(
            "Binanceu se trenutačno ne može pristupiti. Provjerite internetsku vezu i pokušajte ponovno."
        ) from None

    check_market_response(response)

    try:
        return response.json()
    except ValueError:
        raise ExternalServiceError("Binance je vratio neispravan odgovor.") from None


def check_market_response(response):
    if response.status_code == 400:
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        if isinstance(payload, dict) and payload.get("code") == -1121:
            raise ValidationError("Odabrani trgovački simbol ne postoji na Binanceu.")
    if response.status_code in (418, 429):
        raise ExternalServiceError("Binance je privremeno ograničio broj zahtjeva. Pokušajte ponovno za minutu.")
    if response.status_code >= 400:
        raise ExternalServiceError(f"Binance je vratio pogrešku (HTTP {response.status_code}).")


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


def now_milliseconds():
    return int(time.time() * 1000)


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


def keep_complete_candles(rows, start_time=None, end_time=None, now=None):
    now = now_milliseconds() if now is None else now
    return [
        row for row in rows
        if row["close_time"] < now
        and (start_time is None or row["open_time"] >= start_time)
        and (end_time is None or row["close_time"] <= end_time)
    ]


def read_cache(cache_file, end_time=None):
    if not os.path.exists(cache_file):
        return None

    saved_at = int(os.path.getmtime(cache_file) * 1000)
    period_was_over = end_time is not None and saved_at > end_time

    if not period_was_over and now_milliseconds() - saved_at > CACHE_TTL_SECONDS * 1000:
        return None

    try:
        return pd.read_csv(cache_file).to_dict(orient="records")
    except pd.errors.EmptyDataError:
        return None


def write_cache(cache_file, rows):
    if rows:
        pd.DataFrame(rows).to_csv(cache_file, index=False)


def fetch_period(symbol, interval, start_time, end_time):
    formatted_data = []
    current_start_time = start_time

    while current_start_time <= end_time:
        raw_data = binance_get(BINANCE_KLINES_URL, {
            "symbol": symbol,
            "interval": interval,
            "limit": MAX_KLINES_PER_REQUEST,
            "startTime": current_start_time,
            "endTime": end_time
        })

        if not raw_data:
            break

        formatted_data.extend(format_kline(item) for item in raw_data)
        current_start_time = raw_data[-1][6] + 1

        if len(raw_data) < MAX_KLINES_PER_REQUEST:
            break

    return formatted_data


def fetch_latest(symbol, interval, limit):
    raw_data = binance_get(BINANCE_KLINES_URL, {
        "symbol": symbol,
        "interval": interval,
        "limit": min(limit + 1, MAX_KLINES_PER_REQUEST)
    })
    return [format_kline(item) for item in raw_data]


def get_market_data(
    symbol="BTCUSDT",
    interval="1d",
    limit=100,
    use_cache=True,
    start_date=None,
    end_date=None
):

    common = validate_market_inputs(symbol, interval, limit, start_date, end_date)
    limit = common["limit"]
    os.makedirs(DATA_DIR, exist_ok=True)

    cache_file = get_cache_file_path(symbol, interval, limit, start_date, end_date)

    if start_date and end_date:
        start_time = date_to_milliseconds(start_date)
        end_time = date_to_milliseconds(end_date, end_of_day=True)
    else:
        start_time = end_time = None

    rows = read_cache(cache_file, end_time) if use_cache else None

    if rows is None:
        if start_time is not None:
            rows = fetch_period(symbol, interval, start_time, end_time)
        else:
            rows = fetch_latest(symbol, interval, limit)

        rows = keep_complete_candles(rows, start_time, end_time)
        write_cache(cache_file, rows)

    rows = keep_complete_candles(rows, start_time, end_time)

    return rows if start_time is not None else rows[-limit:]


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
