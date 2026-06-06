def rsi_strategy(df, period=14, oversold=30, overbought=70):

    df = df.copy()

    delta = df["close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss

    df["RSI"] = 100 - (100 / (1 + rs))

    df["signal"] = 0

    df.loc[df["RSI"] < oversold, "signal"] = 1
    df.loc[df["RSI"] > overbought, "signal"] = 0

    df["signal"] = df["signal"].replace(0, None).ffill().fillna(0)
    df["position"] = df["signal"].diff()

    return df