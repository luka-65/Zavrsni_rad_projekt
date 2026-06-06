from flask import Blueprint, request

from services.binance_service import get_dataframe
from strategies.moving_average import moving_average_strategy
from backtesting.backtester import run_backtest
from strategies.rsi import rsi_strategy
from strategies.bollinger import bollinger_bands_strategy
from database.db import save_simulation

backtest_bp = Blueprint("backtest", __name__)

@backtest_bp.route("/api/backtest/moving-average", methods=["GET"])
def moving_average_backtest():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)

    short_window = request.args.get("short_window", 20, type=int)
    long_window = request.args.get("long_window", 50, type=int)
    initial_balance = request.args.get("initial_balance", 10000, type=float)

    df = get_dataframe(symbol, interval, limit)

    df = moving_average_strategy(
        df,
        short_window=short_window,
        long_window=long_window
    )

    result = run_backtest(
        df,
        initial_balance=initial_balance
    )
    save_simulation(
    "Moving Average Crossover",
    symbol,
    interval,
    result
)

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

    period = request.args.get("period", 14, type=int)
    oversold = request.args.get("oversold", 30, type=float)
    overbought = request.args.get("overbought", 70, type=float)
    initial_balance = request.args.get("initial_balance", 10000, type=float)

    df = get_dataframe(symbol, interval, limit)

    df = rsi_strategy(
        df,
        period=period,
        oversold=oversold,
        overbought=overbought
    )

    result = run_backtest(
        df,
        initial_balance=initial_balance
    )
    save_simulation(
    "Relative Strength Index",
    symbol,
    interval,
    result
)

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

    window = request.args.get("window", 20, type=int)
    num_std = request.args.get("num_std", 2, type=float)
    initial_balance = request.args.get("initial_balance", 10000, type=float)

    df = get_dataframe(symbol, interval, limit)

    df = bollinger_bands_strategy(
        df,
        window=window,
        num_std=num_std
    )

    result = run_backtest(
        df,
        initial_balance=initial_balance
    )
    save_simulation(
    "Bollinger Bands",
    symbol,
    interval,
    result
)

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
def compare_strategies():
    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)
    initial_balance = request.args.get("initial_balance", 10000, type=float)

    df = get_dataframe(symbol, interval, limit)

    ma_df = moving_average_strategy(df)
    rsi_df = rsi_strategy(df)
    bollinger_df = bollinger_bands_strategy(df)

    ma_result = run_backtest(ma_df, initial_balance)
    rsi_result = run_backtest(rsi_df, initial_balance)
    bollinger_result = run_backtest(bollinger_df, initial_balance)

    return {
        "status": "success",
        "symbol": symbol,
        "interval": interval,
        "initial_balance": initial_balance,
        "results": [
            {
                "strategy": "Moving Average Crossover",
                "return_pct": ma_result["return_pct"],
                "final_balance": ma_result["final_balance"],
                "max_drawdown_pct": ma_result["max_drawdown_pct"],
                "win_rate_pct": ma_result["win_rate_pct"],
                "number_of_trades": ma_result["number_of_trades"]
            },
            {
                "strategy": "Relative Strength Index",
                "return_pct": rsi_result["return_pct"],
                "final_balance": rsi_result["final_balance"],
                "max_drawdown_pct": rsi_result["max_drawdown_pct"],
                "win_rate_pct": rsi_result["win_rate_pct"],
                "number_of_trades": rsi_result["number_of_trades"]
            },
            {
                "strategy": "Bollinger Bands",
                "return_pct": bollinger_result["return_pct"],
                "final_balance": bollinger_result["final_balance"],
                "max_drawdown_pct": bollinger_result["max_drawdown_pct"],
                "win_rate_pct": bollinger_result["win_rate_pct"],
                "number_of_trades": bollinger_result["number_of_trades"]
            }
        ]
    }