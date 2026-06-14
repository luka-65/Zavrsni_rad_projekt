from flask import Blueprint, request
from database.db import save_simulation
from datetime import datetime
from services.backtest_service import (
    run_moving_average,
    run_rsi,
    run_bollinger,
    compare_strategies
)

backtest_bp = Blueprint("backtest", __name__)

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


@backtest_bp.route("/api/backtest/moving-average", methods=["GET"])
def moving_average_backtest():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)
    initial_balance = request.args.get("initial_balance", 10000, type=float)
    short_window = request.args.get("short_window", 20, type=int)
    long_window = request.args.get("long_window", 50, type=int)
    start_date, end_date, date_error = get_validated_dates(interval)

    if date_error:
        message, status_code = date_error
        return {"status": "error", "message": message}, status_code

    result = run_moving_average(
        symbol, interval, limit, initial_balance, short_window, long_window, start_date, end_date
    )

    save_simulation("Moving Average Crossover", symbol, interval, result, start_date, end_date)

    return {
        "status": "success",
        "strategy": "Moving Average Crossover",
        "symbol": symbol,
        "interval": interval,
        "start_date": start_date,
        "end_date": end_date,
        "short_window": short_window,
        "long_window": long_window,
        "result": result
    }


@backtest_bp.route("/api/backtest/rsi", methods=["GET"])
def rsi_backtest():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)
    initial_balance = request.args.get("initial_balance", 10000, type=float)
    period = request.args.get("period", 14, type=int)
    oversold = request.args.get("oversold", 30, type=float)
    overbought = request.args.get("overbought", 70, type=float)
    start_date, end_date, date_error = get_validated_dates(interval)

    if date_error:
        message, status_code = date_error
        return {"status": "error", "message": message}, status_code

    result = run_rsi(
        symbol, interval, limit, initial_balance, period, oversold, overbought, start_date, end_date
    )

    save_simulation("Relative Strength Index", symbol, interval, result, start_date, end_date)

    return {
        "status": "success",
        "strategy": "Relative Strength Index",
        "symbol": symbol,
        "interval": interval,
        "start_date": start_date,
        "end_date": end_date,
        "period": period,
        "oversold": oversold,
        "overbought": overbought,
        "result": result
    }


@backtest_bp.route("/api/backtest/bollinger", methods=["GET"])
def bollinger_backtest():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)
    initial_balance = request.args.get("initial_balance", 10000, type=float)
    window = request.args.get("window", 20, type=int)
    num_std = request.args.get("num_std", 2, type=float)
    start_date, end_date, date_error = get_validated_dates(interval)

    if date_error:
        message, status_code = date_error
        return {"status": "error", "message": message}, status_code

    result = run_bollinger(
        symbol, interval, limit, initial_balance, window, num_std, start_date, end_date
    )

    save_simulation("Bollinger Bands", symbol, interval, result, start_date, end_date)

    return {
        "status": "success",
        "strategy": "Bollinger Bands",
        "symbol": symbol,
        "interval": interval,
        "start_date": start_date,
        "end_date": end_date,
        "window": window,
        "num_std": num_std,
        "result": result
    }


@backtest_bp.route("/api/backtest/compare", methods=["GET"])
def compare():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)
    initial_balance = request.args.get("initial_balance", 10000, type=float)
    start_date, end_date, date_error = get_validated_dates(interval)

    if date_error:
        message, status_code = date_error
        return {"status": "error", "message": message}, status_code

    results = compare_strategies(symbol, interval, limit, initial_balance, start_date, end_date)

    return {
        "status": "success",
        "symbol": symbol,
        "interval": interval,
        "start_date": start_date,
        "end_date": end_date,
        "initial_balance": initial_balance,
        "results": results
    }
