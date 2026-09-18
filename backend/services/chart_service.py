from services.binance_service import get_dataframe
from strategies.moving_average import moving_average_strategy
from strategies.rsi import rsi_strategy
from strategies.bollinger import bollinger_bands_strategy
from services.chart_data import build_chart_data


def get_moving_average_chart(
    symbol,
    interval,
    limit,
    short_window,
    long_window,
    start_date=None,
    end_date=None
):
    df = get_dataframe(symbol, interval, limit, True, start_date, end_date)
    df = moving_average_strategy(df, short_window, long_window)

    buy_signals = []
    sell_signals = []

    for _, row in df.iterrows():
        if row["position"] == 1:
            buy_signals.append({"price": row["close"]})
        elif row["position"] == -1:
            sell_signals.append({"price": row["close"]})

    return {
        **build_chart_data(df),
        "symbol": symbol,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals
    }


def get_rsi_chart(
    symbol,
    interval,
    limit,
    period,
    oversold,
    overbought,
    start_date=None,
    end_date=None
):
    df = get_dataframe(symbol, interval, limit, True, start_date, end_date)
    df = rsi_strategy(df, period, oversold, overbought)

    return {
        **build_chart_data(df),
        "symbol": symbol,
        "oversold": [oversold] * len(df),
        "overbought": [overbought] * len(df)
    }


def get_bollinger_chart(
    symbol,
    interval,
    limit,
    window,
    num_std,
    start_date=None,
    end_date=None
):
    df = get_dataframe(symbol, interval, limit, True, start_date, end_date)
    df = bollinger_bands_strategy(df, window, num_std)

    return {
        **build_chart_data(df),
        "symbol": symbol,
    }
