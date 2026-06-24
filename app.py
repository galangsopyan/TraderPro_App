import os
import sys

# --- FORCE PYTHON UNTUK MENEMUKAN FOLDER UTILS ---
# Kode ini memaksa server Cloud membaca direktori tempat app.py berada
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- BARU MASUKKAN IMPORT LAINNYA ---
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.data_fetcher import get_stock_data, get_stock_info
from utils.indicators import calculate_indicators




# --- CONFIG HALAMAN ---
st.set_page_config(
    page_title="TradePro Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- INJEK CSS KUSTOM ---
try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# --- SIDEBAR (NAVIGASI & INDEKS GLOBAL) ---
with st.sidebar:
    st.markdown("<h2 style='color: #2962FF; margin-bottom: 0;'>📈 TradePro</h2>", unsafe_allow_html=True)
    st.caption("Plan. Trade. Profit.")
    st.write("")
    
    # Navigasi Menu utama
    menu = ["🏠 Dashboard", "🔍 Screener", "⚡ Backtester", "🛡️ Risk Management", "📰 Market News", "⚙️ Settings"]
    for item in menu:
        st.button(item, use_container_width=True)
        
    st.divider()
    st.write("**MARKET STATUS**")
    st.success("🟢 Market Open")
    st.caption("15:35:42 WIB · June 21, 2026")
    
    st.divider()
    st.write("**MAJOR INDICES**")
    st.metric("S&P 500", "5,487.03", "+0.65%")
    st.metric("Nasdaq 100", "19,868.12", "+0.82%")
    st.metric("Dow Jones", "38,589.16", "+0.35%")

# --- HEADER UTAMA ---
col_title, _ = st.columns([3, 1])
with col_title:
    st.title("Market Overview")
    st.caption("Stay updated with real-time market data and technical analysis")

# --- FILTER CONTROLLER ---
col_ticker, col_period = st.columns(2)
with col_ticker:
    selected_ticker = st.selectbox("TICKER", ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"], index=0)
with col_period:
    selected_period = st.selectbox("PERIOD", ["1M", "3M", "6M", "YTD", "1Y", "5Y", "ALL"], index=0)

# Mapping input ke format parameter yfinance
period_map = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "YTD": "ytd", "1Y": "1y", "5Y": "5y", "ALL": "max"}
yf_period = period_map[selected_period]

# --- PIPELINE PENGOLAHAN DATA ---
raw_data = get_stock_data(selected_ticker, yf_period)
df = calculate_indicators(raw_data)
info = get_stock_info(selected_ticker)

if not df.empty:
    # Ekstraksi poin data terupdate untuk ringkasan metrik
    current_price = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2]
    change_1d = current_price - prev_close
    pct_change_1d = (change_1d / prev_close) * 100
    current_rsi = df['RSI_14'].iloc[-1] if 'RSI_14' in df.columns else 50.0
    current_vol = df['Volume'].iloc[-1]
    avg_vol = df['Volume'].mean()

    # --- ROW 1: METRICS CARDS ---
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("PRICE", f"${current_price:.2f} USD")
    m2.metric("CHANGE (1D)", f"+${change_1d:.2f}" if change_1d > 0 else f"${change_1d:.2f}", f"{pct_change_1d:+.2f}%")
    m3.metric("RSI (14)", f"{current_rsi:.2f}")
    
    # Kalkulasi Tren Sederhana
    trend = "Bullish" if current_price > df['EMA_50'].iloc[-1] else "Bearish"
    trend_icon = "🟢" if trend == "Bullish" else "🔴"
    m4.metric("TREND", f"{trend_icon} {trend}", "Above EMA50" if trend == "Bullish" else "Below EMA50")
    m5.metric("VOLUME", f"{current_vol/1e6:.2f}M", f"Avg: {avg_vol/1e6:.2f}M")

    # --- ROW 2: CHART MULTI-SUBPLOTS (PRICE, VOLUME, RSI) ---
    st.write("")
    st.markdown("### Price Chart")
    
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.04, 
        row_heights=[0.6, 0.2, 0.2]
    )

    # Subplot 1: Candlestick & Garis EMA
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name='Price'
    ), row=1, col=1)import os
import sys

# --- FORCE PYTHON UNTUK MENEMUKAN FOLDER UTILS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.data_fetcher import get_stock_data, get_stock_info
from utils.indicators import calculate_indicators

# --- CONFIG HALAMAN ---
st.set_page_config(
    page_title="TradePro Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- INJEK CSS KUSTOM ---
try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# --- STATE MANAGEMENT UNTUK NAVIGASI ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"

# --- SIDEBAR (NAVIGASI) ---
with st.sidebar:
    st.markdown("<h2 style='color: #2962FF; margin-bottom: 0;'>📈 TradePro</h2>", unsafe_allow_html=True)
    st.caption("Plan. Trade. Profit.")
    st.write("")
    
    # List Menu
    menu_options = [
        "🏠 Dashboard", 
        "🔍 Screener", 
        "⚡ Backtester", 
        "🛡️ Risk Management", 
        "📰 Market News", 
        "⚙️ Settings"
    ]
    
    # Render tombol navigasi dengan deteksi halaman aktif
    for item in menu_options:
        if st.button(item, use_container_width=True):
            st.session_state.current_page = item
        
    st.divider()
    st.write("**MARKET STATUS**")
    st.success("🟢 Market Open")
    st.caption("15:35:42 WIB · June 21, 2026")
    
    st.divider()
    st.write("**MAJOR INDICES**")
    st.metric("S&P 500", "5,487.03", "+0.65%")
    st.metric("Nasdaq 100", "19,868.12", "+0.82%")

# --- LOGIK HALAMAN (ROUTING CONTROLLER) ---

# 1. HALAMAN DASHBOARD MAIN
if st.session_state.current_page == "🏠 Dashboard":
    st.title("Market Overview")
    st.caption("Stay updated with real-time market data and technical analysis")
    
    col_ticker, col_period = st.columns(2)
    with col_ticker:
        selected_ticker = st.selectbox("TICKER", ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"], index=0)
    with col_period:
        selected_period = st.selectbox("PERIOD", ["1M", "3M", "6M", "YTD", "1Y"], index=0)

    period_map = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "YTD": "ytd", "1Y": "1y"}
    
    raw_data = get_stock_data(selected_ticker, period_map[selected_period])
    df = calculate_indicators(raw_data)
    info = get_stock_info(selected_ticker)

    if not df.empty:
        current_price = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        change_1d = current_price - prev_close
        pct_change_1d = (change_1d / prev_close) * 100
        current_rsi = df['RSI_14'].iloc[-1] if 'RSI_14' in df.columns else 50.0

        # Metrics cards
        m1, m2, m3 = st.columns(3)
        m1.metric("PRICE", f"${current_price:.2f} USD")
        m2.metric("CHANGE (1D)", f"${change_1d:+.2f}", f"{pct_change_1d:+.2f}%")
        m3.metric("RSI (14)", f"{current_rsi:.2f}")

        # Chart
        st.write("")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
        if 'EMA_20' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='#FF9800', width=1.2), name='EMA 20'), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='gray'), row=2, col=1)
        fig.update_layout(template='plotly_dark', height=450, margin=dict(l=10, r=10, t=10, b=10), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Gagal memuat data pasar.")

# 2. HALAMAN SCREENER
elif st.session_state.current_page == "🔍 Screener":
    st.title("🛡️ Market Screener")
    st.caption("Pindai kondisi pasar saham berdasarkan indikator teknikal real-time.")
    
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"]
    screener_data = []
    
    with st.spinner("Scanning market conditions..."):
        for t in tickers:
            data = get_stock_data(t, "1mo")
            data = calculate_indicators(data)
            if not data.empty:
                cp = data['Close'].iloc[-1]
                rsi = data['RSI_14'].iloc[-1]
                ema20 = data['EMA_20'].iloc[-1]
                cond = "Oversold 🟢" if rsi < 35 else ("Overbought 🔴" if rsi > 65 else "Neutral 🟡")
                screener_data.append({"Ticker": t, "Price": f"${cp:.2f}", "RSI (14)": f"{rsi:.2f}", "EMA 20": f"${ema20:.2f}", "Signal": cond})
                
    st.dataframe(pd.DataFrame(screener_data), use_container_width=True, hide_index=True)

# 3. HALAMAN BACKTESTER
elif st.session_state.current_page == "⚡ Backtester":
    st.title("⚡ Strategy Backtester")
    st.caption("Uji performa strategi trading 'Price vs EMA 20' menggunakan data historis.")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        bt_ticker = st.selectbox("Pilih Ticker", ["AAPL", "MSFT", "TSLA"])
    with col_b2:
        capital = st.number_input("Modal Awal ($)", value=10000)
        
    bt_data = get_stock_data(bt_ticker, "1y")
    bt_data = calculate_indicators(bt_data)
    
    if len(bt_data) > 20:
        # Logika simulasi trading sederhana
        shares = 0
        balance = capital
        for i in range(1, len(bt_data)):
            price = bt_data['Close'].iloc[i]
            ema = bt_data['EMA_20'].iloc[i]
            prev_price = bt_data['Close'].iloc[i-1]
            prev_ema = bt_data['EMA_20'].iloc[i-1]
            
            # Buy signal (Golden Cross over EMA20)
            if prev_price < prev_ema and price > ema and balance > price:
                shares = balance // price
                balance -= (shares * price)
            # Sell signal (Death Cross under EMA20)
            elif prev_price > prev_ema and price < ema and shares > 0:
                balance += (shares * price)
                shares = 0
                
        final_asset = balance + (shares * bt_data['Close'].iloc[-1])
        roi = ((final_asset - capital) / capital) * 100
        
        c1, c2 = st.columns(2)
        c1.metric("Nilai Akhir Portofolio", f"${final_asset:.2f}")
        c2.metric("Return on Investment (ROI)", f"{roi:+.2f}%")
    else:
        st.warning("Data tidak mencukupi untuk melakukan backtest.")

# 4. HALAMAN RISK MANAGEMENT
elif st.session_state.current_page == "🛡️ Risk Management":
    st.title("🛡️ Position Size Calculator")
    st.caption("Hitung alokasi modal dan risiko per trade secara sistematis.")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        acc_size = st.number_input("Total Saldo Akun ($)", value=5000)
        risk_pct = st.slider("Risiko per Transaksi (%)", 1.0, 5.0, 2.0, 0.5)
    with col_r2:
        entry_p = st.number_input("Harga Entry ($)", value=150.0)
        stop_l = st.number_input("Harga Stop Loss ($)", value=145.0)
        
    if entry_p > stop_l:
        amount_at_risk = acc_size * (risk_pct / 100)
        risk_per_share = entry_p - stop_l
        position_size = amount_at_risk / risk_per_share
        total_cost = position_size * entry_p
        
        st.divider()
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Uang Berisiko (Max Loss)", f"${amount_at_risk:.2f}")
        rc2.metric("Jumlah Saham Ditransaksikan", f"{position_size:.2f} Lembar")
        rc3.metric("Total Nilai Pembelian", f"${total_cost:.2f}")
    else:
        st.error("Harga Stop Loss harus lebih rendah dari Harga Entry untuk posisi Buy.")

# 5. HALAMAN MARKET NEWS
elif st.session_state.current_page == "📰 Market News":
    st.title("📰 Tech Market News")
    st.caption("Kumpulan berita fundamental pasar terkini.")
    
    news_list = [
        {"title": "Apple Unveils New AI Features", "time": "2 hours ago", "desc": "Apple announced new generative AI architecture integrated into upcoming operating systems."},
        {"title": "iPhone 16 Rumors Heat Up", "time": "5 hours ago", "desc": "Supply chain leaks point towards camera sensor upgrades and improved battery density."},
        {"title": "Macro Impact on Tech Stocks", "time": "1 day ago", "desc": "Analysts break down how interest rates are shifting institutional money back to mega-caps."}
    ]
    for n in news_list:
        with st.container():
            st.markdown(f"### {n['title']}")
            st.caption(n['time'])
            st.write(n['desc'])
            st.divider()

# 6. HALAMAN SETTINGS
elif st.session_state.current_page == "⚙️ Settings":
    st.title("⚙️ System Settings")
    st.caption("Konfigurasi parameter default dashboard TradePro.")
    
    st.checkbox("Aktifkan Notifikasi Real-time Email", value=True)
    st.checkbox("Gunakan Cache Data Historis (Lebih Cepat)", value=True)
    st.selectbox("Default Indicator MA Type", ["EMA (Exponential)", "SMA (Simple)", "WMA (Weighted)"])
    st.button("Simpan Pengaturan", type="primary")
