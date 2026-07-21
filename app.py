import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

st.set_page_config(
    page_title="AI Trading Pro",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI Trading Pro")
st.caption("Realtime Trading Dashboard")

# ======================
# Sidebar
# ======================

market = st.sidebar.selectbox(
    "Market",
    [
        "Saham Indonesia",
        "Crypto",
        "Forex",
        "Emas"
    ]
)

if market == "Saham Indonesia":
    symbol = st.sidebar.text_input("Kode", "BBCA.JK")

elif market == "Crypto":
    symbol = st.sidebar.text_input("Kode", "BTC-USD")

elif market == "Forex":
    symbol = st.sidebar.text_input("Kode", "EURUSD=X")

else:
    symbol = st.sidebar.text_input("Kode", "GC=F")

interval = st.sidebar.selectbox(
    "Timeframe",
    [
        "5m",
        "15m",
        "30m",
        "1h",
        "1d"
    ],
    index=1
)

period = "7d"

# ======================
# Download Data
# ======================

df = yf.download(
    symbol,
    period=period,
    interval=interval,
    auto_adjust=False,
    progress=False
)

if df.empty:
    st.error("Data tidak tersedia")
    st.stop()

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.droplevel(1)

df = df.dropna()

# ======================
# Indicator
# ======================

df["EMA20"] = EMAIndicator(df["Close"], 20).ema_indicator()
df["EMA50"] = EMAIndicator(df["Close"], 50).ema_indicator()

macd = MACD(df["Close"])

df["MACD"] = macd.macd()
df["MACD_SIGNAL"] = macd.macd_signal()

df["RSI"] = RSIIndicator(df["Close"]).rsi()

atr = AverageTrueRange(
    df["High"],
    df["Low"],
    df["Close"]
)

df["ATR"] = atr.average_true_range()
# ======================
# AI SIGNAL
# ======================

last = df.iloc[-1]

score = 0
alasan = []

# EMA
if last["EMA20"] > last["EMA50"]:
    score += 30
    alasan.append("EMA Bullish")
else:
    alasan.append("EMA Bearish")

# MACD
if last["MACD"] > last["MACD_SIGNAL"]:
    score += 25
    alasan.append("MACD Bullish")
else:
    alasan.append("MACD Bearish")

# RSI
if 50 <= last["RSI"] <= 70:
    score += 20
    alasan.append("RSI Sehat")
elif last["RSI"] < 30:
    score += 10
    alasan.append("Oversold")
elif last["RSI"] > 70:
    alasan.append("Overbought")

# Trend
if last["Close"] > last["EMA20"]:
    score += 15

# ATR
if last["ATR"] < df["ATR"].mean():
    score += 10

confidence = min(score, 100)

if confidence >= 70:
    signal = "🟢 BUY"
elif confidence >= 45:
    signal = "🟡 HOLD"
else:
    signal = "🔴 SELL"

entry = float(last["Close"])
sl = entry - float(last["ATR"] * 2)
tp = entry + float(last["ATR"] * 3)

# ======================
# DASHBOARD
# ======================

c1, c2, c3, c4 = st.columns(4)

c1.metric("Signal", signal)
c2.metric("Confidence", f"{confidence}%")
c3.metric("Entry", f"{entry:,.2f}")
c4.metric("RSI", f"{last['RSI']:.2f}")

st.success(f"Stop Loss : {sl:,.2f}")
st.success(f"Take Profit : {tp:,.2f}")

with st.expander("Analisis AI"):
    for x in alasan:
        st.write("✅", x)

# ======================
# CHART
# ======================

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Candlestick"
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=df["EMA20"],
    name="EMA20"
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=df["EMA50"],
    name="EMA50"
))

fig.update_layout(height=650)

st.plotly_chart(fig, use_container_width=True)
# ======================
# AI SCANNER
# ======================

st.divider()
st.subheader("📋 AI Scanner")

watchlist = {
    "Saham": [
        "BBCA.JK",
        "BBRI.JK",
        "BMRI.JK",
        "TLKM.JK",
        "ASII.JK",
        "BBNI.JK",
        "ANTM.JK",
        "MDKA.JK"
    ],
    "Crypto": [
        "BTC-USD",
        "ETH-USD",
        "SOL-USD",
        "BNB-USD",
        "XRP-USD",
        "DOGE-USD"
    ],
    "Forex": [
        "EURUSD=X",
        "GBPUSD=X",
        "USDJPY=X",
        "AUDUSD=X"
    ],
    "Emas": [
        "GC=F"
    ]
}

kategori = st.selectbox(
    "Pilih Scanner",
    list(watchlist.keys())
)

hasil = []

for kode in watchlist[kategori]:

    try:

        d = yf.download(
            kode,
            period="5d",
            interval="1h",
            progress=False,
            auto_adjust=False
        )

        if d.empty:
            continue

        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.droplevel(1)

        d = d.dropna()

        d["EMA20"] = EMAIndicator(
            d["Close"],
            20
        ).ema_indicator()

        d["EMA50"] = EMAIndicator(
            d["Close"],
            50
        ).ema_indicator()

        d["RSI"] = RSIIndicator(
            d["Close"]
        ).rsi()

        x = d.iloc[-1]

        score = 0

        if x["EMA20"] > x["EMA50"]:
            score += 50

        if x["RSI"] > 50:
            score += 50

        if score >= 80:
            signal = "BUY"
        elif score >= 50:
            signal = "HOLD"
        else:
            signal = "SELL"

        hasil.append({
            "Kode": kode,
            "Harga": round(float(x["Close"]), 2),
            "Signal": signal,
            "Confidence": score
        })

    except Exception:
        pass

if hasil:
    st.dataframe(
        pd.DataFrame(hasil),
        use_container_width=True
      )
    # ======================
# MULTI TIMEFRAME ANALYSIS
# ======================

st.divider()
st.subheader("🧠 Multi Timeframe AI")

timeframes = ["15m", "1h", "1d"]
hasil_tf = []

for tf in timeframes:
    try:
        d = yf.download(
            symbol,
            period="30d",
            interval=tf,
            progress=False,
            auto_adjust=False
        )

        if d.empty:
            continue

        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.droplevel(1)

        d = d.dropna()

        d["EMA20"] = EMAIndicator(d["Close"], 20).ema_indicator()
        d["EMA50"] = EMAIndicator(d["Close"], 50).ema_indicator()

        d["RSI"] = RSIIndicator(d["Close"]).rsi()

        x = d.iloc[-1]

        score = 0

        if x["EMA20"] > x["EMA50"]:
            score += 50

        if x["RSI"] > 50:
            score += 50

        if score >= 80:
            signal = "🟢 BUY"
        elif score >= 50:
            signal = "🟡 HOLD"
        else:
            signal = "🔴 SELL"

        hasil_tf.append({
            "Timeframe": tf,
            "Signal": signal,
            "Confidence": score
        })

    except:
        pass

if hasil_tf:
    st.dataframe(
        pd.DataFrame(hasil_tf),
        use_container_width=True
    )
    # ======================
# VOLUME ANALYSIS
# ======================

st.divider()
st.subheader("📊 Volume Analysis")

df["VOL_MA20"] = df["Volume"].rolling(20).mean()

volume_now = float(df["Volume"].iloc[-1])
volume_avg = float(df["VOL_MA20"].iloc[-1])

if volume_avg > 0:
    volume_ratio = volume_now / volume_avg
else:
    volume_ratio = 1

if volume_ratio >= 2:
    volume_signal = "🔥 Volume Spike"
elif volume_ratio >= 1.3:
    volume_signal = "🟢 Above Average"
else:
    volume_signal = "⚪ Normal"

c1, c2, c3 = st.columns(3)

c1.metric("Volume", f"{volume_now:,.0f}")
c2.metric("Avg 20", f"{volume_avg:,.0f}")
c3.metric("Status", volume_signal)
# ======================
# BREAKOUT DETECTION
# ======================

st.divider()
st.subheader("🚀 Breakout Detection")

high20 = df["High"].tail(20).max()
low20 = df["Low"].tail(20).min()
close = float(df["Close"].iloc[-1])

if close >= high20 * 0.998:
    breakout = "🚀 Bullish Breakout"

elif close <= low20 * 1.002:
    breakout = "🔻 Bearish Breakdown"

else:
    breakout = "➡️ Sideways"

st.info(breakout)
  # ======================
# SUPPORT & RESISTANCE
# ======================

st.divider()
st.subheader("📊 Support & Resistance")

support = df["Low"].tail(20).min()
resistance = df["High"].tail(20).max()

c1, c2 = st.columns(2)

c1.metric(
    "Support",
    f"{support:,.2f}"
)

c2.metric(
    "Resistance",
    f"{resistance:,.2f}"
)

# ======================
# RISK MANAGEMENT
# ======================

st.divider()
st.subheader("⚖️ Risk Management")

risk = entry - sl
reward = tp - entry

rr = reward / risk if risk > 0 else 0

c1, c2, c3 = st.columns(3)

c1.metric("Risk", f"{risk:,.2f}")
c2.metric("Reward", f"{reward:,.2f}")
c3.metric("R:R", f"1 : {rr:.2f}")

# ======================
# TREND
# ======================

st.divider()

if last["EMA20"] > last["EMA50"]:
    st.success("📈 Trend Utama : BULLISH")
else:
    st.error("📉 Trend Utama : BEARISH")

# ======================
# DATA TERAKHIR
# ======================

st.divider()
st.subheader("📄 Data Terbaru")

st.dataframe(
    df.tail(20),
    use_container_width=True
)
