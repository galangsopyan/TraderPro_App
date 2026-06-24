import yfinance as yf

def get_stock_data(ticker, period="1mo"):
    """Mengambil data historis harga saham"""
    try:
        # Menggunakan yf.download biasanya lebih aman dari rate limit dibanding Ticker.history
        df = yf.download(ticker, period=period, progress=False)
        return df
    except Exception:
        return pd.DataFrame()

def get_stock_info(ticker):
    """Mengambil data fundamental perusahaan dengan pengaman rate limit"""
    try:
        stock = yf.Ticker(ticker)
        # Jika sukses, kembalikan dict info bawaan yfinance
        return stock.info
    except Exception:
        # Jika diblokir/rate limit oleh Yahoo Finance, kembalikan dict kosong agar app tidak crash
        return {}
