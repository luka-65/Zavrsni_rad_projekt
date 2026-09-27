import time

from services.binance_service import binance_get

BINANCE_EXCHANGE_INFO_URL = "https://api.binance.com/api/v3/exchangeInfo"

SYMBOLS_CACHE_TTL_SECONDS = 3600
_symbols_cache = {"fetched_at": None, "symbols": []}


def get_usdt_symbols():
    fetched_at = _symbols_cache["fetched_at"]

    if fetched_at is None or time.time() - fetched_at > SYMBOLS_CACHE_TTL_SECONDS:
        data = binance_get(BINANCE_EXCHANGE_INFO_URL)
        _symbols_cache["symbols"] = [
            {
                "symbol": item["symbol"],
                "base_asset": item["baseAsset"],
                "quote_asset": item["quoteAsset"]
            }
            for item in data["symbols"]
            if item["quoteAsset"] == "USDT" and item["status"] == "TRADING"
        ]
        _symbols_cache["fetched_at"] = time.time()

    return _symbols_cache["symbols"]


def search_symbols(query=""):
    query = query.upper()

    return [
        item for item in get_usdt_symbols()
        if query in item["symbol"] or query in item["base_asset"]
    ][:20]
