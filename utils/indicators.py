import pandas as pd


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghitung indikator teknikal utama menggunakan pustaka pandas_ta 
    dan menambahkannya langsung ke kolom DataFrame.
    """
    if df.empty:
        return df
    
    # Menghitung Exponential Moving Average (EMA)
    df.ta.ema(length=20, append=True)
    df.ta.ema(length=50, append=True)
    df.ta.ema(length=200, append=True)
    
    # Menghitung Relative Strength Index (RSI)
    df.ta.rsi(length=14, append=True)
    
    # Menghitung Moving Average Convergence Divergence (MACD)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    
    return df
