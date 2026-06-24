import pandas as pd
import streamlit as st


@st.cache_data(ttl=86400)
def load_idx_stocks():

    try:

        url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"

        df = pd.read_csv(url)

        return df

    except Exception:

        return pd.DataFrame()
