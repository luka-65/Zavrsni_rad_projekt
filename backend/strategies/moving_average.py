import pandas as pd

def moving_average_strategy(df, short_window=20, long_window=50):

    df = df.copy()

    df["MA_SHORT"] = df["close"].rolling(window=short_window).mean()
    df["MA_LONG"] = df["close"].rolling(window=long_window).mean()

    df["signal"] = 0

    df.loc[
        df["MA_SHORT"] > df["MA_LONG"],
        "signal"
    ] = 1

    df["position"] = df["signal"].diff()

    return df