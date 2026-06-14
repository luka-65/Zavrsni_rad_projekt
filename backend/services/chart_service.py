from services.binance_service import get_dataframe
from strategies.moving_average import moving_average_strategy
from strategies.rsi import rsi_strategy
from strategies.bollinger import bollinger_bands_strategy


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
        "symbol": symbol,
        "prices": df["close"].tolist(),
        "ma_short": df["MA_SHORT"].fillna(0).tolist(),
        "ma_long": df["MA_LONG"].fillna(0).tolist(),
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
        "symbol": symbol,
        "prices": df["close"].tolist(),
        "rsi": df["RSI"].fillna(0).tolist(),
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
        "symbol": symbol,
        "prices": df["close"].tolist(),
        "upper_band": df["UPPER_BAND"].fillna(0).tolist(),
        "middle_band": df["MA"].fillna(0).tolist(),
        "lower_band": df["LOWER_BAND"].fillna(0).tolist()
    }
