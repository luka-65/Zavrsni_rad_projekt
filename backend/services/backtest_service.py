from services.binance_service import get_dataframe
from strategies.moving_average import moving_average_strategy
from strategies.rsi import rsi_strategy
from strategies.bollinger import bollinger_bands_strategy
from backtesting.backtester import run_backtest


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
    df = get_dataframe(symbol, interval, limit, True, start_date, end_date)
    df = moving_average_strategy(df, short_window, long_window)
    return run_backtest(df, initial_balance)


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
    df = get_dataframe(symbol, interval, limit, True, start_date, end_date)
    df = rsi_strategy(df, period, oversold, overbought)
    return run_backtest(df, initial_balance)


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
    df = get_dataframe(symbol, interval, limit, True, start_date, end_date)
    df = bollinger_bands_strategy(df, window, num_std)
    return run_backtest(df, initial_balance)


def format_compare_result(strategy, result):
    return {
        "strategy": strategy,
        "return_pct": result["return_pct"],
        "final_balance": result["final_balance"],
        "max_drawdown_pct": result["max_drawdown_pct"],
        "win_rate_pct": result["win_rate_pct"],
        "number_of_trades": result["number_of_trades"]
    }


def compare_strategies(symbol, interval, limit, initial_balance, start_date=None, end_date=None):
    ma = run_moving_average(
        symbol, interval, limit, initial_balance, 20, 50, start_date, end_date
    )
    rsi = run_rsi(
        symbol, interval, limit, initial_balance, 14, 30, 70, start_date, end_date
    )
    bollinger = run_bollinger(
        symbol, interval, limit, initial_balance, 20, 2, start_date, end_date
    )

    return [
        format_compare_result("Moving Average Crossover", ma),
        format_compare_result("Relative Strength Index", rsi),
        format_compare_result("Bollinger Bands", bollinger)
    ]
