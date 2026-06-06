from flask import Blueprint, request
from database.db import save_simulation
from services.backtest_service import (
    run_moving_average,
    run_rsi,
    run_bollinger,
    compare_strategies
)

backtest_bp = Blueprint("backtest", __name__)


@backtest_bp.route("/api/backtest/moving-average", methods=["GET"])
def moving_average_backtest():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)
    initial_balance = request.args.get("initial_balance", 10000, type=float)
    short_window = request.args.get("short_window", 20, type=int)
    long_window = request.args.get("long_window", 50, type=int)

    result = run_moving_average(
        symbol, interval, limit, initial_balance, short_window, long_window
    )

    save_simulation("Moving Average Crossover", symbol, interval, result)

    return {
        "status": "success",
        "strategy": "Moving Average Crossover",
        "symbol": symbol,
        "interval": interval,
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

    result = run_rsi(
        symbol, interval, limit, initial_balance, period, oversold, overbought
    )

    save_simulation("Relative Strength Index", symbol, interval, result)

    return {
        "status": "success",
        "strategy": "Relative Strength Index",
        "symbol": symbol,
        "interval": interval,
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

    result = run_bollinger(
        symbol, interval, limit, initial_balance, window, num_std
    )

    save_simulation("Bollinger Bands", symbol, interval, result)

    return {
        "status": "success",
        "strategy": "Bollinger Bands",
        "symbol": symbol,
        "interval": interval,
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

    results = compare_strategies(symbol, interval, limit, initial_balance)

    return {
        "status": "success",
        "symbol": symbol,
        "interval": interval,
        "initial_balance": initial_balance,
        "results": results
    }