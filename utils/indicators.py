import pandas as pd

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghitung indikator teknikal (EMA, RSI, MACD) menggunakan fungsi 
    native Pandas untuk menjamin kompatibilitas penuh di Streamlit Cloud.
    """
    if df.empty:
        return df
    
    # Salin dataframe untuk menghindari masalah SettingWithCopyWarning
    df = df.copy()
    
    # 1. Menghitung Exponential Moving Average (EMA)
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    # 2. Menghitung Relative Strength Index (RSI - Wilder's Style)
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Menggunakan Wilder's exponential moving average smoothing
    avg_gain = gain.ewm(com=13, adjust=False).mean()
    avg_loss = loss.ewm(com=13, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # 3. Menghitung MACD (12, 26, 9)
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD_12_26_9'] = exp1 - exp2
    df['MACD_sign'] = df['MACD_12_26_9'].ewm(span=9, adjust=False).mean()
    
    return df
