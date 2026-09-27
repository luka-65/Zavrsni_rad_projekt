def rsi_strategy(df, period=14, oversold=30, overbought=70):

    df = df.copy()

    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss.where(avg_loss > 0)
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.mask((avg_loss == 0) & (avg_gain > 0), 100.0)
    rsi = rsi.mask((avg_loss == 0) & (avg_gain == 0), 50.0)

    df["RSI"] = rsi

    df["signal"] = float("nan")

    df.loc[df["RSI"] < oversold, "signal"] = 1
    df.loc[df["RSI"] > overbought, "signal"] = 0

    df["signal"] = df["signal"].ffill().fillna(0)
    df["position"] = df["signal"].diff()

    return df
