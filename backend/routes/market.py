from flask import Blueprint, request
from services.binance_service import get_market_data

market_bp = Blueprint("market", __name__)

@market_bp.route("/api/market-data", methods=["GET"])
def market_data():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 100, type=int)

    data = get_market_data(symbol, interval, limit)

    return {
        "status": "success",
        "symbol": symbol,
        "interval": interval,
        "records": len(data),
        "data": data
    }