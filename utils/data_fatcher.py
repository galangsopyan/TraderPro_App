import yfinance as yf
import pandas as pd

def get_stock_data(ticker: str, period: str = "1mo") -> pd.DataFrame:
    """
    Mengambil data historis pasar saham berdasarkan ticker dan periode.
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    return df

def get_stock_info(ticker: str) -> dict:
    """
    Mengambil data fundamental / statistik kunci dari sebuah perusahaan.
    """
    stock = yf.Ticker(ticker)
    return stock.info
