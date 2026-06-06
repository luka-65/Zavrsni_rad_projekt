from flask import Blueprint, request

from services.binance_service import get_dataframe
from strategies.moving_average import moving_average_strategy
from strategies.rsi import rsi_strategy
from strategies.bollinger import bollinger_bands_strategy

chart_bp = Blueprint("chart", __name__)

@chart_bp.route("/api/chart/moving-average", methods=["GET"])
def moving_average_chart():

    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)

    df = get_dataframe(symbol, interval, limit)

    df = moving_average_strategy(df)

    buy_signals = []
    sell_signals = []

    for _, row in df.iterrows():

        if row["position"] == 1:
            buy_signals.append({
                "price": row["close"]
            })

        elif row["position"] == -1:
            sell_signals.append({
                "price": row["close"]
            })

    return {
        "symbol": symbol,
        "prices": df["close"].tolist(),
        "ma_short": df["MA_SHORT"].fillna(0).tolist(),
        "ma_long": df["MA_LONG"].fillna(0).tolist(),
        "buy_signals": buy_signals,
        "sell_signals": sell_signals
    }

@chart_bp.route("/api/chart/rsi", methods=["GET"])
def rsi_chart():

    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)

    df = get_dataframe(symbol, interval, limit)
    df = rsi_strategy(df)

    return {
        "symbol": symbol,
        "prices": df["close"].tolist(),
        "rsi": df["RSI"].fillna(0).tolist(),
        "oversold": [30] * len(df),
        "overbought": [70] * len(df)
    }

@chart_bp.route("/api/chart/bollinger", methods=["GET"])
def bollinger_chart():

    symbol = request.args.get("symbol", "BTCUSDT")
    interval = request.args.get("interval", "1d")
    limit = request.args.get("limit", 200, type=int)

    df = get_dataframe(symbol, interval, limit)

    df = bollinger_bands_strategy(df)

    return {
        "symbol": symbol,
        "prices": df["close"].tolist(),
        "upper_band": df["UPPER_BAND"].fillna(0).tolist(),
        "middle_band": df["MA"].fillna(0).tolist(),
        "lower_band": df["LOWER_BAND"].fillna(0).tolist()
    }