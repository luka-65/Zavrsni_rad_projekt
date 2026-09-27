from flask import Blueprint, request
from services.binance_service import get_market_data

from utils.errors import register_error_handlers
from utils.validation import parse_request_inputs

market_bp = Blueprint("market", __name__)

register_error_handlers(market_bp)

@market_bp.route("/api/market-data", methods=["GET"])
def market_data():
    common, _ = parse_request_inputs(request.args, include_balance=False, default_limit=100)
    symbol, interval = common["symbol"], common["interval"]
    data = get_market_data(**common)

    return {
        "status": "success",
        "symbol": symbol,
        "interval": interval,
        "records": len(data),
        "data": data
    }