from flask import Blueprint, request
from datetime import datetime
from services.chart_service import (
    get_moving_average_chart,
    get_rsi_chart,
    get_bollinger_chart
)

chart_bp = Blueprint("chart", __name__)

MAX_RANGE_DAYS = {
    "1h": 90,
    "4h": 365,
    "1d": 1825,
    "1w": 3650,
    "1M": 3650
}


def get_validated_dates(interval):
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not start_date and not end_date:
        return None, None, None

    if not start_date or not end_date:
        return None, None, ("Potrebno je odabrati datum od i datum do.", 400)

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return None, None, ("Datum mora biti u formatu YYYY-MM-DD.", 400)

    if end < start:
        return None, None, ("Datum do ne može biti prije datuma od.", 400)

    today = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)

    if end > today:
        return None, None, ("Datum do ne moze biti u buducnosti.", 400)

    max_days = MAX_RANGE_DAYS.get(interval)

    if max_days is not None and (end - start).days > max_days:
        return None, None, (
            f"Za interval {interval} moguće je odabrati najviše {max_days} dana.",
            400
        )

    return start_date, end_date, None


@chart_bp.route("/api/chart/moving-average", methods=["GET"])
def moving_average_chart():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)
    short_window = request.args.get("short_window", 20, type=int)
    long_window = request.args.get("long_window", 50, type=int)
    start_date, end_date, date_error = get_validated_dates(interval)

    if date_error:
        message, status_code = date_error
        return {"status": "error", "message": message}, status_code

    return get_moving_average_chart(
        symbol, interval, limit, short_window, long_window, start_date, end_date
    )


@chart_bp.route("/api/chart/rsi", methods=["GET"])
def rsi_chart():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)
    period = request.args.get("period", 14, type=int)
    oversold = request.args.get("oversold", 30, type=float)
    overbought = request.args.get("overbought", 70, type=float)
    start_date, end_date, date_error = get_validated_dates(interval)

    if date_error:
        message, status_code = date_error
        return {"status": "error", "message": message}, status_code

    return get_rsi_chart(
        symbol, interval, limit, period, oversold, overbought, start_date, end_date
    )


@chart_bp.route("/api/chart/bollinger", methods=["GET"])
def bollinger_chart():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)
    window = request.args.get("window", 20, type=int)
    num_std = request.args.get("num_std", 2, type=float)
    start_date, end_date, date_error = get_validated_dates(interval)

    if date_error:
        message, status_code = date_error
        return {"status": "error", "message": message}, status_code

    return get_bollinger_chart(symbol, interval, limit, window, num_std, start_date, end_date)
