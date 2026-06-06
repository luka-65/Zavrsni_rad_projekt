from flask import Blueprint, request
from services.chart_service import (
    get_moving_average_chart,
    get_rsi_chart,
    get_bollinger_chart
)

chart_bp = Blueprint("chart", __name__)


@chart_bp.route("/api/chart/moving-average", methods=["GET"])
def moving_average_chart():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)
    short_window = request.args.get("short_window", 20, type=int)
    long_window = request.args.get("long_window", 50, type=int)

    return get_moving_average_chart(
        symbol, interval, limit, short_window, long_window
    )


@chart_bp.route("/api/chart/rsi", methods=["GET"])
def rsi_chart():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)
    period = request.args.get("period", 14, type=int)
    oversold = request.args.get("oversold", 30, type=float)
    overbought = request.args.get("overbought", 70, type=float)

    return get_rsi_chart(
        symbol, interval, limit, period, oversold, overbought
    )


@chart_bp.route("/api/chart/bollinger", methods=["GET"])
def bollinger_chart():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)
    window = request.args.get("window", 20, type=int)
    num_std = request.args.get("num_std", 2, type=float)

    return get_bollinger_chart(symbol, interval, limit, window, num_std)