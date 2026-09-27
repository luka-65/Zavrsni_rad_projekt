from utils.validation import validate_strategy, require_market_rows, finite_number
from services.binance_service import get_dataframe
from strategies.moving_average import moving_average_strategy
from strategies.rsi import rsi_strategy
from strategies.bollinger import bollinger_bands_strategy
from backtesting.backtester import run_backtest
from services.chart_data import build_chart_data


def run_moving_average(
    symbol,
    interval,
    limit,
    initial_balance,
    short_window,
    long_window,
    start_date=None,
    end_date=None
):
    params = validate_strategy("moving-average", {
        "short_window": short_window, "long_window": long_window,
    })
    short_window, long_window = params["short_window"], params["long_window"]
    initial_balance = finite_number(initial_balance, "initial_balance", positive=True)
    df = get_dataframe(symbol, interval, limit, True, start_date, end_date)
    require_market_rows(df, long_window)
    df = moving_average_strategy(df, short_window, long_window)
    result = run_backtest(df, initial_balance)
    result["chart_data"] = build_chart_data(df)
    return result


def run_rsi(
    symbol,
    interval,
    limit,
    initial_balance,
    period,
    oversold,
    overbought,
    start_date=None,
    end_date=None
):
    params = validate_strategy("rsi", {
        "period": period, "oversold": oversold, "overbought": overbought,
    })
    period, oversold, overbought = params["period"], params["oversold"], params["overbought"]
    initial_balance = finite_number(initial_balance, "initial_balance", positive=True)
    df = get_dataframe(symbol, interval, limit, True, start_date, end_date)
    require_market_rows(df, period + 1)
    df = rsi_strategy(df, period, oversold, overbought)
    result = run_backtest(df, initial_balance)
    result["chart_data"] = build_chart_data(df)
    result["chart_data"]["oversold"] = [oversold] * len(df)
    result["chart_data"]["overbought"] = [overbought] * len(df)
    return result


def run_bollinger(
    symbol,
    interval,
    limit,
    initial_balance,
    window,
    num_std,
    start_date=None,
    end_date=None
):
    params = validate_strategy("bollinger", {
        "window": window, "num_std": num_std,
    })
    window, num_std = params["window"], params["num_std"]
    initial_balance = finite_number(initial_balance, "initial_balance", positive=True)
    df = get_dataframe(symbol, interval, limit, True, start_date, end_date)
    require_market_rows(df, window)
    df = bollinger_bands_strategy(df, window, num_std)
    result = run_backtest(df, initial_balance)
    result["chart_data"] = build_chart_data(df)
    return result


COMPARISON_CONFIGURATIONS = (
    ("Moving Average Crossover", run_moving_average, {"short_window": 20, "long_window": 50}),
    ("Relative Strength Index", run_rsi, {"period": 14, "oversold": 30, "overbought": 70}),
    ("Bollinger Bands", run_bollinger, {"window": 20, "num_std": 2}),
)


def format_compare_result(strategy, parameters, result):
    return {
        "strategy": strategy,
        "parameters": parameters,
        "return_pct": result["return_pct"],
        "final_balance": result["final_balance"],
        "max_drawdown_pct": result["max_drawdown_pct"],
        "win_rate_pct": result["win_rate_pct"],
        "number_of_trades": result["number_of_trades"]
    }


def compare_strategies(symbol, interval, limit, initial_balance, start_date=None, end_date=None):
    return [
        format_compare_result(strategy, parameters, runner(
            symbol=symbol, interval=interval, limit=limit, initial_balance=initial_balance,
            start_date=start_date, end_date=end_date, **parameters
        ))
        for strategy, runner, parameters in COMPARISON_CONFIGURATIONS
    ]
