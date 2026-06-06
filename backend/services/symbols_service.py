import requests

BINANCE_EXCHANGE_INFO_URL = "https://api.binance.com/api/v3/exchangeInfo"

def search_symbols(query=""):
    response = requests.get(BINANCE_EXCHANGE_INFO_URL)
    response.raise_for_status()

    data = response.json()

    query = query.upper()

    results = []

    for item in data["symbols"]:
        symbol = item["symbol"]
        base_asset = item["baseAsset"]
        quote_asset = item["quoteAsset"]
        status = item["status"]

        if quote_asset != "USDT":
            continue

        if status != "TRADING":
            continue

        if query in symbol or query in base_asset:
            results.append({
                "symbol": symbol,
                "base_asset": base_asset,
                "quote_asset": quote_asset
            })

        if len(results) >= 20:
            break

    return results