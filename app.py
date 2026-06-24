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
    ), row=1, col=1)
    
    if 'EMA_20' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='#FF9800', width=1.2), name='EMA 20'), row=1, col=1)
    if 'EMA_50' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], line=dict(color='#4CAF50', width=1.2), name='EMA 50'), row=1, col=1)
    if 'EMA_200' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_200'], line=dict(color='#9C27B0', width=1.2), name='EMA 200'), row=1, col=1)

    # Subplot 2: Volume Bar Chart (Warna disesuaikan Close vs Open)
    vol_colors = ['#EF5350' if close < open else '#26A69A' for open, close in zip(df['Open'], df['Close'])]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_colors, name='Volume'), row=2, col=1)

    # Subplot 3: Indikator RSI
    if 'RSI_14' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI_14'], line=dict(color='#E040FB', width=1.5), name='RSI'), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#EF5350", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#26A69A", row=3, col=1)

    fig.update_layout(
        template='plotly_dark',
        height=580,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_rangeslider_visible=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- ROW 3: ANALISIS TEKNIKAL, SIGNAL GAUGES, DAN STATISTIK ---
    st.write("")
    col_tech, col_sig, col_stats = st.columns([1.5, 1, 1.5])
    
    with col_tech:
        st.markdown("### Technical Summary")
        macd_val = df['MACD_12_26_9'].iloc[-1] if 'MACD_12_26_9' in df.columns else 0.0
        
        tech_table = {
            "Indicator": ["RSI (14)", "MACD (12,26,9)", "EMA 20", "EMA 50", "EMA 200"],
            "Value": [f"{current_rsi:.2f}", f"{macd_val:.2f}", f"${df['EMA_20'].iloc[-1]:.2f}", f"${df['EMA_50'].iloc[-1]:.2f}", f"${df['EMA_200'].iloc[-1]:.2f}"],
            "Condition": [
                "Neutral" if 30 < current_rsi < 70 else ("Oversold" if current_rsi <= 30 else "Overbought"),
                "Bearish Call" if macd_val < 0 else "Bullish Call",
                "Below Price (Bull)" if current_price > df['EMA_20'].iloc[-1] else "Above Price (Bear)",
                "Below Price (Bull)" if current_price > df['EMA_50'].iloc[-1] else "Above Price (Bear)",
                "Below Price (Bull)" if current_price > df['EMA_200'].iloc[-1] else "Above Price (Bear)"
            ]
        }
        st.dataframe(pd.DataFrame(tech_table), hide_index=True, use_container_width=True)

    with col_sig:
        st.markdown("### Signal")
        # Logika Sederhana Penentu Keputusan Sistem
        if trend == "Bearish" and current_rsi < 40:
            status_signal, gauge_score, color_signal = "HOLD", 50, "gold"
            desc = "Kondisi pasar sedang netral atau berada di area jenuh jual."
        elif trend == "Bullish" and current_rsi > 55:
            status_signal, gauge_score, color_signal = "BUY", 85, "lightgreen"
            desc = "Sinyal tren naik kuat didukung oleh akumulasi momentum positif."
        else:
            status_signal, gauge_score, color_signal = "SELL", 20, "lightcoral"
            desc = "Indikator teknikal mengindikasikan tekanan distribusi keluar."

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=gauge_score,
            title={'text': status_signal, 'font': {'size': 22, 'color': color_signal}},
            gauge={
                'axis': {'range': [0, 100], 'visible': False},
                'bar': {'color': color_signal},
                'steps': [{'range': [0, 100], 'color': "#2A2E39"}]
            }
        ))
        fig_gauge.update_layout(height=160, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.caption(f"<p style='text-align:center;'>{desc}</p>", unsafe_allow_html=True)

    with col_stats:
        st.markdown("### Key Statistics")
        raw_cap = info.get('marketCap', 0)
        cap_string = f"${raw_cap / 1e12:.2f}T" if raw_cap > 1e12 else f"${raw_cap / 1e9:.2f}B"
        
        stats_table = pd.DataFrame({
            "Metric": ["Open", "High", "Low", "Prev Close", "Market Cap", "P/E Ratio", "EPS (TTM)", "Dividend Yield"],
            "Value": [
                f"${df['Open'].iloc[-1]:.2f}", f"${df['High'].iloc[-1]:.2f}", f"${df['Low'].iloc[-1]:.2f}", f"${prev_close:.2f}",
                cap_string, f"{info.get('trailingPE', 'N/A')}", f"{info.get('trailingEps', 'N/A')}", f"{info.get('dividendYield', 0)*100:.2f}%"
            ]
        })
        st.dataframe(stats_table, hide_index=True, use_container_width=True)

    # --- ROW 4: NEWS CARD BAR FEED ---
    st.divider()
    st.markdown("### Latest News")
    n1, n2, n3, n4 = st.columns(4)
    with n1:
        st.image("https://via.placeholder.com/150x90/131722/FFFFFF?text=TradePro+AI", use_container_width=True)
        st.write("**Apple Unveils New AI Features**")
        st.caption("2 hours ago · Apple announced new AI features across ecosystem...")
    with n2:
        st.image("https://via.placeholder.com/150x90/131722/FFFFFF?text=Hardware+Leaks", use_container_width=True)
        st.write("**iPhone 16 Rumors Heat Up**")
        st.caption("5 hours ago · Leaked reports suggest major hardware upgrades...")
    with n3:
        st.image("https://via.placeholder.com/150x90/131722/FFFFFF?text=Market+Trend", use_container_width=True)
        st.write("**Apple Stock: What Analysts Say**")
        st.caption("1 day ago · Financial analysts remain divided on stock growth...")
    with n4:
        st.image("https://via.placeholder.com/150x90/131722/FFFFFF?text=WWDC+Updates", use_container_width=True)
        st.write("**WWDC Highlights**")
        st.caption("2 days ago · Key developer updates and software benchmarks...")
else:
    st.error("Gagal mendapatkan data instrumen saham. Periksa kembali jaringan atau simbol Ticker.")
