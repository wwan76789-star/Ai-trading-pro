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
st.caption("AI Trading Signal Dashboard")

market = st.sidebar.selectbox(
    "Market",
    ["Saham Indonesia","Crypto","Forex","Emas"]
)

if market=="Saham Indonesia":
    symbol=st.sidebar.text_input("Kode","BBCA.JK")
elif market=="Crypto":
    symbol=st.sidebar.text_input("Kode","BTC-USD")
elif market=="Forex":
    symbol=st.sidebar.text_input("Kode","EURUSD=X")
else:
    symbol=st.sidebar.text_input("Kode","GC=F")

interval=st.sidebar.selectbox(
    "Timeframe",
    ["5m","15m","30m","1h","1d"],
    index=1
)

period="7d"

df=yf.download(
    symbol,
    period=period,
    interval=interval,
    auto_adjust=False,
    progress=False
)

if df.empty:
    st.error("Data tidak tersedia")
    st.stop()

if isinstance(df.columns,pd.MultiIndex):
    df.columns=df.columns.droplevel(1)

df=df.dropna()

df["EMA20"]=EMAIndicator(df["Close"],20).ema_indicator()
df["EMA50"]=EMAIndicator(df["Close"],50).ema_indicator()

macd=MACD(df["Close"])

df["MACD"]=macd.macd()
df["MACD_SIGNAL"]=macd.macd_signal()

df["RSI"]=RSIIndicator(df["Close"]).rsi()

atr=AverageTrueRange(
    df["High"],
    df["Low"],
    df["Close"]
)

df["ATR"]=atr.average_true_range()

last=df.iloc[-1]


entry=float(last["Close"])
sl=entry-float(last["ATR"]*2)
tp=entry+float(last["ATR"]*3)

c1,c2,c3,c4=st.columns(4)

c1.metric("Signal", signal)
c2.metric("Confidence", f"{confidence}%")
c3.metric("Entry", f"{entry:,.2f}")
c4.metric("RSI", f"{last['RSI']:.2f}")
st.write("### Analisis AI")
for a in alasan:
    st.write("✅", a)
st.write(f"Stop Loss : {sl:,.2f}")
st.write(f"Take Profit : {tp:,.2f}")
score = 0
alasan = []

# EMA
if last["EMA20"] > last["EMA50"]:
    score += 30
    alasan.append("EMA Bullish")
else:
    score -= 20
    alasan.append("EMA Bearish")

# MACD
if last["MACD"] > last["MACD_SIGNAL"]:
    score += 25
    alasan.append("MACD Bullish")
else:
    score -= 15
    alasan.append("MACD Bearish")

# RSI
if 55 <= last["RSI"] <= 70:
    score += 20
    alasan.append("RSI Sehat")
elif last["RSI"] < 30:
    score += 15
    alasan.append("Oversold")
elif last["RSI"] > 70:
    score -= 20
    alasan.append("Overbought")

# Trend
if last["Close"] > last["EMA20"]:
    score += 15

# Volatilitas
if last["ATR"] < df["ATR"].mean():
    score += 10

confidence = max(0, min(score, 100))

if confidence >= 70:
    signal = "🟢 BUY"
elif confidence >= 45:
    signal = "🟡 HOLD"
else:
    signal = "🔴 SELL"
fig=go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Price"
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

st.plotly_chart(fig,use_container_width=True)
st.divider()
st.subheader("📋 AI Scanner")

watchlist = {
    "Saham": [
        "BBCA.JK",
        "BBRI.JK",
        "BMRI.JK",
        "TLKM.JK",
        "ASII.JK"
    ],
    "Crypto": [
        "BTC-USD",
        "ETH-USD",
        "SOL-USD",
        "BNB-USD",
        "XRP-USD"
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

pilih = st.selectbox(
    "Scanner",
    ["Saham","Crypto","Forex","Emas"]
)

hasil = []

for kode in watchlist[pilih]:

    try:

        data = yf.download(
            kode,
            period="5d",
            interval="1h",
            progress=False,
            auto_adjust=False
        )

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        data = data.dropna()

        data["EMA20"] = EMAIndicator(
            data["Close"],
            20
        ).ema_indicator()

        data["EMA50"] = EMAIndicator(
            data["Close"],
            50
        ).ema_indicator()

        rsi = RSIIndicator(
            data["Close"]
        ).rsi()

        last = data.iloc[-1]

        score = 0

        if last["EMA20"] > last["EMA50"]:
            score += 50

        if rsi.iloc[-1] > 50:
            score += 50

        if score >= 80:
            signal = "🟢 BUY"
        elif score >= 50:
            signal = "🟡 HOLD"
        else:
            signal = "🔴 SELL"

        hasil.append({
            "Kode": kode,
            "Harga": round(float(last["Close"]),2),
            "Signal": signal,
            "Confidence": score
        })

    except:
        pass

if len(hasil):
    st.dataframe(
        pd.DataFrame(hasil),
        use_container_width=True
)
