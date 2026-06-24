import pandas as pd
import streamlit as st


@st.cache_data(ttl=86400)
def load_stocks():

    try:
        return pd.read_csv("data/idx_stocks.csv")

    except:
        return pd.DataFrame()
