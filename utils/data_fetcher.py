import yfinance as yf
import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def get_stock_data(ticker, period="1y"):

    try:

        df = yf.download(
            ticker,
            period=period,
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return pd.DataFrame()

        # FIX MULTIINDEX YFINANCE
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Pastikan semua OHLCV berupa numeric Series
        for col in ["Open", "High", "Low", "Close", "Volume"]:

            if col in df.columns:

                if isinstance(df[col], pd.DataFrame):
                    df[col] = df[col].iloc[:, 0]

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

        df.dropna(inplace=True)

        return df

    except Exception as e:

        print(e)

        return pd.DataFrame()


@st.cache_data(ttl=600)
def get_stock_info(ticker):

    try:

        stock = yf.Ticker(ticker)

        return stock.info

    except:

        return {}
