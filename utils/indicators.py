import pandas as pd


def calculate_rsi(close, period=14):

    delta = close.diff()

    gain = delta.where(delta > 0, 0)

    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_indicators(df):

    if df.empty:
        return df

    close = pd.Series(df["Close"]).astype(float)

    df["EMA_20"] = close.ewm(
        span=20,
        adjust=False
    ).mean()

    df["EMA_50"] = close.ewm(
        span=50,
        adjust=False
    ).mean()

    df["EMA_200"] = close.ewm(
        span=200,
        adjust=False
    ).mean()

    df["RSI_14"] = calculate_rsi(
        close,
        14
    )

    return df
