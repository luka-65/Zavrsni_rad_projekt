def bollinger_bands_strategy(df, window=20, num_std=2):

    df = df.copy()

    df["MA"] = df["close"].rolling(window=window).mean()
    df["STD"] = df["close"].rolling(window=window).std()

    df["UPPER_BAND"] = df["MA"] + (num_std * df["STD"])
    df["LOWER_BAND"] = df["MA"] - (num_std * df["STD"])

    # Missing signals preserve the previous state; zero explicitly closes it.
    df["signal"] = float("nan")

    df.loc[df["close"] < df["LOWER_BAND"], "signal"] = 1
    df.loc[df["close"] > df["UPPER_BAND"], "signal"] = 0

    df["signal"] = df["signal"].ffill().fillna(0)
    df["position"] = df["signal"].diff()

    return df
