import math


def build_chart_data(df):
    """Keep the chart and execution history tied to the same market snapshot."""
    time_column = "close_time" if "close_time" in df else "open_time"
    data = {
        "timestamps": [int(value) for value in df[time_column]] if time_column in df else [],
        "prices": [float(value) for value in df["close"]],
    }
    columns = {
        "MA_SHORT": "ma_short", "MA_LONG": "ma_long", "RSI": "rsi",
        "UPPER_BAND": "upper_band", "MA": "middle_band", "LOWER_BAND": "lower_band",
    }
    for column, key in columns.items():
        if column in df:
            data[key] = [float(value) if math.isfinite(value) else None for value in df[column]]
    return data
